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


@pytest.mark.parametrize("as_of", ["2026-10-11T17:00:00Z", None])
def test_content_sequence_changes_only_with_stored_content(api, store_mod, as_of):
    record = _record(asOf=as_of)
    assert store_mod.put_player_statistics(record)
    first = store_mod.get_player_statistics(record["athleteId"])
    assert first["statsVersion"] == 1
    assert not store_mod.put_player_statistics(record)
    assert store_mod.get_player_statistics(record["athleteId"]) == first
    record["stats"] = {"passing_yards": Decimal("300")}
    assert store_mod.put_player_statistics(record)
    assert store_mod.get_player_statistics(record["athleteId"])["statsVersion"] == 2
    record["gameStatus"] = "Halftime"
    assert store_mod.put_player_statistics(record)
    assert store_mod.get_player_statistics(record["athleteId"])["statsVersion"] == 3


def test_sequence_upgrades_legacy_and_rejects_stale_or_replay(api, store_mod):
    record = _record()
    api.table("PlayerStats").put_item(Item=record)
    changed = dict(record, gameStatus="Halftime")
    assert store_mod.put_player_statistics(changed)
    assert store_mod.get_player_statistics(record["athleteId"])["statsVersion"] == 1
    assert not store_mod.put_player_statistics(dict(changed, asOf="2026-10-11T16:00:00Z"))
    assert not store_mod.put_player_statistics(dict(changed, source="replay"))
    assert not store_mod.put_player_statistics(dict(changed, asOf=None))
    assert store_mod.get_player_statistics(record["athleteId"])["statsVersion"] == 1


def test_competing_content_writes_allocate_distinct_sequences_with_put_only(api, store_mod, monkeypatch):
    from botocore.client import BaseClient
    import os
    record = _record()
    assert store_mod.put_player_statistics(record)
    real_call = BaseClient._make_api_call
    operations = []
    injected = False

    def competing_write(client, operation, params):
        nonlocal injected
        if params.get("TableName") == os.environ["PLAYER_STATS_TABLE"]:
            operations.append(operation)
            if operation == "PutItem" and params["Item"].get("statsVersion") == 2 and not injected:
                injected = True
                assert store_mod.put_player_statistics(dict(record, gameStatus="Halftime"))
        return real_call(client, operation, params)

    monkeypatch.setattr(BaseClient, "_make_api_call", competing_write)
    assert store_mod.put_player_statistics(dict(record, stats={"passing_yards": Decimal("300")}))
    assert injected
    assert set(operations) == {"PutItem"}, "both ingest IAM roles grant only PutItem on this table"
    final = store_mod.get_player_statistics(record["athleteId"])
    assert final["statsVersion"] == 3
    assert final["stats"]["passing_yards"] == 300


def test_sequence_exhaustion_preserves_the_last_record(api, store_mod):
    record = dict(_record(), statsVersion=(1 << 24) - 1)
    api.table("PlayerStats").put_item(Item=record)
    assert not store_mod.put_player_statistics(_record())
    with pytest.raises(RuntimeError, match="sequence exhausted"):
        store_mod.put_player_statistics(_record(gameStatus="Halftime"))
    assert store_mod.get_player_statistics(record["athleteId"]) == record


def test_store_errors_other_than_a_conditional_race_propagate(api, store_mod, monkeypatch):
    from botocore.client import BaseClient
    from botocore.exceptions import ClientError

    def unavailable(client, operation, params):
        raise ClientError({"Error": {"Code": "AccessDeniedException", "Message": "test denial"}}, operation)

    monkeypatch.setattr(BaseClient, "_make_api_call", unavailable)
    with pytest.raises(ClientError, match="AccessDeniedException"):
        store_mod.put_player_statistics(_record())


