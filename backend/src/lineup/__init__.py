"""DES-AFC-P2-LINEUP lineup sources (Yahoo read-only or labeled manual) and scoring presets.

AFC-STUB module: P2-B03 replaces each body; the signatures are final.
"""


def _pending():
    return "AFC-STUB: lineup is implemented by P2-B03"


def active_lineup(profile_id):
    """AFC-STUB (P2-B03): The profile's one active Lineup (source, team, league, starters, scoring), or None."""
    raise NotImplementedError(_pending())
