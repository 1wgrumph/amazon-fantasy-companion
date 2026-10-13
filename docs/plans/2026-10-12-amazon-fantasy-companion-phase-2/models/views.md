---
type: sysml-view-metadata
title: AFC SysML v2 view metadata (ST-3b)
okf_status: draft
tags: [modeling, planning, afc, spec-track]
---

# AFC SysML v2 view metadata (ST-3b)

- Modeling mode: `sysml-v2` (plan-mandated ST-3; sm-contextual-pass.md section 5).
- Language authority: OMG SysML v2 formal/2026-03-02, File ID formal/26-03-02
  (bibliographic identity per sysml-modeling `sysml-v2-validation.md` receipt
  SRC-EMV-SYSMLV2). No OMG clause numbers are cited anywhere in this model.
- Native sources (normative for ST-4 figures and text):
  - `models/AFC-Structure.sysml` (package AFCStructure)
  - `models/AFC-Interfaces.sysml` (package AFCInterfaces)
  - `models/AFC-States.sysml` (package AFCStates)
  - `models/AFC-Data.sysml` (package AFCData)
- Model revision digest (sha256 over the four native sources concatenated in
  sorted filename order — `AFC-Data`, `AFC-Interfaces`, `AFC-States`,
  `AFC-Structure`):
  - `8f5798823b3a9463f8963c7c6fa2cf94d018189edd0ca6160123362d48a075ff`
  (P2 delta revision; ST-3d revision was
  `14fb815b78c2c6817d556c36d351b22dd3996db5f5a7e34a87251ce69bfdcfe5`)
- Per-file sha256:
  - AFC-Data.sysml `4fcb3174666f80f13e405230c5e0df2498d2c6d62ea584160bd249f966f14031`
  - AFC-Interfaces.sysml `504cfcb82dd83beca534d463dde1c07f2714d56ce26390c4519c5f55ac7a4851`
  - AFC-States.sysml `3055e76043cf6c1b7763aa7804b61dfd9ec4a8095fb954ec4b77ee1dd9cd7904`
  - AFC-Structure.sysml `54b87c488cadd65c825b6a66b3308cc7920bd7d32eb05cfa7ac789902dc0221c`
- Native-or-derived status: the `.sysml` files above are the native sources.
  The four `.svg` views are derived projections: each cites this digest in its
  `<desc>` element and replaces nothing. This file and `allocation.md` are
  traceability companions, not model sources.
- No local normative-coverage claim is made; no AZEdge `.sysml` fixture is
  cited as language law; no Mermaid is presented as SysML.

## Typed gaps

- `CHECKER_UNAVAILABLE`: no SysML v2 parser is installed in this environment
  (`syside`: not found; no sysml/kerml tool on PATH; no sysml Python package).
  The `.sysml` files follow the OMG textual shape in the skill examples but
  have not been parser-verified. ST-4 consumers must treat trigger bindings and
  multiplicity forms as review-level until a parser run exists.
  The Requirements System `check` command exists but validates a package
  against a per-model profile, SEIT matrix, design and receipt that this
  spec-track journey does not define; running it without those inputs would
  be a fabricated gate, so it was not run.
  ST-3d closure (DEC-AFC-SD-032): parser proof now exists — all four files
  import into SysON project `afc-product-models` with zero errors and zero
  warnings; trigger bindings verified. See
  `specialists/sm-syson-receipt.md`.
  P2 delta closure (DEC-AFC-SD-035): the four amended files re-import into
  the new SysON project `afc-product-models-p2` with zero errors and zero
  warnings; the `ScoringPreset` default binding resolves (Data reference
  count rises 37 → 39 with no resolution warnings). See
  `specialists/sm-p2-delta-receipt.md`.
- `S8-LEDGER-MISSING` (observation, non-blocking): the standalone
  `engineering-methods/references/standards-receipts.md` ledger is absent
  from the skills tree (the `engineering-methods` skill directory does not
  exist). Same observation the Requirements Engineer recorded at ST-2 without
  gating impact. The OMG receipt content relied on here is embedded in the
  readable `sysml-v2-validation.md`; no cited content is affected.

## Abstraction decisions (apply to all views)

1. Self-contained packages: each `.sysml` file declares one package with no
   `import` bindings, so every file stands alone for review and grep-level
   checking. Cross-package linkage is by element name in `doc` comments plus
   `allocation.md`. A future single-tool load may add `import` bindings; that
   is ST-4-or-later work, not a silent change.
   Exception (ST-3d): `AFC-Data.sysml` carries `import ScalarValues::*;` so
   the KerML primitive typings resolve in a conforming tool; cross-package
   linkage stays doc-name-only.
2. Allocation granularity: parts, port defs and port usages, interface defs,
   state defs, states, signals, item/enum defs. Owned detail (interface ends,
   attributes, enum values, transitions) inherits its parent def allocation
   and is listed per item in `allocation.md` Table 2 as `via <parent>`.
   Packages are namespaces and carry no allocation.
3. Attribute types use KerML primitives (String, Integer, Boolean, Real) as
   review-level placeholders; wire contracts stay with the ST-4 spec author.

## View V-ST3b-1 — structure

