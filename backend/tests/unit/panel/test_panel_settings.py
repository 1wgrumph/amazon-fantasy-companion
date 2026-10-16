"""Panel reflects team, league and display settings (VCASE-AFC-PR-044; spec 4.1.9, 4.1.12).

The panel is a view of the recorded Settings, not a second configuration:
a preset, team/league or visibility change appears on the next read with a
higher revision, and no panel content contradicts the recorded settings.
"""

import pytest

from panel_support import (LEAGUE, OTHER_PAIR, RECEIVER, TEAM, TEAM_LEAGUE, check_envelope,  # noqa: F401
                           game_event, link, match, number, panel_env, player_ids, points,
                           seed_lineup, seed_profile, statistics, update_profile)

OTHER_TEAM_LEAGUE = OTHER_PAIR["league"] + "/" + OTHER_PAIR["team"]


def projected(env, **settings):
    seed_profile("fan", **settings)
    seed_lineup("fan", [RECEIVER])
    env.stats["9000001"] = statistics(receptions=4)
    event = game_event("401999001401")
    env.project(event, [match("fan", event)])


def test_preset_change_rescores_on_the_next_read(panel_env):
    projected(panel_env, scoringPreset="halfPpr")
    before = panel_env.snapshot("fan")
    assert check_envelope(before)["scoringBasis"] == "halfPpr"
    update_profile("fan", scoringPreset="ppr")
    after = panel_env.snapshot("fan")
    data = check_envelope(after)
    assert data["scoringBasis"] == "ppr"
    assert points(data, "9000001") == pytest.approx(4.0)
    assert after["revision"] > before["revision"], "a settings change must raise the revision"


def test_preset_change_through_the_profile_api_reaches_get_panel(panel_env):
    token = link(panel_env.api, "owner")
    seed_lineup("owner", [RECEIVER])
    panel_env.stats["9000001"] = statistics(receptions=4)
    event = game_event("401999001401")
    panel_env.project(event, [match("owner", event)])
    status, before = panel_env.api.request("GET", "/v1/panel", token=token)
    assert status == 200, f"GET /v1/panel must serve the panel envelope, got {status}: {before!r}"
    assert check_envelope(before)["scoringBasis"] == "halfPpr"
    status, profile = panel_env.api.request("GET", "/v1/profile", token=token)
    assert status == 200
    status, _ = panel_env.api.request("PUT", "/v1/profile", token=token, body={
        "revision": profile["revision"], "data": {"scoringPreset": "ppr"}})
    assert status == 200
    status, after = panel_env.api.request("GET", "/v1/panel", token=token)
    assert status == 200
    data = check_envelope(after)
    assert data["scoringBasis"] == "ppr"
    assert points(data, "9000001") == pytest.approx(4.0)
    assert after["revision"] > before["revision"]


def test_settings_team_league_selects_the_panel(panel_env):
    projected(panel_env, teamLeague={"league": LEAGUE, "team": TEAM})
    data = panel_env.data("fan")
    assert data["teamLeague"] == TEAM_LEAGUE
    assert player_ids(data) == {"9000001"}


def test_without_a_team_league_setting_the_active_lineup_is_followed(panel_env):
    projected(panel_env)
    assert panel_env.data("fan")["teamLeague"] == TEAM_LEAGUE


def test_requested_team_league_is_echoed(panel_env):
    projected(panel_env, teamLeague={"league": LEAGUE, "team": TEAM})
    assert panel_env.data("fan", TEAM_LEAGUE)["teamLeague"] == TEAM_LEAGUE


def test_another_team_league_shows_no_foreign_rows(panel_env):
    projected(panel_env, teamLeague=dict(OTHER_PAIR))
    data = panel_env.data("fan")
    assert data["teamLeague"] == OTHER_TEAM_LEAGUE, "the panel follows the recorded team/league"
    assert data["rows"] == [], "rows of another team must not appear under the selected pair"
    assert number(data["teamTotal"]["value"]) is None


def test_team_league_change_moves_the_panel(panel_env):
    projected(panel_env, teamLeague=dict(OTHER_PAIR))
    assert panel_env.data("fan")["rows"] == []
    update_profile("fan", teamLeague={"league": LEAGUE, "team": TEAM})
    data = panel_env.data("fan")
    assert data["teamLeague"] == TEAM_LEAGUE
    assert player_ids(data) == {"9000001"}


def test_get_panel_passes_the_team_league_query(panel_env):
    token = link(panel_env.api, "owner")
    seed_lineup("owner", [RECEIVER])
    panel_env.stats["9000001"] = statistics(receptions=4)
    event = game_event("401999001401")
    panel_env.project(event, [match("owner", event)])
    status, body = panel_env.api.request("GET", "/v1/panel", token=token,
                                         query={"teamLeague": OTHER_TEAM_LEAGUE})
    assert status == 200, f"GET /v1/panel must serve the panel envelope, got {status}: {body!r}"
    data = check_envelope(body)
    assert data["teamLeague"] == OTHER_TEAM_LEAGUE
    assert data["rows"] == []


def test_visibility_reflects_panel_prefs(panel_env):
    projected(panel_env, panelPrefs={"visible": False})
    before = panel_env.snapshot("fan")
    assert check_envelope(before)["visible"] is False
    update_profile("fan", panelPrefs={"visible": True})
    after = panel_env.snapshot("fan")
    assert check_envelope(after)["visible"] is True
    assert after["revision"] > before["revision"]


def test_visibility_defaults_to_shown(panel_env):
    projected(panel_env)
    assert panel_env.data("fan")["visible"] is True


def test_unrelated_settings_change_keeps_the_panel_facts(panel_env):
    projected(panel_env, scoringPreset="ppr")
    before = check_envelope(panel_env.snapshot("fan"))
    update_profile("fan", excitement="Hype")
    after = check_envelope(panel_env.snapshot("fan"))
    assert after["scoringBasis"] == before["scoringBasis"] == "ppr"
    assert points(after, "9000001") == points(before, "9000001") == pytest.approx(4.0)
