---
type: planning-receipt
title: IE chronology and profile projection receipt (DEC-AFC-SD-040/041)
okf_status: draft
tags: [planning, afc, phase-2, integration, chronology]
---

# IE chronology/profile projection receipt

**Verdict: CANDIDATE_READY** (author planning delta; not review or assurance).

- Route: Integration Engineer planning, frozen `opensource-hackathon`
  primary Claude Code / Claude Opus 5.5 / high. No nested agents.
- Skills: bearing-lite 1.1.7 `integration-engineer` and `integration-engineering`.
- Baseline: both specialist files were byte-identical to
  `51bc730a880105c9b21d37a7a2dc5da79ada875f` before this delta.
- Inputs: `specialists/chronology-opus-review.md`,
  `evidence/chronology-opus-review/proposal.json`, the current technical
  plan, and the Phase 1 `journey.json` `profile_selection.frozen_snapshots`.

## Changed paths

| Path | sha256 |
|---|---|
| `specialists/slice-graph.md` | `b382d93da5f82d6b096fa9a33595e851cb2c6d334b3cfed2f229adea3ff51a5b` |
| `specialists/integration-plan.md` | `2dbcf9b99a9138ae6b5beef8f6475d1a069d02efe35804edb700a1d3e8ec7827` |
| `specialists/ie-chronology-041-receipt.md` | this file |
| `evidence/chronology-profile-delta/ie-apply.py` | deterministic rebuild from the baseline. A second run gave identical hashes. |
| `evidence/chronology-profile-delta/ie-check.py`, `ie-check.json` | 32 checks against the baseline |

No git mutation, no remote write, and no runtime, device or AWS action.
No canonical technical plan, design, SEIT or implementation edit.

## What changed

- **Slice graph.**
  - The column is now `GitHub milestone, wave`. Each slice takes its issue's
    M01..M13 from the proposal; the wave column is unchanged.
  - Text where Mn meant a wave or release now says Wn or Wave n. This covers
    R1..R4 "every other Wave n slice", X11 W3 exit, SCR1 W4 exit, D02 before
    W4 exit, the L05/R5 W5 candidate, the L03 Wave 3 backend head and A01 W1.
  - P2-L01 now creates M01..M13.
  - In X05, PR 1 is labelled CP-X05-HIST (feeds R1 in M03 and B02 in M05),
    and PR 2 closes the M04 issue. The X05→R1 condition token M2 is now M04.
  - New notes:
    - Release prerequisites derive from the wave, never from the 13 GitHub
      milestone groups.
    - Wave 2 entry is per lane: X01 for X04, B01 for the backend, A01 for A02.
      X04 does not wait for R1.
  - Lane bindings now name `opensource-hackathon` for every lane and the
    Scribe; `bug-triager` stays for defects. The note carries the full
    profile sha256 and the `--contributor-mode on` hold, and the bearing-lite
    skill paths now point to 1.1.7.
- **Integration plan.**
  - Every step now has `milestone` (the proposal's
    `integration_step_milestone`) and `wave` (the old milestone number).
    IE-P2-1, IE-P2-6 and IE-P2-11 also carry a `milestone_note`.
  - The steps summary is grouped by wave and lists each step's GitHub
    milestone. It also states CP-X05-HIST, CP-X03-REG, per-lane Wave 2 entry,
    and that IE-P2-35 still precedes IE-P2-34.
  - Cut-offs CO-M1..CO-M5 keep their IDs and times and now apply to W1..W5.
  - `wave_gate_costs` entries carry `release_checkpoint` and
    `github_milestones`.
  - `apk.m<n>` and `release.m<n>` keep their names, with n defined as the wave.
  - `frozen_capability_binding` now holds:
    - `lane_profiles`;
    - the full `opensource-hackathon` binding: 13 role/session routes with
      ordered fallbacks and cadences, TDD, concurrency, clean session,
      `review.coverage_assist` required, `deterministic_verification.reverify`
      enabled, and the Muse hold;
    - the `bug-triager` binding, byte-identical.
  - Lifecycle assessment sessions now use the `opensource-hackathon` IE
    execution and ATE routes for every lane. The tech-writing assurance
    exemption is removed.
  - Historical `concurrency_findings` are unchanged; their Mn means Wn.

## Checks (`python3 …/ie-check.py`: 32/32 PASS)

- **Slices and dependencies:**
  - 52 slices, same order, wave membership identical.
  - Lane/role, UIDs, AC, spec, design, write sets, commands, leases and
    skills are unchanged.
  - Goal and depends-on cells equal the baseline after token mapping only.
  - 81 arrows; only the X05→R1 token changed.
  - 121 dependencies, with an identical edge set between the old
    milestone-derived and the new wave-derived release expansion.
  - R1..R4 follow every other slice of their wave.
  - The graph is acyclic. X04 does not wait for R1, and X04 precedes R1
    through A01.
- **Issues and steps:**
  - 39 issues in 13 milestones, per-milestone counts equal to the proposal
    (all within 2–6), and 13 TDD pairs that share their issue's milestone.
  - 44 steps with id, order, merges and after unchanged. Step milestone and
    merged-slice milestone agree.
  - Step text equals the baseline after Mn→Wn mapping.
  - 14 cut-off IDs and times are unchanged.
  - Gate costs are unchanged (720/900/2100/0/120 s), and so are resource
    groups, branches, stubs, glue, anomaly handling and the final candidate.
- **Profile binding:**
  - Recomputed sha256 of the compact sorted snapshot is `7d501eb8…6ab1`.
  - The routes equal the journey snapshot. Capabilities and holds are
    present, and bug-triager is unchanged.
- **Hygiene:** no stale wave tokens outside the historical findings, and no
  home paths.

OCR delegation is not run: this is assembly authoring, not independent
review. Reverify: not applicable, because these are planning sources with no
binary. BRAN is unavailable (no native policy).

## Residuals for the parent

Exact proposed text; I did not write these myself.

1. **Technical plan, M09 exit criteria (line 306).** Change "redeployed at
   the M3 backend head" to "redeployed at the Wave 3 backend head".
2. **`evidence/pi-p2-codex/gen_impl.py` (Plan Integrator).** Required before
   `implementation.json` is regenerated:
   - read the column `GitHub milestone, wave`;
   - derive R1..R4 prerequisites from the wave column, not from milestone
     membership (CHR-OBS-002);
   - accept step `wave`/`milestone_note`;
   - replace the asserts for X05 `M1`/`M2`, count-5 and `M1..M5`.

   I did not run it, because it writes `implementation.json` outside this
   write set. By inspection, it cannot parse the current sources:
   `gen_impl.py:431` reads `s["M, wave"]`, and `:379-392` derives `MS_OF`
   from the milestone table.
3. **`seit.json` `frozen_profile_binding` (Test Engineer).** It still keys
   the primary, frontend, heavyweight and tech-writing lanes. The bug-triager
   `source_ref` here still points at `seit.json/frozen_profile_binding/bug-triager`
   (unchanged by instruction). TE should rebind to `opensource-hackathon`.
4. **RE row verdicts** (MS-01, REL-02, DX-02, RISK-13). This projection does
   not depend on them. The parent integrates them only after RE passes.
5. **Schedule risk W-1** (X04 timebox against R1 at 2026-10-14T23:00Z) stays
   an owner decision. No date moved.

## developer_feedback

- IE-CHR-OBS-001 (planning generator, needs work): `gen_impl.py`
  hard-codes the column name `M, wave` and derives releases from milestone
  membership. Any grouping change silently changes release prerequisites;
  keying them on the wave removes that coupling (same as CHR-OBS-002).
