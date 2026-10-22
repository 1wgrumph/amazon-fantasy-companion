"""Shared DynamoDB accessors, one per table operation of DES-AFC-P2-BACKEND.

Item shapes follow models/AFC-Data.sysml (GameEvent, Alert, Lineup, PanelState,
Settings) plus the key attributes declared in backend/template.yaml. Table names
come from the function environment. Conditional writes return False on conflict
instead of raising, so callers map them to contract statuses.
"""

import functools
import logging
import os
import re
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr, Key
from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError


@functools.cache
def _dynamodb(config=None):
    if config is not None:
        return boto3.resource("dynamodb", config=config)
    return boto3.resource("dynamodb")


def _table(variable, config=None):
    dynamodb = _dynamodb(config) if config is not None else _dynamodb()
    return dynamodb.Table(os.environ[variable])


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
    # Strongly consistent: profile.revision feeds the panel revision, which never decreases.
    return _table("PROFILES_TABLE").get_item(
        Key={"profileId": profile_id}, ConsistentRead=True).get("Item")


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
        "playerIds", "eventTime", "correctionOf", "period", "scoringPlay", "matchup",
        "channel", "sport"}))


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
# lineupVersion is a store-allocated monotonic content version: it advances
# on every content change (including a change back and an empty/removal
# row, which is the retained tombstone) and is preserved on an identical
# rewrite. get_lineup hides it so the stored Lineup shape is unchanged;
# panel reads it through get_lineup_version.
_LINEUP_FIELDS = {"profileId", "source", "sport", "team", "league", "starters", "scoring",
                  "updatedAt"}
_LINEUP_CONTENT = ("source", "sport", "team", "league", "starters", "scoring")


def _lineup_row(profile_id):
    # Strongly consistent: a lagging replica would serve a lower lineupVersion.
    return _table("LINEUPS_TABLE").get_item(
        Key={"profileId": profile_id}, ConsistentRead=True).get("Item")


MAX_STARTERS = 32  # frozen panel row bound the TV decoder enforces


def _check_starters(item):
    """Reject rows the panel cannot serve: over 32 starters, blank or repeated ids."""
    if "starters" not in item:
        return
    starters = item["starters"]
    if not isinstance(starters, list) or len(starters) > MAX_STARTERS:
        raise ValueError(f"Lineup starters must be a list of at most {MAX_STARTERS}")
    key = "player_key" if item.get("source") == "yahoo" else "athlete_id"
    ids = [starter.get(key) if isinstance(starter, dict) else None for starter in starters]
    if any(not isinstance(i, str) or not i.strip() for i in ids):
        raise ValueError(f"Every lineup starter needs a non-blank {key}")
    if len(set(ids)) != len(ids):
        raise ValueError(f"Lineup starters repeat a {key}")


def put_lineup(lineup):
    """Store a lineup and return the content version allocated by its successful CAS."""
    item = _shaped(dict(lineup), _LINEUP_FIELDS | {"lineupVersion"})
    item.pop("lineupVersion", None)  # allocated here, never caller-supplied
    _check_starters(item)
    table = _table("LINEUPS_TABLE")
    for _attempt in range(3):
        current = _lineup_row(item["profileId"])
        version = int(current.get("lineupVersion", 0)) if current else 0
        unchanged = (current is not None and "lineupVersion" in current and all(
            current.get(field) == item.get(field) for field in _LINEUP_CONTENT))
        item["lineupVersion"] = version if unchanged else version + 1
        if current is None:
            condition = Attr("profileId").not_exists()
        elif "lineupVersion" in current:
            condition = Attr("lineupVersion").eq(version)
        else:
            condition = Attr("lineupVersion").not_exists()
        if _written(table.put_item, Item=item, ConditionExpression=condition):
            return item["lineupVersion"]
    raise RuntimeError(f"lineup write for {item['profileId']} kept losing races")


def _without_version(row):
    if row is None or not (set(row) - {"profileId", "lineupVersion", "updatedAt"}):
        return None
    return {key: value for key, value in row.items() if key != "lineupVersion"}


def get_lineup(profile_id):
    return _without_version(_lineup_row(profile_id))


def get_lineup_version(profile_id):
    """Monotonic lineup content version; 0 for no row or a legacy row."""
    row = _lineup_row(profile_id)
    return int(row.get("lineupVersion", 0)) if row else 0


