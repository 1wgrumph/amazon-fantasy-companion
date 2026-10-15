"""Local broadcast red tests (VCASE-AFC-PR-029; spec 4.1.8).

For local CBS/FOX/NBC games the result shows the channel and offers a
carrying provider app when one is installed; otherwise it gives no deep link.
"""

import pytest

from resolver_support import LOCAL_BROADCAST, resolver, seed_pref  # noqa: F401

EVENT = "evt-local-1"


def test_local_channel_with_installed_carrier_offers_its_route(resolver):
    resolver.channels[EVENT] = "CBS"
    seed_pref(order=["beta_tv"], market="Test Market 1")
    resolver.install("test.beta.firetv")
    result = resolver.resolve(EVENT)
    assert (result["provider"], result["channel"]) == ("beta_tv", "CBS"), result
    assert isinstance(result.get("route"), dict), result


def test_local_channel_without_installed_carrier_has_no_deep_link(resolver):
    resolver.channels[EVENT] = "CBS"
    seed_pref(order=["alpha_stream", "beta_tv"], confirmed=["alpha_stream"], market="Test Market 1")
    resolver.install("test.alpha.firetv")
    result = resolver.resolve(EVENT)
    assert result["channel"] == "CBS", result
    assert result.get("provider") is None and result.get("route") is None, result


@pytest.mark.parametrize("channel", LOCAL_BROADCAST)
def test_local_channel_with_no_installed_carrier_shows_channel_only(resolver, channel):
    resolver.channels[EVENT] = channel
    seed_pref(market="Test Market 1")
    resolver.install("test.alpha.firetv", "test.gamma.firetv", "test.gamma.vega")
    result = resolver.resolve(EVENT)
    assert result["channel"] == channel, result
    assert result.get("provider") is None and result.get("route") is None, result
    assert result["accessBasis"] == "unknown", result


def test_local_carrier_installed_only_still_reads_unknown(resolver):
    resolver.channels[EVENT] = "CBS"
    seed_pref(market="Test Market 1")
    resolver.install("test.beta.firetv")
    result = resolver.resolve(EVENT)
    assert result["provider"] == "beta_tv", result
    assert result["accessBasis"] == "unknown", result
