ROLE
Test Implementer (BEARING_ROLE=test_implementer), Lifecycle AFC-2026-10-11, defect B3 (spec-authoring builder renders Appendix A section references as plain text), bug-triager route per DEC-AFC-SD-037. RESPONSIBILITY: the red regression only. Not the builder.
BUG_ROUTE: bug-triager test_implementer (Claude Code / Claude Opus 5.5 / medium).

STATE
FACTS:
- Dispatch record in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json: lease_id B3T-g1; repository alphazede/Alphazedehq; worktree (cwd) $HOME/alphazede/worktrees/alphazedehq-afc-b3; branch afc/b3-appendix-links; base c323c56f556cf708b7104838d2f2977af015fe67; evidence_dir $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/B3/.
- Defect (found by ST-4-g4 on the AFC spec; receipt $HOME/alphazede/worktrees/amazon-fantasy-companion-st4/docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g4/receipt.json, failure ST4-G4-F1): skills/spec-authoring/scripts/spec_build.py joins trace[req] section names as plain text in the generated Appendix A traceability table, so all 66 rows of the AFC spec carry unlinked section references. Origin: PR #316 added the link rule and lint for section sources but not for builder-generated content. Escape: lint checks sources, not the built file. Owner intent (ST5-F1): every reference to another section is clickable.

OBJECTIVE
Add a test in skills/spec-authoring/tests that builds a fixture spec with traced requirements and asserts every Appendix A section reference is a Markdown link to that section's in-document anchor (and the anchor exists in the built file). Also assert the built file passes the skill's own link rule (run the lint's reference check over the built Appendix). RED on the current builder with assertion failures.

AUTHORITY
Allowed writes: skills/spec-authoring/tests/**; the evidence_dir. Commit (author from env; never Co-Authored-By); push the branch. Prohibited: scripts/**, template/**, other paths, PR creation, merge, force-push.

VERIFY
The spec-authoring test suite (stock invocation per its tests; supply trigger results the way the stock pattern does or run without the trigger test and say so): only the new tests fail, with assertion failures; record text and sha256s.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE; head SHA; changed paths; red receipt; sha256s; developer_feedback ("no new observations" + tools if none).

STOP
After the push with the red receipt recorded.
