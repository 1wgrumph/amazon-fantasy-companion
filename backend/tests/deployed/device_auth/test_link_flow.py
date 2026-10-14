"""Deployed DES-AFC-P2-AUTH link flow (SEIT-AFC-PR-038; L02/L03 execution)."""

from deployed_helpers import assert_error, call


def test_issue_returns_a_pending_code(deployed):
    status, device = call(deployed.base, "POST", "/v1/link")
    assert status == 201, device
    assert len(device["code"]) == 8 and device["handle"] != device["code"]
    assert "sessionToken" not in device
    status, polled = call(deployed.base, "GET", "/v1/link?handle=" + device["handle"])
    assert status == 200 and polled["state"] == "codePending", polled


def test_pending_poll_cannot_authorize_the_device(deployed):
    _, device = call(deployed.base, "POST", "/v1/link")
    status, body = call(deployed.base, "GET", "/v1/profile", token=device["handle"])
    assert_error(status, body, 401)


def test_confirmed_device_polls_a_usable_session(linked):
    status, body = call(linked.base, "GET", "/v1/profile", token=linked.token)
    assert status == 200 and body["id"] == linked.profile, body


def test_unknown_session_is_rejected_on_protected_routes(deployed):
    for method, path in [("GET", "/v1/profile"), ("GET", "/v1/alerts"),
                         ("PUT", "/v1/profile")]:
        status, body = call(deployed.base, method, path, token="unknown-test-session",
                            body={"revision": 0, "data": {}} if method == "PUT" else None)
        assert_error(status, body, 401)
