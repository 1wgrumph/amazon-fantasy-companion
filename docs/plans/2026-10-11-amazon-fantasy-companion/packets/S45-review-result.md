---
type: review-result
title: AFC S45T and S45 Independent Review
okf_status: active
tags: [internal, review, afc]
---

# S45T + S45 review result

**Verdict: REPAIR_REQUIRED**

- Lifecycle: AFC-2026-10-11; Reviewer; bug-triager route per DEC-AFC-SD-037 (Codex CLI / GPT-6 Astra / high).
- Candidate: https://github.com/alphazede/Alphazedehq/pull/317
- Branch: `afc/s45-gate-template-bugs`.
- Exact head: `df7a7e8f44165ee196e6112518814ac5cdc17aa9`.
- Exact base: `23f0bb28a9ef9e0ec6ca1d4ec130489e8c569beb`.
- Boundary: one independent review of the integrated S45T + S45 candidate. This session did not author or repair it. Candidate worktree was clean at review start.
- Inputs: S45T-g1.md, S45-g1.md, S45T-red-receipt.txt, complete base-to-head diff, connected installer/tests/contract, and the referenced AFC origin/main gate. No separate Assurance Test Engineer receipt was supplied; deterministic checks below were independently rerun.
- Scope: shared template, contract and new regression tests; generated repositories with local hooks and fixture repositories. No deployment or binary behavior claim.

The change removes inherited Git location variables and replaces raw whitespace diagnostics with location-only output. D1's requested isolation behavior passes. R2 remains incomplete, and an existing required suite regresses.

## Findings

| ID | Priority | File:line | Defect and evidence | Exact repair target |
| --- | --- | --- | --- | --- |
| S45-R1 | P2 | `skills/setup-pre-commit/templates/gate.sh:24` | The regex processes Git's source-content records as though they were diagnostic headers. A staged line `<generated fake>:123:payload` followed by trailing spaces emits `+<generated fake>:123:WS-CHECK`. Reproduced through a real installed pre-commit hook; the generated fake was present in captured output. This violates R2 and `gate-contract.md:24` even though the commit is blocked. | Parse diagnostic headers separately from their following source-content records; consume/discard the content records without applying the location regex. Preserve location output and failure on nonzero Git exits. Add a generated colon-shaped payload regression through the gate, ensuring the payload never appears in output. Do not merely restrict the assertion to one credential assignment format. |
| S45-R2 | P2 | `skills/setup-pre-commit/templates/gate.sh:19` and `:26`; affected callers `skills/setup-pre-commit/tests/test-install-hooks.sh:62` and `:98` | The existing installer suite passes on the base and exits 1 on this head. Lines 62, 64 and 67 still expect `FAIL check exit 2`, but hygiene now returns 1. After correcting only those expectations in a disposable copy, the suite still fails: its exact-string insertion at lines 98–100 targets the removed one-line hygiene case, so `alpha`/`beta` never receive handlers and clean changed-area checks fail. | Update all three expected detail lines to `FAIL check exit 1`. Insert the `alpha|beta` run-area handler before the first `        *) return 2 ;;` with replacement count 1, and assert that the insertion succeeded. Preserve all existing installer, commit/push, conflict, changed-selection and rename assertions. These two compatibility corrections in a disposable copy restored the complete suite to exit 0. |

S45-R1 is a product/security defect: the R2 port filters every output line rather than distinguishing headers from contents. The new regression's `aws_key = <fake>` shape does not exercise a content line matching the header regex, which explains missed detection. Prevention: include a generated payload before `:123:` and require absence from both stdout and stderr.

S45-R2 is test-integration breakage introduced by the template change, not a Git or harness failure. The existing tests were not weakened or edited; they became incompatible. Prevention: retain the full installer suite as a required passing gate and assert fixture insertions actually match. This review's required run caught the breakage; a passing new-test receipt alone cannot establish the full suite passed.

