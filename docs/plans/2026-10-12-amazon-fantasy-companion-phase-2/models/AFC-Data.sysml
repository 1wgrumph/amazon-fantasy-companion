package AFCData {
    doc /*
    * Amazon Fantasy Companion data model: GameEvent, Alert, Lineup,
    * PanelState, Settings, ScoringPreset, plus RoutingOutcome (the six
    * provider-launch outcomes) and DeviceCode (the device-link payload). Language
    * authority: OMG SysML v2 formal/2026-03-02 (bibliographic identity
    * per sysml-v2-validation.md receipt SRC-EMV-SYSMLV2). No local
    * normative-coverage claim; no AZEdge fixture used. Sources:
    * requirements-register.md AFC-PR-001..066; sm-contextual-pass.md
    * section 3 (data interfaces). Allocation of every item below to
    * register UIDs: models/allocation.md. Attributes inherit their item
    * allocation; enum values inherit their enum allocation.
    */

    import ScalarValues::*;

    item def GameEvent {
        doc /* One ingested NFL game event from ESPN or labeled replay. */
        attribute score : String;
        attribute fieldPosition : String;
        attribute possession : String;
        attribute playerIds : String;
        attribute eventTime : String;
        attribute correctionOf : String;
    }

    item def Alert {
        doc /*
        * One emitted alert: typed, policy-gated, carrying verified trigger
        * context and the resolved provider route. Commentary, when
        * attached, names only entities grounded in the triggering event.
        */
        attribute alertType : String;
        attribute triggerContext : String;
        attribute providerRoute : String;
        attribute commentary : String;
        attribute emittedAt : String;
    }

    item def Lineup {
        doc /*
        * Active lineup context from exactly one source: the Yahoo
        * read-only connection or labeled manual entry.
        */
        attribute source : String;
        attribute team : String;
        attribute league : String;
        attribute starters : String;
        attribute scoring : String;
    }

    item def PanelState {
        doc /*
        * Lineup panel content and freshness: points, statuses, totals and
        * progress under the league scoring context, with stale or
        * unavailable labels where values are missing or aged.
        */
        attribute visible : Boolean;
        attribute teamTotal : String;
        attribute progress : String;
        attribute freshness : String;
    }

    item def Settings {
        doc /*
        * Customer profile and settings: fantasy selections, alert policy,
        * presentation, provider preference, switching confirmation, panel
        * display and detection opt-in. The panel reflects these settings;
        * it is not a second configuration.
        */
        attribute fantasySelections : String;
        attribute teamLeague : String;
        attribute alertTypes : String;
        attribute frequency : String;
        attribute quietHours : String;
        attribute gameDayPeriods : String;
        attribute spoilerDelay : String;
        attribute presentation : String;
        attribute voice : String;
        attribute excitement : String;
        attribute providerPref : String;
        attribute switchingConfirm : String;
        attribute panelPrefs : String;
        attribute detectionOptIn : String;
        attribute scoringPreset : ScoringPreset default ScoringPreset::halfPpr;
    }

    enum def ScoringPreset {
        doc /* Manual-lineup scoring preset: PPR or Half-PPR, default Half-PPR (PR-065, PR-066). */
        enum ppr;
        enum halfPpr;
    }

    enum def RoutingOutcome {
        doc /* The six explicit provider-launch routing outcomes (PR-031). */
        enum gameOpened;
        enum searchOpened;
        enum appHomeOpened;
        enum appAbsent;
        enum accessUnknown;
        enum playbackDenied;
    }

    item def DeviceCode {
        doc /* Device-code link payload completed on phone or browser. */
        attribute code : String;
        attribute expires : String;
    }
}
