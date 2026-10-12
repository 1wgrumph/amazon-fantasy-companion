---
type: specialist-receipt
title: Requirements Engineer ST-2 gate — AFC-ST-2026-10-12
okf_status: draft
tags: [requirements, planning, afc, spec-track]
---

verdict: **NEEDS_OWNER_DECISION** (non-row blocker; the row gate itself is 65/65 PASS after one self-correction round)

candidate_ref: Lifecycle AFC-ST-2026-10-12, step ST-2, branch `plan/2026-10-12-afc-spec-track`.
Intended candidate file `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/afc-product-requirements.sdoc`
does not exist: its write was refused by the Requirements System guard (exact error below).
The gated draft (65 rows, full fields) is recorded in this receipt as gate input; it is not the
specification. Materialize it into the `.sdoc` unchanged once the write path is resolved, then
re-run bridge + lint + readback before ST-3c.

changed_paths: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/re-st2-receipt.md` only
(this file). No `.sdoc` was created, modified, or bound; no checkout was created, released, or moved.

rows_checked: **65 product requirements (AFC-PR-001..065); 65 PASS, 0 failing, 0 NEEDS_OWNER_DECISION rows**
after one self-correction round (4 fixes: 1 statement rewrite, 1 row split, 2 added rows; details under
"Self-correction pass"). No second round was needed. No row was left failing.

blocker: OD-AFC-12 mandates the register as "draft `.sdoc` in the spec-track plan directory", but the
Requirements System guard refuses any `.sdoc` outside `docs/coe` or `migrations/<project>`, and this
role's authority covers only the plan directory. The refused write was not retried, forced, or routed
around. Owner decision required: (a) grant a guard exception for the OD-AFC-12 path, (b) amend OD-AFC-12
to a managed-root path with matching write authority, or (c) direct another placement. Validation and
host binding are blocked on the same missing file (exact errors below); the other checkout on the shared
host (MID-MAESTRO-SPECIFICATION-CORE-0001) was not touched.

mechanical_receipt: No `lint-sdoc.py` or StrictDoc bridge output exists: both require the `.sdoc` file,
which the guard refused to create. Per the role skill this is `NEEDS_MORE_EVIDENCE` for the mechanical
leg; the checklist leg below is complete. A 1-requirement probe validated the intended mechanics
(22-field grammar, `lint_profile: project-specification`, `implemented-by` relations to in-document
element nodes): bridge `status: ok`, `validation.status: valid`, lint exit 0.

method_note: The `requirements-engineering` method skill and its references (authoring, NASA checklist,
quality gate, interface profile) were read and applied. S8 citations use only the row ids embedded in
those references (SRC-EMV-NASA-SEH, SRC-EMV-COE, SRC-EMV-29148, metadata-only); no ISO clause is
invented. Observation S8-LEDGER-MISSING: the standalone `engineering-methods/references/standards-receipts.md`
ledger is absent from the skills tree; recorded as an observation, not a gate failure, because no cited
content is affected. Register derived from issue #1, SD/C batch, and sm-contextual-pass.md; the f885e48
product rows were not read or copied. The parent RE receipt was consulted for gate pattern and known
pitfalls only (its ALERT-04, PANEL-01/03/04 findings are addressed by AFC-PR-015/021, AFC-PR-065,
AFC-PR-042, AFC-PR-046).

## Typed gaps

- WRITE_BLOCKED_RS_GUARD: `write_file` for `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/afc-product-requirements.sdoc`
  refused: "BLOCKED by requirements-system-guard.sh — <worktree>/docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/afc-product-requirements.sdoc,
  which is outside every Requirements System-managed root in this repository; an .sdoc belongs under a
  migrations/<project> tree with a registry.toml, or under docs/coe" (home prefix redacted per SD-010).
- VALIDATION_BLOCKED_NO_FILE: StrictDoc bridge and `lint-sdoc.py` not run; no input file exists.
- BINDING_BLOCKED_NO_FILE: `alphazede-requirements-system checkout create --spec MID-AFC-ST2-SPEC-0001
  --doc-mid 9f3c1a7e4b2d4f6a8c0e1d2f3a4b5c6d --doc afc-product-requirements.sdoc
  --root <plan-dir> --revision REV-0` → "alphazede-requirements-system: --doc is not an existing file
  inside --root: afc-product-requirements.sdoc" (exit 1; fails before any state change; no checkout touched).

## Coverage — issue #1 retained items and panel

| Source | UIDs |
|---|---|
| Item 1 profile | 001, 002, 003, 004, 005, 006, 007, 038 |
| Item 2 monitor | 008, 009, 010, 011, 012, 013, 064 |
| Item 3 alerts | 014, 015, 016, 017, 018, 019, 020, 021, 022, 023, 024, 025, 026, 027, 028 |
| Item 4 watch | 029, 030, 031, 032, 033, 034, 035, 036 |
| Item 6 controls + linking | 002, 009, 010, 016, 017, 018, 019, 020, 021, 022, 023, 034, 035, 037, 038 |
| Panel | 039, 040, 041, 042, 043, 044, 045, 046, 047, 048, 049, 050, 051, 065 |
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

## Coverage — conditionals C1..C9 (typed) and decisions SD-001..SD-011, SD-024

| ID | Type / honoring |
|---|---|
| C1 enforced_rule | 052 platform target; assumptions (model unconfirmed); owner-return in constraints |
| C2 expected_outcome | 013 replay substitution; 012 ingest; evidence note |
| C3 enforced_rule | 012 constraints (owner terms flag at submission) |
| C4 enforced_rule | 054 Free-tier-only hosting |
| C5 expected_outcome | 047 Mode A fallback; 048 provider routing; 041 constraints |
| C6 expected_outcome | 006 manual entry at T_yahoo; 007 single source; 065 manual scoring |
| C7 enforced_rule | 056 path hygiene |
| C8 enforced_rule | 022 voice announcements; 036 Alexa tuning |
| C9 enforced_rule | 055 server-side secrets; owner-action constraints on 006/038/054 |
| SD-001 | Real-device verification environment on 015, 021, 022, 027-scope rows: 003, 005, 009, 010, 015, 021, 022, 030, 031, 035, 036, 039–048, 052 |
| SD-002 | 052 assumptions (newer device acceptable context) |
| SD-003 | 052 target; 053 minSdk; starter in 052 assumptions (build method, not a requirement) |
| SD-004 | 012 ESPN ingest; 013 replay |
| SD-005 | 054 AWS serverless Free-tier |
| SD-006 | 041 unobscured video; 047/048 Mode A |
| SD-006a | 049 sourcing; 050 label; 051 no NFL footage |
| SD-007 | 001 Yahoo read-only; 006/007/065 swappable source; 055 secrets |
| SD-008 | 036 Alexa conditional; 054 rationale (AWS Builder services) |
| SD-009 | Honored as owner scope via C9 constraints (005-range rows, 055) and scope note; no product UID (repo flip/license is an owner action, not product behavior) |
| SD-010 | 056 no local absolute paths |
| SD-011 | Honored via evidence note (verification evidence published with plan materials); no product UID (publication is program process) |
| SD-024 | Evidence note (`evidence/visual/`, no account/customer data); demonstration criteria on 015, 030, 039–043, 047 |
| Unknown access | 004 verified-only marking; 031 outcome enum; 032 unknown marking; 033 no inclusion promise |
| Stale data | 012 timestamps/corrections; 026 correction propagation; 040 stale/unavailable labels; 046 consistency |

## ST-3a allocation elements (AFC-EL nodes in the intended .sdoc)

SHELL MainActivity.kt; BUILD build.gradle.kts; MANIFEST AndroidManifest.xml; PROFILE ProfileSettingsScreen.kt;
DETECTOR AppDetector.kt; ALERTSVC AlertService.kt; NOTIFIER AlertNotifier.kt; LAUNCHER WatchLauncher.kt;
PANEL LineupPanel.kt; PLAYER CompanionPlayer.kt; IAC backend/template.yaml; AUTH backend/src/device_auth/;
API backend/src/api/; INGEST backend/src/feed_ingest/; REPLAY replay.py + fixtures/replay/;
LINEUP backend/src/lineup/; MATCHER backend/src/matcher/; POLICY backend/src/alert_policy/;
RESOLVER backend/src/provider_resolver/; PANELSVC backend/src/panel/; SECRET SSM SecureString;
STORE DynamoDB profile/event tables. Every UID below carries implemented-by to ≥1 element; every element
receives ≥1 UID.

## Draft register — gate input (65 rows; materialize into the .sdoc once unblocked)

Common fields (all rows): STATUS Draft; OWNER Amazon Fantasy Companion specification;
VALIDATION_METHOD owner review at ST-5; EXPECTED_RESULT pending Phase 2 verification;
ACTUAL_RESULT not executed (planning register); ANOMALY none recorded;
CORRECTIVE_ACTION none (revise through ST-2 correction rounds); WAIVER none;
CLOSURE open pending ST-5 owner review. VERIFICATION_CASE VCASE-AFC-PR-NNN per row.
Gate codes reference CHK-RE-NN (NASA-adapted checklist); S8 rows
SRC-EMV-NASA-SEH, SRC-EMV-COE, SRC-EMV-29148 (metadata-only, no clauses).

### AFC-PR-001 — Yahoo lineup retrieval
- statement: The backend shall retrieve the customer's leagues, teams, rosters by week, and league scoring settings through a read-only Yahoo Fantasy OAuth connection.
- source: #1 item 1; #1 Yahoo rows; SD-007.
- rationale: Yahoo is the lineup/league context source; read-only OAuth bounds access to need.
- allocation: LINEUP.
- verification: test, backend, AWS Free-plan deployment (SD-005). Criteria: positive — roster distinguishes active slots from bench and returns scoring settings; negative — no write-scope call is attempted and no player eligibility value is used as a starting-slot fact; check VCASE-AFC-PR-001.
- assumptions: Yahoo application approved before T_yahoo, else PR-006; endpoint candidates confirmed at integration.
- constraints: C6 fallback; C9 credentials owner-handled; external interface Yahoo Fantasy API.
- gate: PASS.

### AFC-PR-002 — Fantasy selection persistence
- statement: The TV app shall persist the customer's selected leagues, teams, starters or specific players, and favorite teams.
- source: #1 items 1, 6 (fantasy selections).
- rationale: Selections drive monitoring, alerts, and panel content; loss across restart breaks trust.
- allocation: PROFILE, API, STORE.
- verification: demonstration, system, real stick (SD-001) + backend. Criteria: positive — select, restart, selections retained; negative — no selection silently dropped; check VCASE-AFC-PR-002.
- assumptions: None beyond Yahoo/manual source availability.
- constraints: Internal interface TV app ↔ /v1/profile.
- gate: PASS.

### AFC-PR-003 — Installed viewing app reporting
- statement: The TV app shall report each supported installed viewing app as installed through platform-permitted detection.
- source: #1 item 1; SD-003.
- rationale: Provider choice needs true installed-app facts without claiming subscription.
- allocation: DETECTOR.
- verification: demonstration, tv-app, real stick (SD-001). Criteria: positive — each installed supported app reported installed; negative — absent app never reported installed; check VCASE-AFC-PR-003.
- assumptions: Platform exposes install visibility on the target; else customer confirmation only.
- constraints: C1 device capability; PR-033 (installed is not subscribed).
- gate: PASS.

### AFC-PR-004 — Verified access marking
- statement: The backend shall mark each game's viewing access as verified only from supported provider integration or explicit customer confirmation.
- source: #1 items 1, 4.
- rationale: Honest availability is a judging emphasis; unverified access must never read as verified.
- allocation: RESOLVER, API.
- verification: test, backend, AWS deployment. Criteria: positive — verified marking carries basis integration or confirmation; negative — installed-app fact alone never yields verified; check VCASE-AFC-PR-004.
- assumptions: At least one provider integration contract from the Phase 2 spike.
- constraints: PR-032 unknown default.
- gate: PASS.

### AFC-PR-005 — Profile review and override
- statement: The TV app shall apply the customer's review and override to all detected profile information and retained local-market information.
- source: #1 item 1.
- rationale: Detection is fallible; the customer is the final authority on their profile.
- allocation: PROFILE, STORE.
- verification: demonstration, tv-app, real stick (SD-001). Criteria: positive — override of a detected app and of local market persists across restart and feed refresh; negative — refresh never silently discards an override; check VCASE-AFC-PR-005.
- assumptions: None.
- constraints: Internal interface TV app ↔ /v1/profile.
- gate: PASS.

### AFC-PR-006 — Manual lineup entry fallback
- statement: When Yahoo approval is absent at T_yahoo (2026-10-16T19:00:00Z), the backend shall accept labeled manual lineup entry built from ESPN rosters as the active lineup source.
- source: #1 item 1; SD-007; C6.
- rationale: Schedule-proof lineup context without misrepresenting manual data as Yahoo data.
- allocation: LINEUP.
- verification: test, backend, AWS deployment. Criteria: positive — at/after T_yahoo without approval, manual entry activates and is labeled manual; negative — manual values never presented as Yahoo values; check VCASE-AFC-PR-006.
- assumptions: ESPN rosters readable for manual construction; C9 owner actions unaffected.
- constraints: C6 expected_outcome; PR-007 single-source invariant; PR-065 manual scoring.
- gate: PASS.

### AFC-PR-007 — Single active lineup source
- statement: The backend shall hold exactly one active lineup source from the Yahoo read-only connection or labeled manual entry.
- source: #1 item 1; SD-007.
- rationale: Two simultaneous sources would fork lineup truth across alerts and panel.
- allocation: LINEUP.
- verification: test, backend, AWS deployment. Criteria: positive — source query returns exactly one active source; negative — switchover never leaves zero or two active; check VCASE-AFC-PR-007.
- assumptions: None.
- constraints: C6; PR-006 trigger.
- gate: PASS.

### AFC-PR-008 — Enabled period monitoring
- statement: The backend shall monitor live NFL game events only for profile-relevant games during customer-enabled viewing periods.
- source: #1 item 2.
- rationale: Relevance and customer control bound noise, cost, and backend load.
- allocation: INGEST, POLICY.
- verification: test, backend, AWS deployment. Criteria: positive — game with a selected player or favorite team inside an enabled period is monitored; negative — irrelevant game, or any game in quiet hours, is not monitored; check VCASE-AFC-PR-008.
- assumptions: None.
- constraints: PR-009 enablement; PR-018/019 periods.
- gate: PASS.

### AFC-PR-009 — Schedule mode recording
- statement: The TV app shall record the customer's selected schedule and game-day mode as the monitoring enablement.
- source: #1 items 2, 6 (quiet hours/game-day periods).
- rationale: The customer decides when the companion watches.
- allocation: PROFILE, POLICY.
- verification: demonstration, system, real stick (SD-001) + backend. Criteria: positive — mode change alters the monitored game set per PR-008; negative — no monitoring outside the recorded enablement; check VCASE-AFC-PR-009.
- assumptions: None.
- constraints: Internal interface TV app ↔ /v1/profile.
- gate: PASS.

### AFC-PR-010 — Viewing detection enablement
- statement: The TV app shall apply current-viewing-context detection only through supported mechanisms while the customer enables that detection.
- source: #1 items 2, 6 (detection use).
- rationale: Viewing-context sensing is sensitive and platform-limited; both bounds apply.
- allocation: DETECTOR, PROFILE.
- verification: demonstration, tv-app, real stick (SD-001). Criteria: positive — enabled detection uses a documented supported mechanism; negative — disabled detection yields no viewing-context reads (decisions label profile-assumption per PR-011); check VCASE-AFC-PR-010.
- assumptions: Supported detection, if any, identified by the Phase 2 spike; absence preserves the setting.
- constraints: PR-037 master opt-in.
- gate: PASS.

### AFC-PR-011 — Monitoring basis labeling
- statement: The backend shall label each monitoring decision with its observed-playback or profile-assumption basis.
- source: #1 item 2.
- rationale: Observed state and assumption must never be confused downstream.
- allocation: POLICY.
- verification: test, backend, AWS deployment. Criteria: positive — every decision record carries exactly one basis label; negative — no decision ships unlabeled; check VCASE-AFC-PR-011.
- assumptions: None.
- constraints: PR-010 detection input; PR-037 opt-in.
- gate: PASS.

### AFC-PR-012 — ESPN event ingest
- statement: The backend shall ingest scores, field position, possession, involved player identifiers, timestamps, and scoring corrections from ESPN's unofficial public JSON.
- source: #1 item 2; #1 feed requirements; SD-004.
- rationale: Owner-selected live feed; corrections and timestamps ground freshness and panel truth.
- allocation: INGEST.
- verification: test, backend, AWS deployment. Criteria: positive — each listed field lands in the event cache; negative — schema-invalid response handled per PR-064, never partially stored; check VCASE-AFC-PR-012.
- assumptions: Endpoint contract as observed at integration; change triggers PR-013.
- constraints: C2 replay; C3 terms flagged at submission (owner action); external interface ESPN JSON.
- gate: PASS.

### AFC-PR-013 — Labeled replay substitution
- statement: When the ESPN endpoint is unavailable or its contract changes, the backend shall substitute labeled replay fixtures for live events on every affected value.
- source: #1 judging alignment (label replays); C2.
- rationale: Repeatability and outage survival without ever faking live access.
- allocation: REPLAY, INGEST.
- verification: test, backend, AWS deployment with fixtures. Criteria: positive — outage run marks every affected value replay; negative — no substituted value presented as live; check VCASE-AFC-PR-013.
- assumptions: Fixtures captured from a permitted window and labeled at capture.
- constraints: C2 expected_outcome.
- gate: PASS.

### AFC-PR-014 — Personalized alert emission
- statement: The backend shall emit alerts for red-zone opportunities, player scores, and close games matching the customer's fantasy selections and alert-type settings.
- source: #1 item 3.
- rationale: The core personalized value: this event matters to this customer.
- allocation: POLICY, MATCHER.
- verification: test, backend, AWS deployment. Criteria: positive — each of the three types fires for a matching selection; negative — non-matching event, or matching event of a disabled type, emits nothing; red zone means inside the 20-yard line; close-game bound is open parameter close_game_margin (owner Phase 2 design, close by Phase 2 plan approval, evidence design review); check VCASE-AFC-PR-014. Alert text claims no player-level inference per PR-028.
- assumptions: close_game_margin defined at Phase 2 design.
- constraints: PR-016 types; PR-023 excitement; PR-028 no inference.
- gate: PASS (open value carried with owner, close-by date, and closure evidence per CHK-RE-10).

### AFC-PR-015 — Heads-up alert presentation
- statement: While heads-up presentation is selected, the TV app shall present each alert as a heads-up notification with Watch and Dismiss actions during third-party viewing-app playback.
- source: #1 item 3; SD-001.
- rationale: The standout moment: brief alert over playback with a direct Watch path.
- allocation: NOTIFIER, ALERTSVC, MANIFEST.
- verification: demonstration, system, real stick (SD-001); evidence under evidence/visual/ (SD-024). Criteria: positive — provider playback continues while the alert shows Watch/Dismiss; negative — no companion-app foregrounding, and no heads-up while panel-only presentation is selected; check VCASE-AFC-PR-015.
- assumptions: Heads-up over third-party playback verified by the Phase 2 spike; Fire OS documentation alone is not proof.
- constraints: PR-021 presentation choice; Fire OS notification service interface.
- gate: PASS after self-correction (added the presentation-selected condition; original contradicted PR-021 per CHK-RE-24).

### AFC-PR-016 — Alert type enablement
- statement: The backend shall emit alerts only for customer-enabled alert types.
- source: #1 items 3, 6 (alert types).
- rationale: Per-type control is the primary noise control.
- allocation: PROFILE, POLICY.
- verification: test, system, backend + settings UI. Criteria: positive — enabled type fires on matching event; negative — disabled type fires on nothing; check VCASE-AFC-PR-016.
- assumptions: None.
- constraints: PR-014 types.
- gate: PASS.

### AFC-PR-017 — Alert frequency cap
- statement: The backend shall emit no more alerts than the customer's frequency setting permits.
- source: #1 items 3, 6 (frequency).
- rationale: Frequency caps keep the companion welcome during simultaneous Sunday games.
- allocation: PROFILE, POLICY.
- verification: test, system, backend + settings UI. Criteria: positive — restrictive setting yields fewer alerts than permissive for an identical event stream; negative — no alert beyond the setting on any run; check VCASE-AFC-PR-017.
- assumptions: None.
- constraints: PR-018/019 periods apply first.
- gate: PASS.

### AFC-PR-018 — Quiet hours suppression
- statement: The backend shall suppress alerts during the customer's quiet hours.
- source: #1 items 3, 6 (quiet hours/game-day periods).
- rationale: Silence when the customer demands silence.
- allocation: PROFILE, POLICY.
- verification: test, system, backend + settings UI. Criteria: positive — triggering event inside quiet hours emits nothing; negative — no quiet-hours alert on any run; check VCASE-AFC-PR-018.
- assumptions: None.
- constraints: PR-019 game-day periods are the complementary emission window.
- gate: PASS.

### AFC-PR-019 — Game-day period emission
- statement: The backend shall emit alerts only during the customer's game-day periods.
- source: #1 items 3, 6 (quiet hours/game-day periods).
- rationale: Alerts belong to game time, not all time.
- allocation: PROFILE, POLICY.
- verification: test, system, backend + settings UI. Criteria: positive — triggering event inside a game-day period emits (subject to other filters); negative — nothing emits outside game-day periods; check VCASE-AFC-PR-019.
- assumptions: None.
- constraints: PR-018 quiet hours; PR-009 monitoring enablement.
- gate: PASS.

### AFC-PR-020 — Spoiler delay application
- statement: The backend shall delay each alert by the customer's spoiler delay.
- source: #1 items 3, 6 (spoiler delay).
- rationale: Customers behind live play must not be spoiled by their own companion.
- allocation: PROFILE, POLICY.
- verification: test, backend, AWS deployment. Criteria: positive — delivery timestamp minus event timestamp is at least the set delay; negative — no alert delivered early; check VCASE-AFC-PR-020.
- assumptions: None.
- constraints: Source-event timestamps per PR-012.
- gate: PASS.

### AFC-PR-021 — Notification presentation choice
- statement: The TV app shall render each alert in the customer's chosen notification presentation.
- source: #1 items 3, 6 (notification presentation).
- rationale: Presentation choice balances intrusiveness and awareness per customer.
- allocation: PROFILE, NOTIFIER.
- verification: demonstration, tv-app, real stick (SD-001). Criteria: positive — each offered presentation renders as chosen; negative — panel-only choice shows no heads-up; check VCASE-AFC-PR-021.
- assumptions: Offered presentations defined at Phase 2 design; heads-up and panel-only always offered.
- constraints: PR-015 heads-up behavior.
- gate: PASS.

### AFC-PR-022 — Voice announcement enablement
- statement: The TV app shall announce alerts by voice only while the customer enables voice announcements over an implemented and verified voice route.
- source: #1 items 3, 6 (voice announcements); C8.
- rationale: Voice is intrusive and platform-conditional; both gates apply.
- allocation: PROFILE, NOTIFIER.
- verification: demonstration, tv-app, real stick (SD-001). Criteria: positive — enabled announcements speak over the verified route; negative — no voice when disabled or when the route is unverified; check VCASE-AFC-PR-022.
- assumptions: Voice route verified by the Phase 2 spike or absent.
- constraints: C8 enforced_rule; PR-036 Alexa tuning.
- gate: PASS.

### AFC-PR-023 — Excitement commentary grounding
- statement: The backend shall attach excitement commentary to an alert only at or below the customer's excitement level with every named entity grounded in the triggering event data.
- source: #1 items 3, 6 (excitement level); #1 judging (grounded commentary).
- rationale: Optional flavor that can never invent events, scores, or player identity.
- allocation: PROFILE, POLICY.
- verification: test, backend, AWS deployment. Criteria: positive — every named entity in commentary appears in the triggering event data; negative — level off attaches nothing, and no model output determines an event, score, or player identity; level change alters commentary for an identical event; open parameter excitement_levels (owner Phase 2 design, close by Phase 2 plan approval, evidence design review); check VCASE-AFC-PR-023.
- assumptions: Level set defined at Phase 2 design with off always present; OD-AFC-02 AI-commentary scope returns at the Phase 2 review.
- constraints: PR-059 backend generation placement.
- gate: PASS (open value per CHK-RE-10).

### AFC-PR-024 — Cross-provider identity resolution
- statement: The backend shall resolve player and event identifiers across providers to single identities.
- source: #1 item 3 (match identifiers).
- rationale: Yahoo, ESPN, and provider ids must converge or matching produces false alerts.
- allocation: MATCHER.
- verification: test, backend, AWS deployment. Criteria: positive — same player/event across sources resolves to one identity; negative — no two identities for one entity, no merged distinct entities; check VCASE-AFC-PR-024.
- assumptions: Provider identifier sources identified by the Phase 2 spike.
- constraints: Interfaces Yahoo API, ESPN JSON, provider registry.
- gate: PASS.

### AFC-PR-025 — Duplicate alert suppression
- statement: The backend shall emit at most one alert per resolved event.
- source: #1 item 3 (duplicate events).
- rationale: Duplicate deliveries for one event destroy trust in the companion.
- allocation: MATCHER, POLICY.
- verification: test, backend, AWS deployment. Criteria: positive — repeated retrieval of an unchanged event emits nothing further; negative — no second alert for one resolved event; check VCASE-AFC-PR-025.
- assumptions: None.
- constraints: PR-024 resolution; PR-026 corrections are new emissions, not duplicates.
- gate: PASS.

### AFC-PR-026 — Scoring correction propagation
- statement: The backend shall propagate each scoring correction to previously emitted alerts and panel state.
- source: #1 item 3 (scoring corrections); panel consistency rule.
- rationale: Stale wrong scores must be repaired everywhere the customer saw them.
- allocation: MATCHER, POLICY, PANELSVC.
- verification: test, system, AWS deployment. Criteria: positive — correction updates the alert record and the panel value; negative — no corrected fact left stale in either surface; check VCASE-AFC-PR-026.
- assumptions: None.
- constraints: PR-040 stale labels; PR-046 consistency.
- gate: PASS.

### AFC-PR-027 — Alert context carriage
- statement: Each alert shall carry the verified player and matchup context that triggered it.
- source: #1 item 3 (verified context).
- rationale: The customer must see why this event matters to them.
- allocation: POLICY, MATCHER.
- verification: demonstration, system, real stick (SD-001) + backend. Criteria: positive — alert shows the triggering player and matchup from lineup and feed data; negative — no alert without its triggering context; check VCASE-AFC-PR-027.
- assumptions: None.
- constraints: PR-028 bounds what context may claim.
- gate: PASS.

### AFC-PR-028 — Red-zone inference withholding
- statement: The system shall withhold any claim that a team red-zone entry proves a particular player is on the field or will score.
- source: #1 item 3 (red zone is not proof).
- rationale: The precise over-claim the owner forbade.
- allocation: POLICY.
- verification: test, system, backend + TV surfaces. Criteria: positive — red-zone alert text makes only team-level claims; negative — any player-on-field or will-score claim from a red-zone entry fails; check VCASE-AFC-PR-028.
- assumptions: None.
- constraints: PR-014 red-zone alerts; PR-023 commentary.
- gate: PASS (prohibition is the need; positive form).

### AFC-PR-029 — Provider channel resolution
- statement: The backend shall resolve each alerted event to an available provider and channel from the customer's installed apps, verified subscriptions, local market, and provider preference.
- source: #1 item 4.
- rationale: Correct game/channel routing is the handoff half of the standout moment.
- allocation: RESOLVER.
- verification: test, backend, AWS deployment. Criteria: positive — resolution output names provider and channel with inputs recorded; negative — no resolution from installed-app fact alone; check VCASE-AFC-PR-029.
- assumptions: One real provider contract from the Phase 2 spike; remaining providers follow.
- constraints: PR-004 verified access; PR-034 preference; PR-032 unknown.
- gate: PASS.

### AFC-PR-030 — Watch action launch
- statement: The TV app shall open the resolved game or channel through a supported provider launch URI or intent upon the customer's Watch action.
- source: #1 item 4 (notification action/deep link).
- rationale: Watch must reach the game, not merely the provider home screen.
- allocation: LAUNCHER.
- verification: demonstration, system, real stick (SD-001); evidence under evidence/visual/ (SD-024). Criteria: positive — correct game/channel opens; negative — app-home landing does not satisfy; app launch alone does not satisfy; check VCASE-AFC-PR-030.
- assumptions: Provider link contract verified on the target by the Phase 2 spike.
- constraints: PR-031 outcome reporting; no invented URI formats.
- gate: PASS.

### AFC-PR-031 — Routing outcome reporting
- statement: The TV app shall report each routing outcome as exactly one of game opened, search or details opened, app home opened, app absent, access unknown, or playback denied.
- source: #1 app-launch research (explicit outcomes).
- rationale: Explicit outcomes make partial success visible instead of silently degraded.
- allocation: LAUNCHER.
- verification: demonstration, tv-app, real stick (SD-001). Criteria: positive — each attempted route reports exactly one enum value; negative — no silent outcome, no invented value; check VCASE-AFC-PR-031.
- assumptions: None.
- constraints: PR-030 launch; PR-032 unknown.
- gate: PASS.

### AFC-PR-032 — Unknown access marking
- statement: The system shall mark game access it cannot verify as unknown.
- source: #1 item 4 (unknown stays unknown).
- rationale: The explicit unknown-access behavior: doubt is displayed, never smoothed over.
- allocation: RESOLVER, LAUNCHER.
- verification: test, system, backend + TV surfaces. Criteria: positive — unverifiable access reads unknown on alerts, Watch routing, and panel; negative — no unverified access reads verified or included; check VCASE-AFC-PR-032.
- assumptions: None.
- constraints: PR-004 verified rule; PR-031 enum.
- gate: PASS.

### AFC-PR-033 — Inclusion promise withholding
- statement: The system shall withhold any promise that a game is included merely because the provider app is installed.
- source: #1 items 1, 4 (installed is not subscribed).
- rationale: The companion must never sell access it cannot confirm.
- allocation: RESOLVER, LAUNCHER.
- verification: test, system, backend + TV surfaces. Criteria: positive — installed-without-verified-subscription reads unknown per PR-032; negative — any inclusion promise from install fact alone fails; check VCASE-AFC-PR-033.
- assumptions: None.
- constraints: PR-003 install reporting; PR-004 verified rule.
- gate: PASS (prohibition is the need; positive form).

### AFC-PR-034 — Provider preference choice
- statement: The backend shall choose among available services by the customer's provider preference.
- source: #1 items 4, 6 (provider preference).
- rationale: The customer decides which of their services wins a contested game.
- allocation: PROFILE, RESOLVER.
- verification: test, system, backend + settings UI. Criteria: positive — preference change reroutes a contested game; negative — no available-service choice contradicts the recorded preference; check VCASE-AFC-PR-034.
- assumptions: None.
- constraints: PR-029 resolution inputs.
- gate: PASS.

### AFC-PR-035 — Switching confirmation honor
- statement: The TV app shall honor the customer's switching-confirmation setting for every viewing switch.
- source: #1 items 4, 6 (switching confirmation).
- rationale: Unconfirmed channel switches would hijack the customer's viewing.
- allocation: PROFILE, LAUNCHER.
- verification: demonstration, system, real stick (SD-001). Criteria: positive — confirmation-required setting blocks switching until confirmed; negative — no automatic switch unless explicitly configured and supported; check VCASE-AFC-PR-035.
- assumptions: Supported switch mechanisms identified by the Phase 2 spike.
- constraints: PR-030 Watch launch.
- gate: PASS.

### AFC-PR-036 — Alexa tuning conditional offer
- statement: The TV app shall offer Alexa-assisted tuning for the resolved game or channel only when the customer enables voice control over an implemented and verified Alexa route.
- source: #1 item 4 (Alexa-assisted tuning); SD-008; C8.
- rationale: Alexa is an additional voice route, never an assumed capability.
- allocation: LAUNCHER.
- verification: demonstration, tv-app, real stick (SD-001). Criteria: positive — enabled control over a verified route offers tuning; negative — no Alexa offer when disabled or the route is unverified; check VCASE-AFC-PR-036.
- assumptions: Alexa stretch scope (OD-AFC-03) returns at the Phase 2 review; route verified by spike or absent.
- constraints: C8 enforced_rule; external interface Alexa voice route (conditional).
- gate: PASS.

### AFC-PR-037 — Detection personalization opt-in
- statement: The system shall use detection data and profile-based personalization only while the customer opts in to detection and personalization.
- source: #1 item 6 (use of detection/personalization).
- rationale: The master switch for sensing and personalization.
- allocation: PROFILE, POLICY.
- verification: test, system, backend + settings UI. Criteria: positive — opt-out yields monitoring without detection data or personalization; negative — no detection-basis decision while opted out (labels per PR-011); check VCASE-AFC-PR-037.
- assumptions: None.
- constraints: PR-010 viewing detection; PR-011 labels.
- gate: PASS.

### AFC-PR-038 — Device-code account linking
- statement: The backend shall link the TV app to the customer account through a device code the customer completes on a phone or browser.
- source: #1 item 6 (device-code linking sufficient).
- rationale: TV-friendly linking without typing credentials on the stick.
- allocation: AUTH, API.
- verification: demonstration, system, real stick + phone/browser page. Criteria: positive — code entry on phone/browser links the TV app; negative — no link completes without the customer's code action; check VCASE-AFC-PR-038.
- assumptions: QR is an optional convenience, not required.
- constraints: C9 credentials owner-handled; interface device-link page.
- gate: PASS.

### AFC-PR-039 — Panel lineup content
- statement: The TV app shall display the selected fantasy team's lineup with each player's fantasy points and game status and the team total and progress under the league's scoring context.
- source: #1 right-side panel (required experience).
- rationale: The panel's core content: my players, my points, my progress.
- allocation: PANEL, PANELSVC.
- verification: demonstration, system, real stick (SD-001) + backend; evidence under evidence/visual/ (SD-024). Criteria: positive — lineup, points, statuses, and total match the Yahoo league context (or PR-065 default table for manual); negative — no value shown without its scoring basis; check VCASE-AFC-PR-039.
- assumptions: None.
- constraints: PR-065 manual scoring; PR-040 staleness.
- gate: PASS.

### AFC-PR-040 — Stale value labeling
- statement: The TV app shall label each unavailable or stale panel value as unavailable or stale.
- source: #1 right-side panel (stale/unavailable marks).
- rationale: The explicit stale-data behavior: age and absence are visible.
- allocation: PANEL, PANELSVC.
- verification: demonstration, tv-app, real stick (SD-001). Criteria: positive — withheld feed and missing value produce stale and unavailable labels; negative — no silently old or silently missing value; staleness bound is open parameter stale_after (owner Phase 2 design, close by Phase 2 plan approval, evidence design review against feed cadence); check VCASE-AFC-PR-040.
- assumptions: stale_after defined at Phase 2 design.
- constraints: PR-012 timestamps; PR-026 corrections.
- gate: PASS (open value per CHK-RE-10).

### AFC-PR-041 — Unobscured video fit
- statement: The TV app shall fit the broadcast video into the screen area remaining beside the right-side lineup panel while preserving broadcast aspect ratio.
- source: #1 right-side panel (unobscured video); SD-006.
- rationale: The panel supplements viewing; it must never cover or crop the broadcast.
- allocation: PANEL, SHELL.
- verification: demonstration, tv-app, real stick (SD-001); evidence under evidence/visual/ (SD-024). Criteria: positive — simultaneous panel and video with no overlap and preserved aspect (dimension-compared capture); negative — any overlap or crop fails; check VCASE-AFC-PR-041.
- assumptions: Provider-video route verified by the panel spike, else PR-047 Mode A.
- constraints: C5 fallback.
- gate: PASS.

### AFC-PR-042 — Remote panel team control
- statement: The TV app shall switch panel visibility and the followed team and league from TV remote input.
- source: #1 right-side panel (show/hide, team/league).
- rationale: Core panel controls operable from the couch.
- allocation: PANEL, PROFILE.
- verification: demonstration, tv-app, real stick (SD-001); evidence under evidence/visual/ (SD-024). Criteria: positive — remote toggles visibility and changes team/league; negative — no panel control requires another input device; check VCASE-AFC-PR-042.
- assumptions: None.
- constraints: PR-043 remote operation.
- gate: PASS (subject is the TV app, not the customer).

### AFC-PR-043 — Remote panel operation
- statement: The lineup panel shall accept all panel operations from TV remote input.
- source: #1 right-side panel (remote navigable).
- rationale: Full panel use without leaving the couch.
- allocation: PANEL.
- verification: demonstration, tv-app, real stick (SD-001); evidence under evidence/visual/ (SD-024). Criteria: positive — every focusable element reachable with a visible focus indicator; negative — no remote-dead operation; check VCASE-AFC-PR-043.
- assumptions: None.
- constraints: PR-042 visibility/team control.
- gate: PASS.

### AFC-PR-044 — Panel settings reflection
- statement: The lineup panel shall reflect the customer's team, league, and display settings.
- source: #1 right-side panel (consistent with settings).
- rationale: The panel is a view of the customer's settings, not a second configuration.
- allocation: PANEL, PANELSVC.
- verification: test, system, backend + TV panel. Criteria: positive — settings change appears on the panel; negative — no panel content contradicts recorded settings; check VCASE-AFC-PR-044.
- assumptions: None.
- constraints: PR-002 selections; PR-021 presentation.
- gate: PASS.

### AFC-PR-045 — Couch legibility acceptance
- statement: The lineup panel shall present lineup text the owner accepts as legible from the couch on the target device.
- source: #1 right-side panel (legible from the couch).
- rationale: Couch legibility is judged by the owner on the real target, not by proxy metrics.
- allocation: PANEL.
- verification: demonstration, tv-app, real stick (SD-001). Criteria: positive — owner accepts lineup text as couch-legible in the demonstration; negative — owner rejection fails the case; check VCASE-AFC-PR-045.
- assumptions: A numeric minimum, if the owner wants one, is set at owner review (see owner question Q3).
- constraints: PR-041 layout.
- gate: PASS (named judge, named target, and demonstration constitute the observable).

### AFC-PR-046 — Lineup alert consistency
- statement: The system shall hold lineup panel state consistent with alerts across starter changes and scoring corrections.
- source: #1 right-side panel (consistency rule).
- rationale: Panel and alerts are two views of one truth.
- allocation: PANELSVC, POLICY.
- verification: test, system, AWS deployment. Criteria: positive — starter change and correction reach both surfaces with identical corrected facts; negative — no fact present in one surface and contradicted in the other (suppressed alerts do not break fact agreement; hidden panel refreshes on show); check VCASE-AFC-PR-046.
- assumptions: None.
- constraints: PR-026 propagation; PR-061 hidden-panel behavior.
- gate: PASS.

### AFC-PR-047 — Mode A panel fallback
- statement: When the panel-beside-provider-video spike fails or exceeds 24 hours from first app install, the TV app shall present the lineup panel beside its own player with labeled sample footage.
- source: #1 panel integration obligation; SD-006; C5.
- rationale: A working panel demonstration survives provider-composition failure, honestly labeled.
- allocation: PANEL, PLAYER.
- verification: demonstration, tv-app, real stick (SD-001); evidence under evidence/visual/ (SD-024). Criteria: positive — panel beside own player with footage label visible; negative — no silent substitution of phone screen, app-switch dashboard, or covering panel; check VCASE-AFC-PR-047.
- assumptions: Spike verdict recorded with elapsed time; footage storage location is owner question Q4.
- constraints: C5 expected_outcome; PR-049/050/051 footage rules; submission states the limitation.
- gate: PASS.

### AFC-PR-048 — Mode A provider routing
- statement: Under Mode A fallback, the TV app shall route alerts and Watch actions to the real provider apps.
- source: SD-006 (alerts and Watch still go to real providers).
- rationale: Mode A degrades only the panel video route, never alerting or handoff.
- allocation: NOTIFIER, LAUNCHER.
- verification: demonstration, system, real stick (SD-001). Criteria: positive — Mode A alert Watch opens the real provider route; negative — no Mode A alert or Watch trapped in the sample player; check VCASE-AFC-PR-048.
- assumptions: None.
- constraints: C5; PR-015 alerts; PR-030 Watch.
- gate: PASS.

### AFC-PR-049 — Sample footage sourcing
- statement: Mode A sample footage shall carry a CC-BY or CC0 license with credit.
- source: SD-006a (footage licensing).
- rationale: Lawful, credited sample content for the Mode A demonstration.
- allocation: PLAYER.
- verification: inspection, tv-app, source and submission review. Criteria: positive — license file and credit name the footage; negative — no unlicensed or uncredited footage ships; check VCASE-AFC-PR-049.
- assumptions: None.
- constraints: PR-050 label; PR-051 NFL exclusion.
- gate: PASS (split from the combined footage row in self-correction per CHK-RE-15).

### AFC-PR-050 — Sample footage labeling
- statement: Mode A playback shall display the label 'Sample footage — not a live broadcast'.
- source: SD-006a (footage labeling).
- rationale: The label prevents any reading of sample footage as a live broadcast.
- allocation: PLAYER.
- verification: inspection, tv-app, real stick playback review. Criteria: positive — label visible during Mode A playback; negative — no unlabeled Mode A playback; check VCASE-AFC-PR-050.
- assumptions: None.
- constraints: PR-049 sourcing; PR-051 NFL exclusion.
- gate: PASS (split from the combined footage row in self-correction per CHK-RE-15).

### AFC-PR-051 — NFL footage exclusion
- statement: Mode A sample footage shall exclude NFL footage.
- source: SD-006a (no NFL footage).
- rationale: Rights protection for the demonstration.
- allocation: PLAYER.
- verification: inspection, tv-app, source and submission review. Criteria: positive — footage manifest lists only non-NFL sources; negative — any NFL footage present fails; check VCASE-AFC-PR-051.
- assumptions: None.
- constraints: PR-049 sourcing.
- gate: PASS (prohibition is the need; positive form).

### AFC-PR-052 — Fire TV stick target
- statement: The TV app shall run on the 2018 Fire TV stick target on Fire OS.
- source: SD-003; SD-002 context; C1.
- rationale: The owner's device is the target; no purchase, no silent platform switch.
- allocation: SHELL, MANIFEST.
- verification: demonstration, tv-app, real 2018 stick (SD-001). Criteria: positive — install, launch, and operate on the target; negative — no target-only failure waived without a C1 owner return; check VCASE-AFC-PR-052.
- assumptions: Exact model unconfirmed (minSdk 25 provisional per SD-003); starter is hello-world-fire-tv (build method); newer device acceptable per SD-002 only by owner direction.
- constraints: C1 enforced_rule (Fire OS 5/older/unable → return to owner; never buy or switch); SD-001.
- gate: PASS.

### AFC-PR-053 — Minimum SDK declaration
- statement: The TV app build shall declare minSdk 25.
- source: SD-003.
- rationale: Pins the provisional floor the target assumes.
- allocation: BUILD.
- verification: inspection, tv-app, source review of build.gradle.kts. Criteria: positive — declaration reads 25; negative — any other value fails; check VCASE-AFC-PR-053.
- assumptions: Provisional until the stick model is confirmed (then C1 or confirmation).
- constraints: C1; PR-052 target.
- gate: PASS.

### AFC-PR-054 — Free-tier serverless hosting
- statement: The backend shall run on AWS serverless services within the Free tier declared in template.yaml.
- source: SD-005; SD-008 (AWS Builder services); C4.
- rationale: Owner-created Free-plan account bounds cost; serverless matches the workload.
- allocation: IAC.
- verification: inspection, backend, template.yaml review + deployment record. Criteria: positive — only Free-tier services (Lambda, HTTP API, DynamoDB on-demand, Scheduler, SSM) declared and deployed; negative — any paid service or undeleted paid resource fails; check VCASE-AFC-PR-054.
- assumptions: Owner creates the Free-plan account (milestone 1 entry).
- constraints: C4 enforced_rule (Free → Paid only by owner decision).
- gate: PASS.

### AFC-PR-055 — Server-side secret holding
- statement: The backend shall hold Yahoo OAuth client secrets and tokens only in SSM SecureString parameters.
- source: SD-007; C9.
- rationale: Secrets stay server-side and owner-handled, never in the APK or repo.
- allocation: SECRET, IAC.
- verification: inspection, backend, source + APK + parameter review. Criteria: positive — parameters exist and code reads only them; negative — any secret value in APK or repo fails; check VCASE-AFC-PR-055.
- assumptions: Owner sets secret values (C9).
- constraints: C9 enforced_rule.
- gate: PASS.

### AFC-PR-056 — Absolute path exclusion
- statement: The TV app and backend sources shall contain no local absolute path.
- source: SD-010; C7.
- rationale: Committed absolute paths leak the builder's machine and break other checkouts.
- allocation: BUILD, IAC.
- verification: inspection, system, repository grep over tracked sources. Criteria: positive — grep for home-rooted and root-anchored local paths returns nothing; negative — any committed local absolute path blocks per C7; check VCASE-AFC-PR-056.
- assumptions: None.
- constraints: C7 enforced_rule.
- gate: PASS.

### AFC-PR-057 — Messaging feature exclusion
- statement: The system shall exclude messenger, message board, community room, shared chat, and watch-party social features.
- source: #1 explicit exclusion (owner decision 10-10).
- rationale: Out of scope by owner decision; the register must say so plainly.
- allocation: SHELL, API.
- verification: inspection, system, source and UI review. Criteria: positive — no messaging surface or endpoint exists; negative — any listed feature present fails; check VCASE-AFC-PR-057.
- assumptions: None.
- constraints: Exclusion binds submission content as well.
- gate: PASS (prohibition is the need; positive form).

### AFC-PR-058 — Backend API operations
- statement: The backend shall expose link, profile, alerts, panel, and provider operations to the TV app.
- source: #1 source review (proposed data flow); #1 items 1, 3, 4, 6; panel.
- rationale: The TV↔backend contract surface the product behaviors need.
- allocation: API.
- verification: test, system, deployed API. Criteria: positive — each operation responds per its contract; negative — no TV behavior depends on an unexposed operation; check VCASE-AFC-PR-058.
- assumptions: REST over HTTP API; exact schemas at Phase 2 design.
- constraints: Internal interface TV app ↔ backend API; PR-038 link; PR-058-series consumers.
- gate: PASS.

### AFC-PR-059 — Backend aggregation placement
- statement: The backend shall perform API aggregation, full-game monitoring, cross-provider matching, and commentary generation.
- source: #1 lightweight device design.
- rationale: Heavy work stays off the stick.
- allocation: INGEST, MATCHER, POLICY.
- verification: inspection, backend, source review. Criteria: positive — each listed function implemented backend-side; negative — no listed function implemented TV-side; check VCASE-AFC-PR-059.
- assumptions: None.
- constraints: PR-060 small updates; no hardware benchmark gate (owner direction).
- gate: PASS.

### AFC-PR-060 — Relevant update filtering
- statement: The backend shall send the TV app only updates relevant to the customer profile.
- source: #1 lightweight device design.
- rationale: Small relevant updates keep the TV light and the customer unbothered.
- allocation: API.
- verification: test, backend, AWS deployment. Criteria: positive — update stream for a fixture profile contains only profile-relevant updates; negative — any irrelevant update fails; check VCASE-AFC-PR-060.
- assumptions: None.
- constraints: PR-008 relevance; PR-059 placement.
- gate: PASS.

### AFC-PR-061 — Burst update coalescing
- statement: The TV app shall coalesce burst updates into changed rows and values.
- source: #1 lightweight device design.
- rationale: No whole-screen rerenders or tickers on a small stick.
- allocation: PANEL, NOTIFIER.
- verification: test, tv-app, instrumented build or review. Criteria: positive — burst input updates only changed rows/values; negative — whole-screen rerender on a burst fails; hidden panel suspends update application and refreshes on show; check VCASE-AFC-PR-061.
- assumptions: None.
- constraints: PR-046 consistency; no hardware benchmark gate.
- gate: PASS.

### AFC-PR-062 — Bounded TV resource caches
- statement: The TV app's alert and panel components shall bound their event queues, retained history, images, and caches.
- source: #1 lightweight device design.
- rationale: Declared bounds replace hope as the memory story; measurement stays excluded.
- allocation: ALERTSVC, PANEL.
- verification: inspection, tv-app, source review. Criteria: positive — each named resource has a declared limit; negative — any unbounded named resource fails; check VCASE-AFC-PR-062.
- assumptions: None.
- constraints: 100 MB background-RAM figure is a Fire OS design reference only, not a measured claim.
- gate: PASS.

### AFC-PR-063 — Off-thread TV work
- statement: The TV app's alert, panel, and detector components shall keep network work, parsing, and computation off the rendering thread.
- source: #1 lightweight device design.
- rationale: The render thread stays free so the UI never janks on I/O.
- allocation: ALERTSVC, PANEL, DETECTOR.
- verification: inspection, tv-app, source review. Criteria: positive — network, parse, and compute paths dispatch off the render thread; negative — any such work on the render thread fails; check VCASE-AFC-PR-063.
- assumptions: None.
- constraints: Background delivery uses supported OS mechanisms.
- gate: PASS.

### AFC-PR-064 — Invalid feed rejection
- statement: The backend shall reject a schema-invalid ESPN response without changing stored events.
- source: #1 item 2 (validation at ingest); SD-004.
- rationale: A malformed poll must never corrupt the event cache.
- allocation: INGEST.
- verification: test, backend, AWS deployment. Criteria: positive — invalid fixture rejected, stored events byte-identical; negative — any partial store from an invalid response fails; check VCASE-AFC-PR-064.
- assumptions: Schema defined from the observed contract at integration.
- constraints: PR-012 ingest; PR-013 contract-change trigger.
- gate: PASS (added in self-correction; fault case was implicit per CHK-RE-43/50).

### AFC-PR-065 — Manual scoring table
- statement: The backend shall score manual lineups under a documented default scoring table naming each counted statistic and its point coefficient.
- source: #1 right-side panel (league scoring context); SD-007 manual entry.
- rationale: Manual lineups have no Yahoo league context; a label alone cannot establish correct points.
- allocation: PANELSVC, LINEUP.
- verification: test, backend, AWS deployment. Criteria: positive — manual lineup points equal the table applied to feed statistics; negative — any manual point without a table row fails; manual scoring labeled 'Default scoring'; check VCASE-AFC-PR-065.
- assumptions: Table authored at Phase 2 design.
- constraints: PR-006 manual source; PR-039 panel content.
- gate: PASS (added in self-correction; manual scoring was incomplete per CHK-RE-17).

## Self-correction pass (round 1 of 1; no further rounds needed)

1. AFC-PR-015 rewrite (CHK-RE-24 CONTRADICTION): original "The TV app shall present each alert as a
   heads-up notification ..." contradicted panel-only presentation (PR-021). Fixed with the
   "While heads-up presentation is selected" condition. Re-gated: PASS.
2. Footage row split (CHK-RE-15 COMPOUND): original single row carried license, credit, and label
   duties. Split into AFC-PR-049 (license with credit), AFC-PR-050 (label display); AFC-PR-051
   (NFL exclusion) unchanged. Re-gated: PASS.
3. AFC-PR-064 added (CHK-RE-43 FAULT_RESPONSE_MISSING, CHK-RE-50 IMPLICIT_IRRELEVANT_CASE):
   schema-invalid ESPN responses had no specified disposition. Gated: PASS.
4. AFC-PR-065 added (CHK-RE-17 INCOMPLETE): manual lineups had no scoring rule. Gated: PASS.
5. Open parameters with owner, close-by date, and closure evidence (CHK-RE-10): close_game_margin
   (PR-014), excitement_levels (PR-023), stale_after (PR-040). PR-045 legibility stays
   owner-acceptance-based (see owner question Q3).

Set-level checks: no smuggled design/operations/tasking (CHK-RE-21/22/23; owner-mandated placements
cite SD/C); no contradictions (CHK-RE-24; filter chain PR-014/016/017/018/019/020 applies conjunctively;
PR-041 and PR-047 agree under C5); terms stable per AFC-SEC-TERMS (CHK-RE-25/26); every row traces to
#1/SD/C (CHK-RE-27/28/30); interfaces named per row (CHK-RE-37/38; full IFACE-PROFILE-EMV-001
treatment belongs to ST-3b interface modeling, not this register); every row carries method, case, and
positive/negative criteria (CHK-RE-47/48). CHK-RE-31 N/A (draft register; baseline at ST-5 owner
review). CHK-RE-42 N/A (no reliability claim beyond specified fault responses).

## Validation and binding evidence

- StrictDoc bridge: not run (no input file; WRITE_BLOCKED_RS_GUARD). Intended command: the RS
  `strictdoc_bridge.py --protocol alphazede.strictdoc.bridge --schema-version 2 --mode sdoc` form
  from use-requirements-system §4, with root and source at the plan directory and
  `afc-product-requirements.sdoc`. Require `status: ok`, `validation.status: valid`.
- `lint-sdoc.py`: not run (same block). Intended: `python3 tools/coe/lint-sdoc.py <sdoc>` from the
  shared-skills checkout; require exit 0 with `lint_profile: project-specification` declared.
- Probe (mechanics only, 1 requirement + 1 element node in a scratch dir): bridge `status: ok`,
  `validation.status: valid`; lint exit 0. Establishes the grammar/relation pattern, not this register.
- Host: local packaged-default Requirements System host, port from
  `$XDG_RUNTIME_DIR/alphazede-requirements-system/host.port`; `/readyz` ready true at session start.
  `checkout list` shows only MID-MAESTRO-SPECIFICATION-CORE-0001 (active, untouched).
- Binding: attempted `checkout create` for this document; exact error recorded under Typed gaps
  (BINDING_BLOCKED_NO_FILE). No checkout created. `rs_status: host_binding_pending` for this document
  until the file exists; then mint fresh MIDs and re-run create (do not reuse the Maestro checkout).

## Intended .sdoc shape (for materialization)

[DOCUMENT] TITLE Amazon Fantasy Companion Product Requirements Register, UID AFC-PRODUCT-REQUIREMENTS,
VERSION 0.1, ENABLE_MID True, MARKUP Text; METADATA type product-requirements-register,
lint_profile project-specification, lifecycle AFC-ST-2026-10-12, step ST-2. [GRAMMAR] TEXT nodes with
MID/UID/STATEMENT; REQUIREMENT nodes with the 22 core fields; RELATIONS Parent derives-from, Child
implemented-by. [TEXT] sections AFC-SEC-SCOPE/COND/TERMS/EVID per this receipt's coverage and evidence
notes; [TEXT] element nodes AFC-EL-SHELL/BUILD/MANIFEST/PROFILE/DETECTOR/ALERTSVC/NOTIFIER/LAUNCHER/
PANEL/PLAYER/IAC/AUTH/API/INGEST/REPLAY/LINEUP/MATCHER/POLICY/RESOLVER/PANELSVC/SECRET/STORE with the
planned paths from sm-contextual-pass.md §2. One REQUIREMENT node per AFC-PR row above with the stated
fields; RELATIONS implemented-by to its elements. Node separator exactly one blank line.

## Owner questions (list only)

1. Guard vs OD-AFC-12: grant a guard exception for `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/afc-product-requirements.sdoc`,
   amend OD-AFC-12 to a managed-root path, or direct another placement? (Blocks ST-2 persistence, validation, binding.)
2. Excitement-level scale: is the level set (with off always present) a Phase 2 design choice, or do you
   want the scale fixed in the register now?
3. Couch legibility (AFC-PR-045): is owner acceptance on the target device sufficient, or do you want a
   numeric minimum (e.g., text size) in the register?
4. Mode A footage storage location if the panel spike selects Mode A (carried open item F12)?
5. Which real provider supplies the first supported game/channel link contract in the Phase 2 spike?
6. Stick located and exact model/OS confirmed? (C1 trigger; milestone 1 entry.)
7. Yahoo application submitted and approval status? (C6/T_yahoo timing.)
8. AWS Free-plan account created? (SD-005; milestone 1 entry.)
9. License choice before the repo visibility flip? (Deferred per scope batch; affects publication.)
10. Restore the missing `engineering-methods` S8 ledger in the skills tree, or waive it (citations use the
    embedded S8 rows; nothing invented)?

## developer_feedback (AC-AFC-DX-04 fields that apply; Scribe contract IDs local to this return)

No submission-scale friction; one blocker and one observation recorded as S8-ledger and guard items above.

- ID RE-ST2-001, reporting role Requirements Engineer (planning session), task ST-2 register draft and gate,
  tool Requirements System guard hook (requirements-system-guard.sh via edit-file PreToolUse).
  Task attempted: write the OD-AFC-12-mandated draft `.sdoc` in the spec-track plan directory.
  Expected: write succeeds (owner-approved plan path). Actual: write refused; `.sdoc` outside
  `docs/coe` or `migrations/<project>` is blocked. Impact: ST-2 persistence, StrictDoc/lint validation,
  and host binding all blocked; full draft + gate preserved in this receipt instead. Workaround: none
  taken (refused checks are not routed around). Actionable suggestion: reconcile the guard's managed-root
  rule with OD-AFC-12 (exception list, amended path, or plan-dir allowance for draft registers).
  Classification: configuration/environment issue (policy conflict, not a product defect).
- ID RE-ST2-002, reporting role Requirements Engineer (planning session), task ST-2 register draft and gate,
  tool skills tree (`requirements-engineering` S8 ledger path). Task attempted: resolve
  `engineering-methods/references/standards-receipts.md`. Expected: ledger present. Actual: absent;
  citations use the S8 rows embedded in the method references. Impact: none on gate content; recorded as
  observation S8-LEDGER-MISSING with an owner question. Classification: configuration/environment issue.
- Tools exercised: `read_skill` (requirements-engineer, requirements-engineering, use-requirements-system),
  `gh api` (issue #1 body), file reads (scope batch, technical plan, journey, sm-contextual-pass.md),
  StrictDoc bridge + `lint-sdoc.py` (probe only), `alphazede-requirements-system checkout list/create`,
  host `/readyz` + `/v1/workspace` reads. No new positive/negative product observations beyond the two
  items above.
