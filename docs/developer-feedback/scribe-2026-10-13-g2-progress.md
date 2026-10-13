# Developer feedback — Scribe session, AFC planning progress (2026-10-13)

Scope: event transcription only (lease SCR-planning-progress). No product edits, no external sending.
Tracks: Fire TV track + AWS Builder mini challenge (per DEC-AFC-SD-008). No AWS services used in this Scribe session.
Field rules: evidence/devpost-feedback-rules.md (DEC-AFC-SD-025). Durations, ease-of-use, and versions are stated only where directly observed in the cited receipts; unknowns are marked unknown.
Sources (read only): execution_receipts in journey.json; Phase 2 specialist receipts te-p2-codex-receipt.md and ie-p2-codex-delta-receipt.md (phase2-plan worktree); ST-4 g5 author receipt.json + verification.txt on main; control packets ST-4-g5-review-result.md, B2-review-result.md, S44-azedge-review-result.md, B3-integrate.md.

## Events transcribed (verified)

- B3: Alphazedehq#320 MERGED at 0467883 (2026-10-13T03:40:57Z). 81 tests; root merge gate PASS; code/test bytes unchanged from the independently reviewed repair; CHANGELOG-only conflict with newer main resolved preserve-both by B3-integrate. Worktree/local/remote branch removed.
- B2: amazon-fantasy-companion#14 MERGED at c2468c9 (2026-10-13T03:55:05Z). Reviewer 39/39 plus independent red/green reproduction and OCR; hosted checks 4/4.
- S44: azedge#304 MERGED at 5ac113e (2026-10-13T03:58:52Z). Independent OCR + foundation 16 PASS + local fast gates 29 PASS / 12 SKIP. No claim the skipped workspace-tests suites ran; the prior provider_reads_once_per_admitted_attempt flake was not reproduced and is not claimed fixed.
- ST-4 / ST5 conditions: amazon-fantasy-companion#10 MERGED at 92f3ed1 (2026-10-13T04:20:58Z). Independent verification: 749 links/anchors, 66/66 UIDs, byte-identical rebuild, approved prose preserved, 39 tests, hosted 4/4, one independent review PASS with zero findings. Untracked g4/g5-review evidence byte-preserved; g5 author evidence on main at the Phase 2 canonical relative paths. No release/tag/visibility change.
- PR11 closed as redundant (2026-10-13T04:13:22Z): patch 579b951 equivalent to already-main d259c169; correctly never marked merged.
- Owner correction recorded as DEC-AFC-SD-039 (2026-10-13T03:55:05Z): the current Codex session is the Planning and Design lead; the pending lead-route question is closed, not a specialist-profile amendment. Root continues configured roles/fallbacks. User task remains planning plus approved tracking setup; no product execution.
- Planning status: TE initial structural PASS (100 proof cases: 63 active product + 37 lifecycle-local; 64 commands) with nine reconciliation findings TE-P2-F01..F09; root applied source corrections; IE correction 2 returned READY (44 steps, 52 slices, 39 logical issue groups; 13 TDD pairs share issues). Plan Integrator running; TE finalization and independent planning review remain. No new independent planning review yet.
- Boundary: the TE planning PASS and IE READY cover planning authorship only. They do not prove product/runtime behavior or owner acceptance. Stated in both receipts.
- Q10/S8 engineering-methods ledger: external, outside this write set; not restored here and not claimed restored.

## Product feedback: Muse Code transcription session

- Tools used and for what: this Muse Code session for read-only Scribe transcription — reads of journey.json (decisions, execution_receipts, history), dispatch/return/review/landing records, control review packets, main-tree author receipts via read-only git, and Phase 2 specialist receipts; appends to journey.json history and this file.
- What worked well: every cited record resolved from the control checkout, origin/main, or the named Phase 2 worktree paths; review packets and receipts each carried their own developer_feedback sections, so no log mining was needed.
- What needs work: nothing observed this session.
- Onboarding (zero to hello world): no setup was needed; the control checkout was the working directory and all evidence paths resolved as dispatched.
- Would you build with this again: yes — read-only inspection plus a bounded write set sufficed for the whole task.

## Per-tool observation/coverage ledger (this session only, from receipts)

Positive paths:

