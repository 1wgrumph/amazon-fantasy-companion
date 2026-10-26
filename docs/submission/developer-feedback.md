# Developer feedback — AZ Fantasy

Prepared from the project running log and the project owner's live-night report,
2026-10-22, with the owner's submission update on 2026-10-23. Primary track:
**Fire TV** (Fire OS 8 / Android 11). Mini challenge:
**AWS Builder**. Vega OS was also exercised on the Vega Virtual Device (VVD);
that evidence does not establish physical Vega hardware or provider playback.
The Open Source mini challenge is not selected in the supplied feedback record.

These are developer observations and requests, not confirmed vendor defects.
Earlier experiments are dated where later work changed the outcome. No live
Yahoo data is included. Build-again answers are our assessment of the recorded
experience; no onboarding duration is inferred from a deployment or test pass.

## Product Feedback

### PF-01 — Amazon Fire TV / Fire OS 8

- **What we used it for:** the primary TV companion, remote navigation, lineup and alert presentation, installed-provider detection, and playback-overlay experiments on a Fire TV Stick 4K, AFTKM, Fire OS 8 / Android 11.
- **What worked well:** the starter installed and launched; D-pad navigation and UI hierarchy dumps supported device checks. Later on-stick work demonstrated the compact corner card, held-Menu control, and automatic close behavior.
- **What needs work:** the October 16 notification experiment posted alerts without an actionable heads-up banner. Windowing experiments did not place a panel beside uncropped video. Later overlays cover part of the picture rather than resize it. On October 22, third-party accessibility services were hidden from Settings, overlay permission needed `appops`, and injected remote events could not exercise the accessibility key filter.
- **Onboarding from zero to hello world:** build the starter, connect with adb, accept the on-TV authorization prompt, install, and launch. The recorded spike spans October 14–16, including waiting for the device and its authorization; active setup time was not recorded.
- **Would we build again? Yes.** The real-device companion and remote controls are useful, but permission setup needs a documented developer path.
- **AWS services used and how:** the device calls the Lambda-backed API Gateway HTTP API for linking, settings, alerts, and panel data; service details follow below.

<!-- Evidence: observations OBS-001, OBS-003..013; CHANGELOG PRs #157, #162, #163, #164; owner live-night report 2026-10-22 items 2, 3, 6. -->

### PF-02 — Android SDK, adb, Kotlin / Gradle toolchain

- **What we used it for:** building, signing, installing, launching, testing, and diagnosing the Fire OS app and device spikes.
- **What worked well:** adb installation and activity launch worked; `uiautomator dump`, D-pad input, and logcat provided useful checks. Android build tools also supported an offline APK recipe.
- **What needs work:** the starter dependency closure required upgrades and dependency verification. Host tests encountered APIs missing from `android.jar`; Kotlin tests needed Unit-returning bodies for JUnit 4. The early instrumented-runner dependency block was later resolved, so it is historical rather than a current inability to test. adb-injected key events still do not prove physical-remote accessibility gestures.
- **Onboarding from zero to hello world:** the starter built and installed during the Fire TV spike. SDK/JDK discovery initially needed explicit environment variables; the repository later added automatic discovery. Separate active setup time was not recorded.
- **Would we build again? Yes.** Signed APKs, host tests, and instrumented tests were achievable; physical-remote checks remain necessary for gesture behavior.
- **AWS services used and how:** none in the build tools themselves.

<!-- Evidence: observations OBS-013, OBS-020..029; scribe-2026-10-14-catchup O4/O5; CHANGELOG PRs #78, #134; owner live-night report 2026-10-22 item 3. -->

### PF-03 — AWS SAM, AWS CLI, and CloudFormation

- **What we used it for:** describing, validating, building, and deploying the serverless backend. CloudFormation manages the resources declared through SAM.
- **What worked well:** `sam validate --lint` and `sam build` ran offline, hash-pinned dependencies were honored, and recorded deployments reached `UPDATE_COMPLETE` with deployed smoke checks.
- **What needs work:** a profile under global SAM parameters made builds depend on a local profile. An interactive deploy under a timeout wrapper stopped at confirmation; that was an invocation problem. The October 16 AWS login flow returned HTTP 400 on the active-session option, concurrent logins interfered, and a session expired during a deploy.
- **Onboarding from zero to hello world:** establish an AWS CLI session, configure deployment parameters, build, and deploy the template. The log records configuration and login workarounds, but no standalone hello-world time.
- **Would we build again? Yes.** One template kept the backend resources together; login and portable build configuration needed extra care.
- **AWS services used and how:** SAM/CloudFormation provision Lambda, an API Gateway HTTP API, DynamoDB tables, EventBridge schedules, CloudWatch log groups, and IAM roles/grants. SSM parameter references support the Yahoo integration setup. IAM permissions are checked against the template; Moto unit tests alone do not enforce IAM.

<!-- Evidence: observations OBS-044, OBS-060..067; scribe-2026-10-14-catchup O9; CHANGELOG deploy entries and PRs #87, #138. -->

### PF-04 — AWS Lambda

- **What we used it for:** API handling, ESPN ingestion, and the event-matching/alert-policy pipeline. NBA ingestion was later separated from NFL ingestion.
- **What worked well:** recorded stack deployments and API smoke checks exercised the hosted backend. Separate NBA ingestion prevents an NBA feed failure from discarding or delaying the NFL poll.
- **What needs work:** production permission coverage cannot be inferred from mocked unit tests; the project had to pair operations with template grant checks. No isolated Lambda performance problem or latency measurement is recorded.
- **Onboarding from zero to hello world:** functions were packaged and deployed through SAM as part of the backend foundation; no separate Lambda-only onboarding time was recorded.
- **Would we build again? Yes.** Functions fit the API and ingest/policy stages used here.
- **AWS services used and how:** API Gateway invokes the API handler; EventBridge Scheduler invokes ingestion; functions read/write DynamoDB, use scoped IAM permissions, and have CloudWatch log groups. SSM parameters support the Yahoo setup without embedding credentials in code.

