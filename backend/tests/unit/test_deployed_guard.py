"""BUG-AFC-L02-DEPLOYED-PIN-001: exercise the real fixture without DNS or network."""

import importlib.util
import socket
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture(params=["connect", "connect_ex"])
def guard(monkeypatch, request):
    path = Path(__file__).resolve().parents[1] / "deployed" / "conftest.py"
    # The deployed conftest adds its helper directory; keep imports test-local.
    monkeypatch.setattr(sys, "path", sys.path.copy())
    spec = importlib.util.spec_from_file_location("deployed_guard", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    connections, queries = [], []

    def connect(sock, address):
        connections.append((sock.family, address))
        return None

    def connect_ex(sock, address):
        connections.append((sock.family, address))
        return 0

    def resolve(host, port, *, type):
        queries.append((host, port, type))
        assert host == "api.example.invalid"
        assert type == socket.SOCK_STREAM
        return [(socket.AF_INET, type, socket.IPPROTO_TCP, "", ("192.0.2.10", 0)),
                (socket.AF_INET, type, socket.IPPROTO_TCP, "", ("192.0.2.11", 0)),
                (socket.AF_INET6, type, socket.IPPROTO_TCP, "", ("2001:db8::10", 0, 0, 0))]

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket.socket, "connect_ex", connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    monkeypatch.setenv("AFC_DEPLOYED_API_URL", "https://api.example.invalid")
    return SimpleNamespace(install=lambda: module.offline.__wrapped__(monkeypatch),
                           method=request.param, connections=connections, queries=queries)


@pytest.mark.parametrize("family,address", [
    (socket.AF_INET, ("192.0.2.10", 443)),
    (socket.AF_INET, ("192.0.2.11", 443)),
    (socket.AF_INET6, ("2001:db8::10", 443, 0, 0)),
])
def test_resolved_api_addresses_are_allowed(guard, family, address):
    guard.install()
    with socket.socket(family) as sock:
        assert getattr(sock, guard.method)(address) == (0 if guard.method == "connect_ex" else None)
    assert guard.connections == [(family, address)]


@pytest.mark.parametrize("family,address", [
    (socket.AF_INET, ("192.0.2.99", 443)),
    (socket.AF_INET6, ("2001:db8::99", 443, 0, 0)),
    (socket.AF_INET, ("other.example.invalid", 443)),
    (socket.AF_INET, ("api.example.invalid", 443)),
    (socket.AF_UNIX, "guard-test.sock"),
    (socket.AF_UNIX, b"guard-test.sock"),
    (socket.AF_UNIX, ("192.0.2.10", 443)),
])
def test_other_destinations_are_rejected(guard, family, address):
    guard.install()
    with socket.socket(family) as sock, pytest.raises(AssertionError, match="may only contact"):
        getattr(sock, guard.method)(address)
    assert guard.connections == []


@pytest.mark.parametrize("family,address", [
    (socket.AF_INET, ("192.0.2.10", 443)),
    (socket.AF_INET6, ("2001:db8::10", 443, 0, 0)),
    (socket.AF_UNIX, "guard-test.sock"),
])
def test_without_url_all_connections_are_rejected(guard, monkeypatch, family, address):
    monkeypatch.delenv("AFC_DEPLOYED_API_URL", raising=False)
    guard.install()
    with socket.socket(family) as sock, pytest.raises(AssertionError, match="without AFC_DEPLOYED_API_URL"):
        getattr(sock, guard.method)(address)
    assert guard.connections == []
    assert guard.queries == []
