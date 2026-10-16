"""Per-platform route red tests (CONTRACT-AFC-P2-PROVIDER-REGISTRY and
CONTRACT-AFC-P2-API as amended for DEC-AFC-SD-049).

Every returned route carries the provider's whole platform_routes map with
fire_os and vega, each verified or REGISTRY_ROUTE_GAP. A missing or
unverified entry is a gap and is never filled from the other platform.
"""

import json

from resolver_support import EXAMPLE_REGISTRY, resolver, seed_pref  # noqa: F401

EVENT = "evt-espn-3"
GAP = "REGISTRY_ROUTE_GAP"


def registry_entry(provider, platform):
    for item in json.loads(EXAMPLE_REGISTRY.read_text())["providers"]:
        if item["id"] == provider:
            return item["platform_routes"][platform]
    raise KeyError(provider)


def routes_for(resolver, provider, *packages):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=[provider])
    resolver.install(*packages)
    result = resolver.resolve(EVENT)
    assert result["provider"] == provider, result
    routes = (result.get("route") or {}).get("platform_routes")
    assert isinstance(routes, dict), result
    return routes


def test_route_carries_both_platform_entries(resolver):
    routes = routes_for(resolver, "alpha_stream", "test.alpha.firetv")
    assert set(routes) == {"fire_os", "vega"}, routes
    assert all(routes[p].get("status") in ("verified", GAP) for p in routes), routes


def test_verified_entries_carry_their_own_launch_data(resolver):
    routes = routes_for(resolver, "alpha_stream", "test.alpha.firetv")
    for platform in ("fire_os", "vega"):
        entry, source = routes[platform], registry_entry("alpha_stream", platform)
        assert entry.get("status") == "verified", routes
        assert entry.get("package") == source["package"], routes
        assert entry.get("launch") == source["launch"], routes


def test_missing_vega_entry_is_a_gap_not_filled_from_fire_os(resolver):
    routes = routes_for(resolver, "beta_tv", "test.beta.firetv")
    fire_os = registry_entry("beta_tv", "fire_os")
    assert routes["fire_os"].get("status") == "verified", routes
    assert routes["vega"].get("status") == GAP, routes
    assert fire_os["package"] not in json.dumps(routes["vega"]), routes
    assert fire_os["launch"]["value"] not in json.dumps(routes["vega"]), routes


def test_unverified_fire_os_entry_is_a_gap_not_filled_from_vega(resolver):
    routes = routes_for(resolver, "gamma_live", "test.gamma.vega")
    vega = registry_entry("gamma_live", "vega")
    assert routes["vega"].get("status") == "verified", routes
    assert routes["fire_os"].get("status") == GAP, routes
    assert vega["package"] not in json.dumps(routes["fire_os"]), routes
    assert vega["launch"]["value"] not in json.dumps(routes["fire_os"]), routes


def test_registry_verified_outcome_is_not_access(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["beta_tv"])
    resolver.install("test.beta.firetv")
    result = resolver.resolve(EVENT)
    assert result["provider"] == "beta_tv", result
    assert result["accessBasis"] == "unknown", result
