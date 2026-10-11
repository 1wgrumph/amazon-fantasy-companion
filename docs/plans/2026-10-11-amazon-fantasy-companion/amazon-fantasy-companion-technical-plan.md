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

- **D1** the product architecture specification, written after approval with
  the D5 shared spec-authoring skill (SD-022, which supersedes SD-013);
- **D2** this program plan to T_deadline with parallel waves and milestone
  definitions;
- **D3** the GitHub milestones, created by the Orchestrator after approval;
- **D4** the shared, repo-agnostic CI/CD capability in the owner's shared
  skills (SD-018..SD-021), landed first, followed by harness hooks;
- **D5** one shared, repo-agnostic spec-authoring skill generalized from the
  GridMarket spec kit (template, build, lint and diagram tooling runnable in
  any repository without a project-specific Python environment), with
  nothing GridMarket-specific (SD-022);
- this repository's Vnv guidance tree (SD-014), its local plus Actions gate,
  and the Scribe developer-feedback deliverables of issue #1.

The product is a hackathon entry, not a production system: no customer data
beyond the owner's own accounts, no paid services, no hardware performance
claims.

## Requirements register

No requirements register exists. The repository is greenfield
(`workspace.md` Observed Systems; `repository-map.md`) and this is not a
specification Lifecycle: D1 is a Markdown architecture specification written
with the D5 skill after approval, not an SDoc register, and no Requirements
System host is bound to this repository. Every requirement below is
Lifecycle-local (`AC-*` / `RISK-*`). Sources are the confirmed decisions
DEC-AFC-001, DEC-AFC-002, DEC-AFC-SD-001..SD-022 except the superseded
SD-013 (written `SD-nnn` below),
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
| Vnv guidance tree | `docs/vnv/AGENTS.md` plus one `docs/vnv/<area>/AGENTS.md` per area naming Scope, Tools, Review Focus and findings target (SD-014). |
| gate entrypoint | The one script a repository's local hooks, Actions workflow and harness hooks all invoke (`tools/ci/gate.sh` here). |
| shared skills | The owner's skills in the Alphazedehq repository `skills/` directory, linked into each harness (SD-018). |
| spec-authoring skill | The D5 shared skill `skills/spec-authoring/` in Alphazedehq (SD-022). |
| vendored spec tools | The D5 scripts copied into this repository's `tools/spec/` by the skill's vendor step, with `VENDORED.md` naming the source commit (Alphazedehq is private, so public CI cannot reach the skill). |
| replay | Backend serving of recorded ESPN fixtures, labeled "Replay — recorded game data" wherever shown (C2). |
| spike | A time-boxed device or data investigation that ends in a recorded verdict file, not in product code. |

## Requirements (Lifecycle-local)

Every row is Lifecycle-local. Allocation names the milestone and the
component; components are allocated against the candidate placements of the
Systems Modeler placement receipt (`specialists/systems-modeler-receipt.md`,
run 2, READY), with the naming mapping recorded in `design.md` §Placement
mapping.

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
| AC-AFC-FEED-01 | The backend shall emit GameEvents for ESPN plays and game-state changes that meet the event definitions in DES-AFC-FEED, and for corrections required by AC-AFC-FEED-02, using CONTRACT-AFC-EVENT with source game id, source play id, event type, involved ESPN athlete ids, possession team, field position, period, game clock, source timestamp and ingest timestamp; it shall emit no GameEvent for a play that meets none of those definitions and shall reject a schema-invalid response without changing stored GameEvents. | SD-004, #1 item 3 | test | M3; FeedIngest |
| AC-AFC-FEED-02 | The backend shall emit at most one original GameEvent per source game id and source play id; when the recorded scoring content for that play changes, it shall emit one correction GameEvent for that change referencing the original event, and repeated retrieval of unchanged scoring content shall emit no additional event. | #1 item 3 (duplicates, corrections) | test | M3; FeedIngest |
| AC-AFC-FEED-03 | If one game's ESPN fetch fails or returns a schema-invalid response feed_fail_limit times in a row, then the backend shall mark that game's data stale; when the operator enables replay, the backend shall serve GameEvents from recorded fixtures and every alert and panel value derived from them shall carry the label "Replay — recorded game data". | C2, #1 §Judging (labeled replay) | test | M3; FeedIngest (ReplaySource) |

