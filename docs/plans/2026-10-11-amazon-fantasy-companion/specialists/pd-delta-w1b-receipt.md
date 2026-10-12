# Planning and Design DELTA receipt: Wave 1 re-dispatch, DEC-AFC-SD-029, DEC-AFC-SD-030, dispatch records

- **Role:** Planning and Design node (`BEARING_ROLE=planning_and_design`), DELTA mode. It applies owner decisions made during the Wave 1 re-dispatch and the Orchestrator's S01 dispatch-record finding. It is not a correction round.
- **Inputs:** `specialists/pd-delta-w1b-prompt.md`; `journey.json` DEC-AFC-SD-029, DEC-AFC-SD-030 and the 2026-10-12T07:10:15Z `wave_receipt`; `packets/S03-r2-run.log` (directory-wide scan, exit masking); `packets/S06-r2-run.log` (`.pyc` matches); the spec-track models in the `amazon-fantasy-companion-spec-track` worktree (read-only).
- **Revision against:** `origin/main` = `d7e4dab`. Its package artifacts are the approved amended package (DEC-AFC-APPROVAL-002, manifest digest `d7d92af7…c334d9`). Local HEAD `756853c` has the same tree.
- **Return:** `DELTA_APPLIED`. SD-030 is in the plan, but `CMD-MODEL-LOAD` cannot pass until the owner decides **OD-AFC-13**. Until then it records the typed gap `MODEL_NOT_REGISTERED`.
- **New manifest (candidate) digest:** `0a85d1e5d58c42ff816f37cc0600cbe0fea51df2e1dd71d430116588e9714843`
- **Rendered DoD Manifest:** sha256 `fdfd2cdff965306cc66897cc56f03f534556044e6f94ce4979667924e93538a8`, template 1.0.1

## Revision diff vs origin/main (d7e4dab)

