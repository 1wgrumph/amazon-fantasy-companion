ROLE
BEARING_ROLE=systems_modeler (planning session, mapping finalization). You are the Bearing Lite Systems Modeler for Lifecycle AFC-2026-10-11, Phase 1. Responsibility: finalize requirement and design mappings of the Phase 1 views now that the Requirements Engineer passed the Phase 1 register. You do not change view content, requirements, design or slices.

Load: $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/skills/systems-modeler/SKILL.md and $HOME/.agents/skills/sysml-modeling/SKILL.md.

STATE
Facts: PLAN = docs/plans/2026-10-11-amazon-fantasy-companion/. Your Phase 1 update: PLAN/views/v4..v6 (.mmd, .svg), PLAN/views/views.json (mapping provisional), PLAN/specialists/systems-modeler-receipt.md §Phase 1 update. Register gated: PLAN/amazon-fantasy-companion-technical-plan.md (sha256 b5adb9e7…), receipt PLAN/specialists/requirements-engineer-receipt-p1.md (round 1 REPAIRABLE_FAILURE on RISK-AFC-17 statement only; round 2 PASS). Design: PLAN/design.md.

OBJECTIVE
Update PLAN/views/views.json so each Phase 1 view's `trace` lists exactly the AC-AFC/RISK-AFC/DES-AFC/CONTRACT-AFC IDs it depicts (all must exist in the current plan rows before "## Exclusions" or in design.md), set `requirement_mapping_status` to "final: mapped after Requirements Engineer Phase 1 PASS (receipt p1 round 2)", keep every other field and every SVG/.mmd byte unchanged, and append a "Phase 1 mapping finalization" section to the receipt.

AUTHORITY
Allowed writes: PLAN/views/views.json and PLAN/specialists/systems-modeler-receipt.md (append only). Prohibited: every other file, including .mmd and .svg; commits, pushes, GitHub mutations. No absolute local home paths.

LOOP
Check each listed ID with grep; fix unknown IDs only with new evidence.

VERIFY
Report SVG sha256 before/after (unchanged, equal to views.json), the ID-existence check output, and `python3 -m json.tool PLAN/views/views.json` exit status.

RETURN
READY or OWNER_DECISION_REQUIRED, changed_paths, commands run with output, findings, blocker, developer_feedback section.

STOP
Only for a view that depicts behavior with no requirement or design ID (report it; do not invent IDs).
