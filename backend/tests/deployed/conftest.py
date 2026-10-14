"""Deployed B01 auth/API cases (SEIT procedures, L02/L03 execution).

These tests address a deployed afc-dev stack over HTTPS only; they never use
the offline Moto fixture and never run in the repository gate. Without
AFC_DEPLOYED_API_URL every test skips (NOT_RUN) and no connection is opened.
Confirm-flow tests additionally need AFC_DEPLOYED_LINK_PASSPHRASE, supplied
only at authorized L02/L03 execution time, never committed.
"""

import os
import socket
import sys
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlsplit

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from deployed_helpers import call  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def offline():
    """Deployed scope: fail closed unless a stack is configured; then pin HTTPS to its host."""
    with pytest.MonkeyPatch.context() as monkeypatch:
        base = os.environ.get("AFC_DEPLOYED_API_URL", "")
        if not base:
            def reject(*args, **kwargs):
                raise AssertionError("Deployed test attempted network without AFC_DEPLOYED_API_URL")
            for method in ("connect", "connect_ex", "sendto", "sendmsg"):
                monkeypatch.setattr(socket.socket, method, reject)
            yield
            return
        host = urlsplit(base).hostname
        if not host:
            raise AssertionError("AFC_DEPLOYED_API_URL must include a host")
        allowed = set()
        resolve = socket.getaddrinfo

        def pinned_getaddrinfo(queried_host, *args, **kwargs):
            addresses = resolve(queried_host, *args, **kwargs)
            if queried_host == host:
                allowed.update((family, address[0]) for family, _, _, _, address in addresses
                               if family in (socket.AF_INET, socket.AF_INET6))
            return addresses

        monkeypatch.setattr(socket, "getaddrinfo", pinned_getaddrinfo)
        socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)

        def check(sock, address):
            if (sock.family not in (socket.AF_INET, socket.AF_INET6)
                    or not isinstance(address, tuple) or not address
                    or (sock.family, address[0]) not in allowed):
                raise AssertionError(f"Deployed test may only contact {host}")

        def pin(original):
            def pinned_connect(self, address, *args, **kwargs):
                check(self, address)
                return original(self, address, *args, **kwargs)
            return pinned_connect

        for method in ("connect", "connect_ex"):
            monkeypatch.setattr(socket.socket, method, pin(getattr(socket.socket, method)))

        sendto, sendmsg = socket.socket.sendto, socket.socket.sendmsg

        def pinned_sendto(self, data, *args):
            check(self, args[-1])
            return sendto(self, data, *args)

        def pinned_sendmsg(self, buffers, ancdata=(), flags=0, address=None):
            if address is not None or self.family not in (socket.AF_INET, socket.AF_INET6):
                check(self, address)
            return sendmsg(self, buffers, ancdata, flags, address)

        monkeypatch.setattr(socket.socket, "sendto", pinned_sendto)
        monkeypatch.setattr(socket.socket, "sendmsg", pinned_sendmsg)
        yield


@pytest.fixture(scope="session")
def deployed(offline):
    base = os.environ.get("AFC_DEPLOYED_API_URL", "").rstrip("/")
    if not base:
        pytest.skip("NOT_RUN: set AFC_DEPLOYED_API_URL to execute against a deployed stack")
    return SimpleNamespace(base=base,
                           profile=os.environ.get("AFC_DEPLOYED_TEST_PROFILE", "deployed-smoke"))


@pytest.fixture(scope="session")
def linked(deployed):
    passphrase = os.environ.get("AFC_DEPLOYED_LINK_PASSPHRASE", "")
    if not passphrase:
        pytest.skip("NOT_RUN: linking needs AFC_DEPLOYED_LINK_PASSPHRASE at L02/L03 time")
    status, device = call(deployed.base, "POST", "/v1/link")
    assert status == 201, device
    status, _ = call(deployed.base, "POST", "/v1/link/confirm", {
        "code": device["code"], "passphrase": passphrase, "profileId": deployed.profile})
    assert status == 200, device
    status, polled = call(deployed.base, "GET", "/v1/link?handle=" + device["handle"])
    assert status == 200 and polled.get("state") == "linked", polled
    assert polled.get("sessionToken"), "Polling must deliver the device session"
    return SimpleNamespace(base=deployed.base, profile=deployed.profile,
                           token=polled["sessionToken"])
