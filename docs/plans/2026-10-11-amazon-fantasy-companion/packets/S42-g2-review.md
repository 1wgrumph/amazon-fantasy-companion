ROLE
Reviewer (BEARING_ROLE=reviewer), Lifecycle AFC-2026-10-11, slice S42 generation 2 (re-vendor after SD-034). RESPONSIBILITY: independent review of one exact candidate for introduced actionable defects. Load the bearing-lite reviewer skill. You did not author this change.

STATE
FACTS: Candidate https://github.com/1wgrumph/amazon-fantasy-companion/pull/11, branch afc/s42-revendor-prose, head 579b9519d5c2e5a92b208112768cb4654d114798, base 5e59270b8320d6085039f26b64f14897736845f6. Worktree (cwd) $HOME/alphazede/worktrees/amazon-fantasy-companion-s42. Read-only plan: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/ — slice S42 in implementation.json, CMD-SPEC-VENDOR and CMD-PATH-SCAN-PLAN in seit.json; packet packets/S42-g2.md; receipt evidence/S42/verify-g2.md.
Source: Alphazedehq main checkout $HOME/alphazede/Alphazedehq at c24e4a36131c03dcda283b5431990cf14e603e68 (PR #309, spec-authoring prose sections).
ASSUMPTIONS to check: tools/spec equals the c24e4a3 skill scripts+template exactly; VENDORED.md pins c24e4a3 and its tree id; THIRD_PARTY_NOTICES.md unchanged is correct; reported exit codes reproduce.

OBJECTIVE
Verdict on the candidate. Re-run CMD-SPEC-VENDOR (with <azhq_d5_sha>=c24e4a36131c03dcda283b5431990cf14e603e68, <alphazedehq_checkout>=$HOME/alphazede/Alphazedehq) and CMD-PATH-SCAN-PLAN yourself.

REQUIRED CAPABILITIES
OCR delegate mode, required: `ocr delegate preview --from 5e59270b8320d6085039f26b64f14897736845f6 --to 579b9519d5c2e5a92b208112768cb4654d114798`, then `ocr delegate rule <every listed file>`; per-file OCR section; tool failure = typed gap with exact error. Reverify: not applicable — no compiled binary.

AUTHORITY
Read-only. Write only $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S42-g2-review-result.md. No commits, PR comments or merges. Other agents work concurrently in other worktrees.

RETURN
Verdict PASS | REPAIR_REQUIRED (any fixable finding => REPAIR_REQUIRED), findings table (ID, P0-P3, file:line, defect, exact fix), re-run exit codes, OCR section, Reverify line, route used, developer_feedback (AC-AFC-DX-04 fields or "no new observations" + tools).

STOP
After the review.
