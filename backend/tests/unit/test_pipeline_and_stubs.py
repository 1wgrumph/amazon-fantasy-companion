"""PolicyFunction chain wiring and the AFC-STUB interfaces for B02..B07 (host-pytest)."""

import copy
import importlib
import json
from datetime import datetime

import pytest
from boto3.dynamodb.types import TypeSerializer

from conftest import BACKEND


def record(name, image):
    serialize = TypeSerializer().serialize
    return {"eventName": name, "dynamodb": {"NewImage": {k: serialize(v) for k, v in image.items()}}}


def test_policy_chain_runs_in_order_and_stores_routed_alerts(api, monkeypatch):
    import alert_policy
    import matcher
    import panel
    import pipeline.handler
    import provider_resolver
    calls = []
    monkeypatch.setattr(matcher, "resolve", lambda e: calls.append(("match", e["eventId"])) or ["m"])
    monkeypatch.setattr(alert_policy, "evaluate", lambda e, m: calls.append(("policy", m)) or [
        {"profileId": "owner", "cursor": "c-" + e["eventId"], "eventId": e["eventId"]}])
    monkeypatch.setattr(provider_resolver, "resolve",
                        lambda p, e: calls.append(("route", p, e)) or "route-" + e)
    monkeypatch.setattr(panel, "project", lambda e, m: calls.append(("panel", e["eventId"], m)))
    event = {"Records": [record("INSERT", {"gameId": "g", "eventId": "e1", "revision": 1}),
                         record("REMOVE", {"gameId": "g", "eventId": "e0"}),
                         record("MODIFY", {"gameId": "g", "eventId": "e2", "revision": 2})]}
    assert pipeline.handler.lambda_handler(event, None) is None
    assert calls == [("match", "e1"), ("policy", ["m"]), ("route", "owner", "e1"),
                     ("panel", "e1", ["m"]), ("match", "e2"), ("policy", ["m"]),
                     ("route", "owner", "e2"), ("panel", "e2", ["m"])]
    alerts = api.table("Alerts").scan()["Items"]
    assert sorted((a["cursor"], a["providerRoute"]) for a in alerts) == [
        ("c-e1", "route-e1"), ("c-e2", "route-e2")]
    calls.clear()
    pipeline.handler.lambda_handler({}, None)
    assert calls == []


def test_stream_images_are_deserialized(api):
    import pipeline.handler
    images = pipeline.handler._game_events({"Records": [
        record("INSERT", {"gameId": "g", "eventId": "e", "revision": 3, "playerIds": "1"})]})
    assert images == [{"gameId": "g", "eventId": "e", "revision": 3, "playerIds": "1"}]


STUBS = []


@pytest.mark.parametrize("module,function,arity,slice_id", STUBS)
def test_stubs_name_their_owning_slice(api, module, function, arity, slice_id):
    target = getattr(importlib.import_module(module), function)
    with pytest.raises(NotImplementedError) as error:
        target(*[None] * arity)
    assert str(error.value) == f"AFC-STUB: {module} is implemented by {slice_id}"


SPIKE_ORDER = ["prime_video", "espn", "directv_stream", "youtube_tv", "local_broadcast"]
ROUTING_OUTCOMES = ("gameOpened", "searchOpened", "appHomeOpened", "appAbsent",
                    "accessUnknown", "playbackDenied")
# Verified fire_os routes are only those with on-device evidence: Prime Video
# (spikes/sp3-provider-links/VERDICT.md) and YouTube TV
# (evidence/nba/ytv-route/). Every other provider stays a gap.
EVIDENCED_ROUTES = {"prime_video": {"fire_os"}, "youtube_tv": {"fire_os"}}


def _parse_timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    assert parsed.tzinfo is not None, f"verified_at has no timezone: {value!r}"


def assert_registry_contract(registry):
    # CONTRACT-AFC-P2-PROVIDER-REGISTRY: spike order; a verified route carries
    # one of the six RoutingOutcome values and a parseable verification time;
    # absent providers carry no route, so no route can be invented for them.
    assert registry["schemaVersion"] == 1
    assert registry["currentAttemptObservation"] == "none"
    assert [p["id"] for p in registry["providers"]] == SPIKE_ORDER, "provider order"
    assert [p["name"] for p in registry["providers"]] == [
        "Prime Video", "ESPN", "DirecTV Stream", "YouTube TV", "Local broadcast"]
    for provider in registry["providers"]:
        assert isinstance(provider["channels_carried"], list)
        assert set(provider["platform_routes"]) <= {"fire_os", "vega"}
        evidenced = EVIDENCED_ROUTES.get(provider["id"], set())
        assert set(provider["platform_routes"]) == evidenced, (
            f"{provider['id']}: evidenced routes are {sorted(evidenced)}, "
            f"registry carries {sorted(provider['platform_routes'])}")
        for route in provider["platform_routes"].values():
            assert route["package"] and route["doc_source"]
            assert route["launch"]["type"] in ("intent", "uri") and route["launch"]["value"]
            assert route["verified_outcome"] in ROUTING_OUTCOMES, (
                f"verified_outcome not a RoutingOutcome: {route['verified_outcome']!r}")
            _parse_timestamp(route["verified_at"])
            assert "currentAttemptObservation" in route


def _committed_registry():
    return json.loads((BACKEND / "src/provider_resolver/registry.json").read_text())


def test_provider_registry_filled_in_contract_shape():
    assert_registry_contract(_committed_registry())


def _prime_route(registry):
    return registry["providers"][0]["platform_routes"]["fire_os"]


def _mutate_invalid_outcome(registry):
    _prime_route(registry)["verified_outcome"] = "teleported"


def _mutate_invalid_timestamp(registry):
    _prime_route(registry)["verified_at"] = "not-a-timestamp"


def _mutate_missing_timestamp(registry):
    del _prime_route(registry)["verified_at"]


def _mutate_fabricated_absent_route(registry):
    registry["providers"][1]["platform_routes"]["fire_os"] = copy.deepcopy(
        _prime_route(registry))


def _mutate_missing_prime_route(registry):
    registry["providers"][0]["platform_routes"] = {}


def _mutate_reversed_order(registry):
    registry["providers"].reverse()


@pytest.mark.parametrize("mutate,error", [
    (_mutate_invalid_outcome, "verified_outcome not a RoutingOutcome"),
    (_mutate_invalid_timestamp, "Invalid isoformat string"),
    (_mutate_missing_timestamp, "verified_at"),
    (_mutate_fabricated_absent_route, "espn: evidenced routes"),
    (_mutate_missing_prime_route, "prime_video: evidenced routes"),
    (_mutate_reversed_order, "provider order"),
])
def test_provider_registry_contract_rejects_each_malformed_case_alone(mutate, error):
    registry = _committed_registry()
    mutate(registry)
    with pytest.raises((AssertionError, KeyError, ValueError), match=error):
        assert_registry_contract(registry)
