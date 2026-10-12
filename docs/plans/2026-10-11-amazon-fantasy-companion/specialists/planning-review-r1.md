# Planning review R1 — AFC-2026-10-11 (slot `planning-review`)

- candidate_ref: `plan/2026-10-11-amazon-fantasy-companion`
- candidate_revision: `4afc998` (HEAD verified: `4afc998ed2fd4a19a28fdfb9d7f815452a60cce5`; base `2c13a6b`)
- candidate_digest: `87fa24334fda312e61582c169cfe9b3c205f989ff30cd6edc7017bf4a9ee78f3`
  (verified: `plan-package.cjs` → `PASS`, `manifest_digest` identical, `findings: []`)
- reviewer: independent; authored none of the package.

## Verdict: REPAIR_REQUIRED

8 verified findings (1 P1, 3 P2, 4 P3), each fixable in a Planning-node repair
round. No finding questions the architecture, lane layout, dependency graph
(acyclic, 71/71 edges consistent), route bindings (54/54 slices match the frozen
snapshots including fallback order), or milestone dates (all ≤ M5 due
2026-10-23T12:00:00Z, 7 h before T_deadline).

## Findings

| ID | Sev | File:line | Defect | Exact fix |
|---|---|---|---|---|
| FR-01 | P1 | `amazon-fantasy-companion-technical-plan.md:408-421` | "Open owner decisions" table lists OD-AFC-01..10 only, but the package carries 12 open items: OA-AFC-A1 (`implementation.json:10844`) and OA-AFC-A2 (`implementation.json:10861`, also rendered in the manifest `:3496-3502`) are `open_for_integrated_review` and missing here. TP entry criterion 1 (`:362-363`) scopes approval to "the decisions listed under Open owner decisions", so the owner could approve without deciding them — yet OA-AFC-A2=B invalidates the slice graph and OA-AFC-A1 pins a host cache path into 8 tv-app-ui slice `skills` lists. | Append two rows to the table, decision + recommendation quoted verbatim from `implementation.json` open_decisions OA-AFC-A1/A2. |
| FR-02 | P2 | `implementation.json:103` | `journey_settings.planning_review.candidate_revision` is `2c13a6b…` — the seed/base commit, which contains no package. The candidate commit is `4afc998`. (The manifest §2 avoids this by saying Baseline + ref + digest.) | Set `candidate_revision` to the planning-branch commit hash containing the repaired package at repair-commit time; keep `candidate_ref` and `candidate_digest` (rebound). |
| FR-03 | P2 | `amazon-fantasy-companion-dod-manifest.html:711`, `implementation.json:10953` | Manifest §2 records `seit.json: cae54c15…`, but the shipped `seit.json` hashes to `bc02a21f…` (`sha256sum` verified). The other three input hashes in the same block match current files, so the block is internally inconsistent. Cause: PD-R1 rebound `seit.json` source_baseline (`d972faa0`→`d83150f7`, per `specialists/pd-r1-correction.md`) without refreshing the rendered value (`:40` `seit_json_sha256_at_integration` correctly keeps the historical value). | Set the `dod_manifest` entry `{"label": "seit.json", "value"}` at `implementation.json:10953` to `bc02a21fe554591576d5de8a82ecc4f09e4480e07aa6a4e30abb568727e967d6` and regenerate the manifest; leave `:40` as the labeled at-integration record. |
| FR-04 | P2 | `implementation.json:5277,5540,5814,6464,6722` (S25/S26/S27/S31/S32 `write_set`), manifest `:3355-3359` (TE-F05 open) | AC-AFC-VIS-01 requires on-stick screenshots "kept with the review evidence" and the five UI slices' stop conditions require screencaps, but no write set covers where they go (TE-F05, still open). Authority already allows `docs/evidence/**`, but role grants limit writers to the dispatched slice's write set. No OD item presents the TE-F05 choice to the owner. | TE-F05 option 1: add `docs/evidence/visual/<slice>/` to the S25, S26, S27, S31, S32 `write_set` arrays (inside existing authority); or record option 2 (untracked Lifecycle evidence dir in `journey.json` `execution_receipts`) as the owner disposition at review. Either closes TE-F05. |
| FR-05 | P3 | `amazon-fantasy-companion-dod-manifest.html:3510` | "Owner entry action for Planning landing" says "Integrated approval of this package (OD-AFC-01..06)" — a stale range contradicting the 12-item table directly above it (`:3436-3502`). (Same stale text in `specialists/slice-graph.md:110`, outside review scope.) | Replace `(OD-AFC-01..06)` with `(OD-AFC-01..10, OA-AFC-A1..A2)`; regenerate or hand-edit the row consistently with `implementation.json` source. |
| FR-06 | P3 | `amazon-fantasy-companion-technical-plan.md:412`, `implementation.json:10776`, `seit.json:80` | OD-AFC-01 recommendations say option B "costs one light slice (S41 …)", contradicting PI-F01: S41 is `work_class: judgement`, role Product Implementer (manifest S41 row `:2651-2655` correctly shows Product Implementer). | Replace "costs one light slice (S41," with "costs one judgement slice (S41," in all three locations. |
| FR-07 | P3 | `implementation.json:8862`, manifest `:3364-3368` (TE-F07 open) | `integration_plan.configuration_identity.aws.template_digest` still reads as a source-file digest and does not name the `SourceCommit`/`TemplateSha256` stack tags that `CMD-TEMPLATE-DIGEST` (seit.json, correct) compares. Executable path is right; the prose is stale. | Reword to: "stack tags SourceCommit (= deployed commit) and TemplateSha256 (= sha256 of backend/template.yaml at that commit), read by CMD-TEMPLATE-DIGEST". |
| FR-08 | P3 | `amazon-fantasy-companion-technical-plan.md:253` vs `seit.json:5165` | AC-AFC-SUB-03 Verification column says `inspection`; its proof case `SEIT-AFC-SUB-03` says `"method": "demonstration"`. The only method-label mismatch across all 81 AC/RISK rows (V&V itself exists and is executable). | Change one label to match the other (recommend `demonstration` in the TP row: the proof records and views device clips). |

