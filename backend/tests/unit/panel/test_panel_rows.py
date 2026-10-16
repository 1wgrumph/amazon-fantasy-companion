"""PanelState rows, total and progress (VCASE-AFC-PR-039; DES-AFC-P2-PANELSVC).

The panel shows each starter of the followed team with fantasy points and
game status, the team total and progress, under the lineup's scoring basis,
in the CONTRACT-AFC-P2-ENVELOPE envelope served by GET /v1/panel.
"""

import pytest

from panel_support import (PASSER, RECEIVER, TEAM_LEAGUE, check_envelope, game_event, link,  # noqa: F401
                           match, number, panel_env, player_ids, points, row, seed_lineup,
                           seed_profile, statistics)

# Half-PPR (default): 5 * 0.5 + 62 * 0.1 + 6 = 14.7 and 250 * 0.04 + 2 * 4 - 1 = 17.0.
RECEIVER_STATS = dict(receptions=5, receiving_yards=62, receiving_touchdowns=1)
PASSER_STATS = dict(passing_yards=250, passing_touchdowns=2, interceptions_thrown=1)


def seeded(env, profile="fan"):
    seed_profile(profile)
    seed_lineup(profile, [RECEIVER, PASSER])
    env.stats["9000001"] = statistics(**RECEIVER_STATS)
    env.stats["9000005"] = statistics(**PASSER_STATS)
    event = game_event("401999001101")
    env.project(event, [match(profile, event)])
    return env.data(profile)


def test_every_starter_has_one_row(panel_env):
    data = seeded(panel_env)
    assert player_ids(data) == {"9000001", "9000005"}
    assert row(data, "9000001")["name"] == "Sample Receiver"
    assert row(data, "9000005")["name"] == "Sample Passer"


def test_rows_carry_points_under_the_basis(panel_env):
    data = seeded(panel_env)
    assert data["scoringBasis"] == "halfPpr"
    assert points(data, "9000001") == pytest.approx(14.7, abs=0.005)
    assert points(data, "9000005") == pytest.approx(17.0, abs=0.005)


def test_rows_carry_game_status(panel_env):
    data = seeded(panel_env)
    assert row(data, "9000001")["gameStatus"] == "Q2 08:14"
    assert row(data, "9000005")["gameStatus"] == "Q2 08:14"


def test_team_total_is_the_sum_of_row_points(panel_env):
    data = seeded(panel_env)
    total = data["teamTotal"]
    assert number(total["value"]) == pytest.approx(31.7, abs=0.01)
    assert total["reason"] is None, "a complete total is a confirmed score without a reason"


def test_repeated_projection_keeps_one_row_per_starter(panel_env):
    seeded(panel_env)
    later = game_event("401999001102", seconds=40)
    panel_env.project(later, [match("fan", later, starters=(PASSER,))])
    data = panel_env.data("fan")
    assert sorted(r["playerId"] for r in data["rows"]) == ["9000001", "9000005"]


def test_progress_is_zero_before_any_kickoff(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    panel_env.stats["9000001"] = statistics(state="pre", status="Sun 1:00 PM")
    panel_env.stats["9000005"] = statistics(state="pre", status="Sun 1:00 PM")
    event = game_event("401999001101")
    panel_env.project(event, [match("fan", event)])
    assert number(panel_env.data("fan")["progress"]["value"]) == pytest.approx(0.0)


def test_progress_is_one_when_every_game_is_final(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    panel_env.stats["9000001"] = statistics(state="post", status="Final", **RECEIVER_STATS)
    panel_env.stats["9000005"] = statistics(state="post", status="Final", **PASSER_STATS)
    event = game_event("401999001101")
    panel_env.project(event, [match("fan", event)])
    data = panel_env.data("fan")
    assert number(data["progress"]["value"]) == pytest.approx(1.0)
    assert row(data, "9000001")["gameStatus"] == "Final"


def test_progress_between_kickoff_and_final_is_partial(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    panel_env.stats["9000001"] = statistics(state="post", status="Final", **RECEIVER_STATS)
    panel_env.stats["9000005"] = statistics(game="401999002", state="pre", status="Sun 4:25 PM")
    event = game_event("401999001101")
    panel_env.project(event, [match("fan", event)])
    progress = number(panel_env.data("fan")["progress"]["value"])
    assert progress is not None and 0.0 < progress < 1.0


def test_envelope_names_the_lineup_source_and_team_league(panel_env):
    seeded(panel_env)
    envelope = panel_env.snapshot("fan")
    data = check_envelope(envelope)
    assert envelope["source"] == "manual"
    assert data["teamLeague"] == TEAM_LEAGUE


def test_rereads_keep_id_and_revision(panel_env):
    seeded(panel_env)
    first, second = panel_env.snapshot("fan"), panel_env.snapshot("fan")
    assert (first["id"], first["revision"]) == (second["id"], second["revision"])


def test_profile_without_lineup_has_no_rows_and_no_fabricated_total(panel_env):
    seed_profile("fan")
    data = panel_env.data("fan", TEAM_LEAGUE)
    assert data["rows"] == []
    assert data["teamTotal"]["value"] is None, "no lineup is unknown, never a zero total"


def test_get_panel_serves_the_snapshot(panel_env):
    token = link(panel_env.api, "owner")
    seed_lineup("owner", [RECEIVER, PASSER])
    panel_env.stats["9000001"] = statistics(**RECEIVER_STATS)
    panel_env.stats["9000005"] = statistics(**PASSER_STATS)
    event = game_event("401999001101")
    panel_env.project(event, [match("owner", event)])
    status, body = panel_env.api.request("GET", "/v1/panel", token=token,
                                         query={"teamLeague": TEAM_LEAGUE})
    assert status == 200, f"GET /v1/panel must serve the panel envelope, got {status}: {body!r}"
    data = check_envelope(body)
    assert data["teamLeague"] == TEAM_LEAGUE
    assert player_ids(data) == {"9000001", "9000005"}
    assert number(data["teamTotal"]["value"]) == pytest.approx(31.7, abs=0.01)