<!-- Evidence: observations OBS-044, OBS-051, OBS-065, OBS-067; CHANGELOG backend foundation, PRs #87, #138. -->

### PF-05 — Amazon API Gateway HTTP API

- **What we used it for:** the TV and phone-link API, profile/settings, alerts, provider routing, lineup panels, and later manual-lineup writes.
- **What worked well:** the deployed HTTP API answered the recorded smoke checks. A manual-lineup endpoint later made lineup setup possible without relying on Yahoo data.
- **What needs work:** the project initially left panel and alert wire shapes too loose; explicit schemas and shared fixtures were needed. This was our contract work, not evidence of an API Gateway defect. No service-specific onboarding or performance issue was recorded.
- **Onboarding from zero to hello world:** created with the Lambda integration in SAM; no separate HTTP API setup duration was recorded.
- **Would we build again? Yes.** It provides the shared HTTP boundary for both TV clients and the phone link flow.
- **AWS services used and how:** API Gateway routes HTTP requests to Lambda; the backend uses DynamoDB for persisted state. The template declares request throttling.

<!-- Evidence: observations OBS-030, OBS-065; CHANGELOG backend foundation, PRs #101, #105, #147. -->

### PF-06 — Amazon DynamoDB

- **What we used it for:** profiles, device links, events, alerts, lineups, panels, and player statistics.
- **What worked well:** tables were deployed with the backend; stored boxscore statistics later supplied real panel values. Offline pytest/Moto suites supported quick iterations with fresh in-process tables.
- **What needs work:** mocks did not catch missing IAM grants. Test seeds needed `Decimal` rather than float. Neither observation establishes a DynamoDB service defect.
- **Onboarding from zero to hello world:** tables were declared through SAM; local fixtures used Moto before deployed checks. No separate table-setup duration was recorded.
- **Would we build again? Yes.** The same store supports device state and the event-to-alert/panel pipeline.
- **AWS services used and how:** Lambda reads/writes DynamoDB under table-scoped IAM grants; the template uses on-demand tables.

<!-- Evidence: observations OBS-040, OBS-043, OBS-044, OBS-065; CHANGELOG PRs #87, #95. -->

### PF-07 — Amazon EventBridge Scheduler

- **What we used it for:** scheduled backend polling of ESPN feeds, with separate NFL and NBA ingestion functions in the later backend.
- **What worked well:** the schedule-to-Lambda arrangement is expressed in the SAM template. A standalone reliability measurement is not recorded.
- **What needs work:** the October 22 live-night report identifies the one-minute minimum as a limit on polling frequency; this is unsuitable for a tighter polling interval without another mechanism. William separately estimated about 70–90 seconds from a play to its alert during the live run. That end-to-end observation does not isolate EventBridge Scheduler or Lambda latency.
- **Onboarding from zero to hello world:** schedules and invocation roles were configured in the backend template; independent setup time was not recorded.
- **Would we build again? Yes.** It fits minute-scale polling; a faster cadence would require a different design.
- **AWS services used and how:** EventBridge Scheduler invokes the Lambda ingest functions using an invocation role; ingestion persists events/statistics in DynamoDB.

<!-- Evidence: product-feedback AWS section; CHANGELOG PR #138; owner live-night report 2026-10-22 item 5. -->

### PF-08 — AWS Systems Manager Parameter Store

- **What we used it for:** storing Yahoo integration configuration and credentials; secrets and refresh tokens used SecureString parameters. No values are included here.
- **What worked well:** the setup log records parameter storage and an updated token version across setup attempts.
- **What needs work:** no Parameter Store-specific failure or performance issue was recorded. Storage of credentials does not establish successful Yahoo data access.
- **Onboarding from zero to hello world:** parameter setup formed part of the documented AWS/Yahoo configuration workflow; its separate duration was not recorded.
- **Would we build again? Yes.** It kept integration secrets outside the source tree.
- **AWS services used and how:** SSM Parameter Store holds integration configuration; IAM limits backend access. The changelog records removal of unused Yahoo SSM read access from the public API function.

<!-- Evidence: observations OBS-067; product-feedback AWS section; CHANGELOG PR #68. -->

### PF-09 — Vega OS, Kepler SDK, and Vega Virtual Device

- **What we used it for:** a compatibility client and virtual-device checks. Recorded versions: Kepler SDK 0.24.12112 and Vega CLI 1.4.5; supported-host work used Ubuntu 24.04.4.
- **What worked well:** after the earlier black-display attempt, a supported-host run rendered the guest using llvmpipe. Later records show linked settings, session persistence with the supported storage package, live NBA panel updates, and two NBA alert banners with a Watch outcome of `accessUnknown`.
- **What needs work:** CLI success/readiness messages did not always mean the guest was usable. Graphics setup, screenshots, proxy networking, developer logs, and storage-package guidance needed workarounds. Some failures were host or app integration problems. Virtual-device success does not establish physical-device playback or entitlement.
- **Onboarding from zero to hello world:** the first attempt reached a shell with a black display and was paused; later supported-host work reached a painted guest and app. No single elapsed hello-world time was recorded.
- **Would we build again? Yes.** The later virtual-device runs supported useful compatibility checks, with a substantial setup cost and a physical-device evidence gap.
- **AWS services used and how:** the client uses the same API Gateway/Lambda backend and DynamoDB-backed state; no separate Vega cloud backend was needed.

<!-- Evidence: observations OBS-110..113; friction-log F-025, F-037..058; CHANGELOG PRs #118, #152, #158, #165. -->

### PF-10 — ESPN public JSON feeds

- **What we used it for:** NFL schedules, game state, scoring plays and broadcasts, plus later NBA boxscore/statistics ingestion.
- **What worked well:** scoreboard and summary endpoints returned HTTP 200 without authentication for 14 sampled completed NFL games. Later panel evidence shows live NBA rows and refreshes.
- **What needs work:** these are unofficial endpoints without a published contract. Historical payloads had reference-only participants, missing timestamps, and post-game edits. On October 22 the live NFL summary omitted play participants, leaving scoring plays without player IDs; parsing `D.Swift` from play text was the workaround. This is not proof of a generally reliable identity contract. Public-use terms remain an unresolved item in the supplied observations.
- **Onboarding from zero to hello world:** two GET endpoints and a standard-library capture tool were exercised in an eight-minute historical-feed spike; that window is not a live-latency measurement.
- **Would we build again? Yes.** The data was useful for this prototype behind validation and replay fixtures, with explicit schema and usage-term caveats.
- **AWS services used and how:** scheduled Lambda ingestion normalizes feed data into DynamoDB; the backend supplies panel and alert responses.

