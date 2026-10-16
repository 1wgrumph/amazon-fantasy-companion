"""B06-REV-001: opaque saved Settings must not imply access or break resolution."""

import pytest

import store

from resolver_support import PROFILE, resolver  # noqa: F401

EVENT = "fixture-event"


def save_pref(pref):
    assert store.put_profile(PROFILE, {"providerPref": pref}, 0, "2026-10-15T12:00:00Z")


@pytest.mark.parametrize("pref", ["x", ["alpha_stream"], True, 1, None])
def test_opaque_preferences_preserve_unknown_resolution(resolver, pref):
    save_pref(pref)
    result = resolver.resolve(EVENT)
    assert result["provider"] is None and result["route"] is None
    assert result["accessBasis"] == "unknown"


@pytest.mark.parametrize("claim, expected", [
    ({"alpha_stream": False}, "unknown"),
    ("not_alpha_stream", "unknown"),
    (True, "unknown"),
    (["alpha_stream", False], "unknown"),
    (["alpha_stream", {"beta_tv": True}], "unknown"),
    ([], "unknown"),
    (["beta_tv"], "unknown"),
    (["alpha_stream"], "customerConfirmed"),
])
def test_only_explicit_provider_id_list_confirms_selected_provider(resolver, claim, expected):
    resolver.channels[EVENT] = "ESPN"
    resolver.install("test.alpha.firetv")
    save_pref({"order": ["alpha_stream"], "confirmedAccess": claim})
    result = resolver.resolve(EVENT)
    assert result["provider"] == "alpha_stream"
    assert result["accessBasis"] == expected


@pytest.mark.parametrize("pref", [
    {"order": 1},
    {"order": "beta_tv"},
    {"order": ["beta_tv", False]},
    {"appOverrides": "test.alpha.firetv"},
    {"appOverrides": ["test.alpha.firetv"]},
    {"localMarket": {"market": "Test Market 1"}},
])
def test_malformed_nested_preferences_keep_detector_facts_safe(resolver, pref):
    resolver.channels[EVENT] = "ESPN"
    resolver.install("test.alpha.firetv", "test.beta.firetv")
    save_pref(pref)
    result = resolver.resolve(EVENT)
    assert result["provider"] == "alpha_stream"
    assert result["accessBasis"] == "unknown"
    assert result["inputs"]["localMarket"] is None


@pytest.mark.parametrize("value", ["false", 1, [True], {"installed": True}])
def test_non_boolean_override_cannot_invent_installation(resolver, value):
    resolver.channels[EVENT] = "ESPN"
    save_pref({"appOverrides": {"test.alpha.firetv": value},
               "confirmedAccess": ["alpha_stream"]})
    result = resolver.resolve(EVENT)
    assert result["provider"] is None and result["route"] is None
    assert result["accessBasis"] == "unknown"
