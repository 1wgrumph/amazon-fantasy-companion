# ST-3a Contextual Placement Pass

- Role: Systems Modeler, planning session (`BEARING_ROLE=systems_modeler`)
- Lifecycle: AFC-ST-2026-10-12 (parent AFC-2026-10-11), step ST-3a
- Consumer: Requirements Engineer, before the first ST-2 register draft
  (technical plan §Phase 1 spec track and Phase 2 sequence, ST-2 entry: ST-3a;
  allocation-inputs rule 1)
- Status: contextual pass only. No requirements drafted, no models authored.
- Sources: issue #1 body (`gh api repos/1wgrumph/amazon-fantasy-companion/issues/1`);
  `docs/plans/2026-10-11-amazon-fantasy-companion/scope-decision-batch.md`
  (SD-001..SD-021, C1..C14); `amazon-fantasy-companion-technical-plan.md`
  (Phase 1); `design.md`; `views/` (V1..V3 reference input);
  `specialists/systems-modeler-receipt.md` (prior product placements, non-binding
  input re-derived here, not copied); starter `AmazonAppDev/hello-world-fire-tv`
  (read via `gh api` only).

## 1. Current flow

None. Greenfield product: the working tree holds `README.md`, `docs/` and the
plan directories only; `tv-app/` and `backend/` do not exist. The Phase 1 plan
defers their creation to Phase 2 (technical plan §Deferred to the spec track
or Phase 2: "Added when Phase 2 creates `tv-app/` and `backend/`"). The parent
Systems Modeler receipt likewise records no source tree at `2c13a6b`
(`specialists/systems-modeler-receipt.md` §Contextual pass). Every placement
below is planned, not anchored in existing product code.

## 2. Candidate element placements

Paths are repo-relative and planned. Each row cites its grounding source.

### 2.1 TV app (`tv-app/`, Kotlin, Jetpack Compose, Fire OS)

Basis: SD-003 (2018 Fire OS stick, starter `AmazonAppDev/hello-world-fire-tv`,
minSdk 25). Starter layout verified via `gh api` (`app/` Gradle module,
`build.gradle.kts`, `app/src/main/java/com/...` source root).

| Element | Planned path | Grounding |
|---|---|---|
| App shell and navigation | `tv-app/app/src/main/java/<pkg>/MainActivity.kt` | Starter `MainActivity`/NavHost pattern; #1 §Selected concept (Fire TV companion) |
| Build configuration (minSdk 25) | `tv-app/app/build.gradle.kts` | SD-003 (minSdk 25 assumption); starter at 21 must be raised |
| Manifest (permissions, services, package visibility) | `tv-app/app/src/main/AndroidManifest.xml` | SD-003; #1 item 1 app detection, item 3 notifications |
| Profile and settings UI (items 1, 6) | `tv-app/app/src/main/java/<pkg>/profile/ProfileSettingsScreen.kt` | #1 item 1 (configure profile), item 6 (customer controls) |
| Installed-app detector | `tv-app/app/src/main/java/<pkg>/detect/AppDetector.kt` | #1 item 1 (detect supported installed viewing apps; installed is not subscribed) |
| Alert foreground service | `tv-app/app/src/main/java/<pkg>/alerts/AlertService.kt` | #1 item 2 (enabled viewing periods), item 3 (alerts) |
| Alert notifier (heads-up, Watch/Dismiss) | `tv-app/app/src/main/java/<pkg>/alerts/AlertNotifier.kt` | #1 item 3; #1 §Source review (Fire OS notifications); SD-001 (real-device proof) |
| Watch launcher (provider intent/deep link) | `tv-app/app/src/main/java/<pkg>/watch/WatchLauncher.kt` | #1 item 4; #1 §App launch and game/channel routing research |
| Right-side lineup panel | `tv-app/app/src/main/java/<pkg>/panel/LineupPanel.kt` | #1 §Right-side fantasy lineup panel; SD-006 (Mode A/B) |
| Companion player (Mode A only) | `tv-app/app/src/main/java/<pkg>/player/CompanionPlayer.kt` | SD-006 (Mode A fallback), SD-006a (CC-BY/CC0 labeled footage) |

### 2.2 Backend (`backend/`, AWS serverless)

Basis: SD-005 (AWS serverless, new Free-plan account); C4 (Free to Paid only by
owner decision).