<!-- Evidence: observations OBS-070..074; CHANGELOG PRs #138, #155, #159; owner live-night report 2026-10-22 item 1. -->

### PF-11 — Yahoo Fantasy Sports API registration and approval workflow

- **What we used it for:** registering the application and navigating access approval for a proposed lineup integration. This feedback does not claim a working live Yahoo import or include live Yahoo data.
- **What worked well:** the earlier setup record shows successful OAuth refresh responses. That success was distinguishable from authorization to use the Fantasy API.
- **What needs work:** earlier unapproved-app reads returned HTTP 403 despite OAuth success. HTTPS redirect and description constraints were discovered through rejected console inputs. The owner reports that approval did not arrive before the submission deadline; the product ships manual lineups. A verified end-to-end Yahoo data-access result is not established.
- **Onboarding from zero to hello world:** app registration, OAuth setup, and approval work occupied an approximately 1.5-hour spike on October 16, largely console setup and diagnosis. That attempt did not reach a Fantasy data hello world.
- **Would we build again? No, for a deadline-critical dependency without verified access first.** We would revisit after onboarding and data authorization are proven; manual lineups provide the current alternative.
- **AWS services used and how:** SSM Parameter Store supports the integration configuration. No credential or Yahoo payload is reproduced here.

<!-- Evidence: observations OBS-080..082; product-feedback Yahoo section; CHANGELOG PRs #145, #147; owner submission update, October 23, 2026. -->

### PF-12 — Prime Video playback surface

- **What we used it for:** playback alongside companion presentation experiments and provider handoff/deep-link investigation on Fire OS.
- **What worked well:** the recorded route opened Prime Video search, and on-demand playback started. A title-detail investigation reached a title page.
- **What needs work:** search parameters were ignored, and no recorded event-to-title mapping established direct opening of the intended live game. Prime Video did not offer PiP in the tested windowing experiment. Some playback frames are protected from screenshots; this is a DRM capture boundary, not an app-rendering failure.
- **Onboarding from zero to hello world:** an approximately ten-minute desk probe exercised intents and links on October 16; separate playback setup time was not recorded.
- **Would we build again? Yes.** It is a useful playback/handoff surface, provided search arrival, game arrival, and entitlement remain distinct claims.
- **AWS services used and how:** the backend provider resolver supplies verified routes; no Prime Video service API integration is claimed.

<!-- Evidence: observations OBS-006..010; friction-log F-003/F-005; CHANGELOG PR #110; owner live-night report 2026-10-22 item 4. -->

### PF-13 — YouTube TV playback surface

- **What we used it for:** a playback/provider-handoff surface for the companion on Fire OS.
- **What worked well:** later device work established a verified Fire OS Watch route to app home, superseding the earlier observation that YouTube TV was absent from the stick.
- **What needs work:** an app-home route does not prove direct arrival at the intended game or viewer entitlement. No additional YouTube TV-specific SDK, playback-performance, or onboarding observation was supplied.
- **Onboarding from zero to hello world:** the running log progresses from app absent to a verified route; installation steps and elapsed setup time were not recorded in the supplied feedback.
- **Would we build again? Yes.** A verified provider launch is useful, while exact-game routing remains a separate requirement.
- **AWS services used and how:** backend provider resolution supplies the Watch route; no YouTube TV service API integration is claimed.

<!-- Evidence: observations OBS-010; CHANGELOG PR #148; owner tool inventory 2026-10-22. -->

## Feature Requests

Priorities reflect the impact on this project. Requests propose behavior; they
are not claims that a vendor currently offers it.

| ID / tool | Description | Why it matters to this project | Priority |
|---|---|---|---|
| FR-01 / Fire TV | Provide a supported actionable alert over provider playback, or document the intended alternative when standard notifications do not peek. | The high-importance notification experiment did not expose Watch/Dismiss actions over playback. | Critical |
| FR-02 / Fire TV | Provide a supported companion panel beside video without cropping or overlap. | Our overlay covers part of the picture; the earlier full-screen fallback interrupts viewing. | Important |
| FR-03 / Fire TV | Expose a supported user setup path for third-party accessibility services, with Fire OS-specific developer instructions. | Held-Menu controls currently need adb enablement on the tested device. | Important |
| FR-04 / Fire TV | Provide a visible overlay-permission grant path or document the required developer `appops` flow. | `SYSTEM_ALERT_WINDOW` has no usable permission UI in the live-night report. | Important |
| FR-05 / Android SDK / Fire TV | Provide or document supported test input that reaches an accessibility key filter with hold and double-tap semantics. | Injected adb keys cannot automate our physical-remote gesture checks. | Important |
| FR-06 / Prime Video and provider apps | Publish live-sports deep-link contracts and event-to-title/channel mappings. | Search or app home does not establish opening the requested game. | Important |
| FR-07 / Fire TV / Prime Video | Document screenshot restrictions and supported playback/layout evidence methods that respect protected video. | Some DRM frames capture black, complicating verification. | Nice-to-have |
| FR-08 / EventBridge Scheduler | Offer a supported sub-minute trigger option or guidance for a faster ingest cadence. | A one-minute minimum constrains live polling frequency. | Important |
| FR-09 / ESPN | Include stable participant/player IDs on live scoring plays and document the public JSON contract and correction timestamps. | Text parsing of `D.Swift` substitutes for missing IDs and cannot provide a general identity guarantee. | Important |
| FR-10 / Yahoo | Publish approval criteria, expected turnaround, API authorization state, and app-form constraints before registration. | Successful OAuth did not establish Fantasy access, delaying the planned lineup source. | Important |
| FR-11 / AWS CLI / SAM | Clarify login/session behavior and document portable SAM profile placement and interactive deployment requirements. | Login errors, expiry, and local configuration caused repeat setup/deployment work. | Important |
| FR-12 / AWS testing guidance | Document a supported way to verify IAM grants alongside offline DynamoDB tests. | Moto does not enforce IAM, so unit success missed required production grants. | Nice-to-have |
| FR-13 / Android tooling | Publish dependency reports per resolved configuration and clearer host-test API/runner dependency guidance. | Compiler/lint graphs and host API differences increased setup work. | Nice-to-have |
| FR-14 / Fire TV testing | Document D-pad automation, keyboard focus, and disabled-package test procedures. | Touch taps and shell package-state changes were unreliable or unavailable in our checks. | Nice-to-have |
| FR-15 / Vega | Reconcile host-version/screenshot documentation and publish supported storage and test setup examples. | Earlier documentation conflicts and a legacy storage binding slowed the port. | Important |
| FR-16 / Vega VVD | Align start/ready/stop results with usable guest and input states; diagnose graphics prerequisites and offer explicit software-renderer selection. | Exit 0 and a ready message could precede an unusable guest, while shutdown could still crash. | Important |
| FR-17 / Vega VVD | Provide reliable screenshots, release-app logs, and a documented developer log command. | Empty screenshots and absent release console output made failures harder to diagnose. | Important |
| FR-18 / Vega VVD | Support a proxy option that preserves destination host names and document guest diagnostic-tool availability. | A host-name allowlist required a custom network workaround before online linking worked. | Important |
| FR-19 / Vega | Honor telemetry opt-out before spawning helpers and document crash-reporter destinations and non-fatal boot diagnostics. | The sandbox run saw helper launches despite opt-out and unexpected diagnostic traffic configuration. | Nice-to-have |
| FR-20 / Vega VVD | Document supported app-private test-state inspection/seeding while preserving app isolation. | The developer shell could not seed a linked session; tests had to use the real link flow. | Nice-to-have |

