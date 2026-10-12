---
type: specialist-receipt
title: Planning Test Engineer — AFC-2026-10-11 — Phase 1 SEIT regeneration
okf_status: draft
tags: [test-engineering, planning, afc, seit]
---

# Planning Test Engineer receipt — Phase 1 SEIT

**Outcome: PASS.** `seit.json` was regenerated for Phase 1 and is valid against `seit.schema.json`. All 32 Phase 1 AC-AFC and RISK-AFC rows have proof cases, and no deferred product row has one. One proof row, SEIT-AFC-RISK-17, can only be OPEN_CARRIED at Phase 1 closeout. It closes at P2-6 (TE-P1-F07). That status is planned, and it is not a stop.

- **Verdict:** the tailored V&V plan is complete for Phase 1:
  - 54 proof cases and 54 traceability rows;
  - 46 commands and procedures;
  - gate claims declared for the `ci` lane;
  - the `spec-and-docs` lane rests on its own tests.

  Every command id in the slice graph exists. The integration sequence follows IE-P1-1..IE-P1-12.
- **candidate_ref:** `plan/2026-10-11-amazon-fantasy-companion` at `f885e48e58a6c10fa716b6c5ef048a71980a977a` plus working-tree changes. The bound inputs and their sha256 at write time:
  - `amazon-fantasy-companion-technical-plan.md`: `2c8aa8f61fe2faa71287d0ad91d4595b91f9bb082ebebbdeb50b5f0b6fe24f08`
  - `design.md`: `0ef4414e9420b6377d04ce4d530cfb7d66335d246ebd452b7cf64115588278f8`
  - `views/views.json`: `8618f13d87a1bed662976e99afcb55f63bef0e98ea3a506372482d9642100435`
- **Output:** `seit.json` sha256 `e35fca6781f3ae3b80862c359709e2b014d48c632389645c6fa6c5cdd45f7bf8`.
- **changed_paths** (nothing committed):
  - `docs/plans/2026-10-11-amazon-fantasy-companion/seit.json`
  - `docs/plans/2026-10-11-amazon-fantasy-companion/specialists/test-engineer-receipt.md`
- **blocker:** none.

## What changed from f885e48

- **Kept with stable ids.** These proof cases and commands were kept where still valid:
  - D4 and D5;
  - CI-01..03, VNV-01, DX-01/02;
  - LAND-01, REV-01, PATH-01;
  - RISK-07, -08, -11, -12, -13, -15, -16.
- **Dropped.** All product proof cases and commands, for example PROF, MON, FEED, ALERT, WATCH, CTRL, PANEL, SPIKE, SEC, LW, SPEC-02/03, PLAN-02, DX-03, SUB, VIS, RISK-01..06/09/10/14, and the device, AWS, APK and Reverify commands.
- **Amended rows.**
  - CI-01: three areas, plus a new `.K` hooks-path row.
  - SPEC-01: the D1 ordering check is removed.
  - VNV-01: three areas.
  - DX-02: the log only.
  - PLAN-01: waves plus the no-milestone check `.M`.
  - REV-01.R: the Reverify not-applicable packet check replaces the APK Reverify.
  - RISK-13: split into `.D` (S06) and `.G` (S09/S11).
  - RISK-16: now proved by the entry receipt.
  - RISK-11: adds `.P` for the planning scrub.
- **New rows.**
  - AC-AFC-CI-04: `.U` unit, `.S` spec area, `.D` docs area.
  - AC-AFC-PLAN-03: PROC-PHASE2-ENTRY.
  - RISK-AFC-17: PROC-PHASE2-PLAN-INSPECT.
  - D5-04.V: the vendor step in use at S42.
  - D4-04.X: the sandbox installer at S11.
- **New commands.**
  - CMD-GATE-DOCS, CMD-NO-MILESTONE, CMD-REVIEW-PACKET-CHECK.
  - CMD-COVERAGE-CI, CMD-MUTATION-CI, CMD-COVERAGE-HOOK, CMD-MUTATION-HOOK.
  - From the IE plan: CMD-HOOK-INSTALL-SANDBOX, CMD-AZHQ-SKILL-TESTS, CMD-SKILL-UNLINK, CMD-HOOKSPATH.
  - PROC-PHASE2-ENTRY and PROC-PHASE2-PLAN-INSPECT.
