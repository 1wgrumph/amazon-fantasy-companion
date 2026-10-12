# Slice graph — AFC-2026-10-11 Phase 1 (Planning and Design input for RE, IE, TE and Plan Integrator; owner change DEC-AFC-SD-023)

This file plus `design.md` is the source of truth for slice content. The Plan
Integrator copies it into `implementation.json`. Command IDs are proposals;
the Planning Test Engineer finalizes them in `seit.json`. Slice IDs are kept
from f885e48. S42 is new. Every f885e48 slice that is not listed here moved
to Phase 2 (technical plan §Deferred to Phase 2).

Lanes and frozen profiles (DEC-AFC-PROFILE-001):

- `spec-and-docs` = tech-writing.
- `ci` = primary. This is the `backend` lane profile; no backend work is
  in Phase 1.
- Light Implementer slices use the lane profile's `light_implementer`
  route.
- The Scribe slice uses the planning profile `primary` `scribe` route.

`repo` is `this` (1wgrumph/amazon-fantasy-companion) unless it says
`Alphazedehq` (alphazede/Alphazedehq), which is a cross-repo write set with
its own pull request per slice.

## Waves

- Wave 1: S01 S02 S03 S06 S07
- Wave 2: S06L S42 S09T S09 S11T S11 S41 S08

Concurrency is impl_agent_cap = 5; the Scribe does not count.

- Wave 1 dispatches all five at approval.
- Wave 2 slices dispatch as their dependencies merge. At most five run at
  once.
- S41 runs only if OD-AFC-01 = B.

## Slices

