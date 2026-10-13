---
type: specialist-receipt
title: Requirements Engineer Phase 2 AC/RISK gate receipt — AFC-2026-10-11 (Lifecycle-local rows)
okf_status: draft
tags: [requirements, planning, afc, phase-2]
---

verdict: **REPAIRABLE_FAILURE**

candidate_ref: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/amazon-fantasy-companion-phase-2-technical-plan.md`
section gated: `## Requirements (Lifecycle-local)` — 23 AC-AFC-P2-* rows + 13 RISK-AFC-P2-* rows (36 total).
role: Requirements Engineer, planning session (BEARING_ROLE=requirements_engineer).
decision basis: DEC-AFC-SD-001..038 and DEC-AFC-APPROVAL-ST5 (Phase 1 journey.json);
issue #1 body (read-only `gh api .../issues/1`); Phase 1 deferred table
(`§Deferred to the spec track or Phase 2`); f885e48 parent rows (superseded-run1 plan);
register `requirements-register.md` (63 active UIDs, by reference, not re-gated).
mechanical: `lint-sdoc.py --profile library` not applicable — Markdown rows are
invisible to the lint (same basis as prior gates); mechanical evidence is the
grep probes in VERIFY. No new published standard cited (s8_rows
SRC-EMV-NASA-SEH, SRC-EMV-COE, SRC-EMV-29148 metadata-only).

changed_paths (exact write set, this node only):

- `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/re-p2-ac-receipt.md` (this file)

counts: 36 rows gated; 29 PASS; 7 FAIL (all repairable by the Planning and
Design node from confirmed sources; exact replacement text below); 1 coverage
GAP (missing owner-checklist row; exact new-row text proposed). No row needs
owner intent beyond the package's own open items, so no NEEDS_OWNER_DECISION.

## Failing rows (Planning node applies the exact text)

### 1. AC-AFC-P2-SPIKE-01 — FAIL

- checklist: CHK-RE-24, typed failure CONTRADICTION.
- evidence: the closed conditional set `(C1, C2, C5, C6, C8)` names C8, but the
  subject routes (`device, provider, feed or lineup`) and the allocation
  (`P2-X01..P2-X07`) exclude the voice route and its spike P2-X11, the only
  spike that triggers C8. No allocated spike can trigger a listed member.
- exact replacement statement: `Before any product slice depends on a device,
  provider, feed, lineup or voice route, the program shall run the spike for
  that route on the real target and land `spikes/<sp>/VERDICT.md` stating the
  verdict, the exact route tried, the observed result with evidence paths, the
  conditional it triggers (C1, C2, C5, C6, C8) and the register UIDs it
  unblocks.`
- exact replacement allocation: `P2-X01..P2-X07, P2-X11 (conditional on OD-AFC-03)`.

### 2. AC-AFC-P2-GATE-01 — FAIL

- checklist: CHK-RE-25 (GLOSSARY_MISMATCH) + CHK-RE-17 (INCOMPLETE).
- evidence: `report a missing tool as GAP` matches no defined term (the
  Glossary defines `typed gap`, and the Phase 1 precedent always says `typed
  gap`); the area's exit code on a missing tool is undefined, so whether a GAP
  run satisfies AC-AFC-P2-LAND-01's `green gate run` cannot be decided.
- exact replacement statement: `The gate entrypoint `tools/ci/gate.sh` shall
  gain the areas `tvapp` (Gradle unit tests, Android lint and debug assemble
  under `tv-app/`) and `backend` (pytest and SAM template validation under
  `backend/`), invoked by the same local hooks and Actions workflow with path
  filters, stable check names and pinned actions per AC-AFC-CI-02; each area
  shall exit non-zero on any failing check, shall record a missing tool as a
  typed gap with its exact error and exit non-zero, and shall report `PASS`
  with the detail `no <dir>/ tree` only when its directory does not exist.`
- source, verification, allocation unchanged.

### 3. AC-AFC-P2-SPEC-01 — FAIL

- checklist: CHK-RE-13 (AMBIGUOUS) + CHK-RE-17 (INCOMPLETE) + CHK-RE-30
  (INCORRECT vs parent Phase 1 deferred AC-AFC-SPEC-03).
