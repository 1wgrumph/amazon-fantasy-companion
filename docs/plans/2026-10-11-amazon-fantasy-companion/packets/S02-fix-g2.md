ROLE
Product Implementer (BEARING_ROLE=implementer), Lifecycle AFC-2026-10-11, slice S02 post-merge integration-defect fix, generation 2. RESPONSIBILITY: make the merged setup-a-repo skill match the shared gate contract and the plan's workflow-check command.

STATE
FACTS:
- Dispatch record (in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json execution_receipts; local, not yet on main): lease_id S02-fix-g2; repository alphazede/Alphazedehq; worktree $HOME/alphazede/worktrees/alphazedehq-afc-s02-fix; branch afc/s02-fix-gate-area; base ac47f0eca149eb281e41a6bdd9d490221c7a14cf (full SHA); evidence_dir docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S02-fix/ (write receipts in the planning worktree); lease alphazedehq-skills/setup-a-repo; authority AUTH-AFC-2026-10-11-002; package digest a018168f575741b5f53bbe7fac4bcb13128e31f37f69d73ba2433cf8d09d5144.
- Defect 1 (found by S09T): skills/setup-a-repo templates/ci.yml calls `gate.sh --area <area>`; the merged setup-pre-commit gate takes the area positionally (`gate.sh <area>`, CONTRACT-AFC-GATE in the plan's design.md) and exits 2 on --area. Your g1 discovery: two template calls and two test fixtures use --area.
- Defect 2 (found by S09): skills/setup-a-repo/scripts/check-workflows.py passes a single workflow file but exits 1 on a directory ("unreadable, malformed or unsupported workflow structure"); the plan's CMD-WORKFLOW-CHECK and S09T's tests call it with a directory (.github/workflows/).
- Plan (read-only): $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/ (design.md CONTRACT-AFC-GATE, seit.json CMD-WORKFLOW-CHECK). S09 return: evidence/S09/return.json.
ASSUMPTIONS to check: nothing else in setup-a-repo depends on --area or on file-only input.
Other agents work in other worktrees concurrently.

OBJECTIVE
Fix both defects in skills/setup-a-repo: positional gate area everywhere (template + fixtures); check-workflows.py accepts a directory (checks every *.yml/*.yaml in it; empty directory is a failure) as well as a file. Add negative tests for both (template using --area fails; directory containing one bad workflow fails; directory of good workflows passes). Keep the skill lean (stock size test). Commit, push, open ONE draft PR.

AUTHORITY
Allowed writes: skills/setup-a-repo/** and the evidence_dir. Commit (author from env; never Co-Authored-By); push the branch; draft PR. Prohibited: other paths, merge, force-push.

LOOP
Fix, test, classify failures, retry only with new evidence.

VERIFY
`python3 -m unittest discover -s skills/setup-a-repo/tests -v` exit 0; `! git grep -n -- '--area' skills/setup-a-repo`; `python3 skills/setup-a-repo/scripts/check-workflows.py skills/setup-a-repo/templates` exit 0; `bash tools/ci/local-gates.sh` exit 0.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE; lease_id; head SHA; PR URL; diff summary; command exit codes and output tails; developer_feedback (AC-AFC-DX-04 fields or "no new observations" + tools).

STOP
After the PR is open with all VERIFY passing, or a failure outside the write set.
