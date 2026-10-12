ROLE
Product Implementer (BEARING_ROLE=implementer), Lifecycle AFC-2026-10-11, slice S06 repair round (the one repair allowed after review; deterministic verification decides, no re-review). RESPONSIBILITY: fix exactly the named gate finding on this candidate.

STATE
FACTS: Candidate PR https://github.com/alphazede/Alphazedehq/pull/305, head 2b19eb757350b960575c70a6a7c0d49530e5e2f5, worktree (cwd) $HOME/alphazede/worktrees/alphazedehq-afc-s06-spec-authoring. Independent review: PASS. Alphazedehq local gates (`bash tools/ci/local-gates.sh`) on this head fail: standards-yaml: skills/spec-authoring/agents/openai.yaml: interface.default_prompt is missing or blank (compare other skills' agents/openai.yaml).
ASSUMPTIONS to check: no other gate fails after the fix.

OBJECTIVE
Fix that finding inside the slice's existing write set, commit, push to the same branch (no force-push), and get `bash tools/ci/local-gates.sh` to exit 0 on the new head. Re-run the slice's VERIFY commands from its g4 packet ($HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S06-g4.md) on the new head.

AUTHORITY
Allowed: the slice's write set only (see its g4 packet); commit (author from env; never Co-Authored-By); push the branch. Prohibited: merging, force-push, other paths, behavior changes beyond the finding. Other agents work concurrently in other worktrees.

LOOP
Fix, run local-gates; if a new failure appears, classify it; fix only if it is in the write set and caused by this slice; otherwise stop.

VERIFY
`bash tools/ci/local-gates.sh` exit 0 with a merge receipt line; slice VERIFY commands exit 0.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE | ENVIRONMENT_FAILURE; new head SHA; diff summary; gate output tail; VERIFY exit codes; developer_feedback (AC-AFC-DX-04 fields or "no new observations" + tools).

STOP
After the gates pass or a failure outside the write set.
