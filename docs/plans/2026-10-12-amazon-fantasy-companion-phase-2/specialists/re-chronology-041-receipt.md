# RE chronology 041 receipt

verdict: REPAIRABLE_FAILURE
candidate_ref: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/amazon-fantasy-companion-phase-2-technical-plan.md`
candidate_sha256: `17ae87e55873b5c91b14015a13d9cd1884825b8f6f2d081135c66ab106711b90`
before_ref: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/chronology-profile-delta/technical-plan.before.txt`
before_sha256: `6a2520ea8e235b1c21210b801bb2570803678ec013123935b7d9ea8e752a5464`
lint: `lint-sdoc.py --profile library` on `requirements-register.md` — exit 0, empty stdout, empty stderr. INAPPLICABLE_TO_MARKDOWN. Not a semantic PASS.
blocker: AC-AFC-P2-MS-01 current text. One `requires_regate` correction. REL-02 and RISK-13 stay closed on this re-gate. DX-02 is `exact_text` and already applied.

S8 rows cited, no invented clauses: `SRC-EMV-NASA-SEH` (full-text; Appendix C paraphrased only), `SRC-EMV-COE` (full-text; index-pin versus ELSD digest mismatch remains as recorded in the standards receipt), `SRC-EMV-29148` (metadata-only). IFACE-PROFILE-EMV-001: NOT_APPLICABLE. These four rows are lifecycle acceptance or schedule-risk controls, not interface obligations.

OCR: not run. This is a semantic requirements gate, not an independent code review. Reverify: not applicable — planning sources only. BRAN: unavailable (no `.bran/policy.yaml`). BUG_ROUTE: not-a-bug. Prior receipts were not edited. Review 1/1 and repair 1/1 stay spent.

## AC-AFC-P2-MS-01 — FAIL

- finding_type: `requires_regate`
- checklist: CHK-RE-13 (AMBIGUOUS). Same cause also fails CHK-RE-30 (INCORRECT) and CHK-RE-48 (NO_PASS_FAIL).
- evidence: The statement correctly names GitHub milestones M01..M13, then says the description's slice list equals "the approved milestone table". The plan now has two tables. `Technical waves and release checkpoints (W1..W5)` keeps the former M1..M5 due times and the Slices column. `GitHub milestones in order (D3; create only after approval)` has thirteen rows M01..M13 and the column Issues in order. A field-for-field `gh api` readback can bind either table, so pass and fail are not unique, and "slice list" is not the agreed 13-row column. Source, verification, and allocation cells are unchanged and still valid. W1..W5 dues and slice lists equal former M1..M5, so this failure is the table pointer, not a deadline or scope change.
- exact corrected statement:

```text
After the owner approves this package, the program shall create GitHub milestones M01..M13 in `1wgrumph/amazon-fantasy-companion` whose title, due date (calendar date; the UTC due time is stated in the description) and description (entry criteria, exit criteria, issues in order) equal the approved table `GitHub milestones in order (D3; create only after approval)`, and shall record a `gh api` readback that matches it field for field; no milestone is created before approval.
```

Return this statement for one re-gate. Do not treat it as closed.

## Gate table

| UID | Disposition | finding_type | Open |
| --- | --- | --- | --- |
| AC-AFC-P2-MS-01 | FAIL | requires_regate | yes |
| AC-AFC-P2-REL-02 | PASS | requires_regate | no |
| RISK-AFC-P2-13 | PASS | requires_regate | no |
| AC-AFC-P2-DX-02 | PASS | exact_text | no |

## PASS table

| UID | PASS | note |
| --- | --- | --- |
| AC-AFC-P2-REL-02 | PASS | W1..W5 dues and slices equal former M1..M5; allocation stays P2-R1..P2-R5; release duty otherwise unchanged; no release at each of M01..M13. |
| RISK-AFC-P2-13 | PASS | 12 h trigger stays on W1..W5 dues, which equal former M1..M5; §Program plan priority order unchanged; earlier M01..M13 dues are not this control. |
| AC-AFC-P2-DX-02 | PASS | `exact_text`: only M5 became W5. W5 due 2026-10-23T12:00:00Z equals former M5. P2-SCR1 and the feedback obligation are unchanged. Candidate text is the canonical replacement. No re-gate. |

