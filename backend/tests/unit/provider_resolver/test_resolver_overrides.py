"""Added coverage (P2-B06): customer appOverrides win over the detector
report, and records persist as stored facts readable outside resolve."""

import store

from resolver_support import PROFILE, attempt, resolver, seed_pref  # noqa: F401

EVENT = "evt-espn-override"


def test_override_off_defeats_detector_report(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["alpha_stream", "beta_tv"],
              overrides={"test.alpha.firetv": False})
    resolver.install("test.alpha.firetv", "test.beta.firetv")
    assert resolver.resolve(EVENT)["provider"] == "beta_tv"


def test_override_on_counts_without_detector_report(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["alpha_stream"], overrides={"test.alpha.firetv": True})
    result = resolver.resolve(EVENT)
    assert result["provider"] == "alpha_stream", result
    assert result["accessBasis"] == "unknown", result


def test_records_are_stored_facts_not_profile_settings(resolver):
    seed_pref(order=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    attempt(resolver.module.record_outcome, PROFILE, EVENT, "playbackDenied")
    state = resolver.module._state_table().get_item(
        Key=resolver.module._state_key(PROFILE)).get("Item")
    assert state["installedPackages"] == ["test.alpha.firetv"], state
    assert state["outcome#" + EVENT] == "playbackDenied", state
    assert store.get_profile(PROFILE)["settings"]["providerPref"]["confirmedAccess"] == []
