"""AFC-PR-001 Yahoo Fantasy read-only client over an injected transport.

The transport is `request(method, url, headers)` returning parsed JSON. Every
call is an authenticated GET; the client never writes. Responses are untrusted:
types, required keys and sizes are validated and anything else raises
ValueError. The bearer token is only placed in the Authorization header,
never logged or stored.
"""

import re



def _api():
    return "https://fantasysports.yahooapis.com/fantasy/v2/"


def _bench_slots():
    return frozenset({"BN", "IR", "NA"})


def _max_items():
    return 200  # far above any real roster/league list; bounds hostile payloads


def __getattr__(name):
    if name == "MAX_ITEMS":
        return _max_items()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _key(value, what):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9._]{1,64}", value):
        raise ValueError(f"Invalid Yahoo {what}")
    return value


def _get(transport, token, path):
    if not isinstance(token, str) or not token:
        raise ValueError("Yahoo access token is required")
    payload = transport.request("GET", _api() + path, {"Authorization": "Bearer " + token})
    if not isinstance(payload, dict):
        raise ValueError("Yahoo response is not a JSON object")
    return payload


def _items(payload, name):
    items = payload.get(name)
    if not isinstance(items, list) or len(items) > _max_items():
        raise ValueError(f"Yahoo response has no bounded {name} list")
    if not all(isinstance(item, dict) for item in items):
        raise ValueError(f"Yahoo {name} entry is not a JSON object")
    return items


def _fields(item, types):
    for field, kind in types.items():
        value = item.get(field)
        if not isinstance(value, kind) or isinstance(value, bool):
            raise ValueError(f"Yahoo field {field} has an unexpected type")
    return {field: item[field] for field in types}


def _echo(payload, field, expected):
    if payload.get(field) != expected:
        raise ValueError(f"Yahoo response {field} does not match the request")


def get_leagues(transport, token):
    payload = _get(transport, token, "users;use_login=1/games;game_keys=nfl/leagues")
    return [_fields(item, {"league_key": str, "name": str, "season": int})
            for item in _items(payload, "leagues")]


def get_teams(transport, token, league_key):
    _key(league_key, "league key")
    payload = _get(transport, token, f"league/{league_key}/teams")
    return [_fields(item, {"team_key": str, "name": str}) for item in _items(payload, "teams")]


def get_roster(transport, token, team_key, week):
    """Starters by recorded slot (never by eligibility) and bench for one week."""
    _key(team_key, "team key")
    if not isinstance(week, int) or isinstance(week, bool) or week < 1:
        raise ValueError("Week must be a positive integer")
    payload = _get(transport, token, f"team/{team_key}/roster;week={week}")
    _echo(payload, "team_key", team_key)
    _echo(payload, "week", week)
    players = []
    for item in _items(payload, "players"):
        player = _fields(item, {"player_key": str, "name": str, "team": str,
                                "positions": list, "slot": str})
        if not all(isinstance(p, str) for p in player["positions"]):
            raise ValueError("Yahoo player positions must be strings")
        players.append(player)
    return {"team_key": team_key, "week": week,
            "starters": [p for p in players if p["slot"] not in _bench_slots()],
            "bench": [p for p in players if p["slot"] in _bench_slots()]}


def get_settings(transport, token, league_key):
    _key(league_key, "league key")
    payload = _get(transport, token, f"league/{league_key}/settings")
    _echo(payload, "league_key", league_key)
    modifiers = payload.get("stat_modifiers")
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