- Codex CLI planning/author routes: TE (first fallback) authored a schema-valid structural SEIT with passing checker and expected negative validator probes; IE correction 2 reconciled TE findings into the assembly plan with a passing artifact validator; ST-4 g5 author produced the verified link/revision amendment. No route switch or nested agent in any of the three receipts.
- Muse Code review routes: ST-4 g5 review PASS (all commands re-run, 80 OCR rules applied, zero findings); S44 azedge review PASS (both required gates re-run, OCR rules for all three files, zero findings).
- Codex CLI review route: B2 review PASS with independently executed 39/39 tests, six-case red/green reproduction, and OCR rules for all four files.
- Deterministic gates: pytest/unittest suites, gate.sh, local-gates.sh, spec build/lint/diagram lint, check-links.py, check-vendor.py, vendor-check.sh, and hosted CI checks all reported with exit codes and counts; byte-identity assertions (rebuild, vendor pin, test-file freeze) verified by hash comparison.
- OCR (OpenCodeReview) delegation: ran in all three product reviews (ST-4 g5: 80/80 rules exit 0; B2: 4/4 files; S44: 3/3 files). Excluded files were read directly by reviewers; no typed capability gaps.
- Reverify: correctly recorded not-applicable for source-only changes (ST-4 g5, B2, S44, IE delta). TE probed the installed tool (0.11.0, engines present) and kept the APK-manifest semantic gap typed as unproven capability, never PASS by substitute.
- git/GitHub CLI: merge-tree conflict scoping, cherry patch-equivalence, PR-head readbacks, and hosted-check queries all behaved as documented.

Friction (see Friction log for detail): owner lead-route correction (orchestration, not vendor); check-vendor.py __pycache__ sensitivity; revision `changes` heading-only restriction; stale packet prep-reference path; gh unsupported-field query; SEIT schema coverage non-enforcement; reverify --version usage error; IE source-projection staleness; historical finding-count prose mismatch (28 vs 27); BRAN unavailable for AFC.

Timing observed: B2 reviewer unittest 8.43s, gate 8.14s; S44 foundation-contracts 40s, fast gate 966s; ST-4 g5 author gate ran 39 tests in 12.02s. All other run durations unknown.

## Friction log

### F1 — Lead-route question raised despite frozen profiles (owner correction)

- Tool: orchestration (route selection), not a vendor product.
- Task: resume Phase 2 Planning and Design after the Claude weekly limit blocked pd-phase2-resume.
- Steps taken: a lead-route question was raised to the owner (Codex CLI route vs waiting for the Claude reset); the owner asked why the question was raised despite profiles, then stated "You are the planning lead now".
- Expected vs actual: expected configured roles/fallbacks to govern without an owner round-trip; actual: one owner round-trip occurred before the lead was settled.
- Classification: orchestration friction; not a vendor bug. Closed by DEC-AFC-SD-039, not a specialist-profile amendment.
- Severity: non-blocking — planning proceeded on the Codex lead; root continues configured roles/fallbacks.
- Evidence: DEC-AFC-SD-039 (2026-10-13T03:55:05Z); supersedes the pending owner_question_pending history record (asked time was and remains unavailable, not fabricated).
- Impact: one avoidable owner interruption; no work lost.
- Workaround used: none needed after the decision; lead route settled.
- Actionable suggestion: when no configured fallback exists for a role, state the default (continue on the controlling session) and let the owner object, rather than asking an open route question.
- Uncertainty: timestamps of the owner's question and statement unknown; user task remains planning plus approved tracking setup, no product execution.

### F2 — check-vendor.py trips on reviewer-owned __pycache__

- Tool: spec-authoring vendor checker (check-vendor.py).
- Task: ST-4 g5 independent review re-runs.
- Steps taken: reviewer's own lint/build runs wrote untracked tools/**/__pycache__/; vendor-check failed its exact file-set assertion until those files were removed.
- Expected vs actual: expected verification runs to be repeatable without cleanup; actual: one manual cleanup needed. Committed tree was never dirty.
- Classification: checker robustness gap; not a candidate defect.
- Severity: non-blocking — author's PYTHONDONTWRITEBYTECODE=1 works around it.
- Evidence: packets/ST-4-g5-review-result.md (reviewer-environment note); main g5 author receipt limitations.
- Impact: one extra cleanup step per review session that runs lint/build without the flag.
- Workaround used: remove reviewer-owned __pycache__; author's verify.sh sets PYTHONDONTWRITEBYTECODE=1.
- Actionable suggestion: ignore __pycache__ in the checker's file-set assertion (see Feature Requests).
- Uncertainty: none material.

### F3 — Revision `changes` accepts source headings only

- Tool: spec-authoring revision metadata (spec_lint + builder).
- Task: ST-4 g5 revision 0.3 rows covering generated Appendix A changes.
- Steps taken: author described generated-Appendix-A changes in `summary` because `changes` identities must be source headings.
- Expected vs actual: expected every rendered change to be identity-traceable; actual: generated-output changes live in free text.
- Classification: tooling limitation, worked around by convention; not a defect in the candidate.
- Severity: non-blocking.
- Evidence: main g5 author receipt developer_feedback needs_work; packets/ST-4-g5-review-result.md developer_feedback.
- Impact: none on this landing; traceability convention documented.
- Workaround used: `summary` carries generated-output changes.
- Actionable suggestion: allow generated-section identities in `changes`, or document the summary convention in the skill (see Feature Requests).
- Uncertainty: none material.

