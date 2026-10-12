# Planning and Design delta R1 receipt (planning review R1 repair)

- Role: Planning and Design, DELTA mode (single aggregated repair after
  `planning-review-r1.md`, verdict REPAIR_REQUIRED). No fresh package, no commit.
- Reviewed candidate: `4afc998ed2fd4a19a28fdfb9d7f815452a60cce5`, digest
  `87fa24334fda312e61582c169cfe9b3c205f989ff30cd6edc7017bf4a9ee78f3`.
- New manifest digest (`plan-package.cjs`): **`2300046ae30b2b9afdceccd1384983f30c0a4840060008635a0990635dcb9621`**
- Rendered DoD Manifest: `sha256:3a60b38e3b7719fe923c6220088f2c25047567a890adb2a617e0f67423d66c2e` (template 1.0.1)
- Write set: `amazon-fantasy-companion-technical-plan.md`, `seit.json`,
  `implementation.json`, `amazon-fantasy-companion-dod-manifest.html`,
  `specialists/slice-graph.md`, this receipt. All inside the plan directory.
  `design.md`, `views/`, `journey.json` and `authority.json` unchanged.

## Return: DELTA_APPLIED

## Per-finding disposition

| ID | Disposition | Where (file:line after repair) |
|---|---|---|
| FR-01 | Fixed. OA-AFC-A1 and OA-AFC-A2 rows appended to Open owner decisions, decision and recommendation copied verbatim from `implementation.json` open_decisions. Entry criterion 1 now names the 13 items. | TP `:363-364` (entry criterion), `:424-425` (rows) |
| FR-02 | Fixed per Orchestrator decision. `candidate_revision` = reviewed candidate `4afc998e…`; `repair_revision` added ("recorded by the Orchestrator in journey.json after the repair commit"); `candidate_digest` rebound to the new manifest digest. | `implementation.json:103-105` |
| FR-03 | Fixed. Manifest §2 `seit.json` value now equals the shipped `seit.json` hash `bd3b4f0b…` (post-delta; the reviewer's `bc02a21f…` was itself superseded by this delta's seit.json edits). `:40` `seit_json_sha256_at_integration` kept as the historical at-integration record. | `implementation.json:10977`; manifest `:711` |
| FR-04 | Not picked, per Orchestrator decision. TE-F05 presented to the owner as **OD-AFC-11** (option 1: commit under `docs/evidence/visual/<slice>/` + add to S25/S26/S27/S31/S32 write sets; option 2: untracked Lifecycle evidence dir in `journey.json` `execution_receipts`). Test Engineer named both options without a preference (`test-engineer-receipt.md:90`), so the row says "owner's choice" and states each option's consequence. Write sets unchanged pending the decision. Also: OD-AFC-11 added to the five slices' `human_decision.open_decisions`, a manifest owner-decision event, the TE-F05 DoD risk row (status "open (owner decision OD-AFC-11)"), and seit.json TE-F05 `owner_decision: true`. | TP `:423`; `implementation.json:10854` (open_decisions), `:5295,5564,5840,6490,6745` (S25/S26/S27/S31/S32), `:13923` (risk); `seit.json:137` (open_items), `:6440`; manifest `:3357-3359`, `:3496` |
| FR-05 | Fixed, extended to 13 items: "(OD-AFC-01..11, OA-AFC-A1..A2)" in approval_boundaries and the manifest owner-entry event; also `specialists/slice-graph.md:110`. BLUF count updated to "13 open owner items (OD-AFC-01..11, OA-AFC-A1..A2)". | `implementation.json:10733`, `:14053`, `:10937`; manifest `:676`, `:3516`; `slice-graph.md:110` |
| FR-06 | Fixed: "costs one judgement slice (S41," in all three locations (manifest OD-AFC-01 event regenerated from source with the same truncation rule). | TP `:413`; `implementation.json:10786`; `seit.json:80` |
| FR-07 | Fixed with the reviewer's exact text: "stack tags SourceCommit (= deployed commit) and TemplateSha256 (= sha256 of backend/template.yaml at that commit), read by CMD-TEMPLATE-DIGEST". TE-F07 DoD risk row closed ("closed (planning delta R1)"). | `implementation.json:8872`, `:13930` |
| FR-08 | Fixed: TP AC-AFC-SUB-03 Verification = `demonstration` (matches `SEIT-AFC-SUB-03`). The derived manifest requirements row was aligned too. | TP `:254`; `implementation.json:11921` |
| dev-feedback (2) | Fixed. `seit.json decision_baseline.open_items` now carries 13 items (OD-AFC-01..11, OA-AFC-A1..A2); the reviewer's 12 plus OD-AFC-11 from FR-04. | `seit.json:137-154` |

