# P2 Delta Receipt — Systems Modeler model/allocation alignment (DEC-AFC-SD-035)

- Verdict: READY
- Role: Systems Modeler, planning session (`BEARING_ROLE=systems_modeler`)
- Lifecycle: AFC-2026-10-11, Phase 2 Planning and Design delta
- Packet: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/sm-p2-delta-prompt.md`
- Skills loaded: `systems-modeler`, `sysml-modeling`
  (`use-requirements-system` consulted read-only for host discovery, as at ST-3d)
- Register of record: `requirements-register.md`, 66 UIDs AFC-PR-001..066
  (63 active; AFC-PR-049..051 Withdrawn by DEC-AFC-SD-035, UIDs retained)
- Changed paths (write set only; no commits, no other paths, no absolute paths):
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/AFC-Structure.sysml`
    (removed `tvApp.player`; register-range cite 066)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/AFC-States.sysml`
    (`PanelMode.modeA` → `PanelMode.fullScreen` + doc; transition
    `t_modeB_modeA` → `t_modeB_fullScreen`; `spikeFailed` kept;
    register-range cite 066)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/AFC-Data.sysml`
    (new `enum def ScoringPreset` with `ppr`, `halfPpr`; new
    `Settings.scoringPreset : ScoringPreset` defaulting to
    `ScoringPreset::halfPpr`; header item list + register-range cite 066)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/allocation.md`
    (66 UIDs: PR-047/048 re-allocated, PR-049..051 withdrawn rows, PR-065
    gains ScoringPreset, new PR-066 row; Table 2 164 elements; P2 delta note;
    P2 digest cite; four latent ST-3 reverse-map mismatches repaired, see §3)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/views.md`
    (P2 digests, P2 SysON closure note, V-ST3b-1/3/4 metadata updates)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/view-structure.svg`
    (player removed, full-screen note, PR ranges, digest cite)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/view-states.svg`
    (modeA → fullScreen, player dropped from owner line, digest cite)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/view-data.svg`
    (scoringPreset row, ScoringPreset strip, PR updates, digest cite)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/view-interfaces.svg`
    (`<desc>` digest cite only)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/sm-p2-delta-receipt.md`
    (this file)
- Untouched by design: `AFC-Interfaces.sysml` (byte-identical; per-file
  digest `504cfcb8…` unchanged); every other SysON project; the Maestro
  checkout; the Requirements System checkout/registry (no `model load`, no
  `checkout create`; `status`/`binding` used read-only for host discovery).
- Repair rounds used: 0 of 3 (first import clean; no model errors found).

## 1. SysON parse-check (DEC-AFC-SD-032 path)

- New project: `afc-product-models-p2` (the one authorized new project)
- Project id: `7b4735e8-a400-4534-88d0-903d977daf82`
- Editing context id: `d7df4524-63f2-47ab-ab3a-d18702ab5fc5`
  (resolved via `viewer.project.currentEditingContext`)
- Template: `sysmlv2-template`, `libraryIds: []`; endpoint: SysON GraphQL
  on loopback, mutations `createProject` + multipart `uploadDocument`
  (frontend-exact shape: single `$input` variable, map string form
  `{"0":"variables.file"}` — verified against the shipped bundle, see
  developer_feedback OBS-SMP2-01).
- Import is a genuine parse: the server log shows each upload parsed by
  SysON's bundled textual engine (`File Parsed`, `N references to resolve`,
  `Document <uuid> uploaded`).

## 2. Import diagnostics before → after (per file, in upload order)

Before: no diagnostics — every file imported clean on its first upload.
After: unchanged (no repairs, no re-uploads). Verbatim per-file results:

1. `AFC-Data.sysml`: `{"data":{"uploadDocument":{"__typename":"UploadDocumentSuccessPayload","id":"19102c04-f45c-422a-9e8d-bd1a7efce287","report":""}}}`
2. `AFC-Interfaces.sysml`: `{"data":{"uploadDocument":{"__typename":"UploadDocumentSuccessPayload","id":"0ca3bc00-f06c-4142-b33b-f133b0abc64d","report":""}}}`
3. `AFC-States.sysml`: `{"data":{"uploadDocument":{"__typename":"UploadDocumentSuccessPayload","id":"63442a84-c1f0-449f-9e10-a5cd18af7b1c","report":""}}}`
4. `AFC-Structure.sysml`: `{"data":{"uploadDocument":{"__typename":"UploadDocumentSuccessPayload","id":"3ba21eed-13ae-4546-87f2-91795f663275","report":""}}}`

(Empty-string `report` = zero errors, zero warnings; ST-3d observed the
same field as null on its clean rounds.)

Final state: all four files import with zero errors and zero warnings.
No diagnostic remains to classify as model error, SysON limitation,
or environment failure.

Server-log corroboration (read-only; thread `3a-d18702ab5fc5`, my
editing context; full UUIDs here, abbreviated above):

- `AFC-Data.sysml`: `File Parsed`, `39 references to resolve`,
  `Document 27bf1c0c-cb0d-4320-b123-d284b64c1b8d uploaded`
  (ST-3d: 37 refs — the +2 are the new `ScoringPreset` typing and the
  `ScoringPreset::halfPpr` default reference, both resolved with no
  "Unable to resolve" warnings, so the grammar-default form holds and
  the value binding resolves)
- `AFC-Interfaces.sysml`: `File Parsed`, `0 references to resolve`,
  `Document dc6ae902-399a-4c1e-b923-63e193e221d1 uploaded`
- `AFC-States.sysml`: `File Parsed`, `39 references to resolve`,
  `Document 5fdcd2c0-cb88-4faa-ad7e-6285655efc29 uploaded`
  (same count as ST-3d: rename-only, `spikeFailed` transition intact)
- `AFC-Structure.sysml`: `File Parsed`, `8 references to resolve`,
  `Document 99a8e599-7dfe-4694-9567-bf8f3f240d29 uploaded`
  (same count as ST-3d)

Parsed-model read-back (GraphQL `search`, whole-word, my context only):

- `fullScreen` → `StateUsage` present; `ScoringPreset` →
  `EnumerationDefinition` with `ppr`/`halfPpr` `EnumerationUsage`s;
  `scoringPreset` → `AttributeUsage` present; `modeA` → 0 matches;
  `player` → 1 Documentation-prose match only, no structural element.

Residue in the new project: one trivial `package P {}` probe document
(`t.sysml`, doc `a994e56d-29a5-4d88-ade7-ae4c89075358`, 0 refs) uploaded
while establishing the working multipart shape. Re-upload creates a new
document and the schema exposes no document-delete mutation, so it is
named here instead of silently kept. No other project was touched.

## 3. Allocation (66 UIDs; probe adapted from ST-3b/c)

Table 1: 66/66 recorded — 63 active UIDs each with ≥1 element;
PR-049/050/051 recorded as `Withdrawn (DEC-AFC-SD-035); no element`.
Table 2: 164/164 elements carry ≥1 UID, `via <parent>` inheritance, or
the one stated reason (`externals` grouping). No Table 2 row cites a
withdrawn UID. Element counts: AFCStructure 49 (7 port defs, 4 tops,
30 subparts, 8 port usages); AFCInterfaces 24 (8 defs, 16 ends);
AFCStates 38 (3 defs, 13 states, 10 signals, 12 transitions); AFCData
53 (8 defs, 37 attributes, 8 enum values).

Latent ST-3 reverse-map mismatches found by the stricter bidirectional
probe and repaired Table-2-side only (Table 1 untouched apart from the
mandated P2 rows; each fix checked against the register row):

- `Settings` gains `010` (PR-010 Table 1 row lists Settings; DETECTOR, PROFILE)
- `Alert` gains `028`, `046` (both Table 1 rows list Alert)
- `tvApp.profileUI` drops erroneous `044` (PR-044 Table 1 row has no
  profileUI; tags are PANEL, PANELSVC, not PROFILE)
- `PanelMode` gains `041` (PR-041 Table 1 row lists PanelMode)

Probes live under the system temp dir and are not committed:
`smp2_check.py` (29 checks), `smp2_xcheck.py` (register cross-check).

Verbatim allocation probe output:

```text
[PASS] T1-has-all-66-UIDs
[PASS] T1-active-have-elements
[PASS] T1-withdrawn-recorded-no-element
[PASS] T2-count-164
[PASS] T2-single-reason-externals
[PASS] T2-no-withdrawn-cites
[PASS] T2-uid-tokens-wellformed
[PASS] T1-elements-resolve-in-T2
[PASS] T2-back-consistent-with-T1
[PASS] T1-forward-consistent-with-T2
[PASS] via-targets-exist-nonvia
[PASS] sysml-declared-count-164
[PASS] sysml-set-equals-T2
combined=8f5798823b3a9463f8963c7c6fa2cf94d018189edd0ca6160123362d48a075ff
  AFC-Data.sysml 4fcb3174666f80f13e405230c5e0df2498d2c6d62ea584160bd249f966f14031
  AFC-Interfaces.sysml 504cfcb82dd83beca534d463dde1c07f2714d56ce26390c4519c5f55ac7a4851
  AFC-States.sysml 3055e76043cf6c1b7763aa7804b61dfd9ec4a8095fb954ec4b77ee1dd9cd7904
  AFC-Structure.sysml 54b87c488cadd65c825b6a66b3308cc7920bd7d32eb05cfa7ac789902dc0221c
