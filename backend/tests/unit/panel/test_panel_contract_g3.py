"""G3 wire-contract regressions: served panels must satisfy the TV contract.

M1/M2: legacy stored lineups with >32 starters or blank/duplicate emitted
row identities fail closed with a handled structured error, never HTTP 200.
M3: lineup content changes, a return to earlier content, removal (empty
starters) and re-add each serve a strictly higher revision.
M4: a mixed dated/undated aggregate is never served as fresh.
"""

import pytest

from panel_support import (LEAGUE, PASSER, RECEIVER, TEAM, YAHOO_RECEIVER,
                           YAHOO_UNMAPPED, at, link, panel_env, seed_lineup,
                           seed_profile, statistics)


def starter(i):
    return {"athlete_id": str(9000000 + i), "name": f"Sample {i}", "team": "PHI", "slot": "WR"}


def seed_legacy(panel_env, starters, source="manual"):
    """Write a pre-contract Lineups row directly, bypassing store.put_lineup."""
    row = {"profileId": "fan", "source": source, "team": TEAM, "league": LEAGUE,
           "starters": starters, "updatedAt": at(0)}
    if source == "yahoo":
        row["scoring"] = {"stat_modifiers": {}}
    panel_env.api.table("Lineups").put_item(Item=row)


def test_legacy_33_starters_are_a_structured_panel_error(panel_env):
    seed_profile("fan")
    seed_legacy(panel_env, [starter(i) for i in range(1, 34)])
    with pytest.raises(panel_env.module.InvalidLineupError):
        panel_env.snapshot("fan")
    token = link(panel_env.api, "fan")
    status, body = panel_env.api.request("GET", "/v1/panel", token=token)
    assert status == 503
    assert body["error"]["code"] == "panel_invalid"
    assert body["error"]["message"]


@pytest.mark.parametrize("starters,source", [
    ([dict(YAHOO_UNMAPPED, player_key="")], "yahoo"),
    ([YAHOO_RECEIVER, YAHOO_RECEIVER], "yahoo"),
    ([YAHOO_RECEIVER, dict(YAHOO_RECEIVER, player_key="nfl.p.7002")], "yahoo"),
    ([RECEIVER, RECEIVER], "manual"),
    ([dict(RECEIVER, athlete_id=" ")], "manual"),
])
def test_legacy_blank_or_duplicate_row_identity_is_refused(panel_env, starters, source):
    seed_profile("fan")
    seed_legacy(panel_env, [dict(s) for s in starters], source=source)
    with pytest.raises(panel_env.module.InvalidLineupError):
        panel_env.snapshot("fan")


def test_32_starters_are_served(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [starter(i) for i in range(1, 33)])
    data = panel_env.data("fan")
    assert len(data["rows"]) == 32


def test_revision_strictly_increases_across_change_return_empty_readd(panel_env):
    seed_profile("fan")
    revisions = []
    for starters in ([RECEIVER], [PASSER], [RECEIVER], [], [RECEIVER]):
        seed_lineup("fan", starters)
        revisions.append(panel_env.snapshot("fan")["revision"])
    assert revisions == sorted(revisions) and len(set(revisions)) == len(revisions), revisions
    assert panel_env.snapshot("fan")["revision"] == revisions[-1], "rereads stay stable"


def test_mixed_dated_undated_aggregate_is_never_fresh(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    panel_env.stats["9000001"] = statistics(receptions=2, as_of=at(0))
    undated = statistics(receptions=8)
    undated["asOf"] = None
    panel_env.stats["9000005"] = undated
    data = panel_env.data("fan")
    total = data["teamTotal"]
    assert total["value"] == pytest.approx(5.0)
    assert total["stale"] is True and total["asOf"] is None, total
    progress = data["progress"]
    assert progress["value"] == pytest.approx(0.5)
    assert progress["stale"] is True and progress["asOf"] is None, progress
