ROLE
Test Implementer (BEARING_ROLE=test_implementer), Lifecycle AFC-2026-10-11, defect B1 (hygiene leaks colon-shaped source text; same flaw as review finding S45-R1, present on AFC main since 17b40b4), bug-triager route per DEC-AFC-SD-037. RESPONSIBILITY: the red regression only. Not tools/ci/gate.sh.
BUG_ROUTE: bug-triager test_implementer (Claude Code / Claude Opus 5.5 / medium).

STATE
FACTS:
- Dispatch record in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json: lease_id B1T-g1; repository 1wgrumph/amazon-fantasy-companion; worktree (cwd) $HOME/alphazede/worktrees/amazon-fantasy-companion-b1; branch afc/b1-hygiene-colon-leak; base 17b40b4bdf8214b300bee05d594e13100d5d0d93 (origin/main); evidence_dir $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/B1/.
- Defect (reproduced by the S45 reviewer on the identical shared-template code; packets/S45-review-result.md): tools/ci/gate.sh hygiene runs a sed location regex over every `git diff --check` output line, including `+<source line>` content records, so a staged line `<token>:123:payload   ` prints `+<token>:123:WS-CHECK`. Origin: R2 fix (17b40b4) filtered all lines instead of distinguishing headers from content; escape: the R2 regression used `aws_key = <fake>`, not a colon-shaped payload.
- core.hooksPath=.githooks is active in this repository: your red commit will fail the pre-commit gate, so commit with `git commit --no-verify` and push with `git push --no-verify`.

OBJECTIVE
Add to tools/ci/tests/test_gate.py a regression: staged line `"review_" + secrets.token_hex(8) + ":123:payload   "` (runtime-generated) run through the hygiene area; assert exit 1 and the token absent from stdout and stderr. RED on current gate.sh with an assertion failure.

AUTHORITY
Allowed writes: tools/ci/tests/**; the evidence_dir. Commit --no-verify (author from env; never Co-Authored-By); `git push --no-verify -u origin afc/b1-hygiene-colon-leak`. Prohibited: tools/ci/gate.sh and other product paths, git config, merge, force-push, PR creation.

VERIFY
`env -u GIT_INDEX_FILE -u GIT_DIR python3 -m unittest discover -s tools/ci/tests -v`: only the new test fails, assertion failure (record text, token redacted); sha256 of test_gate.py.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE; head SHA; receipt; sha256; developer_feedback ("no new observations" + tools if none).

STOP
After the push with the red receipt recorded.
