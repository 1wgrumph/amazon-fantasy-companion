"""DES-AFC-P2-POLICY alert gates and commentary.

AFC-STUB module: P2-B05 replaces each body; the signatures are final.
"""


def _pending():
    return "AFC-STUB: alert_policy is implemented by P2-B05"


def evaluate(game_event, matches):
    """AFC-STUB (P2-B05): Alert items (store.put_alert shape) the policy gates admit for the matched profiles."""
    raise NotImplementedError(_pending())


def pending(profile_id, cursor):
    """AFC-STUB (P2-B05): GET /v1/alerts body: {"alerts": [enveloped Alert], "cursor": str}, after cursor (None = start)."""
    raise NotImplementedError(_pending())