### Product — alerts (issue #1 item 3)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-ALERT-01 | When a GameEvent of a customer-enabled alert type is a scoring play credited to a followed player, a red_zone_entry by a followed player's team, or a close_game state of a followed player's game, the backend shall create one alert for that customer naming the player or team, the matchup, the event and the source timestamp; a red-zone alert shall state the team's field position only and shall not state that the player is on the field. | #1 item 3 | test | M3; Matcher, AlertPolicy |
| AC-AFC-ALERT-02 | The backend shall create at most one alert per customer per source event, shall hold each alert for the customer's spoiler_delay before release, shall release no alert during the customer's quiet hours, and shall release at most one alert per game per alert_min_gap for that customer. | #1 item 3, #1 item 6 | test | M3; AlertPolicy |
| AC-AFC-ALERT-03 | When a correction GameEvent changes an event that produced a released alert, the backend shall release one correction alert to that customer and shall apply the correction to that customer's panel totals. | #1 item 3, #1 §Right-side panel | test | M4; AlertPolicy, PanelService |
| AC-AFC-ALERT-04 | While a provider app plays video in the foreground and the customer is in an enabled viewing period with heads-up presentation selected, the TV app shall retrieve and present each released alert as a heads-up notification with Watch and Dismiss actions without bringing the companion app to the foreground; while panel-only presentation is selected, it shall suppress heads-up notifications. | #1 item 3, #1 §Development setup | demonstration | M3; AlertService, AlertNotifier |
| AC-AFC-ALERT-05 | The backend shall select alert text through a documented mapping from each customer-selectable excitement level to a fixed template, substituting only GameEvent fields and matched player data; no generative model shall determine an event, score or player identity. | #1 item 3, #1 §Proposed standout moment | test, inspection | M3; AlertPolicy |

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
| AC-AFC-PANEL-01 | The lineup panel shall show the selected team’s starters, each player’s fantasy points and game status, and the team total using the league’s Yahoo scoring rules or, for a manual lineup, a documented default scoring table that specifies each counted statistic and its point coefficient; it shall label manual scoring “Default scoring,” mark each value older than stale_after “Stale,” and mark each unavailable value “Unavailable.” | #1 §Right-side panel | test | M3; PanelService, LineupPanel |
| AC-AFC-PANEL-02 | While the panel is shown with video, the video shall occupy the area left of the panel with its aspect ratio preserved, and no pixel of the video frame shall be covered or cropped. | #1 §Right-side panel | demonstration, inspection | M3; LineupPanel, CompanionPlayer |
| AC-AFC-PANEL-03 | The TV app shall let the customer show and hide the lineup panel and select the followed team and league using only the remote’s D-pad, select and back keys, with a visible focus indicator on every focusable element. | #1 §Right-side panel | demonstration | M3; LineupPanel |
| AC-AFC-PANEL-04 | When a starter change or scoring correction reaches the backend, the backend shall include it in subsequent panel responses, and the visible panel shall request those responses every panel_refresh and apply each received response; after being hidden, the panel shall request updated state when shown, and any panel value and released alert referring to the same event shall use the same corrected source facts, irrespective of whether other events produced alerts. | #1 §Right-side panel | test | M4; PanelService, LineupPanel |
| AC-AFC-PANEL-05 | The SP-4 spike shall record a Mode B verdict naming the verified route, or a Mode A verdict, within spike_panel_max; in Mode A the companion player shall play only CC-BY or CC0 footage showing the label "Sample footage — not a live broadcast" on screen, and the README shall credit that footage. | SD-006, SD-006a, C5 | inspection, demonstration | M2 (verdict), M3 (Mode A or B build); CompanionPlayer |

### Product — spikes, security and lightweight design

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-SPIKE-01 | The SP-1 spike shall record the stick's model, Fire OS version and Android API level; if the API level is below min_sdk, the OS is Fire OS 5 or older, or the provider apps cannot run, then device work shall stop and the finding shall return to the owner without any purchase or platform switch. | SD-001, SD-003, C1 | inspection | M2; SP-1 device compatibility verdict (`docs/spikes/`), TV app build configuration |
| AC-AFC-SPIKE-02 | The program shall record a verdict file `docs/spikes/SP-<n>-<topic>.md` for each spike SP-1..SP-6, containing the route tried, exact steps, evidence paths, verdict and limits, with SP-1..SP-5 complete by M2 exit and SP-6 recorded at T_yahoo. | #1 §Development setup, #1 §Right-side panel (record which routes work) | inspection | M2 (SP-1..SP-5), M3 entry at T_yahoo (SP-6); spike verdict records, DeviceAuth/LineupConnector access check |
| AC-AFC-SEC-01 | The APK and every tracked file shall contain no Yahoo client secret, OAuth token, AWS credential or device token; the backend shall read the Yahoo client secret from SSM Parameter Store SecureString and shall keep Yahoo OAuth tokens exclusively in backend storage, without returning them to the TV app. | Cross-repo rule 2, SD-005 | test, inspection | M1 (hygiene), M3; DeviceAuth, LineupConnector |
| AC-AFC-SEC-02 | The backend shall require a valid device bearer token on every API route except link start, link status, link verify and the OAuth callback, and shall answer a request with a missing or invalid token with HTTP 401 and no change to stored state. | Cross-repo rule 2 | test | M3; API, DeviceAuth |
| AC-AFC-SEC-03 | The backend template shall declare only resource types on the template allow list (Lambda, API Gateway HTTP API, DynamoDB on-demand, EventBridge Scheduler, SSM parameter, IAM role, CloudWatch log group), and the deploy command shall fail before any change when the template declares another type. | SD-005, C4 | test | M1 (check), M2 (deploy); backend infra |
| AC-AFC-SEC-04 | The backend shall request only Yahoo's read scope. | #1 §Source review (read-only) | inspection | M3; LineupConnector |
| AC-AFC-LW-01 | The TV app shall run network requests and JSON parsing off the main thread, shall redraw only panel rows whose values changed, and shall stop panel requests while the panel is hidden; no document or submission text shall state a measured device latency, frame rate or memory figure. | #1 §Lightweight device design | inspection, test | M3, M5; TV app, docs |

