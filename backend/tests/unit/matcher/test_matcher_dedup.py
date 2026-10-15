"""At most one alert per resolved event red tests (VCASE-AFC-PR-025; DES-AFC-P2-MATCH).

Event identity is ESPN game id + play id and an alert is keyed by
(profile, event id): a re-delivered or retried unchanged event yields nothing
once its alert exists, and one event that concerns several starters or
satisfies several alert types is still one match, so the policy can emit at
most one alert for it. The matcher itself never writes alert records.
"""

from matcher_support import (MANUAL_PASSER, MANUAL_RECEIVER, YAHOO_RECEIVER,  # noqa: F401
                             athlete_ids, for_profile, game_event, match_env, seed_alert,
                             seed_lineup)

EVENT = "401999001201"


def test_first_delivery_yields_one_new_match(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    matches = match_env.resolve(game_event(EVENT, ["9000001"]))
    assert len(for_profile(matches, "fan")) == 1
    assert matches[0]["cursor"] is None, "no alert exists yet, so none is revised"
    assert matches[0]["revision"] == 1


def test_redelivery_after_alert_yields_nothing(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    event = game_event(EVENT, ["9000001"])
    assert len(match_env.resolve(event)) == 1
    seed_alert("fan", "c-0001", EVENT, 1)
    assert match_env.resolve(event) == []


def test_repeated_retries_yield_one_match_per_resolved_event(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    event = game_event(EVENT, ["9000001"])
    total = []
    for delivery in range(4):
        matches = match_env.resolve(dict(event))
        total.extend(for_profile(matches, "fan"))
        if delivery == 0:
            seed_alert("fan", "c-0001", EVENT, 1)
    assert len(total) == 1, f"retries produced {len(total)} matches for one resolved event"


def test_two_starters_in_one_event_are_one_match(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER, MANUAL_PASSER])
    matches = match_env.resolve(game_event(EVENT, ["9000005", "9000001"]))
    assert len(for_profile(matches, "fan")) == 1
    assert athlete_ids(matches[0]) == {"9000001", "9000005"}


def test_event_matching_multiple_alert_types_is_one_match(match_env):
    # A starter's touchdown inside the 20 that leaves a one-point fourth-quarter
    # margin is a player score, a red-zone play and a close game at once.
    seed_lineup("fan", "yahoo", [YAHOO_RECEIVER])
    event = game_event(EVENT, ["9000001"], score=(21, 20), field_position=3)
    matches = match_env.resolve(event)
    assert len(matches) == 1, f"one event must stay one match, got {matches!r}"
    assert matches[0]["profileId"] == "fan"
    assert athlete_ids(matches[0]) == {"9000001"}


def test_each_concerned_profile_matches_once(match_env):
    seed_lineup("fan-one", "manual", [MANUAL_RECEIVER])
    seed_lineup("fan-two", "yahoo", [YAHOO_RECEIVER])
    matches = match_env.resolve(game_event(EVENT, ["9000001"]))
    assert sorted(m["profileId"] for m in matches) == ["fan-one", "fan-two"]


def test_distinct_event_for_same_starter_is_not_deduplicated(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    seed_alert("fan", "c-0001", EVENT, 1)
    matches = match_env.resolve(game_event("401999001202", ["9000001"]))
    assert len(for_profile(matches, "fan")) == 1
    assert matches[0]["cursor"] is None, "a different play is a new resolved event"


def test_matcher_creates_no_alert_records(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    matches = match_env.resolve(game_event(EVENT, ["9000001"]))
    assert len(matches) == 1
    assert match_env.api.table("Alerts").scan()["Items"] == []