## Digest re-embedding

| Input | Old | New |
|---|---|---|
| technical-plan.md (seit + implementation planning_inputs, manifest §2) | `9bda1ff5…` | `f413d1bcebd134d2c569dca2fb4b702ea3efe8dcd9dedd9856e597f8128df3ce` |
| design.md | `d83150f7…` | unchanged |
| views/views.json | `965a8b8c…` | unchanged |
| seit.json (manifest §2) | `cae54c15…` (stale) | `bd3b4f0bd4cc1dced3c58ffe4d8cf3686a698001d31b87b8eedbdf414232f91a` |
| candidate_digest | `87fa2433…` | `2300046ae30b2b9afdceccd1384983f30c0a4840060008635a0990635dcb9621` |

JSON files were rewritten in their existing serialization (round-trip verified
byte-identical before editing: implementation.json indent 2 / UTF-8, seit.json
indent 1 / UTF-8).

## Commands and exit codes

Run from the repository root; `$B` = the bearing-lite 1.1.6 plugin cache.

| Command | Result | Exit |
|---|---|---|
| `node $B/hooks/plan-package.cjs docs/plans/2026-10-11-amazon-fantasy-companion` | `PASS`, manifest_digest `2300046a…9621`, `findings: []` | 0 |
| `node $B/tools/render-dod-manifest.mjs <plan>/implementation.json` | `RENDER_WRITE … digest=sha256:3a60b38e…6c2e template=1.0.1` | 0 |
| `node $B/tools/render-dod-manifest.mjs <plan>/implementation.json --check` | `RENDER_CHECK_PASS digest=sha256:3a60b38e…6c2e` | 0 |
| `python3` + `jsonschema` 4.19.2: implementation.json vs `$B/schemas/implementation.schema.json` | VALID | 0 |
| `python3` + `jsonschema` 4.19.2: seit.json vs `$B/schemas/seit.schema.json` | VALID | 0 |
| `grep -nE "/home/[a-z]\|/Users/\|C:\\\\Users"` over TP, implementation.json, seit.json, manifest, slice-graph.md | 2 hits, both pre-existing detector regexes in seit.json command text (`:563`, `:1109`); no literal home path | 0 |
| `grep -c "OD-AFC-01..06\|costs one light slice\|cae54c15…"` on the manifest | 0 | 1 |

## developer_feedback

- FR-03's target value moved: any delta that touches seit.json re-stales the
  manifest §2 `seit.json` row, and `plan-package.cjs` does not compare that row
  to disk (it only checks planning_inputs and candidate_digest). A check that
  the rendered `seit.json` identity row equals `sha256(seit.json)` would have
  caught FR-03 mechanically.
- The prompt asked for a 12-item `open_items` refresh and a 13-item range; I
  used 13 everywhere (OD-AFC-11 included) so the projection matches
  `implementation.json`.
- OD-AFC-11 option 1, if chosen, needs a follow-on mechanical delta: add
  `docs/evidence/visual/<slice>/` to five write sets and rewrite the SEIT `<review_evidence_dir>`
  evidence paths of the UI-slice proof cases (S25/S26/S27/S31/S32). Option 2 needs no package change.
- Orchestrator to do: record the repair commit hash in `journey.json` (FR-02)
  and the new digest `2300046a…9621`; `journey.json` was not touched here.