- **Not applicable in Phase 1.** Reverify is recorded in every proof case as `Reverify: not applicable — Phase 1 changes are skill text, shell and Python scripts and workflow YAML; no compiled binary is built or claimed`. CMD-OCR-DELEGATE is kept.
- **Gate claims.**
  - `ci` lane (primary, tdd, assurance enabled):
    - red-then-green: unittest, and the bash hook tests;
    - changed-line coverage: coverage.py + diff-cover via uv, at least 90 %;
    - mutation: mutmut 2.x via uvx, at least 0.70.
  - Shell coverage and shell mutation are declared typed gaps (TOOL_MISSING), because kcov and a shell mutation tool are absent.
  - `spec-and-docs` lane (tech-writing, assurance disabled): red-then-green, coverage and mutation are NOT_APPLICABLE with reasons. Its gate is the skills' own tests plus the size, agnostic and trigger checks (OA-AFC-A2 option A).

## Reconciliation during this session

The Integration Engineer Phase 1 plan landed at 19:43. The Orchestrator applied its findings to the technical plan, `design.md` and `slice-graph.md` at 19:45, while this session was running.

The first coverage cross-check caught the change: `missing: ['CMD-HOOK-INSTALL-SANDBOX']`. I re-read the changed inputs and reconciled them:

- the S11 sandbox install and the live install at IE-P1-10 (IE-P1-F04);
- template vendoring and tree-id pinning in CMD-SPEC-VENDOR (IE-P1-F03);
- the entry receipt path `evidence/phase2-entry-receipt.json` (IE-P1-F08);
- the D4/D5 suite rerun CMD-AZHQ-SKILL-TESTS (IE-P1-F09);
- landing on a private repository, where CMD-LANDING-CHECK now proves no force-push by ancestor checks (IE-P1-F10);
- the new open item OA-AFC-A3.

The requirement rows were unchanged: a diff of the technical plan shows only the §Program plan, Exit criteria and owner-items edits. The digests above are of the reconciled inputs.

## Commands run and output

Schema validation and coverage cross-check: `python3 <scratch>/verify.py $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/schemas/seit.schema.json`. It uses jsonschema 4.19.2 with Draft202012Validator. The script is outside the repository. Final run, verbatim, `verify_exit=0`:

```text
schema_errors: 0
phase1_plan_rows: 32 proof_cases: 54 requirements_covered: 32 commands: 46
missing_from_proof_cases: []
unknown_requirement_ids: []
deferred_ids_in_cases_or_matrix: []
case_command_ids_unknown: []
slice_graph_command_ids: 20 missing: []
actor_fields: []
unknown_design_ids: []
matrix_rows: 54 bad_columns: 0
cases_missing_reverify_line: []
tdd_cases_missing_slice_fields: []
dup_case_ids: 0
slices_without_rows: []
seq_rows_unknown: []
seq_cmds_unknown: []
required_cmds_unknown: []
```

Correction rounds (2 of 3 allowed):

1. **Unknown id.** The slice graph changed concurrently and named `CMD-HOOK-INSTALL-SANDBOX`. Hypothesis: the IE-P1 findings had been applied. Fix: reconcile against the IE plan, as described above.
2. **Command syntax.** `bash -n` and `shellcheck -s bash -S error` were run over every CMD command string, with `<placeholders>` substituted. The placeholder `<vendored_source_commit_from_VENDORED.md>` was not a valid token. Fix: rename it to `<vendored_source_commit>` and define it in the pass rule. Rerun: `bash_syntax_ok`, `shellcheck_errors_none`.

Other checks:

- **Rule 12 scan of `seit.json`:** `grep -cE '(/home/|/Users/)[A-Za-z0-9._-]+/'` returned `0`.
- **Slice → proof rows** (`slice_proof_map`):
  - S01, S02, S03: 5 each.
  - S06: 10.
  - S06L, S07, S08: 2 each.
  - S09: 13.
  - S09T: 5.
  - S11: 9.
  - S11T: 1.
  - S41: 3.
  - S42: 4.

Read-only commands:

- `git rev-parse f885e48`;
- `git show f885e48:<plan>/seit.json`;
- `sha256sum` of the bound inputs;
- `git status --short`;
- `command -v` tool probes: kcov, mutmut and diff-cover are absent; ocr v1.12.13, uv 0.11.6, dot, gh, jq, claude and shellcheck are present;
- reads of the journey profile snapshots: `primary` assurance enabled, `tech-writing` assurance disabled, `coverage_assist` enabled and required, `reverify` enabled.

## Findings (planning_findings_for_plan_integrator)

