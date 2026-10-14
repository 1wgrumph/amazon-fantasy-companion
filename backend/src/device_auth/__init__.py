"""DES-AFC-P2-AUTH device-code linking and bearer sessions.

The TV gets an 8-character code and a separate polling handle. The customer
confirms the code on a phone with the owner passphrase held in SSM SecureString.
The first poll after confirmation receives a 256-bit opaque session token; only
SHA-256 hashes of the handle and the token are stored.
"""

import hashlib
import hmac
import os
import secrets
import time
from datetime import datetime, timezone

import boto3

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
    """Report the link state; the first poll after confirmation carries the session token."""
    link = store.find_link(_digest(handle))
    if link is None:
        return {"state": "unlinked"}
    if link["state"] == "codePending":
        return {"state": "expired" if link["expiresAt"] <= time.time() else "codePending"}
    if link["state"] == "confirmed" and store.complete_link(link["code"]):
        token = secrets.token_urlsafe(32)
        store.put_session(_digest(token), link["profileId"], _rfc3339(time.time()))
        return {"state": "linked", "sessionToken": token}
    return {"state": "linked"}


def confirm(code, passphrase, profile_id):
    """Return "linked", "unauthorized" (wrong passphrase) or "gone" (unknown, used or expired)."""
    secret = boto3.client("ssm").get_parameter(
        Name=os.environ["LINK_PASSPHRASE_PARAMETER"], WithDecryption=True)["Parameter"]["Value"]
    if not hmac.compare_digest(passphrase.encode(), secret.encode()):
        return "unauthorized"
    if store.confirm_link(code.strip().upper(), profile_id, int(time.time())):
        return "linked"
    return "gone"


def authenticate(token):
    """Profile bound to a bearer session token, or None."""
    session = store.get_session(_digest(token)) if token else None
    return session["profileId"] if session else None