<!-- Evidence: feature-requests FR-005..013, FR-021/022; friction-log F-013/014, F-037..058; owner live-night report 2026-10-22 items 1..6. -->

## Friction Log

Severity uses **Major** for a blocked feature or substantial workaround and
**Minor** for a recoverable diagnostic or setup problem. Ratings describe project
impact, not vendor-defect status. Dates and source labels distinguish recorded
experiments from the owner's October 22 live-night report. Where the report did
not provide a workaround or command sequence, that absence is explicit.

### FL-01 — Fire OS notifications did not expose alert actions

- **Task attempted:** Show a Watch/Dismiss alert over Prime Video playback.
- **Steps taken:** Posted a foreground-service notification on a high-importance channel; retried priority, sound/vibration, and a full-screen intent; inspected Notification Center.
- **Expected result:** A focusable heads-up banner with alert actions.
- **Actual result:** On October 16 the notification posted but never peeked; Notification Center showed only the service card.
- **Severity:** Major
- **Workaround used:** Used alerts inside the companion panel; a toast provided display-only awareness. Later custom overlay cards are recorded separately in the changelog.
- **Actionable suggestion:** Provide a supported actionable presentation API or document the intended Fire OS alternative.
- **Evidence:** Project device-spike log, October 16: OBS-003/004, source F-001; later overlay work: CHANGELOG PR #157.

### FL-02 — No tested composition placed a panel beside uncropped video

- **Task attempted:** Show lineup data beside playing Prime Video.
- **Steps taken:** Tried provider PiP through HOME, panel PiP, application overlay, split-screen, and freeform windowing.
- **Expected result:** Side-by-side video and panel without overlap.
- **Actual result:** The October 16 experiment stopped playback on HOME, overlaid the panel, or launched full-screen. Later overlays still cover part of the picture.
- **Severity:** Major
- **Workaround used:** Initially used the full-screen companion; later implemented an over-video corner card and expandable side panel, not video resizing.
- **Actionable suggestion:** Provide a documented companion composition mechanism or provider PiP support.
- **Evidence:** Project windowing spike, October 16: OBS-006, source F-002; CHANGELOG PRs #157/#162/#163.

### FL-03 — Provider links did not establish specific-game arrival

- **Task attempted:** Open the intended live game from Watch.
- **Steps taken:** Probed Prime Video home, search, and title-detail intents/links; checked other provider availability. Later verified a YouTube TV route.
- **Expected result:** A documented event-specific route.
- **Actual result:** Prime Video home/search/title pages were reachable, with search queries ignored. The later YouTube TV route opens app home; these results do not establish game arrival or entitlement.
- **Severity:** Major
- **Workaround used:** Registered proven routes and retained limited routing outcomes rather than reporting game arrival.
- **Actionable suggestion:** Publish live-event deep links and an event-to-provider identifier mapping.
- **Evidence:** Project provider spike, October 16: OBS-008..010, source F-003; CHANGELOG PRs #110/#148.

### FL-04 — One monkey launch failed

- **Task attempted:** Launch the starter on Fire OS.
- **Steps taken:** Repeated the starter launch during the device-spike repair check.
- **Expected result:** The activity resumes.
- **Actual result:** `adb shell monkey` exited 251 without resuming the activity; an activity-manager launch worked. No vendor root cause was established.
- **Severity:** Minor
- **Workaround used:** Used `am start` and checked activity state.
- **Actionable suggestion:** Document a reliable explicit activity-launch example for TV starters.
- **Evidence:** Project device-spike repair log: OBS-002, source F-004.

### FL-05 — Shell could not disable a provider package for a test

- **Task attempted:** Exercise installed-but-disabled detection.
- **Steps taken:** Tried `pm disable` on a provider package.
- **Expected result:** A disabled package state for the test.
- **Actual result:** Fire OS returned a SecurityException saying the shell cannot change component state.
- **Severity:** Minor
- **Workaround used:** Used an owned fixture package that self-disabled; restored and verified its state.
- **Actionable suggestion:** Document the supported disabled-package test procedure and shell restrictions.
- **Evidence:** Project detection spike, October 19: OBS-011, source F-006.

