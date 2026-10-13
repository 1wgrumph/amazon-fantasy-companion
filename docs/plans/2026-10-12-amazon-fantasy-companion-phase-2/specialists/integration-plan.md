---
type: planning-input
title: Phase 2 integration plan (Integration Engineer planning session)
okf_status: draft
tags: [planning, afc, phase-2, integration]
---

# Phase 2 integration plan — AFC-2026-10-11

Author: Integration Engineer, planning session (`BEARING_ROLE=integration_engineer`,
frozen primary planning first fallback: Codex CLI / GPT-6.1 Sol / xhigh).
This is continuation/correction **2** on 2026-10-13, after initial IE findings
were applied as correction 1; no planning, review or repair budget resets.
Confirmed Claude weekly-limit evidence: `evidence/ie-p2-codex/route-evidence.json`.
DEC-AFC-SD-039 makes the parent Codex session the Planning and Design lead.
Skills: bearing-lite `integration-engineer` 1.1.6 and the `integration-engineering`
method skill. Method reference: ISO/IEC/IEEE 24748-6 (metadata only, S8
SRC-EMV-24748-6) and NASA Systems Engineering Handbook Appendix H (named, not
copied).

This plan covers assembly strategy only. It is author planning work, not
independent review or assurance. SEIT commands, proof methods and criteria remain
owned by TE; none was edited or rerun. Historical `concurrency_findings` and the
initial receipt remain correction-1 evidence, not a new dispatch hold list.
Current source bytes and lineage are in `evidence/ie-p2-codex/input-provenance.json`.
BRAN is unavailable (no native policy); direct repository discovery was used.

**Chronology and profile delta (DEC-AFC-SD-040/041, 2026-10-13).** Author:
Integration Engineer planning session on the frozen `opensource-hackathon`
route `integration_engineer.planning` (Claude Code / Claude Opus 5.5 / high), Bearing
Lite 1.1.7 skills. Projection only, applied by
`evidence/chronology-profile-delta/ie-apply.py`. Step and slice `milestone`
values now name the 13 chronological GitHub milestones M01..M13 from
`evidence/chronology-opus-review/proposal.json` (`integration_step_milestone`
and issue groups); each step also carries its unchanged technical `wave`.
Technical waves and release checkpoints W1..W5 (formerly M1..M5) keep their
dates, membership, gate costs, cut-off IDs CO-M1..CO-M5 (stable identifiers
that name wave exits) and the identity names `apk.m<n>` / `release.m<n>`
(n = wave). No step ID, order, `after` list, merge set, lease, write set or
dependency condition changed. Historical `concurrency_findings` keep their
original Mn tokens, which mean wave exits Wn. Lane bindings are replaced by
the frozen `opensource-hackathon` snapshot; `bug-triager` is unchanged. This
is author planning work, not review or assurance.

## Inputs and evidence read (original inspection plus correction-2 source binding)

| Input | Identity |
|---|---|
| Plan branch | `plan/2026-10-12-afc-phase-2` at `771c28958f78e611048528aedbd9ed4490f308e1` plus working-tree changes (technical plan, design, slice graph, register, models) |
| `origin/main` | `17b40b4bdf8214b300bee05d594e13100d5d0d93` (fetched 2026-10-12). **S09 has landed**: `tools/ci/gate.sh` (areas `spec docs hygiene`), `.githooks/pre-commit` (`gate.sh --changed`), `.github/workflows/ci.yml` (jobs `gate / spec`, `gate / docs`, `gate / hygiene`), `tools/ci/VENDORED.md`. `core.hooksPath=.githooks` is set. Original inspection had no `CHANGELOG.md`; current lead sources record PR #14 created it. Preserve it at planning landing. |
| Current Phase 1 entry source | Technical-plan Entry criteria: land PR #10 with ST5-F1/F2; S42 content already landed as d259c169; PR #11 is redundant, not another prerequisite. No remote state was refreshed in this delta. |
| Repository settings | private; rulesets and branch protection API return HTTP 403 "Upgrade to GitHub Pro or make this repository public"; `allow_squash_merge=true`; `delete_branch_on_merge=false`; no milestones exist |
| Development host | `python3` = 3.14.4; `python3.12` = 3.12.3; Original host inspection had JDK 21 and Docker; `adb`, `sdkmanager`, `sam`, `cfn-lint` absent (X01 qualifies JDK17/Android/build-tools before A01T; B01T prepares scanned Python deps, B01 owns SAM/cfn-lint acquisition) |
| Frozen profiles | Phase 1 journey `profile_selection.frozen_snapshots` (DEC-AFC-SD-041): `opensource-hackathon` for all implementation lanes and the Scribe (full profile sha256 `7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1`, configuration digest `11c4478edb7b0c94da196cdc8be2317f498378724ae041bde0c108832b1e2036`); `bug-triager` for defects (`6ca3ffccea9bae0e26f960b075e7a7fe2ffc01048474f1c8a70c31d8e748138b`, unchanged). The superseded primary/frontend/heavyweight/tech-writing lane snapshots are historical (`evidence/profile-migration-041/prior-profile-selection.json`). |
| Phase 1 IE findings | `f885e48:…/specialists/integration-plan.md` IE-F01..IE-F18. How each carries into Phase 2 is shown in the table at the end of this file. |

## Assembly model

- **One repository, trunk integration.** Each slice, or TDD pair, works in its
  own worktree `$HOME/alphazede/worktrees/amazon-fantasy-companion-<lane>-<slice>`
  on branch `afc/p2-<slice-lowercase>`, cut from `main` once its entry criteria
  hold. It lands on `main` through its own pull request. Integration steps
  `IE-P2-<k>` are the ordered landings, deployments, installs and rehearsals,
  each with entry criteria, post-step V&V and rollback.
- **TDD pairs.** The `<id>T` red and green slices share one worktree and one
  PR (DES-AFC-P2-LANES). `merges` lists both for scope accounting; it does not
  mean a red-only PR. Green waits for verified CMD-RED behavioral assertions
  with frozen tests/bootstrap hashes in that worktree. Only empty build/test/
  interface scaffolding is allowed before red; tool/import/collection failures
  are preparation gaps. Product-to-product and landed spike dependencies remain
  merge dependencies. A01T waits for X01 host preparation. Cross-test shared
  fixture handoffs B04T→B05T and A03T→A04T consume verified red receipts, not merges.
- **Two-PR spikes.** X03/X05 retain one logical slice/issue each and two PR
  landings; after PR 1 cleanup, PR 2 gets a new visible worktree from current main.
- **Landing control.** `main-landing` is the only merge lease: one merge at a
  time, and the CHANGELOG entry is added under it. Before every merge the lander
  runs CMD-PR-CHECKS. The repository is private on GitHub Free,
  so no ruleset enforces PR-only merges, required checks or the no-squash rule
  (IE-P2-F22). Merges use `gh pr merge --rebase` or `--merge`, and the remote
  branch is deleted after merge.
- **Contract freeze.** Merging P2-B01 records the digests of `openapi.yaml`,
  `template.yaml`, `store/`, `pipeline/` and `presets.py`, and CMD-CONTRACT-FROZEN
  guards them. Merging P2-X03 records the registry digest; merging
  P2-X05 records the fixture-index digests. A later change to a frozen artifact
  needs the `backend-template` lease and is declared in its PR body.
- **Single build host for stick APKs.** Every APK installed on the stick is
  built on the one development host, so the debug signing key never changes.
  Updates use `adb install -r` and keep app data and the device session. CI
  artifacts are never installed on the stick.

### Finalized command references (TE owns definitions)

All command IDs in the JSON resolve to `seit.json/procedures_and_commands`.
Use those exact definitions and pass/fail/gap rules; old IE proposals are superseded.
Build paths are `./tv-app/gradlew -p tv-app assembleDebug` and
`./tv-app/gradlew -p tv-app assembleRelease`, with `-PafcApiBaseUrl=<ApiUrl>`.
CMD-JUDGE-ACCESS checks B01 OpenAPI authentication/polling, not assumed anonymous
GET success. CMD-REVERIFY-APK keeps the frozen backend and exact APK hash;
unproven semantics remains REVERIFY_CAPABILITY_GAP with no ordinary ATE substitute.
Inspection of a main-built final APK may precede tag; tagged-main/publication
stays OWNER_EVIDENCE_PENDING until OA-8 and tag readback.

P2-L01 uses the technical-plan GitHub work organization procedure after
integrated approval **and** plan landing. Derive 39 issue groups from 52 slices
(13 TDD pairs share an issue), retain the conditional issue, and create approved
M01..M13 with exact table due dates (UTC times in descriptions). Duplicate-search/reuse comes before policy-tool
dry-run and submission. Saved labels, body, milestone, dependencies and URLs
are read back; every slice maps exactly once. The configured filing entrypoint is
`python3 "$HOME/alphazede/Alphazedehq/hooks/issue-labels.py" file --repo
1wgrumph/amazon-fantasy-companion --kind <enhancement-or-documentation> --title
<approved-title> --body-file <approved-body>`; run without `--submit` first,
then with it only under recorded integrated approval. No remote action runs here.

## Configuration identity

Every step receipt records the identities below in `journey.json`
`execution_receipts`, and later steps consume them by name.

- `p2.base`: the `main` merge commit of the planning PR (IE-P2-1).
- `merge.<slice>`: each slice's merge commit on `main`, plus its PR number.
- `device`: from P2-X01 VERDICT front matter — stick model, Fire OS version,
  API level and `first_install_at` (UTC). It also records the starter
  repository and pinned commit, the Android SDK platform/build-tools versions,
  and the scan receipt IDs.
- `contracts.b01`: CMD-CONTRACT-DIGEST at `merge.P2-B01`. Consumed by
  B02..B07, A01..A05 and both deploy steps.
- `registry.v1` / `registry.v2`: sha256 of `registry.json` at the merge of
  P2-X03 PR 1 and PR 2.
- `fixtures.v1` / `fixtures.v2`: sha256 of every `index.json` at the merge of
  P2-X05 PR 1 and PR 2.
- `panel_mode`: `PanelMode.modeB` or `PanelMode.fullScreen`, from the P2-X04
  verdict. `notify_route`: from P2-X02. `detect_support`: from P2-X07.
  `lineup_source`: from P2-X06.
- `deploy.<n>`: stack name `afc-dev`, CLI profile `afc-dev`, region name (read
  from the profile configuration; no credential), deployed commit (tag
  `GitCommit`), template sha256, `ApiUrl` output, and smoke/test receipt. Also
  `deploy.last_green`.
- `apk.m<n>`: build commit (the P2-R<n> merge), sha256, signer certificate
  SHA-256, JDK/AGP/Gradle versions, and the `-PafcApiBaseUrl` value used.
  `apk.last_green` is the APK last installed on the stick that passed its step.
- `release.m<n>`: tag name, target commit, and draft release URL.
- `candidate.final`: see `final_candidate`.
- `toolchain`: AZHQ skill checkout HEAD at dispatch (skill paths resolve there,
  Phase 1 IE-F16); `tools/ci/VENDORED.md` and `tools/spec/VENDORED.md` pins.

## Stubs and glue

- **Authorized glue: none.** No adapter, fake server, simulator or shim may
  connect two realized elements. If an interface does not connect, it is a
  defect routed to bug-triager or a typed gap.
- **Product stubs (B01, A01).** B01T/A01T may prepare only the bounded empty
  interface/build/test harness described in DES-AFC-P2-LANES before valid red.
  No tested feature behavior is allowed in that preparation. Each stub carries the final signature and the
  marker `AFC-STUB`. Backend stubs raise `NotImplementedError`, which the router
  maps to 503 `not_implemented`. TV stubs render an "unavailable" placeholder.
  CMD-STUB-SCAN must be empty before the Wave 3 rehearsal (IE-P2-29, M10) and at the
  final candidate.

## Concurrency and assembly readiness — correction 2 (author check)

Source: current graph plus design DES-AFC-P2-LANES/Planning completion controls;
SEIT `planning_findings_for_plan_integrator` F01/F02/F06/F07/F09 and `levels`.
The before artifact and unchanged historical findings preserve correction 1.
This is no independent concurrency review or hardware feasibility proof.

- B01T owns deployed `conftest.py`, `device_auth/` and `api/`; B02T..B07T
  own disjoint deployed `feed_ingest/`, `lineup/`, `matcher/`, `alert_policy/`,
  `provider_resolver/`, `panel/`. Shared conftest/dependency changes serialize
  under backend-template. A02T owns instrumented `profile/` and `detect/`;
  all instrumented T slices and green/review runs hold fire-tv-stick.
- A01T bootstrap manifest/Gradle paths use tv-app-manifest/tv-app-gradle;
  B01T bootstrap/shared conftest uses backend-template. Bootstrap ownership
  transfers inside the pair after frozen red evidence; no concurrent writers.
- First five ready implementation packets: X01, X05, B01T, D01, G01T.
  A01T queues until X01 qualifies host tools. Pair green starts only after its
  verified red receipt; G01 product lands before A01/B01 product landings.
- B04T's verified red/shared-fixture handoff precedes B05T; B04 product still
  precedes B05 product. Every other product dependency remains landed.
- Stick priority remains X01→X04 uninterrupted until verdict or first install
  +24h→A01 review→X02→X03 desk→X07; X03 live TNF then applicable instrumented
  qualification/reviews, rehearsal, X09/X10, selected X11, final APK and X12.
  X05 host-only TNF capture shares live-game-window with disjoint stick users.
- D02 waits for X01..X07 final verdicts plus selected X11 terminal disposition;
  it records every landed verdict through freeze. IE-P2-34 waits on IE-P2-35:
  Stable IDs remain; only their assembly order swaps. Later verdicts
  receive a bounded D02 delta before W4 exit, never an omitted topic.

The technical plan's schedule baseline is 2026-10-13T04:00:00Z (10d15h to
T_deadline). October 12 is removed from remaining live opportunities. Host-only
earlier captures stay historical/replay. Remaining windows: October 15 TNF,
October 18 Sunday, October 19 MNF, October 22 TNF; kickoff is rechecked at capture.
The five wave release-checkpoint dates (W1..W5) are unchanged; the 13 GitHub
milestone due times reuse existing cut-offs only. CO-STICK-START remains a planning
forecast at 2026-10-14T03:15Z; qualification adds pressure and its real duration
is unmeasured. Missed forecasts never authorize provider omissions or earlier-APK
clips as final proof. Exact omitted topics/claims and consequences need an owner
scope decision with evidence; no new owner question is posed by this delta.

### Wave resources and incremental gate estimates

`wave_gate_costs` below carries SEIT `levels.expected_gate_time_delta`, exact
case resource declarations, normalized actual host/device/deployment groups,
and integer `added_gate_seconds`: W1 720, W2 900, W3 2100, W4 0, W5 120.
These are additive planning budgets, not hardware benchmarks or wall-clock
predictions. W4 has no fixed gate increase; changed-suite requalification and
estimated replay ≤300s are separate. W5's 120s docs forecast excludes unmeasured
final binary/deployed/independent assessment work. Suites with disjoint actual
resources may run concurrently; a system suite needing both stick and AWS
competes for both, in the SEIT lease order.

Apply existing PROC-PREPARE and PROC-RELIABILITY: a new/changed engine/server/
driver/browser suite needs **5 consecutive passes + one two-concurrent-copy
run**. Copies launch together with unique owned roots; the named cross-process
fire-tv-stick lock serializes the whole instrumented run on the one stick.
No extra device or simulator substitutes. Owned state/cleanup, bounded readiness,
fresh fault state, exact candidate/input hashes and slowest-test/cost evidence
come from SEIT. Ordinary qualified gate reuse for review/landing on unchanged
candidate/inputs is separate; no routine seven-execution rerun is added.
Changed suites/inputs invalidate reuse; evidence-only unchanged-tree merges
reuse qualified runtime evidence while retaining required source gates.

## Steps, cut-offs and the final candidate

The step list is in the JSON block. Steps are grouped by technical wave;
`milestone` is the GitHub milestone (M01..M13) and `wave` the technical wave.
Release prerequisites for P2-R1..R4 come from wave membership, never from the
13 GitHub milestone groups. Summary:

- **Wave 1 / W1** (release checkpoint due 2026-10-14T23:00Z): IE-P2-1..8 (M01 1, 2, 3; M02 4, 5; M04 6; M03 7, 8). Package baseline, gate areas,
  device baseline, backend skeleton with frozen contracts, first fixtures, TV
  scaffold, release v0.1.0 draft.
- **Wave 2 / W2** (release checkpoint due 2026-10-17T01:00Z): IE-P2-9..20 (M03 9; M04 10, 11, 12; M05 13, 14, 15; M04 16, 17; M06 18, 19, 20). Spike
  verdicts, ingest, lineup, first deploy, profile UI, TNF amendments, Yahoo or
  manual verdict, v0.2.0.
