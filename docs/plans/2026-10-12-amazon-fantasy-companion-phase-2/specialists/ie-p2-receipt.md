---
type: planning-receipt
title: Integration Engineer planning receipt, Phase 2 (AFC-2026-10-11)
okf_status: draft
tags: [planning, afc, phase-2, integration, receipt]
---

# IE planning receipt — Phase 2

- **outcome:** `GAPS`
- **verdict:** The Phase 2 integration plan is complete: 44 ordered steps
  (IE-P2-1..44) place all 52 slices, with every contract checked, plus
  deployments, rollback, cut-offs, the final candidate, Lifecycle-end inputs
  and owner dependencies. The independent concurrency check found 28 defects
  in the inputs (26 CONFIRMED, 2 PLAUSIBLE). Each has exact corrected text.
  The affected slices must not be dispatched until their corrections are
  applied (see the table below). No owner decision blocks the plan: the new
  owner items (OA-10, optional OA-11, milestone due changes) belong at the
  integrated review, which is already pending.
- **candidate_ref:** inputs at `plan/2026-10-12-afc-phase-2`
  `771c28958f78e611048528aedbd9ed4490f308e1` + working tree (2026-10-12);
  `origin/main` `17b40b4bdf8214b300bee05d594e13100d5d0d93`.
- **changed_paths:**
  `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/integration-plan.md`,
  `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/ie-p2-receipt.md`
  (both new, uncommitted, per authority).
- **tests:** none authored (role boundary). Self-checks on the JSON block are
  listed under Commands run.

## Commands run (read-only)

| Command | Result |
|---|---|
| `git fetch origin`; `git log origin/main`; `git ls-tree origin/main` | main `17b40b4`. S09 has landed (gate.sh areas spec/docs/hygiene, hooks, ci.yml); no CHANGELOG.md |
| `git config --get core.hooksPath` | `.githooks` (set; STATE said unset) |
| `gh pr list --state all` / `gh pr view 10,11` | #9 merged; #10 open, head `771c289` = plan base; #11 open, touches `tools/spec/**` |
| `gh api …/rulesets`, `…/branches/main/protection` | HTTP 403 "Upgrade to GitHub Pro or make this repository public" |
| `gh api repos/…` | private, allow_squash_merge=true, delete_branch_on_merge=false |
| `gh api …/milestones?state=all` | none |
| `git show origin/main:tools/ci/{gate.sh,check_docs.py,check_paths.py}`, `.githooks/pre-commit`, `ci.yml`, `.gitignore`, `THIRD_PARTY_NOTICES.md` | area matching, CRED/PATH shapes, `*.log` ignore read |
| Tool versions on the host | python3 3.14.4, python3.12 3.12.3, JDK 21, Docker present; adb, sdkmanager, sam, cfn-lint absent |
| python: parse journey `frozen_snapshots` | IE execution / ATE routes per lane profile recorded in the plan |
| python: pairwise write-set prefix comparison over 52 slices plus reachability over the arrows | overlaps with no edge: X05×B01; R1..R5 pairwise |
| `git show f885e48:…/integration-plan.md` | Phase 1 IE-F01..F18 mapped to Phase 2 |
| python: JSON block validation | 13 required keys, no extra keys; no forbidden key; 44 steps in order; `after` refers only to earlier steps; all 52 slices in `merges`; P2-X03 and P2-X05 appear twice on purpose (two-PR spikes) |
| grep for absolute home paths in both output files | none |

## Findings

Full records, including the two write sets compared and the target file, are
in the `concurrency_findings` array of `integration-plan.md`. Summary, with
the exact corrected text repeated for each:

