---
type: planning-input
title: Phase 2 milestone chronology review and 13-milestone proposal (DEC-AFC-SD-040)
okf_status: draft
tags: [planning, afc, phase-2, milestones, chronology]
---

# Phase 2 milestone chronology review

Reviewer: Claude Code / Claude Opus 5.5 / high, in a fresh session, as the
owner requested in DEC-AFC-SD-040. Candidate `51bc730a…` (plan digest
`67ac7a90…`, payload `f485d8f6…`). This is a proposal only; the parent
applies and validates it. The machine-readable form is
`evidence/chronology-opus-review/proposal.json`. Checks are in
`evidence/chronology-opus-review/checks.md` (20/20 PASS).

## Recommendation

Replace the five GitHub milestones (7/11/10/4/7 issues) with **13
chronological milestones, M01..M13**, holding 3,2,3,4,3,3,3,3,2,2,4,4,3
issues (mean 3.0, every one within 2–6). Keep the **five waves and five
releases exactly as they are**, and call them *release checkpoints* W1..W5
(Wave 1..5 exit = P2-R1..R5). This separates the GitHub grouping from the
integration cadence, as the packet prefers:

- No slice, dependency, wave, gate cost, cut-off, live window, proof,
  command, UID, route or OCR/Reverify setting changes.
- Each issue keeps its stable ID and body scope. Only the `[Mnn]` title
  prefix, the milestone it belongs to, and the text that names milestones
  change.
- Every due time is an existing cut-off or milestone time. No date was
  invented or moved.
- Each release P2-R1..R4 is the last issue of a milestone (M03, M06, M10,
  M11), so the release cadence stays visible.

## The 13 milestones in order

Times are UTC. "∥" marks work that can start in parallel at the
milestone's start. "→" marks a sequence.

| # | Outcome | Issues in order | Waits for | Due (basis) | Owner prerequisites |
|---|---|---|---|---|---|
| M01 | Day one: tracking, verification guidance and product gate | ∥ L01, ∥ D01, ∥ G01 | Integrated approval and planning PR merged (IE-P2-1) | 10-14 20:00 (CO-M1) | Integrated approval |
| M02 | Fire TV stick qualified and backend skeleton with device linking | ∥ X01, ∥ B01 (B01 lands after G01) | M01: G01 landing, for B01 landing only. X01 starts with M01. | 10-14 20:00 (CO-M1); X01 starts by 10-14 03:15 (CO-STICK-START) | OA-1, OA-4 Prime |
| M03 | Panel spike, TV app scaffold, **release v0.1.0** | X04 → A01 (review after the stick is free) → R1 | M02 (X01 merged; host tools; B01 landed), M01 (G01). Early checkpoint CP-X05-HIST for R1 | 10-14 23:00 (R1) | OA-4 Prime; OA-8 to publish |
| M04 | Stick spikes and Thursday Oct 15 live checks | X02 → X03 PR 1 desk → X07 → TNF: X03 PR 2 ∥ X05 PR 2 (X05 started at approval) | M03 (stick released by X04 and the A01 review), M02 (B01) | 10-17 01:00 (CO-M2); X03 desk 10-15 20:00 | OA-4 ESPN, DirecTV Stream, YouTube TV |
| M05 | Feed ingest, lineup sources and first AWS deploy | ∥ B03, ∥ L02, then B02 after CP-X05-HIST | M02 (B01). Runs alongside M03/M04 (backend lane) | 10-17 01:00 (CO-M2); Yahoo path: deploy before T_yahoo 10-16 19:00 | OA-3, OA-10 |
| M06 | Profile settings, lineup-source verdict, **release v0.2.0** | A02 ∥ X06 → R2 | M03 (A01, R1), M04 (X07), M05 (L02, B03) | 10-17 01:00 (CO-M2) | OA-2 (optional); OA-8 |
| M07 | Event matching, alert policy and panel service | B04 → (B05 ∥ B07) | Wave 3 entry (M04, M06 verdicts; T_yahoo applied); M05 (B02, B03) | 10-18 09:00 (CO-M3-CODE) | — |
| M08 | Provider resolver, TV alerts and Watch | ∥ B06, ∥ A03T → A03 (after B05), A04 (after A03T red, B06) | Wave 3 entry; M04 (X02, X03 registry); M06 (A02); M07 (B05) | 10-18 09:00 (CO-M3-CODE) | OA-4 sessions |
| M09 | TV lineup panel and integrated backend deploy | A05 (after B07) ∥ L03 (after B05, B06, B07, X06) | M03 (X04), M06 (A02, X06), M07, M08 | 10-18 11:00 (CO-M3-CODE rule) | — |
| M10 | Sunday Oct 18 live end-to-end, **release v0.3.0** | rehearsal IE-P2-29 → X09 → R3 | M08, M09 (and R2) | 10-19 12:00 (CO-M3); rehearsal 10-18 15:00 | OA-4 live, OA-10; OA-8 |
| M11 | Monday Oct 19 hardening, conditional Alexa, spec revision, **release v0.4.0** | Sunday fixes → X10 (MNF) → X11 *(conditional)* → D02 → R4 | Wave 4 entry = M10 (R3); final verdicts from M02–M06 | 10-21 23:00 (CO-M4); fixes 10-19 20:00; Alexa drop 10-21 12:00 | OD-AFC-03; OA-10; OA-8 |
| M12 | Submission documents and developer feedback | ∥ D03, ∥ D04, ∥ D05, then SCR1 | Wave 5 entry = M11 (R4) | 10-22 16:00 (CO-M5-DOCS) | OA-6 before D04 final |
| M13 | Release candidate **v1.0.0**, final APK, demo capture and handover | R5 → L05 → X12 (TNF 10-22); IE-P2-39/40/44 non-issue steps | M12, M11 | 10-23 12:00 (CO-M5); R5 10-22 17:00, L05 19:00, demo 10-23 06:00 | OA-5, OA-9, OA-11 opt., OA-8, then OA-7 |

