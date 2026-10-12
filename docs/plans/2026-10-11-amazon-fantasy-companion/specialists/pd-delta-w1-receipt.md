# Planning and Design DELTA receipt: Wave 1 owner decisions DEC-AFC-SD-026..028

- **Role:** Planning and Design node (`BEARING_ROLE=planning_and_design`), DELTA mode. It applies owner decisions made during Wave 1 execution. It is not a correction round.
- **Inputs:** `specialists/pd-delta-w1-prompt.md`; `journey.json` DEC-AFC-SD-026, -027, -028 and the Wave 1 `wave_receipt` (execution_receipts); slice returns `packets/S01-run.log`, `S02-run.log`, `S03-run.log`, `S06-run.log`; Alphazedehq `skills/release-process/tests/test_release_process.py` and `trigger-requests.json` (the stock pattern).
- **Revision against:** `origin/main` = `888bc19`. Its package artifacts are the approved Phase 1 package 173e005 (DEC-AFC-APPROVAL-001, manifest digest `4128aa9c…e55e84`). Only `authority.json` differs, by the approval receipt.
- **Return:** `DELTA_APPLIED`
- **New manifest (candidate) digest:** `d7d92af72feaf95259869bf2fe80c14b0abaea3b7c309549ddfb5866a9c334d9`
- **Rendered DoD Manifest:** sha256 `50ea1240bf7664775734a98b46c3ba3f98f3b310898039c86743bf542ad2252b`, template 1.0.1

## Revision diff vs origin/main (888bc19)

