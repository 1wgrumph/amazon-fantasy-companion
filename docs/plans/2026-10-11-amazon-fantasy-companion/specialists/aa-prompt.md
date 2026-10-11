You are the Bearing Lite Architectural Alignment planning node (BEARING_ROLE=architectural_alignment). Load and follow the bearing-lite:architectural-alignment skill exactly.

Confirmed inputs (DEC-AFC-001, journey.json):
- Repository root (checkout): $HOME/alphazede/worktrees/amazon-fantasy-companion-planning  (linked worktree of $HOME/alphazede/Hackathons/amazon-fantasy-companion)
- GitHub: 1wgrumph/amazon-fantasy-companion (private)
- Branch: plan/2026-10-11-amazon-fantasy-companion at 2c13a6b (seed commit: README.md, .gitignore only)
- Plan directory (repo-relative): docs/plans/2026-10-11-amazon-fantasy-companion/
- Lifecycle title: Amazon Fantasy Companion: architecture, program plan, milestones

Authority: write ONLY workspace.md and repository-map.md inside the plan directory. Do not edit journey.json or anything else. No git commit, push, or branch operations. Read-only elsewhere.

Bounded discovery per the skill (depth 2, <= 40 paths, <= 64 KiB). The repo contains no product code, so expect no existing architecture: record that gap and state that the Systems Modeler must be activated; do not design architecture.

External starting points (record under Unknowns/Constraints as candidates; do NOT clone or choose; selection is a Scope Definition owner decision). The owner said a GitHub starter repo should exist. Candidates found in the AmazonAppDev org via :
- AmazonAppDev/vega-sports-app — Vega sample for sports content, theming, catalog/services integration
- AmazonAppDev/react-native-multi-tv-helloworld — Yarn-workspace starter sharing code across Vega (Fire TV), Android TV, Apple TV
- AmazonAppDev/react-native-multi-tv-app-sample — Expo RN TV sample for Fire OS + Vega + Android TV + tvOS with video player
- AmazonAppDev/hello-world-fire-tv — Android Jetpack Compose Fire OS hello world
- AmazonAppDev/vega-video-sample, vega-epg-sample, vega-tv-interfaces-sample — Vega player / EPG / TV UI samples
You may run  and read each repo's README via  for at most these 7 repos to record language, target OS, license, and run commands as [observed, not run]. Do not clone.

Product context: GitHub issue 1wgrumph/amazon-fantasy-companion#1 (## Origin

William requested an issue to join and work Build, Ship, Shape: Amazon Developer Hackathon.

## Harness / version

Participation and build tracking; no product defect or harness version applies. Requirements checked October 6, 2026.

## What

Build a personalized Fire TV fantasy-sports alert companion for the Amazon Developer Hackathon. Connect Yahoo Fantasy starters to live NFL events, notify viewers while they use their viewing apps, and help them reach the relevant game through supported provider links or Alexa. Include a right-side lineup and team-progress panel alongside unobscured television playback. All behavior is customer-configurable. Community messaging is excluded by owner decision on October 10, 2026.

## Current evidence