### Deliverable D5 — shared spec-authoring skill (Alphazedehq)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-D5-01 | The Alphazedehq repository shall contain one shared skill `skills/spec-authoring/` holding a `SKILL.md` within skill_size_max, a specification template, and build, lint and diagram scripts that run with `uv run --script` (PEP 723 inline dependencies) and Graphviz `dot`, without any project-specific Python environment, and shall retain the GridMarket MIT copyright and permission notice. | SD-022, C10, `create-lean-skill` | test, inspection | M1; D5 (S06) |
| AC-AFC-D5-02 | The spec-authoring skill’s operational text, templates and tool invocation shall contain no GridMarket product name, document id or `--project backend` flag; GridMarket references shall occur only in retained license, attribution and provenance records, and the skill shall contain no absolute local path; building and linting its shipped template in a temporary directory outside any git repository shall exit 0. | SD-022 ("nothing GridMarket-specific"), SD-019, C7 | test | M1; D5 (S06) |
| AC-AFC-D5-03 | The spec-authoring skill description shall name SDoc and Requirements System documents as non-triggers and shall cite `requirements-engineering` by reference without restating its checklist, so that a request to author and build a Markdown specification selects spec-authoring and a request to publish an SDoc revision to the Requirements System selects `use-requirements-system`. | `create-lean-skill`, C10 | test, inspection | M1; D5 (S06) |
| AC-AFC-D5-04 | The skill's vendor step shall copy its scripts to `<repo>/tools/spec/` with a `VENDORED.md` naming the source repository, commit and MIT notice, and shall refuse to overwrite a vendored copy whose files differ from that recorded commit. | SD-022, SD-010 | test | M1; D5 (S06) |
| AC-AFC-D5-05 | The program shall land the spec-authoring skill in Alphazedehq through its own pull request merged by rebase or merge commit, shall then link it into every harness skill directory that already links the shared skills, and shall have the D4 hook installer link it for the remaining harnesses of SD-021 or record each as a typed gap. | SD-022, workspace rule (never squash), coverage ledger (Muse skills gap) | inspection | M1; D5 shared spec-authoring skill and shared-skill links; M2; shared harness hook installer and harness skill-directory configurations |

### Deliverable D1 — architecture specification (written with D5)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-SPEC-01 | When the D5 pull request (AC-AFC-D5-01..05) is merged, the D1 slice shall vendor `tools/spec/` with the D5 vendor step, with `VENDORED.md` naming the merged Alphazedehq commit and `THIRD_PARTY_NOTICES.md` carrying the GridMarket MIT notice, and no D1 authoring shall start before that merge. | SD-022, SD-009 | inspection | M2; D1 specification sources, vendored spec tools and license/provenance records (S19) |
| AC-AFC-SPEC-02 | The specification under `spec/amazon-fantasy-companion/` shall contain every structural-floor element required by COE-ASA-001, bind every product AC-AFC row in at least one section, pass the spec lint and figure lint with zero findings, and produce a byte-identical built file on a second build from unchanged sources. | SD-012, SD-022, COE-ASA-001 | test | M2 (rev 0.1), M4 (rev 1.0); D1 specification sources and build (S19, S35) |
| AC-AFC-SPEC-03 | The specification revision 1.0 shall record the SP-1..SP-6 verdicts, the panel mode, the SP-3 provider route and every recorded limitation. | SD-006, #1 §Right-side panel | inspection | M4; D1 specification revision 1.0 (S35) |

### Deliverables D2 and D3 — program plan and milestones

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-PLAN-01 | The program plan shall define milestones M1..M5, each with title, due date, entry criteria, exit criteria and slices; every slice shall belong to exactly one milestone and one wave, and no wave shall schedule more than impl_agent_cap concurrent implementation agents. | SD-012, Rule 17 | inspection | Planning, checked at M1 entry; D2 program plan and milestone/wave table |
| AC-AFC-PLAN-02 | When the owner approves this package, the Orchestrator shall create milestones M1..M5 in `1wgrumph/amazon-fantasy-companion` with the planned titles, due dates and descriptions, and the `gh api` readback shall equal the milestone table. | SD-012 (D3) | inspection | M1; D3 GitHub milestone records |

### This repository's gate and Vnv tree

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-CI-01 | The repository shall have one gate entrypoint `tools/ci/gate.sh` with the areas `android`, `backend`, `spec` and `hygiene`; the local pre-commit and pre-push hooks and the Actions workflow shall invoke that entrypoint with the same area arguments, and each area shall exit non-zero when any of its checks fails. | SD-016, SD-021 | test | M1; repo gate |
| AC-AFC-CI-02 | The Actions workflow shall trigger on `pull_request` and `push` to `main` only (never `pull_request_target`), shall use a concurrency group per workflow and ref with cancel-in-progress, shall run an area only when its paths change, shall report one stable check name per area, shall pin every action to a full commit SHA, shall grant `contents: read` only, shall expose no secret to fork pull requests, and shall run on GitHub-hosted runners. | SD-017, SD-021, C14 | test | M1; repo gate |
| AC-AFC-CI-03 | The `hygiene` area shall reject tracked files matching an absolute user-home path shape or the repository’s documented credential-detection rules for Yahoo client secrets, OAuth tokens, AWS credentials and device tokens, and shall identify each finding by file and rule identifier without printing the matched secret. | Cross-repo rule 12, SD-010, C7 | test | M1; repo gate |
| AC-AFC-VNV-01 | The repository shall contain the Vnv guidance tree: `docs/vnv/AGENTS.md` and one `docs/vnv/<area>/AGENTS.md` per area (tv-app, backend, device-integration, ci-cd, spec, developer-feedback), each naming Scope, Tools, Review Focus and findings target. | SD-014 | inspection | M1; Vnv guidance tree (`docs/vnv/AGENTS.md` and area guidance files) |

