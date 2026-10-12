# Planning and Design CHANGE receipt: DEC-AFC-SD-025 (Devpost developer-feedback fields)

- **Role:** Planning and Design node (`BEARING_ROLE=planning_and_design`), owner CHANGE at integrated review P1. This is not a correction round.
- **Input:** `specialists/pd-change-sd025-prompt.md`; DEC-AFC-SD-025 (`journey.json`); `evidence/devpost-feedback-rules.md` (sha256 `e35bbfb8…12c6`, curl HTTP 200 on 2026-10-12)
- **Revision against:** `49029171ea62a5ef57c31b066c20a7b059ebc26b` (candidate digest `23a97b49…1a37`, CHANGE_REQUESTED)
- **Return:** `PLAN_REVIEW_READY`
- **New candidate (manifest) digest:** `283b7a069266ad818d1ac5e860fb5ed7083a55e64a0ad3ffa8aeb6284ef6a746`
- **Rendered DoD Manifest:** sha256 `f39e4e0fd1151f2491052504ded4c01f2225a1fed47ebd7e15916c847556b3a1`, template 1.0.1

## Revision diff vs 4902917

| Area | Change |
|---|---|
| Requirements (32 → 33) | **AC-AFC-DX-02 amended:** the log holds the AC-AFC-DX-04 tables, and every row is complete: each cell is a value, `n/a` or `unknown`. DEC-AFC-SD-025 is added to the source. **AC-AFC-DX-04 new:** the log schema. The Observations header carries three column groups: the issue #1 Scribe columns; the Devpost Product Feedback columns (used for, what worked well, what needs work, onboarding zero to hello world, would build again Yes/No and why, AWS services used and how); and the Friction Log Entry columns (task attempted, steps taken, expected result, actual result, severity rating, workaround used, actionable suggestion). The Feature requests header carries ID, Tool, Description, Why it matters to this project and Priority, and Priority is Critical, Important or Nice-to-have. AC-AFC-DX-01 is unchanged. |
| Deferred row | It is now "AC-AFC-DX-02 (submission assembly), DX-03". It lists the Phase 2 deliverables: per-tool Product Feedback including AWS Builder services, optional Feature Requests, and sanitized Friction Log entries. It records the up-to-10% Stage 1 bonus, and DX-03 checks the deliverables against the rules current at submission. |
| Technical plan prose | The Outcome bullet now says the log carries every Devpost field from its first row. The frontmatter revision note is updated. |
| Design | DES-AFC-DX gains the log schema: headings `## Observations` and `## Feature requests`, a column table, the `n/a`/`unknown` rule, and expected/actual as two columns that Phase 2 joins. The severity scale is Blocker, Major, Minor or None. The rules name no scale, so this is a design choice the owner can change at review. AWS services are filled only for AWS tools. Submission assembly stays in Phase 2. |
| SEIT (54 → 55 proof cases, 46 → 47 commands) | **New:** SEIT-AFC-DX-04 and CMD-DX-SCHEMA, an inline python3 stdlib check of both table headers and the Priority values. **Amended:** SEIT-AFC-DX-02 and CMD-DX-COVERAGE. A complete-row check (cell count matches, no empty cell) replaces the old header grep. DX-02 now has the precondition that SEIT-AFC-DX-04 passes. Also updated: the S08 scribe gate, the IE-P1-11 pre_merge and rows, the slice_proof_map, the counts, and DEC-AFC-SD-025 in decision_baseline. Existing IDs are stable. |
| Slices | S08: +AC-AFC-DX-04, +SEIT-AFC-DX-04, +CMD-DX-SCHEMA; the goal and stop condition now name the schema. All 13 slices' `developer_feedback.rule` now asks for the AC-AFC-DX-04 fields that apply, so entries are captured as they happen. No slice, wave, write set, route, dependency or authority changed. |
| implementation.json other | Traceability gains AC-AFC-DX-04. Also updated: the `dod_manifest.requirements` mirror (DX-02 updated, DX-04 added), the models trace, the Wave 2 exit, IE-P1-11 post-step V&V and exit, `deferred_to_phase_2`, and the authority evidence string. `revision_against` and `revision_diff` now describe this change; the f885e48 pair is kept in `revision_history`. `planning_review.candidate_revision` = 4902917 and `candidate_digest` is rebound. The BLUF counts are 33/55/47. |
| DX-006 correction | `scope-decision-batch.md` DX-006 now ends with a dated resolution note: curl got HTTP 200, so the 403 came from WebFetch alone, and the sections are verbatim in `evidence/`. No other planning text claimed the rules were unverified (grep over the TP, design, JSON and workspace files). |
| `specialists/slice-graph.md` | The S08 row is synced: +AC-AFC-DX-04 and the stop condition. |

