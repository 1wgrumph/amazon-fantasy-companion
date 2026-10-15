"""Detector report and RoutingOutcome record red tests (AFC-PR-003 input,
VCASE-AFC-PR-031 backend record, VCASE-AFC-PR-033).

The detector report is stored as an untrusted installed fact; the outcome
record keeps exactly one of the six modeled values and rejects others.
"""

import pytest

from resolver_support import PROFILE, attempt, resolver, seed_pref  # noqa: F401

OUTCOMES = ("gameOpened", "searchOpened", "appHomeOpened", "appAbsent",
            "accessUnknown", "playbackDenied")


def test_installed_report_is_stored_and_returned(resolver):
    record = resolver.install("test.alpha.firetv", "test.beta.firetv")
    assert isinstance(record, dict), record
    assert sorted(record.get("packages", [])) == ["test.alpha.firetv", "test.beta.firetv"], record


def test_latest_installed_report_replaces_the_previous_one(resolver):
    resolver.install("test.alpha.firetv")
    record = resolver.install("test.beta.firetv")
    assert record.get("packages") == ["test.beta.firetv"], record
    resolver.channels["evt-r1"] = "ESPN"
    seed_pref(order=["alpha_stream", "beta_tv"])
    assert resolver.resolve("evt-r1")["provider"] == "beta_tv"


def test_installed_report_does_not_create_access_confirmation(resolver):
    seed_pref(order=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    import store
    pref = store.get_profile(PROFILE)["settings"]["providerPref"]
    assert pref["confirmedAccess"] == [], pref


@pytest.mark.parametrize("outcome", OUTCOMES)
def test_each_modeled_outcome_is_recorded(resolver, outcome):
    record = attempt(resolver.module.record_outcome, PROFILE, "evt-o1", outcome)
    assert isinstance(record, dict), record
    assert record.get("outcome") == outcome and record.get("eventId") == "evt-o1", record


@pytest.mark.parametrize("outcome", ["launched", "success", "", None])
def test_invented_outcome_is_rejected(resolver, outcome):
    try:
        attempt(resolver.module.record_outcome, PROFILE, "evt-o2", outcome)
    except ValueError:
        return
    raise AssertionError(f"record_outcome accepted invented outcome {outcome!r}")


def test_game_opened_outcome_does_not_verify_access(resolver):
    resolver.channels["evt-o3"] = "ESPN"
    seed_pref(order=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    attempt(resolver.module.record_outcome, PROFILE, "evt-o3", "gameOpened")
    assert resolver.resolve("evt-o3")["accessBasis"] == "unknown"
