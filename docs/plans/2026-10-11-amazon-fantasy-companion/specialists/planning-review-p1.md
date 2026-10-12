# Planning review P1 — AFC-2026-10-11 (slot `planning-review`)

- candidate_ref: `plan/2026-10-11-amazon-fantasy-companion`
- candidate_revision: `82e767d` (HEAD verified: `82e767d57c5ff5d5b8f070349a77cedf7ef60793`; base `f885e48`)
- candidate_digest: `f213dcebb4e5acffa97ded459fbd69eea7298b4dc111d9e4bec3e9a642ee1d98`
  (verified: `plan-package.cjs` → `PASS`, `manifest_digest` identical, `findings: []`)
- reviewer: independent; authored none of the package.

## Verdict: REPAIR_REQUIRED

3 verified findings (2 P2, 1 P3), each fixable in a Planning-node repair
round. No finding questions the SD-023 phasing, the lane layout, the
dependency graph (acyclic, 21/21 edges consistent), route bindings (13/13
slices match the frozen snapshots including fallback order), the schedule
(all Phase 1 targets ≤ 2026-10-13T23:00:00Z, 10 days before T_deadline), or
the Deferred coverage (14/14 rows account for the f885e48 product scope).

## Findings

| ID | Sev | File:line | Defect | Exact fix |
|---|---|---|---|---|
| FP1-01 | P2 | `implementation.json:813,967,1081,1207,1757,2046,2053,3287,3442,3516,3543`, `amazon-fantasy-companion-technical-plan.md:129,180` | Six slices carry SEIT proof rows for requirements missing from their `requirement_ids`, and S08 declares DX-01 with no DX-01 proof row: S06 proves `SEIT-AFC-RISK-16` without declaring RISK-AFC-16; S07/S06L/S42 prove `SEIT-AFC-PATH-01.P` without declaring PATH-01; S42 also proves RISK-16 without declaring it; S11 proves `SEIT-AFC-RISK-13.G` without declaring RISK-13; S08 proves `SEIT-AFC-CI-02.P` without declaring CI-02 and declares DX-01 without its proof. The proof stimuli name exactly these slices (e.g. PATH-01.P: "planning commit, S06L, S42, S07"), so the proofs are correctly placed and the declarations are missing. Traceability disagrees a third way (PATH-01 lists only S09T/S09; RISK-13 only S06/S09; CI-02 only S09T/S09; RISK-16 only S06), and TP Allocation cells omit S08 (CI-02) and S11 (RISK-13). The f885e48 package had 0 orphan proofs (e.g. base S06L declared PATH-01 for its `.P` proof), so this is a regeneration regression. | In `requirement_ids`: S06 add `"RISK-AFC-16"`; S07 add `"AC-AFC-PATH-01"`; S06L add `"AC-AFC-PATH-01"`; S42 add `"AC-AFC-PATH-01"`, `"RISK-AFC-16"`; S11 add `"RISK-AFC-13"`; S08 add `"AC-AFC-CI-02"`. In S08 `seit_proof_rows` add `"SEIT-AFC-DX-01"`. In traceability `slices`: CI-02 add `"S08"`; PATH-01 add `"S07"`, `"S06L"`, `"S42"`; RISK-13 add `"S11"`; RISK-16 add `"S42"`. In TP Allocation: CI-02 → "S09T, S09, S08; repo gate workflow"; RISK-13 → "S06, S09, S11; acquisition receipts". Rebind the TP sha256 in `seit.json` planning_inputs, `implementation.json` dod_manifest and the manifest; recompute `candidate_digest`. No `design_ids` change (base S06L pattern: slices cite their primary design only). |
| FP1-02 | P2 | `implementation.json:2919` (OWN-P1-01), `implementation.json:3630` (approval_boundaries) | Both Orchestrator-consumed approval gates list 8 open items `(OD-AFC-01, -06, -07, -08, -09, -10, -12, OA-AFC-A2)` and omit OA-AFC-A3, while the TP owner table (`:420-432`), the manifest OD rows (`:2079-2129`), `seit.json` open_items and Wave 1 entry (`implementation.json:226`) all carry the full 9. OA-AFC-A3 is the decision that unblocks every merge (IE-P1-F01: per-step review boundaries); gating Wave 1 entry on the 8-item text lets dispatch proceed with the review boundary undecided. | Append `, OA-AFC-A3` inside the closing parenthesis in both strings, matching `:226`. |
| FP1-03 | P3 | `implementation.json` `journey_settings.planning_review.candidate_revision` | Names `f885e48…` (the base) instead of the candidate commit, and `repair_revision` is a prose placeholder. The packet + `candidate_digest` bind the candidate unambiguously and the manifest §2 avoids the field (Baseline + Revision-against + ref + digest), so this is a mild FR-02 recurrence. | At repair-commit time, set `candidate_revision` to the repair commit hash; keep `candidate_ref`, rebind `candidate_digest`. |

## What was verified clean (no finding)

- Routes: all 13 slices' `model_route` primary + `ordered_fallbacks` (order
  included) and `review_path.reviewer_route` match
  `journey.json profile_selection.frozen_snapshots` for their lane profile;
  `planning_review.reviewer_slots` matches the frozen primary reviewer route
  and fallback order; lane→profile bindings match DEC-AFC-PROFILE-001
  (spec-and-docs=tech-writing, ci=primary, scribe-side-lane=primary/scribe).
- Graph: no cycles; no dep on a later wave; `dependencies` == slice edges
  (21/21); S41 conditional gates present (`depends_on_text`, `human_decision`,
  OD-AFC-01); S11/S08 conditional wording covers the OD-AFC-01≠B case.