### FL-06 — TV input needed D-pad and keyboard-specific handling

- **Task attempted:** Drive link/profile screens during on-device checks.
- **Steps taken:** Tried touch/mouse taps, D-pad input, keyboard actions, and UI hierarchy dumps.
- **Expected result:** Controls activate and text editing returns to navigation predictably.
- **Actual result:** TV buttons required D-pad focus plus CENTER. In the earlier multiline form, keyboard Next did nothing while Previous exited. Some focus behavior was our app implementation.
- **Severity:** Minor
- **Workaround used:** Used D-pad navigation and hierarchy dumps; the later app fix added explicit field traversal and editing/IME behavior.
- **Actionable suggestion:** Document TV automation and keyboard behavior; keep app focus handling covered by real-remote checks.
- **Evidence:** Project device log: OBS-012/014, source F-007; CHANGELOG PRs #129/#132 record the app repair.

### FL-07 — Accessibility service hidden from Fire OS Settings

- **Task attempted:** Enable the third-party accessibility service for remote gestures.
- **Steps taken:** Attempted Settings-based enablement; the owner report records adb as the required route. Exact command sequence was not supplied.
- **Expected result:** A discoverable user-facing service switch.
- **Actual result:** Fire OS hid third-party accessibility services from Settings on the tested setup.
- **Severity:** Major
- **Workaround used:** Enabled through adb, as reported; no consumer-only setup path was demonstrated.
- **Actionable suggestion:** Provide a supported visible enablement path and Fire OS-specific setup documentation.
- **Evidence:** Project owner live-night report, October 22, item 2. This is the supplied observation; no separate command receipt was supplied.

### FL-08 — Injected adb keys did not reach the accessibility filter

- **Task attempted:** Automate held or double-tap remote gestures.
- **Steps taken:** Tried injected adb key events against an AccessibilityService key filter; exact invocations were not supplied.
- **Expected result:** Injected input exercises the same gesture path as the physical remote.
- **Actual result:** The injected events did not reach the filter, so they could not automate hold/double-tap behavior.
- **Severity:** Major
- **Workaround used:** No automation workaround was supplied. Earlier physical held-Menu evidence is recorded, but it does not demonstrate automation.
- **Actionable suggestion:** Document the injection boundary and offer a supported test input path for accessibility key filtering.
- **Evidence:** Project owner live-night report, October 22, item 3; CHANGELOG PR #163 records earlier on-stick held-Menu evidence.

### FL-09 — Prime Video protected frames could not be captured

- **Task attempted:** Capture playback/layout evidence.
- **Steps taken:** Used adb screenshots during the earlier playback sweeps; the owner reported the restriction again on October 22.
- **Expected result:** A capture useful for verifying the visible layout.
- **Actual result:** Some video frames were blocked by DRM or appeared as a black secure surface. This does not show that playback failed.
- **Severity:** Minor
- **Workaround used:** Earlier checks used media-session state and window geometry. Public demo work was restricted to companion UI rather than provider screens.
- **Actionable suggestion:** Document protected-frame limits and evidence methods that respect DRM; no protection bypass is requested.
- **Evidence:** Project playback spikes: OBS-007, source F-005; owner live-night report, October 22, item 4; CHANGELOG PRs #140/#141.

### FL-10 — Scheduler minimum constrained live polling frequency

- **Task attempted:** Poll backend sports data more frequently during live play.
- **Steps taken:** Used EventBridge Scheduler for polling; the owner reported its one-minute minimum. No sub-minute configuration attempt was supplied.
- **Expected result:** A polling cadence shorter than one minute for faster updates.
- **Actual result:** The one-minute minimum limited how frequently this scheduler could initiate polls. No measured end-to-end delay was supplied.
- **Severity:** Major
- **Workaround used:** No faster-cadence workaround was supplied; the recorded schedule uses a minute-scale interval.
- **Actionable suggestion:** Offer a supported sub-minute option or document an alternative for faster ingest.
- **Evidence:** Project owner live-night report, October 22, item 5; product-feedback AWS section records `rate(1 minute)`.

### FL-11 — Overlay permission had no usable Fire OS UI

- **Task attempted:** Grant `SYSTEM_ALERT_WINDOW` for companion overlays.
- **Steps taken:** Attempted the Fire OS permission setup; the owner report identifies `appops` as necessary. Exact command sequence was not supplied.
- **Expected result:** A visible permission-grant screen.
- **Actual result:** The tested Fire OS setup had no UI for this permission.
- **Severity:** Major
- **Workaround used:** Used `appops`, as reported. The earlier assumption of a usable Settings grant is not retained as a current result.
- **Actionable suggestion:** Expose a permission UI or document the supported Fire OS developer grant procedure.
- **Evidence:** Project owner live-night report, October 22, item 6; earlier overlay setup context: OBS-006.

### FL-12 — Live NFL scoring plays lacked participant IDs

- **Task attempted:** Match a live scoring play to a fantasy starter.
- **Steps taken:** Consumed the live NFL summary; the owner report records parsing `D.Swift` from play text after participant data was absent.
- **Expected result:** Scoring plays carry player IDs usable for matching.
- **Actual result:** The live summary omitted play participants, leaving scoring plays without player IDs.
- **Severity:** Major
- **Workaround used:** Parsed `D.Swift` from the play description. No general accuracy or ambiguity-resolution result was supplied.
- **Actionable suggestion:** Include stable participant IDs on live scoring plays and document when they may be absent.
- **Evidence:** Project owner live-night report, October 22, item 1. No raw live payload or separate command receipt was supplied.

### FL-13 — Historical ESPN payloads needed defensive normalization

- **Task attempted:** Normalize plays, broadcast networks, and corrections.
- **Steps taken:** Captured 14 completed NFL games and repeated a final-game capture.
- **Expected result:** Predictable broadcast/participant/timestamp shapes and usable correction times.
- **Actual result:** Broadcasts were nested under the competition, participants used references, a play lacked `wallclock`, and 89% of sampled plays had later edits. Minute-precision `modified` and changing final bodies could not establish live correction timing.
- **Severity:** Minor
- **Workaround used:** Validated ingestion before writes and retained labeled replay fixtures; later stored per-event broadcast information.
- **Actionable suggestion:** Publish the JSON contract and change notes, including stable identity and correction semantics.
- **Evidence:** Project historical-feed spike, October 14: OBS-070..074, source F-012; CHANGELOG PR #114. Public-use terms remain unresolved in OBS-074.