| Item | Change |
|---|---|
| 1. SD-029 `CMD-D4-AGNOSTIC` | The ID is kept. The new command is `d=$(git diff --name-only --diff-filter=ACMR <base>..HEAD -- <slice_paths>)`. It filters out `^$`, `\.pyc$`, `(^\|/)(__pycache__\|build\|dist)/` and GATES.md, prints `scanned:` for each file, and fails on an empty list. It then runs `git grep -nIiE '<pattern>' HEAD -- $f; [ $? -eq 1 ]`, so it reads committed content only and never sees untracked or uncommitted files. `<base>` is the base SHA from the slice's dispatch record. The combined Wave 1 exit run uses the oldest base among S01..S03. A match exits 1, and any other non-zero status (for example 128 for a bad base) is a typed gap. The pass rule, the description, SEIT-AFC-D4-06 stimulus and evidence, the traceability row and the integration_vv_sequence pre_merge text are all updated. |
| 1. SD-029 `CMD-D5-AGNOSTIC` | The ID is kept. The template build, lint and diagram steps are unchanged. The name scan and the home-path scan now read only the tracked files S06 changed (`<base>..HEAD -- skills/spec-authoring`), with generated artifacts excluded, through `git grep … HEAD`. The provenance exclusions are the same as before: `LICENSE-gridmarket`, `vendor.sh` and `references/`. The MIT check is `git grep -q … HEAD -- LICENSE-gridmarket`. An empty scanned list is FAIL. The pass rule, the description and the D5-01 and D5-02 stimulus text are updated. |
| 1. Exit masking | Every command that ended with `; echo "exit=$?"` (25 besides the two above) now ends with `; rc=$?; echo "exit=$rc"; (exit $rc)`. CMD-RED and CMD-LANDING-CHECK had the echo in the middle of the command. They keep their trailing receipt and cleanup steps and then exit with `rc`. A new `seit.json` `environments.exit_status` entry states the rule. Zero `echo "exit=$?"` remain in any command. |
| 2. SD-030 `CMD-MODEL-LOAD` (new, 48th command) | The command saves `checkout list` (before), the sha256 of each model, and `model load --package <models_dir>` stdout and stderr into `<st_evidence_dir>`. It then saves `checkout list` (after), and `cmp` requires the before and after lists to be identical. The rule: never `--replace`, never `checkout create`, `release` or `move`, never another package, never the Maestro checkout. A parse error is FAIL and goes to the Systems Modeler for repair. A refusal before parsing is `MODEL_NOT_REGISTERED` or `HOST_UNAVAILABLE`, never PASS. `used_by` is ST-3 (b)/(c) and the ST-4 entry criterion. |
| 2. SD-030 ST-3 / ST-4 | Updated in the TP table, `implementation.json` `phase2_sequence` and design DES-AFC-PHASE2. ST-3 gains step (d), the SysON parse check after (b) and again after (c). Its exit requires CMD-MODEL-LOAD PASS on the final model digest, or the recorded gap while OD-AFC-13 is open. ST-4 entry adds "ST-3 (d) PASS, or the owner's OD-AFC-13 decision". ST-4 figures come from views of the loaded model revision. |
| 2. SD-030 `authority.json` | The spec-track scope line adds CMD-MODEL-LOAD. One allowed action: `model load --package <spec-track models dir>` on the local packaged-default host, starting it with `start --no-browser` if it is down (rule 14). One prohibited action: `--replace`, `checkout create`, `release` or `move`, any other package, the Maestro checkout, and stopping the host while a busy claim is active. The granting decisions add SD-029 and SD-030. |
| 2. OD-AFC-13 (new, open) | **Finding:** `model load` refuses any package that the host's compiled-in model registry does not bind (requirements-system `migrations/*/registry/registry.toml`, `include_str!`). The bound model must also be governed by a specification with an active checkout. I ran CMD-MODEL-LOAD as written against a scratch copy of the four spec-track `.sysml` files. The result was `package is not bound to a configured model`, exit 1, before any POST, and the checkout list was unchanged. Options: **A**, a requirements-system registry entry plus a governing AFC `.sdoc` and its own `checkout create` (needs authority beyond this envelope); **B**, a host checker or parser path without a native load; **C**, the owner accepts the gap. OD-AFC-13 is recorded in `implementation.json` open_decisions, the TP open-items table and `dod_manifest.authority`. |
| 3. Dispatch records | New `implementation.json` `dispatch_records`. Before each dispatch the Orchestrator writes a `dispatch_record` to `journey.json` execution_receipts with these fields: `lease_id` = `<slice>-g<generation>` (generation counts earlier rounds), slice, generation, leases, repository, worktree, branch, `base` (full SHA, the `<base>` of the agnostic checks), `evidence_dir` = `docs/plans/2026-10-11-amazon-fantasy-companion/evidence/<slice>/` (with a `g<n>/` subdirectory per generation), packet, route and `dispatched_at`. A packet without its record is CONTRACT_FAILURE before any edit. `seit.json` `evidence_dirs` now resolves `<evidence_dir>` from the record, and the new `dispatch_base` defines `<base>`. DES-AFC-LANES gains the convention, and the slice `verification_note`s (S01, S02, S03, S06, S41) name it. |
| Bookkeeping | `revision_against` is now d7e4dab / `d7d92af7…` APPROVED, decided by SD-029 and SD-030. The prior pair moves to `revision_history`. `revision_diff` is rewritten. `planning_review.repair_revision` and `candidate_digest` are rebound, as are the identity rows (Revision against, Authority, the inputs, seit, Candidate digest). There are still 33 requirement rows with no statement changed, so no Requirements Engineer gate is needed. The plan holds 55 proof cases and 48 commands, and all earlier IDs are stable. No write set, wave, route or dependency changed. |

`git diff --stat origin/main -- <plan dir>` (package files):

```text
amazon-fantasy-companion-dod-manifest.html | 18   amazon-fantasy-companion-technical-plan.md | 5
authority.json | 12   design.md | 32   implementation.json | 137   seit.json | 100
```

## Digests

| Artifact | origin/main | New |
|---|---|---|
| technical plan | `4dbaf7e0…1fe07` | `4e6571573a1f22aff6c2245af67b903abcfdebd22a6e0a67dd18fb608b13fe66` |
| design.md | `7c53f5eb…923d3` | `b9c52d4200aa6731c5548c54ba21317fd314296f2b4ccfa242a8851ef1ef2e30` |
| views/views.json | `d54a59f8…2ce6` | unchanged |
| seit.json | `fc03a461…ccdcf` | `a4d39d5e2fb95b1a0526b67e858ff8100bc4609d644b6ff8cc3b6f46068926df` |
| candidate (manifest digest) | `d7d92af7…c334d9` | `0a85d1e5d58c42ff816f37cc0600cbe0fea51df2e1dd71d430116588e9714843` |
| authority.json | `5a49c74f…a3ad6` | `9e080ffd2357d79b81b493159d588d9e2c449fd551837e1898b582ed4f43c896` |
| implementation.json | `1b68d0ff…2ea3` | `72b00a4de0c9526ad26ba2c5d54d70649276dfc1d4b719974c9a67c92d8fd9c4` |

