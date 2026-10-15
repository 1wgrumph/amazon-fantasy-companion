"""Monitoring scope and basis labels (VCASE-AFC-PR-008, VCASE-AFC-PR-011).

Only profile-relevant games are monitored, only during enabled periods, and
every decision carries exactly one basis label. Game, team and athlete ids
come from two captured games; relevance is never invented.
"""

import pytest

from feed_support import (GAME, OTHER_GAME, attempt, boxscore_athlete_ids,
                          competitor_team_ids, fresh_summary, require_attr,
                          require_module)

BASES = ("observed-playback", "profile-assumption")


def decide(games, players, teams, enabled=True, basis="profile-assumption"):
    func = require_attr(require_module("feed_ingest.monitoring"), "monitored_decisions")
    return attempt(func, games, players, teams, enabled, basis)


def captured_games():
    games = []
    for game_id in (GAME, OTHER_GAME):
        summary = fresh_summary(game_id)
        games.append({"gameId": game_id,
                      "teamIds": sorted(competitor_team_ids(summary)),
                      "playerIds": sorted(boxscore_athlete_ids(summary))})
    return games


def monitored_ids(decisions):
    return {decision["gameId"] for decision in decisions if decision["monitored"]}


def test_a_game_with_a_selected_player_is_monitored():
    games = captured_games()
    selected = [games[0]["playerIds"][0]]
    assert monitored_ids(decide(games, selected, [])) == {GAME}


def test_a_game_with_a_favorite_team_is_monitored():
    games = captured_games()
    favorite = [games[1]["teamIds"][0]]
    assert monitored_ids(decide(games, [], favorite)) == {OTHER_GAME}


def test_an_irrelevant_game_is_not_monitored():
    games = captured_games()
    decisions = decide(games, ["no-such-athlete"], ["no-such-team"])
    assert monitored_ids(decisions) == set()
    assert {decision["gameId"] for decision in decisions} == {GAME, OTHER_GAME}


def test_no_game_is_monitored_outside_an_enabled_period():
    games = captured_games()
    everyone = [player for game in games for player in game["playerIds"]]
    decisions = decide(games, everyone, [], enabled=False)
    assert monitored_ids(decisions) == set()
    assert len(decisions) == len(games)


def test_every_game_gets_exactly_one_decision():
    games = captured_games()
    decisions = decide(games, [], [])
    assert [decision["gameId"] for decision in decisions] == [g["gameId"] for g in games]
    assert all(set(decision) == {"gameId", "monitored", "basis"} for decision in decisions)
    assert all(isinstance(decision["monitored"], bool) for decision in decisions)


@pytest.mark.parametrize("basis", BASES)
def test_every_decision_carries_its_basis_label(basis):
    games = captured_games()
    decisions = decide(games, [games[0]["playerIds"][0]], [], basis=basis)
    assert decisions and all(decision["basis"] == basis for decision in decisions)


@pytest.mark.parametrize("basis", [None, "", "live", "guessed"])
def test_an_unlabeled_or_unknown_basis_is_rejected(basis):
    with pytest.raises(ValueError):
        decide(captured_games(), [], [], basis=basis)


def test_monitoring_does_not_widen_to_the_other_captured_game():
    games = captured_games()
    only_first = [games[0]["playerIds"][0]]
    decisions = decide(games, only_first, [])
    by_game = {decision["gameId"]: decision["monitored"] for decision in decisions}
    assert by_game == {GAME: True, OTHER_GAME: False}
