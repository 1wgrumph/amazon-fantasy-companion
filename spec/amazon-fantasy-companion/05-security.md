---
requirements: ["AFC-PR-037", "AFC-PR-038", "AFC-PR-055", "AFC-PR-056"]
---

## 5 Security

The trust boundary protects customer identity, consent and server-held secrets.

The TV is a client, external feeds and provider routes are untrusted inputs, and AWS owns profile/event processing. The backend authenticates and authorizes profile access before returning data. Yahoo client secrets and tokens remain server-side in SSM SecureString; the APK and repository contain no values. Device linking uses the customer's phone/browser action instead of TV credential entry.

This is a design boundary, not a security review result. Phase 2 must close session lifecycle, code expiry/entropy/rate limiting and account-revocation behavior before deployment acceptance.

Inspection and adversarial contract cases for AFC-PR-037, AFC-PR-038 and AFC-PR-055 check consent, linking and secret containment; the path scan checks AFC-PR-056. These controls stay at the trust boundary so a modified TV client cannot become its own authority.
