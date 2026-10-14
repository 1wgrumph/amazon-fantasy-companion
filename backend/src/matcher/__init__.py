"""DES-AFC-P2-MATCH identity, deduplication and corrections.

AFC-STUB module: P2-B04 replaces each body; the signatures are final.
"""


def _pending():
    return "AFC-STUB: matcher is implemented by P2-B04"


def resolve(game_event):
    """AFC-STUB (P2-B04): Profiles and starters the GameEvent concerns, keyed by (profile, event id); corrections revise, never duplicate."""
    raise NotImplementedError(_pending())