### FL-14 — OAuth success did not establish Yahoo Fantasy authorization

- **Task attempted:** Complete onboarding for the planned lineup source.
- **Steps taken:** The October 16 setup attempted refresh and read authorization with and without the read scope, then applied for access.
- **Expected result:** An approved read-only integration can access leagues and rosters.
- **Actual result:** The earlier refresh responses were HTTP 200 while Fantasy reads returned HTTP 403 for the unapproved app. Yahoo Fantasy API access approval did not arrive before the submission deadline, according to the owner's October 23 update. This feedback establishes neither live data access nor import success.
- **Severity:** Major
- **Workaround used:** Shipped manual lineups for the submission; a manual-lineup API lets the owner enter teams without waiting for Yahoo approval.
- **Actionable suggestion:** Show API authorization status separately from OAuth success and publish approval criteria and timing.
- **Evidence:** Project Yahoo setup spike, October 16: OBS-080/082, source F-008; CHANGELOG PR #147; owner submission update, October 23, 2026. No live Yahoo data is reproduced.

### FL-15 — Yahoo registration constraints appeared after rejection

- **Task attempted:** Register the application.
- **Steps taken:** Entered redirect/description settings and corrected rejected values.
- **Expected result:** The form explains its constraints before submission.
- **Actual result:** An out-of-band redirect was rejected in favor of HTTPS, and the description could not contain the provider name.
- **Severity:** Minor
- **Workaround used:** Used an HTTPS localhost redirect and reworded the description.
- **Actionable suggestion:** Display redirect and description requirements directly on the app-creation form.
- **Evidence:** Project registration log: OBS-081, source F-009; no app identifier or contact data included.

### FL-16 — AWS login flow and session expiry interrupted deployment

- **Task attempted:** Authenticate and deploy the backend.
- **Steps taken:** Tried the active-session sign-in option, concurrent logins, deployment, and local SDK use.
- **Expected result:** A working sign-in and a session usable for the deployment workflow.
- **Actual result:** The October 16 record shows HTTP 400 on the active-session option and interference from concurrent logins. A deployment also encountered session expiry; local boto3 could not use the login credentials. Time to expiry was not recorded.
- **Severity:** Minor
- **Workaround used:** Used Sign in to new session, one login at a time, renewed the session when needed, and used the AWS CLI for local calls.
- **Actionable suggestion:** Clarify session lifetime and SDK compatibility, and diagnose the active-session sign-in path.
- **Evidence:** Project AWS setup/deploy log: OBS-060..062, source F-010; scribe-2026-10-14-catchup O9.

### FL-17 — SAM build configuration and interactive invocation were not portable

- **Task attempted:** Build offline and deploy.
- **Steps taken:** Ran a build with a profile set globally; attempted an interactive deploy under a timeout wrapper.
- **Expected result:** Builds do not require deployment-only local settings, and deployment can receive confirmation input.
- **Actual result:** A missing local profile blocked the build; the timeout-wrapped deploy stopped at its prompt. No SAM product defect was reproduced.
- **Severity:** Minor
- **Workaround used:** Moved the profile to deploy parameters and retried the deployment in a foreground process group.
- **Actionable suggestion:** Document profile scoping and interaction requirements beside the configuration/deploy examples.
- **Evidence:** Project SAM log, CLI 1.169.0: OBS-063/064, source F-011.

### FL-18 — Mocked DynamoDB tests did not verify deployed IAM

- **Task attempted:** Ensure backend table operations had sufficient permissions.
- **Steps taken:** Ran offline tests with Moto and compared required operations with the deployment template.
- **Expected result:** Test evidence reveals missing production grants.
- **Actual result:** Moto did not enforce IAM; missing Scan/PutItem permissions were invisible to those unit tests. This is a testing boundary, not a DynamoDB defect.
- **Severity:** Major
- **Workaround used:** Paired template changes with exact-grant contract tests and corrected the table-scoped permissions.
- **Actionable suggestion:** Document IAM verification as a separate requirement from mocked service behavior.
- **Evidence:** Project backend test/deploy log: OBS-044, source F-015; CHANGELOG PR #87.

### FL-19 — Android dependency setup required extra qualification

- **Task attempted:** Prepare the starter build and instrumented-test toolchain.
- **Steps taken:** Scanned starter/runner/compiler dependency closures and examined resolved configurations.
- **Expected result:** A documented dependency set suitable for the build and test workflow.
- **Actual result:** The early scan was indeterminate and recorded advisory findings; merged reports hid configuration-specific versions. The instrumented-runner admission block was later resolved, rather than remaining an ongoing inability to test.
- **Severity:** Major
- **Workaround used:** Upgraded the build toolchain, used strict dependency verification and configuration-specific reports, and later admitted checksum-verified runner artifacts.
- **Actionable suggestion:** Publish clear resolved dependency inventories and patched toolchain guidance.
- **Evidence:** Project setup log: OBS-020..024, source F-013; scribe catch-up O4/O5; CHANGELOG PR #134 records the later runner resolution. Scanner observations are historical, not a fresh vulnerability assessment.

### FL-20 — Android host-test APIs differed from JVM expectations

- **Task attempted:** Compile host tests and collect JUnit cases.
- **Steps taken:** Used JSON/file APIs, an expression-bodied coroutine test, and a Gradle command without discovered SDK/JDK settings.
- **Expected result:** APIs compile and JUnit collects the intended tests.
- **Actual result:** Some APIs were absent from the Android host compile surface; a non-Unit expression produced a should-be-void collection error; missing SDK settings blocked the command. These were compatibility/setup problems.
- **Severity:** Minor
- **Workaround used:** Used available iteration/file APIs and Unit-typed test bodies; set SDK/JDK variables. The repository later added toolchain discovery.
- **Actionable suggestion:** Provide concise Android TV host-test API and JUnit examples with toolchain discovery guidance.
- **Evidence:** Project test log: OBS-025..028, source F-014; CHANGELOG PR #78.

