ROLE
Requirements Engineer, planning session (BEARING_ROLE=requirements_engineer), Phase 2 Planning and Design register delta for Lifecycle AFC-2026-10-11 (Amazon Fantasy Companion). You change and re-gate only the rows named below. You do not author design, SEIT, slices or models.

Load and follow (absolute SKILL.md paths; $HOME is the invoking user's home):
- $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/skills/requirements-engineer/SKILL.md
- $HOME/.agents/skills/requirements-engineering/SKILL.md

STATE
Facts (cwd = the Phase 2 planning worktree; PLAN = docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/):
- Register of record PLAN/requirements-register.md (Markdown, DEC-AFC-SD-027; 66 UIDs, 049..051 Withdrawn). Prior gates: PLAN/specialists/re-st2-receipt.md, re-st2b-receipt.md, re-sd035-receipt.md.
- DEC-AFC-SD-035 (owner, 2026-10-12): no Mode A sample footage; when the panel-beside-provider-video spike fails or exceeds 24 h the lineup panel is a full screen in the companion app. The approved spec (spec/amazon-fantasy-companion/04.1.99-allocation.md, 04.7-model-correspondence.md) records that PR-047 "retains PLAYER in the register ... pending Phase 2 design" and that the PLAYER element (CompanionPlayer.kt) is a retained Mode A allocation.
- Phase 2 design decision (this planning node): there is no companion player. The full-screen panel is rendered by the app shell and the panel component. A concurrent Systems Modeler delta removes `tvApp.player` and renames PanelMode.modeA to PanelMode.fullScreen in PLAN/models (not your write set).

OBJECTIVE
1. AFC-PR-047 Allocation: PANEL, PLAYER -> PANEL, SHELL. Statement, rationale and verification method unchanged unless your gate finds a defect.
2. "## ST-3a allocation elements": retire PLAYER (e.g. "PLAYER retired by DEC-AFC-SD-035 (Phase 2 design: no companion player)"), keeping the rule "every UID allocates to >=1 element; every element receives >=1 UID" true for active elements (withdrawn UIDs 049..051 keep their historical text; state that withdrawn rows carry no live allocation if needed).
3. Header paragraph: one dated sentence recording this Phase 2 delta.
4. Re-gate the changed rows (047, the element list, any row referencing PLAYER) with the requirements-engineering quality gate; confirm no other active row allocates to PLAYER (grep).

AUTHORITY
Allowed writes: PLAN/requirements-register.md and PLAN/specialists/re-p2-delta-receipt.md only.
Prohibited: every other path; commits, pushes, branch operations, GitHub mutations; renumbering or deleting UIDs; changing any statement other than the named allocation fields. Never write an absolute local home path (rule 12). Other agents work concurrently in PLAN/models; do not touch it.

VERIFY
Report verbatim: `grep -n "PLAYER" PLAN/requirements-register.md`, the UID count check (66 rows, 3 withdrawn), and the gate result per changed row.

RETURN (in the receipt and as your final message)
PASS | REPAIRABLE_FAILURE | NEEDS_OWNER_DECISION; changed paths; diff summary; gate table; remaining risks; developer_feedback section (observations, or "no new observations" naming the tools exercised).

STOP
After the gate result. Stop with NEEDS_OWNER_DECISION only if the change would alter owner-decided behavior.
