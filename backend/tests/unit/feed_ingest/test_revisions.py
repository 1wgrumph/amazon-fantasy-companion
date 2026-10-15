"""Revisions and scoring corrections (VCASE-AFC-PR-012; DES-AFC-P2-MATCH).

A correction is a new revision of the same event id, never a second event.
ESPN edits plays after the fact and `modified` has minute precision
(X05-OBS-002), so a correction is observed as changed play content on a
later poll; the changed variant is derived from the capture in test code.
"""

from feed_support import (GAME, attempt, fresh_summary, plays_in,
                          require_attr, require_module)


def normalize(payload, prior=None):
    func = require_attr(require_module("feed_ingest.normalize"), "normalize_summary")
    return attempt(func, payload, GAME, prior=prior)


def first_poll():
    events = normalize(fresh_summary())
    return {event["eventId"]: event for event in events}


def corrected_summary():
    """The capture with one play's score and text edited, as ESPN does."""
    summary = fresh_summary()
    play = plays_in(summary)[10]
    play["homeScore"] += 3
    play["text"] += " Correction applied."
    play["modified"] = "2026-10-11T18:24Z"
    return summary, play


def test_an_unchanged_repoll_emits_nothing():
    assert normalize(fresh_summary(), prior=first_poll()) == []


def test_a_correction_emits_one_new_revision_of_the_same_event():
    summary, play = corrected_summary()
    emitted = normalize(summary, prior=first_poll())
    assert [event["eventId"] for event in emitted] == [play["id"]]
    assert emitted[0]["gameId"] == GAME
    assert emitted[0]["revision"] == 2
    assert emitted[0]["correctionOf"] == 1


def test_a_correction_carries_the_corrected_score():
    summary, play = corrected_summary()
    emitted = normalize(summary, prior=first_poll())
    assert emitted[0]["score"] == {"away": play["awayScore"], "home": play["homeScore"]}


def test_revisions_stay_monotonic_across_two_corrections():
    prior = first_poll()
    summary, play = corrected_summary()
    second = normalize(summary, prior=prior)
    prior[play["id"]] = second[0]
    again, same_play = corrected_summary()
    plays_in(again)[10]["homeScore"] += 4
    third = normalize(again, prior=prior)
    assert [event["eventId"] for event in third] == [same_play["id"]]
    assert third[0]["revision"] == 3
    assert third[0]["correctionOf"] == 2


def test_a_new_play_after_the_first_poll_starts_at_revision_one():
    prior = first_poll()
    summary = fresh_summary()
    extra = dict(plays_in(summary)[-1])
    extra["id"] = GAME + "999001"
    extra["sequenceNumber"] = "99900100"
    summary["drives"]["previous"][-1]["plays"].append(extra)
    emitted = normalize(summary, prior=prior)
    assert [event["eventId"] for event in emitted] == [extra["id"]]
    assert emitted[0]["revision"] == 1
    assert emitted[0]["correctionOf"] is None


def test_ingesting_a_correction_revises_the_stored_event_in_place(api):
    ingest_summary = require_attr(require_module("feed_ingest.ingest"), "ingest_summary")
    attempt(ingest_summary, fresh_summary(), GAME)
    summary, play = corrected_summary()
    attempt(ingest_summary, summary, GAME)
    items = api.table("Events").scan()["Items"]
    matching = [item for item in items if item["eventId"] == play["id"]]
    assert len(matching) == 1, "a correction must not duplicate the stored event"
    assert int(matching[0]["revision"]) == 2
    assert len(items) == len(plays_in(fresh_summary()))


def test_ingesting_the_same_poll_twice_changes_no_revision(api):
    ingest_summary = require_attr(require_module("feed_ingest.ingest"), "ingest_summary")
    attempt(ingest_summary, fresh_summary(), GAME)
    attempt(ingest_summary, fresh_summary(), GAME)
    items = api.table("Events").scan()["Items"]
    assert items and all(int(item["revision"]) == 1 for item in items)