- **Wave 3 / W3** (release checkpoint due 2026-10-19T12:00Z): IE-P2-21..31 (M07 21, 22; M08 23; M07 24; M09 25; M08 26, 27; M09 28; M10 29, 30, 31). Matcher,
  policy, resolver, panel service, Wave 3 deploy, alerts, Watch and panel UI,
  rehearsal, Sunday live run, v0.3.0.
- **Wave 4 / W4** (release checkpoint due 2026-10-21T23:00Z): IE-P2-32..36 (M11 32, 33, 35, 34, 36). Sunday defects, MNF hardening,
  D1 revision, Alexa stretch, v0.4.0.
- **Wave 5 / W5** (release checkpoint due 2026-10-23T12:00Z): IE-P2-37..44 (M12 37, 38; M13 39, 40, 41, 42, 43, 44). Submission docs, Scribe
  assembly, visibility flip, final deploy, v1.0.0 candidate, final APK with
  Reverify, demo capture on the final APK, Lifecycle-end assessments.

CP-X05-HIST: IE-P2-6 (X05 PR 1) belongs to the M04 issue but executes during
M02/M03 and feeds IE-P2-8 (R1, M03) and IE-P2-13 (B02, M05). CP-X03-REG:
IE-P2-11 (X03 PR 1) feeds IE-P2-12 (X07) and IE-P2-23/27 (B06, A04). Wave 2
entry is per lane: X01 merged for X04, B01 merged for backend Wave 2 slices,
A01 merged for A02; X04 never waits for R1. X04 → A01 review → R1 sits in M03
(schedule risk W-1; no date moved). IE-P2-35 still precedes IE-P2-34 in M11.

## Phase 1 IE findings carried into Phase 2

| Phase 1 | Phase 2 status |
|---|---|
| IE-F01 fixtures × backend overlap | Recurs → IE-P2-F01, F02 |
| IE-F02/F03/F09/F10/F15 gate ordering, vendoring | Closed: S09 landed with `VENDORED.md`; hygiene runs `tools/ci/tests` |
| IE-F04 net interface | Recurs → IE-P2-F10 (ApiClient for every operation, DTOs, WatchLauncher stub) |
| IE-F05 hidden hot files | Partly closed: design gives A01/B01 complete manifest, Gradle and template. Recurs for write sets, requirements, store, pipeline, conftest → F10, F12 |
| IE-F06 API base URL | Recurs → IE-P2-F11 |
| IE-F07 worktree per slice | Closed (DES-AFC-P2-LANES) |
| IE-F08 red-test commit handling | Closed (DES-AFC-P2-LANES) |
| IE-F11/F12 fixture schedule | Recurs → IE-P2-F03 |
| IE-F13/F18 S41, S01 | Not applicable to Phase 2 |
| IE-F14 Yahoo verdict edge | Recurs in a new form → IE-P2-F04 (X06 feeds L03, not B03) |
| IE-F16 AZHQ skill checkout | Carried as `toolchain` identity (read-only dependency) |
| IE-F17 ignore files | Recurs → IE-P2-F24 |

## integration_plan

