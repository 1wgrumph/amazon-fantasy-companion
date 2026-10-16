---
requirements: []
---

## 6 Programming model

Implement the modeled parts behind typed adapters and one shared source of facts.

Planned Kotlin components follow the Fire TV starter and contextual placements; the backend is organized by the modeled auth, API, ingest, lineup, matcher, policy, resolver and panel responsibilities. Keep adapters swappable for Yahoo/manual and ESPN/replay without forking downstream truth. Avoid adding a framework or abstraction solely to mirror a diagram.

Treat the schema, identity and revision contracts as shared API artifacts during Phase 2. A UI cache is not the scoring source of truth. Apply row-level updates off the network/parsing path, cancel unneeded subscriptions and retain only declared bounded history. Provider-specific route handling belongs in the registry/launcher boundary, not scattered through notification rendering.

This arrangement supports AFC-PR-058 and AFC-PR-059 without turning every model element into a framework layer. Contract tests exercise adapters at their real boundaries, and the AFC-PR-061 through AFC-PR-063 checks verify incremental rendering, bounded state and thread placement.
