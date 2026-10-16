"""P2-B07 repair regressions: B07-R01 and B07-R02 from independent review.

R01: a starter change with no new play must still raise the snapshot
revision, or the TV discards the changed rows as already consumed.
R02: overlapping projections of different games for one panel must both
survive; a lost conditional-write race re-reads and merges.
"""

from panel_support import (GAME, OTHER_GAME, PASSER, RECEIVER, TEAM_LEAGUE,
                           game_event, match, panel_env, seed_lineup, seed_profile)


def test_r01_lineup_change_has_a_new_revision_without_a_new_play(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    event = game_event("401999001101")
    panel_env.project(event, [match("fan", event)])
    before = panel_env.snapshot("fan")

    seed_lineup("fan", [PASSER])
    after = panel_env.snapshot("fan")
    assert before["id"] == after["id"]
    assert before["data"]["rows"] != after["data"]["rows"]
    assert after["revision"] > before["revision"]


def test_r01_rereads_after_a_lineup_change_keep_the_revision(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    event = game_event("401999001101")
    panel_env.project(event, [match("fan", event)])
    seed_lineup("fan", [PASSER])
    first, second = panel_env.snapshot("fan"), panel_env.snapshot("fan")
    assert (first["id"], first["revision"]) == (second["id"], second["revision"])


def test_r01_next_projection_after_a_lineup_change_still_advances(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    first = game_event("401999001101", game=GAME)
    panel_env.project(first, [match("fan", first)])
    seed_lineup("fan", [PASSER])
    changed = panel_env.snapshot("fan")
    second = game_event("401999002101", ("9000005",), game=OTHER_GAME, seconds=1)
    panel_env.project(second, [match("fan", second, starters=(PASSER,))])
    projected = panel_env.snapshot("fan")
    assert projected["revision"] > changed["revision"]


def test_r02_overlapping_game_projections_preserve_both_games(panel_env, monkeypatch):
    import store

    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    first = game_event("401999001101", game=GAME)
    second = game_event("401999002101", ("9000005",), game=OTHER_GAME, seconds=1)
    real_get = store.get_panel
    injected = False

    def read_then_run_other_projection(profile_id, team_league):
        nonlocal injected
        row = real_get(profile_id, team_league)
        if not injected:
            injected = True
            panel_env.project(second, [match("fan", second, starters=(PASSER,))])
            assert OTHER_GAME in real_get("fan", TEAM_LEAGUE)["freshness"]["games"]
        return row

    monkeypatch.setattr(store, "get_panel", read_then_run_other_projection)
    panel_env.project(first, [match("fan", first)])
    assert set(panel_env.snapshot("fan")["data"]["games"]) == {GAME, OTHER_GAME}


def test_r02_sequential_control_keeps_both_games(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    first = game_event("401999001101", game=GAME)
    second = game_event("401999002101", ("9000005",), game=OTHER_GAME, seconds=1)
    panel_env.project(first, [match("fan", first)])
    panel_env.project(second, [match("fan", second, starters=(PASSER,))])
    assert set(panel_env.snapshot("fan")["data"]["games"]) == {GAME, OTHER_GAME}
