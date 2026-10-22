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
