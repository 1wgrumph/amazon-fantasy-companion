ROLE
Requirements Engineer, planning session (BEARING_ROLE=requirements_engineer), Phase 2 Planning and Design for Lifecycle AFC-2026-10-11 (Amazon Fantasy Companion). Gate the Lifecycle-local requirement rows of the Phase 2 technical plan. You do not author design, SEIT, slices or models, and you do not change the product register.

Load and follow (absolute SKILL.md paths; $HOME is the invoking user's home):
- $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/skills/requirements-engineer/SKILL.md
- $HOME/.agents/skills/requirements-engineering/SKILL.md

STATE
Facts (cwd = Phase 2 planning worktree; PLAN = docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/):
- Candidate: PLAN/amazon-fantasy-companion-phase-2-technical-plan.md, section "## Requirements (Lifecycle-local)" — rows AC-AFC-P2-* and RISK-AFC-P2-* (statement, source, verification, allocation; risks add rationale and response). Product requirements are the register PLAN/requirements-register.md (63 active UIDs, by reference; do not re-gate them).
- Artifact grammar: $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/skills/planning-and-design/references/artifact-grammar.md §Requirements register rule 3: Lifecycle-local rows are criteria about write sets, seams, gates, schedule, submission or concurrency, and must not restate registered content. Glossary quantity names cited in rows must exist in the plan's Glossary tables.
- Owner decisions in force: DEC-AFC-SD-001..038 (journey at $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json), DEC-AFC-APPROVAL-ST5. Issue #1 obligations: `gh api repos/1wgrumph/amazon-fantasy-companion/issues/1 --jq .body` (read only).

OBJECTIVE
Apply the requirements-engineering quality gate to every AC-AFC-P2-* and RISK-AFC-P2-* row: singular, verifiable, unambiguous, traceable to its source, feasible within the plan, consistent with the register and owner decisions, no restated register content, defined quantity names. Also check coverage: every issue #1 submission/feedback obligation and every Phase 1 deferred item that Phase 2 owns (technical plan of docs/plans/2026-10-11-amazon-fantasy-companion/ §Deferred to the spec track or Phase 2) is covered by a register UID or a Lifecycle-local row, or is an owner action.

AUTHORITY
Allowed writes: PLAN/specialists/re-p2-ac-receipt.md only. Do NOT edit the technical plan; give exact replacement text for each failing row in the receipt (the Planning and Design node applies it).
Prohibited: every other path; commits, pushes, GitHub mutations. Never write an absolute local home path (rule 12).

VERIFY
Report the per-row gate table (ID, PASS/FAIL, check, exact proposed text for FAIL) and the coverage table (obligation → covering ID or owner action, or GAP).

RETURN (in the receipt and as your final message)
PASS | REPAIRABLE_FAILURE | NEEDS_OWNER_DECISION; counts; gate table; coverage table; proposed text; remaining risks; developer_feedback section (observations, or "no new observations" naming the tools exercised).

STOP
After the gate. NEEDS_OWNER_DECISION only where a row needs owner intent the decisions do not give.
