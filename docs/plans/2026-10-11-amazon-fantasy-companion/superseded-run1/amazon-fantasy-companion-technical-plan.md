---
type: technical-plan
status: complete
lifecycle: AFC-2026-10-11
title: "Amazon Fantasy Companion: architecture, program plan, milestones"
plan_dir: docs/plans/2026-10-11-amazon-fantasy-companion/
---

# Amazon Fantasy Companion — Technical Plan

## Outcome

A customer-configurable Fire TV companion, built for the Amazon Developer
Hackathon Fire TV track and the AWS Builder mini challenge (SD-008), that
notices NFL moments relevant to the viewer's fantasy starters, alerts the
viewer while another viewing app plays, helps the viewer reach the game in a
provider app the viewer already uses, and shows a right-side lineup panel
beside unobscured video. It retains experience items 1, 2, 3, 4 and 6 of
issue #1 plus the right-side panel, and excludes every messaging and
community feature. It runs on the owner's 2018 Fire TV stick on Fire OS from
the `AmazonAppDev/hello-world-fire-tv` starter (SD-001, SD-003), reads live
NFL data from ESPN's unofficial public JSON (SD-004), reads lineups from Yahoo
or, from T_yahoo without approval, from labeled manual entry (SD-007), and
runs its backend on an owner-created AWS Free-plan account (SD-005). The panel
route is decided by a spike bounded by spike_panel_max; on failure the panel
runs beside the app's own player with labeled open-licensed footage (Mode A,
SD-006, SD-006a).

This Lifecycle also delivers (SD-012, SD-016, SD-021):

- **D1** the product architecture specification, built with the gridmarket
  spec kit (SD-013);
- **D2** this program plan to T_deadline with parallel waves and milestone
  definitions;
- **D3** the GitHub milestones, created by the Orchestrator after approval;
- **D4** the shared, repo-agnostic CI/CD capability in the owner's shared
  skills (SD-018..SD-021), landed first, followed by harness hooks;
- this repository's Vnv guidance tree (SD-014), its local plus Actions gate,
  and the Scribe developer-feedback deliverables of issue #1.

The product is a hackathon entry, not a production system: no customer data
beyond the owner's own accounts, no paid services, no hardware performance
claims.

## Requirements register

No requirements register exists. The repository is greenfield
(`workspace.md` Observed Systems; `repository-map.md`) and this is not a
specification Lifecycle: D1 is a Markdown architecture specification built
with the gridmarket kit, not an SDoc register. Every requirement below is
Lifecycle-local (`AC-*` / `RISK-*`). Sources are the confirmed decisions
DEC-AFC-001, DEC-AFC-002, DEC-AFC-SD-001..SD-021 (written `SD-nnn` below),
DEC-AFC-PROFILE-001, the typed conditionals C1..C14 and the coverage ledger
of `scope-decision-batch.md`, and issue #1 (cited `#1 §<heading>`).

## Glossary

### Quantity definitions (copied verbatim from the Scope Definition final batch)

| Name | Formula / value | Population / denominator | Units | Source |
|---|---|---|---|---|
| T_deadline | Devpost submission close | Single event | 2026-10-23T19:00:00Z | Issue #1 |
| T_yahoo | Manual-entry trigger | Single event | 2026-10-16T19:00:00Z | SD-007 |
| spike_panel_max | Elapsed time from first app install on the stick to the panel-route verdict | One spike | ≤ 24 h | SD-006 |
| min_sdk | Lowest supported Android API level | One APK | API 25 | SD-003 |
| T_judge_access | Last date judges must reach the repo and backend | Single date | 2026-11-20 | Issue #1 |
| aws_free_window | The earlier of 6 months after opening or credits used up | One account | Months | aws.amazon.com/free |
| impl_agent_cap | Concurrent implementation agents per orchestrating session; reviewers excluded | Per session | 5 | Rule 17 |
| gh_private_minutes | Included GitHub Actions minutes per month for a GitHub Free account's private repos; public repos use standard runners free | Per account per month | 2,000 min | GitHub billing docs |
| skill_size_max | Size limit for `SKILL.md`, frontmatter included | Per skill | < 60 lines and < 650 words | `create-lean-skill` |

### Lifecycle-local design quantities (Planning and Design proposals; approved with the plan)

These add design constants the confirmed table does not define. None
redefines a quantity above.

