---
type: planning-handoff
title: Correction 2 exact source reconciliation for the planning lead
okf_status: draft
tags: [planning, afc, integration, delta]
---

# Root-only source corrections — proposed, not applied by IE

Authority is DEC-AFC-SD-039 and this continuation packet. These are routine
assembly/packet corrections inside the approved outcome, not new owner intent.
No review/repair budget resets. The source paths below are outside the IE write
set. Return to the parent Planning and Design lead; ask no new owner question.

BUG_ROUTE: not-a-bug — bounded planning author reconciliation and an artifact-check count assumption; no reproduced product defect or nested triage.

## IE-D2-G01 — literal graph dependency conditions

Target: `specialists/slice-graph.md`, Dependencies / Condition.
For each of the 13 own-pair arrows listed below, replace `merged` with this
exact condition:

> Verified CMD-RED behavioral-assertion receipt in the shared pair worktree,
> with baseline/diff, bootstrap and test-file hashes frozen; tests remain
> uncommitted until green. No separate red-only PR or red merge dependency.

Own-pair arrows: G01T→G01, A01T→A01, B01T→B01, B02T→B02, B03T→B03,
A02T→A02, B04T→B04, B05T→B05, B06T→B06, B07T→B07, A03T→A03,
A04T→A04, A05T→A05 (all use the P2- prefix).

For `P2-B04T --> P2-B05T`, replace `merged` with:

> Verified B04T red receipt and frozen shared-fixture inventory handed off;
> no red-only merge. B04 product landing remains required before B05 product
> landing.

For `P2-A03T --> P2-A04T`, replace `merged` with:

> Verified A03T red receipt and required frozen interface/test inventory
> handed off; no red-only merge. Each green slice retains its own landed
> product prerequisites.

These 15 literal conditions already have the intended override in the graph's
Codex planning-lead reconciliation paragraph; this correction makes machine
consumers agree with that paragraph.

## IE-D2-G02 — preparation edge, new instrumented paths and shared leases

Target: graph Dependencies. Add:

| Arrow | Condition |
|---|---|
| `P2-X01 --> P2-A01T` | Qualified host JDK17/SDK/build-tools preparation receipt with pins and scans; no extra stick slot; missing tool/import/build/collection is preparation gap, not valid red |

Target: graph slice A01T Leases. Replace `—` with:

> tv-app-manifest, tv-app-gradle (bootstrap paths only; Test Implementer
> then Product Implementer take turns in the same pair worktree)

Target: graph slice A02T Leases. Replace `—` with:

> fire-tv-stick (instrumented red/qualification runs only; whole-run
> cross-process lock)

The existing B01T backend-template lease stays. Its deployed conftest ownership
and distinct deployed subdirectories, plus A02T profile/detect androidTest
directories, are already added to the source graph; preserve them exactly.

Target: technical-plan Leases table. Add
`backend/tests/deployed/conftest.py` to backend-template Resource, and change
its Holders to:

> P2-B01T creates test/bootstrap/shared conftest under its bounded write set;
> P2-B01 creates the product shared artifacts; later authorized edits one at
> a time, declared in the PR body; module Test Implementers own distinct
> deployed directories and do not edit shared conftest without this lease.

For tv-app-manifest Holders use:

> P2-A01T creates empty bootstrap manifest; P2-A01 completes every component
> and permission after verified red; then one of P2-A02..A05 at a time.

For tv-app-gradle Holders use:

> P2-A01T creates empty build/test harness; P2-A01 completes runtime/build
> and release-signing configuration after verified red; P2-A02..A05 own
> entries one at a time; P2-R1..R5 version bump.

## IE-D2-G03 — D02 complete verdict dependency projection

Target: graph Dependencies. Retain X02/X03-final/X04→D02 and add:

| Arrow | Condition |
|---|---|
| `P2-X01 --> P2-D02` | Final required verdict landed; include through specification freeze |
| `P2-X05 --> P2-D02` | PR 2 final live-timing verdict landed; historical PR 1 is not final live proof |
| `P2-X06 --> P2-D02` | Yahoo/manual final disposition verdict landed |
| `P2-X07 --> P2-D02` | Final detection verdict landed |
| `P2-X11 --> P2-D02` | Selected X11 terminal disposition and verdict when run; if unselected, recorded OD-AFC-03/no-offer disposition; never infer enabled voice evidence |