## What was verified clean (no finding)

- Routes: all 54 slices' `model_route` primary + `ordered_fallbacks` (order
  included) and `review_path.reviewer_route` match
  `journey.json profile_selection.frozen_snapshots` for their lane profile;
  lane→profile bindings match `DEC-AFC-PROFILE-001`.
- Graph: no cycles; no dep points to a later wave/milestone; `dependencies`
  section == slice edges (71/71); S41/S34 conditional gates present
  (`dispatchable: false`, `conditional_on`, `human_decision`).
- Parallelism: 7 unordered write-set overlaps found mechanically; all are
  benign by design (S08→S39 sequential phases; S33 defect lane with the
  documented dispatch-time write-set check, TP Wave 4 row).
- Traceability: 65 AC + 16 RISK rows each have ≥1 of the 126 SEIT proof cases;
  all proof/trace `command_id`s resolve to the 75 defined procedures; all
  slice `command_ids`/`requirement_ids`/`design_ids`/`seit_proof_rows` resolve;
  every AC is bound to ≥1 slice (RISK-07/08/11/16 are Orchestrator-executed
  PROC rows, as allocated).
- Owner boundary: no slice or SEIT command performs a C9/owner-only action
  (`PROC-SUB-INSPECT` is read-only and asserts no agent flipped visibility);
  S18/S21 declare owner actions in `human_decision`; S06/S41 carry their OD
  gates; all write sets are inside `authority.json` allowed paths (two
  conditional Alphazedehq paths match their OD conditions).