| Name | Formula / value | Population / denominator | Units | Source |
|---|---|---|---|---|
| feed_poll_interval | Period between two backend fetches of one in-progress game's ESPN summary | Per in-progress game | 15 s | Planning and Design proposal |
| feed_fail_limit | Consecutive failed or schema-invalid fetches of one game before that game is marked stale | Per game | 3 fetches | Planning and Design proposal |
| stale_after | Age of a displayed value, measured from its last successful source fetch, at which it is marked stale | Per displayed value | 120 s | Planning and Design proposal |
| alert_poll_wait | Longest time one alert long-poll request waits for an alert before returning empty | Per request | 20 s | Planning and Design proposal; API Gateway HTTP API 30 s limit |
| alert_min_gap | Customer-set minimum time between two released alerts for the same game | Per customer per game | 0–600 s, default 120 s | Planning and Design proposal; #1 item 6 "frequency" |
| spoiler_delay | Customer-set hold between alert creation and release | Per customer | 0–120 s, default 0 s | Planning and Design proposal; #1 item 6 |
| device_code_ttl | Lifetime of one device-link code | Per code | 600 s | Planning and Design proposal |
| red_zone_yards | Distance from the opponent's goal line at or inside which possession counts as a red-zone entry | Per play | 20 yards | NFL convention |
| close_game_margin | Largest score difference in the 4th quarter or overtime that counts as a close game | Per game | 8 points | Planning and Design proposal |
| panel_refresh | Period between two panel data requests while the panel is visible | Per device | 30 s | Planning and Design proposal |

### Terms

| Term | Meaning |
|---|---|
| starter | A player in an active (non-bench) roster slot of the selected Yahoo team for the current NFL week, read from the roster's selected position, or a player the customer entered as a starter in a manual lineup. |
| followed player | A starter, a player the customer selected individually, or any player of a favorite NFL team. |
| enabled viewing period | A time inside the customer's monitoring schedule (always on, game-day mode, or custom hours) and outside quiet hours. |
| GameEvent | The backend's normalized record of one ESPN play or game-state change (`design.md` CONTRACT-AFC-EVENT). |
| alert | One customer-specific message derived from one GameEvent, released under the customer's alert policy. |
| launch outcome | One of GAME_OPENED, PROVIDER_DETAILS, APP_HOME, APP_ABSENT, ACCESS_UNKNOWN, PLAYBACK_DENIED (`design.md` CONTRACT-AFC-LAUNCH). |
| Mode B | The panel beside a provider app's own video, by a route the SP-4 spike verifies. |
| Mode A | The panel beside the companion's own player showing CC-BY or CC0 footage labeled "Sample footage — not a live broadcast" (SD-006a). |
| provider app | A third-party viewing app on the Fire TV that can show NFL games. |
| allow-listed package | A provider app package name listed in the provider contract registry (`design.md` CONTRACT-AFC-PROVIDERS). |
| Vnv guidance tree | `docs/vnv/AGENTS.md` plus one guidance file per area naming Scope, Tools, Review Focus and findings target (SD-014). |
| gate entrypoint | The one script a repository's local hooks, Actions workflow and harness hooks all invoke (`tools/ci/gate.sh` here). |
| shared skills | The owner's skills in the Alphazedehq repository `skills/` directory, linked into each harness (SD-018). |
| replay | Backend serving of recorded ESPN fixtures, labeled "Replay — recorded game data" wherever shown (C2). |
| spike | A time-boxed device or data investigation that ends in a recorded verdict file, not in product code. |

## Requirements (Lifecycle-local)

Every row is Lifecycle-local. Allocation names the milestone and the
component; component placement follows the Systems Modeler placement receipt
(`specialists/systems-modeler-receipt.md`).

### Product — profile and lineup (issue #1 item 1)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-PROF-01 | When the customer starts Yahoo linking on the TV app, the TV app shall display a device code and a link URL, and the backend shall bind the Yahoo authorization the customer completes in a phone browser to that device if it completes within device_code_ttl, and shall store the Yahoo OAuth tokens only in the backend. | #1 item 1, #1 item 6 (device-code linking), SD-005, SD-007 | test, demonstration | M3; DeviceAuth, LineupConnector, ProfileSettings |
| AC-AFC-PROF-02 | When a linked Yahoo account exists, the backend shall list the customer's NFL leagues and teams, and the TV app shall let the customer select teams, individual players and favorite NFL teams; the backend shall classify each roster player as starter, bench or unknown from the roster's selected position for the current NFL week. | #1 item 1, #1 §Source review (Yahoo) | test | M3; LineupConnector, ProfileSettings |
| AC-AFC-PROF-03 | The TV app shall detect which allow-listed packages are installed using the Android package manager, shall show each detected provider app's subscription status as "Unknown" until the customer confirms it, and shall let the customer override the detected apps, each subscription status, and the local market. | #1 item 1, #1 item 4 | test, demonstration | M3; AppDetector, ProfileSettings |
| AC-AFC-PROF-04 | If Yahoo access is not approved at T_yahoo, then the system shall offer manual lineup entry from ESPN team rosters and shall label that lineup "Manual lineup" on every screen and panel that shows it. | SD-007, C6 | test | M3; LineupConnector (ManualSource), ProfileSettings |

