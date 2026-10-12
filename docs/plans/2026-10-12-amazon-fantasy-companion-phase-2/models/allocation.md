---
type: allocation-mapping
title: AFC register UID to SysML v2 model element allocation (ST-3c)
okf_status: draft
tags: [modeling, planning, afc, spec-track]
---

# AFC allocation: register UID ↔ model element (ST-3c)

Register of record: `requirements-register.md` (65 UIDs AFC-PR-001..065,
gated PASS at ST-2b per DEC-AFC-SD-027). Model sources: `models/AFC-*.sysml`
(packages AFCStructure, AFCInterfaces, AFCStates, AFCData), revision digest
`14fb815b78c2c6817d556c36d351b22dd3996db5f5a7e34a87251ce69bfdcfe5`
(ST-3d revision; ST-3b/c revision was
`d16b0e3d0badb519dce178475a5a4b6694a736c0bbb0062d51a0270d64efb632`).

Element names are dotted paths as declared in the `.sysml` sources
(`tvApp.panel`, `BackendDeviceLink`, `AlertLifecycle.matched`,
`GameEvent.score`, `RoutingOutcome.gameOpened`). Packages are namespaces and
carry no allocation.

Granularity rule (per `views.md` decision 2): parts, port defs and port
usages, interface defs, state defs, states, signals, item/enum defs. Owned
detail — interface ends, attributes, enum values, transitions — inherits its
parent def allocation and is listed per item in Table 2 as `via <parent>`.
Port defs inherit the allocation of their port usages; signals inherit the
allocation of their consuming state def.

## Table 1 — UID → model elements (65/65)

