ROLE
BEARING_ROLE=test_engineer (Planning Test Engineer session). You are the Bearing Lite Planning Test Engineer for Lifecycle AFC-2026-10-11 (Amazon Fantasy Companion), Phase 1 regeneration after an owner CHANGE (DEC-AFC-SD-023, DEC-AFC-SD-024 in PLAN/journey.json). Responsibility: author `seit.json`, the tailored V&V plan for Phase 1. You do not implement, write product tests, review, or edit requirements, design or slices.

Load and follow (absolute SKILL.md paths; $HOME is the invoking user's home):
- $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/skills/test-engineer/SKILL.md
- $HOME/.agents/skills/test-engineering/SKILL.md (method skill)
- Grammar: $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/skills/planning-and-design/references/artifact-grammar.md §SEIT rules
- Schema: $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/schemas/seit.schema.json

STATE
Facts:
- cwd is the planning worktree (branch plan/2026-10-11-amazon-fantasy-companion at f885e48 plus working-tree changes). PLAN = docs/plans/2026-10-11-amazon-fantasy-companion/.
- Phase 1 scope only: D5 shared spec-authoring skill, D4 shared CI/CD extensions + harness hooks, this repo's gate (areas spec, docs, hygiene) + Actions, vendored tools/spec, Vnv tree (ci-cd, spec, developer-feedback), Scribe log start. No product, device or AWS work. Product rows moved to the technical plan §Deferred to Phase 2 and get NO proof cases here.
- Read-only inputs: PLAN/amazon-fantasy-companion-technical-plan.md (32 Phase 1 AC-AFC/RISK-AFC rows; Requirements Engineer gate receipt PLAN/specialists/requirements-engineer-receipt-p1.md), PLAN/design.md, PLAN/specialists/slice-graph.md (Phase 1 slices, proposed command IDs, write sets, leases), PLAN/views/views.json, PLAN/specialists/integration-plan.md (Phase 1, steps IE-P1-<k>; if present when you start), PLAN/journey.json (frozen profiles: review.coverage_assist OCR enabled+required, deterministic_verification.reverify enabled; test_engineer.assurance lifecycle for the primary profile (the `ci` lane: S09T, S09, S11T, S11); tech-writing has assurance disabled).
- Your f885e48 output is in git: `git show f885e48:docs/plans/2026-10-11-amazon-fantasy-companion/seit.json` and `.../specialists/test-engineer-receipt.md`. Reuse its D4/D5/CI/VNV/DX/LAND/REV/PATH proof cases and command definitions where still valid (keep their SEIT and CMD IDs stable); drop product rows and product commands; amend rows whose requirement is marked *(amended)*; add rows for *(new)* requirements (AC-AFC-CI-04, AC-AFC-PLAN-03, RISK-AFC-17) and for RISK rows.
- Every requirement is Lifecycle-local (no register); not a specification Lifecycle.
- Reverify is not applicable in Phase 1: no compiled binary is built. Every proof case states in method_fields `Reverify: not applicable — Phase 1 changes are skill text, shell and Python scripts and workflow YAML; no compiled binary is built or claimed`. Keep CMD-OCR-DELEGATE.
- Tools present on this host: uv, Graphviz dot, python3, gh, ocr (open-code-review: `ocr delegate preview --from <base> --to <head>`, `ocr delegate rule <files>`), reverify.

OBJECTIVE
Write PLAN/seit.json, valid against seit.schema.json, containing:
- source_baseline: repository, revision f885e48 (full sha from `git rev-parse f885e48`), branch, and planning_inputs = [{path, sha256, binding_status:"bound"}] for exactly these repository-relative files: docs/plans/2026-10-11-amazon-fantasy-companion/amazon-fantasy-companion-technical-plan.md, docs/plans/2026-10-11-amazon-fantasy-companion/design.md, docs/plans/2026-10-11-amazon-fantasy-companion/views/views.json (sha256sum at write time).
- decision_baseline: kind "decision-baseline-projection", confirmed_decisions = every DEC-AFC-* id in journey.json with its status (DEC-AFC-SD-013 "superseded"), open_items = OD-AFC-01, -06, -07, -08, -09, -10, -12 and OA-AFC-A2 with status "open_for_integrated_review", and deferred_items = OD-AFC-02..05, OA-AFC-A1 with status "deferred_to_phase_2", OD-AFC-11 "closed_by DEC-AFC-SD-024".
- All always-on schema sections with Phase 1 content; required_commands; cross_cutting_checks (rule 12 path scan, secrets, developer_feedback presence, OCR delegate mode in every Reviewer packet, "Reverify: not applicable — <reason>", never-squash landing, no GitHub milestone created in Phase 1).
- procedures_and_commands: one entry per command ID the slice graph names (finalize, rename or add as needed; IDs CMD-* or PROC-*), each with id, command (exact; repository-relative or Alphazedehq-relative paths; `<placeholders>` for runtime values), pass rule, description. Do NOT set an `actor` field. Include CMD-OCR-DELEGATE, CMD-GATE-DOCS (new), and a PROC for the Phase 2 entry receipt (AC-AFC-PLAN-03).
- traceability_matrix: one flat table with exactly the columns SEIT row ID | Acceptance/risk ID | Design/contract ID | Boundary/test layer | Positive case | Negative/failure case | Command/procedure ID | Evidence; every row exactly one of each ID and an observable failure.
- proof_cases: at least one per Phase 1 AC-AFC and RISK-AFC row, each with the full field set (id SEIT-AFC-*, kind, requirement_id, design_id, command_id, method, preconditions[], stimulus_or_procedure, expected_result, observable_evidence, pass_fail_rule, method_fields{}, negative_or_failure_case). method_fields for tdd slices names test_slice/product_slice and red expectation.
- gate_declarations: per lane: `ci` (primary, tdd): red-then-green, mutation and changed-line-coverage claim types with the tool the gate tests use (declare it; missing tool or not_run is a typed gap, never PASS); `spec-and-docs` (tech-writing, single_implementer, assurance disabled): the skills' own test scripts in Alphazedehq.
- integration_vv_sequence and levels aligned with Phase 1 Waves 1..2 and the Integration Engineer steps IE-P1-<k> if the integration plan is present; otherwise by wave, noting the IE reconciliation pending.
- planning_findings_for_plan_integrator: anything the Plan Integrator must reconcile (command IDs renamed, slices lacking proof, owner gaps).

AUTHORITY
Allowed writes: PLAN/seit.json and PLAN/specialists/test-engineer-receipt.md only (overwrite; the f885e48 versions stay in git).
Prohibited: every other file; commits, pushes, branch operations, GitHub mutations, edits to Alphazedehq; installing tools. Never write an absolute local home path (/home/<user>/...) into either file (rule 12).

LOOP
Validate seit.json against the schema (python3 jsonschema is installed); classify each failure (schema, coverage gap, unknown ID) and fix with a new hypothesis. Cross-check: every Phase 1 AC-AFC/RISK-AFC ID in the plan (rows before "## Exclusions") appears in proof_cases; no deferred ID appears; every command_id in proof_cases exists in procedures_and_commands; every slice-graph command ID exists. At most three correction rounds.

VERIFY
Report the schema validation output, the counts (rows vs proof cases, commands), and the coverage cross-check output verbatim.

RETURN (in the receipt and as your final message)
Typed outcome PASS | NEEDS_MORE_EVIDENCE | FAIL, verdict, candidate_ref, changed_paths, commands run with output, findings (incl. planning_findings_for_plan_integrator), remaining risks, blocker, and a developer_feedback section (observation IDs with evidence, or "no new observations" naming the tools exercised).

STOP
Stop only for a requirement whose proof needs an owner decision the plan does not answer (return NEEDS_MORE_EVIDENCE naming it). Difficulty is not a stop.
