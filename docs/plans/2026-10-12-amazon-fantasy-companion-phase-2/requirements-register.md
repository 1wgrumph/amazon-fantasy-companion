---
type: product-requirements-register
title: Amazon Fantasy Companion Product Requirements Register
okf_status: draft
tags: [requirements, planning, afc, spec-track]
---

# Amazon Fantasy Companion Product Requirements Register

Lifecycle AFC-ST-2026-10-12, step ST-2. Register of record per DEC-AFC-SD-027
(2026-10-12): Markdown in this repository, not bound to the Requirements System host.
66 product requirements (AFC-PR-001..066), gated in
`specialists/re-st2-receipt.md` (65/65 PASS), transcribed in ST-2b, and updated by the
DEC-AFC-SD-035 delta (2026-10-12): P1/P2/P3 decided in place (PR-014/023/040); Q3 floor
in PR-045; Q4 full-screen panel fallback in PR-047/048 with PR-049..051 withdrawn
(UIDs retained, never renumbered); Q5 order and local-broadcast behavior in PR-029;
Q9 recorded below; D1 closed by SD-035 delta 2 with PR-065 presets and PR-066 selection. See `specialists/re-sd035-receipt.md`. Phase 2 design delta (2026-10-12): PR-047 reallocates PANEL, PLAYER to PANEL, SHELL and PLAYER is retired (no companion player); see `specialists/re-p2-delta-receipt.md`.

Common fields: STATUS Draft, except AFC-PR-049..051 Withdrawn by DEC-AFC-SD-035 (2026-10-12); OWNER Amazon Fantasy Companion specification;
VALIDATION_METHOD owner review at ST-5; EXPECTED_RESULT pending Phase 2 verification;
ACTUAL_RESULT not executed (planning register); ANOMALY none recorded;
CORRECTIVE_ACTION none (revise through ST-2 correction rounds); WAIVER none;
CLOSURE open pending ST-5 owner review. VERIFICATION_CASE VCASE-AFC-PR-NNN per row.
Assumptions and constraints per row are carried in the verification criteria or the
rationale column context; full assumption/constraint text remains in the ST-2 receipt.

## Coverage — issue #1 retained items and panel

| Source | UIDs |
|---|---|
| Item 1 profile | 001, 002, 003, 004, 005, 006, 007, 038 |
| Item 2 monitor | 008, 009, 010, 011, 012, 013, 064 |
| Item 3 alerts | 014, 015, 016, 017, 018, 019, 020, 021, 022, 023, 024, 025, 026, 027, 028 |
| Item 4 watch | 029, 030, 031, 032, 033, 034, 035, 036 |
| Item 6 controls + linking | 002, 009, 010, 016, 017, 018, 019, 020, 021, 022, 023, 034, 035, 037, 038 |
| Panel | 039, 040, 041, 042, 043, 044, 045, 046, 047, 048, 049, 050, 051, 065 (049, 050, 051 withdrawn by SD-035; UIDs retained) |
| Platform/hosting/scope/LW | 052, 053, 054, 055, 056, 057, 058, 059, 060, 061, 062, 063 |

## Coverage — customer controls (every #1 item 6 setting + alert/panel settings)

| Control | UID | Control | UID |
|---|---|---|---|
| Fantasy selections | 002 | Notification presentation | 021 |
| Alert types | 016 | Voice announcements | 022 |
| Frequency | 017 | Excitement level | 023 |
| Quiet hours / game-day periods | 018, 019 (monitor: 009) | Provider preference | 034 |
| Spoiler delay | 020 | Switching confirmation | 035 |
| Detection/personalization opt-in | 037 (viewing: 010) | Panel show/hide | 042 |
| Team/league selection | 042 | Device-code linking | 038 |

## Coverage — conditionals C1..C9

| ID | Type / honoring |
|---|---|
| C1 enforced_rule | 052 platform target; assumptions (model unconfirmed); owner-return in constraints |
| C2 expected_outcome | 013 replay substitution; 012 ingest; evidence note |
| C3 enforced_rule | 012 constraints (owner terms flag at submission) |
| C4 enforced_rule | 054 Free-tier-only hosting |
| C5 expected_outcome | 047 full-screen panel fallback; 048 provider routing under fallback; 041 constraints |
| C6 expected_outcome | 006 manual entry at T_yahoo; 007 single source; 065 manual scoring |
| C7 enforced_rule | 056 path hygiene |
| C8 enforced_rule | 022 voice announcements; 036 Alexa tuning |
| C9 enforced_rule | 055 server-side secrets; owner-action constraints on 006/038/054 |

## ST-3a allocation elements

SHELL MainActivity.kt; BUILD build.gradle.kts; MANIFEST AndroidManifest.xml; PROFILE ProfileSettingsScreen.kt;
DETECTOR AppDetector.kt; ALERTSVC AlertService.kt; NOTIFIER AlertNotifier.kt; LAUNCHER WatchLauncher.kt;
PANEL LineupPanel.kt; IAC backend/template.yaml; AUTH backend/src/device_auth/;
API backend/src/api/; INGEST backend/src/feed_ingest/; REPLAY replay.py + fixtures/replay/;
LINEUP backend/src/lineup/; MATCHER backend/src/matcher/; POLICY backend/src/alert_policy/;
RESOLVER backend/src/provider_resolver/; PANELSVC backend/src/panel/; SECRET SSM SecureString;
STORE DynamoDB profile/event tables. PLAYER retired by DEC-AFC-SD-035 (Phase 2 design: no companion player).
Every active UID below allocates to ≥1 active element; every active element
receives ≥1 UID. Withdrawn UIDs 049..051 carry no live allocation (historical PLAYER text retained).

