# Planning and Design DELTA receipt: OR-01 relabel (Phase 1, correction round 2 of 2)

- **Role:** Planning and Design node, DELTA mode (`BEARING_ROLE=planning_and_design`)
- **Finding applied:** OR-01 (Orchestrator, packet error). Only this finding is applied.
- **Return:** `DELTA_APPLIED`
- **New candidate (manifest) digest:** `f213dcebb4e5acffa97ded459fbd69eea7298b4dc111d9e4bec3e9a642ee1d98`
  (was `253294a017eb51171ce795e25184f036a27a310afb8840793ff4f86a65863688`)
- **Rendered DoD Manifest:** sha256 `c772815ab57941c60fdd2e9318d991a8f5f1e4887bff18cef705203b58f36b6b`, template 1.0.1

## What changed

The owner's approved split (DEC-AFC-SD-023) now holds everywhere in the package:

- **Phase 1** contains D5 and D4, the hooks and this repository's gate (the D5/D4 waves, unchanged).
  It also contains the **spec track**: the requirements register, the SysML v2 models, D1 assembly with D5, and the owner's spec review.
- **Phase 2** contains implementation planning from the approved spec, then the full-detail milestones (D3), created after that plan is approved, then implementation.

### ID mapping

| Before | After | Phase |
|---|---|---|
| P2-1 | ST-1, open the spec-track plan directory and its journey | 1 (spec track) |
| P2-2 | ST-2, requirements register (Requirements Engineer) | 1 (spec track) |
| P2-3 (P2-3a, P2-3b/c) | ST-3 (ST-3a, ST-3b/c), SysML v2 models (Systems Modeler) | 1 (spec track) |
| P2-4 | ST-4, D1 assembly with D5 | 1 (spec track) |
| P2-5 | ST-5, owner spec review (closes the spec track) | 1 (spec track) |
| P2-6 | P2-6, unchanged | 2 |
| P2-7 | P2-7, unchanged | 2 |

### What did not change

- Content, sequencing, dependencies and roles are unchanged.
  - ST-2 and ST-3 are planning-role sessions that start at package approval, in parallel with the D5/D4 waves.
  - ST-4 waits for S06, S42 and S09 and for ST-2 PASS and ST-3 (c).
  - P2-6 waits for ST-5.
- Authority paths, slices, waves, SEIT ids, CMD and PROC ids, and requirement IDs are unchanged.
- These stable identifiers still carry "phase2" or "phase-2" and were deliberately left as they are:
  - the plan-directory glob `docs/plans/*-amazon-fantasy-companion-phase-2/`;
  - `evidence/phase2-entry-receipt.json`;
  - PROC-PHASE2-ENTRY, PROC-PHASE2-PLAN-INSPECT and DES-AFC-PHASE2;
  - the JSON keys `phase2_sequence`, `deferred_to_phase_2`, `phase2_entry_receipt` and `phase2_reference_ids`.

  `implementation.json` gains `phase2_sequence_note`, which records this mapping.
- Text that really is Phase 2 keeps its Phase 2 label:
  - RISK-AFC-17 (P2-6);
  - the android and backend gate areas;
  - the product Vnv areas;
  - the per-tool summary and friction log;
  - submission;
  - the product owner actions;
  - the product-lane IE findings;
  - the Phase 2 integrated review.

### By file

**Technical plan**
- Outcome now has a spec-track bullet and a Phase 2 bullet.
- The glossary rewrites Phase 1 and Phase 2 and adds two terms:
  - **spec track**;
  - **Phase 1 closeout**, which means this Lifecycle's D5/D4 wave closeout; the spec track ends at ST-5.
- The section is renamed **Phase 1 spec track and Phase 2 sequence**, with a mapping paragraph. Its table rows are relabelled and its Mermaid graph is updated.
- **Deferred to Phase 2** is renamed **Deferred to the spec track or Phase 2**:
  - its intro and the destination of each row are corrected;
  - rows for product implementation stay Phase 2.
- Exclusions now say "product *implementation* work".
- The wave target is reworded as "the Phase 1 D5/D4 waves exit by …".
- The exit criteria gain a note that the spec track closes at ST-5.
- The accountable controller now opens both the spec track and Phase 2.
- In the AC and RISK rows, the wording changes are limited to:
  - AC-AFC-PLAN-01 now reads "Phase 1 spec track and Phase 2 sequence";
  - AC-AFC-PLAN-03 now reads "spec-track entry receipt" and "each spec-track and Phase 2 entry criterion";
  - RISK-AFC-16 now reads "spec-track D1 assembly (ST-4)" and "spec-track requirements and model work (ST-2, ST-3)";
  - RISK-AFC-17 has its allocation and response reworded.

  No obligation changed. The mechanical AC lint output is byte-identical to `ac-mechanical-lint-p1.txt` (32 rows, 6 flagged, same as before).

**`design.md`**
- Revision note and intro updated.
- The heading of DES-AFC-PHASE2 is now "Spec track and Phase 2 sequence". Its ID is kept, and its body is relabelled.
- Product placements are now "spec-track input (ST-3)".

**`seit.json`, `implementation.json`, `authority.json`**
- Same relabels: "spec-track entry receipt", ST-n IDs, "spec-track plan directory", and "spec track or Phase 2" for deferral.
- Changes in `authority.json` text:
  - the allowed-scope wording now names the Phase 1 spec-track sessions ST-1..ST-3;
  - the role-grant labels changed;
  - the annotation on the prohibited `spec/**` now names ST-4 under the spec-track plan.

  Path globs are unchanged.
