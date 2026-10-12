# ST-3d Receipt — Systems Modeler SysON parse-check + repairs

- Verdict: PASS
- Role: Systems Modeler, planning session (`BEARING_ROLE=systems_modeler`)
- Lifecycle: AFC-ST-2026-10-12, step ST-3d (per DEC-AFC-SD-032)
- Packet: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/sm-syson-prompt.md`
- Skills loaded: `systems-modeler`, `sysml-modeling`
  (`use-requirements-system` consulted read-only for host discovery)
- Changed paths (write set only; no commits, no other paths, no absolute paths):
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/AFC-States.sysml`
    (repair: `signal def` → `signal`)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/AFC-Data.sysml`
    (repair: added `import ScalarValues::*;`)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/views.md`
    (ST-3d digests, `CHECKER_UNAVAILABLE` closure, decision-1 stdlib exception)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/allocation.md`
    (ST-3d digest citation only; Table 1/2 content unchanged)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/view-*.svg`
    (4 files, `<desc>` digest cite only)
  - `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/sm-syson-receipt.md`
    (this file)
- Untouched by design: `AFC-Structure.sysml`, `AFC-Interfaces.sysml`
  (clean on first import); every other SysON project; the Maestro checkout;
  the Requirements System checkout/registry (no `model load`, no `checkout create`).

## SysON project

- Project name: `afc-product-models` (the one authorized new project)
- Project id: `2a033855-6bae-4fe1-975c-00bbb9419100`
- Editing context id: `9565c8a1-1054-41f1-8da4-f5109df2ded1`
  (resolved via `viewer.project.currentEditingContext`; it differs from the
  project id and uploads against the project id fail generically)
- Template: `sysmlv2-template`; endpoint: SysON GraphQL on loopback
  (discovered via host `binding`, `AZ_REQUIREMENTS_SYSON_HEALTH`), mutations
  `createProject` + `uploadDocument` (multipart to `/api/graphql/upload`,
  replicating the shipped frontend call)
- Import is a genuine parse: the server log shows each upload parsed by
  SysON's bundled textual engine (`Call syside application`, `File Parsed`,
  `N references to resolve`, `Document <uuid> uploaded`)

## Import diagnostics before → after (per file, in upload order)

1. `AFC-Data.sysml` round 1: `UploadDocumentSuccessPayload` with 36 warnings,
   one per attribute typing: `Unable to resolve name 'String'/'Boolean' for
   reference 'type'` (e.g. `[FeatureTyping] AFCData::GameEvent::score`).
   Classification: real model gap — KerML primitives need an explicit
   `ScalarValues` import. Repair: added `import ScalarValues::*;` to the
   package. Round 2: `UploadDocumentSuccessPayload`, null report (zero
   errors, zero warnings).
2. `AFC-Structure.sysml`: `UploadDocumentSuccessPayload`, null report on the
   first upload. No repair. (8 references resolved server-side.)
3. `AFC-Interfaces.sysml`: `UploadDocumentSuccessPayload`, null report on the
   first upload. No repair.
4. `AFC-States.sysml` round 1: success payload carrying an error report —
   `The SysML file contains syntax errors and cannot be imported. Only the
   part of the file located before the first error could be parsed.` plus
   `line 14: Expecting token of type '}' but found 'def'` (and EOF variant).
   Classification: real model syntax error — the grammar accepts no
   `signal def` form. Repair: the ten trigger declarations changed from
   `signal def <name>;` to `signal <name>;` (names, triggers and transitions
   unchanged). Round 2: `UploadDocumentSuccessPayload`, null report,
   so the `transition … first … accept … then …` forms parse as written.
   (39 references resolved server-side.)

Final state: all four files import with zero errors and zero warnings.
No diagnostic remains to classify as a SysON limitation.

## Documents in the project

Final (exactly the four current sources):
`AFC-Structure` 8e27706b, `AFC-Interfaces` cf4c0348, `AFC-States` (repaired)
75a69da0, `AFC-Data` (repaired) 975a72e6 (ids abbreviated; full UUIDs in §Evidence).
Repair-loop residue in the same project: `AFC-Data` round-1 doc 0f1c9821 and
`AFC-States` round-1 partial doc 723f16e5. Re-upload creates a new document
rather than replacing, and the schema exposes no document-delete mutation
(deletion needs live explorer-tree item ids), so the two stale docs were left
in place and are named here instead of silently kept.

## Evidence ( diagnostics transcripts, server log excerpts)

