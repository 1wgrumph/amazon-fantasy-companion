"""Access basis red tests (VCASE-AFC-PR-004, -032, -033; DES-AFC-P2-RESOLVE).

Installation is a detector fact, never access. Only an explicit customer
confirmation yields customerConfirmed; no entitlement integration exists, so
nothing yields verified. Every unverifiable case reads unknown.
"""

from resolver_support import PROFILE, attempt, resolver, seed_pref  # noqa: F401

EVENT = "evt-espn-1"


def test_installed_only_reads_unknown(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    result = resolver.resolve(EVENT)
    assert result["provider"] == "alpha_stream", result
    assert result["accessBasis"] == "unknown", result


def test_installed_only_never_reads_verified_or_confirmed(resolver):
    resolver.channels[EVENT] = "ESPN"
    resolver.install("test.alpha.firetv", "test.beta.firetv", "test.gamma.firetv", "test.gamma.vega")
    result = resolver.resolve(EVENT)
    assert result["accessBasis"] not in ("verified", "customerConfirmed"), result


def test_customer_confirmation_reads_customer_confirmed(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["alpha_stream"], confirmed=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    result = resolver.resolve(EVENT)
    assert result["provider"] == "alpha_stream", result
    assert result["accessBasis"] == "customerConfirmed", result


def test_confirmation_is_never_promoted_to_verified(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["beta_tv"], confirmed=["beta_tv"])
    resolver.install("test.beta.firetv")
    assert resolver.resolve(EVENT)["accessBasis"] != "verified"


def test_confirmation_of_another_provider_does_not_carry_over(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["alpha_stream"], confirmed=["gamma_live"])
    resolver.install("test.alpha.firetv")
    result = resolver.resolve(EVENT)
    assert result["provider"] == "alpha_stream", result
    assert result["accessBasis"] == "unknown", result


def test_unknown_broadcast_stays_unknown(resolver):
    seed_pref(order=["alpha_stream"], confirmed=["alpha_stream"])
    resolver.install("test.alpha.firetv")
    result = resolver.resolve("evt-no-broadcast")
    assert result.get("channel") is None, result
    assert result.get("provider") is None and result.get("route") is None, result
    assert result["accessBasis"] == "unknown", result


def test_no_profile_and_no_report_reads_unknown(resolver):
    resolver.channels[EVENT] = "ESPN"
    result = resolver.resolve(EVENT)
    assert result["channel"] == "ESPN", result
    assert result["accessBasis"] == "unknown", result


def test_installed_fact_is_recorded_separately_from_access(resolver):
    resolver.channels[EVENT] = "ESPN"
    seed_pref(order=["alpha_stream"], market="Test Market 1")
    resolver.install("test.alpha.firetv")
    result = resolver.resolve(EVENT)
    inputs = result.get("inputs")
    assert isinstance(inputs, dict), result
    assert inputs.get("installed") is True, result
    assert inputs.get("localMarket") == "Test Market 1", result
    assert result["accessBasis"] == "unknown", result


def test_providers_api_reads_unknown_after_installed_report(resolver):
    api = resolver.api
    _, device = api.request("POST", "/v1/link")
    api.request("POST", "/v1/link/confirm", {"code": device["code"], "profileId": PROFILE})
    _, polled = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    token = polled.get("sessionToken")
    assert token, polled
    resolver.channels[EVENT] = "ESPN"
    status, body = resolver.api.request("POST", "/v1/installed-apps",
                                        {"packages": ["test.alpha.firetv"]}, token=token)
    assert status == 200, body
    status, body = resolver.api.request("GET", "/v1/providers", token=token,
                                        query={"eventId": EVENT})
    assert status == 200, body
    assert body.get("accessBasis") == "unknown", body
