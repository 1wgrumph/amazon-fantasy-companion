"""Shared DynamoDB accessors, one per table operation of DES-AFC-P2-BACKEND.

Item shapes follow models/AFC-Data.sysml (GameEvent, Alert, Lineup, PanelState,
Settings) plus the key attributes declared in backend/template.yaml. Table names
come from the function environment. Conditional writes return False on conflict
instead of raising, so callers map them to contract statuses.
"""

import functools
import os

import boto3
from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError


@functools.cache
def _dynamodb():
    return boto3.resource("dynamodb")


def _table(variable):
    return _dynamodb().Table(os.environ[variable])


def _shaped(item, fields):
    unknown = set(item) - fields
    if unknown:
        raise ValueError("Unknown item attributes: " + ", ".join(sorted(unknown)))
    return item


def _written(write, **request):
    try:
        write(**request)
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise
        return False
    return True


# Profiles: profile, Settings, revision.
def get_profile(profile_id):
    return _table("PROFILES_TABLE").get_item(
        Key={"profileId": profile_id}).get("Item")


def monitoring_profiles():
    """Enumerate profile monitoring settings and starters, including every scan page."""
    profiles = []
    scan = {"ProjectionExpression": "profileId, #settings",
            "ExpressionAttributeNames": {"#settings": "settings"}}
    while True:
        page = _table("PROFILES_TABLE").scan(**scan)
        for profile in page["Items"]:
            lineup = get_lineup(profile["profileId"]) or {}
            profiles.append({"settings": profile.get("settings", {}),
                             "starters": lineup.get("starters", [])})
        if "LastEvaluatedKey" not in page:
            return profiles
        scan["ExclusiveStartKey"] = page["LastEvaluatedKey"]


def put_profile(profile_id, settings, revision, updated_at):
    """Store revision + 1 only while the stored revision equals `revision` (0 = none yet)."""
    item = {"profileId": profile_id, "settings": settings, "revision": revision + 1,
            "updatedAt": updated_at}
    condition = (Attr("profileId").not_exists() if revision == 0
                 else Attr("revision").eq(revision))
    if _written(_table("PROFILES_TABLE").put_item, Item=item, ConditionExpression=condition):
        return item
    return None


# Links: device code, polling-handle hash, state, expiry; session token hashes.
def put_link(code, handle_hash, expires_at):
    item = {"pk": "code#" + code, "code": code, "handleHash": handle_hash,
            "state": "codePending", "expiresAt": expires_at}
    return _written(_table("LINKS_TABLE").put_item, Item=item,
                    ConditionExpression=Attr("pk").not_exists())


def find_link(handle_hash):
    items = _table("LINKS_TABLE").query(
        IndexName="handle", KeyConditionExpression=Key("handleHash").eq(handle_hash))["Items"]
    return items[0] if items else None


def confirm_link(code, profile_id, now):
    """Bind a pending, unexpired code to a profile exactly once."""
    return _written(
        _table("LINKS_TABLE").update_item, Key={"pk": "code#" + code},
        UpdateExpression="SET #state = :confirmed, profileId = :profile",
        ConditionExpression="#state = :pending AND expiresAt > :now",
        ExpressionAttributeNames={"#state": "state"},
        ExpressionAttributeValues={":confirmed": "confirmed", ":pending": "codePending",
                                   ":profile": profile_id, ":now": now})


def complete_link(code):
    """Move a confirmed code to linked; already-linked codes stay linked."""
    return _written(
        _table("LINKS_TABLE").update_item, Key={"pk": "code#" + code},
        UpdateExpression="SET #state = :linked",
        ConditionExpression="#state = :confirmed",
        ExpressionAttributeNames={"#state": "state"},
        ExpressionAttributeValues={":linked": "linked", ":confirmed": "confirmed"})


def record_link_session(code, session_hash):
    """Record the link's current session hash, returning the superseded one (if any)."""
    response = _table("LINKS_TABLE").update_item(
        Key={"pk": "code#" + code}, UpdateExpression="SET currentSessionHash = :hash",
        ExpressionAttributeValues={":hash": session_hash}, ReturnValues="ALL_OLD")
    return response.get("Attributes", {}).get("currentSessionHash")


