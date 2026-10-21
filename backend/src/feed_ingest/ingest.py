"""Validate, normalize and store ESPN polls and labeled replay (DES-AFC-P2-FEED)."""

import logging

from botocore.exceptions import ClientError

import store
from feed_ingest.normalize import boxscore_statistics, normalize_summary
from feed_ingest.validation import validate_summary


def store_events(events):
    """Apply the same monotonic revision path to validated live or replay events."""
    changed = []
    for event in events:
        before = store.get_event(event["gameId"], event["eventId"])
        if before is not None:
            facts = {key: value for key, value in event.items()
                     if key not in ("revision", "correctionOf")}
            if all(key not in before or before[key] == value for key, value in facts.items()):
                continue
            event = dict(event, revision=int(before["revision"]) + 1,
                         correctionOf=int(before["revision"]))
        store.put_event(event)
        changed.append(event)
    return changed


def rejected_item(exc):
    """True for a write DynamoDB refused for the item's own shape (payload-caused)."""
    return isinstance(exc, ClientError) and exc.response.get("Error", {}).get("Code") == "ValidationException"


def store_player_statistics(records, *, config=None):
    """Overwrite each athlete's stored boxscore with the latest summary's.

    Only an item rejected for its own content is skipped; any other failure
    (access, missing table, throttling, endpoint) propagates so outages stay visible.
    """
    skipped, first = 0, None
    for record in records:
        try:
            if config is None:
                store.put_player_statistics(record)
            else:
                store.put_player_statistics(record, config=config)
        except (ClientError, ArithmeticError) as exc:
            if isinstance(exc, ClientError) and not rejected_item(exc):
                raise
            skipped, first = skipped + 1, first or exc
    if skipped:
        logging.getLogger(__name__).warning(
            "Skipped %d player statistics writes rejected as invalid (first: %.200s)",
            skipped, f"{type(first).__name__}: {first}")


def ingest_summary(payload, game_id, source="live"):
    """Validate before any event read or write, then store new or corrected plays."""
    validate_summary(payload, game_id)
    events = store_events(normalize_summary(payload, game_id, source=source))
    store_player_statistics(boxscore_statistics(payload, game_id, source=source))
    return events
