"""Validate, normalize and store ESPN polls and labeled replay (DES-AFC-P2-FEED)."""

import store
from feed_ingest.normalize import normalize_summary
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


def ingest_summary(payload, game_id, source="live"):
    """Validate before any event read or write, then store new or corrected plays."""
    validate_summary(payload, game_id)
    return store_events(normalize_summary(payload, game_id, source=source))