## Register

| UID | Statement | Rationale | Verification method | Allocation | Sources |
|---|---|---|---|---|---|
| AFC-PR-001 | The backend shall retrieve the customer's leagues, teams, rosters by week, and league scoring settings through a read-only Yahoo Fantasy OAuth connection. | Yahoo is the lineup/league context source; read-only OAuth bounds access to need. | Test, backend, AWS Free-plan deployment (SD-005). Positive: roster distinguishes active slots from bench and returns scoring settings. Negative: no write-scope call is attempted and no player eligibility value is used as a starting-slot fact. VCASE-AFC-PR-001. | LINEUP | #1 item 1; #1 Yahoo rows; SD-007 |
| AFC-PR-002 | The TV app shall persist the customer's selected leagues, teams, starters or specific players, and favorite teams. | Selections drive monitoring, alerts, and panel content; loss across restart breaks trust. | Demonstration, system, real stick (SD-001) + backend. Positive: select, restart, selections retained. Negative: no selection silently dropped. VCASE-AFC-PR-002. | PROFILE, API, STORE | #1 items 1, 6 (fantasy selections) |
| AFC-PR-003 | The TV app shall report each supported installed viewing app as installed through platform-permitted detection. | Provider choice needs true installed-app facts without claiming subscription. | Demonstration, tv-app, real stick (SD-001). Positive: each installed supported app reported installed. Negative: absent app never reported installed. VCASE-AFC-PR-003. | DETECTOR | #1 item 1; SD-003 |
| AFC-PR-004 | The backend shall mark each game's viewing access as verified only from supported provider integration or explicit customer confirmation. | Honest availability is a judging emphasis; unverified access must never read as verified. | Test, backend, AWS deployment. Positive: verified marking carries basis integration or confirmation. Negative: installed-app fact alone never yields verified. VCASE-AFC-PR-004. | RESOLVER, API | #1 items 1, 4 |
| AFC-PR-005 | The TV app shall apply the customer's review and override to all detected profile information and retained local-market information. | Detection is fallible; the customer is the final authority on their profile. | Demonstration, tv-app, real stick (SD-001). Positive: override of a detected app and of local market persists across restart and feed refresh. Negative: refresh never silently discards an override. VCASE-AFC-PR-005. | PROFILE, STORE | #1 item 1 |
| AFC-PR-006 | When Yahoo approval is absent at T_yahoo (2026-10-16T19:00:00Z), the backend shall accept labeled manual lineup entry built from ESPN rosters as the active lineup source. | Schedule-proof lineup context without misrepresenting manual data as Yahoo data. | Test, backend, AWS deployment. Positive: at/after T_yahoo without approval, manual entry activates and is labeled manual. Negative: manual values never presented as Yahoo values. VCASE-AFC-PR-006. | LINEUP | #1 item 1; SD-007; C6 |
| AFC-PR-007 | The backend shall hold exactly one active lineup source from the Yahoo read-only connection or labeled manual entry. | Two simultaneous sources would fork lineup truth across alerts and panel. | Test, backend, AWS deployment. Positive: source query returns exactly one active source. Negative: switchover never leaves zero or two active. VCASE-AFC-PR-007. | LINEUP | #1 item 1; SD-007 |
| AFC-PR-008 | The backend shall monitor live NFL game events only for profile-relevant games during customer-enabled viewing periods. | Relevance and customer control bound noise, cost, and backend load. | Test, backend, AWS deployment. Positive: game with a selected player or favorite team inside an enabled period is monitored. Negative: irrelevant game, or any game in quiet hours, is not monitored. VCASE-AFC-PR-008. | INGEST, POLICY | #1 item 2 |
| AFC-PR-009 | The TV app shall record the customer's selected schedule and game-day mode as the monitoring enablement. | The customer decides when the companion watches. | Demonstration, system, real stick (SD-001) + backend. Positive: mode change alters the monitored game set per PR-008. Negative: no monitoring outside the recorded enablement. VCASE-AFC-PR-009. | PROFILE, POLICY | #1 items 2, 6 (quiet hours/game-day periods) |
| AFC-PR-010 | The TV app shall apply current-viewing-context detection only through supported mechanisms while the customer enables that detection. | Viewing-context sensing is sensitive and platform-limited; both bounds apply. | Demonstration, tv-app, real stick (SD-001). Positive: enabled detection uses a documented supported mechanism. Negative: disabled detection yields no viewing-context reads (decisions label profile-assumption per PR-011). VCASE-AFC-PR-010. | DETECTOR, PROFILE | #1 items 2, 6 (detection use) |
| AFC-PR-011 | The backend shall label each monitoring decision with its observed-playback or profile-assumption basis. | Observed state and assumption must never be confused downstream. | Test, backend, AWS deployment. Positive: every decision record carries exactly one basis label. Negative: no decision ships unlabeled. VCASE-AFC-PR-011. | POLICY | #1 item 2 |
| AFC-PR-012 | The backend shall ingest scores, field position, possession, involved player identifiers, timestamps, and scoring corrections from ESPN's unofficial public JSON. | Owner-selected live feed; corrections and timestamps ground freshness and panel truth. | Test, backend, AWS deployment. Positive: each listed field lands in the event cache. Negative: schema-invalid response handled per PR-064, never partially stored. VCASE-AFC-PR-012. | INGEST | #1 item 2; #1 feed requirements; SD-004 |
| AFC-PR-013 | When the ESPN endpoint is unavailable or its contract changes, the backend shall substitute labeled replay fixtures for live events on every affected value. | Repeatability and outage survival without ever faking live access. | Test, backend, AWS deployment with fixtures. Positive: outage run marks every affected value replay. Negative: no substituted value presented as live. VCASE-AFC-PR-013. | REPLAY, INGEST | #1 judging alignment (label replays); C2 |
| AFC-PR-014 | The backend shall emit alerts for red-zone opportunities, player scores, and close games matching the customer's fantasy selections and alert-type settings. | The core personalized value: this event matters to this customer. | Test, backend, AWS deployment. Positive: each of the three types fires for a matching selection. Negative: non-matching event, or matching event of a disabled type, emits nothing; red zone means inside the 20-yard line; close_game_margin (DEC-AFC-SD-035, P1) is within 8 points in the 4th quarter or overtime. VCASE-AFC-PR-014. Alert text claims no player-level inference per PR-028. | POLICY, MATCHER | #1 item 3; SD-035 (P1) |
| AFC-PR-015 | While heads-up presentation is selected, the TV app shall present each alert as a heads-up notification with Watch and Dismiss actions during third-party viewing-app playback. | The standout moment: brief alert over playback with a direct Watch path. | Demonstration, system, real stick (SD-001); evidence under evidence/visual/ (SD-024). Positive: provider playback continues while the alert shows Watch/Dismiss. Negative: no companion-app foregrounding, and no heads-up while panel-only presentation is selected. VCASE-AFC-PR-015. | NOTIFIER, ALERTSVC, MANIFEST | #1 item 3; SD-001 |
| AFC-PR-016 | The backend shall emit alerts only for customer-enabled alert types. | Per-type control is the primary noise control. | Test, system, backend + settings UI. Positive: enabled type fires on matching event. Negative: disabled type fires on nothing. VCASE-AFC-PR-016. | PROFILE, POLICY | #1 items 3, 6 (alert types) |
| AFC-PR-017 | The backend shall emit no more alerts than the customer's frequency setting permits. | Frequency caps keep the companion welcome during simultaneous Sunday games. | Test, system, backend + settings UI. Positive: restrictive setting yields fewer alerts than permissive for an identical event stream. Negative: no alert beyond the setting on any run. VCASE-AFC-PR-017. | PROFILE, POLICY | #1 items 3, 6 (frequency) |
| AFC-PR-018 | The backend shall suppress alerts during the customer's quiet hours. | Silence when the customer demands silence. | Test, system, backend + settings UI. Positive: triggering event inside quiet hours emits nothing. Negative: no quiet-hours alert on any run. VCASE-AFC-PR-018. | PROFILE, POLICY | #1 items 3, 6 (quiet hours/game-day periods) |
| AFC-PR-019 | The backend shall emit alerts only during the customer's game-day periods. | Alerts belong to game time, not all time. | Test, system, backend + settings UI. Positive: triggering event inside a game-day period emits (subject to other filters). Negative: nothing emits outside game-day periods. VCASE-AFC-PR-019. | PROFILE, POLICY | #1 items 3, 6 (quiet hours/game-day periods) |
| AFC-PR-020 | The backend shall delay each alert by the customer's spoiler delay. | Customers behind live play must not be spoiled by their own companion. | Test, backend, AWS deployment. Positive: delivery timestamp minus event timestamp is at least the set delay. Negative: no alert delivered early. VCASE-AFC-PR-020. | PROFILE, POLICY | #1 items 3, 6 (spoiler delay) |
| AFC-PR-021 | The TV app shall render each alert in the customer's chosen notification presentation. | Presentation choice balances intrusiveness and awareness per customer. | Demonstration, tv-app, real stick (SD-001). Positive: each offered presentation renders as chosen. Negative: panel-only choice shows no heads-up. VCASE-AFC-PR-021. | PROFILE, NOTIFIER | #1 items 3, 6 (notification presentation) |
| AFC-PR-022 | The TV app shall announce alerts by voice only while the customer enables voice announcements over an implemented and verified voice route. | Voice is intrusive and platform-conditional; both gates apply. | Demonstration, tv-app, real stick (SD-001). Positive: enabled announcements speak over the verified route. Negative: no voice when disabled or when the route is unverified. VCASE-AFC-PR-022. | PROFILE, NOTIFIER | #1 items 3, 6 (voice announcements); C8 |
| AFC-PR-023 | The backend shall attach excitement commentary to an alert only at or below the customer's excitement level with every named entity grounded in the triggering event data. | Optional flavor that can never invent events, scores, or player identity. | Test, backend, AWS deployment. Positive: every named entity in commentary appears in the triggering event data. Negative: level off attaches nothing, and no model output determines an event, score, or player identity; level change alters commentary for an identical event; excitement_levels (DEC-AFC-SD-035, P2) are Off / Mild / Hype. VCASE-AFC-PR-023. | PROFILE, POLICY | #1 items 3, 6 (excitement level); #1 judging (grounded commentary); SD-035 (P2) |
| AFC-PR-024 | The backend shall resolve player and event identifiers across providers to single identities. | Yahoo, ESPN, and provider ids must converge or matching produces false alerts. | Test, backend, AWS deployment. Positive: same player/event across sources resolves to one identity. Negative: no two identities for one entity, no merged distinct entities. VCASE-AFC-PR-024. | MATCHER | #1 item 3 (match identifiers) |
| AFC-PR-025 | The backend shall emit at most one alert per resolved event. | Duplicate deliveries for one event destroy trust in the companion. | Test, backend, AWS deployment. Positive: repeated retrieval of an unchanged event emits nothing further. Negative: no second alert for one resolved event. VCASE-AFC-PR-025. | MATCHER, POLICY | #1 item 3 (duplicate events) |
| AFC-PR-026 | The backend shall propagate each scoring correction to previously emitted alerts and panel state. | Stale wrong scores must be repaired everywhere the customer saw them. | Test, system, AWS deployment. Positive: correction updates the alert record and the panel value. Negative: no corrected fact left stale in either surface. VCASE-AFC-PR-026. | MATCHER, POLICY, PANELSVC | #1 item 3 (scoring corrections); panel consistency rule |
| AFC-PR-027 | Each alert shall carry the verified player and matchup context that triggered it. | The customer must see why this event matters to them. | Demonstration, system, real stick (SD-001) + backend. Positive: alert shows the triggering player and matchup from lineup and feed data. Negative: no alert without its triggering context. VCASE-AFC-PR-027. | POLICY, MATCHER | #1 item 3 (verified context) |
| AFC-PR-028 | The system shall withhold any claim that a team red-zone entry proves a particular player is on the field or will score. | The precise over-claim the owner forbade. | Test, system, backend + TV surfaces. Positive: red-zone alert text makes only team-level claims. Negative: any player-on-field or will-score claim from a red-zone entry fails. VCASE-AFC-PR-028. | POLICY | #1 item 3 (red zone is not proof) |
| AFC-PR-029 | The backend shall resolve each alerted event to an available provider and channel from the customer's installed apps, verified subscriptions, local market, and provider preference. | Correct game/channel routing is the handoff half of the standout moment. Phase 2 link-contract spike order per SD-035 (Q5): Prime Video (TNF), ESPN app, DirecTV Stream app, YouTube TV. | Test, backend, AWS deployment. Positive: resolution output names provider and channel with inputs recorded; local-broadcast games (CBS/FOX/NBC) resolve to the channel plus a carrying provider app when one is available. Negative: no resolution from installed-app fact alone; no deep link when no carrying app is available. VCASE-AFC-PR-029. | RESOLVER | #1 item 4; SD-035 (Q5) |
| AFC-PR-030 | The TV app shall open the resolved game or channel through a supported provider launch URI or intent upon the customer's Watch action. | Watch must reach the game, not merely the provider home screen. | Demonstration, system, real stick (SD-001); evidence under evidence/visual/ (SD-024). Positive: correct game/channel opens. Negative: app-home landing does not satisfy; app launch alone does not satisfy. VCASE-AFC-PR-030. | LAUNCHER | #1 item 4 (notification action/deep link) |
| AFC-PR-031 | The TV app shall report each routing outcome as exactly one of game opened, search or details opened, app home opened, app absent, access unknown, or playback denied. | Explicit outcomes make partial success visible instead of silently degraded. | Demonstration, tv-app, real stick (SD-001). Positive: each attempted route reports exactly one enum value. Negative: no silent outcome, no invented value. VCASE-AFC-PR-031. | LAUNCHER | #1 app-launch research (explicit outcomes) |
| AFC-PR-032 | The system shall mark game access it cannot verify as unknown. | The explicit unknown-access behavior: doubt is displayed, never smoothed over. | Test, system, backend + TV surfaces. Positive: unverifiable access reads unknown on alerts, Watch routing, and panel. Negative: no unverified access reads verified or included. VCASE-AFC-PR-032. | RESOLVER, LAUNCHER | #1 item 4 (unknown stays unknown) |
| AFC-PR-033 | The system shall withhold any promise that a game is included merely because the provider app is installed. | The companion must never sell access it cannot confirm. | Test, system, backend + TV surfaces. Positive: installed-without-verified-subscription reads unknown per PR-032. Negative: any inclusion promise from install fact alone fails. VCASE-AFC-PR-033. | RESOLVER, LAUNCHER | #1 items 1, 4 (installed is not subscribed) |
| AFC-PR-034 | The backend shall choose among available services by the customer's provider preference. | The customer decides which of their services wins a contested game. | Test, system, backend + settings UI. Positive: preference change reroutes a contested game. Negative: no available-service choice contradicts the recorded preference. VCASE-AFC-PR-034. | PROFILE, RESOLVER | #1 items 4, 6 (provider preference) |
| AFC-PR-035 | The TV app shall honor the customer's switching-confirmation setting for every viewing switch. | Unconfirmed channel switches would hijack the customer's viewing. | Demonstration, system, real stick (SD-001). Positive: confirmation-required setting blocks switching until confirmed. Negative: no automatic switch unless explicitly configured and supported. VCASE-AFC-PR-035. | PROFILE, LAUNCHER | #1 items 4, 6 (switching confirmation) |
| AFC-PR-036 | The TV app shall offer Alexa-assisted tuning for the resolved game or channel only when the customer enables voice control over an implemented and verified Alexa route. | Alexa is an additional voice route, never an assumed capability. | Demonstration, tv-app, real stick (SD-001). Positive: enabled control over a verified route offers tuning. Negative: no Alexa offer when disabled or the route is unverified. VCASE-AFC-PR-036. | LAUNCHER | #1 item 4 (Alexa-assisted tuning); SD-008; C8 |
| AFC-PR-037 | The system shall use detection data and profile-based personalization only while the customer opts in to detection and personalization. | The master switch for sensing and personalization. | Test, system, backend + settings UI. Positive: opt-out yields monitoring without detection data or personalization. Negative: no detection-basis decision while opted out (labels per PR-011). VCASE-AFC-PR-037. | PROFILE, POLICY | #1 item 6 (use of detection/personalization) |
| AFC-PR-038 | The backend shall link the TV app to the customer account through a device code the customer completes on a phone or browser. | TV-friendly linking without typing credentials on the stick. | Demonstration, system, real stick + phone/browser page. Positive: code entry on phone/browser links the TV app. Negative: no link completes without the customer's code action. VCASE-AFC-PR-038. | AUTH, API | #1 item 6 (device-code linking sufficient) |
| AFC-PR-039 | The TV app shall display the selected fantasy team's lineup with each player's fantasy points and game status and the team total and progress under the league's scoring context. | The panel's core content: my players, my points, my progress. | Demonstration, system, real stick (SD-001) + backend; evidence under evidence/visual/ (SD-024). Positive: lineup, points, statuses, and total match the Yahoo league context (or PR-065 selected preset table for manual). Negative: no value shown without its scoring basis. VCASE-AFC-PR-039. | PANEL, PANELSVC | #1 right-side panel (required experience) |
| AFC-PR-040 | The TV app shall label each unavailable or stale panel value as unavailable or stale. | The explicit stale-data behavior: age and absence are visible. | Demonstration, tv-app, real stick (SD-001). Positive: withheld feed and missing value produce stale and unavailable labels. Negative: no silently old or silently missing value; stale_after is 60 seconds (DEC-AFC-SD-035, P3). VCASE-AFC-PR-040. | PANEL, PANELSVC | #1 right-side panel (stale/unavailable marks); SD-035 (P3) |
| AFC-PR-041 | The TV app shall fit the broadcast video into the screen area remaining beside the right-side lineup panel while preserving broadcast aspect ratio. | The panel supplements viewing; it must never cover or crop the broadcast. | Demonstration, tv-app, real stick (SD-001); evidence under evidence/visual/ (SD-024). Positive: simultaneous panel and video with no overlap and preserved aspect (dimension-compared capture). Negative: any overlap or crop fails. VCASE-AFC-PR-041. | PANEL, SHELL | #1 right-side panel (unobscured video); SD-006 |
| AFC-PR-042 | The TV app shall switch panel visibility and the followed team and league from TV remote input. | Core panel controls operable from the couch. | Demonstration, tv-app, real stick (SD-001); evidence under evidence/visual/ (SD-024). Positive: remote toggles visibility and changes team/league. Negative: no panel control requires another input device. VCASE-AFC-PR-042. | PANEL, PROFILE | #1 right-side panel (show/hide, team/league) |
| AFC-PR-043 | The lineup panel shall accept all panel operations from TV remote input. | Full panel use without leaving the couch. | Demonstration, tv-app, real stick (SD-001); evidence under evidence/visual/ (SD-024). Positive: every focusable element reachable with a visible focus indicator. Negative: no remote-dead operation. VCASE-AFC-PR-043. | PANEL | #1 right-side panel (remote navigable) |
| AFC-PR-044 | The lineup panel shall reflect the customer's team, league, and display settings. | The panel is a view of the customer's settings, not a second configuration. | Test, system, backend + TV panel. Positive: settings change appears on the panel. Negative: no panel content contradicts recorded settings. VCASE-AFC-PR-044. | PANEL, PANELSVC | #1 right-side panel (consistent with settings) |
| AFC-PR-045 | The lineup panel shall present lineup text the owner accepts as legible from the couch on the target device, with body text at least 24 px and scores at least 32 px at 1080p. | Couch legibility is judged by the owner on the real target, with a numeric floor per SD-035 (Q3). | Demonstration, tv-app, real stick (SD-001). Positive: owner accepts lineup text as couch-legible in the demonstration and body text measures at least 24 px with scores at least 32 px at 1080p. Negative: owner rejection or under-size text fails the case. VCASE-AFC-PR-045. | PANEL | #1 right-side panel (legible from the couch); SD-035 (Q3) |
| AFC-PR-046 | The system shall hold lineup panel state consistent with alerts across starter changes and scoring corrections. | Panel and alerts are two views of one truth. | Test, system, AWS deployment. Positive: starter change and correction reach both surfaces with identical corrected facts. Negative: no fact present in one surface and contradicted in the other (suppressed alerts do not break fact agreement; hidden panel refreshes on show). VCASE-AFC-PR-046. | PANELSVC, POLICY | #1 right-side panel (consistency rule) |
| AFC-PR-047 | When the panel-beside-provider-video spike fails or exceeds 24 hours from first app install, the TV app shall present the lineup panel as a full screen in the companion app. | No Mode A footage per owner decision (SD-035, Q4): the product is alerts + Watch, and the panel fallback is a full screen in our own app. | Demonstration, tv-app, real stick (SD-001); evidence under evidence/visual/ (SD-024). Positive: full-screen lineup panel in the companion app. Negative: no stand-in video, no provider video claimed, and no silent substitution of phone screen, app-switch dashboard, or covering panel. VCASE-AFC-PR-047. | PANEL, SHELL | #1 panel integration obligation; SD-006; SD-035 (Q4); C5 |
| AFC-PR-048 | While the lineup panel is shown full-screen in the companion app, the TV app shall route alerts and Watch actions to the real provider apps. | Full-screen panel degrades only the panel video route, never alerting or handoff. | Demonstration, system, real stick (SD-001). Positive: full-screen-panel alert Watch opens the real provider route. Negative: no alert or Watch trapped in the companion app. VCASE-AFC-PR-048. | NOTIFIER, LAUNCHER | SD-006; SD-035 (Q4) (alerts and Watch still go to real providers) |
| AFC-PR-049 | WITHDRAWN by DEC-AFC-SD-035 (2026-10-12). Original: Mode A sample footage shall carry a CC-BY or CC0 license with credit. | Withdrawal rationale: owner answered NO Mode A sample footage (Q4); the product is alerts + Watch with a full-screen panel fallback per PR-047. UID retained, never renumbered. | Withdrawn — no verification (VCASE-AFC-PR-049 retired). | PLAYER | SD-006a (footage licensing); SD-035 (Q4 withdrawal) |
| AFC-PR-050 | WITHDRAWN by DEC-AFC-SD-035 (2026-10-12). Original: Mode A playback shall display the label 'Sample footage — not a live broadcast'. | Withdrawal rationale: owner answered NO Mode A sample footage (Q4); no label needed without the footage. UID retained, never renumbered. | Withdrawn — no verification (VCASE-AFC-PR-050 retired). | PLAYER | SD-006a (footage labeling); SD-035 (Q4 withdrawal) |
| AFC-PR-051 | WITHDRAWN by DEC-AFC-SD-035 (2026-10-12). Original: Mode A sample footage shall exclude NFL footage. | Withdrawal rationale: owner answered NO Mode A sample footage (Q4); the exclusion is moot without the footage. UID retained, never renumbered. | Withdrawn — no verification (VCASE-AFC-PR-051 retired). | PLAYER | SD-006a (no NFL footage); SD-035 (Q4 withdrawal) |
| AFC-PR-052 | The TV app shall run on the 2018 Fire TV stick target on Fire OS. | The owner's device is the target; no purchase, no silent platform switch. | Demonstration, tv-app, real 2018 stick (SD-001). Positive: install, launch, and operate on the target. Negative: no target-only failure waived without a C1 owner return. VCASE-AFC-PR-052. | SHELL, MANIFEST | SD-003; SD-002 context; C1 |
| AFC-PR-053 | The TV app build shall declare minSdk 25. | Pins the provisional floor the target assumes. | Inspection, tv-app, source review of build.gradle.kts. Positive: declaration reads 25. Negative: any other value fails. VCASE-AFC-PR-053. | BUILD | SD-003 |
| AFC-PR-054 | The backend shall run on AWS serverless services within the Free tier declared in template.yaml. | Owner-created Free-plan account bounds cost; serverless matches the workload. | Inspection, backend, template.yaml review + deployment record. Positive: only Free-tier services (Lambda, HTTP API, DynamoDB on-demand, Scheduler, SSM) declared and deployed. Negative: any paid service or undeleted paid resource fails. VCASE-AFC-PR-054. | IAC | SD-005; SD-008 (AWS Builder services); C4 |
| AFC-PR-055 | The backend shall hold Yahoo OAuth client secrets and tokens only in SSM SecureString parameters. | Secrets stay server-side and owner-handled, never in the APK or repo. | Inspection, backend, source + APK + parameter review. Positive: parameters exist and code reads only them. Negative: any secret value in APK or repo fails. VCASE-AFC-PR-055. | SECRET, IAC | SD-007; C9 |
| AFC-PR-056 | The TV app and backend sources shall contain no local absolute path. | Committed absolute paths leak the builder's machine and break other checkouts. | Inspection, system, repository grep over tracked sources. Positive: grep for home-rooted and root-anchored local paths returns nothing. Negative: any committed local absolute path blocks per C7. VCASE-AFC-PR-056. | BUILD, IAC | SD-010; C7 |
| AFC-PR-057 | The system shall exclude messenger, message board, community room, shared chat, and watch-party social features. | Out of scope by owner decision; the register must say so plainly. | Inspection, system, source and UI review. Positive: no messaging surface or endpoint exists. Negative: any listed feature present fails. VCASE-AFC-PR-057. | SHELL, API | #1 explicit exclusion (owner decision 10-10) |
| AFC-PR-058 | The backend shall expose link, profile, alerts, panel, and provider operations to the TV app. | The TV↔backend contract surface the product behaviors need. | Test, system, deployed API. Positive: each operation responds per its contract. Negative: no TV behavior depends on an unexposed operation. VCASE-AFC-PR-058. | API | #1 source review (proposed data flow); #1 items 1, 3, 4, 6; panel |
| AFC-PR-059 | The backend shall perform API aggregation, full-game monitoring, cross-provider matching, and commentary generation. | Heavy work stays off the stick. | Inspection, backend, source review. Positive: each listed function implemented backend-side. Negative: no listed function implemented TV-side. VCASE-AFC-PR-059. | INGEST, MATCHER, POLICY | #1 lightweight device design |
| AFC-PR-060 | The backend shall send the TV app only updates relevant to the customer profile. | Small relevant updates keep the TV light and the customer unbothered. | Test, backend, AWS deployment. Positive: update stream for a fixture profile contains only profile-relevant updates. Negative: any irrelevant update fails. VCASE-AFC-PR-060. | API | #1 lightweight device design |
| AFC-PR-061 | The TV app shall coalesce burst updates into changed rows and values. | No whole-screen rerenders or tickers on a small stick. | Test, tv-app, instrumented build or review. Positive: burst input updates only changed rows/values. Negative: whole-screen rerender on a burst fails; hidden panel suspends update application and refreshes on show. VCASE-AFC-PR-061. | PANEL, NOTIFIER | #1 lightweight device design |
| AFC-PR-062 | The TV app's alert and panel components shall bound their event queues, retained history, images, and caches. | Declared bounds replace hope as the memory story; measurement stays excluded. | Inspection, tv-app, source review. Positive: each named resource has a declared limit. Negative: any unbounded named resource fails. VCASE-AFC-PR-062. | ALERTSVC, PANEL | #1 lightweight device design |
| AFC-PR-063 | The TV app's alert, panel, and detector components shall keep network work, parsing, and computation off the rendering thread. | The render thread stays free so the UI never janks on I/O. | Inspection, tv-app, source review. Positive: network, parse, and compute paths dispatch off the render thread. Negative: any such work on the render thread fails. VCASE-AFC-PR-063. | ALERTSVC, PANEL, DETECTOR | #1 lightweight device design |
| AFC-PR-064 | The backend shall reject a schema-invalid ESPN response without changing stored events. | A malformed poll must never corrupt the event cache. | Test, backend, AWS deployment. Positive: invalid fixture rejected, stored events byte-identical. Negative: any partial store from an invalid response fails. VCASE-AFC-PR-064. | INGEST | #1 item 2 (validation at ingest); SD-004 |
| AFC-PR-065 | The backend shall score manual lineups under the customer's selected preset from exactly two presets, PPR and Half-PPR, with Default preset Half-PPR, and shall score Yahoo leagues under Yahoo's own league scoring. | Manual lineups have no Yahoo league context; two documented presets give correct points without inventing league rules. PPR: 1 pt per reception, 1 pt per 10 rushing+receiving yards, 6 per rushing/receiving TD, 1 pt per 25 passing yards, 4 per passing TD, -1 per interception, -2 per fumble lost. Half-PPR: identical except 0.5 pt per reception. | Test, backend, AWS deployment. Positive: manual lineup points equal the selected preset table applied to feed statistics, and default selection is Half-PPR. Negative: any manual point without a table row fails; any third preset or Yahoo-league use of a preset table fails; manual scoring labeled with the selected preset ('PPR' or 'Half-PPR'). VCASE-AFC-PR-065. | PANELSVC, LINEUP | #1 right-side panel (league scoring context); SD-007 manual entry; SD-035 (D1) |
| AFC-PR-066 | The TV app shall record the customer's selected manual-lineup scoring preset from PPR and Half-PPR, defaulting to Half-PPR. | The customer chooses between the two most popular scoring modes (SD-035 D1); the default preserves half-PPR behavior. | Demonstration, system, real stick (SD-001) + backend. Positive: preset change alters manual points per PR-065 and persists across restart; default is Half-PPR. Negative: no third preset offered and no silent preset change. VCASE-AFC-PR-066. | PROFILE, LINEUP | SD-035 (D1) |