| ID | Class | Target file | Corrected text |
|---|---|---|---|
| IE-P2-F01 | write overlap | slice-graph.md P2-B01 Write set | `backend/` except `backend/fixtures/` |
| IE-P2-F02 | dependency | slice-graph.md P2-X05 Depends on | package approved (capture starts at dispatch); PR 1 lands after P2-B01 merged |
| IE-P2-F03 | schedule | slice-graph.md P2-X05 Goal, P2-B02T Depends on, Dependencies | Goal: `SP-5 in two pull requests. PR 1 (M1): record the ESPN scoreboard and summary endpoints and the capture tool; capture fixtures per CONTRACT-AFC-P2-FIXTURE from completed games (the 2026-10-11 games and the 2026-10-12 MNF game once final; that game live if this package is approved before kickoff); stop at an interim VERDICT.md (verdict PARTIAL, live timing pending) plus fixtures. PR 2 (M2): capture the Thu 2026-10-15 TNF game live, measure update timing, record correction evidence, append fixtures as later sequence files; stop at the final VERDICT.md.` B02T Depends on: `P2-X05 PR 1 (first fixtures on main), P2-B01`. Replace `P2-X05 --> P2-B02T` with `P2-X05 (PR 1 fixtures) --> P2-B02T`. |
| IE-P2-F04 | schedule / dependency | slice-graph.md Dependencies, note, P2-X06 Depends on | Replace `P2-X06 --> P2-B03` with `P2-X06 --> P2-L03`; add `P2-B03 --> P2-X06` (Yahoo path only). Note: `The P2-X06 arrow carries only the deployed lineup-source configuration: P2-B03T/B03 build both sources from recorded responses, start at P2-B01 and land when green; P2-L03 applies the P2-X06 verdict as deploy configuration. The Yahoo path of P2-X06 runs through the deployed role (P2-B01 auth and P2-B03 client deployed by P2-L02 or a redeploy); the agent never reads the SSM secret.` X06 Depends on: `Yahoo path: OA-2, P2-B03 merged and deployed (P2-L02 or a redeploy under aws-afc-dev); manual path: T_yahoo`. |
| IE-P2-F05 | shared resource / schedule | slice-graph.md P2-X03 Goal and Depends on, P2-X07 Depends on, Dependencies | Goal: `SP-3 in two pull requests. PR 1: provider links in order Prime Video, ESPN, DirecTV Stream, YouTube TV, then local broadcast, with desk evidence (on-demand or live-channel content); write the registry per CONTRACT-AFC-P2-PROVIDER-REGISTRY with verified_outcome from that evidence; release fire-tv-stick; stop at an interim VERDICT.md (Prime Video TNF check pending) plus registry. PR 2: live Prime Video TNF check 2026-10-15, holding fire-tv-stick and live-game-window for the game window only; amend only the Prime Video registry entry (verified_outcome, verified_at) and the verdict; stop at the final VERDICT.md.` X03 Depends on: `P2-X02 (stick order); P2-B01 merged before the PR 1 registry commit; OA-4`. X07 Depends on: `P2-X03 PR 1 desk work complete (stick released)`. Arrows: `P2-X03 (desk part, stick released) --> P2-X07`; `P2-X03 (PR 1 registry on main) --> P2-B06T`; `P2-X03 (PR 1 registry on main) --> P2-A04T`; `P2-X03 (PR 2 final verdict) --> P2-D02`. |
| IE-P2-F06 | owner dependency | technical plan OA-4 Needed by; slice-graph.md P2-X01 Depends on | OA-4: `P2-X01's first install (Prime Video signed in at minimum; the spike_panel_max clock starts at that install); ESPN, DirecTV Stream and YouTube TV before P2-X03`. X01: `OA-1; OA-4 (Prime Video) before the first install`. |
| IE-P2-F07 | lease priority | technical plan Wave 2 row; slice-graph.md P2-A01 Depends on | Prepend: `P2-X04 holds fire-tv-stick from P2-X01's release until its verdict or first_install_at + spike_panel_max, without interruption; P2-A01's on-device review queues behind it and runs between P2-X04 and P2-X02.` A01: `P2-A01T; P2-X01 (SDK installed, stick usable); its review step runs after P2-X04 releases the stick; lands after P2-G01 and P2-B01 (ApiClient builds against openapi.yaml)`. |
| IE-P2-F08 | lease semantics | technical plan Leases `live-game-window` row | `| live-game-window | A live NFL window | Shared by slices whose other leases are disjoint (P2-X05 host-only capture may hold it together with P2-X03, P2-X09, P2-X10 or P2-X12 on the stick); it serializes only competing demands on fire-tv-stick or aws-afc-dev during the game |` |
| IE-P2-F09 | missing lease | slice-graph.md P2-A03T/A04T/A05T Leases | fire-tv-stick (instrumented CMD-RED run only) |
| IE-P2-F10 | hidden hot files (TV) | slice-graph.md P2-A01 Goal/Write set; P2-A02..A05 Write set | See plan JSON: A01 Goal append (ApiClient + DTOs for every operation, navigation, AFC-STUB stubs incl. `WatchLauncher.launch(route: ProviderRoute): RoutingOutcome`, all dependencies, complete manifest, `tv-app/.gitignore`, THIRD_PARTY_NOTICES.md). A01 Write set `tv-app/`, `THIRD_PARTY_NOTICES.md`, `evidence/visual/P2-A01/`. A02..A05 append `tv-app/app/src/main/AndroidManifest.xml`, `tv-app/app/build.gradle.kts`, `tv-app/gradle/libs.versions.toml` (own entries only, under the leases); only P2-A05 edits MainActivity.kt. |
| IE-P2-F11 | interface configuration | design.md DES-AFC-P2-TV; slice-graph.md P2-A01 Goal | `- The API base URL comes from Gradle property afcApiBaseUrl into BuildConfig.AFC_API_BASE_URL; empty shows "Backend not configured"; on-device and release builds pass -PafcApiBaseUrl=<afc-dev stack output ApiUrl>; the APK carries no secret.` A01 append `; AFC_API_BASE_URL is read from Gradle property afcApiBaseUrl.` |
| IE-P2-F12 | shared interface (backend) | slice-graph.md P2-B01 Goal; technical plan `backend-template` lease row | See plan JSON: B01 append (store/ accessors, pipeline/handler.py composition, router calls, AFC-STUB stubs, empty registry, samconfig stack/profile afc-dev, backend/.gitignore, all pins). Lease row covers template.yaml, samconfig.toml, requirements*.txt, openapi.yaml, store/, pipeline/, tests/conftest.py. |
| IE-P2-F13 | configuration identity | slice-graph.md P2-L02, P2-L03 Goal and Commands | Goal append `; deploy with sam deploy --config-env default --tags GitCommit=<sha> (stack afc-dev from samconfig.toml); record ApiUrl and the deployed commit.` Commands append `CMD-STACK-OUTPUTS, CMD-DEPLOYED-COMMIT`. |
| IE-P2-F15 | owner dependency | technical plan owner-action table | New OA-10 row (link passphrase in SSM; owner-performed /link confirmations); OA-2 append on the Yahoo redirect URI (exact text in plan JSON) |
| IE-P2-F16 | owner dependency / identity | slice-graph.md P2-L05 Goal; technical plan new OA-11 row | L05 Goal and OA-11 (optional) row, exact text in plan JSON (debug signing configuration unless the owner supplies a keystore; CMD-APK-CERT) |
| IE-P2-F17 | identity / dependency | slice-graph.md Dependencies; P2-R5, P2-L05, P2-X12 rows; technical plan Wave 5 | Replace `P2-X12 --> P2-L05`, `P2-D03 --> P2-L05`, `P2-L05 --> P2-R5` with `P2-D03/D04/D05/SCR1 --> P2-R5`, `P2-R5 --> P2-L05`, `P2-L05 --> P2-X12`; R5, L05, X12 and Wave 5 text in plan JSON |
| IE-P2-F18 | write overlap / dependency | slice-graph.md Dependencies; P2-R1..R5 Leases | Add `P2-R1 --> P2-R2`, `P2-R2 --> P2-R3`, `P2-R3 --> P2-R4`, `P2-R4 --> P2-R5`. Leases `tv-app-gradle, main-landing (held from branch cut until its merge; no other pull request merges in between)` |
| IE-P2-F19 | dependency | slice-graph.md P2-D02 Depends on | P2-X02, P2-X03 (PR 2 final verdict), P2-X04 verdicts; PR #10 and PR #11 merged (the byte-identical rebuild uses the merged tools/spec) |
| IE-P2-F20 | schedule | technical plan M2 Due | 2026-10-17T01:00:00Z (T_yahoo + 6 h for the P2-X06 verdict pull request and P2-R2) |
| IE-P2-F21 | schedule (PLAUSIBLE) | technical plan M3 Due | 2026-10-19T12:00:00Z |
| IE-P2-F22 | landing control | technical plan `main-landing` lease row | Landing procedure; one merge at a time; before each merge CMD-PR-CHECKS (every check on the head commit passes, including gate / hygiene and each path-selected gate / <area>); merge only with gh pr merge --rebase or --merge; delete the remote branch. While the repository is private, GitHub enforces no ruleset; after the OA-5 visibility flip the Orchestrator applies the main ruleset (PR-only, required checks, no squash). |
| IE-P2-F23 | toolchain identity | design.md CONTRACT-AFC-P2-GATE-AREAS | `gate.sh backend`: when `backend/` exists, runs `python3.12 -m pytest backend/tests/unit backend/tests/contract` and `cfn-lint backend/template.yaml`; exit 3 when python3.12 or cfn-lint is missing. |
| IE-P2-F24 | ignore rules | design.md DES-AFC-P2-VISUAL; slice-graph.md X01/X02/X03/X04/X07/X12 Write set | `Text evidence (adb, dumpsys, run logs) uses the .txt suffix; the root .gitignore ignores *.log.` Spikes append `spikes/<sp>/.gitignore (ignores local.properties, .gradle/, build/)`; X12 `evidence/demo/ (manifest.md and .gitignore ignoring *.mp4 and *.mov)` |
| IE-P2-F25 | gate hygiene vs test data | slice-graph.md P2-B01T, P2-B03T, P2-A01T Goal | append `; token values in tests and recorded responses are generated at run time or are shorter than 32 characters (hygiene CRED-* shapes).` |
| IE-P2-F26 | visual review needs backend | slice-graph.md P2-A01 Goal; P2-A02 Depends on | A01 append `; PROC-VISUAL-REVIEW in M1 covers the shell, "Backend not configured" and network-error states; the code-shown, expired and linked captures run as post-step V&V of P2-L02 (IE-P2-15) against aws-afc-dev.` A02 `P2-A02T; P2-X07 for detector behavior; P2-L02 (deployed API for the visual review)` |
| IE-P2-F28 | shared history | technical plan Entry criteria item 2 | The Orchestrator lands PR #10 (with ST5-F1 and ST5-F2) and PR #11 first, merges origin/main into plan/2026-10-12-afc-phase-2, commits the package after scrubbing absolute local paths from specialists/ prompts and logs, and lands it on main through a pull request that also seeds CHANGELOG.md, before any Phase 2 lane branches from main. |
| IE-P2-F30 | readback shape (PLAUSIBLE) | technical plan AC-AFC-P2-MS-01 | `…whose title, due date (calendar date; the UTC due time is stated in the description) and description … equal the approved milestone table …` (full sentence in plan JSON) |

