---
type: specialist-receipt
role: test_engineer (Planning Test Engineer session)
lifecycle: AFC-2026-10-11
harness: Claude Code / Claude Opus 5.5
date: 2026-10-11
---

# Planning Test Engineer receipt — AFC-2026-10-11

## Typed outcome

- **outcome:** PASS
- **verdict:** `seit.json` is written and valid against `seit.schema.json`. It has 126 proof cases covering all 65 AC-AFC rows and all 16 RISK-AFC rows, 75 commands, one flat 126-row traceability matrix, and gate declarations per lane. Every command ID named by the slice graph is present. Every command ID named by the integration plan is present, except `CMD-REVERIFY`, which is renamed to `CMD-REVERIFY-APK` (TE-F01). Ten findings go to the Plan Integrator (TE-F01..TE-F10). None needs a new owner decision.
- **candidate_ref:** `1wgrumph/amazon-fantasy-companion` @ `2c13a6bf560e87d11864cc6234f48e40dd9cf529` on `plan/2026-10-11-amazon-fantasy-companion`, plus the untracked plan directory. Bound inputs (sha256):
  - `amazon-fantasy-companion-technical-plan.md` `9bda1ff52d520302ec41da3dbf44d5d706d189110f52acb6babeb6e347f685bb`
  - `design.md` `d972faa0f583b262d19c7ebdbc900e47d0d07695fb8c6c8fa6f5cc440edf095c`
  - `views/views.json` `965a8b8c4821238387fed209969b9d6fb8ff7369f41484967e527719ace4130d`
  - output `seit.json` `cae54c15641549606b449da2a6bd396d592d11e096f0002d4487553789cc30d3`
- **changed_paths:** `docs/plans/2026-10-11-amazon-fantasy-companion/seit.json`, `docs/plans/2026-10-11-amazon-fantasy-companion/specialists/test-engineer-receipt.md`
- **blocker:** none.

## What seit.json contains

- `source_baseline`: the three bound inputs above. `decision_baseline`: a `decision-baseline-projection` of 26 DEC-AFC ids (DEC-AFC-SD-013 `superseded` by SD-022) and OD-AFC-01..10 as `open_for_integrated_review`, plus the frozen OCR, Reverify and assurance settings.
- All always-on sections, `required_commands` (18), `cross_cutting_checks` (path, secrets, developer_feedback, OCR, Reverify, on-device visual review, landing, real device, supply chain, typed gap).
- `procedures_and_commands`: 75 entries with `id`, exact `command`, `pass`, `description`, `repository`, `used_by` and tool availability on 2026-10-11. No `actor` field.
- `proof_cases`: 48 red-then-green rows naming the test and product slices; 22 rows on the stick or the dev stack naming the lease and evidence path; Reverify applies only to `SEIT-AFC-SEC-01.R` and `SEIT-AFC-REV-01.R` (S40 APK). Every other row states `Reverify: not applicable — <reason>`.
- `gate_declarations`:
  - Backend: pytest, coverage.py + diff-cover (≥ 90 % changed lines) and mutmut (≥ 0.70).
  - tv-app: Gradle JUnit, Kover + diff-cover (≥ 80 %) and PIT (≥ 60 %).
  - `tools/ci`: unittest red-then-green and coverage; mutation is a typed gap.
  - Alphazedehq skills: their own tests and coverage.py for Python (≥ 80 %); shell coverage and mutation are typed gaps.
  - Alphazedehq hooks: red-then-green; coverage and mutation are typed gaps.
  - Spikes and scaffolds: NOT_APPLICABLE, each with a reason.
  - Every declared gate whose tool is missing, or whose outcome is `not_run`, is a typed gap and never PASS.
- `integration_vv_sequence`: aligned with IE-M1-1..IE-M5-3, plus a per-phase row for the review, landing, developer-feedback and route checks.

## Commands run (verbatim output)

Schema validation and cross-check (`python3` + `jsonschema` 4.19.2, Draft 2020-12), final round:

```
schema_errors: 0
AC rows: 65  RISK rows: 16  proof cases: 126  commands: 75
AC rows without proof case: []
RISK rows without proof case: []
proof requirement ids not in plan: []
proof command_ids missing from procedures: []
slice-graph command ids: 34  missing from seit: []
integration-plan command ids: 47  missing from seit: ['CMD-REVERIFY']
unknown design ids: []
duplicate SEIT ids: []
bad SEIT id grammar: []
bad command id grammar: []
trace rows: 126  bad column sets: 0  empty negatives: 0
actor fields: 0
Reverify applies: ['SEIT-AFC-SEC-01.R', 'SEIT-AFC-REV-01.R']
rows lacking reverify note: []
tdd rows: 48  device/lease rows: 22
absolute home paths: []
decisions: 26 superseded  open_items: ['OD-AFC-01', 'OD-AFC-02', 'OD-AFC-03', 'OD-AFC-04', 'OD-AFC-05', 'OD-AFC-06', 'OD-AFC-07', 'OD-AFC-08', 'OD-AFC-09', 'OD-AFC-10']
slice coverage gaps: 0
```

`CMD-REVERIFY` is the intentional rename to `CMD-REVERIFY-APK` (TE-F01).

Correction rounds: 1 of 3.