### FL-21 — Vega documentation and version reporting were inconsistent

- **Task attempted:** Choose a supported host, screenshot path, and SDK version.
- **Steps taken:** Compared install/CI/screenshot documentation and read CLI version output when `vvman` was absent.
- **Expected result:** Consistent supported-host guidance and an unambiguous SDK version.
- **Actual result:** Pages differed on host/screenshot support; the fallback version command printed 0.200.0 while the Vega command identified SDK 0.24.12112.
- **Severity:** Minor
- **Workaround used:** Used the supported-host run and the SDK version reported by `vega --version`; later evidence supersedes the earlier paused black-display attempt.
- **Actionable suggestion:** Reconcile documentation and explain which version each command prints.
- **Evidence:** Project Vega log, October 20–21: OBS-110, source F-025/F-038; CHANGELOG PR #118.

### FL-22 — VVD boot depended on lock and graphics environment

- **Task attempted:** Boot a rendered virtual-device guest on the supported host.
- **Steps taken:** Started in a fresh process namespace with copied locks; tried default graphics and the no-GL-acceleration option.
- **Expected result:** A painted guest or a useful prerequisite error.
- **Actual result:** A copied lock PID could refer to another process. Missing Mesa drivers caused a default-mode SIGSEGV; the no-GL-acceleration run reported running but showed a black guest. These results depend on host configuration.
- **Severity:** Major
- **Workaround used:** Cleared stale emulator locks for that isolated run, kept default graphics flags, and supplied the recorded llvmpipe environment/driver closure. The guest painted without host DRM-node access. Non-fatal font/audio/Vulkan diagnostics remained.
- **Actionable suggestion:** Diagnose stale locks and graphics prerequisites, expose software-renderer selection, and document non-fatal diagnostics and hardware access requirements.
- **Evidence:** Project supported-host Vega log, October 20: source F-039..041/F-047/F-048; Kepler SDK 0.24.12112, Ubuntu 24.04.4.

### FL-23 — VVD success messages did not prove usable input or clean stop

- **Task attempted:** Automate virtual-device start, input, and shutdown.
- **Steps taken:** Started with a deadline, sent input during splash after the ready message, and later stopped a rendered session.
- **Expected result:** Failed starts return failure, ready means input is usable, and stop completes cleanly.
- **Actual result:** An unresponsive start exited 0. Splash-time input threw a trim error and dropped the device. Stop returned 0 and stopped status, but the process group still ended with SIGSEGV.
- **Severity:** Major
- **Workaround used:** Checked running status and a rendered frame, waited for the usable UI before input, and recorded shutdown signals separately from stopped status.
- **Actionable suggestion:** Align exit/readiness states with a usable guest and make early input and shutdown robust.
- **Evidence:** Project Vega lifecycle log, October 20: source F-037/F-042/F-044. The successful input attempt waited 12 seconds; this is one observed wait, not a universal readiness timeout.

### FL-24 — VVD screenshot tool produced an empty capture

- **Task attempted:** Capture the rendered guest UI.
- **Steps taken:** Used the SDK screenshooter and copy-from on a frame also visible through `xwd`.
- **Expected result:** A non-empty guest screenshot.
- **Actual result:** The screenshooter reported Incomplete and the copied file was empty, while `xwd` showed the UI.
- **Severity:** Minor
- **Workaround used:** Captured with `xwd`.
- **Actionable suggestion:** Make the SDK screenshooter capture the rendered guest or return an actionable error.
- **Evidence:** Project Vega capture log, October 20: source F-043.

### FL-25 — Vega helper launches did not match sandbox expectations

- **Task attempted:** Boot with telemetry opted out and a network allowlist.
- **Steps taken:** Observed the successful boot with opt-in false and a no-execute home mount.
- **Expected result:** Opt-out prevents telemetry helper launches and crash reporting respects the configured network boundary.
- **Actual result:** The telemetry helper was spawned 28 times but every exec was denied by the mount. A crash reporter was launched with an off-allowlist destination; no connection from that process was recorded. This does not establish data exfiltration.
- **Severity:** Minor
- **Workaround used:** The sandbox blocked helper execution and disallowed destinations; no CLI-level workaround was recorded.
- **Actionable suggestion:** Honor telemetry opt-out before spawning and document or configure crash-report destinations.
- **Evidence:** Project sandboxed Vega boot log, October 20: source F-045/F-046; no destination, account, or sandbox path reproduced.

### FL-26 — Vega developer logs lacked expected release-app output

- **Task attempted:** Inspect app/request behavior on the virtual device.
- **Steps taken:** Tried `journalctl`, then the developer logging command, during release-bundle runs.
- **Expected result:** An accessible app log with useful runtime messages.
- **Actual result:** The developer shell rejected `journalctl`; release logs omitted app console output and showed unformatted commit-time placeholders.
- **Severity:** Major
- **Workaround used:** Used `loggingctl log -v` for the package; screen captures and proxy connection logs supplemented missing app output.
- **Actionable suggestion:** Document the developer-mode log command and provide useful release-app output with formatted fields.
- **Evidence:** Project Vega logging log, October 21: source F-049/F-050.

### FL-27 — VVD tests lacked a supported app-state inspection path

- **Task attempted:** Start a linked-session test and inspect link/settings state.
- **Steps taken:** Probed app-private storage from the developer shell; read the online link/settings flow from captures.
- **Expected result:** A supported test-state mechanism while preserving app isolation.
- **Actual result:** The developer shell could not inspect or seed private storage. The app had no state dump, so link code and settings had to be read from screen captures. The missing app dump is our instrumentation gap.
- **Severity:** Major
- **Workaround used:** Used the real link flow and read captures; no private-storage bypass was used.
- **Actionable suggestion:** Document a supported virtual-device test-state interface; provide app-owned test observability without exposing real sessions.
- **Evidence:** Project Vega test-state log, October 21: source F-051/F-052. No link code or saved personal data included.

