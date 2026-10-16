"""Verified-route field checks (CONTRACT-AFC-P2-PROVIDER-REGISTRY).

A platform entry is verified only when verified_outcome is a defined
RoutingOutcome and verified_at is an ISO-8601 UTC timestamp; any other
entry is a REGISTRY_ROUTE_GAP and its launch data is never served.
"""

import json

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
    for provider in json.loads(LANDED_REGISTRY.read_text())["providers"]:
        routes = module._route(provider)["platform_routes"]
        for platform in module.PLATFORMS:
            entry = (provider.get("platform_routes") or {}).get(platform) or {}
            before = ("verified" if entry.get("verified_outcome") and entry.get("verified_at")
                      else GAP)
            assert routes[platform]["status"] == before, (provider["id"], platform, entry)