def get_lineup_with_version(profile_id):
    """Single-read (lineup or None, monotonic lineupVersion) so snapshot never tears."""
    row = _lineup_row(profile_id)
    return _without_version(row), (int(row.get("lineupVersion", 0)) if row else 0)


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
    # Strongly consistent: freshness.counter feeds the panel revision, which never decreases.
    return _table("PANELS_TABLE").get_item(
        Key={"profileId": profile_id, "teamLeague": team_league}, ConsistentRead=True).get("Item")


# Pregame slate: one reserved PlayerStats item, replaced on each pregame poll.
# "pregame" is not an athlete id (those are numeric), so a statistics write
# cannot overwrite it and a player lookup cannot read it.
_PREGAME_ID = "pregame"
_PREGAME_TEAM = re.compile(r"[A-Z0-9]{2,4}")
NBA_PREGAME_WINDOW = 12 * 60 * 60
MAX_PREGAME_SEQUENCE = (1 << 24) - 1


def put_nba_pregame(teams, *, config=None):
    """Replace even an empty slate, allocating a sequence with PutItem-only IAM."""
    if not isinstance(teams, dict):
        return False
    clean = {}
    for abbr, detail in teams.items():
        if (isinstance(abbr, str) and _PREGAME_TEAM.fullmatch(abbr)
                and isinstance(detail, str) and detail.strip() and len(detail) <= 80):
            clean[abbr] = detail
    if teams and not clean:
        return False
    table = (_table("PLAYER_STATS_TABLE", config) if config is not None
             else _table("PLAYER_STATS_TABLE"))
    previous = None
    for _ in range(16):
        moment = datetime.now(timezone.utc)
        sequence = 1
        condition = Attr("athleteId").not_exists()
        if previous is not None:
            try:
                stamp = datetime.fromisoformat(previous.get("asOf", "").replace("Z", "+00:00"))
                expired = (moment - stamp).total_seconds() > NBA_PREGAME_WINDOW
            except (ValueError, TypeError, AttributeError):
                expired = True
            sequence = int(previous.get("sequence", 0))
            # Refreshing an expired slate must outrun the panel's expiry bit.
            sequence += int(previous.get("teams") != clean or expired or not sequence)
            condition = Attr("athleteId").exists()
            for field in ("sequence", "asOf", "teams"):
                condition &= (Attr(field).eq(previous[field]) if field in previous
                              else Attr(field).not_exists())
        if sequence > MAX_PREGAME_SEQUENCE:
            raise ClientError({"Error": {"Code": "SequenceExhausted",
                                         "Message": "NBA pregame sequence exhausted"}}, "PutItem")
        item = {"athleteId": _PREGAME_ID, "sequence": sequence, "teams": clean,
                "asOf": moment.strftime("%Y-%m-%dT%H:%M:%SZ")}
        try:
            table.put_item(Item=item, ConditionExpression=condition,
                           ReturnValuesOnConditionCheckFailure="ALL_OLD")
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise
            previous = {key: TypeDeserializer().deserialize(value)
                        for key, value in exc.response.get("Item", {}).items()} or None
            conflict = exc
    raise conflict


def get_nba_pregame():
    return _table("PLAYER_STATS_TABLE").get_item(
        Key={"athleteId": _PREGAME_ID}, ConsistentRead=True).get("Item")


# Player statistics: latest stored boxscore per ESPN athlete (panel seam).
# One record per athlete; the panel refuses a record from another game than
# the starter's latest projected game, so no gameId range key is needed.
MAX_STATS_VERSION = (1 << 24) - 1
_STATS_FIELDS = {"athleteId", "gameId", "gameState", "gameStatus", "source", "asOf", "stats"}


def _statistics_item(record):
    item = {key: value for key, value in _shaped(record, _STATS_FIELDS).items()
            if not (key == "asOf" and value is None)}
    athlete_id = item.get("athleteId")
    if not isinstance(athlete_id, str) or not re.fullmatch(r"[0-9]{1,20}", athlete_id):
        logging.getLogger(__name__).warning(
            "Skipping player statistics write with invalid athleteId: %.40r", athlete_id)
        return None
    return item