## Requirements Engineer gate (changed rows only, one round)

- **Route:** journey frozen primary `requirements_engineer` planning route, Muse Code / Muse Spark 1.3 / max (primary, available). Launched with `muse exec … --yolo --prompt-file specialists/re-sd025-prompt.md < /dev/null`; exit 0.
- **Verdict: PASS.** DX-02 and DX-04 pass with no defect, and the Deferred-row check passes. Receipt: `specialists/requirements-engineer-receipt-sd025.md`. Log: `specialists/re-sd025-run.log`, with home paths rewritten to `$HOME`.
- **Hash read by the RE:** `be35c1c8…daad4`. After the PASS, the technical plan changed only in its frontmatter `revision_note`; the final hash is `0051816b…bc82c`. The register rows are byte-identical: `ac-mechanical-lint-sd025.txt` differs from `ac-mechanical-lint-p1.txt` only by `+AC-AFC-DX-04 OK` and `rows=33 flagged=6`.
- **RE observation:** S08 in implementation.json and slice-graph.md listed only DX-01 and DX-02. The RE read them before the sync. Both are now synced.

## Commands and results

```text
node <bearing-lite 1.1.6>/hooks/plan-package.cjs <plan dir>                      exit 0
{ "outcome": "PASS", "manifest_digest": "283b7a069266ad818d1ac5e860fb5ed7083a55e64a0ad3ffa8aeb6284ef6a746", "findings": [] }
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json        exit 0  RENDER_WRITE sha256:f39e4e0f…b3a1
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json --check exit 0  RENDER_CHECK_PASS sha256:f39e4e0f…b3a1
python3 jsonschema Draft202012Validator (<bearing-lite 1.1.6>/schemas)           implementation 0 | seit 0 | authority 0 | journey 0
orphan-proof 3-way check (slice requirement_ids / seit_proof_rows / traceability)  0 mismatches; 33 requirements, 55 proofs
evaluatePlanningReview({planning_review, plan_dir, dod_manifest, round 1, 0 completed})  NEEDS_MORE_EVIDENCE / review_round_pending (manifest present)
rule 12 home-path shape scan over TP, design, *.json, manifest, views/, evidence/, new specialists files  0 hits
python3 -B specialists/ac_mechanical_lint.py <lint-sdoc.py> <TP>                 exit 0, rows=33 flagged=6 (same 6 pre-existing flags)
CMD-DX-SCHEMA / CMD-DX-COVERAGE self-test on fixture logs (outside repo)         good: no output; bad: MISSING column, BAD priority, BAD row, EMPTY cell, MISSING DX-007, MISSING table
```

## Digests

| Artifact | Old (4902917) | New |
|---|---|---|
| technical plan | `dfc1b9b2…12cd6` | `0051816b697836e111a21ec7bf01a13ad9559eb239ad3aa8192deb2c185bc82c` |
| design.md | `f33b50c5…1308b` | `4b397fb81756115e07fdd630c78e57dafd6e2f0a9ec97af568ddec43275e57ca` |
| seit.json | `4c64a103…4c7e7` | `9475fa1518a49054913212bc7e8a935de28a38137121e563bcde8fe11bf9bac0` |
| candidate | `23a97b49…1a37` | `283b7a069266ad818d1ac5e860fb5ed7083a55e64a0ad3ffa8aeb6284ef6a746` |

`views/` is unchanged. The old candidate digest survives only in `revision_against`, where it is intentional.

## Write set

Changed: TP, `design.md`, `seit.json`, `implementation.json`, manifest HTML, `scope-decision-batch.md` (DX-006 note) and `specialists/slice-graph.md`. New: `specialists/re-sd025-{prompt.md,applied.diff,start.txt,run.log}`, `specialists/ac-mechanical-lint-sd025.txt`, the RE receipt and this receipt. `journey.json`, `authority.json` and `views/` were not edited by this node; the journey diff is the Orchestrator's. No commits, pushes or branch operations. The pre-edit backup is outside the repository.

