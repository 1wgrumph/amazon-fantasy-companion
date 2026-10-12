---
type: integration-plan
status: gaps
lifecycle: AFC-2026-10-11
role: integration_engineer (planning session)
revision_note: "Phase 1 regeneration after DEC-AFC-SD-023 and DEC-AFC-SD-024. The f885e48 version (41-slice product plan) stays in git; its product findings are Phase 2 input."
inputs: amazon-fantasy-companion-technical-plan.md, design.md, specialists/slice-graph.md, journey.json, f885e48 specialists/integration-plan.md
---

# Integration plan — AFC-2026-10-11 Phase 1 (planning session)

This plan defines how the 13 Phase 1 slices (S01, S02, S03, S06, S07, S06L,
S42, S09T, S09, S11T, S11, S41, S08) assemble into one Phase 1 candidate
across two repositories. It covers items and versions, interface checks,
order, entry criteria, stubs, configuration identity, post-step V&V handoff,
anomaly handling, rollback, recovery, cut-offs, the final candidate, the
Phase 2 entry receipt and the closeout assessment inputs. It does not
implement, change requirements or design, author tests or review.

Command IDs come from `slice-graph.md`. IDs marked *proposed* are new; the
Planning Test Engineer finalizes them in `seit.json`. The Plan Integrator
copies the `integration_plan` JSON block into `implementation.json`.

**Outcome: GAPS.** The assembly strategy is complete. Ten slice-graph,
design or technical-plan defects (IE-P1-F01..F10) need correcting before the
affected slices dispatch. The most serious is F01: read literally, the
review rule in the plan deadlocks Wave 2. None of the ten needs a new owner
decision. Each has exact corrected text in `concurrency_findings`. The owner
sees the corrected package at the integrated review.

## Assembly model

- **Items.**
  - *this*: `1wgrumph/amazon-fantasy-companion`. S07, S06L, S42, S09T+S09
    and S08 each land through their own PR.
  - *AZHQ*: `alphazede/Alphazedehq`. D4-A (S01), D4-B (S02), D4-C (S03),
    D5 (S06), D4-E (S11T+S11) and D4-F (S41, only if OD-AFC-01 = B) each
    land through their own PR.
- **Integration level.** Each slice (or TDD pair) has one branch in one
  worktree. Its PR merges straight to `main`; Phase 1 has no lane branches.
  - Merge method: `gh pr merge --merge` in both repositories.
  - A merge commit keeps the reviewed PR head SHA as an ancestor of `main`.
    So the Reviewer's exact candidate ref, the CMD-RED test-file digests
    and the TDD author-identity commit order all stay valid after merge.
    Rebase merge is allowed by policy, but it rewrites those SHAs.
  - Never squash, never force-push.
- **Readiness.** A PR merges only when all of these hold:
  - its slice reached its stop condition;
  - it had one Reviewer review at its integration step: OCR delegate mode,
    plus `Reverify: not applicable — Phase 1 changes are skill text, shell
    and Python scripts and workflow YAML; no compiled binary is built or
    claimed` (AC-AFC-REV-01). See F01.
  - it had at most one repair round;
  - deterministic verification is green: the PR's checks plus the slice's
    local command receipts on the PR head.
- **Live skills.** Every harness skill link resolves into the AZHQ main
  checkout, `<workspace>/Alphazedehq/skills/<skill>`. This was verified with
  `readlink` for `setup-pre-commit` in the Claude Code, Codex, `.agents`
  and Cursor skill directories.
  - A merged AZHQ change goes live for every agent on the host only when
    CMD-AZHQ-SYNC fast-forwards that checkout.
  - The checkout is on `main`, level with `origin/main` at
    `47c46f2e16fed060482a1bf3a0e34ddcb9bc57fc`. It has one untracked
    directory (`evals /`), which does not block a fast-forward.
- **Integration receipts.** The Orchestrator records each step's merge SHA,
  command outputs and digests in `journey.json` `execution_receipts`. This
  creates no new tracked write set.

## Interface and compatibility checks

| Contract | Producer → consumer | Static check | Exercised at |
|---|---|---|---|
| CONTRACT-AFC-GATE | S01 template `templates/gate.sh` (azhq.d4a) → S09 `tools/ci/gate.sh` → `.githooks`, `ci.yml`, S11 hook | CMD-CI-VENDOR-PIN (proposed): `tools/ci/VENDORED.md` names azhq.d4a and azhq.d4b, and the vendored `check_workflows.py` equals `skills/setup-a-repo/scripts/check-workflows.py` at azhq.d4b; CMD-WORKFLOW-CHECK | IE-P1-9 CMD-GATE-ALL on the merge commit, plus PR checks `gate / spec`, `gate / docs`, `gate / hygiene`; IE-P1-10 CMD-HOOK-DEMO (proposed) |
| CONTRACT-AFC-HOOK | S11 `hooks/ci-gate-hook.sh` → harness configurations | CMD-HOOK-TEST; CMD-HOOK-INSTALL-SANDBOX (proposed, F04) | IE-P1-10 CMD-HOOK-INSTALL `--verify` (live, from the main checkout) and CMD-HOOK-DEMO |
| CONTRACT-AFC-SPECKIT | S06 `scripts/`, `template/`, `vendor.sh` (azhq.d5) → S42 `tools/spec/` → `spec` gate area → Phase 2 P2-4 | CMD-SPEC-VENDOR, amended per F03: tree-equality against azhq.d5 that includes `template/` | IE-P1-9 CMD-GATE-SPEC (template build path, AC-AFC-CI-04); Phase 2 P2-4 |

Structural two-endpoint completeness: `design.md` §Contracts names the
producer and consumer obligations of all three contracts. One defect
breaks compatibility:

- The SPECKIT vendor step copies only `scripts/`.
- The GATE `spec` area reads `tools/spec/template/`.
- F03 corrects this.

A structural pass is not runtime proof. Runtime proof comes only from the
"Exercised at" column.

## Stubs and simulators

| Stub or simulator | Where | Replaced by / removal |
|---|---|---|
| S09T red tests (failing until S09) | S09 TDD worktree, uncommitted | S09 green; the tests are committed first under the Test Implementer identity |
| S11T red tests | S11 TDD worktree in AZHQ, uncommitted | S11 green; same commit rule |
| Temporary HOME for the pre-merge installer run (F04) | `mktemp -d` scratch HOME during S11 | Deleted after S11's run. The live install happens only at IE-P1-10. |
| Scratch worktree with a deliberate hygiene failure | IE-P1-10 CMD-HOOK-DEMO, `<workspace>/worktrees/amazon-fantasy-companion-hookdemo` | Removed right after the demo. Never pushed. |
| `spec` area template-build path (no `spec/<name>/` yet) | `tools/ci/gate.sh` | Permanent by design until Phase 2 P2-4 adds `spec/amazon-fantasy-companion/` |
| Muse or AGY without a hook surface | installer `--verify` | Typed gap (RISK-AFC-12), never a pass |

## Ordered steps

The same `order` value means the steps are independent: they land in
readiness order. "After" lists steps that must have merged first.

| Step | Order | Merges (repo) | After | Consumed as |
|---|---|---|---|---|
| IE-P1-1 | 1 | S01 (AZHQ) | planning PR merged | azhq.d4a |
| IE-P1-2 | 1 | S02 (AZHQ) | planning PR merged | azhq.d4b |
| IE-P1-3 | 1 | S03 (AZHQ) | planning PR merged | azhq.d4c |
| IE-P1-4 | 1 | S06 (AZHQ) | planning PR merged | azhq.d5 |
| IE-P1-5 | 1 | S07 (this) | planning PR merged | this.vnv |
| IE-P1-6 | 2 | S06L (this) | IE-P1-4 + sync | this.skill_links |
| IE-P1-7 | 2 | S42 (this) | IE-P1-4 | this.spec_vendor |
| IE-P1-8 | 2 | S41 (AZHQ, conditional) | IE-P1-1..3 | azhq.d4f |
| IE-P1-9 | 3 | S09T + S09 (this) | IE-P1-1, -2, -5, -7 | this.gate |
| IE-P1-10 | 4 | S11T + S11 (AZHQ), then live install | IE-P1-1..4, -6, -9, -8 or n/a | azhq.d4e |
| IE-P1-11 | 5 | S08 (this) | IE-P1-9; S11 and S41 returned (F06) | this.dx_log |
| IE-P1-12 | 6 | none (final candidate and closeout) | IE-P1-1..11 | this.p1_final, azhq.p1_final |

