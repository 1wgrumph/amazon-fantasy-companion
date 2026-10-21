"""A stored lineup without league/team never matches a pair (#137).

Legacy or out-of-band Lineups rows can carry starters with no pair. Such a
lineup cannot match any team/league, so the panel serves the existing
no-lineup state instead of raising KeyError.
"""

import pytest

from panel_support import (LEAGUE, RECEIVER, TEAM, TEAM_LEAGUE, at,  # noqa: F401
                           check_envelope, game_event, link, match, panel_env,
                           seed_profile)

PAIRLESS = [{"team": TEAM}, {"league": LEAGUE}, {}]
IDS = ["missing-league", "missing-team", "missing-both"]


def seed_pairless(panel_env, pair):
    """A stored lineup with starters and an incomplete (or absent) pair."""
    row = {"profileId": "fan", "source": "manual", "starters": [dict(RECEIVER)],
           "updatedAt": at(0), **pair}
    panel_env.api.table("Lineups").put_item(Item=row)


@pytest.mark.parametrize("pair", PAIRLESS, ids=IDS)
def test_pairless_lineup_never_matches_a_selected_pair(panel_env, pair):
    seed_profile("fan")
    seed_pairless(panel_env, pair)
    data = panel_env.data("fan", TEAM_LEAGUE)
    assert data["teamLeague"] == TEAM_LEAGUE
    assert data["rows"] == []
    assert data["teamTotal"]["value"] is None
    assert data["teamTotal"]["reason"] == "no lineup for this team/league"


@pytest.mark.parametrize("pair", PAIRLESS, ids=IDS)
def test_pairless_lineup_with_no_selection_serves_the_default_pair(panel_env, pair):
    seed_profile("fan")
    seed_pairless(panel_env, pair)
    data = check_envelope(panel_env.snapshot("fan"))
    assert data["teamLeague"] == "unassigned/unassigned"
    assert data["rows"] == []
    assert data["teamTotal"]["reason"] == "no lineup for this team/league"


@pytest.mark.parametrize("pair", PAIRLESS, ids=IDS)
def test_project_skips_a_pairless_lineup(panel_env, pair):
    seed_profile("fan")
    seed_pairless(panel_env, pair)
    event = game_event("401999001101")
    panel_env.project(event, [match("fan", event)])
    assert panel_env.api.table("Panels").scan()["Items"] == []


def test_get_panel_serves_a_pairless_lineup_as_no_lineup(panel_env):
    seed_profile("fan")
    seed_pairless(panel_env, {})
    token = link(panel_env.api, "fan")
    status, body = panel_env.api.request("GET", "/v1/panel", token=token,
                                         query={"teamLeague": TEAM_LEAGUE})
    assert status == 200, f"GET /v1/panel must not fail on a pairless lineup: {status}: {body!r}"
    data = check_envelope(body)
    assert data["rows"] == []
    assert data["teamTotal"]["reason"] == "no lineup for this team/league"
