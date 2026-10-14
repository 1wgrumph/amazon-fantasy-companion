"""CONTRACT-AFC-P2-API router behavior beyond the frozen P2-B01T cases (host-pytest)."""

import base64
import json
import re
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from conftest import link_device


def call(method, path, raw="", token=None, query=None, b64=False, headers=None):
    import api.handler
    headers = dict(headers or {})
    if token is not None:
        headers["authorization"] = "Bearer " + token
    event = {"rawPath": path, "requestContext": {"http": {"method": method}},
             "headers": headers, "queryStringParameters": query, "body": raw,
             "isBase64Encoded": b64}
    response = api.handler.lambda_handler(event, SimpleNamespace())
    return response["statusCode"], response


def error_of(response):
    return json.loads(response["body"])["error"]


@pytest.fixture
def owner(api):
    return link_device(api)[1]


def test_unknown_route_is_a_structured_404(api):
    status, response = call("DELETE", "/v1/profile")
    assert status == 404
    assert error_of(response) == {"code": "not_found", "message": "Unknown route."}


def test_body_limit_is_exactly_64_kib(api):
    exact = '{"p":"' + "x" * (65536 - 8) + '"}'
    assert len(exact.encode()) == 65536
    assert call("POST", "/v1/link", exact)[0] == 201
    status, response = call("POST", "/v1/link", exact[:-2] + 'x"}')
    assert status == 400
    assert error_of(response) == {"code": "payload_too_large",
                                  "message": "Request body exceeds 64 KiB."}


def test_base64_bodies_are_decoded_and_bad_encodings_rejected(api):
    encoded = base64.b64encode(b'{"code": "x"}').decode()
    status, response = call("POST", "/v1/link/confirm", encoded, b64=True)
    assert status == 400 and error_of(response)["message"] == "Field passphrase is missing or invalid."
    assert call("POST", "/v1/link", "e30=", b64=True)[0] == 201
    for raw in ["not base64!", "e30=\n!", base64.b64encode(b"\xff\xfe").decode()]:
        status, response = call("POST", "/v1/link", raw, b64=True)
        assert status == 400
        assert error_of(response) == {"code": "invalid_request",
                                      "message": "Request body must be UTF-8 JSON."}


def test_non_object_json_is_rejected(api):
    for raw in ["[1]", "not json"]:
        status, response = call("POST", "/v1/link", raw)
        assert status == 400
        assert error_of(response) == {"code": "invalid_request",
                                      "message": "Request body must be a JSON object."}
    assert call("POST", "/v1/link", "  ")[0] == 201


def test_json_responses_are_not_cached(api):
    status, response = call("POST", "/v1/link")
    assert status == 201
    assert response["headers"] == {"content-type": "application/json", "cache-control": "no-store"}


def test_bearer_scheme_is_case_insensitive_and_other_schemes_refused(api, owner):
    assert call("GET", "/v1/profile", headers={"authorization": "bearer " + owner})[0] == 200
    assert call("GET", "/v1/profile", headers={"authorization": "Bearer  " + owner})[0] == 200
    status, response = call("GET", "/v1/profile", headers={"authorization": "Basic " + owner})
    assert status == 401
    assert error_of(response) == {"code": "unauthenticated",
                                  "message": "A linked device session is required."}
    status, response = call("GET", "/v1/profile", token=owner, query={"profileId": "foreign"})
    assert error_of(response) == {"code": "forbidden",
                                  "message": "This device is not linked to that profile."}
    status, response = call("GET", "/v1/profile", '{"profileId": "foreign"}', owner)
    assert status == 403


@pytest.mark.parametrize("selector", [[], {}, 1, True, None])
def test_non_string_profile_selectors_are_rejected_without_mutation(api, owner, selector):
    before = api.table("Profiles").scan()["Items"]
    status, response = call("PUT", "/v1/profile",
                            json.dumps({"profileId": selector, "revision": 0, "data": {}}), owner)
    assert status == 400
    assert error_of(response) == {"code": "invalid_request",
                                  "message": "Field profileId must be a string."}
    assert api.table("Profiles").scan()["Items"] == before
    status, response = call("GET", "/v1/profile", token=owner, query={"profileId": selector})
    assert status == 400
    assert error_of(response)["code"] == "invalid_request"


