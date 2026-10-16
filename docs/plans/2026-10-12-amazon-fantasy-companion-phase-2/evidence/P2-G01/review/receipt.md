# P2-G01 review receipt

**REPAIR_REQUIRED** — `83603febf3e9b5dcdfef6f5648ecdc8053a94538` against `4994aad44ace64f3c9434f73461f3fe2d12f694b`. One fresh independent review, lease `P2-G01-review`, unit `IE-P2-3`; Codex CLI / GPT-6 Astra / high under the recorded owner amendment.

One independent review of the exact stable candidate. Assurance Test Engineer and Integration Engineer execution are lifecycle cadence; consumed latest author gate-chain/bug1 receipt because no ATE receipt is due at IE-P2-3. These reruns support review findings, not lifecycle acceptance.

## Findings

### G01-R01 — P2: Duplicate test module basename breaks full-tree pytest collection

Location: `tools/ci/tests/mutation/test_backend_adapter.py:1`.

Both new adapter suites are non-package files named test_backend_adapter.py. Default pytest imports the coverage file under that name, then refuses to collect the mutation file.

Scenario/evidence: Run python3.12 -m pytest -q tools/ci/tests on the frozen candidate: exit 2, import file mismatch. Clean archives reproduce base collection exit 0 (39 cases) versus candidate exit 2 (63 collected plus one error), ruling out the pre-existing worktree caches.

Reproducer: python3.12 -m pytest -q tools/ci/tests; compare python3.12 -m pytest --collect-only -q tools/ci/tests on git archives of base and candidate.

Repair: Give the mutation adapter suite a unique basename and verify whole-tree collection. Do not casually add __init__.py: that would also make the normal unittest gate recurse into native-tool suites, changing its prerequisites.

Write set: tools/ci/tests/mutation/test_backend_adapter.py (rename); tools/ci/tests/ (collection regression if needed).

SEIT: SEIT-AFC-P2-GATE-01; PROC-GATE-TOOL-QUALIFY.

Escape: Introduced by G01 adapter controls, not by bug1. Per-directory qualification and top-level unittest discovery cannot expose cross-directory pytest module collisions. The bug1 receipt correctly calls it pre-existing relative to bug1, but that does not make it baseline debt for this review.

Logs: pytest.log; collection-and-exits.log.

### G01-R02 — P2: Final exec bypasses mutation workspace cleanup

Location: `tools/ci/mutation/backend.sh:33`.

The wrapper installs an EXIT trap at line 21 but exec replaces the shell before it can run. Every completed native mutation run leaves its archived backend and mutants tree on disk.

Scenario/evidence: Set TMPDIR to a fresh owned directory and run the existing known-killed fixture. The adapter returns 0, yet one newly created work directory remains containing backend/ and backend/mutants/.

Reproducer: Use BackendMutationAdapter.setUp(), set TMPDIR to an isolated directory, snapshot its children, run_adapter with CONTROL and BOTH, then compare children after return; inspect only the newly created child. Native result: exit 0, LEAKED_WORKDIR_COUNT 1.

Repair: Call the evaluator without exec and exit with its status so EXIT cleanup runs on PASS, FAIL and GAP; verify cleanup of only the owned workspace.

Write set: tools/ci/mutation/backend.sh; tools/ci/tests/mutation/test_backend_adapter.py (or renamed successor).

SEIT: PROC-GATE-TOOL-QUALIFY; SEIT-AFC-P2-GATE-01.

Escape: The checkout-is-unchanged assertion checks the source repo, not the separately allocated mktemp workspace.

Logs: mutation-repro.log.

### G01-R03 — P2: Stale XML for an existing file can falsely pass changed-line coverage

Location: `tools/ci/coverage/evaluate.py:50`.

Completeness validation checks only that each changed filename appears in diff-cover src_stats. It does not bind the XML to the source revision or ensure that newly added executable lines are represented.

Scenario/evidence: Generate real 100% XML for control.py, commit a candidate that changes one previously covered return and adds an untested function, then evaluate the old XML against the new candidate. It returns PASS/0 at 100% over one line. Running the native wrapper afresh on the same candidate returns FAIL/1 at 66% over three lines.

