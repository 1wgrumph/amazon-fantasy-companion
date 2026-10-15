"""Import-safe seams for the P2-B06 provider resolver red tests.

Missing modules and AFC-STUB bodies fail by assertion so CMD-RED shows
behavioral red, never collection errors, import errors or skips.

Handoff seams (frozen with this suite, read at call time by resolve):
- provider_resolver.REGISTRY_PATH: the registry document; defaults to the
  landed backend/src/provider_resolver/registry.json and is read-only.
- provider_resolver.event_channel(event_id): the event's ESPN broadcast
  channel short name (summary broadcast media.shortName), or None.
Profile inputs are the landed Settings.providerPref shape written by the TV
app: order, confirmedAccess, appOverrides, localMarket.
"""

import importlib
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent
EXAMPLE_REGISTRY = HERE / "registry" / "example.json"
LANDED_REGISTRY = HERE.parents[2] / "src" / "provider_resolver" / "registry.json"
PROFILE = "owner"
ACCESS_BASES = ("verified", "customerConfirmed", "unknown")
LOCAL_BROADCAST = ("CBS", "FOX", "NBC")


def require_module(name):
    """Import a module under test; a missing module is an assertion failure."""
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        raise AssertionError(f"provider resolver is not implemented: cannot import {name}: {exc}")


def attempt(func, *args, **kwargs):
    """Call product code; an AFC-STUB NotImplementedError is an assertion failure."""
    try:
        return func(*args, **kwargs)
    except NotImplementedError as exc:
        raise AssertionError(f"provider resolver is not implemented (AFC-STUB): {exc}")


def seed_pref(order=(), confirmed=(), market=None, overrides=None):
    import store
    pref = {"order": list(order), "confirmedAccess": list(confirmed),
            "appOverrides": dict(overrides or {}), "localMarket": market}
    assert store.put_profile(PROFILE, {"providerPref": pref}, 0, "2026-10-15T12:00:00Z")


@pytest.fixture
def resolver(api, monkeypatch, tmp_path):
    """Fresh resolver bound to a per-test copy of the example registry and a channel table."""
    module = require_module("provider_resolver")
    registry = tmp_path / "registry.json"
    shutil.copyfile(EXAMPLE_REGISTRY, registry)
    channels = {}
    monkeypatch.setattr(module, "REGISTRY_PATH", registry, raising=False)
    monkeypatch.setattr(module, "event_channel", channels.get, raising=False)

    def install(*packages):
        return attempt(module.record_installed_apps, PROFILE, list(packages))

    def resolve(event_id):
        result = attempt(module.resolve, PROFILE, event_id)
        assert isinstance(result, dict), f"resolve must return a mapping, got {result!r}"
        assert result.get("accessBasis") in ACCESS_BASES, result
        return result

    return SimpleNamespace(module=module, registry=registry, channels=channels,
                           install=install, resolve=resolve, api=api)
