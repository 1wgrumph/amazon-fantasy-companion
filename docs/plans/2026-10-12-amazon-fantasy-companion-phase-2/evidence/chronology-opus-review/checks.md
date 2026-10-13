---
type: evidence
title: Phase 2 chronology review — checks
okf_status: draft
tags: [planning, afc, phase-2, chronology, review]
---

# Chronology review checks (DEC-AFC-SD-040)

Candidate `plan/2026-10-12-afc-phase-2` @ `51bc730a880105c9b21d37a7a2dc5da79ada875f`,
base `92f3ed1a0d178d2704c0efdc073ad332dc67b79f`, plan digest
`67ac7a9071859e8d4ef05b863c3e6e4d4931d2451a162abb5bb8115eeb1b7d46`, tracking
payload `f485d8f62f72bf09c1e90c57493e03a178ec93ba7e9fc155cd776a32f736f5e9`.
All checks are read-only against the candidate plus `proposal.json`. Nothing
was applied to canonical artifacts, the payload, GitHub or `journey.json`.

## Deterministic proposal checks

The check script ran with `python3 -I` from a private temporary directory
(not committed). It read `proposal.json`, `github-work-items.json`,
`implementation.json` and `seit.json`.

| Check | Result |
|---|---|
| C01 39 issues exactly once, equal to the payload set | PASS |
| C02 52 slices exactly once, equal to `implementation.json` slices | PASS |
| C03 13 TDD pairs share one issue each | PASS |
| C04 every milestone holds 2..6 issues (3,2,3,4,3,3,3,3,2,2,4,4,3; mean 3.00) | PASS |
| C05 milestone IDs M01..M13 contiguous | PASS |
| C06 no issue dependency points to a later milestone, except the tracked checkpoint CP-X05-HIST → P2-R1 | PASS |
| C07 same-milestone dependencies appear in listed order | PASS |
| C08 all 121 slice dependencies respect milestone order (same single exception) | PASS |
| C09 P2-R1..R4 still follow every other slice of their **wave** | PASS |
| C10 P2-R5 follows D03, D04, D05, SCR1, R4 and precedes L05, X12 | PASS |
| C11 wave entry conditions preserved (Wave 3 after M04 + M06, Wave 4 after M10, Wave 5 after M11) | PASS |
| C12 due times non-decreasing; last is 2026-10-23T12:00:00Z, before T_deadline 19:00Z | PASS |
| C13 every due time already appears in `implementation.json` (no invented dates) | PASS |
| C14 all 44 integration steps mapped exactly once | PASS |
| C15 step → milestone mapping agrees with each step's merged slices | PASS (second run) |
| C16 P2-X11 stays a visible conditional issue | PASS |
| C17 predecessor milestones are all earlier, except one tracked checkpoint (M03 ← M04) | PASS |
| C18 issue titles change only in the `[Mnn]` prefix; the 39 stable IDs are unchanged | PASS |
| C19 SEIT still has 100 proofs and 70 commands | PASS |
| C20 five waves and five releases unchanged | PASS |

The first run failed C15. The draft had split P2-L01 and P2-D01 across M01
and M02, but integration step IE-P2-2 merges both. M01 and M02 were
regrouped (M01 = L01, D01, G01; M02 = X01, B01), and the rerun passed all 20
checks. This was a fault in my own draft, not a product defect
(`BUG_ROUTE: not-a-bug`).

## OpenCodeReview (delegation mode)

- `ocr delegate preview --from 92f3ed1a… --to 51bc730a…`, open-code-review
  v1.13.0, exit 0. It listed 68 reviewable files out of 240 (53 `.json`,
  12 `.py`, 1 `.html`, 1 `.sh`, 1 `.gitignore`).
- 172 files were excluded as `unsupported_ext`. That includes every `.md`
  file: the technical plan, `design.md`, `slice-graph.md`,
  `integration-plan.md`, the 39 issue bodies and the SVG views. This is a
  **typed coverage gap**. I reviewed those sources directly; OCR did not
  cover them.
- `ocr delegate rule <68 files>` exit 0 returned three rule groups: default
  (`.gitignore`, `.html`, `.sh`), `**/*.{json,json5}` (key spelling) and
  `**/*.{py,pyi,ipynb}`. Raw outputs stay in private temp storage and are
  not committed.
- JSON key-spelling rule: a mechanical pass parsed all 53 JSON files
  (0 parse errors, 1,449 distinct keys). The singleton-word scan found no
  misspelled key; `sched` and `vcase` are deliberate abbreviations.
- Python rule group, applied to the chronology-relevant generators: there
  are no defects in the current candidate. These are coupling points the
  delta must update:
  - `evidence/pi-p2-codex/gen_impl.py:194`: asserts the milestone table is
    exactly `M1..M5`.
  - `gen_impl.py:379-392`: builds the P2-R1..R4 "every other slice"
    dependencies from the technical plan's milestone-table `Slices` column.
    If that table becomes the 13-row tracking table, the release
    dependencies silently shrink. Keep a five-row wave/release-checkpoint
    table as this source.
  - `gen_impl.py:572,616,635,658`: fixed X05, M2-date, count-5 and X05-M2
    asserts. Lines 619-623 bind releases to M1..M5. Lines 1122-1125 group
    the HTML close-out table by M1..M5.
  - `evidence/pi-p2-final-refresh/verify.py:37,82-88,129-130` and
    `evidence/te-p2-finalize/check_delta.py:80,119` are historical
    receipts. Keep them unchanged; a new delta validator replaces them for
    the next candidate.
- The default rule group on `.html`/`.sh`/`.gitignore` found nothing
  chronology-relevant. The HTML milestone content is generated, so it is
  covered through the generator above.
- Scope: OCR assisted this review and is not the independent review. Files
  outside the chronology question (Phase 1 receipts, ST-4 scripts) got only
  the mechanical key-spelling pass.

## Reverify

Reverify: not applicable — planning sources only. No compiled binary is
built, inspected or claimed. No runtime proof is claimed.

## Other

- BRAN: unavailable (no `.bran/policy.yaml` in this repository). Normal
  discovery was used.
- No usage or rate limit was hit.
- No nested agents, GitHub writes, installs, device or AWS actions,
  commits or pushes.