- Rule 12: no literal `/home/<user>/`, `/Users/`, or `C:\Users\` path in any
  review-scope file (`$HOME`/`<user>` placeholders and detector regexes only).
  The single `$HOME` occurrence in the worktree is in the untracked,
  git-ignored `specialists/planning-review-run.log`, not in `4afc998`
  (which also confirms OD-AFC-06's premise: `.gitignore:5: *.log`).
- Cross-checks: D4 skill-size claims verified on disk (`setup-a-repo` 60
  lines, `ship-pull-request` 82); all four `views.json` `svg_sha256` match;
  manifest TP/design/views hashes match; milestone slice lists match slice
  fields; `design_lenses` all valid; every `review_path` carries OCR delegate
  + Reverify (AC-AFC-REV-01); SD-013 consistently superseded by SD-022.
- Schedule: milestone dues M1 10-13T23:00Z → M5 10-23T12:00Z fit T_deadline
  with the documented 7 h owner buffer; live-game windows (10-12/15/18/19/22)
  match RISK-AFC-14; S16/M2/S28 sequencing is satisfiable. Tight but not
  provably infeasible — pressure noted, not a finding.

## OCR coverage_assist (delegate mode, REQUIRED)

- `ocr delegate preview --from 2c13a6b --to 4afc998`: OK, 8 reviewable files
  (rest excluded `unsupported_ext`; the excluded `.md` review-scope files were
  read directly per packet scope).
- `ocr delegate rule <file>` for all 8: OK, no tool failures. Rule groups
  applied per file:

| File | Rule group | Result |
|---|---|---|
| `amazon-fantasy-companion-dod-manifest.html` | system/default (correctness, security, performance, maintainability, tests) | PASS. No `<script>`/event-handler/`javascript:`/iframe/object content; 4 embedded static SVGs + 1 `<style>` block only. No XSS surface; static generated artifact. Content fidelity spot-checked (SUB-03 row, S41 role, §2 hashes → FR-03). |
| `authority.json` | json-keys spelling | PASS, no key typos (mechanical aspell pass over all key words; only domain terms flagged). |
| `implementation.json` | json-keys spelling | PASS, no key typos (430 unique keys checked). |
| `journey.json` | json-keys spelling | PASS, no key typos. |
| `seit.json` | json-keys spelling | PASS, no key typos. |
| `views/views.json` | json-keys spelling | PASS, no key typos. |
| `specialists/ac_mechanical_lint.py` | python rules | PASS, no blocking issue. Non-blocking note: no `argv` guard (`sys.argv[1]/[2]` raise `IndexError` when misinvoked); `exec_module` target is operator-supplied, not attacker-controlled — not flagged. Script demonstrably ran (`ac-mechanical-lint-r1.txt`). |
| `superseded-run1/ac_mechanical_lint.py` | python rules | PASS, identical file (`diff` clean), same non-blocking note. |

No OCR-identified defect rises to a review finding; the OCR note on the lint
scripts is advisory and needs no repair budget.

## Reverify

Reverify: not applicable — the candidate contains no compiled binary.

## Route actually used

Primary `planning-review` route: Muse Code / Muse Spark / max (this session;
no fallback activated; no 429 encountered).

## developer_feedback

- Observations: (1) The package is unusually self-consistent for its size;
  most deltas (IE-F, TE-F, PI-F) were applied with receipts before this
  review. (2) `seit.json decision_baseline.open_items` still lists only
  OD-AFC-01..10 (pre-amendment projection); the authoritative 12-item list in
  `implementation.json` is complete, so this is cosmetic — consider refreshing
  the projection in the repair round. (3) Schedule pressure is real (M1 packs
  four cross-repo PRs + gate + scaffolds into ~36 h post-approval) but fits
  the owner-set deadline; no date change proposed. (4) S20T's formal dep on
  full S16 is stricter than its "first capture" text needs, but harmless since
  Wave 3 follows M2.
- Tools exercised: `node plan-package.cjs` (PASS), `ocr delegate preview`
  + `ocr delegate rule` ×8, `sha256sum`, `aspell`, project JSON parsed with
  `python3` (purpose-built check scripts in `/tmp/afc-review/`, not committed),
  `git show`/`git status`/`git check-ignore`, `diff`, `grep`.
