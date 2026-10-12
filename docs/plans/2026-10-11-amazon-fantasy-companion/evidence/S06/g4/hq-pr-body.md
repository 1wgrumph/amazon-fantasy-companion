## What changed

- Add a portable Markdown specification workflow with a neutral template, build/lint/diagram commands, and MIT attribution.
- Vendor committed tools with source identity and refuse to overwrite modified downstream copies. Resolve Git paths from the repository root.
- Route SDoc, StrictDoc and Requirements System work to its existing skill and refer requirement quality to requirements-engineering.

## Why

AFC S06 needs reproducible Markdown assembly outside Git and a CI-accessible tool copy without colliding with SDoc authoring. This is the spec-and-docs implementation candidate under AUTH-AFC-2026-10-11-002, lease S06-g4.

## Validation

- `uv run --no-project --with 'pytest==9.0.3' --with 'pyyaml==6.0.3' python -m pytest skills/spec-authoring/tests --ignore=skills/spec-authoring/tests/test_spec_authoring.py -rA` with the prescribed offline scanned-wheel environment: exit 0, 37 passed. Baseline: 36 passed, vendoring regression failed.
- CMD-D5-AGNOSTIC: exit 0; build, section lint and diagram lint outside Git; tracked-file name/home-path scans and MIT notice check passed against dispatch base 47c46f2e16fed060482a1bf3a0e34ddcb9bc57fc.
- CMD-SKILL-SIZE: exit 0; installed creator validation on portable metadata, 46 lines/339 words, pinned BRAN identity and bran-strict passed.
- CMD-SKILL-TRIGGER and reciprocal evaluator: exit 0 each; fresh Read-only Claude sessions returned MATCH/NO_MATCH and NO_MATCH/MATCH respectively.
- `shellcheck skills/spec-authoring/scripts/vendor.sh`: exit 0.
- `git diff --check`: exit 0.
- Full expanded commands, candidate SHAs and logs: planning-worktree evidence/S06/g4 (commands.json and command logs).

## Residual risk

- Draft awaits the configured independent phase review with OCR delegation; no independent review or assurance is claimed. Reverify is not applicable: no compiled binary built or claimed.
- GridMarket source and Python wheel scan receipts pass; historical acquisition receipts for unchanged installed uv and Graphviz were not located. SEIT-AFC-RISK-13.D remains partial.
- Merge/landing and Phase 2 entry proof are outside this implementer packet. The reciprocal requirements-system description change has its own draft PR.
