ROLE
Reviewer (BEARING_ROLE=reviewer), Lifecycle AFC-2026-10-11, slice S06, review unit = its own integration step (OA-AFC-A3). RESPONSIBILITY: independent review of one exact candidate for introduced actionable defects. Load the bearing-lite reviewer skill. You did not author this change.

STATE
FACTS: Candidate https://github.com/alphazede/Alphazedehq/pull/305 and https://github.com/alphazede/requirements-system/pull/532 (head b30391948cd7084680fbf135c36f44e94ced564a, base c1e07c92c630ae1a5aa50a19d34d3f625adeb2ad, worktree $HOME/alphazede/worktrees/requirements-system-afc-s06; run OCR on that range too), head 2b19eb757350b960575c70a6a7c0d49530e5e2f5, base 47c46f2e16fed060482a1bf3a0e34ddcb9bc57fc (Alphazedehq origin/main at creation). Worktree (cwd): $HOME/alphazede/worktrees/alphazedehq-afc-s06-spec-authoring. Implementer flagged RISK-13.D partial: uv/Graphviz historical scan receipts missing. Judge whether that is a real defect for this slice (note: scan-software-supply-chain does not apply to an unchanged installed local tool merely being invoked). Read-only plan: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/ — slice S06 in implementation.json (requirements, design, command_ids, seit_proof_rows), seit.json commands. Implementer receipt: evidence/S06/g4/.
ASSUMPTIONS to check: reported exit codes reproduce.

OBJECTIVE
Verdict on the candidate against its requirements and design; lean, repo-agnostic, follows Alphazedehq stock skill-test pattern (skills/release-process/tests/); negative tests exist for each bypass. Re-run every slice VERIFY command yourself with <base>=47c46f2e16fed060482a1bf3a0e34ddcb9bc57fc.

REQUIRED CAPABILITIES
OCR delegate mode, required: `ocr delegate preview --from 47c46f2e16fed060482a1bf3a0e34ddcb9bc57fc --to 2b19eb757350b960575c70a6a7c0d49530e5e2f5`, then `ocr delegate rule <every listed file>`; per-file OCR section; tool failure = typed gap with exact error. Reverify: not applicable — no compiled binary.

AUTHORITY
Read-only. Write only $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S06-review-result.md. No commits, PR comments or merges. Other agents may work concurrently in other worktrees.

RETURN
Verdict PASS | REPAIR_REQUIRED (any fixable finding ⇒ REPAIR_REQUIRED), findings table (ID, P0-P3, file:line, defect, exact fix), re-run command exit codes, OCR section, Reverify line, route used, developer_feedback (AC-AFC-DX-04 fields or "no new observations" + tools).

STOP
After the review.
