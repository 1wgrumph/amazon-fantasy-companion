"""Pregame content revisions are allocated by the real DynamoDB protocol (Moto)."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from botocore.client import BaseClient


def test_pregame_sequence_changes_only_with_content_and_never_reuses_a_value(api):
    import store

    sequences = []
    for teams in [{"GS": "tip"}, {"GS": "tip"}, {}, {}, {"GS": "tip"}]:
        assert store.put_nba_pregame(teams)
        item = store.get_nba_pregame()
        assert item["teams"] == teams
        sequences.append(item["sequence"])
    assert sequences == [1, 1, 2, 2, 3]


def test_pregame_reads_are_strongly_consistent(api, monkeypatch):
    import store

    observed = []
    original = BaseClient._make_api_call
    def observe(client, operation, params):
        if operation == "GetItem" and params["TableName"] == api.table("PlayerStats").name:
            observed.append(params.get("ConsistentRead"))
        return original(client, operation, params)
    monkeypatch.setattr(BaseClient, "_make_api_call", observe)
    assert store.put_nba_pregame({})
    assert store.get_nba_pregame()["teams"] == {}
    assert observed == [True]


def test_invalid_slate_does_not_clear_the_current_content(api):
    import store

    assert store.put_nba_pregame({"GS": "tip"})
    assert store.put_nba_pregame({"bad-team": "tip"}) is False
    assert store.put_nba_pregame(None) is False
    assert store.get_nba_pregame()["teams"] == {"GS": "tip"}


def test_legacy_slate_is_upgraded_without_resetting_content(api):
    import store

    api.table("PlayerStats").put_item(Item={"athleteId": "pregame", "teams": {"GS": "tip"},
                                           "asOf": "2026-10-22T00:00:00Z"})
    assert store.put_nba_pregame({"GS": "tip"})
    assert store.get_nba_pregame()["sequence"] == 1
    assert store.get_nba_pregame()["teams"] == {"GS": "tip"}


def test_concurrent_different_slate_writes_have_distinct_sequences(api, monkeypatch):
    import store

    assert store.put_nba_pregame({})
    table = api.table("PlayerStats")
    original = table.put_item
    barrier = Barrier(2)
    def collide(**kwargs):
        if kwargs["Item"]["teams"] and kwargs["Item"].get("sequence", 1) in (1, 2):
            barrier.wait(timeout=10)
        return original(**kwargs)
    monkeypatch.setattr(table, "put_item", collide)
    monkeypatch.setattr(store, "_table", lambda *args: table)
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert all(pool.map(store.put_nba_pregame, [{"GS": "tip"}, {"LAL": "tip"}]))
    assert store.get_nba_pregame()["sequence"] == 3
