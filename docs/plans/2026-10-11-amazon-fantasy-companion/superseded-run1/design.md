---
type: design
status: complete
lifecycle: AFC-2026-10-11
technical_plan: amazon-fantasy-companion-technical-plan.md
---

# Amazon Fantasy Companion — Design

The design realizes `amazon-fantasy-companion-technical-plan.md`. It is the
smallest system that shows every retained experience item on the owner's
stick before T_deadline: a thin Kotlin TV app that only renders and launches,
and a small AWS serverless backend that does all fetching, matching and
policy (issue #1 §Lightweight device design: "keep API aggregation, full-game
monitoring, cross-provider matching ... on the backend"). Build order is
contract-first: wave 1 freezes every shared name (API schema, GameEvent,
alert, launch target, provider registry, panel state, gate entrypoint) as
code stubs, so later lanes build in parallel against fixed interfaces.

Views: `views/views.json` (MODEL-AFC-V1 context/boundary, V2 use cases, V3
operational flow, V4 CI/CD gate flow; Systems Modeler,
`specialists/systems-modeler-receipt.md`).

## Design lenses

These lens names are the only values slices may cite in `design_lenses`.

| Lens | Question it answers |
|---|---|
| Contract-first | Does the slice build against a frozen contract without changing it? |
| Device integration | Does it hold on the real stick, with evidence captured on the device? |
| Data ingestion | Is external data validated, deduplicated, corrected and labeled when stale or replayed? |
| Personalization | Does the customer's selection and setting decide the outcome? |
| Honest outcomes | Are unknown, unavailable, stale, replay and sample states shown as such? |
| Security controls | Are secrets, tokens and trust boundaries kept where the design puts them? |
| Lightweight TV | Is device work minimal (off main thread, row-level redraw, no idle polling)? |
| Spec discipline | Does the specification pass its lint and rebuild byte-identically? |
| Parallel-safe CI | Is the check deterministic, path-filtered, pinned and safe to run concurrently? |
| Lean skill | Is the skill within skill_size_max, tested on a matching and non-matching request, with overflow in references? |
| Developer feedback | Does the work carry a developer_feedback section the Scribe can ingest? |
| Owner boundary | Does the work stop at owner-only actions and conditionals C1..C14? |

## Repository layout (target)

```
README.md                         setup, credits, limitations, judge access (S36)
THIRD_PARTY_NOTICES.md            gridmarket MIT notice, starter MIT-0, footage credits (S06, S36)
.githooks/pre-commit, pre-push    call tools/ci/gate.sh (S09)
.github/workflows/ci.yml          calls tools/ci/gate.sh per area (S09)
tools/ci/gate.sh                  gate entrypoint (CONTRACT-AFC-GATE, S09)
tools/ci/check_paths.py           rule-12 shape scan + credential patterns (S09)
tools/spec_build.py, spec_lint.py, azdiagram/, tests/, pyproject.toml, uv.lock   spec kit (S06)
skills/spec-author|spec-diagram|spec-lint/SKILL.md                              spec kit skills (S06)
spec/template/                    gridmarket template (S06)
spec/amazon-fantasy-companion/    D1 section sources + figures (S19, S35)
spec/Amazon-Fantasy-Companion-Specification.md   built D1 (S19, S35)
tv-app/                           Gradle project from AmazonAppDev/hello-world-fire-tv (S04)
  app/src/main/java/afc/companion/{MainActivity,settings,link,detect,alerts,watch,panel,player,net}/
backend/                          Python 3.12 package + AWS SAM (S05)
  template.yaml, samconfig.toml, pyproject.toml, uv.lock
  api/openapi.yaml                CONTRACT-AFC-API
  src/afc_backend/{api,auth,feed,lineup,match,policy,resolver,panel,store}/
  providers/registry.json         CONTRACT-AFC-PROVIDERS
  fixtures/espn/                  recorded ESPN responses (S16)
  tools/check_template.py         AC-AFC-SEC-03 allow list
  tests/
docs/vnv/                         Vnv guidance tree (S07)
docs/spikes/SP-<n>-<topic>.md     spike verdicts (S12..S17, S34)
spikes/sp<n>/                     throwaway spike probes
docs/developer-feedback/          observations.md, tool-summary.md, friction-log.md (S08, S39)
docs/submission/                  checklist.md, storyboard.md, clips/README.md (S37, S38)
docs/runbooks/deploy.md           backend deploy runbook (S18)
docs/evidence/                    milestone evidence indexes (integration steps)
```

The Kotlin package is `afc.companion`. Paths in committed files are
repository-relative (AC-AFC-PATH-01).

## Decisions

### DES-AFC-ARCH — Split of work between TV and backend

- The backend owns every external fetch (ESPN, Yahoo), identity matching,
  alert policy, provider resolution and fantasy scoring. The TV app owns
  settings input, app detection, notification display, the launch intent and
  the panel rendering. No secret or third-party token reaches the TV app
  (AC-AFC-SEC-01).
- Transport is HTTPS JSON to one API Gateway HTTP API. Alerts reach the TV
  by long-poll (`GET /v1/alerts?wait=` up to alert_poll_wait) only during
  enabled viewing periods (AC-AFC-MON-04). Push through Amazon Device
  Messaging is the documented alternative if SP-2 shows the long-poll service
  does not survive provider playback; adopting it is a class C owner decision
  because it needs an owner developer-console registration.
- Requirements: AC-AFC-MON-02, AC-AFC-MON-04, AC-AFC-SEC-01, AC-AFC-LW-01.
- Lenses: Contract-first, Lightweight TV, Security controls.

### DES-AFC-TV — TV app structure (Fire OS, Kotlin, Compose)

- Starter `AmazonAppDev/hello-world-fire-tv` (MIT-0) is imported into
  `tv-app/` after scan-software-supply-chain; `minSdk` 25 (min_sdk);
  `targetSdk` per the starter unless SP-1 shows the stick needs lower.
- Dependencies limited to: Jetpack Compose (starter), AndroidX Media3
  ExoPlayer (Mode A only), OkHttp, kotlinx.serialization. Gradle wrapper
  checksum is verified at import.
- Components and their packages: `settings` (ProfileSettings, DataStore
  persistence, AC-AFC-CTRL-01..03), `link` (device-code screen,
  AC-AFC-PROF-01), `detect` (AppDetector over allow-listed packages,
  AC-AFC-PROF-03), `alerts` (AlertService foreground service and
  AlertNotifier, AC-AFC-ALERT-04, AC-AFC-MON-04), `watch` (WatchLauncher,
  AC-AFC-WATCH-02, -03), `panel` (LineupPanel, AC-AFC-PANEL-01..04), `player`
  (CompanionPlayer, AC-AFC-PANEL-02, -05), `net` (API client generated by hand
  from CONTRACT-AFC-API).
- The S04 skeleton owns `AndroidManifest.xml`, `build.gradle.kts`,
  `settings.gradle.kts`, `MainActivity` and navigation, declaring every
  component as a stub; feature slices write only inside their package and
  its tests. A feature needing a manifest or dependency change returns
  `NEEDS_OWNER_DECISION` to the Orchestrator, who routes a one-line change to
  the skeleton owner.
- Lightweight rules (AC-AFC-LW-01): network and parsing on `Dispatchers.IO`;
  panel rows are keyed `LazyColumn` items so only changed rows recompose;
  panel requests every panel_refresh only while visible; no animation beyond
  focus highlights.
- Lenses: Lightweight TV, Contract-first, Device integration.

### DES-AFC-ALERTPATH — Alert delivery on the device

- `AlertService` runs as a foreground service only inside an enabled viewing
  period (schedule computed locally from saved settings), long-polls
  `/v1/alerts`, and hands each alert to `AlertNotifier`.
- `AlertNotifier` posts a high-priority notification using the Fire TV
  heads-up notification extras documented by Amazon (verified in SP-2 on the
  stick), with Watch and Dismiss actions as `PendingIntent`s. It never starts
  an activity by itself (AC-AFC-ALERT-04: no foreground takeover).
- Labels: every alert text carries "Based on your profile" unless observed
  playback context was used (AC-AFC-MON-03), "Replay — recorded game data"
  for replay (AC-AFC-FEED-03), and "Manual lineup" for manual lineups
  (AC-AFC-PROF-04).
- Lenses: Device integration, Honest outcomes, Lightweight TV.

### DES-AFC-WATCH — Provider resolution and launch

- The backend `ProviderResolver` maps the ESPN `broadcasts` of the game to
  provider ids in CONTRACT-AFC-PROVIDERS, intersects them with the
  customer's provider apps, applies local market and preference, and returns
  one CONTRACT-AFC-LAUNCH target (AC-AFC-WATCH-01). A provider whose
  subscription status is "Unknown" yields a target labeled access unknown.
- The TV `WatchLauncher` applies the switching-confirmation setting, then
  starts the target with an explicit intent (`setPackage` to an allow-listed
  package) and posts the launch outcome to `/v1/alerts/{id}/outcome`. It
  reports GAME_OPENED only as "launched content target"; GAME_OPENED as a
  verified fact comes only from device observation in SP-3 and the M3 live
  test (AC-AFC-WATCH-02).
- Registry entries are added only for providers whose launch form SP-3
  verified on the stick; unverified providers get app-home targets only.
- Lenses: Honest outcomes, Device integration, Personalization.

### DES-AFC-PANEL — Lineup panel and panel modes

- Layout: a horizontal split; the panel takes a fixed 30 % of screen width on
  the right; the video occupies the left 70 % with resize mode FIT, so the
  frame is letterboxed, never cropped or covered (AC-AFC-PANEL-02).
- Mode B candidates for SP-4, tried in this order inside spike_panel_max:
  provider picture-in-picture beside the companion activity; platform
  multi-window; a provider integration exposed by Amazon Builder Tools. A
  system overlay drawn over provider video is rejected by AC-AFC-PANEL-02.
- Mode A: `CompanionPlayer` plays one CC-BY or CC0 clip fetched by
  `tools/fetch-footage.sh` against a pinned sha256 (not committed), with the
  on-screen label "Sample footage — not a live broadcast" (SD-006a).
- Data: `/v1/panel` every panel_refresh while visible; each value carries
  `fetched_at`; the TV marks values older than stale_after "Stale" and absent
  values "Unavailable" (AC-AFC-PANEL-01). Remote: D-pad left/right moves
  focus between video and panel; a dedicated menu toggles show/hide; team
  and league selection is a focusable list (AC-AFC-PANEL-03).
- Lenses: Device integration, Honest outcomes, Lightweight TV.

### DES-AFC-FEED — ESPN ingestion

- `FeedIngest` runs on an EventBridge Scheduler schedule that fires every
  minute only inside NFL game windows; each invocation fetches the
  scoreboard once, then each followed in-progress game's summary every
  feed_poll_interval for up to 60 s (AC-AFC-MON-01, -02).
- Responses are validated against a schema derived from the SP-5 fixtures;
  invalid responses count toward feed_fail_limit and never overwrite stored
  events (AC-AFC-FEED-01, -03).
- Dedupe key `GAME#<game id>` + `PLAY#<play id>`; a changed scoring play
  emits one `correction` GameEvent referencing the original (AC-AFC-FEED-02).
- Red-zone entry: possession team's ball on or inside red_zone_yards of the
  opponent goal line on a play where the previous play was outside it.
  Close game: 4th quarter or overtime with margin ≤ close_game_margin, emitted
  once per game per lead change into that state.
- `ReplaySource` serves `backend/fixtures/espn/` events on a schedule when the
  SAM parameter `ReplayMode` is `on`; every derived alert and panel value
  carries `replay: true` (AC-AFC-FEED-03). No admin endpoint exists.
- Lenses: Data ingestion, Honest outcomes.

### DES-AFC-LINEUP — Lineup sources

- CONTRACT-AFC-LINEUPSOURCE has two implementations. `YahooSource` uses
  OAuth 2.0 authorization code with read scope only (AC-AFC-SEC-04), calls
  `/users;use_login=1/games;game_keys=nfl/teams`,
  `/team/{team_key}/roster;week={week}` and `/league/{league_key}/settings`,
  and classifies slots from `selected_position` (AC-AFC-PROF-02).
  `ManualSource` builds a lineup from ESPN team rosters entered on the TV
  (AC-AFC-PROF-04).
- The active source per customer is Yahoo when linked; at T_yahoo, if no
  Yahoo client credential exists in SSM (SP-6 check), ManualSource becomes
  the default and every view labels "Manual lineup" (C6).
- `Matcher` maps Yahoo player keys to ESPN athlete ids by normalized name,
  NFL team and position, with a reviewed override file
  `backend/src/afc_backend/match/overrides.json`; unmatched players show
  "Unmatched" (RISK-AFC-10).
- Lenses: Personalization, Honest outcomes, Security controls.

### DES-AFC-POLICY — Matching and alert policy

- Relevance rules of AC-AFC-ALERT-01; policy order: enabled alert type →
  quiet hours → duplicate check (one alert per customer per source event) →
  alert_min_gap per game → spoiler_delay hold → release (AC-AFC-ALERT-02).
- Correction GameEvents release a correction alert and update panel totals
  (AC-AFC-ALERT-03, AC-AFC-PANEL-04).
- Text templates: three intensity levels keyed by excitement level; template
  inputs are GameEvent fields and matched names only (AC-AFC-ALERT-05). No
  generative commentary unless the owner selects OD-AFC-02.
- Lenses: Personalization, Honest outcomes.

### DES-AFC-AUTH — Device linking and tokens

- `POST /v1/link/start` returns `device_code`, short `user_code`,
  `verify_url`, `expires_in` = device_code_ttl. The phone browser opens
  `verify_url`, enters `user_code`, and is redirected to Yahoo OAuth; the
  callback stores Yahoo tokens under the device's customer record and marks
  the link complete. The TV polls `/v1/link/status` and receives a random
  256-bit device bearer token, stored hashed (SHA-256) in DynamoDB
  (AC-AFC-PROF-01, AC-AFC-SEC-01, -02).
- Manual-lineup customers link without Yahoo: `link/start` then confirm on
  the TV yields a device token with no Yahoo tokens.
- The Yahoo client id and secret live in SSM Parameter Store SecureString
  parameters the owner creates (credential access is owner-only); Lambda
  reads them through its IAM role.
- Lenses: Security controls.

### DES-AFC-INFRA — AWS serverless on the Free plan

- AWS SAM `backend/template.yaml`: one Lambda per route group (Python 3.12,
  arm64, 128 MB), one HTTP API, one DynamoDB table `afc` (on-demand, TTL
  attribute `expires_at`), one EventBridge Scheduler group for game windows,
  SSM parameters by reference only, CloudWatch log groups with 7-day
  retention.
- `backend/tools/check_template.py` fails on any resource type outside the
  allow list of AC-AFC-SEC-03 and runs before every deploy and in the gate.
- Deploys use the owner's named AWS CLI profile `afc-dev` and the stack
  `afc-dev`; one deploy at a time (deploy lease). No account, credential or
  plan change is agent work (C4, C9).
- Lenses: Security controls, Owner boundary.

### DES-AFC-SPIKES — Spikes SP-1..SP-7

| Spike | Question | Evidence | Verdict rule |
|---|---|---|---|
| SP-1 | Which stick, OS and API level; does ADB over network and screencap work; does the starter APK install and run? | `adb shell getprop`, screencaps | C1 stop if API < min_sdk, Fire OS ≤ 5, or provider apps cannot run. |
| SP-2 | Does a heads-up notification from a foreground service appear over a provider app's playback; does the service survive 30 minutes of playback; is current-playback context exposed? | screencaps during playback, `dumpsys notification`, service log | PASS if visible over playback and the service survives; otherwise limitation (RISK-AFC-02). |
| SP-3 | For one provider app the owner subscribes to, which launch forms work: content deep link to a specific game, details page, app home? | screencaps of the landed screen, intent used | Record the best verified outcome per form; registry draft `docs/spikes/SP-3-provider-registry.json`. |
| SP-4 | Can the panel sit beside the provider's own video without covering or cropping it? | screencaps per candidate route | Mode B with the route named, or Mode A, within spike_panel_max from SP-1's first install. |
| SP-5 | ESPN endpoint shapes, field position, scoring plays, athlete ids, timestamps, corrections, update timing during live games. | fixtures from the 2026-10-12 and 2026-10-15 US games | Schema and timing notes; fixture set for replay and tests. |
| SP-6 | At T_yahoo, do Yahoo client credentials exist in SSM (name check only, no value read)? | `aws ssm describe-parameters` output | Yahoo or manual default (C6). |
| SP-7 (stretch, OD-AFC-03) | Can a verified Alexa route tune to the game? | device screencaps, voice transcript | Only a verified route may be shown (C8). |

- Spike probes live under `spikes/sp<n>/` and are excluded from the android
  gate area. SP-1..SP-4 hold the device lease in that order.
- Lenses: Device integration, Honest outcomes, Owner boundary.

### DES-AFC-SPEC — D1 architecture specification with the gridmarket kit

- Copy from public `1wgrumph/gridmarket` at a pinned commit: `spec/template/`,
  `tools/spec_build.py`, `tools/spec_lint.py`, `tools/azdiagram/`,
  `tools/tests/`, `skills/spec-author`, `skills/spec-diagram`,
  `skills/spec-lint`; record the source commit and the MIT notice in
  `THIRD_PARTY_NOTICES.md` (AC-AFC-SPEC-01).
- Adaptation: replace `uv run --project backend --frozen` with
  `uv run --project tools --frozen` backed by `tools/pyproject.toml`
  (PyYAML) and `tools/uv.lock`; Graphviz `dot` from the host (present).
- Specification `spec/amazon-fantasy-companion/` with `spec.yaml`
  (document_id `AFC-ARCH-001`), feature sections `04.1.<n>-<feature>.md` per
  design decision group, figures from views V1..V4 redrawn as azdiagram YAML
  (F1 context, F2 decomposition, F4 deployment and trust boundary, F5 alert
  sequence, F7 panel mode state machine).
- Rev 0.1 at M2 from this design; rev 1.0 at M4 with spike verdicts
  (AC-AFC-SPEC-02, -03).
- Lenses: Spec discipline.

### DES-AFC-GATE — This repository's gate

- `tools/ci/gate.sh` implements CONTRACT-AFC-GATE with four areas:
  - `android`: `cd tv-app && ./gradlew --no-daemon :app:lintDebug
    :app:testDebugUnitTest :app:assembleDebug` (paths `tv-app/**`).
  - `backend`: `uv run --project backend --frozen ruff check backend`,
    `uv run --project backend --frozen pytest backend/tests`,
    `uv run --project backend --frozen python backend/tools/check_template.py
    backend/template.yaml` (paths `backend/**`).
  - `spec`: `uv run --project tools --frozen python tools/spec_lint.py
    spec/amazon-fantasy-companion/`, the azdiagram lint, a rebuild and
    `git diff --exit-code` on the built file, `uv run --project tools
    --frozen pytest tools/tests` (paths `spec/**`, `tools/**`, `skills/**`).
  - `hygiene`: `python3 tools/ci/check_paths.py` over all tracked files
    (AC-AFC-CI-03, AC-AFC-PATH-01) plus the shared workflow checker from
    D4-B over `.github/workflows/` (always runs).
- `.githooks/pre-commit` runs `gate.sh --changed hygiene` plus the areas of
  staged paths; `.githooks/pre-push` runs `gate.sh --changed` against the
  merge base with `origin/main`.
- `.github/workflows/ci.yml` (AC-AFC-CI-02): `on: pull_request` and `push`
  to `main`; `concurrency: ci-${{ github.workflow }}-${{ github.ref }}` with
  `cancel-in-progress: true`; a `changes` job computes areas with a pinned
  path-filter action; one job per area named `gate / <area>`; every action
  pinned by full SHA; `permissions: contents: read`; `ubuntu-latest`
  GitHub-hosted runners; no secrets referenced.
- Lenses: Parallel-safe CI, Security controls.

### DES-AFC-D4 — Shared CI/CD capability (Alphazedehq)

Write set in `alphazede/Alphazedehq` (cross-repo; each sub-change is its own
PR, branch `ci-cd/<topic>`, worktree `worktrees/Alphazedehq-ci-cd-<topic>`):

| Sub-change | Files | Content |
|---|---|---|
| D4-A `setup-pre-commit` (S01) | `skills/setup-pre-commit/SKILL.md`, `skills/setup-pre-commit/references/gate-contract.md`, `skills/setup-pre-commit/templates/gate.sh`, `skills/setup-pre-commit/scripts/install-hooks.sh`, `skills/setup-pre-commit/tests/test-install-hooks.sh` | Replace the `[TODO]` template with the gate entrypoint procedure: inventory checks → write `tools/ci/gate.sh` from the template → install `.githooks` via `core.hooksPath` → wire Actions per `setup-a-repo` → verify by a deliberate failing change. |
| D4-B `setup-a-repo` (S02) | `skills/setup-a-repo/SKILL.md`, `skills/setup-a-repo/references/workflow-authoring.md`, `skills/setup-a-repo/templates/ci.yml`, `skills/setup-a-repo/scripts/check-workflows.py`, `skills/setup-a-repo/tests/test_check_workflows.py` | Workflow-authoring rules (AC-AFC-CI-02 list, free hosted runners on public repos, gh_private_minutes budget, C11, C14) and a checker that exits 1 on violation. `SKILL.md` gains one "Workflows" step and is trimmed below skill_size_max; scope wording covers personal and organization repositories (SD-019). |
| D4-C `ship-pull-request` (S03) | `skills/ship-pull-request/SKILL.md`, `skills/ship-pull-request/references/GATES.md`, `skills/ship-pull-request/references/EDIT-PR.md` | Gate step: when `docs/vnv/AGENTS.md` or `Vnv/AGENTS.md` exists run `vnv-review`, else record `REFUSED_NO_VNV` (C12, never a pass). GATES.md: a shared-gate row (`tools/ci/gate.sh`) and an amazon-fantasy-companion row. The Edit section moves to `references/EDIT-PR.md` so `SKILL.md` drops from 82 lines to below skill_size_max (C10). |
| D4-E harness hooks (S11) | `hooks/ci-gate-hook.sh`, `hooks/test-ci-gate-hook.sh`, `hooks/install-ci-gate-hook.py`, `hooks/README.md` | CONTRACT-AFC-HOOK; the installer edits each harness configuration idempotently after writing a timestamped backup, and links the D4 skills and `vnv-review` into Muse's skill directory. Runs only after D4-A..C merge (C13). |
| D4-F thin entry-point skill (S41, only if OD-AFC-01 = B) | `skills/ci-cd/SKILL.md` | A router under 25 lines naming the three skills; no procedure of its own. |

- Every changed `SKILL.md` is checked with `wc -l` and `wc -w` against
  skill_size_max and exercised on one matching and one non-matching request
  per create-lean-skill (AC-AFC-D4-05). No text names specific repositories
  as pilots or exclusions (AC-AFC-D4-06); the amazon-fantasy-companion GATES
  row is gate data, not scoping.
- Recommendation for OD-AFC-01: extensions only.
- Lenses: Lean skill, Parallel-safe CI, Owner boundary.

### DES-AFC-VNV — Vnv guidance tree

- `docs/vnv/AGENTS.md` indexes areas; `docs/vnv/<area>.md` for tv-app,
  backend, device-integration, ci-cd, spec, developer-feedback, each with
  Scope (paths), Tools (commands from CONTRACT-AFC-GATE, adb screencap),
  Review Focus (the lenses that apply) and findings target (GitHub issues in
  this repository with the `vnv` label, filed through the issue-label policy
  tool). Shape follows the shared `vnv-review` skill's profile schema.
- Lenses: Spec discipline, Owner boundary.

### DES-AFC-DX — Scribe developer-feedback deliverables

- `docs/developer-feedback/observations.md`: the running log (public per
  SD-011), one row per observation with the fields of issue #1 §Scribe
  contract; seeded with DX-001..DX-007 and planning observations (S08).
- `docs/developer-feedback/tool-summary.md` and
  `docs/developer-feedback/friction-log.md` (S39): sanitized, checked by the
  hygiene area and against the official rules page (AC-AFC-DX-03).
- Every packet template in `implementation.json` carries the
  `developer_feedback` section (AC-AFC-DX-01).
- Lenses: Developer feedback, Owner boundary.

### DES-AFC-SUB — Submission materials

- `README.md` (S36): what it does, architecture summary with the D1 link,
  setup for judges with their own AWS Free-plan account or the replay mode,
  footage credits, limitations (panel mode, provider route, voice), judge
  access through T_judge_access.
- `docs/submission/checklist.md` and `storyboard.md` (S37) list owner-only
  actions with due times before T_deadline (AC-AFC-SUB-02).
- Device clips (S38) by `adb shell screenrecord`, stored untracked under
  `submission-media/` (git-ignored), indexed in `docs/submission/clips/README.md`.
- Lenses: Honest outcomes, Owner boundary.

### DES-AFC-LANES — Lanes, worktrees, leases and landing

- Lanes and frozen profiles (DEC-AFC-PROFILE-001): `tv-app-ui` = frontend,
  `backend` = primary, `device-integration-spikes` = heavyweight,
  `spec-and-docs` = tech-writing, `defects` = bug-triager. Light slices use
  the Light Implementer route of their lane's profile.
- Development strategy: `tdd` lanes split each feature into a Test
  Implementer slice (red, `<id>T`) and a Product Implementer slice (green);
  scaffold and spike slices are single Product Implementer slices
  (OD-AFC-04); `spec-and-docs` is `single_implementer`.
- Worktrees: `worktrees/amazon-fantasy-companion-<lane>` (one per lane) and
  `worktrees/Alphazedehq-ci-cd-<topic>`; branches `afc/<lane>-m<n>` and
  `ci-cd/<topic>`; never hidden directories.
- Shared mutable resources and their leases, held by the Orchestrator and
  granted to one slice at a time: `fire-tv-stick` (S12..S15, S25 device
  checks, S28, S38, visual reviews), `aws-afc-dev` (S18, every deploy step),
  `alphazedehq-skills` (no two D4 slices edit the same skill), `live-game-window`
  (S16 recorder, S28).
- impl_agent_cap: at most 5 concurrent Implementer, Test Implementer, Light
  Implementer and repair sessions per orchestrating session; Reviewers,
  Scribe and Integration Engineer sessions are not counted.
- Landing: one PR per lane per milestone into `main`, rebase or merge commit;
  each reviewed once at the phase boundary on the lane profile's reviewer
  route with OCR delegate mode (AC-AFC-REV-01) and on-device visual review
  for UI (AC-AFC-VIS-01); at most one repair; gate green; then merge.
- Lenses: Parallel-safe CI, Owner boundary.

## Contracts

### CONTRACT-AFC-API — REST surface (`backend/api/openapi.yaml`)

| Route | Auth | Purpose |
|---|---|---|
| `POST /v1/link/start` | none | Start device link; returns `device_code`, `user_code`, `verify_url`, `expires_in`. |
| `GET /v1/link/status?device_code=` | none | `pending` \| `linked` \| `expired`; returns the device token once. |
| `GET /v1/link/verify?user_code=` | none (browser) | Redirect to Yahoo OAuth or confirm manual link. |
| `GET /v1/link/yahoo/callback` | OAuth state | Store Yahoo tokens; complete link. |
| `GET /v1/profile`, `PUT /v1/profile` | device token | Settings, followed players and teams, provider apps, local market. |
| `GET /v1/leagues` | device token | Yahoo leagues and teams. |
| `GET /v1/roster?team_key=` | device token | Roster with slot classification. |
| `PUT /v1/lineup/manual` | device token | Manual lineup from ESPN rosters. |
| `GET /v1/alerts?after=&wait=` | device token | Long-poll; returns `alerts[]` (CONTRACT-AFC-ALERT) and `cursor`. |
| `POST /v1/alerts/{id}/outcome` | device token | Launch outcome (CONTRACT-AFC-LAUNCH). |
| `GET /v1/panel?team_key=` | device token | CONTRACT-AFC-PANEL. |
| `GET /v1/providers` | device token | Registry subset for the device. |

Errors: JSON `{error, reason}`; 401 for missing or invalid token with no state
change (AC-AFC-SEC-02).

### CONTRACT-AFC-EVENT — GameEvent

`{event_id, source_game_id, source_play_id, type: red_zone_entry|touchdown|field_goal|two_point|safety|close_game|correction, athlete_ids[], possession_team, yard_line, period, clock, home_score, away_score, source_ts, ingest_ts, corrects_event_id?, replay: bool}`.

### CONTRACT-AFC-ALERT — Alert

`{alert_id, event_id, kind: event|correction, player?, team, matchup, text, intensity, source_ts, release_ts, labels[]: based_on_profile|replay|manual_lineup, launch: CONTRACT-AFC-LAUNCH}`.

### CONTRACT-AFC-LAUNCH — Launch target and outcome

Target `{kind: content|details|app_home|app_absent|access_unknown, provider_id?, package?, intent: {action, data_uri?, extras{}}?, access: confirmed|unknown}`.
Outcome codes: `GAME_OPENED`, `PROVIDER_DETAILS`, `APP_HOME`, `APP_ABSENT`,
`ACCESS_UNKNOWN`, `PLAYBACK_DENIED`, plus `reason` text.

### CONTRACT-AFC-PROVIDERS — Provider contract registry (`backend/providers/registry.json`)

`[{provider_id, display_name, package, broadcast_names[], markets[]?, launch: {content?, details?, app_home}, verified: {form, outcome, date, device_model}}]`.
Only SP-3-verified forms are present (DES-AFC-WATCH).

### CONTRACT-AFC-PANEL — Panel state

`{team_key, team_name, league_name, source: yahoo|manual, scoring: league|default, players[]: {name, position, slot, game_status, points, fetched_at, state: ok|stale|unavailable|unmatched}, total, projected?, fetched_at, replay}`.

### CONTRACT-AFC-LINEUPSOURCE — Lineup source interface

`list_leagues(customer) -> [League]`, `roster(team_key, week) -> [RosterSlot]`,
`scoring(league_key) -> ScoringRules`; implementations `YahooSource`,
`ManualSource`.

### CONTRACT-AFC-TABLES — DynamoDB single table `afc`

Keys: `DEVICE#<token hash>`, `LINK#<device_code>`, `CUST#<id>#YAHOO`,
`CUST#<id>#PROFILE`, `GAME#<id>#PLAY#<id>`, `CUST#<id>#ALERT#<ts>`,
`PANEL#<team_key>`; TTL on link and alert items.

### CONTRACT-AFC-GATE — Gate entrypoint (shared contract, D4-A)

`tools/ci/gate.sh [--changed[=<base>]] [--list] [<area>...]`. No area means
all areas. `--changed` runs only areas whose paths changed against `<base>`
(default: merge base with `origin/main`) plus `hygiene`. Exit 0 pass, 1 check
failure, 2 usage error, 3 required tool missing (a typed gap, never a pass).
Each area prints `gate: <area>: PASS|FAIL|GAP <detail>`. The same invocation
runs in git hooks, in Actions (`gate.sh <area>` per job) and from harness
hooks.

### CONTRACT-AFC-HOOK — Harness hook (D4-E)

`hooks/ci-gate-hook.sh` reads the harness's pre-tool event on stdin, acts
only when the shell command is `git commit` or `git push` in a repository
that has `tools/ci/gate.sh`, and then runs `tools/ci/gate.sh --changed` when
the repository's git hooks are not installed or the command carries
`--no-verify`; a non-zero gate blocks the tool call with the gate output. It
is advisory (prints a notice) in repositories without a gate entrypoint.
Harness adapters: Claude Code `PreToolUse` (Bash), Codex `hooks.json`,
Cursor `beforeShellExecution`, Muse and AGY where a pre-tool hook surface is
verified; otherwise a typed gap (AC-AFC-D4-04).

## Diagrams

Feature views are canonical Mermaid sources with SVG renderings, listed in
`views/views.json` and embedded in the DoD Manifest:

- MODEL-AFC-V1 `views/v1-context.mmd` — context and trust boundaries.
- MODEL-AFC-V2 `views/v2-use-cases.mmd` — retained items, panel, outcomes.
- MODEL-AFC-V3 `views/v3-operational-flow.mmd` — feed → match → alert →
  Watch → launch; panel refresh; Mode B / Mode A branch.
- MODEL-AFC-V4 `views/v4-cicd-gate.mmd` — one gate entrypoint from git hooks,
  Actions and harness hooks; vnv-review branch.
