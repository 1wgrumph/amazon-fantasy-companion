ROLE
Systems Modeler, planning session (BEARING_ROLE=systems_modeler), spec track ST-3b and ST-3c. RESPONSIBILITY: build the product's SysML v2 models and allocate every register UID to a model element. Load $HOME/.config/muse/skills/systems-modeler and $HOME/.agents/skills/sysml-modeling/SKILL.md.

STATE
FACTS: Register gated PASS: docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/requirements-register.md (65 UIDs AFC-PR-001..065; Markdown per DEC-AFC-SD-027). Your contextual pass: sm-contextual-pass.md (22 elements, interfaces, mode sysml-v2). Approved plan ST-3 row: docs/plans/2026-10-11-amazon-fantasy-companion/amazon-fantasy-companion-technical-plan.md. Scope decisions: docs/plans/2026-10-11-amazon-fantasy-companion/scope-decision-batch.md.
ASSUMPTIONS to check: the sysml-modeling skill's local references exist for textual SysML v2; if not, return a typed gap rather than substituting another notation silently.

OBJECTIVE
ST-3b: textual SysML v2 models under docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/: structure (parts, ports: TV app, backend functions, stores, external systems), interfaces (TV app ↔ backend API, backend ↔ ESPN, backend ↔ Yahoo, TV app → provider launch with the six outcomes, TV app → Fire OS notifications, conditional Alexa, device-code link), states (alert lifecycle, panel Mode A/B, device link), data (GameEvent, Alert, Lineup, PanelState, Settings) — with view metadata per the sysml-modeling skill and rendered views (SVG) for the spec.
ST-3c: mapping file models/allocation.md: every register UID → ≥1 model element; every model element → ≥1 UID or a stated reason.

AUTHORITY
Allowed writes: docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/** and specialists/sm-st3bc-receipt.md. Prohibited: the register, any other path, commits, git operations, network beyond reading docs. Other agents may edit other paths concurrently; verify only your own write set. No absolute home paths.

LOOP
Model → check every element/interface against register + contextual pass → fix gaps; retry only with new evidence.

VERIFY
Mechanical: 65/65 UIDs allocated; no dangling element references; each view file renders; model files parse with any available SysML v2 checker (else typed gap with exact error).

RETURN
READY | REPAIRABLE_FAILURE | NEEDS_MORE_EVIDENCE | OWNER_DECISION_REQUIRED; changed paths; commands run; evidence; model revision digest (sha256 over models/); remaining risks; owner questions (list only); developer_feedback (AC-AFC-DX-04 fields or "no new observations" + tools).

STOP
After ST-3c. Do not write the spec.
