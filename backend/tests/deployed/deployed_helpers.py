"""Stdlib HTTPS helpers for the deployed B01 cases (no AWS SDK, no Moto)."""

import json
import urllib.error
import urllib.request


def call(base, method, path, body=None, token=None, raw=None):
    data = raw.encode() if raw is not None else (
        None if body is None else json.dumps(body).encode())
    request = urllib.request.Request(base + path, data=data, method=method,
                                     headers={"content-type": "application/json"})
    if token is not None:
        request.add_header("authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read().decode()
            return response.status, json.loads(payload) if payload else None
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode()
        return exc.code, json.loads(payload) if payload else None


def assert_error(status, body, expected):
    assert status == expected, body
    assert isinstance(body["error"]["code"], str) and body["error"]["code"]
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]
