ROLE
Light Implementer (BEARING_ROLE=light_implementer), spec track ST-4 repair, generation 2. RESPONSIBILITY: fix one review finding mechanically.

STATE
FACTS: Dispatch record lease_id ST-4-g2 in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json. Worktree (cwd) $HOME/alphazede/worktrees/amazon-fantasy-companion-st4, branch afc/st4-spec, head b39553be846d7905ea4f0b0028082d6979cab402 (PR #10). Review: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/ST-4-review-result.md finding F1: docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/verification.txt:39-40 claims 96 authorized files / 96 changed paths; the committed candidate has 97 of each.

OBJECTIVE
Re-run the coverage/file-count check the implementer used (see that evidence directory), update verification.txt so its counts match the actual committed candidate, commit, push (no force-push).

AUTHORITY
Allowed writes: docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/** only. Prohibited: spec content, other paths, merge, force-push.

VERIFY
`git diff --name-only 5e59270b8320d6085039f26b64f14897736845f6..HEAD | wc -l` equals the count now stated; the spec build still byte-identical (rerun the build command from the evidence).

RETURN
PASS | REPAIRABLE_FAILURE; head SHA; diff; command outputs; developer_feedback ("no new observations" + tools if none).

STOP
After push.
