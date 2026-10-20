# Amazon Fantasy Companion

A Fire TV fantasy-football companion built for the Build, Ship, Shape:
Amazon Developer Hackathon 2026. While NFL games are on, it follows the
viewer's fantasy starters, shows a lineup panel with live fantasy points,
and raises alerts for moments that matter to those starters (red-zone
trips, player scores, close late games), with a Watch action that hands
off to a verified provider app route where one exists.

The system has two parts:

- `tv-app/` — the Fire TV (Android/Kotlin) app: device linking, profile
  and settings, the full-screen lineup panel, and the alert presentation.
- `backend/` — an AWS SAM backend (Python 3.12 Lambda, HTTP API,
  DynamoDB): ESPN feed ingest, player matching, alert policy, the panel
  service (`GET /v1/panel`), the alert feed (`GET /v1/alerts`), and the
  provider resolver (`GET /v1/providers`).

## What it does

- Links a TV with a short-lived device code confirmed on the `/link`
  page from a phone or browser (code only; no password on the TV).
- Serves a lineup panel with one row per starter: fantasy points under
  the selected PPR or Half-PPR preset (Half-PPR is the default), game
  status, team total and progress. Unavailable values are shown as
  unavailable, never as zero, and values older than 60 seconds are
  labeled stale.
- Generates alerts only for the linked profile's starters, gated by
  enabled alert types, game-day periods, quiet hours, a per-game
  minimum gap, and a spoiler delay.
- Presents alerts inside the companion app (panel-only; see the
  limitations below), newest first, each with Watch and Dismiss.
  Dismissals and the alert cursor persist on the device.
- Launches Watch only through a verified Fire OS provider-registry
  route, honors the viewer's switching confirmation, and reports
  exactly one routing outcome per attempt.

## What it deliberately does not do

- It does not place bets, sell anything, or act on the viewer's behalf.
- It does not write to Yahoo Fantasy; any Yahoo access is read-only,
  and the selected lineup source today is manual entry (see SP-6).
- It does not guess: unmatched or ambiguous players are never matched,
  provider access is never inferred from an app merely being installed,
  and unverified provider routes are reported as gaps, not launched.
- It does not interrupt or cover provider playback with notifications
  or a picture-in-picture panel; both routes failed on the tested
  device (see SP-2 and SP-4).

## Status and known limitations

Verdicts below use the spike record's own words. A `PARTIAL` or
`FAILS` verdict means the named capability is not offered as proven.

