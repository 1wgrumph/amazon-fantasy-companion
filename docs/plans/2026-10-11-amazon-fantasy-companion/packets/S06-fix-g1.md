ROLE
Product Implementer (BEARING_ROLE=implementer), spec-and-docs lane (tech-writing), S06 follow-up fix for owner decision DEC-AFC-SD-034. RESPONSIBILITY: change how spec-authoring sections are written so specs read like real specifications.

STATE
FACTS:
- Dispatch record lease_id S06-fix-g1 in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json; worktree (cwd) $HOME/alphazede/worktrees/alphazedehq-afc-s06-fix; branch afc/s06-fix-section-prose; base 120dee00207425201aa77d1f42f3756ee6bc406e (full SHA); evidence_dir docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S06-fix/ (planning worktree); lease alphazedehq-skills/spec-authoring.
- Today skills/spec-authoring/references/section-rules.md (lines 16-18) requires a printed `**BLUF:**` sentence and a `**Frame**` list (Who/What/Why/How/When/Where); the template sections carry them and lint enforces them. Owner decision SD-034: remove both printed forms. The opening sentence of each section states its point in the architect's voice. An UNPRINTED writer's checklist guides each section: Decision (what the section decides or defines), Concern (the driving requirement or stakeholder concern, citing requirement UIDs), Mechanism (how it works: interfaces, dependencies), Rationale (why this option; alternatives rejected), Verification (how it is proven). Tables/figures rules stay.
- Stock skill-test pattern: skills/release-process/tests/. Keep SKILL.md lean (<60 lines).
Other agents work concurrently in other worktrees.

OBJECTIVE
Update spec-authoring: section-rules.md (checklist replaces BLUF/Frame; state they are never printed), every template section (remove BLUF/Frame stubs; leave a one-line HTML comment listing the 5 checklist questions as authoring guidance, which the build strips from output — verify the build strips comments, else use no comment), lint (stop requiring BLUF/Frame; FAIL if a section prints `**BLUF` or `**Frame` or the old W-labels; FAIL if a section's first paragraph is empty), tests (positive and negative for the new lint rules), and any SKILL.md wording. Build the template spec and confirm output contains no BLUF/Frame labels. Commit, push, open ONE draft PR.

AUTHORITY
Allowed writes: skills/spec-authoring/** and the evidence_dir. Commit (author from env; never Co-Authored-By); push; draft PR. Prohibited: other paths, merge, force-push.

LOOP
Change, test, build, classify failures, retry only with new evidence.

VERIFY
Skill tests exit 0 (stock pattern incl. size/metadata and trigger); template build exit 0 and `! grep -nE '\*\*(BLUF|Frame|Who|What|Why|How|When|Where):?\*\*' <built template>`; `bash tools/ci/local-gates.sh` exit 0.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE; lease_id; head SHA; PR URL; diff summary; command exit codes; developer_feedback (AC-AFC-DX-04 fields that apply).

STOP
After the draft PR is open with VERIFY passing.
