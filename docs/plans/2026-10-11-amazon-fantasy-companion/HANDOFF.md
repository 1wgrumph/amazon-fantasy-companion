# Current planning-lead handoff — AFC-2026-10-11

Updated 2026-10-13T05:39:44Z. Current Codex controller is active; check the lease and live
children before any resume. Do not duplicate work from the historical handoff
below. Owner said **begin**, then **“You are the planning lead now”**; recorded
as DEC-AFC-SD-039. Scope is planning completion and, after integrated approval,
GitHub issue/milestone organization. Product execution stays on hold.

## Verified completed prerequisites

- AFC PR #14 (B2) merged `c2468c9e7850745f1245bf4cfc81e55047e3fb55`:
  39 tests, independent red/green + OCR, all four hosted checks.
- Alphazedehq PR #320 (B3) merged `04678835350b529b44ab69ee5f805ca21cab5e76`:
  81 tests, prior review/repair preserved, local gate, changelog-only integration.
- azedge PR #304 merged `5ac113e343df448b23cff28cab6e3938ec64a2de`:
  independent review, foundation check, fast gates 29 PASS / 12 SKIP.
  Previously reported workspace-test flake is not claimed fixed or reproduced.
- AFC PR #10 merged `92f3ed1a0d178d2704c0efdc073ad332dc67b79f`:
  ST5-F1/F2 satisfied, spec0.3, 749 links/anchors, 66 UIDs, byte-identical build,
  independent amendment review, gate39tests and hosted4/4. No release/tag.
- PR #11 was actually OPEN, contrary to the old handoff. Closed as redundant:
  its patch579b951 is already on main as d259c169. No obsolete vendor merge.
- Merged task worktrees/local/remote branches cleaned. ST4 g4 and g5-review
  untracked evidence preserved byte-for-byte in control evidence/ST-4/preserved
  and restored to the Phase2 plan's canonical evidence/ST-4 paths.

## Current planning work

Control remains journey.json in this planning worktree. Its retired branch
**must never be pushed**. Publish sanitized records from a safe current branch.

