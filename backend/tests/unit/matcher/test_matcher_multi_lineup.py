"""The matcher sees every lineup a profile holds (multisport arch-review, sections 3 and 7).

It uses the union of starters across all the profile's lineups, de-duplicated
by ESPN athlete id, and still makes one match per (profile, event id).
"""

import store
from matcher_support import (MANUAL_PASSER, MANUAL_RECEIVER, TIMESTAMP,  # noqa: F401
                             athlete_ids, game_event, match_env)

GUARD = {"athlete_id": "9100001", "name": "Sample Guard", "team": "SHO", "slot": "PG"}


def put(league, team, starters, sport=None):
    row = {"profileId": "fan", "source": "manual", "league": league, "team": team,
           "starters": [dict(s) for s in starters], "updatedAt": TIMESTAMP}
    if sport:
        row["sport"] = sport
    store.put_lineup(row)


def test_nfl_and_nba_events_each_match_their_own_starter(match_env):
    assert store.put_profile("fan", {}, 0, TIMESTAMP)
    put("league-a", "team-7", [MANUAL_RECEIVER])
    put("nba-demo", "afc-nba", [GUARD], sport="nba")
    nfl = match_env.resolve(game_event("401999001301", ["9000001"]))
    assert [(m["profileId"], athlete_ids(m)) for m in nfl] == [("fan", {"9000001"})], \
        f"an NFL event must match the NFL starter of a profile that also holds NBA: {nfl!r}"
    nba = match_env.resolve(dict(game_event("401999101301", ["9100001"]),
                                 gameId="401999101", sport="nba"))
    assert [(m["profileId"], athlete_ids(m)) for m in nba] == [("fan", {"9100001"})]


def test_shared_athlete_across_lineups_is_reported_once(match_env):
    assert store.put_profile("fan", {}, 0, TIMESTAMP)
    put("league-a", "team-7", [MANUAL_RECEIVER, MANUAL_PASSER])
    put("league-b", "team-2", [MANUAL_RECEIVER])
    matches = match_env.resolve(game_event("401999001302", ["9000001", "9000005"]))
    assert len(matches) == 1, f"one match per (profile, event): {matches!r}"
    ids = [s["athlete_id"] for s in matches[0]["starters"]]
    assert sorted(ids) == ["9000001", "9000005"], \
        f"starters are the union across lineups, each ESPN id once: {ids}"
