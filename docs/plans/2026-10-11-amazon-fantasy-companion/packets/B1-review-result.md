---
type: review-result
title: AFC B1 Independent Review
okf_status: active
tags: [internal, review, afc]
---

# B1 review result

**Verdict: REPAIR_REQUIRED**

The change fixes the supplied colon-shaped content leak. It also removes legitimate whitespace locations when a repository-root filename begins with `+`. The latter is an introduced, reproducible diagnostic regression; the gate still blocks the commit.

## Frozen candidate and scope

- Lifecycle AFC-2026-10-11; Reviewer; DEC-AFC-SD-037 bug-triager route: Codex CLI / GPT-6 Astra / high. No route substitution.
- Candidate: https://github.com/1wgrumph/amazon-fantasy-companion/pull/12, branch `afc/b1-hygiene-colon-leak`.
- Head: `a22dab4a07cf4b26fecf9244e278c05d70003349`.
- Base: `17b40b4bdf8214b300bee05d594e13100d5d0d93`.
- Changed paths: `tools/ci/gate.sh`, `tools/ci/tests/test_gate.py`.
- Gate SHA-256: `10d1f4f2aacc080cf63606d1fb0fc5bd0c38b409a80bf7bca4763a20f525cda7`.
- Test SHA-256: `9d430a2f7de753f57c0efc37e4e38c8fa7ee40e18e4803bbf00c280d7c320545`.
- Independent session; neither authored nor repaired this candidate. Consumed B1T-g1.md, B1-g1.md, B1-review.md, B1T-g1-receipt.md, B1-g1/verify.log and S45-review-result.md. No separate Assurance Test Engineer receipt was supplied; the latest author gate receipt was consumed and the requested checks independently rerun.
- Read the complete diff, gate, tests/helpers, hook callers, workflow checker, path checker, docs checker and applicable DES-AFC-GATE / CONTRACT-AFC-GATE text. Expected usage is local commit/push and CI checks over one repository.
- Tracked working tree and index were unchanged at start and finish; pre-existing untracked Python bytecode directories were left alone. Only this result packet is persisted. Disposable fixtures were removed on exit.

## Findings

| ID | Priority | File:line | Defect | Exact fix |
| --- | --- | --- | --- | --- |
| B1-R1 | P3 | `tools/ci/gate.sh:43` | `/^+/d` removes both source records and valid headers for root filenames beginning with `+`. Stage `+plus.txt` containing `ordinary` followed by three spaces and a newline. Base prints `+plus.txt:1:WS-CHECK`; head prints only the generic gate failure. A location-preservation assertion passes on base and fails on head. This contradicts B1's requirement to preserve `file:line:WS-CHECK` diagnostics. | Replace the unconditional prefix deletion with diagnostic-record parsing that preserves headers whose filename begins with `+` while consuming their source-content records without printing them. If distinguishing Git diagnostic message types, normalize their locale and handle diagnostics with and without following content records. Add a regression for `+plus.txt` requiring its location, exit 1, and no source text; retain the existing colon-shaped non-disclosure test and unconditional failure on nonzero Git status. |

Reachability: both `.githooks/pre-commit` and `.githooks/pre-push` invoke this gate, as does the hosted hygiene job. No exotic configuration is necessary. Git 2.53.0 itself emits the following for the staged fixture (trailing spaces shown as `<SP>`):

```text
+plus.txt:1: trailing whitespace.
+ordinary<SP><SP><SP>
```

The B1-g1 assumption that diagnostic headers never start with `+` is therefore false. Origin: the new line-prefix filter. Escape: both the supplied regression and the author's ordinary-whitespace check use filenames without that prefix. Classification: product diagnostic regression, not a test or harness failure. No security bypass was observed in this case.

Repair targets/write set: `tools/ci/gate.sh` and `tools/ci/tests/test_gate.py`. The parent should include the bounded test addition in the repair packet; no repair was made here. References: B1-g1 OBJECTIVE (preserve locations and fail closed), DES-AFC-GATE, AC-AFC-CI-01 / SEIT-AFC-CI-01.U. Prevention: exercise the legitimate-header and source-content sides of the delimiter assumption, preserving existing assertions.

## Red-then-green receipt

Ran the exact new head test twice. An in-memory wrapper around the existing `copy_repo` helper replaced only the gate inside each disposable fixture with `git show <ref>:tools/ci/gate.sh`. The candidate was never edited. Each test ran in its own Python process.

| Gate revision | Test-process exit | Result |
| --- | --- | --- |
| Base `17b40b4` | 1 | One assertion failure, zero errors: generated token present in captured stdout/stderr. Gate exit-1 assertion held. |
| Head `a22dab4` | 0 | One test passed; token absent. |

Red failure, with generated token redacted by the test:

```text
AssertionError: True is not false : hygiene output echoed colon-shaped staged line text:
+<token>:123:WS-CHECK
notes.md:2:WS-CHECK
gate: hygiene: FAIL check exit 1
```

Comparison driver exited 0 after confirming the expected child exits. The base-to-head test diff only adds the ten-line regression; no existing assertion was weakened. The test-file diff between red-test commit `41fa6e3aed774f0822b1555f994c9138f1a1fc0c` and head is empty.

