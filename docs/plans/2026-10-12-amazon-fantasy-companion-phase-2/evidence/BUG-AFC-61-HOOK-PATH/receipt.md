# Issue #61 — local hook backend environment

- Packet: Bug-triager Implementer, Codex CLI / GPT-6.1 Sol / high, profile
  `bug-triager`; bounded worker, no nested orchestration or route changes.
- Baseline: `4e9013a15752e4a45e39e4977ac3d3f6b706daed` (`origin/main`), branch
  `afc/bug-61-hook-path`. [Issue #61](https://github.com/1wgrumph/amazon-fantasy-companion/issues/61).
- Next action: commit the verified write set with hooks enabled and return to
  the orchestrator for independent review and landing. Worker checks passed.
- BRAN: unavailable (no native policy). Reverify: not applicable — shell/Python
  change, no compiled-binary claim. Independent review/OCR belongs to the
  orchestrator's subsequent reviewer; no review or assurance PASS claimed here.

## Cause and scope

Valid tooling defect, no new trust boundary or data recovery. Shared hook
entrypoints introduced in `a460e88`; backend checks added in `dfb12ca` resolve
`python3.12` from ambient PATH. The environment assumption became observable
once backend tests imported moto. Prior receipts explicitly exported the venv,
which concealed the bare-shell case. The original backend requirement
AC-AFC-P2-GATE-01 requires missing tools to produce a GAP, not a failing test.
No evidence attributes the escape to a particular model or review verdict.

The one location source is
[the deployed-pin receipt](../BUG-AFC-L02-DEPLOYED-PIN-001/receipt.md), which names
`$HOME/.local/share/afc-tools/backend-tests/bin`. No existing override was found.
The gate now prepends that bin for local backend checks, checks its interpreter
and test imports, and reports a named GAP plus a quoted provisioning command
using the existing hash-pinned `backend/requirements-dev.txt`. Local tool
lookup also appends `$HOME/.local/bin`, needed for uv and cfn-lint with a system
PATH. `CI=true` or `GITHUB_ACTIONS=true` retains ambient tool selection.

Reach: the shared gate, both unchanged hook callers, existing product-gate
protocol fixtures (explicit CI mode), new hook/environment regressions, and
Unreleased changelog. No backend, TV app, workflow, dependency or gate check
was changed or skipped.

## Verification

Method: test (test-engineering → write-tests). Five tests use real installed
pytest/cfn-lint and tiny import/test corpora in isolated temporary repositories;
no AWS, network, server, engine or shared mutable resource. On hosts without
the local venv, local entrypoint tests require the specified provisioning GAP;
this host exercises actual success and actual backend-test rejection.

| Command (each bounded by `timeout 600`) | Exit | Evidence |
| --- | --- | --- |
| Baseline backend reproduction, with user tools available but no venv on PATH | 1 | Saved red output shows raw `ModuleNotFoundError: boto3`, backend FAIL; system-only PATH also showed missing cfn-lint (exit 3). Issue #61 records the equivalent missing-moto failure. |
| `python3 -m unittest discover -s tools/ci/tests -p test_hook_path.py -v` with baseline gate | 1 expected | [red.txt](red.txt); same five test IDs, raw missing dependency reproduced. |
| Same command with fixed gate, rerun after resume | 0 | [green.txt](green.txt): all five tests pass. `TMPDIR` used an isolated directory on `/var/tmp` to avoid the prior `/tmp` quota failure. |
| First minimal-PATH full gate attempt | 1 | [first-path-gate.txt](first-path-gate.txt): captured red-log whitespace failed hygiene; backend passed. Evidence whitespace was normalized before the successful rerun. |
| `env PATH=/usr/bin:/bin bash tools/ci/gate.sh` (with isolated `TMPDIR` and `PYTHONDONTWRITEBYTECODE=1`) | 0 | [minimal-path-gate.txt](minimal-path-gate.txt): spec, docs, hygiene (66 tests), tvapp (no tree), backend (379 tests) PASS. No activation or backend PATH export. |

## Issue acceptance

| Acceptance box | Evidence/status |
| --- | --- |
| A bare `git commit` / `git push` with a green tree passes on a host where the documented backend test environment exists | Both actual hook scripts exit 0 under system-only PATH in the regression. Worker closeout commits with hooks enabled; no remote push authorized. |
| Missing environment names path and provisioning instead of raw import error | Absent and incomplete directories under an isolated HOME with spaces: exit 3, backend GAP, environment path and venv/hash-pinned pip command; no raw import error. |
| CI behavior unchanged | Both CI flags retain ambient missing-tool GAP; existing CI-mode success/failure/selection protocol tests retained; workflow untouched. |

Prevention: hygiene discovers the new tests automatically; they remove the venv
from PATH, execute both hook entrypoints, check missing/incomplete environments,
and require a deliberately failing backend test to remain blocking. No gate
assertions were weakened. No push, PR, issue mutation or branch change is
within this worker's authority. PR #TBD remains for the landing orchestrator.

Resume closeout: logs use `$HOME`/`$REPO` placeholders; no untracked
`__pycache__` files remain. All changes are limited to `tools/ci/`,
`CHANGELOG.md`, and this evidence directory. The interrupted run's red evidence
was preserved; only green verification and the full minimal-PATH gate were rerun.
