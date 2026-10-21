# P2-V01 visual evidence

Guest captures are committed under the milestone evidence directory. Current
feature verdicts are in [feature-verdicts.md](../../../docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-V01/feature-verdicts.md).

| State | Evidence | Current interpretation |
| --- | --- | --- |
| Link requesting, network error and focused retry | [Stage 2](../../../docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2/stage2-summary.md) | Negative network path observed; no successful-link claim from these screens. |
| Link code and the original relaunch failure | [Stage 2c](../../../docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2c/stage2c-summary.md) | Historical token-persistence defect. The two link-code PNG endpoint regions are blanked for public hygiene; exact originals are retained privately. |
| Profile/Settings, saved RedZone and linked relaunch | [bug-token repair](../../../docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/bug-token/summary.md) | Current persistence verdict PASS: saved state restored after terminate/launch without requesting a new code. |
| Default lineup panel and held state | [bug-panel repair](../../../docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/bug-panel/summary.md) | Current empty-state verdict PASS: server identity, Half-PPR, no rows, Total: Unavailable. |
| Review repairs for saved-panel settings, pending requests and stale labels | [review repair](../../../docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/review-repair/summary.md) | Source regressions only; no new device captures in this round. |

The captures are 1920x1080 VVD root windows containing the guest surface and
simulator chrome. Matching checks require the recorded viewport, focus and
converter. Initial boot/capture gaps were superseded by these guest captures;
populated lineup rows, live-value aging on screen, alert banners over playback,
provider Watch playback, app detection and physical Vega remain unverified.
The empty synthetic profile cannot establish those capabilities. Native
data-root messages remain unresolved despite working persistence.