```json integration_plan
{
  "branches": [
    {
      "name": "main",
      "role": "trunk; PR-only by procedure (private repo: no ruleset, IE-P2-F22); merges by rebase or merge commit only",
      "consumed_as": "merge.<slice>"
    },
    {
      "name": "plan/2026-10-12-afc-phase-2",
      "role": "planning package",
      "base": "771c28958f78e611048528aedbd9ed4490f308e1 (equals PR #10 head)",
      "merge": "after PR #10 (ST5-F1/F2) lands and origin/main is merged into the planning branch; preserve existing CHANGELOG and add linked planning entry",
      "consumed_as": "p2.base"
    },
    {
      "name": "afc/st4-spec",
      "role": "Phase 1 PR #10 (D1 spec, ST5-F1/F2)",
      "merge": "before the planning PR",
      "consumed_as": "phase1.pr10"
    },
    {
      "name": "afc/s42-revendor-prose",
      "role": "historical PR #11 record; S42 tools/spec content already landed as d259c169 per current technical-plan Entry criteria",
      "merge": "not an additional prerequisite",
      "consumed_as": "tools/spec/VENDORED.md pin at p2.base"
    },
    {
      "name": "afc/p2-<slice-lowercase>",
      "role": "one per running slice or TDD pair (pair uses the product slice ID, e.g. afc/p2-b01 for P2-B01T+P2-B01)",
      "base": "origin/main at dispatch, after the slice's landing predecessors merged",
      "merge": "own PR to main under main-landing; remote branch deleted after merge",
      "consumed_as": "merge.<slice>"
    },
    {
      "name": "afc/p2-x03 and afc/p2-x05",
      "role": "two-PR spikes; recreate a visible worktree/branch from then-current main for PR 2 after PR 1 cleanup; keep one logical slice/issue identity",
      "consumed_as": "merge.P2-X03.pr1/pr2, merge.P2-X05.pr1/pr2"
    },
    {
      "name": "afc/bug-<issue>",
      "role": "bug-triager fix per defect (AC-AFC-P2-BUG-01); write set = triage-named files, dispatched only when disjoint from running slices",
      "consumed_as": "merge.bug-<issue>"
    }
  ],
  "worktrees": [
    {
      "path": "$HOME/alphazede/worktrees/amazon-fantasy-companion-phase2-plan",
      "use": "existing planning continuation; IE writes only its three authorized output areas"
    },
    {
      "path": "$HOME/alphazede/worktrees/amazon-fantasy-companion-<lane>-<slice>",
      "use": "one per running slice or TDD pair; test/product sessions take turns in the shared pair worktree; remove worktree and local/remote branch after each merged PR"
    },
    {
      "path": "$HOME/alphazede/worktrees/amazon-fantasy-companion-integration",
      "use": "IE execution session and post-step V&V on clean checkouts of merge commits (detached HEAD at the recorded SHA); APK builds for the stick happen only here or in the slice worktree on the same host"
    },
    {
      "path": "$HOME/alphazede/worktrees/amazon-fantasy-companion-bug-<issue>",
      "use": "bug-triager fix per defect"
    }
  ],
  "steps": [
    {"id": "IE-P2-1", "milestone": "M01", "wave": "Wave 1", "milestone_note": "entry", "order": 1, "merges": [], "after": [],
     "entry_criteria": ["Owner approved the Phase 2 package at the integrated review (DEC-AFC-SD-023 P2-6)", "PR #10 with ST5-F1/F2 landed; S42 tools/spec content already landed as d259c169 per current technical-plan Entry criteria; PR #11 is not an additional prerequisite; origin/main merged into planning branch", "Sanitized tracked planning artifacts and evidence; raw agent logs remain local; CMD-GATE-HYGIENE exit 0", "Preserve existing CHANGELOG.md and add the planning PR's linked [Unreleased] entry; seed only if absent (AC-AFC-P2-REL-01)", "CMD-PR-CHECKS pass; merge by --merge or --rebase"],
     "post_step_vv": ["CMD-MAIN-GATE on the merge commit", "record p2.base"],
     "rollback": "revert PR (no force-push); Phase 2 dispatch waits",
     "exit": "p2.base recorded; every Phase 2 branch cuts from it or later"},
    {"id": "IE-P2-2", "milestone": "M01", "wave": "Wave 1", "order": 2, "merges": ["P2-L01", "P2-D01"], "after": ["IE-P2-1"],
     "entry_criteria": ["P2-L01 after integrated approval AND p2.base landing: approved M01..M13 plus derived work issues; one issue per logical deliverable, TDD pair shares one, all 52 slices exactly once in 39 groups; conditional X11 stays labeled conditional; reuse matching identities; policy-tool dry-run then submit; saved labels/body/milestone/dependency/URL readback and slice-to-issue map; CMD-MILESTONES-CREATE and CMD-MILESTONES-READBACK match approved table (day precision; UTC due time in description)", "P2-D01: CMD-GATE-DOCS exit 0; three Vnv areas with Scope, Tools, Review Focus, Findings target headings", "one Reviewer review each (OCR delegate; Reverify: not applicable — no binary)"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-MILESTONES-READBACK re-run on main merge", "Use technical-plan GitHub work organization/P2-L01 readback and SEIT existing proof rows; no issue/milestone created in this planning session"],
     "rollback": "revert PR; milestones edited by gh api to the approved table (no deletion without owner)",
     "exit": "AC-AFC-P2-MS-01, AC-AFC-P2-VNV-01 evidence recorded"},
    {"id": "IE-P2-3", "milestone": "M01", "wave": "Wave 1", "order": 3, "merges": ["P2-G01T", "P2-G01"], "after": ["IE-P2-1"],
     "entry_criteria": ["S09 merged (verified: origin/main 17b40b4)", "P2-G01T CMD-RED receipt with test file sha256; P2-G01 green", "CMD-WORKFLOW-CHECK exit 0; new actions SHA-pinned and CMD-SUPPLY-SCAN PASS", "gate backend uses python3.12 per IE-P2-F23 correction", "Reviewer review recorded; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE: tvapp and backend print `PASS no tv-app/ tree` / `PASS no backend/ tree`", "CMD-GATE-ALL on a scratch branch with an empty tv-app/ and backend/ shows GAP when the tool is missing (G01T cases)", "gh run view: jobs `gate / tvapp` and `gate / backend` exist with path filters"],
     "rollback": "revert PR; A01/B01 landings wait (RISK-AFC-P2-11)",
     "exit": "gate areas tvapp and backend on main (W1 exit item 1)"},
    {"id": "IE-P2-4", "milestone": "M02", "wave": "Wave 1", "order": 4, "merges": ["P2-X01"], "after": ["IE-P2-1"],
     "entry_criteria": ["OA-1 done; OA-4 Prime Video signed in before the first install (IE-P2-F06)", "PROC-PREPARE and CMD-SUPPLY-SCAN before first use: actual compatible JDK17, Android command-line/platform/SDK/build-tools including apkanalyzer/apksigner, Gradle wrapper/plugins and pinned starter; qualify host build tools and record pins before A01T", "CMD-ADB-BASELINE, CMD-ADB-INSTALL, CMD-ADB-SCREENCAP receipts; first_install_at recorded in VERDICT front matter", "CMD-VERDICT-CHECK exit 0; spikes/sp1-device/.gitignore ignores local.properties (IE-P2-F24)", "RISK-AFC-P2-01: Fire OS 5 or API < 25 → class C owner stop, device slices halt"],
     "post_step_vv": ["CMD-MAIN-GATE (hygiene: no PATH-HOME in evidence)", "record device identity; set spike_panel_max deadline = first_install_at + 24 h in the lease log", "Record X01 host-preparation completion separately from first_install_at and full verdict landing; A01T host red may start on this receipt without a new stick slot"],
     "rollback": "verdict is evidence; a wrong verdict is superseded by a new verdict PR, never edited silently",
     "exit": "device identity and clock start recorded; stick released to P2-X04 immediately"},
    {"id": "IE-P2-5", "milestone": "M02", "wave": "Wave 1", "order": 5, "merges": ["P2-B01T", "P2-B01"], "after": ["IE-P2-3"],
     "entry_criteria": ["B01T PROC-PREPARE with scanned/pinned Python test deps and empty API/interface harness; valid CMD-RED behavior-assertion receipt in shared B01T/B01 worktree with baseline/diff/bootstrap/test hashes, left uncommitted; B01 green on same tests; CMD-GATE-BACKEND, CMD-SAM-VALIDATE", "write set excludes backend/fixtures/ (IE-P2-F01)", "B01 carries the IE-P2-F12 content: store/ accessors, pipeline/handler.py composition, router calls, AFC-STUB stubs, empty registry.json in contract shape, samconfig.toml (stack afc-dev, profile afc-dev), backend/.gitignore, every B02..B07 dependency pinned", "CMD-SUPPLY-SCAN PASS for SAM CLI, cfn-lint and every pinned Python dependency", "test tokens generated at run time (IE-P2-F25)", "Reviewer review; CMD-PR-CHECKS pass", "B01T owns backend/tests/deployed/conftest.py and deployed/device_auth/, api/; shared conftest and dependency edits under backend-template; other T slices own distinct deployed module directories per current graph and TE-P2-F01"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CONTRACT-DIGEST → contracts.b01", "CMD-SAM-VALIDATE on main"],
     "rollback": "revert PR; dependents keep developing against the branch",
     "exit": "frozen contracts recorded; backend skeleton with device-code link green (W1 exit item 4)"},
    {"id": "IE-P2-6", "milestone": "M04", "wave": "Wave 1", "milestone_note": "CP-X05-HIST, executes during M02/M03", "order": 6, "merges": ["P2-X05"], "after": ["IE-P2-5"],
     "entry_criteria": ["X05 PR 1: capture tool, endpoints and completed-game fixtures with historical/replay provenance per CONTRACT-AFC-P2-FIXTURE; interim PARTIAL verdict, live timing pending; October 12 is no longer a remaining live opportunity; first planned live capture is TNF October 15", "lands after P2-B01 so the backend area has tests and template (IE-P2-F02)", "CMD-FIXTURE-INDEX-CHECK, CMD-VERDICT-CHECK exit 0", "Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE (backend area runs)", "CMD-CONTRACT-DIGEST → fixtures.v1"],
     "rollback": "revert PR; fixtures are never edited, a bad capture is superseded by later sequence files",
     "exit": "first fixtures on main (W1 exit item 6); B02T may start"},
    {"id": "IE-P2-7", "milestone": "M03", "wave": "Wave 1", "order": 7, "merges": ["P2-A01T", "P2-A01"], "after": ["IE-P2-3", "IE-P2-4", "IE-P2-5"],
     "entry_criteria": ["A01T waits for X01 qualified host JDK17/SDK/build-tools receipt; PROC-PREPARE, buildable empty test/interface harness only, no tested feature behavior; valid CMD-RED behavior assertions in shared A01T/A01 worktree with frozen bootstrap/test hashes, left uncommitted; A01 CMD-GATE-TVAPP green on same tests", "A01 carries IE-P2-F10 and F11 content (ApiClient for every operation, DTOs, navigation, stubs with AFC-STUB, all dependencies, complete manifest, tv-app/.gitignore, THIRD_PARTY_NOTICES.md starter notice, AFC_API_BASE_URL from afcApiBaseUrl)", "CMD-API-CLIENT-MATCH against contracts.b01 openapi.yaml", "CMD-SUPPLY-SCAN PASS for starter, Gradle wrapper and plugins", "PROC-VISUAL-REVIEW on the stick for shell, not-configured and network-error states, taken after P2-X04 released the stick (IE-P2-F07, F26)", "Reviewer review with Reverify on the debug APK claim (minSdk 25, package); CMD-PR-CHECKS pass", "A01 configures release variant with host debug signing unless owner supplies OA-11; L05 only executes that already-configured build; no signing configuration authored by Light Implementer"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-APK-BUILD-DEBUG (empty ApiUrl), CMD-APK-SHA256, CMD-APK-CERT", "CMD-ADB-INSTALL on the stick (fire-tv-stick lease, next free slot)"],
     "rollback": "revert PR; CMD-ADB-ROLLBACK on the stick (first app install: adb uninstall com.afc.companion)",
     "exit": "tv-app scaffold builds and installs on the stick (W1 exit item 3); apk.last_green set"},
    {"id": "IE-P2-8", "milestone": "M03", "wave": "Wave 1", "order": 8, "merges": ["P2-R1"], "after": ["IE-P2-2", "IE-P2-3", "IE-P2-4", "IE-P2-5", "IE-P2-6", "IE-P2-7"],
     "entry_criteria": ["every other Wave 1 slice merged", "R1 holds main-landing from branch cut to merge (IE-P2-F18)", "CMD-RELEASE-PREP, CMD-CHANGELOG-CHECK exit 0; versionName 0.1.0"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-APK-BUILD-DEBUG at merge.P2-R1, CMD-APK-SHA256, CMD-APK-CERT → apk.m1", "draft release v0.1.0 targets merge.P2-R1; publication waits for OA-8"],
     "rollback": "revert PR; draft release deleted (unpublished draft only)",
     "exit": "W1 exit; release.m1 recorded"},
    {"id": "IE-P2-9", "milestone": "M03", "wave": "Wave 2", "order": 9, "merges": ["P2-X04"], "after": ["IE-P2-4"],
     "entry_criteria": ["X04 held fire-tv-stick continuously from X01 release; ended at verdict or first_install_at + 24 h", "modeB only with CMD-ADB-GEOMETRY + capture (or OA-9 camera, RISK-AFC-P2-09) showing video and panel without overlap or crop; else fullScreen (AC-AFC-P2-SPIKE-02)", "CMD-VERDICT-CHECK; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "record panel_mode"],
     "rollback": "verdict superseded only by a new verdict PR inside the clock; after the clock, TIMEBOX → fullScreen stands",
     "exit": "panel_mode fixed for A05T/A05, X09, D02"},
    {"id": "IE-P2-10", "milestone": "M04", "wave": "Wave 2", "order": 10, "merges": ["P2-X02"], "after": ["IE-P2-9"],
     "entry_criteria": ["stick released by X04 (and the A01 review slot)", "CMD-ADB-INSTALL, CMD-ADB-SCREENCAP over Prime Video playback; CMD-VERDICT-CHECK", "RISK-AFC-P2-02: no heads-up route → class C owner stop before A03 product code", "Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "record notify_route"],
     "rollback": "verdict superseded by new verdict PR",
     "exit": "notify_route fixed for A03T/A03"},
    {"id": "IE-P2-11", "milestone": "M04", "wave": "Wave 2", "milestone_note": "CP-X03-REG", "order": 11, "merges": ["P2-X03"], "after": ["IE-P2-10", "IE-P2-5"],
     "entry_criteria": ["PR 1 of P2-X03 (IE-P2-F05): desk evidence per provider in spike order; registry.json per CONTRACT-AFC-P2-PROVIDER-REGISTRY; interim VERDICT; stick released", "no invented URI (AC-AFC-P2-SPIKE-03); gameOpened only where arrival observed", "CMD-REGISTRY-CHECK, CMD-VERDICT-CHECK; Reviewer review; CMD-PR-CHECKS pass (backend area runs)"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CONTRACT-DIGEST → registry.v1"],
     "rollback": "revert PR; registry returns to the empty contract shape",
     "exit": "B06T and A04T may start"},
    {"id": "IE-P2-12", "milestone": "M04", "wave": "Wave 2", "order": 12, "merges": ["P2-X07"], "after": ["IE-P2-10"],
     "entry_criteria": ["X03 desk part complete and stick released (X07 may run before IE-P2-11 lands)", "CMD-ADB-INSTALL, CMD-VERDICT-CHECK; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "record detect_support"],
     "rollback": "verdict superseded by new verdict PR",
     "exit": "A02 detector behavior fixed"},
    {"id": "IE-P2-13", "milestone": "M05", "wave": "Wave 2", "order": 13, "merges": ["P2-B02T", "P2-B02"], "after": ["IE-P2-5", "IE-P2-6"],
     "entry_criteria": ["B02T red against fixtures.v1 (and fixtures.v2 cases if landed)", "B02 green: CMD-GATE-BACKEND", "CMD-CONTRACT-FROZEN vs contracts.b01", "Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CONTRACT-FROZEN on main"],
     "rollback": "revert PR",
     "exit": "ingest merged"},
    {"id": "IE-P2-14", "milestone": "M05", "wave": "Wave 2", "order": 14, "merges": ["P2-B03T", "P2-B03"], "after": ["IE-P2-5"],
     "entry_criteria": ["B03T verified CMD-RED receipt in shared B03 pair worktree; B03 green on unchanged test IDs/hashes", "both sources (Yahoo read-only from recorded responses, manual) and presets exactly per CONTRACT-AFC-P2-PRESETS; lands when green, not at T_yahoo (IE-P2-F04)", "recorded responses carry no token shapes (IE-P2-F25)", "CMD-CONTRACT-FROZEN; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CONTRACT-DIGEST (presets.py)"],
     "rollback": "revert PR",
     "exit": "lineup merged; X06 Yahoo path becomes testable once deployed"},
    {"id": "IE-P2-15", "milestone": "M05", "wave": "Wave 2", "order": 15, "merges": ["P2-L02"], "after": ["IE-P2-5"],
     "entry_criteria": ["OA-3 done (afc-dev profile); OA-10 passphrase stored for the link-confirm smoke (IE-P2-F15)", "aws-afc-dev lease free; no in-progress game window held", "deploy commit = main HEAD (includes B02/B03 when merged); CMD-SAM-BUILD, CMD-SAM-DEPLOY with --tags GitCommit=<sha>", "any Paid-plan prompt → stop, class F (RISK-AFC-P2-07)"],
     "post_step_vv": ["CMD-STACK-OUTPUTS → ApiUrl", "CMD-DEPLOYED-COMMIT", "CMD-DEPLOYED-SMOKE (link issue 200, profile 401 without token, confirm with OA-10 passphrase entered by the owner)", "CMD-APK-BUILD-DEBUG with -PafcApiBaseUrl=ApiUrl; CMD-ADB-INSTALL; PROC-VISUAL-REVIEW of A01 code-shown, expired, linked states (IE-P2-F26)", "evidence PR lands under main-landing"],
     "rollback": "first deploy failure: stack in ROLLBACK_COMPLETE → `sam delete --stack-name afc-dev --profile afc-dev --no-prompts` (dev data only) and retry; later failures: redeploy deploy.last_green",
     "exit": "deploy.1 recorded; deploy.last_green = deploy.1"},
    {"id": "IE-P2-16", "milestone": "M04", "wave": "Wave 2", "order": 16, "merges": ["P2-X03"], "after": ["IE-P2-11"],
     "entry_criteria": ["PR 2 of P2-X03: Thu 2026-10-15 TNF live check (fire-tv-stick + live-game-window for the game only); amends only the Prime Video registry entry and the verdict", "CMD-REGISTRY-CHECK; CMD-GATE-BACKEND green with the amended registry (B06 tests if merged)", "Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CONTRACT-DIGEST → registry.v2"],
     "rollback": "revert PR (registry.v1 stands); live window missed → RISK-AFC-P2-08: desk outcome stands and the TNF check moves to X09",
     "exit": "provider-link verdict final (W2 exit)"},
    {"id": "IE-P2-17", "milestone": "M04", "wave": "Wave 2", "order": 17, "merges": ["P2-X05"], "after": ["IE-P2-6"],
     "entry_criteria": ["PR 2 of P2-X05: TNF 2026-10-15 live capture appended as later sequence files; timing and correction evidence; final VERDICT", "CMD-FIXTURE-INDEX-CHECK (existing files byte-identical); Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CONTRACT-DIGEST → fixtures.v2"],
     "rollback": "revert PR; fixtures.v1 stands; live captures retried at X09 (RISK-AFC-P2-08)",
     "exit": "ESPN live timing verdict (W2 exit)"},
    {"id": "IE-P2-18", "milestone": "M06", "wave": "Wave 2", "order": 18, "merges": ["P2-A02T", "P2-A02"], "after": ["IE-P2-7", "IE-P2-12", "IE-P2-15"],
     "entry_criteria": ["A02T red; A02 CMD-GATE-TVAPP green; detector per detect_support (unsupported → control hidden, limit stated)", "manifest/gradle edits only under their leases (IE-P2-F10)", "APK with -PafcApiBaseUrl=ApiUrl; PROC-VISUAL-REVIEW on the stick for each control state", "Reviewer review with Reverify on any APK claim; CMD-PR-CHECKS pass", "A02T owns profile/ and detect/ under androidTest as well as host unit paths; all instrumented use holds fire-tv-stick cross-process lock; backend-template protects any authorized shared conftest change"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-API-CLIENT-MATCH", "CMD-ADB-INSTALL of main-head APK"],
     "rollback": "revert PR; CMD-ADB-ROLLBACK to apk.last_green",
     "exit": "profile and settings UI merged with visual review (W2 exit)"},
    {"id": "IE-P2-19", "milestone": "M06", "wave": "Wave 2", "order": 19, "merges": ["P2-X06"], "after": ["IE-P2-1"],
     "entry_criteria": ["Yahoo path: OA-2 done incl. redirect URI registered at the deployed ApiUrl; P2-B03 merged and deployed (IE-P2-15 or a redeploy); OAuth read through the deployed role only", "manual path: at T_yahoo 2026-10-16T19:00:00Z without approval", "CMD-VERDICT-CHECK; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "record lineup_source (consumed by IE-P2-25 deploy configuration)"],
     "rollback": "verdict superseded by new verdict PR; Yahoo failure after approval → manual (C6)",
     "exit": "T_yahoo outcome recorded (Wave 3 entry)"},
    {"id": "IE-P2-20", "milestone": "M06", "wave": "Wave 2", "order": 20, "merges": ["P2-R2"], "after": ["IE-P2-8", "IE-P2-9", "IE-P2-10", "IE-P2-11", "IE-P2-12", "IE-P2-13", "IE-P2-14", "IE-P2-15", "IE-P2-16", "IE-P2-17", "IE-P2-18", "IE-P2-19"],
     "entry_criteria": ["every other Wave 2 slice merged; P2-R1 merged", "main-landing held from branch cut to merge"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CHANGELOG-CHECK", "apk.m2 (build at merge.P2-R2, sha256, cert)", "draft v0.2.0"],
     "rollback": "revert PR; delete unpublished draft",
     "exit": "W2 exit"},
    {"id": "IE-P2-21", "milestone": "M07", "wave": "Wave 3", "order": 21, "merges": ["P2-B04T", "P2-B04"], "after": ["IE-P2-13", "IE-P2-14"],
     "entry_criteria": ["B04T red (correction cases on fixtures.v2 when landed); B04 green", "CMD-CONTRACT-FROZEN; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE"],
     "rollback": "revert PR",
     "exit": "matcher merged"},
    {"id": "IE-P2-22", "milestone": "M07", "wave": "Wave 3", "order": 22, "merges": ["P2-B05T", "P2-B05"], "after": ["IE-P2-21"],
     "entry_criteria": ["B05T waits for verified B04T red receipt and frozen shared-fixture handoff, not a red-only merge; its own red receipt is verified in shared B05 pair worktree; B04 product merge remains a B05 landing prerequisite", "B05 green; implements only alert_policy.evaluate (pipeline composition is B01's)", "CMD-CONTRACT-FROZEN; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE"],
     "rollback": "revert PR",
     "exit": "policy merged; A03 may land"},
    {"id": "IE-P2-23", "milestone": "M08", "wave": "Wave 3", "order": 23, "merges": ["P2-B06T", "P2-B06"], "after": ["IE-P2-11"],
     "entry_criteria": ["B06T against registry.v1 (or v2); B06 reads registry.json read-only", "CMD-REGISTRY-CHECK unchanged digest; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CONTRACT-FROZEN (registry)"],
     "rollback": "revert PR",
     "exit": "resolver merged; A04 may land"},
    {"id": "IE-P2-24", "milestone": "M07", "wave": "Wave 3", "order": 24, "merges": ["P2-B07T", "P2-B07"], "after": ["IE-P2-21"],
     "entry_criteria": ["B07T valid CMD-RED receipt in shared B07 pair worktree; B07 green on unchanged test IDs/hashes", "B07 green (stale at 60 s, null-with-reason)", "CMD-CONTRACT-FROZEN; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE"],
     "rollback": "revert PR",
     "exit": "panel service merged; A05 may land"},
    {"id": "IE-P2-25", "milestone": "M09", "wave": "Wave 3", "order": 25, "merges": ["P2-L03"], "after": ["IE-P2-15", "IE-P2-19", "IE-P2-21", "IE-P2-22", "IE-P2-23", "IE-P2-24"],
     "entry_criteria": ["B04..B07 merged; CMD-STUB-SCAN clean for backend/src", "lineup_source applied as deploy configuration (IE-P2-F04)", "aws-afc-dev lease; deploy commit = main HEAD with --tags GitCommit"],
     "post_step_vv": ["CMD-STACK-OUTPUTS (ApiUrl unchanged; if changed, every later APK rebuilds with the new value)", "CMD-DEPLOYED-COMMIT", "CMD-DEPLOYED-SMOKE", "CMD-DEPLOYED-TESTS"],
     "rollback": "redeploy deploy.last_green (CMD-SAM-DEPLOY at that commit)",
     "exit": "deploy.2; deploy.last_green = deploy.2"},
    {"id": "IE-P2-26", "milestone": "M08", "wave": "Wave 3", "order": 26, "merges": ["P2-A03T", "P2-A03"], "after": ["IE-P2-18", "IE-P2-10", "IE-P2-22"],
     "entry_criteria": ["A03T red incl. instrumented run on the stick (fire-tv-stick lease, IE-P2-F09)", "A03 green: CMD-GATE-TVAPP, CMD-TVAPP-INSTRUMENTED on the stick over provider playback, PROC-VISUAL-REVIEW", "AlertNotifier Watch calls the A01 WatchLauncher signature unchanged", "Reviewer review with Reverify on APK claims; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-API-CLIENT-MATCH"],
     "rollback": "revert PR; CMD-ADB-ROLLBACK",
     "exit": "alert UI merged"},
    {"id": "IE-P2-27", "milestone": "M08", "wave": "Wave 3", "order": 27, "merges": ["P2-A04T", "P2-A04"], "after": ["IE-P2-18", "IE-P2-11", "IE-P2-23"],
     "entry_criteria": ["A04T started after A03T's red receipt; red instrumented run under fire-tv-stick", "A04 green; on-device launch per provider and PROC-VISUAL-REVIEW; one RoutingOutcome per attempt", "Reviewer review with Reverify; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE"],
     "rollback": "revert PR; CMD-ADB-ROLLBACK",
     "exit": "Watch merged"},
    {"id": "IE-P2-28", "milestone": "M09", "wave": "Wave 3", "order": 28, "merges": ["P2-A05T", "P2-A05"], "after": ["IE-P2-9", "IE-P2-18", "IE-P2-24"],
     "entry_criteria": ["A05T verified red receipt, including applicable instrumented run under fire-tv-stick cross-process lock; A05 green on same test IDs/hashes", "A05 builds panel_mode only; MainActivity.kt edited by A05 alone", "CMD-TVAPP-INSTRUMENTED, PROC-VISUAL-REVIEW, CMD-TEXT-SIZE-MEASURE (body ≥ 24 px, scores ≥ 32 px)", "Reviewer review with Reverify; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-STUB-SCAN clean for tv-app/app/src/main"],
     "rollback": "revert PR; CMD-ADB-ROLLBACK",
     "exit": "panel UI merged"},
    {"id": "IE-P2-29", "milestone": "M10", "wave": "Wave 3", "order": 29, "merges": [], "after": ["IE-P2-25", "IE-P2-26", "IE-P2-27", "IE-P2-28"],
     "entry_criteria": ["W3 candidate = main HEAD; CMD-TREE-EQUAL backend/ between candidate and deploy.last_green commit (else redeploy first)", "OA-4 sessions live; OA-10 linked device", "cut-off 2026-10-18T15:00:00Z"],
     "post_step_vv": ["CMD-STUB-SCAN", "CMD-APK-BUILD-DEBUG with ApiUrl, CMD-APK-SHA256, CMD-APK-CERT, CMD-ADB-INSTALL", "CMD-E2E-REPLAY with screencaps and geometry"],
     "rollback": "CMD-ADB-ROLLBACK; failing behavior → bug-triager; owner scope decision (RISK-AFC-P2-13) if not fixable by 2026-10-18T15:00Z",
     "exit": "rehearsal receipt; candidate APK installed for X09"},
    {"id": "IE-P2-30", "milestone": "M10", "wave": "Wave 3", "order": 30, "merges": ["P2-X09"], "after": ["IE-P2-29"],
     "entry_criteria": ["Sun 2026-10-18 windows; holds fire-tv-stick, aws-afc-dev, live-game-window", "no deploy during an in-progress game"],
     "post_step_vv": ["PROC-E2E-LIVE record; CMD-ADB-SCREENCAP, CMD-ADB-GEOMETRY", "defects → PROC-BUG-TRIAGE", "run-record PR: CMD-MAIN-GATE"],
     "rollback": "missed window or no qualifying event → labeled replay + next window (RISK-AFC-P2-08)",
     "exit": "W3 live evidence (W3 exit item 1)"},
    {"id": "IE-P2-31", "milestone": "M10", "wave": "Wave 3", "order": 31, "merges": ["P2-R3"], "after": ["IE-P2-20", "IE-P2-21", "IE-P2-22", "IE-P2-23", "IE-P2-24", "IE-P2-25", "IE-P2-26", "IE-P2-27", "IE-P2-28", "IE-P2-29", "IE-P2-30"],
     "entry_criteria": ["every other Wave 3 slice merged; P2-R2 merged; main-landing held"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CHANGELOG-CHECK", "apk.m3", "draft v0.3.0"],
     "rollback": "revert PR; delete unpublished draft",
     "exit": "W3 exit"},
    {"id": "IE-P2-32", "milestone": "M11", "wave": "Wave 4", "order": 32, "merges": [], "after": ["IE-P2-30"],
     "entry_criteria": ["each Sunday defect fixed on bug-triager routes with reproduction, origin/escape, red-then-green regression, prevention check (AC-AFC-P2-BUG-01); write set disjoint from running slices", "fix PRs merged by 2026-10-19T20:00:00Z"],
     "post_step_vv": ["CMD-MAIN-GATE per merge", "redeploy (CMD-SAM-DEPLOY, CMD-DEPLOYED-COMMIT, CMD-DEPLOYED-SMOKE, CMD-DEPLOYED-TESTS) when backend/ changed", "CMD-APK-BUILD-DEBUG + CMD-ADB-INSTALL when tv-app/ changed", "CMD-E2E-REPLAY"],
     "rollback": "revert fix PR; redeploy deploy.last_green; CMD-ADB-ROLLBACK",
     "exit": "deploy.last_green and apk.last_green current for X10"},
    {"id": "IE-P2-33", "milestone": "M11", "wave": "Wave 4", "order": 33, "merges": ["P2-X10"], "after": ["IE-P2-32"],
     "entry_criteria": ["Mon 2026-10-19 MNF (~2026-10-20T00:15Z); holds fire-tv-stick, aws-afc-dev, live-game-window"],
     "post_step_vv": ["PROC-E2E-LIVE record; CMD-DEPLOYED-TESTS; labeled replay for repeatability", "run-record PR: CMD-MAIN-GATE"],
     "rollback": "missed window → labeled replay; the gap is owner-accepted at class C or carried as a typed gap",
     "exit": "corrections/starter changes verified (W4 exit item 1)"},
    {"id": "IE-P2-35", "milestone": "M11", "wave": "Wave 4", "order": 34, "merges": ["P2-X11"], "after": ["IE-P2-31"],
     "entry_criteria": ["OD-AFC-03 = yes and W3 exited on time; drop at 2026-10-21T12:00:00Z if unverified", "CMD-VERDICT-CHECK; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE"],
     "rollback": "Unselected or timeboxed X11 records exact terminal/no-offer disposition under OD-AFC-03; only applicable no-offer criteria can close; enabled voice proof remains not_run/typed gap, never inferred PASS",
     "exit": "X11 terminal disposition recorded; verdict landed when run; D02 may freeze only after this prerequisite"},
    {"id": "IE-P2-34", "milestone": "M11", "wave": "Wave 4", "order": 35, "merges": ["P2-D02"], "after": ["IE-P2-1", "IE-P2-4", "IE-P2-9", "IE-P2-10", "IE-P2-12", "IE-P2-16", "IE-P2-17", "IE-P2-19", "IE-P2-35"],
     "entry_criteria": ["All required final X01..X07 verdicts landed (X03 PR 2, X05 PR 2 included); selected X11 terminal disposition recorded and its verdict landed when run; if unselected, record OD-AFC-03/no-offer disposition without claiming enabled-voice proof", "PR #10 landed and merged tools/spec content/pin available (S42 d259c169); redundant PR #11 is not another prerequisite", "Freeze inventory binds every landed verdict through the specification freeze: paths, merge SHAs and digests; D02 includes all limits, selected modes/routes and aligned model names; any later landed verdict requires a bounded D02 delta in the same scope before W4 exit", "CMD-GATE-SPEC byte-identical rebuild; revision row with changed sections, PR and diff links", "Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE"],
     "rollback": "revert PR",
     "exit": "AC-AFC-P2-SPEC-01 evidence; all landed verdicts through freeze incorporated; same D02 slice owns any necessary later delta"},
    {"id": "IE-P2-36", "milestone": "M11", "wave": "Wave 4", "order": 36, "merges": ["P2-R4"], "after": ["IE-P2-31", "IE-P2-32", "IE-P2-33", "IE-P2-34", "IE-P2-35"],
     "entry_criteria": ["All Wave 4 slices landed or explicit conditional terminal disposition recorded; D02 freeze inventory includes every landed required verdict and X11 when run; P2-R3 merged; no unresolved actionable review defect at any priority without explicit owner acceptance of residual risk; every active register case has its own passing evidence or owner-accepted typed gap; main-landing held"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-CHANGELOG-CHECK", "apk.m4", "draft v0.4.0"],
     "rollback": "revert PR; delete unpublished draft",
     "exit": "W4 exit; tv-app/ and backend/ frozen except bug-triager fixes"},
    {"id": "IE-P2-37", "milestone": "M12", "wave": "Wave 5", "order": 37, "merges": ["P2-D03", "P2-D04", "P2-D05"], "after": ["IE-P2-33"],
     "entry_criteria": ["D03 PROC-README-FRESH-SETUP pass from a clean checkout", "D04 final wording after OA-6", "D05 ≤ 2 min 50 s plan with source per shot", "CMD-GATE-DOCS, CMD-GATE-HYGIENE; Reviewer review each; CMD-PR-CHECKS pass", "cut-off 2026-10-22T16:00:00Z"],
     "post_step_vv": ["CMD-MAIN-GATE", "PROC-SUBMISSION-CHECK"],
     "rollback": "revert PR",
     "exit": "submission docs on main"},
    {"id": "IE-P2-38", "milestone": "M12", "wave": "Wave 5", "order": 38, "merges": ["P2-SCR1"], "after": ["IE-P2-36"],
     "entry_criteria": ["PROC-SCRIBE-ASSEMBLY pass; CMD-GATE-HYGIENE; Reviewer review; CMD-PR-CHECKS pass"],
     "post_step_vv": ["CMD-MAIN-GATE"],
     "rollback": "revert PR",
     "exit": "AC-AFC-P2-DX-02"},
    {"id": "IE-P2-39", "milestone": "M13", "wave": "Wave 5", "order": 39, "merges": [], "after": ["IE-P2-37", "IE-P2-38"],
     "entry_criteria": ["CMD-GATE-HYGIENE on main HEAD clean (secrets and paths)", "OA-5 by the owner: LICENSE committed (or agent PR approved) and visibility flipped to public (OD-AFC-P2-04: 2026-10-22)"],
     "post_step_vv": ["CMD-JUDGE-ACCESS against B01 frozen OpenAPI authentication/polling contract; no assumed successful anonymous GET /v1/link; protect returned link codes/tokens; verify anonymous repository only after OA-5", "Orchestrator applies the main ruleset (PR-only, required checks, no squash) now that rulesets are available (IE-P2-F22)"],
     "rollback": "exposure found after flip → RISK-AFC-P2-12: owner flips back to private and rotates; revert the leaking commit by PR",
     "exit": "judge access verified"},
    {"id": "IE-P2-40", "milestone": "M13", "wave": "Wave 5", "order": 40, "merges": [], "after": ["IE-P2-36"],
     "entry_criteria": ["backend/ frozen at W4 exit; if main's backend/ tree differs from deploy.last_green, redeploy at main HEAD; aws-afc-dev lease"],
     "post_step_vv": ["CMD-DEPLOYED-COMMIT", "CMD-DEPLOYED-SMOKE", "CMD-DEPLOYED-TESTS"],
     "rollback": "redeploy deploy.last_green",
     "exit": "deploy.final with backend/ tree equal to the candidate's"},
    {"id": "IE-P2-41", "milestone": "M13", "wave": "Wave 5", "order": 41, "merges": ["P2-R5"], "after": ["IE-P2-36", "IE-P2-37", "IE-P2-38", "IE-P2-39", "IE-P2-40"],
     "entry_criteria": ["D03, D04, D05, SCR1 merged; P2-R4 merged (IE-P2-F17, F18)", "R5 moves [Unreleased] under 1.0.0 and bumps versionName 1.0.0 / versionCode; main-landing held", "cut-off 2026-10-22T17:00:00Z"],
     "post_step_vv": ["CMD-MAIN-GATE on merge.P2-R5", "CMD-CHANGELOG-CHECK", "candidate.final = merge.P2-R5"],
     "rollback": "revert PR; candidate falls back to the IE-P2-36 state with v0.4.0",
     "exit": "W5 candidate commit fixed"},
    {"id": "IE-P2-42", "milestone": "M13", "wave": "Wave 5", "order": 42, "merges": ["P2-L05"], "after": ["IE-P2-41"],
     "entry_criteria": ["Build from candidate.final on main with -PafcApiBaseUrl=deploy.final ApiUrl; release signing already configured by A01 (host debug signer unless OA-11); actual tools and signer pinned; no new credential access", "cut-off 2026-10-22T19:00:00Z"],
     "post_step_vv": ["CMD-APK-BUILD-RELEASE, CMD-APK-SHA256, CMD-APK-CERT", "CMD-REVERIFY-APK on exact APK sha256, selected frozen backend unchanged: meaningful grounded minSdk/package/permission/service claims required; unproven semantics, absent mapping or unsupported capability = REVERIFY_CAPABILITY_GAP; ordinary ATE/apkanalyzer/ZIP-string checks never substitute; raw output private, sanitized receipt bound to raw digest", "CMD-ADB-INSTALL of the final APK on the stick", "draft v1.0.0 release notes carry the APK sha256 (draft body, no commit); tag v1.0.0 targets candidate.final at OA-8 publication", "Main build identity and APK inspection may complete before tag; AC-AFC-P2-APK-01 tagged-main/publication subcriterion stays OWNER_EVIDENCE_PENDING until OA-8 authorization and tag readback names candidate.final; no early tag/release"],
     "rollback": "build failure → bug-triager; stick: CMD-ADB-ROLLBACK to apk.m4",
     "exit": "Exact final APK identity/inspection and truthful Reverify disposition; tagged-main/publication remains OWNER_EVIDENCE_PENDING until OA-8 tag readback"},
    {"id": "IE-P2-43", "milestone": "M13", "wave": "Wave 5", "order": 43, "merges": ["P2-X12"], "after": ["IE-P2-42", "IE-P2-37"],
     "entry_criteria": ["captures on the final APK (sha256 from IE-P2-42); TNF 2026-10-22 live window; OA-9 camera shots", "manifest names and sha256 of clips; clips untracked (evidence/demo/.gitignore)", "docs-only PR: changes no tv-app/ or backend/ path", "Manifest PR target 2026-10-23T06:00:00Z; a missed deadline records missing shots/claims, candidate hashes and remaining windows, then requires explicit owner scope decision identifying exact omissions/consequences; no automatic dropped shot"],
     "post_step_vv": ["CMD-MAIN-GATE", "CMD-TREE-EQUAL candidate.final vs main HEAD (tv-app/, backend/)"],
     "rollback": "Revert evidence PR if needed; retain final-APK capture obligation; earlier X09/X10 clips are historical evidence of those APKs only, never demonstration of apk.final; any material restriction requires exact owner scope decision",
     "exit": "demo clips manifest complete"},
    {"id": "IE-P2-44", "milestone": "M13", "wave": "Wave 5", "order": 44, "merges": [], "after": ["IE-P2-42"],
     "entry_criteria": ["final_candidate block complete; assessments start at IE-P2-42 receipt (≈2026-10-22T19:00Z)", "Assurance Test Engineer and IE execution sessions fresh, no author ancestry", "Assessments may start at IE-P2-42, but final closeout waits for IE-P2-43 manifest/tree comparison and all 100 SEIT row dispositions; tagged-main/publication subcriterion stays pending until OA-8 tag readback; author planning delta and TE planning PASS supply no independent review/assurance"],
     "post_step_vv": ["IE execution: system-level validation against technical plan §Outcome and W5 exit on candidate.final", "Assurance Test Engineer: seit.json results per register UID and AC-AFC-P2 row", "final CMD-TREE-EQUAL after IE-P2-43; CMD-DEPLOYED-COMMIT tree check vs candidate.final backend/"],
     "rollback": "a failing assessment finding → bug-triager in the current round; candidate re-forms at the fix merge (R5 version stays) with IE-P2-42 rebuilt; owner told of any W5 slip (RISK-AFC-P2-13)",
     "exit": "W5 technical closeout only when final capture/evidence and required independent assessments complete; owner checklist handed over; pending tag/publication subcriteria remain explicitly pending until OA-8, never complete by planning PASS"}
  ],
  "configuration_identity": {
    "repository": "1wgrumph/amazon-fantasy-companion",
    "records": [
      "p2.base",
      "merge.<slice> (and .pr1/.pr2 for X03, X05)",
      "device {model, fire_os, api_level, first_install_at, starter_repo, starter_commit, sdk_platform, build_tools, scan_receipts}",
      "contracts.b01 {openapi.yaml, template.yaml, samconfig.toml, store/, pipeline/, presets.py sha256}",
      "registry.v1, registry.v2",
      "fixtures.v1, fixtures.v2",
      "panel_mode, notify_route, detect_support, lineup_source",
      "deploy.<n> {stack: afc-dev, profile: afc-dev, region name, GitCommit tag, template sha256, ApiUrl, smoke and tests receipts}; deploy.last_green; deploy.final",
      "apk.m1..m4 (m<n> = wave release checkpoint W<n>), apk.final {build commit, sha256, signer cert SHA-256, JDK, AGP, Gradle, afcApiBaseUrl}; apk.last_green",
      "release.m1..m5 (m<n> = wave n) {tag, target commit, draft URL}",
      "toolchain {AZHQ skill checkout HEAD at dispatch, tools/ci/VENDORED.md, tools/spec/VENDORED.md}",
      "red.<pair> {shared worktree, baseline commit, dirty diff digest, test IDs/file hashes, bootstrap file hashes, scanned tool pins, preparation disposition}; consumed before green, never a red-only merge",
      "spec.freeze {required X01..X07 final verdict paths/merge SHAs/digests, X11 terminal disposition and verdict when run, every other landed verdict through freeze, later D02 delta if needed}",
      "work.organization {approved graph/payload digests, 39 logical issue groups for 52 slices, 13 GitHub milestones M01..M13 (5 wave release checkpoints W1..W5 unchanged), duplicate search, policy dry-run/submit receipts, saved labels/body/milestone/dependency/URL readback}",
      "qualification.<suite> {candidate/input/suite hashes, five consecutive passes and one two-concurrent-copy pass, named cross-process locks, owned cleanup, actual duration}; ordinary reuse only for unchanged qualified candidate/inputs",
      "publication {OA-8 authorization, tag readback target on main}; separate from prepublication APK inspection"
    ],
    "proposed_commands": [],
    "rule": "Never consume an unrecorded identity: predecessor merge receipt for product, explicit preparation/red handoff for premerge TDD, and terminal conditional disposition for X11. Stable step IDs retain identity; order/after/entry predicates place IE-P2-35 before IE-P2-34.",
    "command_registry_ref": "seit.json/procedures_and_commands (64 finalized IDs; unchanged in this delta)",
    "frozen_capability_binding": {
      "decision": "DEC-AFC-SD-041 (Bearing Lite 1.1.7; supersedes the primary/frontend/heavyweight/tech-writing lane bindings)",
      "lane_profiles": {
        "tv-app-ui": "opensource-hackathon",
        "backend": "opensource-hackathon",
        "device-integration-spikes": "opensource-hackathon",
        "spec-and-docs": "opensource-hackathon",
        "scribe-side-lane": "opensource-hackathon",
        "defects": "bug-triager"
      },
      "opensource-hackathon": {
        "source_ref": "docs/plans/2026-10-11-amazon-fantasy-companion/journey.json#/profile_selection/frozen_snapshots/opensource-hackathon",
        "role_routes_ref": "docs/plans/2026-10-11-amazon-fantasy-companion/journey.json#/profile_selection/frozen_snapshots/opensource-hackathon/snapshot/roles",
        "full_profile_sha256": "7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1",
        "configuration_digest_sha256": "11c4478edb7b0c94da196cdc8be2317f498378724ae041bde0c108832b1e2036",
        "role_routes": {
          "implementer": {
            "enabled": true,
            "primary": "Claude Code / Claude Opus 5.5 / medium",
            "ordered_fallbacks": [
              "Muse Code / Muse WonderFull / xhigh",
              "Codex CLI / GPT-6.1 Sol / high"
            ]
          },
          "test_implementer": {
            "enabled": true,
            "primary": "Codex CLI / GPT-6.1 Sol / high",
            "ordered_fallbacks": [
              "Muse Code / Muse WonderFull / xhigh",
              "Claude Code / Claude Opus 5.5 / medium"
            ]
          },
          "light_implementer": {
            "enabled": true,
            "primary": "Muse Code / Muse Spark 1.3 / xhigh",
            "ordered_fallbacks": [
              "Cursor Agent / Grok 4.7 / medium",
              "Cursor Agent / Muse Spark 1.3 / high",
              "Claude Code / Claude Sonnet 5.5 / medium"
            ]
          },
          "coordinator": {
            "enabled": true,
            "primary": "AGY / Gemini 3.8 Flash / medium",
            "ordered_fallbacks": [
              "Cursor Agent / Claude Haiku 5.5 / xhigh",
              "Cursor Agent / Grok 4.7 / low",
              "Deep Code CLI / DeepSeek V4 Flash / max"
            ]
          },
          "reviewer": {
            "enabled": true,
            "primary": "Cursor Agent / Grok 4.7 / high",
            "ordered_fallbacks": [
              "Muse Code / Muse Spark 1.3 / max",
              "Codex CLI / GPT-6 Astra / high",
              "Claude Code / Claude Opus 5.5 / high"
            ],
            "cadence": "phase"
          },
          "scribe": {
            "enabled": true,
            "primary": "Muse Code / Muse Spark 1.3 / xhigh",
            "ordered_fallbacks": [
              "Claude Code / Claude Haiku 5.5 / xhigh",
              "AGY / Claude Sonnet 5.5 / medium",
              "Codex CLI / GPT-6.1 Sol / medium",
              "AGY / Gemini 3.8 Flash / high"
            ]
          },
          "plan_integrator": {
            "enabled": true,
            "primary": "Muse Code / Muse Spark 1.3 / max",
            "ordered_fallbacks": [
              "Claude Code / Claude Opus 5.5 / high",
              "Codex CLI / GPT-6.1 Sol / xhigh"
            ]
          },
          "systems_modeler.planning": {
            "enabled": true,
            "primary": "Muse Code / Muse Spark 1.3 / max",
            "ordered_fallbacks": [
              "Cursor Agent / Grok 4.7 / medium",
              "Claude Code / Claude Opus 5.5 / high",
              "Codex CLI / GPT-6.1 Sol / high"
            ]
          },
          "test_engineer.planning": {
            "enabled": true,
            "primary": "Claude Code / Claude Opus 5.5 / high",
            "ordered_fallbacks": [
              "Cursor Agent / Grok 4.7 / xhigh",
              "Codex CLI / GPT-6 Astra / xhigh",
              "Muse Code / Muse WonderFull / xhigh"
            ]
          },
          "test_engineer.assurance": {
            "enabled": true,
            "primary": "Codex CLI / GPT-6.1 Sol / xhigh",
            "ordered_fallbacks": [
              "Cursor Agent / Grok 4.7 / high",
              "Claude Code / Claude Opus 5.5 / medium",
              "Muse Code / Muse WonderFull / xhigh"
            ],
            "cadence": "lifecycle"
          },
          "integration_engineer.planning": {
            "enabled": true,
            "primary": "Claude Code / Claude Opus 5.5 / high",
            "ordered_fallbacks": [
              "Codex CLI / GPT-6 Astra / xhigh",
              "Muse Code / Muse WonderFull / xhigh",
              "Cursor Agent / Grok 4.7 / xhigh"
            ]
          },
          "integration_engineer.execution": {
            "enabled": true,
            "primary": "Codex CLI / GPT-6.1 Sol / high",
            "ordered_fallbacks": [
              "Claude Code / Claude Opus 5.5 / medium",
              "Cursor Agent / Grok 4.7 / high",
              "Muse Code / Muse WonderFull / xhigh"
            ],
            "cadence": "lifecycle"
          },
          "requirements_engineer.planning": {
            "enabled": true,
            "primary": "Cursor Agent / Grok 4.7 / high",
            "ordered_fallbacks": [
              "Muse Code / Muse Wonder / xhigh",
              "Codex CLI / GPT-6 Astra / high",
              "Claude Code / Claude Opus 5.5 / medium"
            ]
          }
        },
        "development_strategy": {
          "mode": "tdd"
        },
        "tdd_scope": "13 existing TDD pairs unchanged; spikes evidence-only; documentation-only slices keep their declared inspection method",
        "concurrency": {
          "dispatch_ready_independent_work": true,
          "preserve_order_for_dependencies_interfaces_write_overlap_and_shared_mutable_resources": true
        },
        "planning_to_implementation_clean_session": true,
        "review": {
          "coverage_assist": {
            "enabled": true,
            "required": true
          }
        },
        "deterministic_verification": {
          "reverify": {
            "enabled": true
          }
        },
        "holds": [
          {
            "id": "muse-contributor-mode",
            "harness": "Muse Code",
            "contributor_mode": "on",
            "required_cli_args": [
              "--contributor-mode",
              "on"
            ],
            "effect": "Every Muse Code primary and fallback dispatch for opensource-hackathon must launch with --contributor-mode on. Freeze this requirement in the lifecycle binding and carry it into every Muse execution packet. Verify the exact per-run flag; if it cannot be honored, return a typed configuration gap. This profile-specific requirement does not change the global Muse setting."
          }
        ],
        "fallback_activation": "ordered; only on verified unavailability or usage/rate-limit exhaustion of the primary and all preceding approved fallbacks",
        "assurance": "test_engineer.assurance and integration_engineer.execution enabled (cadence lifecycle) for every lane bound to this profile; no tech-writing exemption",
        "backend_resolution": {
          "coverage_assist": "OpenCodeReview delegation; TE help/provenance inspected; execution not_run here; missing/unavailable is typed gap",
          "reverify": "reverify 0.11.0 selected; TE backend inventory inspected; exact-APK execution not_run; APK semantic grounding unproven, REVERIFY_CAPABILITY_GAP; no backend change or ATE substitute"
        }
      },
      "bug-triager": {
        "source_ref": "seit.json/frozen_profile_binding/bug-triager",
        "role_routes_ref": "seit.json/frozen_profile_binding/bug-triager/roles",
        "configuration_digest_sha256": "6ca3ffccea9bae0e26f960b075e7a7fe2ffc01048474f1c8a70c31d8e748138b",
        "review": {
          "coverage_assist": {
            "enabled": true,
            "required": true
          }
        },
        "deterministic_verification": {
          "reverify": {
            "enabled": true
          }
        },
        "backend_resolution": {
          "coverage_assist": "OpenCodeReview delegation; TE help/provenance inspected; execution not_run here; missing/unavailable is typed gap",
          "reverify": "reverify 0.11.0 selected; TE backend inventory inspected; exact-APK execution not_run; APK semantic grounding unproven, REVERIFY_CAPABILITY_GAP; no backend change or ATE substitute"
        }
      }
    }
  },
  "authorized_glue": [],
  "stubs": [
    {
      "owner_slice": "P2-A01T and P2-B01T",
      "paths": "Only bootstrap/build/test/interface paths expressly authorized by current graph",
      "replaced_by": "Paired green Product Implementer realizes all tested behavior",
      "removal_check": "PROC-PREPARE before CMD-RED; freeze test/bootstrap hashes; missing tools/imports/collection/build is a preparation gap, never valid red"
    },
    {
      "owner_slice": "P2-B01",
      "paths": "backend/src/{feed_ingest,lineup,matcher,alert_policy,provider_resolver,panel}/ public functions with final signatures, marked AFC-STUB, raising NotImplementedError (router → 503 not_implemented)",
      "replaced_by": "P2-B02, P2-B03, P2-B04, P2-B05, P2-B06, P2-B07 respectively",
      "removal_check": "CMD-STUB-SCAN backend/src clean at IE-P2-25"
    },
    {
      "owner_slice": "P2-B01",
      "paths": "backend/src/pipeline/handler.py (PolicyFunction: matcher.resolve → alert_policy.evaluate → provider_resolver.resolve → panel.project) and backend/src/api/ router calling each module",
      "replaced_by": "not replaced; real composition that works once the module stubs are filled",
      "removal_check": "n/a (not a stub); CMD-CONTRACT-FROZEN"
    },
    {
      "owner_slice": "P2-B01",
      "paths": "backend/src/provider_resolver/registry.json = empty provider list in contract shape",
      "replaced_by": "P2-X03 PR 1",
      "removal_check": "CMD-REGISTRY-CHECK non-empty at IE-P2-11"
    },
    {
      "owner_slice": "P2-A01",
      "paths": "tv-app/app/src/main/java/com/afc/companion/{profile/ProfileSettingsScreen.kt, detect/AppDetector.kt, alerts/AlertService.kt, alerts/AlertNotifier.kt, watch/WatchLauncher.kt (launch(route: ProviderRoute): RoutingOutcome), panel/LineupPanel.kt} marked AFC-STUB; MainActivity.kt navigation to each",
      "replaced_by": "P2-A02 (profile, detect), P2-A03 (alerts), P2-A04 (watch), P2-A05 (panel and MainActivity panel hosting)",
      "removal_check": "CMD-STUB-SCAN tv-app/app/src/main clean at IE-P2-28 and IE-P2-29"
    }
  ],
  "deployments": [
    {"id": "deploy.1", "integration": "IE-P2-15", "slice": "P2-L02", "target": "aws-afc-dev stack afc-dev via profile afc-dev", "commit": "main HEAD at deploy (≥ merge.P2-B01)", "checks": ["CMD-STACK-OUTPUTS", "CMD-DEPLOYED-COMMIT", "CMD-DEPLOYED-SMOKE"], "rollback": "ROLLBACK_COMPLETE on create → sam delete (dev only) and retry; else redeploy deploy.last_green"},
    {"id": "deploy.2", "integration": "IE-P2-25", "slice": "P2-L03", "commit": "main HEAD with B04..B07 and lineup_source configuration", "checks": ["CMD-STACK-OUTPUTS", "CMD-DEPLOYED-COMMIT", "CMD-DEPLOYED-SMOKE", "CMD-DEPLOYED-TESTS"], "rollback": "redeploy deploy.last_green"},
    {"id": "deploy.fix.<n>", "integration": "IE-P2-32", "slice": "bug-triager fix (L03 command set re-run under aws-afc-dev)", "commit": "fix merge commit", "checks": ["CMD-DEPLOYED-COMMIT", "CMD-DEPLOYED-SMOKE", "CMD-DEPLOYED-TESTS"], "rollback": "redeploy deploy.last_green", "window_rule": "never during an in-progress game"},
    {"id": "deploy.final", "integration": "IE-P2-40", "commit": "main HEAD after W4 (backend/ tree equals candidate.final)", "checks": ["CMD-DEPLOYED-COMMIT", "CMD-DEPLOYED-SMOKE", "CMD-DEPLOYED-TESTS"], "rollback": "redeploy deploy.last_green", "kept_until": "T_judge_access 2026-11-20"}
  ],
  "anomaly_rollback_recovery": {
    "classification": [
      {"class": "product defect (failing gate on main, acceptance check, flaky test, review finding, live-run failure)", "action": "PROC-BUG-TRIAGE on bug-triager routes (Implementer Muse Code / Muse Spark 1.3 / max; Reviewer Codex CLI / GPT-6 Astra / high); fixed in the current round, never filed instead; packet carries reproduction, origin/escape, product vs test-only, red-then-green, prevention"},
      {"class": "harness, tool or environment failure (GAP exit, missing tool, OCR/Reverify cannot run)", "action": "typed gap with exact error; never a pass; tool issues filed per issue-labels policy"},
      {"class": "spike route fails", "action": "verdict (FAILS/PARTIAL/TIMEBOX) and its conditional; class C owner stop for RISK-AFC-P2-01/-02"},
      {"class": "live window missed or no qualifying event", "action": "labeled replay for logic; next live window for device evidence (RISK-AFC-P2-08)"},
      {"class": "Paid-plan prompt or paid service", "action": "stop, class F owner stop (RISK-AFC-P2-07)"},
      {"class": "route usage limit", "action": "next approved fallback with class B receipt or queue (RISK-AFC-P2-10)"},
      {"class": "secret, account data or absolute path in tracked material", "action": "block merge/publication; exposure → record without value, notify owner for rotation (RISK-AFC-P2-12)"},
      {"class": "Actions minutes exhausted (private repo)", "action": "landing blocked (no green checks); owner decides (earlier visibility flip or billing); local CMD-MAIN-GATE is not a substitute for required checks"}
    ],
    "rollback": {
      "main": "revert PR (no force-push), repair on a branch, reland",
      "deployment": "redeploy deploy.last_green with CMD-SAM-BUILD + CMD-SAM-DEPLOY at that commit; stores are dev data",
      "stick": "CMD-ADB-ROLLBACK: adb install -r -d apk.last_green (same signer keeps data and session); signer mismatch → uninstall, install, OA-10 relink",
      "spike": "no repair; superseding verdict PR only",
      "release": "unpublished drafts deleted and re-prepared; published releases are owner actions"
    },
    "landing_control": "main-landing lease, CMD-PR-CHECKS, gh pr merge --rebase or --merge, remote branch deleted (repo private: no ruleset until IE-P2-39)",
    "correction_limit": "at most three evidence-changing corrections per gate; the third is a class C owner question"
  },
  "cutoffs": [
    {
      "id": "CO-STICK-START",
      "applies_to": "P2-X01",
      "time": "2026-10-14T03:15:00Z",
      "rule": "latest X01 start that keeps the X03 desk part before TNF; requires approval, OA-1, OA-4",
      "on_miss": "Preserve all required provider trials in order. Record exact untried providers/routes, evidence and schedule consequences; material omissions require explicit owner decision identifying omitted topics and consequences. Owner notice alone grants no reduction; untried is not appAbsent/accessUnknown evidence."
    },
    {
      "id": "CO-PANEL",
      "applies_to": "P2-X04",
      "time": "first_install_at + 24 h",
      "rule": "AC-AFC-P2-SPIKE-02",
      "on_miss": "TIMEBOX → PanelMode.fullScreen"
    },
    {
      "id": "CO-M1",
      "applies_to": "W1",
      "time": "2026-10-14T20:00:00Z",
      "rule": "last Wave 1 slice merge; R1 by 2026-10-14T23:00:00Z",
      "on_miss": "W1 exit remains unmet until all required slices land; preserve release-checkpoint dates and wave membership; record forecast and request explicit scope decision for any material omission, never release completion from a partial set"
    },
    {
      "id": "CO-X03-DESK",
      "applies_to": "P2-X03 PR 1",
      "time": "2026-10-15T20:00:00Z",
      "rule": "stick free 4 h before TNF kickoff (~2026-10-16T00:15Z)",
      "on_miss": "Preserve all required provider trials in order. Record exact untried providers/routes, evidence and schedule consequences; material omissions require explicit owner decision identifying omitted topics and consequences. Owner notice alone grants no reduction; untried is not appAbsent/accessUnknown evidence."
    },
    {
      "id": "CO-M2",
      "applies_to": "W2",
      "time": "2026-10-17T01:00:00Z",
      "rule": "X06 verdict at T_yahoo then R2",
      "on_miss": "owner scope decision if > 12 h late"
    },
    {
      "id": "CO-M3-CODE",
      "applies_to": "P2-A03, P2-A04, P2-A05, P2-B04..B07",
      "time": "2026-10-18T09:00:00Z",
      "rule": "merged; L03 by 2026-10-18T11:00:00Z; rehearsal by 2026-10-18T15:00:00Z",
      "on_miss": "owner scope decision by priority list; X09 runs with what landed; missing behavior is a typed gap in the run record"
    },
    {
      "id": "CO-M3",
      "applies_to": "W3",
      "time": "2026-10-19T12:00:00Z",
      "rule": "X09 record and R3 merged",
      "on_miss": "R3 merges late; Wave 4 entry waits"
    },
    {
      "id": "CO-SUNDAY-FIX",
      "applies_to": "IE-P2-32",
      "time": "2026-10-19T20:00:00Z",
      "rule": "fixes merged, redeployed, reinstalled before MNF",
      "on_miss": "X10 re-checks with the defect open; fix lands after MNF with replay evidence"
    },
    {
      "id": "CO-ALEXA",
      "applies_to": "P2-X11",
      "time": "2026-10-21T12:00:00Z",
      "rule": "OD-AFC-03",
      "on_miss": "dropped"
    },
    {
      "id": "CO-M4",
      "applies_to": "W4",
      "time": "2026-10-21T23:00:00Z",
      "rule": "R4 merged",
      "on_miss": "owner scope decision"
    },
    {
      "id": "CO-M5-DOCS",
      "applies_to": "P2-D03, P2-D04, P2-D05, P2-SCR1",
      "time": "2026-10-22T16:00:00Z",
      "rule": "merged before R5",
      "on_miss": "R5 waits; every hour late shifts L05 and the assessments"
    },
    {
      "id": "CO-CANDIDATE",
      "applies_to": "P2-R5, P2-L05",
      "time": "R5 2026-10-22T17:00:00Z; L05 2026-10-22T19:00:00Z",
      "rule": "final APK on the stick before the TNF capture",
      "on_miss": "Final-APK demo requirement remains open. Earlier APK clips are labeled historical for their own candidate, not proof of apk.final. Record final APK status/hash, missed shots/window and consequences; exact owner scope decision required if final-candidate capture cannot be met."
    },
    {
      "id": "CO-DEMO",
      "applies_to": "P2-X12",
      "time": "2026-10-23T06:00:00Z",
      "rule": "manifest PR merged",
      "on_miss": "Final-APK demo requirement remains open. Earlier APK clips are labeled historical for their own candidate, not proof of apk.final. Record final APK status/hash, missed shots/window and consequences; exact owner scope decision required if final-candidate capture cannot be met."
    },
    {
      "id": "CO-M5",
      "applies_to": "W5",
      "time": "2026-10-23T12:00:00Z",
      "rule": "assessments returned; owner checklist handed over (7 h before T_deadline)",
      "on_miss": "owner informed immediately; submission proceeds on owner decision"
    }
  ],
  "final_candidate": {
    "ref": "candidate.final = merge commit of P2-R5 on main (tag v1.0.0 at OA-8 publication)",
    "includes": [
      "apk.final sha256 + signer cert SHA-256 + Reverify receipt (P2-L05)",
      "deploy.final: stack afc-dev, GitCommit tag, backend/ tree equal to candidate.final",
      "registry.v2 and fixtures.v2 digests",
      "contracts.b01 digests (or declared successors)",
      "spike verdicts SP-1..SP-7 (+SP-8 if run)",
      "spec revision built byte-identically (P2-D02)",
      "tools/ci/VENDORED.md, tools/spec/VENDORED.md pins"
    ],
    "invariants": [
      "CMD-MAIN-GATE PASS on candidate.final",
      "CMD-STUB-SCAN clean",
      "CMD-TREE-EQUAL candidate.final vs final main HEAD for tv-app/ and backend/ (later merges docs/evidence only)",
      "CMD-DEPLOYED-COMMIT tree check",
      "no absolute home path or credential shape in tracked files (hygiene)",
      "Final demo captures bind apk.final, not an earlier APK; any claim restriction requires exact owner scope decision",
      "APK inspection before tag does not close tagged-main subcriterion: OWNER_EVIDENCE_PENDING until OA-8 tag readback",
      "REVERIFY_CAPABILITY_GAP stays visible while APK semantics ungrounded; no frozen backend switch or ordinary-assurance substitution"
    ]
  },
  "lifecycle_assessment_inputs": {
    "sessions": "Lifecycle cadence on candidate.final, fresh sessions rejecting author ancestry; routes from the frozen snapshots (DEC-AFC-SD-041). opensource-hackathon (tv-app-ui, backend, device-integration-spikes, spec-and-docs and the Scribe side lane): Integration Engineer execution Codex CLI / GPT-6.1 Sol / high (ordered fallbacks Claude Code / Claude Opus 5.5 / medium, Cursor Agent / Grok 4.7 / high, Muse Code / Muse WonderFull / xhigh), cadence lifecycle; Assurance Test Engineer Codex CLI / GPT-6.1 Sol / xhigh (ordered fallbacks Cursor Agent / Grok 4.7 / high, Claude Code / Claude Opus 5.5 / medium, Muse Code / Muse WonderFull / xhigh), cadence lifecycle. Both sessions are enabled for every lane bound to this profile, so assurance covers spec-and-docs slices too; the former tech-writing assurance exemption no longer applies. bug-triager (defects, unchanged): Integration Engineer execution Codex CLI / GPT-6.1 Sol / high (ordered fallbacks Claude Code / Claude Opus 5.5 / medium, Muse Code / Muse Spark 1.3 / max), cadence lifecycle; Assurance Test Engineer Codex CLI / GPT-6.1 Sol / xhigh (ordered fallbacks Claude Code / Claude Opus 5.5 / medium, Muse Code / Muse Spark 1.3 / max), cadence lifecycle. Every opensource-hackathon Muse Code primary or fallback launches with --contributor-mode on or returns a typed configuration gap. Fallbacks activate only on verified unavailability or usage/rate-limit exhaustion. A session whose route model authored a slice under assessment records that overlap; independence is by fresh session, per skill.",
    "inputs": [
      "final_candidate block and every configuration_identity record",
      "journey.json execution_receipts for IE-P2-1..44 (merge SHAs, command output, digests)",
      "Reviewer record per PR with OCR delegate section and Reverify or not-applicable line",
      "spike verdicts",
      "PROC-E2E-LIVE records 2026-10-18 and 2026-10-19 with screencaps and geometry",
      "CMD-E2E-REPLAY receipts (IE-P2-29, IE-P2-32)",
      "visual-review captures per A01..A05 (AC-AFC-P2-VIS-01)",
      "CMD-REVERIFY-APK output on apk.final",
      "seit.json results per active register UID and AC-AFC-P2 row",
      "owner-accepted limitations (class C) and typed gaps",
      "bug-triager records with regression and prevention evidence",
      "CHANGELOG.md and release drafts v0.1.0..v1.0.0",
      "All 100 existing SEIT proof-row dispositions including every negative case; fallback proof closes only its own criteria",
      "Qualification and wave resource/cost receipts; review/landing reuse bound to unchanged candidate/inputs",
      "D02 verdict freeze inventory; P2-L01 approved payload and exact slice-to-issue readback",
      "OA-8/tag readback or explicit OWNER_EVIDENCE_PENDING; REVERIFY_CAPABILITY_GAP where semantic proof ungrounded"
    ],
    "approved_outcome": "technical plan §Outcome and the W5 exit criteria (GitHub milestone M13)"
  },
  "owner_dependencies": [
    {
      "id": "OA-1",
      "action": "Stick located, ADB debugging on LAN, model/Fire OS recorded",
      "blocks": [
        "P2-X01",
        "every stick step"
      ],
      "latest_safe": "2026-10-14T03:15:00Z"
    },
    {
      "id": "OA-2",
      "action": "Yahoo app submitted; on approval client id/secret into SSM, deployed /link callback registered as redirect URI after IE-P2-15, OAuth consent in a browser",
      "blocks": [
        "P2-X06 Yahoo path"
      ],
      "latest_safe": "2026-10-16T19:00:00Z (T_yahoo); manual path otherwise"
    },
    {
      "id": "OA-3",
      "action": "AWS Free-plan account and CLI profile afc-dev",
      "blocks": [
        "IE-P2-15",
        "IE-P2-18 visual review",
        "IE-P2-25",
        "P2-X09"
      ],
      "latest_safe": "2026-10-15T12:00:00Z (W2); hard 2026-10-17T12:00:00Z"
    },
    {
      "id": "OA-4",
      "action": "Provider apps installed and signed in; Prime Video before the first install (IE-P2-F06); others before P2-X03",
      "blocks": [
        "P2-X01 first install",
        "P2-X04",
        "P2-X02",
        "P2-X03"
      ],
      "latest_safe": "before P2-X01 first install"
    },
    {
      "id": "OA-5",
      "action": "LICENSE and visibility flip after W5 hygiene scan",
      "blocks": [
        "IE-P2-39 judge access",
        "ruleset enforcement"
      ],
      "latest_safe": "2026-10-22T18:00:00Z"
    },
    {
      "id": "OA-6",
      "action": "ESPN unofficial JSON terms review",
      "blocks": [
        "P2-D04 final"
      ],
      "latest_safe": "2026-10-22T12:00:00Z"
    },
    {
      "id": "OA-7",
      "action": "Devpost draft, video upload, submission; judge access through 2026-11-20",
      "blocks": [
        "submission"
      ],
      "latest_safe": "2026-10-23T19:00:00Z"
    },
    {
      "id": "OA-8",
      "action": "Authorize each release publication (v0.1.0..v1.0.0) and the v1.0.0 tag",
      "blocks": [
        "publication",
        "AC-AFC-P2-APK-01 tagged-main subcriterion (OWNER_EVIDENCE_PENDING until tag readback)"
      ],
      "latest_safe": "per wave release checkpoint W1..W5"
    },
    {
      "id": "OA-9",
      "action": "Camera capture of protected provider video (OD-AFC-P2-02 = A)",
      "blocks": [
        "P2-X04 modeB evidence if adb is black",
        "P2-X09 composition evidence",
        "P2-X12 camera shots"
      ],
      "latest_safe": "each window"
    },
    {
      "id": "OA-10",
      "action": "Store the manual-mode link passphrase as SSM SecureString under the B01 template's parameter name; perform /link confirmation for the stick when smoke, X09, X10 or a data-clearing rollback need it",
      "blocks": [
        "IE-P2-15 smoke confirm",
        "P2-X09",
        "P2-X10"
      ],
      "latest_safe": "before IE-P2-15"
    },
    {
      "id": "OA-11 (optional)",
      "action": "Supply a release signing keystore for the submitted APK; absent → debug signing config, README states sideload-only",
      "blocks": [
        "none (default applies)"
      ],
      "latest_safe": "2026-10-22T17:00:00Z"
    },
    {
      "id": "OD-items",
      "action": "OD-AFC-02..05, OA-AFC-A1, OD-AFC-P2-01..05 and the milestone due changes of IE-P2-F20/F21 at the integrated review",
      "blocks": [
        "IE-P2-1"
      ],
      "latest_safe": "with package approval"
    }
  ],
  "concurrency_findings": [
    {"id": "IE-P2-F01", "class": "write overlap", "verdict": "CONFIRMED", "slices": ["P2-X05", "P2-B01"], "compared": "P2-X05 `backend/fixtures/replay/` vs P2-B01 `backend/`; both W1, both in the first dispatch, no edge", "target": "slice-graph.md P2-B01 row, Write set", "corrected_text": "`backend/` except `backend/fixtures/`"},
    {"id": "IE-P2-F02", "class": "dependency (landing order)", "verdict": "CONFIRMED", "slices": ["P2-X05", "P2-B01", "P2-G01"], "compared": "After P2-G01 lands, any change under `backend/**` runs the backend area (`python3 -m pytest backend/tests/unit backend/tests/contract`, `cfn-lint backend/template.yaml`); a P2-X05 PR landing before P2-B01 creates `backend/` with only fixtures, so the area fails (no tests, no template) instead of `PASS no backend/ tree`", "target": "slice-graph.md P2-X05 row, Depends on", "corrected_text": "package approved (capture starts at dispatch); PR 1 lands after P2-B01 merged"},
    {"id": "IE-P2-F03", "class": "schedule infeasibility", "verdict": "CONFIRMED", "slices": ["P2-X05", "P2-B02T"], "compared": "P2-X05 stop needs a live capture; MNF 2026-10-12 (kickoff ~2026-10-13T00:15Z) needs approval before kickoff, else the first live window is TNF ending ~2026-10-16T03:30Z, after M1 due 2026-10-14T23:00Z; P2-B02T (M3 critical path) waits for P2-X05", "target": "slice-graph.md P2-X05 row Goal; P2-B02T Depends on; Dependencies list", "corrected_text": "P2-X05 Goal: `SP-5 in two pull requests. PR 1 (M1): record the ESPN scoreboard and summary endpoints and the capture tool; capture fixtures per CONTRACT-AFC-P2-FIXTURE from completed games (the 2026-10-11 games and the 2026-10-12 MNF game once final; that game live if this package is approved before kickoff); stop at an interim VERDICT.md (verdict PARTIAL, live timing pending) plus fixtures. PR 2 (M2): capture the Thu 2026-10-15 TNF game live, measure update timing, record correction evidence, append fixtures as later sequence files; stop at the final VERDICT.md.` P2-B02T Depends on: `P2-X05 PR 1 (first fixtures on main), P2-B01`. Dependencies list: replace `P2-X05 --> P2-B02T` with `P2-X05 (PR 1 fixtures) --> P2-B02T`."},
    {"id": "IE-P2-F04", "class": "schedule infeasibility / dependency", "verdict": "CONFIRMED", "slices": ["P2-X06", "P2-B03", "P2-B04T", "P2-L03", "P2-X09"], "compared": "`P2-X06 --> P2-B03` holds B03's merge until T_yahoo 2026-10-16T19:00Z; B04T needs B03, so B04 → B05/B07 → A03/A05 → L03 → X09 (2026-10-18T17:00Z) leaves ~46 h for four review-and-land generations plus stick reviews and no rehearsal. The source choice is runtime (AFC-PR-007, one active source per profile), not code. P2-X06's Yahoo path reads the owner's SSM secret 'by role only', so it needs B03's client deployed — the agent never reads the credential", "target": "slice-graph.md Dependencies list, the note under it, P2-X06 Depends on", "corrected_text": "Dependencies list: replace `P2-X06 --> P2-B03` with `P2-X06 --> P2-L03` and add `P2-B03 --> P2-X06` (Yahoo path only). Note: `The P2-X06 arrow carries only the deployed lineup-source configuration: P2-B03T/B03 build both sources from recorded responses, start at P2-B01 and land when green; P2-L03 applies the P2-X06 verdict as deploy configuration. The Yahoo path of P2-X06 runs through the deployed role (P2-B01 auth and P2-B03 client deployed by P2-L02 or a redeploy); the agent never reads the SSM secret.` P2-X06 Depends on: `Yahoo path: OA-2, P2-B03 merged and deployed (P2-L02 or a redeploy under aws-afc-dev); manual path: T_yahoo`."},
    {"id": "IE-P2-F05", "class": "shared resource / schedule", "verdict": "CONFIRMED", "slices": ["P2-X03", "P2-X07", "P2-B06T", "P2-A04T", "P2-A01", "P2-A02"], "compared": "P2-X03 holds fire-tv-stick until its stop (VERDICT + registry), which includes the TNF check ending ~2026-10-16T03:30Z; P2-X07 (stick order), the A01/A02 review steps and the registry consumers B06T and A04T all wait behind it", "target": "slice-graph.md P2-X03 Goal, Depends on; P2-X07 Depends on; Dependencies list", "corrected_text": "P2-X03 Goal: `SP-3 in two pull requests. PR 1: provider links in order Prime Video, ESPN, DirecTV Stream, YouTube TV, then local broadcast, with desk evidence (on-demand or live-channel content); write the registry per CONTRACT-AFC-P2-PROVIDER-REGISTRY with verified_outcome from that evidence; release fire-tv-stick; stop at an interim VERDICT.md (Prime Video TNF check pending) plus registry. PR 2: live Prime Video TNF check 2026-10-15, holding fire-tv-stick and live-game-window for the game window only; amend only the Prime Video registry entry (verified_outcome, verified_at) and the verdict; stop at the final VERDICT.md.` P2-X03 Depends on: `P2-X02 (stick order); P2-B01 merged before the PR 1 registry commit; OA-4`. P2-X07 Depends on: `P2-X03 PR 1 desk work complete (stick released)`. Dependencies list: `P2-X03 --> P2-X07` becomes `P2-X03 (desk part, stick released) --> P2-X07`; `P2-X03 --> P2-B06T` becomes `P2-X03 (PR 1 registry on main) --> P2-B06T`; `P2-X03 --> P2-A04T` becomes `P2-X03 (PR 1 registry on main) --> P2-A04T`; `P2-X03 --> P2-D02` becomes `P2-X03 (PR 2 final verdict) --> P2-D02`."},
    {"id": "IE-P2-F06", "class": "owner dependency (timing)", "verdict": "CONFIRMED", "slices": ["P2-X01", "P2-X04"], "compared": "The spike_panel_max clock starts at P2-X01's first install; P2-X04 needs Prime Video playing; OA-4 is listed as needed by P2-X02..X04 (M2), so the clock can run while X04 is blocked", "target": "technical plan §Owner-action entry criteria OA-4 row 'Needed by'; slice-graph.md P2-X01 Depends on", "corrected_text": "OA-4 Needed by: `P2-X01's first install (Prime Video signed in at minimum; the spike_panel_max clock starts at that install); ESPN, DirecTV Stream and YouTube TV before P2-X03`. P2-X01 Depends on: `OA-1; OA-4 (Prime Video) before the first install`."},
    {"id": "IE-P2-F07", "class": "shared resource (lease priority)", "verdict": "CONFIRMED", "slices": ["P2-X04", "P2-A01"], "compared": "P2-A01 depends on 'P2-X01 (stick usable)' and holds fire-tv-stick for its review step in W1; P2-X04 needs the stick right after P2-X01 inside first_install_at + 24 h; no rule says which goes first", "target": "technical plan Waves table, Wave 2 row; slice-graph.md P2-A01 Depends on", "corrected_text": "Wave 2 row, prepend: `P2-X04 holds fire-tv-stick from P2-X01's release until its verdict or first_install_at + spike_panel_max, without interruption; P2-A01's on-device review queues behind it and runs between P2-X04 and P2-X02.` P2-A01 Depends on: `P2-A01T; P2-X01 (SDK installed, stick usable); its review step runs after P2-X04 releases the stick; lands after P2-G01 and P2-B01 (ApiClient builds against openapi.yaml)`."},
    {"id": "IE-P2-F08", "class": "shared resource (lease semantics)", "verdict": "CONFIRMED", "slices": ["P2-X03", "P2-X05"], "compared": "`live-game-window` is granted 'to one slice at a time', but P2-X03 (stick) and P2-X05 (host-only ESPN capture) both need TNF 2026-10-15; serialized, one misses the window", "target": "technical plan §Program plan, Leases table, `live-game-window` row", "corrected_text": "| `live-game-window` | A live NFL window | Shared by slices whose other leases are disjoint (P2-X05 host-only capture may hold it together with P2-X03, P2-X09, P2-X10 or P2-X12 on the stick); it serializes only competing demands on fire-tv-stick or aws-afc-dev during the game |"},
    {"id": "IE-P2-F09", "class": "shared resource (missing lease)", "verdict": "CONFIRMED", "slices": ["P2-A03T", "P2-A04T", "P2-A05T"], "compared": "Their write sets include `tv-app/app/src/androidTest/...` and A03T's goal names an 'instrumented test for notification on the stick; stop at CMD-RED'; instrumented tests need the device, but their Leases are '—'", "target": "slice-graph.md P2-A03T, P2-A04T, P2-A05T rows, Leases", "corrected_text": "fire-tv-stick (instrumented CMD-RED run only)"},
    {"id": "IE-P2-F10", "class": "write overlap (hidden hot files, TV)", "verdict": "CONFIRMED", "slices": ["P2-A01", "P2-A02", "P2-A03", "P2-A04", "P2-A05"], "compared": "A02/A03/A04 lease tv-app-manifest 'if needed' and A05 may need manifest edits for a modeB route, yet none of their write sets contains `AndroidManifest.xml` or the Gradle files. A03 and A05 call WatchLauncher (A04) and every screen calls `net/` (A01), with no edge between A03, A04 and A05. `local.properties` holds an absolute sdk.dir that hygiene rejects. The starter's license notice belongs in `THIRD_PARTY_NOTICES.md`, which no write set lists", "target": "slice-graph.md P2-A01 Goal and Write set; P2-A02..P2-A05 Write set", "corrected_text": "P2-A01 Goal append: `; net/ApiClient.kt and net/Dto.kt implement every CONTRACT-AFC-P2-API operation of backend/src/api/openapi.yaml with request and response types (envelope; Profile and Settings incl. scoringPreset; Alert with route and access basis; PanelState; ProviderRoute; RoutingOutcome six values; InstalledApps); MainActivity.kt routes Link, Profile/Settings and Panel to stub screens; stubs ProfileSettingsScreen, AppDetector, AlertService, AlertNotifier, WatchLauncher (launch(route: ProviderRoute): RoutingOutcome) and LineupPanel exist in their packages with final signatures and the AFC-STUB marker; build.gradle.kts and libs.versions.toml declare every runtime and test dependency A02..A05 need; AndroidManifest.xml declares every component and permission DES-AFC-P2-TV and DES-AFC-P2-ALERTPATH name; tv-app/.gitignore ignores local.properties, .gradle/ and build/; the starter's license is added to THIRD_PARTY_NOTICES.md.` P2-A01 Write set: `tv-app/`, `THIRD_PARTY_NOTICES.md`, `evidence/visual/P2-A01/`. P2-A02, P2-A03, P2-A04, P2-A05 Write set append: `tv-app/app/src/main/AndroidManifest.xml` and `tv-app/app/build.gradle.kts`, `tv-app/gradle/libs.versions.toml` (own entries only, under tv-app-manifest / tv-app-gradle). Only P2-A05 edits MainActivity.kt."},
    {"id": "IE-P2-F11", "class": "missing interface configuration", "verdict": "CONFIRMED", "slices": ["P2-A01", "P2-L02", "P2-L05"], "compared": "No Phase 2 artifact says how the APK learns the backend URL (searched design.md, technical plan and slice-graph.md for base URL, BuildConfig and ApiUrl: no hit); this is Phase 1 IE-F06, still open", "target": "design.md DES-AFC-P2-TV (new bullet); slice-graph.md P2-A01 Goal", "corrected_text": "design.md DES-AFC-P2-TV add bullet: `- The API base URL comes from Gradle property afcApiBaseUrl into BuildConfig.AFC_API_BASE_URL; empty shows \"Backend not configured\"; on-device and release builds pass -PafcApiBaseUrl=<afc-dev stack output ApiUrl>; the APK carries no secret.` P2-A01 Goal append: `; AFC_API_BASE_URL is read from Gradle property afcApiBaseUrl.`"},
    {"id": "IE-P2-F12", "class": "missing shared interface (backend)", "verdict": "CONFIRMED", "slices": ["P2-B01", "P2-B02", "P2-B03", "P2-B04", "P2-B05", "P2-B06", "P2-B07"], "compared": "Six tables are written and read by different slices (Events: B02→B04; Lineups: B03→B07; Alerts: B05→router; Panels: B07→router), but no frozen item shape or accessor exists. The PolicyFunction chain matcher → policy → alert records (+route from resolver) → panel projections is owned by no slice, while B05 does not depend on B06 or B07. `requirements*.txt` and `tests/conftest.py` are shared files with no owner after B01", "target": "slice-graph.md P2-B01 Goal; technical plan Leases table `backend-template` row", "corrected_text": "P2-B01 Goal append: `; backend/src/store/ implements one accessor per table operation of DES-AFC-P2-BACKEND (Profiles, Links, Events, Alerts, Lineups, Panels) with item shapes from models/AFC-Data.sysml; backend/src/pipeline/handler.py (PolicyFunction) calls matcher.resolve, alert_policy.evaluate, provider_resolver.resolve and panel.project in that order; the ApiFunction router calls each module's public function; each module stub has its final signature, the AFC-STUB marker and raises NotImplementedError (router → 503 not_implemented); registry.json holds an empty provider list in the contract shape; samconfig.toml names stack afc-dev and profile afc-dev; backend/.gitignore ignores .aws-sam/, __pycache__/ and .pytest_cache/; requirements.txt and requirements-dev.txt pin every runtime and test dependency of B02..B07.` Leases row: `| backend-template | backend/template.yaml, backend/samconfig.toml, backend/requirements.txt, backend/requirements-dev.txt, backend/src/api/openapi.yaml, backend/src/store/, backend/src/pipeline/, backend/tests/conftest.py | P2-B01 (creates); later edits one at a time, declared in the PR body |`"},
    {"id": "IE-P2-F13", "class": "configuration identity", "verdict": "CONFIRMED", "slices": ["P2-L02", "P2-L03"], "compared": "No artifact names the SAM stack, and no deploy records which commit it deployed (the only grep hits for 'afc-dev' are the profile name); rollback to 'the last green commit' cannot be verified", "target": "slice-graph.md P2-L02 and P2-L03 rows, Goal and Commands", "corrected_text": "Goal append: `; deploy with sam deploy --config-env default --tags GitCommit=<sha> (stack afc-dev from samconfig.toml); record ApiUrl and the deployed commit.` Commands append: `CMD-STACK-OUTPUTS, CMD-DEPLOYED-COMMIT`."},
    {"id": "IE-P2-F15", "class": "owner dependency (missing)", "verdict": "CONFIRMED", "slices": ["P2-L02", "P2-X09", "P2-X10", "P2-X06"], "compared": "DES-AFC-P2-AUTH puts the manual-mode link on an 'owner-set link passphrase held in SSM SecureString', but OA-1..OA-9 have no action for it. The L02 deployed link smoke and every linked-device live run need it, and reading it is credential access (owner only). OA-2 does not cover registering the deployed callback as the Yahoo redirect URI, which is only known after P2-L02", "target": "technical plan §Owner-action entry criteria (new row; OA-2 row)", "corrected_text": "Add row: `| OA-10 | Store the manual-mode link passphrase as an SSM SecureString parameter in aws-afc-dev under the name P2-B01's template declares, and perform the /link confirmation for the stick when P2-L02 smoke, P2-X09, P2-X10 or a data-clearing APK rollback needs a linked device. | P2-L02 link smoke (M2) | Deployed link confirmation; linked-device live runs |`. OA-2 append: ` After P2-L02 reports the stack's ApiUrl, register the deployed /link callback as the Yahoo app redirect URI.`"},
    {"id": "IE-P2-F16", "class": "owner dependency / configuration identity", "verdict": "CONFIRMED", "slices": ["P2-L05"], "compared": "P2-L05 builds 'the release APK', but no artifact defines its signing (grep for keystore, signing and apksigner over the plan, design, slice graph and spec: no hit). Creating a release keystore is credential creation, which is owner only (technical plan §Exclusions)", "target": "slice-graph.md P2-L05 Goal; technical plan §Owner-action entry criteria (new row)", "corrected_text": "P2-L05 Goal: `Build the release APK at the M5 candidate commit, signed with the development host's Android debug signing configuration (no new credential; README states sideload-only) unless the owner supplies a release keystore (OA-11); record sha256 and the signer certificate SHA-256 (CMD-APK-CERT); run Reverify on that APK for minSdk, package, permissions and services; stop at the receipt (Reverify failure is a typed gap).` New row: `| OA-11 (optional) | Supply a release signing keystore for the submitted APK. | P2-L05 (M5) | Debug signing configuration is used |`."},
    {"id": "IE-P2-F17", "class": "configuration identity / dependency", "verdict": "CONFIRMED", "slices": ["P2-R5", "P2-L05", "P2-X12", "P2-D03"], "compared": "P2-R5 (after P2-L05) bumps versionName in `tv-app/app/build.gradle.kts`, so the APK P2-L05 built is not built from the v1.0.0 tagged commit (AC-AFC-P2-APK-01). P2-X12 captures demo clips before P2-L05, so the clips do not show the submitted APK", "target": "slice-graph.md Dependencies list; P2-R5, P2-L05, P2-X12 rows (Goal / Depends on); technical plan Wave 5 row", "corrected_text": "Dependencies list: replace `P2-X12 --> P2-L05`, `P2-D03 --> P2-L05`, `P2-L05 --> P2-R5` with `P2-D03 --> P2-R5`, `P2-D04 --> P2-R5`, `P2-D05 --> P2-R5`, `P2-SCR1 --> P2-R5`, `P2-R5 --> P2-L05`, `P2-L05 --> P2-X12`. P2-R5 Goal: `Prepare release v1.0.0 via release-process: move [Unreleased] under 1.0.0 and bump versionName/versionCode; its merge commit is the M5 candidate; after P2-L05, put the APK sha256 in the draft release notes (no further commit); tag v1.0.0 names the candidate commit at publication; stop at draft; publish only on OA-8.` P2-L05 Depends on: `P2-R5 merged`. P2-X12 Depends on: `P2-D05; P2-L05 (captures use the final APK); OA-9 for camera shots`. Wave 5 row: `P2-D03, P2-D04, P2-D05 in parallel; P2-SCR1 after M4; P2-R5 after those four merge; P2-L05 at the P2-R5 merge commit; P2-X12 on the final APK in the Thu 2026-10-22 TNF window, landing a docs-only manifest PR after the candidate.`"},
    {"id": "IE-P2-F18", "class": "write overlap / dependency", "verdict": "CONFIRMED", "slices": ["P2-R1", "P2-R2", "P2-R3", "P2-R4", "P2-R5"], "compared": "All five write `CHANGELOG.md` and `tv-app/app/build.gradle.kts`, with no R<n> --> R<n+1> edge (R2 waits on M2 slices only, not on R1, which also waits on P2-L01 and P2-D01). While R<n>'s branch is open, next-milestone PRs keep appending CHANGELOG entries under main-landing, so R<n> conflicts", "target": "slice-graph.md Dependencies list; P2-R1..P2-R5 Leases", "corrected_text": "Dependencies list add: `P2-R1 --> P2-R2`, `P2-R2 --> P2-R3`, `P2-R3 --> P2-R4`, `P2-R4 --> P2-R5`. P2-R1..P2-R5 Leases: `tv-app-gradle, main-landing (held from branch cut until its merge; no other pull request merges in between)`."},
    {"id": "IE-P2-F19", "class": "dependency (read before write)", "verdict": "CONFIRMED", "slices": ["P2-D02"], "compared": "P2-D02's stop condition is `gate.sh spec` with a byte-identical rebuild, which runs the vendored `tools/spec/**`; open PR #11 re-vendors `tools/spec/**` (spec_lint.py, VENDORED.md, templates). D02 depends only on PR #10", "target": "slice-graph.md P2-D02 row, Depends on", "corrected_text": "P2-X02, P2-X03 (PR 2 final verdict), P2-X04 verdicts; PR #10 and PR #11 merged (the byte-identical rebuild uses the merged tools/spec)"},
    {"id": "IE-P2-F20", "class": "schedule infeasibility", "verdict": "CONFIRMED", "slices": ["P2-X06", "P2-R2"], "compared": "M2 is due at T_yahoo (2026-10-16T19:00:00Z), but P2-X06's manual verdict is triggered at T_yahoo, and the verdict PR, its review and P2-R2 come after it", "target": "technical plan Milestones table, M2 row, Due (UTC)", "corrected_text": "2026-10-17T01:00:00Z (T_yahoo + 6 h for the P2-X06 verdict pull request and P2-R2)"},
    {"id": "IE-P2-F21", "class": "schedule infeasibility", "verdict": "PLAUSIBLE", "slices": ["P2-X09", "P2-R3"], "compared": "The last Sunday window ends ~2026-10-19T03:30Z. The X09 run-record PR (review, one repair, gate) and then P2-R3 (main-landing hold, review) must both merge by the M3 due time 2026-10-19T06:00Z, which leaves ~2.5 h", "target": "technical plan Milestones table, M3 row, Due (UTC)", "corrected_text": "2026-10-19T12:00:00Z"},
    {"id": "IE-P2-F22", "class": "missing evidence (landing control)", "verdict": "CONFIRMED", "slices": ["all"], "compared": "`gh api repos/1wgrumph/amazon-fantasy-companion/rulesets` and `/branches/main/protection` return HTTP 403 'Upgrade to GitHub Pro or make this repository public'; the repo shows allow_squash_merge=true and delete_branch_on_merge=false, so 'PR-only main', required checks and no-squash are not enforced by GitHub while the repo is private", "target": "technical plan Leases table, `main-landing` row, Holders", "corrected_text": "Landing procedure; one merge at a time; before each merge CMD-PR-CHECKS (every check on the head commit passes, including gate / hygiene and each path-selected gate / <area>); merge only with gh pr merge --rebase or --merge; delete the remote branch. While the repository is private, GitHub enforces no ruleset; after the OA-5 visibility flip the Orchestrator applies the main ruleset (PR-only, required checks, no squash)."},
    {"id": "IE-P2-F23", "class": "configuration identity (toolchain)", "verdict": "CONFIRMED", "slices": ["P2-G01", "P2-B01..P2-B07"], "compared": "CONTRACT-AFC-P2-GATE-AREAS runs `python3 -m pytest`. On the development host `python3` is 3.14.4, while the Lambda runtime and the CI setup are Python 3.12, so local hook results and CI results come from different interpreters and pinned wheels", "target": "design.md CONTRACT-AFC-P2-GATE-AREAS, `gate.sh backend` sentence", "corrected_text": "`gate.sh backend`: when `backend/` exists, runs `python3.12 -m pytest backend/tests/unit backend/tests/contract` and `cfn-lint backend/template.yaml`; exit 3 when python3.12 or cfn-lint is missing."},
    {"id": "IE-P2-F24", "class": "missing evidence (ignore rules)", "verdict": "CONFIRMED", "slices": ["P2-X01", "P2-X02", "P2-X03", "P2-X04", "P2-X07", "P2-X12", "all evidence writers"], "compared": "The root `.gitignore` ignores `*.log` except `docs/plans/**/specialists/*.log`, so adb or run logs named *.log under `evidence/` or `spikes/` are silently left untracked. Spike Gradle probes create `local.properties`, whose absolute sdk.dir trips hygiene PATH-HOME-POSIX. P2-X12's clips must stay untracked, but no write set holds an ignore rule for them", "target": "design.md DES-AFC-P2-VISUAL (append); slice-graph.md P2-X01, P2-X02, P2-X03, P2-X04, P2-X07 and P2-X12 Write set", "corrected_text": "DES-AFC-P2-VISUAL append: `Text evidence (adb, dumpsys, run logs) uses the .txt suffix; the root .gitignore ignores *.log.` P2-X01/X02/X03/X04/X07 Write set append: `spikes/<sp>/.gitignore (ignores local.properties, .gradle/, build/)`. P2-X12 Write set: `evidence/demo/ (manifest.md and .gitignore ignoring *.mp4 and *.mov)`."},
    {"id": "IE-P2-F25", "class": "interface (gate hygiene vs test data)", "verdict": "CONFIRMED", "slices": ["P2-B01T", "P2-B03T", "P2-A01T"], "compared": "`tools/ci/check_paths.py` flags `device_token`, `access_token` and `refresh_token` followed by `[\"']?\\s*[:=]\\s*[\"']?` and 32 or more token characters (CRED-DEVICE-TOKEN, CRED-OAUTH-TOKEN). 256-bit session tokens in tests, or recorded Yahoo OAuth responses, written as literals fail hygiene on every commit", "target": "slice-graph.md P2-B01T, P2-B03T, P2-A01T Goal", "corrected_text": "Goal append: `; token values in tests and recorded responses are generated at run time or are shorter than 32 characters (hygiene CRED-* shapes).`"},
    {"id": "IE-P2-F26", "class": "missing evidence (visual review needs backend)", "verdict": "CONFIRMED", "slices": ["P2-A01", "P2-A02", "P2-L02"], "compared": "P2-A01's review covers the link states 'code shown, expired, linked', which need a reachable backend. The first deployment is P2-L02 (M2, OA-3), no local backend route is designed, and authorized glue is none. P2-A02's profile states also need the API", "target": "slice-graph.md P2-A01 Goal; P2-A02 Depends on", "corrected_text": "P2-A01 Goal append: `; PROC-VISUAL-REVIEW in M1 covers the shell, \"Backend not configured\" and network-error states; the code-shown, expired and linked captures run as post-step V&V of P2-L02 (IE-P2-15) against aws-afc-dev.` P2-A02 Depends on: `P2-A02T; P2-X07 for detector behavior; P2-L02 (deployed API for the visual review)`."},
    {"id": "IE-P2-F28", "class": "dependency (shared history)", "verdict": "CONFIRMED", "slices": ["planning package", "PR #10", "PR #11"], "compared": "The planning branch base 771c28958f78e611048528aedbd9ed4490f308e1 is PR #10's head (`gh pr view 10 --json headRefOid`). ST5-F1/F2 commits still land on #10, so the planning PR carries #10's history and conflicts if they diverge", "target": "technical plan §Entry criteria item 2", "corrected_text": "The Orchestrator lands PR #10 (with ST5-F1 and ST5-F2) and PR #11 first, merges origin/main into plan/2026-10-12-afc-phase-2, commits the package after scrubbing absolute local paths from specialists/ prompts and logs, and lands it on main through a pull request that also seeds CHANGELOG.md, before any Phase 2 lane branches from main."},
    {"id": "IE-P2-F30", "class": "missing evidence (readback shape)", "verdict": "PLAUSIBLE", "slices": ["P2-L01"], "compared": "AC-AFC-P2-MS-01 requires a field-for-field readback of due dates given as UTC times (e.g. 2026-10-14T23:00:00Z). GitHub milestone due_on is a calendar date (the web UI has no time), so the time of day is expected not to read back. No milestone exists yet to confirm this", "target": "technical plan AC-AFC-P2-MS-01 Statement", "corrected_text": "After the owner approves this package, the program shall create GitHub milestones M1..M5 in 1wgrumph/amazon-fantasy-companion whose title, due date (calendar date; the UTC due time is stated in the description) and description (entry criteria, exit criteria, slice list) equal the approved milestone table, and shall record a gh api readback that matches it field for field; no milestone is created before approval."}
  ],
  "wave_gate_costs": [
    {
      "wave": 1,
      "release_checkpoint": "W1",
      "github_milestones": ["M01", "M02", "M03", "M04"],
      "integration_steps": [
        "IE-P2-1",
        "IE-P2-2",
        "IE-P2-3",
        "IE-P2-4",
        "IE-P2-5",
        "IE-P2-6",
        "IE-P2-7",
        "IE-P2-8"
      ],
      "slices": [
        "P2-L01",
        "P2-X01",
        "P2-X05",
        "P2-D01",
        "P2-G01T",
        "P2-G01",
        "P2-A01T",
        "P2-A01",
        "P2-B01T",
        "P2-B01",
        "P2-R1"
      ],
      "added_gate_seconds": 720,
      "estimate_source": "seit.json/levels/0/expected_gate_time_delta",
      "estimate_text": "Estimate +2 min host gate tests, +8 min Gradle unit/lint/assemble, +2 min Python unit/contract; first engine-suite qualification separately 7 runs; actual baseline not measured.",
      "resource_groups": [
        "aws-afc-dev",
        "fire-tv-stick",
        "host-gate-fixtures",
        "host-gradle",
        "host-pytest"
      ],
      "seit_case_resource_groups": [
        "aws-afc-dev (isolated fixture-profile data; deployment lease); host-pytest local TDD",
        "host-gate-fixtures; unique temporary repository/root per test"
      ],
      "resource_case_refs": [
        "SEIT-AFC-PR-012",
        "SEIT-AFC-PR-013",
        "SEIT-AFC-PR-058",
        "SEIT-AFC-PR-064",
        "SEIT-AFC-P2-GATE-01",
        "SEIT-AFC-P2-PATH-01",
        "SEIT-RISK-AFC-P2-05",
        "SEIT-RISK-AFC-P2-12"
      ],
      "qualification_ref": "seit.json/procedures_and_commands/PROC-RELIABILITY",
      "limits": "Planning forecast only, not measured/hardware benchmark; additive work budget, not wall-clock promise. W4 fixed increment 0; changed-suite requalification extra and replay <=300s estimate. W5 120s docs estimate excludes unmeasured final binary/deployed/independent assurance. Qualification five consecutive + two concurrent copies is separate from ordinary qualified gate reuse."
    },
    {
      "wave": 2,
      "release_checkpoint": "W2",
      "github_milestones": ["M03", "M04", "M05", "M06"],
      "integration_steps": [
        "IE-P2-9",
        "IE-P2-10",
        "IE-P2-11",
        "IE-P2-12",
        "IE-P2-13",
        "IE-P2-14",
        "IE-P2-15",
        "IE-P2-16",
        "IE-P2-17",
        "IE-P2-18",
        "IE-P2-19",
        "IE-P2-20"
      ],
      "slices": [
        "P2-X04",
        "P2-X02",
        "P2-X03",
        "P2-X07",
        "P2-X06",
        "P2-B02T",
        "P2-B02",
        "P2-B03T",
        "P2-B03",
        "P2-A02T",
        "P2-A02",
        "P2-L02",
        "P2-R2"
      ],
      "added_gate_seconds": 900,
      "estimate_source": "seit.json/levels/1/expected_gate_time_delta",
      "estimate_text": "Estimate +5 min deployed suite and +10 min stick suite per relevant candidate; engine qualification 7 runs where applicable. Live-window observation scheduled separately.",
      "resource_groups": [
        "aws-afc-dev",
        "fire-tv-stick",
        "host-gate-fixtures",
        "host-gradle",
        "host-pytest"
      ],
      "seit_case_resource_groups": [
        "aws-afc-dev (isolated fixture-profile data; deployment lease); host-pytest local TDD",
        "fire-tv-stick (cross-process lock); aws-afc-dev when system",
        "host-gate-fixtures; unique temporary repository/root per test"
      ],
      "resource_case_refs": [
        "SEIT-AFC-PR-001",
        "SEIT-AFC-PR-006",
        "SEIT-AFC-PR-007",
        "SEIT-AFC-PR-008",
        "SEIT-AFC-PR-011",
        "SEIT-AFC-PR-012",
        "SEIT-AFC-PR-013",
        "SEIT-AFC-PR-016",
        "SEIT-AFC-PR-017",
        "SEIT-AFC-PR-018",
        "SEIT-AFC-PR-019",
        "SEIT-AFC-PR-020",
        "SEIT-AFC-PR-023",
        "SEIT-AFC-PR-029",
        "SEIT-AFC-PR-034",
        "SEIT-AFC-PR-037",
        "SEIT-AFC-PR-044",
        "SEIT-AFC-PR-064",
        "SEIT-AFC-PR-065",
        "SEIT-AFC-P2-PATH-01",
        "SEIT-RISK-AFC-P2-05"
      ],
      "qualification_ref": "seit.json/procedures_and_commands/PROC-RELIABILITY",
      "limits": "Planning forecast only, not measured/hardware benchmark; additive work budget, not wall-clock promise. W4 fixed increment 0; changed-suite requalification extra and replay <=300s estimate. W5 120s docs estimate excludes unmeasured final binary/deployed/independent assurance. Qualification five consecutive + two concurrent copies is separate from ordinary qualified gate reuse."
    },
    {
      "wave": 3,
      "release_checkpoint": "W3",
      "github_milestones": ["M07", "M08", "M09", "M10"],
      "integration_steps": [
        "IE-P2-21",
        "IE-P2-22",
        "IE-P2-23",
        "IE-P2-24",
        "IE-P2-25",
        "IE-P2-26",
        "IE-P2-27",
        "IE-P2-28",
        "IE-P2-29",
        "IE-P2-30",
        "IE-P2-31"
      ],
      "slices": [
        "P2-B04T",
        "P2-B04",
        "P2-B05T",
        "P2-B05",
        "P2-B06T",
        "P2-B06",
        "P2-B07T",
        "P2-B07",
        "P2-A03T",
        "P2-A03",
        "P2-A04T",
        "P2-A04",
        "P2-A05T",
        "P2-A05",
        "P2-L03",
        "P2-X09",
        "P2-R3"
      ],
      "added_gate_seconds": 2100,
      "estimate_source": "seit.json/levels/2/expected_gate_time_delta",
      "estimate_text": "Estimate three changed instrumented areas at +10 min each, serialized on stick; backend suite +5 min. Reuse same qualified run for review/landing only on identical inputs.",
      "resource_groups": [
        "aws-afc-dev",
        "fire-tv-stick",
        "host-gate-fixtures",
        "host-gradle",
        "host-pytest"
      ],
      "seit_case_resource_groups": [
        "aws-afc-dev (isolated fixture-profile data; deployment lease); host-pytest local TDD",
        "fire-tv-stick (cross-process lock); aws-afc-dev when system",
        "host-gate-fixtures; unique temporary repository/root per test"
      ],
      "resource_case_refs": [
        "SEIT-AFC-PR-001",
        "SEIT-AFC-PR-004",
        "SEIT-AFC-PR-006",
        "SEIT-AFC-PR-007",
        "SEIT-AFC-PR-008",
        "SEIT-AFC-PR-011",
        "SEIT-AFC-PR-012",
        "SEIT-AFC-PR-013",
        "SEIT-AFC-PR-014",
        "SEIT-AFC-PR-016",
        "SEIT-AFC-PR-017",
        "SEIT-AFC-PR-018",
        "SEIT-AFC-PR-019",
        "SEIT-AFC-PR-020",
        "SEIT-AFC-PR-023",
        "SEIT-AFC-PR-024",
        "SEIT-AFC-PR-025",
        "SEIT-AFC-PR-026",
        "SEIT-AFC-PR-028",
        "SEIT-AFC-PR-029",
        "SEIT-AFC-PR-032",
        "SEIT-AFC-PR-033",
        "SEIT-AFC-PR-034",
        "SEIT-AFC-PR-037",
        "SEIT-AFC-PR-044",
        "SEIT-AFC-PR-046",
        "SEIT-AFC-PR-058",
        "SEIT-AFC-PR-060",
        "SEIT-AFC-PR-061",
        "SEIT-AFC-PR-064",
        "SEIT-AFC-PR-065",
        "SEIT-AFC-P2-PATH-01",
        "SEIT-RISK-AFC-P2-05"
      ],
      "qualification_ref": "seit.json/procedures_and_commands/PROC-RELIABILITY",
      "limits": "Planning forecast only, not measured/hardware benchmark; additive work budget, not wall-clock promise. W4 fixed increment 0; changed-suite requalification extra and replay <=300s estimate. W5 120s docs estimate excludes unmeasured final binary/deployed/independent assurance. Qualification five consecutive + two concurrent copies is separate from ordinary qualified gate reuse."
    },
    {
      "wave": 4,
      "release_checkpoint": "W4",
      "github_milestones": ["M11"],
      "integration_steps": [
        "IE-P2-32",
        "IE-P2-33",
        "IE-P2-34",
        "IE-P2-35",
        "IE-P2-36"
      ],
      "slices": [
        "P2-X10",
        "P2-D02",
        "P2-X11",
        "P2-R4"
      ],
      "added_gate_seconds": 0,
      "estimate_source": "seit.json/levels/3/expected_gate_time_delta",
      "estimate_text": "No fixed increase assumed: rerun changed-suite qualification and record actual delta; replay functional checks <=5 min estimate, live MNF observation separate.",
      "resource_groups": [
        "aws-afc-dev",
        "fire-tv-stick",
        "host-gate-fixtures",
        "host-gradle"
      ],
      "seit_case_resource_groups": [
        "aws-afc-dev (isolated fixture-profile data; deployment lease); host-pytest local TDD",
        "host-gate-fixtures; unique temporary repository/root per test"
      ],
      "resource_case_refs": [
        "SEIT-AFC-PR-025",
        "SEIT-AFC-PR-026",
        "SEIT-AFC-PR-046",
        "SEIT-AFC-P2-PATH-01"
      ],
      "qualification_ref": "seit.json/procedures_and_commands/PROC-RELIABILITY",
      "limits": "Planning forecast only, not measured/hardware benchmark; additive work budget, not wall-clock promise. W4 fixed increment 0; changed-suite requalification extra and replay <=300s estimate. W5 120s docs estimate excludes unmeasured final binary/deployed/independent assurance. Qualification five consecutive + two concurrent copies is separate from ordinary qualified gate reuse."
    },
    {
      "wave": 5,
      "release_checkpoint": "W5",
      "github_milestones": ["M12", "M13"],
      "integration_steps": [
        "IE-P2-37",
        "IE-P2-38",
        "IE-P2-39",
        "IE-P2-40",
        "IE-P2-41",
        "IE-P2-42",
        "IE-P2-43",
        "IE-P2-44"
      ],
      "slices": [
        "P2-D03",
        "P2-D04",
        "P2-D05",
        "P2-X12",
        "P2-SCR1",
        "P2-L05",
        "P2-R5"
      ],
      "added_gate_seconds": 120,
      "estimate_source": "seit.json/levels/4/expected_gate_time_delta",
      "estimate_text": "Docs-only gate estimated <=2 min; final binary/deployed/assurance commands actual times recorded; no repeated full engine gate for evidence-only merge with unchanged trees.",
      "resource_groups": [
        "aws-afc-dev",
        "fire-tv-stick",
        "host-gate-fixtures",
        "host-gradle"
      ],
      "seit_case_resource_groups": [
        "aws-afc-dev (isolated fixture-profile data; deployment lease); host-pytest local TDD",
        "fire-tv-stick (cross-process lock); aws-afc-dev when system",
        "host-gate-fixtures; unique temporary repository/root per test"
      ],
      "resource_case_refs": [
        "SEIT-AFC-PR-001",
        "SEIT-AFC-PR-004",
        "SEIT-AFC-PR-006",
        "SEIT-AFC-PR-007",
        "SEIT-AFC-PR-008",
        "SEIT-AFC-PR-011",
        "SEIT-AFC-PR-012",
        "SEIT-AFC-PR-013",
        "SEIT-AFC-PR-014",
        "SEIT-AFC-PR-016",
        "SEIT-AFC-PR-017",
        "SEIT-AFC-PR-018",
        "SEIT-AFC-PR-019",
        "SEIT-AFC-PR-020",
        "SEIT-AFC-PR-023",
        "SEIT-AFC-PR-024",
        "SEIT-AFC-PR-025",
        "SEIT-AFC-PR-026",
        "SEIT-AFC-PR-028",
        "SEIT-AFC-PR-029",
        "SEIT-AFC-PR-032",
        "SEIT-AFC-PR-033",
        "SEIT-AFC-PR-034",
        "SEIT-AFC-PR-037",
        "SEIT-AFC-PR-044",
        "SEIT-AFC-PR-046",
        "SEIT-AFC-PR-058",
        "SEIT-AFC-PR-060",
        "SEIT-AFC-PR-061",
        "SEIT-AFC-PR-064",
        "SEIT-AFC-PR-065",
        "SEIT-AFC-P2-GATE-01",
        "SEIT-AFC-P2-PATH-01",
        "SEIT-RISK-AFC-P2-05",
        "SEIT-RISK-AFC-P2-12"
      ],
      "qualification_ref": "seit.json/procedures_and_commands/PROC-RELIABILITY",
      "limits": "Planning forecast only, not measured/hardware benchmark; additive work budget, not wall-clock promise. W4 fixed increment 0; changed-suite requalification extra and replay <=300s estimate. W5 120s docs estimate excludes unmeasured final binary/deployed/independent assurance. Qualification five consecutive + two concurrent copies is separate from ordinary qualified gate reuse."
    }
  ]
}
```

IDs IE-P2-F14, F27 and F29 are not used: those analyses were folded into F04,
F07 and the X09 entry criteria (IE-P2-29) during the single pass.