Phase2 worktree: `$HOME/alphazede/worktrees/amazon-fantasy-companion-phase2-plan`,
branch `plan/2026-10-12-afc-phase-2`, HEAD
`7f000aff70e435b0cac923931fd818c69111f07d` (main/spec merge; gate passed).
Plan directory: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/`.
All current planning artifacts are uncommitted; preserve them.

- Technical plan/design/graph corrected by current lead. Full63active product
  UIDs retained, 3 withdrawn; 52 slices, 44 integration steps, 39 issue groups,
  13 TDD pairs, five milestones. X05's issue closes in M2; M1 is its historical
  fixture checkpoint. Product-execution hold is explicit in proposed authority.
- TE initial authorship + finalization: 100 proof cases; finalization has70
  command IDs and concrete prospective tool ownership/report/threshold bindings.
  Runtime qualification and APK Reverify semantics remain typed gaps.
- IE correction2 is complete. Do not reset its spent correction count.
  Exact source corrections applied; transition evidence is in
  `evidence/P2-6/codex-lead/`. No independent Phase2 planning review spent yet.
- PI generated implementation.json and the Manifest, but final refresh is
  still required. It incorrectly disabled four required SysML views after an
  XML-prolog renderer refusal. Parent rejected that workaround. Light packet
  removed only their39-byte XML declarations; XML trees and SysML source hashes
  are unchanged; all four pass the renderer sanitizer. Final PI must restore
  selected/required=true and embed all seven views, never omit required views.
- **Active owning TE continuation:** `specialists/te-p2-filing-binding-prompt.md`
  and its local run log. It corrects only tracking command binding and current
  source/authority hashes after the actual helper-scope refusal. Same frozen
  Codex CLI / GPT-6 Astra / xhigh session; no new review/assurance.
- The helper policy does not cover this personal repository. All39 helper
  dry-runs refused on scope before inspecting bodies; not passing checks.
  `specialists/filing-scope-resolution.md` and
  `evidence/github-work-items/repository-preflight.json` record39 passing
  local body/label/target checks, zero submissions, no policy change.
  After approval use the repository-applicable workflow; re-evaluate scope at
  action time and use the mandatory helper if policy then covers the target.
- Draft39issue bodies and5milestone payloads are under
  `evidence/github-work-items/`. Refresh their final source digest/mappings
  against the finalized package before approval; nothing created remotely.

## Next actions, in order

1. Wait for and verify the active TE filing-binding receipt; preserve100proofs,
   70commands, all frozen routes/capabilities and source transition history.
2. Dispatch bounded PI refresh on frozen Muse Code / Muse Spark1.3 / max using
   TE `evidence/te-p2-finalize/pi-refresh.json` plus the latest binding receipt.
   Restore required views; normalize M2 due_on to `2026-10-17T01:00:00Z` with
   its explanation separate; preserve X05 checkpoint semantics and scope-aware
   filing. Split the overly long register path/hash identity value for readable
   layout without changing source authority. Regenerate/freeze/render/check.
3. Validate issue/milestone drafts, sanitized evidence, complete source coverage
   and proposed authority. Exclude raw agent run logs. One known control-copy
   home path is in evidence/S44/azedge-review/review.md; sanitize for publication.
4. Commit/push the planning candidate (never local main or retired control
   branch), open its PR, and run the **one** independent planning-review slot
   on frozen primary Muse Code / Muse Spark1.3 / max. At most one aggregate
   repair, deterministic closure, no automatic second review.
5. Present the complete package and concrete tracking drafts for one integrated
   owner approval. Only that approval can authorize tracking creation; it does
   not start product code/spikes/deployment. Complete authorized tracking after
   approval; preserve all protected publication/credential boundaries.

Local loopback preview exists for the current Manifest. Browser DOM/navigation
work; screenshots timed out three times (capture gap, never a visual PASS).
The preview must be refreshed after final PI rendering. Keep no intermediate
browser tab as a final deliverable. No app, backend, AWS or device work ran.

Claude weekly usage limit was confirmed; existing specialist fallbacks were
used. Do not switch routes for configuration/runtime errors. Every codex exec
must receive stdin from /dev/null unless actively supplying input. Keep raw
agent logs local and use the existing frozen snapshots, not live-profile edits.

---

# Historical handoff from the preceding Orchestrator
# Orchestrator handoff — AFC-2026-10-11 (next Orchestrator: Codex CLI)

Source: Claude Code Orchestrator session 5cfe4230-d897-4ac4-b3d0-f27628781c70, 2026-10-12, stopped at the Claude session limit.
Canonical copy: docs/plans/2026-10-11-amazon-fantasy-companion/HANDOFF.md in 1wgrumph/amazon-fantasy-companion.

ROLE
Bearing Lite Orchestrator (running in Codex CLI) for Lifecycle AFC-2026-10-11 (repo 1wgrumph/amazon-fantasy-companion; Amazon Developer Hackathon entry).
RESPONSIBILITY: sequence and dispatch slices on their frozen routes, write dispatch/return/landing records, verify returns yourself, land verified PRs, and own the owner conversation. Never implement or self-review.

STATE
FACTS (verified by me unless marked "agent-reported"):
- Control state: $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json. It holds decisions DEC-AFC-SD-001..038, approvals, the frozen profile snapshots, and every dispatch/return/landing record. Packets are under packets/ and specialists/ there. Its records up to this handoff were scrubbed ($HOME paths, fake keys redacted, gitleaks clean) and published on main by the handoff PR (branch plan/afc-handoff-records); the planning worktree's local branch plan/2026-10-11-amazon-fantasy-companion (0b987de + edits) is superseded by that PR and must not be pushed. Keep writing journey.json in the planning worktree, and publish later records the same way (scrub, gitleaks, PR).
- Owner decisions this session:
  - SD-035: answers to the spec open items. Excitement levels Off/Mild/Hype. Text 24px body, 32px scores. No Mode A footage: the fallback is alerts + Watch only, with a full-screen panel. Provider order Prime TNF, ESPN, DirecTV Stream, YouTube TV; local games show the channel. Close game = within 8 points in Q4/OT. Stale after 60 s. Scoring presets PPR and Half-PPR (default Half-PPR). License Apache-2.0. Restore the S8 ledger.
  - SD-036: discuss AWS analytics and the NBA on Prime in the spec and write-up only; no build scope.
  - SD-037: defects route to the bug-triager profile (Muse implementer, Codex GPT-6 Astra reviewer; Claude Opus test implementer first under TDD), with bug-hunter-triage. Rule is in Hackathons/AGENTS.md.
  - SD-038: revision record. Every landed PR adds a CHANGELOG [Unreleased] entry linking its PR. Spec revisions list changed sections and link PR + diff. Releases go through release-process. Workspace AGENTS.md #21, Hackathons/AGENTS.md.
  - DEC-AFC-APPROVAL-ST5: spec content approved at PR #10 771c289, conditional on clickable references (ST5-F1) and linked revision rows (ST5-F2). Owner said to proceed to Phase 2 planning once those land.
- Merged (verified): AFC #9 (S09 gate/hooks), #11, #12 (B1 hygiene fix). Alphazedehq #309, #316 (S43 links/revision/changelog skills), #317 (S45), #322 (B4). betbot #69, odi-graph #19, maestro #96, requirements-system #540. AFC core.hooksPath=.githooks is re-installed.
- Open work:
  1. B2, AFC gate (worktree $HOME/alphazede/worktrees/amazon-fantasy-companion-b2, branch afc/b2-gate-spec-staged, HEAD = origin/main 423496e). The B2T-g1 test-implementer run hit the session limit and committed nothing (packet packets/B2T-g1.md). Defects: B2a, gate_support.copy_repo excludes docs/plans (test-only); B2b, tools/ci/gate.sh spec area runs `git diff --exit-code HEAD -- <output>` and should compare against the index (`git diff --exit-code -- <output>`).
  2. B3, Alphazedehq PR #320 (worktree alphazedehq-afc-b3, head 1eadf6e). One review plus one repair round are done; repair B3-r1 is PASS (agent-reported). Still to do: my own verification, local-gates, land.
  3. azedge PR #304 (worktree azedge-afc-s44, head b8604b5d): allowlist admits CHANGELOG.md; PASS (agent-reported). Still to do: verify, land. Agent-reported pre-existing flaky test: provider_reads_once_per_admitted_attempt (BrokenPipe, ~1/3 of parallel runs). That is a bug for bug-triager.
  4. ST-4 g4 spec links (worktree amazon-fantasy-companion-st4, branch afc/st4-spec, PR #10). Uncommitted work: 144 links, revision 0.3, CHANGELOG.md, and tools/spec re-vendored to 8f5c4c2. It is blocked on B2 + B3. After both land, merge main, re-vendor tools/spec to the new Alphazedehq main, rebuild, and commit (packet packets/ST-4-g4.md, receipt in evidence/ST-4/g4/).
  5. Phase 2 Planning and Design (worktree amazon-fantasy-companion-phase2-plan, branch plan/2026-10-12-afc-phase-2, packet specialists/pd-phase2-prompt.md). This run also hit the session limit (rc=1). It left partial artifacts: technical plan, design.md, authority.json. Relaunch it; it may reuse what is there.
- Environment: /tmp is tmpfs with a per-user quota that other sessions' azedge temp dirs fill. Run gates and agents with TMPDIR=/var/tmp/az. GUI work uses DISPLAY=:50 only.
- Codex orchestrator notes: load skills by path ($HOME/.codex/plugins/cache/bearing-lite/bearing-lite/1.1.6/skills/bearing-lite/SKILL.md, $HOME/alphazede/Alphazedehq/skills/*, $HOME/.claude/skills/bug-hunter-triage/SKILL.md). Launch children as separate processes with stdin </dev/null and output to packets/<id>-run.log, appending an exit line: Claude `claude -p --model claude-opus-5-5 --effort <r> --dangerously-skip-permissions < packet`; Muse `muse exec --model muse-spark-1.3 --reasoning-effort max --workspace <wt> --yolo --prompt-file <packet> < /dev/null`; Codex `codex exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check -m <model> -c model_reasoning_effort=<r> -C <wt> - < packet`. Set GIT_AUTHOR_NAME/EMAIL per child harness (e.g. Codex <1wgrumph+codex@gmail.com>). Write packets with quoted heredocs or files (unquoted heredocs execute backticks). Never `pkill -f` a pattern that also matches your own shell; kill by PID.
- Claude routes (test_implementer, P&D) reset at 09:30 America/Chicago; if still limited, that is a typed gap; use the frozen ordered fallback (bug-triager test_implementer fallback: Codex GPT-6.1 Sol high) and record it.
- A Claude-session cron (2c8e4924, 02:02 CDT 2026-10-13) may also resume; check for duplicate dispatch before launching (pgrep and the latest dispatch_record).
ASSUMPTIONS to check: remote branch heads match the SHAs above; no agent is still running (pgrep codex/muse/claude); the Muse and Codex routes are available.

OBJECTIVE
The AFC spec on PR #10 is merged with every reference clickable and linked revision rows (ST-5 conditions met), and the Phase 2 implementation plan and milestone definitions are frozen (plan-package.cjs PASS) and presented to the owner for one integrated approval.

AUTHORITY
Allowed: everything the AFC Lifecycle authority (AUTH-AFC-2026-10-11-002, the approvals above) grants the Orchestrator. That covers dispatching on frozen routes (bug fixes on bug-triager), writing journey records, verifying, landing PRs with `gh pr merge N -R <literal repo> --rebase --delete-branch` as separate commands (requirements-system uses tools/ci/merge-queue.sh land N), cleaning merged worktrees, and tagging spec-v0.3 per SD-038.
Prohibited: creating GitHub milestones before owner approval of the Phase 2 plan; destructive git without owner OK; force-push; git switch; squash merges; publishing anything external beyond the authorized repos; API-key services.

TIME BUDGET
session: 6 h; per-call: 20 min; at T minus 5 stop new dispatches and update this handoff and journey.json.

LOOP
Read journey.json and agent logs
→ Select ready items (B2 red tests; B3 verify+land; azedge verify+land; P&D relaunch, all in parallel, at most 5 implementation agents)
→ Write a dispatch_record with the full base SHA, then dispatch
→ Verify each return yourself (tests, gates, hosted checks)
→ Land, or route a typed failure back as one repair round
→ After B2 and B3 land: ST-4 g5 (re-vendor, rebuild, commit), independent review, merge PR #10, release spec-v0.3
→ Present the frozen Phase 2 plan to the owner.

VERIFY
- AFC repository gate: `bash tools/ci/gate.sh` exit 0, plus PR hosted checks (Detect changes, gate/spec, gate/docs, gate/hygiene) pass on each landed head.
- Alphazedehq: `bash tools/ci/local-gates.sh` exit 0 (receipt written) before each merge.
- PR #10 built spec: spec-authoring lint exit 0 (links + revision rules), two builds byte-identical, all anchors resolve, 66/66 UIDs.
- Phase 2: `node $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/hooks/plan-package.cjs <phase-2 plan dir>` PASS.
- Every dispatch has a prior dispatch_record; every landing has a landing_record.

RETURN
Outcome: PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE | ENVIRONMENT_FAILURE | NEEDS_MORE_EVIDENCE | OWNER_DECISION_REQUIRED.
Include merged PRs with merge SHAs, commands with exit codes, the Phase 2 review package path, remaining risks, and blockers.

STOP WHEN
- PR #10 is merged and the Phase 2 plan is presented for owner approval;
- an owner decision is required (scope change, plan approval, destructive git, credentials);
- a repair round fails or would change approved scope (OWNER_DECISION_REQUIRED naming the candidate);
- a required route is unavailable (typed gap, never substitution).