### Deliverable D4 — shared CI/CD capability (Alphazedehq shared skills)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-D4-01 | The shared `setup-pre-commit` skill shall define one repo-agnostic gate entrypoint contract, shall ship a template gate script and an installer for local git hooks that invoke it, shall state that GitHub Actions invoke the same entrypoint, shall contain no `[TODO]` text, and its `SKILL.md` shall be within skill_size_max. | SD-018, SD-021, DX-007, C10 | test, inspection | M1; D4 |
| AC-AFC-D4-02 | The shared `setup-a-repo` skill shall reference a workflow-authoring guide stating the rules of AC-AFC-CI-02 plus free hosted runners on public repositories and the gh_private_minutes budget (C11), and shall ship a checker script that exits non-zero on a workflow violating any of those rules; its `SKILL.md` shall be within skill_size_max. | SD-017, SD-019, SD-021, C11, C14 | test | M1; D4 |
| AC-AFC-D4-03 | The shared `ship-pull-request` skill shall run `vnv-review` when the repository has a Vnv guidance tree (`docs/vnv/AGENTS.md` or `Vnv/AGENTS.md`) and otherwise record REFUSED_NO_VNV, never a pass; its `references/GATES.md` shall gain a shared-gate row and an amazon-fantasy-companion row; its `SKILL.md` shall be within skill_size_max. | SD-020, SD-021, C10, C12 | test, inspection | M1; D4 |
| AC-AFC-D4-04 | When AC-AFC-D4-01..03 are merged (C13), one shared hook script shall run the current repository's gate entrypoint before an agent-initiated `git commit` or `git push` in every harness named in SD-021 that exposes a pre-tool hook; the installer shall record each harness without one as a typed gap with its exact evidence, and shall expose the D4 skills in Muse's skill directory. | SD-021, C13, coverage ledger (Muse skills gap) | test, demonstration | M2; D4 |
| AC-AFC-D4-05 | The program shall land each D4 skill change in Alphazedehq through its own pull request merged by rebase or merge commit, after the skill is exercised against one matching and one non-matching request. | SD-021, create-lean-skill, workspace rule (never squash) | inspection | M1; D4 |
| AC-AFC-D4-06 | The D4 skill and hook text shall name no repository, owner, pilot or exclusion that scopes the capability. | SD-019 | inspection | M1; D4 |

### Scribe developer feedback (issue #1 contract)

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-DX-01 | The program shall give every dispatch packet and every return in this Lifecycle a `developer_feedback` section that lists observations with IDs and evidence, or states "no new observations" and names the tools exercised. | #1 §Scribe contract | inspection | M1–M5; Lifecycle dispatch/return records and Scribe observation log |
| AC-AFC-DX-02 | The repository shall contain the running observation log, a per-tool summary (purpose, onboarding, what worked, what needs work, willingness to reuse) and a sanitized friction log (task, reproduction steps, expected and actual behavior, severity, workaround, suggestion) that cover every tool, API, SDK and device used and carry DX-001..DX-007. | #1 §Scribe contract, SD-011 | inspection | M1; developer-feedback observation log; M5; per-tool summary and friction log |
| AC-AFC-DX-03 | The per-tool summary and the friction log shall contain no credential, personal account detail or absolute local path, and shall be checked against the current official rules before submission. | #1 §Scribe contract, SD-010, C7 | test, inspection | M5; developer-feedback per-tool summary and friction log |