- `AFC-Data` round-1 report: 36× `[Warning] Unable to resolve name …`
  (11 Alert/GameEvent/Lineup `String`, 1 `Boolean`, 4 PanelState, 14 Settings,
  2 DeviceCode typings); round-2 report: null.
- `AFC-States` round-1 report: `[ERROR] The SysML file contains syntax errors
  and cannot be imported. …` + three `line 14` def-token errors; round-2
  report: null. `AFC-Structure` / `AFC-Interfaces` reports: null, first try.
- Server log (SysON application log, read-only): `File Parsed` +
  `Document 0f1c9821-… uploaded` (36 refs), `Document 8e27706b-… uploaded`
  (8 refs), `Document cf4c0348-… uploaded` (0 refs), `Document 723f16e5-…
  uploaded` (no parse: syntax error), `Document 75a69da0-… uploaded`
  (39 refs), `Document 975a72e6-… uploaded` (37 refs).

## Allocation check (65/65 unchanged)

- Re-ran the ST-3b/c probe from the system temp dir with exactly two
  adaptations to the repaired truth (revision digest constant, `signal`
  usage form): RESULT OK — 17/17 checks, `defined-in-sysml=161 table2=161`,
  UID coverage 65/65, back-consistency, via-targets, SVG parse + digest
  cites, combined-digest match, no-absolute-paths.
- Re-ran the ST-3b/c register cross-check unchanged: REGISTER-CROSSCHECK OK
  (allocation UID set == register UID set, 65 == 65, both directions).
- Allocation content is byte-identical apart from the digest citation line:
  the repairs rename nothing (`signal` keeps all ten trigger names; the
  `import` adds no model element).

## Model revision digest (ST-3d)

- Combined (sha256 over the four native `.sysml` sources concatenated in
  sorted filename order):
  `14fb815b78c2c6817d556c36d351b22dd3996db5f5a7e34a87251ce69bfdcfe5`
- Per-file sha256 over `models/`:
  - AFC-Data.sysml `1d342eef5bb5656e0d33b2c3da742000cd1cb889324fc6a77e119bedf91bc3b0`
  - AFC-Interfaces.sysml `504cfcb82dd83beca534d463dde1c07f2714d56ce26390c4519c5f55ac7a4851`
  - AFC-States.sysml `7d25c0f1975c11faad3956e19c65e04c74aa971cbb271a01874cc9c6e6e50128`
  - AFC-Structure.sysml `13d20b60f3d521e5748d91f555f43f319b76d87c0b8b0dad478091a29a8346b3`
  - allocation.md `1fee120c07f46618863e6b110cb3787cd8a592a10c413b6fa1ad8558f625a3c7`
  - view-data.svg `9362384266b43edb3e02c15d8dd811a30c87c8278335332b7f4a79a7a7679def`
  - view-interfaces.svg `ec453eb3e2d5003adb0c50b3e09c53d5c3eaf16c0da77c2441018e41441f5733`
  - view-states.svg `9159b58d77db20168666ba995e52822bb112d1e06cc8604a809f6b0023178b56`
  - view-structure.svg `4f27478268f031fb7312166e635aab173336ad7f8c1d6cd547842376506de47a`
  - views.md `0d427a200d76a44fea2d5efa672bcf6e2c1f914860dc63c97e5e365e98397904`

## Remaining risks

- Two stale repair-loop documents stay in `afc-product-models` (named above);
  a future project-wide validation would see them alongside the four final
  docs. Harmless for the ST-3d verdict; revisit only if a whole-project gate
  is ever run.
- Other agents were active on the shared SysON host during this run
  (unrelated projects created and deleted by others); this receipt verifies
  only the `afc-product-models` write set.
- Parse conformance is SysON's bundled textual engine, not an independent
  OMG-conformance proof; no OMG clause numbers are claimed.

## developer_feedback

Tool used: local SysON workbench (GraphQL `createProject`, multipart
`uploadDocument`), no API key, no install. What worked: textual `.sysml`
import with per-file diagnostic reports; reports distinguish hard syntax
errors from resolution warnings precisely enough to repair against.
Frictions worth knowing: (1) `uploadDocument` needs the editing-context id
from `viewer.project.currentEditingContext`, not the project id — the wrong
id yields only a generic unexpected-error payload with no server log line;
(2) the multipart `map` must use the string form `{"0":"variables.file"}`
(the spec array form crashes the upload controller); project creation needs
an explicit `templateId` (`sysmlv2-template`) plus `libraryIds: []`.
No device, SDK, or simulator use. Nothing else to classify under AC-AFC-DX-04.
