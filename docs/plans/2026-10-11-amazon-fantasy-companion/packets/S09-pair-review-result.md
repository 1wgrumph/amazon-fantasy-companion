# S09T + S09 pair review result (REVIEWER, independent)

- Lifecycle: AFC-2026-10-11. Review unit: S09T + S09 (repo gate, local checkers, git hooks, Actions workflow).
- Candidate: PR [#9](https://github.com/1wgrumph/amazon-fantasy-companion/pull/9), branch `afc/s09t-gate-tests`,
  head `be366cc2612edfa56ef20ff018a35bd12d95f3af`, base `5e59270b8320d6085039f26b64f14897736845f6`.
  Local verification on the same head in `$HOME/alphazede/worktrees/amazon-fantasy-companion-s09`.
  Note: `origin/main` has since moved to `d259c16` (S42-g2 tools/spec re-vendor); CI evaluates the
  merge commit `3caf450` (Merge be366cc into d259c16).
- Verdict: **REPAIR_REQUIRED** (2 fixable findings, each with file:line + reproducer).
- Evidence dir: `evidence/S09/review/` (all logs below are relative to it).
- Reviewer route: Muse Code / Muse Spark 1.3 / max (this session). Not the author.

## Findings (all must be fixed in the single k=1 repair round)

| ID | Sev | file:line | Defect | Exact fix | Product vs test-only |
|----|-----|-----------|--------|-----------|----------------------|
| R1 | P1 | `tools/ci/tests/test_gate.py:135-137` | `test_fresh_build_passes_and_stale_build_exits_1` hardcodes old-template prose: `.replace('**BLUF:** <One assertive sentence', ...)`. The S42-g2 re-vendor on main dropped the `**BLUF:** ` prefix, so on the PR merge commit the replace silently no-ops, `commit_all` makes an empty commit, the rebuild is byte-identical, the gate correctly PASSes, and the test fails `0 != 1`. Fails CI `gate / hygiene` on run 38251512127 and blocks the S09 stop condition. Reproduced locally on a merge of be366cc+d259c16: `AssertionError: 0 != 1 : gate: spec: PASS checks completed` at line 140 (`repro-stale-test-on-merge.log`; CI log `CI-hygiene-job.log` line 318). | Replace the anchor with text present in both templates and assert the edit took effect: `old_text = intro.read_text(...); new_text = old_text.replace('<One assertive sentence', '<One changed assertive sentence'); self.assertNotEqual(new_text, old_text, 'stale-edit anchor not found in template'); intro.write_text(new_text, ...)`. Anchor verified present in both `be366cc` and `d259c16` templates. | test-only (gate product behaves correctly) |
| R2 | P2 | `tools/ci/gate.sh:38` | `git diff --check HEAD --` prints git's raw diagnostics (`file:line: message` plus a `+<full line content>` line), violating the hygiene FAIL contract (`file:line:rule-id` lines that never contain the matched text, CMD-GATE-HYGIENE pass rule) and DES-AFC-GATE ("never the matched text"). A staged credential line with trailing whitespace is echoed verbatim into hook/CI output (`repro-ws-secret-echo.log`, fake 40xA material), ahead of `check_paths.py` which would have reported it cleanly. Reachable on every commit with a whitespace error. | Keep the enforcement, drop the content (proven in `/tmp/afc-ws-repro`): replace line 38 with `ws=$(git diff --check HEAD -- 2>&1 \| sed -n 's/^\([^:][^:]*:[0-9][0-9]*\):.*/\1:WS-CHECK/p' \| sort -u); if [[ -n "$ws" ]]; then printf '%s\n' "$ws"; return 1; fi`. Output becomes `file:line:WS-CHECK` with zero secret bytes; exit 1 preserved. Deleting the line is an acceptable alternative (the step is design-silent and untested; it is inherited from the D4-A template). Add a regression test that seeds a whitespace error (with and without a fake credential) and asserts FAIL output matches `file:line:rule-id` shape with no echoed content. | product (`gate.sh` output handling) |

## Re-run exit codes (reviewer, exact candidate head be366cc unless noted)

| Command | Exit | Evidence / note |
|---------|------|-----------------|
| unittest discover (33 tests) | 0 | `unittest-green.log`: Ran 33, OK |
| CMD-GATE-HYGIENE | 0 | `CMD-GATE-hygiene.log`: `gate: hygiene: PASS` |
| CMD-GATE-DOCS | 0 | `CMD-GATE-docs.log`: `gate: docs: PASS` |
| CMD-GATE-SPEC | 0 | `CMD-GATE-spec.log`: `gate: spec: PASS` |
| CMD-GATE-ALL | 0 | `CMD-GATE-ALL.log`: all three PASS lines |
| CMD-WORKFLOW-CHECK | 0 | `CMD-WORKFLOW-CHECK.log`: `.github/workflows/ci.yml: PASS` |
| CMD-CI-VENDOR-PIN | 0 | `CMD-CI-VENDOR-PIN.log`; checker sha256 `5919f62d…cd4d3f` matches VENDORED.md |
| CMD-SCAN (verdict greps, 6 receipts) | 0 | `CMD-SCAN-verify.log`: all `verdict: PASS`; action SHAs match ci.yml pins; coverage/diff-cover/mutmut receipts predate first use (11:57:30 vs 11:57:41Z) |
| CMD-COVERAGE-CI | 0 | `CMD-COVERAGE-CI.log`: 92% (check_docs 100%, check_paths 100%, vendored checker 88.0% counted via the known plan-command `--exclude` defect — stricter, still ≥90). Offline env per recorded author env. |
| CMD-MUTATION-CI | 0 (PASS) | Score 114/(114+20+0+6)=0.8143 ≥ 0.70 (`mutation-score.json`, `mutation-ci.txt`); final `git diff --exit-code -- tools/ci` exit 0 (restored). Killed counts are absent from `mutmut results` 2.5.1 output — read from the run's SQLite cache via read-only query (plan-command note, not a slice defect). First attempt without PYTHONPATH failed the baseline with `ModuleNotFoundError: No module named 'yaml'` (uvx env lacks yaml; fixed by exporting the scanned `host-yaml` PYTHONPATH as in the coverage env). `mutmut run` exit 10 observed with complete classification (no pending/timeout statuses); SEIT exit is the diff step. |
| CMD-PR-CHECKS as written | 1 (plan-command defect) | `CMD-PR-CHECKS-aswritten.log`: `gh pr checks --json` → `unknown flag: --json` (gh 2.46.0). Equivalent readback below. |
| PR readback (equivalent) | n/a | `gate / hygiene` FAIL (`repro-stale-test-on-merge.log`, CI `CI-hygiene-job.log`); `gate / spec`, `gate / docs`, `Detect changes` pass; baseRefName `main`. Run 38251512127 completed on be366cc. |
| PROC-ACTIONS-BUDGET | typed gap | `PROC-ACTIONS-BUDGET.log`: billing API 404 + `needs the "user" scope` (exact error recorded); repo PRIVATE. Usage number unavailable. |
| Shell coverage (kcov) | TOOL_MISSING | `kcov` absent (`which` empty). Typed gap per SEIT, never PASS. |
| check_paths over tracked tree | 0, empty | `check-paths-tracked.log` + independent `git grep -o` enumeration (`independent-literals.log`): only the `home/evidence/` segment inside relative `components/home/evidence/` paths (56, correctly skipped by lookbehind); no /Users/, no Windows, no AKIA/ASIA, no 40-char secrets, no private keys. Assumption holds. |
| CMD-RED shape | n/a (green head) | Red proven by S09T g1/g2 receipts (25 tests, AssertionError-only failures) + S09T g3 D1 red; reviewer additionally proved the FINAL D1 test fails on the unfixed gate with the sentinel-write assertion (`d1-final-test-vs-unfixed-gate.log`) and passes on the fixed gate (green suite). |
| Hooks, automatic dispatch | 0/0 | Throwaway clone, `core.hooksPath=.githooks` set THERE ONLY: commit without `--no-verify` → all three areas PASS, +1 commit, 0 `fixture`-message commits, worktree+index clean (`hook-commit-exercise2.log`); push without `--no-verify` to local bare remote → hook PASS, push ok, remote has 0 fixture commits, index intact (`hook-push-exercise.log`). Shared repo `core.hooksPath` left unset (verified). |

## Proof-row status (reviewer adjudication)

- SEIT-AFC-CI-01.U: PASS on head (gate areas, --list, hooks/jobs invoke gate positionally, exits 0/1/2/3); R2 does not break the row's expected result but violates the FAIL-output contract — fixed by R2.
- SEIT-AFC-CI-01.K: PASS-SHAPE (throwaway clone: hooksPath set, hooks executable, invoke gate.sh). Live-installer run stays at IE-P1-9.
- SEIT-AFC-CI-01.A: NOT_RUN (no main merge commit yet; local CMD-GATE-ALL PASS is diagnostic only).
- SEIT-AFC-CI-02.W: PASS (checker exit 0; 8 negative fixtures green in-suite).
- SEIT-AFC-CI-02.P: FAIL (hygiene FAILURE on the PR merge commit; cause R1, test-only). Must re-run after repair.
- SEIT-AFC-CI-03: PASS (8 rule ids report file:line:rule-id without matched text; placeholders pass; --files same rules).
- SEIT-AFC-CI-04.U: CONDITIONAL — spec/docs unit behaviors PASS on head, but the suite's stale-build test FAILS on the merge commit (R1). PASS after R1 repair + green re-run.
- SEIT-AFC-CI-04.S / 04.D: PASS on head (template self-check; docs over tracked Markdown).
- SEIT-AFC-PATH-01.H: PASS (no PATH-HOME-* over tracked files; independent enumeration corroborates).
- SEIT-AFC-RISK-08: TYPED GAP (billing scope; exact error in evidence). No budget concern evident (runs ≤40s).
- SEIT-AFC-RISK-11.H: PASS on head (clean tree passes hygiene); R2 hardens the failure path.
- SEIT-AFC-RISK-13.G: PASS (receipts for 3 action SHAs + coverage/diff-cover/mutmut, all PASS, predate first use; pins match).
- Gate-chain extras: changed-line coverage 92% ≥ 90% PASS; shell coverage TOOL_MISSING (typed gap); mutation 0.814 ≥ 0.70 PASS (check_docs 46/17/2, check_paths 68/3/4 killed/survived/suspicious).

## OCR section (review.coverage_assist, delegate mode, required)

- `ocr delegate preview --from 5e59270b8320d6085039f26b64f14897736845f6 --to be366cc2612edfa56ef20ff018a35bd12d95f3af`: exit 0 (`ocr-preview.txt`). 8 reviewable / 14 total, +1259/-0. Excluded: `tools/ci/VENDORED.md` (unsupported_ext), 5 test files (default_path) — exclusions advisory; reviewer read all 14 files in full (test files are the S09T half of the unit).
- `ocr delegate rule <all 14 files>`: exit 0 (`ocr-rules.txt`, 162 lines, 3 rule groups: default, workflow, python). No tool errors.
- Per-file review against OCR rules (defects found by independent review, rules as checklist):
  - `.githooks/pre-commit`, `.githooks/pre-push`: call `bash tools/ci/gate.sh --changed` after cd-toplevel; match the D4-A unchanged-body provenance and the tested contract. No defect.
  - `.github/workflows/ci.yml`: triggers, concurrency, path filters, per-area `gate / <area>` jobs, full-SHA pins, contents:read, no secrets, ubuntu-latest, Graphviz+uv provisioning per design. No defect. Advisory: no `timeout-minutes` (OCR reliability rule; checker does not require it).
  - `tools/ci/VENDORED.md`: names D4-A `448d40c…` and D4-B `120dee0…`; checker sha256 matches. No defect.
  - `tools/ci/gate.sh`: areas, --changed/--list/usage, exit mapping 0/1/2/3, per-area PASS/FAIL/GAP lines, hook-env unset (D1 fix, proven by isolation test + hook exercise). One defect: R2 (`diff --check` content echo).
  - `tools/ci/check_paths.py`: 8 rules, placeholders, --files, skips dirs/binaries, never prints matches, exit 1 on unreadable/git failure. No defect.
  - `tools/ci/check_docs.py`: headings, relative-link resolution with line-preserving code-strip, skips external/anchors/absolute. No defect. Advisory: reference-style `[text][ref]` usages not resolved (design-silent; possible follow-up).
  - `tools/ci/check_workflows.py`: strict shape checker, byte-identical to merged D4-B (vendor pin exit 0). No defect (must not be modified; any upstream concern belongs to D4-B).
  - `tools/ci/tests/gate_support.py`: in-process main() harness, fixture repos, copy_repo with stub tests (no recursion), PATH farm. No defect.
  - `tools/ci/tests/test_check_paths.py`, `test_check_docs.py`, `test_workflows.py`: generated fixtures without literals, entrypoint/usage/error paths, 8 workflow violations. No defect.
  - `tools/ci/tests/test_gate.py`: entrypoint/exit-code/hook/job-invocation coverage solid. One defect: R1 (template-coupled stale anchor).
  - `tools/ci/tests/test_gate_isolation.py`: D1 regression proven both directions by reviewer (fails on unfixed gate, passes on fixed). No defect.

## Reverify

Reverify: not applicable — shell, Python and workflow YAML only; no compiled binary is built or claimed.

## Route used

Reviewer: Muse Code / Muse Spark 1.3 / max (primary reviewer route). No fallback activation. OCR v1.12.13 delegate mode executed as declared; no probing beyond the packet invocation.

## developer_feedback

- Observation 1 (friction): `gh pr checks --json` (CMD-PR-CHECKS as written in seit.json) is rejected by gh 2.46.0 (`unknown flag: --json`). Readback required `gh pr checks` text + `gh api .../check-runs`. Devpost Product Feedback: n/a. Feature Request: pin a minimum gh version for `--json` support or amend CMD-PR-CHECKS to the check-runs API form. Time cost: unknown. Tools: gh 2.46.0.
- Observation 2 (friction): CMD-COVERAGE-CI/CMD-MUTATION-CI are not reproducible from seit.json alone: offline `uv run`/`uvx` need UV_PYTHON=/usr/bin/python3 + PYTHONPATH=<wheels>/host-yaml (uv's ephemeral Python lacks yaml; mutmut baseline fails with ModuleNotFoundError otherwise) plus the scanned wheel dir. Same class as the S09T-g3 note; extends it to mutation. Devpost Product Feedback: n/a. Feature Request: record the metrics env (UV_PYTHON, PYTHONPATH, wheel dir) in seit.json command definitions. Time cost: unknown. Tools: uv 0.11.6, mutmut 2.5.1, coverage 7.16.2, diff-cover 9.7.2, python 3.14.4.
- Observation 3 (friction): `str.replace` for stale-edit probes fails silently when anchor prose drifts (R1). Asserting `new != old` at the edit site would have pointed at the template instead of the gate. Devpost Product Feedback: n/a. Feature Request: n/a. Time cost: unknown. Tools: python unittest.
- Otherwise: no new observations. Tools used in this review: ocr, gh, git, bash, python3/unittest, uv/uvx, coverage, diff-cover, mutmut.

## Advisories (not findings; no repair budget spent)

1. `gate.sh:37` prints a Python traceback before the GAP line when yaml is missing; exit 3 + GAP line still correct. Cosmetic.
2. ci.yml jobs lack `timeout-minutes` (checker-silent). Consider timeouts in a later slice.
3. `check_workflows.py:63` secret-regex over `str(document)` can false-positive on prose containing "secrets" (e.g. a step named "rotate secrets"). Vendored file — any change belongs upstream (D4-B), not this repair.
4. `check_docs.py` does not resolve reference-style `[text][ref]` link usages, and no test exercises a `[ref]: target` definition (surviving mutant #117 swaps in nonexistent `group(3)`). Design-silent; possible follow-up with its own tests.
5. Characterized surviving mutants below the passing threshold (no action required): #55 (`check_paths.py:36` `continue`→`break` — directory-skip order untested), #83 (`check_docs.py:15` fence-strip regex neutered — no test nests a fake link/heading in a code fence). 17 further survivors unexamined.
5. `--changed` without `origin/main` (e.g. single-branch clones) exits 2 and blocks hooks. Design-mandated default base; consider a documented fallback in a later slice.
6. Known plan-command defects (not slice defects): CMD-COVERAGE-CI `--exclude` mismatch (stricter, passes); CMD-PR-CHECKS `--json` unsupported (equivalent readback done).
7. Typed gaps (not slice defects): shell coverage TOOL_MISSING (kcov absent); Actions budget readback (token scope); SEIT-AFC-CI-01.A NOT_RUN until the main merge exists.

## Reviewer notes for the repair packet

- Write set for repair: `tools/ci/tests/test_gate.py` (R1), `tools/ci/gate.sh` (R2) plus one regression test for R2 (location: `tools/ci/tests/`, S09T-owned dir — same pair unit). No product behavior change beyond R2's output sanitization.
- After repair: re-run the full battery on the new head AND on its merge commit with current main (R1's lesson: the suite must pass on the merge, not just the branch head); re-run CMD-PR-CHECKS to green SEIT-AFC-CI-02.P; mutation re-run needs the coverage env plus `PYTHONPATH=<wheels>/host-yaml` (uvx Python lacks yaml otherwise). Deterministic verification decides (no further review round per n=1/k=1/c=0).
- `git diff` / `git status` in the review worktree were left as found (only pre-existing untracked `__pycache__` dirs); `core.hooksPath` untouched in the shared repo; no commits, pushes, PR comments, or merges by the reviewer.