Dispatch timing:

- S11T dispatches as soon as IE-P1-1..3 merge.
- The S09T and S09 red phase dispatches as soon as IE-P1-1, -2 and -7
  merge.
- S09's green phase also needs IE-P1-5.

None of these is an integration step. Their merges are IE-P1-9 and
IE-P1-10.

## Cut-offs (UTC)

| Point | Target | If missed |
|---|---|---|
| Wave 1 merged (IE-P1-1..5) | 2026-10-12T18:00:00Z | Record the slip. Wave 2 dispatches per merged dependency, not per wave. |
| IE-P1-6, -7, -8 merged | 2026-10-12T23:00:00Z | Same. |
| IE-P1-9 gate on `main` | 2026-10-13T12:00:00Z | P2-4 cannot start (RISK-AFC-16). P2-2 and P2-3 continue. |
| IE-P1-10, -11 merged | 2026-10-13T18:00:00Z | Same. |
| Final candidate frozen (IE-P1-12 entry) | 2026-10-13T18:00:00Z | Closeout moves with it. |
| Phase 1 exit | 2026-10-13T23:00:00Z | The Phase 2 entry receipt states the slip, the days left to T_deadline (2026-10-23T19:00:00Z) and the remaining live NFL windows. Any scope cut is an owner decision at the Phase 2 integrated review (RISK-AFC-17). Never fall back to the project-local GridMarket kit (RISK-AFC-16). |
| S41 | Runs only if OD-AFC-01 = B | Otherwise IE-P1-8 is recorded as not applicable. |

## Owner-only dependencies

None of these is a new question. Each is an entry criterion that the
package already names.

| ID | Owner action | Blocks |
|---|---|---|
| OWN-P1-01 | Integrated approval of the Phase 1 package (OD-AFC-01, -06, -07, -08, -09, -10, -12, OA-AFC-A2) | Everything. The planning PR merge after approval is agent work. |
| OWN-P1-02 | OD-AFC-01 = A or B | IE-P1-8 and the IE-P1-10 install timing (F05) |
| OWN-P1-03 | OD-AFC-07 | S06 scope (the `use-requirements-system` description line) |
| OWN-P1-04 | OD-AFC-09 | S42 / IE-P1-7, and through it IE-P1-9 |
| OWN-P1-05 | Destructive git on the AZHQ main checkout, only if a fast-forward is blocked (AN-04) | Every sync after it |
| OWN-P1-06 | Paid Actions overage, only if gh_private_minutes runs out (RISK-AFC-08). This repository is private today. | Hosted CI runs only; the local gate continues |
| OWN-P1-07 | Credential rotation, only if a secret is exposed (RISK-AFC-11) | The affected PR |
| OWN-P1-08 | Class C stop on a third evidence-changing correction round | That slice |
| OWN-P1-09 | Phase 2 product owner actions: stick and ADB, AWS account and profile, Yahoo application, provider app sign-in | Phase 2 only. The receipt records them as met, not met, or owner action pending. |

The visibility flip is not part of Phase 1. When the owner flips it later,
the vendored D4 files (`tools/ci/`) and D5 files (`tools/spec/`) become
public. They are in the approved design, so no new decision is needed.

## Concurrency proof

**Method.** I compared the `Write set` columns of `slice-graph.md` (current
working tree) pairwise for every pair of slices that the dependency graph
leaves unordered. Paths in different repositories are disjoint by
construction. I then checked shared runtime resources, hot files and
read-before-write edges against the live host state.

**Wave 1 (S01 S02 S03 S06 S07), 10 pairs, all disjoint:**

- AZHQ pairs. Each slice owns its own skill directories:
  - S01: `skills/setup-pre-commit/**` (6 files);
  - S02: `skills/setup-a-repo/**` (5 files);
  - S03: `skills/ship-pull-request/{SKILL.md,references/GATES.md,references/EDIT-PR.md}`;
  - S06: `skills/spec-authoring/**` plus `skills/use-requirements-system/SKILL.md`.

  These are four distinct top-level skill directories. The six pairs
  S01×S02, S01×S03, S01×S06, S02×S03, S02×S06 and S03×S06 are disjoint.
- S07 (this repository, `docs/vnv/`) is in a different repository from
  S01, S02, S03 and S06: 4 more disjoint pairs.
- Hidden AZHQ shared files: none of the four writes `.bran/policy.yaml`,
  `AGENTS.md` or `.github/workflows/coe-gates.yml`.
  - `.bran/policy.yaml` `canonical_documents` is an opt-in list, so new
    skill files need no entry.
  - If a slice finds it must touch one of these files, that is a write
    outside its set. It stops and routes a single-writer delta. It does not
    edit in parallel.
- Runtime:
  - Four AZHQ worktrees share one object store. The Orchestrator creates
    them one after another before dispatch, so the `.git/worktrees` lock
    never races.
  - No fast-forward happens before the first merge.
  - Five agents is exactly impl_agent_cap. A Wave 1 repair run counts
    against the cap, so it queues if Wave 2 slices hold the other slots.

**Wave 2: unordered pairs in the current graph, all write-disjoint:**

- S06L×S42: `docs/plans/2026-10-11-amazon-fantasy-companion/evidence/skill-links.txt`
  vs `tools/spec/`, `THIRD_PARTY_NOTICES.md`. Disjoint. They do contend on
  the exclusive `alphazedehq-main-checkout` lease, although both only read
  it (F02).
- S06L × {S09T, S09, S08}: the evidence file vs `tools/ci/tests/`, vs
  `tools/ci/*`, `.githooks/*`, `.github/workflows/ci.yml`, and vs
  `docs/developer-feedback/observations.md`. All disjoint.
- S06L × {S11T, S41}, S42 × {S11T, S41}, S09T × {S11T, S41},
  S09 × {S11T, S41}, S11T × S08, S41 × S08: different repositories.
- S11T×S41 and S11×S41: `hooks/test-ci-gate-hook.sh` and
  `hooks/{ci-gate-hook.sh,install-ci-gate-hook.py,README.md}` vs
  `skills/ci-cd/SKILL.md`. Disjoint by path. They have a read dependency:
  the installer links "every shared skill the harness lacks" into Muse, so
  a `ci-cd` skill merged after the live install is missing there (F05).
- S11×S08: different repositories. However:
  - the live install edits harness configurations, which can include
    Muse's, while the Scribe runs on Muse Code;
  - S08 must also carry S11's observations (F06).
- Peak concurrent implementation agents: {S06L, S42, S11T, S41} = 4, plus
  at most one Wave 1 repair = 5. That is within the cap when the
  Orchestrator queues by slot. S08 (Scribe) is not counted.

**Hot files (single writer each; no defect):**