- [Overview / registration](https://amazonappdev2026.devpost.com/), [official rules](https://amazonappdev2026.devpost.com/rules), [resources](https://amazonappdev2026.devpost.com/resources).
- Submission window: August 31–October 23, 2026. Deadline: **October 23 at 12:00 PM PDT / 2:00 PM CDT (America/Chicago)**.
- Tracks: Fire TV, Alexa+, Bee, Ring. Fire TV must run on Fire OS/Vega OS with device/simulator evidence. Alexa+ supports an Agent Skill, self-hosted MCP (spec 2025-11-25+, Streamable HTTP), or a working web simulation. Bee needs actual Bee-device/Apple-Watch Bee data. Ring supports APIs/SDKs/simulators/devices; hardware is optional.
- Optional mini challenges: AWS Builder and Open Source. Open Source requires an additional project or contribution alongside the primary entry.
- Cash pool: $138,000, plus AWS credits and other awards. Judging covers implementation, design, impact, and idea quality.

## Expected

The selected concept targets the Fire TV track. Alexa/Alexa+ is a proposed voice and viewing integration; entering an additional track or mini challenge remains undecided. The owner selected the concept below on October 10, 2026. The private working repository is recorded below; target device/OS, API access, architecture, and bounded build milestones remain to be established. This records product intent and research, not completed feasibility verification or an approved implementation plan.

### Selected concept and owner scope — October 10, 2026

A customer-configurable Fire TV companion that notices sports moments relevant to the viewer's fantasy starters and helps the viewer watch the corresponding game using available services. It operates across supported viewing apps; it is not limited to Prime Video or Thursday Night Football. A Thursday game is one possible initial live test, while Sunday coverage must exercise simultaneous games.

The owner retained items 1, 2, 3, 4, and 6 from the discussed experience:

1. **Configure the profile.** Connect Yahoo Fantasy; select leagues, teams, starters or specific players, and favorite teams. Detect supported installed viewing apps where the platform permits it. Identify subscriptions through supported provider integration or customer confirmation, retain local-market information, and let customers review and override detected information. An installed app alone is not proof of subscription or game access.
2. **Monitor during enabled viewing periods.** Monitor relevant NFL games using the profile and customer-selected schedule/game-day mode. Investigate supported detection of current viewing context, with customer control over whether it is used. Keep observed playback and profile-based assumptions distinct.
3. **Deliver personalized alerts.** Notify about relevant red-zone opportunities, player scores, and close games. A team entering the red zone is not proof that a particular player is on the field or will score. Provide verified player/matchup context and optional AI-generated excitement commentary grounded in the event data. Yahoo supplies lineup and league context; the live game feed supplies game events. Match identifiers across providers and account for duplicate events and scoring corrections.
4. **Help the customer watch the game.** Resolve the event to an available provider/channel using the customer's apps, subscriptions, local market, and provider preference. Investigate a notification action/deep link and Alexa-assisted tuning. Unknown access must remain unknown; do not promise the game is included merely because the provider app is installed. Honor the customer's switching and confirmation preferences through supported mechanisms.
6. **Customer controls throughout.** Configure fantasy selections, alert types, frequency, quiet hours/game-day periods, spoiler delay, notification presentation, voice announcements, excitement level, provider preference, switching confirmation, and use of available detection/personalization. Device-code linking is sufficient; QR is an optional convenience, not a requirement.

**Explicit exclusion:** no messenger, message boards, community rooms, shared chat, or watch-party social features in this build or submission. The owner removed these from scope to limit the concept shared with Amazon. Do not reintroduce them through the earlier ChatGPT discussion. This issue is private; recording the concept does not authorize public export or submission.

### Right-side fantasy lineup panel — owner addition October 10, 2026

Add a customer-configurable fantasy lineup panel on the right side of the TV screen so viewers can track their players and see how their team is doing while continuing to watch television. This extends the selected concept; it is not community messaging.

**Required experience:**

- Display the selected Yahoo fantasy team's lineup, each player's fantasy points and game status, and the team total/progress. Apply the league's scoring context and make unavailable or stale values clear.
- Keep the broadcast fully visible beside the panel, preserving its aspect ratio. Reserve space for the panel and fit the video into the remaining area; do not cover or crop the broadcast to make room.
- Let the customer show/hide the panel and choose the team/league to follow. Keep the interface legible from the couch, remote navigable, and consistent with the existing customer-configurable settings.
- Keep lineup state and alerts consistent, including changes to starters and scoring corrections. The panel supplements the brief alerts and supported game/channel handoff.

**Development integration obligation:** prove simultaneous video and panel display on the selected device/OS and viewing-provider route. Brief system notifications and app-launch/deep-link support do not by themselves establish the ability to resize or compose another app's video. Investigate supported split-view, playback, or provider/platform integration mechanisms during development. Record exactly which routes work. Do not silently replace this requirement with a phone screen, an app-switch-only dashboard, or a panel covering the broadcast. If the supported platform cannot realize it, return the precise limitation for an owner scope decision.

**Development evidence:**

- [ ] Show the right-side lineup panel and ongoing video simultaneously on the target device, with no overlap or cropped video.
- [ ] Verify lineup, player values, team progress and update freshness against the selected data source/scoring context.
- [ ] Demonstrate show/hide and team/league selection using the TV remote; exercise unavailable/stale data behavior.
- [ ] Capture the actual integration route and its provider/OS limits, along with Scribe friction and ease-of-use feedback.

**Demo/judging emphasis:** include the working right-side lineup panel in the video as a second standout moment alongside alert -> Watch -> correct game/channel. Show a player/team update while the broadcast remains visible. Use the proposed storyboard's profile/personalization segment to demonstrate the panel without extending the video beyond three minutes. This is recorded intent, not a claim of implemented or verified display support.

### Source review and proposed implementation route — October 10, 2026

These are documentation findings and candidate approaches, not live integration results.

| Source | Finding | Use in this concept / remaining gap |
|---|---|---|
| [Amazon Devices Builder Tools capabilities](https://developer.amazon.com/docs/adbt/capabilities) | AI-assisted development through MCP and agent skills, with full Vega support and limited Fire OS support. Relevant capabilities include Content Launcher, Live TV/EPG and tuning integration, Content Personalization, and TV UI/focus/performance tooling. | Useful development guidance for choosing the device/OS and implementing integrations. These are builder capabilities, not proof that a third-party companion can inspect or control all other apps or their subscriptions. No tools have been installed. |
| [Yahoo Fantasy API documentation](https://sports.yahoo.com/developer/docs/) | OAuth 2.0 with Read access; user/team discovery, team roster by week, selected roster positions, and league scoring settings. Roster examples distinguish active slots from bench slots. | Use a read-only Yahoo connection for lineup/league context. Investigate `/users;use_login=1/games;game_keys=nfl/teams`, `/team/{team_key}/roster;week={week}`, and `/league/{league_key}/settings`. Confirm application access and current responses; do not use player eligibility as evidence of the selected starting slot. |
| [Yahoo developer access](https://sports.yahoo.com/developer/) | Yahoo describes application submission, review, and approval for Fantasy API access. | Confirm access early; successful documentation retrieval is not an API approval. |
| [NFL developer portal](https://developer.nfl.com/get-started/overview) | Browser navigation reaches NFL's sign-on page. Public endpoint contracts and project access were not verified. | Direct NFL API access is an unresolved dependency. Need schedule, game status, possession/field position, scoring plays, involved player IDs, timestamps, and correction semantics. Do not label a third-party service as the NFL's official developer API. |
| [Fire OS notifications](https://developer.amazon.com/docs/fire-tv/notifications.html) | Amazon documents heads-up notifications outside the app UI; page last updated in 2020. | Prototype a background event reaching a visible notification while another viewing app plays on the exact target device/OS. Documentation alone is not evidence of current device behavior. |
| [Alexa Video Skills Kit](https://www.developer.amazon.com/docs/video-skills-fire-tv-apps/integrate-alexa-client-library) | Participating apps receive Alexa video directives through the client integration. | Verify the actual handoff to a supported viewing provider; receiving commands in our app does not imply authority to issue arbitrary cross-app Alexa commands. Proactive custom speech also needs a separate proof. |

Proposed data flow: Yahoo lineup/league context + NFL game events + customer settings/viewing availability -> player matching and event filtering -> Fire TV alert -> customer-selected viewing action or supported Alexa route.

Do not assume a paid sports-data contract is necessary. Investigate direct NFL access and free/low-cost candidates, including the owner's ESPN suggestion, against required event coverage, latency, stability, and permitted use before selecting a source. No provider or price has been selected.

### App launch and game/channel routing research — October 10, 2026

**Owner clarification:** the desired capability is ordinary app opening and supported game/channel deep linking, not unrestricted control of other apps. Investigate Apple and Roku's approach, use Amazon's existing capabilities, and identify any routing functionality we can implement ourselves. Messaging remains excluded.

| Platform / source | Documented mechanism | Implication |
|---|---|---|
| [Apple Video Partner Program](https://developer.apple.com/programs/video-partner/) and [Universal Links](https://developer.apple.com/documentation/Xcode/allowing-apps-and-websites-to-link-to-your-content) | Video partners integrate Live Tune-In, Universal Search, Siri, and the TV app. Universal links can send users directly to content in a receiving app, including on tvOS. | Apple's integrated discovery/tuning experience relies on provider integration; use this as an architectural reference, not evidence that all Apple partner data is public to other developers. |
| [Roku deep linking](https://developer.roku.com/dev/docs/implementing-deep-linking) | Launch requests carry a provider-defined `contentId` and `mediaType`; `sportsevent` identifies a live sports event and `livefeed` a linear stream. The receiving app validates and handles the target. | A game-aware entry point can launch the provider at the intended content. Provider content IDs must be resolved; Roku's ECP testing interface is not being selected as a production dependency. |
| [Amazon Vega app-to-app deep linking](https://developer.amazon.com/docs/vega/0.22/deep-links-vega-apps) and [Linking API](https://www.developer.amazon.com/docs/react-native-vega/0.72/linking) | Amazon explicitly documents app-to-app links to movies, shows, or live channels based on a contract between the apps. `Linking.canOpenURL` and `Linking.openURL` check/launch supported URIs. The cited guide is version 0.22 open-beta documentation; confirm the selected SDK's current contract during the spike. | Amazon has a documented cross-app launch mechanism. Test a real provider link on the target OS instead of treating app opening as a missing platform capability. A URI handler being present does not prove entitlement or successful playback. |
| [Fire TV launcher integration](https://developer.amazon.com/docs/catalog/integrate-with-launcher.html) and [linear-app playback tests](https://www.developer.amazon.com/docs/fire-tv/test-cases-for-linear-apps.html) | Providers integrate playback intents and channel/event deep links. Amazon's tests expect direct playback without first showing the provider home screen. | Fire TV already supports direct content/channel launches through integrated providers. Determine which provider-supported entry points our companion can invoke. |
| [DIRECTV's Fire TV integration](https://www.directv.com/insider/news/fire-tv-launches-new-linear-live-tv-experience-for-directv-stream-subscribers/) | DIRECTV documents Fire TV Live/Guide integration and the voice example “Alexa, tune to ABC in DIRECTV” (published April 18, 2023). | Concrete provider evidence for Alexa channel tuning. Current behavior and any app-triggered Alexa handoff still require testing; this is not a verified public API for submitting arbitrary Alexa utterances. |

**Candidate implementation:** add a provider routing component that maps an NFL event to its regional broadcaster and provider-specific event/channel identifier, chooses among customer-configured available services, and supplies a supported launch URI/intent for the alert's Watch action. Direct app links can serve the button flow; Alexa remains an additional voice route where supported. A resolver is our proposed implementation, not a claim that Amazon lacks one internally.

Keep routing outcomes explicit: specific game/channel opened; provider search/details opened; app home opened; app absent; access unknown; or playback denied. App launch alone does not satisfy the specific-game acceptance condition. Avoid inventing provider URI formats or promising channel access from an installed app alone.

Planned early-development spike: select one real provider and target Fire TV, obtain its supported game/channel link contract and identifier source, then demonstrate alert -> customer action -> correct channel/game. Record app opening and direct tuning separately. If an essential provider contract is unavailable, capture the exact missing interface as an Amazon/provider integration proposal; no external proposal or feedback submission has been authorized.

### Development setup, integration spikes, and validation

**Owner clarification, October 10, 2026:** development-tool setup and the working alert-to-game prototype/test are part of development. Carry them into the implementation plan as early setup, integration, and validation work. Do not require a working prototype or preinstalled tools to approve the concept or begin planning. Record technical uncertainties and access/device dependencies without treating unimplemented behavior as a failed readiness gate.

- [ ] Select a Fire TV device and Fire OS/Vega version; prove background notification delivery while a separate viewing app plays.
- [ ] Read an authorized Yahoo lineup and league settings; distinguish starters, bench, and unavailable/unknown slots.
- [ ] Establish usable NFL event-feed access and measure update timing; verify field position, player scoring, corrections, and identifier matching.
- [ ] Determine what installed-app, subscription, and current-viewing detection is actually exposed; preserve customer configuration when detection is unavailable.
- [ ] Demonstrate one supported event-to-game viewing handoff, including Alexa behavior where available; distinguish app launch from reaching the correct game.
- [ ] Verify customer controls, spoiler timing, duplicate suppression, and behavior when data or viewing access is unavailable.
- [ ] Reconcile the five retained experience items and the owner-added right-side lineup panel into the build plan; do not silently shrink the concept because one integration is difficult.

### Scribe and every-agent developer-feedback contract — owner direction October 10, 2026

The Scribe is responsible for continuous, evidence-backed developer-experience capture and submission-feedback preparation for this project. This is a project-specific extension requested by William, not a modification of the shared Scribe skill or role routing. It supplements the Scribe's decision/authority history responsibilities without granting engineering approval, independent assurance, or publication authority.

**Every participating role contributes:** Orchestrator, Coordinator, implementers, light implementers, integration, reviewers, assurance/test roles, research/setup agents, and the Scribe. Capture both difficulties and successful/easy experiences while they occur, not retrospectively at submission time. This applies to every tool, API, SDK, device, simulator, and platform actually used.

**Required in every future dispatch packet and return:** include a `developer_feedback` section containing observation IDs/evidence or an explicit statement that no new observations occurred. Missing feedback is incomplete reporting, not evidence of a friction-free experience. A return with no new observations should name the tools exercised so the Scribe can track coverage. Do not fabricate positive or negative experiences to fill the section.

Each observation records:

- ID, timestamp, reporting role, relevant task/packet, tool/API/SDK, version, and device/OS where applicable.
- Task attempted and purpose; onboarding/setup, documentation/discoverability, integration, testing/debugging, reliability/performance, accessibility or ease of use, as applicable.
- Steps and prerequisites, expected result, actual result, and a redacted reproducible evidence reference.
- What worked well and why, as well as what was confusing, slow, missing, or unsuccessful.
- Impact/severity; measured time/retries when actually measured. Unknown durations remain unknown.
- Workaround and result, unresolved dependency or proposed improvement, and whether the agent would use the technology again with a reason based on experience.
- Classification: positive experience, documentation gap, expected prerequisite, configuration/environment/harness issue, suspected product defect, or verified product defect. A failed request alone is not a vendor bug.

**Scribe workflow:** ingest observations at each return, preserve reporter attribution and underlying evidence, deduplicate recurring friction without erasing affected versions, track resolution and unresolved gaps, and maintain a per-tool coverage ledger. Orchestrators and Coordinators carry forward observations and ensure the Scribe receives them at each wave boundary. Missing observations return to the reporting agent for completion; the Scribe does not invent measurements or silently turn uncertainty into a pass.

**Feedback deliverables:** the future Lifecycle must allocate a private running observation log, a per-tool summary covering purpose, onboarding, what worked, what needs work, and willingness to reuse, plus a sanitized submission-ready friction log containing the task, reproduction steps, expected/actual behavior, severity, workaround, and actionable suggestion. Record exact paths in that Lifecycle when created; no Lifecycle or agent lineup has yet been established by this issue update. Preserve this contract in the approved plan and all dispatch templates. Explicitly account for reporting overhead using lightweight entries; do not require repetitive essays.

Review submitted feedback against source evidence. Separate customer app messaging (excluded) from developer-experience documentation (required). Keep credentials, personal account details, private paths, unrelated repository data, and proprietary agent prompts/routes out of submission materials. Sending feedback to Amazon/Yahoo/NFL or submitting the hackathon entry remains an owner-authorized external action; the Scribe prepares the material but does not send it automatically.

**Prospective completion conditions:**

- [ ] Every participating agent packet/return includes the feedback obligation.
- [ ] Scribe coverage includes every tool/API/SDK actually used, including positive observations and explicit evidence gaps.
- [ ] Each reported friction item is grounded in observed behavior, classified, deduplicated, and accompanied by an actionable suggestion where appropriate.
- [ ] Final product-feedback and friction-log drafts are sanitized and checked against the current [official rules](https://amazonappdev2026.devpost.com/rules).

### Readiness checks and initial observations — October 10, 2026

| Check | Current evidence / status |
|---|---|
| Devpost registration | **CONFIRMED:** the signed-in event page explicitly displays “You're registered for this hackathon.” Read-only browser check; no registration action or new agreement was submitted. |
| Submission draft | **NOT STARTED:** [My projects](https://devpost.com/submit-to/30992-build-ship-shape-amazon-developer-hackathon/manage/submissions) displays the empty state inviting a new project. |
| Age/location eligibility | **CONFIRMED FROM OWNER:** adult U.S. resident. Exact birth details are unnecessary for this issue. |
| Employer eligibility check | The owner corrected the earlier Amazon-employment statement to AMD. Do not use the retracted statement as a disqualification. This does not trigger the sponsor-employee exclusion. Other conflict/ownership clauses remain applicable; registration itself is not an organizer eligibility ruling. |
| Target device/provider | Owner reports a roughly 2018 Fire TV that still needs to be located; exact model, OS and first viewing provider remain unconfirmed. No purchase selected or made. |
| Local tooling | **PLANNED DEVELOPMENT SETUP:** `adb`, `vega`, Android `emulator`, `sdkmanager`, and `avdmanager` were not found on PATH. Linux x86_64 host has accessible KVM and QEMU. Tool installation/configuration belongs in development; its current absence does not block concept approval or planning. |
| Simulator route | [Vega SDK 0.24 installation documentation](https://developer.amazon.com/docs/vega/0.24/install-vega-sdk) provides a virtual device and supports specified Ubuntu x86_64 versions. OS release/dependency verification and SDK setup remain outstanding. A Vega simulator does not establish behavior on the owner's older Fire OS device or prove playback in third-party services. |
| Yahoo access | **UNVERIFIED:** no approved application or successful authenticated API call has been established. The current [access form](https://sports.yahoo.com/developer/access/) requires review and describes currently read-only access. The public browser session was signed out. Application/account approval and user OAuth authorization are separate steps. |
| NFL access | **UNVERIFIED:** the earlier developer-portal check reached NFL sign-on. No authenticated endpoint or event-feed access has been established. |
| Alert-to-game handoff | **PLANNED DEVELOPMENT SPIKE:** implement and exercise the notification-to-provider game/channel route during development. The test has not run; this is expected at concept stage and is not a prerequisite for planning. |

Initial feedback observations for the future Scribe:

- **DX-001 — Positive documentation experience:** [Amazon Builder Tools capabilities](https://developer.amazon.com/docs/adbt/capabilities) groups capabilities by OS and gives concrete prompts. This made it straightforward to identify launcher, Live TV, focus, and personalization guidance. No runtime use or measured onboarding time is claimed.
- **DX-002 — Yahoo documentation inconsistency:** the [API guide](https://sports.yahoo.com/developer/docs/) describes selecting Read or Read/Write access. The [current application form](https://sports.yahoo.com/developer/access/) says write access is unavailable, while lower helper text still invites exceptional read/write details. Observed directly in the browser. Impact: avoidable uncertainty about current access options; it does not block this read-only use case. Workaround: follow current read-only onboarding. Suggestion: align the guide and form's access language. This is a documentation observation, not a filed defect.
- **DX-003 — Expected access prerequisite:** NFL developer documentation requires sign-in. Impact: endpoint and access verification could not proceed anonymously. No product failure is established. Next step is approved account access or selection of another usable feed.
- **DX-004 — Retrieval-tool limitation:** web retrieval returned Yahoo HTTP 429 responses while the same documentation opened in the signed-in-browser environment. Workaround: browser-based reading. Root cause is unverified; keep this as internal research-tool context rather than attributing a confirmed Yahoo product defect.

### Judging alignment and proposed demonstration strategy — October 10, 2026

Concept fit: Fire TV sports viewing, personalized to the customer's fantasy lineup and available services. The retained scope is profiles, monitoring, alerts, supported viewing handoff, customer controls, and the owner-added right-side fantasy lineup panel alongside unobscured playback; messaging remains excluded. The following is a proposed implementation/demo emphasis, not proof of working features, a guarantee of winning, or an approved technical design.

[Official rules, Sections 4 and 6](https://amazonappdev2026.devpost.com/rules): Stage One assesses viability/track fit. Stage Two equally weights Tech Implementation, Design, Potential Impact, and Quality of the Idea. Tech Implementation is the first tiebreaker. Friction-log bonus is up to 10%, assessed by the organizers, not guaranteed.

| Criterion | Feature emphasis | Evidence to produce during development |
|---|---|---|
| Tech Implementation | Yahoo starting-lineup integration, live-event filtering, Fire TV notification, and correct provider game/channel launch. | Demonstrate a complete actual flow and exercise lineup changes, duplicates/corrections, stale data, and unavailable routes. Use source-event timestamps for freshness. Hardware performance benchmarking is excluded by the owner; any development measurements must be clearly labeled by environment. |
| Design | Legible TV notification, deliberate remote focus, clear Watch/dismiss behavior, and customer-configurable announcements, frequency, spoiler delay, provider preference, and switching confirmation. | Demonstrate the flow with the remote on the selected target and show that one preference change alters behavior. Voice functionality is shown only if implemented and verified. |
| Potential Impact | Help fantasy viewers notice relevant action and reach it through a service they already use. | A concrete before/after user story and a functioning viewing handoff. Do not invent usage, retention, customer, or latency figures. |
| Quality of the Idea | Connect personal roster relevance, timely game context, and available viewing destinations in one interaction. | Show why this event matters to this customer and why the suggested destination is appropriate. Existing generic sports alerts are the baseline; differentiation is the verified personalized handoff and customer control. |

**Proposed standout moment:** while another viewing app is playing, a brief notification identifies an opportunity relevant to a selected fantasy starter. The customer selects Watch and the correct game/channel opens in their configured service. Optional verified voice/AI context explains its relevance. Scoring detection and player identity remain grounded in data, rather than inferred by an LLM. No automatic channel switch is implied unless explicitly configured and supported.

**Proposed video storyboard (2 minutes 45 seconds):**

- 0:00–0:15: State the customer problem and show the personalized alert immediately.
- 0:15–0:35: Show the connected Yahoo lineup and preferred viewing service, with account details protected.
- 0:35–1:20: Show the complete alert -> customer action -> correct game/channel handoff on Fire TV hardware or the allowed simulator. Demonstrate actual app behavior rather than animated screens.
- 1:20–1:45: Show implemented Alexa/voice behavior and grounded commentary if available. If unavailable, show another real supported interaction and state the limitation in submission materials; do not silently treat intended voice scope as completed.
- 1:45–2:10: Show customer controls taking effect, including suppression/spoiler preference and provider choice as implemented.
- 2:10–2:30: Show one concise reliability behavior, such as clearly unavailable viewing access or corrected/stale data, and any genuinely measured result.
- 2:30–2:45: Explain the fantasy-personalization differentiator and summarize the implemented Amazon integration.

Use only authorized footage/assets. If a past-event replay or simulated input is used for repeatability, label it clearly; do not represent it as live feed access. The application's notification and navigation behavior must still run. All retained scope must remain accounted for even when the video emphasizes only the clearest flow.

**Code priorities for the standout experience:** fast and dependable foreground handoff; accurate mapping among Yahoo players, game events and provider identifiers; low-noise notifications; coherent remote/voice interaction; honest availability and failure behavior. Design for low overhead and bounded memory. Hardware performance verification is excluded by the owner; do not claim measured physical-device latency or RAM results. Scribe feedback covers all tools and includes ease of use, successful paths, observed friction, and actionable suggestions.

**Eligibility/submission status:** registration and adult U.S. residence are confirmed. The owner's corrected employer is AMD, not Amazon; no automatic sponsor-employee exclusion is established by that fact. Full eligibility still depends on the event's other affiliation/conflict clauses and ownership/third-party-rights conditions; no employment/IP agreement has been reviewed and no organizer determination is claimed. Product access, device/OS selection, setup, implementation, and handoff tests remain work to carry into development. Submission materials must include the repository, setup instructions, public short video, description, required product feedback, and judge access. Keep the existing deadline and owner publication boundary.

### Lightweight device design and performance scope — October 10, 2026

**Owner direction:** consider Fire TV processor, graphics/rendering hardware, and RAM when designing the app, but do not perform hardware performance verification/benchmarking. Keep the implementation lightweight to reduce lag and RAM consumption. Functional integration demonstrations remain separate from performance measurement. Do not introduce a hardware benchmark gate, claim measured device performance, or advertise zero lag. This supersedes earlier suggestions to obtain physical-device latency/memory measurements for judging.

**Documented reference tiers, not a certified support matrix:**

| Device | OS | CPU / GPU | System RAM | Proposed consideration |
|---|---|---|---|---|
| Fire TV Stick 4K, 1st Gen (2018) | Fire OS 6 / Android API 25 | Quad-core 1.7 GHz; IMG GE8300 | 1.5 GB | Older-device design reference. Owner's exact 2018 model is still unknown; it must not be assumed to be this model. Backward support depends on APIs selected for the functional integrations. |
| Fire TV Stick 4K Max, 2nd Gen (2023) | Fire OS 8 / Android API 30 | 4x Cortex-A55 up to 2.0 GHz; GE9215 up to 850 MHz | 2 GB | Recommended primary Fire OS compatibility target, not an owner-approved purchase or final platform selection. |
| Fire TV Stick 4K Select (2025) | Vega OS 1.1 | 4x Cortex-A55 up to 1.7 GHz; G310v2 up to 500 MHz | 1 GB | Separate Vega implementation/compatibility decision; do not assume Android APK compatibility. |
| Fire TV Stick 4K, 3rd Gen (2026) | Vega OS 2.0 | 4x Cortex-A55 up to 1.7 GHz; ARM G310 V2 up to 500 MHz | 1 GB | Newer low-memory platform reference; newer model year does not imply more RAM. |

Source: [Amazon streaming-device specifications](https://developer.amazon.com/docs/device-specs/device-specifications-fire-tv-streaming-media-player.html), checked October 10, 2026. RAM is shared system capacity, not memory allocated to our app. Clock rates alone are not cross-architecture performance rankings. Final OS/device scope must follow the functional notification, lineup-panel and provider-link integration decisions; no dual-platform implementation is silently added.

**Proposed engineering guidance for the plan:**

- Keep API aggregation, full-game monitoring, cross-provider matching and AI generation on the backend; send small relevant updates to the TV. Shared event ingestion avoids repeatedly fetching the same games for each viewer.
- Render a compact 2D lineup/alert interface. Update changed rows and values, coalesce bursts, and avoid whole-screen rerenders, continuous tickers, particle effects, blur-heavy layers, and large animated imagery.
- Bound event queues, retained history, images and caches. Decode images at their displayed size; release hidden-screen resources and dispose subscriptions/timers when no longer needed.
- Keep network work, parsing and expensive computation off the rendering/main thread. Suspend unnecessary updates outside enabled viewing periods and avoid tight polling. Background delivery must use supported OS mechanisms rather than assuming the UI process stays alive indefinitely.
- Preserve hardware video decoding and supported compositor/player paths wherever playback integration permits. Do not copy video frames into the app or decode/re-encode broadcasts to draw the fantasy panel. The supported way to compose the panel beside third-party playback remains a functional integration question.
- Use lightweight platform components and only dependencies justified by the workflow; framework selection remains part of design. Do not assume a particular framework automatically satisfies the memory goal.
- [Amazon's Fire OS guidance](https://developer.amazon.com/docs/app-testing/app-performance-scripts.html) recommends restricting background app RAM to 100 MB. Treat this as a Fire OS design reference and aim for headroom, not a measured result or an inferred Vega/foreground limit. No arbitrary foreground memory or frame-rate guarantee is established here.

**Evidence boundary:** assess implementation structure and, where useful, development/simulator profiler observations without presenting them as physical-device results. Scribe entries distinguish expected efficiency from observed development behavior. Keep functional notification, simultaneous panel/video and game/channel launch evidence in the development plan; excluding hardware performance verification does not establish those capabilities automatically.

### Repository — created October 10, 2026

- Working repository name: `amazon-fantasy-companion` (not a final public product/Devpost name).
- GitHub: https://github.com/alphazede/amazon-fantasy-companion
- Visibility: **private**, verified after creation.
- Local checkout: `$HOME/alphazede/Hackathons/amazon-fantasy-companion`
- Initial state: empty repository; no implementation, dependencies, publication, or submission added. The concept, scope decisions, source research, and Scribe obligations remain recorded in this issue for the subsequent plan.

### Join and scope

- [ ] Confirm eligibility, participation terms, project ownership, and third-party rights; choose individual/team entry and representative if needed.
- [x] Confirm Devpost registration (signed-in browser evidence, October 10, 2026).
- [ ] Create the project draft and record its URL; currently no project exists.
- [ ] Set up the selected track's developer account and environment using the resources page; keep credentials out of this issue.
- AWS credit requests are no longer available: the official rules report that codes ran out on October 7, 2026. Do not plan around the earlier October 21 request cutoff.
- [x] Select the Fire TV concept and record its scope (owner decision, October 10, 2026).
- [ ] Record a bounded build plan and deadline buffer; decide any additional track or mini challenge.

### Build and verify

- [ ] Prove the selected track's integration and required device/data behavior with a working spike.
- [ ] Complete and verify the primary workflow, error handling, and fresh setup.
- [ ] Collect product feedback continuously through every agent and the Scribe, following the owner-required contract above. Friction-log preparation is mandatory for this project even though optional under the event rules; the advertised bonus is up to 10%, not guaranteed.

## Acceptance

- [ ] Working demo and code satisfy the selected track; actual required technology is used where applicable, rather than merely described.
- [ ] GitHub repository includes all source/assets and setup instructions. Choose public open source with a license, or a dedicated private submission repository shared with the reviewers specified in the rules. Do not share HQ wholesale.
- [ ] For private submission, verify reviewer access and invitation timing; invitations expire after seven days.
- [ ] Public English YouTube/Vimeo video under three minutes demonstrates the actual track experience.
- [ ] Submission includes description, selected track/mini challenges, feedback on every tool/API/SDK used, and explanation of significant in-window changes for an existing project.
- [ ] If selected, AWS Builder integrations and Open Source contribution URLs/username/description satisfy the extra fields.
- [ ] Judge access remains available through November 20, 2026.
- [ ] Owner authorizes the exact external sharing/publication and final submission before those actions.
- [ ] Submit before the deadline and record the final Devpost URL and confirmation. Leave closure for William.). Extract only constraints relevant to the repository map (target OS candidates, device tiers, deadline 2026-10-23 12:00 PDT, excluded scope, Scribe developer_feedback contract). Do not plan.

Return (under 500 words): status (WORKSPACE_READY | NEEDS_EVIDENCE | BLOCKED), written paths, map freshness, evidence, blockers, gaps (Systems Modeler activation), next planning stage.

developer_feedback: observations on any tool/API/SDK/doc touched (positive or friction), or "no new observations" naming tools exercised.
