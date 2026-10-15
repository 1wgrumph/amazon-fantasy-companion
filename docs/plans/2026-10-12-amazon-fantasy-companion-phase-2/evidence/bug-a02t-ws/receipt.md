# A02T whitespace repair

## Worker binding and next action

- Lifecycle: AFC-2026-10-11; delegated Implementer packet `coord-w2-bug-a02t-ws`.
- Checkout: `$HOME/alphazede/worktrees/amazon-fantasy-companion-bug-a02t-ws`;
  branch `afc/bug-a02t-ws`; starting revision `71d3e649fec8406cc593519e9d8cab5eb7c65575`.
- Frozen bug-triager binding SHA-256:
  `4950987be8ea55c2525e7f4ab05226712e7720d734ade5b516bee76502308041`.
- Route: Codex CLI / GPT-6.1 Sol / high. The delegated packet authorizes
  this worker's tests and implementation. No independent review or push.
- The parent journey's recorded controller checkout is historical; the current
  owner packet supplies this worker's checkout, branch, baseline and write set.
- Next action: reproduce WS-CHECK, repair its comparison base, run the focused
  regression and full gate, then commit with hooks enabled and return to the
  coordinator. This receipt records worker execution, not parent acceptance.
- OCR remains enabled and required in the frozen binding; independent review
  belongs to the coordinator. Reverify is enabled; not applicable to this packet
  because it makes no compiled-binary claim. BRAN: unavailable (no native policy).

## Cause and escape

PR #74 introduced a trailing space at line 2 of `P2-A02T/cmd-red.txt`.
This is evidence hygiene, not a product-runtime or test-only defect.
`git diff --check HEAD` examines added lines between HEAD and the worktree,
regardless of extension. The hook could see the log before its commit; the
clean CI checkout could not. Also, `--changed=<base>` selected gate areas
without applying that base to WS-CHECK. No extension exclusion caused this.

Both routes now apply the existing Git whitespace rule to the relevant change:
the selected local base (or merge-base with origin/main), and the GitHub event's
PR base or push `before` commit. A shallow CI checkout fetches only its missing
base commit. An invalid or unavailable CI base fails closed. Existing sanitized
`file:line:WS-CHECK` reporting is preserved. Historical whitespace outside the
change is not rewritten.

## Verification

Method: test, using real Git repositories and depth-1 local clones; no engine,
network service, shared port, device or AWS. Expected focused-test cost: about
7 seconds, isolated temporary directories removed by unittest cleanup.

- Original unmodified log: `git diff --check HEAD^ HEAD -- <cmd-red.txt>`
  with the gate's existing location formatter reports
  `P2-A02T/cmd-red.txt:2:WS-CHECK`.
- Regression ID:
  `test_gate.AC_AFC_CI_01.test_committed_evidence_whitespace_fails_locally_and_in_ci`.
  Before repair it failed in all three modes: local, pull_request and push;
  each incorrectly returned PASS for committed whitespace.
- After repair the same regression passes: each mode reports the same
  `cmd-red.txt:2:WS-CHECK` finding, does not echo the line content, and passes
  after a clean replacement is committed. CI cases exercise the missing-base
  fetch through a real local Git remote and a shallow checkout.
- Byte comparison against the baseline confirms that the historical log loses
  exactly one space and has no other changes. The same Git whitespace check
  passes for the corrected path.
- `bash tools/ci/gate.sh`: exit 0 with the installed pinned Android SDK and
  JDK supplied through environment variables. All five areas pass; hygiene
  runs 67 tests and backend runs 380 tests. The initial run's SDK provisioning
  gap was corrected by supplying the installed SDK, without installing tools.
- The focused regression, clean-copy path check, and ambient backend-tool
  selection test also pass with `GITHUB_ACTIONS=true` and an inherited event
  path (3 tests). Fixture events use their own repository history, preserving
  explicit CI flags and the new regression's explicitly supplied event.
- `bash -n tools/ci/gate.sh` and `git diff --check`: pass.
- Final commit and hook results are returned in the coordinator packet.

No issue filing, independent review, push, PR or publication is part of this packet.
