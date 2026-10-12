ROLE
Reviewer (BEARING_ROLE=reviewer), Lifecycle AFC-2026-10-11, slice S07, review unit = its own integration step (OA-AFC-A3). Load bearing-lite reviewer skill (your skills dir). You did not author this change.

STATE
Candidate: PR https://github.com/1wgrumph/amazon-fantasy-companion/pull/3, branch afc/s07-vnv-tree, head ac0638d946c2b8f508ff3b2ebb533e61bccd4894, base 99d59ae (main). Worktree (cwd): the S07 worktree. Plan (read-only): $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/ — requirement AC-AFC-VNV-01, AC-AFC-PATH-01, design DES-AFC-VNV, seit.json proof rows SEIT-AFC-VNV-01 and SEIT-AFC-PATH-01.P.

OBJECTIVE
Independently review the exact candidate for introduced actionable defects against the requirement, design and the vnv-review skill's guidance-tree contract ($HOME/.claude/skills/vnv-review/SKILL.md: docs/vnv/AGENTS.md index, per-lane AGENTS.md with Scope, Tools, Review Focus, findings target; tools lists must be concrete, never generic). Re-run CMD-VNV-CHECK and CMD-PATH-SCAN-PLAN yourself (commands in seit.json). Verified findings only.

REQUIRED CAPABILITIES
- OCR delegate mode, required: `ocr delegate preview --from 99d59ae --to ac0638d`, then `ocr delegate rule <every listed file>`; per-file OCR section. Tool failure = typed gap with exact error, never PASS.
- Reverify: not applicable — no compiled binary.

AUTHORITY
Read-only. Write only your review file at $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S07-review-result.md. No commits, no PR comments, no merge.

RETURN
Verdict PASS | REPAIR_REQUIRED (fixable finding ⇒ REPAIR_REQUIRED), findings table (ID, P0-P3, file:line, defect, exact fix), re-run command exit codes, OCR section, Reverify line, route used, developer_feedback (AC-AFC-DX-04 fields or "no new observations" + tools).

STOP
After the review.