Reproducer: Use BackendCoverageAdapter with CONTROL/BOTH to generate XML; preserve XML; set base to that HEAD; commit CONTROL.replace("covered", "new") plus def untested(): return "new logic", and update the covered assertion. Invoke evaluate.py BASE STALE_XML OUT, then backend.sh BASE OUT. Observed exits 0 then 1.

Repair: Bind native evidence to candidate/source digests and reject mismatched reports, and/or compare report statements with a candidate executable-line inventory. Add a stale-same-file control, not just the existing newly-added-file control.

Write set: tools/ci/coverage/evaluate.py; tools/ci/coverage/backend.sh (report binding if used); tools/ci/tests/coverage/test_backend_adapter.py.

SEIT: PROC-GATE-TOOL-QUALIFY; CMD-COVERAGE-BACKEND; SEIT-AFC-P2-GATE-01.

Escape: The existing stale-XML test adds an entirely new file, so filename presence is enough to pass that test while missing the stated stale-report obligation.

Logs: coverage-repro.log.

### G01-R04 — P2: Incomplete mutation inventory is accepted as complete evidence

Location: `tools/ci/mutation/evaluate.py:43`.

The parser accepts any nonempty inventory with one matching module and scores independent aggregate stats. It never reconciles parsed IDs/statuses with total or status counts. The wrapper also ignores the export/results command status at line 31.

Scenario/evidence: A real native run produces four killed mutant IDs and total=4. Retain only the first native inventory line, preserving the native stats. The evaluator returns PASS/0 with mutants=1, killed=4 and total=4. An interrupted or partially written results export can therefore omit survivors or unresolved cases without invalidating the score.

Reproducer: After the real CONTROL/BOTH adapter run, truncate mutmut-results.txt to its first __mutmut_ line; invoke python3 tools/ci/mutation/evaluate.py OUT backend/src/control.py 0. Observed PASS/0 with inconsistent counts.

Repair: Require successful export and results commands, validate supported schema/statuses, and reconcile all unique IDs and per-status counts with native totals before scoring. Reject missing, truncated or inconsistent inventory as GAP.

Write set: tools/ci/mutation/backend.sh; tools/ci/mutation/evaluate.py; tools/ci/tests/mutation/test_backend_adapter.py (or renamed successor).

SEIT: PROC-GATE-TOOL-QUALIFY; CMD-MUTATION-BACKEND; SEIT-AFC-P2-GATE-01.

Escape: Controls cover an absent/empty inventory, timeout and absent file mapping, but not partial native inventory or exporter failure.

Logs: mutation-repro.log.

### G01-R05 — P2: Unchanged functions dilute the changed-behavior mutation score

Location: `tools/ci/mutation/backend.sh:25`.

only_mutate selects whole changed files, and evaluate.py scores every native mutant in those files. The approved denominator is changed executable behavior, not all behavior in a file that happened to change.

Scenario/evidence: Start with two unchanged, fully tested functions (eight killed mutants), then add only one untested function to their file (two no-tests mutants). The adapter returns PASS/0 at 80%, although zero of the two mutants in the actual changed behavior are killed.

Reproducer: Commit CONTROL plus CONTROL renamed verdict2, with BOTH tests for each. Set base to that commit. Append only def untested(): return "untested" and run backend.sh BASE OUT. Native result: killed=8, no_tests=2, PASS 80%; both new function mutants are listed as no tests.

Repair: Bind selected native mutant IDs to changed executable behavior/functions before calculating the score, preserving full inventory for review. If the admitted backend cannot establish this mapping, return a named scope GAP instead of a whole-file PASS.

Write set: tools/ci/mutation/backend.sh; tools/ci/mutation/evaluate.py; tools/ci/tests/mutation/test_backend_adapter.py (or renamed successor).

SEIT: seit.json gate_tool_plan mutation threshold; CMD-MUTATION-BACKEND; PROC-GATE-TOOL-QUALIFY.

Escape: All positive/negative fixtures introduce an entire new source file, so they never distinguish changed behavior from previously tested code.

Logs: mutation-scope-repro.log.

### G01-R06 — P2: A function mutant masks unsupported module-level changes in the same file