| Item | Change |
|---|---|
| 1. SD-026 `CMD-SKILL-SIZE` | The ID is kept. The command now runs the per-skill stock unittest `python3 -m unittest discover -s <skill_dir>/tests -t <skill_dir>/tests -p 'test_<skill_snake>.py' -k test_creator_validation_and_repository_metadata`. Then the pinned BRAN runtime sha256 must match `bran-release-pin.json`, and `bran check . bran-strict` must pass. The test asserts < 60 lines, < 650 words (S41 router < 25), no `[TODO]`, `name` equal to the skill and non-empty `type`, `title`, `okf_status`, `tags`. It runs `quick_validate.py` (check=True) on a temp copy that holds only the portable fields. `quick_validate` never runs on the repository SKILL.md. It uses the host python3 with Debian PyYAML, an unchanged installed tool, as the stock test does. |
| 1. SD-026 `CMD-SKILL-TRIGGER` | The ID is kept. The 1-turn `claude -p --max-turns 1 --allowedTools Skill` probe is removed. The new command copies SKILL.md and `tests/trigger-requests.json` (only those two files, never the checker) to a scratch directory. There, a fresh evaluator session (`claude -p … --output-format json --max-turns 5 --allowedTools Read --disallowedTools Bash,Write,Edit,WebFetch,WebSearch < /dev/null`) prints its classification. The command extracts it from `session.json` with `jq` into `results.json`, then copies that file to `<evidence_dir>/trigger-results-<skill>.json` and keeps the harness version and session output. `<SKILL_PREFIX>_TRIGGER_RESULTS` then points `test_trigger_classifications` at it, and the test expects `{request_1: MATCH, request_2: NO_MATCH}`. This mirrors `RELEASE_TRIGGER_RESULTS`. S06 adds a reciprocal check: the same evaluator, given the requirements-system `use-requirements-system` SKILL.md, must return the inverse. |
| 1. SD-026 proof and design text | Evidence, expected and negative strings are updated in SEIT-AFC-D4-01.S, -02.S, -03.S, -05.T, D5-01.S, D5-03.T and RISK-15, in both proof_cases and traceability_matrix. Also updated: `vv_methods` evaluation and test, `applicable_documents` standards[3], and the DES-AFC-D4 and DES-AFC-D5 validation bullets. `CMD-D5-TEST` gains `--ignore=…/test_spec_authoring.py`, because pytest would otherwise collect the stock unittest without its results file. |
| 1. Write sets | S01, S02, S03 and S41 gain `tests/test_<skill_snake>.py` and `tests/trigger-requests.json`. S06's `skills/spec-authoring/` already covers them, and the entry now names them. `dod_manifest.tasks` and `specialists/slice-graph.md` are synced. Each of S01, S02, S03, S06 and S41 gets a `verification_note`. |
| 2. `CMD-D4-AGNOSTIC` | The check is now per slice. `<slice_paths>` is the slice's own directory: S01 `skills/setup-pre-commit`, S02 `skills/setup-a-repo`, S03 `skills/ship-pull-request`, S11 its hook files, S41 `skills/ci-cd`. A combined run over the three D4 directories happens only at the Wave 1 exit, on the Alphazedehq main checkout after S01..S03 merge. The change reaches `waves[0].exit`, the IE-P1-3 post-step V&V, the seit `integration_vv_sequence`, SEIT-AFC-D4-06 and `used_by`. |
| 3. PyYAML (S02) | A new `environments.python_wheels` entry defines `<afc_uv_env>` = `UV_OFFLINE=1 UV_NO_CACHE=1 UV_FIND_LINKS=<wheel_dir> UV_PYTHON="$(command -v python3)"`. `<wheel_dir>` is a host directory outside every repository. It is filled once by `python3 -m pip download --only-binary=:all: --dest <wheel_dir> 'pytest==9.0.3' 'pyyaml==6.0.3'` and scanned by CMD-SCAN (scan-software-supply-chain) before first use, and the scan receipt records the wheel sha256s. `CMD-D4B-TEST`, `CMD-D5-TEST` and `CMD-D5-AGNOSTIC` run `env <afc_uv_env> uv run …` with exact pins. Offline with no cache, uv can use only the scanned wheels, and an empty directory fails resolution. CMD-SCAN `used_by` adds S02. |
| 4. SD-028 | The S06 write set replaces `Alphazedehq:skills/use-requirements-system/SKILL.md` with `requirements-system:skills/use-requirements-system/SKILL.md`. The lease is renamed `requirements-system-skills/use-requirements-system`. A new `cross_repo_write` block requires a worktree `<workspace>/worktrees/requirements-system-afc-s06-nontrigger` and an edit to the real file, never the Alphazedehq symlink, with its own PR. The stop condition names both PRs. IE-P1-4 adds the requirements-system PR checks, `rs.d5nt` merge identity, and a fast-forward of the checkout the symlink resolves to, done only if it is clean (otherwise a typed gap). `authority.json` adds the repository (S06 only), its one allowed path, a prohibited line for every other requirements-system path, a scope line, and granting decisions SD-026..028. design.md and the TP Wave 1 text are updated. |
| 5. SD-027 | ST-2 (TP, `implementation.json` `phase2_sequence`, design DES-AFC-PHASE2) is now the Markdown register `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/requirements-register.md` in this repository. It has one table with the columns UID, statement, rationale, verification method, allocation and sources. The Requirements Engineer gates it, and it is not bound to the Requirements System host. ST-4 and D1 still cite its UIDs. OD-AFC-12 is `closed_by DEC-AFC-SD-027` in `implementation.json` and in the seit `decision_baseline`, with a resolution; its old recommendation is marked superseded. The TP OD row is closed. The spec-track scope in `authority.json` drops "running the local packaged-default Requirements System host for them (cross-repo rule 14)". The plan held no `.sdoc` PROC/CMD to remove. Cross-repo rule 14 is not touched. |
| Bookkeeping | `revision_against` → 888bc19 / `4128aa9c…` APPROVED, decided by SD-026..028. The prior pair moves to `revision_history`, and `revision_diff` is rewritten. `planning_review.repair_revision` and `candidate_digest` are rebound, and so are the identity rows (Revision against, Repository, Authority now effective, the input digests, seit, candidate). Requirements stay at 33 rows, with no statement changed, so no Requirements Engineer gate is needed. The plan still has 55 proof cases and 47 commands, all IDs stable. |

