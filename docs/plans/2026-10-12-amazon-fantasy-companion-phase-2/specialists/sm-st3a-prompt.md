ROLE
Systems Modeler, planning session (BEARING_ROLE=systems_modeler), spec track ST-3a, Lifecycle AFC-ST-2026-10-12 (parent AFC-2026-10-11). Load $HOME/.config/muse/skills/systems-modeler (bearing-lite systems-modeler) and $HOME/.agents/skills/sysml-modeling/SKILL.md.

STATE
- Owner-approved Phase 1 plan on main: docs/plans/2026-10-11-amazon-fantasy-companion/ (technical plan §Phase 1 spec track ST-1..ST-5, §Deferred to the spec track or Phase 2, design.md, views/). Spec-track journey: docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/journey.json.
- Product intent: GitHub issue 1wgrumph/amazon-fantasy-companion#1 (`gh api repos/1wgrumph/amazon-fantasy-companion/issues/1 --jq .body`); scope decisions: docs/plans/2026-10-11-amazon-fantasy-companion/scope-decision-batch.md (SD-001..SD-011, SD-024, C1..C9).
- Greenfield product: no product code exists. Starter: AmazonAppDev/hello-world-fire-tv (Kotlin/Compose, read via gh api only). Backend: AWS serverless (SD-005). Feed: ESPN unofficial JSON (SD-004). Lineup: Yahoo Fantasy read-only OAuth with manual fallback (SD-007). Device: owner's 2018 Fire OS stick (SD-003). Panel Mode A/B (SD-006).

OBJECTIVE
ST-3a only: the contextual placement pass that the Requirements Engineer consumes before the first register draft (bearing-lite planning-and-design references/allocation-inputs.md rule 1). Produce: current flow (none; greenfield), candidate element placements (TV app, backend functions, data stores, external systems ESPN/Yahoo/provider apps/Fire OS notification service) with planned repo-relative paths, interfaces to model, constraints (C1..C9, lightweight device), and the modeling mode decision for ST-3b (expected sysml-v2 per DEC-AFC-SD-023: structure, interface, state, data). Do NOT draft requirements or full models yet.

AUTHORITY
Write only inside docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/ (files: sm-contextual-pass.md, specialists/sm-st3a-receipt.md). No commits, no other paths. No absolute home paths in written files (use $HOME).

VERIFY
Every placement cites its source (issue #1 section, SD-id, or plan line). Every external interface named in issue #1 / SD decisions appears. Mode decision stated with reason.

RETURN
READY | NEEDS_EVIDENCE, paths, summary of placements and interfaces, open questions for the owner (list, do not ask), developer_feedback (AC-AFC-DX-04 fields that apply, or "no new observations" + tools exercised).

STOP
After ST-3a. Stop with NEEDS_EVIDENCE if a placement cannot be grounded.
