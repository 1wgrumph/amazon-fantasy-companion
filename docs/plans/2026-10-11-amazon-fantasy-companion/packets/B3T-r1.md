ROLE
Test Implementer (BEARING_ROLE=test_implementer), Lifecycle AFC-2026-10-11, B3 repair round 1 (review findings B3-R1, B3-R2), bug-triager route per DEC-AFC-SD-037. RESPONSIBILITY: red regressions only. Not the builder.
BUG_ROUTE: bug-triager test_implementer (Claude Code / Claude Opus 5.5 / medium).

STATE
FACTS:
- Dispatch record in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json: lease_id B3T-r1; worktree (cwd) $HOME/alphazede/worktrees/alphazedehq-afc-b3; branch afc/b3-appendix-links (PR alphazede/Alphazedehq#320); head 2b46eae6e855629ef161075ba32bf76d9c7cc0c1; evidence_dir $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/B3/r1/.
- Review result with reproductions: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/B3-review-result.md. B3-R1 (P2): spec_build.py:140 links duplicate headings to the last occurrence (section_anchors keyed by title). B3-R2 (P2): title/slug collisions (e.g. two headings whose GitHub slugs collide, or a heading slug equal to another's deduplicated slug like "foo-1") produce wrong targets; GitHub appends -1, -2 to repeated slugs in document order.
- Use TMPDIR=/var/tmp/az.

OBJECTIVE
Add regressions in skills/spec-authoring/tests: (1) two sections with the same title, each traced by different requirements: each Appendix A link targets its own heading's anchor (computed independently with GitHub's slug + dedupe rules over the built file, in document order) and every anchor exists; (2) a slug collision case from the review receipt. RED on the current builder (assertion failures).

AUTHORITY
Allowed writes: skills/spec-authoring/tests/**; the evidence_dir. Commit (author from env; never Co-Authored-By); plain push. Prohibited: scripts/**, template/**, other paths, merge, force-push.

VERIFY
spec-authoring suite on a clean tree (deselect the trigger test and say so): only the new tests fail, assertion failures; sha256s.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE; head SHA; red receipt; sha256s; developer_feedback ("no new observations" + tools if none).

STOP
After the push with the red receipt recorded.