- evidence: `record the verdicts` most naturally reads as the three trigger
  verdicts (panel, provider, notification), leaving the device (P2-X01), ESPN
  (P2-X05), Yahoo/manual (P2-X06) and detection (P2-X07) verdicts with no
  spec-recording carrier, while parent SPEC-03 requires all SP verdicts, the
  panel mode, the provider route and every recorded limitation. `the closed
  contract constants` has no referent: the only constants in the plan are the
  Glossary Lifecycle-local design quantities, still proposals pending
  OD-AFC-05.
- exact replacement statement: `When the panel (P2-X04), provider (P2-X03) and
  notification (P2-X02) spike verdicts have landed, the D1 specification shall
  be revised to record every landed spike verdict from P2-X01..P2-X07 (plus
  P2-X11 when it runs), the verdict-selected panel mode and provider routes
  with every recorded limitation, the aligned model names
  (`PanelMode.fullScreen`, no `tvApp.player`, AFC-PR-066 allocation) and the
  Glossary Lifecycle-local design quantities as approved under OD-AFC-05, with
  a revision row listing the changed sections and linking the pull request and
  its diff, and `gate.sh spec` shall pass with a byte-identical rebuild.`
- source, verification, allocation unchanged.

### 4. AC-AFC-P2-SUB-01 — FAIL

- checklist: CHK-RE-17 (INCOMPLETE) + CHK-RE-30 (INCORRECT vs parent Phase 1
  deferred AC-AFC-SUB-01).
- evidence: parent SUB-01 requires `the panel-mode and voice limitation
  statements`. `the known limitations recorded by the spike verdicts` covers
  the panel mode (P2-X04 verdict) but not the voice/Alexa status when P2-X11
  never runs (OD-AFC-03 = no, or dropped), in which case no verdict records
  it and the README could omit it while satisfying the row.
- exact replacement statement: `The repository shall contain a README with a
  product description, fresh-setup instructions for the TV app and the backend
  (from a clean checkout, using only repository-relative paths and documented
  owner-supplied inputs), the judge-access route through T_judge_access, the
  known limitations recorded by the spike verdicts, and the voice/Alexa status
  (implemented and verified on the device, or not offered).`
- source, verification, allocation unchanged.

### 5. AC-AFC-P2-DX-02 — FAIL

- checklist: CHK-RE-17 (INCOMPLETE) + CHK-RE-30 (INCORRECT vs parent Phase 1
  deferred AC-AFC-DX-03).
- evidence: parent DX-03 requires the per-tool summary and friction log to be
  `checked against the current official rules before submission`. The row
  covers assembly and sanitization but drops the rules check, which no other
  row carries.
- exact replacement statement: `Before M5 exit the Scribe shall assemble, from
  `docs/developer-feedback/observations.md`, a per-tool Product Feedback file
  (used for, what worked well, what needs work, onboarding from zero to hello
  world, would build again Yes/No and why, AWS services used and how),
  optional Feature Requests with priority Critical / Important / Nice-to-have,
  and a sanitized Friction Log with the Devpost entry fields, covering every
  tool, API, SDK and device used in Phase 2, with no credentials, account
  details or local paths, and shall check the Product Feedback file and the
  Friction Log against the official rules current at submission.`
- source, verification, allocation unchanged.

### 6. RISK-AFC-P2-06 — FAIL

- checklist: CHK-RE-13 (AMBIGUOUS) + CHK-RE-25 (GLOSSARY_MISMATCH).
- evidence: `the manual verdict` is outside the Glossary's closed verdict
  vocabulary (`WORKS`, `PARTIAL`, `FAILS`, `TIMEBOX`). The Yahoo route's
  outcome at T_yahoo without approval is a failure of that route with manual
  entry selected.
- exact replacement statement (control): `If Yahoo approval is absent at
  T_yahoo, then P2-X06 shall record a FAILS verdict for the Yahoo route
  selecting labeled manual entry, and the backend shall use labeled manual
  entry as the single active source (AFC-PR-006, -007).`
- source, verification, allocation, risk, response unchanged.

### 7. RISK-AFC-P2-09 — FAIL

- checklist: CHK-RE-31 (UNCONFIRMED_ASSUMPTION).
- evidence: `an owner camera capture of the screen` is a shall-duty, but owner
  filming exists only under OD-AFC-P2-02 = A (OA-9 is itself conditional);
  under option B the duty is unsatisfiable. Plan convention conditions duties
  on open decisions (OD-AFC-03/05 precedents); this row silently assumes A.
