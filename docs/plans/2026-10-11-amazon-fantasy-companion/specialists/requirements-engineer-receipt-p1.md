---
type: specialist-receipt
title: Requirements Engineer gate — AFC-2026-10-11 — Phase 1 regeneration
okf_status: draft
tags: [requirements, planning, afc]
---

verdict: **REPAIRABLE_FAILURE** (one failing row: RISK-AFC-17; exact replacement proposed below)

candidate_ref: `plan/2026-10-11-amazon-fantasy-companion` at `f885e48e58a6c10fa716b6c5ef048a71980a977a`, plus working-tree changes. Technical plan: `docs/plans/2026-10-11-amazon-fantasy-companion/amazon-fantasy-companion-technical-plan.md`; sha256: `aee9f476bf659d32a20dead7e109ff95381e70fc89af79125e6790550a0a33af`. Design: `design.md` sha256 `c0b9ccc58bae9eb2e88f98fa16d064918e2810ecd25b87f7a7861ca9361b41c4`. Slice graph: `specialists/slice-graph.md` sha256 `1295ae80123c65c2e0fa0f54d12dc3c9a44f2d6276a20bdb9a9a314f05fc4bf3`.

mechanical_receipt: `specialists/ac-mechanical-lint-p1.txt:1–33`, re-run reproduced byte-for-byte: **32 rows (24 AC + 8 RISK), 6 agnostic-term flags, exit 0**. The adapter imports `lint-sdoc.py` library-rule constants over Lifecycle-local Markdown rows; this is **not** a full `lint-sdoc.py --profile library` run or SDoc-conformance evidence. Exit 0 is not evidence of zero findings. All six flags are dispositioned below; each names a platform fixed by a confirmed owner decision.