| ID | Class | Needed | Owner decision |
|---|---|---|---|
| TE-P1-F01 | integration reconciliation | Copy the IE-P1 post-step commands into `implementation.json` with the finalized ids. IE CMD-P2-ENTRY-RECEIPT becomes PROC-PHASE2-ENTRY. IE-P1-11's row-field check is CMD-DX-COVERAGE, not CMD-DX-PRESENCE. | no |
| TE-P1-F02 | command ids added to slices | Add the listed commands to S01..S03, S02, S07, S06L, S42, S09, S11, S41 and S08, plus the step-level and Lifecycle-level commands. No slice-graph id was renamed. | no |
| TE-P1-F03 | command corrected | f885e48 CMD-SCAN called Alphazedehq `hooks/scan-supply-chain.sh`, which is an advisory routing hook that always exits 0, not a scanner. It now runs the scan-software-supply-chain skill procedure and checks the verdict line. | no |
| TE-P1-F04 | test-design convention | The S11T test runs the installer through `$AFC_HOOK_PY` (default `python3`). The S09T tests call `check_paths`/`check_docs` `main(argv)` in-process, so coverage.py can measure them. | no |
| TE-P1-F05 | resolved | The template vendoring and entry-receipt path gaps were closed by IE-P1-F03 and IE-P1-F08. | no |
| TE-P1-F06 | private-repo landing | Run CMD-PR-CHECKS before every this-repo merge. CMD-LANDING-CHECK uses ancestor checks while the rulesets API returns 403. | no |
| TE-P1-F07 | proof completes outside Phase 1 | The DoD Manifest shows SEIT-AFC-RISK-17 as OPEN_CARRIED until P2-6. | no |
| TE-P1-F08 | declared typed gaps | Shell coverage and shell mutation are TOOL_MISSING. Spec-and-docs has no coverage or mutation claims under OA-AFC-A2 option A. Option B means regenerating this SEIT. | no |
| TE-P1-F09 | slice proof coverage | Every slice has proof rows. Copy `slice_proof_map` into `implementation.json`. | no |
| TE-P1-F10 | open owner item | OA-AFC-A3 sets the review boundary per integration step, or amends the cadence to `slice`. The proof rows are the same either way. | yes (OA-AFC-A3, already open for integrated review) |

## Remaining risks

- **Unverified tool flags.** The mutmut 2.x and diff-cover flags are declared but were not executed: installing them was out of scope, and they need CMD-SCAN first. A flag or runtime failure at first use is TOOL_MISSING or NOT_RUN, never PASS.
- **No Assurance pass on the shared tooling.** The executable shared tooling in the spec-and-docs lane (gate template, installer script, workflow checker, D5 scripts) gets its own tests and the Reviewer only (OA-AFC-A2 A).
- **Skill selection is evaluated, not proven.** CMD-SKILL-TRIGGER evaluates LLM skill selection; it does not prove it deterministically.
- **Concurrent edits.** The bound inputs were edited during this session. Any later edit to the technical plan, `design.md` or `views.json` invalidates these digests and needs a Planning Test Engineer delta.

## developer_feedback

- **TE-P1-OBS-001**, classified as a configuration, environment or harness issue in the Lifecycle orchestration. The Planning Test Engineer was dispatched while the Integration Engineer Phase 1 run was still producing its plan. The Orchestrator then edited three bound inputs mid-session (all three were modified at 19:45, and the IE log finished at 19:44).
  - Evidence: `ls -la --time-style=+%H:%M` on `integration-plan.md`, `slice-graph.md`, `design.md` and the technical plan, and the first cross-check line `missing: ['CMD-HOOK-INSTALL-SANDBOX']`.
  - Impact: one reconciliation round, about a third of the session.
  - Workaround: the cross-check script caught it.
  - Suggestion: dispatch the Test Engineer after the IE findings are applied, or freeze the bound inputs for the duration of the run.
- **TE-P1-OBS-002**, classified as a documentation gap in the prior artifact. The f885e48 SEIT defined CMD-SCAN as `bash hooks/scan-supply-chain.sh <artifact>`, but that file is an advisory PreToolUse hook. The command was never exercised against the tool it names.
  - Evidence: the head of `hooks/scan-supply-chain.sh` ("Advisory PreToolUse hook … always fails open").
  - Suggestion: the planning review should spot-check one invocation per new command id.
- **Positive.** The `seit.schema.json` validation, combined with a scripted id cross-check (plan rows, slice-graph ids, design ids and sequence rows), gave a fast, exact loop.
- **Tools exercised:** python3 jsonschema 4.19.2, git, sha256sum, grep/sed/diff, bash -n, shellcheck, and `command -v` probes.

Skipped: no command was executed against Alphazedehq or GitHub, because this was planning only. The mutmut and diff-cover CLIs were not fetched.
