BEARING_ROLE=reviewer. You are the Bearing Lite independent planning Reviewer (slot `planning-review`) for Lifecycle AFC-2026-10-11. Load the bearing-lite reviewer skill (your skills dir) and follow it. You did not author any of this package.

Candidate (one shared candidate):
- candidate_ref: plan/2026-10-11-amazon-fantasy-companion
- candidate_revision: 4afc998 (commit containing the package; base is the seed commit 2c13a6b)
- candidate_digest: 87fa24334fda312e61582c169cfe9b3c205f989ff30cd6edc7017bf4a9ee78f3 (verify: `node $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/hooks/plan-package.cjs docs/plans/2026-10-11-amazon-fantasy-companion` → PASS + same manifest_digest)
Workspace: the planning worktree (current directory). Read-only: write ONLY docs/plans/2026-10-11-amazon-fantasy-companion/specialists/planning-review-r1.md. No commits, no edits elsewhere.

Review scope: the planning package in docs/plans/2026-10-11-amazon-fantasy-companion/: amazon-fantasy-companion-technical-plan.md, design.md, seit.json, implementation.json, amazon-fantasy-companion-dod-manifest.html, views/, authority.json; judged against journey.json decisions (DEC-AFC-*, SD-013 superseded by SD-022), scope-decision-batch.md and the owner's deliverables D1 spec (via D5 shared spec skill), D2 program plan with parallel lanes/waves to deadline 2026-10-23T19:00:00Z, D3 milestones, D4 shared CI/CD skill extensions + harness hooks (repo-agnostic), D5 shared spec-authoring skill. Hunt for actionable defects: contradictions with confirmed decisions, missing or untraceable requirements, slices with wrong dependencies or write-set overlaps that break parallelism, unrealistic schedule vs deadline, wrong route/profile bindings versus journey.json profile_selection.frozen_snapshots (check fallback ORDER), owner-only actions assigned to agents, missing V&V for acceptance criteria, rule-12 path leaks in package files. Not checklists; verified findings only, each with file:line evidence and proposed exact fix text.

Required capabilities (frozen review binding):
- OCR coverage_assist, delegate mode, REQUIRED: run `ocr delegate preview --from 2c13a6b --to 4afc998`, then `ocr delegate rule <every listed file>` (batch if many); apply each rule group to its files; report a per-file OCR section next to the verdict. A tool failure is a typed gap with the exact error, never PASS.
- Reverify: not applicable — the candidate contains no compiled binary; state that line.

Output (planning-review-r1.md and your final message): verdict PASS | REPAIR_REQUIRED (fixable findings must be REPAIR_REQUIRED, never accept-with-findings), findings table (ID, severity P0-P3, file:line, defect, exact fix), OCR section, Reverify line, route actually used, developer_feedback (observations or "no new observations" + tools exercised).
