## What changed

- Replace printed BLUF/Frame scaffolding in all 38 template sections with unlabeled opening prose.
- Guide authors with an unprinted Decision, Concern, Mechanism, Rationale, Verification checklist.
- Reject retired writer labels and missing opening paragraphs; retain table and figure checks.

## Why

DEC-AFC-SD-034 requires specifications to read in the architect's voice. The builder preserves HTML comments, so this change uses the explicitly authorized no-comment fallback and keeps the checklist in the section-rules reference.

## Validation

- `SPEC_AUTHORING_TRIGGER_RESULTS=<evidence>/trigger-results.json python3 -m pytest skills/spec-authoring/tests -q` — exit 0; 57 passed.
- `python3 skills/spec-authoring/scripts/spec_build.py skills/spec-authoring/template <evidence>/template-built.md` — exit 0.
- `python3 skills/spec-authoring/scripts/spec_lint.py skills/spec-authoring/template` — exit 0.
- `! grep -nE '\*\*(BLUF|Frame|Who|What|Why|How|When|Where):?\*\*' <evidence>/template-built.md` — exit 0.
- `bash tools/ci/local-gates.sh` — exit 0 on committed candidate; 2 applicable gates passed, 15 not applicable. Prior pre-commit run passed all 17 gates.
- BRAN strict validation — exit 0. SKILL.md: 47 lines, 349 words. Installed creator validation and independent MATCH/NO_MATCH trigger evaluation passed.
- Regression before implementation: 34 failures, 3 passes; updated lint: 37/37 focused cases pass.

## Residual risk

- Draft pending the orchestrator's independent review with required OCR coverage assistance. This implementer receipt is not assurance or acceptance.
- Reverify: not applicable — Python and Markdown changes; no compiled binary is built or claimed.
- Template placeholders remain authoring scaffolds; lint cannot prove semantic prose quality.
- AFC spec rewrite and merge are outside this packet.
