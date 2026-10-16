## What changed

- Rewrite the product architecture as specification prose, preserving the floor sections, full source coverage and requirement-register authority.
- Apply SD-035: Off/Mild/Hype, 24/32 px legibility plus owner acceptance, 60-second staleness, the settled close-game rule, PPR/Half-PPR selection, provider spike order and channel/access-aware Watch.
- Replace the footage fallback with the full-screen companion-app panel; retain all 66 UIDs in Appendix A and mark AFC-PR-049, AFC-PR-050 and AFC-PR-051 withdrawn.
- Add verified YouTube competitive context and SD-036 Prime Vision/Next Gen Stats and NBA future discussion. Distinguish historical NFL.com support from the current ESPN/Yahoo help pages.
- Annotate historical footage-related model elements pending Phase 2 design, without editing native models. Keep only Q6, Q7, Q8 and Q10 in the owner open-items table.

## Why

The earlier draft printed the writer’s checklist and reflected decisions superseded by SD-034/035. Revision 0.2 aligns the prose and verification approach with the amended register and keeps SD-036 discussion separate from delivered capability. Apache-2.0 is selected; publication remains separate.

Lease ST-4-g3, input base `4d9b549696408ddaa5f432bac4911cbc349cb874`, spec-and-docs lane. The write set is the specification and ST-4 evidence. Historical g1/g2 evidence remains unchanged.

## Validation

With `UV_OFFLINE=1 UV_PYTHON=3.12 PYTHONDONTWRITEBYTECODE=1`:

- `bash docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g3/verify.sh` — exit 0; exact child commands and outputs in `g3/verification.txt`.
- `uv run --script tools/spec/spec_build.py spec/amazon-fantasy-companion spec/amazon-fantasy-companion/amazon-fantasy-companion.md` — exit 0.
- `uv run --script tools/spec/spec_lint.py spec/amazon-fantasy-companion` — exit 0.
- `uv run --script tools/spec/diagram.py lint spec/amazon-fantasy-companion` — exit 0; all eight figure renders also exit 0.
- `uv run --script tools/spec/spec_build.py spec/amazon-fantasy-companion docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g3/rebuild.tmp.md` — exit 0.
- `cmp spec/amazon-fantasy-companion/amazon-fantasy-companion.md docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g3/rebuild.tmp.md` — exit 0; byte-identical.
- `python3 docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g3/check-spec.py` — exit 0; 66/66 UIDs and Appendix A rows, three withdrawn, no unknown UIDs, local links resolve and write set is bounded.

A log-redirection collision in the initial grep path scan was corrected by reusing the Python shape scanner in silent mode; errors now propagate. The final verification runner records zero-output printed-label and Rule-12 scans and the bounded withdrawal/model-only matches for the footage terms. The generated Markdown’s intentional header hard break is checked separately from source whitespace.

## Residual risk

This is author realization, not independent review or ST-5 owner acceptance. The PR stays draft; merge is prohibited by this packet. Frozen `review.coverage_assist` remains enabled and required, with OCR delegation belonging to the independent reviewer. It was not run by the author and is not passing review evidence. Frozen Reverify remains enabled and is not applicable to this Markdown/SVG claim; no compiled binary is claimed.

The shared `tools/ci/gate.sh` is absent at this base and owned by concurrent S09; no shared-gate pass is claimed. VnV guidance is present under `docs/vnv`; review is still outstanding. BRAN is unavailable without a native policy.

Remaining owner prerequisites: Q6 model/OS, Q7 Yahoo application, Q8 AWS account and Q10 completion of the chosen S8 ledger restoration in Alphazedehq. Phase 2 still owes provider/feed/security/transport contracts, native model alignment, real-stick demonstrations and product verification. No runtime or public capability is established by the external sources. Issue #1 stays open.

AC-AFC-DX-04 developer feedback and the verified source URL list are in `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g3/receipt.json` and `sources.json`.
