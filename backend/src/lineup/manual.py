"""AFC-PR-006 labeled manual entry from ESPN rosters when Yahoo is not approved.

Constants are function-scoped for the mutation gate; T_YAHOO and MAX_ENTRIES
stay readable as module attributes.
"""

from datetime import datetime, timezone
import re

from lineup import presets



def _t_yahoo():
    return "2026-10-16T19:00:00Z"


def _max_entries():
    return 200


def _max_starters():
    return 32  # frozen panel row bound the TV decoder enforces


def __getattr__(name):
    if name == "T_YAHOO":
        return _t_yahoo()
    if name == "MAX_ENTRIES":
        return _max_entries()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _instant(value):
    if not isinstance(value, str):
        raise ValueError("Timestamp must be an RFC 3339 UTC string")
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def activation(now_iso, yahoo_approved):
    """`yahoo` once approved; otherwise `pending` before T_yahoo and `manual` from it."""
    now = _instant(now_iso)
    if not isinstance(yahoo_approved, bool):
        raise ValueError("yahoo_approved must be a boolean")
    if yahoo_approved:
        return "yahoo"
    return "manual" if now >= _instant(_t_yahoo()) else "pending"


def build(espn_roster, entries, preset):
    """A manual Lineup of ESPN roster players, labeled manual with its preset."""
    if preset not in presets.TABLES:
        raise ValueError(f"Unknown scoring preset: {preset!r}")
    if not isinstance(espn_roster, list) or len(espn_roster) > _max_entries():
        raise ValueError("ESPN roster must be a bounded list")
    players = {}
    for player in espn_roster:
        if not (isinstance(player, dict) and isinstance(player.get("athlete_id"), str)
                and player["athlete_id"] and isinstance(player.get("name"), str)):
            raise ValueError("ESPN roster entry needs an athlete_id and name")
        team = player.get("team")
        if not isinstance(team, str) or not re.fullmatch(r"[A-Z0-9]{2,4}", team):
            raise ValueError("ESPN roster entry needs a team of 2-4 uppercase letters/digits")
        players[player["athlete_id"]] = player
    if not isinstance(entries, list) or len(entries) > _max_starters():
        raise ValueError("Lineup entries must be a list of at most 32 starters")
    starters = []
    for entry in entries:
        if (not isinstance(entry, dict) or not isinstance(entry.get("athlete_id"), str)
                or not isinstance(entry.get("slot"), str) or not entry["slot"]):
            raise ValueError("Lineup entry needs an athlete_id and slot")
        athlete = entry.get("athlete_id")
        if athlete not in players:
            raise ValueError(f"Player {athlete!r} is not on the ESPN roster")
        if any(s["athlete_id"] == athlete for s in starters):
            raise ValueError(f"Player {athlete!r} is entered twice")
        player = players[athlete]
        starters.append({"athlete_id": athlete, "name": player["name"],
                         "team": player["team"], "slot": entry["slot"]})
    return {"source": "manual", "scoring": {"preset": preset}, "starters": starters}
