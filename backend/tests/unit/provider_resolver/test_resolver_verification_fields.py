"""Verified-route field checks (CONTRACT-AFC-P2-PROVIDER-REGISTRY).

A platform entry is verified only when verified_outcome is a defined
RoutingOutcome and verified_at is a real UTC instant in the registry's
canonical form YYYY-MM-DDTHH:MM:SSZ; any other
entry is a REGISTRY_ROUTE_GAP and its launch data is never served.
"""

import json

import pytest

from resolver_support import LANDED_REGISTRY, require_module, resolver, seed_pref  # noqa: F401

EVENT = "evt-espn-3"
GAP = "REGISTRY_ROUTE_GAP"


def fire_os_route(resolver, **fields):
    """Resolve alpha_stream after replacing fields on its fire_os entry (None removes)."""
    registry = json.loads(resolver.registry.read_text())
    provider = next(p for p in registry["providers"] if p["id"] == "alpha_stream")
    entry = provider["platform_routes"]["fire_os"]
    for key, value in fields.items():
        if value is None:
            entry.pop(key, None)
        else:
            entry[key] = value
    resolver.registry.write_text(json.dumps(registry))
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    result = resolver.resolve(EVENT)
    assert result["provider"] == "alpha_stream", result
    return result["route"]["platform_routes"]["fire_os"]


def test_unknown_outcome_is_a_gap(resolver):
    assert fire_os_route(resolver, verified_outcome="teleported") == {"status": GAP}


def test_non_string_outcome_is_a_gap(resolver):
    assert fire_os_route(resolver, verified_outcome=["gameOpened"]) == {"status": GAP}


def test_unparseable_timestamp_is_a_gap(resolver):
    assert fire_os_route(resolver, verified_at="not-a-timestamp") == {"status": GAP}


def test_non_utc_timestamp_is_a_gap(resolver):
    assert fire_os_route(resolver, verified_at="2026-10-14T18:00:00+02:00") == {"status": GAP}


def test_naive_timestamp_is_a_gap(resolver):
    assert fire_os_route(resolver, verified_at="2026-10-14T18:00:00") == {"status": GAP}


@pytest.mark.parametrize("verified_at", [
    "2026-10-14T18:00:00+00:00:00.000001",
    "2026-10-14T18:00:00+00:00:00",
    "2026-10-14T18:00:00+00:00",
    "2026-10-14T18:00:00-00:00",
    "2026-10-14T18:00:00+0000",
    "2026-10-14T18:00:00.123456Z",
    "2026-10-14",
    "20261014T180000Z",
    "2026-W42-3T18:00Z",
    "2026-10-14 18:00:00Z",
    "2026-10-14T18Z",
    "2026-10-14T18:00Z",
    "2026-02-30T18:00:00Z",
    "2026-10-14T18:00:00Z\n",
    "２０２６-10-14T18:00:00Z",
])
def test_non_canonical_timestamp_is_a_gap(resolver, verified_at):
    assert fire_os_route(resolver, verified_at=verified_at) == {"status": GAP}


def test_missing_outcome_is_a_gap(resolver):
    assert fire_os_route(resolver, verified_outcome=None) == {"status": GAP}


def test_missing_timestamp_is_a_gap(resolver):
    assert fire_os_route(resolver, verified_at=None) == {"status": GAP}


def test_valid_entry_is_verified(resolver):
    route = fire_os_route(resolver, verified_outcome="gameOpened",
                          verified_at="2026-10-14T18:00:00Z")
    assert route["status"] == "verified", route
    assert route["verified_outcome"] == "gameOpened", route
    assert route["package"] == "test.alpha.firetv", route


def test_landed_registry_routes_resolve_as_before():
    module = require_module("provider_resolver")
    providers = json.loads(LANDED_REGISTRY.read_text())["providers"]
    resolved = {p["id"]: module._route(p)["platform_routes"] for p in providers}
    prime_fire_os = providers[0]["platform_routes"]["fire_os"]
    youtube_tv = next(p for p in providers if p["id"] == "youtube_tv")
    youtube_fire_os = youtube_tv["platform_routes"]["fire_os"]
    assert resolved == {
        "prime_video": {"fire_os": dict(prime_fire_os, status="verified"),
                        "vega": {"status": GAP}},
        "espn": {"fire_os": {"status": GAP}, "vega": {"status": GAP}},
        "directv_stream": {"fire_os": {"status": GAP}, "vega": {"status": GAP}},
        "youtube_tv": {"fire_os": dict(youtube_fire_os, status="verified"),
                       "vega": {"status": GAP}},
        "local_broadcast": {"fire_os": {"status": GAP}, "vega": {"status": GAP}},
    }
    assert resolved["prime_video"]["fire_os"]["package"] == "com.amazon.firebat"
    assert resolved["prime_video"]["fire_os"]["verified_outcome"] == "searchOpened"
    assert resolved["prime_video"]["fire_os"]["verified_at"] == "2026-10-16T20:10:00Z"
    assert resolved["youtube_tv"]["fire_os"]["package"] == "com.amazon.firetv.youtube.tv"
    assert resolved["youtube_tv"]["fire_os"]["verified_outcome"] == "appHomeOpened"
    assert resolved["youtube_tv"]["fire_os"]["verified_at"] == "2026-10-21T13:30:07Z"
    assert resolved["youtube_tv"]["fire_os"]["launch"]["value"] == "https://tv.youtube.com/"
    assert youtube_tv["channels_carried"] == ["ESPN"]
