"""BUG-AFC-B01-AUTH-002: bound the poll retry window, one live session per link."""

import hashlib
import time

from conftest import link_device


def _expire_link(api, code):
    table = api.table("Links")
    [item] = [x for x in table.scan()["Items"] if x.get("code") == code]
    item["expiresAt"] = int(time.time()) - 1
    table.put_item(Item=item)


def test_poll_after_expiry_mints_no_session(api):
    device, token = link_device(api)
    _expire_link(api, device["code"])
    status, body = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and body["state"] == "expired"
    assert "sessionToken" not in body
    import device_auth
    assert device_auth.authenticate(token) == "owner", "minted session outlives the window"


def test_second_linked_poll_supersedes_the_first(api, monkeypatch):
    import store
    deleted = []
    monkeypatch.setattr(store, "delete_session", deleted.append)
    device, first_token = link_device(api)
    assert deleted == [], "first linked poll deletes nothing"
    monkeypatch.setattr(store, "delete_session",
                        lambda h: (deleted.append(h), api.table("Links").delete_item(
                            Key={"pk": "session#" + h})))
    status, retry = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and retry.get("state") == "linked"
    second_token = retry["sessionToken"]
    assert second_token != first_token
    assert deleted == [hashlib.sha256(first_token.encode()).hexdigest()]
    import device_auth
    assert device_auth.authenticate(first_token) is None
    assert device_auth.authenticate(second_token) == "owner"
    status, _ = api.request("GET", "/v1/profile", token=first_token)
    assert status == 401
    status, body = api.request("GET", "/v1/profile", token=second_token)
    assert status == 200 and body["id"] == "owner"
