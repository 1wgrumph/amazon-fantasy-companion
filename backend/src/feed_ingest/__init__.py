"""DES-AFC-P2-FEED: profile-relevant ESPN polling with labeled replay fallback."""

import functools
import json
import logging
import os
import time
from pathlib import Path
from urllib import parse, request

from botocore.exceptions import ClientError

import store
from feed_ingest.ingest import ingest_summary, rejected_item, store_events, store_player_statistics
from feed_ingest.monitoring import monitored_decisions
from feed_ingest.replay import load_events, load_statistics
from feed_ingest.validation import validate_scoreboard


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("ESPN redirects are refused")


@functools.cache
def _opener():
    return request.build_opener(_NoRedirect)


def _feed():
    return "https://site.api.espn.com/apis/site/v2/sports/football/nfl/"


def _max_bytes():
    return 4 * 1024 * 1024  # above the largest capture; bounds hostile bodies


_REQUEST_SECONDS = 10  # _get_json timeout; deadline guards reserve it per request

# shortcut: warm-container counts only, upgrade to a durable store when
# IngestFunction gains a state-table grant (a cold start resets the count).
_FAILURES = {}


def _nba_enabled():
    return os.environ.get("AFC_ENABLE_NBA", "").lower() in ("1", "true", "yes")


def _fixtures():
    # Packaged under CodeUri src/ (template Globals); never walk above it.
    return Path(__file__).resolve().parent / "replay_data"


def _get_json(url):
    """GET from the ESPN allowlist only, with no redirects and bounded size/time."""
    parts = parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "site.api.espn.com":
        raise ValueError("Feed requests go only to https://site.api.espn.com")
    with _opener().open(url, timeout=_REQUEST_SECONDS) as response:
        body = response.read(_max_bytes() + 1)
    if len(body) > _max_bytes():
        raise ValueError("ESPN response exceeds the size bound")
    return json.loads(body)


def _monitored(game, profiles, enabled=None):
    teams, players = [], []
    for competition in game.get("competitions", []):
        for competitor in competition.get("competitors", []):
            team = competitor["team"]
            teams.extend(team[key] for key in ("id", "abbreviation") if key in team)
        for category in competition.get("leaders", []):
            players.extend(leader["athlete"]["id"] for leader in category["leaders"])
    descriptor = {"gameId": game["id"], "teamIds": teams, "playerIds": players}
    if enabled is None:
        enabled = game.get("status", {}).get("type", {}).get("state") == "in"
    monitored = False
    for profile in profiles:
        selections = profile["settings"].get("fantasySelections", {})
        if not isinstance(selections, dict):
            selections = {}
        starters = profile["starters"]
        selected = [player.get("athlete_id", player.get("player_key")) for player in starters]
        favorites = selections.get("favoriteTeamIds", [])
        # Lineup starters carry their NFL team; ESPN scoreboards do not carry full rosters.
        starter_teams = [player["team"] for player in starters if "team" in player]
        decision = monitored_decisions([descriptor], selected, favorites + starter_teams,
                                       enabled, basis="profile-assumption")[0]
        logging.getLogger(__name__).info("Monitoring decision: %s", decision)
        monitored |= decision["monitored"]
    return monitored


def _fallback(game_id, failures, result):
    """Count one consecutive failure; at three, store labeled replay or report stale."""
    result["failed"].append(game_id)
    failures[game_id] = failures.get(game_id, 0) + 1
    if failures[game_id] < 3:
        return
    try:
        events = store_events(load_events(game_id, _fixtures()))
        store_player_statistics(load_statistics(game_id, _fixtures()))
    except (ValueError, OSError):
        result.setdefault("stale", []).append(game_id)
        return
    result["stored"] += len(events)


def _captured_relevant(profiles):
    """Packaged replay games relevant to a profile, for scoreboard outages.

    Relevance comes from each capture's own scoreboard; its historical final
    state is not the enabled period — the scheduled invocation is. Replay
    hashes are still verified by load_events before anything is stored.
    """
    relevant = []
    for index_path in sorted(_fixtures().glob("*/index.json")):
        try:
            index = json.loads(index_path.read_text())
            boards = [e for e in index["files"] if e["endpoint"] == "scoreboard"]
            board = json.loads(
                (index_path.parent / Path(boards[-1]["file"]).name).read_text())
            game = next(g for g in board["events"] if g["id"] == index["game_id"])
            if _monitored(game, profiles, enabled=True):
                relevant.append(game["id"])
        except (ValueError, OSError, KeyError, TypeError, StopIteration, IndexError):
            continue  # one unreadable capture must not block the others' fallback
    return relevant


def poll(failures=None, remaining=None):
    """Isolate each monitored game's failures; counts outlive one invocation.

    `remaining`, when given, returns the invocation seconds left; no request
    starts unless its ten-second bound fits inside them.
    """
    if failures is None:
        failures = _FAILURES
    result = {"stored": 0, "failed": []}
    if remaining is not None and remaining() <= _REQUEST_SECONDS:
        return result
    try:
        scoreboard = _get_json(_feed() + "scoreboard")
    except OSError:
        for game_id in _captured_relevant(store.monitoring_profiles()):
            _fallback(game_id, failures, result)
        return result
    validate_scoreboard(scoreboard)
    profiles = store.monitoring_profiles()
    for game in scoreboard["events"]:
        if not _monitored(game, profiles):
            continue
        if remaining is not None and remaining() <= _REQUEST_SECONDS:
            break
        game_id = game["id"]
        try:
            summary = _get_json(_feed() + "summary?event=" + game_id)
            events = ingest_summary(summary, game_id)
        except (ValueError, OSError):
            _fallback(game_id, failures, result)
            continue
        except ClientError as exc:
            if not rejected_item(exc):
                raise
            # A schema-valid body DynamoDB still rejects fails only its own game.
            logging.getLogger(__name__).warning(
                "Feed write rejected for game %s: %.200s", game_id, exc)
            _fallback(game_id, failures, result)
            continue
        failures[game_id] = 0
        result["stored"] += len(events)
    if _nba_enabled():  # AFC_ENABLE_NBA stretch spike; inert when the flag is off
        import nba

        nba_result = nba.poll(_get_json)
        result["stored"] += nba_result["stored"]
        result["failed"].extend(nba_result["failed"])
    return result


def lambda_handler(event, context):
    """Poll at the configured interval while a whole further poll fits the budget."""
    if not isinstance(event, dict) or event.get("source", "aws.scheduler") != "aws.scheduler":
        raise ValueError("IngestFunction accepts only its schedule event")
    interval = int(os.environ.get("FEED_POLL_INTERVAL_SECONDS", "15"))
    if interval <= 0:
        raise ValueError("Feed polling interval must be positive")
    remaining = (lambda: context.get_remaining_time_in_millis() / 1000
                 if context is not None else None)
    poll_seconds = _REQUEST_SECONDS
    total = {"stored": 0, "failed": []}
    while True:
        before = remaining()
        result = poll(_FAILURES, remaining if context is not None else None)
        if before is not None:
            # The last poll's observed cost bounds the next one (same games).
            poll_seconds = max(_REQUEST_SECONDS, before - remaining())
        total["stored"] += result["stored"]
        for key, game_ids in result.items():
            if key == "stored":
                continue
            for game_id in game_ids:
                if game_id not in total.setdefault(key, []):
                    total[key].append(game_id)
        if context is None or remaining() <= interval + poll_seconds:
            return total
        time.sleep(interval)
