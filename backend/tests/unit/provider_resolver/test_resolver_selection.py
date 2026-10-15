"""Provider selection red tests (VCASE-AFC-PR-029, -034; DES-AFC-P2-RESOLVE).

The resolver picks among installed providers that carry the event's channel
in the customer's preference order; the registry (spike) order never
overrides it. Output names provider, channel and the registry route.
"""

import json

from resolver_support import LANDED_REGISTRY, attempt, resolver, seed_pref  # noqa: F401

EVENT = "evt-espn-2"
CONTESTED = ("test.alpha.firetv", "test.beta.firetv", "test.gamma.vega")


def test_resolution_names_provider_channel_and_route(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    result = resolver.resolve(EVENT)
    assert (result["provider"], result["channel"]) == ("alpha_stream", "ESPN"), result
    assert isinstance(result.get("route"), dict), result


def test_preference_selects_among_installed_carriers(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["gamma_live", "beta_tv", "alpha_stream"])
    resolver.install(*CONTESTED)
    assert resolver.resolve(EVENT)["provider"] == "gamma_live"


def test_preference_change_reroutes_contested_game(resolver):
    resolver.channels[EVENT] = "ESPN"
    resolver.install(*CONTESTED)
    seed_pref(order=["beta_tv", "alpha_stream"])
    first = resolver.resolve(EVENT)["provider"]
    import store
    stored = store.get_profile("owner")
    pref = dict(stored["settings"]["providerPref"], order=["alpha_stream", "beta_tv"])
    assert store.put_profile("owner", {"providerPref": pref}, stored["revision"],
                             "2026-10-15T12:05:00Z")
    second = resolver.resolve(EVENT)["provider"]
    assert (first, second) == ("beta_tv", "alpha_stream")


def test_spike_order_does_not_override_preference(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["beta_tv"])
    resolver.install("test.alpha.firetv", "test.beta.firetv")
    assert resolver.resolve(EVENT)["provider"] == "beta_tv"


def test_uninstalled_preferred_provider_falls_to_next_installed_preference(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["gamma_live", "alpha_stream"])
    resolver.install("test.alpha.firetv")
    assert resolver.resolve(EVENT)["provider"] == "alpha_stream"


def test_no_carrier_for_channel_gives_no_route(resolver):
    resolver.channels[EVENT] = "Test Network Z"
    seed_pref(order=["alpha_stream"], confirmed=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    result = resolver.resolve(EVENT)
    assert result["channel"] == "Test Network Z", result
    assert result.get("provider") is None and result.get("route") is None, result
    assert result["accessBasis"] == "unknown", result


def test_registry_is_read_only(resolver):
    before = resolver.registry.read_bytes()
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    resolver.resolve(EVENT)
    assert resolver.registry.read_bytes() == before


def test_default_registry_is_the_landed_document(api):
    from resolver_support import require_module
    module = require_module("provider_resolver")
    path = getattr(module, "REGISTRY_PATH", None)
    assert path is not None, "provider_resolver.REGISTRY_PATH is not defined"
    assert LANDED_REGISTRY.resolve() == type(LANDED_REGISTRY)(path).resolve()
    assert json.loads(LANDED_REGISTRY.read_text())["schemaVersion"] == 1


def test_landed_empty_registry_resolves_no_route(api, monkeypatch):
    from resolver_support import PROFILE, require_module
    module = require_module("provider_resolver")
    monkeypatch.setattr(module, "event_channel", {EVENT: "ESPN"}.get, raising=False)
    seed_pref(order=["alpha_stream"], confirmed=["alpha_stream"])
    result = attempt(module.resolve, PROFILE, EVENT)
    assert isinstance(result, dict), result
    assert result.get("provider") is None and result.get("route") is None, result
    assert result.get("accessBasis") == "unknown", result
