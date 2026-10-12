## What changed

- Add the D1 architecture specification for retained issue #1 items 1, 2, 3, 4, 6 and the lineup panel, with all 65 gated UIDs in generated Appendix A.
- Define model-grounded allocation, interfaces, data, states, fault handling, lightweight-device design and security boundaries; keep unverified capabilities and owner questions explicit.
- Include eight editable model-derived figures and reproducible offline build/verification evidence.

## Why

ST-4 turns the gated register and ST-3d models into the product architecture candidate for Phase 2. Requirement statements remain in the register. Mode A, replay and manual-lineup fallbacks preserve their distinct triggers and labels. This branch is limited to the specification and ST-4 evidence; it does not implement the product or alter models, tools or CI.

Lease ST-4-g1, tech-writing / single_implementer, input base `5e59270b8320d6085039f26b64f14897736845f6`. Frozen review coverage assistance remains required and Reverify enabled; neither is silently disabled. Reverify is not applicable to the Markdown/SVG artifact claim.

## Validation

Run with `UV_OFFLINE=1 UV_PYTHON=3.12 PYTHONDONTWRITEBYTECODE=1`:

- `bash docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/verify.sh` — exit 0; individual command exits in `verification.txt`.
- `uv run --script tools/spec/spec_build.py spec/amazon-fantasy-companion spec/amazon-fantasy-companion/amazon-fantasy-companion.md` — exit 0.
- `uv run --script tools/spec/spec_lint.py spec/amazon-fantasy-companion` — exit 0.
- `uv run --script tools/spec/diagram.py lint spec/amazon-fantasy-companion` — exit 0; all eight figure render commands also exit 0.
- `uv run --script tools/spec/spec_build.py spec/amazon-fantasy-companion docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/rebuild.tmp.md` — exit 0.
- `cmp spec/amazon-fantasy-companion/amazon-fantasy-companion.md docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/rebuild.tmp.md` — exit 0; identical rebuild.
- `python3 docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/check-spec.py` — exit 0; 65/65 UIDs in document and Appendix A, zero unknown UIDs, resolved local links, clean Rule-12/C7 scan and bounded write set.

The receipt records the default-Python offline cache failure and successful installed-Python 3.12 correction. No network download or vendored-tool edit was needed. Generated Markdown retains the builder’s intentional hard break; a dedicated assertion checks that it is the sole generated trailing-whitespace line.

## Residual risk

Draft by contract: independent review and ST-5 owner acceptance remain outstanding. No merge is authorized in this packet. OCR delegation belongs to the independent reviewer; it was not run by the author.

The shared `tools/ci/gate.sh` is absent at this leased base and is owned by concurrent S09 work; no shared-gate pass is claimed. Vnv status is REFUSED_NO_VNV because this checkout has no guidance tree. These remain integration/review gaps.

Spec section 2 surfaces ST-2 Q2–Q10, the three open owner parameters, default manual scoring and concrete transport/security tuning. Q1 is resolved by SD-027. Device, provider, notification, detection, entitlement, panel composition and conditional voice capabilities still require functional evidence. No runtime API/device verification, hardware benchmark, formal acceptance or public submission is claimed.

Developer feedback for the spec-authoring skill, vendored tools, uv/Python/PyYAML, Graphviz, Git/GitHub CLI and workflow skills is in the ST-4 receipt. Issue #1 remains open.
