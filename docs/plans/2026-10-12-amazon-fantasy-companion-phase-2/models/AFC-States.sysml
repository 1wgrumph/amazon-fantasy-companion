package AFCStates {
    doc /*
    * Amazon Fantasy Companion state model: alert lifecycle, panel modes,
    * device link. Language authority: OMG SysML v2 formal/2026-03-02
    * (bibliographic identity per sysml-v2-validation.md receipt
    * SRC-EMV-SYSMLV2). No local normative-coverage claim; no AZEdge
    * fixture used. Sources: requirements-register.md AFC-PR-001..065;
    * sm-contextual-pass.md section 3. Allocation of every state machine,
    * state and signal below to register UIDs: models/allocation.md.
    * Transitions are behavior owned by their state def and inherit its
    * allocation; trigger names are package signals declared below.
    */

    signal identify;
    signal passFilters;
    signal blockFilters;
    signal delayElapsed;
    signal present;
    signal correct;
    signal spikeFailed;
    signal requestCode;
    signal userConfirm;
    signal codeTimeout;

    state def AlertLifecycle {
        doc /*
        * Alert lifecycle, owned by backend.policy with backend.matcher.
        * detected: event ingested. matched: player/event identity resolved
        * (PR-024). gated: policy gates passed, held for the spoiler delay
        * (PR-020). emitted: exactly one alert per resolved event (PR-025).
        * delivered: presented in the chosen presentation (PR-021).
        * suppressed: blocked by type, frequency, quiet hours or game-day
        * filters (PR-016..019). corrected: scoring correction propagated
        * to the alert record (PR-026). Red-zone claims stay team-level
        * throughout (PR-028).
        */
        entry; then detected;

        state detected;
        state matched;
        state gated;
        state emitted;
        state delivered;
        state suppressed;
        state corrected;

        transition t_detected_matched first detected accept identify then matched;
        transition t_matched_gated first matched accept passFilters then gated;
        transition t_matched_suppressed first matched accept blockFilters then suppressed;
        transition t_gated_emitted first gated accept delayElapsed then emitted;
        transition t_emitted_delivered first emitted accept present then delivered;
        transition t_emitted_corrected first emitted accept correct then corrected;
        transition t_delivered_corrected first delivered accept correct then corrected;
    }

    state def PanelMode {
        doc /*
        * Panel presentation mode, owned by tvApp.panel with tvApp.player.
        * modeB: lineup panel beside provider video, broadcast unobscured
        * (PR-041). modeA: panel-beside-provider-video spike failed or
        * exceeded 24 h from first install (C5): panel beside the companion
        * player with labeled sample footage (PR-047). No return transition:
        * C5 names fallback only. Under modeA, alerts and Watch actions
        * still route to the real provider apps (PR-048).
        */
        entry; then modeB;

        state modeB;
        state modeA;

        transition t_modeB_modeA first modeB accept spikeFailed then modeA;
    }

    state def DeviceLink {
        doc /*
        * Device-code link, owned by backend.auth with backend.api.
        * unlinked: no link. codePending: device code issued, awaiting the
        * customer action on phone or browser. linked: TV app linked after
        * the code action. expired: code lapsed without completion; a new
        * request returns to codePending. No link completes without the
        * customer code action (PR-038).
        */
        entry; then unlinked;

        state unlinked;
        state codePending;
        state linked;
        state expired;

        transition t_unlinked_pending first unlinked accept requestCode then codePending;
        transition t_pending_linked first codePending accept userConfirm then linked;
        transition t_pending_expired first codePending accept codeTimeout then expired;
        transition t_expired_pending first expired accept requestCode then codePending;
    }
}
