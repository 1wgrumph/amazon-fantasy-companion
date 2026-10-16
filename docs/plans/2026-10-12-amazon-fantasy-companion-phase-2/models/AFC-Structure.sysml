package AFCStructure {
    doc /*
    * Amazon Fantasy Companion structure model: parts and ports.
    * Language authority: OMG SysML v2 formal/2026-03-02 (bibliographic
    * identity per sysml-v2-validation.md receipt SRC-EMV-SYSMLV2). No local
    * normative-coverage claim; no AZEdge fixture used.
    * Sources: requirements-register.md AFC-PR-001..066; sm-contextual-pass.md
    * section 2 (placements), section 3 (interfaces), section 4 (constraints).
    * Allocation of every part/port below to register UIDs: models/allocation.md.
    * This package is self-contained: linkage to AFCInterfaces, AFCStates and
    * AFCData is by element name in doc comments plus allocation.md (see
    * models/views.md for the abstraction decision). No import bindings.
    */

    port def ApiPort;
    port def NotifyPort;
    port def LaunchPort;
    port def AlexaPort;
    port def EspnPort;
    port def YahooPort;
    port def LinkPort;

    part tvApp {
        doc /* Fire TV companion app on the 2018 stick target (SD-003).
        * Planned path tv-app/. Exposes apiPort (TvBackendApi), notifyPort
        * (TvFireOSNotify), launchPort (TvProviderLaunch), alexaPort (TvAlexa). */

        port apiPort : ApiPort;
        port notifyPort : NotifyPort;
        port launchPort : LaunchPort;
        port alexaPort : AlexaPort;

        part shell;
        // App shell and navigation. Planned: MainActivity.kt.

        part build;
        // Build configuration, minSdk 25. Planned: build.gradle.kts.

        part manifest;
        // Permissions, services, package visibility. Planned: AndroidManifest.xml.

        part profileUI;
        // Profile and settings UI (items 1, 6). Planned: profile/ProfileSettingsScreen.kt.

        part detector;
        // Installed-app detector; viewing-context detection only while enabled.
        // Planned: detect/AppDetector.kt.

        part alertSvc;
        // Alert foreground service. Planned: alerts/AlertService.kt.

        part notifier;
        // Heads-up notifier with Watch/Dismiss. Planned: alerts/AlertNotifier.kt.

        part launcher;
        // Provider launch via supported URI/intent; reports RoutingOutcome.
        // Planned: watch/WatchLauncher.kt.

        part panel;
        // Right-side lineup panel. Planned: panel/LineupPanel.kt.
    }

    part backend {
        doc /* AWS serverless backend, Free-tier services only (SD-005, C4).
        * Planned path backend/. Exposes apiPort (TvBackendApi), espnPort
        * (BackendEspn), yahooPort (BackendYahoo), linkPort (BackendDeviceLink). */

        port apiPort : ApiPort;
        port espnPort : EspnPort;
        port yahooPort : YahooPort;
        port linkPort : LinkPort;

        part auth;
        // Device-code auth and /v1/link. Planned: backend/src/device_auth/.

        part api;
        // REST API: /v1/link, /v1/profile, /v1/alerts, /v1/panel, /v1/providers.
        // Planned: backend/src/api/. No messaging/social operations (PR-057).

        part ingest;
        // ESPN feed ingest with validation at ingest. Planned: backend/src/feed_ingest/.

        part replay;
        // Labeled replay source. Planned: backend/src/feed_ingest/replay.py
        // plus stores.fixtures.

        part lineup;
        // Lineup connector: Yahoo OAuth read-only plus manual fallback.
        // Planned: backend/src/lineup/.

        part matcher;
        // Player/event identity matcher. Planned: backend/src/matcher/.

        part policy;
        // Alert policy engine: filtering, frequency, quiet hours, spoiler
        // delay, commentary grounding. Planned: backend/src/alert_policy/.

        part resolver;
        // Provider resolver and registry. Planned: backend/src/provider_resolver/.

        part panelSvc;
        // Panel service: points, freshness, consistency with alerts.
        // Planned: backend/src/panel/.

        part iac;
        // Infrastructure as code (SAM). Planned: backend/template.yaml.
    }

    part stores {
        doc /* Backend-owned stores declared in backend/template.yaml
        * (DynamoDB on-demand tables, SSM SecureString, replay fixtures). */

        part profileStore;
        // Profile, settings and device-link store (DynamoDB).

        part eventStore;
        // Event cache with dedup identities and correction log (DynamoDB).

        part secrets;
        // Yahoo OAuth client secrets and tokens (SSM SecureString, owner-set).

        part fixtures;
        // Labeled replay fixtures. Planned: backend/fixtures/replay/.
    }

    part externals {
        doc /* External systems: interface endpoints only, not in repo
        * (sm-contextual-pass.md section 2.4). */

        part espn;
        // ESPN unofficial public JSON: live NFL game events and corrections.

        part yahoo;
        // Yahoo Fantasy API, OAuth 2.0 read-only: lineup and league context.

        part manualEntry;
        // Labeled manual lineup entry from ESPN rosters (C6 fallback at T_yahoo).

        part providerApps;
        // Installed provider apps: viewing destinations reached by supported
        // intent or deep link.

        part fireOSNotify;
        // Fire OS notification service: heads-up delivery over third-party playback.

        part alexaRoute;
        // Alexa voice route (Video Skills / tuning). Conditional per C8:
        // offered only when implemented and verified.

        part linkConsumer;
        // Device-link consumer: customer phone or browser completing the
        // device code.
    }
}