## Independent reruns

Git 2.53.0; ShellCheck 0.11.0. Python bytecode writes were disabled for review invocations.

| Command / exercise | Exit | Result |
| --- | --- | --- |
| `env -u GIT_INDEX_FILE -u GIT_DIR python3 -m unittest discover -s tools/ci/tests -v` | 0 | 35 tests passed, 8.860 seconds. |
| `bash tools/ci/gate.sh` | 0 | spec, docs and hygiene PASS; embedded 35-test suite passed in 8.760 seconds. |
| `shellcheck tools/ci/gate.sh .githooks/pre-commit .githooks/pre-push` | 0 | No diagnostics. |
| Real installed pre-commit hook, colon-shaped trailing-whitespace payload | 1 | Commit rejected; `notes.md:2:WS-CHECK` present; generated token absent from combined stdout/stderr. HEAD and staged tree unchanged. |
| Ordinary `plain.txt` trailing whitespace, base and head | 1 each | Both print `plain.txt:1:WS-CHECK`. |
| `+plus.txt` trailing whitespace, base and head | 1 each | Base preserves location; head drops it. Separate location assertion PASS on base, FAIL on head; B1-R1. |
| Actual invalid `.git/index` in disposable head clone | 1 | Only generic hygiene failure; no false PASS or raw Git error. |

The hook exercise used a throwaway local clone at the exact head, configured `core.hooksPath=.githooks`, set its `origin/main` ref to the declared base, and invoked ordinary `git commit` without `--no-verify`. It used isolated HOME/global Git configuration, a generated fake token and the unmodified installed hook. No candidate commit was attempted. The first full object-copy clone hit the temporary-storage quota before the exercise ran; a local `--shared --no-checkout` clone avoided copying the object database and completed the exercise. This was a recovered environment issue, not a product finding or unresolved coverage gap.

The suites' `fatal: not a git repository` lines belong to passing intentional negative tests. They are not gate failures.

Inspection confirms every nonzero status captured from `git diff --check` returns 1, including when no header parses. In the hygiene whitespace-error branch, only sanitized locations and fixed gate status text are printed. The downstream path checker reports locations/rule IDs, and workflow errors do not echo parsed source. This is not a repository-wide non-disclosure guarantee: the unchanged spec area's `git diff --exit-code` at gate line 67 intentionally prints generated-document differences, outside B1's hygiene repair.

## Hosted checks

PR #12 was OPEN and draft, with `headRefOid` equal to the frozen head. All four checks completed successfully in [CI run 38258011060](https://github.com/1wgrumph/amazon-fantasy-companion/actions/runs/38258011060), and a final `gh pr checks` rerun exited 0:

| Check | Conclusion | Duration |
| --- | --- | --- |
| Detect changes | SUCCESS | 8s |
| gate / hygiene | SUCCESS | 28s |
| gate / docs | SUCCESS | 5s |
| gate / spec | SUCCESS | 19s |

The installed gh version rejected `baseRefOid` as a JSON field on the initial metadata query. Repeating with supported fields succeeded; the declared base was independently confirmed by Git/OCR. No hosted-check gap remains.

## OCR coverage assist

Required backend: OpenCodeReview delegate mode, available. `ocr delegate preview --from 17b40b4bdf8214b300bee05d594e13100d5d0d93 --to a22dab4a07cf4b26fecf9244e278c05d70003349` exited 0. Merge base matches the declared base; 1 reviewable / 2 total files. `ocr delegate rule` was run for both listed files, including the excluded test; both commands exited 0. Rules were applied in this independent reviewer session, not substituted for review.

| File | Preview disposition | Rules applied and outcome |
| --- | --- | --- |
| `tools/ci/gate.sh` | Reviewable | System/default correctness, security, performance, maintainability and test coverage. Traced callers, Git output records, error status and downstream output. Supplied leak fixed; B1-R1 found. No additional actionable performance or maintenance finding. |
| `tools/ci/tests/test_gate.py` | Excluded: `default_path`; still read and ruled | Python boundaries, state, error handling, resource cleanup, subprocess safety and security-sensitive output. Real disposable fixtures and runtime-generated/redacted tokens; red-to-green reproduced; no prior assertions weakened. Filename-prefix boundary is missing and belongs in B1-R1's prevention regression. |

**Reverify: not applicable — no compiled binary claim.** Required OCR and Reverify applicability were retained explicitly; no live profile substitution or ordinary test run was treated as Reverify.

BRAN status: unavailable; no native `.bran/policy.yaml` in this repository ancestry. Used bounded direct repository and supplied-plan reads; no BRAN coverage claimed.

## developer_feedback

One new observation: B1-R1, a valid `+`-prefixed filename loses its whitespace location. Tools: Git, Bash, Python unittest/disposable-fixture drivers, ShellCheck, OCR delegate preview/rule and gh read-only PR checks. Recovered temporary-storage and gh-field compatibility issues are recorded above. No issue, PR comment, candidate change, commit, push or merge was made.

Not performed: repair or post-repair acceptance; this is the single independent review receipt. Remaining risk: whitespace failures for `+`-prefixed root filenames provide no location. Parent coordinates the bounded repair and deterministic revalidation; stop after this review.
