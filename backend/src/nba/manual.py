"""Manual NBA lineup from an ESPN roster (issue #137).

Same entry checks as lineup.manual. With AFC_ENABLE_NBA off, build raises
and writes nothing. Pass league and team together to copy the fantasy pair
onto the lineup, the same fields an NFL manual row stores so the panel can
match the profile's teamLeague.
"""

import re

from nba import enabled


def _max_entries():
    return 200


def _max_starters():
    return 32


def build(espn_roster, entries, *, league=None, team=None):
    """A manual lineup of ESPN roster players, labeled manual and sport nba.

    league and team are optional together. When both are set they are the
    fantasy pair panel.snapshot compares with the selected teamLeague.
    """
    if not enabled():
        raise ValueError("NBA manual lineups are disabled")
    if league is not None or team is not None:
        if (not isinstance(league, str) or not league
                or not isinstance(team, str) or not team):
            raise ValueError("Manual lineup needs a league and a team")
    if not isinstance(espn_roster, list) or len(espn_roster) > _max_entries():
        raise ValueError("ESPN roster must be a bounded list")
    players = {}
    for player in espn_roster:
        if not (isinstance(player, dict) and isinstance(player.get("athlete_id"), str)
                and player["athlete_id"].strip() and isinstance(player.get("name"), str)):
            raise ValueError("ESPN roster entry needs an athlete_id and name")
        roster_team = player.get("team")
        if not isinstance(roster_team, str) or not re.fullmatch(r"[A-Z0-9]{2,4}", roster_team):
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
    lineup = {"source": "manual", "sport": "nba", "starters": starters}
    if league is not None:
        lineup["league"] = league
        lineup["team"] = team
    return lineup