### F4 — Named-document references still need author inspection beyond lint

- Tool: spec-authoring link lint.
- Task: ST-4 g5 arbitrary named-document and scope-decision references.
- Steps taken: lint enforced linked references; author still inspected non-mechanical references manually.
- Expected vs actual: expected lint to close all reference checks; actual: a residual manual-inspection step remains.
- Classification: known tooling boundary; the S43 probe's 19 unlinked references are closed, so this is narrower than before.
- Severity: non-blocking.
- Evidence: main g5 author receipt developer_feedback needs_work.
- Impact: none on this landing; reviewer re-verified references independently.
- Workaround used: direct author inspection of named targets.
- Actionable suggestion: none proposed; boundary is explicit.
- Uncertainty: none material.

### F5 — Packet prep-reference path stale

- Tool: packet template (test-engineering preparation reference path).
- Task: S44 azedge review preparation.
- Steps taken: packet named test-engineering/references/test-preparation.md, which does not exist; reviewer used preparation-and-evidence.md.
- Expected vs actual: expected the named path to exist; actual: one lookup miss, immediately resolved.
- Classification: stale template path; not a candidate defect.
- Severity: non-blocking.
- Evidence: packets/S44-azedge-review-result.md developer_feedback.
- Impact: none on the review outcome.
- Workaround used: current file preparation-and-evidence.md.
- Actionable suggestion: update the packet template path (see Feature Requests).
- Uncertainty: none material.

### F6 — jsonschema CLI deprecation warnings are environment noise

- Tool: gate environment (jsonschema CLI).
- Task: S44 azedge gate runs.
- Steps taken: deprecation warnings appeared in gate output; sanitized from gates.log.
- Expected vs actual: expected clean gate output; actual: warnings present but unrelated to the candidate.
- Classification: environment noise; not a candidate defect.
- Severity: non-blocking.
- Evidence: packets/S44-azedge-review-result.md developer_feedback.
- Impact: none; output sanitized.
- Workaround used: sanitize warnings from the committed log.
- Actionable suggestion: none for the product.
- Uncertainty: none material.

### F7 — gh query requested unsupported baseRefOid

- Tool: GitHub CLI (gh pr view fields).
- Task: B2 review PR identity readback.
- Steps taken: an optional identity query first requested unsupported baseRefOid; corrected to supported fields and readback succeeded.
- Expected vs actual: expected the field to exist; actual: one corrected retry.
- Classification: query compatibility observation; not a product defect.
- Severity: non-blocking.
- Evidence: packets/B2-review-result.md (Developer feedback and limits).
- Impact: none; readback succeeded.
- Workaround used: supported fields.
- Actionable suggestion: none for the product.
- Uncertainty: none material.

### F8 — SEIT schema does not enforce coverage/traceability/lineage

- Tool: Bearing Lite SEIT schema + local check_seit.py cross-check.
- Task: TE Phase 2 proof-plan authorship.
- Steps taken: schema admits contentful proof objects but does not enforce exact register coverage, one-ID traceability, command resolution, source hashes, or frozen capability preservation; TE's bounded checker cross-checked those omissions and all three rejection probes behaved as expected.
- Expected vs actual: expected schema-level enforcement; actual: enforcement lives in a per-artifact checker.
- Classification: schema boundary, explicitly compensated; no schema modification proposed or made.
- Severity: non-blocking for this artifact.
- Evidence: Phase 2 specialists/te-p2-codex-receipt.md developer_feedback TE-P2-OBS-002; evidence/te-p2-codex/validation.txt, validator-self-check.json.
- Impact: none on this artifact; future authors must keep running an equivalent cross-check.
- Workaround used: bounded check_seit.py with expected negative probes.
- Actionable suggestion: none proposed by the author.
- Uncertainty: none material.

### F9 — reverify --version is an invalid invocation

- Tool: Reverify CLI (0.11.0).
- Task: TE capability probing.
- Steps taken: `reverify --version` returned a usage error; version came from installed package metadata instead.
- Expected vs actual: expected a version flag; actual: usage error, version obtained another way.
- Classification: usage error, not a product defect.
- Severity: non-blocking.
- Evidence: Phase 2 specialists/te-p2-codex-receipt.md (Commands run and output).
- Impact: none.
- Workaround used: installed metadata inspection.
- Actionable suggestion: none for the product.
- Uncertainty: none material.

### F10 — Assembly prose can repair semantics while literal conditions stay stale