- exact replacement statement (control): `If `adb` screencap or screenrecord
  returns black or blank frames for protected provider video, then the visual
  evidence shall combine the companion UI capture with window geometry from
  `dumpsys` and, if OD-AFC-P2-02 = A, an owner camera capture of the screen
  (OA-9); the demo plan shall mark any owner-filmed shots as owner-filmed and,
  if OD-AFC-P2-02 = B, shall use companion UI captures only for those shots.`
- source, verification, allocation, risk unchanged; response becomes `Geometry
  plus owner camera capture under A, companion UI only under B (OD-AFC-P2-02).`

### 8. Coverage GAP — missing owner-checklist row (new row proposed)

- checklist: CHK-RE-18, typed failure COVERAGE_GAP.
- evidence: Phase 1 deferred AC-AFC-SUB-02 (`The submission checklist shall
  list every owner-only action ... with its due time before T_deadline, and
  agents shall perform none of them`) has no carrier: no register UID (not
  product behavior), no Lifecycle-local row, and not an owner action (M5 exit
  and Exit criterion 4 assume the program hands the checklist over). Worse,
  slice P2-D05 already plans `docs/submission/owner-checklist.md` in its
  write set while tracing only AC-AFC-P2-SUB-02 — work with no covering
  requirement.
- exact new row for the `### Submission and developer feedback` table:

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-P2-SUB-04 | The program shall produce a submission checklist listing every owner-only action (OA-1..OA-9 and the §Exclusions owner-only actions) with its due time before T_deadline, and agents shall perform none of those actions. | #1 §Acceptance; Phase 1 deferred AC-AFC-SUB-02; DEC-AFC-SD-009 | inspection | P2-D05 |

## PASS table