Location: `tools/ci/mutation/evaluate.py:47`.

The unmapped check requires only one mutant anywhere in each changed module. It therefore loses the required PYTHON_NONFUNCTION_MUTATION_GAP when unsupported changed module-level behavior coexists with supported functions.

Scenario/evidence: Add control.py containing LIMIT = 3 followed by the tested CONTROL function, with BOTH tests. Native mutmut emits four function mutants and none for LIMIT, yet the evaluator returns PASS/0 at 100%.

Reproducer: Run the admitted adapter against a committed new control.py with "LIMIT = 3\n\n" + CONTROL and BOTH. Native inventory contains only control.x_verdict__mutmut_1..4; result is PASS rather than PYTHON_NONFUNCTION_MUTATION_GAP.

Repair: Inspect changed executable scope and explicitly reject unsupported module-level behavior with the planned typed gap, even when the same file has function mutants. Preserve any exclusions only through explicit approved scope disposition.

Write set: tools/ci/mutation/backend.sh; tools/ci/mutation/evaluate.py; tools/ci/tests/mutation/test_backend_adapter.py (or renamed successor).

SEIT: seit.json gate_tool_plan PYTHON_NONFUNCTION_MUTATION_GAP; implementation.json assurance limitations; PROC-GATE-TOOL-QUALIFY.

Escape: The existing negative case puts LIMIT in a separate constants.py file, where filename mapping catches it; it misses mixed supported/unsupported behavior.

Logs: mutation-repro.log.

### G01-R07 — P2: Action admission PASS conflicts with explicitly stale scanner data

