"""Scoring-correction red tests (VCASE-AFC-PR-026, AFC-PR-046; DES-AFC-P2-MATCH).

A correction is a later revision of the same event id. It revises the
profile's existing alert in place (same cursor, the alert id) and carries the
corrected revision on to the panel; it never allocates a new alert id. A
stale or re-delivered revision yields nothing.
"""

from matcher_support import (MANUAL_PASSER, MANUAL_RECEIVER, YAHOO_RECEIVER,  # noqa: F401
                             for_profile, game_event, match_env, seed_alert, seed_lineup)

EVENT = "401999001301"


def corrected(players=("9000001",), revision=2, score=(14, 20)):
    return game_event(EVENT, list(players), revision=revision, correction_of=revision - 1,
                      score=score)


def test_correction_revises_the_existing_alert(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    seed_alert("fan", "c-0001", EVENT, 1)
    matches = match_env.resolve(corrected())
    assert len(matches) == 1
    assert matches[0]["profileId"] == "fan"
    assert matches[0]["cursor"] == "c-0001", "the correction must revise the existing alert"
    assert matches[0]["revision"] == 2


def test_correction_does_not_allocate_a_new_alert_id(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    seed_alert("fan", "c-0001", EVENT, 1)
    matches = match_env.resolve(corrected())
    cursors = [m.get("cursor") for m in for_profile(matches, "fan")]
    assert cursors == ["c-0001"], f"a correction allocated a new alert id: {cursors!r}"
    stored = match_env.api.table("Alerts").scan()["Items"]
    assert [item["cursor"] for item in stored] == ["c-0001"]


def test_correction_reassigning_the_play_still_revises_the_alert(match_env):
    # The corrected play no longer credits the starter: the stale alert and
    # panel fact must still be revised for that profile, not left behind.
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    seed_alert("fan", "c-0001", EVENT, 1)
    matches = match_env.resolve(corrected(players=("9000077",)))
    assert [m["cursor"] for m in for_profile(matches, "fan")] == ["c-0001"]
    assert matches[0]["revision"] == 2


def test_correction_revises_every_concerned_profile_in_place(match_env):
    seed_lineup("fan-one", "manual", [MANUAL_RECEIVER])
    seed_lineup("fan-two", "yahoo", [YAHOO_RECEIVER])
    seed_alert("fan-one", "c-0101", EVENT, 1)
    seed_alert("fan-two", "c-0202", EVENT, 1)
    matches = match_env.resolve(corrected())
    assert {m["profileId"]: m["cursor"] for m in matches} == {"fan-one": "c-0101",
                                                              "fan-two": "c-0202"}
    assert [m["revision"] for m in matches] == [2, 2]


def test_stale_revision_after_correction_yields_nothing(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    seed_alert("fan", "c-0001", EVENT, 2)
    assert match_env.resolve(game_event(EVENT, ["9000001"], revision=1)) == []


def test_correction_redelivery_yields_nothing(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    seed_alert("fan", "c-0001", EVENT, 2)
    assert match_env.resolve(corrected()) == []
