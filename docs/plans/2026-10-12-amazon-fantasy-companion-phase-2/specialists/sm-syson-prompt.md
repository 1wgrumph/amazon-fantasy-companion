ROLE
Systems Modeler, planning session (BEARING_ROLE=systems_modeler), spec track ST-3d. RESPONSIBILITY: get the product SysML v2 models parse-checked in SysON and repair parse errors. Load $HOME/.config/muse/skills/systems-modeler and $HOME/.agents/skills/sysml-modeling/SKILL.md.

STATE
FACTS: Models at docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/ (your ST-3b/c output; receipt specialists/sm-st3bc-receipt.md; CHECKER_UNAVAILABLE gap). Owner decision DEC-AFC-SD-032: import the models directly into the local SysON as a NEW project using SysON's own textual SysML import — not the Requirements System CLI `model load` (refuses unregistered packages), not syside, nothing that needs an API key. SysON runs locally as part of the Requirements System workbench (java processes on localhost; discover its URL from `alphazede-requirements-system status`/`binding` or the host config, read-only).
ASSUMPTIONS to check: SysON exposes textual SysML import (UI "upload/import model" or its HTTP/GraphQL API) for a new project.

OBJECTIVE
Create one new SysON project "afc-product-models", import every .sysml file, capture the import diagnostics, repair parse errors in the .sysml sources (same semantics, allocation unchanged), re-import until clean, and record the project id, import result and a sha256 over models/.

AUTHORITY
Allowed: create ONE new SysON project and import into it; edit files under docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/** and write specialists/sm-syson-receipt.md. Prohibited: modifying, deleting or importing into any other SysON project; touching the active Maestro checkout or any Requirements System checkout/registry; `model load`, `--replace`, `checkout create`; installing software; API keys; commits; other paths. Other agents may be working concurrently; verify only your own write set. No absolute home paths in written files.

LOOP
Import → read diagnostics → classify (syntax error in model / SysON limitation / environment) → repair only real model errors → re-import. Retry only with new evidence.

VERIFY
Import completes with zero errors (or each remaining diagnostic is classified as a SysON limitation with evidence); 65/65 UID allocation unchanged (re-run your allocation check).

RETURN
PASS | REPAIRABLE_FAILURE | ENVIRONMENT_FAILURE | NEEDS_MORE_EVIDENCE; project id; import diagnostics before/after; changed model files; allocation check result; models sha256; remaining risks; developer_feedback (AC-AFC-DX-04 fields that apply — SysON is a tool used, record it).

STOP
After a clean import or a typed failure with exact error.