def delete_session(session_hash):
    _table("LINKS_TABLE").delete_item(Key={"pk": "session#" + session_hash})


def put_session(session_hash, profile_id, linked_at):
    _table("LINKS_TABLE").put_item(Item={"pk": "session#" + session_hash,
                                         "sessionHash": session_hash,
                                         "profileId": profile_id, "linkedAt": linked_at})


def get_session(session_hash):
    # Strongly consistent: the TV uses a session right after the poll that created it.
    return _table("LINKS_TABLE").get_item(
        Key={"pk": "session#" + session_hash}, ConsistentRead=True).get("Item")


# Events: game, event id, revision, source plus GameEvent attributes.
def put_event(event):
    _table("EVENTS_TABLE").put_item(Item=_shaped(event, {
        "gameId", "eventId", "revision", "source", "score", "fieldPosition", "possession",
        "playerIds", "eventTime", "correctionOf", "period", "scoringPlay"}))


def get_event(game_id, event_id):
    return _table("EVENTS_TABLE").get_item(
        Key={"gameId": game_id, "eventId": event_id}).get("Item")


# Alerts: profile, cursor, Alert attributes.
def put_alert(alert):
    _table("ALERTS_TABLE").put_item(Item=_shaped(alert, {
        "profileId", "cursor", "eventId", "revision", "alertType", "triggerContext",
        "providerRoute", "commentary", "emittedAt"}))


def list_alerts(profile_id, after, limit, include_after=False):
    """Alerts for one profile with cursor strictly after `after` (None = from the start).

    include_after also returns the row at `after` itself, so revision-aware
    delivery can re-serve a corrected alert at the client's progress cursor.
    """
    condition = Key("profileId").eq(profile_id)
    if after is not None:
        bound = Key("cursor").gte(after) if include_after else Key("cursor").gt(after)
        condition = condition & bound
    return _table("ALERTS_TABLE").query(KeyConditionExpression=condition, Limit=limit)["Items"]


# Lineups: profile, source, starters, scoring basis.
def put_lineup(lineup):
    _table("LINEUPS_TABLE").put_item(Item=_shaped(lineup, {
        "profileId", "source", "team", "league", "starters", "scoring", "updatedAt"}))


def get_lineup(profile_id):
    return _table("LINEUPS_TABLE").get_item(
        Key={"profileId": profile_id}).get("Item")


# Panels: profile, team/league, PanelState.
_PANEL_FIELDS = {"profileId", "teamLeague", "visible", "teamTotal", "progress",
                 "freshness", "rows", "updatedAt"}


def put_panel(panel):
    _table("PANELS_TABLE").put_item(Item=_shaped(panel, _PANEL_FIELDS))


def put_panel_conditional(panel, expected_counter):
    """Put a panel only while freshness.counter still equals `expected_counter`.

    None means no row exists yet. Returns False on a lost race so the caller
    can re-read and merge instead of erasing another writer's facts.
    """
    item = _shaped(panel, _PANEL_FIELDS)
    if expected_counter is None:
        return _written(_table("PANELS_TABLE").put_item, Item=item,
                        ConditionExpression=Attr("profileId").not_exists())
    return _written(
        _table("PANELS_TABLE").put_item, Item=item,
        ConditionExpression="#freshness.#counter = :expected",
        ExpressionAttributeNames={"#freshness": "freshness", "#counter": "counter"},
        ExpressionAttributeValues={":expected": expected_counter})


def get_panel(profile_id, team_league):
    return _table("PANELS_TABLE").get_item(
        Key={"profileId": profile_id, "teamLeague": team_league}).get("Item")


# Player statistics: latest stored boxscore per ESPN athlete (panel seam).
# shortcut: one record per athlete, so the latest ingested game wins across
# games too; add a gameId range key when the panel needs per-game history.
def put_player_statistics(record):
    _table("PLAYER_STATS_TABLE").put_item(Item=_shaped(record, {
        "athleteId", "gameId", "gameState", "gameStatus", "source", "asOf", "stats"}))


def get_player_statistics(athlete_id):
    return _table("PLAYER_STATS_TABLE").get_item(
        Key={"athleteId": athlete_id}).get("Item")