## Commands and results

```text
node <bearing-lite 1.1.6>/hooks/plan-package.cjs <plan dir>                        exit 0  PASS, findings [], manifest_digest 0a85d1e5…714843
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json          exit 0  RENDER_WRITE sha256:fdfd2cdf…38a8
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json --check  exit 0  RENDER_CHECK_PASS sha256:fdfd2cdf…38a8
python3 jsonschema Draft202012Validator (<bearing-lite 1.1.6>/schemas)             implementation 0 | seit 0 | authority 0 | journey 0
slice command_ids / seit_proof_rows -> seit                                         0 orphans; 55 proofs, 48 commands
rule 12 home-path shape scan (TP, design, *.json, manifest, views/, evidence/, slice-graph.md)   0 hits
Self-test, commands extracted verbatim from seit.json:
  CMD-D4-AGNOSTIC, Alphazedehq main (read-only), skills/ship-pull-request, <base>=HEAD      scanned: none, exit=1, wrapper=1 (empty list fails)
  CMD-D4-AGNOSTIC, same, <base>=1c96ccbb^ (last SKILL.md change)                           scans SKILL.md, PR-BODY.md only; PR-BODY.md:56 match, exit=1, wrapper=1
  CMD-D4-AGNOSTIC, scratch repo: clean change + untracked pyc + GATES.md + old file        exit=0; committed violation exit=1; bad base exit=128; uncommitted text not scanned
  CMD-D5-AGNOSTIC scan part, scratch repo: provenance files + untracked .pyc with home path  exit=0; committed home path exit=1, wrapper=1
  CMD-MODEL-LOAD, scratch copy of the 4 spec-track models, host 0.1.0-102                  "package is not bound to a configured model", exit=1, wrapper=1, no POST
```

The positive CMD-MODEL-LOAD path was not exercised: it needs OD-AFC-13. CMD-D5-AGNOSTIC's build and lint half is unchanged and was not rerun here, because it needs S06's scanned wheels.

## Write set

