"""BUG-AFC-L02-404-ENVELOPE-001: catch-all requests remain structured 404s."""

import pytest


@pytest.mark.parametrize("method,path", [
    ("GET", "/v1/unknown-path"), ("POST", "/v1/unknown-path"),
    ("GET", "/missing/nested"), ("GET", "/"), ("OPTIONS", "/missing"),
])
def test_unknown_paths_return_the_error_envelope_without_a_session(api, method, path):
    status, body = api.request(method, path)
    assert status == 404
    assert body == {"error": {"code": "not_found", "message": "Unknown route."}}
