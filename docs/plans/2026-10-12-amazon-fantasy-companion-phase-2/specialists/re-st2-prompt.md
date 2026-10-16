ROLE
Requirements Engineer, planning session (BEARING_ROLE=requirements_engineer), spec track ST-2, Lifecycle AFC-ST-2026-10-12. Load: $HOME/.config/muse/skills/requirements-engineer (bearing-lite), $HOME/.agents/skills/requirements-engineering/SKILL.md, $HOME/.agents/skills/use-requirements-system/SKILL.md.

STATE
- Approved parent plan on main: docs/plans/2026-10-11-amazon-fantasy-companion/ — technical plan ST-2 row, §Deferred to the spec track or Phase 2 (the f885e48 product rows are NON-BINDING input: re-derive, never copy), scope-decision-batch.md (SD-001..SD-011, SD-024, C1..C9), journey.json decisions.
- Product intent: issue 1wgrumph/amazon-fantasy-companion#1 (`gh api repos/1wgrumph/amazon-fantasy-companion/issues/1 --jq .body`): retained items 1, 2, 3, 4, 6 and the right-side lineup panel; messaging excluded.
- Systems Modeler contextual pass (consume BEFORE drafting): docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/sm-contextual-pass.md.
- Register form (OD-AFC-12, approved): draft .sdoc in the spec-track plan directory, bound to the local packaged-default Requirements System host for review readback. Host: port in $XDG_RUNTIME_DIR/alphazede-requirements-system/host.port (currently up). Another checkout (MID-MAESTRO-SPECIFICATION-CORE-0001) is active: never touch, release or claim it.

OBJECTIVE
Write the product requirements register docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/afc-product-requirements.sdoc: UID, statement, rationale, verification method, allocation (to ST-3a placements) for every retained issue #1 item and the panel, with FULL customer-control coverage (every setting #1 item 6 lists and every setting the alerts/panel expose: fantasy selections, alert types, frequency, quiet hours/game-day periods, spoiler delay, notification presentation, voice announcements, excitement level, provider preference, switching confirmation, detection/personalization opt-in, panel show/hide, team/league selection), conditionals C1..C9 typed, SD-001..SD-011 and SD-024 honored, unknown-access and stale-data behavior explicit. Run the requirements-engineering quality gate on every row (precision, measurability, traceability, allocation) and fix failures yourself; one self-correction pass max, then report remaining rows.
Validate the .sdoc locally (StrictDoc or the RS tool's validate command, per use-requirements-system). Then bind for readback: create a NEW checkout for this document on the local host per use-requirements-system (do not reuse others'); if binding is not possible, record a typed gap with the exact error and continue.

AUTHORITY
Write only inside docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/ (register .sdoc, re-st2-receipt.md, specialists/). Local RS host checkout create/read for THIS document only. No commits, no publication, no other repos. No absolute home paths in written files.

VERIFY
Every row PASSes the quality gate or is listed with its exact failing criterion; every issue #1 retained item and every control above maps to ≥1 UID; every UID allocated to an ST-3a element; .sdoc validates; host readback digest recorded or typed gap.

RETURN
PASS | REPAIRABLE_FAILURE | NEEDS_OWNER_DECISION (per-row NEEDS_OWNER_DECISION for owner-value gaps; complete the gate, do not stop at the first), counts, coverage table, validation + binding evidence, owner questions (list only), developer_feedback (AC-AFC-DX-04 fields that apply, or "no new observations" + tools exercised).

STOP
After the register and its gate. Owner-value gaps never stop the gate: mark the row NEEDS_OWNER_DECISION and continue.
