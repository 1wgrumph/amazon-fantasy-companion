"""Alert types, context and red-zone wording red tests (VCASE-AFC-PR-014, -027, -028).

DES-AFC-P2-POLICY: red-zone opportunity is possession strictly inside
red_zone_yards (20) by a team with a relevant starter, so 19 yards qualifies
and 20 and 21 do not; player score is a scoring play listing a relevant
starter; close game is a margin within close_game_margin (8) in the 4th
quarter or overtime, once per game per entry into that state. One event that
satisfies several types is one alert carrying every matching type
(DES-AFC-P2-MATCH).
"""

import pytest

from policy_support import (OVERCLAIM, PASSER, RECEIVER, TYPES, deliver,  # noqa: F401
                            evaluate, for_profile, game_event, match, policy, seed_profile,
                            types_of)


def only_types(policy, event, profile="fan", starters=(RECEIVER,)):
    alerts = for_profile(evaluate(policy, event, [match(profile, event, starters)]), profile)
    assert len(alerts) <= 1, alerts
    return types_of(alerts[0]) if alerts else set()


@pytest.mark.parametrize("yards, expected", [(19, {"RedZone"}), (20, set()), (21, set())],
                         ids=["19-inside", "20-boundary", "21-outside"])
def test_afc_pr_014_red_zone_is_strictly_inside_the_20(policy, yards, expected):
    """AFC-PR-014: red zone means inside the 20-yard line; red_zone_yards is exclusive."""
    seed_profile("fan")
    event = game_event("401999001101", field_position=yards, possession="PHI")
    assert only_types(policy, event) == expected


def test_afc_pr_014_twenty_yards_is_not_inside_the_20(policy):
    """AFC-PR-014 boundary on its own: at exactly 20 yards no red-zone alert exists."""
    seed_profile("fan")
    event = game_event("401999001102", field_position=20, possession="PHI")
    alerts = evaluate(policy, event, [match("fan", event)])
    assert not any("RedZone" in types_of(alert) for alert in alerts), alerts


def test_afc_pr_014_red_zone_needs_the_starters_team_in_possession(policy):
    """AFC-PR-014: the opponent inside the 20 is not this customer's red-zone opportunity."""
    seed_profile("fan")
    event = game_event("401999001103", field_position=8, possession="DAL")
    assert "RedZone" not in only_types(policy, event)


def test_afc_pr_014_player_score_fires_for_a_scoring_play_with_the_starter(policy):
    """AFC-PR-014 positive: a scoring play listing a relevant starter is a player score."""
    seed_profile("fan")
    event = game_event("401999001104", field_position=35, scoring=True, score=(10, 10))
    assert only_types(policy, event) == {"PlayerScore"}


def test_afc_pr_014_non_scoring_play_is_not_a_player_score(policy):
    """AFC-PR-014 negative: a starter's ordinary play emits nothing."""
    seed_profile("fan")
    event = game_event("401999001105", field_position=35, scoring=False)
    assert only_types(policy, event) == set()


@pytest.mark.parametrize("period, score, expected", [
    (4, (20, 28), {"CloseGame"}),
    (4, (20, 29), set()),
    (3, (20, 21), set()),
    (5, (24, 24), {"CloseGame"}),
    (6, (27, 19), {"CloseGame"}),
], ids=["q4-margin-8", "q4-margin-9", "q3-margin-1", "ot-tied", "ot2-margin-8"])
def test_afc_pr_014_close_game_is_within_8_in_q4_or_ot(policy, period, score, expected):
    """AFC-PR-014: close_game_margin (DEC-AFC-SD-035 P1) is within 8 points in Q4 or OT."""
    seed_profile("fan")
    event = game_event("401999001106", period=period, score=score, field_position=60)
    assert only_types(policy, event) == expected


def test_afc_pr_014_close_game_fires_once_per_entry_into_the_state(policy):
    """AFC-PR-014: a game that stays close emits its close-game alert once."""
    seed_profile("fan")
    first = game_event("401999001107", period=4, score=(17, 20), field_position=60)
    second = game_event("401999001108", period=4, score=(17, 20), field_position=55,
                        seconds=40)
    assert [types_of(a) for a in deliver(policy, first, [match("fan", first)])] == [{"CloseGame"}]
    assert deliver(policy, second, [match("fan", second)]) == []


def test_afc_pr_014_simultaneous_matching_types_are_one_alert(policy):
    """AFC-PR-014 with DES-AFC-P2-MATCH: a Q4 touchdown from the 5 in a close game is
    red zone, player score and close game at once, and is one alert carrying all three."""
    seed_profile("fan")
    event = game_event("401999001109", field_position=5, scoring=True, period=4,
                       score=(21, 24))
    alerts = evaluate(policy, event, [match("fan", event)])
    assert len(alerts) == 1, alerts
    assert types_of(alerts[0]) == set(TYPES)


def test_afc_pr_014_simultaneous_types_keep_only_enabled_ones(policy):
    """AFC-PR-014/-016: the merged alert lists only the customer's enabled types."""
    seed_profile("fan", alertTypes=["PlayerScore", "CloseGame"])
    event = game_event("401999001110", field_position=5, scoring=True, period=4,
                       score=(21, 24))
    alerts = evaluate(policy, event, [match("fan", event)])
    assert len(alerts) == 1, alerts
    assert types_of(alerts[0]) == {"PlayerScore", "CloseGame"}
    assert alerts[0]["alertType"] != "RedZone"


@pytest.mark.parametrize("kind, fields", [
    ("RedZone", {"field_position": 19}),
    ("PlayerScore", {"field_position": 35, "scoring": True}),
    ("CloseGame", {"period": 4, "score": (13, 17), "field_position": 60}),
])
def test_afc_pr_027_alert_carries_its_verified_trigger_context(policy, kind, fields):
    """AFC-PR-027: every alert carries the starters and game facts that triggered it."""
    seed_profile("fan")
    event = game_event("401999001111", players=["9000001", "9000005"], source="replay",
                       **fields)
    alerts = evaluate(policy, event, [match("fan", event, (RECEIVER, PASSER))])
    assert len(alerts) == 1 and types_of(alerts[0]) == {kind}, alerts
    context = alerts[0]["triggerContext"]
    assert context.get("gameId") == event["gameId"]
    assert context.get("eventId") == event["eventId"]
    assert context.get("source") == "replay", "the replay label travels with the alert"
    assert context.get("score") == event["score"]
    starters = context.get("starters")
    assert isinstance(starters, list), context
    assert {s.get("athlete_id") for s in starters} == {"9000001", "9000005"}
    assert alerts[0]["revision"] == event["revision"]


@pytest.mark.parametrize("level", ["Mild", "Hype"])
def test_afc_pr_028_red_zone_text_makes_only_team_level_claims(policy, level):
    """AFC-PR-028: red-zone text never claims the starter is on the field or will score."""
    seed_profile("fan", excitement=level)
    event = game_event("401999001112", field_position=19, possession="PHI")
    alerts = evaluate(policy, event, [match("fan", event)])
    assert len(alerts) == 1 and types_of(alerts[0]) == {"RedZone"}, alerts
    text = alerts[0].get("commentary")
    assert isinstance(text, str) and text, f"{level} commentary is attached: {alerts[0]!r}"
    assert not OVERCLAIM.search(text), f"red-zone over-claim: {text!r}"
    assert not OVERCLAIM.search(str(alerts[0]["triggerContext"])), alerts[0]["triggerContext"]