### Product — monitoring and feed (issue #1 item 2)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-MON-01 | While a game involving a followed player is in progress and at least one following customer is in an enabled viewing period, the backend shall fetch that game's ESPN summary once every feed_poll_interval, and shall fetch no game that no such customer follows. | #1 item 2, SD-004 | test | M3; FeedIngest |
| AC-AFC-MON-02 | The backend shall fetch each in-progress game at most once per feed_poll_interval regardless of how many customers follow it. | #1 §Lightweight device design (shared ingestion) | test | M3; FeedIngest |
| AC-AFC-MON-03 | The TV app shall read no current-playback context unless the customer has enabled detection; if the device exposes no supported current-playback interface (SP-2 verdict), then the detection setting shall read "Not available on this device"; every alert and panel state not derived from observed playback shall be labeled "Based on your profile". | #1 item 2 | test, inspection | M3; ProfileSettings, AlertNotifier |
| AC-AFC-MON-04 | While the device is outside every enabled viewing period, the TV app shall send no alert long-poll requests. | #1 item 2, #1 §Lightweight device design | test | M3; AlertService |
| AC-AFC-FEED-01 | The backend shall normalize each ESPN play into a GameEvent carrying the source game id, source play id, event type (red_zone_entry, touchdown, field_goal, two_point, safety, close_game), involved ESPN athlete ids, possession team, field position, period, game clock, source timestamp and ingest timestamp, and shall reject a schema-invalid response without changing stored GameEvents. | SD-004, #1 item 3 | test | M3; FeedIngest |
| AC-AFC-FEED-02 | The backend shall emit at most one GameEvent per source game id and source play id, and when ESPN changes a scoring play that was already emitted, the backend shall emit exactly one correction GameEvent that references the original. | #1 item 3 (duplicates, corrections) | test | M3; FeedIngest |
| AC-AFC-FEED-03 | If one game's ESPN fetch fails or returns a schema-invalid response feed_fail_limit times in a row, then the backend shall mark that game's data stale; when the operator enables replay, the backend shall serve GameEvents from recorded fixtures and every alert and panel value derived from them shall carry the label "Replay — recorded game data". | C2, #1 §Judging (labeled replay) | test | M3; FeedIngest (ReplaySource) |

### Product — alerts (issue #1 item 3)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-ALERT-01 | When a GameEvent of a customer-enabled alert type is a scoring play credited to a followed player, a red_zone_entry by a followed player's team, or a close_game state of a followed player's game, the backend shall create one alert for that customer naming the player or team, the matchup, the event and the source timestamp; a red-zone alert shall state the team's field position only and shall not state that the player is on the field. | #1 item 3 | test | M3; Matcher, AlertPolicy |
| AC-AFC-ALERT-02 | The backend shall create at most one alert per customer per source event, shall hold each alert for the customer's spoiler_delay before release, shall release no alert during the customer's quiet hours, and shall release at most one alert per game per alert_min_gap for that customer. | #1 item 3, #1 item 6 | test | M3; AlertPolicy |
| AC-AFC-ALERT-03 | When a correction GameEvent changes an event that produced a released alert, the backend shall release one correction alert to that customer and shall apply the correction to that customer's panel totals. | #1 item 3, #1 §Right-side panel | test | M4; AlertPolicy, PanelService |
| AC-AFC-ALERT-04 | While a provider app plays video in the foreground and the customer is in an enabled viewing period, the TV app shall show each released alert as a heads-up notification with Watch and Dismiss actions within one alert_poll_wait of its release, without bringing the companion app to the foreground. | #1 item 3, #1 §Development setup | demonstration | M3; AlertService, AlertNotifier |
| AC-AFC-ALERT-05 | The backend shall build alert text from the GameEvent and matched player data with fixed templates whose wording intensity follows the customer's excitement level; no generative model shall decide an event, a score or a player identity. | #1 item 3, #1 §Proposed standout moment | test, inspection | M3; AlertPolicy |

### Product — watch the game (issue #1 item 4)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-WATCH-01 | When the backend creates an alert, it shall attach a launch target selected from the game's ESPN broadcasts, the customer's provider apps and their subscription status, the local market and the provider preference, as exactly one of: content target with provider content id, provider details target, app home target, app absent, or access unknown; it shall attach no content target for a provider whose subscription status is "Unknown" without labeling access as unknown. | #1 item 4, #1 §App launch research | test | M3; ProviderResolver |
| AC-AFC-WATCH-02 | When the customer selects Watch, the TV app shall, after the confirmation the customer's switching-confirmation setting requires, launch the attached target by an explicit intent to an allow-listed package and record one launch outcome; for the provider chosen in SP-3, the outcome GAME_OPENED shall be shown on the device for one live or scheduled NFL game. | #1 item 4, SD-001 | demonstration | M3; WatchLauncher |
| AC-AFC-WATCH-03 | If the target package is not installed or the launch intent fails, then the TV app shall show the launch outcome and its reason, and shall show no success state. | #1 item 4 | test | M3; WatchLauncher |