Changed: TP, `design.md`, `seit.json`, `implementation.json`, `authority.json`, the manifest HTML. New: this receipt. Not edited: `journey.json` (the Orchestrator's own uncommitted edit is preserved), `views/`, `packets/`, `specialists/slice-graph.md` (no write set changed) and `specialists/pd-delta-w1b-run.log`. No commits, pushes or branch operations. The pre-edit backup and the delta scripts (`delta.py`, `rebind.py`) live in a host cache directory outside the repository.

## Orchestrator follow-ups

- **Authority:** record DEC-AFC-SD-029 and DEC-AFC-SD-030 in `journey.json` as the basis for the new digest `0a85d1e5…`, the same way as for SD-026..028.
- **OD-AFC-13:** owner decision needed before ST-3 (d) can pass. ST-2, ST-3 (a) to (c) and every Wave 1 or Wave 2 slice are unaffected.
- **Re-dispatch:** regenerate `packets/S01`, `S03` and `S06` from `implementation.json` and write each slice's `dispatch_record` first. S01, S03 and S06 have each been dispatched twice, so their next `lease_id` is `-g3`. S03's earlier blocker (PR-BODY.md and edit-pr.test.sh) is now out of scope unless S03 changes those files.
- **S02 (PR #303, already PASS):** it ran the old CMD-D4-AGNOSTIC, whose wrapper always exited 0. Check its receipt for a printed `exit=0` before you land it, or rerun the new form on its head.

## developer_feedback

| ID | Tool | Used for | Worked well | Needs work (task / steps / expected / actual) | Severity | Workaround | Suggestion | Would build again |
|---|---|---|---|---|---|---|---|---|
| PD-W1B-OBS-1 | Requirements System 0.1.0-102 `model load` | SD-030 SysON parse check of a new product model | Fails closed before any POST, with a clear message | Load a new, unregistered SysML package to check that it parses / `model load --package <dir>` / a parse result / `package is not bound to a configured model`, exit 1. The registry is compiled in, so a new product cannot be parse-checked without a code change and a governing `.sdoc`. | Major | OD-AFC-13 | A host `model parse --package DIR` (or a check with no registry) that loads into a scratch native project and reports parser diagnostics only | Yes |
| PD-W1B-OBS-2 | Plan (this Lifecycle) | Command wrappers | `exit=` lines made the evidence readable | 27 commands ended in `; echo "exit=$?"`, so every wrapper exited 0. S03 caught it by hand. | Major | `rc=$?; echo; (exit $rc)` | A plan-package lint that rejects a trailing bare `echo "exit=$?"` in seit commands | Yes |
| PD-W1B-OBS-3 | plan-package.cjs | Digest rebind | PASS/FAIL with exact digests | The two-pass rebind is still needed (repeats PD-W1-OBS-3) | Minor | Two-pass script | A `rebind` subcommand | Yes |
| PD-W1B-OBS-4 | Plan (this Lifecycle) | Pre-dispatch validation | n/a | Like PD-W1-OBS-4: the agnostic scope and `.pyc` defects would have surfaced in a dry run of each slice's commands against its base. | Major | This delta | Dry-run each slice's commands on its dispatch-record base before dispatch | Yes |

AWS services: n/a. Tools exercised: python3 (json, jsonschema, hashlib), node v22.23.3 (plan-package, render-dod-manifest), git 2.53.0, alphazede-requirements-system 0.1.0-102 (`checkout list`, `model load`, refused), sha256sum, cmp.

---

# Addendum: OD-AFC-13 resolution delta (DEC-AFC-SD-031)

- **Role:** Planning and Design node, DELTA mode. Prompt: `specialists/pd-delta-od13-prompt.md`.
- **Revision against:** the approved W1b candidate, manifest `0a85d1e5…714843` (DEC-AFC-APPROVAL-003), on top of local HEAD `756853c`. The W1b `revision_against` and `revision_diff` pair moved to `revision_history`.
- **Return:** `DELTA_APPLIED`.
- **New manifest (candidate) digest:** `7a9a87433dd0c1aebcb00acd82c3f49989fef915730bcda22c817239d00f055d`
- **Rendered DoD Manifest:** sha256 `6fb09423e0f6051205ef345b8a2c26765d9fb7f6a524db01113b4a16646ca924`, template 1.0.1

## Disposition

| Item | Change |
|---|---|
| `CMD-MODEL-LOAD` → `CMD-MODEL-PARSE` | The SysON `model load` command is replaced in place. It is still the 48th command, and no proof case cites it. The new command clears the earlier run's log and digests. It finds every `.sysml` under `<models_dir>`, sorted, and an empty list fails. It requires the CMD-SCAN receipt `<syside_scan>` to have `verdict: PASS` and to contain the sha256 of the pinned `syside-0.11.0-cp312-abi3-manylinux_2_31_x86_64.whl`. It requires `syside.__version__` = 0.11.0 in `<syside_venv>`. It writes `model-digests.txt`, then runs `syside.load_model(<all files>)` under `python -I`, which raises ModelError when the model has errors. The command ends `rc=$?; cat log; echo "exit=$rc"; (exit $rc)`, so the exit status is the verdict and is not masked. Typed gaps: TOOL_MISSING (no receipt, wrong digest or version) and SYSIDE_LICENSE_MISSING. A ModelError is FAIL and goes to the Systems Modeler for repair. Nothing touches the Requirements System. |
| seit `environments.syside` (new) | `pip download --only-binary=:all: --no-deps 'syside==0.11.0'` into `<syside_wheel_dir>`, outside every repository. Then CMD-SCAN writes the receipt to the spec-track `evidence/model-parse/scan-syside.md`, recording the wheel sha256. Only after PASS: `python3 -m venv <syside_venv>`, then `pip install --no-index --find-links <syside_wheel_dir> 'syside==0.11.0'`. The `host` line records syside as absent on 2026-10-12. CMD-SCAN's description and `used_by` list the syside wheel (ST-3). `decision_baseline` adds SD-029..031 (SD-030's SysON method is superseded by SD-031) and marks OD-AFC-13 closed. |
| OD-AFC-13 | Closed by DEC-AFC-SD-031 in `implementation.json` open_decisions (status and resolution), the TP open-items row and its "Closed since" line, and the `dod_manifest.authority` event (Closed decision OD-AFC-13). |
| ST-3 / ST-4 | The TP table, `phase2_sequence` and DES-AFC-PHASE2 are updated. ST-3 (d) is now the syside parse check after (b) and again after (c). It depends on (b) or (c) being done and a syside CMD-SCAN PASS receipt. Its exit is CMD-MODEL-PARSE PASS on the final model digest, and the MODEL_NOT_REGISTERED alternative is removed. ST-4 figures come from views of the syside-parsed model revision. ST-4 entry requires CMD-MODEL-PARSE PASS on the final model digest. |
| `authority.json` | The Requirements System host model-load action is removed. The scan-and-install action adds the pinned syside wheel and venv for the spec track. The spec-track scope line now runs CMD-MODEL-PARSE. The prohibited Requirements System line now forbids any host action for the spec-track models and any change to Maestro or other packages. Granting decisions add DEC-AFC-APPROVAL-003 and DEC-AFC-SD-031. `approval_receipt.amendments` adds APPROVAL-003 (manifest `0a85d1e5…`). |
| Bookkeeping | `revision_against` (decided_by SD-031), `revision_diff`, `planning_review.repair_revision` and `candidate_digest`, and the identity rows (Revision against, Authority, input digests, seit, Candidate digest) are all rebound. 33 requirement rows are unchanged, so no Requirements Engineer gate is needed. 55 proofs and 48 commands. No slice, write set, wave, route or dependency changed. |

## Digests

| Artifact | W1b (0a85d1e5) | New |
|---|---|---|
| technical plan | `4e657157…13fe66` | `e264f214436aa410b203db370d3c01b0431327cd589e5b2a95bf6631cf3768ad` |
| design.md | `b9c52d42…2ef30` | `28f534220e3444cbf82cf8327b935dadca440d1da527015de526af416757fa4e` |
| views/views.json | `d54a59f8…2ce6` | unchanged |
| seit.json | `a4d39d5e…926df` | `71d3552f7f059b92e008fdfcec4dccfd75f31635cfb83e85dc265161a38b1d4a` |
| authority.json | `9e080ffd…c896` | `6ee0da7e8554d42a8cf8384c7b0f015bb1dc214f86c16ac357c0d869dac4784e` |
| implementation.json | `72b00a4d…d9c4` | `f4c31203d79f0dc814434d36ed51b429097bde218970464adf0d8dd13eae235f` |
| candidate (manifest digest) | `0a85d1e5…714843` | `7a9a87433dd0c1aebcb00acd82c3f49989fef915730bcda22c817239d00f055d` |

## Commands and results

```text
node <bearing-lite 1.1.6>/hooks/plan-package.cjs <plan dir>                        exit 0  PASS, findings [], manifest_digest 7a9a8743…f055d
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json          exit 0  RENDER_WRITE sha256:6fb09423…a924
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json --check  exit 0  RENDER_CHECK_PASS sha256:6fb09423…a924
python3 jsonschema Draft202012Validator (<bearing-lite 1.1.6>/schemas)             implementation 0 | seit 0 | authority 0 | journey 0
slice command_ids / seit_proof_rows -> seit                                         0 orphans; 55 proofs, 48 commands
rule 12 real-home-path scan (TP, design, *.json except journey, manifest, views/, evidence/, slice-graph.md)  0 hits
  (the shape-pattern scan finds 3 lines, all pre-existing placeholder or regex text: design.md:181 `/home/<user>/`, seit CMD-D5-AGNOSTIC and CMD-PATH-SCAN-PLAN grep patterns)
Self-test, CMD-MODEL-PARSE extracted verbatim from seit.json, run on a scratch dir with a stub syside module (load_model raises ModelError on a bad file):
  empty models dir exit=1 | 1 good file exit=0 | bad file ModelError exit=1 | receipt BLOCK exit=1 | wheel digest not in receipt exit=1 | version 0.10.3 exit=1 (wrapper = exit in every case)
  The first self-test found that a stale syside-parse.log from an earlier run was echoed when a later run failed before parsing; fixed by the leading `rm -f`.
syside 0.11.0 facts (PyPI JSON, docs.sensmetry.com): requires_python >=3.12; one cp312-abi3 manylinux_2_31_x86_64 wheel; no runtime deps; LicenseRef-Proprietary; needs SYSIDE_LICENSE_KEY. No `syside check` CLI is documented, so the command uses the documented `syside.load_model` API.
```

The real syside was not installed or run. It needs a CMD-SCAN receipt (cross-repo rule 10) and the owner's license key, and both are ST-3 execution steps.

## Write set

Changed: TP, `design.md`, `seit.json`, `implementation.json`, `authority.json`, the manifest HTML, and this receipt (append only). Not edited: `journey.json` (byte-identical to its pre-delta state), `packets/`, `views/`, `specialists/slice-graph.md`. No commits. The backup and `delta.py` are in a host cache directory outside the repository.

## Orchestrator follow-ups

- **Approval:** record SD-031 as the basis for the new digest `7a9a8743…` in `journey.json`. This delta changes authority: it removes an action and adds the syside install. Whether that needs an owner re-approval like APPROVAL-003 is the Orchestrator's call.
- **Owner precondition (new fact):** syside Automator is proprietary and needs `SYSIDE_LICENSE_KEY`. The owner must supply a key in the ST-3 run environment. Without one, CMD-MODEL-PARSE records SYSIDE_LICENSE_MISSING and ST-4 cannot start. Agents never read the key.
- No Wave 1 or Wave 2 slice is affected. The S01, S03 and S06 g3 packets cite only slice commands, so they do not need regeneration.

## developer_feedback

| ID | Tool | Used for | Worked well | Needs work (task / steps / expected / actual) | Severity | Workaround | Suggestion | Would build again |
|---|---|---|---|---|---|---|---|---|
| PD-OD13-OBS-1 | syside 0.11.0 docs | Choosing a parse-check entry point | `load_model` raising ModelError is clearly stated | Find a CLI parse check / read docs.sensmetry.com / a `syside check` with exit codes / only `interactive` and `server` are documented | Minor | Use the Python API under `python -I` | Document a `check` subcommand with exit codes | Yes |
| PD-OD13-OBS-2 | Plan delta scripting | Multi-file delta | Assert-on-replace caught text drift | `delta.py` wrote `seit.json` before an assert failed on `implementation.json`, so the package was half applied until it was restored from backup | Minor | Restore from backup, then rerun | Stage all outputs in memory and write them only after every assert passes | Yes |

AWS services: n/a. Tools exercised: python3 3.14.4 (json, jsonschema), node (plan-package, render-dod-manifest), bash, sha256sum, curl (PyPI JSON), pip index.

---

# Addendum: SysON parse-check delta (DEC-AFC-SD-032)

- **Role:** Planning and Design node, DELTA mode. Prompt: `specialists/pd-delta-sd032-prompt.md`.
- **Revision against:** the OD-AFC-13 candidate, manifest `7a9a8743…f055d` (DEC-AFC-SD-031, recorded in `journey.json` as DEC-AFC-SD-031-DIGEST). Its `revision_against` and `revision_diff` pair moved to `revision_history`.
- **Return:** `DELTA_APPLIED`. No new owner decision.
- **New manifest (candidate) digest:** `a018168f575741b5f53bbe7fac4bcb13128e31f37f69d73ba2433cf8d09d5144`
- **Rendered DoD Manifest:** sha256 `ad2d4d3d124b0bd4017e1f7701ce24fe15e393f55eb6ab02bc9e5ac696419067`, template 1.0.1

## Disposition

| Item | Change |
|---|---|
| `CMD-MODEL-PARSE` → `CMD-MODEL-SYSON` | Replaced in place. It is still the 48th command, and no proof case cites it. The command makes a new `<st_evidence_dir>` (a reused one fails, so stale evidence is never echoed). It lists every `.sysml` under `<models_dir>`, sorted, and an empty list fails. It writes `model-digests.txt`. It creates one new SysON project `afc-model-parse-<run>` through SysON's own GraphQL `createProject` (template `blank-project`) and records the id in `project-id.txt`. It resolves the project's editing context. Each file is uploaded through `uploadDocument` at `/api/graphql/upload` (map `{"0":"variables.file"}`), with one end-marker package `AFCParseEnd<n>` appended; the uploaded copy is kept under `upload/`. Each response is saved and summarised in `import-diagnostics.jsonl`. It reads the project back (`/api/rest/projects/<id>/commits/<nil>/elements`) and requires every end marker. PASS needs success, no GraphQL errors and an empty report for every file, plus every marker. The command ends `rc=$?; …; echo "exit=$rc"; (exit $rc)`. A non-empty report or a missing marker is FAIL, which goes to the Systems Modeler. No project id is SYSON_UNAVAILABLE. Nothing uses the Requirements System CLI, registry, checkouts or bindings. No key is needed. |
| Why the end marker | Self-test: a file with a syntax error at line 3 was imported **with an empty report**, and everything after the error was dropped (eclipse-syson#2510, already listed in the requirements-system capability audit). A plain "success and empty report" verdict would have passed it. The appended marker is lost whenever the file is truncated, so the read-back catches it. |
| seit environments | `syside` was removed and replaced in place by `syson`. `<syson_url>` = `http://127.0.0.1:<port>`, with the port read from `$XDG_RUNTIME_DIR/alphazede-requirements-system/syson.port` (the writable port, never the review port). If SysON is down, start the host with `start --no-browser` (rule 14). It names the exact SysON API calls. Each run leaves its own project as evidence, and no run edits or deletes any other project. The `host` line drops "syside absent". CMD-SCAN no longer lists a syside wheel or `ST-3 (spec track: syside)`. `decision_baseline` adds SD-032 and records `DEC-AFC-SD-031 (syside parse method)` as superseded by SD-032. |
| ST-3 / ST-4 | The TP table (work, depends_on and exit columns), `phase2_sequence` and DES-AFC-PHASE2 are updated. ST-3 (d) is now the SysON parse check. It depends on (b) or (c) being done and on the local SysON answering. Its exit is CMD-MODEL-SYSON PASS on the final model digest, with the project id recorded. ST-4 figures come from views of the SysON-imported revision. ST-4 entry needs CMD-MODEL-SYSON PASS (SD-032). |
| `authority.json` | The scan-and-install action is back to "(uv, Graphviz)". The spec-track scope runs CMD-MODEL-SYSON. A new allowed action creates one new SysON project per run, uploads the spec-track models into it and reads it back, starting the host if it is down. The prohibited line forbids any registry, checkout or `model` action for these models, any change to or deletion of another SysON project, the Maestro checkout or other packages, and any keyed or licensed tool. Granting decisions add DEC-AFC-SD-032. |
| OD-AFC-13 | It stays closed. The resolution text in `open_decisions`, the TP row and its "Closed since" line now say the method is SD-032. The `dod_manifest.authority` close event is reworded, and a new event records DEC-AFC-SD-032. |
| Removed | `syside`, `SYSIDE_LICENSE_KEY`, `SYSIDE_LICENSE_MISSING`, `<syside_*>` and CMD-MODEL-PARSE no longer appear in any operative text. `syside` still appears only where history records what SD-032 superseded: the OD-AFC-13 resolution, the CMD-MODEL-SYSON description, `revision_diff`, the SD-032 authority event and `revision_history`. |
| Bookkeeping | `revision_against` (decided_by SD-032), `revision_diff`, `planning_review.repair_revision` and `candidate_digest`, and the identity rows (Revision against, Authority `SD-026..032`, the input digests, seit, Candidate digest) are rebound. The 33 requirement rows are unchanged, so no Requirements Engineer gate is needed. 55 proofs and 48 commands, 0 orphans. No slice, write set, wave, route or dependency changed. |

## Digests

| Artifact | SD-031 (7a9a8743) | New |
|---|---|---|
| technical plan | `e264f214…3768ad` | `afffae3cd7396dd0459d09baf8a9fbf67bd70da3bc0d507427b3def959439f6f` |
| design.md | `28f53422…757fa4e` | `a872f0cbff796a87900ccc17f87b81fc178d0a8e2963532aa9d4ece2d58fc80b` |
| views/views.json | `d54a59f8…2ce6` | unchanged |
| seit.json | `71d3552f…a38b1d4a` | `2d8fe28878bac9c1c9b8eb10427a3d144d37eed6956e3c1ace28bef54a3f7d8e` |
| authority.json | `6ee0da7e…dac4784e` | `6084ed9eb032f12676c9e4d27f9f8abed1596b7ca3ba980376b9442163475958` |
| implementation.json | `f4c31203…eae235f` | `4d33331c283939bfbdb412df16ef12ca6784c39d9edc4bfbb194c5d956944c4f` |
| candidate (manifest digest) | `7a9a8743…f055d` | `a018168f575741b5f53bbe7fac4bcb13128e31f37f69d73ba2433cf8d09d5144` |

## Commands and results

```text
node <bearing-lite 1.1.6>/hooks/plan-package.cjs <plan dir>                        exit 0  PASS, findings [], manifest_digest a018168f…d5144
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json          exit 0  RENDER_WRITE sha256:ad2d4d3d…19067
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json --check  exit 0  RENDER_CHECK_PASS sha256:ad2d4d3d…19067
python3 jsonschema Draft202012Validator (<bearing-lite 1.1.6>/schemas)             implementation 0 | seit 0 | authority 0 | journey 0
slice command_ids -> seit                                                           0 orphans; 55 proofs, 48 commands
rule 12 home-path shape scan (TP, design, seit, implementation, authority, manifest, slice-graph.md, views/)  0 hits
Self-test against the local SysON (packaged-default host, writable port), scratch projects deleted afterwards (0 remain):
  2 clean files exit=0 | empty dir exit=1 | syntax error with EMPTY report (silent truncation) exit=1 via missing end marker
  unresolved name ([Warning] Unable to resolve name) exit=1 | SysON down (curl 7) exit=4 | reused evidence dir exit=1, no stale output
  command re-extracted verbatim from seit.json: clean exit=0, truncation exit=1 (wrapper = exit in every case)
  current spec-track draft models (4 files, read-only): exit=1 (AFC-States.sysml line 14 syntax error "found `def`";
    AFC-Data.sysml unresolved `String`/`Boolean`, so ScalarValues is not imported). AFC-Interfaces and AFC-Structure import clean.
```

## Write set

Changed: TP, `design.md`, `seit.json`, `implementation.json`, `authority.json`, the manifest HTML, and this receipt (append only). Not edited: `journey.json` (its last write, 02:48:22 local, is the Orchestrator's SD-032 entry), `packets/`, `views/`, `specialists/slice-graph.md` and the spec-track models (read only). No commits. The backup, `delta.py`, `rebind.py` and the self-test files are in a host cache directory outside the repository. Five scratch SysON projects were created by the self-test (`afc-sd032-selftest-*`, `afc-model-parse-selftest-*`) and deleted through `deleteProject`. No other SysON project was touched.

## Orchestrator follow-ups

- **Digest:** record the new digest `a018168f…` in `journey.json` as the result of SD-032, in the same way as DEC-AFC-SD-031-DIGEST.
- **Spec track (new fact):** the current draft models fail CMD-MODEL-SYSON (AFC-States line 14 syntax; AFC-Data unresolved scalar types). That is ST-3 Systems Modeler repair work. This plan does not change it.
- **Rule 12 (outside this write set):** the untracked implementer evidence under `evidence/S01/g4`, `evidence/S03/g4` and `evidence/S06/g4` contains absolute home paths (12 files). Sanitize or keep it untracked before committing `evidence/`.

## developer_feedback

| ID | Tool | Used for | Worked well | Needs work (task / steps / expected / actual) | Severity | Workaround | Suggestion | Would build again |
|---|---|---|---|---|---|---|---|---|
| PD-SD032-OBS-1 | SysON (packaged-default host) `uploadDocument` | Parse-checking textual SysML | `[ERROR] line N` diagnostics when it reports | Import a file with a syntax error / upload / an `[ERROR]` report / sometimes an empty report and a silently truncated model (eclipse-syson#2510). A later identical upload instead said "could not be checked for syntax errors". | Major | An appended end marker plus read-back | A report that always names the first syntax error | Yes |
| PD-SD032-OBS-2 | SysON REST `/api/rest/projects` | Finding self-test projects to delete | Lists every project | The id field is `@id`, but GraphQL uses `id`; `.id` returned null and `deleteProject` answered "Not found" | Minor | Read `."@id"` | n/a (documented REST shape) | Yes |

AWS services: n/a. Tools used: python3 (json, jsonschema, hashlib), node (plan-package, render-dod-manifest), bash, curl, jq, sha256sum, and the local SysON GraphQL and REST APIs.