## developer_feedback

- **PD-SD025-OBS-1: digests chase each other after any late TP edit.** A frontmatter-only edit after the RE PASS forced a second rebind across `seit.json`, `implementation.json` and the candidate digest. Suggestion: give the plan package a `rebind` helper that recomputes `planning_inputs`, `seit_json_sha256_at_integration`, the identity rows and `candidate_digest` in one step.
- **PD-SD025-OBS-2: `seit.json` slice_proof_map S08 omits SEIT-AFC-DX-01, which implementation.json S08 carries.** This predates this change, and `plan-package.cjs` does not compare the two maps. I left it as is because it is out of scope.
- **PD-SD025-OBS-3: Muse headless output prints absolute workspace paths.** The run log and final message contain them, so they need a rule-12 rewrite before they are kept.
- **Tools exercised:** python3 (json, jsonschema, re, hashlib), node (plan-package, render-dod-manifest, planning-review), Muse Code 1.4.6 `muse exec`, git diff/show, sed, grep, sha256sum, diff.

## DELTA: PD-SD025-OBS-2 disposition (Planning and Design, DELTA mode)

- **Finding:** `seit.json` `system_description_and_requirements_flowdown.slice_proof_map.S08` omitted SEIT-AFC-DX-01, which `implementation.json` S08 `seit_proof_rows` carries.
- **Fix:** SEIT-AFC-DX-01 was added to `slice_proof_map.S08`, in the same position as in `implementation.json`: CI-02.P, DX-02, DX-01, DX-04. `slice_proof_map` is the only place in `seit.json` that lists proof rows per slice. The `method_fields.slice` text on the proof cases is free text and not a slice mapping. SEIT-AFC-DX-01 says "all Phase 1 slices" there, which already includes S08, so that text is unchanged.
- **Mechanical sweep:** all 13 slices' `seit_proof_rows` were compared with `slice_proof_map`, matching on exact list and order, and the slice key sets were compared too. Before the fix: 1 mismatch (S08). After: 0. The key sets are equal. No other mismatch was found, so no other edit was made.
- **Rebind:** `seit.json` `9475fa15…bac0` → `17710bbbc095509728eb12c3560cc200b8addba4f1e7787870a68bd0e34ab158`. This updated `source_baseline.seit_json_sha256_at_integration` and the manifest identity row. The candidate digest `283b7a06…6a746` → `4128aa9cdacd1fca06edfb68652258730db107eb6213f6dca3faf9e9cca55e84`, updated in `planning_review.candidate_digest` and the identity row. The TP, `design.md` and `views/` are unchanged, so their input digests stand. The old digests survive only in the history sections of this receipt above.
- **Rendered DoD Manifest:** sha256 `39abc3b316d4161712fc3ba583c133c7efc71d7a684e1045b3b33937a9605b3e`, template 1.0.1.
- **Write set:** `seit.json`, `implementation.json` (digest strings only), the manifest HTML and this receipt. No commits.

```text
node <bearing-lite 1.1.6>/hooks/plan-package.cjs <plan dir>                       exit 0  PASS, findings [], manifest_digest 4128aa9c…e55e84
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json         exit 0  RENDER_WRITE sha256:39abc3b3…605b3e
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json --check exit 0  RENDER_CHECK_PASS sha256:39abc3b3…605b3e
python3 jsonschema Draft202012Validator (<bearing-lite 1.1.6>/schemas)            implementation 0 | seit 0 | authority 0 | journey 0
slice_proof_map vs implementation seit_proof_rows (exact list, 13 slices)          0 mismatches (was 1: S08)
slice seit_proof_rows -> seit proof_cases orphan check                            0 orphans; 55 proofs, 33 requirements
rule 12 home-path shape scan over TP, design, *.json, manifest, views/, evidence/, this receipt   0 hits
```

- **developer_feedback:** OBS-2 is closed by this delta. The prevention gap is still there: `plan-package.cjs` does not compare `slice_proof_map` with `seit_proof_rows`. Tools exercised: python3 (json, jsonschema), node (plan-package, render-dod-manifest), sed, grep, sha256sum.
