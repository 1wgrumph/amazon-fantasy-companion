"""Replay labels on every value (VCASE-AFC-PR-013, CONTRACT-AFC-P2-FIXTURE).

When the endpoint is unavailable or its contract changes, captured fixtures
substitute for live events and every affected value says `replay`; no
substituted value is ever presented as live.
"""

import json
import shutil

import pytest

from feed_support import (FIXTURES, GAME, attempt, fresh_summary, plays_in,
                          require_attr, require_module)


def load_events(game_id=GAME, fixtures_dir=FIXTURES):
    func = require_attr(require_module("feed_ingest.replay"), "load_events")
    return attempt(func, game_id, fixtures_dir)


def test_replay_loads_every_captured_play():
    events = load_events()
    assert [event["eventId"] for event in events] == [
        play["id"] for play in plays_in(fresh_summary())]


def test_every_replay_value_is_labeled_replay():
    events = load_events()
    assert events, "the captured game must replay its plays"
    assert all(event["source"] == "replay" for event in events)


def test_no_replay_value_claims_to_be_live():
    for event in load_events():
        assert event["source"] != "live", event


def test_replay_values_match_the_capture():
    summary = fresh_summary()
    by_id = {event["eventId"]: event for event in load_events()}
    for play in plays_in(summary):
        event = by_id[play["id"]]
        assert event["score"] == {"away": play["awayScore"], "home": play["homeScore"]}
        assert event["eventTime"] == play["wallclock"]
        assert event["revision"] == 1


def test_normalizing_as_replay_labels_every_event():
    func = require_attr(require_module("feed_ingest.normalize"), "normalize_summary")
    events = attempt(func, fresh_summary(), GAME, source="replay")
    assert events and all(event["source"] == "replay" for event in events)


def test_ingesting_replay_stores_the_replay_label(api):
    ingest_summary = require_attr(require_module("feed_ingest.ingest"), "ingest_summary")
    attempt(ingest_summary, fresh_summary(), GAME, source="replay")
    items = api.table("Events").scan()["Items"]
    assert items and all(item["source"] == "replay" for item in items)


def test_replay_of_an_uncaptured_game_is_rejected():
    with pytest.raises(ValueError):
        load_events(game_id="401872999")


def test_replay_rejects_a_fixture_that_fails_its_index_hash(tmp_path):
    game_dir = tmp_path / GAME
    shutil.copytree(FIXTURES / GAME, game_dir)
    payload = json.loads((game_dir / "001-summary.json").read_text())
    plays_in(payload)[0]["homeScore"] = 99
    (game_dir / "001-summary.json").write_text(json.dumps(payload))
    with pytest.raises(ValueError):
        load_events(fixtures_dir=tmp_path)
