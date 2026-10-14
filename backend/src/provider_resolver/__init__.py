"""DES-AFC-P2-RESOLVE provider route and access basis from registry.json (read-only).

AFC-STUB module: P2-B06 replaces each body; the signatures are final.
"""


def _pending():
    return "AFC-STUB: provider_resolver is implemented by P2-B06"


def resolve(profile_id, event_id):
    """AFC-STUB (P2-B06): Provider, channel, registry route and access basis (verified, customerConfirmed or unknown) for the event."""
    raise NotImplementedError(_pending())


def record_outcome(profile_id, event_id, outcome):
    """AFC-STUB (P2-B06): Record one Watch attempt's RoutingOutcome; returns the stored record."""
    raise NotImplementedError(_pending())


def record_installed_apps(profile_id, packages):
    """AFC-STUB (P2-B06): Record the TV detector's installed package list; returns the stored record."""
    raise NotImplementedError(_pending())
