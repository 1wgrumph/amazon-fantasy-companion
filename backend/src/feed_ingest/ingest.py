"""Validate, normalize and store ESPN polls and labeled replay (DES-AFC-P2-FEED)."""

import logging

from botocore.exceptions import BotoCoreError, ClientError

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


def store_player_statistics(records):
    """Overwrite each athlete's stored boxscore with the latest summary's."""
    for record in records:
        try:
            store.put_player_statistics(record)
        except (ClientError, BotoCoreError, ValueError, ArithmeticError, TypeError, KeyError) as exc:
            logging.getLogger(__name__).warning("Skipping failed player statistics write: %s", exc)


def ingest_summary(payload, game_id, source="live"):
    """Validate before any event read or write, then store new or corrected plays."""
    validate_summary(payload, game_id)
    events = store_events(normalize_summary(payload, game_id, source=source))
    store_player_statistics(boxscore_statistics(payload, game_id, source=source))
    return events
