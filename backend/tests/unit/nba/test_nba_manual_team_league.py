"""Manual NBA builder output renders for a matching teamLeague (#137).

The lineup stored here is what nba.manual.build returns, plus the store
fields profileId and updatedAt. Nothing after build() adds league or team.
A profile whose selected teamLeague equals that pair gets NBA panel rows.
A different pair keeps the empty "no lineup for this team/league" panel.
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "nba"
GAME = "401999101"
GUARD, WING, CENTER = "9100001", "9100002", "9100003"
LEAGUE, TEAM = "nba-demo", "afc-nba"
PAIR = f"{LEAGUE}/{TEAM}"
OTHER = "other-league/other-team"
WHEN = "2026-10-21T13:45:00Z"
NBA_POINTS = {GUARD: 37.8, WING: 34.5, CENTER: 31.9}
ENTRIES = [{"athlete_id": GUARD, "slot": "PG"}, {"athlete_id": WING, "slot": "SF"},
           {"athlete_id": CENTER, "slot": "C"}]


def load(path):
    return json.loads(path.read_text())


def espn_roster():
    return load(FIXTURES / "yahoo" / "espn_roster.json")


@pytest.fixture
def nba_panel(api, monkeypatch):
    import panel
    import store
    from nba.normalize import boxscore_statistics_nba

    records = {r["athleteId"]: {k: r[k] for k in ("gameId", "gameState", "gameStatus",
                                                   "source", "asOf", "stats")}
               for r in boxscore_statistics_nba(load(FIXTURES / "summary.json"), GAME)}
    monkeypatch.setattr(panel, "player_statistics", records.get)
    monkeypatch.setattr(panel, "now", lambda: "2026-10-21T00:05:30Z")
    return store, panel


def test_builder_lineup_renders_for_the_matching_team_league(monkeypatch, nba_panel):
    import nba.manual as manual

    store, panel = nba_panel
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    lineup = manual.build(espn_roster(), ENTRIES, league=LEAGUE, team=TEAM)
    assert lineup["source"] == "manual"
    assert lineup["sport"] == "nba"
    assert lineup["league"] == LEAGUE
    assert lineup["team"] == TEAM
    assert lineup["starters"][0]["team"] == "SHO"
    row = dict(lineup, profileId="hoops", updatedAt=WHEN)
    assert set(row) - set(lineup) == {"profileId", "updatedAt"}
    assert store.put_profile("hoops", {
        "scoringPreset": "halfPpr",
        "teamLeague": {"league": LEAGUE, "team": TEAM},
    }, 0, WHEN)
    store.put_lineup(row)

    for selected in (None, PAIR):
        matched = panel.snapshot("hoops", selected)["data"]
        assert matched["teamLeague"] == PAIR
        assert matched["sport"] == "nba"
        assert matched["scoringBasis"] == "nbaPoints"
        got = {item["playerId"]: item for item in matched["rows"]}
        assert set(got) == set(NBA_POINTS)
        for athlete, expected in NBA_POINTS.items():
            assert got[athlete]["points"]["value"] == pytest.approx(expected, abs=0.005)
        assert got[CENTER]["gameStatus"] == "10:00 - 3rd"

    other = panel.snapshot("hoops", OTHER)["data"]
    assert other["teamLeague"] == OTHER
    assert other["rows"] == []
    assert other["teamTotal"]["value"] is None
    assert other["teamTotal"]["reason"] == "no lineup for this team/league"


@pytest.mark.parametrize("league,team", [
    ("nba-demo", None),
    (None, "afc-nba"),
    ("", "afc-nba"),
    ("nba-demo", ""),
    (1, "afc-nba"),
    ("nba-demo", 1),
])
def test_build_refuses_a_partial_team_league(monkeypatch, league, team):
    import nba.manual as manual

    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    with pytest.raises(ValueError, match="league and a team"):
        manual.build(espn_roster(), ENTRIES, league=league, team=team)


def test_build_with_team_league_is_refused_when_nba_is_off(monkeypatch):
    import nba.manual as manual

    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    with pytest.raises(ValueError, match="disabled"):
        manual.build(espn_roster(), ENTRIES, league=LEAGUE, team=TEAM)
