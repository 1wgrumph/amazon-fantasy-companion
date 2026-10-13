ROLE
Test Implementer (BEARING_ROLE=test_implementer), Lifecycle AFC-2026-10-11, review finding B1-R1 (hygiene drops the location header when a filename begins with "+") in two places: AFC repo PR #12 and the merged shared setup-pre-commit template (defect B4, same code), bug-triager route per DEC-AFC-SD-037. RESPONSIBILITY: red regressions only, in both repositories.
BUG_ROUTE: bug-triager test_implementer (Claude Code / Claude Opus 5.5 / medium).

STATE
FACTS:
- Dispatch record in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json: lease_id B1T-r1.
- Target A: 1wgrumph/amazon-fantasy-companion, worktree $HOME/alphazede/worktrees/amazon-fantasy-companion-b1, branch afc/b1-hygiene-colon-leak (PR #12), base a22dab4a07cf4b26fecf9244e278c05d70003349; tests in tools/ci/tests/test_gate.py.
- Target B: alphazede/Alphazedehq, worktree $HOME/alphazede/worktrees/alphazedehq-afc-b4, branch afc/b4-plus-filename-location, base c323c56f556cf708b7104838d2f2977af015fe67; tests in skills/setup-pre-commit/tests/test_gate_template.py.
- Defect (reviewer-reproduced, packets/B1-review-result.md): both gate.sh versions run `sed -n '/^+/d; s/^\([^:][^:]*:[0-9][0-9]*\):.*/\1:WS-CHECK/p'` over `git diff --check` output. git prints a header `path:line: message` and then the offending source line prefixed with `+`. Deleting every `+`-leading line also deletes headers of files whose names start with `+` (e.g. `+plus.txt`), so the failure prints no location (exit 1 is kept). Contract: one `file:line:rule-id` line per finding, never the source text.
- Evidence dir: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/B1/r1/ (A) and evidence/B4/ (B).
- AFC has hooks active: commit with --no-verify for the red commit. Use TMPDIR=/var/tmp/az.

OBJECTIVE
In each target add a regression: stage a file named `+plus.txt` with a trailing-whitespace line whose content is a runtime-generated colon-shaped token (`"review_" + secrets.token_hex(8) + ":7:payload   "`); assert exit 1, output contains `+plus.txt:1:WS-CHECK`, and the token is absent from stdout and stderr (use assertFalse with a redacted message, not assertNotIn). RED on the current gate.sh/template (missing location), assertion failure.

AUTHORITY
Allowed writes: the two test files' directories (tools/ci/tests/** in A, skills/setup-pre-commit/tests/** in B) and the evidence dirs. Commit (author from env; never Co-Authored-By; --no-verify in A); plain push of each branch (B: `git push -u origin afc/b4-plus-filename-location`). Prohibited: gate.sh/templates, other paths, PR creation, merge, force-push.

VERIFY
Each repository's suite: only the new test fails, with an assertion failure (record text, token redacted); sha256 of changed test files.

RETURN
Per target: PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE; head SHA; red receipt; sha256. developer_feedback ("no new observations" + tools if none).

STOP
After both pushes with red receipts recorded.
