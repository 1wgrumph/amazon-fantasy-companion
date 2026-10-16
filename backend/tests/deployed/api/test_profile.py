"""Deployed CONTRACT-AFC-P2-API profile behavior (SEIT-AFC-PR-058; L02/L03 execution)."""

from deployed_helpers import assert_error, call


def test_profile_roundtrip_preserves_revision(linked):
    status, body = call(linked.base, "GET", "/v1/profile", token=linked.token)
    assert status == 200, body
    revision = body["revision"]
    status, body = call(linked.base, "PUT", "/v1/profile", token=linked.token,
                        body={"revision": revision, "data": {"scoringPreset": "ppr"}})
    assert status == 200 and body["revision"] == revision + 1, body
    status, body = call(linked.base, "GET", "/v1/profile", token=linked.token)
    assert status == 200 and body["data"] == {"scoringPreset": "ppr"}, body


def test_foreign_profile_is_forbidden(linked):
    status, body = call(linked.base, "GET", "/v1/profile?profileId=foreign-profile",
                        token=linked.token)
    assert_error(status, body, 403)


def test_malformed_body_is_a_structured_400(linked):
    status, body = call(linked.base, "PUT", "/v1/profile", token=linked.token, raw="{")
    assert_error(status, body, 400)


def test_unknown_route_is_a_structured_404(linked):
    status, body = call(linked.base, "GET", "/v1/unknown-path", token=linked.token)
    assert_error(status, body, 404)