Totals: 39 issues, each in exactly one milestone. The 52 slices and the 13
test-first pairs stay with their issues. P2-X11 stays a visible conditional
issue in M11.

### Parallel lanes, read across

- **Stick lane (one device, strictly serial):** X01 (M02) → X04 → A01
  review (M03) → X02 → X03 desk → X07 → TNF X03 PR 2 (M04) → A02
  review (M06) → A03/A04 runs (M08) → A05 runs (M09) → rehearsal → X09
  (M10) → X10 → X11 (M11) → X12 on the final APK (M13).
- **Backend lane:** G01 (M01) → B01 (M02) → B03/L02/B02 (M05) → X06
  (M06) → B04 → B05/B07 (M07) → B06 (M08) → L03 (M09).
- **TV app lane:** A01 (M03) → A02 (M06) → A03/A04 (M08) → A05 (M09).
- **Docs and release lane:** L01, D01 (M01) → R1 (M03) → R2 (M06) → R3
  (M10) → D02, R4 (M11) → D03..D05, SCR1 (M12) → R5, L05, X12 (M13).

The milestones run in parallel in two places: M03 ∥ M05 ∥ early M04, and
M07 ∥ M08 ∥ the start of M09. The cap of five implementation agents still
governs, and the stick chain counts as one agent. GitHub stores only a due
*date*, so M01–M03 all show Oct 14, M04–M06 Oct 17 and M07–M09 Oct 18. The
zero-padded `Mnn` title prefix keeps them in chronological order, and each
description carries the exact UTC time.

### Early checkpoints (tracked exceptions)

- **CP-X05-HIST:** X05 PR 1 historical fixtures (IE-P2-6). They land after
  B01 (M02) and feed R1 (M03, the only forward reference) and B02 (M05).
  The X05 issue closes only at the TNF live-timing verdict in M04,
  unchanged from today.
- **CP-X03-REG:** X03 PR 1 desk evidence plus `registry.v1`. It feeds X07
  inside M04 and B06/A04 in M08. The issue closes at the TNF PR 2 verdict.

