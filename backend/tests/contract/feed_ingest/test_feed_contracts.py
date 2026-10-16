"""Frozen feed contracts (DES-AFC-P2-FEED, CONTRACT-AFC-P2-FIXTURE,
CONTRACT-AFC-P2-ENVELOPE).

The pinned schema lives in src/feed_ingest/schema/, replay fixtures keep the
captured layout with a verifying index, and each normalized value carries
the GameEvent envelope fields. Product calls run first, so a missing
implementation fails by assertion, never by collection error.
"""

import hashlib
import importlib
import json
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[3]
FIXTURES = BACKEND / "fixtures" / "replay"
SRC = BACKEND / "src" / "feed_ingest"
GAME = "401872981"
ENVELOPE_SOURCES = ("live", "replay", "yahoo", "manual")


def require_module(name):
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        raise AssertionError(f"feed behavior is not implemented: cannot import {name}: {exc}")


def attempt(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except NotImplementedError as exc:
        raise AssertionError(f"feed behavior is not implemented (AFC-STUB): {exc}")


def summary():
    return json.loads((FIXTURES / GAME / "001-summary.json").read_text())


def normalized():
    module = require_module("feed_ingest.normalize")
    try:
        func = module.normalize_summary
    except AttributeError:
        raise AssertionError("feed behavior is not implemented: no normalize_summary")
    return attempt(func, summary(), GAME)


@pytest.mark.contract
def test_pinned_schemas_exist_and_parse():
    validate = require_module("feed_ingest.validation")
    assert hasattr(validate, "validate_summary"), "validation entry point is missing"
    schema_dir = SRC / "schema"
    assert schema_dir.is_dir(), "DES-AFC-P2-FEED pins the schema under src/feed_ingest/schema/"
    schemas = sorted(schema_dir.glob("*.json"))
    assert len(schemas) >= 2, "scoreboard and summary each need a pinned schema"
    for path in schemas:
        assert isinstance(json.loads(path.read_text()), dict), path


@pytest.mark.contract
def test_every_normalized_value_carries_the_envelope():
    events = normalized()
    assert events, "the captured game must normalize to events"
    for event in events:
        assert isinstance(event["eventId"], str) and event["eventId"], event
        assert isinstance(event["revision"], int) and event["revision"] >= 1, event
        assert event["source"] in ENVELOPE_SOURCES, event
        assert isinstance(event["eventTime"], str) and event["eventTime"], event


@pytest.mark.contract
def test_event_identity_is_game_plus_play():
    plays = [play for drive in summary()["drives"]["previous"]
             for play in drive.get("plays") or []]
    events = normalized()
    assert {(event["gameId"], event["eventId"]) for event in events} == {
        (GAME, play["id"]) for play in plays}
    assert len(events) == len(plays), "one event per play, never a duplicate identity"


@pytest.mark.contract
def test_replay_fixture_index_verifies_through_replay():
    replay = require_module("feed_ingest.replay")
    events = attempt(replay.load_events, GAME, FIXTURES)
    assert events and all(event["source"] == "replay" for event in events)
    index = json.loads((FIXTURES / GAME / "index.json").read_text())
    assert index["game_id"] == GAME and index["schema"] == "afc.replay-index.v1"
    for entry in index["files"]:
        raw = (FIXTURES / GAME / entry["file"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"], entry["file"]
        assert entry["provenance"] == "historical-replay", entry
        assert entry["http_status"] == 200, entry


@pytest.mark.contract
def test_all_captured_games_replay_with_the_label():
    replay = require_module("feed_ingest.replay")
    game_ids = sorted(path.name for path in FIXTURES.iterdir() if path.is_dir())
    assert len(game_ids) == 14, "P2-X05 PR 1 captured 14 completed games"
    for game_id in game_ids:
        events = attempt(replay.load_events, game_id, FIXTURES)
        assert events, game_id
        assert all(event["source"] == "replay" for event in events), game_id
        assert all(event["gameId"] == game_id for event in events), game_id


@pytest.mark.contract
def test_lambda_handler_remains_the_ingest_entry_point():
    module = require_module("feed_ingest")
    handler = getattr(module, "lambda_handler", None)
    assert callable(handler), "template IngestFunction handler is feed_ingest.lambda_handler"
    with pytest.raises(ValueError):
        attempt(handler, {"source": "not-a-schedule"}, None)
