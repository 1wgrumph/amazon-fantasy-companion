"""Import-safe seams and Moto seeding for the P2-B04 matcher red tests.

Missing modules and AFC-STUB bodies fail by assertion so CMD-RED shows
behavioral red, never collection errors, import errors or skips.

Handoff contract (frozen with this suite; DES-AFC-P2-MATCH):
- matcher.resolve(game_event) takes a stored GameEvent (store.put_event shape)
  and returns a list of match mappings, at most one per (profileId, eventId).
  Each match carries profileId, eventId, revision (the event's revision),
  starters (the profile's starters the event concerns, each with its ESPN
  athlete_id) and cursor.
- cursor is the existing Alerts row's cursor (the alert id) when the profile
  already holds an alert for this eventId at a lower revision: the correction
  revises that alert in place. It is None when no alert exists yet. A profile
  whose alert already holds this revision or a later one yields no match.
- resolve never writes alert records; the policy and pipeline own alerts.
- matcher.PLAYER_MAP_PATH: module-level path to the explicit Yahoo-to-ESPN
  mapping table, read at call time, defaulting to the landed
  backend/src/matcher/player_map.json. Document shape:
  {"schemaVersion": 1, "players": [{"espn_athlete_id", "name", "team",
  "position", "confidence"}]}. A Yahoo starter maps to an entry with its exact
  name and team and a position in its positions list; zero or several such
  entries leave it unmatched (never guessed). Manual starters already carry
  their ESPN athlete_id.
"""

import importlib
import json
from types import SimpleNamespace

import pytest

TIMESTAMP = "2026-10-15T20:00:00Z"
GAME = "401999001"

# Synthetic ESPN identities; names and ids belong to no real athlete.
PLAYER_MAP = {"schemaVersion": 1, "players": [
    {"espn_athlete_id": "9000001", "name": "Sample Receiver", "team": "PHI",
     "position": "WR", "confidence": "exact"},
    {"espn_athlete_id": "9000002", "name": "Sample Receiver", "team": "DAL",
     "position": "WR", "confidence": "exact"},
    {"espn_athlete_id": "9000003", "name": "Twin Runner", "team": "KC",
     "position": "RB", "confidence": "exact"},
    {"espn_athlete_id": "9000004", "name": "Twin Runner", "team": "KC",
     "position": "RB", "confidence": "exact"},
    {"espn_athlete_id": "9000005", "name": "Sample Passer", "team": "PHI",
     "position": "QB", "confidence": "exact"},
]}

YAHOO_RECEIVER = {"player_key": "nfl.p.7001", "name": "Sample Receiver", "team": "PHI",
                  "positions": ["WR"], "slot": "WR"}
YAHOO_PASSER = {"player_key": "nfl.p.7005", "name": "Sample Passer", "team": "PHI",
                "positions": ["QB"], "slot": "QB"}
YAHOO_TWIN = {"player_key": "nfl.p.7003", "name": "Twin Runner", "team": "KC",
              "positions": ["RB"], "slot": "RB"}
MANUAL_RECEIVER = {"athlete_id": "9000001", "name": "Sample Receiver", "team": "PHI",
                   "slot": "WR"}
MANUAL_PASSER = {"athlete_id": "9000005", "name": "Sample Passer", "team": "PHI",
                 "slot": "QB"}
YAHOO_SCORING = {"league_key": "nfl.l.1001", "stat_modifiers": {"receptions": 1}}


def require_module(name):
    """Import a module under test; a missing module is an assertion failure."""
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        raise AssertionError(f"matcher behavior is not implemented: cannot import {name}: {exc}")


def attempt(func, *args, **kwargs):
    """Call product code; an AFC-STUB NotImplementedError is an assertion failure."""
    try:
        return func(*args, **kwargs)
    except NotImplementedError as exc:
        raise AssertionError(f"matcher behavior is not implemented (AFC-STUB): {exc}")


def game_event(event_id, players, revision=1, correction_of=None, score=(14, 17),
               field_position=8, possession="PHI"):
    """A GameEvent in the store.put_event shape normalize_summary produces."""
    return {"gameId": GAME, "eventId": event_id, "revision": revision,
            "correctionOf": correction_of, "source": "live",
            "score": {"away": score[0], "home": score[1]}, "fieldPosition": field_position,
            "possession": possession, "playerIds": list(players), "eventTime": TIMESTAMP}


def seed_lineup(profile_id, source, starters):
    import store
    assert store.put_profile(profile_id, {}, 0, TIMESTAMP), "profile seed must succeed"
    row = {"profileId": profile_id, "source": source, "team": "Red Testers",
           "league": "Red League Alpha", "starters": list(starters), "updatedAt": TIMESTAMP}
    if source == "yahoo":
        row["scoring"] = YAHOO_SCORING
    store.put_lineup(row)


def seed_alert(profile_id, cursor, event_id, revision):
    """The Alerts row the pipeline stored for an earlier delivery of this event."""
    import store
    store.put_alert({"profileId": profile_id, "cursor": cursor, "eventId": event_id,
                     "revision": revision, "alertType": "playerScore",
                     "triggerContext": {"eventId": event_id}, "emittedAt": TIMESTAMP})


def athlete_ids(match):
    starters = match.get("starters")
    assert isinstance(starters, list), f"match must list its starters, got {match!r}"
    return {starter.get("athlete_id") for starter in starters}


def for_profile(matches, profile_id):
    return [match for match in matches if match.get("profileId") == profile_id]


@pytest.fixture
def match_env(api, monkeypatch, tmp_path):
    """Fresh matcher bound to a per-test mapping table and this test's Moto tables."""
    module = require_module("matcher")
    player_map = tmp_path / "player_map.json"
    player_map.write_text(json.dumps(PLAYER_MAP))
    monkeypatch.setattr(module, "PLAYER_MAP_PATH", player_map, raising=False)

    def resolve(event):
        import store
        store.put_event(event)
        before = len(api.table("Alerts").scan()["Items"])
        result = attempt(module.resolve, event)
        assert isinstance(result, list), f"resolve must return a list of matches, got {result!r}"
        for match in result:
            assert isinstance(match, dict), f"each match must be a mapping, got {match!r}"
            assert match.get("eventId") == event["eventId"], match
            assert "cursor" in match, f"match must carry cursor (alert id or None): {match!r}"
        keys = [(match.get("profileId"), match.get("eventId")) for match in result]
        assert len(keys) == len(set(keys)), f"more than one match per (profile, event): {keys}"
        after = len(api.table("Alerts").scan()["Items"])
        assert after == before, "the matcher must never write alert records"
        return result

    return SimpleNamespace(module=module, resolve=resolve, api=api, player_map=player_map)
