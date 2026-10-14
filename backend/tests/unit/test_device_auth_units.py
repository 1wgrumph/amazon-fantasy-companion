"""DES-AFC-P2-AUTH edge cases beyond the frozen P2-B01T cases (host-pytest)."""

import hashlib

import pytest

from conftest import confirm as confirm_http
from conftest import issue as issue_http
from conftest import link_device, scalar_values


@pytest.fixture
def auth(api):
    import device_auth
    return device_auth


def test_issue_retries_code_collisions_three_times(auth, monkeypatch):
    import store
    attempts = []
    monkeypatch.setattr(store, "put_link", lambda *a: attempts.append(a) or len(attempts) == 3)
    device = auth.issue()
    assert len(attempts) == 3 and attempts[-1][0] == device["code"]
    assert attempts[-1][1] == hashlib.sha256(device["handle"].encode()).hexdigest()
    attempts.clear()
    monkeypatch.setattr(store, "put_link", lambda *a: attempts.append(a) and False)
    with pytest.raises(RuntimeError) as error:
        auth.issue()
    assert str(error.value) == "Could not allocate a unique device code" and len(attempts) == 3


def test_issue_stores_the_configured_ttl(auth, monkeypatch, api):
    monkeypatch.setattr(auth.time, "time", lambda: 1_000_000.75)
    device = auth.issue()
    assert device["expires"] == "1970-01-12T13:56:40Z"
    [item] = api.table("Links").scan()["Items"]
    assert item["expiresAt"] == 1_000_600


def test_code_is_pending_until_the_expiry_second(auth, monkeypatch):
    device = auth.issue()
    import store
    expires = int(store.find_link(hashlib.sha256(device["handle"].encode()).hexdigest())["expiresAt"])
    monkeypatch.setattr(auth.time, "time", lambda: expires - 0.5)
    assert auth.poll(device["handle"]) == {"state": "codePending"}
    monkeypatch.setattr(auth.time, "time", lambda: expires)
    assert auth.poll(device["handle"]) == {"state": "expired"}


def test_dropped_linked_poll_response_is_recoverable_by_retry(api):
    device = issue_http(api)
    status, _ = confirm_http(api, device["code"])
    assert status in (200, 201)
    status, first = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and first.get("state") == "linked" and "sessionToken" in first
    # The first response is lost on the wire; the same device retries.
    status, retry = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and retry.get("state") == "linked"
    assert isinstance(retry.get("sessionToken"), str) and retry["sessionToken"]
    status, body = api.request("GET", "/v1/profile", token=retry["sessionToken"])
    assert status == 200 and body["id"] == "owner"
    status, foreign = api.request("GET", "/v1/link", query={"handle": "unknown-handle"})
    assert status == 200 and foreign == {"state": "unlinked"}
    values = scalar_values(api.table("Links").scan()["Items"])
    assert hashlib.sha256(retry["sessionToken"].encode()).hexdigest() in values
    assert retry["sessionToken"] not in values and api.passphrase not in values


def test_linked_poll_retry_keeps_confirm_one_time_and_hashes_only(api, auth):
    device, token = link_device(api)
    retry = auth.poll(device["handle"])
    assert retry["state"] == "linked"
    assert isinstance(retry.get("sessionToken"), str) and retry["sessionToken"]
    assert auth.authenticate(token) is None, "a retry supersedes the previous token"
    assert auth.authenticate(retry["sessionToken"]) == "owner"
    assert auth.poll("unknown-handle") == {"state": "unlinked"}
    assert auth.confirm(device["code"], api.passphrase, "owner") == "gone"
    sessions = [x for x in api.table("Links").scan()["Items"] if "sessionHash" in x]
    assert len(sessions) == 1 and all(s["profileId"] == "owner" for s in sessions)
    assert all(s["linkedAt"].endswith("Z") and len(s["linkedAt"]) == 20 for s in sessions)


def test_failed_session_write_leaves_the_link_recoverable(api, auth, monkeypatch):
    import store
    device = issue_http(api)
    assert auth.confirm(device["code"], api.passphrase, "owner") == "linked"
    real, calls = store.put_session, []
    def flaky(*args):
        calls.append(args)
        if len(calls) == 1:
            raise RuntimeError("DynamoDB unavailable")
        return real(*args)
    monkeypatch.setattr(store, "put_session", flaky)
    with pytest.raises(RuntimeError):
        auth.poll(device["handle"])
    retry = auth.poll(device["handle"])
    assert retry["state"] == "linked"
    assert auth.authenticate(retry["sessionToken"]) == "owner"


def test_confirm_normalizes_the_typed_code(api, auth):
    device = auth.issue()
    assert auth.confirm(" " + device["code"].lower() + " ", api.passphrase, "owner") == "linked"
    assert auth.confirm(device["code"], api.passphrase, "owner") == "gone"
    assert auth.confirm(device["code"], api.passphrase + "x", "owner") == "unauthorized"


def test_empty_token_never_reaches_the_store(auth, monkeypatch):
    import store
    monkeypatch.setattr(store, "get_session", lambda h: pytest.fail("store queried"))
    assert auth.authenticate("") is None
    assert auth.authenticate(None) is None


def test_codes_draw_from_the_unambiguous_alphabet_and_handles_are_256_bit(auth, monkeypatch):
    alphabets = []
    monkeypatch.setattr(auth.secrets, "choice", lambda seq: alphabets.append(seq) or seq[-1])
    device = auth.issue()
    assert set(alphabets) == {"ABCDEFGHJKLMNPQRSTUVWXYZ23456789"} and device["code"] == "99999999"
    assert len(device["handle"]) == 43


def test_session_tokens_are_256_bit(api):
    _, token = link_device(api)
    assert len(token) == 43
