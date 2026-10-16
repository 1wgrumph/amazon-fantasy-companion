package AFCInterfaces {
    doc /*
    * Amazon Fantasy Companion interface model: system interfaces and their ends.
    * Language authority: OMG SysML v2 formal/2026-03-02 (bibliographic
    * identity per sysml-v2-validation.md receipt SRC-EMV-SYSMLV2). No local
    * normative-coverage claim; no AZEdge fixture used.
    * Sources: requirements-register.md AFC-PR-001..065; sm-contextual-pass.md
    * section 3 (interfaces to model).
    * Allocation of every interface below to register UIDs: models/allocation.md.
    * Ends name their connected AFCStructure ports in doc comments; no import
    * bindings (see models/views.md). Ends inherit their interface allocation.
    */

    interface def TvBackendApi {
        doc /*
        * TV app <-> backend REST API: link, profile, alerts long-poll,
        * panel, providers. Carries profile-relevant updates only.
        * No messaging or social operations (AFC-PR-057 exclusion).
        * Ends: tvApp.apiPort .. backend.apiPort (see AFCStructure).
        */
        end tvEnd;
        end backendEnd;
    }

    interface def BackendEspn {
        doc /*
        * Backend <-> ESPN unofficial public JSON: poll during game windows;
        * validation at ingest; schema-invalid responses rejected without
        * changing stored events; labeled replay substitution on outage or
        * contract change (C2). Ends: backend.espnPort .. externals.espn.
        */
        end backendEnd;
        end espnEnd;
    }

    interface def BackendYahoo {
        doc /*
        * Backend <-> Yahoo Fantasy API: read-only OAuth connection for
        * leagues, teams, rosters by week and league scoring settings;
        * token refresh via SSM-held secrets; switchover to labeled manual
        * entry when approval is absent at T_yahoo (C6). Single active
        * lineup source at all times. Ends: backend.yahooPort .. externals.yahoo.
        */
        end backendEnd;
        end yahooEnd;
    }

    interface def TvProviderLaunch {
        doc /*
        * TV app -> provider apps: game or channel opened through a supported
        * provider launch URI or intent on the customer Watch action.
        * Every routing attempt reports exactly one AFCData::RoutingOutcome:
        * game opened, search or details opened, app home opened, app absent,
        * access unknown, playback denied. Ends: tvApp.launchPort ..
        * externals.providerApps.
        */
        end tvEnd;
        end providerEnd;
    }

    interface def TvFireOSNotify {
        doc /*
        * TV app -> Fire OS notification service: heads-up alert delivery
        * with Watch and Dismiss actions during third-party viewing-app
        * playback, in the customer-chosen presentation. Ends:
        * tvApp.notifyPort .. externals.fireOSNotify.
        */
        end tvEnd;
        end osEnd;
    }

    interface def TvAlexa {
        doc /*
        * TV app <-> Alexa route, conditional per C8: voice announcements and
        * Alexa-assisted tuning are offered only while the customer enables
        * voice control over an implemented and verified route. Ends:
        * tvApp.alexaPort .. externals.alexaRoute.
        */
        end tvEnd;
        end alexaEnd;
    }

    interface def BackendDeviceLink {
        doc /*
        * Backend -> device-link page: device-code flow. The backend issues a
        * device code (AFCData::DeviceCode); the customer completes it on a
        * phone or browser; the TV app links. No link completes without the
        * customer code action. Ends: backend.linkPort .. externals.linkConsumer.
        */
        end backendEnd;
        end consumerEnd;
    }

    interface def IngestMatcherPolicy {
        doc /*
        * Backend-internal chain: ingest -> matcher -> policy -> alert and
        * panel delivery. Carries GameEvent identity resolution, duplicate
        * suppression and scoring-correction propagation to alerts and panel
        * state. Ends: backend.ingest .. backend.matcher .. backend.policy
        * (represented as one chain interface with two boundary ends).
        */
        end ingestEnd;
        end policyEnd;
    }
}