| UID | Model elements |
|---|---|
| AFC-PR-001 | backend.lineup, backend.yahooPort, BackendYahoo, externals.yahoo, Lineup |
| AFC-PR-002 | tvApp.profileUI, backend.api, stores, stores.profileStore, TvBackendApi, Settings |
| AFC-PR-003 | tvApp.detector |
| AFC-PR-004 | backend.resolver, backend.api |
| AFC-PR-005 | tvApp.profileUI, stores.profileStore, Settings |
| AFC-PR-006 | backend.lineup, externals.manualEntry, externals.yahoo, BackendYahoo, Lineup |
| AFC-PR-007 | backend.lineup, externals.yahoo, BackendYahoo, Lineup |
| AFC-PR-008 | backend.ingest, backend.policy, GameEvent |
| AFC-PR-009 | tvApp.profileUI, backend.policy, Settings |
| AFC-PR-010 | tvApp.detector, tvApp.profileUI, Settings |
| AFC-PR-011 | backend.policy |
| AFC-PR-012 | backend.ingest, backend.espnPort, BackendEspn, externals.espn, GameEvent, stores.eventStore |
| AFC-PR-013 | backend.replay, backend.ingest, stores.fixtures, BackendEspn, externals.espn, GameEvent |
| AFC-PR-014 | backend.policy, backend.matcher, AlertLifecycle, AlertLifecycle.detected, AlertLifecycle.matched, AlertLifecycle.emitted, Alert |
| AFC-PR-015 | tvApp.notifier, tvApp.alertSvc, tvApp.manifest, tvApp.notifyPort, TvFireOSNotify, externals.fireOSNotify, AlertLifecycle.delivered, Alert |
| AFC-PR-016 | tvApp.profileUI, backend.policy, AlertLifecycle.suppressed, Settings |
| AFC-PR-017 | tvApp.profileUI, backend.policy, AlertLifecycle.suppressed, Settings |
| AFC-PR-018 | tvApp.profileUI, backend.policy, AlertLifecycle.suppressed, Settings |
| AFC-PR-019 | tvApp.profileUI, backend.policy, AlertLifecycle.suppressed, Settings |
| AFC-PR-020 | tvApp.profileUI, backend.policy, AlertLifecycle.gated, AlertLifecycle.delivered, Settings |
| AFC-PR-021 | tvApp.profileUI, tvApp.notifier, Settings |
| AFC-PR-022 | tvApp.profileUI, tvApp.notifier, TvAlexa, externals.alexaRoute, Settings |
| AFC-PR-023 | tvApp.profileUI, backend.policy, Alert, Settings |
| AFC-PR-024 | backend.matcher, IngestMatcherPolicy, AlertLifecycle.matched |
| AFC-PR-025 | backend.matcher, backend.policy, stores.eventStore, IngestMatcherPolicy, AlertLifecycle.emitted, Alert |
| AFC-PR-026 | backend.matcher, backend.policy, backend.panelSvc, IngestMatcherPolicy, AlertLifecycle.corrected, PanelState, Alert |
| AFC-PR-027 | backend.policy, backend.matcher, Alert |
| AFC-PR-028 | backend.policy, Alert |
| AFC-PR-029 | backend.resolver, externals.providerApps, TvProviderLaunch, Alert |
| AFC-PR-030 | tvApp.launcher, tvApp.launchPort, TvProviderLaunch, externals.providerApps |
| AFC-PR-031 | tvApp.launcher, externals.providerApps, TvProviderLaunch, RoutingOutcome |
| AFC-PR-032 | backend.resolver, tvApp.launcher, TvProviderLaunch, RoutingOutcome |
| AFC-PR-033 | backend.resolver, tvApp.launcher, TvProviderLaunch, RoutingOutcome |
| AFC-PR-034 | tvApp.profileUI, backend.resolver, Settings |
| AFC-PR-035 | tvApp.profileUI, tvApp.launcher, Settings |
| AFC-PR-036 | tvApp.launcher, tvApp.alexaPort, TvAlexa, externals.alexaRoute |
| AFC-PR-037 | tvApp.profileUI, backend.policy, Settings |
| AFC-PR-038 | backend.auth, backend.api, backend.linkPort, BackendDeviceLink, DeviceLink, DeviceLink.unlinked, DeviceLink.codePending, DeviceLink.linked, DeviceLink.expired, DeviceCode, externals.linkConsumer, TvBackendApi |
| AFC-PR-039 | tvApp.panel, backend.panelSvc, PanelState, Lineup |
| AFC-PR-040 | tvApp.panel, backend.panelSvc, PanelState |
| AFC-PR-041 | tvApp.panel, tvApp.shell, PanelMode, PanelMode.modeB |
| AFC-PR-042 | tvApp.panel, tvApp.profileUI, PanelState, Settings |
| AFC-PR-043 | tvApp.panel |
| AFC-PR-044 | tvApp.panel, backend.panelSvc, PanelState, Settings |
| AFC-PR-045 | tvApp.panel |
| AFC-PR-046 | backend.panelSvc, backend.policy, PanelState, Alert |
| AFC-PR-047 | tvApp.panel, tvApp.player, PanelMode, PanelMode.modeB, PanelMode.modeA |
| AFC-PR-048 | tvApp.notifier, tvApp.launcher, TvProviderLaunch, TvFireOSNotify, PanelMode.modeA |
| AFC-PR-049 | tvApp.player |
| AFC-PR-050 | tvApp.player |
| AFC-PR-051 | tvApp.player |
| AFC-PR-052 | tvApp, tvApp.shell, tvApp.manifest, TvFireOSNotify, externals.fireOSNotify |
| AFC-PR-053 | tvApp.build |
| AFC-PR-054 | backend, backend.iac |
| AFC-PR-055 | stores.secrets, backend.iac, BackendYahoo |
| AFC-PR-056 | tvApp.build, backend.iac |
| AFC-PR-057 | tvApp.shell, backend.api, TvBackendApi |
| AFC-PR-058 | backend.api, tvApp.apiPort, backend.apiPort, TvBackendApi |
| AFC-PR-059 | backend.ingest, backend.matcher, backend.policy, IngestMatcherPolicy |
| AFC-PR-060 | backend.api, TvBackendApi |
| AFC-PR-061 | tvApp.panel, tvApp.notifier, PanelState |
| AFC-PR-062 | tvApp.alertSvc, tvApp.panel |
| AFC-PR-063 | tvApp.alertSvc, tvApp.panel, tvApp.detector |
| AFC-PR-064 | backend.ingest, BackendEspn, externals.espn, GameEvent, stores.eventStore |
| AFC-PR-065 | backend.panelSvc, backend.lineup, PanelState, Lineup |