## Owner questions and open items (DEC-AFC-SD-035, 2026-10-12)

| ID | Question / parameter | Status |
|---|---|---|
| Q1 | Guard vs OD-AFC-12 placement | Closed by SD-027 (Markdown register; no host binding) |
| Q2 | Excitement-level scale | Closed by SD-035: Off / Mild / Hype fixed in PR-023 |
| Q3 | Couch legibility numeric minimum (PR-045) | Closed by SD-035: owner acceptance plus body text >= 24 px, scores >= 32 px at 1080p |
| Q4 | Mode A footage (F12) | Closed by SD-035: NO Mode A footage; alerts + Watch product; full-screen panel fallback (PR-047/048); PR-049..051 withdrawn |
| Q5 | First provider link contract in Phase 2 spike | Closed by SD-035: Prime Video (TNF), ESPN app, DirecTV Stream app, YouTube TV; local broadcast (CBS/FOX/NBC): show channel, offer carrying app, else no deep link (PR-029) |
| Q6 | Stick located, model/OS confirmed? | Open: stick found; model/OS still unrecorded |
| Q7 | Yahoo application submitted? | Open: not applied |
| Q8 | AWS Free-plan account created? | Open: not created |
| Q9 | License choice | Closed by SD-035: Apache-2.0 |
| Q10 | Restore engineering-methods S8 ledger, or waive? | Open: separate Alphazedehq task (not this register) |
| P1 | close_game_margin (PR-014) | Closed by SD-035: within 8 points in the 4th quarter or overtime |
| P2 | excitement_levels (PR-023) | Closed by SD-035: Off / Mild / Hype |
| P3 | stale_after (PR-040) | Closed by SD-035: 60 seconds |
| D1 | Manual-lineup default scoring (PR-065) | Closed by SD-035: customer-selectable preset of PPR and Half-PPR; Default preset Half-PPR (PR-065/066) |

