"""DES-AFC-P2-FEED: profile-relevant ESPN polling with labeled replay fallback."""

import functools
import json
import logging
import os
import time
from pathlib import Path
from urllib import parse, request

import store
from feed_ingest.ingest import ingest_summary, store_events
from feed_ingest.monitoring import monitored_decisions
from feed_ingest.replay import load_events
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


def _fixtures():
    return Path(__file__).resolve().parents[2] / "fixtures" / "replay"


def _get_json(url):
    """GET from the ESPN allowlist only, with no redirects and bounded size/time."""
    parts = parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "site.api.espn.com":
        raise ValueError("Feed requests go only to https://site.api.espn.com")
    with _opener().open(url, timeout=10) as response:
        body = response.read(_max_bytes() + 1)
    if len(body) > _max_bytes():
        raise ValueError("ESPN response exceeds the size bound")
    return json.loads(body)


def _monitored(game, profiles):
    teams, players = [], []
    for competition in game.get("competitions", []):
        for competitor in competition.get("competitors", []):
            team = competitor["team"]
            teams.extend(team[key] for key in ("id", "abbreviation") if key in team)
        for category in competition.get("leaders", []):
            players.extend(leader["athlete"]["id"] for leader in category["leaders"])
    descriptor = {"gameId": game["id"], "teamIds": teams, "playerIds": players}
    enabled = game.get("status", {}).get("type", {}).get("state") == "in"
    monitored = False
    for profile in profiles:
        selections = profile["settings"].get("fantasySelections", {})
        if not isinstance(selections, dict):
            selections = {}
        starters = profile["starters"]
        selected = [player.get("athlete_id", player.get("player_key")) for player in starters]
        favorites = selections.get("favoriteTeamIds", [])
        # Yahoo starters carry their NFL team; ESPN scoreboards do not carry full rosters.
        starter_teams = [player["team"] for player in starters if "team" in player]
        decision = monitored_decisions([descriptor], selected, favorites + starter_teams,
                                       enabled, basis="profile-assumption")[0]
        logging.getLogger(__name__).info("Monitoring decision: %s", decision)
        monitored |= decision["monitored"]
    return monitored


def poll(failures=None):
    """Isolate each monitored game's failures; the invocation owns consecutive counts."""
    if failures is None:
        failures = {}
    scoreboard = _get_json(_feed() + "scoreboard")
    validate_scoreboard(scoreboard)
    profiles = store.monitoring_profiles()
    result = {"stored": 0, "failed": []}
    for game in scoreboard["events"]:
        if not _monitored(game, profiles):
            continue
        game_id = game["id"]
        try:
            summary = _get_json(_feed() + "summary?event=" + game_id)
            events = ingest_summary(summary, game_id)
        except (ValueError, OSError):
            result["failed"].append(game_id)
            failures[game_id] = failures.get(game_id, 0) + 1
            if failures[game_id] < 3:
                continue
            try:
                events = store_events(load_events(game_id, _fixtures()))
            except (ValueError, OSError):
                result.setdefault("stale", []).append(game_id)
                continue
        else:
            failures[game_id] = 0
        result["stored"] += len(events)
    return result


def lambda_handler(event, context):
    """Poll at the configured interval, retaining a ten-second request/deadline margin."""
    if not isinstance(event, dict) or event.get("source", "aws.scheduler") != "aws.scheduler":
        raise ValueError("IngestFunction accepts only its schedule event")
    interval = int(os.environ.get("FEED_POLL_INTERVAL_SECONDS", "15"))
    if interval <= 0:
        raise ValueError("Feed polling interval must be positive")
    failures = {}
    total = {"stored": 0, "failed": []}
    while True:
        result = poll(failures)
        total["stored"] += result["stored"]
        for key, game_ids in result.items():
            if key == "stored":
                continue
            for game_id in game_ids:
                if game_id not in total.setdefault(key, []):
                    total[key].append(game_id)
        if context is None or context.get_remaining_time_in_millis() <= (interval + 10) * 1000:
            return total
        time.sleep(interval)