| Spike | Verdict | What it means for this product |
|---|---|---|
| SP-1 device baseline | WORKS | The app installs and launches on the tested Fire TV stick (model AFTKM, Fire OS 8.1.8.5, API 30). See `spikes/sp1-device/VERDICT.md` ([PR #89](https://github.com/1wgrumph/amazon-fantasy-companion/pull/89)). |
| SP-2 heads-up notifications | FAILS | No heads-up banner appears over provider playback on the tested stick. Alerts are panel-only inside the app. See `spikes/sp2-notify/VERDICT.md` ([PR #109](https://github.com/1wgrumph/amazon-fantasy-companion/pull/109)). |
| SP-3 provider links | PARTIAL | Prime Video's search route opened its search screen on the stick; a live Prime Video Thursday Night Football `gameOpened` check is still pending, so `gameOpened` is not claimed for any provider. ESPN, DirecTV Stream and YouTube TV were not installed on the stick, and their routes remain gaps. See `spikes/sp3-provider-links/VERDICT.md` ([PR #110](https://github.com/1wgrumph/amazon-fantasy-companion/pull/110)). |
| SP-4 panel beside video | FAILS | No picture-in-picture or split composition works over Prime Video on the tested stick. The panel is full-screen inside the app. See `spikes/sp4-panel-video/VERDICT.md` ([PR #106](https://github.com/1wgrumph/amazon-fantasy-companion/pull/106)). |
| SP-5 ESPN feed | PARTIAL | ESPN endpoints, the capture tool, and historical replay fixtures are proven. Live update timing is not yet proven. See `spikes/sp5-espn-feed/VERDICT.md` ([PR #63](https://github.com/1wgrumph/amazon-fantasy-companion/pull/63)). |
| SP-6 Yahoo Fantasy | FAILS | The Yahoo Fantasy API returns HTTP 403 for this unapproved app even though OAuth succeeds. The selected lineup source is manual entry. See `spikes/sp6-yahoo/VERDICT.md` ([PR #100](https://github.com/1wgrumph/amazon-fantasy-companion/pull/100)). |
| SP-7 installed-app detection | PARTIAL | Shell-level installed/absent detection works on the tested stick; the disabled-state probe is unsupported from the ADB shell, and the product keeps detection off behind its support flag. See `spikes/sp7-detection/VERDICT.md`. |

Pending, not yet proven (do not read these as results):

- PENDING — X09 live end-to-end run and X10 live hardening have not
  run yet. The live flow is scheduled for the next live game window.
- PENDING — SP-3 PR 2 (live Prime Video `gameOpened`) and SP-5 PR 2
  (live ESPN timing) checks are still outstanding.
- Vega OS is a paused stretch compatibility target only. It is not
  delivered, and no Vega capability is claimed here. Fire OS is the
  primary target.

### Alexa and voice

PENDING — X11 disposition. Voice/Alexa is not offered as an
implemented-and-verified feature in this revision. The TV code keeps
voice off unless a route is verified. This section will be updated
when the X11 disposition lands; until then, treat Alexa/voice as
not offered.

## Fresh setup from a clean checkout

All paths below are relative to the repository root. Owner-supplied
inputs are called out as such; no secret values belong in this
repository.

### Prerequisites

- Git, Python 3.12 (backend), and a JDK 17 with the Android SDK
  (`ANDROID_HOME` or `ANDROID_SDK_ROOT`) for the TV app.
- `cfn-lint` for the backend gate (installed with the backend test
  environment below).
- For the hygiene gate: the `python3` that runs `tools/ci/gate.sh`
  must import PyYAML (`python3 -c 'import yaml'`). Installing the
  backend dependencies into the backend virtual environment does
  not satisfy this unless that environment is activated (so its
  `python3` is first on `PATH`). To provision the hygiene
  environment, install the pinned hygiene closure into the
  `python3` you will run the gate with:

  ```bash
  python3 -m pip install --require-hashes -r tools/ci/requirements-hygiene.txt
  python3 -c 'import yaml'
  ```

  (CI installs the same file with `python3.12`; use the
  interpreter that your `python3` resolves to. On an
  externally-managed system Python (PEP 668) that install is
  refused; run the hygiene gate with the backend virtual
  environment below activated instead — its pinned dependencies
  already include PyYAML.)
- For deployment only: the AWS CLI and SAM CLI, an AWS account, and
  a named CLI profile. This project uses profile `afc-dev` in region
  `us-east-2` and stack `afc-dev` (see `backend/samconfig.toml`).
- For device work only: a Fire TV stick with ADB debugging enabled
  on the local network, reachable with `adb connect`, and Prime
  Video signed in if provider routes are to be exercised. Device
  addresses are owner-local details and are not recorded here.

### Backend: install test dependencies and run tests

The backend gate expects a dedicated virtual environment. From the
repository root:

```bash
python3.12 -m venv "$HOME/.local/share/afc-tools/backend-tests"
"$HOME/.local/share/afc-tools/backend-tests/bin/python3.12" -m pip install --require-hashes -r backend/requirements-dev.txt
bash tools/ci/gate.sh backend
```

The backend gate runs the unit and contract suites
(`backend/tests/unit` and `backend/tests/contract`) and
`cfn-lint backend/template.yaml`. Tests under `backend/tests/deployed`
run against a deployed stack as separate procedures; they are not
part of the gate.

### Backend: deploy (owner action)

Deployment needs an authenticated AWS session and is an owner-run
step. Sign in from a normal terminal, then build and deploy from
`backend/`, tagging the stack with the deployed commit:

```bash
aws login --profile afc-dev
aws sts get-caller-identity --profile afc-dev
cd backend
sam build
sam deploy --config-env default --tags GitCommit=<full-commit-sha>
```

Record the stack's `ApiUrl` output and the deployed commit. The TV
app is built against that `ApiUrl` (next section). Full AWS and
Yahoo wiring, including known sign-in failures, is documented in
[docs/operations/aws-and-yahoo-setup.md](docs/operations/aws-and-yahoo-setup.md).

SSM parameters (owner-written; names are the `backend/template.yaml`
defaults):

| Name | Type | Holds |
|---|---|---|
| `/afc/dev/yahoo-client-id` | String | Yahoo app Client ID |
| `/afc/dev/yahoo-client-secret` | SecureString | Yahoo app Client Secret |
| `/afc/dev/yahoo-token` | SecureString | Yahoo OAuth refresh token |

Because the Yahoo app is unapproved (SP-6, FAILS), these parameters
do not make Yahoo lineups live. Leave the lineup source manual until
a later change selects Yahoo after approval.

### TV app: build, test, and install

From the repository root, with `JAVA_HOME` (JDK 17) and
`ANDROID_HOME` set:

```bash
bash tools/ci/gate.sh tvapp
```

The TV gate runs `testDebugUnitTest`, `lintDebug`, and
`assembleDebug`. To build an APK pointed at a deployed backend, pass
the recorded `ApiUrl` as a Gradle property; an empty value makes the
app show "Backend not configured":

```bash
./tv-app/gradlew -p tv-app assembleDebug -PafcApiBaseUrl=<ApiUrl>
adb connect <stick-address>
adb install -r tv-app/app/build/outputs/apk/debug/app-debug.apk
```

The stick address is owner-supplied. Accept the RSA prompt on the TV
after matching the host key fingerprint, and confirm the stick shows
as `device` in `adb devices` before installing.

### First run: link the TV (lineup entry unavailable)

1. Launch the app on the stick. It shows a short-lived device code.
2. On a phone or browser, open the deployed `<ApiUrl>/link` page and
   confirm the code shown on your own TV. Codes expire quickly and
   each code links one session only; confirm only a code on your
   own TV.
3. In Profile/Settings, pick the scoring preset (PPR or Half-PPR;
   Half-PPR is the default), the alert types, quiet hours, and
   spoiler delay, then save the profile. These controls update
   profile selections only.
4. Optionally enable "Show panel on new alert" (default on) so a new
   alert re-shows a hidden panel.

UNAVAILABLE in this revision — entering a lineup: the TV shell
offers Link, Profile/Settings, and Panel, and none of them enters
starters; the backend API likewise has no lineup-write route.
There is therefore no supported first-run procedure that
populates a lineup from a fresh install, and the panel and alerts
have no starters to follow until a lineup-write route is built.
SP-6 selected manual entry as the lineup source, but that source
is not yet enterable through the product. Do not work around this
by hand-editing stored data; no such procedure is supported or
documented here.

## Judge access

Judge access route (owner decision, 2026-10-20 — "Repo public is
enough."): this public repository,
<https://github.com/1wgrumph/amazon-fantasy-companion>, plus the
setup in this README. No separate submission access is needed to
read the source or run the host checks. The owner keeps this
route available through T_judge_access (2026-11-20).

Without the owner's Fire TV stick, a judge can:

- Read this repository: source (`tv-app/`, `backend/`), the spike
  verdicts under `spikes/`, the architecture and plans under
  `docs/plans/`, and the change history in `CHANGELOG.md`.
- Run every host check from a clean checkout with the commands in
  this README (backend gate, TV gate, docs and hygiene gates).
- PENDING — watch the demo video from the Devpost submission once
  the owner publishes it (owner upload; shots of protected
  provider video may be owner-filmed and are marked as such in
  the demo plan).

Real limits, stated plainly:

- The live TV experience needs a Fire TV stick, a deployed backend,
  and a linked profile; none of those ship inside this repository.
- The deployed backend is reachable only at the `ApiUrl` recorded at
  deploy time, and only while the owner keeps the dev stack up. It
  is not a public demo endpoint, and no credentials are provided.
- Live-game behavior (live ESPN timing, live Prime Video handoff,
  the X09 end-to-end run) can only be observed during a live game
  window; outside one, the recorded verdicts and replay fixtures are
  the evidence.
- Yahoo Fantasy lineups are not live (SP-6, FAILS), and lineup
  entry is unavailable in this revision (see First run above).
- The demo video is still PENDING: it is an owner upload linked
  from the Devpost submission once the owner publishes it. That
  pending item does not change the judge-access route above,
  which is this public repository, kept through 2026-11-20.

## Verification

From the repository root:

```bash
bash tools/ci/gate.sh backend
bash tools/ci/gate.sh tvapp
bash tools/ci/gate.sh docs
bash tools/ci/gate.sh hygiene
```

Each gate prints `PASS`, `FAIL`, or `GAP` (a required tool is
missing). A `GAP` is not a pass. The same gates run in CI.

Fresh-setup walkthrough (PROC-README-FRESH-SETUP) executed
2026-10-20 from a clean `git archive` checkout of `origin/main`
(`44a7e06`): docs, hygiene, backend and TV gates passed; the
configured TV APK installed on the Fire TV stick; the first-run
device-code link completed against the already-deployed `afc-dev`
backend; and the lineup-entry limitation above was re-verified
(no lineup-write route exists). Not re-run in that walkthrough,
and therefore not walkthrough-proven: the `sam deploy` step
itself (verified read-only against the existing stack instead),
fresh-host download of the pinned backend dependencies (the
documented virtual environment already existed on the walkthrough
host, so the hash-pinned install resolved as already satisfied),
and the owner-only steps (`aws login`, SSM parameter writes,
Yahoo app creation). The per-step
record is in
`docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-D03/fresh-setup-walkthrough.md`.

## Repository layout

- `tv-app/` — Fire TV app (Kotlin, Gradle wrapper included).
- `backend/` — SAM backend (`template.yaml`, `src/`, `tests/`).
- `spikes/` — time-boxed device and feed spikes, each with a
  `VERDICT.md`.
- `spec/` — architecture specification sources.
- `docs/` — plans, operations notes, and verification guidance.
- `tools/ci/` — the shared gate (`gate.sh`) and its checks.
- `evidence/` — captured run evidence.

## License

Licensed under the Apache License, Version 2.0. See
[LICENSE](LICENSE). Third-party notices are in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Adding the license
file prepares the already-selected Apache-2.0 terms; it does not by
itself publish this repository or change its visibility.
