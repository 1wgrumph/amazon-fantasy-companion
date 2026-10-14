"""Validate, normalize and store one ESPN summary poll (DES-AFC-P2-FEED)."""

import store
from feed_ingest.normalize import _plays, normalize_summary
from feed_ingest.validation import validate_summary


def ingest_summary(payload, game_id, source="live"):
    """Store the poll's new or corrected GameEvents in place and return them.

    Validation runs before any read or write, so a rejected poll leaves the table unchanged.
    """
    validate_summary(payload, game_id)
    prior = {}
    for play in _plays(payload):
        stored = store.get_event(game_id, play["id"])
        if stored is not None:
            prior[play["id"]] = stored
    events = normalize_summary(payload, game_id, source=source, prior=prior)
    for event in events:
        store.put_event(event)
    return events