[PASS] views-cites-combined
[PASS] alloc-cites-combined
[PASS] views-cites-AFC-Data.sysml
[PASS] views-cites-AFC-Interfaces.sysml
[PASS] views-cites-AFC-States.sysml
[PASS] views-cites-AFC-Structure.sysml
[PASS] view-structure.svg-parse+digest
[PASS] view-structure.svg-renderer-safe
[PASS] view-interfaces.svg-parse+digest
[PASS] view-interfaces.svg-renderer-safe
[PASS] view-states.svg-parse+digest
[PASS] view-states.svg-renderer-safe
[PASS] view-data.svg-parse+digest
[PASS] view-data.svg-renderer-safe
[PASS] no-absolute-home-paths
[PASS] removed-names-only-in-alloc-note
grep hits (8):
  AFC-Data.sysml:22:attribute playerIds : String;
  AFC-States.sysml:28:* detected: event ingested. matched: player/event identity resolved
  allocation.md:30:P2 delta (DEC-AFC-SD-035): `tvApp.player` removed with withdrawn
  allocation.md:31:AFC-PR-049..051 (Mode A sample footage refused, no companion player);
  allocation.md:32:`PanelMode.modeA` renamed to `PanelMode.fullScreen`; `ScoringPreset`
  allocation.md:251:| GameEvent.playerIds | via GameEvent |
  view-data.svg:11:<text x="34" y="124" font-size="12">possession, playerIds,</text>
  views.md:93:| Interpretation | Boxes are parts; labeled ports bind to the interfaces in V-ST3b-2; `ext
RESULT OK — 29/29 checks
```

