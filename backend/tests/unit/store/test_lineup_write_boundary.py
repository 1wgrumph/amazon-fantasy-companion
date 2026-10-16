"""Lineup write races, write-boundary row checks and strongly consistent panel reads."""

import pytest

import panel
import store


def lineup(starters, source="manual"):
    return {"profileId": "owner", "source": source, "team": "T", "league": "L",
            "starters": starters, "updatedAt": "2026-10-18T20:00:00Z"}


def starter(athlete_id):
    return {"athlete_id": athlete_id, "name": "P" + athlete_id, "team": "PHI", "slot": "WR"}


A, B, C = [starter("1")], [starter("2")], [starter("3")]


def competing_writer(monkeypatch, *rivals):
    """Run one rival put_lineup between put_lineup's read and its conditional write."""
    read = store._lineup_row
    pending = list(rivals)

    def racing_read(profile_id):
        row = read(profile_id)
        if pending:
            rival = pending.pop(0)
            monkeypatch.setattr(store, "_lineup_row", read)
            rival()
            monkeypatch.setattr(store, "_lineup_row", racing_read)
        return row

    monkeypatch.setattr(store, "_lineup_row", racing_read)


def test_concurrent_writer_never_reuses_a_version(api, monkeypatch):
    store.put_lineup(lineup(A))
    competing_writer(monkeypatch, lambda: store.put_lineup(lineup(B)))
    store.put_lineup(lineup(C))
    assert store.get_lineup_with_version("owner") == (lineup(C), 3)


def test_concurrent_writer_on_a_legacy_row_upgrades_to_one_then_two(api, monkeypatch):
    api.table("Lineups").put_item(Item=lineup(A))
    competing_writer(monkeypatch, lambda: store.put_lineup(lineup(B)))
    store.put_lineup(lineup(C))
    assert store.get_lineup_with_version("owner") == (lineup(C), 2)


def test_concurrent_first_writers_both_land(api, monkeypatch):
    competing_writer(monkeypatch, lambda: store.put_lineup(lineup(B)))
    store.put_lineup(lineup(C))
    assert store.get_lineup_with_version("owner") == (lineup(C), 2)


def test_writer_that_loses_three_races_raises_without_overwriting(api, monkeypatch):
    store.put_lineup(lineup(A))
    competing_writer(monkeypatch, *[lambda s=s: store.put_lineup(lineup(s)) for s in (B, A, B)])
    with pytest.raises(RuntimeError, match="kept losing races"):
        store.put_lineup(lineup(C))
    assert store.get_lineup_with_version("owner") == (lineup(B), 4)


@pytest.mark.parametrize("starters,source", [
    ([starter(str(i)) for i in range(33)], "manual"),
    ([starter("1"), starter("1")], "manual"),
    ([starter(" ")], "manual"),
    ([{"name": "No id", "slot": "WR"}], "manual"),
    (["1"], "manual"),
    ({"athlete_id": "1"}, "manual"),
    ([{"player_key": "p.1"}, {"player_key": "p.1"}], "yahoo"),
    ([{"player_key": ""}], "yahoo"),
    ([starter("1")], "yahoo"),
])
def test_put_lineup_rejects_rows_the_panel_cannot_serve(api, starters, source):
    with pytest.raises(ValueError):
        store.put_lineup(lineup(starters, source))
    assert store.get_lineup_with_version("owner") == (None, 0)


def test_put_lineup_accepts_the_32_starter_bound_and_tombstones(api):
    store.put_lineup(lineup([starter(str(i)) for i in range(32)]))
    store.put_lineup(lineup([{"player_key": f"p.{i}"} for i in range(32)], "yahoo"))
    store.put_lineup({"profileId": "owner"})
    assert store.get_lineup_with_version("owner") == (None, 3)


def test_snapshot_fails_closed_on_an_oversized_legacy_row_before_reading_statistics(
        api, monkeypatch):
    api.table("Lineups").put_item(Item=lineup([starter(str(i)) for i in range(200)]))
    reads = []
    monkeypatch.setattr(panel, "player_statistics", lambda athlete: reads.append(athlete))
    with pytest.raises(panel.InvalidLineupError):
        panel.snapshot("owner", "L/T")
    assert reads == []


def test_panel_snapshot_reads_are_strongly_consistent(api, monkeypatch):
    store.put_lineup(lineup(A))
    calls = []
    table = store._table

    class Recording:
        def __init__(self, inner, name):
            self.inner, self.name = inner, name

        def get_item(self, **request):
            calls.append((self.name, request.get("ConsistentRead")))
            return self.inner.get_item(**request)

        def __getattr__(self, attr):
            return getattr(self.inner, attr)

    monkeypatch.setattr(store, "_table", lambda variable: Recording(table(variable), variable))
    panel.snapshot("owner", None)
    store.put_lineup(lineup(B))
    names = {name for name, _ in calls}
    assert {"PROFILES_TABLE", "LINEUPS_TABLE", "PANELS_TABLE"} <= names
    assert all(consistent is True for name, consistent in calls
               if name in {"PROFILES_TABLE", "LINEUPS_TABLE", "PANELS_TABLE"}), calls
