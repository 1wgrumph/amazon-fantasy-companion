---
requirements: []
---

## 4 Feature architecture

The feature architecture keeps one backend truth and a small TV presentation layer.

The decomposition below follows the retained issue items and the model allocations. Backend ingestion can be shared across relevant viewers, but filtering and delivery stay profile-scoped. No planned module name establishes implementation completion.

AFC-PR-058 through AFC-PR-060 motivate this division: the API exposes a small product surface while processing and filtering remain backend responsibilities. Source inspection and deployed API cases check placement and profile relevance separately.