Verbatim register cross-check output:

```text
alloc: active=63 withdrawn=['AFC-PR-049', 'AFC-PR-050', 'AFC-PR-051']
reg:   active=63 withdrawn=['AFC-PR-049', 'AFC-PR-050', 'AFC-PR-051']
REGISTER-CROSSCHECK OK
```

Verbatim `grep -rn "player\|modeA\|footage" PLAN/models` output
(no live references; matches are the live `playerIds` identity
attribute, `player/event` doc prose, and the P2 withdrawal/delta
notes in `allocation.md` and `views.md`):

```text
models/view-data.svg:11:  <text x="34" y="124" font-size="12">possession, playerIds,</text>
models/AFC-Data.sysml:22:        attribute playerIds : String;
models/views.md:93:| Interpretation | Boxes are parts; labeled ports bind to the interfaces in V-ST3b-2; `externals` members are endpoints, not repo code; no companion player — the panel falls back to full-screen (C5) |
models/allocation.md:30:P2 delta (DEC-AFC-SD-035): `tvApp.player` removed with withdrawn
models/allocation.md:31:AFC-PR-049..051 (Mode A sample footage refused, no companion player);
models/allocation.md:32:`PanelMode.modeA` renamed to `PanelMode.fullScreen`; `ScoringPreset`
models/allocation.md:251:| GameEvent.playerIds | via GameEvent |
models/AFC-States.sysml:28:        * detected: event ingested. matched: player/event identity resolved
```

## 4. Digests (P2 delta revision)

- Combined (sha256 over the four native `.sysml` sources concatenated
  in sorted filename order):
  `8f5798823b3a9463f8963c7c6fa2cf94d018189edd0ca6160123362d48a075ff`
- Per-file sha256 over `models/`:
  - AFC-Data.sysml `4fcb3174666f80f13e405230c5e0df2498d2c6d62ea584160bd249f966f14031`
  - AFC-Interfaces.sysml `504cfcb82dd83beca534d463dde1c07f2714d56ce26390c4519c5f55ac7a4851`
  - AFC-States.sysml `3055e76043cf6c1b7763aa7804b61dfd9ec4a8095fb954ec4b77ee1dd9cd7904`
  - AFC-Structure.sysml `54b87c488cadd65c825b6a66b3308cc7920bd7d32eb05cfa7ac789902dc0221c`
  - allocation.md `d206b170c871de57aabe639bdf3f3f8787daad1c9d5245f75f463fdd501118cb`
  - view-data.svg `70f524ffadbc726e0f2eddf1daf76ae75588167eb1d129d4d100167ed980d909`
  - view-interfaces.svg `a36f182c8d3f8bb429e032be1900db9640cf9893a22a11f8223fa2e424752ef2`
  - view-states.svg `b25bdcbb60f0e704072c1037c1fe70d30be872bc1a81bb018bcf078252bc8560`
  - view-structure.svg `b3ff61d868d9d082bad125feeb4abe4b306c7685ff513dfc9d5c664da514b00e`
  - views.md `4557a805853cbc17ca4ab5c706edee3922d5dd9122215f6270b81781215b3afc`

