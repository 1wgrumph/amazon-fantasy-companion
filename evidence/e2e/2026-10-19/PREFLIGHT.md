# P2-X10 preflight results (preparation unit, issue #44)

Observed 2026-10-20T13:09Z on branch `afc/p2-x10-e2e` at
`350ef51a6f10e89f257134642cfd67410bdd73fd` (origin/main baseline).
Preparation only: no device command ran (stick leased to P2-X11 and
reserved for C3/P2-X09 2026-10-22T23:30Z to 2026-10-23T03:30Z), no AWS
mutation, no live scenario executed. `live_claim: false` throughout.

| # | Check | Command | Exit | Result |
|---|---|---|---|---|
| PF-1 | Source revision | `git rev-parse HEAD && git branch --show-current && git status --short` | 0 | Observed: `350ef51a6f10e89f257134642cfd67410bdd73fd`, branch `afc/p2-x10-e2e`, clean at probe time |
| PF-2 | Toolchain | `python3.12 --version && python3.12 -m pytest --version` | 0 | Observed: Python 3.12.3, pytest 8.4.2 |
| PF-3 | Backend suite | `bash tools/ci/gate.sh backend` | not run | PENDING: not run in this preparation unit; the live unit must run it in the gate venv. A bare host pytest is not a substitute (see PF-4 note) |
| PF-4 | Deployed suite | `python3.12 -m pytest backend/tests/deployed -v --junitxml=evidence/e2e/2026-10-19/deployed.xml` | 2 (collection) | GAP (environment): collection fails on the bare host interpreter with `ModuleNotFoundError: No module named 'moto'` from `backend/tests/conftest.py`; test deps are pinned in `backend/requirements-dev.txt` for the gate/CI venv. Also `AFC_DEPLOYED_API_URL` is unset, so even with deps every case would be NOT_RUN. Not a pass; the live unit runs PF-4 in the provisioned venv with the stack ApiUrl |
| PF-5 | AWS session | `aws sts get-caller-identity --profile afc-dev` | 255 | OWNER_DECISION_REQUIRED: session expired (`Your session has expired. Please reauthenticate`). Exact owner command: `aws login`. CLI present: aws-cli 2.38.0 (exit 0 for `--version`) |
| PF-6 | Endpoint + deployed commit | CMD-STACK-OUTPUTS / CMD-DEPLOYED-COMMIT (see RUNBOOK PF-6) | not run | PENDING: blocked by PF-5; run after owner `aws login`, before the live window |
| PF-7 | App identity on stick | dumpsys package identity (see RUNBOOK PF-7) | not run | PENDING: stick not leased to this unit; `adb` is also not on PATH on this host. Run only at or after 2026-10-23T03:30Z release |
| PF-8 | Event 401873010 re-check | CMD-ESPN-CAPTURE live capture + verify (see RUNBOOK PF-8) | not run | PENDING-LIVE: live window not open; the frozen binding targets `--date 20261022 --event 401873010`. Do not capture early and relabel |
| PF-9 | Replay fixture integrity | `python3.12 spikes/sp5-espn-feed/capture.py verify` | 0 | Observed: `verify: OK` over `backend/fixtures/replay/` (14 games, `provenance: historical-replay`). Logic-readiness only, not live evidence |
| PF-10 | Gates (preparation-time) | `bash tools/ci/gate.sh hygiene` | 0 | Observed pass before authoring (all areas not-applicable except hygiene). Docs gate and post-author exits are recorded in the author return, not pre-claimed here |

## Typed blockers

- OWNER_DECISION_REQUIRED (PF-5/PF-6): owner runs `aws login`; no
  credential access by the agent.
- PENDING (PF-3/PF-4): provisioned gate venv + `AFC_DEPLOYED_API_URL`
  required; missing `moto` on the bare host is an environment gap,
  never a pass.
- PENDING (PF-7): stick lease (P2-X11 now; C3/P2-X09
  2026-10-22T23:30Z to 2026-10-23T03:30Z) plus missing `adb` on PATH.
- PENDING-LIVE (PF-8, S1–S5): live window opens for X10 at or after
  2026-10-23T03:30Z; depends on P2-X09 completing first.
