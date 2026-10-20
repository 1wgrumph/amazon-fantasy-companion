# Amazon Fantasy Companion — hackathon submission write-up

Track: Fire TV. Optional mini-challenge addressed in this write-up: AWS Builder.
Primary target: Fire OS (AFC-PR-052, AFC-PR-053). Every capability sentence
below names its landed evidence. Anything that still depends on a live run is
marked PENDING in place; no pending result is asserted.

## What the product does

The companion watches live NFL games for the viewer's fantasy starters and
raises tune-in alerts — red-zone entry, player score, and close game — with a
Watch action that hands off to the provider app carrying that game. A lineup
panel shows each starter's points, the team total, and progress. The backend
holds the profile, ingests the live feed, matches events to starters, applies
the alert policy, and serves the panel; the Fire TV app polls for alerts and
panel state, presents them, and executes Watch.

## Fire TV integration (from evidence)

- **Device baseline — SP-1 verdict WORKS.** On a physical Fire TV stick
  (model AFTKM, Fire OS 8.1.8.5, Android 11 / API 30, display override
  1920x1080) the pinned starter installed, launched, and rendered
  (`spikes/sp1-device/VERDICT.md`, first install 2026-10-16T12:19:31Z,
  PR #89). Limits recorded there: the original install's "Success" line was
  not committed (install is evidenced by the device install record plus an
  installed-APK hash match), and Prime Video sign-in for that slice was
  owner-reported, not device-verified.
- **Lineup panel — SP-4 verdict FAILS for beside-video; full-screen selected.**
  Five composition routes were tried against playing Prime Video
  (`spikes/sp4-panel-video/VERDICT.md`, PR #106): Prime Video declares no
  picture-in-picture support; panel picture-in-picture works mechanically but
  covers the video; an overlay needs a Settings grant and would still cover
  it; split-screen and freeform launches come up full-screen. No route shows
  the panel *beside* playing provider video with no overlap and no crop, so
  the panel is built as `PanelMode.fullScreen` per AFC-PR-047. The panel
  serves one row per starter with points under the selected PPR / Half-PPR
  preset (or Yahoo league stat modifiers for Yahoo leagues), the scoring
  basis on every panel, unavailable values as null with a reason (never
  zero), and stale values labeled at 60 s (CHANGELOG, PR #88; TV panel,
  PR #81).
- **Alerts — SP-2 verdict FAILS for heads-up; panel-only selected.** A
  foreground service can post a high-importance notification with Watch and
  Dismiss on this stick and Prime Video playback continues undisturbed, but
  Fire OS never shows it as a heads-up banner — not over playback, not over
  Home, not with `PRIORITY_HIGH` or a full-screen intent — and Settings >
  Notifications presents only the foreground-service notification, not the
  alert or its actions (`spikes/sp2-notify/VERDICT.md`, PR #109). AFC-PR-015's
  heads-up case is therefore not claimed; alerts appear panel-only above the
  full-screen lineup, newest three first, each with D-pad Watch and Dismiss,
  with the cursor and dismissals persisted on the device (CHANGELOG,
  PRs #80, #85, #115 — the G5 wiring entry). A device-local switch,
  "Show panel on new alert" (default on), re-shows a hidden full-screen
  panel when a new alert arrives.
- **Provider routing — SP-3 verdict PARTIAL.** Desk evidence on the same
  stick (`spikes/sp3-provider-links/VERDICT.md`, PR #110;
  `backend/src/provider_resolver/registry.json`): Prime Video's
  `https://watch.amazon.com/search` URI opens its search screen
  (`searchOpened` registered; query parameters are ignored) and on-demand
  playback starts (player chrome and media-session state; the picture itself
  is not capturable). ESPN, DirecTV Stream, and YouTube TV are not installed
  (`appAbsent` observed) and local broadcast has no carrying app; every
  unproven route is `REGISTRY_ROUTE_GAP`. A `/detail?gti=` link opens a Prime
  Video title page but is not registered: no documented mapping from an ESPN
  event to a Prime title GTI exists. The TV Watch launcher executes only a
  verified `fire_os` registry route and reports exactly one routing outcome
  per attempt (CHANGELOG, PR #83; resolver, PR #77). Live Prime Video
  Thursday Night Football `gameOpened` is unproven — see Pending.
- **Linking.** The TV shows a short-lived device code; the viewer confirms
  only a code on their own TV (code-only linking, short expiry, one-time
  confirmation) (CHANGELOG, PRs #60, #68, #73).
- **Installed-app detection — SP-7 verdict PARTIAL.** Installed/absent
  detection works at shell level, Prime Video leanback launchability
  resolves, and a later in-app probe reported installed-enabled, absent, and
  installed-disabled (own-package self-disable only); disabled-state creation
  is unsupported from the ADB shell on this Fire OS build
  (`spikes/sp7-detection/VERDICT.md`). The product keeps detection hidden
  behind `detectionSupported = false`; no product activation is claimed.
  Resolution never infers subscription or game access from installation
  alone (CHANGELOG, PR #74, PR #77).

## AWS Builder integration (from the repository and deployed evidence)

The backend is a SAM application (`backend/template.yaml`) deployed as the
CloudFormation stack `afc-dev` in `us-east-2`
(`docs/operations/aws-and-yahoo-setup.md`). Services and what each does:

- **API Gateway (HTTP API)** — the `/v1` routes (`/v1/link`, `/v1/profile`,
  `/v1/alerts`, `/v1/panel`, `/v1/providers`, `/v1/routing-outcome`,
  `/v1/installed-apps`) plus the `/link` confirmation page, with throttling.
- **Lambda (python3.12)** — three functions: the API router
  (`api.handler.lambda_handler`), the ESPN ingest
  (`feed_ingest.lambda_handler`), and the DynamoDB Streams pipeline consumer
  (matcher, alert policy, provider route, panel). Each carries
  least-privilege per-function DynamoDB grants; the public API function's
  unused Yahoo SSM read access was removed (CHANGELOG, PRs #60, #68).
- **DynamoDB (on-demand)** — Profiles, Links, Events (with a NEW_IMAGE
  stream), Alerts, Lineups, Panels, and PlayerStats tables.
- **EventBridge Scheduler** — `rate(1 minute)` ingest trigger, disabled by
  default (`IngestScheduleState`); it runs only while a profile-relevant game
  is in progress.
- **SSM Parameter Store** — Yahoo client secret and OAuth refresh credential
  as `SecureString`; no secret value is in the repository.
- **CloudWatch Logs** — per-function log groups.

Deployed results are claimed only where recorded: the `afc-dev` deploys in
CHANGELOG reached stack `UPDATE_COMPLETE` with deployed smoke 4 passed (22
deselected by the link filter) and suite 26 passed for the recorded commits
(PRs #104, #107); the earlier P2-L02 deploy answered eleven known routes
with nine deployed smoke tests passed and two panel tests deferred (PR #70),
and the P2-L03 deploys recorded the new PlayerStats table with lineup source
manual (PR #96). The ingest path validates ESPN payloads against a pinned
schema before any store write, replays labeled historical fixtures (14
completed games, PR #63), and bounds boxscore ingest against denial-of-service
inputs (PR #103; `spikes/sp5-espn-feed/VERDICT.md`).

## Differentiation from YouTube TV Fantasy View (external context)

> External context — not product capability. Sources accessed 2026-10-20:
> YouTube's Fantasy View announcement
> (https://blog.youtube/news-and-events/introducing-fantasy-view-youtube-tv/)
> and YouTube TV Help, Fantasy Football View
> (https://support.google.com/youtubetv/answer/9119412;
> current page: https://support.google.com/youtubetv/answer/15583839).

Roster scores beside the game there; tune-in alerts and cross-provider Watch
here. YouTube TV links an ESPN or Yahoo league and shows roster scores
beside the game. This companion instead collects personalized tune-in
alerts in the background and presents them in its own full-screen panel
(panel-only presentation; no reachable notification during provider
playback — the heads-up route failed, see Honest limits) and offers a
cross-provider Watch
handoff resolved from the event's channel and the viewer's installed apps,
subscriptions, local market, and preference. No tune-in-alert or
cross-provider Watch claim is made for Fantasy View; the comparison claims
only what the cited sources say.

## Future direction — DEC-AFC-SD-036 (external context, discussion only)

> External context — not product capability. Sources accessed 2026-10-20:
> Amazon, "How Prime Video is using AWS-powered AI to change the way fans
> watch Thursday Night Football"
> (https://www.aboutamazon.com/news/aws/prime-video-thursday-night-football-next-gen-stats-ai-features);
> Amazon, "Prime Video reaches a landmark 11-year streaming deal with the NBA
> and the WNBA"
> (https://www.aboutamazon.com/news/entertainment/prime-video-nba-wnba-streaming-deal);
> Amazon Ads, "Prime Video and NBA announce landmark global coverage deal"
> (https://advertising.amazon.com/blog/prime-video-nba-2025-deal).

Prime Video already ships an analytics viewing layer over Thursday Night
Football (Prime Vision with Next Gen Stats and AI features, per the first
source), and Amazon holds NBA and WNBA rights on Prime Video (11-year deal:
NBA beginning with the 2025–26 season and WNBA beginning in 2026, per the
second and third sources). If this product grew
in that direction, the sport-agnostic parts — alert policy, Watch handoff,
and panel — would carry over; the NFL-specific parts — the ESPN feed adapter
and the PPR / Half-PPR scoring presets — would need sport-specific
replacement. None of this is built, scheduled, or claimed as product
capability.

## Honest limits

- No heads-up notification over provider playback (SP-2 FAILS; panel-only is
  the shipped presentation). Playback was never interrupted by a post, but
  the alert and its Watch/Dismiss actions are unreachable through the
  notification UI on this Fire OS build.
- No picture-in-picture or panel beside provider video (SP-4 FAILS); the
  panel is full-screen in the companion app. Protected provider video also
  captures black, so playback evidence is player chrome plus media-session
  state (RISK-AFC-P2-09).
- Provider `gameOpened` is unproven for every provider (SP-3 PARTIAL). The
  one registered Prime Video route lands on search, not the game; ESPN,
  DirecTV Stream, YouTube TV, local broadcast, and all `vega` routes are
  `REGISTRY_ROUTE_GAP`. Routing outcomes are reported honestly and never
  relabeled (RISK-AFC-P2-03); there is no current-attempt observation
  (`currentAttemptObservation: "none"`), so a launch reports `accessUnknown`
  rather than reusing a historical outcome.
- Yahoo Fantasy is blocked for the unapproved app (SP-6 FAILS,
  `spikes/sp6-yahoo/VERDICT.md`, PR #100): OAuth succeeds, the Fantasy API
  returns HTTP 403 `This application is not authorized`. The selected lineup
  source is manual. No live Yahoo API data is used.
- Live feed timing is unmeasured (SP-5 PARTIAL): capture and historical
  replay fixtures prove parsing and validation only; the 15 s
  `feed_poll_interval` check and live correction behaviour wait for a live
  capture sequence. ESPN edits most plays after the game (2,367 of 2,656
  captured plays carry a `modified` time over an hour after `wallclock`), so
  correction timing cannot be derived from a final snapshot.
- Detection limits (SP-7 PARTIAL): installed/absent detection is supported;
  disabled-state creation is unsupported from the shell on this build, and
  the in-app disabled proof used only an own-package self-disable. Detection
  is not product-activated, and installation alone never proves subscription
  or access.
- Vega: PAUSED by the owner. Vega is named only as a paused stretch
  compatibility target with its stated limits — VVD build only, no physical
  Vega device, provider/DRM/entitlement behaviour unproven there — never as
  delivered, and it does not gate the Fire OS release (RISK-AFC-P2-14).
- No Alexa offer is claimed (X11 disposition pending), and no live X09/X10
  result is claimed (see Pending). This write-up contains no credential,
  account name, device address, or local absolute path (RISK-AFC-P2-12).

## Pending (not asserted)

- PENDING — X09 live end-to-end run (C3, 2026-10-23T00:15Z, ESPN event
  401873010) and X10 live hardening: scheduled, not yet run; no result is
  claimed.
- PENDING — X03 PR 2 (live Prime Video TNF `gameOpened` check) and X05 PR 2
  (live feed timing and correction sequence): both verdicts remain PARTIAL
  until those live checks land.
- PENDING — X11 Alexa disposition: no Alexa offer is made until it lands.
- PENDING (owner) — submission-rule confirmations that issue #1 and the
  technical plan do not settle: final track/mini-challenge selection beyond
  Fire TV, and the ESPN-terms question for public submission (OA-6/C3, still
  open per the SP-5 verdict). These are recorded as owner items rather than
  guessed.
- The combined `PROC-SUBMISSION-CHECK` needs all three M12 deliverables
  (write-up, demo plan, owner checklist). The write-up part is run now; the
  combined check completes when D05 lands.

## Evidence index

- Device, panel, alerts, providers, detection: `spikes/sp1-device/VERDICT.md`
  (WORKS), `spikes/sp2-notify/VERDICT.md` (FAILS),
  `spikes/sp3-provider-links/VERDICT.md` (PARTIAL),
  `spikes/sp4-panel-video/VERDICT.md` (FAILS), `spikes/sp7-detection/VERDICT.md`
  (PARTIAL); PRs #89, #106, #109, #110, #114, #115.
- Feed: `spikes/sp5-espn-feed/VERDICT.md` (PARTIAL); PR #63, PR #103.
- Lineup source: `spikes/sp6-yahoo/VERDICT.md` (FAILS, manual selected);
  PR #100.
- Backend, deployment, TV app: `backend/template.yaml`, `backend/src/`,
  `tv-app/app/src/main/java/com/afc/companion/`, `CHANGELOG.md`, and
  `docs/operations/aws-and-yahoo-setup.md` (stack `afc-dev`, `us-east-2`, SSM
  parameter names; no secret values).
