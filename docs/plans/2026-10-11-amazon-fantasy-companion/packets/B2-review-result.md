# B2 independent review — PASS

Candidate: `9752ef28d69c2a6a7a5aa3c835920bc95dce2b27`.
Base: `3be60fca776f61ce620a83ea3c18f29bc9ee4472`.
Scope: `commits=3be60fca776f61ce620a83ea3c18f29bc9ee4472..9752ef28d69c2a6a7a5aa3c835920bc95dce2b27`.
PR: [14](https://github.com/1wgrumph/amazon-fantasy-companion/pull/14).

This is the first and only independent B2 review, by the assigned frozen
bug-triager reviewer route in a fresh session. No nested agents or authoring.
Bearing verdict: ACCEPT; packet verdict: PASS. No actionable P0–P3 findings,
repair targets, blockers, or missing required checks. One review consumed;
no repair consumed. This receipt establishes the bounded review result only.

## Evidence and identity

Consumed `B2T-g1.md`, `B2T-g2-codex.md`, `B2-g2.md`, the B2T test receipt,
and the latest B2-g2 product gate-chain receipt. Author diagnostics were inputs,
not independent acceptance. Independently inspected all four changed files,
their connected callers and tests, `.githooks/pre-commit`, `.githooks/pre-push`,
`.github/workflows/ci.yml`, the docs/path/workflow checkers, and spec build/lint
entrypoints. Read DES-AFC-GATE, CONTRACT-AFC-GATE and relevant SEIT rows.

The live PR head and final local HEAD both equal the candidate. The working
tree and index have no tracked differences. Only the same four pre-existing
`__pycache__` directories remain untracked. The two test files match
`46f662dd6e1da7c89f9e3fc41fc97690efee729f` byte-for-byte, confirmed by Git diff
and SHA-256; hashes are in the [receipt](../evidence/B2/review/receipt.json).

## Command results

| Command | Result |
|---|---|
| `env -u GIT_INDEX_FILE -u GIT_DIR TMPDIR=/var/tmp/az PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools/ci/tests -v` | Exit 0; 39/39 pass, 8.430 seconds |
| `env TMPDIR=/var/tmp/az PYTHONDONTWRITEBYTECODE=1 bash tools/ci/gate.sh` | Exit 0; spec/docs/hygiene PASS; nested 39/39 tests pass, 8.138 seconds |
| `git diff --check` | Exit 0; no output |
| `gh pr checks 14 -R 1wgrumph/amazon-fantasy-companion` | Exit 0; Detect changes and all three gate jobs pass |
| Frozen test-file diff from `46f662d` to candidate | Exit 0; no differences |
| Independent six-case baseline/candidate reproduction | Exit 0; all expected red/green outcomes confirmed |

The unittest stderr messages about a non-repository directory belong to the
intentional Git-failure tests, which passed. They are not harness or product
failures. [GitHub Actions evidence](https://github.com/1wgrumph/amazon-fantasy-companion/actions/runs/38343279287)
is bound to the candidate by the separate PR-head readback.

The independent reproducer imported the candidate's frozen test cases and ran
them on their owned temporary Git repositories. For the old B2a behavior it
loaded `gate_support.py` from the exact base using `git show`, then temporarily
substituted only `copy_repo`, preserving the fixture's patched source root.
For old B2b behavior a test subclass replaced only the temporary repository's
`gate.sh` with the exact base version after setup. It then ran the same cases
with the candidate implementation. No source or index in the candidate was
changed. Each case required one test, zero errors and the expected assertion
count. Baseline failures also required `DOC-LINK` or `AssertionError: 1 != 0`
with `gate: spec: FAIL`, respectively.

| Case | Base behavior | Candidate behavior |
|---|---|---|
| Linked tracked document / excluded untracked content | Assertion failure, DOC-LINK | Pass |
| Staged source plus rebuilt/staged output | Assertion failure, gate exits 1 | Pass, gate exits 0 |
| Staged source without rebuilt/staged output | Pass, gate correctly exits 1 | Pass, gate correctly exits 1 |

Sanitized individual outcomes: [red/green receipt](../evidence/B2/review/red-green.jsonl).

## OCR per-file coverage

`review.coverage_assist`: enabled, required, backend OpenCodeReview delegation,
available and completed. The exact requested `ocr delegate preview --from
3be60fca776f61ce620a83ea3c18f29bc9ee4472 --to
9752ef28d69c2a6a7a5aa3c835920bc95dce2b27` exited 0 and returned two reviewable
files out of four. Explicit `ocr delegate rule` calls for all four files exited
0, including both default exclusions. Rules were applied in this reviewer
session; OCR supplied coverage guidance, not a verdict.

| File | Preview / rules | Independent application |
|---|---|---|
| `CHANGELOG.md:1–14` | Excluded `unsupported_ext`; explicit system/default rules | Entire file read; Unreleased entry accurately describes the index comparison and links PR 14. No sensitive data or runtime behavior introduced. |
| `tools/ci/gate.sh:70` | Included; system/default rules | Full gate and callers read. Removing HEAD compares the regenerated file against the index. Real staged positive and negative cases confirm both outcomes. Lint, diagram lint, rebuild, tracked-file check at line 69, quoted paths, temporary cleanup, Git environment isolation, docs and hygiene remain intact. |
| `tools/ci/tests/gate_support.py:83–100` | Included; Python rules | Entire helper and every copy_repo caller read. Tracked-only enumeration includes linked planning files while omitting untracked files; test recursion remains excluded. Real Git fixture, copy permissions, cleanup ownership and error propagation retained. |
| `tools/ci/tests/test_gate.py:124–142,212–242` | Excluded `default_path`; explicit Python rules | Entire file read. Linked-file case uses a real source repository; the patch changes only its selected root. Spec cases run the real builder and gate in fresh repositories, stage through Git, and cover both successful rebuild and missing rebuild. Existing lint, gap, hygiene and isolation coverage passes. |

Full rule output: [OCR rules](../evidence/B2/review/ocr-rules.txt).
`deterministic_verification.reverify`: enabled; not applicable — shell/Python
source behavior, no compiled binary claims. No capability substitution.
BRAN: unavailable because there is no native repository policy; ordinary
repository discovery provided the required evidence. This is not a required
OCR or verification gap.

## Origin, missed detection and prevention

B2a was a test-only S09T fixture defect: `copy_repo` excluded `docs/plans`
despite copying spec sources. When a spec linked those documents, the fixture
produced a false DOC-LINK even though the real repository resolved the link.
Earlier cases lacked this cross-directory link. The repair at
`gate_support.py:90–94` copies tracked documents and excludes untracked content;
`test_gate.py:124` now fails under the old copier and passes under the candidate.
This closes the concrete fixture gap in AC-AFC-CI-01 / SEIT-AFC-CI-01.U and the
relative-link behavior of AC-AFC-CI-04 / SEIT-AFC-CI-04.U.

B2b originated in the S09 product gate's HEAD comparison. DES-AFC-GATE and
SEIT-AFC-CI-04.U required a rebuild/diff check, but earlier tests committed
changes before checking and did not exercise a correctly staged pre-commit
source/output pair. `gate.sh:70` now compares against the index, which equals
HEAD in clean CI. The frozen positive at `test_gate.py:230` and negative at
`:238` prevent regression in either direction. Hooks and CI retain the same
shared gate entrypoint; all related checks pass. The supplied specialist
receipts identify this same origin and escape, and the independent red/green
exercise corroborates them. No model artifact is changed or needed for these
shell/Python behaviors.

## Developer feedback and limits

Tools: Git, Python unittest, uv, Graphviz dot, vendored spec tools,
OpenCodeReview delegation and GitHub CLI. An optional PR identity query first
requested unsupported `baseRefOid`; it was corrected to supported fields and
readback succeeded. This is a query compatibility observation, not evidence
of a product defect. No other new observations.

No broader repository audit, Requirements System document review, compiled
binary verification, publication or runtime activation was performed. No
candidate edits, commits, push, merge, issues, or GitHub reviews/comments.
Only this result and `evidence/B2/review/**` were persisted in the control plan.
Stop after this one review; landing and any subsequent authority remain with
the parent controller.