### Product — customer controls (issue #1 item 6)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-CTRL-01 | The TV app shall let the customer set with the remote: followed teams and players, alert types, alert_min_gap, quiet hours, monitoring schedule, spoiler_delay, notification presentation (heads-up or panel only), excitement level, provider preference, switching confirmation and detection opt-in; the backend shall apply each saved setting to the next alert decision for that customer. | #1 item 6 | test, demonstration | M3 (core), M4 (complete); ProfileSettings, AlertPolicy |
| AC-AFC-CTRL-02 | The TV app shall keep every saved setting across an app restart and a device reboot. | #1 item 6 | test | M4; ProfileSettings |
| AC-AFC-CTRL-03 | The TV app shall show the voice-announcement setting only if voice announcements are implemented and verified on the device (C8). | #1 item 6, SD-008, C8 | inspection | M4; ProfileSettings |

### Product — right-side lineup panel (issue #1 §Right-side panel)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-PANEL-01 | The lineup panel shall show the selected team's starters with each player's fantasy points and game status, and the team total, computed with the league's Yahoo scoring settings or, for a manual lineup, with a labeled default scoring; it shall mark each value older than stale_after "Stale" and each unavailable value "Unavailable". | #1 §Right-side panel | test | M3; PanelService, LineupPanel |
| AC-AFC-PANEL-02 | While the panel is shown with video, the video shall occupy the area left of the panel with its aspect ratio preserved, and no pixel of the video frame shall be covered or cropped. | #1 §Right-side panel | demonstration, inspection | M3; LineupPanel, CompanionPlayer |
| AC-AFC-PANEL-03 | The customer shall show and hide the panel and choose the followed team and league using only the remote's D-pad, select and back keys, with a visible focus indicator on every focusable element. | #1 §Right-side panel | demonstration | M3; LineupPanel |
| AC-AFC-PANEL-04 | When a starter change or a scoring correction reaches the backend, the panel shall show it within one panel_refresh, and the panel totals shall agree with the alerts released for the same events. | #1 §Right-side panel | test | M4; PanelService, LineupPanel |
| AC-AFC-PANEL-05 | The SP-4 spike shall record a Mode B verdict naming the verified route, or a Mode A verdict, within spike_panel_max; in Mode A the companion player shall play only CC-BY or CC0 footage showing the label "Sample footage — not a live broadcast" on screen, and the README shall credit that footage. | SD-006, SD-006a, C5 | inspection, demonstration | M2 (verdict), M3 (Mode A or B build); CompanionPlayer |

### Product — spikes, security and lightweight design

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-SPIKE-01 | SP-1 shall record the stick's model, Fire OS version and Android API level; if the API level is below min_sdk, the OS is Fire OS 5 or older, or the provider apps cannot run, then device work shall stop and the finding shall return to the owner without any purchase or platform switch. | SD-001, SD-003, C1 | inspection | M2; device-integration-spikes |
| AC-AFC-SPIKE-02 | Each spike SP-1..SP-6 shall end with a verdict file `docs/spikes/SP-<n>.md` that records the route tried, exact steps, evidence paths, verdict and limits. | #1 §Development setup, #1 §Right-side panel (record which routes work) | inspection | M2; device-integration-spikes, backend |
| AC-AFC-SEC-01 | The APK and every tracked file shall contain no Yahoo client secret, OAuth token, AWS credential or device token; the backend shall read the Yahoo client secret from SSM Parameter Store SecureString and keep OAuth tokens only in its DynamoDB table. | Cross-repo rule 2, SD-005 | test, inspection | M1 (hygiene), M3; DeviceAuth, LineupConnector |
| AC-AFC-SEC-02 | Every API route except link start, link status and the OAuth callback shall require a valid device bearer token; a request with a missing or invalid token shall receive HTTP 401 and change no stored state. | Cross-repo rule 2 | test | M3; API, DeviceAuth |
| AC-AFC-SEC-03 | The backend template shall declare only resource types on the template allow list (Lambda, API Gateway HTTP API, DynamoDB on-demand, EventBridge Scheduler, SSM parameter, IAM role, CloudWatch log group), and the deploy command shall fail before any change when the template declares another type. | SD-005, C4 | test | M1 (check), M2 (deploy); backend infra |
| AC-AFC-SEC-04 | The backend shall request only Yahoo's read scope. | #1 §Source review (read-only) | inspection | M3; LineupConnector |
| AC-AFC-LW-01 | The TV app shall run network requests and JSON parsing off the main thread, shall redraw only panel rows whose values changed, and shall stop panel requests while the panel is hidden; no document or submission text shall state a measured device latency, frame rate or memory figure. | #1 §Lightweight device design | inspection, test | M3, M5; TV app, docs |

### Deliverable D1 — architecture specification

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-SPEC-01 | The repository shall contain the gridmarket spec kit (`spec/template/`, `tools/spec_build.py`, `tools/spec_lint.py`, `tools/azdiagram/`, and the `spec-author`, `spec-diagram` and `spec-lint` skills) with gridmarket's MIT copyright and permission notice retained, and every kit command shall run without gridmarket's backend project flag. | SD-013 | inspection, test | M1; spec-and-docs |
| AC-AFC-SPEC-02 | The specification under `spec/amazon-fantasy-companion/` shall keep every COE-ASA-001 floor subsection the template carries, shall bind every product AC-AFC row in at least one section, shall pass spec-lint and the figure lint with zero findings, and a second build shall leave the built file byte-identical. | SD-012, SD-013 | test | M2 (rev 0.1), M4 (rev 1.0); spec-and-docs |
| AC-AFC-SPEC-03 | Specification revision 1.0 shall record the SP-1..SP-6 verdicts, the panel mode, the SP-3 provider route and every recorded limitation. | SD-006, #1 §Right-side panel | inspection | M4; spec-and-docs |