Target: D02 Depends on, replace with:

> P2-X01..P2-X07 final verdicts landed (X03 PR 2 and X05 PR 2 included);
> selected P2-X11 terminal disposition and verdict when run; recorded
> no-offer disposition when unselected; PR #10 and the already-landed S42
> tools/spec content/pin. Include every landed verdict through freeze;
> later landed verdicts require a bounded D02 delta before M4 exit.

Both integration step identities stay. IE-P2-34 depends on IE-P2-35;
their assembly positions swap (IE-P2-35 order 34, IE-P2-34 order 35), so the
ordered list and dependency graph agree. No new step or slice is needed.

## IE-D2-G04 — remove passed-window promise in X05 row

Target: graph X05 Goal. Replace only this old substring:

> the 2026-10-11 games and the 2026-10-12 MNF game once final; that game live
> if this package is approved before kickoff

with:

> completed 2026-10-11 and 2026-10-12 games with historical/replay provenance;
> October 12 is no longer a remaining live opportunity; first planned live
> capture is TNF 2026-10-15

Keep PR 1 PARTIAL/live-timing-pending and PR 2 final live capture. Preserve all
five milestone dates and the existing technical-plan remaining-window list.

## IE-D2-G05 — final Gradle path and explanatory diagrams

Target: design CONTRACT-AFC-P2-GATE-AREAS. Replace:

`./gradlew -p tv-app testDebugUnitTest lintDebug assembleDebug`

with:

`./tv-app/gradlew -p tv-app testDebugUnitTest lintDebug assembleDebug`

Target: technical-plan Mermaid. Replace `APP --> A01T[P2-A01T] --> A01[P2-A01 tv scaffold]`
with `X01 --> A01T[P2-A01T host preparation ready] --> A01[P2-A01 tv scaffold]`.
Retain its X04→D02 edge and add X01, X02, X03, X05, X06, X07 and X11→D02
edges, labeling X03/X05 as final verdict and X11 as selected terminal disposition.
The full graph/IE entry predicates control these explanatory diagrams.

## IE-D2-G06 — wave 3 readiness order

Target: technical-plan Wave 3, replace only its initial red-dispatch sentence:

> Dispatch ready red slices under cap 5: P2-B04T first; P2-B05T after its
> verified red/shared-fixture handoff; P2-B06T, P2-A03T and P2-A05T when
> their own prerequisites hold. Greens follow their verified red receipts;
> P2-B07T/B07 and P2-A04T/A04 proceed as dependencies/leases permit.

Keep all existing product landing dependencies, L03, X09 and R3 obligations.

## IE-D2-G07 — Plan Integrator source/proof lineage

Target: Plan Integrator packet and integrated package provenance, not SEIT edits.
Use this exact instruction:

> Consume correction-2 specialists/integration-plan.md as assembly authority,
> including IE-P2-34 waiting for IE-P2-35 and wave_gate_costs. Copy existing
> SEIT command definitions, proof-row allocations, methods, negative criteria,
> resource declarations and frozen capabilities without reauthoring or rerunning
> TE. SEIT source_baseline and integration_vv_sequence retain TE's prior author
> bytes/projection; do not represent them as current assembly order or silently
> claim their old input hashes equal changed files. Bind current package inputs
> by their actual hashes, retain evidence/P2-6/codex-lead/input-delta.json and
> evidence/ie-p2-codex/input-provenance.json as explicit transition lineage, and
> record the current assembly projection with the unchanged TE proof authority.
> If the consuming validator requires refreshed TE-bound input hashes or
> projection, report SEIT_INPUT_PROJECTION_STALE to the planning lead for a
> bounded owning-role disposition; do not bypass the precondition. IE has no
> authority to edit SEIT or rerun TE in this packet. This remains correction 2,
> not a budget reset or independent planning review.

The unchanged SEIT SHA-256 is
`747376ca2c0aeace71bfe33daa58793fa8d2b112a0176e7dd8b57170c3b67ae0`.
Its technical-plan/design input hashes are the documented lead-delta `before`
values; the current bytes equal `after`. Its IE-P2-34 `after` projection and
IE-P2-34/35 order projection are stale. This is a visible synthesis gap,
not missing proof coverage or a runtime
PASS. Coverage/mutation TOOL_UNALLOCATED and Reverify APK semantic gap remain
separate execution/acceptance gaps.