### Dispatch hold until corrected

| Slices | Findings |
|---|---|
| P2-B01, P2-B01T | F01, F12, F25 |
| P2-X05 | F02, F03 |
| P2-X01 | F06, F24 |
| P2-A01, P2-A01T | F07, F10, F11, F25, F26 |
| P2-X03, P2-X07 | F05, F24 |
| P2-B03, P2-B03T, P2-X06 | F04, F25 |
| P2-A02..A05, P2-A03T..A05T | F09, F10 |
| P2-L02, P2-L03 | F13, F15 |
| P2-D02 | F19 |
| P2-R1..R5, P2-L05, P2-X12 | F16, F17, F18 |
| P2-G01 | F23 |
| P2-L01 | F30 |

P2-G01T and P2-D01 have no hold.

## Remaining risks

- **Approval timing.** Package approval, OA-1 and OA-4 are needed by
  2026-10-14T03:15Z (CO-STICK-START), or the X03 desk part no longer fits
  before TNF.
- **The panel spike may use its full 24 h**, which pushes A01's stick review
  close to the M1 due time.
- **Actions minutes.** The private repo has 2,000 min/month. A Gradle tvapp
  job on every tv-app PR and every push to main could exhaust them before the
  visibility flip. Not measured: reading the billing API needs scopes this
  session did not use.