### Release checkpoints (unchanged waves)

| Checkpoint | Wave | Release | Closes in | Due |
|---|---|---|---|---|
| W1 (was M1) | Wave 1 | P2-R1 v0.1.0 | M03 | 2026-10-14T23:00:00Z |
| W2 (was M2) | Wave 2 | P2-R2 v0.2.0 | M06 | 2026-10-17T01:00:00Z |
| W3 (was M3) | Wave 3 | P2-R3 v0.3.0 | M10 | 2026-10-19T12:00:00Z |
| W4 (was M4) | Wave 4 | P2-R4 v0.4.0 | M11 | 2026-10-21T23:00:00Z |
| W5 (was M5) | Wave 5 | P2-R5 v1.0.0 (candidate.final) | M13 | 2026-10-23T12:00:00Z |

Wave ⊃ milestone: Wave 1 = M01–M03 (plus the start of X05); Wave 2 = X04
in M03, then M04–M06; Wave 3 = M07–M10; Wave 4 = M11; Wave 5 = M12–M13.

## Ordering traps in the current package

1. **R1's date cannot hold if X04 uses its full 24-hour timebox.** P2-A01
   (Wave 1) needs its on-device review after P2-X04 (Wave 2) releases the
   stick. X04 holds the stick until its verdict or first_install_at + 24 h.
   R1 needs A01 merged and is due 2026-10-14T23:00Z. If X01 first installs
   on 10-14, a full X04 timebox ends after R1's due time. Today this
   dependency is hidden: M1 lists A01 but not X04 (the issue dependency
   says "on-device review step only"). M03 now holds X04 → A01 → R1
   together, so the chain is visible. **The date is not moved. This is a
   schedule risk for the owner.**
2. **Wave 2's entry can be read as a cycle.** "M1 exit for device and
   backend slices", read as R1 merged, gives R1 ← A01 ← X04 ← "M1 exit".
   The slice arrows show the real rule: X01 merged for X04, B01 merged for
   the backend Wave 2 slices, A01 merged for A02. Reword the entry to say
   so. This is a clarification, not a change in meaning.
3. **The single X05 issue spans two milestones** (it starts at approval and
   closes after TNF). This is kept as the one tracked forward checkpoint
   (CP-X05-HIST).
4. **The release dependencies are generated from milestone membership**
   (`gen_impl.py:379-392`, from the technical plan's milestone `Slices`
   column). If that table becomes the 13-row GitHub table, R1..R4 lose
   most of their predecessors without any error. The five-row
   release-checkpoint table must stay the source for that derivation.
5. **D02 waits on X11, but the step IDs suggest otherwise.** IE-P2-34 (D02)
   runs after IE-P2-35 (X11). M11 lists X11 before D02 so the order is
   explicit.
6. **SCR1 has two predecessors.** The arrow says X10; the text says "M4
   exit". The stricter one (R4, the Wave 5 entry) is kept, which puts SCR1
   in M12.
7. **Wave 3 and Wave 5 entries are stricter than the slice arrows.** B06T
   needs only the X03 registry and B01, but Wave 3 entry waits for all
   Wave 2 verdicts and T_yahoo. D03..D05 need only X10, but Wave 5 entry is
   R4. Both are preserved as written; whether ready slices may start early
   is a parent/owner clarification, not changed here.
8. **"M1" next to "M01" is ambiguous.** The five technical groupings
   should be renamed to wave exits W1..W5 in the text.

## Prior decisions about five milestones

None of the 49 decisions before DEC-AFC-SD-040 fixes the number of
milestones at five. DEC-AFC-SD-010 (milestones live in this repository and
go public), SD-012 (D3 GitHub milestones are a deliverable), SD-023
(milestones are created only after the Phase 2 plan is approved),
DEC-AFC-APPROVAL-ST5 (authorizes planning milestones) and SD-039 (prepare
issue/milestone organization) all concern milestones but not their count.
SD-038 (releases through release-process) does not fix a count either.

