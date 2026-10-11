---
type: integration-plan
status: gaps
lifecycle: AFC-2026-10-11
role: integration_engineer (planning session)
inputs: amazon-fantasy-companion-technical-plan.md, design.md, specialists/slice-graph.md, views/views.json, specialists/systems-modeler-receipt.md, journey.json
---

# Integration plan — AFC-2026-10-11 (planning session)

This plan defines how the 41 slices are assembled into one integrated candidate. It covers items and versions, interface checks, order, entry criteria, stubs, configuration identity, post-step V&V handoff, anomaly handling, rollback, cut-offs and owner-only dependencies. It does not implement, change requirements or design, author tests or review.
Post-step command IDs come from `slice-graph.md`. IDs marked *proposed* are new, and the Planning Test Engineer finalizes them in `seit.json`.
The Plan Integrator copies the `integration_plan` JSON block into `implementation.json` mechanically.

Outcome: **GAPS**. The assembly strategy is complete. However, 18 slice-graph or design defects must be corrected before the affected slices dispatch (section "Concurrency proof and findings").
None of them needs an owner decision. Each one has exact corrected text in `concurrency_findings`.

## Assembly model

- **Items.** There are two repositories:
  - `1wgrumph/amazon-fantasy-companion`, here called *this*;
  - `alphazede/Alphazedehq`, here called *AZHQ*: D4-A/B/C/E/F and D5, each landing through its own PR.
- **This repository's integration levels:**
  - *Slice branch.* One per running slice or TDD pair (finding IE-F07).
  - *Lane branch.* `afc/<lane>-m<n>`, one PR per lane per milestone (DES-AFC-LANES).
  - *`main`.* Lane PRs merge with `gh pr merge --merge`, because lane branches contain merge commits. Never squash, never force-push.
  - A pushed lane branch is synchronized by merging `origin/main` into it. It is never rebased.
- **Readiness.** A lane PR merges only after all of these hold:
  - every slice in it reached its stop condition;
  - the lane PR passed one Reviewer review, with OCR delegate mode and Reverify or `not applicable` (AC-AFC-REV-01), plus an on-device visual review for UI (AC-AFC-VIS-01);
  - at most one repair round followed;
  - its `gate / <area>` checks are green.
- **Contract-first freeze.**
  - S04 and S05 freeze the device and API surface. S06 freezes SPECKIT. S01 freezes GATE. S11 freezes HOOK.
  - After each freeze, the step's CMD-CONTRACT-FROZEN (proposed) check fails on any change to a frozen file that did not arrive through a routed hot-file delta.
- **Hot files** have one owner each. Any later change is a *hot-file delta*:
  - a separate one-file packet on the owner lane;
  - holds lease `hot-file/<path>`;
  - merged into the owner lane branch, then merged into the consuming lane branch before the consumer's slice continues.
  - Hot-file deltas are routed product changes, never integration glue.
- **Live skills.** AZHQ skills go live on this host only when the AZHQ main checkout fast-forwards. Harness links resolve to `<workspace>/Alphazedehq/skills/<skill>`, verified by `readlink` for `setup-pre-commit`. That checkout is therefore a leased resource, `alphazedehq-main-checkout` (IE-F16).
- **Integration receipts.** Merge SHA, command outputs and digests for each step are recorded in `journey.json` `execution_receipts` by the Orchestrator. No new tracked write set is created for them.

## Interface and compatibility checks

| Contract | Producer → consumer | Freeze point | Static check | Exercised at |
|---|---|---|---|---|
| CONTRACT-AFC-GATE | S01 template → S09 `gate.sh` → S11 hook, Actions | IE-M1-1 / IE-M1-6 | CMD-CI-VENDOR-PIN (proposed): `tools/ci/VENDORED.md` names `azhq.d4a`, `azhq.d4b`; CMD-WORKFLOW-CHECK | IE-M1-6 PR checks; IE-M2-1 CMD-HOOK-DEMO (proposed) |
| CONTRACT-AFC-HOOK | S11 → harness configs | IE-M2-1 | CMD-HOOK-TEST | CMD-HOOK-INSTALL `--verify`, CMD-HOOK-DEMO |
| CONTRACT-AFC-SPECKIT | S06 → S19 `tools/spec/` → `spec` gate area | IE-M1-3 | CMD-SPEC-VENDOR (VENDORED.md commit = `azhq.d5`, files identical) | IE-M2-4 CMD-GATE-SPEC; IE-M4-5 |
| CONTRACT-AFC-API | S05 `backend/api/openapi.yaml` ↔ TV `net/` (S04 interface, S25 impl) | IE-M1-6 | CMD-CONTRACT-FROZEN on `openapi.yaml` and `net/ApiClient.kt` | IE-M3-2 CMD-SMOKE; IE-M3-4 CMD-E2E-REPLAY (proposed) |
| CONTRACT-AFC-EVENT | S20 feed → S22 match/policy, S24 panel, S30 | IE-M1-6 | S05 contract tests in `gate / backend` | IE-M3-1 lane merge order S20→S22→S24, each followed by CMD-GATE-BACKEND |
| CONTRACT-AFC-ALERT | S22 → `/v1/alerts` → S25 alerts | IE-M1-6 | S05 contract tests; S25T parsing tests | IE-M3-4 CMD-E2E-REPLAY (heads-up over playback) |
| CONTRACT-AFC-LAUNCH | S23 target → S25 watch; S25 outcome → `/v1/alerts/{id}/outcome` | IE-M1-6 | S23T/S25T tests | IE-M3-4, IE-M3-5 (S28 GAME_OPENED) |
| CONTRACT-AFC-PROVIDERS | S14 `docs/spikes/SP-3-provider-registry.json` → S23 `backend/providers/registry.json` | IE-M2-3 | CMD-REGISTRY-CHECK (proposed): every registry entry's `verified.form` appears verified in the SP-3 draft | IE-M3-1 |
| CONTRACT-AFC-PANEL | S24 → `/v1/panel` → S27 panel, S32 labels | IE-M1-6 | S05 contract tests; S27T tests | IE-M3-4; IE-M4-6 |
| CONTRACT-AFC-LINEUPSOURCE | S21 Yahoo/Manual → S22, S24 | IE-M1-6 | S21T tests | IE-M3-1 merge S21 before S22 |
| CONTRACT-AFC-TABLES | S05 `store/` → S20..S24, S30 | IE-M1-6 | CMD-CONTRACT-FROZEN on `backend/src/afc_backend/store/` (IE-F05) | IE-M3-2 deployed stack smoke |

Two-endpoint completeness, checked against the interface-completeness profile: each contract above names its producer and consumer obligations in `design.md` §Contracts.
Passing this structural check is not runtime proof. Runtime proof comes only from the "Exercised at" column.

## Stubs and simulators

| Stub | Introduced | Replaced by | Removal check |
|---|---|---|---|
| TV component stubs (`afc.companion.*`) | S04 | S25, S26, S27, S31, S32 | CMD-STUB-SCAN (proposed): no `AFC-STUB` marker under `tv-app/app/src/main/` at IE-M4-6 |
| Backend route stubs | S05 | S20..S24, S30 | CMD-STUB-SCAN under `backend/src/` at IE-M4-6 |
| Empty provider registry | S05 | S23 (SP-3-verified entries only) | CMD-REGISTRY-CHECK |
| `ReplaySource` + `backend/fixtures/espn/` | S16, S20 | Live ESPN (ReplayMode off) for S28 | Replay label present whenever ReplayMode on (CMD-E2E-REPLAY) |
| `ManualSource` | S21 | YahooSource if S17 verdict = Yahoo | S17 verdict recorded |
| Mode A `CompanionPlayer` | S27 | Mode B only if S15 verdict = Mode B | S15 verdict; label check in CMD-E2E-REPLAY |
| `spec` area `GAP tools/spec missing` / `PASS nothing to check` | S09 | S19 vendored kit | CMD-GATE-SPEC PASS at IE-M2-4 |
| Gate `GAP` exit 3 (tool missing) | S09 | — (typed gap, never a pass) | Any GAP at a post-step is an anomaly, not a pass |

Stubs that are permanent by design are not removed: ReplaySource, ManualSource and Mode A. Every other stub is gone at the final candidate.

## Ordered steps (summary)

Steps with the same `order` inside a milestone are independent and land in readiness order.

| Step | Order | Merges | Gate to enter (short) |
|---|---|---|---|
| IE-M1-1 | 1 | S01 (AZHQ) | S01 receipts, review, AZHQ checks |
| IE-M1-2 | 1 | S02 (AZHQ) | same |
| IE-M1-3 | 1 | S06 (AZHQ) | same + trigger test both directions |
| IE-M1-4 | 1 | S03 (AZHQ) | same |
| IE-M1-5 | 2 | S04 | CMD-ANDROID-BUILD, scan PASS |
| IE-M1-6 | 3 | S05, S09T, S09 | IE-M1-1..3 merged; IE-M1-5 merged |
| IE-M1-7 | 4 | S07, S10, S06L, S08 | IE-M1-6 merged; IE-M1-3 merged and AZHQ checkout synced |
| IE-M2-1 | 1 | S11T, S11 (AZHQ) | IE-M1-1,2,4 merged (C13); IE-M1-6 merged |
| IE-M2-2 | 1 | S41 (AZHQ, conditional) | OD-AFC-01 = B |
| IE-M2-3 | 2 | S12, S13, S14, S15 | four verdicts; spike_panel_max held |
| IE-M2-4 | 2 | S19 | IE-M1-3 and IE-M1-6 merged |
| IE-M2-5 | 3 | S16, S18 | 10-15 capture done; S18 smoke |
| IE-M3-1 | 1 | S17, S20T..S24 | pairs green; T_yahoo verdict |
| IE-M3-2 | 2 | (deploy) | IE-M3-1 merged |
| IE-M3-3 | 2 | S26T, S26, S27T, S27 | pairs green; visual review |
| IE-M3-4 | 3 | (candidate) S25T, S25 on lane branch + main | IE-M3-1..3 done; cut-off 10-18T15:00Z |
| IE-M3-5 | 4 | S25T, S25, S28 | live evidence |
| IE-M4-1 | 1 | S30T, S30 (+deploy) | green |
| IE-M4-2 | 1 | S31T, S31, S32T, S32 | green; visual review |
| IE-M4-3 | 1 | S34 (stretch, conditional) | OD-AFC-03 = yes |
| IE-M4-4 | 2 | S33 | each fix + regression test |
| IE-M4-5 | 2 | S35 | IE-M3-5, IE-M2-4 merged |
| IE-M4-6 | 3 | (M4 candidate) | IE-M4-1..5 done |
| IE-M5-1 | 1 | S36, S37, S39 | IE-M4-6 exit |
| IE-M5-2 | 2 | S38, S40 | IE-M5-1 merged |
| IE-M5-3 | 3 | (handoff) | final candidate frozen |