## Table 2 — model element → UIDs (161 elements)

### AFCStructure: port defs, parts, ports

| Element | UIDs or reason |
|---|---|
| ApiPort | via tvApp.apiPort, backend.apiPort |
| NotifyPort | via tvApp.notifyPort |
| LaunchPort | via tvApp.launchPort |
| AlexaPort | via tvApp.alexaPort |
| EspnPort | via backend.espnPort |
| YahooPort | via backend.yahooPort |
| LinkPort | via backend.linkPort |
| tvApp | AFC-PR-052 |
| backend | AFC-PR-054 |
| stores | AFC-PR-002 |
| externals | Reason: grouping part for external endpoints; allocation held by member parts, no UID attaches to the grouping itself |
| tvApp.shell | AFC-PR-041, 052, 057 |
| tvApp.build | AFC-PR-053, 056 |
| tvApp.manifest | AFC-PR-015, 052 |
| tvApp.profileUI | AFC-PR-002, 005, 009, 010, 016, 017, 018, 019, 020, 021, 022, 023, 034, 035, 037, 042, 044 |
| tvApp.detector | AFC-PR-003, 010, 063 |
| tvApp.alertSvc | AFC-PR-015, 062, 063 |
| tvApp.notifier | AFC-PR-015, 021, 022, 048, 061 |
| tvApp.launcher | AFC-PR-030, 031, 032, 033, 035, 036, 048 |
| tvApp.panel | AFC-PR-039, 040, 041, 042, 043, 044, 045, 047, 061, 062, 063 |
| tvApp.player | AFC-PR-047, 049, 050, 051 |
| tvApp.apiPort | AFC-PR-058 |
| tvApp.notifyPort | AFC-PR-015 |
| tvApp.launchPort | AFC-PR-030 |
| tvApp.alexaPort | AFC-PR-036 |
| backend.auth | AFC-PR-038 |
| backend.api | AFC-PR-002, 004, 038, 057, 058, 060 |
| backend.ingest | AFC-PR-008, 012, 013, 059, 064 |
| backend.replay | AFC-PR-013 |
| backend.lineup | AFC-PR-001, 006, 007, 065 |
| backend.matcher | AFC-PR-014, 024, 025, 026, 027, 059 |
| backend.policy | AFC-PR-008, 009, 011, 014, 016, 017, 018, 019, 020, 023, 025, 026, 027, 028, 037, 046, 059 |
| backend.resolver | AFC-PR-004, 029, 032, 033, 034 |
| backend.panelSvc | AFC-PR-026, 039, 040, 044, 046, 065 |
| backend.iac | AFC-PR-054, 055, 056 |
| backend.apiPort | AFC-PR-058 |
| backend.espnPort | AFC-PR-012 |
| backend.yahooPort | AFC-PR-001 |
| backend.linkPort | AFC-PR-038 |
| stores.profileStore | AFC-PR-002, 005 |
| stores.eventStore | AFC-PR-012, 025, 064 |
| stores.secrets | AFC-PR-055 |
| stores.fixtures | AFC-PR-013 |
| externals.espn | AFC-PR-012, 013, 064 |
| externals.yahoo | AFC-PR-001, 006, 007 |
| externals.manualEntry | AFC-PR-006 |
| externals.providerApps | AFC-PR-029, 030, 031 |
| externals.fireOSNotify | AFC-PR-015, 052 |
| externals.alexaRoute | AFC-PR-022, 036 |
| externals.linkConsumer | AFC-PR-038 |