`git diff --stat origin/main -- <plan dir>` (package files):

```text
amazon-fantasy-companion-dod-manifest.html | 44   amazon-fantasy-companion-technical-plan.md | 14
authority.json | 18   design.md | 44   implementation.json | 174   seit.json | 128   specialists/slice-graph.md | 10
```

## Digests

| Artifact | origin/main | New |
|---|---|---|
| technical plan | `0051816b…bc82c` | `4dbaf7e00d1a956c329db3ce525ad0aae2f0b6cd0c37f738c64e86193991fe07` |
| design.md | `4b397fb8…57ca` | `7c53f5eb93c8341f9db9c5f38f5740bdea1222760ef2419223b7527ef32923d3` |
| views/views.json | `d54a59f8…2ce6` | unchanged |
| seit.json | `17710bbb…b158` | `fc03a46162b0b2f031b3f2916f1d9b23b745189815653ec6fc6b535ebe3ccdcf` |
| candidate (manifest digest) | `4128aa9c…e55e84` | `d7d92af72feaf95259869bf2fe80c14b0abaea3b7c309549ddfb5866a9c334d9` |
| authority.json | — | `c8b4443090d6dda5b6134a3c88c701b47dea5b6c0ca7e6b4bb52e39f213ccbc1` |
| implementation.json | — | `1b68d0ff14bcaab1daa95cf10d16b606b19187a2ff13fc2b8a14f4e8b5182ea3` |

## Commands and results

```text
node <bearing-lite 1.1.6>/hooks/plan-package.cjs <plan dir>                        exit 0  PASS, findings [], manifest_digest d7d92af7…c334d9
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json          exit 0  RENDER_WRITE sha256:50ea1240…2252b
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json --check  exit 0  RENDER_CHECK_PASS sha256:50ea1240…2252b
python3 jsonschema Draft202012Validator (<bearing-lite 1.1.6>/schemas)             implementation 0 | seit 0 | authority 0 | journey 0
slice_proof_map vs seit_proof_rows (13 slices); dod_manifest.tasks vs slice write sets   0 mismatches | 0 mismatches
slice seit_proof_rows/command_ids -> seit                                          0 orphans; 55 proofs, 47 commands
rule 12 home-path shape scan (TP, design, *.json, manifest, views/, evidence/, slice-graph.md)   0 hits
Self-test, stock pattern on Alphazedehq skills/release-process (read-only):
  CMD-SKILL-SIZE form (unittest -k test_creator_validation_and_repository_metadata; pin check; bran-strict)   exit 0
  CMD-SKILL-TRIGGER form (fresh read-only `claude -p` evaluator, Claude Code 2.1.296) -> {"request_1":"MATCH","request_2":"NO_MATCH"}; test_trigger_classifications OK
  CMD-D4-AGNOSTIC per-slice form on skills/setup-a-repo                            exit 1: SKILL.md:16 names a repository (baseline text that S02 owns and must remove)
  <afc_uv_env> with an empty <wheel_dir>                                            resolution fails (fail closed, as intended)
```

The positive `<afc_uv_env>` path, with real scanned wheels, was not exercised here. Downloading the wheels is an acquisition, and it belongs to S02's CMD-SCAN.

## Write set

Changed: TP, `design.md`, `seit.json`, `implementation.json`, `authority.json`, the manifest HTML, `specialists/slice-graph.md`. New: this receipt. Not edited: `journey.json` (the Orchestrator's), `views/`, `packets/*.md`, `specialists/integration-plan.md` (historical IE output), and `specialists/pd-delta-w1-run.log` (its working-tree change is this session's stdout redirect). No commits, pushes or branch operations. The pre-edit backup and the delta scripts are outside the repository.

## Orchestrator follow-ups

