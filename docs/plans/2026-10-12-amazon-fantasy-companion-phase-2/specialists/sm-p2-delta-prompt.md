ROLE
Systems Modeler, planning session (BEARING_ROLE=systems_modeler), Phase 2 Planning and Design delta for Lifecycle AFC-2026-10-11 (Amazon Fantasy Companion). RESPONSIBILITY: align the product SysML v2 models and allocation with the amended register (DEC-AFC-SD-035) so Phase 2 implementation slices can trace to current model elements; parse-check the result in SysON. You do not author requirements, design, SEIT or slices.

Load and follow (absolute SKILL.md paths; $HOME is the invoking user's home):
- $HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/skills/systems-modeler/SKILL.md
- $HOME/.agents/skills/sysml-modeling/SKILL.md

STATE
Facts (cwd = the Phase 2 planning worktree; PLAN = docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/):
- Register of record: PLAN/requirements-register.md, 66 UIDs AFC-PR-001..066 (049..051 Withdrawn by DEC-AFC-SD-035, UIDs retained). PR-047 is now "full-screen lineup panel in the companion app" when the panel-beside-provider-video spike fails or exceeds 24 h (no Mode A sample footage, no companion player). PR-048: under that full-screen panel, alerts and Watch still route to the real provider apps. PR-066 (new): the TV app records the customer's manual-lineup scoring preset (PPR or Half-PPR, default Half-PPR). PR-065: backend scores manual lineups under the selected preset; Yahoo leagues use Yahoo scoring.
- Models: PLAN/models/AFC-{Structure,Interfaces,States,Data}.sysml, PLAN/models/allocation.md (says 65 UIDs), PLAN/models/views.md, PLAN/models/view-*.svg. ST-3d SysON parse PASS receipt: PLAN/specialists/sm-syson-receipt.md (project afc-product-models 2a033855-6bae-4fe1-975c-00bbb9419100, combined digest 14fb815b…).
- Known stale content (approved spec spec/amazon-fantasy-companion/04.7-model-correspondence.md says "retained pending Phase 2 design"): `tvApp.player` part (Mode A only), `PanelMode.modeA` doc text "companion player with labeled sample footage", allocation rows mapping PR-047/048 to modeA/player and PR-049..051 to tvApp.player, no allocation for PR-066, allocation header says 65.
- Spec is read-only for you (a later spec-and-docs slice aligns its 4.7/4.1.12 text and figure).

OBJECTIVE
1. Edit the models with minimal semantic change: remove part `tvApp.player`; rename `PanelMode.modeA` to `PanelMode.fullScreen` (doc: full-screen lineup panel in the companion app, no stand-in video, PR-047; alerts and Watch still route to the real provider apps, PR-048), keeping `modeB` and the `spikeFailed` transition (modeB -> fullScreen); add the manual scoring preset to the data model (e.g. enum def ScoringPreset {ppr; halfPpr;} and a Settings attribute `scoringPreset : ScoringPreset` defaulting to halfPpr if the grammar allows a default, else documented), with no other changes.
2. Update allocation.md: 66 UIDs; PR-047 -> tvApp.panel, PanelMode, PanelMode.modeB, PanelMode.fullScreen; PR-048 -> tvApp.notifier, tvApp.launcher, TvProviderLaunch, TvFireOSNotify, PanelMode.fullScreen; PR-049..051 -> "Withdrawn (DEC-AFC-SD-035); no element"; PR-065 add ScoringPreset; PR-066 -> tvApp.profileUI, stores.profileStore, Settings, ScoringPreset; Table 2 reverse map consistent (every element >=1 UID; withdrawn UIDs excluded from the every-element rule). Re-run your allocation/register cross-check probes (ST-3b/c probe adapted; run from the system temp dir, do not commit probe files): register active UID set == allocation UID set (63 active + 3 withdrawn recorded).
3. Regenerate the affected view SVGs (structure, states, data; interfaces only if touched) and views.md digests/notes. Keep the renderer-safe SVG subset already used (no script, foreignObject, external hrefs).
4. Parse-check per DEC-AFC-SD-032: create ONE new SysON project `afc-product-models-p2` via SysON's own textual import (same GraphQL createProject + uploadDocument path as sm-syson-receipt.md), upload all four files, record project id, per-file diagnostics, and repair real model errors only; re-upload into the same new project until clean.
5. Record the new combined digest (sha256 over the four .sysml concatenated in sorted filename order) and per-file sha256 values.

AUTHORITY
Allowed writes: PLAN/models/** and PLAN/specialists/sm-p2-delta-receipt.md only. Allowed host action: create ONE new SysON project and upload into it (local dev/test host; agent work).
Prohibited: every other path (the register, spec, technical plan, design, seit, implementation files); modifying, deleting or importing into any other SysON project; the Requirements System CLI registry/checkout (`model load`, `checkout create`, `--replace`); the active Maestro checkout; installing software; anything needing an API key; commits, pushes, branch operations, GitHub mutations. Never write an absolute local home path into any file (rule 12). Other agents may work concurrently in PLAN; touch only your write set.

LOOP
Edit -> local allocation probe -> SysON import -> classify each diagnostic (model error / SysON limitation / environment) -> repair real model errors -> re-import. Retry only with new evidence. At most three repair rounds.

VERIFY
Report verbatim: allocation probe output, register cross-check output, SysON per-file import results, the new combined digest and per-file sha256, and `grep -rn "player\|modeA\|footage" PLAN/models` output (expect no live references except withdrawal notes).

RETURN (in the receipt and as your final message)
READY | REPAIRABLE_FAILURE | ENVIRONMENT_FAILURE | NEEDS_MORE_EVIDENCE; changed paths; SysON project id; diagnostics before/after; allocation result; digests; the element list the Phase 2 plan should trace to (one line per changed or new element); remaining risks; developer_feedback section (observation IDs with tool, version, task, expected/actual, workaround, would-use-again, or "no new observations" naming the tools exercised).

STOP
After a clean import plus passing allocation probes, or a typed failure with the exact error.