Repair write set: `skills/setup-pre-commit/templates/gate.sh`, `skills/setup-pre-commit/tests/test_gate_template.py`, and `skills/setup-pre-commit/tests/test-install-hooks.sh`; update the contract only if the implemented behavior changes. The parent must record the bounded test-write correction because the original S45 implementation packet froze tests. No candidate edits were made here. Requirements/case references are packet S45T objectives 1–2 (D1/R2) and S45 VERIFY's existing-suite requirement; no separate SEIT case identifiers were supplied.

## Red-then-green receipt

The exact same head test module was loaded with bytecode disabled, and its `TEMPLATE` path pointed at a temporary file populated by `git show <ref>:skills/setup-pre-commit/templates/gate.sh`. No source file was replaced.

Test SHA-256: `51558d776a50c13e07e6dd637bb6881235643da9956897ed29ad6f01f8e62f44`.

| Template | D1 test | R2 test | Suite result |
| --- | --- | --- | --- |
| Base `23f0bb28a9ef9e0ec6ca1d4ec130489e8c569beb` | Assertion failure: sentinel branch ref changed; sentinel log acquired a `fixture` commit | Assertion failure: generated fake appeared in raw whitespace output | Expected red: 2 failures, 0 errors; unittest success-to-exit mapping 1 |
| Head `df7a7e8f44165ee196e6112518814ac5cdc17aa9` | PASS | PASS for the supplied payload shape | Green: 2 tests, 0 failures/errors; mapping 0 |

The comparison driver exited 0 after reporting both expected results. A separate conventional head invocation also exited 0, as recorded below. `git diff 2262a1c795ec59a4a23672fe8b6a1fd48c337a99 df7a7e8f44165ee196e6112518814ac5cdc17aa9 -- skills/setup-pre-commit/tests` was empty: S45 did not modify S45T's tests or existing tests.

## Independent reruns

Git: 2.53.0. ShellCheck: 0.11.0. Tests use real disposable repositories, isolated HOME/config and generated fake material; nothing below used real credentials.

