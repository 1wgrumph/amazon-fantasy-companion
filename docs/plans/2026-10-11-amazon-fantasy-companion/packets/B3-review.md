ROLE
Reviewer (BEARING_ROLE=reviewer), Lifecycle AFC-2026-10-11, defect B3 (spec-authoring builder Appendix A section references unlinked), bug-triager route per DEC-AFC-SD-037. RESPONSIBILITY: independent review of one exact candidate. You did not author it.
BUG_ROUTE: bug-triager reviewer (Codex CLI / GPT-6 Astra / high).

STATE
FACTS: Candidate https://github.com/alphazede/Alphazedehq/pull/320, branch afc/b3-appendix-links, head 2b46eae6e855629ef161075ba32bf76d9c7cc0c1, base c323c56f556cf708b7104838d2f2977af015fe67. Worktree (cwd) $HOME/alphazede/worktrees/alphazedehq-afc-b3. Packets B3T-g1.md, B3-g1.md and evidence/B3/ in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/. AFC spec sources with pending link work: $HOME/alphazede/worktrees/amazon-fantasy-companion-st4/spec/amazon-fantasy-companion/ (uncommitted; copy, do not modify).
ASSUMPTIONS to check: red on base, green on head; anchors match GitHub heading slugs (including punctuation and duplicate headings); builds stay byte-identical; no test weakened; the built AFC spec has all 66 rows linked with existing anchors.

OBJECTIVE
Verdict. Re-run the spec-authoring suite on a clean tree (trigger test: classify trigger-requests.json yourself from SKILL.md and supply results), template build twice + cmp, template lint, a temp-dir build of the AFC spec copy with a link/anchor check, and `bash tools/ci/local-gates.sh`. Use TMPDIR=/var/tmp/az (tmpfs /tmp has a per-user quota under load).

REQUIRED CAPABILITIES
OCR delegate mode, required: `ocr delegate preview --from c323c56f556cf708b7104838d2f2977af015fe67 --to 2b46eae6e855629ef161075ba32bf76d9c7cc0c1`, then `ocr delegate rule <every listed file>`; per-file OCR section; tool failure = typed gap. Reverify: not applicable — no compiled binary.

AUTHORITY
Read-only. Write only $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/B3-review-result.md.

RETURN
Verdict PASS | REPAIR_REQUIRED, findings table (ID, P0-P3, file:line, defect, exact fix), red-then-green receipt, re-run exit codes, OCR section, Reverify line, developer_feedback.

STOP
After the review.
