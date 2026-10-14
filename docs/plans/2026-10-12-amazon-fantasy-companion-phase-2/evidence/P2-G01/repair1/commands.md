# P2-G01 repair1 verification commands (lease P2-G01-repair1, base 83603fe)

Red (before fix) / green (after fix) per finding; full logs beside this file.

| Check | Command | Exit |
|---|---|---:|
| R01 red | `python3.12 -m pytest -q tools/ci/tests` | 2 |
| R01 green | `python3.12 -m pytest -q tools/ci/tests` | 0 |
| R02 red | leak probe via `BackendMutationAdapter` + isolated `TMPDIR` | 1 leaked workdir |
| R02 green | same probe | 0 leaked workdirs |
| R03 red | stale same-file `evaluate.py` vs fresh `backend.sh` | 0 then 1 |
| R03 green | same pair | 3 then 1 |
| R04 red | truncate `mutmut-results.txt`, run `evaluate.py` | 0 (bad PASS) |
| R04 green | same | 3 GAP mismatch |
| R05 red | changed-only untested function via `backend.sh` | 0 (bad 80% PASS) |
| R05 green | same | 1 FAIL 0% scored 2/10 |
| R06 red | `LIMIT=3` + tested function via `backend.sh` | 0 (bad PASS) |
| R06 green | same | 3 `PYTHON_NONFUNCTION_MUTATION_GAP` |
| R07 red | stale DB + PASS verdicts in `supply-scan.json` | contradiction |
| R07 green | fresh DB `trivy fs` on exact pins, `supply-scan.json` updated | 0, 0 |
| unittest gate shape | `python3 -m unittest discover -s tools/ci/tests` | 0 (50 tests) |
| qualify coverage | `python3 -m unittest discover -s tools/ci/tests/coverage` | 0 (12 tests) |
| qualify mutation | `python3 -m unittest discover -s tools/ci/tests/mutation` | 0 (13 tests) |
| gate | `bash tools/ci/gate.sh` | 0 |
| workflow lint | `actionlint` | 0 |
| frozen G01T sha256 | before/after diff | unchanged |
| `git diff --check` | — | clean |
| absolute home-dir paths in change set | grep | none |

`mutmut` ran from the admitted venv first on `PATH`.
New scope-gap control also checked against pre-fix `evaluate.py`: old code
returned PASS where the new control requires `MUTATION_SCOPE_GAP`.
