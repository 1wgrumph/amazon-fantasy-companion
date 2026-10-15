"""DES-AFC-P2-MATCH identity, deduplication and corrections (P2-B04).

Canonical player id is the ESPN athlete id. Manual starters carry it;
Yahoo starters map through player_map.json on exact name + team + position,
and zero or several candidate entries leave the starter unmatched, never
guessed. A match is keyed by (profile, event id): when the profile already
holds an alert for the event at a lower revision the match revises it in
place (cursor = that alert id) even if the corrected play no longer credits
its starter; an equal or higher stored revision yields no match. The
matcher never writes alert records.
"""

import functools
import json
import os
from pathlib import Path

import boto3
from boto3.dynamodb.conditions import Key

PLAYER_MAP_PATH = Path(__file__).resolve().parent / "player_map.json"


@functools.cache
def _dynamodb():
    return boto3.resource("dynamodb")


def _table(variable):
    return _dynamodb().Table(os.environ[variable])


def _scan(variable):
    items, request = [], {}
    while True:
        page = _table(variable).scan(**request)
        items.extend(page["Items"])
        if "LastEvaluatedKey" not in page:
            return items
        request["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def _alert_for(profile_id, event_id):
    """The profile's stored alert row for this event, or None (Query, paged)."""
    request = {"KeyConditionExpression": Key("profileId").eq(profile_id),
               "ConsistentRead": True}
    while True:
        page = _table("ALERTS_TABLE").query(**request)
        for item in page["Items"]:
            if item.get("eventId") == event_id:
                return item
        if "LastEvaluatedKey" not in page:
            return None
        request["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def _espn_id(starter, players):
    if starter.get("athlete_id"):
        return str(starter["athlete_id"])
    positions = starter.get("positions") or []
    entries = [p for p in players
               if p.get("name") == starter.get("name")
               and p.get("team") == starter.get("team")
               and p.get("position") in positions]
    return str(entries[0]["espn_athlete_id"]) if len(entries) == 1 else None


def resolve(game_event):
    """Profiles and starters the GameEvent concerns, at most one match per (profile, event id)."""
    event_id = game_event["eventId"]
    revision = int(game_event.get("revision", 1))
    player_ids = {str(p) for p in game_event.get("playerIds") or []}
    try:
        players = json.loads(Path(PLAYER_MAP_PATH).read_text()).get("players") or []
    except (OSError, ValueError):
        players = []
    matches = []
    # shortcut: profiles come from a Lineups scan; a profile without a lineup
    # row has no starters to concern and lineups are never deleted, so every
    # alert holder still appears. Upgrade to an index when lineups grow.
    for lineup in _scan("LINEUPS_TABLE"):
        profile_id = lineup.get("profileId")
        if not profile_id:
            continue
        stored = _alert_for(profile_id, event_id)
        if stored is not None and int(stored.get("revision", 0)) >= revision:
            continue
        concerned = []
        for starter in lineup.get("starters") or []:
            espn_id = _espn_id(starter, players)
            if espn_id is not None and espn_id in player_ids:
                concerned.append(dict(starter, athlete_id=espn_id))
        if stored is None and not concerned:
            continue
        matches.append({"profileId": profile_id, "eventId": event_id,
                        "revision": revision, "starters": concerned,
                        "cursor": stored["cursor"] if stored else None})
    return matches
