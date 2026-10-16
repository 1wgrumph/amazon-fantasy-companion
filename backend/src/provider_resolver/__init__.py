"""DES-AFC-P2-RESOLVE provider route and access basis from registry.json (read-only).

Selection: among registry providers carrying the event's channel with a
fire_os or vega package effectively installed (latest detector report, with
the customer's appOverrides winning over detection), the first in
providerPref.order wins; registry order only breaks ties the preference
does not cover. Installation is an untrusted detector fact, never access:
accessBasis is customerConfirmed only for a provider in confirmedAccess,
otherwise unknown; no entitlement integration exists, so never verified.
Detector reports and routing outcomes persist on a providerState# item in
the Profiles table (no dedicated table or store accessor exists); that item
never touches the profile's Settings/providerPref.
"""

import functools
import json
import os
from pathlib import Path

import boto3

import store

REGISTRY_PATH = Path(__file__).resolve().parent / "registry.json"
OUTCOMES = ("gameOpened", "searchOpened", "appHomeOpened", "appAbsent",
            "accessUnknown", "playbackDenied")
PLATFORMS = ("fire_os", "vega")
GAP = "REGISTRY_ROUTE_GAP"


def event_channel(event_id):
    """The event's ESPN broadcast channel short name, or None.

    shortcut: the stored GameEvent shape has no broadcast field and no
    source is readable inside this write set (P2B06T-DX-001), so production
    reads unknown until a slice stores the broadcast; tests replace this seam.
    """
    return None


@functools.cache
def _dynamodb():
    return boto3.resource("dynamodb")


def _state_table():
    return _dynamodb().Table(os.environ["PROFILES_TABLE"])


def _state_key(profile_id):
    return {"profileId": "providerState#" + profile_id}


def _installed_packages(profile_id):
    item = _state_table().get_item(Key=_state_key(profile_id)).get("Item") or {}
    return list(item.get("installedPackages") or [])


def _route(provider):
    routes = {}
    for platform in PLATFORMS:
        entry = (provider.get("platform_routes") or {}).get(platform) or {}
        if entry.get("verified_outcome") and entry.get("verified_at"):
            routes[platform] = dict(entry, status="verified")
        else:
            # A missing or unverified entry is a gap; never fill it, and
            # never hand out its unverified launch data as a route.
            routes[platform] = {"status": GAP}
    return {"platform_routes": routes}


def resolve(profile_id, event_id):
    """Provider, channel, registry route and access basis for the event."""
    channel = event_channel(event_id)
    profile = store.get_profile(profile_id) or {}
    pref = (profile.get("settings") or {}).get("providerPref") or {}
    if not isinstance(pref, dict):
        pref = {}
    market = pref.get("localMarket")
    result = {"provider": None, "channel": channel, "route": None,
              "accessBasis": "unknown",
              "inputs": {"installed": False,
                         "localMarket": market if isinstance(market, str) else None}}
    if channel is None:
        return result
    overrides = pref.get("appOverrides") or {}
    if not isinstance(overrides, dict):
        overrides = {}
    overrides = {p: on for p, on in overrides.items()
                 if isinstance(p, str) and type(on) is bool}
    installed = {p for p in _installed_packages(profile_id)
                 if overrides.get(p) is not False}
    installed.update(p for p, on in overrides.items() if on)
    order = pref.get("order")
    if not isinstance(order, list) or not all(isinstance(p, str) for p in order):
        order = []
    registry = json.loads(Path(REGISTRY_PATH).read_text())
    candidates = []
    for index, provider in enumerate(registry.get("providers") or []):
        if channel not in (provider.get("channels_carried") or []):
            continue
        packages = [(provider.get("platform_routes") or {}).get(p, {}).get("package")
                    for p in PLATFORMS]
        if not any(package in installed for package in packages):
            continue
        rank = order.index(provider["id"]) if provider["id"] in order else len(order)
        candidates.append((rank, index, provider))
    if not candidates:
        return result
    chosen = min(candidates)[2]
    result.update(provider=chosen["id"], route=_route(chosen))
    result["inputs"]["installed"] = True
    confirmed = pref.get("confirmedAccess")
    if (isinstance(confirmed, list) and all(isinstance(p, str) for p in confirmed)
            and chosen["id"] in confirmed):
        result["accessBasis"] = "customerConfirmed"
    return result


def record_outcome(profile_id, event_id, outcome):
    """Record one Watch attempt's RoutingOutcome; returns the stored record."""
    if outcome not in OUTCOMES:
        raise ValueError(f"Unknown RoutingOutcome: {outcome!r}")
    _state_table().update_item(
        Key=_state_key(profile_id), UpdateExpression="SET #key = :outcome",
        ExpressionAttributeNames={"#key": "outcome#" + event_id},
        ExpressionAttributeValues={":outcome": outcome})
    return {"profileId": profile_id, "eventId": event_id, "outcome": outcome}


def record_installed_apps(profile_id, packages):
    """Record the TV detector's installed package list; latest report replaces."""
    packages = list(packages)
    _state_table().update_item(
        Key=_state_key(profile_id), UpdateExpression="SET installedPackages = :packages",
        ExpressionAttributeValues={":packages": packages})
    return {"profileId": profile_id, "packages": packages}