| File | Writer | Note |
|---|---|---|
| `THIRD_PARTY_NOTICES.md` | S42 only | Absent today; S42 creates it. S09 vendors owner code (D4), not third-party code. |
| `tools/ci/VENDORED.md` | S09 only | S09T only reads it. |
| `.gitignore` | Orchestrator only (the OD-AFC-06 negation in the planning commit) | No Phase 1 slice writes it. Any slice that needs it routes a delta to the Orchestrator. |
| AZHQ `hooks/README.md` | S11 only | `tools/coe/test-pre-commit-gates.sh` asserts two lines in it, and the AZHQ `lint` lane runs that test on a README change. This is in the IE-P1-10 entry criteria. |
| `core.hooksPath` (this repository's shared git config, seen by every worktree) | S09 (the D4-A installer) | `.githooks` resolves per worktree, so branches without `.githooks/` run no hooks. Recorded in configuration identity. Rollback unsets it. |

**Read and write dependencies checked:**

- These edges are present and correct:
  - S06→S06L, S06→S42, S42→S09T and S07→S09;
  - {S01, S02}→S09T, for the template and checker S09 vendors;
  - {S01, S02, S03}→S11T, for C13;
  - S09→S11 (the demo needs `gate.sh`), S06→S11 and S06L→S11;
  - S09→S08 (the hygiene receipt).
- The missing edges are F05 and F06.

**f885e48 findings carried forward:**

- Applied in this package: IE-F03, IE-F07, IE-F08, IE-F09, IE-F10, IE-F15,
  IE-F16 and IE-F18. They appear in `design.md` and `slice-graph.md`.
- Phase 2 input (product lanes): IE-F01, IE-F02, IE-F04, IE-F05, IE-F06,
  IE-F11, IE-F12 and IE-F14. The Phase 2 entry receipt lists them.
- Moot: IE-F13 (S41 milestone) and IE-F17 (product ignore paths).

```json integration_plan
{
  "branches": [
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/setup-pre-commit", "slices": ["S01"], "base": "AZHQ origin/main at dispatch (SHA recorded as azhq.base)", "merge": "gh pr merge --merge (never squash, never force-push)", "consumed_as": "azhq.d4a"},
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/setup-a-repo", "slices": ["S02"], "base": "AZHQ origin/main at dispatch", "merge": "gh pr merge --merge", "consumed_as": "azhq.d4b"},
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/ship-pull-request", "slices": ["S03"], "base": "AZHQ origin/main at dispatch", "merge": "gh pr merge --merge", "consumed_as": "azhq.d4c"},
    {"repo": "alphazede/Alphazedehq", "branch": "spec-authoring/d5", "slices": ["S06"], "base": "AZHQ origin/main at dispatch", "merge": "gh pr merge --merge", "consumed_as": "azhq.d5"},
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/entry-point", "slices": ["S41"], "base": "AZHQ origin/main at or after azhq.d4a, azhq.d4b, azhq.d4c", "merge": "gh pr merge --merge", "consumed_as": "azhq.d4f", "conditional": "OD-AFC-01 = B"},
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/harness-hooks", "slices": ["S11T", "S11"], "base": "AZHQ origin/main at or after azhq.d4a, azhq.d4b, azhq.d4c, azhq.d5", "merge": "gh pr merge --merge (tests commit first under the Test Implementer author identity)", "consumed_as": "azhq.d4e"},
    {"repo": "this", "branch": "afc/spec-and-docs-p1-s07", "slices": ["S07"], "base": "origin/main after the planning PR (this.plan)", "merge": "gh pr merge --merge", "consumed_as": "this.vnv"},
    {"repo": "this", "branch": "afc/spec-and-docs-p1-s06l", "slices": ["S06L"], "base": "origin/main at dispatch", "merge": "gh pr merge --merge", "consumed_as": "this.skill_links"},
    {"repo": "this", "branch": "afc/spec-and-docs-p1-s42", "slices": ["S42"], "base": "origin/main at dispatch", "merge": "gh pr merge --merge", "consumed_as": "this.spec_vendor"},
    {"repo": "this", "branch": "afc/ci-p1-s09", "slices": ["S09T", "S09"], "base": "origin/main at or after this.spec_vendor; origin/main merged in (no rebase) after this.vnv before S09 green", "merge": "gh pr merge --merge (tests commit first under the Test Implementer author identity)", "consumed_as": "this.gate"},
    {"repo": "this", "branch": "afc/scribe-p1-s08", "slices": ["S08"], "base": "origin/main at or after this.gate", "merge": "gh pr merge --merge", "consumed_as": "this.dx_log"},
    {"rule": "A repair after review commits on the same branch. A repair after merge or revert starts a new branch <branch>-r<n> from origin/main. A pushed branch is synchronized by merging origin/main, never by rebase or force-push. Never commit on local main."}
  ],
  "worktrees": [
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-setup-pre-commit", "slices": ["S01"]},
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-setup-a-repo", "slices": ["S02"]},
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-ship-pull-request", "slices": ["S03"]},
    {"path": "<workspace>/worktrees/Alphazedehq-spec-authoring", "slices": ["S06"]},
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-entry-point", "slices": ["S41"], "conditional": "OD-AFC-01 = B"},
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-harness-hooks", "slices": ["S11T", "S11"], "note": "shared TDD-pair worktree"},
    {"path": "<workspace>/worktrees/amazon-fantasy-companion-spec-and-docs-s07", "slices": ["S07"]},
    {"path": "<workspace>/worktrees/amazon-fantasy-companion-spec-and-docs-s06l", "slices": ["S06L"]},
    {"path": "<workspace>/worktrees/amazon-fantasy-companion-spec-and-docs-s42", "slices": ["S42"]},
    {"path": "<workspace>/worktrees/amazon-fantasy-companion-ci-s09", "slices": ["S09T", "S09"], "note": "shared TDD-pair worktree"},
    {"path": "<workspace>/worktrees/amazon-fantasy-companion-scribe-s08", "slices": ["S08"]},
    {"path": "<workspace>/worktrees/amazon-fantasy-companion-hookdemo", "slices": [], "note": "IE-P1-10 CMD-HOOK-DEMO scratch worktree, detached at this.gate, never pushed, removed after the demo"},
    {"rule": "The Orchestrator creates worktrees one at a time before dispatch. Never in hidden directories or /tmp. After the PR merges, remove the worktree, the local branch and the remote branch in the same session, unless the worktree holds uncommitted or unmerged work."}
  ],
  "steps": [
    {
      "id": "IE-P1-1", "phase": "Phase 1", "order": 1, "repo": "alphazede/Alphazedehq", "merges": ["S01"], "after": ["planning PR merged on this main (this.plan)"],
      "entry_criteria": ["S01 stop condition met at the PR head: CMD-D4A-TEST, CMD-SKILL-SIZE exit 0; CMD-SKILL-TRIGGER routes the matching request to setup-pre-commit and the non-matching one to its stated peer", "No [TODO] text in skills/setup-pre-commit/ (AC-AFC-D4-01); no repository-scoping names (AC-AFC-D4-06)", "One Reviewer review at this step (F01) with OCR delegate and the Reverify not-applicable line; at most one repair", "AZHQ PR checks green and mergeable; lease alphazedehq-skills/setup-pre-commit held by S01 only"],
      "post_step_vv": ["CMD-MERGE-IDENTITY (proposed): record PR number, merge commit as azhq.d4a, and git rev-parse azhq.d4a:skills/setup-pre-commit", "CMD-AZHQ-SKILL-TESTS (proposed) at azhq.d4a: CMD-D4A-TEST and CMD-SKILL-SIZE rerun locally, because AZHQ coe-gates path filters do not run this suite (F09)", "CMD-AZHQ-SYNC (proposed): fast-forward the AZHQ main checkout under the exclusive form of lease alphazedehq-main-checkout (F02); record pre and post HEAD and the running sessions"],
      "rollback": "Revert PR in Alphazedehq: branch revert/ci-cd-setup-pre-commit from origin/main, git revert -m 1 azhq.d4a, PR, gh pr merge --merge. Then CMD-AZHQ-SYNC. S09T, S09 and S11T do not dispatch, or are re-pinned, until the change relands. Never force-push.",
      "exit": "azhq.d4a and its skill tree id recorded; the skill is live on the host at the synced HEAD."
    },
    {
      "id": "IE-P1-2", "phase": "Phase 1", "order": 1, "repo": "alphazede/Alphazedehq", "merges": ["S02"], "after": ["this.plan"],
      "entry_criteria": ["S02 stop condition met: CMD-D4B-TEST, CMD-SKILL-SIZE exit 0; skills/setup-a-repo/templates/ci.yml passes check-workflows.py; CMD-SKILL-TRIGGER", "SKILL.md description no longer scopes to one named repository (SD-019, AC-AFC-D4-06)", "Reviewer review at this step (F01); at most one repair; AZHQ checks green; lease alphazedehq-skills/setup-a-repo"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> azhq.d4b (+ tree id of skills/setup-a-repo)", "CMD-AZHQ-SKILL-TESTS (proposed) at azhq.d4b (CMD-D4B-TEST)", "CMD-AZHQ-SYNC"],
      "rollback": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC. If S09 already vendored check_workflows.py from azhq.d4b, an S09 repair packet re-vendors it from the reverted state and updates tools/ci/VENDORED.md.",
      "exit": "azhq.d4b recorded."
    },
    {
      "id": "IE-P1-3", "phase": "Phase 1", "order": 1, "repo": "alphazede/Alphazedehq", "merges": ["S03"], "after": ["this.plan"],
      "entry_criteria": ["S03 stop condition met: skills/ship-pull-request/tests/edit-pr.test.sh passes (CMD-D4C-TEST); CMD-SKILL-SIZE exit 0 (SKILL.md below 60 lines and 650 words); CMD-SKILL-TRIGGER", "The vnv-review step passes --scope=commits=<base>..HEAD and records REFUSED_NO_VNV as a non-pass, non-blocking row (OD-AFC-10)", "Reviewer review at this step (F01); AZHQ checks green; lease alphazedehq-skills/ship-pull-request"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> azhq.d4c", "CMD-AZHQ-SKILL-TESTS (proposed) at azhq.d4c (CMD-D4C-TEST)", "CMD-AZHQ-SYNC, only when no session of this Lifecycle is opening or landing a PR, because this changes the PR gate procedure for every agent on the host (F02)"],
      "rollback": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC.",
      "exit": "azhq.d4c recorded. With azhq.d4a and azhq.d4b this satisfies C13, so S11T and S41 (if B) can dispatch."
    },
    {
      "id": "IE-P1-4", "phase": "Phase 1", "order": 1, "repo": "alphazede/Alphazedehq", "merges": ["S06"], "after": ["this.plan"],
      "entry_criteria": ["S06 stop condition met: CMD-SCAN PASS (uv, Graphviz, the GridMarket source at its pinned commit; RISK-AFC-13); CMD-D5-TEST, CMD-D5-AGNOSTIC, CMD-SKILL-SIZE exit 0; CMD-SKILL-TRIGGER routes the Markdown-spec request to spec-authoring and the SDoc publication request to use-requirements-system (AC-AFC-D5-03, RISK-AFC-15)", "vendor.sh copies scripts/ and template/ and records the source commit and skill tree id (F03)", "OD-AFC-07 disposition applied: the use-requirements-system description edit is present only if approved", "skills/spec-authoring/LICENSE-gridmarket present (AC-AFC-D5-01)", "Reviewer review at this step (F01); AZHQ checks green; leases alphazedehq-skills/spec-authoring and alphazedehq-skills/use-requirements-system"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> azhq.d5 (+ git rev-parse azhq.d5:skills/spec-authoring)", "CMD-AZHQ-SKILL-TESTS (proposed) at azhq.d5 (CMD-D5-TEST, CMD-D5-AGNOSTIC)", "CMD-AZHQ-SYNC; record HEAD for the S06L and S42 packets"],
      "rollback": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC. If S06L already ran, CMD-SKILL-UNLINK (proposed) removes its four links. If S42 already merged, IE-P1-7 rolls back too. P2-4 waits for the change to reland (RISK-AFC-16).",
      "exit": "azhq.d5 and its skill tree id recorded. This unblocks S06L and S42."
    },
    {
      "id": "IE-P1-5", "phase": "Phase 1", "order": 1, "repo": "this", "merges": ["S07"], "after": ["this.plan"],
      "entry_criteria": ["CMD-VNV-CHECK: docs/vnv/AGENTS.md plus ci-cd, spec and developer-feedback area files, each with Scope, Tools, Review Focus and Findings target (AC-AFC-VNV-01)", "Reviewer review at this step (F01). No gate exists yet, so CMD-PATH-SCAN-PLAN (proposed: tools-free rule-12 scan) runs on the diff.", "CMD-PR-CHECKS (proposed): the Orchestrator confirms PR-only landing, because this private repository has no ruleset (F10)"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> this.vnv", "CMD-VNV-CHECK on this.vnv"],
      "rollback": "Revert PR on this repository. After IE-P1-9, the docs area then has no Vnv area to check, and ship-pull-request records REFUSED_NO_VNV. Reland through a repair branch.",
      "exit": "this.vnv recorded. It satisfies S09's S07 dependency."
    },
    {
      "id": "IE-P1-6", "phase": "Phase 1", "order": 2, "repo": "this", "merges": ["S06L"], "after": ["IE-P1-4"],
      "entry_criteria": ["CMD-AZHQ-SYNC after IE-P1-4: main checkout HEAD at or after azhq.d5 and git rev-parse HEAD:skills/spec-authoring equals the azhq.d5 tree id", "Lease harness-configs held by S06L; shared read lease on alphazedehq-main-checkout (F02)", "CMD-SKILL-LINK: four lines, $HOME/.claude/skills, $HOME/.codex/skills, $HOME/.agents/skills and $HOME/.cursor/skills /spec-authoring resolving to <workspace>/Alphazedehq/skills/spec-authoring, written $HOME-relative; the evidence file holds no absolute home path", "Reviewer review at this step (F01); CMD-PR-CHECKS"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> this.skill_links", "CMD-SKILL-LINK re-read on the host", "CMD-SKILL-TRIGGER (spec-authoring matching request) in a fresh session, to show that the link is live"],
      "rollback": "CMD-SKILL-UNLINK (proposed): remove each path in evidence/skill-links.txt, only if it is a symlink whose target is the AZHQ main checkout skill path; revert the evidence PR.",
      "exit": "D5 skill linked in the four harness directories (AC-AFC-D5-05 part 2). harness-configs released for S11."
    },
    {
      "id": "IE-P1-7", "phase": "Phase 1", "order": 2, "repo": "this", "merges": ["S42"], "after": ["IE-P1-4"],
      "entry_criteria": ["OD-AFC-09 approved", "S42 ran skills/spec-authoring/scripts/vendor.sh from the main checkout at HEAD with skill tree equal to azhq.d5's, under the shared read lease (F02)", "CMD-SPEC-VENDOR (amended per F03): tools/spec/ equals git archive azhq.d5 skills/spec-authoring/{scripts,template} (excluding VENDORED.md); tools/spec/VENDORED.md names the source commit, the skill tree id equal to azhq.d5's, and the MIT notice; THIRD_PARTY_NOTICES.md carries the GridMarket MIT notice", "uv run --script tools/spec/spec_build.py and spec_lint.py build and lint tools/spec/template in a temporary directory with exit 0 (pre-gate interface smoke)", "Reviewer review at this step (F01); CMD-PR-CHECKS"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> this.spec_vendor", "CMD-SPEC-VENDOR on this.spec_vendor"],
      "rollback": "Revert PR on this repository. The spec area then returns GAP tools/spec missing (exit 3), a typed gap. Re-vendor from azhq.d5 in a repair packet.",
      "exit": "AC-AFC-SPEC-01 evidence. S09T can dispatch, given IE-P1-1 and IE-P1-2."
    },
    {
      "id": "IE-P1-8", "phase": "Phase 1", "order": 2, "repo": "alphazede/Alphazedehq", "merges": ["S41"], "after": ["IE-P1-1", "IE-P1-2", "IE-P1-3"],
      "entry_criteria": ["OD-AFC-01 = B; otherwise record this step as not_applicable with the decision ID", "CMD-SKILL-SIZE: router under 25 lines; CMD-SKILL-TRIGGER; no procedure of its own", "Reviewer review at this step (F01); lease alphazedehq-skills/ci-cd"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> azhq.d4f", "CMD-AZHQ-SYNC", "CMD-SKILL-TRIGGER rerun on the host"],
      "rollback": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC. Rerun CMD-HOOK-INSTALL --verify so that Muse's stale ci-cd link is reported or removed.",
      "exit": "azhq.d4f recorded, or the step is marked not_applicable."
    },
    {
      "id": "IE-P1-9", "phase": "Phase 1", "order": 3, "repo": "this", "merges": ["S09T", "S09"], "after": ["IE-P1-1", "IE-P1-2", "IE-P1-5", "IE-P1-7"],
      "entry_criteria": ["CMD-RED receipt from S09T: failing output plus sha256 of each test file in tools/ci/tests/", "S09 green: tests committed first under the Test Implementer author identity, then the product; --no-verify never used; CMD-SCAN PASS for each pinned GitHub Action (RISK-AFC-13)", "CMD-CI-VENDOR-PIN (proposed): tools/ci/VENDORED.md names azhq.d4a and azhq.d4b; tools/ci/check_workflows.py equals azhq.d4b:skills/setup-a-repo/scripts/check-workflows.py; gate.sh derives from azhq.d4a:skills/setup-pre-commit/templates/gate.sh", "CMD-WORKFLOW-CHECK exit 0; CMD-GATE-HYGIENE, CMD-GATE-DOCS, CMD-GATE-SPEC exit 0 in the worktree", "The planning package on main holds no absolute home path and no broken relative Markdown link. Checked 2026-10-11: 61 Markdown files, 0 broken links; 0 tracked files with home paths. The untracked re-p1-run.log and sm-p1-run.log contain home paths and must be scrubbed before OD-AFC-06 tracks them.", "PR shows gate / spec, gate / docs and gate / hygiene green (CMD-PR-CHECKS); Reviewer review at this step (F01)"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> this.gate", "CMD-GATE-ALL on this.gate: spec PASS (template path), docs PASS, hygiene PASS; any GAP is an anomaly (AN-05)", "CMD-HOOKSPATH (proposed): git config --get core.hooksPath equals .githooks; record it", "CMD-WORKFLOW-CHECK on main"],
      "rollback": "Revert PR on this repository, then git config --unset core.hooksPath in this repository. Branches that merged main after the step merge the revert. Reland from afc/ci-p1-s09-r1.",
      "exit": "Repository gate live on main and in PR checks (AC-AFC-CI-01..04). P2-4's S09 criterion met."
    },
    {
      "id": "IE-P1-10", "phase": "Phase 1", "order": 4, "repo": "alphazede/Alphazedehq", "merges": ["S11T", "S11"], "after": ["IE-P1-1", "IE-P1-2", "IE-P1-3", "IE-P1-4", "IE-P1-6", "IE-P1-9", "IE-P1-8 merged or not_applicable"],
      "entry_criteria": ["CMD-RED receipt from S11T, then CMD-HOOK-TEST green at the PR head", "CMD-HOOK-INSTALL-SANDBOX (proposed, F04): installer --install --verify against HOME=$(mktemp -d) reports each SD-021 harness as wired or typed gap; no live harness configuration edited before merge; hook command path is <checkout>/hooks/ci-gate-hook.sh of the checkout the installer runs from", "bash tools/coe/test-pre-commit-gates.sh passes (hooks/README.md coupling); AZHQ lint and te-hooks lanes green", "Reviewer review at this step (F01); lease harness-configs free"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> azhq.d4e", "CMD-AZHQ-SKILL-TESTS (proposed) at azhq.d4e (CMD-HOOK-TEST)", "CMD-AZHQ-SYNC", "Live install under lease harness-configs, with no implementer or Scribe session running: CMD-HOOK-INSTALL from <workspace>/Alphazedehq (the main checkout, never a linked worktree); record each edited config's sha256 before and after and its timestamped backup path, $HOME-relative", "CMD-HOOK-INSTALL --verify: one line per harness (Claude Code, Codex, Cursor, Muse, AGY), wired or typed_gap with evidence; D4 skills, D5 skill and vnv-review linked into $HOME/.config/muse/skills (and AGY's if verified) or typed gap (AC-AFC-D4-04, AC-AFC-D5-05 part 3)", "CMD-HOOK-DEMO (proposed): in the hookdemo scratch worktree, a commit with a deliberate PATH-HOME-POSIX finding is blocked under each wired harness in a fresh headless session; the worktree is removed afterwards"],
      "rollback": "CMD-HOOK-RESTORE (proposed): installer restores each harness configuration from its recorded backup and removes the skill links it created (from its receipt). Then revert PR in Alphazedehq and CMD-AZHQ-SYNC. If a harness's tool calls fail after install, restore first, then diagnose (AN-07).",
      "exit": "azhq.d4e recorded. Hooks wired or typed gaps (RISK-AFC-12). Config digests and backups recorded."
    },
    {
      "id": "IE-P1-11", "phase": "Phase 1", "order": 5, "repo": "this", "merges": ["S08"], "after": ["IE-P1-9", "S11 returned", "S41 returned or not dispatched"],
      "entry_criteria": ["docs/developer-feedback/observations.md carries DX-001..DX-007, the planning observations and the developer_feedback of every Phase 1 implementation and Reviewer return up to S11 (F06)", "CMD-GATE-HYGIENE and CMD-GATE-DOCS exit 0 on the branch (no home path, no secret, links resolve)", "The S08 commit runs under the git hooks and, if the live install has happened, under the harness hook; --no-verify never used", "Reviewer review at this step (F01); CMD-PR-CHECKS gate / docs and gate / hygiene green"],
      "post_step_vv": ["CMD-MERGE-IDENTITY -> this.dx_log", "CMD-GATE-ALL on main", "CMD-DX-PRESENCE (from f885e48 seit; TE to confirm): every row has the issue #1 Scribe contract fields"],
      "rollback": "Revert PR. The log is evidence, so a correction is a new commit, never an in-place edit after merge.",
      "exit": "AC-AFC-DX-02 evidence."
    },
    {
      "id": "IE-P1-12", "phase": "Phase 1", "order": 6, "repo": "both", "merges": [], "after": ["IE-P1-1", "IE-P1-2", "IE-P1-3", "IE-P1-4", "IE-P1-5", "IE-P1-6", "IE-P1-7", "IE-P1-8 or not_applicable", "IE-P1-9", "IE-P1-10", "IE-P1-11"],
      "entry_criteria": ["Every Phase 1 PR merged or recorded as not_applicable; no open repair; no unresolved anomaly", "Final candidate frozen: no merge to Phase 1 paths after this point except a revert", "CMD-AZHQ-SYNC: AZHQ main checkout at azhq.p1_final"],
      "post_step_vv": ["CMD-GATE-ALL on this.p1_final, with each area's line recorded", "CMD-AZHQ-SKILL-TESTS at azhq.p1_final: all D4/D5 suites", "CMD-SKILL-LINK and CMD-HOOK-INSTALL --verify readback on the host", "CMD-SKILL-SIZE and CMD-SKILL-TRIGGER for every changed SKILL.md at azhq.p1_final", "CMD-SPEC-VENDOR and CMD-CI-VENDOR-PIN on this.p1_final", "CMD-P2-ENTRY-RECEIPT (proposed): the Integration Engineer execution session assembles phase2_entry_receipt; the Assurance Test Engineer and the Integration Engineer execution session return verdicts on the candidate"],
      "rollback": "There is no merge to roll back. A failing closeout check returns to AN-01 for the owning step.",
      "exit": "Phase 1 candidate assessed. Phase 2 entry receipt recorded and landed with the DoD Manifest closeout (F08)."
    }
  ],
  "configuration_identity": {
    "this": {"plan": "merge commit of the planning PR on main", "vnv": "IE-P1-5", "skill_links": "IE-P1-6", "spec_vendor": "IE-P1-7", "gate": "IE-P1-9", "dx_log": "IE-P1-11", "p1_final": "origin/main HEAD at IE-P1-12 entry"},
    "azhq": {"base": "AZHQ origin/main at Wave 1 dispatch (observed 47c46f2e16fed060482a1bf3a0e34ddcb9bc57fc on 2026-10-11; re-record at dispatch)", "d4a": "IE-P1-1", "d4b": "IE-P1-2", "d4c": "IE-P1-3", "d5": "IE-P1-4", "d4f": "IE-P1-8 (conditional)", "d4e": "IE-P1-10", "p1_final": "AZHQ origin/main HEAD at IE-P1-12 entry"},
    "per_merge_record": ["PR number and URL", "merge method (merge)", "GitHub mergeCommit oid", "reviewed PR head SHA (an ancestor of the merge)", "git rev-parse <merge>:<owned path> tree id for each owned directory"],
    "vendored": {"tools/spec/VENDORED.md": "source repository, source commit, skills/spec-authoring tree id equal to azhq.d5's, MIT notice", "tools/ci/VENDORED.md": "source repository, azhq.d4a, azhq.d4b"},
    "alphazedehq_main_checkout": "HEAD before and after each CMD-AZHQ-SYNC, with the sessions running at that moment",
    "harness_skill_links": ["$HOME/.claude/skills/spec-authoring", "$HOME/.codex/skills/spec-authoring", "$HOME/.agents/skills/spec-authoring", "$HOME/.cursor/skills/spec-authoring", "each -> <workspace>/Alphazedehq/skills/spec-authoring"],
    "harness_hook_configs": "per installer --verify line: config file ($HOME-relative), sha256 before and after, timestamped backup path; Muse skill directory $HOME/.config/muse/skills (exists; today holds only Bearing Lite links); AGY surface or typed gap",
    "git_config": "this repository core.hooksPath = .githooks (shared across all worktrees of the repository)",
    "tools": "uv, Graphviz dot and python3 versions used by the gate and D5 tests; scan-software-supply-chain receipt per acquisition; pinned SHA of every action in .github/workflows/ci.yml; pinned GridMarket source commit"
  },
  "authorized_glue": [],
  "authorized_glue_note": "None. Renaming check-workflows.py to tools/ci/check_workflows.py and deriving gate.sh from the D4-A template are part of S09's product write set, not glue. A needed contract change is CONTRACT_STOP to the Orchestrator.",
  "stubs": [
    {"id": "STUB-P1-1", "what": "S09T red tests", "removed_by": "S09 green (IE-P1-9)"},
    {"id": "STUB-P1-2", "what": "S11T red tests", "removed_by": "S11 green (IE-P1-10)"},
    {"id": "SIM-P1-1", "what": "temporary HOME for the pre-merge installer run (F04)", "removed_by": "deleted after S11's run; live install at IE-P1-10"},
    {"id": "SIM-P1-2", "what": "hookdemo scratch worktree with a deliberate hygiene failure", "removed_by": "removed right after CMD-HOOK-DEMO; never pushed"},
    {"id": "PERM-P1-1", "what": "spec area template-build path while no spec/<name>/ exists", "removed_by": "permanent by design; Phase 2 P2-4 adds spec/amazon-fantasy-companion/"}
  ],
  "anomaly_rollback_recovery": {
    "anomalies": [
      {"id": "AN-01", "class": "post-merge check failure on main (either repository)", "action": "Stop dependent dispatches and merges. Revert PR (git revert -m 1 <merge>, PR, merge commit). Repair on <branch>-r1 from origin/main. Reland through the same step id with suffix -r1."},
      {"id": "AN-02", "class": "interface mismatch on GATE, HOOK or SPECKIT", "action": "Return the work to the producer slice if it violates the contract, else to the consumer. A needed contract change is CONTRACT_STOP to the Orchestrator (Planning and Design), never glue."},
      {"id": "AN-03", "class": "AZHQ skill regression after a sync", "action": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC; re-issue packets dispatched after the bad sync with the new HEAD."},
      {"id": "AN-04", "class": "AZHQ main checkout cannot fast-forward (owner local work or an untracked path conflicts, for example `evals /`)", "action": "Do not stash, reset, clean or switch. Report the conflicting path to the owner (OWN-P1-05). Consumers wait."},
      {"id": "AN-05", "class": "gate GAP (exit 3) at a post-step", "action": "Typed gap, never a pass. Provision the tool after scan-software-supply-chain and rerun."},
      {"id": "AN-06", "class": "route exhausted mid-step (RISK-AFC-07)", "action": "Next ordered fallback of the frozen profile, with a class B receipt that preserves the coverage-assist and Reverify settings. Queue the slice if all fallbacks are exhausted."},
      {"id": "AN-07", "class": "live hook install breaks a harness (tool calls error or every commit is blocked)", "action": "CMD-HOOK-RESTORE at once, then record a typed gap. S11 repair round. Re-install only after IE-P1-10 entry criteria hold again."},
      {"id": "AN-08", "class": "trigger collision D5 vs use-requirements-system (RISK-AFC-15)", "action": "D5 repair round narrows the descriptions per the OD-AFC-07 disposition. Never merge the two skills."},
      {"id": "AN-09", "class": "gh_private_minutes exhausted (RISK-AFC-08); both repositories are private", "action": "Stop hosted runs. Local gate receipts (CMD-GATE-ALL) stand as deterministic evidence. No paid overage without the owner (OWN-P1-06)."},
      {"id": "AN-10", "class": "scan BLOCK or INDETERMINATE (RISK-AFC-13)", "action": "Fail closed. The slice stops. No substitute tool without a passing scan."},
      {"id": "AN-11", "class": "secret or absolute home path detected (RISK-AFC-11)", "action": "Block the merge until sanitized. If already exposed, record the artifact without the value and notify the owner (OWN-P1-07)."},
      {"id": "AN-12", "class": "cut-off missed", "action": "Record the slip in the Phase 2 entry receipt. P2-2 and P2-3 continue. Any scope cut is an owner decision (RISK-AFC-16, RISK-AFC-17)."}
    ],
    "rollback_rules": ["Revert PRs only. Never force-push, reset or delete a branch that holds unmerged work.", "Harness configurations are restored from the timestamped backups the installer records (CMD-HOOK-RESTORE).", "Skill links are removed only from the paths recorded in evidence/skill-links.txt and in the installer receipt, and only when they are symlinks into the AZHQ main checkout (CMD-SKILL-UNLINK).", "this repository: git config --unset core.hooksPath when IE-P1-9 is reverted."],
    "recovery": "After a revert, the consuming steps re-pin to the relanded merge commit. Their post-step V&V reruns on the new identity. A third evidence-changing correction round is a class C owner stop (OWN-P1-08)."
  },
  "cutoffs": [
    {"point": "Wave 1 merged (IE-P1-1..5)", "target": "2026-10-12T18:00:00Z"},
    {"point": "IE-P1-6, IE-P1-7, IE-P1-8 merged", "target": "2026-10-12T23:00:00Z"},
    {"point": "IE-P1-9 gate on main (P2-4 precondition)", "target": "2026-10-13T12:00:00Z"},
    {"point": "IE-P1-10, IE-P1-11 merged", "target": "2026-10-13T18:00:00Z"},
    {"point": "final candidate frozen (IE-P1-12 entry)", "target": "2026-10-13T18:00:00Z"},
    {"point": "Phase 1 exit", "target": "2026-10-13T23:00:00Z", "on_miss": "AN-12"},
    {"point": "S41", "target": "only if OD-AFC-01 = B"}
  ],
  "final_candidate": {
    "definition": "Composite candidate: this.p1_final (this repository main) plus azhq.p1_final (Alphazedehq main) plus the recorded host configuration (harness skill links, harness hook configs with digests, core.hooksPath)",
    "contents": ["azhq.d4a, azhq.d4b, azhq.d4c, azhq.d5, azhq.d4e, azhq.d4f (if B) as ancestors of azhq.p1_final", "this.vnv, this.skill_links, this.spec_vendor, this.gate, this.dx_log as ancestors of this.p1_final", "AZHQ main checkout HEAD = azhq.p1_final at assessment"],
    "assessed_by": "Integration Engineer execution session (fresh, no author ancestry; route per journey.json integration_engineer.execution, cadence lifecycle) and the Assurance Test Engineer"
  },
  "phase2_entry_receipt": {
    "requirement": "AC-AFC-PLAN-03",
    "author": "Integration Engineer execution session at IE-P1-12",
    "location": "docs/plans/2026-10-11-amazon-fantasy-companion/evidence/phase2-entry-receipt.json, landed in the Phase 1 closeout PR with the DoD Manifest closeout (F08)",
    "contents": ["D5 merge commit azhq.d5: PR, merge method, skill tree id", "D4 merge commits azhq.d4a, azhq.d4b, azhq.d4c, azhq.d4e, and azhq.d4f or not_applicable", "Vendored tools/spec/ commit on main (this.spec_vendor), with the CMD-SPEC-VENDOR result and the tools/spec/VENDORED.md source commit", "The gate run on main: CMD-GATE-ALL at this.p1_final with each area's PASS, FAIL or GAP line", "Status of each Phase 2 entry criterion as met, not met or owner action pending: P2-1 (Phase 1 approval); P2-4 (S06 merged, S42 on main, S09 gate on main, P2-2 PASS, P2-3(c) done); OD-AFC-12; owner actions for stick and ADB, AWS account and profile, Yahoo application (T_yahoo 2026-10-16T19:00:00Z), provider app sign-in", "Slips against the cut-offs; days left to T_deadline; remaining live NFL windows (RISK-AFC-16, RISK-AFC-17)", "Typed gaps: Muse and AGY hook surfaces, any GAP exits", "Open anomalies and their resolutions", "f885e48 product-lane findings forwarded as Phase 2 input: IE-F01, IE-F02, IE-F04, IE-F05, IE-F06, IE-F11, IE-F12, IE-F14", "Harness link and hook readback (CMD-SKILL-LINK, CMD-HOOK-INSTALL --verify) at azhq.p1_final"]
  },
  "lifecycle_assessment_inputs": ["final_candidate and every configuration_identity value", "Step receipts in journey.json execution_receipts (merge SHAs, command outputs, digests, sync records)", "Reviewer record per PR, with the OCR delegate section and the Reverify not-applicable line (AC-AFC-REV-01)", "seit.json V&V results per Phase 1 AC-AFC and RISK-AFC row", "CMD-AZHQ-SKILL-TESTS, CMD-SKILL-SIZE and CMD-SKILL-TRIGGER evidence at azhq.p1_final", "CMD-GATE-ALL at this.p1_final", "CMD-HOOK-INSTALL --verify, CMD-HOOK-DEMO, CMD-SKILL-LINK readbacks", "CMD-RED receipts for S09T and S11T, and the author-identity commit order", "scan-software-supply-chain receipts (RISK-AFC-13) and route receipts (RISK-AFC-07)", "Anomaly log AN-* with resolutions; typed gaps", "Scribe log at this.dx_log", "Phase 2 entry receipt"],
  "owner_dependencies": [
    {"id": "OWN-P1-01", "action": "Integrated approval of the Phase 1 package (OD-AFC-01, -06, -07, -08, -09, -10, -12, OA-AFC-A2)", "blocks": "all steps"},
    {"id": "OWN-P1-02", "action": "OD-AFC-01 A or B", "blocks": "IE-P1-8; IE-P1-10 install timing (F05)"},
    {"id": "OWN-P1-03", "action": "OD-AFC-07", "blocks": "S06 scope (IE-P1-4)"},
    {"id": "OWN-P1-04", "action": "OD-AFC-09", "blocks": "IE-P1-7, then IE-P1-9"},
    {"id": "OWN-P1-05", "action": "Destructive git on the AZHQ main checkout, only if a fast-forward is blocked (AN-04)", "blocks": "every sync after it"},
    {"id": "OWN-P1-06", "action": "Paid Actions overage (RISK-AFC-08)", "blocks": "hosted CI only"},
    {"id": "OWN-P1-07", "action": "Credential rotation after exposure (RISK-AFC-11)", "blocks": "affected PR"},
    {"id": "OWN-P1-08", "action": "Class C stop on a third correction round", "blocks": "that slice"},
    {"id": "OWN-P1-09", "action": "Phase 2 product owner actions (stick and ADB, AWS, Yahoo, provider app)", "blocks": "Phase 2 only; recorded in the receipt"}
  ],
  "concurrency_findings": [
    {"id": "IE-P1-F01", "class": "dependency", "slices": ["S01", "S02", "S03", "S06", "S07", "S06L", "S42", "S09T", "S09", "S11T", "S11", "S41", "S08"], "compared": "The technical plan §Program plan ('one review per Phase 1 pull request at the phase boundary') and DES-AFC-LANES Landing ('reviewed once at the Phase 1 boundary') put every review at the single Phase 1 boundary. Merge needs that review (AC-AFC-LAND-01). But the Wave 2 edges need merges inside Phase 1: S06->S42 ('S06 merged'), S42->S09T, S09->S11, S09->S08, and C13 for S11T. Read literally, no Wave 2 slice can start until Phase 1 ends, and Phase 1 cannot end without them.", "target": "technical plan §Program plan — Phase 1 waves, second sentence; design.md DES-AFC-LANES Landing, last bullet", "corrected_text": "Technical plan: 'The Reviewer cadence is `phase`. Phase 1's review boundaries are its integration steps IE-P1-1..IE-P1-11 (specialists/integration-plan.md): each Phase 1 pull request is reviewed once at its own integration step, after its slice reaches its stop condition, then gets at most one repair and the deterministic gate before it merges. The Reviewer packet declares that step as the cadence boundary.' DES-AFC-LANES: '- Every pull request is reviewed once at its integration step (the Phase 1 review boundary unit), on the lane profile's reviewer route, with OCR delegate mode and `Reverify: not applicable` (AC-AFC-REV-01). It gets at most one repair and a green gate, then merges by merge commit.'"},
    {"id": "IE-P1-F02", "class": "shared resource", "slices": ["S06L", "S42", "S11"], "compared": "S06L lease 'harness-configs, alphazedehq-main-checkout' and S42 lease 'alphazedehq-main-checkout'. Both only read the checkout, and both dispatch on the S06 merge. Because DES-AFC-LANES grants each lease 'to one slice at a time', they serialize for no reason. Separately, 'fast-forward only, between dispatches' does not stop a fast-forward while Wave 1 or Wave 2 sessions run: under continuous dispatch, merges always land while other sessions are running. The S03 fast-forward changes ship-pull-request for every PR-opening session on the host.", "target": "design.md DES-AFC-LANES Leases, alphazedehq-main-checkout bullet", "corrected_text": "- `alphazedehq-main-checkout`: a reader-writer lease. Slices that read skills from the checkout (S06L, S42) and the IE-P1-10 live install hold a shared read lease. The Orchestrator's fast-forward (CMD-AZHQ-SYNC) takes it exclusively. It runs only when no read lease is held and no session of this Lifecycle is opening or landing a pull request. Each sync records the HEAD before and after it and the sessions running at that moment. The HEAD is recorded in each later packet."},
    {"id": "IE-P1-F03", "class": "dependency (interface mismatch)", "slices": ["S06", "S42", "S09"], "compared": "CONTRACT-AFC-SPECKIT vendor step ('copies the scripts to <repo root>/tools/spec/') and DES-AFC-D5 references/vendoring.md ('copy scripts/') vs DES-AFC-GATE spec area ('copies tools/spec/template/ into a temporary directory', AC-AFC-CI-04). The template is never vendored. S42 stop condition 'VENDORED.md names the merged D5 commit': vendor.sh runs from the live main checkout, which may already be past the D5 merge, so the commit it records is undefined.", "target": "design.md §Contracts CONTRACT-AFC-SPECKIT, vendor bullet; design.md DES-AFC-D5 files table, references/vendoring.md row; slice-graph.md S42 Stop condition", "corrected_text": "CONTRACT-AFC-SPECKIT: '- `<skill>/scripts/vendor.sh <repo root>` — copies the contents of `scripts/` and the `template/` directory to `<repo root>/tools/spec/` (template at `tools/spec/template/`) and writes `VENDORED.md` (source repository; source commit = `git log -1 --format=%H -- <skill dir>` in the source checkout; the tree id of the skill directory at that commit; MIT notice); refuses to run when the skill directory has uncommitted changes, and refuses to overwrite a vendored copy whose files differ from its recorded commit.' vendoring.md row: 'When a repository's CI cannot reach the shared skill (private skill, public repository): copy `scripts/` and `template/` to `<repo>/tools/spec/` with `scripts/vendor.sh`, which writes `VENDORED.md` (source commit, skill tree id, MIT notice).' S42 Stop condition: '`tools/spec/VENDORED.md` names a source commit whose `skills/spec-authoring/` tree id equals that of the merged D5 commit; vendored files (scripts and template) equal that tree; MIT notice present in both files.'"},
    {"id": "IE-P1-F04", "class": "shared resource", "slices": ["S11"], "compared": "S11 stop condition: 'installer --verify reports each SD-021 harness as wired or a typed gap; Muse skill directory exposes D4 and D5 skills'. To meet it before merge, S11 must run the installer against the live harness configurations. That writes, into every harness on the host, a hook path inside the linked worktree worktrees/Alphazedehq-ci-cd-harness-hooks. The worktree is deleted after merge, which leaves every harness pointing at a missing hook. The installer also runs unreviewed code against shared harness configs while other sessions are running.", "target": "slice-graph.md S11 Commands and Stop condition", "corrected_text": "Commands: `CMD-HOOK-TEST, CMD-HOOK-INSTALL-SANDBOX`. Stop condition: `Hook tests green; installer --install --verify run with HOME set to a temporary directory reports each SD-021 harness as wired or a typed gap and links the D4 and D5 skills into the sandbox Muse skill directory or records a typed gap; the installer writes the hook path of the checkout it runs from; no live harness configuration is edited before merge. The live install (CMD-HOOK-INSTALL) runs at integration step IE-P1-10 from the Alphazedehq main checkout after merge and fast-forward.`"},
    {"id": "IE-P1-F05", "class": "dependency", "slices": ["S41", "S11"], "compared": "S41 writes skills/ci-cd/SKILL.md. S11's installer links 'every shared skill the harness lacks' into Muse and AGY, and AC-AFC-D4-04 requires the D4 skills in Muse's directory. S41 and S11 have no edge, so a ci-cd skill that merges after the live install is never linked into Muse.", "target": "slice-graph.md S11 Depends on; Dependencies list", "corrected_text": "S11 Depends on: `S11T, S09 merged, S06 merged, S06L, S41 merged when OD-AFC-01 = B`. Dependencies list add: `S41 --> S11 (only when OD-AFC-01 = B)`."},
    {"id": "IE-P1-F06", "class": "dependency", "slices": ["S08", "S11", "S41"], "compared": "S08 stop condition 'Log carries DX-001..DX-007, planning and Phase 1 observations' and AC-AFC-DX-02 'every Phase 1 observation'. S08 depends only on S09 merged, so it can land before S11 (and S41) return their developer_feedback sections.", "target": "slice-graph.md S08 Depends on; Dependencies list", "corrected_text": "S08 Depends on: `S09 merged (hygiene area exists); S11 returned; S41 returned or not dispatched; observations accumulate from Wave 1 dispatch`. Dependencies list add: `S11 --> S08; S41 --> S08`."},
    {"id": "IE-P1-F07", "class": "missing evidence", "slices": ["S06L"], "compared": "S06L writes docs/plans/2026-10-11-amazon-fantasy-companion/evidence/skill-links.txt in this repository. DES-AFC-LANES Landing lists PRs only for S07, S42, S09 and S08, so S06L's evidence has no landing path.", "target": "design.md DES-AFC-LANES Landing, 'This repository' bullet", "corrected_text": "- This repository: one pull request each for S07, S06L (link readback evidence), S42, S09 (tests and gate) and S08."},
    {"id": "IE-P1-F08", "class": "missing evidence", "slices": [], "compared": "AC-AFC-PLAN-03 requires a recorded Phase 2 entry receipt. The slice-graph Lifecycle-level rows allocate it to 'the Integration Engineer at Phase 1 closeout', but no artifact path or landing exists, so the closeout PR would not carry it.", "target": "slice-graph.md §Lifecycle-level rows, AC-AFC-PLAN-03 bullet", "corrected_text": "- AC-AFC-PLAN-03: the Integration Engineer execution session at Phase 1 closeout, recorded at `docs/plans/2026-10-11-amazon-fantasy-companion/evidence/phase2-entry-receipt.json` (contents per integration-plan.md `phase2_entry_receipt`) and landed in the Phase 1 closeout pull request with the DoD Manifest closeout."},
    {"id": "IE-P1-F09", "class": "missing evidence", "slices": ["S01", "S02", "S03", "S06", "S11"], "compared": "The Alphazedehq .github/workflows/coe-gates.yml path filters (lint: docs/**, tools/coe/**, hooks/README.md; yaml: skills/*/agents/*.yaml; hooks: hooks/**; skills: skills/visual-review/** only) and the te-hooks lane's explicit test list (test-issue-labels.py, test-bug-report-routing.sh, edit-pr.test.sh) run none of the D4-A, D4-B or D5 suites or the new hooks/test-ci-gate-hook.sh. edit-pr.test.sh runs only when hooks/** or test-engineering paths change, not on an S03-only PR. So 'AZHQ checks green' is not evidence for these slices. Adding lanes would make coe-gates.yml a hot file for four concurrent Wave 1 slices, which is out of Phase 1 scope.", "target": "technical plan §Exit criteria, item 2", "corrected_text": "2. Every D4 and D5 pull request is merged in Alphazedehq by rebase or merge commit. Alphazedehq CI path filters do not run the D4/D5 suites, so each D4/D5 merge commit also carries a local rerun receipt of its suite (CMD-AZHQ-SKILL-TESTS), and the Phase 1 closeout reruns every suite at the final Alphazedehq commit. This repository's gate pull request is merged with the `gate / spec`, `gate / docs` and `gate / hygiene` checks green."},
    {"id": "IE-P1-F10", "class": "shared resource", "slices": ["S07", "S06L", "S42", "S09", "S08"], "compared": "On 2026-10-11, `gh repo view` reports 1wgrumph/amazon-fantasy-companion as PRIVATE, and the rulesets API returns 403 ('Upgrade to GitHub Pro or make this repository public'). DES-AFC-LANES and AC-AFC-LAND-01 assume enforced PR-only main and green required checks. Here neither is enforced, and the five PRs' Actions runs consume gh_private_minutes (RISK-AFC-08, C11).", "target": "design.md DES-AFC-LANES Landing, add a bullet after 'This repository: …'", "corrected_text": "- This repository is private until the owner flips visibility, and a private GitHub Free repository has no rulesets or branch protection. So PR-only `main` and green `gate / <area>` checks are enforced by the Orchestrator: CMD-PR-CHECKS before every merge, and no direct push to `main`. Its Actions runs count against gh_private_minutes (RISK-AFC-08)."}
  ]
}
```

## Proposed command IDs (for the Planning Test Engineer)

| ID | Purpose |
|---|---|
| CMD-MERGE-IDENTITY | Record PR number, merge method, mergeCommit oid, reviewed head SHA and owned-path tree ids (`gh pr view --json mergeCommit,headRefOid,number`; `git rev-parse <sha>:<path>`) |
| CMD-AZHQ-SYNC | `git -C <workspace>/Alphazedehq merge --ff-only origin/main` under the exclusive form of the main-checkout lease; record HEAD before and after and the running sessions |
| CMD-AZHQ-SKILL-TESTS | Rerun the D4/D5 suites (CMD-D4A/D4B/D4C/D5-TEST, CMD-D5-AGNOSTIC, CMD-HOOK-TEST) on a given AZHQ commit, in a detached scratch worktree under `worktrees/` |
| CMD-CI-VENDOR-PIN | `tools/ci/VENDORED.md` names azhq.d4a and azhq.d4b; the vendored checker equals `git show azhq.d4b:skills/setup-a-repo/scripts/check-workflows.py` |
| CMD-SPEC-VENDOR (amend) | Compare against `git archive azhq.d5 skills/spec-authoring/scripts skills/spec-authoring/template`, and accept a VENDORED.md commit whose skill tree id equals azhq.d5's (F03) |
| CMD-SKILL-UNLINK | Remove the recorded skill links only if each is a symlink into the AZHQ main checkout |
| CMD-HOOK-INSTALL-SANDBOX | `HOME=$(mktemp -d) python3 hooks/install-ci-gate-hook.py --install --verify` |
| CMD-HOOK-DEMO / CMD-HOOK-RESTORE | As in f885e48 `seit.json`, retargeted to IE-P1-10 |
| CMD-HOOKSPATH | `git config --get core.hooksPath` equals `.githooks` |
| CMD-PR-CHECKS | `gh pr checks <n>`: every `gate / <area>` check is pass, and the PR targets `main` |
| CMD-PATH-SCAN-PLAN | Scan the diff for rule-12 home-path shapes before the gate exists (IE-P1-5) |
| CMD-P2-ENTRY-RECEIPT | Assemble and validate the receipt keys in `phase2_entry_receipt` |

## Typed outcome

- **Outcome:** GAPS.
- **Verdict:** The Phase 1 assembly strategy is complete: 12 steps, all three
  contracts checked, cut-offs, rollback and the Phase 2 entry receipt
  defined. Before the affected slices dispatch, the Plan Integrator must
  apply IE-P1-F01..F10:
  - F01 affects every merge;
  - F03 affects S06 and S42;
  - F04 and F05 affect S11;
  - F06 affects S08;
  - F02, F07, F08, F09 and F10 are design and plan text.

  No owner decision is required.
- **candidate_ref:** none; this is a planning session. The planning base is
  `f885e48` plus working-tree changes on
  `plan/2026-10-11-amazon-fantasy-companion`.
- **changed_paths:** `docs/plans/2026-10-11-amazon-fantasy-companion/specialists/integration-plan.md`.
- **Remaining risks:**
  - F01 redefines the Phase 1 review boundary unit without changing the
    frozen `cadence: phase` value. If the Orchestrator judges that this
    changes the frozen profile, it becomes an owner amendment at the
    integrated review.
  - A live hook install edits configurations shared by every session on
    the host (AN-07).
  - Both repositories are private, so CI minutes are metered.
- **Blocker:** none for the planning output. Dispatch blockers are
  F01, F03, F04, F05 and F06.

## developer_feedback

- **DX-IE-P1-01** (Alphazedehq CI coverage):
  - Observation: `coe-gates.yml` path filters run no suite for changed
    skills other than `visual-review`, and `edit-pr.test.sh` is not
    triggered by `skills/ship-pull-request/**`.
  - Evidence: `.github/workflows/coe-gates.yml` filters block and te-hooks
    lane, read on 2026-10-11.
  - Cost: every D4/D5 merge needs a manual local rerun (F09).
  - Candidate enhancement for `alphazede/Alphazedehq` (rule 18). Filing is
    the Orchestrator's call.
- **DX-IE-P1-02** (GitHub plan limits):
  - Observation: a private repository on GitHub Free returns 403 for
    rulesets, so "PR-only main by ruleset" cannot hold for this
    repository until it is public.
  - Evidence: `gh api repos/1wgrumph/amazon-fantasy-companion/rulesets`
    returned HTTP 403 on 2026-10-11.
- **DX-IE-P1-03** (BRAN):
  - Observation: the BRAN hook reported `bran_status: unavailable` for
    this repository (no `.bran/policy.yaml`), so ordinary discovery was
    used.
- **Tools exercised:** git, gh (repo view, rulesets, branch protection),
  readlink, grep/sed/awk, python3 (Markdown link scan), the Bearing Lite
  integration-engineer skill (1.1.6) and the integration-engineering method
  skill.