@pytest.mark.parametrize("nba_first", [False, True])
def test_generic_and_nba_writers_share_one_cas_sequence(api, store_mod, monkeypatch, nba_first):
    from botocore.client import BaseClient

    record = _record(stats={"points": Decimal("0")})
    assert store_mod.put_nba_statistics(record)
    real_call = BaseClient._make_api_call
    injected = False
    writer = store_mod.put_nba_statistics if nba_first else store_mod.put_player_statistics
    competitor = store_mod.put_player_statistics if nba_first else store_mod.put_nba_statistics

    def collide(client, operation, params):
        nonlocal injected
        candidate = (params["TransactItems"][0]["Put"]["Item"]
                     if operation == "TransactWriteItems" else params.get("Item", {}))
        if candidate.get("statsVersion") == 2 and not injected:
            injected = True
            assert competitor(dict(record, stats={"points": Decimal("5")}))
        return real_call(client, operation, params)

    monkeypatch.setattr(BaseClient, "_make_api_call", collide)
    assert writer(dict(record, stats={"points": Decimal("7")}))
    assert injected
    accepted = store_mod.get_player_statistics(record["athleteId"])
    assert accepted["statsVersion"] == 3
    assert accepted["stats"]["points"] == 7
    assert accepted["nbaMilestones"] == []
    events = api.table("Events").scan()["Items"]
    assert [event["matchup"] for event in events] == ([] if nba_first else ["+5 fantasy pts"])
    if events:
        assert events[0]["eventId"] == f'{record["gameId"]}00000002{record["athleteId"]}05'


def test_nba_sequence_exhaustion_preserves_statistics_and_events(api, store_mod):
    record = _record(stats={"points": Decimal("9")})
    stored = dict(record, statsVersion=(1 << 24) - 1, nbaMilestones=[])
    api.table("PlayerStats").put_item(Item=stored)
    assert not store_mod.put_nba_statistics(record)
    with pytest.raises(RuntimeError, match="sequence exhausted"):
        store_mod.put_nba_statistics(dict(record, stats={"points": Decimal("14")}))
    assert store_mod.get_player_statistics(record["athleteId"]) == stored
    assert api.table("Events").scan()["Items"] == []


def test_generic_correction_retains_consumed_nba_milestones(api, store_mod):
    record = _record(stats={"points": Decimal("9")})
    assert store_mod.put_nba_statistics(record)
    high = dict(record, stats={"points": Decimal("10")})
    assert store_mod.put_nba_statistics(high)
    [event] = api.table("Events").scan()["Items"]
    assert store_mod.put_player_statistics(record)
    assert store_mod.get_player_statistics(record["athleteId"])["nbaMilestones"] == ["10"]
    assert store_mod.put_nba_statistics(high)
    assert store_mod.get_player_statistics(record["athleteId"])["statsVersion"] == 4
    assert api.table("Events").scan()["Items"] == [event]


def test_nba_transaction_advances_the_merged_panel_revision(api, store_mod, monkeypatch):
    import panel
    from panel_support import LEAGUE, TEAM, at, seed_profile

    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    monkeypatch.setattr(panel, "now", lambda: at(5))
    seed_profile("fan")
    store_mod.put_lineup({"profileId": "fan", "source": "manual", "sport": "nba",
                          "team": TEAM, "league": LEAGUE, "updatedAt": at(0),
                          "starters": [{"athlete_id": "4040715", "name": "Guard",
                                        "team": "MIN", "slot": "PG"}]})
    assert store_mod.put_nba_pregame({"MIN": "tip"})
    slate = store_mod.get_nba_pregame()
    record = _record(stats={"points": Decimal("0")}, asOf=at(1))
    assert store_mod.put_nba_statistics(record)
    previous = panel.snapshot("fan", None)
    for version, points in enumerate((5, 0, 5), start=2):
        current = dict(record, stats={"points": Decimal(points)})
        assert store_mod.put_nba_statistics(current)
        assert store_mod.get_player_statistics(record["athleteId"])["statsVersion"] == version
        snapshot = panel.snapshot("fan", None)
        assert snapshot["revision"] > previous["revision"]
        assert snapshot["data"]["rows"][0]["points"]["value"] == points
        assert not store_mod.put_nba_statistics(current)
        assert panel.snapshot("fan", None) == snapshot
        previous = snapshot
    assert store_mod.get_nba_pregame() == slate