### AFCInterfaces: interfaces and ends

| Element | UIDs or reason |
|---|---|
| TvBackendApi | AFC-PR-002, 038, 057, 058, 060 |
| BackendEspn | AFC-PR-012, 013, 064 |
| BackendYahoo | AFC-PR-001, 006, 007, 055 |
| TvProviderLaunch | AFC-PR-029, 030, 031, 032, 033, 048 |
| TvFireOSNotify | AFC-PR-015, 048, 052 |
| TvAlexa | AFC-PR-022, 036 |
| BackendDeviceLink | AFC-PR-038 |
| IngestMatcherPolicy | AFC-PR-024, 025, 026, 059 |
| TvBackendApi.tvEnd | via TvBackendApi |
| TvBackendApi.backendEnd | via TvBackendApi |
| BackendEspn.backendEnd | via BackendEspn |
| BackendEspn.espnEnd | via BackendEspn |
| BackendYahoo.backendEnd | via BackendYahoo |
| BackendYahoo.yahooEnd | via BackendYahoo |
| TvProviderLaunch.tvEnd | via TvProviderLaunch |
| TvProviderLaunch.providerEnd | via TvProviderLaunch |
| TvFireOSNotify.tvEnd | via TvFireOSNotify |
| TvFireOSNotify.osEnd | via TvFireOSNotify |
| TvAlexa.tvEnd | via TvAlexa |
| TvAlexa.alexaEnd | via TvAlexa |
| BackendDeviceLink.backendEnd | via BackendDeviceLink |
| BackendDeviceLink.consumerEnd | via BackendDeviceLink |
| IngestMatcherPolicy.ingestEnd | via IngestMatcherPolicy |
| IngestMatcherPolicy.policyEnd | via IngestMatcherPolicy |

### AFCStates: state defs, states, signals, transitions

| Element | UIDs or reason |
|---|---|
| AlertLifecycle | AFC-PR-014 |
| PanelMode | AFC-PR-047 |
| DeviceLink | AFC-PR-038 |
| AlertLifecycle.detected | AFC-PR-014 |
| AlertLifecycle.matched | AFC-PR-014, 024 |
| AlertLifecycle.gated | AFC-PR-020 |
| AlertLifecycle.emitted | AFC-PR-014, 025 |
| AlertLifecycle.delivered | AFC-PR-015, 020 |
| AlertLifecycle.suppressed | AFC-PR-016, 017, 018, 019 |
| AlertLifecycle.corrected | AFC-PR-026 |
| PanelMode.modeB | AFC-PR-041, 047 |
| PanelMode.modeA | AFC-PR-047, 048 |
| DeviceLink.unlinked | AFC-PR-038 |
| DeviceLink.codePending | AFC-PR-038 |
| DeviceLink.linked | AFC-PR-038 |
| DeviceLink.expired | AFC-PR-038 |
| identify | via AlertLifecycle |
| passFilters | via AlertLifecycle |
| blockFilters | via AlertLifecycle |
| delayElapsed | via AlertLifecycle |
| present | via AlertLifecycle |
| correct | via AlertLifecycle |
| spikeFailed | via PanelMode |
| requestCode | via DeviceLink |
| userConfirm | via DeviceLink |
| codeTimeout | via DeviceLink |
| AlertLifecycle.t_detected_matched | via AlertLifecycle |
| AlertLifecycle.t_matched_gated | via AlertLifecycle |
| AlertLifecycle.t_matched_suppressed | via AlertLifecycle |
| AlertLifecycle.t_gated_emitted | via AlertLifecycle |
| AlertLifecycle.t_emitted_delivered | via AlertLifecycle |
| AlertLifecycle.t_emitted_corrected | via AlertLifecycle |
| AlertLifecycle.t_delivered_corrected | via AlertLifecycle |
| PanelMode.t_modeB_modeA | via PanelMode |
| DeviceLink.t_unlinked_pending | via DeviceLink |
| DeviceLink.t_pending_linked | via DeviceLink |
| DeviceLink.t_pending_expired | via DeviceLink |
| DeviceLink.t_expired_pending | via DeviceLink |

