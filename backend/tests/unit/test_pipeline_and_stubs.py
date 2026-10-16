"""PolicyFunction chain wiring and the AFC-STUB interfaces for B02..B07 (host-pytest)."""

import importlib
import json

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


STUBS = [
    ("panel", "project", 2, "P2-B07"),
    ("panel", "snapshot", 2, "P2-B07"),
]


@pytest.mark.parametrize("module,function,arity,slice_id", STUBS)
def test_stubs_name_their_owning_slice(api, module, function, arity, slice_id):
    target = getattr(importlib.import_module(module), function)
    with pytest.raises(NotImplementedError) as error:
        target(*[None] * arity)
    assert str(error.value) == f"AFC-STUB: {module} is implemented by {slice_id}"


def test_provider_registry_starts_empty_in_contract_shape():
    registry = json.loads((BACKEND / "src/provider_resolver/registry.json").read_text())
    assert registry == {"schemaVersion": 1, "providers": [], "currentAttemptObservation": "none"}
