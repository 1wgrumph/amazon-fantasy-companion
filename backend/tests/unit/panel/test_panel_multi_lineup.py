"""Panels per pair for a profile holding NFL and NBA lineups (multisport arch-review 3, 5, 7).

project() writes only to pairs whose lineup sport (default nfl) equals the
event sport (default nfl). snapshot() for a pair shows only that pair's
rows, and a pair's revision never drops across writes to either pair.
"""

import pytest
import panel_support

from panel_support import (LEAGUE, RECEIVER, TEAM, TEAM_LEAGUE, at,  # noqa: F401
                           game_event, match, panel_env, player_ids, seed_lineup,
                           seed_profile, update_profile)

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


def test_nfl_event_projects_only_to_the_nfl_pair(panel_env, monkeypatch):
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
    monkeypatch.setattr(panel_support, "BASES", (*panel_support.BASES, "nbaPoints"))
    nba = panel_env.data("fan", NBA_PAIR)
    assert nba["scoringBasis"] == "nbaPoints"
    assert set(nba["games"]) == {"401999101"}, \
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


def test_every_pair_snapshot_lists_all_the_profile_pairs(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    nfl_only = panel_env.snapshot("fan", TEAM_LEAGUE)
    assert nfl_only["data"]["teamLeagues"] == [TEAM_LEAGUE]
    seed_nba([GUARD])
    both = sorted([TEAM_LEAGUE, NBA_PAIR])
    for pair in (TEAM_LEAGUE, NBA_PAIR, None):
        assert panel_env.snapshot("fan", pair)["data"]["teamLeagues"] == both


def test_default_uses_settings_then_sole_pair_then_unassigned(panel_env):
    import store

    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    assert panel_env.snapshot("fan")["data"]["teamLeague"] == TEAM_LEAGUE
    seed_nba([GUARD])
    before = panel_env.snapshot("fan")
    assert before["data"]["teamLeague"] == "unassigned/unassigned"
    version = store.get_lineup_version("fan")
    seed_lineup("fan", [RECEIVER])
    assert store.get_lineup_version("fan") == version
    assert panel_env.snapshot("fan") == before
    for league, team in ((LEAGUE, TEAM), (NBA_LEAGUE, NBA_TEAM)):
        update_profile("fan", teamLeague={"league": league, "team": team})
        assert panel_env.snapshot("fan")["data"]["teamLeague"] == f"{league}/{team}"


@pytest.mark.parametrize("legacy", [True, False], ids=["legacy", "map"])
@pytest.mark.parametrize("selection", ["query", "settings"])
def test_sole_nfl_yahoo_absent_pair_keeps_entire_envelope(panel_env, monkeypatch, legacy, selection):
    from decimal import Decimal

    pair = "missing/team"
    seed_profile("fan", **({"teamLeague": {"league": "missing", "team": "team"}}
                           if selection == "settings" else {}))
    entry = {"source": "yahoo", "league": LEAGUE, "team": TEAM,
             "starters": [{"player_key": "nfl.p.7001", "name": "Sample Receiver",
                           "team": "PHI", "positions": ["WR"], "slot": "WR"}],
             "scoring": {"stat_modifiers": {"receptions": Decimal("1.5")}},
             "updatedAt": at(0)}
    row = {"profileId": "fan", "lineupVersion": 2}
    row.update(entry if legacy else {"lineups": {TEAM_LEAGUE: entry}})
    panel_env.api.table("Lineups").put_item(Item=row)
    reads = []
    monkeypatch.setattr(panel_env.module, "player_statistics", lambda athlete: reads.append(athlete))
    result = panel_env.snapshot("fan", pair if selection == "query" else None)
    unknown = {"value": None, "source": None, "asOf": None, "stale": True}
    assert result == {
        "schemaVersion": 1, "id": f"panel/fan/{pair}",
        "revision": 128 * (1 + 3 * panel_env.module.LINEUP_REVISION_SCALE),
        "source": "yahoo", "updatedAt": at(5),
        "data": {"teamLeague": pair, "teamLeagues": [TEAM_LEAGUE],
                 "scoringBasis": "yahooLeague", "visible": True,
                 "rows": [], "games": {},
                 "teamTotal": dict(unknown, reason="no lineup for this team/league"),
                 "progress": dict(unknown, reason="game progress unavailable")},
    }
    assert reads == [], "an absent pair never reads another pair's statistics"
