"""Schema validation rejects without mutation (VCASE-AFC-PR-064, -012).

The external feed is untrusted: a payload that fails the pinned schema is
rejected before any store write, and stored events stay byte-identical.
Malformed variants are derived from the captured fixtures in test code.
"""

import pytest

from feed_support import (GAME, attempt, fresh_scoreboard, fresh_summary,
                          plays_in, require_attr, require_module)


def validation():
    return require_module("feed_ingest.validation")


def ingest():
    return require_module("feed_ingest.ingest")


def validate_summary(payload, game_id=GAME):
    return attempt(require_attr(validation(), "validate_summary"), payload, game_id)


def validate_scoreboard(payload):
    return attempt(require_attr(validation(), "validate_scoreboard"), payload)


def test_captured_summary_passes_validation():
    assert validate_summary(fresh_summary()) is None


def test_captured_scoreboard_passes_validation():
    assert validate_scoreboard(fresh_scoreboard()) is None


def test_summary_for_another_game_is_rejected():
    with pytest.raises(ValueError):
        validate_summary(fresh_summary(), game_id="401872999")


def test_non_object_summary_is_rejected():
    with pytest.raises(ValueError):
        validate_summary(["not", "a", "summary"])


def test_summary_without_header_is_rejected():
    payload = fresh_summary()
    del payload["header"]
    with pytest.raises(ValueError):
        validate_summary(payload)


def test_summary_without_competitions_is_rejected():
    payload = fresh_summary()
    payload["header"]["competitions"] = []
    with pytest.raises(ValueError):
        validate_summary(payload)


def test_summary_without_drives_is_rejected():
    payload = fresh_summary()
    del payload["drives"]
    with pytest.raises(ValueError):
        validate_summary(payload)


def test_play_without_id_is_rejected():
    payload = fresh_summary()
    del plays_in(payload)[0]["id"]
    with pytest.raises(ValueError):
        validate_summary(payload)


def test_play_with_non_numeric_score_is_rejected():
    payload = fresh_summary()
    plays_in(payload)[0]["awayScore"] = "seven"
    with pytest.raises(ValueError):
        validate_summary(payload)


def test_play_with_non_string_wallclock_is_rejected():
    payload = fresh_summary()
    plays_in(payload)[0]["wallclock"] = 123
    with pytest.raises(ValueError):
        validate_summary(payload)


def test_captured_missing_wallclock_validates_ingests_and_replays_all_183_plays(api):
    from feed_support import FIXTURES
    game_id = "401872986"
    payload = fresh_summary(game_id)
    validate_summary(payload, game_id)
    live = ingest().ingest_summary(payload, game_id)
    replay = require_module("feed_ingest.replay").load_events(game_id, FIXTURES)
    expected = [play["id"] for play in plays_in(payload)]
    assert len(expected) == len(live) == len(replay) == 183
    assert [event["eventId"] for event in live] == expected
    assert [event["eventId"] for event in replay] == expected
    for events, source in ((live, "live"), (replay, "replay")):
        kickoff = next(event for event in events if event["eventId"] == "40187298640")
        assert kickoff["eventTime"] is None
        assert {event["source"] for event in events} == {source}
    assert len(api.table("Events").scan()["Items"]) == 183


def test_scoreboard_without_events_is_rejected():
    payload = fresh_scoreboard()
    del payload["events"]
    with pytest.raises(ValueError):
        validate_scoreboard(payload)


def test_scoreboard_event_without_id_is_rejected():
    payload = fresh_scoreboard()
    del payload["events"][0]["id"]
    with pytest.raises(ValueError):
        validate_scoreboard(payload)


def stored_events(api):
    items = api.table("Events").scan()["Items"]
    return sorted((item["gameId"], item["eventId"], int(item["revision"]))
                  for item in items)


def test_invalid_poll_leaves_stored_events_unchanged(api):
    ingest_summary = require_attr(ingest(), "ingest_summary")
    stored = attempt(ingest_summary, fresh_summary(), GAME)
    assert stored, "a valid captured summary must store its events"
    before = stored_events(api)
    bad = fresh_summary()
    plays_in(bad)[0]["homeScore"] = "corrupt"
    with pytest.raises(ValueError):
        attempt(ingest_summary, bad, GAME)
    assert stored_events(api) == before


def test_invalid_first_poll_stores_nothing(api):
    ingest_summary = require_attr(ingest(), "ingest_summary")
    bad = fresh_summary()
    del bad["header"]
    with pytest.raises(ValueError):
        attempt(ingest_summary, bad, GAME)
    assert stored_events(api) == []