changed_paths: `docs/plans/2026-10-11-amazon-fantasy-companion/specialists/requirements-engineer-receipt-p1.md` only (this session's write).

rows_checked: **32 = 24 AC + 8 RISK; 31 PASS, 1 failing row.** Every row was checked for statement, source/rationale, verification method and allocation. The 22 unmarked rows were diffed cell-by-cell against f885e48: all 22 statements are byte-identical to the previous PASS (receipt r2); only metadata changed (Allocation in all 22; Source also narrowed in LAND-01, RISK-AFC-07, RISK-AFC-11, RISK-AFC-15; Risk rationale reworded in RISK-AFC-07, RISK-AFC-15). Those metadata edits remove dangling traces (RISK-AFC-11 drops deferred AC-AFC-SEC-01; milestone refs become Phase 1 slices/records) and were re-checked, not assumed.

blocker: **none** beyond the one proposed row repair. No owner decision change is needed: the RISK-AFC-17 fix re-anchors its trigger to defined plan events without altering any confirmed decision.

## Failing row

### RISK-AFC-17 *(new)* — plan L174

- Checklist: CHK-RE-05 (UNMEASURABLE), CHK-RE-17 (INCOMPLETE).
- Defect (measurability): the trigger `"moves later than its target in §Program plan"` has no referent for two of the three listed events. §Program plan states exactly one target: `"Target: Phase 1 exits by 2026-10-13T23:00:00Z"`. No target exists anywhere in the plan for the owner's spec review (P2-5) or the Phase 2 plan approval (P2-6) — the Phase 2 sequence table carries entry criteria and dependencies but no dates. A slip of P2-5 or P2-6 therefore cannot be observed, so the control's activation condition is unmeasurable. (Incidental: the compound subject takes a singular verb, `"Phase 1 exit, ... moves"`.)
- Evidence: quoted trigger phrase above; plan §Program plan target line; §Phase 2 planning sequence table (no date column).
- Exact proposed replacement statement (other cells unchanged):

```text
When the Phase 2 plan is approved (P2-6), it shall state the remaining days to T_deadline and the live NFL windows still available, and shall present any scope reduction as an owner decision at the Phase 2 integrated review rather than cutting scope silently.
```

- Why this form: P2-6 approval is a defined event (Phase 2 sequence Exit: "Phase 2 package approved"); T_deadline is a Glossary quantity; the duty (remaining-days/windows visibility, no silent cuts) is fully preserved and is inspectable at approval, subsuming any earlier slip including Phase 1 exit. The `"it"` pronoun follows register precedent (RISK-AFC-11).

## Per-row findings

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-D5-01 | PASS | — | None |
| AC-AFC-D5-02 | PASS | — | None |
| AC-AFC-D5-03 | PASS | — | None |
| AC-AFC-D5-04 | PASS | — | None |
| AC-AFC-D5-05 | PASS | — | None |
| AC-AFC-D4-01 | PASS | — | None |
| AC-AFC-D4-02 | PASS | — | None |
| AC-AFC-D4-03 | PASS | — | None |
| AC-AFC-D4-04 | PASS | — | None |
| AC-AFC-D4-05 | PASS | — | None |
| AC-AFC-D4-06 | PASS | — | None |
| AC-AFC-CI-01 *(amended)* | PASS | — | None |
| AC-AFC-CI-02 | PASS | — | None |
| AC-AFC-CI-03 | PASS | — | None |
| AC-AFC-CI-04 *(new)* | PASS | — | None |
| AC-AFC-SPEC-01 *(amended)* | PASS | — | None |
| AC-AFC-VNV-01 *(amended)* | PASS | — | None |
| AC-AFC-DX-01 | PASS | — | None |
| AC-AFC-DX-02 *(amended)* | PASS | — | None |
| AC-AFC-PLAN-01 *(amended)* | PASS | — | None |
| AC-AFC-PLAN-03 *(new)* | PASS | — | None |
| AC-AFC-LAND-01 | PASS | — | None |
| AC-AFC-REV-01 | PASS | — | None |
| AC-AFC-PATH-01 | PASS | — | None |
| RISK-AFC-07 | PASS | — | None |
| RISK-AFC-08 | PASS | — | None |
| RISK-AFC-11 | PASS | — | None |
| RISK-AFC-12 | PASS | — | None |
| RISK-AFC-13 *(amended)* | PASS | — | None |
| RISK-AFC-15 | PASS | — | None |
| RISK-AFC-16 *(amended)* | PASS | — | None |
| RISK-AFC-17 *(new)* | measurability | Trigger `"moves later than its target in §Program plan"` is unmeasurable for P2-5/P2-6: no such targets exist in the plan. | `When the Phase 2 plan is approved (P2-6), it shall state the remaining days to T_deadline and the live NFL windows still available, and shall present any scope reduction as an owner decision at the Phase 2 integrated review rather than cutting scope silently.` |

## PASS rows

Plan line numbers refer to the candidate above; design references to `design.md` at the candidate hash.

| UID | Result | Note |
|---|---|---|
| AC-AFC-D5-01 | PASS | Plan L109: Unchanged PASS; allocation S06 matches slice-graph S06 requirements. |
| AC-AFC-D5-02 | PASS | Plan L110: Unchanged PASS; allocation S06 matches slice-graph S06. |
| AC-AFC-D5-03 | PASS | Plan L111: Unchanged PASS; allocation S06 matches slice-graph S06; lint line 3 dispositioned below. |
| AC-AFC-D5-04 | PASS | Plan L112: Unchanged PASS; allocation S06 matches slice-graph S06 (also required by S42). |
| AC-AFC-D5-05 | PASS | Plan L113: Unchanged PASS; S06/S06L/S11 split matches slice-graph (all three list D5-05) and design DES-AFC-D5 linking. |
| AC-AFC-D4-01 | PASS | Plan L119: Unchanged PASS; allocation S01 matches slice-graph S01; lint line 6 dispositioned below. |
| AC-AFC-D4-02 | PASS | Plan L120: Unchanged PASS; cited AC-AFC-CI-02 is a Phase 1 row; allocation S02 matches slice-graph S02. |
| AC-AFC-D4-03 | PASS | Plan L121: Unchanged PASS; allocation S03 matches slice-graph S03. |
| AC-AFC-D4-04 | PASS | Plan L122: Unchanged PASS; S11T/S11 match slice-graph (both list D4-04); cited D4-01..03 are Phase 1 rows. |
| AC-AFC-D4-05 | PASS | Plan L123: Unchanged PASS; S01/S02/S03/S11/S41 each list D4-05 in slice-graph. |
| AC-AFC-D4-06 | PASS | Plan L124: Unchanged PASS; S01/S02/S03/S11/S41 each list D4-06 in slice-graph. |
| AC-AFC-CI-01 *(amended)* | PASS | Plan L130: Areas correctly rescoped to spec/docs/hygiene per SD-023; S09T/S09 match slice-graph; design DES-AFC-GATE implements the three areas. |
| AC-AFC-CI-02 | PASS | Plan L131: Unchanged PASS; allocation S09T/S09 matches slice-graph; lint line 13 dispositioned below. |
| AC-AFC-CI-03 | PASS | Plan L132: Unchanged PASS; allocation S09T/S09 matches slice-graph; design names the rule IDs. |
| AC-AFC-CI-04 *(new)* | PASS | Plan L133: Spec-area behaviors (vendored lint, figure lint via `diagram.py lint`, byte-identical rebuild, template fallback) and docs-area failures (Vnv headings per SD-014, dangling relative links) are each test-observable; "figure lint" resolves via design DES-AFC-GATE/CONTRACT-AFC-SPECKIT; allocation S09T/S09 matches slice-graph. Two-area grouping follows register precedent (CI-02). |
| AC-AFC-SPEC-01 *(amended)* | PASS | Plan L134: D1-authoring hold correctly removed (D1 is P2-4); vendoring duty is inspection-observable; allocation S42 matches slice-graph and S42 write set; OD-AFC-09 source is an open integrated-review item, normal pre-review state (prior precedent: pending OD-AFC-07 at PASS). |
| AC-AFC-VNV-01 *(amended)* | PASS | Plan L135: Areas correctly narrowed to ci-cd/spec/developer-feedback per SD-023; allocation S07 matches slice-graph S07 and its stop condition. |
| AC-AFC-DX-01 | PASS | Plan L141: Unchanged PASS; Lifecycle-level allocation (dispatch/return records) matches slice-graph lifecycle list. |
| AC-AFC-DX-02 *(amended)* | PASS | Plan L142: "Fields of the issue #1 Scribe contract" resolves to `specialists/issue-1-body.md:116–124` ("Each observation records"); DX-001..DX-007 in scope-decision-batch.md; hygiene pass observable via S09; allocation S08 matches slice-graph S08 and its stop condition. |
| AC-AFC-PLAN-01 *(amended)* | PASS | Plan L148: Wave table assigns each of the 13 slices to exactly one wave; Wave 1 dispatches 5 (= impl_agent_cap), Wave 2 caps at five with serialization; Phase 2 table carries entry criteria + dependencies per step; milestone prohibition is the need (CHK-RE-09 permits); lint line 20 dispositioned below. |
| AC-AFC-PLAN-03 *(new)* | PASS | Plan L149: Receipt contents (D5/D4 merge commits, vendored commit, gate run per area, per-criterion status against the Phase 2 sequence entry criteria) are inspection-observable; Lifecycle-level allocation matches slice-graph lifecycle list. |
| AC-AFC-LAND-01 | PASS | Plan L155: Statement unchanged; Source narrowing (dropped plan-section pointer) leaves workspace-rule traceability intact; Lifecycle-level allocation fits. |
| AC-AFC-REV-01 | PASS | Plan L156: Unchanged PASS; Phase 1 Reverify N/A is stated in plan text below the rows; allocation matches Reviewer-packet records. |
| AC-AFC-PATH-01 | PASS | Plan L157: Unchanged PASS; allocation (planning + all Phase 1 slices; hygiene gate) matches entry criterion 2 and S09. |
| RISK-AFC-07 | PASS | Plan L167: Statement unchanged; Source/Risk rewordings preserve PROFILE-001 traceability and the frozen-settings control; allocation matches slice-graph lifecycle list. |
| RISK-AFC-08 | PASS | Plan L168: Unchanged PASS; gh_private_minutes is a Glossary quantity; allocation S09 matches slice-graph S09. |
| RISK-AFC-11 | PASS | Plan L169: Statement unchanged; Source correctly drops deferred AC-AFC-SEC-01 (no dangling trace); S09 + planning-scrub allocation matches entry criterion 2. |
| RISK-AFC-12 | PASS | Plan L170: Unchanged PASS; allocation S11 matches slice-graph S11; lint line 28 dispositioned below. |
| RISK-AFC-13 *(amended)* | PASS | Plan L171: Acquisition list correctly rescoped to Phase 1 (uv, Graphviz, pinned GridMarket source, pinned Actions); Gradle clause correctly removed with the product scope; self-citation removed from Source; allocation S06/S09 matches slice-graph (both carry CMD-SCAN); lint line 29 dispositioned below. |
| RISK-AFC-15 | PASS | Plan L172: Statement unchanged; OD-AFC-07 source and integrated-review disposition preserved; allocation S06 matches slice-graph S06. |
| RISK-AFC-16 *(amended)* | PASS | Plan L173: D1-wait/entry-receipt/no-revert/continue-model-work control is coherent across the Phase 1/2 boundary and inspection-observable via S06/S42 landing and PLAN-03; multi-clause form follows risk-register precedent. |

## Owner questions

None required by this gate. The RISK-AFC-17 repair re-anchors the trigger to defined plan events and changes no confirmed decision. Open OD-AFC items (including OD-AFC-09 cited by SPEC-01) remain for the integrated review; this verdict neither answers them nor accepts future outcomes as equivalent evidence.

## Decision coverage

uncovered: none. Sources resolve: SD-001..SD-024 (SD-013 superseded by SD-022, cited only as superseded), DEC-AFC-001/002/PROFILE-001, C1..C14, `#1 §Scribe contract` (issue-1-body.md:108), `#1 §Development setup` (issue-1-body.md:96), Glossary quantities skill_size_max/gh_private_minutes/impl_agent_cap/T_deadline. No register row cites a deferred ID and no allocation cites a milestone (both greps empty). Deferred-coverage check: all 52 f885e48 AC/RISK IDs not kept in Phase 1 expand from the §Deferred to Phase 2 ranges — missing: none (43 AC + 9 RISK verified by range expansion; DX-02's deferred parts noted alongside its kept row).

## Mechanical dispositions

| Evidence | Flag | Disposition |
|---|---|---|
| lint-p1.txt:3 | D5-03: `requirements system` | Retained from previous PASS: required non-trigger/handoff identity per SD-022/C10. |
| lint-p1.txt:6 | D4-01: `github` | Retained from previous PASS: SD-021 explicitly selects Actions; repo-agnostic capability supports it. |
| lint-p1.txt:13 | CI-02: `github` | Retained from previous PASS: SD-017/SD-021 explicitly select GitHub-hosted runners/Actions. |
| lint-p1.txt:20 | PLAN-01: `github` | Accepted: D3 milestones are GitHub milestones per SD-012 ("GitHub milestones in `1wgrumph/amazon-fantasy-companion`"); SD-023 fixes the Phase 1 prohibition. |
| lint-p1.txt:28 | RISK-AFC-12: `agy` | Retained from previous PASS: SD-021 requires the harness identity. |
| lint-p1.txt:29 | RISK-AFC-13: `github` | Accepted: pinned GitHub Actions are fixed by SD-017/SD-021 workflow rules. |

Planning-node position judged and accepted: the agnostic-term list targets vendor-neutral library standards; every flagged term names a platform fixed by confirmed owner scope (SD-017/SD-021/SD-022, SD-012). No finding.

## Method and limits

Applied Requirements Engineer 1.1.6 role and gate-report reference, plus Requirements Engineering authoring, NASA-adapted checklist CHK-RE-01..50, quality-gate and interface-completeness references. Inspection and analysis assess requirement quality; listed Verification methods were not executed. Typed failures: UNMEASURABLE + INCOMPLETE on RISK-AFC-17 only. Typed capability blocker: none.

Round applicability retained from receipt r2: CHK-RE-12's separate-register-layer form is N/A for these owner-designated Lifecycle-local Markdown rows. CHK-RE-06/07/21/22/23 permit the explicitly scoped process and D4/D5 duties and selected platforms. CHK-RE-15/16 multi-duty/multi-subject rows are accepted per register precedent (CI-02, RISK-07/11) where each duty is independently observable. Hardware-performance checks CHK-RE-34..36 are N/A (no performance claims; device scope deferred). Interface, maintainability, reliability, fault, continuity and flag checks are N/A on rows without those obligations. Sources and surrounding plan supply rationale/assumptions. Prospective V&V cases remain the later Test Engineer's work. This receipt authors no case, design or interface profile.

OCR: not applicable — requirement quality gate, not code review. Reverify: not applicable — no compiled-binary claim. These dispositions do not alter later frozen review/verification settings.

## Commands run

All commands were read-only except creation of this receipt. `PLAN` below denotes `docs/plans/2026-10-11-amazon-fantasy-companion`; paths are portable (`$HOME` never expanded into this file).

- Identity/status: `pwd`, `git status --short`, `git branch --show-current` (`plan/2026-10-11-amazon-fantasy-companion`), `git rev-parse HEAD` (`f885e48e58a6c10fa716b6c5ef048a71980a977a`).
- Evidence reads over requested skills/references, plan, design, scope-decision-batch, journey.json, prior receipt r2, placement receipt, slice-graph, issue-1-body, lint adapter/output.
- `sha256sum` over the technical plan, design.md and slice-graph (hashes in candidate_ref).
- `PYTHONDONTWRITEBYTECODE=1 python3 $PLAN/specialists/ac_mechanical_lint.py $HOME/alphazede/Alphazedehq/tools/coe/lint-sdoc.py $PLAN/amazon-fantasy-companion-technical-plan.md`: exit 0, byte-identical to supplied `ac-mechanical-lint-p1.txt`.
- `git show f885e48:$PLAN/amazon-fantasy-companion-technical-plan.md` + cell-by-cell old/new comparison of all 32 rows (22 unmarked statements byte-identical; 7 amended + 3 new as marked).
- Register-section greps for deferred-ID references and milestone references: both empty.
- Deferred-table range expansion over all 52 not-kept f885e48 IDs: uncovered none.

No commit, push, branch mutation or GitHub mutation ran. No check was retried without new evidence. No file besides this receipt was written; Alphazedehq was only read (lint constants).

## developer_feedback

- **RE-P1-OBS-001 — prompt/state note (no defect):** the packet states unmarked rows changed "except their Allocation column"; four rows also narrowed Source (LAND-01, RISK-AFC-07, RISK-AFC-11, RISK-AFC-15) and two reworded Risk rationale (RISK-AFC-07, RISK-AFC-15). All changes are correct (dangling-trace removal, milestone→Phase 1 rewording) and were re-checked. Future packets can say "statements unchanged; metadata re-scoped to Phase 1".
- **RE-P1-OBS-002 — new-row trigger hygiene:** RISK-AFC-17's slip trigger referenced targets that exist for Phase 1 exit only. When a new risk spans Phase 1/2, anchor each trigger event to a dated plan commitment or a defined sequence event before gating.
- Tools exercised: read-only shell/git, grep/sed/wc/sha256sum/diff, Python stdlib, installed lint adapter/constants. No product runtime, device, browser, OCR or Reverify execution.

Skipped: implementation, product/device V&V, external-rule refresh, plan edits and publication; these are outside this gate.
Remaining risk: the verdict establishes requirement quality only (after the one repair); realization and integrated owner acceptance remain pending.

---

## Round 2 (repair confirmation)

verdict: **PASS** — the applied RISK-AFC-17 statement equals the round-1 proposal verbatim; all other bytes (hence the other 31 rows) are identical to round 1.

candidate_ref: same base `f885e48e58a6c10fa716b6c5ef048a71980a977a`. Technical plan sha256 now: `b5adb9e7cb380c7c96673f341dfa379f51dd828ec750398ac7d0b0202b9a7f91` (round 1: `aee9f476bf659d32a20dead7e109ff95381e70fc89af79125e6790550a0a33af`).

changed_paths: `docs/plans/2026-10-11-amazon-fantasy-companion/specialists/requirements-engineer-receipt-p1.md` only (this Round 2 section appended; round-1 body untouched).

### Checks

1. Applied statement equals proposal: current plan L174 statement cell == round-1 proposed text, verified by exact string comparison (`STMT_MATCH: True`). Non-statement cells of the row identical old-vs-new (`NONSTMT_CELLS_IDENTICAL: True`).
2. Other 31 rows byte-identical: reconstructed the round-1 file (current file with L174 replaced by the diff's `<` line); its sha256 is `aee9f476bf659d32a20dead7e109ff95381e70fc89af79125e6790550a0a33af`, exactly the round-1 hash. Independent `diff` of reconstruction vs current is byte-identical to `specialists/re-p1-applied.diff` (single `174c174` hunk). No other row changed.
3. Mechanical lint re-run: exit 0; `RISK-AFC-17 OK`; `rows=32 flagged=6` — same row/flag counts as round 1. Full output below.

### Quoted evidence

Diff (`specialists/re-p1-applied.diff`, all 4 lines):

```text
174c174
< | RISK-AFC-17 *(new)* | If Phase 1 exit, the owner's spec review (P2-5) or the Phase 2 plan approval (P2-6) moves later than its target in §Program plan, then the Phase 2 plan shall state the remaining days to T_deadline and the live NFL windows still available, and shall present any scope reduction as an owner decision at the Phase 2 integrated review rather than cutting scope silently. | DEC-AFC-SD-023, T_deadline, #1 §Development setup | inspection | Phase 2 entry receipt; Phase 2 plan | Spec-first moves product implementation later; the deadline is fixed. Moving all product slices out of Phase 1 also drops the f885e48 plan to capture ESPN fixtures from the Monday 2026-10-12 US game. | Requirements and model work start at approval in parallel with Phase 1; the Phase 2 plan re-plans spikes and fixture capture against the remaining windows (Thu 10-15, Sun 10-18, Mon 10-19, Thu 10-22 US time); owner decides cuts. |
---
> | RISK-AFC-17 *(new)* | When the Phase 2 plan is approved (P2-6), it shall state the remaining days to T_deadline and the live NFL windows still available, and shall present any scope reduction as an owner decision at the Phase 2 integrated review rather than cutting scope silently. | DEC-AFC-SD-023, T_deadline, #1 §Development setup | inspection | Phase 2 entry receipt; Phase 2 plan | Spec-first moves product implementation later; the deadline is fixed. Moving all product slices out of Phase 1 also drops the f885e48 plan to capture ESPN fixtures from the Monday 2026-10-12 US game. | Requirements and model work start at approval in parallel with Phase 1; the Phase 2 plan re-plans spikes and fixture capture against the remaining windows (Thu 10-15, Sun 10-18, Mon 10-19, Thu 10-22 US time); owner decides cuts. |
```

Lint (RISK-AFC-17 line + rows line; exit 0):

```text
RISK-AFC-17 OK
rows=32 flagged=6
```

### Commands run (round 2)

`PLAN` below denotes `docs/plans/2026-10-11-amazon-fantasy-companion`; paths are portable (`$HOME` never expanded into this file).

- `sha256sum $PLAN/amazon-fantasy-companion-technical-plan.md` → `b5adb9e7…9a7f91`; `git status --short`, `git rev-parse HEAD` (`f885e48e58a6c10fa716b6c5ef048a71980a977a`), `git branch --show-current`.
- `sed -n '174p'`, `grep -n 'RISK-AFC-17'` (L174 row + L315 deferred-table citation, the latter out of the register).
- Python stdlib: statement-cell equality vs proposal; non-statement-cell equality; round-1 reconstruction + `sha256sum` → `aee9f476…0a33af` (matches round-1 hash).
- `diff` reconstruction vs current → identical to `re-p1-applied.diff`.
- `PYTHONDONTWRITEBYTECODE=1 python3 $PLAN/specialists/ac_mechanical_lint.py $HOME/alphazede/Alphazedehq/tools/coe/lint-sdoc.py $PLAN/amazon-fantasy-companion-technical-plan.md` → exit 0, `RISK-AFC-17 OK`, `rows=32 flagged=6`.

No commit, push, branch mutation or GitHub mutation ran. No file besides this receipt was written.

### developer_feedback (round 2)

- Round-2 packet was exactly verifiable: one-line diff file + stated round-1 hash enabled a byte-level reconstruction proof. Keep this shape for future repair confirmations.
- Tools exercised: read-only shell/git, grep/sed/sha256sum/diff, Python stdlib, installed lint adapter/constants. No product runtime, device, browser, OCR or Reverify execution.

Round-2 skipped: re-gating of the 31 PASS rows' requirement quality (byte-identical to round 1, proof above); implementation, product/device V&V, plan edits and publication.

