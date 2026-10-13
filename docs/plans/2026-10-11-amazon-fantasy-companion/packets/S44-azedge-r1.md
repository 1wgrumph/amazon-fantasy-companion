ROLE
Light Implementer (BEARING_ROLE=light_implementer), Lifecycle AFC-2026-10-11, S44 repair for alphazede/azedge PR #304. RESPONSIBILITY: admit CHANGELOG.md to the foundation-contracts top-level allowlist, nothing else.
BUG_ROUTE: not-a-bug gate allowlist extension required by owner rule #21 (workspace AGENTS.md), not a defect.

STATE
FACTS: worktree (cwd) $HOME/alphazede/worktrees/azedge-afc-s44; branch afc/s44-revision-record (PR #304); head 45c3fa92. tools/ci/foundation-contracts.sh line ~815 fails "unexpected Slice 2.2 top-level repository content: CHANGELOG.md" via is_allowed_slice_top_level_entry. Owner rule #21 (workspace $HOME/alphazede/AGENTS.md): every repository keeps a CHANGELOG.md. Read azedge AGENTS.md first and follow its rules for gate changes and tests.

OBJECTIVE
Add exactly CHANGELOG.md (a root file) to the allowlist in is_allowed_slice_top_level_entry, plus the matching test or fixture if the repository tests that allowlist; update any doc that enumerates the allowlist; add the change to this PR's CHANGELOG.md entry.

AUTHORITY
Allowed writes: tools/ci/foundation-contracts.sh (allowlist only), the allowlist's tests/docs if they enumerate it, CHANGELOG.md; evidence dir $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S44/azedge/. Commit (author from env; never Co-Authored-By); plain push. Prohibited: any other gate change, weakening any other check, merge, force-push. Use TMPDIR=/var/tmp/az for gate runs (tmpfs /tmp has a per-user quota under load).

VERIFY
`bash tools/ci/foundation-contracts.sh` exit 0; the repository's documented fast gates (see AGENTS.md) exit 0; diff touches only the named files.

RETURN
PASS | CONTRACT_FAILURE | ENVIRONMENT_FAILURE; head SHA; changed paths; commands with exit codes; developer_feedback ("no new observations" + tools if none).

STOP
After the push with VERIFY passing, or if the change needs more than the allowlist entry (CONTRACT_FAILURE naming why).
