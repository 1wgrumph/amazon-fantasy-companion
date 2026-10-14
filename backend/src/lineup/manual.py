"""AFC-PR-006 labeled manual entry from ESPN rosters when Yahoo is not approved."""

from datetime import datetime, timezone

from lineup import presets

T_YAHOO = "2026-10-16T19:00:00Z"
MAX_ENTRIES = 200
_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def _instant(value):
    if not isinstance(value, str):
        raise ValueError("Timestamp must be an RFC 3339 UTC string")
    return datetime.strptime(value, _FORMAT).replace(tzinfo=timezone.utc)


def activation(now_iso, yahoo_approved):
    """`yahoo` once approved; otherwise `pending` before T_yahoo and `manual` from it."""
    now = _instant(now_iso)
    if not isinstance(yahoo_approved, bool):
        raise ValueError("yahoo_approved must be a boolean")
    if yahoo_approved:
        return "yahoo"
    return "manual" if now >= _instant(T_YAHOO) else "pending"


def build(espn_roster, entries, preset):
    """A manual Lineup of ESPN roster players, labeled manual with its preset."""
    if preset not in presets.TABLES:
        raise ValueError(f"Unknown scoring preset: {preset!r}")
    if not isinstance(espn_roster, list) or len(espn_roster) > MAX_ENTRIES:
        raise ValueError("ESPN roster must be a bounded list")
    names = {}
    for player in espn_roster:
        if not (isinstance(player, dict) and isinstance(player.get("athlete_id"), str)
                and player["athlete_id"] and isinstance(player.get("name"), str)):
            raise ValueError("ESPN roster entry needs an athlete_id and name")
        names[player["athlete_id"]] = player["name"]
    if not isinstance(entries, list) or len(entries) > MAX_ENTRIES:
        raise ValueError("Lineup entries must be a bounded list")
    starters = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("slot"), str) or not entry["slot"]:
            raise ValueError("Lineup entry needs an athlete_id and slot")
        athlete = entry.get("athlete_id")
        if athlete not in names:
            raise ValueError(f"Player {athlete!r} is not on the ESPN roster")
        if any(s["athlete_id"] == athlete for s in starters):
            raise ValueError(f"Player {athlete!r} is entered twice")
        starters.append({"athlete_id": athlete, "name": names[athlete], "slot": entry["slot"]})
    return {"source": "manual", "scoring": {"preset": preset}, "starters": starters}
