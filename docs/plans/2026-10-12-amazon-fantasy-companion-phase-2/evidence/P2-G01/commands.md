# Command / exit ledger (P2-G01)

Repository-root commands. `$HOME` replaces the home directory; `P2` means
`docs/plans/2026-10-12-amazon-fantasy-companion-phase-2`.

| Command | Exit |
|---|---:|
| `git status --short`; `git log`; reads of receipt, implementation.json, seit.json, design.md, gate.sh, hooks, ci.yml, tests | 0 each |
| `git ls-remote --tags` and `git clone --depth 1 --branch <tag>` of actions/setup-java and actions/setup-python into session scratch | 0 each |
| `clamscan -r` on both action trees | 0 each |
| `gitleaks dir --redact` on both trees | 1 each (entropy-only false positives, see supply-scan.json) |
| `trivy fs --offline-scan --skip-db-update --scanners vuln` on each package-lock.json | 0 each |
| `bash tools/ci/gate.sh tvapp backend` after gate edit | 0 |
| `python3 tools/ci/check_workflows.py .github/workflows/`; `actionlint` | 0; 0 |
| `python3 -m unittest discover -s tools/ci/tests -v` (before tool install) | 0 (50 tests) |
| Negative control gate run in scratch repo (gradlew exit 3, pytest zero collected) | 1 (both FAIL) |
| Frozen test sha256 comparison against P2-G01T/test-sha256.json | 0 (10/10 match) |
| `bash tools/ci/gate.sh` | 0 |
| `python3.12 -m mutmut --version`; `python3.12 -m diff_cover --version` | 1; 1 |
| `diff-cover --version`; `cfn-lint --version` | 0; 0 |
| mutmut fixture experiment in scratch (`mutmut run`, `export-cicd-stats`, `results`) | 0 each |
| diff-cover fixture experiment in scratch | 0 |
| Coverage adapter controls `-p test_backend_adapter.py` | 0 (6 tests) |
| Sanity mutation (unmapped check disabled), rerun, restore | 1 (expected), restored |
| Mutation adapter controls `-p test_backend_adapter.py` | 0 (6 tests) |
| `python3 -m unittest discover -s tools/ci/tests -v` (after tool install) | 0 (50 tests) |
| `python3 -m unittest discover -s tools/ci/tests/coverage -v` | 1 (frozen diff_cover probe only) |
| `python3 -m unittest discover -s tools/ci/tests/mutation -v` | 1 (frozen mutmut probe only) |
| `bash tools/ci/gate.sh` | 0 |
| `git commit` (normal pre-commit hook) -> dfb12ca | 0 |
