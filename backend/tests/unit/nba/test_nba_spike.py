"""NBA stretch spike (DEC-AFC-NBA-STRETCH-20261020): flag-gated ESPN NBA
ingest, points-league scoring and panel rows. With AFC_ENABLE_NBA off the
NFL behavior is unchanged: the NBA poll never fetches and an nbaPoints
scoring preset is refused exactly like any other unknown preset.
"""

import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "nba"
GAME = "401999101"
GUARD, WING, CENTER = "9100001", "9100002", "9100003"
STARTERS = [
    {"athlete_id": GUARD, "name": "Sample Guard", "team": "SHO", "slot": "PG"},
    {"athlete_id": WING, "name": "Sample Wing", "team": "SHO", "slot": "SF"},
]
# Guard: 20*1 + 9*1.2 + 4*1.5 + 1*3 + 0*3 - 2 = 37.8
# Wing:  12*1 + 5*1.2 + 7*1.5 + 2*3 + 1*3 - 3 = 34.5
GUARD_POINTS, WING_POINTS = 37.8, 34.5


def load(name):
    return json.loads((FIXTURES / name).read_text())


def fresh_summary():
    return copy.deepcopy(load("summary.json"))


# -- flag -------------------------------------------------------------------

def test_flag_defaults_off(monkeypatch):
    import nba

    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    assert nba.enabled() is False
    for value in ("false", "0", "no", "", "off"):
        monkeypatch.setenv("AFC_ENABLE_NBA", value)
        assert nba.enabled() is False, value
    for value in ("true", "1", "yes", "TRUE"):
        monkeypatch.setenv("AFC_ENABLE_NBA", value)
        assert nba.enabled() is True, value


# -- scoring ----------------------------------------------------------------

def test_scoring_table_is_the_named_points_league_basis():
    from nba.scoring import NBA_POINTS_TABLE

    assert NBA_POINTS_TABLE == {"points": 1, "rebounds": 1.2, "assists": 1.5,
                                "steals": 3, "blocks": 3, "turnovers": -1}


def test_score_applies_table_and_missing_stats_count_zero():
    from nba.scoring import score

    stats = {"points": 20, "rebounds": 9, "assists": 4, "steals": 1,
             "blocks": 0, "turnovers": 2}
    assert score(stats) == pytest.approx(GUARD_POINTS)
    assert score({"points": 10}) == pytest.approx(10.0)
    assert score({}) == 0


def test_score_refuses_a_stat_without_a_table_row():
    from nba.scoring import score

    with pytest.raises(ValueError):
        score({"rushing_yards": 80})


# -- ingest -----------------------------------------------------------------

def test_scoreboard_games_describes_each_event():
    from nba.normalize import scoreboard_games

    games = scoreboard_games(load("scoreboard.json"))
    assert games == [{"gameId": GAME, "state": "in",
                      "teamIds": ["901", "SHO", "902", "SAW"],
                      "playerIds": [GUARD]}]


def test_scoreboard_validation_refuses_malformed_bodies():
    from nba.normalize import scoreboard_games

    with pytest.raises(ValueError):
        scoreboard_games({"events": [{"id": "not-numeric"}]})
    with pytest.raises(ValueError):
        scoreboard_games({})


def test_summary_boxscore_maps_only_scoring_stats_as_decimals():
    from nba.normalize import boxscore_statistics_nba

    records = {r["athleteId"]: r for r in boxscore_statistics_nba(fresh_summary(), GAME)}
    assert set(records) == {GUARD, WING, CENTER}
    guard = records[GUARD]
    assert guard["gameId"] == GAME
    assert guard["gameState"] == "in"
    assert guard["gameStatus"] == "10:00 - 3rd"
    assert guard["source"] == "live"
    assert guard["asOf"] == "2026-10-21T00:05:00Z"  # latest play wallclock
    assert guard["stats"] == {"points": Decimal("20"), "rebounds": Decimal("9"),
                              "assists": Decimal("4"), "turnovers": Decimal("2"),
                              "steals": Decimal("1"), "blocks": Decimal("0")}
    assert all(isinstance(v, Decimal) for v in guard["stats"].values())


def test_summary_for_another_game_or_source_is_refused():
    from nba.normalize import boxscore_statistics_nba, validate_nba_summary

    with pytest.raises(ValueError):
        validate_nba_summary(fresh_summary(), "401999999")
    with pytest.raises(ValueError):
        boxscore_statistics_nba(fresh_summary(), GAME, source="fabricated")


def test_summary_skips_invalid_athlete_ids_and_unparseable_stats():
    from nba.normalize import boxscore_statistics_nba

    payload = fresh_summary()
    athletes = payload["boxscore"]["players"][0]["statistics"][0]["athletes"]
    athletes[0]["athlete"]["id"] = "not/an/id"
    athletes[1]["stats"][1] = "many"  # points unparseable: dropped, rest kept
    records = {r["athleteId"]: r for r in boxscore_statistics_nba(payload, GAME)}
    assert set(records) == {WING, CENTER}
    assert "points" not in records[WING]["stats"]
    assert records[WING]["stats"]["rebounds"] == Decimal("5")