| UID | Gate | note |
|---|---|---|
| AC-AFC-P2-SPIKE-02 | PASS | Singular duty; spike_panel_max defined; PanelMode.modeB + fullScreen verified in models (AFC-States.sysml, allocation.md); `otherwise` cleanly covers PARTIAL/FAILS/TIMEBOX; sources SD-006/SD-035-Q4/C5/PR-041/PR-047 check out. |
| AC-AFC-P2-SPIKE-03 | PASS | Provider order + local-broadcast behavior match SD-035 Q5 and PR-029; six-value vocabulary resolves via cited PR-029..031; no-invented-URI prohibition is the #1-stated need; allocation P2-X03 correct. |
| AC-AFC-P2-VNV-01 | PASS | Three area paths match the deferred table verbatim (tv-app, backend, device-integration); four required headings match Phase 1 AC-AFC-CI-04/VNV-01; SD-014 source confirmed. |
| AC-AFC-P2-LAND-01 | PASS | Rebase-or-merge, one review at integration step, no squash/force-push/local-main all match rules 4+9 and DEC-AFC-APPROVAL-001 (OA-AFC-A3 = A, confirmed); inspection-verifiable via landing records. |
| AC-AFC-P2-REV-01 | PASS | OCR delegation commands, Reverify-or-not-applicable, typed-gap-on-incomplete all match rule 15 verbatim; `typed gap` is the Glossary term. |
| AC-AFC-P2-VIS-01 | PASS | Stick adaptation of rule 16 with SD-024 path (`evidence/visual/<slice>/`) and no-account-data bound; judged-against cites PR-043/-045 by identity only. Note: allocation names P2-X09, a spike that changes no UI; harmless over-allocation (duty binds only UI-changing slices). |
| AC-AFC-P2-BUG-01 | PASS | Matches SD-037 + rule 20 (triage skill, bug-triager routes, packet contents, BUG_ROUTE escape); defect enumeration matches the rule's bug definition. |
| AC-AFC-P2-PATH-01 | PASS | Prohibition is the need (CHK-RE-09 justified); matches rule 12 + SD-010; PR-056 cited by identity, not restated; test-verifiable via `hygiene`. |
| AC-AFC-P2-SUPPLY-01 | PASS | Matches rule 10 (receipt before first use; refuse on BLOCK/INDETERMINATE); enumerated acquisitions are the plan's concrete external set; allocations cover first-use slices. |
| AC-AFC-P2-REL-01 | PASS | Matches SD-038 + rule 21 ([Unreleased] entry linking the PR; seed when absent); Keep-a-Changelog sections bounded. |
| AC-AFC-P2-REL-02 | PASS | Matches SD-038 + rules 4/21 (release-process skill; notes from changelog; publication owner-authorized); allocation P2-R1..R5. |
| AC-AFC-P2-PLAN-01 | PASS | Follows the Phase 1 AC-AFC-PLAN-01 pattern; impl_agent_cap defined (5, rule 17); all seven leases match the plan's lease table; serialization closure matches plan text. Note: `every slice belongs to exactly one wave` reasonably reads as planned slices; on-demand defect slices join the wave current at dispatch. |
| AC-AFC-P2-MS-01 | PASS | Covers deferred AC-AFC-PLAN-02 field for field (title, due date, description; `gh api` readback); `no milestone before approval` matches SD-023 (P2-7); allocation P2-L01. |
| AC-AFC-P2-SCHED-01 | PASS | Covers Phase 1 RISK-AFC-17 (remaining days to T_deadline, remaining live windows, scope cuts as owner decisions); both quantity/term names defined; spike-before-window scheduling is elaboration, not contradiction. |
| AC-AFC-P2-SUB-02 | PASS | 2:50 bound satisfies #1's under-three-minutes with margin; both standout moments required; closed per-shot source vocabulary; `no shot claims behavior that has no passing evidence` carries deferred SUB-03 (labeled replay) and the demo half of SUB-04. |
| AC-AFC-P2-SUB-03 | PASS | Three conjuncts, one deliverable; Fantasy View differentiation matches SD-035 competitive verbatim; SD-036 discussion-only + public citations + external-context marking preserved; SD-008 track scope correct. |
| AC-AFC-P2-DX-01 | PASS | Matches #1 §Scribe contract (every packet/return; IDs + evidence or `no new observations` naming tools); follows f885e48 DX-01. |
| AC-AFC-P2-APK-01 | PASS | Tagged commit + sha256 + Reverify-on-exact-APK match rule 15 and the f885e48 M5 exit; `minSdk 25` mirrors PR-053's own spelling (attribute claim, not quantity citation); typed-gap clause present. |
| RISK-AFC-P2-01 | PASS | Conditional duty with recorded rationale (Q6) and response; min_sdk defined; no-purchase/no-switch matches SD-003; class C stop consistent with approved Phase 1 usage. |
| RISK-AFC-P2-02 | PASS | Verdict-names-limitation + class C stop before PR-015 product code matches #1 Fire OS notification finding; no-silent-substitution matches the integration obligation; PR-015 by identity. |
| RISK-AFC-P2-03 | PASS | Five non-success outcomes match PR-031 minus `gameOpened`; no-relabel clause is checkable; `honestly` adds no standalone bound (VAGUE_TERM N/A: the bound is `strongest observed outcome` + no-relabel). |
| RISK-AFC-P2-04 | PASS | Full-screen fallback + alerts/Watch preserved match SD-035 Q4 and PR-047/-048 (cited, not restated); consistent with SPIKE-02's `otherwise` for the PARTIAL case. |
| RISK-AFC-P2-05 | PASS | Labeled-replay + reject-invalid-without-mutation derive from PR-013/-064 (cited, conditional trigger is the Lifecycle-local content); C3 owner-terms presentation matches OA-6 timing. |
| RISK-AFC-P2-07 | PASS | Stop + class F owner stop + no-agent-upgrade match SD-005 and C4; PR-054 by identity; allocation covers AWS-touching slices. |
| RISK-AFC-P2-08 | PASS | Labeled-replay-for-repeatability + reserve-live-windows-for-device-evidence match #1 judging section and C2; `four live windows` matches the Glossary term (Mon 10-12 is ESPN-capture-only). Note: allocation omits P2-X03, a `live-game-window` lease holder; the statement's `the slice` still binds it. |
| RISK-AFC-P2-10 | PASS | Confirmed-limit trigger, next-approved-fallback-or-queue response, no-switch-on-other-errors; preserves frozen coverage-assist/Reverify settings per owner-stops class B. |
| RISK-AFC-P2-11 | PASS | Wait-for-S09/P2-G01 + no-landing-without-green-gate consistent with LAND-01 and the Wave 1 order; work-continues-on-branch keeps the response feasible. |
| RISK-AFC-P2-12 | PASS | Follows Phase 1 RISK-AFC-11 (block-until-sanitized; record-without-value; owner rotates); `customer data` addition justified by capture/token leakage paths; rules 2+12, PR-055/-056, C9 all check out. |
| RISK-AFC-P2-13 | PASS | 12 h trigger is measurable with urgency rationale (eleven days, fixed windows); priority order resolves to §Program plan's Scope-reduction list; no-silent-cuts matches RISK-AFC-17 lineage. |