The "five" lives only in the unapproved Phase 2 package: the technical plan
D3 table and AC-AFC-P2-MS-01, AC-AFC-P2-REL-02 ("at each milestone exit"),
RISK-AFC-P2-13, the open item OD-AFC-P2-03 (versions at M1..M5), the
DES-AFC-P2-REVREC wording, and the projections derived from them.
SD-040 supersedes their count and grouping, not their scope. The previous
review round and repair round stay spent; this review is the one
additional review SD-040 authorized.

## Smallest coherent source changes (for the parent to apply)

1. **Technical plan.**
   - Rename §Milestones to "Release checkpoints (wave exits W1..W5)" and
     keep the five rows as they are, including the `Slices` column used by
     the generator.
   - Add a "GitHub milestones (chronological, D3)" table with the 13 rows
     above (ID, title, due and basis, issues in order, waits for).
   - Reword these requirement rows:
     - AC-AFC-P2-MS-01: "M1..M5" becomes "M01..M13".
     - AC-AFC-P2-REL-02: "at each milestone exit" becomes "at each wave
       exit W1..W5".
     - RISK-AFC-P2-13: "milestone exit" becomes "wave exit".
     - These three are Lifecycle-local acceptance rows, so the Requirements
       Engineer and Test Engineer must acknowledge the rewording.
   - Update the GitHub-organization text: "five" becomes "thirteen", and
     X05 now belongs to M04.
   - Reword the Wave 2 entry (trap 2).
   - In the owner-action "Needed by" column, Exit criteria 2, and the
     OD-AFC-P2-03 recommendation, change M*n* to W*n*.
   - Add an "Outcome" bullet: M01..M13.