### Deliverables D2 and D3 — program plan and milestones

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-PLAN-01 | The program plan shall define milestones M1..M5, each with title, due date, entry criteria, exit criteria and slices; every slice shall belong to exactly one milestone and one wave, and no wave shall schedule more than impl_agent_cap concurrent implementation agents. | SD-012, Rule 17 | inspection | Planning (this package) |
| AC-AFC-PLAN-02 | After owner approval, milestones M1..M5 shall exist in `1wgrumph/amazon-fantasy-companion` with the planned titles, due dates and descriptions, as read back with `gh api`. | SD-012 (D3) | inspection | M1; light work |

### This repository's gate and Vnv tree

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-CI-01 | The repository shall have one gate entrypoint `tools/ci/gate.sh` with the areas `android`, `backend`, `spec` and `hygiene`; the local pre-commit and pre-push hooks and the Actions workflow shall invoke that entrypoint with the same area arguments, and each area shall exit non-zero when any of its checks fails. | SD-016, SD-021 | test | M1; repo gate |
| AC-AFC-CI-02 | The Actions workflow shall trigger on `pull_request` and `push` to `main` only (never `pull_request_target`), shall use a concurrency group per workflow and ref with cancel-in-progress, shall run an area only when its paths change, shall report one stable check name per area, shall pin every action to a full commit SHA, shall grant `contents: read` only, shall expose no secret to fork pull requests, and shall run on GitHub-hosted runners. | SD-017, SD-021, C14 | test | M1; repo gate |
| AC-AFC-CI-03 | The `hygiene` area shall fail when any tracked file contains an absolute user-home path, detected by shape (`/home/<user>/`, `/Users/<user>/`, `C:\Users\<user>\`), or a credential pattern. | Cross-repo rule 12, SD-010, C7 | test | M1; repo gate |
| AC-AFC-VNV-01 | The repository shall contain the Vnv guidance tree: `docs/vnv/AGENTS.md` and one guidance file per area (tv-app, backend, device-integration, ci-cd, spec, developer-feedback), each naming Scope, Tools, Review Focus and findings target. | SD-014 | inspection | M1; spec-and-docs |

### Deliverable D4 — shared CI/CD capability (Alphazedehq shared skills)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-D4-01 | The shared `setup-pre-commit` skill shall define one repo-agnostic gate entrypoint contract, shall ship a template gate script and an installer for local git hooks that invoke it, shall state that GitHub Actions invoke the same entrypoint, shall contain no `[TODO]` text, and its `SKILL.md` shall be within skill_size_max. | SD-018, SD-021, DX-007, C10 | test, inspection | M1; D4 |
| AC-AFC-D4-02 | The shared `setup-a-repo` skill shall reference a workflow-authoring guide stating the rules of AC-AFC-CI-02 plus free hosted runners on public repositories and the gh_private_minutes budget (C11), and shall ship a checker script that exits non-zero on a workflow violating any of those rules; its `SKILL.md` shall be within skill_size_max. | SD-017, SD-019, SD-021, C11, C14 | test | M1; D4 |
| AC-AFC-D4-03 | The shared `ship-pull-request` skill shall run `vnv-review` when the repository has a Vnv guidance tree (`docs/vnv/AGENTS.md` or `Vnv/AGENTS.md`) and otherwise record REFUSED_NO_VNV, never a pass; its `references/GATES.md` shall gain a shared-gate row and an amazon-fantasy-companion row; its `SKILL.md` shall be within skill_size_max. | SD-020, SD-021, C10, C12 | test, inspection | M1; D4 |
| AC-AFC-D4-04 | After AC-AFC-D4-01..03 are merged (C13), one shared hook script shall run the current repository's gate entrypoint before an agent-initiated `git commit` or `git push` in Claude Code, Codex, Cursor, Muse and AGY wherever that harness exposes a pre-tool hook; a harness without one shall be recorded as a typed gap with its exact evidence; and Muse's skill directory shall expose the D4 skills. | SD-021, C13, coverage ledger (Muse skills gap) | test, demonstration | M2; D4 |
| AC-AFC-D4-05 | Each D4 skill change shall land in Alphazedehq through its own pull request merged by rebase or merge commit, after the skill is exercised against one matching and one non-matching request. | SD-021, create-lean-skill, workspace rule (never squash) | inspection | M1; D4 |
| AC-AFC-D4-06 | No D4 skill or hook text shall scope the capability to named repositories, owners, pilots or exclusions. | SD-019 | inspection | M1; D4 |

### Scribe developer feedback (issue #1 contract)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-DX-01 | Every dispatch packet and every return in this Lifecycle shall carry a `developer_feedback` section that lists observations with IDs and evidence, or states "no new observations" and names the tools exercised. | #1 §Scribe contract | inspection | All milestones |
| AC-AFC-DX-02 | The repository shall contain the running observation log, a per-tool summary (purpose, onboarding, what worked, what needs work, willingness to reuse) and a sanitized friction log (task, reproduction steps, expected and actual behavior, severity, workaround, suggestion) that cover every tool, API, SDK and device used and carry DX-001..DX-007. | #1 §Scribe contract, SD-011 | inspection | M1 (log), M5 (summary, friction log) |
| AC-AFC-DX-03 | The per-tool summary and the friction log shall contain no credential, personal account detail or absolute local path, and shall be checked against the current official rules before submission. | #1 §Scribe contract, SD-010, C7 | test, inspection | M5 |

### Submission

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-SUB-01 | The README shall give setup steps (build the APK, deploy the backend to the reader's own AWS Free-plan account, link Yahoo or enter a manual lineup, run replay), footage credits, the panel-mode and voice limitation statements, and the judge-access arrangement through T_judge_access. | #1 §Acceptance, SD-006, C8 | inspection | M5; spec-and-docs |
| AC-AFC-SUB-02 | The submission checklist shall list every owner-only action (license choice, visibility flip, ESPN terms decision, video upload, reviewer access, Devpost submission, external feedback) with its due time before T_deadline, and agents shall perform none of them. | SD-009, C3, C9 | inspection | M5 |
| AC-AFC-SUB-03 | The demo material shall consist of clips recorded from the device for the storyboard segments of #1, with every replay segment labeled as replay and every Mode A segment labeled as sample footage. | #1 §Proposed video storyboard, C2, SD-006a | inspection | M5 |
| AC-AFC-SUB-04 | Voice and Alexa behavior shall appear in the demo or the submission text only if implemented and verified on the device. | SD-008, C8 | inspection | M5 |

### Lifecycle-level requirements

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-LAND-01 | Each phase's lane branches shall land on `main` through pull requests merged by rebase or merge commit after one Reviewer review, at most one repair round and a green gate entrypoint run; no squash merge, force-push or commit on local `main`. | Workspace rules, CLAUDE.md | inspection | All milestones |
| AC-AFC-REV-01 | Every Reviewer packet shall carry OCR in delegation mode (`ocr delegate preview`, `ocr delegate rule`) and either Reverify (claims about the built APK) or `Reverify: not applicable — <reason>`; an OCR or Reverify run that cannot complete is a typed gap with its exact error. | Cross-repo rule 15, frozen profiles (`review.coverage_assist`, `deterministic_verification.reverify`) | inspection | All milestones |
| AC-AFC-VIS-01 | Every change to rendered TV UI shall be reviewed on the stick with screenshots captured by `adb exec-out screencap -p` for each changed screen and state, kept with the review evidence and containing no customer data. | Cross-repo rule 16 | inspection | M3, M4 |
| AC-AFC-PATH-01 | No committed file of this Lifecycle shall contain an absolute local home path; plan artifacts use repository-relative paths or `<PLANNING_WORKTREE>` / `$HOME` placeholders. | Cross-repo rule 12, SD-010, C7 | test | All milestones |

### Risks

| ID | Risk | Control | Response |
|---|---|---|---|
| RISK-AFC-01 | The stick cannot be found, is Fire OS 5 or older, is below min_sdk, or cannot run the provider apps. | AC-AFC-SPIKE-01 (C1); M2 entry criterion. | Stop device work and return to the owner; never buy or switch platforms on the owner's behalf. |
| RISK-AFC-02 | Fire OS on the stick does not show a heads-up notification over a provider app's playback. | SP-2 first in M2; AC-AFC-ALERT-04. | Record the exact limitation; panel-only presentation remains; owner scope decision (class C). |
| RISK-AFC-03 | No provider exposes a content-level deep link the companion can invoke for a specific game. | SP-3; AC-AFC-WATCH-01 outcome set. | Ship the best verified outcome (details or app home), state the limitation, and record the missing interface as an integration proposal for the owner. |
| RISK-AFC-04 | No supported route places the panel beside a provider app's video. | SP-4 bounded by spike_panel_max (C5). | Mode A with labeled footage; limitation stated in the submission. |
| RISK-AFC-05 | ESPN's unofficial endpoints change, rate-limit or go down. | AC-AFC-FEED-01 schema validation; AC-AFC-FEED-03 stale marking and labeled replay (C2); fixtures captured in M2. | Switch to labeled replay for the demo; owner decides ESPN terms at submission (C3). |
| RISK-AFC-06 | Yahoo access is not approved by T_yahoo. | AC-AFC-PROF-04 manual lineup (C6) built in M3 regardless. | Labeled manual lineup. |
| RISK-AFC-07 | A frozen route's usage window is exhausted mid-wave (observed: Muse HTTP 429 on 2026-10-11, reset 2026-10-12T00:00:00Z). | Ordered fallbacks in the frozen profiles; class B activation with receipt. | Activate the next approved fallback; queue the slice when all are exhausted. |
| RISK-AFC-08 | Actions minutes on the private repository run out (C11). | AC-AFC-CI-02 path filters and concurrency cancel; local gate first. | Hosted runs stop; local gate evidence continues; no paid overage without the owner. |
| RISK-AFC-09 | AWS Free-plan limits or credits are reached, or a paid resource is introduced (C4). | AC-AFC-SEC-03 template allow list; on-demand DynamoDB; schedule only during game windows. | Stop the scheduler; owner decides any plan change. |
| RISK-AFC-10 | Yahoo and ESPN player identities mismatch, so alerts miss or misattribute a player. | Matcher identity map with recorded fixtures; unmatched players shown "Unmatched" in the panel. | Manual mapping override in the identity map; correction alert. |
| RISK-AFC-11 | A secret, account detail or absolute local path reaches the public repository. | AC-AFC-SEC-01, AC-AFC-CI-03, AC-AFC-PATH-01 in the gate; push protection when the repository goes public. | Remove before merge; credential rotation is the owner's action. |
| RISK-AFC-12 | Muse or AGY exposes no pre-tool hook surface. | AC-AFC-D4-04 typed gap. | Record the gap; git hooks still run the gate locally. |
| RISK-AFC-13 | Imported software (starter, Android SDK, Gradle wrapper, AWS SAM CLI, uv, spec kit) is compromised. | scan-software-supply-chain before first use (cross-repo rule 10); Gradle wrapper checksum verification. | Fail closed on BLOCK or INDETERMINATE. |
| RISK-AFC-14 | Few live NFL windows remain before T_deadline (Mon 10-12, Thu 10-15, Sun 10-18, Mon 10-19, Thu 10-22 US time). | Fixture capture in M2; Sunday 2026-10-18 live test fixed in M3; replay for repeatable demos. | Fall back to labeled replay for any segment that misses its window. |

## Exclusions

- Messaging, message boards, community rooms, shared chat and watch-party
  social features (issue #1, owner 2026-10-10).
- Hardware performance benchmarking or measured device latency, frame rate or
  memory claims (issue #1 §Lightweight device design).
- Vega OS builds, a second device, any device purchase (SD-003).
- NFL broadcast footage or highlights (SD-006a).
- Paid AWS resources or a plan upgrade (C4); paid Actions overage (C11).
- Alexa+ track, Open Source mini challenge (SD-008); Alexa voice unless
  implemented and verified (C8).
- Generative AI commentary unless the owner selects it at the integrated
  review (coverage ledger: `typesafe-ai` deferred). Recommendation: exclude.
- Automatic channel switching without the customer's configured confirmation
  (issue #1 §Proposed standout moment).
- Any owner-only action: license choice, visibility flip, video upload,
  Devpost submission, reviewer access, external feedback, AWS account and
  credential creation, Yahoo application (C9).

## Program plan (D2) — milestones and waves

Times are UTC. One phase is one milestone; the Reviewer cadence is `phase`.
Parallel lanes run inside each wave; work is serialized only on a
dependency, a shared interface, a write-set overlap, or a shared mutable
resource: the single Fire TV stick (device lease), the single AWS account
(deploy lease), the Alphazedehq `skills/` tree, and impl_agent_cap. The slice
graph, write sets and wave membership are in `implementation.json`; the
summary follows.

| Milestone | Title | Due | Entry criteria | Exit criteria |
|---|---|---|---|---|
| M1 | Foundation and shared CI/CD | 2026-10-13T23:00:00Z | Owner approves this package at the integrated review. | Planning package merged on `main`; milestones created (AC-AFC-PLAN-02); D4 skill PRs merged in Alphazedehq (AC-AFC-D4-01..03, -05, -06); repo gate green on a PR (AC-AFC-CI-01..03); Vnv tree (AC-AFC-VNV-01); spec kit imported and building (AC-AFC-SPEC-01); TV starter imported, scanned, debug APK built by the gate; backend skeleton with the frozen API contract green; Scribe log created. |
| M2 | Device and data spikes | 2026-10-15T23:00:00Z | M1 exit for the lanes it consumes; owner has located the stick, confirmed its model, enabled ADB debugging and signed in to at least one provider app; owner has created the AWS Free-plan account and a named AWS CLI profile; owner has submitted the Yahoo application. | SP-1..SP-6 verdict files (AC-AFC-SPIKE-01, -02); panel mode decided within spike_panel_max (AC-AFC-PANEL-05); ESPN fixtures recorded from the 10-12 and 10-15 games; backend skeleton deployed to the dev stage; harness hooks wired (AC-AFC-D4-04); specification rev 0.1 built. |
| M3 | End-to-end slice on the stick | 2026-10-19T06:00:00Z | M2 verdicts; T_yahoo outcome applied (Yahoo or manual lineup). | On Sunday 2026-10-18 with simultaneous live games: alert over provider playback → Watch → provider launch outcome recorded on the stick; panel in the decided mode with live points; profile, monitoring, alerts, watch and core controls verified (AC-AFC-PROF-*, MON-*, FEED-*, ALERT-01, -02, -04, -05, WATCH-*, PANEL-01..03, -05, SEC-*, LW-01, CTRL-01 core). |
| M4 | Feature complete and hardened | 2026-10-21T23:00:00Z | M3 exit. | Corrections, panel consistency, complete controls, persistence (AC-AFC-ALERT-03, PANEL-04, CTRL-01..03); replay labeled; defect queue has no open P0 or P1; specification rev 1.0 (AC-AFC-SPEC-02, -03); visual review evidence (AC-AFC-VIS-01). |
| M5 | Submission ready | 2026-10-23T12:00:00Z | M4 exit. | README and judge access (AC-AFC-SUB-01); owner checklist (AC-AFC-SUB-02); device clips (AC-AFC-SUB-03, -04); per-tool summary and sanitized friction log (AC-AFC-DX-02, -03); final APK built and Reverify run on it; Integration Engineer Lifecycle assessment; the owner submits before T_deadline (owner-only). |

The M5 due time leaves a 7-hour buffer before T_deadline for the owner's
actions.

## Entry criteria

1. The owner approves this five-artifact package at the single integrated
   review, including the decisions listed under Open owner decisions.
2. The Orchestrator commits the planning package on
   `plan/2026-10-11-amazon-fantasy-companion`, scrubbing absolute local paths
   from `specialists/` prompts and logs first (SD-010, SD-011), and lands it
   on `main` through a PR before any lane branches from `main`.
3. Owner-action dependencies are entry criteria, not agent work: stick
   located and model confirmed with ADB debugging enabled (M2), AWS Free-plan
   account and named CLI profile (M2), Yahoo application submitted (M2),
   provider app signed in on the stick (M2), license chosen before the
   visibility flip (M5).
4. Every imported tool passes scan-software-supply-chain before first use.

## Exit criteria

1. Every AC-AFC row has passing evidence named by its SEIT row, or a recorded
   limitation the owner accepted at a class C stop (RISK-AFC-02..04).
2. M1..M5 exit criteria met; each phase reviewed once (OCR included), repaired
   at most once, verified deterministically and landed on `main`.
3. The Assurance Test Engineer (Lifecycle cadence) and the Integration
   Engineer execution session (Lifecycle cadence) return their verdicts on
   the M5 candidate.
4. The DoD Manifest closeout is appended; owner-only actions are listed for
   the owner, not performed.

## Rollback or repair

- A failing slice returns to its lane implementer inside the same phase; one
  repair round per phase after review, then deterministic verification.
- A merged phase that breaks `main` is reverted by a revert PR (no
  force-push), repaired on the lane branch and relanded.
- D4 changes in Alphazedehq are reverted by a revert PR in that repository;
  harness hook wiring is restored from the configuration backup the D4 hook
  slice writes before editing.
- A spike that fails produces a verdict, not a repair; the conditional
  outcome (C1, C5, C6) or a class C owner stop follows.
- A third evidence-changing correction round of any planning gate is a class
  C owner question (owner-stops).

## Accountable controller

The Bearing Lite Orchestrator for AFC-2026-10-11 (Claude Code / Claude Opus
5.5, the checkout-lease controller in `journey.json`) controls dispatch,
landing, leases and owner stops. Coordinators, if used, own one wave each.
William Rumph holds every owner-only action.

## Open owner decisions for the integrated review

| ID | Decision | Recommendation |
|---|---|---|
| OD-AFC-01 | D4 form: extensions of existing shared skills only (SD-018), or extensions plus one thin shared entry-point skill (owner's latest words "Just create the shared skill please"). | Extensions only. `setup-pre-commit` becomes the shared CI/CD gate skill and is already linked into every harness; a second entry-point skill would duplicate its trigger surface, which C10 forbids. Option B costs one light slice (D4-F) if chosen. |
| OD-AFC-02 | Build the optional AI excitement commentary (would load `typesafe-ai`)? | No. Fixed templates driven by the excitement-level setting (AC-AFC-ALERT-05) meet item 3 without a new provider or credential before T_deadline. |
| OD-AFC-03 | Alexa voice spike (C8) as a stretch slice after M3? | Yes, as stretch only: started after M3 exit if every M4 slice is on schedule, dropped at 2026-10-21T12:00:00Z if unverified. |
| OD-AFC-04 | Spike slices on the heavyweight lane run as evidence-only investigations rather than test-first pairs. | Yes. Spikes write verdict files and throwaway probes under `spikes/`; production code that follows a spike uses the lane's `tdd` strategy. |
| OD-AFC-05 | Approve the Lifecycle-local design quantities in the Glossary. | Approve as proposed. |
| OD-AFC-06 | `.gitignore` `*.log` hides specialist logs cited as evidence. | Add a negation for `docs/plans/**/specialists/*.log` in the planning commit so evidence is tracked (SD-011). |