## 5. Element list for Phase 2 plan tracing (one line per changed/new element)

- `tvApp.player` — REMOVED (withdrawn with AFC-PR-049..051); slices must not trace here
- `PanelMode.fullScreen` — renamed state (ex modeA), PR-047 + PR-048
- `PanelMode.t_modeB_fullScreen` — renamed transition (modeB → fullScreen on spikeFailed), via PanelMode
- `PanelMode` — now PR-041 + PR-047 (041 cite restored)
- `ScoringPreset` — new enum def, PR-065 + PR-066
- `ScoringPreset.ppr` — new enum value, via ScoringPreset
- `ScoringPreset.halfPpr` — new enum value (the default), via ScoringPreset
- `Settings.scoringPreset` — new attribute, default `halfPpr`, via Settings
- `Settings` — gains PR-010 (latent fix) and PR-066
- `Alert` — gains PR-028 and PR-046 (latent fixes)
- `tvApp.profileUI` — gains PR-066, drops erroneous PR-044 (latent fix)
- `stores.profileStore` — gains PR-066

PR-047 traces to: `tvApp.panel`, `PanelMode`, `PanelMode.modeB`,
`PanelMode.fullScreen`. PR-048 traces to: `tvApp.notifier`,
`tvApp.launcher`, `TvProviderLaunch`, `TvFireOSNotify`,
`PanelMode.fullScreen`. PR-065 traces to: `backend.panelSvc`,
`backend.lineup`, `PanelState`, `Lineup`, `ScoringPreset`. PR-066
traces to: `tvApp.profileUI`, `stores.profileStore`, `Settings`,
`ScoringPreset`. PR-049..051 trace nowhere (withdrawn; UIDs retained).

## 6. Remaining risks

- One trivial probe document (`t.sysml`, `package P {}`) stays in
  `afc-product-models-p2` beside the four final docs (named in §1; no
  document-delete mutation exists). Harmless for the verdict; revisit
  only if a whole-project gate is ever run.
- Parse conformance is SysON's bundled textual engine, not an
  independent OMG-conformance proof; no OMG clause numbers are claimed.
- Approved spec `04.7-model-correspondence.md` still says "retained
  pending Phase 2 design" for the removed/renamed elements — a later
  spec-and-docs slice owns that alignment; the models are now ahead of
  the spec text by design.
- Shared local host; other agents may be active on it. Verified only
  this packet's write set and the one new project.

## developer_feedback

- OBS-SMP2-01 — tool: SysON workbench GraphQL `uploadDocument`
  (host build serving `/assets/index-DLVwWwxj.js`); task: textual
  `.sysml` import; expected: GraphQL-multipart-spec map
  (`{"0":["variables.input.file"]}` or equivalent) substitutes the file;
  actual: `variables.input.file` map → empty HTTP 400, spec array form →
  SPA-index fallback, separate-variables + `variables.file` → file stays
  null; the only working shape is the frontend-exact one (single
  `$input: UploadDocumentInput!` variable, map string form
  `{"0":"variables.file"}`, file field null in operations) — confirmed
  by reading the shipped bundle, which hardcodes exactly this;
  workaround: replicate the bundle call byte-for-shape; would-use-again: yes.
- OBS-SMP2-02 — tool: SysON GraphQL `queryBasedString` (AQL) on
  semantic objects; task: read back the `scoringPreset` default value;
  expected: `aql:self.name` returns the element name; actual: null even
  for `self.name`, so AQL read-back was unusable in this context;
  workaround: proved default-reference resolution via the server log
  (Data `39 references to resolve`, +2 over ST-3d, zero resolution
  warnings) plus `search` read-back of the involved elements;
  would-use-again: yes for `search` read-back; no for AQL read-back
  until the null behavior is understood.
- No new observations for: `read_skill` (systems-modeler,
  sysml-modeling, use-requirements-system read-only), file edits,
  `python3` probes (`smp2_check.py`, `smp2_xcheck.py` under the system
  temp dir, not committed), `sha256sum`, `grep`, `xml.etree` SVG
  parses, `alphazede-requirements-system status`/`binding` (read-only
  host discovery). No device, SDK, API integration, or simulator use.