2. **design.md.** Two wording edits: line 32 ("milestone release" becomes
   "wave release") and line 331 ("each milestone exit" becomes "each wave
   exit").
3. **slice-graph.md.**
   - Change the "M, wave" column to "GitHub milestone, wave".
   - In P2-L01's goal, "M1..M5" becomes "M01..M13".
   - R1..R4: "every other M*n* slice" becomes "every other Wave *n* slice".
     Make the same change in the note below the arrows.
   - X11 "M3 exit", SCR1 "M4 exit" and D02 "before M4 exit" become
     W3/W4/W4.
   - In the X05→R1 arrow condition, "M2" becomes "M04".
4. **seit.json** (text only; IDs and counts unchanged).
   - Rewrite CMD-MILESTONES-CREATE, CMD-MILESTONES-READBACK,
     PROC-TRACKING-SETUP and SEIT-AFC-P2-MS-01 for 13 milestones read back
     against the approved 13-row table. Drop the exact "M2
     2026-10-17T01:00:00Z" assertion and check each row's due time
     instead.
   - Set `tracking_workflow.milestones` to 13 and update its groups.
   - Rename the M*n* tokens that mean a wave to W*n*, for example "X11
     conditional after M3" in 14 visual-review proofs, "M4 closure" in
     SPIKE-01, "M3 rehearsal" in CMD-STUB-SCAN, "A01 M1" in
     PROC-VISUAL-REVIEW, and the `levels` and `wave_gate_costs` entries.
   - Keep cut-off IDs CO-M1..CO-M5 as stable identifiers and note that
     they name wave exits.
5. **integration-plan.md and implementation.json.**
   - Each slice's and step's `milestone` becomes its GitHub milestone (use
     the step map in `proposal.json`); `wave` stays.
   - Add `releases[].checkpoint` W*n*.
   - Set `work_issues.groups[].milestone` and the P2-L01 text to 13.
   - Regenerate through `gen_impl.py` with these changes:
     - Read the checkpoint table into `MS_OF` (trap 4).
     - Parse the new 13-row table.
     - Replace the fixed M1..M5, count-5 and X05/M2 asserts.
     - Group the close-out table by wave.
6. **Tracking payload.**
   - 13 milestone objects, with titles, `due_on` and descriptions from
     `proposal.json`. The descriptions carry the start, finish, issues in
     order, waits-for, owner prerequisites and the exact UTC time.
   - Retitle all 39 issues by prefix only.
   - In each body: the "within milestone **M*n***" line, plus one new
     "Sequence: step *k* of *n* in M*nn*; starts when …" line from
     `proposal.json`. Change X05's last acceptance bullet to "the early
     historical-fixture checkpoint (consumed by R1 in M03 and B02 in M05)
     may pass while this M04 issue stays open".
   - Dependencies are unchanged. New body hashes and a new payload hash
     follow. `payload-supersession.json` records f485d8f6… as superseded.
7. **authority.json** (via `write_authority.py`). "milestones M1..M5"
   becomes "M01..M13". This is the approval binding, so the owner approves
   it with the package.
8. **HTML manifest and views.**
   - Relabel `views/p2-program-waves.svg` from "milestones and waves / M*n*"
     to "waves and release checkpoints / W*n*".
   - Add one plain table, "GitHub milestones in order", next to the task
     graph: the 13 rows above plus the lane line. No new SVG and no new
     framework.
   - Recheck the DOM for overflow at phone width.
9. **Historical receipts.** `verify.py`, `check_delta.py`, the TE/PI/IE
   receipts and the P2-review evidence stay as they are. A new delta
   validator (the same 20 checks as `checks.md`, plus plan-package
   validators, renderer `--check`, the repository gate and a hash
   comparison showing unchanged proofs, commands and UIDs) supplies the new
   candidate's evidence.
10. **journey.json** (controlling copy). After the owner accepts, record
    the application of SD-040, the new candidate digest and the payload
    hash.

Future command and proof text affected: CMD-MILESTONES-CREATE,
CMD-MILESTONES-READBACK, PROC-TRACKING-SETUP, SEIT-AFC-P2-MS-01 (13
milestones); IE-P2-2 entry text; CO-M1..M5 descriptions (wave exits). No
command is added or removed.

## Warnings and schedule risks (no date changed)

- **W-1 (R1/M03 feasibility, trap 1).** R1's 10-14 23:00 due time holds
  only if X04 ends well before its 24-hour timebox, or X01's first install
  happens early on 10-14 or before. The owner decides whether to accept a
  later W1 exit; nothing is moved silently.
- **W-2 (approval latency).** The package is CHANGE_REQUESTED, and this
  review adds a delta, an owner approval and a landing before X01 can
  start. CO-STICK-START (latest X01 start 2026-10-14T03:15Z) protects the
  X03 desk work before TNF. Each hour of delay comes out of that margin;
  RISK-AFC-P2-13 and the CO-STICK-START on-miss rule apply.
- **W-3 (Wave 3 compression, existing).** Wave 3 starts after T_yahoo
  (10-16 19:00) and the Wave 2 verdicts, and code must merge by 10-18
  09:00. Seven test-first pairs plus a deploy share one stick for
  instrumented runs. I make no effort estimate. The issue counts per
  milestone do not measure workload: M04 holds three serial stick spikes
  and a live game.
- **W-4.** GitHub's due date has day precision, so the exact times live
  only in the descriptions.
- **W-5.** Three rewritten Lifecycle-local acceptance rows (MS-01, REL-02,
  RISK-13) need Requirements Engineer and Test Engineer acknowledgement
  inside the parent's delta. Without it, the frozen proofs would cite text
  that no longer exists.
- **W-6 (OCR gap).** Every `.md` source was outside OCR coverage
  (`unsupported_ext`) and was reviewed directly. Reverify: not applicable,
  because these are planning sources with no binary.

## developer_feedback

- CHR-OBS-001 (OpenCodeReview 1.13.0, needs work): delegation mode
  excludes `.md` as `unsupported_ext`. In a planning-only diff, that leaves
  every canonical source out of rule coverage. This is a recurring gap for
  planning reviews.
- CHR-OBS-002 (planning generator, needs work): release dependencies are
  derived from milestone-table membership. Changing the grouping would
  silently drop release prerequisites. Keying them on `wave` would remove
  that coupling.
- Tools exercised: git (read), python3 (read-only checks), ocr delegate
  preview/rule.
