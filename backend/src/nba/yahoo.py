"""Yahoo Fantasy NBA reads over the injected lineup.yahoo transport.

Same rules as the NFL client: authenticated GET only, untrusted payloads
validated, bearer token only in the Authorization header. NBA rosters are
read by calendar date (`roster;date=YYYY-MM-DD`). With AFC_ENABLE_NBA off,
get_leagues returns nothing and every other read or import raises before
a request or a store write.
"""

import re
from datetime import datetime, timezone
from decimal import Decimal

from lineup.yahoo import _echo, _fields, _get, _items, _key, _max_items
from nba import enabled


def _bench_slots():
    return frozenset({"BN", "IL", "IL+"})


# Yahoo NBA stat ids -> ESPN boxscore keys. One table: correct it here when
# the live Yahoo app is checked (planned 2026-10-23). 12 PTS, 15 REB, 16 AST,
# 17 ST, 18 BLK, 19 TO. An unknown id fails the whole map (no partial table).
def _stat_ids():
    return {"12": "points", "15": "rebounds", "16": "assists", "17": "steals",
            "18": "blocks", "19": "turnovers"}


# Yahoo team code -> ESPN site API abbreviation, only where they differ.
# ESPN side read 2026-10-20 from
# https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams
# (GS, NO, NY, SA, UTAH, WSH). Yahoo's public roster pages use the other code.
def _yahoo_to_espn_team():
    return {"GSW": "GS", "NOP": "NO", "NYK": "NY", "SAS": "SA", "UTA": "UTAH",
            "WAS": "WSH"}


def _require():
    if not enabled():
        raise ValueError("NBA Yahoo is disabled")


def _date(value):
    """Strict calendar date. Reject before any Yahoo request."""
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Date must be YYYY-MM-DD")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be a real calendar date") from None
    if parsed.strftime("%Y-%m-%d") != value:
        raise ValueError("Date must be YYYY-MM-DD")
    return value


def _team(abbreviation):
    """ESPN abbreviation for a Yahoo or already-ESPN team code."""
    if not isinstance(abbreviation, str):
        return None
    return _yahoo_to_espn_team().get(abbreviation, abbreviation)


def get_leagues(transport, token):
    if not enabled():
        return []
    payload = _get(transport, token, "users;use_login=1/games;game_keys=nba/leagues")
    return [_fields(item, {"league_key": str, "name": str, "season": int})
            for item in _items(payload, "leagues")]


def get_teams(transport, token, league_key):
    _require()
    _key(league_key, "league key")
    payload = _get(transport, token, f"league/{league_key}/teams")
    return [_fields(item, {"team_key": str, "name": str}) for item in _items(payload, "teams")]


def get_roster(transport, token, team_key, date):
    """Starters by recorded slot (never by eligibility) and bench for one date."""
    _require()
    _key(team_key, "team key")
    _date(date)
    payload = _get(transport, token, f"team/{team_key}/roster;date={date}")
    _echo(payload, "team_key", team_key)
    _echo(payload, "date", date)
    players = []
    for item in _items(payload, "players"):
        player = _fields(item, {"player_key": str, "name": str, "team": str,
                                "positions": list, "slot": str})
        if not all(isinstance(p, str) for p in player["positions"]):
            raise ValueError("Yahoo player positions must be strings")
        players.append(player)
    keys = [p["player_key"] for p in players]
    if any(not key.strip() for key in keys):
        raise ValueError("Yahoo player_key must be non-blank")
    if len(set(keys)) != len(keys):
        raise ValueError("Yahoo roster repeats a player_key")
    if sum(p["slot"] not in _bench_slots() for p in players) > 32:
        raise ValueError("Yahoo roster exceeds the 32-starter panel limit")
    return {"team_key": team_key, "date": date,
            "starters": [p for p in players if p["slot"] not in _bench_slots()],
            "bench": [p for p in players if p["slot"] in _bench_slots()]}


def get_settings(transport, token, league_key):
    """League settings. A category league omits stat_modifiers; that is {}."""
    _require()
    _key(league_key, "league key")
    payload = _get(transport, token, f"league/{league_key}/settings")
    _echo(payload, "league_key", league_key)
    modifiers = payload.get("stat_modifiers", {})
    if not isinstance(modifiers, dict) or len(modifiers) > _max_items() or not all(
            isinstance(k, str) and isinstance(v, (int, float)) and not isinstance(v, bool)
            for k, v in modifiers.items()):
        raise ValueError("Yahoo settings have no valid stat_modifiers")
    slots = payload.get("roster_slots")
    if not isinstance(slots, list) or len(slots) > _max_items() or not all(
            isinstance(s, str) for s in slots):
        raise ValueError("Yahoo settings have no valid roster_slots")
    return {"league_key": league_key, "stat_modifiers": dict(modifiers),
            "roster_slots": list(slots)}


def league_scoring(stat_modifiers):
    """ESPN-key modifiers, or None when empty or any Yahoo stat id is unknown."""
    if not isinstance(stat_modifiers, dict) or not stat_modifiers:
        return None
    mapped = {}
    for stat_id, value in stat_modifiers.items():
        name = _stat_ids().get(str(stat_id))
        if name is None or isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        mapped[name] = float(value)
    return mapped


def map_starters(starters, espn_roster):
    """Copy each starter, adding athlete_id when name and team match one ESPN player.

    Team comparison normalizes known Yahoo/ESPN abbreviation differences.
    The stored team stays the Yahoo code. Two different ESPN athletes with
    the same name and team match nobody.
    """
    if not isinstance(starters, list) or not isinstance(espn_roster, list):
        raise ValueError("starters and espn_roster must be lists")
    by_name_team = {}
    for player in espn_roster:
        if not isinstance(player, dict):
            raise ValueError("ESPN roster entry must be an object")
        key = (player.get("name"), _team(player.get("team")))
        athlete = player.get("athlete_id")
        if key in by_name_team and by_name_team[key] != athlete:
            by_name_team[key] = None
        elif key not in by_name_team:
            by_name_team[key] = athlete
    mapped = []
    for starter in starters:
        if not isinstance(starter, dict):
            raise ValueError("Yahoo starter must be an object")
        row = dict(starter)
        row.pop("athlete_id", None)
        athlete = by_name_team.get((starter.get("name"), _team(starter.get("team"))))
        if isinstance(athlete, str) and athlete.strip():
            row["athlete_id"] = athlete
        mapped.append(row)
    return mapped


def import_lineup(transport, token, profile_id, league_key, team_key, date, espn_roster):
    """Store the dated NBA starters. The token is never written."""
    _require()
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError("profile_id must be a non-empty string")
    _key(league_key, "league key")
    _key(team_key, "team key")
    _date(date)
    if not isinstance(espn_roster, list):
        raise ValueError("ESPN roster must be a list")
    roster = get_roster(transport, token, team_key, date)
    settings = get_settings(transport, token, league_key)
    table = league_scoring(settings["stat_modifiers"])
    # DynamoDB rejects float. str keeps 1.0 and -0.5 exact.
    scoring = ({"stat_modifiers": {key: Decimal(str(value)) for key, value in table.items()}}
               if table is not None else {})
    import store
    store.put_lineup({
        "profileId": profile_id, "source": "yahoo", "sport": "nba",
        "team": team_key, "league": league_key,
        "starters": map_starters(roster["starters"], espn_roster),
        "scoring": scoring,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