- Tool: integration-plan authoring (human-readable paragraphs vs literal arrows/conditions).
- Task: IE correction 2 reconciliation.
- Steps taken: completion paragraphs repaired intended semantics while literal arrow Conditions and SEIT author projections stayed stale; IE proposed seven exact root-only corrections (IE-D2-G01..G07) without applying them outside its write set.
- Expected vs actual: expected prose and literal conditions to move together; actual: synthesis must bind current assembly and retain prior proof lineage explicitly.
- Classification: authoring-process observation; typed gap SOURCE_PACKET_RECONCILIATION_PENDING remains before integrated freeze.
- Severity: non-blocking for this delta; blocking for integrated freeze until root reconciles.
- Evidence: Phase 2 specialists/ie-p2-codex-delta-receipt.md developer_feedback IE-D2-OBS-001; evidence/ie-p2-codex/root-proposed-text.md, validation.json.
- Impact: root/Plan Integrator must synthesize; hashes must not be silently relabeled current.
- Workaround used: exact root-proposed text handed off; intended semantics explicit in the source continuation paragraph.
- Actionable suggestion: none for the product; process note for the Plan Integrator.
- Uncertainty: reconciliation outcome pending (Plan Integrator running).

### F11 — Historical receipt prose says 28 findings; actual JSON has 27

- Tool: planning evidence (historical finding-count prose).
- Task: IE correction 2 artifact validation.
- Steps taken: the artifact validator's first run assumed the receipt's stated 28 historical findings and rejected; actual unchanged JSON has 27 unique (25 CONFIRMED, 2 PLAUSIBLE). Check corrected to actual bytes, then passed; initial receipt left untouched.
- Expected vs actual: expected prose count to match data; actual: off by one, no finding dropped by the delta.
- Classification: historical receipt precision slip; local artifact-check assumption, not product runtime failure and not a consumed review/repair round.
- Severity: non-blocking.
- Evidence: Phase 2 specialists/ie-p2-codex-delta-receipt.md developer_feedback IE-D2-OBS-003; before snapshot and validation.txt.
- Impact: none; corrected before handoff.
- Workaround used: validate against actual bytes, not prose counts.
- Actionable suggestion: none for the product.
- Uncertainty: none material.

### F12 — BRAN unavailable for AFC (recurring)

- Tool: BRAN.
- Task: repository context for Scribe transcription and Phase 2 specialist work.
- Steps taken: per dispatch and receipts, BRAN has no native policy for AFC, so context was gathered by direct repository reads / ordinary discovery.
- Expected vs actual: expected BRAN-assisted reads; actual: direct reads, all transcriptions and receipts completed without gap.
- Classification: capability unavailable for this repository; not a failure.
- Severity: non-blocking — workarounds fully covered the need.
- Evidence: this packet; TE receipt (Authority/source); IE receipt (Commands and evidence); ST-4 g5 author receipt limitations; B2 review BRAN note.
- Impact: none on transcribed work.
- Workaround used: direct repository reads / ordinary discovery. Existing configured BRAN continues for HQ/azedge where applicable.
- Actionable suggestion: none; a native AFC BRAN policy is an owner decision, not a Scribe need.
- Uncertainty: whether an AFC policy will be configured later is unknown.

## Feature requests

### FR1 — Ignore __pycache__ in check-vendor.py file-set assertion

- Description: the vendor checker's exact file-set assertion should ignore __pycache__ directories produced by ordinary verification runs.
- Why it matters: reviewers re-running lint/build currently need a manual cleanup (or the PYTHONDONTWRITEBYTECODE=1 flag) before vendor-check passes; from F2.
- Priority: Nice-to-have.

### FR2 — Generated-section identities in revision `changes` (or documented convention)

- Description: allow generated-section identities (e.g. Appendix A rows) in revision `changes`, or document the summary-carries-generated-changes convention in the spec-authoring skill.
- Why it matters: keeps every rendered change identity-traceable instead of splitting traceability between `changes` and free-text `summary`; from F3.
- Priority: Nice-to-have.

### FR3 — Update packet template prep-reference path

- Description: change the packet template's test-engineering preparation reference from test-preparation.md to the current preparation-and-evidence.md.
- Why it matters: removes a stale-path lookup miss at the start of every review that follows the template; from F5.
- Priority: Nice-to-have.

### FR4 — Machine-readable usage-limit signal (carried from prior session)

- Description: usage-limit refusals should carry a machine-readable marker (distinct exit code or structured field) instead of sharing the generic failure exit with task errors.
- Why it matters: the orchestrator currently distinguishes "account exhausted, use fallback" from "task failed, repair" by matching log text; a typed signal removes that fragile parse.
- Priority: Nice-to-have.
- Note: carried forward from scribe-2026-10-13-g1-resume.md FR1; no new usage-limit event this session.
