---
requirements: []
---

## 6 Programming model

**BLUF:** Implement the modeled parts behind typed adapters and one shared source of facts.

**Frame**

- **Who:** Product implementation and verification teams.
- **What:** Programming model.
- **Why:** Preserve the approved experience and its evidence boundaries.
- **How:** Apply the cited register and model contracts.
- **When:** Phase 2 implementation and subsequent verification.
- **Where:** Fire TV companion and AWS backend.

Planned Kotlin components follow the Fire TV starter and contextual placements; the backend is organized by the modeled auth, API, ingest, lineup, matcher, policy, resolver and panel responsibilities. Keep adapters swappable for Yahoo/manual and ESPN/replay without forking downstream truth. Avoid adding a framework or abstraction solely to mirror a diagram.

Treat the schema, identity and revision contracts as shared API artifacts during Phase 2. A UI cache is not the scoring source of truth. Apply row-level updates off the network/parsing path, cancel unneeded subscriptions and retain only declared bounded history. Provider-specific route handling belongs in the registry/launcher boundary, not scattered through notification rendering.