| ID | Lane (profile) | Role | Type / work_class | Depends on | Requirements | Design | Write set | Lease | Commands | Stop condition |
|---|---|---|---|---|---|---|---|---|---|---|
| S01 | spec-and-docs (tech-writing) | Product Implementer | skill / judgement | — | AC-AFC-D4-01, AC-AFC-D4-05, AC-AFC-D4-06 | DES-AFC-D4, CONTRACT-AFC-GATE | Alphazedehq: `skills/setup-pre-commit/SKILL.md`, `skills/setup-pre-commit/agents/openai.yaml`, `skills/setup-pre-commit/references/gate-contract.md`, `skills/setup-pre-commit/templates/gate.sh`, `skills/setup-pre-commit/scripts/install-hooks.sh`, `skills/setup-pre-commit/tests/test-install-hooks.sh` | alphazedehq-skills (setup-pre-commit) | CMD-D4A-TEST, CMD-SKILL-SIZE, CMD-SKILL-TRIGGER | Tests and size check exit 0; trigger check routes both requests correctly; PR open in Alphazedehq. |
| S02 | spec-and-docs (tech-writing) | Product Implementer | skill / judgement | — | AC-AFC-D4-02, AC-AFC-D4-05, AC-AFC-D4-06 | DES-AFC-D4 | Alphazedehq: `skills/setup-a-repo/SKILL.md`, `skills/setup-a-repo/references/workflow-authoring.md`, `skills/setup-a-repo/templates/ci.yml`, `skills/setup-a-repo/scripts/check-workflows.py`, `skills/setup-a-repo/tests/test_check_workflows.py` | alphazedehq-skills (setup-a-repo) | CMD-D4B-TEST, CMD-SKILL-SIZE, CMD-SKILL-TRIGGER | Checker tests exit 0; template passes the checker; PR open. |
| S03 | spec-and-docs (tech-writing) | Product Implementer | skill / judgement | — | AC-AFC-D4-03, AC-AFC-D4-05, AC-AFC-D4-06 | DES-AFC-D4 | Alphazedehq: `skills/ship-pull-request/SKILL.md`, `skills/ship-pull-request/references/GATES.md`, `skills/ship-pull-request/references/EDIT-PR.md` | alphazedehq-skills (ship-pull-request) | CMD-D4C-TEST, CMD-SKILL-SIZE, CMD-SKILL-TRIGGER | Existing `tests/edit-pr.test.sh` passes; size check exit 0; PR open. |
| S06 | spec-and-docs (tech-writing) | Product Implementer | skill / judgement | — | AC-AFC-D5-01, AC-AFC-D5-02, AC-AFC-D5-03, AC-AFC-D5-04, AC-AFC-D5-05, RISK-AFC-13, RISK-AFC-15 | DES-AFC-D5, CONTRACT-AFC-SPECKIT | Alphazedehq: `skills/spec-authoring/` (whole new directory: `SKILL.md`, `agents/openai.yaml`, `references/section-rules.md`, `references/figures.md`, `references/vendoring.md`, `template/`, `scripts/spec_build.py`, `scripts/spec_lint.py`, `scripts/diagram.py`, `scripts/azdiagram/`, `scripts/vendor.sh`, `tests/`, `LICENSE-gridmarket`), `skills/use-requirements-system/SKILL.md` (description lines only, OD-AFC-07) | alphazedehq-skills (spec-authoring, use-requirements-system) | CMD-SCAN, CMD-D5-TEST, CMD-D5-AGNOSTIC, CMD-SKILL-SIZE, CMD-SKILL-TRIGGER | Tests, repo-agnostic build and size check exit 0; trigger check routes both requests correctly; PR open in Alphazedehq. |
| S07 | spec-and-docs (tech-writing) | Product Implementer | docs / judgement | — | AC-AFC-VNV-01 | DES-AFC-VNV | this: `docs/vnv/` | — | CMD-VNV-CHECK | Index plus ci-cd, spec and developer-feedback area files, each with Scope, Tools, Review Focus, Findings target. |
| S06L | spec-and-docs (tech-writing) | Light Implementer | link / light | S06 merged; alphazedehq-main-checkout at or after the S06 merge commit | AC-AFC-D5-05 | DES-AFC-D5 | this: `docs/plans/2026-10-11-amazon-fantasy-companion/evidence/skill-links.txt` | harness-configs, alphazedehq-main-checkout | CMD-SKILL-LINK | `readlink` of the four harness links resolves to the merged skill directory. |
| S42 | spec-and-docs (tech-writing) | Light Implementer | vendor / light | S06 merged; alphazedehq-main-checkout at or after the S06 merge commit | AC-AFC-SPEC-01, AC-AFC-D5-04 | DES-AFC-D5, CONTRACT-AFC-SPECKIT | this: `tools/spec/`, `THIRD_PARTY_NOTICES.md` | alphazedehq-main-checkout | CMD-SPEC-VENDOR | `tools/spec/VENDORED.md` names a source commit whose `skills/spec-authoring/` tree id equals that of the merged D5 commit; vendored files (scripts and template) equal that tree; MIT notice present in both files (IE-P1-F03). |
| S09T | ci (primary) | Test Implementer | test / judgement | S01, S02, S42 merged | AC-AFC-CI-01, AC-AFC-CI-02, AC-AFC-CI-03, AC-AFC-CI-04, AC-AFC-PATH-01 | DES-AFC-GATE, CONTRACT-AFC-GATE | this: `tools/ci/tests/` | — | CMD-RED | Named tests fail for the missing gate (red receipt). |
| S09 | ci (primary) | Product Implementer | ci / judgement | S09T, S07 merged | AC-AFC-CI-01, AC-AFC-CI-02, AC-AFC-CI-03, AC-AFC-CI-04, AC-AFC-PATH-01, RISK-AFC-08, RISK-AFC-11, RISK-AFC-13 | DES-AFC-GATE, CONTRACT-AFC-GATE | this: `tools/ci/gate.sh`, `tools/ci/check_paths.py`, `tools/ci/check_docs.py`, `tools/ci/check_workflows.py`, `tools/ci/VENDORED.md`, `.githooks/pre-commit`, `.githooks/pre-push`, `.github/workflows/ci.yml` | — | CMD-SCAN, CMD-GATE-HYGIENE, CMD-GATE-DOCS, CMD-GATE-SPEC, CMD-WORKFLOW-CHECK, CMD-GATE-ALL | S09T tests green; workflow checker exit 0; PR shows `gate / spec`, `gate / docs`, `gate / hygiene` green. |
| S11T | ci (primary) | Test Implementer | test / judgement | S01, S02, S03 merged | AC-AFC-D4-04 | DES-AFC-D4, CONTRACT-AFC-HOOK | Alphazedehq: `hooks/test-ci-gate-hook.sh` | — | CMD-RED | Hook tests fail before the hook exists. |
| S11 | ci (primary) | Product Implementer | hook / judgement | S11T, S09 merged, S06 merged, S06L, S41 merged when OD-AFC-01 = B | AC-AFC-D4-04, AC-AFC-D4-05, AC-AFC-D4-06, AC-AFC-D5-05, RISK-AFC-12 | DES-AFC-D4, CONTRACT-AFC-HOOK | Alphazedehq: `hooks/ci-gate-hook.sh`, `hooks/install-ci-gate-hook.py`, `hooks/README.md` | harness-configs | CMD-HOOK-TEST, CMD-HOOK-INSTALL-SANDBOX | Hook tests green; installer `--install --verify` run with HOME set to a temporary directory reports each SD-021 harness as wired or a typed gap and links the D4 and D5 skills into the sandbox Muse skill directory or records a typed gap; the installer writes the hook path of the checkout it runs from; no live harness configuration is edited before merge. The live install (CMD-HOOK-INSTALL) runs at integration step IE-P1-10 from the Alphazedehq main checkout after merge and fast-forward (IE-P1-F04). |
| S41 | spec-and-docs (tech-writing) | Product Implementer | skill / judgement (conditional) | OD-AFC-01 = B; S01, S02, S03 merged | AC-AFC-D4-05, AC-AFC-D4-06 | DES-AFC-D4 | Alphazedehq: `skills/ci-cd/SKILL.md` | alphazedehq-skills (ci-cd) | CMD-SKILL-SIZE, CMD-SKILL-TRIGGER | Not dispatched unless the owner selects option B. |
| S08 | (planning primary) | Scribe | docs / judgement | S09 merged (hygiene area exists); S11 returned; S41 returned or not dispatched; observations accumulate from Wave 1 dispatch (IE-P1-F06) | AC-AFC-DX-01, AC-AFC-DX-02 | DES-AFC-DX | this: `docs/developer-feedback/observations.md` | — | CMD-GATE-HYGIENE | Log carries DX-001..DX-007, planning and Phase 1 observations; hygiene PASS. |

