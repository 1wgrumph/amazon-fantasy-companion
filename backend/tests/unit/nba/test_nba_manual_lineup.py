"""Manual NBA lineup red tests (issue #137, M16 NBA stretch).

The spike's panel tests store a hand-written manual row under an nbaPoints
profile. These cover the builder path: nba.manual.build turns synthetic ESPN
NBA roster entries into a labeled manual lineup with sport "nba", the store
keeps sport, and the panel scores it on nbaPoints with "sport": "nba" even
under a default (NFL halfPpr) profile. With the flag off it cannot be built.
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "nba"
GAME = "401999101"
GUARD, WING, CENTER = "9100001", "9100002", "9100003"
NBA_POINTS = {GUARD: 37.8, WING: 34.5, CENTER: 31.9}
ENTRIES = [{"athlete_id": GUARD, "slot": "PG"}, {"athlete_id": WING, "slot": "SF"},
           {"athlete_id": CENTER, "slot": "C"}]


def load(path):
    return json.loads(path.read_text())


def espn_roster():
    return load(FIXTURES / "yahoo" / "espn_roster.json")


def build(*args):
    import importlib

    try:
        module = importlib.import_module("nba.manual")
    except ImportError as exc:
        raise AssertionError(f"NBA manual lineup is not implemented: {exc}") from None
    return module.build(*args)


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


def test_build_labels_a_manual_nba_lineup(monkeypatch):
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    lineup = build(espn_roster(), ENTRIES)
    assert lineup["source"] == "manual"
    assert lineup["sport"] == "nba"
    assert lineup["starters"] == [
        {"athlete_id": GUARD, "name": "Sample Guard", "team": "SHO", "slot": "PG"},
        {"athlete_id": WING, "name": "Sample Wing", "team": "SHO", "slot": "SF"},
        {"athlete_id": CENTER, "name": "Sample Center", "team": "SAW", "slot": "C"}]


@pytest.mark.parametrize("entries", [
    [{"athlete_id": "9100999", "slot": "PG"}],                  # not on the ESPN roster
    [{"athlete_id": GUARD, "slot": "PG"}, {"athlete_id": GUARD, "slot": "G"}],  # twice
    [{"athlete_id": GUARD, "slot": ""}],                        # no slot
])
def test_build_refuses_invalid_entries(monkeypatch, entries):
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    with pytest.raises(ValueError):
        build(espn_roster(), entries)


def test_build_is_refused_with_the_flag_off(monkeypatch):
    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    with pytest.raises(ValueError):
        build(espn_roster(), ENTRIES)


def test_manual_nba_lineup_scores_on_nba_points_under_a_default_profile(monkeypatch, nba_panel):
    store, panel = nba_panel
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    store.put_lineup(dict(build(espn_roster(), ENTRIES), profileId="hoops", team="team-9",
                          league="nba-league", updatedAt="2026-10-20T22:00:00Z"))
    assert store.get_lineup("hoops")["sport"] == "nba"
    data = panel.snapshot("hoops", "nba-league/team-9")["data"]
    assert data["scoringBasis"] == "nbaPoints"
    assert data["sport"] == "nba"
    got = {r["playerId"]: r for r in data["rows"]}
    for athlete, expected in NBA_POINTS.items():
        assert got[athlete]["points"]["value"] == pytest.approx(expected, abs=0.005)
    assert got[CENTER]["gameStatus"] == "10:00 - 3rd"
    assert data["teamTotal"]["value"] == pytest.approx(sum(NBA_POINTS.values()), abs=0.005)
