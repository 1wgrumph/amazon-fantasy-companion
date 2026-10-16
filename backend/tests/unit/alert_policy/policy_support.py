"""Import-safe seams, fixtures and Moto seeding for the P2-B05 alert-policy red tests.

Missing modules and AFC-STUB bodies fail by assertion so CMD-RED shows
behavioral red, never collection errors, import errors or skips. Policy inputs
are built here as fixtures in the match shape P2-B04T froze; the stub matcher
is never called.

Handoff contract (frozen with this suite; DES-AFC-P2-POLICY):
- alert_policy.evaluate(game_event, matches) returns a list of Alert items in
  the store.put_alert shape (keys within ALERT_KEYS; providerRoute is added by
  the pipeline). It reads each matched profile's Settings with
  store.get_profile and the profile's earlier alerts with store.list_alerts; it
  never emits for a profile absent from `matches`.
- matches follow P2-B04T: {profileId, eventId, revision, starters, cursor};
  cursor None means a new alert, a cursor string means revise that alert in
  place (same cursor).
- GameEvent is the store.put_event shape plus two ESPN play fields the policy
  needs and the Phase 2 data model omits: `period` (int; 4 = 4th quarter,
  5 and above = overtime) and `scoringPlay` (bool). fieldPosition is ESPN
  start.yardsToEndzone.
- Settings use the TV ProfileCodec wire shape: alertTypes from
  {RedZone, PlayerScore, CloseGame}; frequency = alert_min_gap seconds;
  quietHours = [{startMinute, endMinute}]; gameDayPeriods =
  {enabled, periods}; spoilerDelay seconds; excitement Off|Mild|Hype;
  detectionOptIn bool. Minutes of day are read in UTC from eventTime because
  Settings carry no time zone. gameDayPeriods.enabled False is never relied on.
- One alert per (profile, event). alertType is one of the matching enabled
  types and triggerContext.alertTypes lists every matching enabled type.
- triggerContext carries gameId, eventId, source, score, starters (each with
  athlete_id) and basis (observed-playback | profile-assumption).
- emittedAt is the release time: never earlier than eventTime + spoilerDelay.
  alert_min_gap compares release times of released alerts of the same game.
- commentary is None at Off and a fixed-template string at Mild/Hype filled
  only from event and trigger fields.
- alert_policy.pending(profile_id, cursor) returns {"alerts": [envelope],
  "cursor": str}: only this profile's alerts with cursor after `cursor` whose
  emittedAt is not in the future, in cursor order; the returned cursor never
  passes a held alert. Envelope: schemaVersion 1, id = cursor, revision =
  alert revision, source = triggerContext.source, updatedAt = emittedAt,
  data with alertType,
  triggerContext, commentary and route = stored providerRoute.
"""

import importlib
import re
from datetime import datetime, timedelta, timezone

import pytest

GAME = "401999001"
OTHER_GAME = "401999002"
KICKOFF = datetime(2026, 10, 18, 20, 0, 0, tzinfo=timezone.utc)  # a Sunday, 20:00 UTC
TYPES = ("RedZone", "PlayerScore", "CloseGame")
ALERT_KEYS = {"profileId", "cursor", "eventId", "revision", "alertType", "triggerContext",
              "providerRoute", "commentary", "emittedAt"}
BASES = ("observed-playback", "profile-assumption")

# Synthetic ESPN identities shared with P2-B04T; names belong to no real athlete.
RECEIVER = {"athlete_id": "9000001", "name": "Sample Receiver", "team": "PHI", "slot": "WR"}
PASSER = {"athlete_id": "9000005", "name": "Sample Passer", "team": "PHI", "slot": "QB"}
DECOY = {"athlete_id": "9000077", "name": "Bench Decoy", "team": "DAL", "slot": "TE"}

# Claims a red-zone entry cannot support (AFC-PR-028): the player is on the field or will score.
OVERCLAIM = re.compile(r"on the field|in the game|in the huddle|will (?:score|find|get)|"
                       r"going to score|about to score|set to score|should score|"
                       r"bound to score|sure to score|(?:is|are) scoring", re.IGNORECASE)


def iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(stamp):
    assert isinstance(stamp, str), f"timestamp must be an ISO-8601 string, got {stamp!r}"
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def at(seconds):
    """eventTime `seconds` after KICKOFF."""
    return iso(KICKOFF + timedelta(seconds=seconds))


def require_module(name):
    """Import a module under test; a missing module is an assertion failure."""
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        raise AssertionError(f"alert policy is not implemented: cannot import {name}: {exc}")


def attempt(func, *args, **kwargs):
    """Call product code; an AFC-STUB NotImplementedError is an assertion failure."""
    try:
        return func(*args, **kwargs)
    except NotImplementedError as exc:
        raise AssertionError(f"alert policy is not implemented (AFC-STUB): {exc}")