- **Round 0.** Schema-valid, with 121 cases. A slice-to-proof cross-check found 15 slice→requirement links where no proof row named the slice (coverage gaps): S04, S05, S06, S08, S11, S13, S14, S16, S17, S27T, S31T, S32T/S32, S34, S36.
- **Fix.** Added `method_fields.contributing_slices` and five rows: PANEL-03.T, PANEL-05.T, PANEL-05.C, CTRL-01.P and PANEL-01.L.
- **Round 1.** Output above.

Other commands run, all read-only apart from the two allowed writes:

- `sha256sum` of the three inputs.
- `jq`, `python3` reads of `journey.json` and `integration-plan.md`.
- Tool checks: `which` (adb, sam, gradle, mutmut absent; java, dot, uv, ocr, reverify, jq, pytest present), `java -version` (OpenJDK 21.0.12), `ocr --version` (v1.12.13), `reverify auto|strings|verify --help`, `ocr delegate --help`.
- `grep COE-ASA-001` in Alphazedehq `docs/coe/index.md`: the identifier is present. The clause text is in the COE-ASA SDoc and was not opened.
- The generator scripts are scratch files outside the repository.

## Findings (planning_findings_for_plan_integrator)

| ID | Finding | Needed |
|---|---|---|
| TE-F01 | `CMD-REVERIFY` → `CMD-REVERIFY-APK`. 26 new CMD/PROC IDs. | Add the IDs to the slice command lists named in the finding text. |
| TE-F02 | S28 lacks `CMD-DUMPSYS`. S17 lacks `CMD-SPIKE-VERDICTS`. S40's AC-AFC-REV-01 needs `CMD-REVERIFY-APK` at IE-M5-3. | Covered by TE-F01; trace REV-01.R and SEC-01.R to S40 and IE-M5-3. |
| TE-F03 | `CMD-REVERIFY-APK` needs `check_paths.py --files`. | DES-AFC-GATE hygiene bullet plus an S09T test. |
| TE-F04 | coverage, diff-cover, mutmut, Kover and PIT are in no dependency list. Thresholds are TE proposals. | Amend DES-AFC-TV/INFRA and the S04/S05 stop conditions (via CMD-SCAN). Show the thresholds at integrated review. Otherwise these claims are typed gaps. |
| TE-F05 | No write set or store for UI screenshots and dumps (VIS-01). | Name `<review_evidence_dir>` or add `docs/evidence/visual/<slice>/` to the UI slice write sets. |
| TE-F06 | Fixed names: D4 trigger requests, the `tools/ci/tests` runner (unittest), spike verdict headings, `spikes/sp5/record.py`. | Copy them into the packets and DES-AFC-GATE. |
| TE-F07 | `CMD-TEMPLATE-DIGEST` changes to stack tags (SAM rewrites the template). | Adopt in the IE configuration identity and the S18 runbook. |
| TE-F08 | The `specialists/` logs and prompts contain absolute home paths; `CMD-PATH-SCAN-PLAN` will flag them. | Orchestrator scrubs them before the planning commit (entry criterion 2). |
| TE-F09 | Rows waiting on owner entry actions OWN-02..05 and the keystore. WATCH-02.D and ALERT-04.D may end as class C limitations. | Track them as OWNER_ACTION_PENDING typed gaps. |
| TE-F10 | CTRL-03 and SUB-04 depend on OD-AFC-03. The S41 rows depend on OD-AFC-01 = B. | Activate or drop them per the integrated-review dispositions. |

## Remaining risks

- **Typed gaps on this host.** adb, the Android SDK, Gradle, AWS SAM and the aws CLI are absent, so every device, Android and deploy command is a typed gap until S04 or S18 installs them after a scan. OpenJDK 21 is present, unlike the packet's "Gradle JDK absent".
- **Trigger checks are evaluations.** `CMD-SKILL-TRIGGER` and the D4/D5 activation rows rely on LLM skill selection, so they are evaluations, not deterministic proof.
- **E2E is not scripted.** `CMD-E2E-REPLAY` is a sequence of primitive adb steps with two manual D-pad navigation steps. It is not a tracked script, so reruns depend on following the SP-3 steps.
- **Coverage and mutation thresholds are unratified.** They are proposals until the integrated review.
- **COE-ASA-001 not read at clause level.** Only the identifier was verified. `SEIT-AFC-SPEC-02.B` relies on `spec_lint` section rules to enforce the floor.

## developer_feedback

- **TE-DX-01.** The dispatch packet says the Gradle JDK is absent, but `java -version` reports OpenJDK 21.0.12 at `/usr/bin/java`. The Android SDK and Gradle are absent.
  - Evidence: the `which` and `java -version` output in this session.
- **TE-DX-02.** `seit.schema.json` does not constrain `procedures_and_commands` item fields (`id`, `command`), the `traceability_matrix` columns, or `gate_declarations`. Schema validation alone cannot catch a missing command id or a malformed trace row; this session needed a scripted cross-check.
  - Evidence: `$HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/schemas/seit.schema.json` `properties`.
- **TE-DX-03.** `slice-graph.md` writes paired green slices as "same as S20T". Mechanical requirement extraction must resolve that phrase; this session skipped such rows because each pair shares its proof rows.
- **Tools exercised:** Bash, `python3` (`json`, `jsonschema`, `re`, `hashlib`), `jq`, `sha256sum`, `grep`, `ocr --help`, `reverify --help`, `java -version`, and the `test-engineer` and `test-engineering` skills. BRAN reported `unavailable` (no policy in this repository).
