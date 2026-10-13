ROLE
Test Implementer (BEARING_ROLE=test_implementer), Lifecycle AFC-2026-10-11, defects B2a (gate test fixture excludes linked documents) and B2b (spec gate compares rebuilt output with HEAD instead of the staged index), bug-triager route per DEC-AFC-SD-037. RESPONSIBILITY: fix the test-only defect B2a and add the red regression for B2b. Not gate.sh.
BUG_ROUTE: bug-triager test_implementer (Claude Code / Claude Opus 5.5 / medium).

STATE
FACTS:
- Dispatch record in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json: lease_id B2T-g1; repository 1wgrumph/amazon-fantasy-companion; worktree (cwd) $HOME/alphazede/worktrees/amazon-fantasy-companion-b2; branch afc/b2-gate-spec-staged; base 423496ee642982841d1748d102abd05a7d93edcc (origin/main); evidence_dir $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/B2/.
- Found by ST-4-g4 (receipt $HOME/alphazede/worktrees/amazon-fantasy-companion-st4/docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g4/receipt.json, failures ST4-G4-F2, F3) while adding clickable links to the spec (uncommitted work in that worktree; read, do not modify).
- B2a (test-only): tools/ci/tests/gate_support.py copy_repo excludes docs/plans while copying spec/, so once spec sources link to docs/plans files, the docs check inside test fixtures reports DOC-LINK and test_gate_isolation fails; the real repository passes. Origin: S09T fixture; escape: no spec linked repository documents before.
- B2b (product): tools/ci/gate.sh spec area rebuilds each spec/<name>/<name>.md in place and then runs `git diff --exit-code HEAD -- <output>`. In pre-commit, a correctly regenerated and staged output differs from HEAD, so a legitimate commit is rejected. Intended contract: the committed built file equals what its sources build; for a commit that is the index (in CI, index == HEAD). Origin: S09; escape: pre-commit with staged regenerated output never exercised.
- Hooks are active (core.hooksPath=.githooks). Commit and push the red state with --no-verify. Use TMPDIR=/var/tmp/az.

OBJECTIVE
1. B2a: copy_repo (or the fixture) includes whatever repository documents the copied sources link to (e.g. docs/), without recursion into heavy or untracked content; prove with a fixture spec source that links to a docs/ file.
2. B2b red regression: in a fixture repo, change a spec section source, rebuild the output, stage both, run `gate.sh spec` (as pre-commit would): expect exit 0. Also the negative: staged source change without a rebuilt/staged output must fail. The positive case must be RED on current gate.sh (assertion failure); the negative may pass now.

AUTHORITY
Allowed writes: tools/ci/tests/**; the evidence_dir. Commit/push with --no-verify (author from env; never Co-Authored-By); `git push --no-verify -u origin afc/b2-gate-spec-staged`. Prohibited: tools/ci/gate.sh and other product paths, git config, PR creation, merge, force-push.

VERIFY
`env -u GIT_INDEX_FILE -u GIT_DIR python3 -m unittest discover -s tools/ci/tests -v`: only the new B2b positive test fails (assertion failure); B2a fixture proof passes; sha256s.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE; head SHA; changed paths; receipts; sha256s; developer_feedback ("no new observations" + tools if none).

STOP
After the push with receipts recorded.
