"""Unit tests for store.put_player_statistics key validation and isolation."""

from decimal import Decimal

import pytest


@pytest.fixture
def store_mod(api):
    import store
    return store


def _record(athlete_id="4040715", **overrides):
    base = {
        "athleteId": athlete_id,
        "gameId": "401872981",
        "gameState": "in",
        "gameStatus": "Q2 05:00",
        "source": "live",
        "asOf": "2026-10-11T17:00:00Z",
        "stats": {"passing_yards": Decimal("220")},
    }
    base.update(overrides)
    return base


@pytest.mark.parametrize("bad_id", [
    "",
    "9" * 2049,
    "9" * 21,
    "4040715a",
    "../4040715",
    " 4040715",
    "\uff11",
    None,
    4040715,
])
def test_put_player_statistics_skips_and_logs_invalid_athlete_id(api, store_mod, caplog, bad_id):
    with caplog.at_level("WARNING", logger="store"):
        result = store_mod.put_player_statistics(_record(athlete_id=bad_id))
    assert result is False
    assert api.table("PlayerStats").scan()["Items"] == []
    assert any("athleteId" in rec.getMessage() for rec in caplog.records)


def test_put_player_statistics_accepts_valid_and_boundary_athlete_ids(api, store_mod):
    boundary_id = "9" * 20
    assert store_mod.put_player_statistics(_record(athlete_id=boundary_id)) is True
    assert store_mod.get_player_statistics(boundary_id)["athleteId"] == boundary_id
    assert store_mod.put_player_statistics(_record(athlete_id="1")) is True
    assert store_mod.get_player_statistics("1")["athleteId"] == "1"


def test_put_player_statistics_rejects_unknown_attributes(store_mod):
    with pytest.raises(ValueError, match="Unknown item attributes: extra"):
        store_mod.put_player_statistics(_record(extra="nope"))


def test_nba_transaction_advances_an_existing_statistics_version(api, store_mod):
    previous = _record(stats={"points": Decimal("10")})
    api.table("PlayerStats").put_item(Item=dict(previous, statsVersion=27))
    current = dict(previous, stats={"points": Decimal("15")}, asOf="2026-10-11T17:00:01Z")
    assert store_mod.put_nba_statistics(current)
    accepted = store_mod.get_player_statistics(previous["athleteId"])
    assert accepted["statsVersion"] == 28
    assert accepted["nbaMilestones"] == ["10"]
    events = api.table("Events").scan()["Items"]
    assert len(events) == 1
    assert events[0]["matchup"] == "+5 fantasy pts"
    assert events[0]["eventId"] == f'{previous["gameId"]}00000028{previous["athleteId"]}05'


def test_nba_statistics_never_overwrites_the_reserved_pregame_item(api, store_mod):
    reserved = {"athleteId": "pregame", "teams": {"SHO": "Starts soon"}, "sequence": 3}
    api.table("PlayerStats").put_item(Item=reserved)
    assert store_mod.put_nba_statistics(_record(athlete_id="pregame")) is False
    assert store_mod.get_player_statistics("pregame") == reserved
    assert api.table("Events").scan()["Items"] == []


def test_versioned_nba_alert_keeps_watch_channel_for_maximum_athlete_id(api, store_mod):
    import provider_resolver
    previous = _record(athlete_id="9" * 20, stats={"points": Decimal("0")})
    assert store_mod.put_nba_statistics(previous, channel="ESPN")
    current = dict(previous, stats={"points": Decimal("5")}, asOf="2026-10-11T17:00:01Z")
    assert store_mod.put_nba_statistics(current, channel="ESPN")
    [event] = api.table("Events").scan()["Items"]
    assert provider_resolver.event_channel(event["eventId"]) == "ESPN"
