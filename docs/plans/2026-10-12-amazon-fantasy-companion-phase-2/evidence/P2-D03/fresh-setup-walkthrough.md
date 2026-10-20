# P2-D03 fresh-setup walkthrough (2026-10-20)

Procedure: `PROC-README-FRESH-SETUP` (SEIT-AFC-P2-SUB-01). Clean
checkout: `git archive origin/main` at
`44a7e0695441034b7749d9d32c5f58121e071f91` extracted to a private
scratch directory; every step below ran there unless marked
device/AWS. Role: Product Implementer (Muse Code /
muse-wonder-full-1.0-contributor / medium). Device captures that
show the link code stay in private storage and are never copied
here; no device address, serial or account detail is recorded
(`<stick_serial>`).

| # | README step | Result | Evidence |
|---|---|---|---|
| 1 | Prerequisites: Git, Python 3.12, JDK 17 + Android SDK | PASS | git 2.53.0, Python 3.12.3, JDK 17 and SDK present under the documented tool paths |
| 2 | Hygiene env: `python3 -c 'import yaml'` | PASS | import OK (PyYAML 6.0.3) for the `python3` used by the gate; no install needed on this host, so a fresh-host download of `tools/ci/requirements-hygiene.txt` was not exercised |
| 3 | Backend venv + `pip install --require-hashes -r backend/requirements-dev.txt` | PASS (limited) | venv create exit 0; pip exit 0 but every requirement "already satisfied": the documented venv pre-existed on this host, so fresh download/install is **not** proven by this run |
| 4 | `bash tools/ci/gate.sh backend` | PASS | `1029 passed, 3 skipped`; `gate: backend: PASS checks completed` |
| 5 | `aws login --profile afc-dev` | OWNER_STEP | Not run (owner-only sign-in). The existing session was valid: `aws sts get-caller-identity --profile afc-dev` returned the `afc-dev` user |
| 6 | `sam build` / `sam deploy` | OWNER_STEP (verified, not re-run) | Deploy step: verified against the existing stack, not re-run. `aws cloudformation describe-stacks --profile afc-dev`: stack `afc-dev` `UPDATE_COMPLETE`, `ApiUrl` output present (value as recorded in P2-L03 evidence), `GitCommit` tag `7da6187b5a57ee80887ef84301ff99a3592bacb6`. SAM CLI 1.169.0 present |
| 7 | SSM parameters (Yahoo client id/secret/token) | OWNER_STEP | Owner-written; values not read or written. Yahoo stays non-live per SP-6 FAILS, lineup source manual, as the README states |
| 8 | `bash tools/ci/gate.sh tvapp` (JAVA_HOME/ANDROID_HOME set) | PASS | `gate: tvapp: PASS checks completed` (Gradle under the host-gradle flock) |
| 9 | Build configured APK `-PafcApiBaseUrl=<ApiUrl>` | PASS | BUILD SUCCESSFUL; `app-debug.apk` sha256 `01cc1be16d5353bd43eb871fc6855a9d31d9757b2bf723c72dc7162c42ad71d3` (identical to the independent PR #129 merge-commit build the same day) |
| 10 | `adb connect` + `adb devices` shows `device` | PASS | Connected; stick listed as `device` (serial not recorded) |
| 11 | `adb install` the APK | PASS after doc fix | The stick already carried the app, so installation used `-r` (Success). README said plain `adb install`, which fails over an existing install; fixed to `adb install -r` (see README changes) |
| 12 | First run 1: app shows a short-lived device code | PASS | After `pm clear` (fresh-install state) the Link screen showed a code with its expiry and the `<ApiUrl>/link` instruction (capture kept private, code never recorded) |
| 13 | First run 2: open `<ApiUrl>/link` and confirm the code | PASS | `GET /link` HTTP 200, page title `Link your TV`; confirmation submitted to the same `POST /v1/link/confirm` endpoint the page uses, for the synthetic dev test profile only: HTTP 200 `{"state": "linked"}`; the TV left the Link screen and loaded the profile. The browser form itself was not driven; the endpoint and TV poll were |
| 14 | First run 3: Profile/Settings controls + Save | PASS | Profile loaded after linking; controls responded (scoring preset halfPpr, alert types, panel and confirm toggles visible); team/league set/clear + Save profile exercised the same day under the fixture rerun and restored |
| 15 | First run 4: "Show panel on new alert" (default on) | PASS | Shown `on (this TV only)` on the fresh install, matching the documented default |
| 16 | Lineup entry UNAVAILABLE statement | PASS (statement accurate) | No lineup-write route exists (`grep` of `backend/src/api/openapi.yaml` and handler: no `/v1/lineup` write); TV shell offers Link, Profile/Settings, Panel only, as documented |
| 17 | Verification gates docs + hygiene | PASS | `gate: docs: PASS` and `gate: hygiene: PASS` in the fresh checkout (private `TMPDIR`) |
| 18 | LICENSE (Apache-2.0, SD-035) | PASS | Standard Apache License text present at repo root |
| 19 | Judge access publication (Devpost, demo, repo access route), kept through 2026-11-20 | OWNER_STEP | Not run. README correctly records this as PENDING owner-supplied access with the retention date; repository-public status alone is not judge-access publication |

## README changes made by this walkthrough

1. TV install command: `adb install tv-app/app/build/outputs/apk/debug/app-debug.apk`
   → `adb install -r tv-app/app/build/outputs/apk/debug/app-debug.apk`
   (plain install fails when the app is already on the stick).
2. Verification section: the `GAP PROC_README_FRESH_SETUP_NOT_RUN`
   paragraph is replaced by the walkthrough record above, keeping
   the not-proven items explicit (deploy itself, fresh-host
   dependency download, owner steps).

No other README instruction was found wrong. No product source
other than `README.md` was changed.

## Device and backend restoration

The walkthrough installed over and relinked the stick. Before:
found APK sha256
`1d80c6822182399794bbe4cec27198a0a31da58e3533ebcb9acf431a2729b988`,
no team/league selected, panel ON, own alerts and lineup absent,
Prime Video process running. After: found APK reinstalled and
verified byte-identical by pulled-APK sha256; final Panel frame
byte-identical to the before capture; profile saved with no
team/league; own fixture alert, lineup and statistics removed;
Prime Video force-stopped (it self-respawned once, as observed
before this run; stopped again as the last device action).

## Verdict for PROC-README-FRESH-SETUP

Executed with the recorded limits. The undocumented-dependency
and false-capability failure modes did not occur: every
agent-runnable README step completes as documented (after the
one-character install fix). Remaining typed items, never a pass:
`OWNER_STEP` rows 5–7 and 19, and fresh-host dependency
*download* (rows 2–3), which this pre-provisioned host cannot
prove.

## Independent verification addendum (2026-10-20, second run)

A second clean-checkout run (same `git archive` method) reproduced
rows 1, 4, 8, 9 and 17: backend gate PASS (1029 passed, 3
skipped), TV gate PASS, configured APK built, docs and hygiene
gates PASS. Two corrections to the table above:

- Row 2 as a provisioning *command* FAILS on this host:
  `python3 -m pip install --require-hashes -r
  tools/ci/requirements-hygiene.txt` exits 1 with
  `error: externally-managed-environment` (PEP 668; the host
  `python3` is the system interpreter). PyYAML was already
  importable, so the gate itself ran; the documented install
  command did not. README now records the activated-backend-venv
  route for PEP 668 hosts. Classify row 2: command FAIL
  (doc defect, fixed), gate outcome PASS.
- Row 3 fresh download: in the second run the hash-pinned
  backend install did download and install (pip exit 0, full
  package list), so fresh backend-venv provisioning is proven;
  only the hygiene-closure download remains unproven.
- `gate.sh` requires a git work tree: run inside a bare
  `git archive` extraction it exits 2 (`fatal: not a git
  repository`). A `git clone` checkout is unaffected; the
  archive scratch needed `git init` before any gate ran.
