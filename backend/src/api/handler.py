"""ApiFunction: HTTP API router for CONTRACT-AFC-P2-API (frozen in openapi.yaml).

Every /v1 route except linking needs a bearer device session bound to the
requested profile (DES-AFC-P2-AUTH). Errors use the {"error": {code, message}}
envelope; module stubs (AFC-STUB) surface as 503 not_implemented.
"""

import base64
import binascii
import json
import logging
import os
import re
import time
from decimal import Decimal
from pathlib import Path

import alert_policy
import device_auth
import panel
import provider_resolver
import store


class ApiError(Exception):
    """A contract failure rendered as the structured error envelope."""

    def __init__(self, status, code, message):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def lambda_handler(event, context):
    try:
        return _dispatch(event)
    except ApiError as exc:
        return _error(exc.status, exc.code, exc.message)
    except NotImplementedError:
        return _error(503, "not_implemented", "This feature is not available yet.")
    except Exception:
        logging.getLogger(__name__).exception("Unhandled API failure")
        return _error(503, "unavailable", "The service is temporarily unavailable.")


def _dispatch(event):
    raw = _raw_body(event)
    method, path = event["requestContext"]["http"]["method"], event["rawPath"]
    action = _routes().get((method, path))
    if action is None:
        raise ApiError(404, "not_found", "Unknown route.")
    query = event.get("queryStringParameters") or {}
    profile_id = None
    if path.startswith("/v1/") and not path.startswith("/v1/link"):
        profile_id = device_auth.authenticate(_bearer(event.get("headers") or {}))
        if profile_id is None:
            raise ApiError(401, "unauthenticated", "A linked device session is required.")
    body = _json(raw)
    if profile_id is not None:
        selectors = [query.get("profileId", profile_id), body.get("profileId", profile_id)]
        if any(not isinstance(value, str) for value in selectors):
            raise ApiError(400, "invalid_request", "Field profileId must be a string.")
        if set(selectors) != {profile_id}:
            raise ApiError(403, "forbidden", "This device is not linked to that profile.")
    return action(profile_id, query, body)


def _routes():
    return {
        ("POST", "/v1/link"): _link_issue,
        ("GET", "/v1/link"): _link_poll,
        ("POST", "/v1/link/confirm"): _link_confirm,
        ("GET", "/link"): _link_page,
        ("GET", "/v1/profile"): _profile_get,
        ("PUT", "/v1/profile"): _profile_put,
        ("GET", "/v1/alerts"): _alerts,
        ("GET", "/v1/panel"): _panel,
        ("GET", "/v1/providers"): _providers,
        ("POST", "/v1/routing-outcome"): _routing_outcome,
        ("POST", "/v1/installed-apps"): _installed_apps,
    }


def _raw_body(event):
    raw = event.get("body") or ""
    try:
        if event.get("isBase64Encoded"):
            raw = base64.b64decode(raw, validate=True).decode()
        size = len(raw.encode())
    except (binascii.Error, UnicodeError):
        raise ApiError(400, "invalid_request", "Request body must be UTF-8 JSON.")
    if size > 65536:
        raise ApiError(400, "payload_too_large", "Request body exceeds 64 KiB.")
    return raw


def _json(raw):
    if not raw.strip():
        return {}
    try:
        body = json.loads(raw, parse_float=Decimal)
    except ValueError:
        raise ApiError(400, "invalid_request", "Request body must be a JSON object.")
    if not isinstance(body, dict):
        raise ApiError(400, "invalid_request", "Request body must be a JSON object.")
    return body


def _bearer(headers):
    scheme, _, token = headers.get("authorization", "").partition(" ")
    return token.strip() if scheme.lower() == "bearer" else ""


def _number(value):
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    raise TypeError(type(value).__name__)


def _respond(status, payload):
    body = json.dumps(payload, default=_number)
    if len(body.encode()) > 65536:
        raise ApiError(503, "unavailable", "The response exceeds the 64 KiB contract.")
    return {"statusCode": status,
            "headers": {"content-type": "application/json", "cache-control": "no-store"},
            "body": body}


def _error(status, code, message):
    return _respond(status, {"error": {"code": code, "message": message}})


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _text(body, name, pattern=r".{1,256}"):
    value = body.get(name)
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise ApiError(400, "invalid_request", f"Field {name} is missing or invalid.")
    return value


def _link_issue(profile_id, query, body):
    return _respond(201, device_auth.issue())


def _link_poll(profile_id, query, body):
    return _respond(200, device_auth.poll(_text(query, "handle")))