- DoD-manifest fields (bluf, outcome, scope, exclusions, requirement rows, risks, architecture, documentation) are relabelled. The render_status of V1..V3 is now "spec-track reference".

**Views**
- V4 `.mmd` and `.svg`: the D1 label is now "Phase 1 spec track, ST-4", the edge label is "spec track ST-4", D1 is described as "dashed consumer, not a D5/D4 slice", and the legend is updated.
- V5 `.mmd` and `.svg`: "Spec-track consumer (dashed, ST-4)", "serves ST-4", and the android/backend/Vnv line is labelled Phase 2.
- V6 `.svg`: product use cases now "return in the spec track (ST-3)".
- `views.json`: the question, concern, abstraction, interpretation and limitation texts are updated, and the `svg_sha256` values for V4, V5 and V6 are rebound.
- The SVGs were rendered in headless Chrome and checked: no text overflow in the boxes that changed.

## Digests re-embedded

| Artifact | New sha256 |
|---|---|
| technical plan | `f4afd24a982a255cf573e2838a8182506b99ea98acef1b6c05ed8e6f5747f982` |
| design.md | `f33b50c593ea766bf4ff50bc49c4e0201dedcf4afcd3edfbfb9cb0b07361308b` |
| views/views.json | `d54a59f85b8bff90c6761d25a104c22b3fca0842fe1e1bcedb32df62888b2ce6` |
| seit.json (in `implementation.json` source_baseline and identity) | `bf723abc2c673da423d142c8f95408f3e37de99d08037a151d25b2eed546b973` |
| candidate digest (`planning_review.candidate_digest` and the identity row) | `f213dcebb4e5acffa97ded459fbd69eea7298b4dc111d9e4bec3e9a642ee1d98` |

The V4, V5 and V6 SVG digests were rebound in both `views.json` and `implementation.json` `dod_manifest.models`.

## Commands and results

```text
node <bearing-lite 1.1.6>/hooks/plan-package.cjs <plan dir>
{ "outcome": "PASS", "manifest_digest": "f213dcebb4e5acffa97ded459fbd69eea7298b4dc111d9e4bec3e9a642ee1d98", "findings": [] }

python3 jsonschema Draft202012Validator
implementation.json schema_errors: 0
seit.json schema_errors: 0
authority.json schema_errors: 0

node <bearing-lite>/tools/render-dod-manifest.mjs implementation.json [--check]
RENDER_WRITE ... digest=sha256:c772815ab57941c60fdd2e9318d991a8f5f1e4887bff18cef705203b58f36b6b template=1.0.1
RENDER_CHECK_PASS digest=sha256:c772815ab57941c60fdd2e9318d991a8f5f1e4887bff18cef705203b58f36b6b template=1.0.1

rule 12 (absolute home-path shape count) over the technical plan, design.md, the three JSON files, the manifest and views/*: 0 in all 19 files
P2-[1-5] left in the manifest: 0;  "OPEN_CARRIED (closes at P2-6)" in the manifest: 2 (unchanged)
python3 specialists/ac_mechanical_lint.py <lint-sdoc.py> <technical plan>: identical to ac-mechanical-lint-p1.txt
```

`design.md` contains `C:\Users\<user>\`. It was already there before this delta, and it is a placeholder shape, not a real path.

## Not changed (outside this finding or not in the packet's file list)

- `journey.json`: it already matches the owner (DEC-AFC-SD-023).
- Specialist receipts and logs, including `integration-plan.md`, `slice-graph.md` and the RE, SM and TE receipts. They are historical records that still carry P2-n IDs; the mapping table above resolves them.
- No commits, pushes or branch operations. Writes stayed inside the plan directory. A pre-edit backup and the relabel script are in `/tmp/afc-relabel/`, outside the repository.

## developer_feedback

- **PD-OR01-OBS-1: global regex relabel clobbered its own mapping notes.**
  - Evidence: a generic `P2-[1-5] → ST-n` substitution ran after the manual mapping text was inserted. It turned "ST-1..ST-5 (were P2-1..P2-5)" into "(were ST-1..ST-5)" in three places.
  - Fix: I caught it with a residual grep and corrected it with exact-match asserts.
  - Lesson: when a delta adds old-to-new mapping text, apply the ID relabel before inserting that text, or exclude it from the substitution.
- **PD-OR01-OBS-2: the view digest chain has a second hop.**
  - Relabelling SVG text changes the `svg_sha256` values in `views.json`, which changes the `views.json` planning-input digest, which changes the `seit.json` digest, and finally the candidate digest.
  - The freeze checks only the last two hops, so a stale `svg_sha256` would pass the freeze silently. I rebound it by hand.
  - Suggestion: have `plan-package.cjs` verify the `views.json` `svg_sha256` values against the files.
- **PD-OR01-OBS-3: `evaluatePlanningReview` call shape.**
  - When I called it with the plan directory path, it returned `NEEDS_MORE_EVIDENCE` / `planning_review_missing`. The earlier receipt recorded `review_round_pending`, so the call shape probably differs.
  - I did not investigate further: presenting the review is the Orchestrator's gate.
- **Tools used:** python3 (json, jsonschema, hashlib, PIL), node (plan-package freeze, render-dod-manifest write and `--check`, planning-review), headless google-chrome for the SVG checks, grep, sed, sha256.
