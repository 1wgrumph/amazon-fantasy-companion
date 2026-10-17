"""Broadcast channel from ingest to resolve (P2B06T-DX-001).

The channel is header.competitions[0].broadcasts[].media.shortName of the
recorded summary (X05-OBS-001). Multiple broadcasts pick the first valid
entry in ESPN's listed order. A malformed or oversize broadcast omits the
channel and never rejects the game; the schema keeps only DoS bounds.
"""

import json
from pathlib import Path

import pytest

from feed_support import (FIXTURES, GAME, attempt, fresh_summary, plays_in,
                          require_attr, require_module)

# Prime Video entry exactly as recorded for 401873010 and 401872995 in
# spikes/sp3-provider-links/espn-summary-receipt.json.
PRIME_BROADCAST = {"type": {"id": "4", "shortName": "Streaming"},
                   "market": {"id": "1", "type": "National"},
                   "media": {"shortName": "Prime Video"},
                   "lang": "en", "region": "us", "isNational": True}
REGISTRY = Path(__file__).resolve().parents[3] / "src" / "provider_resolver" / "registry.json"


def broadcasts(summary):
    return summary["header"]["competitions"][0]["broadcasts"]


def normalize(summary, game_id=GAME):
    func = require_attr(require_module("feed_ingest.normalize"), "normalize_summary")
    return attempt(func, summary, game_id)


def ingest(summary, game_id=GAME):
    func = require_attr(require_module("feed_ingest.ingest"), "ingest_summary")
    return attempt(func, summary, game_id)


def event_channel(event_id):
    return attempt(require_module("provider_resolver").event_channel, event_id)


@pytest.mark.parametrize("game_id", sorted(path.name for path in FIXTURES.iterdir()))
def test_channel_is_normalized_from_every_replay_fixture(game_id):
    summary = fresh_summary(game_id)
    expected = broadcasts(summary)[0]["media"]["shortName"]
    events = normalize(summary, game_id)
    assert events and all(event["channel"] == expected for event in events), expected


def test_multiple_broadcasts_pick_the_first_listed():
    # 401872994 is recorded with ESPN then ABC.
    summary = fresh_summary("401872994")
    assert [entry["media"]["shortName"] for entry in broadcasts(summary)] == ["ESPN", "ABC"]
    assert {event["channel"] for event in normalize(summary, "401872994")} == {"ESPN"}


def test_an_invalid_first_broadcast_falls_through_to_the_next_valid_one():
    summary = fresh_summary()
    broadcasts(summary).insert(0, {"media": {"shortName": " "}})
    expected = broadcasts(summary)[1]["media"]["shortName"]
    assert {event["channel"] for event in normalize(summary)} == {expected}


def test_channel_survives_ingest_storage(api):
    summary = fresh_summary()
    expected = broadcasts(summary)[0]["media"]["shortName"]
    stored = ingest(summary)
    items = api.table("Events").scan()["Items"]
    assert stored and len(items) == len(plays_in(summary))
    assert all(item["channel"] == expected for item in items)


def test_event_channel_reads_the_stored_channel_for_a_play(api):
    summary = fresh_summary()
    expected = broadcasts(summary)[0]["media"]["shortName"]
    ingest(summary)
    for play in plays_in(summary)[:3]:
        assert event_channel(play["id"]) == expected, play["id"]


@pytest.mark.parametrize("event_id", ["401872981999999", "evt-espn", "", None,
                                      "4018729811", "4" * 40])
def test_event_channel_is_none_for_an_unknown_or_malformed_event(api, event_id):
    ingest(fresh_summary())
    assert event_channel(event_id) is None


def test_resolve_serves_the_prime_video_route_for_a_prime_broadcast(api):
    import store
    registry = json.loads(REGISTRY.read_text())
    prime = next(p for p in registry["providers"] if p["id"] == "prime_video")
    assert prime["channels_carried"] == ["Prime Video"]
    summary = fresh_summary()
    broadcasts(summary)[:] = [dict(PRIME_BROADCAST)]
    ingest(summary)
    resolver = require_module("provider_resolver")
    attempt(resolver.record_installed_apps, "owner",
            [prime["platform_routes"]["fire_os"]["package"]])
    assert store.put_profile("owner", {"providerPref": {"order": ["prime_video"]}}, 0,
                             "2026-10-16T12:00:00Z")
    result = attempt(resolver.resolve, "owner", plays_in(summary)[0]["id"])
    assert result["channel"] == "Prime Video", result
    assert result["provider"] == "prime_video", result
    assert result["route"]["platform_routes"]["fire_os"]["status"] == "verified", result


def _absent(summary):
    del summary["header"]["competitions"][0]["broadcasts"]


@pytest.mark.parametrize("mutate", [
    _absent,
    lambda s: broadcasts(s).clear(),
    lambda s: broadcasts(s)[0]["media"].update(shortName=""),
    lambda s: broadcasts(s)[0]["media"].update(shortName="   "),
    lambda s: broadcasts(s)[0]["media"].update(shortName="x" * 33),
    lambda s: broadcasts(s)[0]["media"].update(shortName=" Fox"),
    lambda s: broadcasts(s)[0]["media"].update(shortName="Fox\n"),
    lambda s: broadcasts(s)[0]["media"].update(shortName=42),
    lambda s: broadcasts(s)[0]["media"].update(shortName=None),
    lambda s: broadcasts(s)[0]["media"].pop("shortName"),
    lambda s: broadcasts(s)[0].pop("media"),
    lambda s: broadcasts(s)[0].update(media="Fox"),
    lambda s: broadcasts(s).__setitem__(0, "Fox"),
    lambda s: s["header"]["competitions"][0].update(broadcasts={"media": "Fox"}),
], ids=["absent", "empty", "blank", "whitespace", "oversize", "padded", "control",
        "number", "null", "no-shortName", "no-media", "media-string", "entry-string",
        "not-a-list"])
def test_a_bad_broadcast_omits_the_channel_and_still_ingests_the_game(api, mutate):
    summary = fresh_summary()
    mutate(summary)
    stored = ingest(summary)
    items = api.table("Events").scan()["Items"]
    assert len(stored) == len(items) == len(plays_in(fresh_summary()))
    assert all("channel" not in item for item in items), items
    assert event_channel(plays_in(summary)[0]["id"]) is None


@pytest.mark.parametrize("mutate", [
    lambda s: broadcasts(s).extend([dict(PRIME_BROADCAST)] * 64),
    lambda s: broadcasts(s)[0]["media"].update(shortName="x" * 257),
], ids=["too-many-broadcasts", "oversize-shortName"])
def test_schema_bounds_broadcast_size(mutate):
    validate = require_attr(require_module("feed_ingest.validation"), "validate_summary")
    summary = fresh_summary()
    mutate(summary)
    with pytest.raises(ValueError, match="pinned schema"):
        validate(summary, GAME)
