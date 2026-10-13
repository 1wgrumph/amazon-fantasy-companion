ROLE
Reviewer (BEARING_ROLE=reviewer), Lifecycle AFC-2026-10-11, slice S06-fix (SD-034). RESPONSIBILITY: independent review of one exact candidate for introduced actionable defects. Load the bearing-lite reviewer skill. You did not author this change.

STATE
FACTS: Candidate https://github.com/alphazede/Alphazedehq/pull/309, branch afc/s06-fix-section-prose, head 8f6fb43ffc1f0c79b828ae3931e9eb9b42b9d085, base (merge-base) 120dee00207425201aa77d1f42f3756ee6bc406e. Worktree (cwd) $HOME/alphazede/worktrees/alphazedehq-afc-s06-fix. Packet: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S06-fix-g1.md; implementer receipt evidence/S06-fix/receipt.json.
Intent (SD-034, owner): spec sections read like a real specification. No printed `**BLUF:**` and no `**Frame**` Who/What/Why/How/When/Where labels. An unprinted writer's checklist (Decision, Concern citing UIDs, Mechanism, Rationale, Verification) guides each section. Rule, templates, lint and tests change together; lint must reject the labels.
ASSUMPTIONS to check: reported exit codes reproduce; no remaining label text in templates, SKILL.md or references; lint does not over-reject ordinary prose (e.g. a sentence starting "What" or a heading); removed tests were replaced, not weakened.

OBJECTIVE
Verdict on the candidate against SD-034 and the S06-fix packet. Re-run every VERIFY command yourself:
- skill tests (stock pattern incl. size/metadata and trigger) exit 0
- template build exit 0 and `! grep -nE '\*\*(BLUF|Frame|Who|What|Why|How|When|Where):?\*\*' <built template>`
- `bash tools/ci/local-gates.sh` exit 0

REQUIRED CAPABILITIES
OCR delegate mode, required: `ocr delegate preview --from 120dee00207425201aa77d1f42f3756ee6bc406e --to 8f6fb43ffc1f0c79b828ae3931e9eb9b42b9d085`, then `ocr delegate rule <every listed file>`; per-file OCR section; tool failure = typed gap with exact error. Reverify: not applicable — no compiled binary.

AUTHORITY
Read-only. Write only $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S06-fix-review-result.md. No commits, PR comments or merges. Other agents work concurrently in other worktrees.

RETURN
Verdict PASS | REPAIR_REQUIRED (any fixable finding => REPAIR_REQUIRED), findings table (ID, P0-P3, file:line, defect, exact fix), re-run exit codes, OCR section, Reverify line, route used, developer_feedback (AC-AFC-DX-04 fields or "no new observations" + tools).

STOP
After the review.