def game_event(event_id, players=("9000001",), *, game=GAME, seconds=0, field_position=50,
               possession="PHI", score=(10, 3), period=2, scoring=False, revision=1,
               correction_of=None, source="live"):
    """A stored GameEvent (store.put_event shape) plus ESPN period and scoringPlay."""
    return {"gameId": game, "eventId": event_id, "revision": revision,
            "correctionOf": correction_of, "source": source,
            "score": {"away": score[0], "home": score[1]}, "fieldPosition": field_position,
            "possession": possession, "playerIds": list(players), "eventTime": at(seconds),
            "period": period, "scoringPlay": scoring}


def match(profile_id, event, starters=(RECEIVER,), cursor=None):
    """One P2-B04T match for this profile and event."""
    return {"profileId": profile_id, "eventId": event["eventId"],
            "revision": event["revision"], "starters": [dict(s) for s in starters],
            "cursor": cursor}


def settings(**overrides):
    """Baseline Settings: every type on, inside a game-day period, no quiet hours,
    no frequency cap, no spoiler delay, commentary off, detection opted out."""
    base = {"fantasySelections": {"leagues": [], "teams": [], "players": ["9000001", "9000005"],
                                  "favoriteTeams": []},
            "alertTypes": list(TYPES), "frequency": 0, "quietHours": [],
            "gameDayPeriods": {"enabled": True,
                               "periods": [{"startMinute": 17 * 60, "endMinute": 23 * 60 + 59}]},
            "spoilerDelay": 0, "excitement": "Off", "detectionOptIn": False}
    base.update(overrides)
    return base


def seed_profile(profile_id, starters=(RECEIVER, PASSER, DECOY), **overrides):
    import store
    assert store.put_profile(profile_id, settings(**overrides), 0, iso(KICKOFF)), "profile seed"
    store.put_lineup({"profileId": profile_id, "source": "manual", "team": "Red Testers",
                      "league": "Red League Alpha", "starters": [dict(s) for s in starters],
                      "scoring": "halfPpr", "updatedAt": iso(KICKOFF)})


def seed_alert(profile_id, cursor, emitted_at, *, event_id="401999001900", revision=1,
               alert_type="PlayerScore", game=GAME, route=None, source="live"):
    import store
    context = {"gameId": game, "eventId": event_id, "source": source,
               "score": {"away": 10, "home": 3}, "alertTypes": [alert_type],
               "starters": [dict(RECEIVER)], "basis": "profile-assumption"}
    item = {"profileId": profile_id, "cursor": cursor, "eventId": event_id,
            "revision": revision, "alertType": alert_type, "triggerContext": context,
            "commentary": None, "emittedAt": emitted_at}
    if route is not None:
        item["providerRoute"] = route
    store.put_alert(item)
    return item


@pytest.fixture
def policy(api):
    """Fresh alert_policy bound to this test's Moto tables."""
    return require_module("alert_policy")


def link_device(api, profile_id):
    """Link a TV to `profile_id` through the landed device-auth API; return its token."""
    status, device = api.request("POST", "/v1/link")
    assert status in (200, 201), device
    status, _ = api.request("POST", "/v1/link/confirm",
                            {"code": device["code"], "profileId": profile_id})
    assert status == 200
    status, polled = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and polled.get("sessionToken"), polled
    return polled["sessionToken"]


def evaluate(policy, event, matches):
    """Run evaluate and check every result is a storable Alert item."""
    result = attempt(policy.evaluate, event, matches)
    assert isinstance(result, list), f"evaluate must return a list of Alert items, got {result!r}"
    for alert in result:
        assert isinstance(alert, dict), f"each alert must be a mapping, got {alert!r}"
        assert set(alert) <= ALERT_KEYS, f"unknown Alert attributes: {set(alert) - ALERT_KEYS}"
        for key in ("profileId", "cursor", "eventId", "revision", "alertType",
                    "triggerContext", "emittedAt"):
            assert key in alert, f"alert lacks {key}: {alert!r}"
        assert alert["eventId"] == event["eventId"], alert
        assert isinstance(alert["cursor"], str) and alert["cursor"], alert
    keys = [(alert["profileId"], alert["eventId"]) for alert in result]
    assert len(keys) == len(set(keys)), f"more than one alert per (profile, event): {keys}"
    return result


def deliver(policy, event, matches):
    """The pipeline half that matters to the policy: evaluate, then store each alert."""
    import store
    alerts = evaluate(policy, event, matches)
    for alert in alerts:
        store.put_alert(dict(alert, providerRoute=None))
    return alerts


def for_profile(alerts, profile_id):
    return [alert for alert in alerts if alert["profileId"] == profile_id]


def types_of(alert):
    listed = alert["triggerContext"].get("alertTypes")
    assert isinstance(listed, list), f"triggerContext must list its alert types: {alert!r}"
    assert alert["alertType"] in listed, alert
    return set(listed)


def numbers(*values):
    """Every integer that appears in the given values, as strings."""
    found = set()
    for value in values:
        if isinstance(value, dict):
            found |= numbers(*value.values())
        elif isinstance(value, (list, tuple)):
            found |= numbers(*value)
        elif isinstance(value, bool) or value is None:
            continue
        elif isinstance(value, (int, float)):
            found.add(str(int(value)))
    return found
