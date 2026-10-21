"""Manual NBA lineup from an ESPN roster (issue #137).

Same entry checks as lineup.manual. With AFC_ENABLE_NBA off, build raises
and writes nothing.
"""

import re

from nba import enabled


def _max_entries():
    return 200


def _max_starters():
    return 32


def build(espn_roster, entries):
    """A manual lineup of ESPN roster players, labeled manual and sport nba."""
    if not enabled():
        raise ValueError("NBA manual lineups are disabled")
    if not isinstance(espn_roster, list) or len(espn_roster) > _max_entries():
        raise ValueError("ESPN roster must be a bounded list")
    players = {}
    for player in espn_roster:
        if not (isinstance(player, dict) and isinstance(player.get("athlete_id"), str)
                and player["athlete_id"].strip() and isinstance(player.get("name"), str)):
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
    return {"source": "manual", "sport": "nba", "starters": starters}
