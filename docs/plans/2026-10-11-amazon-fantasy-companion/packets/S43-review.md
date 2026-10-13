ROLE
Reviewer (BEARING_ROLE=reviewer), Lifecycle AFC-2026-10-11, slice S43 (owner decisions DEC-AFC-SD-038 and ST-5 items ST5-F1/F2). RESPONSIBILITY: independent review of one exact candidate for introduced actionable defects. Load the bearing-lite reviewer skill. You did not author this change.

STATE
FACTS:
- Candidate: https://github.com/alphazede/Alphazedehq/pull/316, branch afc/s43-revision-record, head 68172c3e987d1825efff3b9fead02ff05d3a9def, base 23f0bb28a9ef9e0ec6ca1d4ec130489e8c569beb. Worktree (cwd) $HOME/alphazede/worktrees/alphazedehq-afc-s43.
- Packet with the owner's words and objective: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S43-g1.md; author receipt evidence/S43/receipt.json. Canonical rule text: $HOME/alphazede/AGENTS.md cross-repo rule #21.
ASSUMPTIONS to check: the link lint catches unlinked issue/PR, section and document references but not code spans/fences, URLs inside links, headings or ordinary prose ("section" as a word, version numbers, dates); revision rows render changed sections and PR/diff links and the first revision is exempt; ship-pull-request's CHANGELOG step creates the file when missing and never duplicates entries; setup-a-repo seeds CHANGELOG.md; release-process moves [Unreleased] under the new version; SKILL.md sizes within lean limits; AGENTS.md pointer mirrors rule #21; no existing test weakened; reported exit codes reproduce.

OBJECTIVE
Verdict on the candidate. Re-run each changed skill's tests (stock pattern; supply trigger results by classifying trigger-requests.json yourself from SKILL.md), the spec-authoring template build twice with byte comparison and template lint, the negative fixtures, `bash tools/ci/local-gates.sh`, and run the new lint against the AFC spec sources (`git -C $HOME/alphazede/Hackathons/amazon-fantasy-companion show origin/afc/st4-spec:spec/amazon-fantasy-companion/<file>` into a temp dir) to report false positives/negatives on real prose.

REQUIRED CAPABILITIES
OCR delegate mode, required: `ocr delegate preview --from 23f0bb28a9ef9e0ec6ca1d4ec130489e8c569beb --to 68172c3e987d1825efff3b9fead02ff05d3a9def`, then `ocr delegate rule <every listed file>`; per-file OCR section; tool failure = typed gap with exact error. Reverify: not applicable — no compiled binary.

AUTHORITY
Read-only. Write only $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S43-review-result.md. No commits, PR comments or merges. Other agents work concurrently.

RETURN
Verdict PASS | REPAIR_REQUIRED (any fixable finding => REPAIR_REQUIRED), findings table (ID, P0-P3, file:line, defect, exact fix), re-run exit codes, AFC-spec lint probe results, OCR section, Reverify line, route used, developer_feedback ("no new observations" + tools if none).

STOP
After the review.