## Before / after

Confirmed against `technical-plan.before.txt`. Only the statement cell changed on each row.

| UID | Before token | After token |
| --- | --- | --- |
| AC-AFC-P2-REL-02 | At each milestone exit | At each technical-wave release checkpoint W1..W5 |
| AC-AFC-P2-MS-01 | M1..M5 | M01..M13; "slice list" and "the approved milestone table" were not updated |
| AC-AFC-P2-DX-02 | Before M5 exit | Before W5 exit |
| RISK-AFC-P2-13 | If a milestone exit | If a technical-wave release checkpoint W1..W5 |

DX-02 canonical replacement, already in the candidate:

```text
Before W5 exit the Scribe shall assemble, from `docs/developer-feedback/observations.md`, a per-tool Product Feedback file (used for, what worked well, what needs work, onboarding from zero to hello world, would build again Yes/No and why, AWS services used and how), optional Feature Requests with priority Critical / Important / Nice-to-have, and a sanitized Friction Log with the Devpost entry fields, covering every tool, API, SDK and device used in Phase 2, with no credentials, account details or local paths, and shall check the Product Feedback file and the Friction Log against the official rules current at submission.
```

## Precheck and lint

Register precheck receipt `evidence/chronology-profile-delta/register-precheck.json` says PASS. It was not trusted on its path. The live plan sha256 equals the receipt (`17ae87e55873b5c91b14015a13d9cd1884825b8f6f2d081135c66ab106711b90`). The installed 1.1.7 `hooks/register-precheck.cjs` sha256 equals the receipt (`ab1d06e0cf36d89a276616deaa85e53b60ab76fa577d27cbec95745d3c2b05d5`).

A read-only replay of pure `checkRegister` (the writer in `precheck_markdown.py` was not run) returned outcome PASS and zero findings. The adapter binds 66 register rows verbatim to `rows.json`: 63 active in-memory `[REQUIREMENT]` blocks, each with original UID, statement, rationale, verification, allocation, and sources, actual SEIT case IDs, and `DEC-AFC-APPROVAL-ST5`. Withdrawn `AFC-PR-049`, `AFC-PR-050`, and `AFC-PR-051` stay in `rows.json` and are excluded from the blocks. Duplicate UID and missing UID are rejected. An empty verification method returns class `verification`. No `.sdoc` was written. The plan contains no `file:line` citations, so the adapter loaded zero cited files. Covered mechanical classes were not re-reported.

Separate lint: `python3` on Alphazedehq `tools/coe/lint-sdoc.py --profile library` against `requirements-register.md` exited 0 with no stdout and no stderr. The register contains zero `[REQUIREMENT]` nodes and zero `[DOCUMENT]` nodes. Record INAPPLICABLE_TO_MARKDOWN. DEC-AFC-SD-027 keeps Markdown as register authority. This gate does not treat that exit 0 as semantic PASS.

## Coverage and limits

Product register coverage preserved: 63 active + 3 withdrawn. The four local rows are not register UIDs. `uncovered: none` inside this four-row gate. DEC-AFC-SD-040 authorizes the 13-milestone count without changing W1..W5 dues or slice lists. DEC-AFC-SD-041 is the profile decision and is outside these four statements.

Owner questions: none.

Commands: plan/plugin sha256 compare; register row count; read-only `checkRegister` replay plus the two negative parser cases and the empty-verification case; `lint-sdoc.py --profile library` as above. Checklist sidecar: `evidence/chronology-profile-delta/re-checklist.json` (50 checks × 4). Findings: `evidence/chronology-profile-delta/re-findings.json`.

Not done: no edit to the technical plan, design, SEIT, or implementation; no whole-package re-gate; no OCR; no proof that the 13-row issue grouping matches every dependency in `proposal.json`; no second RE round.