def test_profile_reads_defaults_and_writes_with_revision_checks(api, owner):
    status, response = call("GET", "/v1/profile", token=owner)
    body = json.loads(response["body"])
    assert status == 200 and body["revision"] == 0 and body["data"] == {"scoringPreset": "halfPpr"}
    assert body["schemaVersion"] == 1 and body["id"] == "owner" and body["source"] == "manual"
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", body["updatedAt"])
    settings = {"scoringPreset": "ppr", "spoilerDelay": 1.5, "frequency": 30}
    status, response = call("PUT", "/v1/profile", json.dumps({"revision": 0, "data": settings}), owner)
    written = json.loads(response["body"])
    assert status == 200 and written["revision"] == 1 and written["data"] == settings
    assert isinstance(written["data"]["frequency"], int)
    status, response = call("PUT", "/v1/profile", json.dumps({"revision": 0, "data": {}}), owner)
    assert status == 409
    assert error_of(response) == {"code": "revision_conflict",
                                  "message": "The profile changed; read it and merge first."}
    status, response = call("GET", "/v1/profile", token=owner)
    assert json.loads(response["body"]) == written
    assert isinstance(json.loads(response["body"])["data"]["frequency"], int)
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", written["updatedAt"])


@pytest.mark.parametrize("body", [
    {"revision": "0", "data": {}}, {"revision": True, "data": {}}, {"revision": -1, "data": {}},
    {"revision": 0, "data": []}, {"revision": 0}, {"data": {}},
    {"revision": 0, "data": {"unknown": 1}}, {"revision": 0, "data": {"scoringPreset": "full"}},
])
def test_invalid_profile_updates_change_nothing(api, owner, body):
    status, response = call("PUT", "/v1/profile", json.dumps(body), owner)
    assert status == 400
    assert error_of(response) == {"code": "invalid_request",
                                  "message": "Profile needs revision and valid Settings data."}
    assert api.table("Profiles").scan()["Items"] == []


def test_oversize_profile_envelope_is_rejected_without_mutation(api, owner):
    assert call("PUT", "/v1/profile", json.dumps({"revision": 0, "data": {"scoringPreset": "ppr"}}),
                owner)[0] == 200
    pad = 65536 - len(json.dumps({"revision": 1, "data": {"fantasySelections": ""}}).encode())
    body = json.dumps({"revision": 1, "data": {"fantasySelections": "x" * pad}})
    assert len(body.encode()) == 65536
    status, response = call("PUT", "/v1/profile", body, owner)
    assert status == 400
    assert error_of(response) == {"code": "payload_too_large",
                                  "message": "Profile response would exceed 64 KiB."}
    [item] = api.table("Profiles").scan()["Items"]
    assert item["revision"] == 1 and item["settings"] == {"scoringPreset": "ppr"}
    status, response = call("GET", "/v1/profile", token=owner)
    assert status == 200 and json.loads(response["body"])["revision"] == 1