## Cut-offs

The live-window times use standard NFL slot times converted from EDT (UTC−4). They are assumptions: S16 and S28 confirm each window from the ESPN scoreboard (CMD-ESPN-RECORD) before relying on it.

- **S16 windows.**
  - The Mon 10-12 game starts about 2026-10-13T00:15Z.
  - The Thu 10-15 game starts about 2026-10-16T00:15Z. This is after the M2 due time (IE-F11).
- **Sunday 2026-10-18, S28.**
  - M3 candidate cut-off is **2026-10-18T15:00:00Z**, giving 2 h before the 17:00Z kickoffs.
  - Late windows: SNF (cut-off 2026-10-18T22:00:00Z), then Mon 10-19 MNF (cut-off 2026-10-19T22:00:00Z, past M3 due; record the slip), then Thu 10-22 (cut-off 2026-10-22T22:00:00Z).
  - If all live windows are missed, labeled replay applies (RISK-AFC-14). The owner must accept the live-only limitation before closeout (technical plan, Exit criteria 1).
- **spike_panel_max.** The S15 verdict is due within 24 h of S12's first install, or Mode A applies by default.
- **T_yahoo.** S17 runs at or after 2026-10-16T19:00:00Z.
- **Stretch S34.** It starts only after M3 exit with M4 on schedule, and drops at **2026-10-21T12:00:00Z**.
- **Conditional S41.** It runs only if OD-AFC-01 = B.
- **Feature freeze.** After the M4 due time (2026-10-21T23:00:00Z), only P0 or P1 fixes (S33) and M5 documents merge.
- **Final candidate freeze: 2026-10-23T08:00:00Z.** This leaves 4 h to the M5 due time (12:00Z) and 11 h to T_deadline (19:00Z). That is the owner's 7-hour M5 buffer plus a 4-hour assessment window.

## Owner-only dependencies (time each blocks ready work)

These are summarized here. Full entries are in `owner_dependencies`.
None is an open question. Each one is an entry criterion that the confirmed decisions already name.

| ID | Action | Blocks | Ready-work blocked from | Latest safe time |
|---|---|---|---|---|
| OWN-01 | Integrated approval + planning PR merge | All 13 wave-1 slices | now (2026-10-11) | 2026-10-12T20:00:00Z (S16 must start before the 10-12 game) |
| OWN-02 | Stick located, model confirmed, ADB on, on network | S12→S13→S14→S15 → S23T, S25T, S27T, S28 | S04 stop condition met | 2026-10-13T23:00:00Z |
| OWN-03 | Provider app installed and signed in | S14 → S15, S23T, S25T, S27T | S13 verdict | S12 first install + 12 h (the spike_panel_max clock runs) |
| OWN-04 | AWS Free-plan account + `afc-dev` profile | S18 → S17, IE-M2-5, IE-M3-2, S28 | S05 stop condition met | 2026-10-15T12:00:00Z (M2); hard limit 2026-10-17T12:00:00Z |
| OWN-05 | Yahoo app submitted; on approval, SSM client id/secret | Live Yahoo path only (manual default otherwise) | M2 entry | 2026-10-16T19:00:00Z (T_yahoo) |
| OWN-06 | OD-AFC-01, -03, -07 at integrated review | S41, S34, S06 scope | review | with OWN-01 |
| OWN-07 | Class C stops (C1, RISK-AFC-02..04) if triggered | Device lane | stop time | within 4 h of the stop, or the M3 cut-off is at risk |
| OWN-08 | M5 actions: license, visibility flip, ESPN terms (C3), video upload, reviewer access, Devpost, external feedback | Submission only | M5 due | before 2026-10-23T19:00:00Z |

## Concurrency proof and findings

**Method.**
- Every pair of slices not ordered by the dependency graph was compared by path prefix within the same repository. The compared write sets are each slice's `Write set` column in `slice-graph.md`.
- Unordered pairs whose write sets overlap:
  - **S05 × S16.** `backend/` ⊇ `backend/fixtures/espn/`. Both are wave 1 and both are in the first five dispatched. This is a defect: IE-F01.
  - **S08 × S39.** Both write `docs/developer-feedback/observations.md`. They are milestone-ordered (M1 vs M5) and never run at the same time, so this is not a defect.
  - **S33 × {S30, S31T, S31, S32T, S32}.** S33 writes `backend/src/` and `tv-app/app/src/` and overlaps their paths. The S33 row already guards this: it dispatches only after a no-overlap write-set check. It is not a defect if that check compares concrete per-defect files.
- Every other unordered pair is disjoint. Per wave:
  - W1: the S01/S02/S03/S06 AZHQ skill directories are pairwise distinct; S04 `tv-app/`, S07 `docs/vnv/`, S08, S09T `tools/ci/tests/`, S09 `tools/ci/*`+`.githooks`+`.github/workflows/ci.yml`, S06L and S10 (distinct files under `evidence/`) are disjoint.
  - W2: S11T and S11 touch distinct `hooks/` files; S12..S15 touch distinct `docs/spikes/SP-n*` and `spikes/spn/` paths; S18 (`backend/samconfig.toml`, `docs/runbooks/deploy.md`) and S19 (`tools/spec/`, `THIRD_PARTY_NOTICES.md`, `spec/`) are disjoint.
  - W3: the backend tests and src packages `feed`, `lineup`+`auth`, `match`+`policy`, `resolver`, `panel` and the `api/*.py` modules are pairwise distinct; the TV `alerts`+`watch`+`net`, `settings`+`link`+`detect` and `panel`+`player` packages are distinct; S17 and S28 write distinct docs.
  - W4: S30, S31x and S32x are disjoint; S34 and S35 are disjoint from all others.
  - W5: S36 to S40 are disjoint.
- Declared write sets are not the whole picture. Hidden shared writes exist on hot files and through read-before-write dependencies; these are findings IE-F02 to IE-F06.
- Shared runtime resources: `fire-tv-stick`, `aws-afc-dev`, `live-game-window`, `harness-configs` and `alphazedehq-skills/<skill>` are serialized by leases. Missing resources are added in IE-F07 (shared worktree index) and IE-F16 (AZHQ main checkout).

Each finding's exact corrected text is in `concurrency_findings`. The Plan Integrator applies the corrections to `slice-graph.md`, `design.md` or the technical plan. This plan does not edit them.