Cross-row checks: no restated register text (all PR cites are identity-only or
conditional derivations); no two rows contradict (SPIKE-02/RISK-04 PARTIAL
handling, LAND-01/RISK-11 gate order, RISK-08/RISK-09 evidence rules all
agree); every quantity name cited in a row (`spike_panel_max`, `min_sdk`,
`T_deadline`, `T_yahoo`, `T_judge_access`, `impl_agent_cap`) exists in the
Glossary tables; feasibility holds within the wave/lease plan for every row.

## Owner questions

none. Every FAIL is repairable from confirmed decisions, parent rows, or the
Glossary; the GAP has a confirmed parent (deferred SUB-02) and an already
planned write set. Open options (OD-AFC-02..05, OA-AFC-A1, OD-AFC-P2-01..05)
stay with the integrated review; RISK-AFC-P2-09's repair conditions on
OD-AFC-P2-02 rather than assuming it.

## Decision coverage (obligation → covering ID, owner action, or GAP)

Issue #1 submission/feedback obligations:

| Obligation | Covering ID / owner action |
|---|---|
| Acceptance: working demo, actual track tech used | Register UIDs (product behaviors) + Exit criteria |
| Acceptance: repo with source/assets + setup instructions | AC-AFC-P2-SUB-01 |
| Acceptance: public video under three minutes | AC-AFC-P2-SUB-02 (plan) + OA-7 owner upload |
| Acceptance: description, tracks, tool feedback | AC-AFC-P2-SUB-03 + AC-AFC-P2-DX-02; SD-008 tracks decided |
| Acceptance: in-window-changes explanation | N/A: no pre-existing project (repo created in-window 2026-10-10); SUB-03 write-up is the fallback carrier |
| Acceptance: AWS Builder extra fields | AC-AFC-P2-SUB-03 + AC-AFC-P2-DX-02 |
| Acceptance: judge access through T_judge_access | AC-AFC-P2-SUB-01 + OA-7 owner keeps access |
| Acceptance: owner authorizes sharing/submission | OA-7, OA-8 (owner actions) |
| Acceptance: submit before deadline, record URL | OA-7 (owner action) |
| Acceptance: private-submission invite timing | N/A: SD-009 chose public; OA-5 owner flip |
| Scribe contract: packets/returns | AC-AFC-P2-DX-01 |
| Scribe contract: assembly + sanitized logs | AC-AFC-P2-DX-02 (with repair) |
| Scribe contract: running log | Phase 1 AC-AFC-DX-02 (exists) |
| Development integration obligation (panel proof) | AC-AFC-P2-SPIKE-01/02 + RISK-AFC-P2-04 |
| Development setup 7-item checklist | AC-AFC-P2-SPIKE-01/02/03 (P2-X01..X07) + register |
| App-launch research (explicit outcomes, no invented URIs) | AC-AFC-P2-SPIKE-03 + RISK-AFC-P2-03 + PR-030/031 |
| Judging/demo (standout, storyboard, labeled replay) | AC-AFC-P2-SUB-02 + RISK-AFC-P2-08/09 |
| Judging: no invented usage/latency figures; no perf benchmarking | §Exclusions + PR-062/063 (declared bounds, no measurement) |

Phase 1 deferred items owned by Phase 2:

| Deferred item | Covering ID / disposition |
|---|---|
| Product AC rows (items 1,2,3,4,6 + panel + controls) | 63 active register UIDs |
| Spikes SP-1..SP-7; SEC-01..04; LW-01 | AC-AFC-P2-SPIKE-01/02/03; PR-054/055/056; PR-059..063 |
| AC-AFC-SPEC-02 (D1 build quality) | Spec-track ST-4, not Phase 2 |
| AC-AFC-SPEC-03 (spike-verdict revision) | AC-AFC-P2-SPEC-01 (with repair) |
| AC-AFC-PLAN-02 (milestones + readback) | AC-AFC-P2-MS-01 |
| AC-AFC-DX-02 assembly + DX-03 (sanitize + rules check) | AC-AFC-P2-DX-02 (with repair) |
| AC-AFC-SUB-01 (README) | AC-AFC-P2-SUB-01 (with repair) |
| AC-AFC-SUB-02 (owner checklist) | GAP → proposed AC-AFC-P2-SUB-04 (P2-D05) |
| AC-AFC-SUB-03 (demo clips) | AC-AFC-P2-SUB-02 |
| AC-AFC-SUB-04 (voice claims) | AC-AFC-P2-SUB-02 (demo) + AC-AFC-P2-SUB-03 (write-up) + SUB-01 repair (README) |
| AC-AFC-VIS-01 (visual review) | AC-AFC-P2-VIS-01 |
| RISK-AFC-01..06, 09, 14 | RISK-AFC-P2-01..08 (01→device, 02→notification, 03→links, 04→panel, 05→ESPN, 06→Yahoo, 07→AWS budget, 08→live windows) |
| RISK-AFC-10 (identity match) | PR-024 (register UID; product behavior, no Lifecycle-local trigger) |
| Gate areas android/backend | AC-AFC-P2-GATE-01 as tvapp/backend (with repair); CONTRACT-AFC-GATE unchanged |
| Vnv areas tv-app/backend/device-integration | AC-AFC-P2-VNV-01 |
| Product design DES-*/CONTRACT-* + quantities; views V1..V3 | Spec-track models/D1, not Phase 2 |
| Slices S04..S40, waves 3..5, milestones M1..M5 | Re-planned: AC-AFC-P2-PLAN-01, AC-AFC-P2-MS-01, §Program plan |
| OD-AFC-02..05, OA-AFC-A1 | Open owner items for the integrated review (owner decision at review) |

uncovered: AC-AFC-SUB-02 only (GAP above; proposed text supplied).

## VERIFY (read-only probes in the worktree)

- Row count `grep -oE` over the technical plan: 36 unique IDs = 23
  AC-AFC-P2-* + 13 RISK-AFC-P2-*.
- Quantity-name probe: every name cited in a row statement
  (`spike_panel_max`, `min_sdk`, `T_deadline`, `T_yahoo`, `T_judge_access`,
  `impl_agent_cap`) appears in the Glossary tables.
- `PanelMode.modeB` verified in `models/AFC-States.sysml` + `models/allocation.md`;
  `CONTRACT-AFC-GATE` verified declared in the Phase 1 `design.md`;
  `typed gap` + class-stop usage match the approved Phase 1 package.
- Rule-12 shape scan `grep -nE '(/home/|/Users/)[A-Za-z0-9._-]+/'` over the
  technical plan: no output.
- P2-D05 goal/write set (`slice-graph.md`) confirms the checklist file
  `docs/submission/owner-checklist.md` is planned but untraced — the GAP.

## Remaining risks

- If the owner picks OD-AFC-P2-02 = B, the repaired RISK-AFC-P2-09 holds, but
  P2-X12's owner-camera shots and OA-9 fall away; Planning owns that slice impact.
- The SPEC-01 repair keys the constants to OD-AFC-05 as approved; amended
  values flow to P2-D02, not to a second gate round.
- SPEC-01's aligned model names assume OD-AFC-P2-05 approves the recorded
  planning truth (sm-p2-delta, re-p2-delta receipts); rejection is a
  package-level rework event, not a row defect.
- Observations (not findings): PLAN-01's `every slice in exactly one wave`
  reads as planned slices (defect slices join the wave current at dispatch);
  VIS-01 over-allocates P2-X09; RISK-AFC-P2-08's allocation omits P2-X03, a
  `live-game-window` holder bound by the statement anyway.

## developer_feedback

no new observations. Tools exercised: file reads (technical plan,
requirements-register.md, re-p2-delta-receipt.md, both SKILL.md files plus the
checklist/quality-gate/gate-report references, artifact-grammar.md,
cross-repo rules, Phase 1 plan/design/journey excerpts), `gh api` read-only
fetch of issue #1 body, `grep`/python verification probes, `write_file` (this
receipt).