## Dependencies (acyclic)

S06 --> S06L; S06 --> S42; S01 --> S09T; S02 --> S09T; S42 --> S09T;
S09T --> S09; S07 --> S09; S09 --> S08; S01 --> S11T; S02 --> S11T;
S03 --> S11T; S11T --> S11; S09 --> S11; S06 --> S11; S06L --> S11;
S01 --> S41; S02 --> S41; S03 --> S41; S41 --> S11 (only when
OD-AFC-01 = B; IE-P1-F05); S11 --> S08; S41 --> S08 (IE-P1-F06).

## Lifecycle-level rows (no slice)

These rows are proved on dispatch and landing records rather than on a
slice output:

- AC-AFC-DX-01: packets and returns.
- AC-AFC-LAND-01: pull request merge records.
- AC-AFC-REV-01: Reviewer packets.
- AC-AFC-PATH-01 at planning: the Orchestrator's scrub before each
  planning commit.
- AC-AFC-PLAN-01: this plan.
- AC-AFC-PLAN-03: the Integration Engineer execution session at Phase 1
  closeout. It is recorded at
  `docs/plans/2026-10-11-amazon-fantasy-companion/evidence/phase2-entry-receipt.json`
  (contents per integration-plan.md `phase2_entry_receipt`) and landed in
  the Phase 1 closeout pull request with the DoD Manifest closeout
  (IE-P1-F08).
- RISK-AFC-07: route receipts.
- RISK-AFC-16: Phase 2 entry receipt.
- RISK-AFC-17: Phase 2 entry receipt and Phase 2 plan.

## Owner-action entry criteria (not slices)

| Needed by | Owner action |
|---|---|
| Wave 1 | Integrated approval of this Phase 1 package (OD-AFC-01, -06, -07, -08, -09, -10, -12, OA-AFC-A2). |
| Phase 2 product work (not Phase 1) | Stick located, model confirmed, ADB enabled; AWS Free-plan account and named CLI profile; Yahoo application; provider app signed in. These can be done now. |
