"""DES-AFC-P2-AUTH edge cases beyond the frozen P2-B01T cases (host-pytest)."""

import hashlib

import pytest

from conftest import link_device


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


def test_only_the_first_linked_poll_carries_the_session(api, auth):
    device, token = link_device(api)
    assert auth.poll(device["handle"]) == {"state": "linked"}
    assert auth.poll("unknown-handle") == {"state": "unlinked"}
    assert auth.authenticate(token) == "owner"
    [session] = [x for x in api.table("Links").scan()["Items"] if "sessionHash" in x]
    assert session["profileId"] == "owner"
    assert session["linkedAt"].endswith("Z") and len(session["linkedAt"]) == 20


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