### AFCData: items, attributes, enum

| Element | UIDs or reason |
|---|---|
| GameEvent | AFC-PR-008, 012, 013, 064 |
| Alert | AFC-PR-014, 015, 023, 025, 026, 027, 029 |
| Lineup | AFC-PR-001, 006, 007, 039, 065 |
| PanelState | AFC-PR-026, 039, 040, 042, 044, 046, 061, 065 |
| Settings | AFC-PR-002, 005, 009, 016, 017, 018, 019, 020, 021, 022, 023, 034, 035, 037, 042, 044 |
| RoutingOutcome | AFC-PR-031, 032, 033 |
| DeviceCode | AFC-PR-038 |
| GameEvent.score | via GameEvent |
| GameEvent.fieldPosition | via GameEvent |
| GameEvent.possession | via GameEvent |
| GameEvent.playerIds | via GameEvent |
| GameEvent.eventTime | via GameEvent |
| GameEvent.correctionOf | via GameEvent |
| Alert.alertType | via Alert |
| Alert.triggerContext | via Alert |
| Alert.providerRoute | via Alert |
| Alert.commentary | via Alert |
| Alert.emittedAt | via Alert |
| Lineup.source | via Lineup |
| Lineup.team | via Lineup |
| Lineup.league | via Lineup |
| Lineup.starters | via Lineup |
| Lineup.scoring | via Lineup |
| PanelState.visible | via PanelState |
| PanelState.teamTotal | via PanelState |
| PanelState.progress | via PanelState |
| PanelState.freshness | via PanelState |
| Settings.fantasySelections | via Settings |
| Settings.teamLeague | via Settings |
| Settings.alertTypes | via Settings |
| Settings.frequency | via Settings |
| Settings.quietHours | via Settings |
| Settings.gameDayPeriods | via Settings |
| Settings.spoilerDelay | via Settings |
| Settings.presentation | via Settings |
| Settings.voice | via Settings |
| Settings.excitement | via Settings |
| Settings.providerPref | via Settings |
| Settings.switchingConfirm | via Settings |
| Settings.panelPrefs | via Settings |
| Settings.detectionOptIn | via Settings |
| RoutingOutcome.gameOpened | via RoutingOutcome |
| RoutingOutcome.searchOpened | via RoutingOutcome |
| RoutingOutcome.appHomeOpened | via RoutingOutcome |
| RoutingOutcome.appAbsent | via RoutingOutcome |
| RoutingOutcome.accessUnknown | via RoutingOutcome |
| RoutingOutcome.playbackDenied | via RoutingOutcome |
| DeviceCode.code | via DeviceCode |
| DeviceCode.expires | via DeviceCode |

## Coverage summary

- Table 1: 65/65 register UIDs allocated to ≥1 model element.
- Table 2: 161/161 model elements carry ≥1 UID, a `via <parent>`
  inheritance, or a stated reason (1 reason: `externals` grouping).
- Element counts: AFCStructure 50 (7 port defs, 4 tops, 31 subparts,
  8 port usages); AFCInterfaces 24 (8 defs, 16 ends); AFCStates 38
  (3 defs, 13 states, 10 signals, 12 transitions); AFCData 49 (7 defs,
  36 attributes, 6 enum values).
- Verified by the probe commands recorded in
  `specialists/sm-st3bc-receipt.md` (UID coverage, dangling-reference,
  back-consistency, SVG parse, C7 grep).