- **M3 critical path is tight even with F03–F05.** The last greens land around
  2026-10-17/18. CO-M3-CODE at 2026-10-18T09:00Z triggers the owner
  scope-reduction decision.
- **Protected provider video** may make adb captures black. Composition
  evidence then needs OA-9 camera shots (RISK-AFC-P2-09).
- **Assessment window.** The Lifecycle-end assessments run from about
  2026-10-22T19:00Z to the M5 due time; a late defect compresses that window.

## Blocker

None for the plan itself. Dispatch of the slices listed above waits for their
corrections in `slice-graph.md`, `design.md` and the technical plan
(the Planning and Design node and the Plan Integrator own those files).

## developer_feedback

- **IE-P2-OBS-001** (needs work; GitHub, private repo on GitHub Free).
  Rulesets and branch protection are unavailable: HTTP 403 "Upgrade to GitHub
  Pro or make this repository public". A plan that assumes "main is PR-only by
  ruleset" silently gets no enforcement. Evidence: `gh api
  repos/1wgrumph/amazon-fantasy-companion/rulesets`, 2026-10-12.
- **IE-P2-OBS-002** (positive; `tools/ci/check_paths.py`). The checker reports
  `file:line:CODE` without echoing values, and its credential shapes are
  explicit regexes, so planning could predict which test data would trip it
  (F25).
- **IE-P2-OBS-003** (needs work; slice-graph authoring). Write sets name
  directories but not the hot files inside the scaffold. A mechanical prefix
  comparison passes while manifest, Gradle, store and pipeline conflicts stay
  hidden (F10, F12). A "hot files" column in the slice table would expose them.
- Tools exercised: git (read), gh CLI 2.46.0 (read), python3 (JSON and
  overlap checks), bearing-lite integration-engineer skill 1.1.6,
  integration-engineering method skill.