def _link_confirm(profile_id, query, body):
    code = _text(body, "code", r"[A-Za-z0-9 -]{1,16}")
    result = device_auth.confirm(code, _text(body, "profileId", r"[A-Za-z0-9_-]{1,64}"))
    if result == "gone":
        raise ApiError(410, "code_expired", "This code is expired, used or unknown.")
    return _respond(200, {"state": "linked"})


def _link_page(profile_id, query, body):
    return {"statusCode": 200,
            "headers": {"content-type": "text/html; charset=utf-8", "cache-control": "no-store",
                        "x-frame-options": "DENY", "referrer-policy": "no-referrer",
                        "content-security-policy": "default-src 'none'; script-src "
                        "'sha256-r5vvOH35j5Xp1ecjHhZ7oNRmS7/Xlp/C7RNPviHqeT8='; "
                        "style-src 'unsafe-inline'; connect-src 'self'; form-action 'self'; "
                        "frame-ancestors 'none'"},
            "body": Path(__file__).with_name("link.html").read_text()}


def _profile(profile_id, item):
    return {"schemaVersion": 1, "id": profile_id, "revision": item["revision"] if item else 0,
            "source": "manual", "updatedAt": item["updatedAt"] if item else _now(),
            "data": item["settings"] if item else {"scoringPreset": "halfPpr"}}


def _profile_get(profile_id, query, body):
    return _respond(200, _profile(profile_id, store.get_profile(profile_id)))


def _nba_enabled():
    """AFC_ENABLE_NBA is the only switch; off is the shipped default."""
    return os.environ.get("AFC_ENABLE_NBA", "").lower() in ("1", "true", "yes")


def _valid_sports(sports):
    """Settings.sports keys are a subset of nfl/nba and every value is a JSON boolean.

    {} is valid. A missing field or key means on, so this check never fills defaults.
    """
    return (type(sports) is dict and set(sports) <= {"nfl", "nba"}
            and all(type(value) is bool for value in sports.values()))


def _profile_put(profile_id, query, body):
    revision, settings = body.get("revision"), body.get("data")
    fields = {"fantasySelections", "teamLeague", "alertTypes", "frequency", "quietHours",
              "gameDayPeriods", "spoilerDelay", "presentation", "voice", "excitement",
              "providerPref", "switchingConfirm", "panelPrefs", "detectionOptIn", "scoringPreset"}
    # openapi Settings is frozen (additionalProperties false). sports is accepted
    # only while the flag is on; off, it stays an unknown field.
    if _nba_enabled():
        fields.add("sports")
    if (type(revision) is not int or revision < 0 or not isinstance(settings, dict)
            or not set(settings) <= fields
            or settings.get("scoringPreset", "ppr") not in ("ppr", "halfPpr")
            or ("sports" in settings and not _valid_sports(settings["sports"]))):
        raise ApiError(400, "invalid_request", "Profile needs revision and valid Settings data.")
    now = _now()
    envelope = json.dumps(_profile(profile_id, {"revision": revision + 1, "updatedAt": now,
                                                "settings": settings}), default=_number)
    if len(envelope.encode()) > 65536:
        raise ApiError(400, "payload_too_large", "Profile response would exceed 64 KiB.")
    item = store.put_profile(profile_id, settings, revision, now)
    if item is None:
        raise ApiError(409, "revision_conflict", "The profile changed; read it and merge first.")
    return _respond(200, _profile(profile_id, item))


def _alerts(profile_id, query, body):
    return _respond(200, alert_policy.pending(profile_id, query.get("cursor")))


def _panel(profile_id, query, body):
    try:
        snapshot = panel.snapshot(profile_id, query.get("teamLeague"))
    except panel.InvalidLineupError:
        raise ApiError(503, "panel_invalid",
                       "The stored lineup cannot be displayed on the panel.")
    return _respond(200, snapshot)


def _providers(profile_id, query, body):
    return _respond(200, provider_resolver.resolve(profile_id, query.get("eventId")))


def _routing_outcome(profile_id, query, body):
    outcome = body.get("outcome")
    if outcome not in ("gameOpened", "searchOpened", "appHomeOpened", "appAbsent",
                       "accessUnknown", "playbackDenied"):
        raise ApiError(400, "invalid_request", "Field outcome is missing or invalid.")
    return _respond(200, provider_resolver.record_outcome(
        profile_id, _text(body, "eventId"), outcome))


def _installed_apps(profile_id, query, body):
    packages = body.get("packages")
    if (not isinstance(packages, list) or len(packages) > 500
            or not all(isinstance(p, str) and re.fullmatch(r"[A-Za-z0-9._]{1,255}", p)
                       for p in packages)):
        raise ApiError(400, "invalid_request", "Field packages must list package names.")
    provider_resolver.record_installed_apps(profile_id, packages)
    return _respond(200, {"profileId": profile_id})
