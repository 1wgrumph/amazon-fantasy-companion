---
type: evidence
title: P2-V01 planning delta receipt
okf_status: draft
tags: [evidence, vega, p2-v01, planning, receipt]
---

# P2-V01 planning delta receipt (issue #59, M14)

- Role: Planning and Design (`BEARING_ROLE=planning_and_design`), delta mode.
- Route: Claude Code / Claude Opus 5.5 / high.
- Date: 2026-10-14.
- Worktree branch: `afc/p2-v01-plan` at base `75afca0` (origin/main).
- Authority:
  - owner SD-040 (issue #59);
  - owner 2026-10-14, "Should match up with what we have";
  - routes from opensource-hackathon as amended by DEC-AFC-SD-043, -044
    and -045 (snapshot sha256
    `d5aabda1f44e2808c53112794afb5a7978ad02f930c100cf58002277d9423eea`,
    recomputed from the active profiles.json, sorted compact JSON).
- Outcome: the P2-V01 slices, commands, SEIT rows, requirements, design,
  milestone M14 and slice-graph nodes have been added. Status: pending
  planning review.

## Changed paths and fields (additive only)

`implementation.json`:

- `slices` += P2-V01T, P2-V01. The key set and order are identical to
  P2-A01.
- `dependencies` += P2-A01..A05 to V01T, V01T to V01, and L03 to V01.
- `waves` += `Wave V (M14 side lane)`.
- `milestones` += M14.
- `work_issues.groups` += P2-V01 (#59).
- `integration_plan.steps` += IE-P2-V01.
- `integration_plan.wave_gate_costs` += wave V.
- `traceability` += AC-AFC-P2-VEGA-01..06 and RISK-AFC-P2-14, -15.
  P2-V01T and P2-V01 are appended to the `slices` of the mirrored register
  UIDs and of AC DX-01, LAND-01, PATH-01, REL-01, REV-01, SUPPLY-01, VIS-01
  and RISK-AFC-P2-10. DES-AFC-P2-VEGA is appended to the mirrored UIDs'
  `design_ids`.
- `dod_manifest.requirements`, `.risks` and `.tasks` += the new rows.
- New top-level `planning_deltas`.

`seit.json`:

- `procedures_and_commands` += 15 commands:
  - PROC-VEGA-PREPARE, CMD-RED-VEGA, PROC-VEGA-PARITY;
  - CMD-GATE-VEGAAPP, CMD-VEGA-UNIT, CMD-VEGA-BUILD;
  - CMD-VVD-START, CMD-VVD-INSTALL, CMD-VVD-INPUT, CMD-VVD-SCREENCAP;
  - PROC-VEGA-FEATURE-VERDICT, CMD-VEGA-DEVICE-INSTALL, CMD-REVERIFY-VPKG;
  - CMD-COVERAGE-VEGAAPP, CMD-MUTATION-VEGAAPP.
- PROC-VISUAL-REVIEW gains `used_by` entries and a `vega_binding` field.
- CMD-SUPPLY-SCAN, CMD-TREE-EQUAL, CMD-CONTRACT-FROZEN, CMD-OCR-DELEGATE,
  CMD-DX-PRESENCE and PROC-GATE-TOOL-QUALIFY gain `used_by` entries.
- `proof_cases` and `traceability_matrix` += 8 rows: SEIT-AFC-P2-VEGA-01..06
  and SEIT-RISK-AFC-P2-14, -15.
- Both `slice_proof_map` copies += P2-V01T and P2-V01.
- `integration_vv_sequence` += IE-P2-V01.
- `wave_gate_costs` += wave V.
- New top-level `vega_feature_verdicts` (prospective) and `planning_deltas`.
- `counts` was left unchanged as a historical record. The delta adds 8
  requirement and proof rows and 15 commands.

Markdown:

- Technical plan: new section `## M14 Vega OS port (P2-V01)`.
- `design.md`: new decision `### DES-AFC-P2-VEGA`, inserted before
  `## Contracts`.
- `requirements-register.md`: new section `## Vega OS port mapping`. No new
  register UID.
- `specialists/slice-graph.md`: two slice rows and three dependency rows.

The mechanical check (scratchpad `verify_additive.py`, old JSON against
new) found:

- every prior JSON value is preserved;
- no existing slice changed;
- no Fire OS slice's `write_set`, `depends_on` or `milestone` changed;
- the V01T and V01 key lists equal P2-A01's.

## Digests

| File | Before | After |
|---|---|---|
| implementation.json | ae2b224ceb242d6a45e8d0564feee1c93e79e555e0d4e2ca045b8ed4b3c64c9a | recorded by the commit |
| seit.json | 8db198397d019aa44310a7132b5b1dd98ef53f33b622fbb3ac34b7732c00c848 | cdef3d3bffac8f1306d8b42fe101d4897f1d1b759cf04b933c56d8197f22dc98 |
| technical plan | 1c33c214324bbb6f7c6a31ee460eff3e5697516b27792a694000cf1669d2bc0f | d7bf7fe0cbba80fb327daa8c2e6aac9d92da606e11ed170c0b39fed6761e154f |
| design.md | 07bcfb0d7ac4b08a386ea242b23a6afec76c89a0eb5ddcd14c3f1976da776c6f | 9ede2ebcb5647a761016a2b1e145fd844f803065509d185e57ae3c4734f26ea3 |
| requirements-register.md | 2ded4228fc3f4703f6843a7d4e631cd884d2d945e860db6bfe8c6f3be3593b9b | 22ee4c1e80573bbbbdcdef6af520dedba8d60a003082c02f694b77b18d37cc15 |
| specialists/slice-graph.md | b382d93da5f82d6b096fa9a33595e851cb2c6d334b3cfed2f229adea3ff51a5b | 6493bac0c37918882c07a4987a8197852e72bb6492bd70c4e6c2251ae7095ef5 |

`plan-package.cjs` gives `manifest_digest`
`ac95cc862e27aef934c351d36d2103e7f3c2f9dfaee8b2fb5e55c520c8d7382d` (delta
candidate). The approved candidate digest
`e02871029b86f8d0f2fdef6617feb989413883cc6bdb70e5dec3a47e64c86da8`
(DEC-AFC-P2-APPROVAL-001) is deliberately not overwritten, so the hook
currently reports:

- `digest_mismatch` for the technical plan, design and register;
- `candidate_digest_mismatch`.

These clear when the Plan Integrator rebinds the inputs after planning
review and regenerates the DoD Manifest HTML. The HTML file is outside this
packet's write set.

BUG_ROUTE: not-a-bug. The digest mismatch is the expected state of a
planning delta that is pending review against a preserved approval binding.

## Host check

Full output is in `host-check.txt`. Summary:

- Ubuntu 26.04.1 LTS, x86_64, kernel 7.0.0-38.
- `/dev/kvm` is read/write for the user through an ACL. The user is not in
  the kvm group.
- 20 CPUs, 30 GB RAM, 249 GB free disk.
- Node v22.23.3.
- Native curl and lz4 are present.
- Watchman is absent. python3.8 is absent, and `libpython3.8-dev` has no
  apt candidate.
- The Vega SDK is not installed.
- reverify, ocr and diff-cover are present.

Assessment: KVM, disk, CPU, Node and curl meet the documented requirements.
The SDK is not proven unrunnable on this host, so the packet's STOP
condition does not apply. The documented host matrix ends at Ubuntu 24.04,
so this is RISK-AFC-P2-15, decided at PROC-VEGA-PREPARE.

## Sources

See `sources.md` (18 rows, all retrieved 2026-10-14). The Vega docs are at
version 0.24 (LATEST), with SDK example version 0.24.9311.

## Open owner questions

| Row | Question | Status |
|---|---|---|
| OQ-V01-1 (OA-13) | Accepting Vega SDK license or terms. The 0.24 install and CI pages name none, and `NONINTERACTIVE=true` skips all prompts. If the installer shows terms, may an agent accept them for you, or will you accept them? | NEEDS_OWNER_DECISION |
| OQ-V01-2 (OA-12) | Physical Vega stick. Does the replacement stick run Vega OS? If so, developer mode needs `vega devmode login` with your Amazon developer account in a browser. The VVD path needs no account according to the docs. | NEEDS_OWNER_DECISION (conditional) |
| OQ-V01-3 (RISK-AFC-P2-15) | Host packages. `libpython3.8-dev` (deadsnakes PPA; no candidate on 26.04) and Watchman are documented Ubuntu dependencies, and system packages need sudo, which agents may not use (rule 23). Options: (A) you install them; (B) user-scope Watchman binary after scan, and skip libpython3.8, which serves native debugging only; (C) a 24.04 VM with nested KVM. Recommendation: B. | NEEDS_OWNER_DECISION |
| OQ-V01-4 | If the replacement stick runs Vega OS, the Fire OS primary path (SD-003, SD-040; P2-X01..X12 on `fire-tv-stick`) has no Fire OS device. That is outside P2-V01, but it changes the M02..M13 device plan. | NEEDS_OWNER_DECISION (conditional; SD-040 unchanged by this delta) |

## Remaining items for planning review

- Token storage (DES-AFC-P2-VEGA): no keychain or secure-storage library is
  on the Vega supported list. The design uses app-sandboxed MMKV or
  AsyncStorage with no encryption claim, which matches A01's "app-private
  storage".
- Screenshot route: S12 and S10 conflict. CMD-VVD-SCREENCAP falls back to a
  labeled host-window capture.
- CMD-MUTATION-VEGAAPP is a typed gap by plan. CMD-COVERAGE-VEGAAPP's
  wrapper needs `tools/ci/coverage/vegaapp.sh` in the P2-V01 write set if
  review wants the wrapper rather than the native commands.
- Tooling notes:
  - The `vegaapp` CI job may need SDK packages that GitHub runners cannot
    fetch. P2-V01T records this and the area reports GAP, never PASS.
  - `seit.json` `levels` and `tracking_workflow.milestone_table` were not
    extended. Wave V is off the W1..W5 release path.

## developer_feedback

- P2V01PD-OBS-001 (friction, Bearing Lite 1.1.7 `orchestrator-write-lock`):
  the hook denied a named-path write to `implementation.json` from this
  in-process Planning and Design subagent. The envelope carried no
  `assigned_role`, so the session read as role-less. Writes ran as separate
  processes with `BEARING_ROLE=planning_and_design`, the fallback the hook
  names. The packet's role should reach the hook envelope.
- P2V01PD-OBS-002 (Vega docs): the docs give conflicting screenshot support
  on the VVD (S10 against S12).
- P2V01PD-OBS-003 (Vega docs): the supported Ubuntu versions differ between
  the install page (Ubuntu dependencies with no version) and the CI page
  (20.04, 22.04, 24.04). Ubuntu 26.04 is not mentioned.
- P2V01PD-OBS-004 (Vega docs): there is no documented secure credential
  store for React Native for Vega. Vega has no Jest or Testing Library setup
  guide, and Jest is listed only as a version.
- Tools exercised: git (read), gh issue view (read), WebFetch and WebSearch
  (developer.amazon.com), node `plan-package.cjs`, python3, and
  `tools/ci/gate.sh`.
