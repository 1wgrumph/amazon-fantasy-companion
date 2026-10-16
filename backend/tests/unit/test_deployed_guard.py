"""BUG-AFC-L02-DEPLOYED-PIN-001: exercise the real fixture without DNS or network."""

import importlib.util
import os
import socket
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def deployed_guard(monkeypatch):
    path = Path(__file__).resolve().parents[1] / "deployed" / "conftest.py"
    # The deployed conftest adds its helper directory; keep imports test-local.
    monkeypatch.setattr(sys, "path", sys.path.copy())
    spec = importlib.util.spec_from_file_location("deployed_guard", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(params=["connect", "connect_ex"])
def guard(monkeypatch, request, deployed_guard):
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
    def install():
        fixture = deployed_guard.offline.__wrapped__()
        request.addfinalizer(fixture.close)
        next(fixture)

    return SimpleNamespace(install=install,
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


@pytest.mark.parametrize("family,ip", [
    (socket.AF_INET, "192.0.2.12"),
    (socket.AF_INET6, "2001:db8::12"),
])
def test_create_connection_accepts_rotated_api_dns(guard, monkeypatch, family, ip):
    queries = []

    def resolve(host, port, *args, **kwargs):
        queries.append(host)
        address = (("192.0.2.10", port or 0) if len(queries) == 1 else
                   (ip, port, 0, 0) if family == socket.AF_INET6 else (ip, port))
        return [(socket.AF_INET if len(queries) == 1 else family,
                 socket.SOCK_STREAM, socket.IPPROTO_TCP, "", address)]

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    guard.install()
    with socket.create_connection(("api.example.invalid", 443)) as sock:
        assert sock.family == family
    assert queries == ["api.example.invalid", "api.example.invalid"]
    assert guard.connections == [(family, (ip, 443, 0, 0) if family == socket.AF_INET6
                                  else (ip, 443))]


def test_resolving_other_host_does_not_authorize_it(guard, monkeypatch):
    def resolve(host, port, *args, **kwargs):
        ip = "192.0.2.10" if host == "api.example.invalid" else "192.0.2.99"
        return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (ip, port or 0))]

    monkeypatch.setattr(socket, "getaddrinfo", resolve)
    guard.install()
    socket.getaddrinfo("other.example.invalid", 443)
    with pytest.raises(AssertionError, match="may only contact"):
        socket.create_connection(("other.example.invalid", 443))
    assert guard.connections == []


@pytest.mark.parametrize("method", ["sendto", "sendmsg"])
@pytest.mark.parametrize("configured", [True, False])
@pytest.mark.parametrize("family,address,allowed", [
    (socket.AF_INET, ("192.0.2.10", 443), True),
    (socket.AF_INET6, ("2001:db8::10", 443, 0, 0), True),
    (socket.AF_INET, ("192.0.2.99", 443), False),
    (socket.AF_INET6, ("2001:db8::99", 443, 0, 0), False),
    (socket.AF_UNIX, "guard-test.sock", False),
])
def test_addressed_sends_follow_guard(guard, monkeypatch, method, configured,
                                    family, address, allowed):
    sends = []

    def send(sock, *args):
        sends.append((sock.family, args[-1]))
        return 1

    monkeypatch.setattr(socket.socket, method, send)
    if not configured:
        monkeypatch.delenv("AFC_DEPLOYED_API_URL", raising=False)
    guard.install()
    args = (b"x", address) if method == "sendto" else ([b"x"], [], 0, address)
    with socket.socket(family, socket.SOCK_DGRAM) as sock:
        if configured and allowed:
            assert getattr(sock, method)(*args) == 1
            assert sends == [(family, address)]
        else:
            message = "may only contact" if configured else "without AFC_DEPLOYED_API_URL"
            with pytest.raises(AssertionError, match=message):
                getattr(sock, method)(*args)
            assert sends == []


def test_guard_precedes_session_link_flow(deployed_guard, tmp_path):
    # Use pytest's actual fixture scheduler; every external boundary is stubbed.
    (tmp_path / "conftest.py").write_text('''
import importlib.util
import socket
import pytest

spec = importlib.util.spec_from_file_location("deployed_guard", %r)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
offline, deployed, linked = module.offline, module.deployed, module.linked

connections = []
def connect(sock, address):
    connections.append(address)
socket.socket.connect = connect
socket.socket.connect_ex = connect
socket.getaddrinfo = lambda *args, **kwargs: [
    (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("192.0.2.10", 443))]

def call(base, method, path, body=None):
    with socket.socket() as sock:
        sock.connect(("192.0.2.10", 443))
        with pytest.raises(AssertionError, match="may only contact"):
            sock.connect(("192.0.2.99", 443))
    if path == "/v1/link":
        return 201, {"code": "test-code", "handle": "test-handle"}
    if path == "/v1/link/confirm":
        return 200, {}
    return 200, {"state": "linked", "sessionToken": "test-token"}
module.call = call
''' % deployed_guard.__file__)
    (tmp_path / "test_link.py").write_text('''
def test_link(linked):
    assert linked.token == "test-token"
    from conftest import connections
    assert connections == [("192.0.2.10", 443)] * 3
''')
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
               AFC_DEPLOYED_API_URL="https://api.example.invalid")
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-c", "/dev/null",
                             "-p", "no:cacheprovider",
                             "--confcutdir", str(tmp_path), str(tmp_path)],
                            env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