- **Authority expiry:** `authority.json` expiry includes "a change to the approved package digest without owner re-approval". DEC-AFC-SD-026..028 are owner decisions made after approval, and they ask for this delta. Record them in `journey.json` as the basis for the new digest `d7d92af7…`.
- **Re-dispatch:** the packets `packets/S01.md`, `S02.md`, `S03.md` and `S06.md` predate this delta. Regenerate them from `implementation.json` before you re-dispatch.
- **S02 finding:** S02's per-slice `CMD-D4-AGNOSTIC` currently fails on `skills/setup-a-repo/SKILL.md:16` (`alphazede/azedge`). This is S02's own AC-AFC-D4-06 work and no longer a cross-slice blocker. The match S02 saw before, in `ship-pull-request`, belongs to S03.

## developer_feedback

| ID | Tool | Used for | Worked well | Needs work (task / steps / expected / actual) | Severity | Workaround | Suggestion | Would build again |
|---|---|---|---|---|---|---|---|---|
| PD-W1-OBS-1 | Bearing Lite 1.1.6 artifact grammar | ST-2 register form | n/a | Grammar rule 7 requires a draft `.sdoc` register for a specification Lifecycle ("Markdown sections are not lint-checkable"). The owner chose Markdown (SD-027). When the spec-track plan freezes, `journey_type: specification` and `requirement_register` may fail or want an `.sdoc` path. | Major | Record SD-027 as the override in the spec-track plan | Let rule 7 accept an owner-selected Markdown register, gated by the Requirements Engineer | Yes, the gate surfaced the conflict early |
| PD-W1-OBS-2 | uv 0.11.6 | Offline scanned-wheel runs | `UV_OFFLINE`, `UV_NO_CACHE`, `UV_FIND_LINKS`, `UV_PYTHON` are documented | `UV_NO_INDEX` is not a documented uv env var, so you cannot express `--no-index` through env. I used `UV_NO_CACHE=1` with offline mode instead. | Minor | `UV_NO_CACHE=1` | n/a | Yes |
| PD-W1-OBS-3 | plan-package.cjs | Digest rebind | PASS/FAIL with exact digests | Each seit.json edit forces two passes: rebind the inputs, read the digest, rebind the candidate. This repeats PD-SD025-OBS-1. | Minor | Two-pass script | A `rebind` subcommand | Yes |
| PD-W1-OBS-4 | Plan (this Lifecycle) | Pre-dispatch validation | n/a | Three Wave 1 blockers were plan defects a dry run would have caught before dispatch: the validator rejects HQ metadata, the 1-turn trigger probe, and the symlinked write-set path. | Major | This delta | Before dispatch, run each slice's verification commands once against the baseline skill, and resolve every write-set path with `realpath` | Yes |

AWS services: n/a. Tools exercised: python3 (json, jsonschema, hashlib), node (plan-package, render-dod-manifest), Claude Code 2.1.296 `claude -p` (one evaluator run), pinned BRAN 0.2.0 `check bran-strict`, uv 0.11.6, git, grep, sha256sum.

## Security review disposition (stop-hook finding, HIGH: agent permission bypass)

- **Finding:** the first `CMD-SKILL-TRIGGER` form launched the evaluator with `--dangerously-skip-permissions` and let it write `results.json`. That session reads skill text still being authored, so it could have run arbitrary tools on the host.
- **Disposition: fixed.** The evaluator now runs with `--allowedTools Read`, `--disallowedTools Bash,Write,Edit,WebFetch,WebSearch` and `--max-turns 5`. It prints the JSON; the command extracts `.result` from `session.json` with `jq` and writes `results.json` with python3. The `pass` rule names the least-privilege requirement. No other command in the plan bypasses permissions (`grep -c dangerously` on seit.json and implementation.json gives 0).
- **Retest on `release-process`:** the evaluator returned `{"request_1": "MATCH", "request_2": "NO_MATCH"}` and `test_trigger_classifications` passed.
- **Re-freeze:** plan-package PASS with zero findings, `d7d92af7…c334d9`; render `--check` PASS, `50ea1240…2252b`; all 4 schemas 0 errors; rule 12: 0 hits.
