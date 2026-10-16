ROLE
Reviewer (BEARING_ROLE=reviewer), Lifecycle AFC-2026-10-11, review unit = the S09T + S09 pair (repo gate, local checkers, git hooks, Actions workflow). RESPONSIBILITY: independent review of one exact candidate for introduced actionable defects. Load the bearing-lite reviewer skill. You did not author this change.

STATE
FACTS:
- Candidate: https://github.com/1wgrumph/amazon-fantasy-companion/pull/9, branch afc/s09t-gate-tests, head be366cc2612edfa56ef20ff018a35bd12d95f3af, base 5e59270b8320d6085039f26b64f14897736845f6 (origin/main has since moved to d259c16 with tools/spec-only changes). Worktree (cwd) $HOME/alphazede/worktrees/amazon-fantasy-companion-s09 (local branch afc/s09-gate, same head).
- Read-only plan: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/ — slices S09T and S09 in implementation.json; seit.json commands CMD-RED, CMD-SCAN, CMD-GATE-HYGIENE, CMD-GATE-DOCS, CMD-GATE-SPEC, CMD-WORKFLOW-CHECK, CMD-GATE-ALL, CMD-PR-CHECKS, CMD-CI-VENDOR-PIN, CMD-COVERAGE-CI, CMD-MUTATION-CI and proof rows listed for both slices; implementer receipts evidence/S09T/g1..g4 and evidence/S09/g3, g4, g6 (g6 return.json is the final author receipt, with the coverage environment in evidence/S09/g3/coverage-command.json).
- Incident history (Orchestrator-observed): before be366cc, running the gate from .githooks/pre-commit and pre-push leaked the hook's GIT_INDEX_FILE/GIT_DIR into test fixtures, which committed "fixture" commits into the real repository. Fixed by gate.sh unsetting inherited git location variables; regression test tools/ci/tests/test_gate_isolation.py. core.hooksPath is UNSET in the shared repo config on purpose until this lands; do not set it there (you may set it in a throwaway clone).
- Known plan-command defect (Orchestrator-recorded, not a slice defect): CMD-COVERAGE-CI `--exclude tools/ci/check_workflows.py` does not match in diff-cover 9.7.2; the vendored checker is counted, which is stricter.
- Not yet run by the author: CMD-MUTATION-CI; CMD-PR-CHECKS (Actions run 38251512127 started on this head); Actions budget readback (PROC-ACTIONS-BUDGET); shell coverage is TOOL_MISSING (kcov absent).
ASSUMPTIONS to check: author exit codes reproduce; the hooks really call the gate as `bash tools/ci/gate.sh --changed`; the workflow passes the vendored checker; no secrets or absolute home paths in tracked files.

OBJECTIVE
Verdict on the candidate against S09T and S09 requirements, design and proof rows. Re-run every listed command yourself (substitute <evidence_dir> = $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S09/review/), including CMD-MUTATION-CI and CMD-PR-CHECKS (wait for the Actions run to finish; report each job). Also exercise the hooks automatically (not with --no-verify) in a throwaway clone with core.hooksPath=.githooks set in that clone only, and confirm a commit and a push to a local bare remote leave no extra commits and an intact index.

REQUIRED CAPABILITIES
OCR delegate mode, required: `ocr delegate preview --from 5e59270b8320d6085039f26b64f14897736845f6 --to be366cc2612edfa56ef20ff018a35bd12d95f3af`, then `ocr delegate rule <every listed file>`; per-file OCR section; tool failure = typed gap with exact error. Reverify: not applicable — no compiled binary.

AUTHORITY
Read-only on the repository. Write only $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S09-pair-review-result.md and the evidence dir above. Mutation runs must leave `git diff` clean. No commits, pushes, PR comments, merges, git config changes in the shared repo. Other agents work concurrently in other worktrees.

RETURN
Verdict PASS | REPAIR_REQUIRED (any fixable finding => REPAIR_REQUIRED), findings table (ID, P0-P3, file:line, defect, exact fix, product vs test-only), re-run exit codes per command, proof-row status, OCR section, Reverify line, route used, developer_feedback (AC-AFC-DX-04 fields or "no new observations" + tools).

STOP
After the review.