Location: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/supply-scan.json:31`.

The receipt records Trivy --offline-scan --skip-db-update with a three-day-old database whose NextUpdate has passed (line 6), but grants PASS to both actions (lines 31 and 55). The invoked supply-chain skill requires INDETERMINATE for missing/stale required scanner data; no owner acceptance of this named residual gap appears in the review authority.

Scenario/evidence: The new setup-java and setup-python workflow pins are admitted based on these PASS claims. Inspection of the receipt reproduces the policy contradiction: stale-required-data guard is false. Disposition of the listed old advisories does not establish that newer advisories are absent.

Reproducer: Parse supply-scan.json: scanners.trivy contains "NextUpdate passed" while both actions[*].verdict equal PASS. Compare scan-software-supply-chain/SKILL.md section 6, which classifies stale required scanner data as INDETERMINATE.

Repair: Rerun the affected vulnerability check on the exact action bytes using current admitted advisory data and persist sanitized results with provenance, or correct the verdict to INDETERMINATE and retain the admission hold until explicit owner residual-risk acceptance. Do not label a new scan or acceptance PASS before it exists.

Write set: docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/supply-scan.json; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/ (refreshed scan evidence and receipt); .github/workflows/ci.yml (only if admission must be held or pins change).

SEIT: SEIT-AFC-P2-SUPPLY-01; AC-AFC-P2-SUPPLY-01; CMD-SUPPLY-SCAN.

Escape: Action scan summary acknowledges expiry but treats source reachability arguments for known advisories as sufficient for overall admission. This finding is an evidence/admission defect, not a claim that either action is malicious or an advisory is reachable.

Logs: inspection.log; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/supply-scan.json.

## Commands and exits

| Command | Exit | Time |
|---|---:|---:|
| `bash tools/ci/gate.sh` | 0 | 41.412 s |
| `actionlint` | 0 | 0.016 s |
| `python3 -m unittest discover -s tools/ci/tests -v` | 0 | 32.712 s |
| `python3 -m unittest discover -s tools/ci/tests/coverage -v && python3 -m unittest discover -s tools/ci/tests/mutation -v` | 0 | 15.092 s |
| `python3.12 -m pytest -q tools/ci/tests` | 2 | 0.415 s |

Gate: 50 hygiene tests pass; tvapp/backend report the exact absent-tree PASS. Qualification: 11 coverage and 8 mutation tests pass. Full pytest: collection error. Clean archive collection: base 0, candidate 2. Additional native reproductions and exits are in receipt.json and the named logs. Cache writes were disabled without changing test behavior.

## OCR per file

OCR delegation completed: preview exit 0, 17 reviewable of 55; rule invocation exit 0 for all 55 listed paths, including exclusions. Each returned rule group was applied; OCR supplies rules, not this verdict.

| File | Applied rule group | Assessment |
|---|---|---|
| `.github/workflows/ci.yml` | Rule Group 1: system / .github/workflows/**/*.{yaml,yml} | Applied workflow security/correctness/reliability rules: explicit contents:read, persist-credentials:false, no PR-title interpolation, SHA pins, path filters and stable jobs match design; actionlint passes. R07 concerns scan admission, not YAML syntax. Actual hosted execution not run. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/CMD-GATE-ALL.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/CMD-RED-green-with-tools.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/CMD-RED-green.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/CMD-WORKFLOW-CHECK.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/PROC-GATE-TOOL-QUALIFY.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/commands.md` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/negative-controls.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/receipt.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/supply-scan.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/tool-binding.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/CMD-RED.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/PROC-GATE-TOOL-QUALIFY.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/baseline-39.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/actionlint.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/full-suite-pytest-mutation-only.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/full-suite-pytest-no-mutation.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/full-suite-pytest-perdir.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/full-suite-pytest-pristine-HEAD.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/full-suite-unittest-verbose.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/full-suite-unittest.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/full-suite.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/gate.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/green.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/prevention-negative.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/prevention-positive.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/qualify-coverage.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/qualify-mutation.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/qualify.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/receipt.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/bug1/red.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/commands.md` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/lease-validation.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/legacy-gate.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/legacy-workflows.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/mutation-diagnostic.txt` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/receipt.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/receipt.md` | Rule Group 1: system / default | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/runs.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/test-diff.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/test-sha256.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/tool-binding.json` | Rule Group 1: system / **/*.{json,json5} | Applied JSON-key or generic evidence rules as returned; checked historical versus current candidate claims, statuses and sanitization. Historical red/tool-gap logs are not current assurance. No literal home paths found in changed committed files. |
| `tools/ci/coverage/backend.sh` | Rule Group 1: system / default | Applied generic rules: real coverage/pytest, fixed rcfile, missing tool guards and fresh report deletion inspected; current controls pass. R03 covers source/report binding across the adapter boundary. |
| `tools/ci/coverage/evaluate.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Applied Python rules; real native stale-same-file control proves R03; missing file/empty denominator controls pass. |
| `tools/ci/gate.sh` | Rule Group 1: system / default | Applied generic shell correctness/resource/security rules; inspected callers/hooks and tested 0 PASS/no-tree, 1 FAIL including child exit 3, 2 usage, 3 missing-tool GAP. Selection parity verified by suite. |
| `tools/ci/mutation/backend.sh` | Rule Group 1: system / default | Applied generic rules; isolated git archive observed, but cleanup fails (R02), export status unbound (R04), and whole-file scope produces R05/R06. |
| `tools/ci/mutation/evaluate.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Applied Python rules; native and truncated-inventory reproductions establish R04/R05/R06. Threshold arithmetic itself matches 70%; source scope/completeness do not. |
| `tools/ci/tests/coverage/control.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Applied Python rules; tiny two-branch native coverage fixture is purposeful and both returns are measured. No introduced defect. |
| `tools/ci/tests/coverage/test_backend_adapter.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Manually reviewed despite preview exclusion, applying returned Python rules. Real native tools and isolated repos used; duplicate imports cause R01. Edge controls omit partial inventory, same-file stale data, mixed module scope and cleanup cases recorded in findings. |
| `tools/ci/tests/coverage/test_native_coverage.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Manually reviewed despite preview exclusion, applying returned Python rules. CLI probes use admitted bindings, temporary mutmut config and bounded subprocesses; repaired probes and drift checks pass. Membership assertions are supplementary and do not alone prove native correctness. |
| `tools/ci/tests/mutation/test_backend_adapter.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Manually reviewed despite preview exclusion, applying returned Python rules. Real native tools and isolated repos used; duplicate imports cause R01. Edge controls omit partial inventory, same-file stale data, mixed module scope and cleanup cases recorded in findings. |
| `tools/ci/tests/mutation/test_native_mutation.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Manually reviewed despite preview exclusion, applying returned Python rules. CLI probes use admitted bindings, temporary mutmut config and bounded subprocesses; repaired probes and drift checks pass. Membership assertions are supplementary and do not alone prove native correctness. |
| `tools/ci/tests/test_gate.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Manually reviewed despite preview exclusion; exact legacy area/job sets updated to include product areas while preserving legacy checks. Full top-level suite passes. |
| `tools/ci/tests/test_product_gate.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Manually reviewed despite preview exclusion. Command-protocol Gradle/cfn-lint fixtures and recursion-prevention stub are explicit, not hidden native qualification. Real pytest excludes deployed tests; behavioral success/failure/missing-tool/path cases pass. |
| `tools/ci/tests/test_workflows.py` | Rule Group 1: system / **/*.{py,pyi,ipynb} | Manually reviewed despite preview exclusion; exact legacy area/job sets updated to include product areas while preserving legacy checks. Full top-level suite passes. |

