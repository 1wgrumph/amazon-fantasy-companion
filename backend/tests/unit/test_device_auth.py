"""DES-AFC-P2-AUTH; supporting red evidence for SEIT-AFC-PR-038/-055/-058.

Resource group: host-pytest (fresh in-process Moto state, no engine or network).
Expected whole backend red suite: <2 min; no wall-clock sleeps or real credentials.
"""

import base64
import hashlib
from datetime import datetime, timezone

import pytest

from conftest import assert_error, confirm, issue, link_device, scalar_values

pytestmark = pytest.mark.auth
PROTECTED = [
    ("GET", "/v1/profile"), ("PUT", "/v1/profile"),
    ("GET", "/v1/alerts"), ("GET", "/v1/panel"), ("GET", "/v1/providers"),
    ("POST", "/v1/routing-outcome"), ("POST", "/v1/installed-apps"),
]


def test_issue_has_8_character_unambiguous_base32_code_and_600_second_expiry(api):
    before = datetime.now(timezone.utc).timestamp()
    device = issue(api)
    after = datetime.now(timezone.utc).timestamp()
    code = device["code"]
    alphabets = ["ABCDEFGHJKLMNPQRSTUVWXYZ23456789", "0123456789ABCDEFGHJKMNPQRSTVWXYZ"]
    assert len(code) == 8 and any(set(code) <= set(a) for a in alphabets)
    expires = datetime.fromisoformat(device["expires"].replace("Z", "+00:00"))
    assert expires.utcoffset().total_seconds() == 0
    assert before + 599 <= expires.timestamp() <= after + 601
    assert device["handle"] != code, "Polling handle is separate from the displayed code"
    assert "sessionToken" not in device, "Issuance is not customer authorization"


def test_pending_poll_cannot_authorize_the_device(api):
    device = issue(api)
    status, body = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and body["state"] == "codePending"
    assert "sessionToken" not in body
    status, body = api.request("GET", "/v1/profile", token=device["handle"])
    assert_error(status, body, 401)


def test_tv_code_alone_confirms_once_and_returns_256_bit_session(api):
    _, token = link_device(api)
    try:
        raw = bytes.fromhex(token)
    except ValueError:
        raw = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
    assert len(raw) >= 32, "Opaque session must contain at least 256 bits"
    assert not api.ssm_reads, "Code-only linking (DEC-AFC-SD-048) reads no SSM secret"
    stored = [item for table in api.tables.values() for item in table.scan()["Items"]]
    values = scalar_values(stored)
    assert hashlib.sha256(token.encode()).hexdigest() in values, "Persist only a session hash"
    assert token not in values, "No raw session in DynamoDB"


def test_wrong_code_rejects_confirmation_and_leaves_code_pending(api):
    device = issue(api)
    wrong = "ZZZZ2222" if device["code"] != "ZZZZ2222" else "YYYY2222"
    status, body = confirm(api, wrong)
    assert_error(status, body, 410)
    status, body = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and body["state"] == "codePending"
    assert "sessionToken" not in body
    status, _ = confirm(api, device["code"])
    assert status in (200, 201), "A wrong code must not consume the valid code"


def test_missing_code_cannot_confirm(api):
    device = issue(api)
    status, body = api.request("POST", "/v1/link/confirm", {"profileId": "owner"})
    assert_error(status, body, 400)
    status, body = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and body["state"] == "codePending"


def test_expired_code_rejects_confirm_and_reports_expired_poll(api):
    device = issue(api)
    table = api.table("Links")
    items = [x for x in table.scan()["Items"] if device["code"] in scalar_values(x)]
    assert len(items) == 1, "Issued code must have one durable link record"
    ttl = api.ttls.get("Links", api.ttls.get("LinksTable"))
    assert ttl, "Links must declare a TTL attribute in the SAM template"
    item = items[0]
    item[ttl] = int(datetime.now(timezone.utc).timestamp()) - 1
    table.put_item(Item=item)
    status, body = confirm(api, device["code"])
    assert_error(status, body, 410)
    status, body = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and body["state"] == "expired"
    assert "sessionToken" not in body


def test_completed_code_cannot_be_replayed_or_rebound_to_another_profile(api):
    device, token = link_device(api)
    status, body = confirm(api, device["code"], profile="foreign")
    assert_error(status, body, 410)
    status, body = api.request("GET", "/v1/profile", token=token, query={"profileId": "foreign"})
    assert_error(status, body, 403)


@pytest.mark.parametrize("method,path", PROTECTED)
def test_every_protected_route_requires_a_session(api, method, path):
    status, body = api.request(method, path)
    assert_error(status, body, 401)


@pytest.mark.parametrize("method,path", PROTECTED)
def test_every_protected_route_rejects_an_unknown_session(api, method, path):
    status, body = api.request(method, path, token="unknown-test-session")
    assert_error(status, body, 401)


@pytest.mark.parametrize("method,path", PROTECTED)
def test_every_protected_route_rejects_a_foreign_profile(api, method, path):
    _, token = link_device(api)
    status, body = api.request(method, path, token=token,
                               body={"profileId": "foreign"}, query={"profileId": "foreign"})
    assert_error(status, body, 403)


def test_known_session_can_reach_its_own_profile(api):
    _, token = link_device(api)
    status, body = api.request("GET", "/v1/profile", token=token, query={"profileId": "owner"})
    assert status in (200, 503), "A valid same-profile session must reach the implemented/stub route"
    if status == 503:
        assert_error(status, body, 503, "not_implemented")


def test_repeated_link_issues_do_not_reuse_codes_or_handles(api):
    first, second = issue(api), issue(api)
    assert first["code"] != second["code"] and first["handle"] != second["handle"]
