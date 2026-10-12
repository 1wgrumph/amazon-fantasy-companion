---
requirements: ["AFC-PR-037", "AFC-PR-038", "AFC-PR-055", "AFC-PR-056"]
---

## 5 Security

**BLUF:** The trust boundary protects customer identity, consent and server-held secrets.

**Frame**

- **Who:** Product implementation and verification teams.
- **What:** Security.
- **Why:** Preserve the approved experience and its evidence boundaries.
- **How:** Apply the cited register and model contracts.
- **When:** Phase 2 implementation and subsequent verification.
- **Where:** Fire TV companion and AWS backend.

The TV is a client, external feeds and provider routes are untrusted inputs, and AWS owns profile/event processing. The backend authenticates and authorizes profile access before returning data. Yahoo client secrets and tokens remain server-side in SSM SecureString; the APK and repository contain no values. Device linking uses the customer's phone/browser action instead of TV credential entry.

This is a design boundary, not a security review result. Phase 2 must close session lifecycle, code expiry/entropy/rate limiting and account-revocation behavior before deployment acceptance.