## Vega OS port mapping (P2-V01, M14; planning delta 2026-10-14)

The Vega build (issue #59, owner SD-040) mirrors the Fire OS TV app. Each
Vega feature reuses the register UIDs below by reference, unchanged. Their
Fire OS VCASE allocations stay as they are; the Vega evidence for them is
SEIT-AFC-P2-VEGA-01 and -03. Vega-specific items (packaging, VVD limits and
verdicts, token storage, optional physical device, Fire OS isolation) are
Lifecycle-local criteria AC-AFC-P2-VEGA-01..06 and RISK-AFC-P2-14/15 in the
technical plan §M14 Vega OS port. No new register UID is added.

| Vega feature | Fire OS slices mirrored | Register UIDs reused |
|---|---|---|
| Device linking and ApiClient | P2-A01T, P2-A01 | AFC-PR-038, -057, -063 |
| Profile settings and detection | P2-A02T, P2-A02 | AFC-PR-002, -003, -005, -009, -010, -016, -017, -018, -019, -020, -021, -022, -023, -034, -035, -037, -042, -044, -066 |
| Alerts | P2-A03T, P2-A03 | AFC-PR-015, -021, -022, -027, -028, -032, -033, -061, -062, -063 |
| Watch | P2-A04T, P2-A04 | AFC-PR-030, -031, -035, -036, -048 |
| Lineup panel | P2-A05T, P2-A05 | AFC-PR-039, -040, -041, -042, -043, -044, -045, -046, -047, -061, -062 |

Not mirrored: AFC-PR-052 (Fire OS on the 2018 stick) and AFC-PR-053 (minSdk 25) have no Vega equivalent.
The Vega packaging rule is AC-AFC-P2-VEGA-02.


## Vega-primary conditional allocation (2026-10-14, selected by DEC-AFC-SD-049)

Selected 2026-10-14: Vega OS primary, Fire OS secondary; both targets are
built and no UID allocation to the Fire OS slices is removed.

The register statements above are preserved. The five-feature Vega mapping
above remains the source inventory, with all listed UIDs retained. The
primary alternative changes realization and proof environment only after
VP-OD-01; it does not manufacture passed VCASEs. Lifecycle-local
AC-AFC-P2-VPRIMARY-01..04 and RISK-AFC-P2-16/17 belong to the technical plan.

| Coverage set | Proposed primary realization / proof | Status |
|---|---|---|
| Every UID mirrored by the five rows in Vega OS port mapping | Same V01T/V01 IDs; requirement/VCASE source replaces nonexistent A02T–A05T test source. Available A01 tests remain reference evidence. Physical X02/X03/X04/X07/X09 prove provider-dependent claims. | Proposed; every application observation not_run |
| AFC-PR-015, 030, 048 | Physical alert/action/playback and real provider game/channel handoff | Blocking physical evidence, no simulator substitute |
| AFC-PR-041, 047 | Physical geometry proof for modeB, or existing timed fullScreen fallback | No new video route or silent waiver |
| AFC-PR-052, 053 | P2-D02 must record an owner-approved Vega target/model/OS and manifest compatibility allocation instead of Fire OS 2018/minSdk 25 | Decided DEC-AFC-SD-049: P2-D02 records the Vega primary target; Fire OS 2018 stick and minSdk 25 stay for the Fire OS secondary build |
| AFC-PR-038, 054, 055, 058, 059, 063 | Shared API/session/security/compute controls; SD-048 code-only confirmation reconciled in backend before integrated proof | SD-048 settled; implementation verification pending |
| All other backend, submission, feedback and lifecycle UIDs | Original allocations retained; downstream slices target the selected artifact and truthful evidence | Not removed by TV contingency |
| RISK-AFC-P2-14 | P2-D04 closes it, P2-V01 supplies the verdict evidence. The Vega build is in the submission only if P2-V01 verification passed before the documents are finalized; otherwise it is reported as in progress with its limits | Decided DEC-AFC-SD-050; F1 closed |