```json integration_plan
{
  "branches": [
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/setup-pre-commit", "slices": ["S01"], "milestone": "M1", "base": "origin/main", "merge": "gh pr merge --merge or --rebase (never squash)", "consumed_as": "azhq.d4a"},
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/setup-a-repo", "slices": ["S02"], "milestone": "M1", "base": "origin/main", "merge": "gh pr merge --merge or --rebase (never squash)", "consumed_as": "azhq.d4b"},
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/ship-pull-request", "slices": ["S03"], "milestone": "M1", "base": "origin/main", "merge": "gh pr merge --merge or --rebase (never squash)", "consumed_as": "azhq.d4c"},
    {"repo": "alphazede/Alphazedehq", "branch": "spec-authoring/d5", "slices": ["S06"], "milestone": "M1", "base": "origin/main", "merge": "gh pr merge --merge or --rebase (never squash)", "consumed_as": "azhq.d5"},
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/harness-hooks", "slices": ["S11T", "S11"], "milestone": "M2", "base": "origin/main at or after azhq.d4a, azhq.d4b, azhq.d4c", "merge": "gh pr merge --merge or --rebase (never squash)", "consumed_as": "azhq.d4e"},
    {"repo": "alphazede/Alphazedehq", "branch": "ci-cd/entry-point", "slices": ["S41"], "milestone": "M2 (per IE-F13)", "base": "origin/main at or after azhq.d4c", "merge": "gh pr merge --merge or --rebase (never squash)", "consumed_as": "azhq.d4f", "conditional": "OD-AFC-01 = B"},
    {"repo": "this", "branch": "afc/device-integration-spikes-m1", "slices": ["S04"], "milestone": "M1", "base": "origin/main after planning PR", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/backend-m1", "slices": ["S05", "S09T", "S09"], "milestone": "M1", "base": "origin/main after planning PR; merge origin/main after IE-M1-5", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/spec-and-docs-m1", "slices": ["S07", "S10", "S06L"], "milestone": "M1", "base": "origin/main after planning PR; merge origin/main after IE-M1-6", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/scribe-m1", "slices": ["S08"], "milestone": "M1", "base": "origin/main after planning PR; merge origin/main after IE-M1-6", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/device-integration-spikes-m2", "slices": ["S12", "S13", "S14", "S15"], "milestone": "M2", "base": "origin/main (APK built from the recorded S04 commit)", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/backend-m2", "slices": ["S16", "S18"], "milestone": "M2", "base": "origin/main; S18 slice branch starts from the recorded S05 commit if IE-M1-6 has not merged", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/spec-and-docs-m2", "slices": ["S19"], "milestone": "M2", "base": "origin/main after IE-M1-6", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/backend-m3", "slices": ["S17", "S20T", "S20", "S21T", "S21", "S22T", "S22", "S23T", "S23", "S24T", "S24"], "milestone": "M3", "base": "origin/main after IE-M1-6", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/tv-app-ui-m3", "slices": ["S26T", "S26", "S27T", "S27"], "milestone": "M3", "base": "origin/main after IE-M1-5", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/device-integration-spikes-m3", "slices": ["S25T", "S25", "S28"], "milestone": "M3", "base": "origin/main after IE-M1-5; merge origin/main after IE-M3-1 and IE-M3-3 (becomes the M3 candidate)", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/backend-m4", "slices": ["S30T", "S30"], "milestone": "M4", "base": "origin/main after IE-M3-1", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/tv-app-ui-m4", "slices": ["S31T", "S31", "S32T", "S32"], "milestone": "M4", "base": "origin/main after IE-M3-3", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/defects-m4", "slices": ["S33"], "milestone": "M4", "base": "origin/main after IE-M3-5", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/device-integration-spikes-m4", "slices": ["S34"], "milestone": "M4", "base": "origin/main after IE-M3-5", "merge": "gh pr merge --merge", "conditional": "OD-AFC-03 = yes"},
    {"repo": "this", "branch": "afc/spec-and-docs-m4", "slices": ["S35"], "milestone": "M4", "base": "origin/main after IE-M3-5", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/spec-and-docs-m5", "slices": ["S36", "S37"], "milestone": "M5", "base": "origin/main after IE-M4-6", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/scribe-m5", "slices": ["S39"], "milestone": "M5", "base": "origin/main after IE-M4-6", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/device-integration-spikes-m5", "slices": ["S38", "S40"], "milestone": "M5", "base": "origin/main after IE-M5-1", "merge": "gh pr merge --merge"},
    {"repo": "this", "branch": "afc/<lane>-m<n>-<slice> (slice branches)", "slices": ["one per running slice or TDD pair; a TDD pair shares one, named after the green slice"], "milestone": "per slice", "base": "the lane branch head at dispatch", "merge": "git merge --no-ff into the lane branch in the lane worktree; never pushed with force"}
  ],
  "worktrees": [
    {"path": "<workspace>/worktrees/amazon-fantasy-companion-<lane>-m<n>", "use": "lane integration worktree: merges completed slice branches, runs post-merge lane gate, opens the lane PR", "owner": "Orchestrator or Coordinator of that wave"},
    {"path": "<workspace>/worktrees/amazon-fantasy-companion-<lane>-<slice>", "use": "one per running slice or TDD pair (IE-F07); never shared by two concurrent sessions", "owner": "the slice's implementer session(s)"},
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-setup-pre-commit", "use": "S01"},
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-setup-a-repo", "use": "S02"},
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-ship-pull-request", "use": "S03"},
    {"path": "<workspace>/worktrees/Alphazedehq-spec-authoring", "use": "S06"},
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-harness-hooks", "use": "S11T, S11"},
    {"path": "<workspace>/worktrees/Alphazedehq-ci-cd-entry-point", "use": "S41 (conditional)"},
    {"rule": "Never hidden directories or /tmp. Remove the worktree, local branch and remote branch in the same session after the PR merges, unless it holds uncommitted or unmerged work."}
  ],
  "steps": [
    {
      "id": "IE-M1-1", "milestone": "M1", "order": 1, "merges": ["S01"],
      "entry_criteria": ["Planning PR merged on main (OWN-01)", "S01 stop condition met at PR head: CMD-D4A-TEST, CMD-SKILL-SIZE, CMD-SKILL-TRIGGER exit 0", "S01 write set includes skills/setup-pre-commit/agents/openai.yaml (IE-F18)", "One Reviewer review with OCR delegate (Reverify: not applicable — no binary) and at most one repair", "AZHQ PR required checks green; PR mergeable without conflict; lease alphazedehq-skills/setup-pre-commit held by S01 only"],
      "post_step_vv": ["CMD-MERGE-IDENTITY (proposed): record AZHQ merge commit as azhq.d4a", "CMD-D4A-TEST and CMD-SKILL-SIZE re-run on azhq.d4a", "CMD-AZHQ-SYNC (proposed): fast-forward the AZHQ main checkout under lease alphazedehq-main-checkout; record HEAD"],
      "rollback": "Revert PR in Alphazedehq (git revert -m 1 azhq.d4a on a new branch, PR, merge commit); CMD-AZHQ-SYNC; S09T/S09/S11T re-pin to the revert-free predecessor or wait for the relanded fix. Never force-push.",
      "exit": "azhq.d4a recorded; skill live on host at the synced HEAD."
    },
    {
      "id": "IE-M1-2", "milestone": "M1", "order": 1, "merges": ["S02"],
      "entry_criteria": ["S02 stop condition met: CMD-D4B-TEST, CMD-SKILL-SIZE, CMD-SKILL-TRIGGER exit 0; template passes the checker", "Reviewer review recorded (OCR delegate; Reverify not applicable — no binary)", "AZHQ checks green; lease alphazedehq-skills/setup-a-repo"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → azhq.d4b", "CMD-D4B-TEST re-run on azhq.d4b", "CMD-AZHQ-SYNC"],
      "rollback": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC; S09 vendored checker re-vendored from the reverted state by a new S09 repair packet.",
      "exit": "azhq.d4b recorded."
    },
    {
      "id": "IE-M1-3", "milestone": "M1", "order": 1, "merges": ["S06"],
      "entry_criteria": ["S06 stop condition met: CMD-SCAN PASS, CMD-D5-TEST, CMD-D5-AGNOSTIC, CMD-SKILL-SIZE exit 0; CMD-SKILL-TRIGGER routes the matching request to spec-authoring and the SDoc request to use-requirements-system", "OD-AFC-07 decision applied (use-requirements-system description edit present only if approved)", "Reviewer review recorded; AZHQ checks green; leases alphazedehq-skills/spec-authoring and alphazedehq-skills/use-requirements-system"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → azhq.d5", "CMD-D5-TEST and CMD-D5-AGNOSTIC re-run on azhq.d5", "CMD-AZHQ-SYNC"],
      "rollback": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC; remove the S06L harness links (restore from S06L evidence); S19 does not start until relanded.",
      "exit": "azhq.d5 recorded; unblocks S06L, S09T (with azhq.d4a, azhq.d4b), S19."
    },
    {
      "id": "IE-M1-4", "milestone": "M1", "order": 1, "merges": ["S03"],
      "entry_criteria": ["S03 stop condition met: existing tests/edit-pr.test.sh passes (CMD-D4C-TEST), CMD-SKILL-SIZE exit 0, CMD-SKILL-TRIGGER", "Reviewer review recorded; AZHQ checks green (coe-gates runs edit-pr.test.sh); lease alphazedehq-skills/ship-pull-request"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → azhq.d4c", "CMD-D4C-TEST re-run on azhq.d4c", "CMD-AZHQ-SYNC (changes the PR gate procedure for every repository on the host: sync only between dispatches)"],
      "rollback": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC.",
      "exit": "azhq.d4c recorded; with azhq.d4a and azhq.d4b satisfies C13 for S11T."
    },
    {
      "id": "IE-M1-5", "milestone": "M1", "order": 2, "merges": ["S04"],
      "entry_criteria": ["S04 stop condition met with corrected commands (IE-F02): CMD-SCAN PASS for starter, Android SDK and Gradle wrapper; CMD-ANDROID-BUILD (proposed) exit 0", "S04 skeleton satisfies IE-F04, IE-F05, IE-F06, IE-F17 (net interface, hot-file contents, API base URL property, footage ignore)", "Starter .github/ dropped (SM F4); minSdk 25, applicationId afc.companion (SM F1, F2)", "Reviewer review recorded (Reverify on the debug APK claim per AC-AFC-REV-01)"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → this.s04", "CMD-ANDROID-BUILD on the merge commit", "CMD-APK-SHA (proposed) of the debug APK; CMD-GATE-ANDROID becomes available after IE-M1-6"],
      "rollback": "Revert PR on this repository (revert branch, PR, merge commit). S12 continues from the recorded S04 APK only if the revert did not change tv-app/app/build.gradle.kts or AndroidManifest.xml; else S12 waits.",
      "exit": "this.s04 and the S04 APK sha256 recorded; tv-app hot-file owner fixed as the device-integration-spikes lane."
    },
    {
      "id": "IE-M1-6", "milestone": "M1", "order": 3, "merges": ["S05", "S09T", "S09"],
      "entry_criteria": ["IE-M1-1, IE-M1-2, IE-M1-3 merged (S09T dependency)", "IE-M1-5 merged and origin/main merged into afc/backend-m1 (so CMD-GATE-ALL on main has tv-app)", "S05 stop condition met with CMD-BACKEND-CHECK (IE-F02); S05 write set excludes backend/fixtures/ (IE-F01) and carries the IE-F05 hot-file contents", "S09T red receipt (CMD-RED) and S09 green; CMD-WORKFLOW-CHECK exit 0; tools/ci/VENDORED.md names azhq.d4a and azhq.d4b (IE-F10); hygiene area runs tools/ci/tests (IE-F09)", "Planning package scrubbed of absolute home paths (hygiene must pass on all tracked files)", "PR shows gate / backend and gate / hygiene checks green; Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → this.s05_s09", "CMD-GATE-ALL on the merge commit: android PASS (debug APK built by the gate), backend PASS, spec PASS nothing to check, hygiene PASS", "CMD-CI-VENDOR-PIN (proposed)", "CMD-CONTRACT-FROZEN (proposed) baseline recorded: sha256 of backend/api/openapi.yaml, backend/template.yaml, backend/src/afc_backend/store/, tv-app/app/src/main/java/afc/companion/net/ApiClient.kt"],
      "rollback": "Revert PR on this repository. Lane branches that merged main after this step merge the revert too. git config core.hooksPath is reset by the D4-A installer's uninstall path if hooks block work after revert.",
      "exit": "Repo gate live on main and in PR checks (AC-AFC-CI-01..03); frozen-contract baseline recorded."
    },
    {
      "id": "IE-M1-7", "milestone": "M1", "order": 4, "merges": ["S07", "S10", "S06L", "S08"],
      "entry_criteria": ["IE-M1-6 merged and origin/main merged into afc/spec-and-docs-m1 and afc/scribe-m1 (hygiene receipt for S08 per IE-F03)", "IE-M1-3 merged and CMD-AZHQ-SYNC HEAD at or after azhq.d5 before S06L ran (IE-F16); lease harness-configs released by S06L", "CMD-VNV-CHECK, CMD-MILESTONES, CMD-SKILL-LINK, CMD-GATE-HYGIENE receipts", "Reviewer review recorded for each PR"],
      "post_step_vv": ["CMD-MERGE-IDENTITY for both PRs", "CMD-GATE-HYGIENE and CMD-VNV-CHECK on main", "CMD-SKILL-LINK re-read on host"],
      "rollback": "Revert the affected PR; S06L links removed by deleting the four symlinks it created (paths in skill-links.txt).",
      "exit": "M1 exit: milestones readback equal (AC-AFC-PLAN-02); D4-A..C and D5 merged and linked; gate green on a PR; Vnv tree; debug APK built by gate; backend skeleton with frozen API green; Scribe log; first ESPN capture committed on the S16 slice branch (IE-F12)."
    },
    {
      "id": "IE-M2-1", "milestone": "M2", "order": 1, "merges": ["S11T", "S11"],
      "entry_criteria": ["IE-M1-1, IE-M1-2, IE-M1-4 merged (C13); IE-M1-6 merged (a repository with tools/ci/gate.sh exists for the demonstration, IE-F15)", "S11T red receipt then CMD-HOOK-TEST green at PR head", "Lease harness-configs free; no implementer session mid-commit (installer changes every harness on the host)", "Reviewer review recorded; AZHQ checks green"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → azhq.d4e", "CMD-AZHQ-SYNC", "CMD-HOOK-INSTALL then installer --verify: per harness wired or typed gap (Muse, AGY)", "CMD-HOOK-DEMO (proposed): in a scratch slice worktree of this repository, a commit carrying a deliberate hygiene failure is blocked under each wired harness; the scratch worktree is removed"],
      "rollback": "CMD-HOOK-RESTORE (proposed): installer restores each harness configuration from its timestamped backup; revert PR in Alphazedehq; CMD-AZHQ-SYNC.",
      "exit": "AC-AFC-D4-04 and AC-AFC-D5-05 (Muse/AGY) evidence; azhq.d4e recorded."
    },
    {
      "id": "IE-M2-2", "milestone": "M2", "order": 1, "merges": ["S41"],
      "entry_criteria": ["OD-AFC-01 = B (else this step is skipped and recorded as not applicable)", "IE-M1-1, IE-M1-2, IE-M1-4 merged", "CMD-SKILL-SIZE, CMD-SKILL-TRIGGER pass; Reviewer review; lease alphazedehq-skills/ci-cd"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → azhq.d4f", "CMD-AZHQ-SYNC", "CMD-SKILL-TRIGGER re-run on host"],
      "rollback": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC.",
      "exit": "azhq.d4f recorded or step marked not applicable."
    },
    {
      "id": "IE-M2-3", "milestone": "M2", "order": 2, "merges": ["S12", "S13", "S14", "S15"],
      "entry_criteria": ["Verdict files SP-1..SP-4 present; C1 not triggered (else class C owner stop, OWN-07, and this step waits)", "S15 verdict timestamp at most S12 first-install + spike_panel_max, or Mode A recorded at expiry", "SP-3 registry draft present", "origin/main merged into afc/device-integration-spikes-m2; Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY", "CMD-SPIKE-VERDICTS (proposed): each verdict file has route, steps, evidence paths, verdict, limits (AC-AFC-SPIKE-02)", "CMD-GATE-HYGIENE on main", "Record panel mode and sha256 of docs/spikes/SP-3-provider-registry.json"],
      "rollback": "Revert PR; verdicts are evidence, so a wrong verdict is superseded by a new verdict commit, never edited in place after merge.",
      "exit": "Panel mode and SP-3 route fixed as inputs to S23T, S25T, S27T."
    },
    {
      "id": "IE-M2-4", "milestone": "M2", "order": 2, "merges": ["S19"],
      "entry_criteria": ["IE-M1-3 merged (azhq.d5) and IE-M1-6 merged (spec area)", "CMD-SPEC-VENDOR: tools/spec/VENDORED.md commit equals azhq.d5 and files equal the AZHQ tree at azhq.d5", "Rev 0.1 builds; CMD-GATE-SPEC PASS; second build byte-identical", "Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY", "CMD-GATE-SPEC and CMD-SPEC-VENDOR on main"],
      "rollback": "Revert PR; re-vendor from azhq.d5 in a repair packet.",
      "exit": "AC-AFC-SPEC-01, -02 (rev 0.1)."
    },
    {
      "id": "IE-M2-5", "milestone": "M2", "order": 3, "merges": ["S16", "S18"],
      "entry_criteria": ["S16 captures from the 10-12 and 10-15 games committed (10-15 game ends about 2026-10-16T04:00Z, IE-F11); CMD-ESPN-RECORD verdict file", "S18: CMD-SCAN PASS (SAM CLI), CMD-SAM-DEPLOY to stack afc-dev with profile afc-dev, CMD-SMOKE 401 without token and 200 on link start; deployed backend/template.yaml sha256 equals main's (CMD-TEMPLATE-DIGEST, proposed)", "origin/main merged into afc/backend-m2; gate / backend and gate / hygiene green; Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY", "CMD-GATE-BACKEND on main", "Record sha256 manifest of backend/fixtures/espn/ (fixture digest)"],
      "rollback": "Revert PR; stack afc-dev stays as deployed (no paid resource by AC-AFC-SEC-03); redeploy from the previous recorded SHA with CMD-SAM-ROLLBACK (proposed) if the template changed.",
      "exit": "M2 exit: SP-1..SP-5 verdicts, panel mode, fixtures, dev stack, hooks wired or typed gaps, spec rev 0.1."
    },
    {
      "id": "IE-M3-1", "milestone": "M3", "order": 1, "merges": ["S17", "S20T", "S20", "S21T", "S21", "S22T", "S22", "S23T", "S23", "S24T", "S24"],
      "entry_criteria": ["Each TDD pair: CMD-RED receipt then green slice (IE-F08 commit handling); CMD-GATE-BACKEND exit 0 in its slice worktree", "Slice branches merged into afc/backend-m3 with git merge --no-ff in order S20 → S21 → S22 → S23 → S24, CMD-GATE-BACKEND after each merge; a non-whitespace conflict returns to the later slice's lane", "CMD-CONTRACT-FROZEN: openapi.yaml, template.yaml, store/ unchanged except routed hot-file deltas", "CMD-REGISTRY-CHECK: registry.json entries subset of SP-3 verified forms", "S17 verdict recorded at or after T_yahoo (2026-10-16T19:00:00Z)", "Reviewer review recorded; target merge 2026-10-17T18:00:00Z"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → this.m3_backend", "CMD-GATE-BACKEND, CMD-GATE-HYGIENE, CMD-CONTRACT-FROZEN on main"],
      "rollback": "Revert PR; IE-M3-4 candidate forms on the device lane branch by merging the unreverted lane heads only if their gate passes, else S28 uses the previous deployed stack in replay mode.",
      "exit": "Backend feature-complete for M3 on main."
    },
    {
      "id": "IE-M3-2", "milestone": "M3", "order": 2, "merges": [],
      "entry_criteria": ["IE-M3-1 merged", "Lease aws-afc-dev free (S17 done)", "OWN-04 satisfied"],
      "post_step_vv": ["CMD-SAM-DEPLOY from this.m3_backend with ReplayMode=on", "CMD-SMOKE", "CMD-TEMPLATE-DIGEST; record stack outputs (ApiUrl) and provider registry sha256"],
      "rollback": "CMD-SAM-ROLLBACK: redeploy the last recorded good SHA (CloudFormation rolls back a failed update automatically); never delete the stack without the owner.",
      "exit": "Dev stack equals main at this.m3_backend; ApiUrl recorded for APK builds."
    },
    {
      "id": "IE-M3-3", "milestone": "M3", "order": 2, "merges": ["S26T", "S26", "S27T", "S27"],
      "entry_criteria": ["S27T started only after IE-M2-3 recorded the panel mode", "Pairs green: CMD-GATE-ANDROID in each slice worktree; CMD-FOOTAGE-FETCH sha256 pinned (Mode A)", "Slice branches merged into afc/tv-app-ui-m3 (S26 then S27), CMD-GATE-ANDROID after each", "On-device visual review with CMD-ADB-SCREENCAP per changed screen and state (AC-AFC-VIS-01); Reviewer review recorded", "No edit to tv-app hot files outside routed hot-file deltas (CMD-CONTRACT-FROZEN)", "Target merge 2026-10-18T06:00:00Z"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → this.m3_tvui", "CMD-GATE-ANDROID on main", "CMD-CONTRACT-FROZEN"],
      "rollback": "Revert PR; IE-M3-4 builds the candidate from the remaining merged lanes and records missing panel or settings screens as an anomaly.",
      "exit": "Settings, link, detect, panel, player on main."
    },
    {
      "id": "IE-M3-4", "milestone": "M3", "order": 3, "merges": ["S25T", "S25"],
      "entry_criteria": ["IE-M3-1 and IE-M3-3 merged (or their recorded lane heads, per anomaly rule AN-03); IE-M3-2 done", "S25 green on JVM and CMD-ANDROID-CONNECTED on the stick", "origin/main merged into afc/device-integration-spikes-m3 without non-whitespace conflict; this merge commit is the M3 candidate", "Leases fire-tv-stick and aws-afc-dev held from 2026-10-18T09:00:00Z", "Cut-off: candidate ready by 2026-10-18T15:00:00Z"],
      "post_step_vv": ["CMD-GATE-ALL on the candidate", "CMD-FOOTAGE-FETCH then APK build with -PafcApiBaseUrl=<ApiUrl> (IE-F06); CMD-APK-SHA", "CMD-INSTALL-APK on the stick", "CMD-E2E-REPLAY (proposed): with ReplayMode=on, a released alert appears as heads-up over provider playback, Watch records a launch outcome, the panel shows replay-labeled points in the decided mode; CMD-ADB-SCREENCAP for each"],
      "rollback": "Uninstall the candidate APK and reinstall the last recorded good APK (CMD-INSTALL-APK with its sha256); reset afc/device-integration-spikes-m3 only by a new revert commit, never by reset or force-push.",
      "exit": "M3 candidate SHA and APK sha256 recorded and rehearsed in replay."
    },
    {
      "id": "IE-M3-5", "milestone": "M3", "order": 4, "merges": ["S25T", "S25", "S28"],
      "entry_criteria": ["IE-M3-4 exit", "Lease live-game-window (Sunday 2026-10-18) plus fire-tv-stick and aws-afc-dev", "Stack redeployed from the same SHA with ReplayMode=off (CMD-SAM-DEPLOY, CMD-TEMPLATE-DIGEST unchanged except the parameter)", "S28 evidence doc committed on afc/device-integration-spikes-m3; Reviewer review (Reverify on the APK claim) recorded"],
      "post_step_vv": ["CMD-INSTALL-APK, CMD-ADB-SCREENCAP, CMD-SCREENRECORD during the live window (S28)", "After merge: CMD-MERGE-IDENTITY → this.m3; CMD-GATE-ALL on main", "CMD-TREE-EQUAL (proposed): tv-app/ and backend/ identical between the live candidate and this.m3; if the repair round changed them, CMD-E2E-REPLAY reruns on this.m3"],
      "rollback": "Revert PR; the live evidence keeps its candidate SHA; if a later window is used (cut-offs), S28 reruns against the then-current candidate.",
      "exit": "M3 exit: live alert over provider playback, Watch outcome, panel live on the stick (or recorded slip per cut-offs)."
    },
    {
      "id": "IE-M4-1", "milestone": "M4", "order": 1, "merges": ["S30T", "S30"],
      "entry_criteria": ["Pair green; CMD-GATE-BACKEND; CMD-CONTRACT-FROZEN", "Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY", "CMD-GATE-BACKEND on main", "CMD-SAM-DEPLOY (ReplayMode=on), CMD-SMOKE, CMD-TEMPLATE-DIGEST"],
      "rollback": "Revert PR; CMD-SAM-ROLLBACK to this.m3.",
      "exit": "Corrections live on the dev stack."
    },
    {
      "id": "IE-M4-2", "milestone": "M4", "order": 1, "merges": ["S31T", "S31", "S32T", "S32"],
      "entry_criteria": ["Pairs green; slice branches merged S31 then S32 into afc/tv-app-ui-m4 with CMD-GATE-ANDROID after each", "Reboot persistence screencaps (S31); label screencaps (S32); visual review (AC-AFC-VIS-01); Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY", "CMD-GATE-ANDROID on main", "CMD-CONTRACT-FROZEN"],
      "rollback": "Revert PR.",
      "exit": "Complete controls, persistence and labels on main."
    },
    {
      "id": "IE-M4-3", "milestone": "M4", "order": 1, "merges": ["S34"],
      "entry_criteria": ["OD-AFC-03 = yes, M3 exit met and every M4 slice on schedule; else not dispatched and recorded not applicable", "Verdict (verified route or drop) by 2026-10-21T12:00:00Z; Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY", "CMD-SPIKE-VERDICTS", "CMD-GATE-HYGIENE"],
      "rollback": "Revert PR.",
      "exit": "SP-7 verdict; voice stays hidden unless verified and implemented (AC-AFC-CTRL-03)."
    },
    {
      "id": "IE-M4-4", "milestone": "M4", "order": 2, "merges": ["S33"],
      "entry_criteria": ["Each defect packet declared concrete files and passed the no-overlap check against running slices", "Each fix has a regression test; CMD-GATE-ALL green on afc/defects-m4 after merging origin/main (after IE-M4-1, IE-M4-2)", "No open P0/P1 defect; Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY", "CMD-GATE-ALL on main"],
      "rollback": "Revert PR (or the single defect's commit by a revert PR) and reopen the defect.",
      "exit": "No open P0/P1."
    },
    {
      "id": "IE-M4-5", "milestone": "M4", "order": 2, "merges": ["S35"],
      "entry_criteria": ["IE-M2-4 and IE-M3-5 merged; S12..S17 verdicts on main", "Rev 1.0 builds; CMD-GATE-SPEC PASS; identical rebuild; Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY", "CMD-GATE-SPEC on main"],
      "rollback": "Revert PR; rev 0.1 remains.",
      "exit": "AC-AFC-SPEC-02, -03 (rev 1.0)."
    },
    {
      "id": "IE-M4-6", "milestone": "M4", "order": 3, "merges": [],
      "entry_criteria": ["IE-M4-1, IE-M4-2, IE-M4-4, IE-M4-5 merged; IE-M4-3 merged or not applicable", "Leases fire-tv-stick and aws-afc-dev", "Cut-off 2026-10-21T23:00:00Z"],
      "post_step_vv": ["CMD-GATE-ALL on main (this.m4)", "CMD-STUB-SCAN", "CMD-SAM-DEPLOY from this.m4, CMD-SMOKE, CMD-TEMPLATE-DIGEST, registry sha256", "CMD-FOOTAGE-FETCH, APK build with -PafcApiBaseUrl, CMD-APK-SHA, CMD-INSTALL-APK", "CMD-E2E-REPLAY including correction alert and panel total agreement (AC-AFC-ALERT-03, AC-AFC-PANEL-04)", "Optional live re-check on Thu 10-22 if S28 used replay"],
      "rollback": "Revert the M4 PR that broke the check; candidate falls back to this.m3 plus the passing M4 PRs.",
      "exit": "M4 candidate this.m4 with APK sha256: input to S38 clips and M5."
    },
    {
      "id": "IE-M5-1", "milestone": "M5", "order": 1, "merges": ["S36", "S37", "S39"],
      "entry_criteria": ["IE-M4-6 exit", "S36 README setup steps run once from a clean clone in replay mode; S37 lists every owner-only action with due times; S39 coverage and sanitization; CMD-GATE-HYGIENE", "Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY", "CMD-GATE-HYGIENE on main", "CMD-TREE-EQUAL: tv-app/ and backend/ unchanged since this.m4"],
      "rollback": "Revert PR.",
      "exit": "Submission documents on main."
    },
    {
      "id": "IE-M5-2", "milestone": "M5", "order": 2, "merges": ["S38", "S40"],
      "entry_criteria": ["IE-M5-1 merged", "S38 clips recorded from the this.m4 APK (sha256 in clips README); replay and Mode A segments labeled", "S40: CMD-APK-RELEASE from apk_build_sha = main after IE-M5-1, after CMD-FOOTAGE-FETCH and with -PafcApiBaseUrl; signing per the remaining-risk note (no owner key assumed)", "CMD-TREE-EQUAL: tv-app/ and backend/ equal between this.m4 and apk_build_sha", "Reviewer review recorded"],
      "post_step_vv": ["CMD-MERGE-IDENTITY → this.final", "CMD-GATE-ALL on this.final", "CMD-TREE-EQUAL: tv-app/ and backend/ equal between apk_build_sha and this.final", "CMD-STUB-SCAN"],
      "rollback": "Revert PR; rebuild the APK from the previous apk_build_sha.",
      "exit": "Final integrated candidate frozen by 2026-10-23T08:00:00Z."
    },
    {
      "id": "IE-M5-3", "milestone": "M5", "order": 3, "merges": [],
      "entry_criteria": ["IE-M5-2 exit", "Dev stack deployed from this.final tree (CMD-TEMPLATE-DIGEST equals this.final backend/template.yaml)"],
      "post_step_vv": ["CMD-REVERIFY (proposed): Reverify on the final APK sha256 (AC-AFC-REV-01)", "Hand the final candidate to the Assurance Test Engineer and the Integration Engineer execution sessions (Lifecycle cadence)"],
      "rollback": "If an assessment fails before 2026-10-23T12:00:00Z: revert the offending M5 PR or repair once and repeat IE-M5-2; after that, report the result to the owner unchanged.",
      "exit": "Lifecycle-end assessment inputs complete; owner M5 actions remain owner-only."
    }
  ],
  "configuration_identity": {
    "this_repo_commits": {"planning": "<planning PR merge SHA>", "this.s04": "<IE-M1-5 merge>", "this.s05_s09": "<IE-M1-6 merge>", "this.m3_backend": "<IE-M3-1 merge>", "this.m3_tvui": "<IE-M3-3 merge>", "m3_candidate": "<IE-M3-4 lane merge commit>", "this.m3": "<IE-M3-5 merge>", "this.m4": "<main at IE-M4-6>", "apk_build_sha": "<main after IE-M5-1>", "this.final": "<IE-M5-2 merge>"},
    "alphazedehq_commits": {"azhq.d4a": "<S01 merge>", "azhq.d4b": "<S02 merge>", "azhq.d4c": "<S03 merge>", "azhq.d5": "<S06 merge>", "azhq.d4e": "<S11 merge>", "azhq.d4f": "<S41 merge or not applicable>", "azhq_checkout_head": "<HEAD after each CMD-AZHQ-SYNC; recorded in every dispatch packet issued after it>"},
    "consumed_pins": {"tools/ci/VENDORED.md": "azhq.d4a (gate template), azhq.d4b (check_workflows.py)", "tools/spec/VENDORED.md": "azhq.d5", "S09T/S11T read inputs": "azhq.d4a, azhq.d4b, azhq.d4c, azhq.d5"},
    "apk": {"debug_apk_sha256": "per IE-M1-5, IE-M3-4, IE-M4-6 (CMD-APK-SHA)", "final_apk_sha256": "S40 docs/evidence/final-apk.md", "build_inputs": ["apk_build_sha", "Gradle wrapper checksum", "footage sha256 pinned in tools/fetch-footage.sh (Mode A)", "Gradle property afcApiBaseUrl value (stack output, not a secret)"]},
    "aws": {"stack_name": "afc-dev", "aws_profile_name": "afc-dev", "template_digest": "sha256 of backend/template.yaml at the deployed SHA (CMD-TEMPLATE-DIGEST)", "parameters": ["ReplayMode"], "stack_outputs": ["ApiUrl"], "ssm_parameter_names": "as declared in backend/template.yaml by S05 (names only; values owner-held)"},
    "provider_registry_digest": "sha256 of backend/providers/registry.json at this.m3_backend, this.m4, this.final; SP-3 draft sha256 at IE-M2-3",
    "fixtures_digest": "sha256 manifest of backend/fixtures/espn/ at IE-M2-5",
    "env_var_names": ["AWS_PROFILE", "GIT_AUTHOR_NAME", "GIT_AUTHOR_EMAIL", "ANDROID_HOME", "JAVA_HOME"],
    "harness_config_backups": "timestamped backups written by install-ci-gate-hook.py at IE-M2-1 (paths recorded in the installer receipt, home-relative)"
  },
  "authorized_glue": {
    "default": "none",
    "allowed_mechanical": ["git merge --no-ff of a completed slice branch into its lane branch", "git merge of origin/main into a lane branch", "resolution of whitespace-only conflicts"],
    "not_glue": ["any non-whitespace conflict: returns to the lane that merged later", "hot-file deltas: routed one-file packets on the owner lane (S04 lane for tv-app hot files, S05 lane for backend hot files)", "any change to a frozen contract: CONTRACT_STOP to the Orchestrator"],
    "hot_file_owners": {"tv-app/app/build.gradle.kts, tv-app/build.gradle.kts, tv-app/settings.gradle.kts, tv-app/gradle/, tv-app/app/src/main/AndroidManifest.xml, MainActivity and navigation": "S04 (device-integration-spikes lane)", "backend/template.yaml, backend/pyproject.toml, backend/uv.lock, backend/api/openapi.yaml, backend/src/afc_backend/store/, backend/src/afc_backend/api router module, backend/tests/conftest.py": "S05 (backend lane)", "THIRD_PARTY_NOTICES.md": "S19 then S36", "docs/developer-feedback/observations.md": "S08 then S39"}
  },
  "stubs": [
    {"stub": "TV component stubs marked AFC-STUB", "by": "S04", "replaced_by": ["S25", "S26", "S27", "S31", "S32"], "removal_check": "CMD-STUB-SCAN at IE-M4-6 and IE-M5-2"},
    {"stub": "Backend route stubs marked AFC-STUB", "by": "S05", "replaced_by": ["S20", "S21", "S22", "S23", "S24", "S30"], "removal_check": "CMD-STUB-SCAN"},
    {"stub": "Empty provider registry", "by": "S05", "replaced_by": ["S23"], "removal_check": "CMD-REGISTRY-CHECK"},
    {"stub": "ReplaySource with recorded fixtures (simulator, permanent)", "by": "S16, S20", "replaced_by": [], "removal_check": "replay label present whenever ReplayMode=on (CMD-E2E-REPLAY)"},
    {"stub": "ManualSource (permanent fallback)", "by": "S21", "replaced_by": [], "removal_check": "S17 verdict decides the default"},
    {"stub": "Mode A CompanionPlayer (permanent fallback)", "by": "S27", "replaced_by": [], "removal_check": "S15 verdict; sample-footage label"},
    {"stub": "spec gate area GAP or PASS nothing to check", "by": "S09", "replaced_by": ["S19"], "removal_check": "CMD-GATE-SPEC PASS at IE-M2-4"}
  ],
  "anomaly_rollback_recovery": {
    "anomalies": [
      {"id": "AN-01", "class": "post-merge check failure on main", "action": "Stop dependent merges; revert PR of the step (git revert -m 1, PR, merge commit); lane repairs on a new slice branch from main; reland through the same step"},
      {"id": "AN-02", "class": "interface mismatch between producer and consumer", "action": "Return to the producer lane if it violates the frozen contract, else to the consumer lane; a needed contract change is CONTRACT_STOP to the Orchestrator (Planning and Design), never glue"},
      {"id": "AN-03", "class": "lane PR not merged by its cut-off (M3)", "action": "Form the candidate on the device lane branch by merging the recorded unmerged lane heads whose gates pass; record the composite SHA; land through review afterwards"},
      {"id": "AN-04", "class": "deploy failure", "action": "CloudFormation automatic rollback; CMD-SAM-ROLLBACK to the last recorded good SHA; no stack deletion or plan change (owner-only)"},
      {"id": "AN-05", "class": "AZHQ skill regression after sync", "action": "Revert PR in Alphazedehq; CMD-AZHQ-SYNC; packets issued after the bad sync are re-issued with the new HEAD"},
      {"id": "AN-06", "class": "AZHQ main checkout cannot fast-forward (local uncommitted owner work conflicts)", "action": "Do not stash, reset or switch; report to the owner with the conflicting path; consumers wait (destructive git is owner-only)"},
      {"id": "AN-07", "class": "device unavailable or C1 triggered", "action": "Class C owner stop (OWN-07); device lane holds; backend and tv-app-ui lanes continue against replay and fakes"},
      {"id": "AN-08", "class": "live window missed", "action": "Next window per cut-offs; replay fallback with labels (RISK-AFC-14)"},
      {"id": "AN-09", "class": "gate GAP (exit 3) at a post-step", "action": "Typed gap, never a pass; provision the tool (after scan-software-supply-chain) and rerun"},
      {"id": "AN-10", "class": "route exhausted mid-step (RISK-AFC-07)", "action": "Next ordered fallback of the frozen profile with an activation receipt; queue if all exhausted"}
    ],
    "rollback_rules": ["Revert PR only; never force-push, reset a pushed branch or commit on local main", "Deploy rollback redeploys a recorded SHA; hook rollback restores the installer's timestamped backups", "A rollback is complete when the post-step V&V of the restored state passes"],
    "recovery": "After a revert, the owning lane repairs on a fresh slice branch from main; the step reruns with the same entry criteria; no new review round unless the repair changed the approved scope (one review + one repair rule)."
  },
  "cutoffs": [
    {"id": "CO-01", "what": "Planning approval and merge for S16 to catch the 10-12 game", "at": "2026-10-12T20:00:00Z"},
    {"id": "CO-02", "what": "S15 panel verdict", "at": "S12 first install + 24 h (spike_panel_max); Mode A at expiry"},
    {"id": "CO-03", "what": "S17 Yahoo check", "at": "not before 2026-10-16T19:00:00Z"},
    {"id": "CO-04", "what": "Backend M3 lane merge target", "at": "2026-10-17T18:00:00Z"},
    {"id": "CO-05", "what": "tv-app-ui M3 lane merge target", "at": "2026-10-18T06:00:00Z"},
    {"id": "CO-06", "what": "M3 candidate ready for Sunday live test", "at": "2026-10-18T15:00:00Z; then SNF 2026-10-18T22:00:00Z, MNF 2026-10-19T22:00:00Z, TNF 2026-10-22T22:00:00Z; else labeled replay plus owner acceptance"},
    {"id": "CO-07", "what": "S34 stretch drop", "at": "2026-10-21T12:00:00Z"},
    {"id": "CO-08", "what": "Feature freeze (only P0/P1 fixes and M5 docs merge after)", "at": "2026-10-21T23:00:00Z"},
    {"id": "CO-09", "what": "Final candidate frozen", "at": "2026-10-23T08:00:00Z"},
    {"id": "CO-10", "what": "M5 due; owner buffer to T_deadline", "at": "2026-10-23T12:00:00Z; T_deadline 2026-10-23T19:00:00Z"}
  ],
  "final_candidate": {
    "ref": "this.final (IE-M5-2 merge commit on main of 1wgrumph/amazon-fantasy-companion)",
    "includes": ["apk_build_sha and final APK sha256 (S40)", "dev stack afc-dev deployed from the this.final backend tree (template digest)", "provider registry digest", "azhq.d4a, azhq.d4b, azhq.d4c, azhq.d4e, azhq.d5 (and azhq.d4f if B)", "vendored pins in tools/ci/VENDORED.md and tools/spec/VENDORED.md", "spec rev 1.0 build (byte-identical rebuild)"],
    "invariants": ["CMD-TREE-EQUAL between apk_build_sha and this.final for tv-app/ and backend/", "CMD-GATE-ALL PASS on this.final", "CMD-STUB-SCAN clean", "no absolute home path in tracked files (hygiene)"]
  },
  "lifecycle_assessment_inputs": {
    "sessions": "Integration Engineer execution session per lane profile at Lifecycle cadence on the same final candidate: primary (Codex CLI / GPT-6.1 Sol), frontend (Claude Code / Claude Opus 5.5), heavyweight (Claude Code / Claude Opus 5.5), bug-triager (Codex CLI / GPT-6.1 Sol), tech-writing (Claude Code / Claude Opus 5.5; the snapshot has no cadence field, so the skill default lifecycle applies). Each starts fresh and rejects author ancestry. The Assurance Test Engineer runs alongside.",
    "inputs": ["final_candidate block and all configuration_identity values", "every step receipt in journey.json execution_receipts (merge SHAs, command outputs, digests)", "Reviewer records per lane PR with OCR sections and Reverify or not-applicable lines", "spike verdicts SP-1..SP-7", "S28 live evidence (or recorded slip and replay evidence)", "IE-M3-4 and IE-M4-6 CMD-E2E-REPLAY screencaps", "visual review screencaps (AC-AFC-VIS-01)", "Reverify output on the final APK", "seit.json V&V results per AC-AFC row", "owner-accepted limitations (class C)", "anomaly log AN-* with resolutions", "typed gaps (Muse/AGY hooks, any GAP exits)"],
    "approved_outcome": "technical plan §Outcome and M5 exit criteria"
  },
  "owner_dependencies": [
    {"id": "OWN-01", "action": "Integrated approval of the planning package and planning PR merge", "blocks": ["all wave-1 slices"], "blocked_from": "2026-10-11", "latest_safe": "2026-10-12T20:00:00Z", "cost_if_late": "S16 misses the 10-12 game; feed fixtures only from 10-15; M1 due at risk"},
    {"id": "OWN-02", "action": "Stick located, model confirmed, ADB debugging enabled, on network", "blocks": ["S12", "S13", "S14", "S15", "S23T", "S25T", "S27T", "S28"], "blocked_from": "S04 stop condition met", "latest_safe": "2026-10-13T23:00:00Z", "cost_if_late": "every hour late delays the device chain and the M3 cut-off one hour"},
    {"id": "OWN-03", "action": "At least one provider app installed and signed in on the stick", "blocks": ["S14", "S15", "S23T", "S25T", "S27T"], "blocked_from": "S13 verdict", "latest_safe": "S12 first install + 12 h", "cost_if_late": "spike_panel_max may expire into Mode A; SP-3 route unverified"},
    {"id": "OWN-04", "action": "AWS Free-plan account and named CLI profile afc-dev", "blocks": ["S18", "S17", "IE-M2-5", "IE-M3-2", "IE-M3-5", "IE-M4-1", "IE-M4-6"], "blocked_from": "S05 stop condition met", "latest_safe": "2026-10-15T12:00:00Z (M2); hard 2026-10-17T12:00:00Z", "cost_if_late": "no deployed backend for the Sunday live test"},
    {"id": "OWN-05", "action": "Yahoo application submitted; on approval, client id and secret into SSM", "blocks": ["live Yahoo path of S21 and S28 only"], "blocked_from": "M2 entry", "latest_safe": "2026-10-16T19:00:00Z", "cost_if_late": "manual lineup default (C6), labeled"},
    {"id": "OWN-06", "action": "OD-AFC-01, OD-AFC-03, OD-AFC-07 at the integrated review", "blocks": ["S41", "S34", "S06 scope"], "blocked_from": "integrated review", "latest_safe": "with OWN-01", "cost_if_late": "S06 lands without the reciprocal non-trigger; S41/S34 not dispatched"},
    {"id": "OWN-07", "action": "Class C stop answers (C1, RISK-AFC-02..04) if triggered", "blocks": ["device lane"], "blocked_from": "stop time", "latest_safe": "stop + 4 h, and before 2026-10-18T09:00:00Z", "cost_if_late": "M3 live test at risk"},
    {"id": "OWN-08", "action": "License choice, visibility flip, ESPN terms (C3), video upload, reviewer access, Devpost submission, external feedback", "blocks": ["submission only"], "blocked_from": "IE-M5-3", "latest_safe": "2026-10-23T19:00:00Z", "cost_if_late": "no submission"}
  ],
  "concurrency_findings": [
    {"id": "IE-F01", "class": "write overlap", "slices": ["S05", "S16"], "compared": "S05 `backend/` (whole new directory) vs S16 `backend/fixtures/espn/`; both wave 1, both in the first five dispatched, no dependency edge", "target": "slice-graph.md S05 row, Write set", "corrected_text": "this: `backend/` except `backend/fixtures/` (new: pyproject, uv.lock, template.yaml, api/openapi.yaml, src skeleton with route stubs, contract tests, tools/check_template.py, providers/registry.json empty list)"},
    {"id": "IE-F02", "class": "dependency (read before write)", "slices": ["S04", "S05", "S09"], "compared": "S04 command CMD-GATE-ANDROID and S05 command CMD-GATE-BACKEND invoke `tools/ci/gate.sh`, which is in S09's write set; S09 waits on S09T, which waits on S01, S02, S06 merges; S04 and S05 have no edge to S09", "target": "slice-graph.md S04 and S05 rows, Commands and Stop condition", "corrected_text": "S04 Commands: `CMD-SCAN, CMD-ANDROID-BUILD`; Stop condition: `Starter and Android SDK scanned PASS; CMD-ANDROID-BUILD (cd tv-app && ./gradlew --no-daemon :app:lintDebug :app:testDebugUnitTest :app:assembleDebug) exit 0 (debug APK built); gate.sh android runs at IE-M1-6.` S05 Commands: `CMD-SCAN, CMD-BACKEND-CHECK`; Stop condition: `Contract tests and template check pass; CMD-BACKEND-CHECK (the three DES-AFC-GATE backend commands) exit 0; gate.sh backend runs on the IE-M1-6 PR.`"},
    {"id": "IE-F03", "class": "dependency (read before write)", "slices": ["S08", "S09"], "compared": "S08 command CMD-GATE-HYGIENE needs `tools/ci/gate.sh` and `tools/ci/check_paths.py` (S09 write set); S08 Depends on is empty", "target": "slice-graph.md S08 row Depends on; Dependencies list", "corrected_text": "S08 Depends on: `S09 (hygiene receipt only; authoring starts at dispatch)`; add edge `S09 --> S08`"},
    {"id": "IE-F04", "class": "dependency (read before write)", "slices": ["S25", "S26", "S27"], "compared": "S25 writes `tv-app/app/src/main/java/afc/companion/net/`; S26 (`settings/`, `link/`, `detect/`) and S27 (`panel/`, `player/`) call the API through `net/` and run concurrently with S25 in wave 3 with no edge", "target": "slice-graph.md S04 Stop condition and S25 Write set", "corrected_text": "S04 Stop condition append: `net/ApiClient.kt declares one Kotlin interface method per CONTRACT-AFC-API route with its request and response types.` S25 Write set: `this: tv-app/app/src/main/java/afc/companion/alerts/, tv-app/app/src/main/java/afc/companion/watch/, tv-app/app/src/main/java/afc/companion/net/ (implements the S04 ApiClient interface; signatures unchanged)`"},
    {"id": "IE-F05", "class": "write overlap (hidden hot files, SM F5)", "slices": ["S04", "S05", "S20", "S21", "S22", "S23", "S24", "S25", "S26", "S27", "S30", "S31"], "compared": "No feature write set lists `tv-app/app/build.gradle.kts`, `AndroidManifest.xml`, navigation, `backend/template.yaml`, `backend/pyproject.toml`, `backend/uv.lock`, `backend/src/afc_backend/store/`, the API router or `backend/tests/conftest.py`; S25 (foreground-service type, POST_NOTIFICATIONS, androidTest deps), S26/S31 (DataStore), S20 (Scheduler resource, HTTP and schema deps), S20..S24 (store accessors) need them while running concurrently. DES-AFC-TV names DataStore persistence but omits DataStore from its dependency list.", "target": "slice-graph.md S04 and S05 Stop conditions; design.md DES-AFC-TV dependencies bullet", "corrected_text": "S04 Stop condition append: `build.gradle.kts declares Jetpack Compose, Media3 ExoPlayer, OkHttp, kotlinx.serialization, AndroidX DataStore Preferences and test dependencies JUnit 4, kotlinx-coroutines-test, AndroidX Test runner, UI Automator; AndroidManifest.xml declares POST_NOTIFICATIONS, FOREGROUND_SERVICE, the AlertService foreground-service type and <queries> by intent (android.intent.action.MAIN + android.intent.category.LEANBACK_LAUNCHER); navigation routes every component stub.` S05 Stop condition append: `pyproject.toml and uv.lock hold every DES-AFC-* runtime and test dependency; store/ implements every CONTRACT-AFC-TABLES key accessor; template.yaml declares every route group, the FeedIngest schedule group, the ReplayMode parameter and the SSM parameter names.` design.md DES-AFC-TV: `Dependencies limited to: Jetpack Compose (starter), AndroidX Media3 ExoPlayer (Mode A only), OkHttp, kotlinx.serialization, AndroidX DataStore Preferences; test-only: JUnit 4, kotlinx-coroutines-test, AndroidX Test runner, UI Automator. Gradle wrapper checksum is verified at import.`"},
    {"id": "IE-F06", "class": "missing interface configuration", "slices": ["S04", "S25", "S40"], "compared": "No artifact defines how the APK learns the backend URL (searched design.md, technical plan, slice-graph.md, SM receipt for base URL, BuildConfig, ApiUrl); the TV-to-backend interface cannot be assembled", "target": "design.md DES-AFC-TV; slice-graph.md S04 Stop condition", "corrected_text": "design.md DES-AFC-TV add bullet: `The API base URL comes from Gradle property afcApiBaseUrl into buildConfigField(\"String\", \"AFC_API_BASE_URL\", ...); empty shows \"Backend not configured\"; the APK build passes -PafcApiBaseUrl=<afc-dev stack output ApiUrl>; it carries no secret.` S04 Stop condition append: `AFC_API_BASE_URL is read from Gradle property afcApiBaseUrl.`"},
    {"id": "IE-F07", "class": "shared resource (worktree index)", "slices": ["S20T..S24", "S25T..S27", "S07, S10, S06L"], "compared": "DES-AFC-LANES gives one worktree per lane, but up to five backend slices (wave 3), S26x and S27x, and S07/S10/S06L run concurrently in one lane; disjoint write sets do not protect a shared index, staging area or the working tree that gate.sh --changed reads", "target": "design.md DES-AFC-LANES Worktrees bullet", "corrected_text": "- Worktrees: one per running slice or TDD pair, `worktrees/amazon-fantasy-companion-<lane>-<slice>` on branch `afc/<lane>-m<n>-<slice>` cut from the lane branch `afc/<lane>-m<n>`; the lane integration worktree `worktrees/amazon-fantasy-companion-<lane>-m<n>` merges completed slice branches with `git merge --no-ff`; `worktrees/Alphazedehq-ci-cd-<topic>` and `worktrees/Alphazedehq-spec-authoring` unchanged; never hidden directories."},
    {"id": "IE-F08", "class": "dependency (gate contract vs tdd red phase)", "slices": ["S20T", "S21T", "S22T", "S23T", "S24T", "S25T", "S26T", "S27T", "S30T", "S31T", "S32T"], "compared": "After S09 (`.githooks/pre-commit` runs `gate.sh --changed`) and S11 (harness hook runs the gate and catches `--no-verify`, CONTRACT-AFC-HOOK), a commit of failing tests under `backend/tests/**` or `tv-app/app/src/test/**` triggers the backend or android area and is blocked; no artifact defines how red tests are committed", "target": "design.md DES-AFC-LANES Development strategy bullet", "corrected_text": "- Development strategy: `tdd` lanes split each feature into a Test Implementer slice (red, `<id>T`) and a Product Implementer slice (green). The red slice ends with the CMD-RED receipt (failing output plus sha256 of each test file) taken in the shared TDD-pair worktree and leaves the tests uncommitted; the green slice continues in that worktree and, when green, commits the tests first with the Test Implementer's author identity and then the product code with its own; the gate runs on each commit; `--no-verify` is never used. Scaffold and spike slices are single Product Implementer slices (OD-AFC-04); `spec-and-docs` is `single_implementer`."},
    {"id": "IE-F09", "class": "missing evidence", "slices": ["S09T", "S09"], "compared": "S09T writes `tools/ci/tests/`; DES-AFC-GATE area paths are `tv-app/**`, `backend/**`, `spec/**` + `tools/spec/**`, and hygiene (always), and hygiene runs only check_paths and the workflow checker, so no gate area, hook or Actions job runs the gate's own tests", "target": "design.md DES-AFC-GATE hygiene bullet", "corrected_text": "- `hygiene`: `python3 tools/ci/check_paths.py` over all tracked files (AC-AFC-CI-03, AC-AFC-PATH-01), the D4-B workflow checker over `.github/workflows/`, and the gate's own tests in `tools/ci/tests/` (always runs; the checker is vendored into `tools/ci/` by S09 from the merged D4-B commit because the shared skill is private)."},
    {"id": "IE-F10", "class": "configuration identity", "slices": ["S09"], "compared": "S09 vendors the D4-B checker (and gate.sh from the D4-A template) into `tools/ci/`, but its write set has no file recording the source commits, unlike S19's `tools/spec/VENDORED.md`", "target": "slice-graph.md S09 row Write set", "corrected_text": "this: `tools/ci/gate.sh`, `tools/ci/check_paths.py`, `tools/ci/check_workflows.py`, `tools/ci/VENDORED.md` (source repository and the D4-A and D4-B merge commits), `.githooks/pre-commit`, `.githooks/pre-push`, `.github/workflows/ci.yml`"},
    {"id": "IE-F11", "class": "dependency (schedule)", "slices": ["S16", "S20T"], "compared": "M2 due 2026-10-15T23:00:00Z precedes the Thu 10-15 game (about 2026-10-16T00:15Z), so S16's stop condition and the M2 exit fixture criterion cannot be met by M2 due; S20T (M3 critical path) waits for S16 completion about 2026-10-16T04:00Z", "target": "technical plan Milestones M2 Due; slice-graph.md S20T Depends on and Dependencies list", "corrected_text": "Technical plan M2 Due: `2026-10-16T06:00:00Z`. slice-graph.md S20T Depends on: `S05, S16 first capture (2026-10-12 fixtures committed)`; Dependencies list: replace `S16 --> S20T` with `S16 (2026-10-12 capture) --> S20T`."},
    {"id": "IE-F12", "class": "milestone inconsistency", "slices": ["S16"], "compared": "slice-graph.md S16 Milestone M2 and stop condition (10-12 and 10-15 fixtures) vs technical plan M1 slice list containing S16 and M1 exit `first ESPN fixtures recorded`", "target": "technical plan Milestones table M1 row", "corrected_text": "M1 Slices: `S01, S02, S03, S04, S05, S06, S06L, S07, S08, S09T, S09, S10`; M1 Exit criterion: replace `first ESPN fixtures recorded` with `S16 2026-10-12 capture committed on its slice branch`; M2 Slices: `S11T, S11, S12, S13, S14, S15, S16, S18, S19`."},
    {"id": "IE-F13", "class": "milestone inconsistency", "slices": ["S41"], "compared": "slice-graph.md S41 Milestone M1 and Wave 4 vs technical plan M4 slice list `S41 (conditional)`; its dependencies (OD-AFC-01 = B; S01..S03 merged) equal S11T's", "target": "slice-graph.md S41 row and Waves; technical plan M2 and M4 rows", "corrected_text": "slice-graph.md S41 Milestone: `M2`; Wave 2: `S11T S11 S12 S13 S14 S15 S18 S19 S41`; Wave 4: `S30T S30 S31T S31 S32T S32 S33 S34 S35`. Technical plan M2 Slices append `S41 (conditional)`; M4 Slices remove `S41 (conditional)`."},
    {"id": "IE-F14", "class": "dependency (missing edge)", "slices": ["S17", "S28", "S35"], "compared": "M3 entry criterion `T_yahoo outcome applied` and the S28 live test need the S17 lineup-source verdict; S35 needs S12..S17 verdicts; the Dependencies list has no S17 edge to either", "target": "slice-graph.md S28 Depends on; Dependencies list", "corrected_text": "S28 Depends on: `S17; M3 assembly complete (IE steps)`; Dependencies list add `S17 --> S28` (also covers S35 through `S28 --> S35`)."},
    {"id": "IE-F15", "class": "dependency (missing edge)", "slices": ["S09", "S11"], "compared": "S11's AC-AFC-D4-04 demonstration and CMD-HOOK-INSTALL --verify need a repository with `tools/ci/gate.sh` (S09 write set); S11 depends only on S11T", "target": "slice-graph.md S11 Depends on; Dependencies list", "corrected_text": "S11 Depends on: `S11T, S09 merged`; Dependencies list add `S09 --> S11`."},
    {"id": "IE-F16", "class": "shared resource (live skill checkout)", "slices": ["S01", "S02", "S03", "S06", "S06L", "S11", "S41"], "compared": "Harness skill links resolve to the Alphazedehq main checkout (`readlink` of the Claude Code `setup-pre-commit` link shows `<workspace>/Alphazedehq/skills/setup-pre-commit`); merged skill changes go live for every agent only when that checkout fast-forwards, and it currently has 1 uncommitted entry; the resource list omits it", "target": "technical plan Program plan shared resources sentence; slice-graph.md S06L Depends on", "corrected_text": "Technical plan: add `the Alphazedehq main checkout that every harness skill link resolves to (alphazedehq-main-checkout lease; fast-forward only, between dispatches, HEAD recorded in each later packet)` to the shared mutable resources. slice-graph.md S06L Depends on: `S06 merged; alphazedehq-main-checkout at or after the S06 merge commit`."},
    {"id": "IE-F17", "class": "write overlap (unowned file)", "slices": ["S27", "S38"], "compared": "S27 fetches footage into git-ignored `tv-app/app/src/main/assets/footage/` and S38 stores clips in git-ignored `submission-media/` (design.md), but no write set includes an ignore file", "target": "slice-graph.md S04 Stop condition and S38 Write set", "corrected_text": "S04 Stop condition append: `tv-app/.gitignore ignores app/src/main/assets/footage/.` S38 Write set: `this: docs/submission/clips/README.md, .gitignore (adds submission-media/ only)`."},
    {"id": "IE-F18", "class": "write set mismatch", "slices": ["S01"], "compared": "design.md DES-AFC-D4 D4-A lists `skills/setup-pre-commit/agents/openai.yaml`; slice-graph.md S01 Write set omits it (the directory today holds only SKILL.md)", "target": "slice-graph.md S01 Write set", "corrected_text": "Alphazedehq: `skills/setup-pre-commit/SKILL.md`, `skills/setup-pre-commit/agents/openai.yaml`, `skills/setup-pre-commit/references/gate-contract.md`, `skills/setup-pre-commit/templates/gate.sh`, `skills/setup-pre-commit/scripts/install-hooks.sh`, `skills/setup-pre-commit/tests/test-install-hooks.sh`"}
  ]
}
```

## Proposed command IDs (for the Planning Test Engineer)

| ID | Purpose |
|---|---|
| CMD-ANDROID-BUILD | DES-AFC-GATE android commands run directly (before `gate.sh` exists) |
| CMD-BACKEND-CHECK | DES-AFC-GATE backend commands run directly |
| CMD-MERGE-IDENTITY | `gh pr view --json mergeCommit,mergedAt` plus `git rev-parse`; records the merge SHA |
| CMD-AZHQ-SYNC | Fast-forward-only update of the AZHQ main checkout; fails closed on conflict; records HEAD |
| CMD-CI-VENDOR-PIN | `tools/ci/VENDORED.md` commits equal `azhq.d4a`/`azhq.d4b`, and vendored files equal those trees |
| CMD-CONTRACT-FROZEN | sha256 of the frozen contract files equals the IE-M1-6 baseline, except for routed deltas |
| CMD-HOOK-DEMO | A deliberate hygiene failure is blocked under each wired harness |
| CMD-HOOK-RESTORE | The installer restores harness configurations from timestamped backups |
| CMD-SPIKE-VERDICTS | Each verdict file has route, steps, evidence paths, verdict and limits |
| CMD-REGISTRY-CHECK | Registry entries ⊆ SP-3 verified forms; sha256 recorded |
| CMD-TEMPLATE-DIGEST | sha256 of the deployed `backend/template.yaml` equals the one in the source commit; stack outputs |
| CMD-SAM-ROLLBACK | Redeploys a recorded SHA to `afc-dev` |
| CMD-APK-SHA | sha256 of the built APK |
| CMD-E2E-REPLAY | On-stick replay rehearsal: heads-up over playback, Watch outcome, panel in mode, labels |
| CMD-STUB-SCAN | No `AFC-STUB` marker under `tv-app/app/src/main/` or `backend/src/` |
| CMD-TREE-EQUAL | `git diff --exit-code <a> <b> -- tv-app backend` |
| CMD-REVERIFY | Reverify on the final APK |

## Remaining risks

- **S16 and the agent cap.** S16 occupies one cap slot from 10-12 to 10-16 if its session stays open. The Orchestrator should close it after the 10-12 capture and continue it for 10-15. Otherwise wave 2 already runs at five, counting S16, S11x, the stick chain, S18 and S19.
- **AZHQ CI coverage.** AZHQ CI (`coe-gates.yml`) does not run the new D4/D5 tests: its skills path group covers only `skills/visual-review/**`, and its hooks group runs named suites only. Their evidence is the post-step reruns on each merge commit, not AZHQ required checks.
- **Release signing.** If `CMD-APK-RELEASE` needs a release keystore, creating one is credential work for the owner. Without that, S40 records a debug-signed sideload APK.
- **Same model routes.** For the primary and heavyweight profiles, the IE execution route is the same model as the implementer route. A fresh session satisfies "rejects author ancestry", but the independence comes from the session, not the model.
- **Live-window times** are slot assumptions until the ESPN scoreboard confirms them.

## Typed outcome

- **outcome:** GAPS
- **verdict:** The integration plan is complete, with 26 steps, every contract checked, cut-offs and owner dependencies. Dispatch of S04, S05, S08, S09, S11, S16/S20T, S25..S27 and the TDD red slices must wait for the corrections in IE-F01..IE-F18. No owner decision is required.
- **candidate_ref:** none (planning session). The final candidate is defined as `this.final`.
- **changed_paths:** `docs/plans/2026-10-11-amazon-fantasy-companion/specialists/integration-plan.md`
- **blocker:** none for the owner. The Plan Integrator / Planning and Design must apply the corrected text before dispatch.

## developer_feedback

- **IE-DX-01.** The `integration_engineer` execution session in the frozen `tech-writing` snapshot has no `cadence` field, while primary, frontend, heavyweight and bug-triager declare `lifecycle`.
  Evidence: `journey.json` `profile_selection.frozen_snapshots.tech-writing.snapshot.roles.integration_engineer`. The skill default (`lifecycle`) was applied.
- **IE-DX-02.** In `slice-graph.md`, the owner-action table rows (`| S12 |`, `| S14 |`, `| S18 |`) share the slice-row prefix. A mechanical parser picks them up as slice rows; this plan's overlap check had to skip them by column count.
  The Plan Integrator's mechanical copy should key on column count or section.
- **Tools exercised:** Bash (`cat`, `sed`, `grep`, `ls`, `wc`, `readlink`), `git -C` read-only on Alphazedehq, `python3` (journey extraction, pairwise write-set overlap check), and the `integration-engineer` and `integration-engineering` skills.
  BRAN reported `unavailable` (no policy here), so normal discovery was used.
