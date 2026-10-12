# Planning and Design DELTA receipt: planning review P1 repair

- **Role:** Planning and Design node, DELTA mode (`BEARING_ROLE=planning_and_design`)
- **Input:** `specialists/planning-review-p1.md` (REPAIR_REQUIRED, FP1-01..FP1-03), reviewed candidate `82e767d57c5ff5d5b8f070349a77cedf7ef60793`
- **Policy:** the single aggregated repair after review (review-policy.md). After it, deterministic PASS decides; there is no re-review.
- **Return:** `DELTA_APPLIED`
- **New candidate (manifest) digest:** `23a97b492e5de074de44ad01ec7489567a1fea8a6c61aaf9e768932d85911a37`
  (was `f213dcebb4e5acffa97ded459fbd69eea7298b4dc111d9e4bec3e9a642ee1d98`)
- **Rendered DoD Manifest:** sha256 `76b591f0c0e15eabf1a74af87870f484cbd99b943411a942ce86b26f7d2e7b8c`, template 1.0.1

## Per-finding disposition

| ID | Disposition | What changed |
|---|---|---|
| FP1-01 | FIXED, as the reviewer's fix text says | `requirement_ids`: S06 +RISK-AFC-16; S07 +AC-AFC-PATH-01; S06L +AC-AFC-PATH-01; S42 +AC-AFC-PATH-01, +RISK-AFC-16; S11 +RISK-AFC-13; S08 +AC-AFC-CI-02. S08 `seit_proof_rows` +SEIT-AFC-DX-01. Traceability `slices`: CI-02 +S08; PATH-01 +S07, S06L, S42; RISK-13 +S11; RISK-16 +S42. TP Allocation: CI-02 → "S09T, S09, S08; repo gate workflow"; RISK-13 → "S06, S09, S11; acquisition receipts". `design_ids` unchanged. The `dod_manifest.requirements` mirror rows (`slices`, `allocation`) got the same edits so they still agree with traceability and the TP. |
| FP1-02 | FIXED, as the reviewer's fix text says | `, OA-AFC-A3` appended inside the parenthesis of both strings: the OWN-P1-01 `action` and the `approval_boundaries` `owner_action`. The script asserted exactly 2 replacements. Both now match Wave 1 entry (`:226`). |
| FP1-03 | FIXED, per the packet's instruction instead of the reviewer's text | `journey_settings.planning_review.candidate_revision` = `82e767d57c5ff5d5b8f070349a77cedf7ef60793`, the reviewed candidate. A commit cannot name its own hash, so the reviewer's "repair commit hash" is not writable. `repair_revision` = "recorded by the Orchestrator in journey.json after the repair commit". `candidate_ref` is unchanged and `candidate_digest` is rebound. |

A mechanical orphan-proof check now finds no mismatches. It covers three things:
- every proof row's requirement is declared on its slice;
- every declared requirement has a proof row on that slice;
- traceability `slices` equals the set of slices that declare the requirement, for all 32 rows.

## Digests re-embedded

| Artifact | Old | New | Where |
|---|---|---|---|
| technical plan | `f4afd24a…5f982` | `dfc1b9b2c92a7f4030d4a95464f190235da4e93b30f3dafd9fcf02cc61112cd6` | `seit.json` planning_inputs; `implementation.json` source_baseline and `dod_manifest.identity`; manifest |
| seit.json | `bf723abc…6b973` | `4c64a1032b1ff91ec9ef16bfa4efd9641ab4919f1aef84df6894ff3f2cd4c7e7` | `implementation.json` `seit_json_sha256_at_integration` and identity; manifest |
| candidate digest | `f213dceb…98` | `23a97b492e5de074de44ad01ec7489567a1fea8a6c61aaf9e768932d85911a37` | `planning_review.candidate_digest` and the identity row; manifest |

These digests did not change: `design.md` (`f33b50c5…`), `views/views.json` (`d54a59f8…`) and the views SVGs. The stale-digest sweep finds 0 occurrences of the old TP, seit, candidate and manifest digests in the TP, `design.md`, the JSON files and the manifest.

## Commands and results

```text
node <bearing-lite 1.1.6>/hooks/plan-package.cjs <plan dir>                  exit 0
{ "outcome": "PASS", "manifest_digest": "23a97b492e5de074de44ad01ec7489567a1fea8a6c61aaf9e768932d85911a37", "findings": [] }

node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json  exit 0
RENDER_WRITE ... digest=sha256:76b591f0c0e15eabf1a74af87870f484cbd99b943411a942ce86b26f7d2e7b8c template=1.0.1
node <bearing-lite 1.1.6>/tools/render-dod-manifest.mjs implementation.json --check   exit 0
RENDER_CHECK_PASS digest=sha256:76b591f0c0e15eabf1a74af87870f484cbd99b943411a942ce86b26f7d2e7b8c template=1.0.1

python3 jsonschema Draft202012Validator (<bearing-lite 1.1.6>/schemas)       exit 0
implementation.json 0 | seit.json 0 | authority.json 0 | journey.json 0 schema_errors

rule 12: home-path shape scan (/home/<user>/, /Users/<user>/, C:\Users\<user>\ with a real segment)
over the TP, design.md, *.json, the manifest and views/*: 0 hits

python3 -B specialists/ac_mechanical_lint.py <lint-sdoc.py> <technical plan>  exit 0
output byte-identical to specialists/ac-mechanical-lint-p1.txt (Allocation column only; no statement changed)
```

The manifest diff against the pre-edit render shows only the three identity digests (candidate, TP, seit). The template does not render requirement `allocation`/`slices`, OWN-P1-01 or `approval_boundaries`, so FP1-01/02 do not change the manifest's visible text.

## Write set

- `amazon-fantasy-companion-technical-plan.md`: 2 Allocation cells.
- `implementation.json`: FP1-01, FP1-02, FP1-03 and the digest rebinds.
- `seit.json`: the TP sha256 only.
- `amazon-fantasy-companion-dod-manifest.html`: re-rendered.
- This receipt.

No commits, pushes or branch operations. `journey.json`, `design.md`, `authority.json` and the views are untouched. A pre-edit backup is in `/tmp/afc-delta-p1/`, outside the repository.

## developer_feedback

- **PD-FP1-OBS-1: the orphan-proof check belongs in the freeze.**
  - FP1-01 regressed silently through regeneration: `plan-package.cjs` PASSed with orphan proofs.
  - The 3-way check used here is about 20 lines over `slices[].requirement_ids`, `slices[].seit_proof_rows`, `seit.json proof_cases[].requirement_id` and `traceability[].slices`.
  - Suggest adding it to the Plan Integrator freeze or `plan-package.cjs`.
- **PD-FP1-OBS-2: `dod_manifest.requirements` carries a third copy of allocation/slices.**
  - It duplicates the TP and traceability but is not rendered, so drift there is invisible in the manifest.
  - Either render it or derive it.
- **PD-FP1-OBS-3: the review asked for something no commit can do.**
  - FP1-03's reviewer fix ("set `candidate_revision` to the repair commit hash") is self-referential. The packet resolved it.
  - The review-policy text could state that `candidate_revision` names the reviewed candidate and `repair_revision` is Orchestrator-recorded post-commit.
- **Tools used:** python3 (json, jsonschema, exact-match asserts), node (plan-package freeze, render-dod-manifest write and `--check`), sha256sum, sed (digest rebinds), grep, cmp, diff.
