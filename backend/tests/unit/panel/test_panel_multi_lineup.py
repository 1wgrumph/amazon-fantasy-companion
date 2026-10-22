"""Panels per pair for a profile holding NFL and NBA lineups (multisport arch-review 3, 5, 7).

project() writes only to pairs whose lineup sport (default nfl) equals the
event sport (default nfl). snapshot() for a pair shows only that pair's
rows, and a pair's revision never drops across writes to either pair.
"""

from panel_support import (LEAGUE, RECEIVER, TEAM, TEAM_LEAGUE, at,  # noqa: F401
                           game_event, match, panel_env, player_ids, seed_lineup,
                           seed_profile)

NBA_LEAGUE, NBA_TEAM = "nba-demo", "afc-nba"
NBA_PAIR = f"{NBA_LEAGUE}/{NBA_TEAM}"
GUARD = {"athlete_id": "9100001", "name": "Sample Guard", "team": "SHO", "slot": "PG"}
CENTER = {"athlete_id": "9100003", "name": "Sample Center", "team": "SHO", "slot": "C"}


def seed_nba(starters):
    import store
    store.put_lineup({"profileId": "fan", "source": "manual", "sport": "nba",
                      "league": NBA_LEAGUE, "team": NBA_TEAM,
                      "starters": [dict(s) for s in starters], "updatedAt": at(0)})


def panel_pairs(panel_env):
    return sorted(p["teamLeague"] for p in panel_env.api.table("Panels").scan()["Items"])


def test_nfl_event_projects_only_to_the_nfl_pair(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    seed_nba([GUARD])
    event = game_event("401999001401")
    panel_env.project(event, [match("fan", event)])
    assert panel_pairs(panel_env) == [TEAM_LEAGUE], \
        f"an NFL event must project into the NFL pair only, got {panel_pairs(panel_env)}"
    nba_event = dict(game_event("401999101401", ("9100001",), game="401999101"), sport="nba")
    panel_env.project(nba_event, [match("fan", nba_event, starters=(GUARD,))])
    assert panel_pairs(panel_env) == sorted([TEAM_LEAGUE, NBA_PAIR])
    # snapshot, not data(): data() rejects nbaPoints, and the api fixture turns NBA on.
    assert set(panel_env.snapshot("fan", NBA_PAIR)["data"]["games"]) == {"401999101"}, \
        "NFL games never enter an NBA games map"
    assert set(panel_env.data("fan", TEAM_LEAGUE)["games"]) == {"401999001"}


def test_each_pair_snapshot_shows_only_its_rows_and_revision_never_drops(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    seed_nba([GUARD])
    nfl = panel_env.snapshot("fan", TEAM_LEAGUE)
    nba = panel_env.snapshot("fan", NBA_PAIR)
    assert player_ids(nfl["data"]) == {"9000001"}, \
        f"the NFL pair must keep its rows after an NBA write: {nfl['data']['rows']!r}"
    assert player_ids(nba["data"]) == {"9100001"}
    assert nfl["source"] == "manual" and nfl["data"]["scoringBasis"] == "halfPpr"
    seed_nba([GUARD, CENTER])
    nfl2, nba2 = panel_env.snapshot("fan", TEAM_LEAGUE), panel_env.snapshot("fan", NBA_PAIR)
    assert player_ids(nfl2["data"]) == {"9000001"}
    assert player_ids(nba2["data"]) == {"9100001", "9100003"}
    assert nfl2["revision"] >= nfl["revision"] and nba2["revision"] > nba["revision"]
    seed_lineup("fan", [RECEIVER, dict(RECEIVER, athlete_id="9000005", name="Sample Passer",
                                       slot="QB")])
    nfl3, nba3 = panel_env.snapshot("fan", TEAM_LEAGUE), panel_env.snapshot("fan", NBA_PAIR)
    assert player_ids(nfl3["data"]) == {"9000001", "9000005"}
    assert player_ids(nba3["data"]) == {"9100001", "9100003"}
    assert nfl3["revision"] > nfl2["revision"] and nba3["revision"] >= nba2["revision"]
