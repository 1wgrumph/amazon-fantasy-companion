# RE chronology 041 re-gate receipt

verdict: PASS
candidate_ref: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/amazon-fantasy-companion-phase-2-technical-plan.md`
candidate_sha256: `1c33c214324bbb6f7c6a31ee460eff3e5697516b27792a694000cf1669d2bc0f`
prior_candidate_sha256: `17ae87e55873b5c91b14015a13d9cd1884825b8f6f2d081135c66ab106711b90`
statement_sha256: `4cc077534ce4d29ab599c0d0c4e2ee5174e6759797012cd86e6e01e40f6507b2`
scope: `AC-AFC-P2-MS-01` only
lint: `lint-sdoc.py --profile library` on `requirements-register.md` — exit 0, empty stdout, empty stderr. INAPPLICABLE_TO_MARKDOWN. Not a semantic PASS.
blocker: none
correction_rounds: 2, not incremented. No third re-gate.

S8 rows cited, no invented clauses: `SRC-EMV-NASA-SEH` (full-text; Appendix C paraphrased only), `SRC-EMV-COE` (full-text; index-pin versus ELSD digest mismatch remains as recorded in the standards receipt), `SRC-EMV-29148` (metadata-only). IFACE-PROFILE-EMV-001: NOT_APPLICABLE. This row is a lifecycle acceptance control, not an interface obligation.

OCR: not run. This is a semantic requirements gate, not an independent code review. Reverify: not applicable — planning sources only. BRAN: unavailable (no `.bran/policy.yaml`). BUG_ROUTE: not-a-bug. Prior independent review 1/1 and repair 1/1 stay spent. REL-02 and RISK-13 stay closed on the prior pass. DX-02 stays `exact_text`.

## Gate table

| UID | Disposition | finding_type | Open |
| --- | --- | --- | --- |
| AC-AFC-P2-MS-01 | PASS | requires_regate | no |

Not re-gated: `AC-AFC-P2-REL-02` (prior PASS), `RISK-AFC-P2-13` (prior PASS), `AC-AFC-P2-DX-02` (`exact_text`).

## PASS table

| UID | PASS | note |
| --- | --- | --- |
| AC-AFC-P2-MS-01 | PASS | Applied text equals the prior `corrected_text` verbatim. The statement names `GitHub milestones in order (D3; create only after approval)`, which is one heading, with 13 data rows M01..M13 and column Issues in order. Pass is title, calendar date from Due (UTC), description (entry criteria, exit criteria, issues in order, UTC time stated with the due date), and a field-for-field `gh api` readback, and no milestone before approval. Fail is any mismatch. W1..W5 is not the target. |

Owner questions: none.

uncovered: none

## Precheck and lint

`evidence/chronology-profile-delta/register-precheck.json` says PASS for this candidate. Rechecked, not trusted on its path. Live plan sha256 equals the receipt (`1c33c214324bbb6f7c6a31ee460eff3e5697516b27792a694000cf1669d2bc0f`). Installed 1.1.7 `hooks/register-precheck.cjs` sha256 equals the receipt (`ab1d06e0cf36d89a276616deaa85e53b60ab76fa577d27cbec95745d3c2b05d5`).

A read-only replay of pure `checkRegister` (the writer in `precheck_markdown.py` was not run) returned outcome PASS and zero findings. The adapter binds 66 register rows verbatim: 63 active in-memory `[REQUIREMENT]` blocks, each with original UID, statement, rationale, verification, allocation, and sources, actual SEIT case IDs, and `DEC-AFC-APPROVAL-ST5`. Withdrawn `AFC-PR-049`, `AFC-PR-050`, and `AFC-PR-051` stay out of the blocks. Duplicate UID and missing UID are rejected. An empty verification method returns class `verification`. Cited files loaded: 0. No `.sdoc` was written. `rows.json` still equals the live register (66 rows). DEC-AFC-SD-027 keeps Markdown as register authority. Covered mechanical classes were not re-reported.

Separate lint: `python3` on Alphazedehq `tools/coe/lint-sdoc.py --profile library` against `requirements-register.md` exited 0 with no stdout and no stderr. The register contains zero `[REQUIREMENT]` nodes and zero `[DOCUMENT]` nodes. Record INAPPLICABLE_TO_MARKDOWN. This gate does not treat that exit 0 as semantic PASS.

## Delta binding

`re-correction-input.json` holds 103 rows (66 register + 37 local) before and after. The only text change is `AC-AFC-P2-MS-01`. No non-text field changed. Its source, verification, and allocation stay `SD-012 (D3); DEC-AFC-SD-023 (P2-7)`, `inspection`, and `P2-L01`. Outgoing references are empty. `known_uids` equals the 85 keys in `re-known-reference-sources.json`. No after-snapshot reference is dangling.

`re-correction-result.json` is `REQUIRES_REGATE`, changed and named `{AC-AFC-P2-MS-01}`, cross_references PASS, `correction_rounds` 2. Attempt 1 is `invalid_input_file`. Attempt 2 is `unresolved_reference` before those known Phase 1 targets were supplied. This re-gate does not spend another round.

Since the prior candidate, the plan diff is the MS-01 statement plus the M09 exit cell `M3 backend head` to `Wave 3 backend head`. That cell is outside governed rows. It does not change a requirement statement, a W1..W5 due, or the 13-row issue lists. W1..W5 dues equal former M1..M5 dues, including the W2 `T_yahoo + 6 h` qualifier.

## developer_feedback

no new observations. Tools exercised: Python 3 (hash, snapshot compare, table extract), Node `checkRegister` from Bearing Lite 1.1.7 (read-only), `lint-sdoc.py --profile library` (read-only).