| Element | Planned path | Grounding |
|---|---|---|
| Infrastructure as code (SAM) | `backend/template.yaml` | SD-005; C4 (Free-tier services: Lambda, HTTP API, DynamoDB on-demand, Scheduler, SSM) |
| Device-code auth and `/v1/link` | `backend/src/device_auth/` | #1 item 6 (device-code linking sufficient) |
| REST API (`/v1/link`, `/v1/profile`, `/v1/alerts`, `/v1/panel`, `/v1/providers`) | `backend/src/api/` | #1 items 1, 3, 4, 6 and §Right-side panel; #1 §Source review (proposed data flow) |
| ESPN feed ingest | `backend/src/feed_ingest/` | SD-004 (ESPN unofficial JSON); #1 item 2 (monitor games) |
| Labeled replay source and fixtures | `backend/src/feed_ingest/replay.py`, `backend/fixtures/replay/` | C2 (ESPN down/change → labeled replay); #1 §Judging alignment (label replays) |
| Lineup connector (Yahoo OAuth read-only + manual fallback) | `backend/src/lineup/` | SD-007 (Yahoo read-only, manual entry from ESPN rosters at T_yahoo); C6; #1 item 1 |
| Player/event identity matcher | `backend/src/matcher/` | #1 item 3 (match identifiers across providers; duplicates, corrections) |
| Alert policy engine | `backend/src/alert_policy/` | #1 item 3 (filtering), item 6 (frequency, quiet hours, spoiler delay); #1 item 2 (schedule/game-day mode) |
| Provider resolver and registry | `backend/src/provider_resolver/` | #1 item 4 (resolve event to provider/channel; unknown stays unknown); one real provider contract from Phase 2 spike |
| Panel service (points, freshness) | `backend/src/panel/` | #1 §Right-side panel (league scoring context, stale/unavailable marks) |
| Yahoo client secret | SSM SecureString parameter declared in `backend/template.yaml` | SD-007; server-side secrets only (never in APK or repo) |

### 2.3 Data stores (backend-owned)

| Store | Planned placement | Grounding |
|---|---|---|
| Profile/settings/device-link store | DynamoDB tables in `backend/template.yaml` | #1 items 1, 6; SD-005 |
| Event cache and dedup/correction log | DynamoDB tables in `backend/template.yaml` | #1 item 3 (duplicates, scoring corrections) |
| Secrets (Yahoo tokens, client secret) | SSM SecureString | SD-007; C9 (credentials are owner-handled) |
| Replay fixtures | `backend/fixtures/replay/` | C2 |

### 2.4 External systems (not in repo; interface endpoints ST-3b must model)

| External system | Role | Grounding |
|---|---|---|
| ESPN unofficial public JSON | Live NFL game events (scores, field position, possession, corrections) | SD-004; C2; C3 (terms flagged at submission); #1 §Source review (feed requirements) |
| Yahoo Fantasy API (OAuth 2.0 read-only) | Lineup/league context: teams, rosters by week, scoring settings | SD-007; C6; #1 §Source review (Yahoo rows, endpoint candidates) |
| Manual lineup entry (customer via ESPN rosters) | Fallback lineup source at T_yahoo | SD-007; C6 |
| Installed provider apps | Viewing destinations reached by supported intent/deep link | #1 item 4; #1 §App launch research (Vega deep links, launcher integration, DIRECTV voice example) |
| Fire OS notification service | Heads-up notification delivery over third-party playback | #1 §Source review (Fire OS notifications row); SD-001; SD-003 |
| Alexa voice route (Video Skills / tuning) | Optional voice announcements and Alexa-assisted tuning | #1 item 4; #1 §Source review (Alexa row); SD-008; C8 (shown only if implemented and verified) |
| Device-link consumer (customer phone/browser) | Completes device-code linking | #1 item 6 |

## 3. Interfaces to model (ST-3b scope)

- TV app ↔ backend REST API (link, profile, alerts long-poll, panel, providers).
- Backend ↔ ESPN unofficial JSON (poll during game windows; validation at ingest;
  replay substitution per C2).
- Backend ↔ Yahoo Fantasy API (read-only OAuth; token refresh; manual-source
  switchover per C6).
