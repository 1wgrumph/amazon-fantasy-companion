ROLE
Requirements Engineer, planning session (BEARING_ROLE=requirements_engineer), spec track ST-2 continuation. RESPONSIBILITY: materialize and gate the product requirements register. Load $HOME/.config/muse/skills/requirements-engineer and $HOME/.agents/skills/requirements-engineering/SKILL.md.

STATE
FACTS: Your previous run gated 65 rows (65/65 PASS) and preserved them verbatim in docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/re-st2-receipt.md. Writing the .sdoc was refused by the Requirements System guard. Owner decision DEC-AFC-SD-027 (2026-10-12): the Requirements System .sdoc register is for Alphazedehq only; this product's register is Markdown in this repository, not bound to the Requirements System host.
ASSUMPTIONS to check: the 65 rows in the receipt are complete and unchanged since the gate.

OBJECTIVE
Write docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/requirements-register.md: one Markdown table (UID, statement, rationale, verification method, allocation to ST-3a elements, sources) holding the 65 gated rows unchanged, plus frontmatter (type, title, okf_status, tags) and a short coverage section (issue #1 items, controls, C1..C9). Re-run the requirements-engineering quality gate on the file as written.

AUTHORITY
Allowed writes: that register file and specialists/re-st2b-receipt.md in the same directory. Prohibited: any other path, the Requirements System host, .sdoc files, commits, git operations. Other agents may be editing other paths in this checkout concurrently: verify only your own write set. No absolute home paths.

LOOP
If a row fails the gate as written, classify (transcription error vs real defect); fix transcription errors; list real defects with the failing criterion. Retry only with new evidence.

VERIFY
Row count 65 and UIDs identical to the receipt (mechanical diff); every issue #1 retained item, every control and C1..C9 mapped; gate result per row.

RETURN
PASS | REPAIRABLE_FAILURE | NEEDS_MORE_EVIDENCE | OWNER_DECISION_REQUIRED; changed paths; commands run; evidence; remaining owner questions (list from re-st2-receipt still open); remaining risks; developer_feedback (AC-AFC-DX-04 fields that apply or "no new observations" + tools).

STOP
After the register file and its gate. Do not draft models or the spec.
