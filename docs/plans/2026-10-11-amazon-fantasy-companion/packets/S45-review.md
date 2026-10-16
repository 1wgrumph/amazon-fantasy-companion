ROLE
Reviewer (BEARING_ROLE=reviewer), Lifecycle AFC-2026-10-11, slices S45T+S45 (prevention for AFC defects D1 hook git-env leak and R2 hygiene line echo in the shared setup-pre-commit gate template), bug-triager route per DEC-AFC-SD-037. RESPONSIBILITY: independent review of one exact candidate. You did not author this change.
BUG_ROUTE: bug-triager reviewer (Codex CLI / GPT-6 Astra / high).

STATE
FACTS:
- Candidate: https://github.com/alphazede/Alphazedehq/pull/317, branch afc/s45-gate-template-bugs, head df7a7e8f44165ee196e6112518814ac5cdc17aa9, base 23f0bb28a9ef9e0ec6ca1d4ec130489e8c569beb. Worktree (cwd) $HOME/alphazede/worktrees/alphazedehq-afc-s45.
- Packets: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S45T-g1.md and S45-g1.md. Reference fixes in 1wgrumph/amazon-fantasy-companion origin/main tools/ci/gate.sh (commits 6f67499, 17b40b4).
ASSUMPTIONS to check: both new tests fail on the base template and pass on the head (red-then-green); no existing test weakened; the hygiene check still fails closed on any git error; the unset list covers the git location variables hooks export; gate-contract.md matches the code.

OBJECTIVE
Verdict. Re-run: the S45T tests against both base and head templates, `bash skills/setup-pre-commit/tests/test-install-hooks.sh`, the creator/metadata test, shellcheck, `bash tools/ci/local-gates.sh`; and exercise a generated repo's real pre-commit hook (install-hooks.sh into a throwaway repo, commit without --no-verify) to confirm no writes leak and whitespace findings print without line text.

REQUIRED CAPABILITIES
OCR delegate mode, required: `ocr delegate preview --from 23f0bb28a9ef9e0ec6ca1d4ec130489e8c569beb --to df7a7e8f44165ee196e6112518814ac5cdc17aa9`, then `ocr delegate rule <every listed file>`; per-file OCR section; tool failure = typed gap with exact error. Reverify: not applicable — no compiled binary.

AUTHORITY
Read-only. Write only $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/packets/S45-review-result.md. No commits, PR comments or merges.

RETURN
Verdict PASS | REPAIR_REQUIRED (any fixable finding => REPAIR_REQUIRED), findings table (ID, P0-P3, file:line, defect, exact fix), red-then-green receipt, re-run exit codes, OCR section, Reverify line, developer_feedback ("no new observations" + tools if none).

STOP
After the review.