### FL-28 — VVD networking did not fit a host-name allowlist proxy

- **Task attempted:** Reach the deployed backend from the guest in the restricted test environment.
- **Steps taken:** Allowlisted the backend and tried the virtual-device networking/proxy path; attempted guest name/address diagnostics.
- **Expected result:** Guest traffic reaches the allowed backend through a host-name CONNECT.
- **Actual result:** The CLI exposed no suitable proxy/DNS option, the emulator proxy used numeric destinations, and guest name resolution failed in the sandbox. `getent` and `ip` were absent. This was specific to the restricted network setup.
- **Severity:** Major
- **Workaround used:** Used a namespace resolver limited to the backend and a forwarder that sent host-name CONNECT requests; TLS remained end to end.
- **Actionable suggestion:** Expose a proxy option preserving host names and document guest networking/diagnostic support.
- **Evidence:** Project restricted-network Vega log, October 21: source F-053/F-058. No host name, address, or proxy configuration value included.

### FL-29 — Our Vega settings screen required excessive remote navigation

- **Task attempted:** Change one setting and save.
- **Steps taken:** Navigated down from the top of Profile/Settings on VVD.
- **Expected result:** Visible initial focus and a readily reachable Save control.
- **Actual result:** Focus began on nothing, fields took focus silently, and Save was about 30 DOWN presses away. This was observed app UI behavior, not a demonstrated SDK defect.
- **Severity:** Minor
- **Workaround used:** Navigated to Save with the recorded repeated DOWN presses.
- **Actionable suggestion:** Improve our initial focus and field focus indicators, and keep Save readily reachable.
- **Evidence:** Project Vega app UI log, October 21: source F-054. No later resolution is established by this source.

### FL-30 — Legacy storage binding lost the Vega session on relaunch

- **Task attempted:** Keep the linked session after restarting the app.
- **Steps taken:** Linked, saved a setting, terminated, and relaunched; then repeated with the supported storage package.
- **Expected result:** Relaunch returns to the linked settings screen.
- **Actual result:** The legacy React Native AsyncStorage binding returned to Link. After using the supported package, relaunch retained the session. Native data-root messages remained, with their origin unresolved.
- **Severity:** Major
- **Workaround used:** Loaded the default export from the supported Amazon AsyncStorage package. An in-memory fake had not exposed the integration failure.
- **Actionable suggestion:** Document the supported storage binding and explain the remaining data-root diagnostics.
- **Evidence:** Project Vega persistence log, October 21: source F-055; CHANGELOG PR #118. This was an app integration repair, not a claim that supported storage still loses sessions.

### FL-31 — Our Vega panel discarded the server default selection

- **Task attempted:** Show a panel when no team or league was selected.
- **Steps taken:** Observed the device error, read the server response, and replayed it through the app decode/controller path.
- **Expected result:** The server default empty state is displayed.
- **Actual result:** The response decoded, but our controller dropped its identity and repeatedly requested the panel. The repair adopted the server identity; the VVD recheck showed the default state.
- **Severity:** Major
- **Workaround used:** Repaired the controller and checked the default state on VVD. Later review wiring changes in that record were not rerun on VVD.
- **Actionable suggestion:** Keep the empty-selection/server-default behavior in app regressions and distinguish controller failures from API/SDK failures.
- **Evidence:** Project Vega panel log, October 21: source F-056; CHANGELOG PR #118 records the repair.

### FL-32 — Our early virtual-device profile had no lineup write path

- **Task attempted:** Show alerts, Watch, and populated panel rows for a synthetic profile.
- **Steps taken:** Linked a synthetic profile and observed alerts/panel without a way to write its lineup through the public API.
- **Expected result:** A documented setup path supplies the test lineup.
- **Actual result:** In that earlier run no public API wrote a lineup, so no matching alert or populated rows appeared. This was our application prerequisite gap, not a VVD limitation.
- **Severity:** Major
- **Workaround used:** No product workaround existed in that run. A manual-lineup API was subsequently added; later VVD evidence shows populated NBA rows, alerts, and a limited Watch outcome.
- **Actionable suggestion:** Keep reproducible manual-lineup setup in the project workflow and do not count an unseeded test as platform failure.
- **Evidence:** Project Vega app log, October 21: source F-057; CHANGELOG PRs #147/#158/#165 supersede the earlier blocked state.

## Source notes

Observers: William is the observer named for the supplied October 22 live-night
report and October 23 submission update. Earlier entries are attributed to the
project test authors through the cited running-log records; where those records
do not name an individual observer or an exact date, this assembly does not
supply one. Vendor-directed suggestions are requests to the named tool provider;
requests about our app are assigned to the project developer.

The project running log is the evidence source for this assembly; these entries
are not new independent reproductions. Some original receipts were marked
unavailable or not durable in that log. The October 22 entries explicitly cite
the project owner's supplied report, without inventing missing commands,
payloads, elapsed times, or verification results.

- [Rules extract](../plans/2026-10-11-amazon-fantasy-companion/evidence/devpost-feedback-rules.md): required Product Feedback, Feature Requests, and Friction Log fields; up to 10% friction-log bonus.
- [Observations index](../developer-feedback/observations.md), [product feedback](../developer-feedback/product-feedback.md), [feature requests](../developer-feedback/feature-requests.md), and [friction log](../developer-feedback/friction-log.md): source IDs used above. Source F/FR IDs refer to the running log; FL/FR IDs in this file identify the assembled submission entries.
- [October 13 resume note](../developer-feedback/scribe-2026-10-13-g1-resume.md), [October 13 progress note](../developer-feedback/scribe-2026-10-13-g2-progress.md), and [October 14 catch-up](../developer-feedback/scribe-2026-10-14-catchup.md): earlier records reconciled through the observations index. Internal workflow/routing details are not exported into the product feedback.
- [Changelog](../../CHANGELOG.md): later resolutions and capabilities, including Android runner admission, manual lineup writes, YouTube TV routing, overlay/remote work, and the supported-host Vega checks.