- Parallelism: no unordered write-set overlap in either wave; leases
  (`alphazedehq-skills/<skill>`, `harness-configs`,
  `alphazedehq-main-checkout` reader-writer) match TP §Program plan.
- Traceability: 32/32 rows have ≥1 of the 54 SEIT proof cases; all proof,
  trace-matrix, slice and integration-sequence `command_id`s resolve to the
  46 procedures; all slice `design_ids` resolve to design.md; `design_lenses`
  all valid; the 7 slice-unbound rows each have `lifecycle_level_bindings`
  (planning, PRs, IE-P1-12, Reviewer packets, route receipts).
- SD-023/SD-024: Phase 1 = D5 + D4 (+hooks, repo gate) + spec track
  ST-1..ST-5; Phase 2 = P2-6 implementation planning + P2-7 milestones after
  spec approval; no milestones in Phase 1; `evidence/visual/` carried for
  Phase 2; Deferred tables (TP + `deferred_to_phase_2`) both list the same
  14 rows covering issue #1 items 1,2,3,4,6, panel, spikes, submission,
  risks and the f885e48 graph; messaging still excluded; SD-013 consistently
  superseded (incl. the PROC-PHASE2-ENTRY kit-copy check).
- Owner boundary: no slice or SEIT command performs a C9/owner-only action;
  S11 live install and S06L links are inside the authority's dev-host grant
  (timestamped backup); S06/S41/S42 carry their OD gates; all write sets are
  inside `authority.json` allowed paths; authority `proposed`/`effective:
  false` pre-approval is correct.
- Rule 12: no literal local absolute path in any review-scope file
  (`$HOME`/`<user>` placeholders and detector regexes only; `git grep`
  for `$HOME` over the plan dir is empty).
- Cross-checks: manifest TP/design/seit/views hashes match current files;
  all 6 `views.json` `svg_sha256` match their SVGs (V1..V3 marked
  2-reference); IE-P1-F01..F10 applied verbatim; S41 is Product
  Implementer / judgement everywhere ("judgement slice" in TP, OD text,
  manifest); R1 FR-04..FR-08 classes re-checked clean (no stale OD ranges,
  no "light slice" wording); RISK-17 live windows match the calendar
  (10-15 Thu, 10-18 Sun, 10-19 Mon, 10-22 Thu); `evidence/
  phase2-entry-receipt.json` shorthand defined in TP/seit/impl notes.
- Schedule: cutoffs 10-12T18:00Z → Phase 1 exit 10-13T23:00:00Z all precede
  T_yahoo and T_deadline; Wave 1 packs 5 reviewed PRs into ~30 h
  post-approval — tight but parallelizable within impl_agent_cap 5, not
  provably infeasible, so pressure noted, not a finding (same bar as R1).

## OCR coverage_assist (delegate mode, REQUIRED)

- `ocr delegate preview --from f885e48 --to 82e767d`: OK, 7 reviewable
  files (rest excluded `unsupported_ext`; the excluded `.md` review-scope
  files were read directly per packet scope — a docs-product package).
- `ocr delegate rule <file>` for all 7: OK, no tool failures. Rule groups
  applied per file:

| File | Rule group | Result |
|---|---|---|
| `amazon-fantasy-companion-dod-manifest.html` | system/default (correctness, security, performance, maintainability, tests) | PASS. No `<script>`/event-handler/`javascript:`/iframe/object/form content (`content=` meta hits are regex false positives); 3 embedded static SVGs + `<style>` only. No XSS surface; static generated artifact. Content fidelity spot-checked (S41 role, OD-A3 row, §identity hashes, requirement rows). |
| `authority.json` | json-keys spelling | PASS, no key typos (aspell over key words; only domain terms flagged). |
| `implementation.json` | json-keys spelling | PASS, no key typos (624 unique keys across the 5 JSON files checked). |
| `journey.json` | json-keys spelling | PASS, no key typos. |
| `seit.json` | json-keys spelling | PASS, no key typos. |
| `views/views.json` | json-keys spelling | PASS, no key typos. |
| `specialists/ac_mechanical_lint.py` | python rules | PASS, no blocking issue. The +3/-1 diff (RISK rows, `*(amended/new)*` markers, stop at `## Exclusions`) is correct; output `ac-mechanical-lint-p1.txt` covers all 32 TP rows with only advisory "agnostic term" notes (github/requirements-system/agy are required namings, not defects). R1's non-blocking argv-guard note carries (reproduced on misinvocation). |

No OCR-identified defect rises to a review finding.

## Reverify

Reverify: not applicable — the candidate contains no compiled binary.

## Route actually used

Primary `planning-review` route: Muse Code / Muse Spark / max (this session;
no fallback activated; no 429 encountered).

## developer_feedback

- Observations: (1) The regeneration is faithful: IE/TE/PI correction rounds
  landed with receipts before this review, and every R1 finding class was
  re-checked — only FR-02 recurs, mildly. (2) The FP1-01 pattern (slice
  proves a row it does not declare) would be caught mechanically by the same
  orphan-proof check used here; consider adding it to the Plan Integrator
  freeze checks. (3) No new schedule risk beyond R1's note: the 10-13T23:00Z
  Phase 1 target leaves 10 days for spec track + Phase 2, guarded by
  RISK-AFC-17's no-silent-cuts rule.
- Tools exercised: `node plan-package.cjs` (PASS), `ocr delegate preview`
  + `ocr delegate rule` ×7, `sha256sum` (via python hashlib), `aspell`,
  project JSON parsed with `python3` (purpose-built check scripts in
  `/tmp/afc-p1-check*.py`, not committed), `git show`/`git rev-parse`/
  `git status`/`git diff`/`git grep`, `grep`, `diff`.
