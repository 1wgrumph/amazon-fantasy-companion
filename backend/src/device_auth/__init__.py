"""DES-AFC-P2-AUTH device-code linking and bearer sessions.

The TV gets an 8-character code and a separate polling handle. The customer
confirms the code on a phone with the code alone (DEC-AFC-SD-048: test device).
While the device-code window is open, every poll after confirmation receives
a 256-bit opaque session token, so a dropped response is recoverable by retry;
each token supersedes the previous one and no token is minted after expiry;
only SHA-256 hashes of the handle and the tokens are stored.
"""

import hashlib
import os
import secrets
import time
from datetime import datetime, timezone

import store


def _digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def _rfc3339(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def issue():
    """Create a pending code (unambiguous base-32, 40 bits) and its polling handle."""
    expires = int(time.time()) + int(os.environ["DEVICE_CODE_TTL_SECONDS"])
    for _ in range(3):
        code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(8))
        handle = secrets.token_urlsafe(32)
        if store.put_link(code, _digest(handle), expires):
            return {"code": code, "expires": _rfc3339(expires), "handle": handle}
    raise RuntimeError("Could not allocate a unique device code")


def poll(handle):
    """Report the link state; a linked poll inside the retry window carries a new session token that supersedes the previous one."""
    link = store.find_link(_digest(handle))
    if link is None:
        return {"state": "unlinked"}
    now = time.time()
    if link["expiresAt"] <= now:
        return {"state": "expired"}
    if link["state"] == "codePending":
        return {"state": "codePending"}
    # The session is persisted before the idempotent completion write, so a
    # failed poll never leaves a completed link without a usable session.
    token = secrets.token_urlsafe(32)
    digest = _digest(token)
    store.put_session(digest, link["profileId"], _rfc3339(now))
    store.complete_link(link["code"])
    prior = store.record_link_session(link["code"], digest)
    if prior and prior != digest:
        store.delete_session(prior)
    return {"state": "linked", "sessionToken": token}


def confirm(code, profile_id):
    """Return "linked" or "gone" (unknown, used or expired)."""
    if store.confirm_link(code.strip().upper(), profile_id, int(time.time())):
        return "linked"
    return "gone"


def authenticate(token):
    """Profile bound to a bearer session token, or None."""
    session = store.get_session(_digest(token)) if token else None
    return session["profileId"] if session else None