def _put_statistics(item, table, previous, commit, *, require_clock=False, channel=None):
    """Allocate one bounded content version; a lost CAS recomputes the transition."""
    for _attempt in range(4):
        if previous:
            old_stamp, new_stamp = previous.get("asOf"), item.get("asOf")
            if ((require_clock and not isinstance(new_stamp, str))
                    or (old_stamp is not None and (not isinstance(new_stamp, str)
                        or not isinstance(old_stamp, str) or old_stamp > new_stamp))):
                return False
            if (previous.get("gameId") == item.get("gameId")
                    and previous.get("source") == "live" and item.get("source") == "replay"):
                return False
            if all(previous.get(key) == item.get(key) for key in _STATS_FIELDS):
                return False
        version = int(previous.get("statsVersion", 0)) + 1
        if version > MAX_STATS_VERSION:
            raise RuntimeError("player statistics content sequence exhausted")
        previous = commit(table, item, previous, version, channel=channel)
        if previous is None:
            return True
    raise RuntimeError("player statistics write kept losing races")


def _statistics_condition(previous):
    if not previous:
        return {"ConditionExpression": "attribute_not_exists(athleteId)"}
    names, values, conditions = {}, {}, []
    # Include absent fields so legacy and versioned writers share the same CAS.
    for index, key in enumerate(sorted(_STATS_FIELDS | {"statsVersion", "nbaMilestones"})):
        name, value = f"#f{index}", f":v{index}"
        names[name] = key
        if key in previous:
            conditions.append(f"{name} = {value}")
            values[value] = previous[key]
        else:
            conditions.append(f"attribute_not_exists({name})")
    return {"ConditionExpression": " AND ".join(conditions),
            "ExpressionAttributeNames": names, "ExpressionAttributeValues": values}


def _commit_statistics(table, item, previous, version, *, channel=None):
    try:
        accepted = dict(item, statsVersion=version)
        if previous.get("gameId") == item.get("gameId") and "nbaMilestones" in previous:
            accepted["nbaMilestones"] = previous["nbaMilestones"]
        table.put_item(Item=accepted, **_statistics_condition(previous),
                       ReturnValuesOnConditionCheckFailure="ALL_OLD")
        return None
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise
        return TypeDeserializer().deserialize({"M": exc.response.get("Item", {})})


def put_player_statistics(record, *, config=None):
    """CAS a content sequence using only PutItem and its conflict response."""
    item = _statistics_item(record)
    if item is None:
        return False
    table = (_table("PLAYER_STATS_TABLE") if config is None
             else _table("PLAYER_STATS_TABLE", config))
    return _put_statistics(item, table, {}, _commit_statistics)


def _commit_nba_statistics(table, item, previous, version, *, channel):
    from nba.alerts import game_events, milestones

    same_game = previous.get("gameId") == item.get("gameId")
    seen = (set(previous.get("nbaMilestones", [])) | milestones(previous)) if same_game else set()
    accepted = dict(item, statsVersion=version, nbaMilestones=sorted(seen | milestones(item)))
    events = game_events(item, previous, channel=channel, version=version)
    request = {"TableName": table.name, "Item": accepted}
    request.update(_statistics_condition(previous))
    try:
        table.meta.client.transact_write_items(TransactItems=[{"Put": request}] + [
            {"Put": {"TableName": os.environ["EVENTS_TABLE"], "Item": event}} for event in events])
        return None
    except ClientError as exc:
        if (exc.response["Error"]["Code"] != "TransactionCanceledException"
                or not any(reason.get("Code") in ("ConditionalCheckFailed", "TransactionConflict")
                           for reason in exc.response.get("CancellationReasons", []))):
            raise
        return table.get_item(Key={"athleteId": item["athleteId"]},
                              ConsistentRead=True).get("Item", {})


def put_nba_statistics(record, *, config=None, channel=None):
    """Commit the shared accepted version and its immutable NBA events atomically."""
    item = _statistics_item(record)
    if item is None:
        return False
    table = _table("PLAYER_STATS_TABLE", config)
    previous = table.get_item(Key={"athleteId": item["athleteId"]},
                              ConsistentRead=True).get("Item", {})
    return _put_statistics(item, table, previous, _commit_nba_statistics,
                           require_clock=True, channel=channel)


def get_player_statistics(athlete_id):
    return _table("PLAYER_STATS_TABLE").get_item(
        Key={"athleteId": athlete_id}, ConsistentRead=True).get("Item")