def test_profile_envelope_exactly_at_64kib_is_stored(api, owner):
    import api.handler
    probe = {"revision": 1, "updatedAt": "2020-01-01T00:00:00Z",
             "settings": {"fantasySelections": ""}}
    room = 65536 - len(json.dumps(api.handler._profile("owner", probe)).encode())
    value = "é" * (room // 6) + "x" * (room % 6)  # dumps escapes é as \u00e9: 6 bytes
    body = json.dumps({"revision": 0, "data": {"fantasySelections": value}})
    assert len(body.encode()) < 65536
    status, response = call("PUT", "/v1/profile", body, owner)
    assert status == 200
    assert len(response["body"].encode()) == 65536


def test_response_cap_counts_serialized_bytes_not_characters(api, owner):
    overhead = len(json.dumps({"revision": 0, "data": {"fantasySelections": ""}}).encode())
    value = "é" * ((65536 - overhead - 10) // 2) + '"\\\n'
    body = json.dumps({"revision": 0, "data": {"fantasySelections": value}}, ensure_ascii=False)
    assert len(body.encode()) <= 65536  # raw UTF-8 request fits
    assert len(body) < 65536  # character counting claims the response fits too
    status, response = call("PUT", "/v1/profile", body, owner)
    assert status == 400
    assert error_of(response) == {"code": "payload_too_large",
                                  "message": "Profile response would exceed 64 KiB."}
    assert api.table("Profiles").scan()["Items"] == []


def test_oversize_json_responses_fail_closed(api):
    import api.handler
    with pytest.raises(api.handler.ApiError) as error:
        api.handler._respond(200, {"pad": "x" * 70000})
    assert (error.value.status, error.value.code, error.value.message) == (
        503, "unavailable", "The response exceeds the 64 KiB contract.")
    exact = api.handler._respond(200, {"pad": "x" * (65536 - len('{"pad": ""}'))})
    assert len(exact["body"].encode()) == 65536


@pytest.mark.parametrize("field", sorted([
    "fantasySelections", "teamLeague", "alertTypes", "frequency", "quietHours",
    "gameDayPeriods", "spoilerDelay", "presentation", "voice", "excitement", "providerPref",
    "switchingConfirm", "panelPrefs", "detectionOptIn"]))
def test_every_settings_attribute_is_accepted(api, owner, field):
    body = {"revision": 0, "data": {field: "x", "scoringPreset": "halfPpr"}}
    assert call("PUT", "/v1/profile", json.dumps(body), owner)[0] == 200


@pytest.mark.parametrize("outcome", ["gameOpened", "searchOpened", "appHomeOpened", "appAbsent",
                                     "accessUnknown", "playbackDenied"])
def test_valid_routing_outcomes_reach_the_resolver_stub(api, owner, outcome):
    status, response = call("POST", "/v1/routing-outcome",
                            json.dumps({"eventId": "e1", "outcome": outcome}), owner)
    assert status == 503
    assert error_of(response) == {"code": "not_implemented",
                                  "message": "This feature is not available yet."}


def test_routing_outcomes_are_validated(api, owner):
    status, response = call("POST", "/v1/routing-outcome",
                            json.dumps({"eventId": "e1", "outcome": "launched"}), owner)
    assert status == 400 and error_of(response) == {
        "code": "invalid_request", "message": "Field outcome is missing or invalid."}
    status, response = call("POST", "/v1/routing-outcome", json.dumps({"outcome": "appAbsent"}), owner)
    assert status == 400 and error_of(response)["message"] == "Field eventId is missing or invalid."


def test_installed_apps_are_validated(api, owner):
    for packages in ["com.a", ["com a"], [1], ["x" * 256], ["com.a"] * 501]:
        status, response = call("POST", "/v1/installed-apps", json.dumps({"packages": packages}), owner)
        assert status == 400 and error_of(response) == {
            "code": "invalid_request", "message": "Field packages must list package names."}
    for packages in [[], ["com.amazon.Prime_video.1"] * 500, ["x" * 255]]:
        status, _ = call("POST", "/v1/installed-apps", json.dumps({"packages": packages}), owner)
        assert status == 503


def test_stub_routes_receive_the_session_profile_and_query(api, owner, monkeypatch):
    import alert_policy
    import panel
    import provider_resolver
    seen = []
    monkeypatch.setattr(alert_policy, "pending", lambda *a: seen.append(a) or {"alerts": []})
    monkeypatch.setattr(panel, "snapshot", lambda *a: seen.append(a) or {"id": "p"})
    monkeypatch.setattr(provider_resolver, "resolve", lambda *a: seen.append(a) or {"accessBasis": "unknown"})
    monkeypatch.setattr(provider_resolver, "record_outcome", lambda *a: seen.append(a) or {"ok": 1})
    monkeypatch.setattr(provider_resolver, "record_installed_apps", lambda *a: seen.append(a) or {"ok": 2})
    assert call("GET", "/v1/alerts", token=owner, query={"cursor": "c1"})[0] == 200
    assert call("GET", "/v1/panel", token=owner, query={"teamLeague": "T/L"})[0] == 200
    assert call("GET", "/v1/providers", token=owner, query={"eventId": "e9"})[0] == 200
    assert call("POST", "/v1/routing-outcome", '{"eventId": "e9", "outcome": "appAbsent"}', owner)[0] == 200
    status, response = call("POST", "/v1/installed-apps", '{"packages": ["com.a"]}', owner)
    assert status == 200 and json.loads(response["body"]) == {"ok": 2}
    assert seen == [("owner", "c1"), ("owner", "T/L"), ("owner", "e9"),
                    ("owner", "e9", "appAbsent"), ("owner", ["com.a"])]


def test_unexpected_failures_return_a_safe_503(api, owner, monkeypatch):
    import store

    def broken(profile_id):
        raise RuntimeError("internal detail")

    monkeypatch.setattr(store, "get_profile", broken)
    status, response = call("GET", "/v1/profile", token=owner)
    assert status == 503
    assert error_of(response) == {"code": "unavailable",
                                  "message": "The service is temporarily unavailable."}


def test_link_confirm_validates_fields_and_maps_results(api):
    import device_auth
    device = json.loads(call("POST", "/v1/link")[1]["body"])
    cases = [({"code": "X" * 17, "passphrase": api.passphrase, "profileId": "owner"}, "code"),
             ({"code": "ab-c d", "passphrase": "", "profileId": "owner"}, "passphrase"),
             ({"code": device["code"], "passphrase": "p" * 257, "profileId": "owner"}, "passphrase"),
             ({"code": device["code"], "passphrase": api.passphrase, "profileId": "a/b"}, "profileId"),
             ({"code": device["code"], "passphrase": api.passphrase, "profileId": "o" * 65}, "profileId")]
    for body, field in cases:
        status, response = call("POST", "/v1/link/confirm", json.dumps(body))
        assert status == 400 and error_of(response) == {
            "code": "invalid_request", "message": f"Field {field} is missing or invalid."}
    status, response = call("POST", "/v1/link/confirm", json.dumps(
        {"code": device["code"], "passphrase": "wrong", "profileId": "owner"}))
    assert status == 401 and error_of(response) == {
        "code": "unauthenticated", "message": "The link passphrase is not correct."}
    status, response = call("POST", "/v1/link/confirm", json.dumps(
        {"code": "ZZZZ2222", "passphrase": api.passphrase, "profileId": "owner"}))
    assert status == 410 and error_of(response) == {
        "code": "code_expired", "message": "This code is expired, used or unknown."}
    status, response = call("POST", "/v1/link/confirm", json.dumps(
        {"code": device["code"].lower(), "passphrase": api.passphrase, "profileId": "O_w-1"}))
    assert status == 200 and json.loads(response["body"]) == {"state": "linked"}
    assert device_auth.poll(device["handle"])["state"] == "linked"


def test_link_poll_requires_a_handle(api):
    status, response = call("GET", "/v1/link", query={})
    assert status == 400 and error_of(response) == {
        "code": "invalid_request", "message": "Field handle is missing or invalid."}
    status, response = call("GET", "/v1/link", query={"handle": "unknown"})
    assert status == 200 and json.loads(response["body"]) == {"state": "unlinked"}


def test_link_page_is_framed_by_strict_headers(api):
    import base64
    import hashlib
    status, response = call("GET", "/link")
    assert status == 200
    headers = response["headers"]
    assert headers["content-type"] == "text/html; charset=utf-8"
    assert headers["cache-control"] == "no-store" and headers["x-frame-options"] == "DENY"
    assert headers["referrer-policy"] == "no-referrer"
    assert headers["content-security-policy"] == (
        "default-src 'none'; script-src 'sha256-r5vvOH35j5Xp1ecjHhZ7oNRmS7/Xlp/C7RNPviHqeT8='; "
        "style-src 'unsafe-inline'; connect-src 'self'; form-action 'self'; "
        "frame-ancestors 'none'")
    script_src = [d for d in headers["content-security-policy"].split("; ")
                  if d.startswith("script-src ")][0]
    assert "'unsafe-inline'" not in script_src
    [script] = response["body"].split("<script>")[1:]
    script = script.split("</script>")[0]
    digest = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
    assert f"'sha256-{digest}'" in script_src
    assert 'action="/v1/link/confirm"' in response["body"]
    assert 'addEventListener("submit"' in response["body"]


def test_only_decimal_values_are_serialized_as_numbers(api):
    import api.handler
    with pytest.raises(TypeError) as error:
        api.handler._number(object())
    assert str(error.value) == "object"


def test_api_errors_carry_their_message(api):
    import api.handler
    error = api.handler.ApiError(418, "teapot", "short and stout")
    assert (str(error), error.status, error.code, error.message) == (
        "short and stout", 418, "teapot", "short and stout")


def test_timestamps_are_utc_now(api, owner):
    body = json.loads(call("GET", "/v1/profile", token=owner)[1]["body"])
    stamp = datetime.strptime(body["updatedAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    assert abs((datetime.now(timezone.utc) - stamp).total_seconds()) < 120


def test_stored_profile_timestamps_are_returned_unchanged(api, owner):
    import store
    store.put_profile("owner", {"voice": "amy"}, 0, "2020-01-01T00:00:00Z")
    body = json.loads(call("GET", "/v1/profile", token=owner)[1]["body"])
    assert body["updatedAt"] == "2020-01-01T00:00:00Z" and body["revision"] == 1


def test_a_profile_may_set_every_settings_attribute_at_once(api, owner):
    data = {field: "x" for field in [
        "fantasySelections", "teamLeague", "alertTypes", "frequency", "quietHours",
        "gameDayPeriods", "spoilerDelay", "presentation", "voice", "excitement", "providerPref",
        "switchingConfirm", "panelPrefs", "detectionOptIn"]}
    data["scoringPreset"] = "ppr"
    assert call("PUT", "/v1/profile", json.dumps({"revision": 0, "data": data}), owner)[0] == 200


def test_unhandled_failures_are_logged_without_detail_in_the_response(api, owner, monkeypatch, caplog):
    import store
    monkeypatch.setattr(store, "get_profile", lambda p: 1 / 0)
    with caplog.at_level("ERROR"):
        status, response = call("GET", "/v1/profile", token=owner)
    assert status == 503 and "division" not in response["body"]
    assert [(r.name, r.getMessage()) for r in caplog.records] == [("api.handler", "Unhandled API failure")]
