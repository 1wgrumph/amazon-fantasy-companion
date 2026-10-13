ROLE
Product Implementer, spec-and-docs lane (profile tech-writing; BEARING_ROLE=implementer), spec track ST-4, generation 4. RESPONSIBILITY: apply the owner's two ST-5 approval conditions to the approved specification and add this repository's changelog. Not content changes, not review, not merge.

STATE
FACTS:
- Dispatch record in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json: lease_id ST-4-g4; worktree (cwd) $HOME/alphazede/worktrees/amazon-fantasy-companion-st4; branch afc/st4-spec (PR #10, https://github.com/1wgrumph/amazon-fantasy-companion/pull/10); base 771c28958f78e611048528aedbd9ed4490f308e1; evidence_dir docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g4/.
- Owner approval DEC-AFC-APPROVAL-ST5 covers content at 771c289; conditions: ST5-F1 "I think we need hyperlinks when you are referencing either to the document or to other sections in the document ... I know what #Issue 1 is but someone else wouldn't so clickable links would be nice"; ST5-F2/SD-038 revision rows show what changed and link to the change; "make sure this is used here".
- The shared spec-authoring skill now enforces both (Alphazedehq main 8f5c4c2a28da984b267611b62d0801666ab2d70f, PR #316): lint fails unlinked issue/PR, section and document references; spec.yaml revisions carry `changes` and `links` (pr, diff), rendered in Revision History. Read $HOME/alphazede/Alphazedehq/skills/spec-authoring/SKILL.md and references. The S43 reviewer's probe found 19 unlinked references in this spec.
- tools/spec/ vendors c24e4a3 (VENDORED.md); re-vendor with the skill's vendor script to 8f5c4c2 (S42 method; normalize file modes if the pristine-copy guard refuses on umask-only differences). THIRD_PARTY_NOTICES.md changes only if the notice text changed.
- Repository rule (workspace AGENTS.md #21, Hackathons/AGENTS.md): every landed PR adds a CHANGELOG.md [Unreleased] entry linking the PR. This repo has none yet. Merged PRs so far: #2 #3 #4 #5 #6 #7 #8 #9 #11 (read titles with `gh pr list -R 1wgrumph/amazon-fantasy-companion --state merged`).
- core.hooksPath=.githooks is active: commits run the gate (tools/ci/gate.sh --changed); let it run (do not use --no-verify unless the gate fails for a reason outside your write set; then report it).

OBJECTIVE
0. First `git fetch origin && git merge --no-edit origin/main` (plain merge; brings tools/ci gate, .githooks and the ci workflow; no conflicts expected). Commits then run the repository gate through the hooks.
1. Re-vendor tools/spec to 8f5c4c2.
2. Make every reference in spec/amazon-fantasy-companion/** clickable: issue #1 -> https://github.com/1wgrumph/amazon-fantasy-companion/issues/1; PRs; section cross-references -> in-document anchors; documents (register, models, plans, scope decisions) -> relative links that resolve from the source and built file. No content change beyond links.
3. Add revision 0.3 in spec.yaml: changes = sections touched; links = PR #10 URL and its files/compare URL; backfill 0.2 with its changes and the same PR link. Rebuild.
4. Create CHANGELOG.md (Keep a Changelog): [Unreleased] entry for PR #10 (spec revision 0.3 with links), and a dated history list of the already-merged PRs with links.

AUTHORITY
Allowed: the plain merge in step 0. Allowed writes: tools/spec/**, THIRD_PARTY_NOTICES.md (only if required), spec/amazon-fantasy-companion/**, CHANGELOG.md, the evidence_dir. Commit (author from env; never Co-Authored-By); plain push of afc/st4-spec; update PR #10 description (gh api PATCH if gh pr edit fails). Prohibited: docs/plans/ outside evidence_dir, .github/, .githooks/, tools/ci/, git config, merge, force-push.

LOOP
Edit, build, lint, fix; classify failures (content / tool / environment); retry only with new evidence.

VERIFY (command, exit code, output tail)
- Vendor check (CMD-SPEC-VENDOR with <azhq_d5_sha>=8f5c4c2a28da984b267611b62d0801666ab2d70f) exit 0.
- Skill build twice byte-identical; skill lint exit 0 (includes the new link and revision rules); label grep clean.
- Every relative link in the built file and sources resolves (script check; record it); UID coverage still 66/66.
- `bash tools/ci/gate.sh` exit 0; rule-12 path scan clean.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE | ENVIRONMENT_FAILURE; head SHA; changed paths; commands with exit codes; link count added; developer_feedback (spec-authoring link/revision rules: worked well, needs work).

STOP
After the push with VERIFY passing, or a typed failure.


ST-4 GENERATION 5 RESUME (supersedes stale pins/dependencies in g4 above):
Owner begin authorizes completion of ST5-F1/F2 and planning; product scope unchanged. Route remains Codex CLI / GPT-6 Astra / medium (tech-writing implementer). Read current handoff/journey; do not repeat accepted g3 review or author content changes.
B3 merged as alphazede/Alphazedehq#320 at 04678835350b529b44ab69ee5f805ca21cab5e76. Use this exact reviewed source revision for vendor (contains new link/revision rules and appendix anchor fixes). B2 PR14 must be verified MERGED by parent before dispatch; its main gate now compares built output with index, fixture includes linked docs.
Reuse g4 uncommitted work (144 links, revision0.3, changelog), preserve all approved text. Before merging origin/main, preserve the existing untracked CHANGELOG.md in your evidence directory if needed; B2 now adds a tracked CHANGELOG.md. Combine B2's PR14 entry with g4 PR10/revision/history entries, never overwrite or drop either. Do not stash or reset. Routine safe merge/conflict resolution is authorized; return any substantive conflict beyond content-preserving record reconciliation.
Write set continues: tools/spec/**, THIRD_PARTY_NOTICES.md only required notice changes, spec/amazon-fantasy-companion/**, CHANGELOG.md, Phase2 evidence/ST-4/g5/**. No other plan artifacts or control journey edits. Load scan-software-supply-chain for the vendoring admission; preserve the prior provenance, verify the exact reviewed source revision and diff, and record its required receipt. Preserve all unmodified files. Use vendor CLI's documented upgrade path; verify pristine-copy/hash checks.
Run build/lint/relative and anchor links/66 UID checks, byte-identical rebuild, gate, private-path hygiene. The gate runs hooks normally after B2 merge; do not bypass. Commit and push afc/st4-spec ordinarily; update PR10 body via REST PATCH/readback. Leave PR unmerged for one independent delta review of the owner's link/revision amendment (g3 content already reviewed). No release/tag, no public export. No nested agents. Include exact source pin, candidate head, all command exits, link/UID counts, changed files, and developer_feedback. Primary result receipt evidence/ST-4/g5/receipt.json. Return after push.
