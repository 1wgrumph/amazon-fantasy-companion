"""Excitement commentary red tests (VCASE-AFC-PR-023; OD-AFC-02).

Commentary is a fixed template per excitement level Off / Mild / Hype
(DEC-AFC-SD-035 P2), filled only from the triggering event and its trigger
context: Off attaches nothing, the level changes the words for an identical
event, and the words never decide the alert type, score or players.
"""

import re

import pytest

from policy_support import (DECOY, PASSER, RECEIVER, evaluate, for_profile,  # noqa: F401
                            game_event, match, numbers, policy, seed_profile)

EVENTS = {
    "red-zone": dict(field_position=19),
    "player-score": dict(field_position=35, scoring=True, score=(10, 17)),
    "close-game": dict(period=4, score=(20, 23), field_position=60),
    "all-three": dict(field_position=4, scoring=True, period=4, score=(27, 24)),
}


def by_level(policy, fields, event_id="401999001301"):
    for level in ("Off", "Mild", "Hype"):
        seed_profile("fan-" + level.lower(), excitement=level)
    event = game_event(event_id, **fields)
    alerts = evaluate(policy, event, [match("fan-" + level, event)
                                      for level in ("off", "mild", "hype")])
    found = {}
    for level in ("off", "mild", "hype"):
        mine = for_profile(alerts, "fan-" + level)
        assert len(mine) == 1, f"one alert per profile, got {alerts!r}"
        found[level] = mine[0]
    return event, found


@pytest.mark.parametrize("kind", EVENTS)
def test_afc_pr_023_off_attaches_no_commentary(policy, kind):
    """AFC-PR-023 negative: excitement Off attaches nothing."""
    _, alerts = by_level(policy, EVENTS[kind])
    assert not alerts["off"].get("commentary"), alerts["off"]


@pytest.mark.parametrize("kind", EVENTS)
def test_afc_pr_023_level_change_alters_commentary(policy, kind):
    """AFC-PR-023: Mild and Hype attach different text for an identical event."""
    _, alerts = by_level(policy, EVENTS[kind])
    mild, hype = alerts["mild"].get("commentary"), alerts["hype"].get("commentary")
    assert isinstance(mild, str) and mild.strip(), alerts["mild"]
    assert isinstance(hype, str) and hype.strip(), alerts["hype"]
    assert mild != hype


@pytest.mark.parametrize("kind", EVENTS)
def test_afc_pr_023_commentary_never_decides_the_alert(policy, kind):
    """AFC-PR-023: no commentary output determines the event, score, type or players."""
    _, alerts = by_level(policy, EVENTS[kind])
    reference = alerts["off"]
    for level in ("mild", "hype"):
        assert alerts[level]["alertType"] == reference["alertType"]
        assert alerts[level]["triggerContext"] == reference["triggerContext"]
        assert alerts[level]["revision"] == reference["revision"]


@pytest.mark.parametrize("kind", EVENTS)
def test_afc_pr_023_every_number_is_grounded_in_the_event(policy, kind):
    """AFC-PR-023: each number in commentary is a score, the margin, the field
    position or the period of the triggering event, or the registered
    red_zone_yards (20)."""
    event, alerts = by_level(policy, EVENTS[kind])
    score = event["score"]
    grounded = numbers(score, event["fieldPosition"], event["period"],
                       abs(score["home"] - score["away"]), 20)
    for level in ("mild", "hype"):
        text = alerts[level].get("commentary") or ""
        assert set(re.findall(r"\d+", text)) <= grounded, (level, text, grounded)


@pytest.mark.parametrize("kind", EVENTS)
def test_afc_pr_023_names_only_trigger_entities(policy, kind):
    """AFC-PR-023: commentary names no lineup player or team outside the trigger.
    The lineup holds Sample Passer and Bench Decoy (DAL); only Sample Receiver
    (PHI) is in the event."""
    _, alerts = by_level(policy, EVENTS[kind])
    for level in ("mild", "hype"):
        text = alerts[level].get("commentary") or ""
        for outsider in (PASSER["name"], DECOY["name"], "DAL"):
            assert outsider not in text, (level, outsider, text)


def test_afc_pr_023_named_player_follows_the_trigger(policy):
    """AFC-PR-023: the same play credited to another starter never carries the first
    starter's name, so names come from the trigger, not a template constant."""
    seed_profile("fan", excitement="Hype")
    texts = {}
    for starter, player_id in ((RECEIVER, "9000001"), (PASSER, "9000005")):
        event = game_event("40199900131" + player_id[-1], players=[player_id],
                           field_position=35, scoring=True)
        alerts = evaluate(policy, event, [match("fan", event, (starter,))])
        assert len(alerts) == 1, alerts
        texts[starter["name"]] = alerts[0].get("commentary") or ""
    assert RECEIVER["name"] not in texts[PASSER["name"]], texts
    assert PASSER["name"] not in texts[RECEIVER["name"]], texts


def test_afc_pr_023_templates_are_fixed(policy):
    """AFC-PR-023 / OD-AFC-02: one level and one event give one text (no generation)."""
    seed_profile("fan-a", excitement="Mild")
    seed_profile("fan-b", excitement="Mild")
    event = game_event("401999001320", field_position=35, scoring=True)
    alerts = evaluate(policy, event, [match("fan-a", event), match("fan-b", event)])
    texts = {alert["profileId"]: alert.get("commentary") for alert in alerts}
    assert set(texts) == {"fan-a", "fan-b"}, alerts
    assert texts["fan-a"] and texts["fan-a"] == texts["fan-b"], texts
