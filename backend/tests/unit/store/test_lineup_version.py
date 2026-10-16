"""store.put_lineup allocates a monotonic lineupVersion at the write boundary."""

import store


def lineup(starters):
    return {"profileId": "owner", "source": "manual", "team": "T", "league": "L",
            "starters": starters, "updatedAt": "2026-10-18T20:00:00Z"}


A = [{"athlete_id": "1", "name": "A", "team": "PHI", "slot": "WR"}]
B = [{"athlete_id": "2", "name": "B", "team": "PHI", "slot": "QB"}]


def version():
    return store.get_lineup_version("owner")


def test_version_increases_on_change_return_and_empty(api):
    store.put_lineup(lineup(A))
    assert version() == 1
    store.put_lineup(lineup(A))
    assert version() == 1, "an identical rewrite is not a content change"
    store.put_lineup(lineup(B))
    assert version() == 2
    store.put_lineup(lineup(A))
    assert version() == 3, "returning to earlier content still advances"
    store.put_lineup(lineup([]))
    assert version() == 4, "removal (empty starters) keeps a tombstone version"


def test_legacy_row_without_version_is_upgraded_above_zero(api):
    api.table("Lineups").put_item(Item=lineup(A))
    store.put_lineup(lineup(B))
    assert version() == 1
