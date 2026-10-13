ROLE
Product Implementer, spec-and-docs lane (profile tech-writing, single_implementer; BEARING_ROLE=implementer), spec track ST-4, generation 1. RESPONSIBILITY: write the product architecture specification (D1) from the gated register and the models. Not requirements authoring, not modeling, not review.

STATE
FACTS:
- Dispatch record (in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json execution_receipts): lease_id ST-4-g1; worktree (cwd) $HOME/alphazede/worktrees/amazon-fantasy-companion-st4; branch afc/st4-spec; base 5e59270b8320d6085039f26b64f14897736845f6; evidence_dir docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/ (in your worktree); owner decision DEC-AFC-SD-033 (start now, exit unchanged).
- Inputs on main (in your worktree): docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/requirements-register.md (65 gated UIDs AFC-PR-001..065, Markdown per SD-027), models/ (SysML v2 structure, interfaces, states, data; allocation.md; SVG views; SysON-parsed, project 2a033855-6bae-4fe1-975c-00bbb9419100), sm-contextual-pass.md, specialists/ receipts (open owner questions are in specialists/re-st2-receipt.md); scope decisions docs/plans/2026-10-11-amazon-fantasy-companion/scope-decision-batch.md; product intent issue 1wgrumph/amazon-fantasy-companion#1 (`gh api repos/1wgrumph/amazon-fantasy-companion/issues/1 --jq .body`).
- Tooling: shared skill $HOME/alphazede/Alphazedehq/skills/spec-authoring/SKILL.md (merged; follow it exactly: template, section format, figures, lint, build) and its vendored copy in this repo's tools/spec/ (VENDORED.md pins it). The repo gate (tools/ci/gate.sh, S09) is being built concurrently and is NOT on main yet.
ASSUMPTIONS to check: the vendored build and lint run here without network.
Other agents work in other worktrees concurrently (S09 owns tools/ci/, .githooks/, .github/); verify only your own write set.

OBJECTIVE
Create spec/amazon-fantasy-companion/ from the spec-authoring template and build the single-file specification with the vendored tools. Sections cite register UIDs (do not restate requirement text) and cover: identification, system context, stakeholders, operational concept (Mode A/B, alert → Watch → provider), feature decomposition per issue #1 retained items 1,2,3,4,6 and the lineup panel, allocation, internal/external interfaces and contracts (from the interface model), data model (from the data model), states (alert lifecycle, panel modes, device link), fault behavior (stale/unknown data, unknown access, feed outage → labeled replay), lightweight-device design (no benchmark claims), security, risks and open items (owner questions from re-st2-receipt, spikes, C1..C9), verification approach per UID. Figures come from the model views. Mark unverified platform capabilities as risks, never facts. Every UID appears in Appendix A traceability.

AUTHORITY
Allowed writes: spec/amazon-fantasy-companion/** , the built spec file the skill names, and the evidence_dir. Commit (author from env; never Co-Authored-By); push the branch; open ONE draft PR. Prohibited: tools/, docs/plans/ outside evidence_dir, .github/, .githooks/, merge, force-push, credentials, absolute home paths.

LOOP
Write, build, lint, fix; classify failures (content / tool / environment); retry only with new evidence.

VERIFY
The skill's build command exits 0 and a second build is byte-identical; the skill's lint exits 0; a script check that all 65 UIDs appear in the built spec and no UID is unknown to the register (record command + output); rule-12 path scan on your write set clean.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE | ENVIRONMENT_FAILURE | NEEDS_MORE_EVIDENCE; lease_id; head SHA; draft PR URL; built file path; commands with exit codes; UID coverage result; open owner questions surfaced in the spec; remaining risks; developer_feedback (AC-AFC-DX-04 fields — spec-authoring skill and vendored tools are tools used: used for, worked well, needs work, onboarding, would build again).

STOP
After the draft PR is open with VERIFY passing, or a typed failure with exact error.
