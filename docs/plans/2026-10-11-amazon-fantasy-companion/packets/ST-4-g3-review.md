ROLE
Reviewer (BEARING_ROLE=reviewer), Lifecycle AFC-2026-10-11, spec track ST-4 generation 3 (architecture specification rewrite). RESPONSIBILITY: independent review of one exact candidate for actionable defects before the owner's spec review. Load the bearing-lite reviewer skill. You did not author this change.

STATE
FACTS:
- Candidate: https://github.com/1wgrumph/amazon-fantasy-companion/pull/10, branch afc/st4-spec, head 771c28958f78e611048528aedbd9ed4490f308e1; review the g3 range 4d9b549696408ddaa5f432bac4911cbc349cb874..771c289 (spec rewrite) and the register deltas 5e59270b8320d6085039f26b64f14897736845f6..4d9b549 (SD-035, two Requirements Engineer commits after a plain merge of main). Worktree (cwd) $HOME/alphazede/worktrees/amazon-fantasy-companion-st4.
- Built spec: spec/amazon-fantasy-companion/amazon-fantasy-companion.md (sources spec/amazon-fantasy-companion/NN-*.md). Register: docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/requirements-register.md (66 UIDs). Packet: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/ST-4-g3.md (owner decisions SD-034, SD-035, SD-036 are stated there; treat them as the contract). Author evidence: docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g3/verification.txt.
- Tooling: $HOME/alphazede/Alphazedehq/skills/spec-authoring/SKILL.md; vendored tools/spec/ (pinned c24e4a3).
ASSUMPTIONS to check: each owner answer in SD-035 is reflected correctly and nowhere contradicted (search for stale Mode A footage, open-parameter wording, old open questions); SD-036 future-direction text cites sources that exist and claims only what they say (open each URL); the YouTube TV comparison claims only what its sources say; sections read as specification prose (decision, concern with UIDs, mechanism, rationale, verification) rather than filler; withdrawn UIDs AFC-PR-049..051 are consistent across register, spec and Appendix A; new AFC-PR-066 is traced.

OBJECTIVE
Verdict on the candidate. Re-run yourself: the skill's build twice with a byte comparison, the skill's lint, the label grep `grep -nE '\*\*(BLUF|Frame|Who|What|Why|How|When|Where):?\*\*'` over spec sources and the built file, a UID coverage check against the register (66, none unknown), and the rule-12 path scan `grep -rnE '(/home/|/Users/)[A-Za-z0-9._-]+/' spec/ docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/` (placeholder users excepted).

REQUIRED CAPABILITIES
OCR delegate mode, required: `ocr delegate preview --from 5e59270b8320d6085039f26b64f14897736845f6 --to 771c28958f78e611048528aedbd9ed4490f308e1`, then `ocr delegate rule <every listed file>`; per-file OCR section; tool failure = typed gap with exact error. Reverify: not applicable — no compiled binary. Visual review: not applicable — no rendered UI; but open the rendered SVG figures referenced by the built spec and check they match the text.

AUTHORITY
Read-only. Write only $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/ST-4-g3-review-result.md. No commits, PR comments or merges. Other agents work concurrently.

RETURN
Verdict PASS | REPAIR_REQUIRED (any fixable finding => REPAIR_REQUIRED), findings table (ID, P0-P3, file:line, defect, exact fix), re-run exit codes, source-check table (URL, claim, supported yes/no), OCR section, Reverify line, route used, developer_feedback ("no new observations" + tools if none).

STOP
After the review.
