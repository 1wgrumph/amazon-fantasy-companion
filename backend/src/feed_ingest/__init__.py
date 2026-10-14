"""DES-AFC-P2-FEED ESPN ingest and labeled replay (IngestFunction).

AFC-STUB module: P2-B02 replaces each body; the signatures are final.
"""


def _pending():
    return "AFC-STUB: feed_ingest is implemented by P2-B02"


def lambda_handler(event, context):
    """AFC-STUB (P2-B02): IngestFunction entry: poll each profile-relevant in-progress game every feed_poll_interval, validate, normalize and store GameEvents."""
    raise NotImplementedError(_pending())