## Evidence limits and capability gaps

Reverify: not applicable — interpreted CI scripts/tests and workflow config; no compiled-binary claim. BRAN unavailable: no native policy.

Used scan-software-supply-chain skill to inspect the two new action admission conclusions. No demonstrated malware/credential finding or confirmed reachable advisory is asserted. Workflow disables optional caches and pins exact SHAs; those facts do not cure expired advisory data or independently reproduce source reachability claims.

Existing hygiene/path regression suite passed; changed committed files contain no literal absolute user-home path shapes. No credentials accessed. This is not a whole-history secret audit or export approval. Review logs sanitize local roots to placeholders.

- **BRAN_UNAVAILABLE**: No native .bran/policy.yaml. Ordinary repository inspection used; no equivalent BRAN claim.
- **SUPPLY_SCAN_ADMISSION_INDETERMINATE**: R07: recorded expired advisory data. This session did not acquire action sources, access GitHub, refresh scanners or independently rerun the external action scans. Exact action SHAs match workflow and receipt; source reachability claims remain author evidence.
- **ANDROID_COVERAGE_COMPATIBILITY_GAP**: Carried from author; no Android tree/report task. Not closed by no-tree gate PASS.
- **ANDROID_MUTATION_COMPATIBILITY_GAP**: Carried from author; no admitted Android native mutation execution.
- **SHELL_GATE_CAPABILITY_GAP**: Shell coverage/mutation not established; ordinary gate tests are not a substitute.
- **CFN_LINT_NATIVE_QUALIFICATION_PENDING**: No actual backend template; command fixtures are not native SAM qualification.
- **MUTMUT_VENV_BACKEND_DEPS**: Real backend runtime qualification remains B01 work; generic native fixture qualification was rerun here.

## Developer feedback

- **G01-REVIEW-DX-01**: Top-level unittest and separately discovered native suites both pass while whole-tree pytest fails. Preserve whole-tree collection as a distinct regression check. Evidence: pytest.log; collection-and-exits.log.
- **G01-REVIEW-DX-02**: Passing native qualification fixtures do not cover report completeness or changed-scope correctness. Add same-file and partial-inventory failure stimuli using native outputs. Evidence: coverage-repro.log; mutation-repro.log; mutation-scope-repro.log.
- **G01-REVIEW-DX-03**: Measured full gate 41.412 s, top-level unittest 32.712 s, qualification 15.092 s. No engine/device/browser run; engine reliability repetition not applicable. Evidence: commands.json.
- **G01-REVIEW-DX-04**: Native mutation completion leaks its archive despite leaving the source checkout untouched; cleanup needs its own assertion. Evidence: mutation-repro.log.

Return all seven findings to the parent for its one bounded repair and deterministic closure. No acceptance, issue closure, publication, merge or second review authorized by this receipt. Findings are not filed as GitHub issues.

No candidate edits, candidate commits, pushes, branch changes, GitHub access, credentials, AWS, adb, installs or deployments. Disposable native fixture repositories were created only to run required verification/reproducers; targeted reproduction roots were cleaned. No unrelated scratch directories were removed.

Receipt and exact log hashes: `receipt.json`. Review is complete; stopped without repairs.