- TV app → provider apps (supported launch URI/intent; outcomes: game opened,
  search/details opened, app home opened, app absent, access unknown, playback
  denied — #1 §App launch research).
- TV app → Fire OS notification service (heads-up delivery during third-party
  playback; unverified until Phase 2 spike).
- TV app ↔ Alexa route, conditional on C8 (voice announcements, assisted tuning).
- Backend → device-link page (device-code flow with the customer).
- Backend-internal: ingest → matcher → policy → alert/panel delivery; scoring
  corrections and duplicate suppression propagation to panel and alerts (#1 item 3,
  §Right-side panel consistency rule).
- Data interfaces: GameEvent, alert, lineup, panel state, settings (technical
  plan ST-3 row (b)).

## 4. Constraints binding placement

| ID | Constraint | Placement impact |
|---|---|---|
| C1 | Stick is Fire OS 5, older model, or cannot run provider apps → return to owner | minSdk 25 provisional (SD-003); no purchase or switch by agents |
| C2 | ESPN endpoint changes or goes down → labeled replay | `replay.py` + `backend/fixtures/replay/` placements |
| C3 | ESPN terms for public submission → flagged at submission | Terms check is an owner action; ingest stays swappable |
| C4 | AWS Free → Paid only by owner decision | Free-tier services only in `backend/template.yaml` |
| C5 | Panel spike fails or exceeds 24 h → Mode A, limitation stated | `CompanionPlayer` placement exists only under Mode A |
| C6 | No Yahoo approval by T_yahoo (2026-10-16T19:00:00Z) → labeled manual entry | `ManualSource` inside `backend/src/lineup/` |
| C7 | Any committed local absolute path → blocked | All paths repo-relative; no user-home-absolute literals in files (SD-010) |
| C8 | Alexa voice shown only if implemented and verified | Alexa interface modeled as conditional |
| C9 | Visibility flip, license, reviewer access, submission, external feedback → owner actions only | No agent-held credentials; secret values set by owner |
| LW | Lightweight device design, no hardware benchmarks (#1 §Lightweight device design) | Aggregation, monitoring, matching, AI commentary on backend; small TV updates; coalesced row updates; bounded queues/caches; off-main-thread I/O; 100 MB background-RAM design reference (not a measured claim); no benchmark gate |

Also carried: impl_agent_cap 5 (SD scope batch; binds Phase 2 lanes, not ST-3b);
single-stick / single-account serialization (parent receipt §Constraints);
T_deadline 2026-10-23T19:00:00Z and T_judge_access 2026-11-20 (scope batch
quantities; bind schedule, not placement).

## 5. Modeling mode decision for ST-3b

**`sysml-v2`.** Reason: the approved Phase 1 plan mandates it — ST-3 is
"SysML v2 models in `sysml-v2` mode" covering (a) this pass, (b) structure
(parts, ports), interface (TV app ↔ backend API, backend ↔ ESPN, backend ↔
Yahoo, TV app ↔ provider app launch), state (alert lifecycle, panel modes A/B,
device link) and data (GameEvent, alert, lineup, panel state, settings) models
with view metadata, and (c) mapping finalization after the register PASSes.
The `diagram-assisted` product views V1..V3 are demoted to reference input, and
the deferred f885e48 product design rows are non-binding input to re-derive
(technical plan §Deferred table). Per the systems-modeler skill and the SysML
Modeling skill, Mermaid must not silently substitute for mandated SysML
(`STOP_SILENT_DEGRADATION`); ST-3b must record model revision/digest and
native-or-derived view status. ST-3b entry check: the sysml-modeling skill's
required local references (standards receipts, method, validation, examples,
quality gate) must exist and be readable, else return `TYPED_GAP` and stop.

## 6. Open questions for the owner (listed, not asked)

1. Stick located and exact model/OS confirmed? (C1 trigger; SD-003; milestone 1
   entry criterion.)
2. Yahoo application submitted and approval status? (C6/T_yahoo fallback timing.)
3. AWS Free-plan account created? (SD-005; backend placements assume it.)
4. Mode A footage storage location if the panel spike selects Mode A? (Carried
   open item F12 from the parent receipt.)
5. Which real provider supplies the first supported game/channel link contract
   in the Phase 2 spike? (Determines the first registry entry; the resolver
   placement stands regardless.)
6. License choice before the repo visibility flip? (Deferred per scope batch;
   affects publication, not placement.)