| Command / exercise | Exit | Result |
| --- | --- | --- |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/setup-pre-commit/tests -p 'test_gate_template.py' -v` | 0 | Both tests pass on head. |
| `bash skills/setup-pre-commit/tests/test-install-hooks.sh` | 1 | Reproduced unchanged; trace stops at line 62's obsolete output assertion. |
| Same installer suite with base template/script in disposable tree | 0 | Both installer and changed-selection sections pass. |
| Head suite in disposable tree, only exit-detail expectations corrected | 1 | `gate: alpha: FAIL check exit 2`; expected gate exit 0, got 1. |
| Head suite in disposable tree, both compatibility corrections applied | 0 | Complete installer and changed-selection sections pass. Diagnostic experiment only, not a repaired candidate receipt. |
| `PYTHONDONTWRITEBYTECODE=1 python3 skills/setup-pre-commit/tests/test_setup_pre_commit.py SetupPreCommitTests.test_creator_validation_and_repository_metadata -v` | 0 | `Skill is valid!`; creator/metadata passes. |
| `shellcheck skills/setup-pre-commit/templates/gate.sh` | 0 | No diagnostics. |
| `bash tools/ci/local-gates.sh` | 0 | 2 passed (diff-check, secret-scan), 0 failed/skipped, 15 not applicable under its path filters. `AZ_GATE_RECEIPTS` pointed at disposable storage to avoid persisting an operational merge receipt during this read-only review. This gate does not run the setup-pre-commit suite. |
| Real installed pre-commit hook: clean outer commit plus fixture-area commit | 0 | Hygiene and fixture PASS. Outer commit has the original parent and exact staged tree; no `fixture` commit exists in outer refs. |
| Real installed hook: ordinary generated payload with trailing spaces | 1 | Only `notes.md:1:WS-CHECK` and gate status lines; fake absent; refs and staged tree unchanged. |
| Real installed hook: colon-shaped generated payload with trailing spaces | 1 | Fake leaked in `+<GENERATED_FAKE>:123:WS-CHECK`; refs and staged tree unchanged. S45-R1. |
| Head hygiene with an invalid index in a disposable repository | 1 | `gate: hygiene: FAIL check exit 1`; no false PASS and no raw Git error echo. |

The hook exercise copied the head template, added the same temporary-repository fixture area used by S45T, selected that area for changed paths, provisioned `origin/main`, installed hooks using the real `install-hooks.sh`, and ran `git commit` without `--no-verify`. All fixture changes stayed in disposable storage. The initial harness compared raw index bytes after a rejected commit; Git's normal index refresh changed them. The corrected check compared refs and `git write-tree`, which stayed unchanged. This was a harness assertion issue, not evidence of leaked writes. D1's separate sentinel HEAD/refs/index byte comparison also passed.

The unset list contains all eleven location variables required by S45, including the location/object variables reported by this Git's `rev-parse --local-env-vars`. Remaining config/replace-control entries are not the requested hook location variables. Review of the error branch confirms every captured nonzero `git diff --check` status returns failure even when no diagnostic is parseable. The contract's failure behavior matches; its unconditional no-content guarantee is disproved by S45-R1.

Minimal S45-R1 input recipe: initialize a disposable repository with a committed baseline and the head template; create `notes.md` containing `"review_" + secrets.token_hex(8) + ":123:payload   \\n"` (a real newline), stage it and run hygiene, or install the hook and commit. Capture both output streams and assert the generated token is absent. Actual output contains the token prefixed with `+` and suffixed with `:123:WS-CHECK`.

## OCR coverage assist

`ocr delegate preview --from 23f0bb28a9ef9e0ec6ca1d4ec130489e8c569beb --to df7a7e8f44165ee196e6112518814ac5cdc17aa9` exited 0: 1 reviewable / 3 total files, merge-base equals the declared base. `ocr delegate rule <file>` was executed for **all three listed files**, including exclusions; each exited 0. No OCR tool gap or substitute review.

| File | Preview disposition | Rules applied and result |
| --- | --- | --- |
| `skills/setup-pre-commit/templates/gate.sh` | Reviewable | System/default correctness, security, performance, maintainability and coverage. Traced hook-to-gate-to-fixture flow, fail-closed handling and diagnostic parsing. S45-R1 and S45-R2. No separate measured performance issue. |
| `skills/setup-pre-commit/references/gate-contract.md` | Excluded: `unsupported_ext`; nevertheless read and ruled | System/default rules; compared claimed output and failure semantics against runtime. No-content promise fails via S45-R1; not counted as a duplicate finding. |
| `skills/setup-pre-commit/tests/test_gate_template.py` | Excluded: `default_path`; nevertheless read and ruled | Python rule group: boundaries, error/resource handling, state, security and reachable behavior. Verified red assertions, isolated real fixtures, cleanup and generated payloads. Existing tests remain unchanged. R2 payload coverage misses S45-R1's header-shaped content. |

**Reverify: not applicable — no compiled binary claim.**

## BRAN and closeout

`bran_status: hit`. Verified the installed HQ runtime SHA-256 against `bran-release-pin.json` (`bran 0.2.0`, digest `776b782a3ab1d9d931f3c121a729a16ae2e8426fa53cb27224273bf59ddd883e`) before executing. Candidate `bran-strict` check exited 0 / pass. The query located `skills/setup-pre-commit/references/gate-contract.md`, `tests/test_gate_template.py`, `SKILL.md`, `templates/gate.sh`, `tests/test-install-hooks.sh` and `scripts/install-hooks.sh`. Coverage: relevant skill, contract, implementation and tests. Broad repository discovery was avoided; bounded reads/searches inspected connected callers, instructions and supplied evidence. The candidate worktree lacks its own runtime executable, so the verified trusted HQ runtime was used as the skill specifies.

`developer_feedback`: Two new observations: S45-R1's content leak and S45-R2's required-suite regression. Tools: BRAN check/query, OCR delegate preview/rule, Git, Bash, Python unittest/temporary-repository drivers and ShellCheck. No tool outage or route substitution; no issue, PR comment, commit or merge created.

Not run: independent trigger classifications, which require `SETUP_PRE_COMMIT_TRIGGER_RESULTS` from a separate evaluator; no results were fabricated. No repair or post-repair acceptance was performed. Risk remaining: source text can enter hook/CI output, and the required installer suite is red. Stop after this receipt; parent coordinates the single bounded repair and deterministic revalidation.
