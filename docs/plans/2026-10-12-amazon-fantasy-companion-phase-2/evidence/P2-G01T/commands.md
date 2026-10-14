# Command / exit ledger

Repository-root commands; `$HOME` replaces the actual home directory. Reads
and probes repeated during qualification retain the same outcomes. Test child
commands and their exact options are frozen in the test sources. `runs.json`
and `tool-binding.json` preserve executed test/probe argv and actual exits.

| Command | Exit |
|---|---:|
| `pwd`; `git status --short`; `git branch --show-current`; `git rev-parse HEAD` | 0 each |
| `rg --files -g AGENTS.md -g CLAUDE.md -g '!node_modules' -g '!vendor'` | 0 |
| `cat $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.7/skills/implementer/SKILL.md` | 0 |
| `cat $HOME/.claude/skills/write-tests/SKILL.md` | 0 |
| `cat $HOME/.codex/skills/create-lean-skill/SKILL.md` | 0 |
| `cat $HOME/.codex/plugins/cache/ponytail/ponytail/5.1.0/skills/ponytail/SKILL.md` | 0 |
| `cat $HOME/alphazede/AGENTS.md` | 0 |
| `ls -la AGENTS.md CLAUDE.md` | 2 (neither root file exists) |
| `cat P2/implementation.json P2/seit.json` | 0 |
| `cat P2/amazon-fantasy-companion-phase-2-technical-plan.md P2/design.md P2/specialists/slice-graph.md` | 0 |
| `git -C <controller> rev-parse HEAD`; `cat <controller>/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json` | 0 each |
| `rg --files tools/ci .github/workflows` | 0 |
| `cat tools/ci/check.sh`; `cat tools/ci/tests/test_check.py` | 1 each (initial nonexistent-name probes, corrected to gate.sh/test_gate.py before execution) |
| Python JSON extraction of slice, commands, proof rows, gate tool plan and controller lease (three invocations) | 0 each |
| `rg -n -A 12 -B 5 'CONTRACT-AFC-P2-GATE-AREAS\|PROC-GATE-TOOL-QUALIFY\|P2-G01T\|P2-G01\|CMD-RED' P2/design.md P2/amazon-fantasy-companion-phase-2-technical-plan.md P2/specialists/slice-graph.md` | 0 |
| `cat tools/ci/gate.sh tools/ci/tests/gate_support.py tools/ci/tests/test_gate.py tools/ci/tests/test_workflows.py .github/workflows/ci.yml` | 0 |
| `cat tools/ci/tests/test_gate_isolation.py tools/ci/check_workflows.py tools/ci/tests/test_check_paths.py`; bounded `sed` reads of gate.sh/test_gate.py | 0 |
| Focused `rg -n` reads of gate contract/design/technical plan | 0 |
| `git -C <controller> show 3ae4cad:docs/plans/2026-10-11-amazon-fantasy-companion/journey.json` piped to lease JSON extraction | 0 |
| `python3 -m unittest discover -s tools/ci/tests -v` before changes | 0 (39/39, 15.038s) |
| `python3.12 -m pytest --version`; `java -version` | 0 each (pytest 8.4.2; host JDK21, not Android/JDK17 qualification) |
| `python3 -m coverage --version` | 1 (`No module named coverage`) |
| `python3.12 -m coverage --version` | 0 (7.13.5) |
| `python3 -m diff_cover --version`; `python3.12 -m diff_cover --version`; `python3.12 -m mutmut --version` | 1 each |
| `cfn-lint --version` | 127 |
| `command -v diff-cover`; `command -v mutmut` | 1 each |
| `python3.12 -m coverage run --help`; `python3.12 -m coverage xml --help`; `python3.12 -m coverage report --help` | 0 each |
| Python edits adapting legacy area assertions | 0 |
| Direct shell subprocess controls `bash -c 'exit 0'`; `bash -c 'exit 1'` | 0; 1 (control driver exit 0) |
| `python3 -m unittest discover -s tools/ci/tests/coverage -v` | 1 (3 native controls PASS, diff_cover GAP) |
| `python3 -m unittest discover -s tools/ci/tests/mutation -v` | 1 (mutmut GAP) |
| Python test/output recorder | 0 (child exits below and in runs.json) |
| `python3 -m unittest discover -s tools/ci/tests -p 'test_check*.py' -v` | 0 (16 tests) |
| `python3 -m unittest discover -s tools/ci/tests -p 'test_gate*.py' -v` | 0 (19 tests) |
| `python3 -m unittest discover -s tools/ci/tests -p test_workflows.py -v` | 0 (4 tests) |
| `python3 -m unittest discover -s tools/ci/tests/coverage -v && python3 -m unittest discover -s tools/ci/tests/mutation -v` | 1 (second half short-circuited; separate diagnostic executed) |
| CMD-RED: `python3 -m unittest discover -s tools/ci/tests -v` | 1 (50 tests, 24 new behavioral assertion failures, zero errors) |
| Python coverage runtime/package/binary hash extraction (two invocations) | 0 each |
| `git diff --stat`; `git diff -- tools/ci/tests/test_gate.py tools/ci/tests/test_workflows.py`; `git status --short`; `ls P2/evidence/P2-G01T` | 0 each |
| `cat P2/evidence/P2-G01T/runs.json` before recorder finished | 1 (not yet written; subsequently available) |
| Python active lease revalidation, frozen hash generation and owned cache cleanup | 0 |
| `git add` exact six test paths | 0 |
| `git diff --cached --binary`; Python tool binding and diff digest recorder | 0 |
| Python typed receipt authoring | 0 |
| `git add P2/evidence/P2-G01T` | 0 |
| `python3 tools/ci/check_paths.py`; `python3 tools/ci/check_workflows.py .github/workflows/`; `python3 tools/ci/check_docs.py` | 0 each |
| `git diff --cached --check` before receipt normalization | 2 (unittest output trailing spaces and patch blank context; test source clean) |
| `git diff --cached --stat` | 0 |
| Python receipt normalization and removal of redundant patch copy | 0 |

`P2` means `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2`.
Final verification and commit results are appended after execution.

Final pre-commit verification: frozen-file and staged-scope/lease self-check exit 0;
`git diff --cached --check`, `python3 tools/ci/check_paths.py`,
`python3 tools/ci/check_docs.py` each exit 0 after evidence normalization.
The red commit uses `git commit --no-verify`; its exit/SHA are returned to the controller.
No full gate rerun after CMD-RED; no native Android build or independent review.
