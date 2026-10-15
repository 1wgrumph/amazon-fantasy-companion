"""SEC-3: warn about remote phishing while preserving code-only linking."""

from conftest import assert_error, confirm, issue


def test_link_page_warns_before_authorizing_a_device(api):
    status, page = api.request("GET", "/link")
    assert status == 200
    instructions = page.split('<form id="link-form"', 1)[0]
    assert "Only enter a code displayed on your own TV in front of you." in instructions
    assert "Do not enter a code sent by someone else" in instructions
    assert "gives that TV access to your profile" in instructions


def test_confirmation_cannot_rebind_a_code_before_the_first_poll(api):
    device = issue(api)
    status, _ = confirm(api, device["code"])
    assert status == 200
    status, body = confirm(api, device["code"], profile="foreign")
    assert_error(status, body, 410, "code_expired")
    status, linked = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and linked["state"] == "linked"
    status, profile = api.request("GET", "/v1/profile", token=linked["sessionToken"])
    assert status == 200 and profile["id"] == "owner"