### Submission

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-SUB-01 | The README shall give setup steps (build the APK, deploy the backend to the reader's own AWS Free-plan account, link Yahoo or enter a manual lineup, run replay), footage credits, the panel-mode and voice limitation statements, and the judge-access arrangement through T_judge_access. | #1 §Acceptance, SD-006, C8 | inspection | M5; README and judge-access setup documentation |
| AC-AFC-SUB-02 | The submission checklist shall list every owner-only action (license choice, visibility flip, ESPN terms decision, video upload, reviewer access, Devpost submission, external feedback) with its due time before T_deadline, and agents shall perform none of them. | SD-009, C3, C9 | inspection | M5; submission checklist and owner-action records |
| AC-AFC-SUB-03 | The demo material shall consist of clips recorded from the device for the storyboard segments of #1, with every replay segment labeled as replay and every Mode A segment labeled as sample footage. | #1 §Proposed video storyboard, C2, SD-006a | inspection | M5; device clips and storyboard/clip index |
| AC-AFC-SUB-04 | The demo material and the submission text shall show voice or Alexa behavior only if it is implemented and verified on the device. | SD-008, C8 | inspection | M5; device clips and submission text |

### Lifecycle-level requirements

| ID | Statement | Source | Verification | Allocation |
|---|---|---|---|---|
| AC-AFC-LAND-01 | The program shall land each phase's lane branches on `main` through pull requests merged by rebase or merge commit after one Reviewer review, at most one repair round and a green gate entrypoint run, with no squash merge, force-push or commit on local `main`. | Workspace cross-repo rules 4 and 9; Worktrees "Never squash-merge"; this plan §Program plan and §Rollback or repair | inspection | M1–M5; phase landing records, Reviewer/repair receipts and gate entrypoint evidence |
| AC-AFC-REV-01 | The program shall put OCR in delegation mode (`ocr delegate preview`, `ocr delegate rule`) into every Reviewer packet together with either Reverify (claims about the built APK) or `Reverify: not applicable — <reason>`, and shall record an OCR or Reverify run that cannot complete as a typed gap with its exact error. | Cross-repo rule 15, frozen profiles (`review.coverage_assist`, `deterministic_verification.reverify`) | inspection | M1–M5; Reviewer dispatch packets, OCR/Reverify capability records and execution receipts |
| AC-AFC-VIS-01 | When a change alters rendered TV UI, the program shall review it on the stick with screenshots captured by `adb exec-out screencap -p` for each changed screen and state, kept with the review evidence and containing no customer data. | Cross-repo rule 16 | inspection | M3, M4; TV app visual-review screenshots and review records |
| AC-AFC-PATH-01 | The program shall commit no file in this Lifecycle that contains an absolute local home path; plan artifacts shall use repository-relative paths or `<PLANNING_WORKTREE>` / `$HOME` placeholders. | Cross-repo rule 12, SD-010, C7 | test | Planning and M1–M5; tracked artifacts and repo hygiene gate |

### Risks

| ID | Statement (control) | Source | Verification | Allocation | Risk (rationale) | Response |
|---|---|---|---|---|---|---|
| RISK-AFC-01 | If the stick cannot be located, its API level is below min_sdk, its OS is Fire OS 5 or older, or the provider apps cannot run, then the program shall stop device work and record the condition for the owner without purchasing a device or switching platforms. | SD-001, SD-003, C1, AC-AFC-SPIKE-01 | inspection | M2; SP-1 device compatibility verdict and device-work entry control | The stick cannot be found, is Fire OS 5 or older, is below min_sdk, or cannot run the provider apps. | Stop device work and return to the owner; never buy or switch platforms on the owner's behalf. |
| RISK-AFC-02 | If SP-2 cannot demonstrate a heads-up notification over provider playback, then the program shall record the exact device and route limitation, retain panel-only presentation, and record AC-AFC-ALERT-04 as unmet pending an owner scope decision. | #1 Development setup, AC-AFC-ALERT-04 | inspection | M2; SP-2 notification verdict and AlertNotifier; M3; integration acceptance record | Fire OS on the stick does not show a heads-up notification over a provider app's playback. | Record the exact limitation; panel-only presentation remains; owner scope decision (class C). |
| RISK-AFC-03 | If SP-3 finds no supported content-level link for a specific game, then the program shall record the verified details-page or app-home outcome and its limitation, prepare the missing-interface proposal for the owner, and retain AC-AFC-WATCH-02 as unmet until a specific-game route is demonstrated or the owner changes its acceptance condition. | #1 App launch and game/channel routing research, AC-AFC-WATCH-01, AC-AFC-WATCH-02 | inspection | M2; SP-3 provider-route verdict and ProviderResolver registry; M3; WatchLauncher integration acceptance record | No provider exposes a content-level deep link the companion can invoke for a specific game. | Ship the best verified outcome (details or app home), state the limitation, and record the missing interface as an integration proposal for the owner. |
| RISK-AFC-04 | If SP-4 fails to verify Mode B within spike_panel_max, then the system shall use Mode A under AC-AFC-PANEL-05 and the submission materials shall state that the panel is beside the companion’s sample footage rather than provider playback. | SD-006, SD-006a, C5, AC-AFC-PANEL-05 | inspection, demonstration | M2; SP-4 verdict; M3; CompanionPlayer/LineupPanel; M5; submission materials | No supported route places the panel beside a provider app's video. | Mode A with labeled footage; limitation stated in the submission. |
| RISK-AFC-05 | If ESPN responses become unavailable or schema-invalid, then the backend shall apply the rejection and stale-data rules of AC-AFC-FEED-01 and AC-AFC-FEED-03 and use labeled replay for the affected demo segments; the submission checklist shall retain the ESPN-terms decision as an owner-only action. | SD-004, C2, C3, AC-AFC-FEED-01, AC-AFC-FEED-03, AC-AFC-SUB-02 | test, inspection | M3; FeedIngest/ReplaySource; M5; submission checklist and demo material | ESPN's unofficial endpoints change, rate-limit or go down. | Switch to labeled replay for the demo; owner decides ESPN terms at submission (C3). |
| RISK-AFC-06 | If Yahoo access is not approved at T_yahoo, then the system shall provide manual lineup entry from ESPN rosters and label every display of that lineup “Manual lineup” under AC-AFC-PROF-04. | SD-007, C6, AC-AFC-PROF-04 | test | M3; LineupConnector (ManualSource), ProfileSettings and LineupPanel | Yahoo access is not approved by T_yahoo. | Labeled manual lineup. |
| RISK-AFC-07 | If a selected route reaches a confirmed usage or rate limit, then the Orchestrator shall record the limit evidence and activate only the next approved fallback in the frozen profile with a class B receipt preserving the selected coverage-assist and Reverify settings, or queue the slice when no approved fallback remains; other invocation, configuration, authentication or runtime errors shall not trigger a route switch. | DEC-AFC-PROFILE-001, frozen profile fallback order, owner route-preservation instructions | inspection | M1–M5; frozen lifecycle binding, dispatch packets and route-activation receipts | A frozen route's usage window is exhausted mid-wave (observed: Muse HTTP 429 on 2026-10-11, reset 2026-10-12T00:00:00Z). | Activate the next approved fallback; queue the slice when all are exhausted. |
| RISK-AFC-08 | If private-repository Actions usage exhausts gh_private_minutes, then the program shall stop hosted workflow runs and retain local gate evidence without enabling paid overage unless the owner authorizes it. | SD-017, C11, AC-AFC-CI-02 | inspection | M1–M5; GitHub Actions workflow/budget control and repo gate evidence | Actions minutes on the private repository run out (C11). | Hosted runs stop; local gate evidence continues; no paid overage without the owner. |
| RISK-AFC-09 | If the AWS Free-plan limits or credits are exhausted or a deployment would introduce a resource outside AC-AFC-SEC-03, then the program shall stop the affected scheduled work or reject that deployment before a change, and shall make no paid-plan change without the owner’s decision. | SD-005, C4, AC-AFC-SEC-03 | test, inspection | M2–M5; backend infrastructure deployment guard and EventBridge scheduler control | AWS Free-plan limits or credits are reached, or a paid resource is introduced (C4). | Stop the scheduler; owner decides any plan change. |
| RISK-AFC-10 | If the Matcher cannot establish a Yahoo-to-ESPN player identity, then the system shall label that player “Unmatched” and withhold player-attributed points and alerts until a verified mapping is available; when a mapping correction changes an already released player attribution, it shall apply the correction to the affected alert and panel state. | #1 item 3 and Right-side fantasy lineup panel; DES-AFC-LINEUP; AC-AFC-ALERT-03 | test | M3; Matcher identity map and LineupPanel; M4; AlertPolicy/PanelService corrections | Yahoo and ESPN player identities mismatch, so alerts miss or misattribute a player. | Manual mapping override in the identity map; correction alert. |
| RISK-AFC-11 | When a secret, personal account detail or absolute local path is detected in material intended for the public repository, the program shall block its merge or publication until sanitized; if exposure has already occurred, it shall record the affected artifact without reproducing the sensitive value and notify the owner for credential rotation or other protected remediation. | Cross-repo rules 2 and 12, SD-010, C7, AC-AFC-SEC-01, AC-AFC-CI-03, AC-AFC-PATH-01 | test, inspection | M1–M5; repo hygiene gate, publication checklist and incident record | A secret, account detail or absolute local path reaches the public repository. | Remove before merge; credential rotation is the owner's action. |
| RISK-AFC-12 | If Muse or AGY exposes no supported pre-tool hook, then the D4 installer shall record that harness as a typed gap with exact capability evidence and retain local git hooks invoking the shared gate, without treating those hooks as proof of the missing harness integration. | SD-021, C13, AC-AFC-D4-04 | inspection, demonstration | M2; shared harness hook installer, harness configurations and local git hooks | Muse or AGY exposes no pre-tool hook surface. | Record the gap; git hooks still run the gate locally. |
| RISK-AFC-13 | The program shall obtain a scan-software-supply-chain receipt before first use of each external software acquisition, refuse use on BLOCK or INDETERMINATE, and verify the pinned distribution checksum for the Gradle wrapper before executing the downloaded distribution. | Cross-repo rule 10; RISK-AFC-13 Control | inspection | M1–M5; software acquisition receipts and TV app build configuration | Imported software (starter, Android SDK, Gradle wrapper, AWS SAM CLI, uv, spec kit) is compromised. | Fail closed on BLOCK or INDETERMINATE. |
| RISK-AFC-15 | If matching and non-matching request checks expose a trigger collision between the D5 skill and `use-requirements-system`, then the program shall record the failing requests and repair the D5 trigger boundary under AC-AFC-D5-03; any reciprocal edit to `use-requirements-system` shall follow the OD-AFC-07 disposition recorded at integrated review. | SD-022, C10, AC-AFC-D5-03, OD-AFC-07 (pending, not confirmed) | inspection | M1; D5 skill description and trigger-check receipts; shared Requirements System skill description only if OD-AFC-07 authorizes its edit | The new spec-authoring skill and `use-requirements-system` both trigger on "architecture specification" requests. | Narrow the descriptions in the D5 repair round; never merge two skills. |
| RISK-AFC-16 | If D5 lands later than planned, then the program shall reschedule D1 after that merge, record the schedule impact, and leave the D1 revision 0.1 M2 exit criterion unmet until delivered, without reverting to the superseded project-local GridMarket kit. | SD-022 superseding SD-013, AC-AFC-SPEC-01, M2 exit criterion | inspection | M1; D5 landing receipt; M2; D1 specification and milestone exit record | D5 lands late and delays D1 rev 0.1. | D1 rev 0.1 moves within M2; M2 exit records the slip; no fallback to copying the GridMarket kit (SD-013 superseded). |
| RISK-AFC-14 | If a planned live-game capture or demonstration window is missed, then the program shall use labeled replay for affected demo segments and record any unmet live-integration obligation separately, without presenting replay as the M3 simultaneous-live-games demonstration. | C2, #1 Judging alignment and Development setup, M3 exit criterion | inspection | M2; FeedIngest fixture capture; M3; live integration record; M5; demo clips | Few live NFL windows remain before T_deadline (Mon 10-12, Thu 10-15, Sun 10-18, Mon 10-19, Thu 10-22 US time). | Fall back to labeled replay for any segment that misses its window. |

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
- Copying the GridMarket kit into this repository as project-local skills
  (SD-013, superseded by SD-022); this repository receives only the vendored
  scripts of the shared D5 skill.
- Generative AI commentary unless the owner selects it at the integrated
  review (coverage ledger: `typesafe-ai` deferred). Recommendation: exclude.
- Automatic channel switching without the customer's configured confirmation
  (issue #1 §Proposed standout moment).
- Any owner-only action: license choice, visibility flip, video upload,
  Devpost submission, reviewer access, external feedback, AWS account and
  credential creation, Yahoo application (C9).

## Program plan (D2) — milestones, lanes and waves

Times are UTC. One phase is one milestone; the Reviewer cadence is `phase`.
Ready independent work is dispatched at once; work is serialized only on a
dependency, a shared interface, a write-set overlap, or a shared mutable
resource: the single Fire TV stick (`fire-tv-stick` lease), the single AWS
account (`aws-afc-dev` lease), one Alphazedehq skill directory per slice
(`alphazedehq-skills/<skill>`), the harness configurations
(`harness-configs`), the Alphazedehq main checkout every harness skill link
resolves to (`alphazedehq-main-checkout`: fast-forward only, between
dispatches, HEAD recorded in each later packet), the live NFL game windows
(`live-game-window`), and impl_agent_cap. Corrections IE-F01..IE-F18 from the
Integration Engineer (`specialists/integration-plan.md`) are applied. The full slice table, dependencies and write sets are in
`slice-graph.md` and, after integration, `implementation.json`.

### Milestones (ready to create as GitHub milestones after approval)

| Milestone | Title | Due | Entry criteria | Exit criteria | Slices |
|---|---|---|---|---|---|
| M1 | Foundation, shared CI/CD and spec skill | 2026-10-13T23:00:00Z | Owner approves this package at the integrated review; planning package merged on `main`. | Milestones created (AC-AFC-PLAN-02); D4-A..C PRs merged in Alphazedehq (AC-AFC-D4-01..03, -05, -06); D5 PR merged and linked (AC-AFC-D5-01..05 except Muse/AGY); repo gate green on a PR (AC-AFC-CI-01..03); Vnv tree (AC-AFC-VNV-01); TV starter imported, scanned, debug APK built by the gate; backend skeleton with the frozen API contract green; Scribe log created (AC-AFC-DX-01, -02 log); S16 2026-10-12 capture committed on its slice branch. | S01, S02, S03, S04, S05, S06, S06L, S07, S08, S09T, S09, S10 |
| M2 | Device and data spikes, harness hooks, spec rev 0.1 | 2026-10-16T06:00:00Z | M1 exit for the lanes it consumes; owner has located the stick, confirmed its model, enabled ADB debugging and signed in to at least one provider app; owner has created the AWS Free-plan account and a named AWS CLI profile; owner has submitted the Yahoo application. | SP-1..SP-5 verdict files (AC-AFC-SPIKE-01, -02); panel mode decided within spike_panel_max (AC-AFC-PANEL-05); ESPN fixtures from the 10-12 and 10-15 games; backend deployed to the dev stage; harness hooks wired or typed gaps (AC-AFC-D4-04, AC-AFC-D5-05 Muse/AGY); specification rev 0.1 built with D5 (AC-AFC-SPEC-01, -02). | S11T, S11, S12, S13, S14, S15, S16, S18, S19, S41 (conditional) |
| M3 | End-to-end slice on the stick | 2026-10-19T06:00:00Z | M2 verdicts; T_yahoo outcome applied (Yahoo or manual lineup). | On Sunday 2026-10-18 with simultaneous live games: alert over provider playback → Watch → provider launch outcome recorded on the stick; panel in the decided mode with live points (AC-AFC-PROF-*, MON-*, FEED-*, ALERT-01, -02, -04, -05, WATCH-*, PANEL-01..03, -05, SEC-*, LW-01, CTRL-01 core). | S17, S20T, S20, S21T, S21, S22T, S22, S23T, S23, S24T, S24, S25T, S25, S26T, S26, S27T, S27, S28 |
| M4 | Feature complete and hardened | 2026-10-21T23:00:00Z | M3 exit. | Corrections, panel consistency, complete controls, persistence (AC-AFC-ALERT-03, PANEL-04, CTRL-01..03); replay labeled; no open P0 or P1 defect; specification rev 1.0 (AC-AFC-SPEC-02, -03); visual review evidence (AC-AFC-VIS-01). | S30T, S30, S31T, S31, S32T, S32, S33, S34 (stretch), S35 |
| M5 | Submission ready | 2026-10-23T12:00:00Z | M4 exit. | README and judge access (AC-AFC-SUB-01); owner checklist (AC-AFC-SUB-02); device clips (AC-AFC-SUB-03, -04); per-tool summary and sanitized friction log (AC-AFC-DX-02, -03); final APK built and Reverify run on it; Integration Engineer Lifecycle assessment; the owner submits before T_deadline (owner-only). | S36, S37, S38, S39, S40 |

The M5 due time leaves a 7-hour buffer before T_deadline for the owner's
actions. Each milestone description on GitHub carries its entry and exit
criteria and slice list from this table (S10).

### Lanes

| Lane | Frozen profile | Strategy | Slices |
|---|---|---|---|
| spec-and-docs | tech-writing | single_implementer | S01, S02, S03, S06, S07, S19, S35, S36, S37, S41 (D4/D5 skill text, D1, docs) |
| backend | primary | tdd | S05, S09T, S09, S11T, S11, S16, S18, S20T..S24, S30T, S30 |
| device-integration-spikes | heavyweight | tdd (spikes evidence-only, OD-AFC-04) | S04, S12, S13, S14, S15, S25T, S25, S28, S34 |
| tv-app-ui | frontend | tdd | S26T, S26, S27T, S27, S31T, S31, S32T, S32 |
| defects | bug-triager | tdd | S33 |
| light work | lane profile's Light Implementer route | light | S06L, S10, S17, S38, S40 |
| Scribe side lane | primary (Scribe route) | — | S08, S39 |

### Waves and dispatch order (impl_agent_cap = 5)

| Wave | Slices | Dispatch order and serialization |
|---|---|---|
| Wave 1 (M1; S16 belongs to M2) | S01 S02 S03 S04 S05 S06 S06L S07 S08 S09T S09 S10 S16 | First five: S16 (the Monday 2026-10-12 game window is the first live data; its session closes between the 10-12 and 10-15 captures to free the slot), S06 (D5 gates D1), S01 (gates S09T and S11T), S04, S05. As slots free: S02, S03, S07, S10, then S09T after S01, S02 and S06 merge, S09 after S09T, S06L after S06 merges. S08 (Scribe) runs beside them, uncounted; its hygiene receipt waits for S09 (IE-F03). S01, S02, S03, S06 touch disjoint skill directories and run in parallel. |
| Wave 2 (M2) | S11T S11 S12 S13 S14 S15 S18 S19 S41 | S12 → S13 → S14 → S15 serialize on `fire-tv-stick`; S18 holds `aws-afc-dev`; S19 starts when S06 is merged; S11T → S11 after S01..S03 merge (C13) and S09 merges (IE-F15), S11 holds `harness-configs`; S41 only if OD-AFC-01 = B. At most five run at once: the stick chain counts one. |
| Wave 3 (M3) | S17 S20T S20 S21T S21 S22T S22 S23T S23 S24T S24 S25T S25 S26T S26 S27T S27 S28 | Red slices first in critical-path order S20T, S22T, S25T, S21T, S23T, then their greens; then S24, S26, S27 pairs (S27T waits for S15's panel verdict). S17 at T_yahoo. S28 on Sunday 2026-10-18 holds `fire-tv-stick`, `aws-afc-dev` and `live-game-window`. |
| Wave 4 (M4) | S30T S30 S31T S31 S32T S32 S33 S34 S35 | S33 dispatches per defect when its write set does not overlap a running slice; S34 only if OD-AFC-03 = yes and M4 is on schedule |
| Wave 5 (M5) | S36 S37 S38 S39 S40 | S36 and S37 in parallel; S38 after S37 (stick); S39 (Scribe) after M4; S40 after S36. |

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
| OD-AFC-01 | D4 form: extensions of existing shared skills only (SD-018), or extensions plus one thin shared entry-point skill (owner's latest words "Just create the shared skill please"). | **A — extensions only.** `setup-pre-commit` becomes the shared CI/CD gate skill and is already linked into every harness; a second entry-point skill would only route to the three extended skills and duplicate their trigger surface, which C10 forbids. If "the shared skill" meant one new named skill, option B costs one light slice (S41, `skills/ci-cd/SKILL.md`, a router under 25 lines) and changes nothing else. |
| OD-AFC-02 | Build the optional AI excitement commentary (would load `typesafe-ai`)? | No. Fixed templates driven by the excitement-level setting (AC-AFC-ALERT-05) meet item 3 without a new provider or credential before T_deadline. |
| OD-AFC-03 | Alexa voice spike (C8) as a stretch slice after M3? | Yes, as stretch only: started after M3 exit if every M4 slice is on schedule, dropped at 2026-10-21T12:00:00Z if unverified. |
| OD-AFC-04 | Spike slices on the heavyweight lane run as evidence-only investigations rather than test-first pairs. | Yes. Spikes write verdict files and throwaway probes under `spikes/`; production code that follows a spike uses the lane's `tdd` strategy. |
| OD-AFC-05 | Approve the Lifecycle-local design quantities in the Glossary. | Approve as proposed. |
| OD-AFC-06 | `.gitignore` `*.log` hides specialist logs cited as evidence. | Add a negation for `docs/plans/**/specialists/*.log` in the planning commit so evidence is tracked (SD-011), after the Orchestrator scrubs absolute local paths. |
| OD-AFC-07 | D5 trigger boundary: the new `spec-authoring` skill owns Markdown section-sourced specifications; `use-requirements-system` keeps SDoc/Requirements System specifications. Add the reciprocal non-trigger to `use-requirements-system`'s description in the same D5 PR? | Yes. Both descriptions today would match "write the architecture specification"; one line in each description removes the collision (RISK-AFC-15). Without it, S06 edits only the new skill and records the residual collision. |
| OD-AFC-08 | D5 shape: one skill `spec-authoring` (author, figure and lint procedures; figure and lint detail in `references/`) versus three skills mirroring GridMarket (`spec-author`, `spec-diagram`, `spec-lint`). | One skill. The three share one trigger surface and one toolchain; one `SKILL.md` within skill_size_max plus references keeps the catalog lean (C10). |
| OD-AFC-09 | Vendor the D5 scripts (MIT-derived from public GridMarket) into this repository's `tools/spec/` so public CI can run the `spec` gate area, given Alphazedehq is private. | Yes. The scripts derive from public MIT code; SD-011 already publishes this repository's contents; the MIT notice travels in `VENDORED.md` and `THIRD_PARTY_NOTICES.md`. |
| OD-AFC-10 | In a repository without a Vnv guidance tree, does `ship-pull-request`'s `REFUSED_NO_VNV` block the merge (SM finding F10)? | No. Record `REFUSED_NO_VNV` as a non-pass gate row in the PR (C12) and let the repository's own required checks decide the merge; blocking would stop merges in every repository the owner touches (SD-019) until each gains a tree. This repository has a tree (SD-014), so its merges always run `vnv-review`. |
