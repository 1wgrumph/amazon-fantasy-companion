You are the Bearing Lite Planning and Design node (BEARING_ROLE=planning_and_design), RESUMING run 2 per bearing-lite references/resume.md. Your base packet is specialists/pd-prompt.md in the plan directory: read it first and follow it, except as amended below. Do not replay accepted work.

Why resuming: the previous node session and the Test Engineer run ended with "You've hit your session limit · resets 6:20pm (America/Chicago)" (specialists/pd-run.log, te-run.log). The limit has reset. Liveness: no specialist process is running (Orchestrator-verified: INACTIVE).

Durable state (verify from files, then continue):
- Systems Modeler: READY (systems-modeler-receipt.md, views/). sm-finalize-prompt.md written but NOT run.
- Requirements Engineer: round 1 applied (re-r1-applied.diff); round 2 PASS (requirements-engineer-receipt-r2.md). Do not run another RE round.
- Integration Engineer: done; findings applied (ie-r1-applied-*.diff).
- Test Engineer (planning): FAILED on session limit before output; te-prompt.md exists. Re-dispatch it on its frozen primary (Claude Code / Claude Opus 5.5 / high).
- Plan Integrator: pi-prompt.md written but NOT run.
- authority.json exists; technical plan, design.md, slice-graph.md drafted.
Remaining, in order: Test Engineer → Systems Modeler finalize (after requirements stable) → Plan Integrator → `node <plugin root>/hooks/plan-package.cjs <plan dir>` PASS → DoD Manifest + rendered HTML → planning-review.cjs check → return.

Route note: Muse quota resets 2026-10-12T00:00:00Z. Before then, Muse-primary roles use their first approved fallback (already receipted). From 00:00:00Z on, a Muse-primary role starting fresh uses its Muse primary again; record which route actually ran in route-receipts.md.

Amendments the Orchestrator must surface (include them as visible review items, do not decide them):
- A1: tv-app-ui lane runs on Codex (frontend profile); name frontend-design by absolute path: $HOME/.claude/plugins/cache/claude-plugins-official/frontend-design/<version>/skills/frontend-design/SKILL.md (resolve the newest installed version; write it with $HOME, not the literal home path).
- A2: D4 and D5 skill-authoring work has no owner-confirmed lane; propose one (current packet implies spec-and-docs = tech-writing) and list it as an owner review item.
Return as defined in the base packet (PLAN_REVIEW_READY | NEEDS_OWNER_DECISION | VALIDATION_FAILED) with paths, evidence, open owner items.
