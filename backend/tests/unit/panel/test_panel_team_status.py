"""A starter without stats shows 0.0 with their team game's status; the total
sums what is known; the remote's pair cycle puts live games first (owner, 2026-10-23)."""


NOW = "2026-10-23T00:30:00Z"


def _lineup(store, team, starters, profile="fan"):
    store.put_lineup({"profileId": profile, "source": "manual", "team": team, "league": "demo-nfl",
                      "starters": starters, "updatedAt": "2026-10-22T22:00:00Z"})


def _slate(store, teams):
    store.put_nba_pregame(teams, item_id=store.NFL_STATUS_ID)


def test_no_stats_starter_gets_zero_with_team_game_status_and_total_sums(api, monkeypatch):
    import panel
    import store

    store.put_profile("fan", {}, 0, "2026-10-22T22:00:00Z")
    _lineup(store, "ne-chi-tonight", [
        {"athlete_id": "9200001", "name": "Sample Back", "team": "NE", "positions": ["RB"]},
        {"athlete_id": "9200002", "name": "Sample Passer", "team": "CHI", "positions": ["QB"]},
    ])
    _slate(store, {"NE": "1st 11:30", "CHI": "1st 11:30"})
    assert store.put_player_statistics({
        "athleteId": "9200001", "gameId": "401888001", "gameState": "in",
        "gameStatus": "1st 11:30", "source": "live", "asOf": "2026-10-23T00:29:50Z",
        "stats": {"rushing_yards": 25}})
    monkeypatch.setattr(panel, "now", lambda: NOW)
    data = panel.snapshot("fan", "demo-nfl/ne-chi-tonight")["data"]
    rows = {row["playerId"]: row for row in data["rows"]}
    assert rows["9200002"]["points"]["value"] == 0.0
    assert rows["9200002"]["gameStatus"] == "1st 11:30"
    assert rows["9200001"]["points"]["value"] == 2.5
    assert data["teamTotal"]["value"] == 2.5
    assert data["teamTotal"]["reason"] is None


def test_partial_values_still_total(api, monkeypatch):
    import panel
    import store

    store.put_profile("fan", {}, 0, "2026-10-22T22:00:00Z")
    _lineup(store, "ne-chi-tonight", [
        {"athlete_id": "9200001", "name": "Sample Back", "team": "NE", "positions": ["RB"]},
        {"athlete_id": "9200003", "name": "Sample Idle", "team": "BYE", "positions": ["WR"]},
    ])
    assert store.put_player_statistics({
        "athleteId": "9200001", "gameId": "401888001", "gameState": "in",
        "gameStatus": "1st 11:30", "source": "live", "asOf": "2026-10-23T00:29:50Z",
        "stats": {"rushing_yards": 40}})
    monkeypatch.setattr(panel, "now", lambda: NOW)
    data = panel.snapshot("fan", "demo-nfl/ne-chi-tonight")["data"]
    assert data["teamTotal"]["value"] == 4.0


def test_pairs_cycle_live_then_upcoming_then_final(api, monkeypatch):
    import panel
    import store

    store.put_profile("fan", {}, 0, "2026-10-22T22:00:00Z")
    _lineup(store, "aa-done", [{"athlete_id": "9200011", "name": "A", "team": "BUF", "positions": ["QB"]}])
    _lineup(store, "bb-later", [{"athlete_id": "9200012", "name": "B", "team": "DAL", "positions": ["QB"]}])
    _lineup(store, "cc-live", [{"athlete_id": "9200013", "name": "C", "team": "NE", "positions": ["QB"]}])
    _slate(store, {"BUF": "Final", "DAL": "Kicks 7:15 PM", "NE": "1st 11:30"})
    monkeypatch.setattr(panel, "now", lambda: NOW)
    data = panel.snapshot("fan", "demo-nfl/aa-done")["data"]
    assert data["teamLeagues"] == ["demo-nfl/cc-live", "demo-nfl/bb-later", "demo-nfl/aa-done"]


def test_start_time_is_central(monkeypatch):
    from datetime import date
    import nba.normalize as normalize
    from nba.normalize import team_status_by_team
    monkeypatch.setattr(normalize, "_today", lambda: date(2026, 10, 22))

    game = {"id": "1", "date": "2026-10-23T00:30Z",
            "status": {"type": {"state": "pre", "shortDetail": "10/22 - 8:30 PM EDT"}},
            "competitions": [{"competitors": [{"team": {"abbreviation": "CLE"}},
                                              {"team": {"abbreviation": "PHI"}}]}]}
    assert team_status_by_team([game], "Tips") == {"CLE": "Tips 7:30 PM", "PHI": "Tips 7:30 PM"}


def test_start_on_another_day_names_the_weekday(monkeypatch):
    from datetime import date
    import nba.normalize as normalize
    monkeypatch.setattr(normalize, "_today", lambda: date(2026, 10, 23))
    sunday = {"id": "2", "date": "2026-10-25T17:00Z",
              "status": {"type": {"state": "pre", "shortDetail": "10/25 - 1:00 PM EDT"}},
              "competitions": [{"competitors": [{"team": {"abbreviation": "CIN"}}]}]}
    monday = {"id": "3", "date": "2026-10-27T00:15Z",
              "status": {"type": {"state": "pre", "shortDetail": "10/26 - 8:15 PM EDT"}},
              "competitions": [{"competitors": [{"team": {"abbreviation": "DAL"}}]}]}
    assert normalize.team_status_by_team([sunday, monday], "Kicks") == {"CIN": "Sun 12:00 PM", "DAL": "Mon 7:15 PM"}


def test_nfl_team_missing_from_the_week_slate_reads_bye(api, monkeypatch):
    # Owner 2026-10-23: a starter whose team has no game this week shows "BYE" and 0.0.
    import panel
    import store

    store.put_profile("fan", {}, 0, "2026-10-22T22:00:00Z")
    _lineup(store, "my-lineup", [
        {"athlete_id": "9200011", "name": "Bye Receiver", "team": "GB", "positions": ["WR"]},
        {"athlete_id": "9200012", "name": "Sunday Back", "team": "NE", "positions": ["RB"]},
    ])
    _slate(store, {"NE": "Sun 12:00 PM", "CHI": "Sun 12:00 PM"})
    monkeypatch.setattr(panel, "now", lambda: NOW)
    rows = {row["playerId"]: row for row in panel.snapshot("fan", "demo-nfl/my-lineup")["data"]["rows"]}
    assert rows["9200011"]["gameStatus"] == "BYE"
    assert rows["9200011"]["points"]["value"] == 0.0
    assert rows["9200012"]["gameStatus"] == "Sun 12:00 PM"
