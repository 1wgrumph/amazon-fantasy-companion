# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Record v0.1.0 in the changelog ([PR #139](https://github.com/1wgrumph/amazon-fantasy-companion/pull/139)).
- Record the v0.1.0 merge commit in the release receipt ([PR #142](https://github.com/1wgrumph/amazon-fantasy-companion/pull/142)).

## [0.1.0] - 2026-10-20

### Fixed

- Admit the Unified Test Platform artifacts (201 files, each checksum-verified against its official repository and supply-chain scanned) into `tv-app/gradle/verification-metadata.xml` so `./gradlew -p tv-app :app:connectedDebugAndroidTest` passes on the Fire TV stick under STRICT dependency verification, replacing the `adb install` + `am instrument` workaround (BUG-38-UTP, evidence `BUG-38-UTP/`, [#134](https://github.com/1wgrumph/amazon-fantasy-companion/pull/134)).

### Added

- Friction log entries F-030 to F-036 for 2026-10-20: advisory device lease, commit-guard directory resolution, pkill self-match, pre-push gate duration, literal dispatch carriers, a false gate-pass self-report, and literal merge repository.
- P2-D03 closeout: README judge access is now this public repository plus the README setup (owner decision 2026-10-20, demo video still pending), and fresh-host evidence proves both hash-pinned installs download into new venvs with empty pip caches (42 and 23 downloads) ([#48](https://github.com/1wgrumph/amazon-fantasy-companion/issues/48)).
- P2-L05 dry-run evidence rehearsing the final-APK build and inspection on `fb6ab2f` (debug-signed release APK, sha256 and signer certificate recorded, manifest and permissions inspected, Reverify capability gap and empty-ApiUrl gap carried to the real run; nothing released) ([#53](https://github.com/1wgrumph/amazon-fantasy-companion/issues/53)).

- Device evidence for the A03–A05 steps that waited on an AWS session (alert card, Watch confirm and outcome, stale-labeled panel value), the P2-A02 D-pad focus recapture on the #129 fix, and the P2-D03 README fresh-setup walkthrough (14 PASS, 1 limited, 4 owner steps); README now uses `adb install -r` and records what the walkthrough did not prove ([PR #132](https://github.com/1wgrumph/amazon-fantasy-companion/pull/132)).
- Friction log entries F-026 to F-029 for 2026-10-20: OCR test-file exclusion, quota cascade across fallbacks, bug-route escape harness gap, CHANGELOG conflicts under parallel landing.
- Add the hackathon submission write-up (`docs/submission/writeup.md`): Fire TV and AWS Builder integrations from landed evidence (spike verdicts WORKS/FAILS/PARTIAL with limits, `afc-dev` deployed smoke only where recorded), the YouTube TV Fantasy View differentiation, the DEC-AFC-SD-036 future direction marked external context with public citations, an honest-limits section covering every FAILS/PARTIAL verdict plus the paused Vega stretch, and X09/X10, X03 PR 2, X05 PR 2, and X11 marked PENDING with no result asserted; the combined `PROC-SUBMISSION-CHECK` completes when D05 lands ([#49](https://github.com/1wgrumph/amazon-fantasy-companion/issues/49)).
- Correct the submission write-up in review repair: current YouTube TV Fantasy View platforms are ESPN or Yahoo, tune-in alerts are collected in the background and presented in the companion's full-screen panel (no reachable notification during provider playback), and the Prime Video deal starts with the NBA 2025–26 season and WNBA in 2026 ([#49](https://github.com/1wgrumph/amazon-fantasy-companion/issues/49), [PR #122](https://github.com/1wgrumph/amazon-fantasy-companion/pull/122)).

### Security

- Bound ESPN boxscore statistics ingest against denial-of-service inputs: validate numeric `athleteId` keys (`1..20` ASCII digits) before any DynamoDB write, cap boxscore athletes per payload (`MAX_BOXSCORE_ATHLETES = 200`) and stats per athlete (`MAX_ATHLETE_STATS = 64`) with deterministic truncation, reject oversize (`MAX_STAT_VALUE_LENGTH = 16`) and subnormal stat strings before `Decimal` conversion, and isolate single-record `PlayerStats` write failures so valid records, `GameEvent`s, and alerts keep ingesting. Review repair: cap play `id` and `wallclock` at 64 characters in the summary schema and treat a DynamoDB `ValidationException` on any feed write as a failure of that game only; skip only payload-rejected `PlayerStats` writes (`ValidationException`, `decimal` signals) so access, table, throttling and endpoint failures surface; aggregate hostile-input warnings into one length-bounded line per payload and batch; reject positive-exponent stat values such as `0E+999`; expose the bounds as plain module constants; and check recorded-fixture statistics against a frozen pre-fix snapshot ([PR #103](https://github.com/1wgrumph/amazon-fantasy-companion/pull/103)).
- Remove unused Yahoo SSM read access from the public API function and warn
  users to confirm only a code on their own TV; preserve code-only linking,
  short code expiry and one-time confirmation ([#68](https://github.com/1wgrumph/amazon-fantasy-companion/pull/68)).

### Changed

- Publish specification revision 0.4 (P2-D02): record landed SP-1 to SP-8 verdicts and close the provider, panel, notification and lineup contract constants; Fire OS primary with Vega paused stretch; pending live checks stay pending ([#46](https://github.com/1wgrumph/amazon-fantasy-companion/issues/46), [PR #124](https://github.com/1wgrumph/amazon-fantasy-companion/pull/124)).

### Added

- Fire TV device evidence for P2-A02 to P2-A05 (#31, #38, #39, #40): install, profile, alert instrumentation, Prime Video search route, full-screen fallback, focus and text-size measurements on the AFTKM stick. Partial: synthetic alert and lineup fixtures wait on an expired afc-dev AWS session; issues stay open.
- Prepare the P2-X10 hardening run (preparation unit, no live claim): scenario run book (corrections, starter changes, duplicate suppression, stale/unavailable, Sunday defect re-check), run-record template with `live_claim: false`, preparation-time preflight with typed pending rows, and the visual capture index under `evidence/e2e/2026-10-19/` and `evidence/visual/e2e-2026-10-19/`; every live scenario stays PENDING-LIVE for the post-P2-X09 window ([#44](https://github.com/1wgrumph/amazon-fantasy-companion/issues/44)).
- Repair the P2-X10 run book after independent review: bind PF-8/PF-9 capture and verification to `--out evidence/e2e/2026-10-19/capture-401873010` (historical fixtures untouched), record labeled replay as `GAP PROCEDURE_UNBOUND` (not executable as a repeatability procedure), and add explicit S2 hide/update/show steps with revision/fact comparisons and template observations; still no live claim ([#44](https://github.com/1wgrumph/amazon-fantasy-companion/issues/44), [PR #126](https://github.com/1wgrumph/amazon-fantasy-companion/pull/126)).
- Assemble the Phase 2 developer feedback set under `docs/developer-feedback/`: an observations index, per-tool Product Feedback, feature requests and a sanitized friction log, with pending sections named for X09, X10, X11 and M13 ([issue #51](https://github.com/1wgrumph/amazon-fantasy-companion/issues/51), [PR #123](https://github.com/1wgrumph/amazon-fantasy-companion/pull/123)); review repair adds `source_not_durable` tags and a typed gap, the six missing scanner and config tools, per-tool build-again answers and corrected counts.
- Add the submission demo plan and owner checklist (P2-D05): a 156 s shot list (12 + 22 + 28 + 30 + 32 + 18 + 14) covering the alert → Watch and lineup panel moments only at proven strength (Prime Video `searchOpened`, full-screen panel, panel-only alerts, manual lineup), with live/Alexa/final-APK shots marked PENDING, the protected-video limit stated conditionally on the unrecorded OD-AFC-P2-02 decision, Vega listed only as a paused stretch target; and a checklist mapping every owner-only action and §Exclusions duty to William with due times before the 2026-10-23T19:00:00Z deadline and evidence-derived states, with the hackathon-admin items unresolved and no owner action performed by agents ([#50](https://github.com/1wgrumph/amazon-fantasy-companion/issues/50), [PR #125](https://github.com/1wgrumph/amazon-fantasy-companion/pull/125)).
- Add the submission README with fresh-setup instructions for the TV app and backend, the judge-access route through T_judge_access, and a limitations table using the spike verdict words (SP-1 WORKS; SP-2 and SP-4 and SP-6 FAILS; SP-3, SP-5 and SP-7 PARTIAL), with Alexa/voice marked PENDING — X11 disposition and the live X09/X10 flow marked pending; prepare the standard Apache-2.0 `LICENSE` file selected by SD-035 (no publication or visibility change) ([#48](https://github.com/1wgrumph/amazon-fantasy-companion/issues/48), [PR #121](https://github.com/1wgrumph/amazon-fantasy-companion/pull/121)).
- Record the SP-8 Alexa route verdict (P2-X11): FAILS — no supported Alexa announcement (AFC-PR-022) or Alexa-assisted tuning (AFC-PR-036) route exists for a third-party Fire OS TV app on the leased stick (AFTKM, Fire OS 8.1.8.5, API 30), so OD-AFC-03 closes with the recorded no-offer disposition; the inspected on-device Alexa package exposed no third-party speak/tune surface (others uninspected), VSK is user-to-app only, and the only speak-capable surface found (Android TTS engines) is non-Alexa and unverified ([#45](https://github.com/1wgrumph/amazon-fantasy-companion/issues/45), [PR #120](https://github.com/1wgrumph/amazon-fantasy-companion/pull/120)).
- Integrate G5 TV wiring onto current main with M03–M05 recovery evidence, mutation-adapter fixture correction, and projected live-prep DOC-LINK repair; this draft replaces conflicting PR #113 without closing it ([PR #115](https://github.com/1wgrumph/amazon-fantasy-companion/pull/115)).
- Record the Phase 1 planning delta for OD-AFC-01 = B: S41 dispatchable, the owner's S06/S06L ordering waiver, dispatch and landing records for S41 (Alphazedehq #361), S11T (#307) and S11 (#364), an execution route note, the Bearing Lite 1.1.7 native-check results, a proposed (not live) SEIT amendment for four command corrections and a proposed Muse skill-path correction; regenerate the DoD Manifest so these slices show as landed ([PR #108](https://github.com/1wgrumph/amazon-fantasy-companion/pull/108)).
- Wire TV alerts and Watch to the live backend (gap G5): the shell starts AlertService when a session exists and at least one alert type is enabled, and stops it otherwise; alerts appear panel-only above the fullScreen lineup (P2-X02 and P2-X04 FAIL), newest three first, each with D-pad Watch and Dismiss (OK, Enter, numpad Enter or gamepad A), in one scrolling panel that brings the focused card or row into view; the alert cursor and dismissals persist on the device, so an AlertService restart neither replays the history nor brings back a dismissed alert; a device-local Profile/Settings switch "Show panel on new alert" (default on) re-shows a hidden fullScreen panel when a new alert arrives; Watch, from the panel or the notification's WatchActivity, uses the alert's route or GET /v1/providers, launches only a verified fire_os registry `uri`/`intent` (never a bare package MAIN, per P2-X03), honors switching confirmation and reports exactly one routing outcome, even when the panel is torn down after the launch; the A04 Watch stubs are removed ([PR #113](https://github.com/1wgrumph/amazon-fantasy-companion/pull/113))
- Record the SP-4 panel-beside-provider-video verdict (P2-X04): FAILS — Prime Video declares no picture-in-picture support, panel picture-in-picture covers the video, overlays need a Settings grant and would still cover it, and split/freeform launches come up full-screen, so the panel is built as `PanelMode.fullScreen` per AFC-PR-047 ([PR #106](https://github.com/1wgrumph/amazon-fantasy-companion/pull/106)).
- Land the sanitized projection of the 2026-10-18 P2-L02 recovery deploy and JUnit evidence (change-set describe, stage and execute receipts, deployed and smoke output and JUnit XML; `<repo>/`, `<tools>/` and `<acct>` placeholders, source and projected sha256 in [`PROJECTION.md`](docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L02/recovery-2026-10-18/PROJECTION.md)), closing the last criterion of [#29](https://github.com/1wgrumph/amazon-fantasy-companion/issues/29) ([PR #116](https://github.com/1wgrumph/amazon-fantasy-companion/pull/116)).
- Record the afc-dev redeploy of origin/main 37dcb7f (G4 alert contract): stack UPDATE_COMPLETE, deployed smoke 4 passed with 22 deselected by the link filter, suite 26 passed ([PR #107](https://github.com/1wgrumph/amazon-fantasy-companion/pull/107)).
- Record the SP-2 (P2-X02) heads-up notification spike verdict: FAILS on the leased Fire TV stick (AFTKM, Fire OS 8.1.8.5, API 30) — a foreground-service high-importance notification with Watch/Dismiss posts without interrupting Prime Video playback but never peeks as a heads-up banner (with or without PRIORITY_HIGH or a full-screen intent) and the Settings > Notifications center does not present the alert or its actions, so AFC-PR-015 is not unblocked and the AFC-PR-021 panel-only presentation is the selected fallback ([PR #109](https://github.com/1wgrumph/amazon-fantasy-companion/pull/109))
- Record the SP-3 provider links desk verdict (PR 1 of 2, PARTIAL, Prime Video TNF check pending in PR 2): on the Fire TV stick, Prime Video's `https://watch.amazon.com/search` URI opens its search screen and on-demand playback starts, while ESPN, DirecTV Stream and YouTube TV are not installed and local broadcast has no carrying app; the provider registry records the verified Prime Video route and `REGISTRY_ROUTE_GAP` for every unproven route; a `/detail?gti=` link opens a Prime Video title page (recorded as an investigation result, not registered), an ESPN summary receipt sources the channel and schedule claims, and the registry contract test rejects invalid outcomes, timestamps and invented or missing routes ([PR #110](https://github.com/1wgrumph/amazon-fantasy-companion/pull/110)).
- Record the afc-dev redeploy of origin/main 66aa531 (G3 panel wire contract and boxscore ingest bounds): stack UPDATE_COMPLETE, deployed smoke 4 passed with 22 deselected by the link filter, suite 26 passed ([PR #104](https://github.com/1wgrumph/amazon-fantasy-companion/pull/104))
- Record the P2-L03 deploys of the integrated backend to afc-dev: interim c194dee, then final af0e0ac with the new PlayerStatsTable; deployed smoke and suite results, and lineup source manual ([#96](https://github.com/1wgrumph/amazon-fantasy-companion/pull/96)).
- Record Phase 2 execution state through wave 4 in implementation.json (planning delta P2-W4-EXECUTION-STATE) and regenerate the DoD Manifest ([#98](https://github.com/1wgrumph/amazon-fantasy-companion/pull/98)).
- Document the dev AWS CLI sign-in, the Yahoo app settings and the Yahoo SSM parameters in docs/operations/aws-and-yahoo-setup.md ([#91](https://github.com/1wgrumph/amazon-fantasy-companion/pull/91)).
- Record the SP-6 Yahoo verdict: the Yahoo route FAILS because unapproved apps receive 403 from the Fantasy API while OAuth succeeds, and the selected lineup source is manual ([PR #100](https://github.com/1wgrumph/amazon-fantasy-companion/pull/100)).
- Record the Phase 1 plan evidence, packets and handoff that were left uncommitted in the planning worktree ([#90](https://github.com/1wgrumph/amazon-fantasy-companion/pull/90)).
- Record the P2-X01 device baseline on the Fire TV stick: Fire OS 8.1.8.5 / API 30, the pinned starter installed and launched, spike verdict WORKS ([#89](https://github.com/1wgrumph/amazon-fantasy-companion/pull/89)).
- Add the backend panel service: GET /v1/panel serves the followed team/league PanelState with one row per starter, points scored under the selected PPR/Half-PPR preset or the Yahoo league stat modifiers, game status, team total and progress, the scoring basis on every panel, unavailable values as null with a reason (never zero), stale values labeled at 60 s, and game facts that agree with the alert record across scoring corrections ([#88](https://github.com/1wgrumph/amazon-fantasy-companion/pull/88)).
- Add the backend alert policy: red-zone (strictly inside the 20 by a matched starter's team), player-score and close-game (margin within 8 in Q4 or overtime, once per entry) alerts gated by enabled types, game-day periods, quiet hours, per-game minimum gap and spoiler delay; fixed-template Mild/Hype commentary that makes no on-field claim; and GET /v1/alerts serving only the linked profile's released alerts ([#85](https://github.com/1wgrumph/amazon-fantasy-companion/pull/85)).
- Add the backend event matcher: ESPN-athlete-id identity for manual starters and Yahoo starters mapped by exact name, team and position through the explicit player map (unmatched or ambiguous players are never guessed), one match per profile and event, and scoring corrections that revise the existing alert in place instead of allocating a new one ([#84](https://github.com/1wgrumph/amazon-fantasy-companion/pull/84)).
- Add the TV Watch launcher: executes only a verified Fire OS registry route (intent or URI with event/channel placeholders filled), reports exactly one routing outcome per attempt (appAbsent, playbackDenied, or accessUnknown while no current-attempt observation is supported, never a reused gameOpened), honors switching confirmation, gates Alexa-assisted tuning on a verified route, and leaves the app after a started full-screen launch ([#83](https://github.com/1wgrumph/amazon-fantasy-companion/pull/83)).
- Add the TV lineup panel: rows, team total, progress and scoring-basis label for the followed team/league; stale values labeled at 60 s and unknown values shown as unavailable, never zero; remote show/hide and team/league switch, changed-row updates on a 30 s refresh, and fullScreen hosting pending the P2-X04 mode verdict ([#81](https://github.com/1wgrumph/amazon-fantasy-companion/pull/81)).
- Add the TV alert path: the foreground long-poll feed with cursor handling, a bounded coalescing queue, local dismiss, alert text carrying the triggering player and matchup with unknown access shown as unknown, heads-up Watch/Dismiss notifications, and voice kept off without a verified route ([#80](https://github.com/1wgrumph/amazon-fantasy-companion/pull/80)).
- Add the backend provider resolver: preference-ordered selection among installed providers carrying the event's channel from the read-only registry, per-platform routes with REGISTRY_ROUTE_GAP for missing or unverified entries, an honest access basis that is never inferred from installation, and recording of detector reports and routing outcomes ([#77](https://github.com/1wgrumph/amazon-fantasy-companion/pull/77)).
- Add ESPN-feed ingest outage handling: packaged replay corpus, scoreboard-error fallback to labeled replay, warm-container failure counts, and a 60s poll deadline ([#76](https://github.com/1wgrumph/amazon-fantasy-companion/pull/76)).
- Add ESPN feed ingest: pinned JSON Schema validation that rejects a bad
  poll before any store write, per-play GameEvent normalization with
  monotonic correction revisions, hash-verified fixture replay labeled
  `replay`, labeled monitoring decisions, and an allowlisted scheduled
  poller ([#76](https://github.com/1wgrumph/amazon-fantasy-companion/pull/76)).
- Add the TV profile and installed-app detection host code: settings codec with schema validation and documented defaults, revision-checked profile persistence, customer overrides over detection, opt-in detector reporting, and the Profile/Settings screen with stated limits for unsupported routes ([#74](https://github.com/1wgrumph/amazon-fantasy-companion/pull/74)).
- Record the P2-L02 afc-dev deploy of origin/main `2d973bd`: eleven known routes answered, nine deployed smoke tests passed; two panel tests remain deferred until P2-B07/L03 ([#70](https://github.com/1wgrumph/amazon-fantasy-companion/pull/70)).
- Add the TV app host foundation: shell, API client, Link screen, Gradle and manifest, 70% host coverage gate, and bounded PIT mutation scoring ([#73](https://github.com/1wgrumph/amazon-fantasy-companion/pull/73)).
- Add lineup sources and scoring presets: read-only Yahoo client, manual
  lineup with T_yahoo activation, one active source per profile, PPR and
  Half-PPR tables with Half-PPR as default ([#65](https://github.com/1wgrumph/amazon-fantasy-companion/pull/65)).
- Add the ESPN feed capture tool and historical replay fixtures for 14
  completed games, with an interim SP-5 verdict ([#63](https://github.com/1wgrumph/amazon-fantasy-companion/pull/63)).
- Add the 2026-10-14 developer friction-log catch-up (ten observations in
  the house format) ([#62](https://github.com/1wgrumph/amazon-fantasy-companion/pull/62)).
- Add the backend foundation: SAM HTTP API with throttling, Lambda router
  and response envelope, DynamoDB store, device-code linking with a
  passphrase-confirmed phone page, bounded session retry, least-privilege
  per-function grants, pipeline and module stubs, and hash-pinned CI
  dependencies ([PR #60](https://github.com/1wgrumph/amazon-fantasy-companion/pull/60)).

- Extend the shared gate with `tvapp` and `backend` areas, their CI jobs
  and backend coverage and mutation checks with qualified tooling
  ([PR #57](https://github.com/1wgrumph/amazon-fantasy-companion/pull/57)).

- Add V&V guidance areas for the TV app, backend and device integration,
  and update the V&V index so every path keeps one owning area
  ([PR #56](https://github.com/1wgrumph/amazon-fantasy-companion/pull/56)).

- Create and verify all 13 Phase 2 milestones and 39 work issues with
  dependency links; reconcile three calendar dates while preserving exact
  deadlines ([PR #55](https://github.com/1wgrumph/amazon-fantasy-companion/pull/55)).

- Add the Phase 2 delivery and verification package with 13 chronological
  GitHub milestones, 39 work-issue drafts and 52 slices, preserving five
  technical waves and release checkpoints; product execution remains held
  pending a separate owner instruction
  ([PR #15](https://github.com/1wgrumph/amazon-fantasy-companion/pull/15)).

### Changed

- OpenCodeReview now reviews test files. Its built-in default path filter skipped Kotlin unit tests under `src/test/` and Python `test_*.py` files, so 7 of 16 code files in a sample commit were never reviewed. `.opencodereview/rule.json` includes them again.
- Make Fire OS the primary target again and Vega a compatibility target proven on the Vega Virtual Device, because the only TV device is a Fire OS stick (owner amendment 2026-10-19, superseding Vega primary); physical-Vega checks become not applicable, the eight Vega overrides are re-scoped to VVD compatibility and R1 ships the Fire OS APK ([PR #117](https://github.com/1wgrumph/amazon-fantasy-companion/pull/117)).
- Keep only the pre-push hook; commits no longer run the gate locally (CI and pre-push still do) ([PR #97](https://github.com/1wgrumph/amazon-fantasy-companion/pull/97)).
- Select Vega OS as the primary TV target with Fire OS remaining the secondary target, and rebind the Phase 2 plan package (DEC-AFC-SD-048 through DEC-AFC-SD-054) ([#72](https://github.com/1wgrumph/amazon-fantasy-companion/pull/72)).
- Link a TV with its device code alone (DEC-AFC-SD-048): drop the link
  passphrase from the `/link` page, the confirm API and its OpenAPI
  contract, and remove the SSM passphrase parameter, its env var and IAM
  grant; code expiry, throttling and one-session-per-link stay ([#66](https://github.com/1wgrumph/amazon-fantasy-companion/pull/66)).
- Record the Phase 2 execution lease and the M01 dispatch, review and
  closeout receipts in the Lifecycle control journey
  ([PR #58](https://github.com/1wgrumph/amazon-fantasy-companion/pull/58)).

- Freeze the complete `opensource-hackathon` profile under Bearing 1.1.7,
  including capability settings and Muse contributor mode; preserve spent
  review limits and validate the Markdown register through the native
  precheck's in-memory interface
  ([PR #15](https://github.com/1wgrumph/amazon-fantasy-companion/pull/15)).

- Add architecture specification revision 0.3 with clickable references, per-revision changed sections and PR/diff links; update the vendored authoring tools ([PR #10](https://github.com/1wgrumph/amazon-fantasy-companion/pull/10), [diff](https://github.com/1wgrumph/amazon-fantasy-companion/pull/10/files)).

### Fixed

- Stop the panel serving a starter's previous-game points as current: a stored statistics record whose game is final and whose `asOf` is older than `FINAL_RECORD_WINDOW` (12 hours) now yields `value: null` with reason "no statistics for current game", no `gameStatus`, and no contribution to progress, so a starter with no event in the new game starts unknown instead of showing last week's final; a final inside the window, or a live game, is still served ([#94](https://github.com/1wgrumph/amazon-fantasy-companion/issues/94), [#131](https://github.com/1wgrumph/amazon-fantasy-companion/pull/131)).
- Let D-pad Up/Down traverse every Profile/Settings text field; Select opens text editing, Back returns to form navigation, IME Next advances focus, and Done dismisses the keyboard (BUG-A02-1, [#129](https://github.com/1wgrumph/amazon-fantasy-companion/pull/129)).
- Repair the submission README after review: mark first-run lineup entry unavailable (no TV starter entry and no backend lineup-write route), document the hygiene `python3`/PyYAML environment and its pinned install command, mark Devpost submission/demo judge access PENDING with the owner publication action and retention through 2026-11-20, and record `GAP PROC_README_FRESH_SETUP_NOT_RUN` for the unrun clean-checkout walkthrough ([#48](https://github.com/1wgrumph/amazon-fantasy-companion/issues/48), [PR #121](https://github.com/1wgrumph/amazon-fantasy-companion/pull/121)).
- Serve the broadcast channel route for a game: ingest stores each game's ESPN broadcast name (the first valid `header.competitions[0].broadcasts[].media.shortName` in ESPN's listed order) on its GameEvents, and `provider_resolver.event_channel` reads it back, so GET /v1/providers and alert routes resolve the registry provider for that channel (for example Prime Video for Thursday Night Football) instead of always reporting an unknown channel. An absent, blank, oversize or malformed broadcast omits the channel without rejecting the game; the summary schema keeps only size bounds on broadcasts ([PR #114](https://github.com/1wgrumph/amazon-fantasy-companion/pull/114)).
- Serve a registry platform route as verified only when its `verified_outcome` is one of the six RoutingOutcome values and its `verified_at` is a real UTC instant in the registry's canonical `YYYY-MM-DDTHH:MM:SSZ` form; an unknown, non-string, missing, unparseable, naive, non-UTC or non-canonical value (including offsets such as `+00:00` and fractional seconds) is now a `REGISTRY_ROUTE_GAP` on every Python version, so the TV never launches a malformed registry entry ([PR #111](https://github.com/1wgrumph/amazon-fantasy-companion/pull/111)).
- Pin the TV-app Gradle daemon memory in tv-app/gradle.properties (-Xmx2g, -XX:MaxMetaspaceSize=1g) so the tvapp gate no longer intermittently dies with OutOfMemoryError: Metaspace in testDebugUnitTest/lintAnalyzeDebug on loaded machines (clean-run metaspace peak measured at roughly 260-288 MiB against Gradle's 384 MiB default), with a tools/ci/tests check that parses the file like java.util.Properties and holds the effective (last) -XX:MaxMetaspaceSize at or above 512 MiB and -Xmx at or above 1 GiB ([PR #112](https://github.com/1wgrumph/amazon-fantasy-companion/pull/112)).
- Make GET /v1/alerts honor the TV alert wire contract on the backend: carry a sourced, optional `matchup` label (away/home abbreviations from the ESPN summary header competitors, bounded in the ingest schema) through GameEvent storage into `triggerContext`, absent rather than fabricated when unknown; keep every producer cursor and `~r<revision>` progress token within the TV's 256-character limit with a deterministic compact form for long event ids and bounded digest tokens for legacy long-key rows, so resume and higher-revision delivery keep working without a rejected-page loop (review repair: digest tokens resolve regardless of revision for 254-256 character legacy cursors, and display-only competitor deviations omit the matchup instead of rejecting the whole summary); define concrete AlertEnvelope/AlertData/TriggerContext/ProviderRoute OpenAPI schemas validated against real served payloads, with backend-generated golden payloads for RedZone, PlayerScore, CloseGame and an empty-starters correction ([PR #105](https://github.com/1wgrumph/amazon-fantasy-companion/pull/105)).
- Make GET /v1/panel honor the TV panel wire contract: lineups over 32 starters or with blank or duplicate player identity are rejected at the manual/Yahoo write boundary and legacy stored rows fail closed with a structured `panel_invalid` error instead of an unusable 200; a store-allocated monotonic lineup version makes every lineup change, return, removal and re-add serve a strictly higher panel revision; mixed dated/undated aggregates are never served as fresh; OpenAPI now defines concrete PanelEnvelope/PanelData/PanelValue/PanelRow schemas whose nullable `source` enums admit the served `null`; the store rejects over-32, blank or duplicate starters at its own write boundary; and the panel reads its revision inputs strongly consistent so a lagging replica never serves a lower revision ([PR #101](https://github.com/1wgrumph/amazon-fantasy-companion/pull/101)).
- Isolate every gate-test fixture git command through one shared helper: it drops host and hook `GIT_DIR`/`GIT_INDEX_FILE`/`GIT_WORK_TREE`-style variables, never discovers a repository above the fixture, and reports git's own error text on failure, so a run from a git hook can no longer write into the host repository and the intermittent `git clone` exit 128 in the CI-base gate test now shows its cause when it recurs. The cause of that exit 128 is not yet proven, so the flake stays open; the gate's fail-closed CI-base behavior is unchanged ([PR #102](https://github.com/1wgrumph/amazon-fantasy-companion/pull/102)).
- Scope the git-hook gate to the change being committed or pushed: pre-commit checks the staged diff only (during a merge, only what the merge itself introduces), and pre-push checks the pushed commit range, so merged-in already-landed whitespace no longer blocks a merge commit and unrelated unstaged or untracked files no longer select the tvapp/backend areas for a docs-only commit ([PR #93](https://github.com/1wgrumph/amazon-fantasy-companion/pull/93)).
- Store per-player ESPN boxscore statistics at ingest and read them through the panel's statistics seam, so the deployed panel shows real fantasy points instead of "statistics unavailable" for every starter ([PR #95](https://github.com/1wgrumph/amazon-fantasy-companion/pull/95)).
- Make the TV app present server-generated alerts (canonical B05 alert types, bounded starter-derived context without a fabricated matchup, Watch event ID from triggerContext) and show panel source provenance (manual/yahoo lineup source, replay values labeled) ([PR #99](https://github.com/1wgrumph/amazon-fantasy-companion/pull/99)).
- Correct the Yahoo setup notes: one app with redirect `https://localhost:8443/link`, the one-command `setup` token flow, and the errors seen on 2026-10-16 ([#92](https://github.com/1wgrumph/amazon-fantasy-companion/pull/92)).
- Grant the policy function table-scoped Lineups Scan access used by the matcher
  and the API function Profiles UpdateItem access for provider routing outcomes
  and installed-app reports, with source-to-template IAM contracts to catch
  permission drift ([#87](https://github.com/1wgrumph/amazon-fantasy-companion/pull/87)).
- Restore legible inherited text and unfocused button labels across the dark TV app theme ([#86](https://github.com/1wgrumph/amazon-fantasy-companion/pull/86)).

- Preserve ESPN play period and scoringPlay in stored GameEvents, validate both before writes, and revise events when either fact changes ([#79](https://github.com/1wgrumph/amazon-fantasy-companion/pull/79)).

- Discover the user-scope JDK 17 and Android SDK for local gate and hook runs
  without exported toolchain variables; preserve explicit settings and CI behavior ([#78](https://github.com/1wgrumph/amazon-fantasy-companion/pull/78)).

- Check committed PR and push changes for whitespace in CI and local hooks,
  and remove trailing whitespace from the P2-A02T evidence log ([#75](https://github.com/1wgrumph/amazon-fantasy-companion/pull/75)).

- Locate the documented backend test environment in local gates and Git hooks,
  and report a provisioning GAP when it is missing; preserve CI tool selection
  ([#71](https://github.com/1wgrumph/amazon-fantasy-companion/pull/71)).
- Bound tv-app mutation probes and parse PIT reports so host-runnable classes score honestly at 70% (DEC-AFC-SD-057) ([#73](https://github.com/1wgrumph/amazon-fantasy-companion/pull/73)).
- Restore client-side profile ID validation on `/link` by escaping the
  pattern's hyphen for Unicode Sets (`v`) mode ([#69](https://github.com/1wgrumph/amazon-fantasy-companion/pull/69)).
- Return the standard 404 error envelope for unknown API routes by routing
  unmatched requests to the existing Lambda router ([#67](https://github.com/1wgrumph/amazon-fantasy-companion/pull/67)).
- Fix the deployed-test network guard so smoke tests reach the configured
  API host (resolved and rotating addresses) while every other destination
  stays blocked ([#64](https://github.com/1wgrumph/amazon-fantasy-companion/pull/64)).
- Spec gate compares the rebuilt output against the staged index instead of
  HEAD, so a correctly regenerated staged output passes before commit
  ([PR](https://github.com/1wgrumph/amazon-fantasy-companion/pull/14)).

## 2026-10-12

### Added

- Publish AFC Lifecycle records and Orchestrator handoff ([PR #13](https://github.com/1wgrumph/amazon-fantasy-companion/pull/13)).
- B1: gate hygiene discards diff content lines before location parse ([PR #12](https://github.com/1wgrumph/amazon-fantasy-companion/pull/12)).
- S09T: gate tests (red) for AC-AFC-CI-01..04, AC-AFC-PATH-01 ([PR #9](https://github.com/1wgrumph/amazon-fantasy-companion/pull/9)).
- Link spec-authoring skill into four harness skill directories ([PR #8](https://github.com/1wgrumph/amazon-fantasy-companion/pull/8)).
- Vendor spec-authoring tools at Alphazedehq ac47f0e (S42) ([PR #7](https://github.com/1wgrumph/amazon-fantasy-companion/pull/7)).
- Spec track ST-1..ST-3: requirements register and SysML v2 models ([PR #6](https://github.com/1wgrumph/amazon-fantasy-companion/pull/6)).
- Wave 1 landing receipts and plan digest a018168f ([PR #5](https://github.com/1wgrumph/amazon-fantasy-companion/pull/5)).
- Phase 1 plan delta SD-026..028 and Wave 1 receipt ([PR #4](https://github.com/1wgrumph/amazon-fantasy-companion/pull/4)).
- docs: add Phase 1 Vnv guidance tree ([PR #3](https://github.com/1wgrumph/amazon-fantasy-companion/pull/3)).
- Add approved Phase 1 planning package (AFC-2026-10-11) ([PR #2](https://github.com/1wgrumph/amazon-fantasy-companion/pull/2)).

[Unreleased]: https://github.com/1wgrumph/amazon-fantasy-companion/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/1wgrumph/amazon-fantasy-companion/compare/2c13a6bf560e87d11864cc6234f48e40dd9cf529...v0.1.0
