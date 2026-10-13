ROLE
Product Implementer (BEARING_ROLE=implementer), Lifecycle AFC-2026-10-11, slice S02 integration-defect fix. RESPONSIBILITY: make the merged setup-a-repo CI template call the shared gate in the contract form.

STATE
FACTS: setup-a-repo (merged #303) templates/ci.yml runs `gate.sh --area <area>`; the merged setup-pre-commit gate (#306, CONTRACT-AFC-GATE in the plan design.md) takes the area positionally (`gate.sh <area>`) and rejects --area with exit 2 (found by S09T). Worktree (cwd) $HOME/alphazede/worktrees/alphazedehq-afc-s02-fix, branch afc/s02-fix-gate-area, base ac47f0eca149eb281e41a6bdd9d490221c7a14cf. Plan (read-only): $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/ (design.md CONTRACT-AFC-GATE).
ASSUMPTIONS to check: no other file in setup-a-repo uses --area.

OBJECTIVE
Change every `gate.sh --area <x>` in skills/setup-a-repo/ to `gate.sh <x>`, add a negative test in skills/setup-a-repo/tests/ that fails if the template uses --area, run the skill's tests + check-workflows, commit, push, open ONE draft PR.

AUTHORITY
Allowed writes: skills/setup-a-repo/** only. Commit (author from env; never Co-Authored-By); push branch; draft PR. Prohibited: other paths, merge, force-push.

VERIFY
`python3 -m unittest discover -s skills/setup-a-repo/tests -v` exit 0; `git grep -n -- '--area' skills/setup-a-repo` no output; `bash tools/ci/local-gates.sh` exit 0.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE; head SHA; PR URL; diff summary; command exit codes; developer_feedback (AC-AFC-DX-04 fields or "no new observations" + tools).

STOP
After the PR is open with all VERIFY passing.
