"""ESPN NBA scoreboard/summary bodies to the NFL statistics seam shape.

Scoreboard validation reuses the pinned NFL scoreboard schema, whose read
fields (events[].id/status, competitors[].team, leaders) are the same ESPN
site API shape for basketball/nba (verified against a live capture).
shortcut: summary validation is hand-checked pinned fields, not a pinned
JSON Schema file; add schema/nba-summary.json if NBA leaves spike scope.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import logging
import re

from feed_ingest.validation import validate_scoreboard

# ESPN NBA boxscore keys that score under nba.scoring; all other keys
# (minutes, splits like "8-15", plusMinus, ...) are deliberately unmapped.
SCORING_KEYS = ("points", "rebounds", "assists", "turnovers", "steals", "blocks")
_SOURCES = ("live", "replay")
_MAX_ATHLETES = 200  # same bound as feed_ingest.normalize.MAX_BOXSCORE_ATHLETES


def scoreboard_games(payload):
    """One descriptor per scoreboard event, after pinned-schema validation."""
    validate_scoreboard(payload)
    games = []
    for game in payload["events"]:
        teams, players = [], []
        for competition in game.get("competitions", []):
            for competitor in competition.get("competitors", []):
                team = competitor["team"]
                teams.extend(team[key] for key in ("id", "abbreviation") if key in team)
            for category in competition.get("leaders", []):
                players.extend(leader["athlete"]["id"] for leader in category["leaders"])
        games.append({"gameId": game["id"],
                      "state": game.get("status", {}).get("type", {}).get("state"),
                      "teamIds": teams, "playerIds": players})
    return games


def pregame_status_by_team(payload):
    """ESPN text for each team's earliest dated pregame; started games omitted."""
    validate_scoreboard(payload)
    found = {}
    for game in payload["events"]:
        status = game.get("status", {}).get("type", {})
        if status.get("state") != "pre":
            continue
        detail = status.get("shortDetail") or status.get("detail")
        if not isinstance(detail, str) or not detail.strip() or len(detail) > 80:
            continue
        try:
            tip = datetime.fromisoformat(game.get("date", "").replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            continue
        if tip.utcoffset() is None:
            continue
        order = (tip, game["id"])
        for competition in game.get("competitions", []):
            for competitor in competition.get("competitors", []):
                abbr = competitor["team"].get("abbreviation")
                if isinstance(abbr, str) and re.fullmatch(r"[A-Z0-9]{2,4}", abbr):
                    if abbr not in found or order < found[abbr][0]:
                        found[abbr] = (order, detail)
    return {abbr: detail for abbr, (_, detail) in found.items()}


_ESPN_TIME = re.compile(r"(\d{1,2}):(\d{2}) (AM|PM) E[DS]T")


def _central(detail, verb):
    """ESPN "10/21 - 8:30 PM EDT" becomes "Tips 7:30 PM": Central is an hour behind Eastern."""
    found = _ESPN_TIME.search(detail)
    if not found:
        return detail
    hour = int(found[1]) % 12 + (12 if found[3] == "PM" else 0) - 1
    return f"{verb} {(hour % 12) or 12}:{found[2]} {'PM' if hour % 24 >= 12 else 'AM'}"


def _today():
    return (datetime.now(timezone.utc) - timedelta(hours=5)).date()


def _weekday(start, text, verb):
    """Owner 2026-10-23: a start on another day names it ("Sun 12:00 PM"); today's keeps the verb.
    Central is taken as UTC-5, the same fixed offset _central assumes."""
    try:
        when = datetime.fromisoformat(str(start).replace("Z", "+00:00")) - timedelta(hours=5)
    except ValueError:
        return text
    if when.date() == _today() or not text.startswith(verb + " "):
        return text
    return when.strftime("%a") + text[len(verb):]


def team_status_by_team(events, verb):
    """Each team's game status today: a live clock beats a start time, which beats a final.

    Takes scoreboard `events` from either sport; `verb` names a start ("Tips" or "Kicks").
    """
    rank = {"in": 0, "pre": 1, "post": 2}
    found = {}
    for game in events if isinstance(events, list) else []:
        status = (game.get("status") or {}).get("type") or {}
        state = status.get("state")
        detail = status.get("shortDetail") or status.get("detail")
        if state not in rank or not isinstance(detail, str) or not detail.strip():
            continue
        text = _central(detail, verb) if state == "pre" else detail
        if state == "pre":
            text = _weekday(game.get("date"), text, verb)
        if len(text) > 80:
            continue
        order = (rank[state], str(game.get("date") or ""))
        for competition in game.get("competitions", []):
            for competitor in competition.get("competitors", []):
                abbr = (competitor.get("team") or {}).get("abbreviation")
                if isinstance(abbr, str) and re.fullmatch(r"[A-Z0-9]{2,4}", abbr):
                    if abbr not in found or order < found[abbr][0]:
                        found[abbr] = (order, text)
    return {abbr: text for abbr, (_, text) in found.items()}


def _status(payload):
    try:
        return payload["header"]["competitions"][0]["status"]["type"]
    except (KeyError, IndexError, TypeError, AttributeError):
        return None


def validate_nba_summary(payload, game_id):
    """None when `payload` is a usable NBA summary for `game_id`; ValueError otherwise."""
    if not isinstance(payload, dict) or (payload.get("header") or {}).get("id") != game_id:
        raise ValueError("ESPN NBA summary is for another game")
    status = _status(payload)
    if not isinstance(status, dict) or status.get("state") not in ("pre", "in", "post"):
        raise ValueError("ESPN NBA summary has no usable game state")
    players = (payload.get("boxscore") or {}).get("players")
    if not isinstance(players, list):
        raise ValueError("ESPN NBA summary has no boxscore players")


def _stat_value(value):
    """A DynamoDB-safe Decimal for one untrusted boxscore value, or None."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        return None
    text = value if isinstance(value, str) else str(value)
    if len(text) > 16:
        return None
    try:
        number = Decimal(text)
    except (InvalidOperation, ArithmeticError, ValueError):
        return None
    if number.is_finite() and abs(number) <= 99999 and -4 <= number.as_tuple().exponent <= 0:
        return number
    return None


def boxscore_statistics_nba(payload, game_id, source="live"):
    """Per-athlete scoring stats from a validated NBA summary's boxscore.

    Same record shape as feed_ingest.normalize.boxscore_statistics, so the
    stored records flow through store.put_player_statistics and the panel
    player_statistics seam unchanged. asOf is the latest play wallclock.
    """
    if source not in _SOURCES:
        raise ValueError(f"Feed events must be labeled live or replay, not {source!r}")
    validate_nba_summary(payload, game_id)
    status = _status(payload)
    detail = status.get("shortDetail") or status.get("detail")
    clocks = [play.get("wallclock") for play in payload.get("plays") or []
              if isinstance(play, dict)]
    clocks = [clock for clock in clocks if isinstance(clock, str) and clock]
    by_athlete, invalid = {}, 0
    for team in payload["boxscore"]["players"]:
        if not isinstance(team, dict):
            continue
        for category in team.get("statistics") or []:
            if not isinstance(category, dict) or not isinstance(category.get("keys"), list):
                continue
            for entry in category.get("athletes") or []:
                if not isinstance(entry, dict) or not isinstance(entry.get("stats"), list):
                    continue
                athlete_id = (entry.get("athlete") or {}).get("id")
                if not (isinstance(athlete_id, str)
                        and re.fullmatch(r"[0-9]{1,20}", athlete_id)):
                    invalid += 1
                    continue
                if athlete_id not in by_athlete and len(by_athlete) >= _MAX_ATHLETES:
                    continue
                stats = by_athlete.setdefault(athlete_id, {})
                for key, value in zip(category["keys"], entry["stats"]):
                    if key in SCORING_KEYS:
                        number = _stat_value(value)
                        if number is not None:
                            stats[key] = number
    if invalid:
        logging.getLogger(__name__).warning(
            "NBA boxscore %.40s: skipped %d entries with invalid athleteId", game_id, invalid)
    return [{"athleteId": athlete_id, "gameId": game_id, "gameState": status["state"],
             "gameStatus": detail if isinstance(detail, str) else None,
             "source": source, "asOf": max(clocks) if clocks else None, "stats": stats}
            for athlete_id, stats in by_athlete.items() if stats]