| Field | Content |
|---|---|
| Engineering question | Which parts and ports implement the product, and where does each live? |
| Concern | Structure: TV app, backend functions, stores, external systems |
| Source IDs | AFC-PR-001..066 (structure column via allocation.md Table 1); SD-003, SD-005, SD-007; C4, C6, C8, C9 |
| View type | Part/port structure (native `.sysml` + derived SVG projection) |
| Selection rationale | ST-3 row (b) mandates structure (parts, ports); the register allocates every UID to ST-3a elements this view formalizes |
| Canonical source | `models/AFC-Structure.sysml`, package AFCStructure |
| Abstraction and omissions | Planned paths in `doc` comments only (greenfield: `tv-app/`, `backend/` do not exist yet); omits operation signatures, deployment mapping, and cross-package `import` bindings per decision 1 |
| Interpretation | Boxes are parts; labeled ports bind to the interfaces in V-ST3b-2; `externals` members are endpoints, not repo code; no companion player — the panel falls back to full-screen (C5) |
| Supported decision | ST-3c allocation of every UID to structure elements; ST-4 spec figures |

Derived artifact: `models/view-structure.svg` (digest cited in `<desc>`).

## View V-ST3b-2 — interfaces

| Field | Content |
|---|---|
| Engineering question | What crosses each system boundary, in which direction, under which conditions? |
| Concern | Interfaces: TV app ↔ backend API, backend ↔ ESPN, backend ↔ Yahoo, TV app → provider launch (six outcomes), TV app → Fire OS notifications, conditional Alexa, device-code link, backend-internal chain |
| Source IDs | AFC-PR-001, 002, 004, 006, 007, 012, 013, 015, 022, 024, 025, 026, 029..033, 036, 038, 048, 052, 055, 057..060, 064; C2, C6, C8 |
| View type | Interface definition (native `.sysml` + derived SVG projection) |
| Selection rationale | ST-3 row (b) mandates the interface model; sm-contextual-pass.md section 3 enumerates the eight interfaces |
| Canonical source | `models/AFC-Interfaces.sysml`, package AFCInterfaces |
| Abstraction and omissions | Operations and payloads summarized in `doc` comments, not formalized as flows; six launch outcomes referenced as `AFCData::RoutingOutcome` by name (decision 1); omits retry/timeout values, which belong to ST-4 design |
| Interpretation | Each `interface def` names its two connected structure ports/systems in its `doc`; dashed TvAlexa edge marks the C8 conditional; IngestMatcherPolicy is backend-internal |
| Supported decision | ST-3c interface allocation; ST-4 API/contract sections cite these interfaces |

Derived artifact: `models/view-interfaces.svg` (digest cited in `<desc>`).

## View V-ST3b-3 — states

| Field | Content |
|---|---|
| Engineering question | What lifecycle does an alert, the panel mode, and the device link follow? |
| Concern | States: alert lifecycle, panel modeB/fullScreen, device link |
| Source IDs | AFC-PR-014, 016..021, 023..028, 038, 041, 047, 048; C5 |
| View type | State definition (native `.sysml` + derived SVG projection) |
| Selection rationale | ST-3 row (b) mandates the state model; the register's filter, dedup, correction, fallback and link obligations need explicit lifecycles |
| Canonical source | `models/AFC-States.sysml`, package AFCStates |
| Abstraction and omissions | Trigger signals are package-level `signal` usages, parser-verified at ST-3d (SysON import, zero errors); no timing values on transitions (spoiler delay, code expiry stay requirements text); panel visibility is data (`PanelState.visible`), not a mode |
| Interpretation | `entry; then` names the initial state; `gated` holds emission for the spoiler delay; `suppressed` is terminal for that event; PanelMode has no return transition because C5 names fallback only |
| Supported decision | ST-3c state allocation; ST-4 behavior sections |

Derived artifact: `models/view-states.svg` (digest cited in `<desc>`).

## View V-ST3b-4 — data

| Field | Content |
|---|---|
| Engineering question | What data items flow through the interfaces and states, and what fields ground them? |
| Concern | Data: GameEvent, Alert, Lineup, PanelState, Settings, ScoringPreset, plus RoutingOutcome and DeviceCode |
| Source IDs | AFC-PR-001, 002, 005..010, 012..014, 016..023, 025..029, 031..035, 037..040, 042, 044, 046, 061, 064..066 |
| View type | Item/enum definition (native `.sysml` + derived SVG projection) |
| Selection rationale | ST-3 row (b) mandates the data model; these eight items are exactly the payloads the interfaces and states reference |
| Canonical source | `models/AFC-Data.sysml`, package AFCData |
| Abstraction and omissions | Attribute types are KerML-primitive placeholders (decision 3); no multiplicities beyond review-level reading; `Settings` groups fifteen separately-controlled settings as one item with fifteen attributes, `scoringPreset` defaulting to `halfPpr` |
| Interpretation | `GameEvent` is the ingest fact; `Alert` is the gated, context-carrying emission; `Lineup` has exactly one active source; `PanelState` is the rendered view of Lineup + feed under Settings; `ScoringPreset` selects the manual-lineup preset (PR-065/066); `RoutingOutcome` enumerates PR-031 exactly |
| Supported decision | ST-3c data allocation; ST-4 contract/data sections |

Derived artifact: `models/view-data.svg` (digest cited in `<desc>`).
