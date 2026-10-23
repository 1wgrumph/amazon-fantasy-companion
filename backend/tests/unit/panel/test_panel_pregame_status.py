"""GET /v1/panel shows the ESPN pregame text for an NBA starter with no stats.

Points are 0.0 with that status, a team with no game today stays blank, and an NFL
row never reads the NBA slate. A stored statistics record still wins.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

TIP = "10/21 - 10:00 PM EDT"
NOW = "2026-10-22T01:30:00Z"
PAIR = "nba-league/team-9"


def _stamp(hours_before):
    moment = datetime(2026, 10, 22, 1, 30, tzinfo=timezone.utc) - timedelta(hours=hours_before)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _slate(api, teams, hours_before=0.5):
    api.table("PlayerStats").put_item(Item={
        "athleteId": "pregame", "asOf": _stamp(hours_before), "teams": teams})


def _lineup(store, starters, *, sport=None, profile="hoops", league="nba-league"):
    store.put_profile(profile, {}, 0, "2026-10-21T22:00:00Z")
    row = {"profileId": profile, "source": "manual", "team": "team-9", "league": league,
           "starters": starters, "updatedAt": "2026-10-21T22:00:00Z"}
    if sport is not None:
        row["sport"] = sport
    store.put_lineup(row)


def _snapshot(monkeypatch, profile="hoops", team_league=PAIR):
    import panel

    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    monkeypatch.setattr(panel, "now", lambda: NOW)
    return panel.snapshot(profile, team_league)["data"]


def test_unstarted_nba_starter_shows_pregame_status_with_zero_points(api, monkeypatch):
    import store

    _lineup(store, [
        {"athlete_id": "9100001", "name": "Sample Guard", "team": "GS", "slot": "PG"},
        {"athlete_id": "9100009", "name": "Sample Idle", "team": "BOS", "slot": "PG"},
    ], sport="nba")
    _slate(api, {"GS": TIP, "LAL": TIP})
    data = _snapshot(monkeypatch)
    rows = {row["playerId"]: row for row in data["rows"]}
    # Owner design 2026-10-23: a starter whose team game has a status shows 0.0 with it;
    # a team with no game today stays unknown, and the total sums what is known.
    assert rows["9100001"]["gameStatus"] == TIP
    assert rows["9100001"]["points"]["value"] == 0.0
    assert rows["9100001"]["points"]["reason"] is None
    assert rows["9100009"]["gameStatus"] is None
    assert rows["9100009"]["points"]["value"] is None
    assert data["teamTotal"]["value"] == 0.0
    assert data["teamTotal"]["reason"] == "partial total"
    assert data["progress"]["value"] is None


def test_stale_pregame_slate_leaves_game_status_blank(api, monkeypatch):
    import store

    _lineup(store, [
        {"athlete_id": "9100001", "name": "Sample Guard", "team": "GS", "slot": "PG"},
    ], sport="nba")
    _slate(api, {"GS": TIP}, hours_before=13)
    data = _snapshot(monkeypatch)
    assert data["rows"][0]["gameStatus"] is None


def test_statistics_record_wins_over_pregame_status(api, monkeypatch):
    import store

    _lineup(store, [
        {"athlete_id": "9100001", "name": "Sample Guard", "team": "GS", "slot": "PG"},
    ], sport="nba")
    _slate(api, {"GS": TIP})
    assert store.put_player_statistics({
        "athleteId": "9100001", "gameId": "401999101", "gameState": "in",
        "gameStatus": "Q1 10:00", "source": "live", "asOf": NOW,
        "stats": {"points": Decimal("2")}})
    data = _snapshot(monkeypatch)
    assert data["rows"][0]["gameStatus"] == "Q1 10:00"
    assert data["rows"][0]["points"]["value"] == 2


def test_nfl_row_ignores_the_nba_pregame_slate(api, monkeypatch):
    import store

    _lineup(store, [
        {"athlete_id": "9000001", "name": "Sample Receiver", "team": "GS", "slot": "WR"},
    ], profile="fan", league="nfl-league")
    _slate(api, {"GS": TIP})
    data = _snapshot(monkeypatch, profile="fan", team_league="nfl-league/team-9")
    assert data["rows"][0]["gameStatus"] is None
    assert "sport" not in data


def test_pregame_changes_and_clear_advance_revision_without_other_writes(api, monkeypatch):
    import panel
    import store

    _lineup(store, [{"athlete_id": "9100001", "name": "Sample Guard", "team": "GS", "slot": "PG"}], sport="nba")
    _snapshot(monkeypatch)
    read = lambda: panel.snapshot("hoops", PAIR)
    before = read()
    for teams, status in [({"GS": TIP}, TIP), ({"GS": "new tip"}, "new tip"), ({}, None)]:
        assert store.put_nba_pregame(teams)
        after = read()
        assert after["data"]["rows"][0]["gameStatus"] == status
        assert after["revision"] > before["revision"]
        assert read()["revision"] == after["revision"]
        before = after


def test_pregame_expiration_and_refresh_never_regress_revision(api, monkeypatch):
    import panel
    import store

    _lineup(store, [{"athlete_id": "9100001", "name": "Sample Guard", "team": "GS", "slot": "PG"}], sport="nba")
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    assert store.put_nba_pregame({"GS": TIP})
    stamp = store.get_nba_pregame()["asOf"]
    moment = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    monkeypatch.setattr(panel, "now", lambda: stamp)
    fresh = panel.snapshot("hoops", PAIR)
    expired_at = moment + timedelta(hours=13)
    monkeypatch.setattr(panel, "now", lambda: expired_at.isoformat())
    expired = panel.snapshot("hoops", PAIR)
    assert expired["data"]["rows"][0]["gameStatus"] is None
    assert expired["revision"] > fresh["revision"]
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return expired_at
    monkeypatch.setattr(store, "datetime", Clock)
    assert store.put_nba_pregame({"GS": TIP})
    refreshed = panel.snapshot("hoops", PAIR)
    assert refreshed["data"]["rows"][0]["gameStatus"] == TIP
    assert refreshed["revision"] > expired["revision"]
