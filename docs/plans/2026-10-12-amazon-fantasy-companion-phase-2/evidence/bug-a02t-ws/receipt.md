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
PR base or push `before` commit. CI hygiene now checks out full history with
credentials persistence disabled. The missing-base fetch remains a fail-closed
fallback. An invalid or unavailable CI base fails closed. Existing sanitized
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

## Review repair: F1 and F2

- Repair baseline: `0753adbb05320ca70035043c1bcc158b5c4b97bd`, same worktree,
  branch and frozen bug-triager Implementer route. The owner-authorized repair
  write set covers the hygiene checkout, gate, gate tests and this evidence
  directory. The packet's shortened evidence path resolves to this existing
  Lifecycle evidence directory; no new top-level evidence directory is needed.
- Next action: finish deterministic verification, commit with hooks enabled,
  and return the repair result to the coordinator. This is author verification,
  not independent assurance. F3's CHANGELOG PR link remains the coordinator's
  landing obligation, outside this worker's write set.
- F1 origin: hygiene used checkout's depth-1 default without persisted
  credentials. Its subsequent private-remote fetch could not authenticate.
  The original file-remote regression escaped this because fetching was allowed.
  Repair: hygiene checkout alone sets `fetch-depth: 0`; `persist-credentials:
  false` and the gate's fail-closed fetch fallback remain intact.
- F2 origin: failure to find `origin/main` selected HEAD without identifying
  the resulting uncommitted-only scope. Repair: print exactly one line,
  `WS-CHECK: no origin/main; checking uncommitted changes only`.

Method: test. Two new named behaviors use real Git repositories, the actual
workflow checkout depth, and isolated local clones. Disabling Git's file
transport after cloning models a remote that denies further fetch access,
without accessing credentials or the network. Both PR and push event shapes
are covered. Depth-1 copies must report `WS-CHECK: CI base unavailable` and
fail; workflow-depth copies must reach the existing base, reject committed
whitespace, and pass after a clean replacement commit. The local fallback must
print its notice once and still reject staged whitespace. Existing redaction
assertions remain, excluding only the new fixed notice from location records.
No engines, services, shared ports or acquired dependencies are involved.

- Red command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/ci/tests python3 -m
  unittest test_gate.AC_AFC_CI_01.test_ci_base_without_fetch_access_fails_closed_or_uses_checkout_history
  test_gate.AC_AFC_CI_01.test_local_without_origin_main_announces_uncommitted_only_fallback`.
  Exit 1 on unchanged product code: PR and push full-history cases instead
  reported `CI base unavailable`; local notice count was 0 instead of 1.
  Depth-1 fail-closed cases already passed. These are expected regression
  failures reproducing F1/F2, not new defects or issue-filing triggers.
- Green command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools/ci/tests python3 -m
  unittest test_gate`. Exit 0: 21 tests, 28.227 seconds. Both new test IDs pass,
  including the previously failing cases. The original committed-evidence
  regression also passes, retaining missing-base fetch coverage
  through an accessible local remote.
- `bash -n tools/ci/gate.sh` and `git diff --check`: exit 0.
- Full gate: `JAVA_HOME="$HOME/.local/share/afc-tools/jdk-17.0.20.1+1"
  ANDROID_HOME="$HOME/.local/share/afc-tools/android-sdk"
  GRADLE_USER_HOME="$HOME/.gradle/afc-p2-a01t" PYTHONDONTWRITEBYTECODE=1
  timeout 600 bash tools/ci/gate.sh`, exit 0. All five areas pass, including
  69 hygiene tests and 380 backend tests. Output includes expected negative
  fixture Git diagnostics and existing botocore deprecation warnings; neither
  is a failed gate. The external repair result records the final commit SHA
  and commit-hook outcome, avoiding a self-referential receipt commit.

BRAN: unavailable (no native policy). OCR: the existing review produced F1/F2;
no extra review round is started by this worker. Reverify: not applicable to
this repair's shell/YAML/Python behavior; no compiled-binary claim is made.
