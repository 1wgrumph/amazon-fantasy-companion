---
type: specialist-receipt
title: Requirements Engineer SD-035 delta receipt — AFC-2026-10-11 spec track ST-2
okf_status: draft
tags: [requirements, planning, afc, spec-track]
---

verdict: **PASS**

decision: DEC-AFC-SD-035 (2026-10-12, owner answers to ST-2 owner questions).
role: Requirements Engineer. Branch `afc/st4-spec`.
Owner questions source: `specialists/re-st2-receipt.md` (Owner questions list only);
Q1 retired by DEC-AFC-SD-027 per `specialists/re-st2b-receipt.md`.

changed_paths (exact write set):
- `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/requirements-register.md`
- `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/re-sd035-receipt.md` (this file)

changed rows (UID: old -> new):
- AFC-PR-014: open parameter close_game_margin -> close game means within 8 points in the 4th quarter or overtime (SD-035, P1); sources + SD-035
- AFC-PR-023: open parameter excitement_levels -> Off / Mild / Hype (SD-035, P2); sources + SD-035
- AFC-PR-029: resolution criteria + Q5 spike order (Prime Video TNF, ESPN app, DirecTV Stream app, YouTube TV) in rationale; local-broadcast (CBS/FOX/NBC) channel + carrying app, else no deep link, in criteria; sources + SD-035
- AFC-PR-040: open parameter stale_after -> 60 seconds (SD-035, P3); sources + SD-035
- AFC-PR-045: owner acceptance only -> owner acceptance plus body text >= 24 px, scores >= 32 px at 1080p, in statement and criteria; sources + SD-035
- AFC-PR-047: panel beside own player with labeled sample footage -> full-screen lineup panel in the companion app; rationale Q4; sources + SD-035
- AFC-PR-048: Under Mode A fallback routing -> routing while panel is full-screen in the companion app; sources + SD-035
- AFC-PR-049: active footage-license requirement -> WITHDRAWN by SD-035 with rationale (UID retained)
- AFC-PR-050: active footage-label requirement -> WITHDRAWN by SD-035 with rationale (UID retained)
- AFC-PR-051: active non-NFL-footage requirement -> WITHDRAWN by SD-035 with rationale (UID retained)
- Header/C5-coverage/Panel-coverage/common-fields: SD-035 delta note; C5 honoring reworded; 049..051 marked withdrawn; STATUS exception recorded
- New section: Owner questions and open items table (Q1..Q10, P1..P3, D1 status)
- AFC-PR-065: unchanged (D1 OPEN; Yahoo default half-PPR proposed, awaiting confirmation)

assumption check (no other row silently depends on Mode A footage): PASS.
Mode A / footage mentions were only in the C5 coverage row and rows 047..051
(PR-009 "mode change" is schedule mode, unrelated; PR-041 is the primary
panel-beside-provider-video path, unchanged). All updated consistently; no new
requirement and no model/allocation change needed (allocations untouched, so the
22/22 ST-3a element coverage from ST-2b still holds; PLAYER stays allocated).

verification methods: unchanged per row except withdrawn rows (no verification,
VCASE retired). Positive/negative criteria kept consistent with the new values.

VERIFY (run in the worktree, branch afc/st4-spec):
- `git merge --no-edit origin/main` -> exit 0 (plain merge, tools/spec re-vendor)
- UID check `grep -oE 'AFC-PR-[0-9]{3}' <register> | sort -u | wc -l` -> 65; ids 001..065 all present
- `grep -nE 'close_game_margin|excitement_levels|stale_after' <register>` -> decided values only, no "open parameter" wording
- `grep -n -i 'sample footage' <register>` -> only withdrawn rows 049..051 (original statements + withdrawal rationale)
- rule-12 path scan `grep -nE '(/home/|/Users/)[A-Za-z0-9._-]+/' <write set>` -> no output

## developer_feedback

no new observations. Tools exercised: `read_skill` (requirements-engineering),
file reads (register, re-st2-receipt.md, re-st2b-receipt.md), `edit_file`
(register), `write_file` (this receipt), `git merge/commit/push`, `grep` probes.

## SD-035 delta 2 — D1 closure (2026-10-12)

verdict: **PASS**

changed_paths (delta 2 write set):
- `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/requirements-register.md`
- `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/specialists/re-sd035-receipt.md` (this file, append only)

changed rows:
- AFC-PR-065: single default table -> customer-selectable preset of exactly two (PPR / Half-PPR); Default preset Half-PPR; full coefficient tables; Yahoo leagues under Yahoo scoring; label with selected preset; sources + SD-035 (D1)
- AFC-PR-066: new — TV app records selected preset (PPR/Half-PPR, default Half-PPR); VCASE-AFC-PR-066; PROFILE, LINEUP; SD-035 (D1)
- AFC-PR-039: default table -> selected preset table for manual
- Header: 65 -> 66 requirements; D1 left open -> closed by SD-035 delta 2
- D1: Open -> Closed by SD-035 (PPR + Half-PPR; Default Half-PPR; PR-065/066)

VERIFY (delta 2, branch afc/st4-spec):
- UID check `grep -oE 'AFC-PR-[0-9]{3}' <register> | sort -u | wc -l` -> 66; ids 001..066 all present; 66 rows; no row dups
- `grep -n "AFC-PR-065" <register>` -> PPR, Half-PPR, Default preset Half-PPR, all coefficients, preset label, Yahoo scoring
- rule-12 path scan `grep -nE '(/home/|/Users/)[A-Za-z0-9._-]+/' <write set>` -> no output

developer_feedback (delta 2): no new observations. Tools exercised: `read_skill` (requirements-engineering), file reads (register, receipt), `edit_file` (register, receipt append), `git commit/push`, `grep` probes.