def test_poll_with_flag_off_never_fetches(monkeypatch):
    import nba

    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)

    def forbidden(url):
        raise AssertionError(f"NBA poll fetched with the flag off: {url}")

    assert nba.poll(forbidden) == {"stored": 0, "failed": []}


def test_poll_with_flag_on_stores_summary_statistics(monkeypatch):
    import nba

    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    scoreboard, summary = load("scoreboard.json"), fresh_summary()
    urls, stored = [], []

    def get_json(url):
        urls.append(url)
        return scoreboard if url.endswith("scoreboard") else summary

    result = nba.poll(get_json, store_records=stored.extend)
    assert urls == ["https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
                    "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event=" + GAME]
    assert result == {"stored": 3, "failed": []}
    assert {r["athleteId"] for r in stored} == {GUARD, WING, CENTER}


def test_poll_isolates_a_failed_summary(monkeypatch):
    import nba

    monkeypatch.setenv("AFC_ENABLE_NBA", "true")

    def get_json(url):
        if url.endswith("scoreboard"):
            return load("scoreboard.json")
        raise OSError("summary unavailable")

    assert nba.poll(get_json, store_records=lambda records: None) == {
        "stored": 0, "failed": [GAME]}


def test_ingest_summary_scores_each_athlete():
    import nba
    from nba.normalize import boxscore_statistics_nba
    from nba.scoring import score

    points = {r["athleteId"]: score(r["stats"])
              for r in boxscore_statistics_nba(fresh_summary(), GAME)}
    assert points[GUARD] == pytest.approx(GUARD_POINTS)
    assert points[WING] == pytest.approx(WING_POINTS)
    assert nba.FEED == "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/"


# -- feed_ingest hook ---------------------------------------------------------

@pytest.fixture
def nfl_poll(monkeypatch):
    """NFL poll() with an empty monitored set and a spy on the NBA poll."""
    import feed_ingest
    import nba

    calls = []
    monkeypatch.setattr(nba, "poll", lambda get_json, store_records=None:
                        calls.append(get_json) or {"stored": 2, "failed": []})
    monkeypatch.setattr(feed_ingest, "_get_json", lambda url: load("scoreboard.json"))
    monkeypatch.setattr(feed_ingest.store, "monitoring_profiles", lambda: [])
    return feed_ingest, calls


def test_feed_hook_does_not_run_nba_with_flag_off(monkeypatch, nfl_poll):
    feed_ingest, calls = nfl_poll
    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    assert feed_ingest.poll({}) == {"stored": 0, "failed": []}
    assert calls == []


def test_scheduled_handler_runs_nba_poll_with_flag_on(monkeypatch, nfl_poll):
    import nba

    _, calls = nfl_poll
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    result = nba.lambda_handler({}, None)
    assert len(calls) == 1
    assert result["stored"] == 2 and result["failed"] == []


# -- panel rows ---------------------------------------------------------------

@pytest.fixture
def nba_panel(api, monkeypatch):
    """Real panel.snapshot over a synthetic NBA lineup (statistics seam faked)."""
    import panel
    import store

    from nba.normalize import boxscore_statistics_nba

    records = {r["athleteId"]: r for r in boxscore_statistics_nba(fresh_summary(), GAME)}
    records = {aid: {k: r[k] for k in ("gameId", "gameState", "gameStatus", "source", "asOf", "stats")}
               for aid, r in records.items()}
    monkeypatch.setattr(panel, "player_statistics", records.get)
    monkeypatch.setattr(panel, "now", lambda: "2026-10-21T00:05:30Z")
    assert store.put_profile("hoops", {"scoringPreset": "nbaPoints"}, 0,
                             "2026-10-20T22:00:00Z")
    store.put_lineup({"profileId": "hoops", "source": "manual", "team": "team-9",
                      "league": "nba-league", "starters": [dict(s) for s in STARTERS],
                      "updatedAt": "2026-10-20T22:00:00Z"})
    return panel


def test_panel_rows_score_the_nba_lineup_with_flag_on(monkeypatch, nba_panel):
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    data = nba_panel.snapshot("hoops", "nba-league/team-9")["data"]
    assert data["scoringBasis"] == "nbaPoints"
    rows = {r["playerId"]: r for r in data["rows"]}
    assert rows[GUARD]["name"] == "Sample Guard"
    assert rows[GUARD]["points"]["value"] == pytest.approx(GUARD_POINTS, abs=0.005)
    assert rows[WING]["points"]["value"] == pytest.approx(WING_POINTS, abs=0.005)
    assert rows[GUARD]["gameStatus"] == "10:00 - 3rd"
    assert data["teamTotal"]["value"] == pytest.approx(GUARD_POINTS + WING_POINTS, abs=0.005)


def test_panel_refuses_nba_preset_with_flag_off(monkeypatch, nba_panel):
    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    with pytest.raises(ValueError, match="Unknown scoring preset"):
        nba_panel.snapshot("hoops", "nba-league/team-9")
