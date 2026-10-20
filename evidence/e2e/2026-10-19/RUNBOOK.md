# P2-X10 hardening run book (preparation unit, issue #44)

Slice P2-X10: Monday 2026-10-19 MNF hardening run — corrections and
starter changes across alerts and panel, duplicate suppression,
stale/unavailable behavior, Sunday defects re-checked; labeled replay
for repeatability; stop at the run record.

This file is preparation only. No scenario in this unit was executed.
Every live scenario stays `PENDING-LIVE`. No live timing, correction,
or starter result is claimed here. Labeled replay is unbound
(`GAP PROCEDURE_UNBOUND` below) and never stands in for live
notification or provider behavior (RISK-AFC-P2-08).

Bindings: `implementation.json` slice P2-X10 (depends on P2-X09;
leases fire-tv-stick, aws-afc-dev, live-game-window; commands
PROC-E2E-LIVE, CMD-DEPLOYED-TESTS; write set `evidence/e2e/2026-10-19/`,
`evidence/visual/e2e-2026-10-19/`); technical plan W4; spec sections
4.1.5, 4.1.12, 4.5. Requirements AFC-PR-025, AFC-PR-026, AFC-PR-040,
AFC-PR-046; risks RISK-AFC-P2-08, RISK-AFC-P2-09, RISK-AFC-P2-10.
Fire OS is primary; Vega is paused — no Vega work or claim
(RISK-AFC-P2-14). Lineup source is manual; no live Yahoo data.

## Timing plan (honest window)

- The slice text names 2026-10-19 (MNF); that window has passed.
- P2-X09 (C3) runs live 2026-10-23T00:15Z, ESPN event 401873010
  (Patriots at Bears), holding the stick exclusively
  2026-10-22T23:30Z to 2026-10-23T03:30Z. Do not touch the stick
  during that lease.
- Earliest X10 live start: after release, at or after
  2026-10-23T03:30Z, while event 401873010 is still relevant
  (post-game ESPN state, corrections, and panel data still served).
- A post-game window can exercise corrections, starter-change
  consistency, duplicate suppression, and stale/unavailable labeling.
  It cannot exercise pre-game or pre-snap live timing, in-game alert
  latency, or live provider handoff timing. Record any such limit in
  the run record; do not backfill it with replay.
- If no qualifying live event remains, keep every live row
  `PENDING-LIVE` for the next live window. Labeled replay is not a
  fallback: it is currently unbound (`GAP PROCEDURE_UNBOUND`, see
  below) and promises no repeatability (RISK-AFC-P2-08).

## Preflight checklist (exact commands)

Run from the repository root. Record command, exit code, and log path
for each row in `PREFLIGHT.md` and the run record. An unrun check is
never a pass.

| # | Check | Exact command |
|---|---|---|
| PF-1 | Source revision | `git rev-parse HEAD && git branch --show-current && git status --short` |
| PF-2 | Toolchain | `python3.12 --version && python3.12 -m pytest --version` |
| PF-3 | Backend suite (offline gate venv) | `bash tools/ci/gate.sh backend` (gate owns the pinned venv; do not substitute a bare host pytest) |
| PF-4 | Deployed suite (CMD-DEPLOYED-TESTS) | `python3.12 -m pytest backend/tests/deployed -v --junitxml=evidence/e2e/2026-10-19/deployed.xml` with `AFC_DEPLOYED_API_URL` set to the stack ApiUrl; without it every deployed test is NOT_RUN/skipped and the row stays a typed gap |
| PF-5 | AWS session state | `aws sts get-caller-identity --profile afc-dev` — on expiry record OWNER_DECISION_REQUIRED `aws login` and continue; never deploy from this run book |
| PF-6 | Deployed endpoint + commit (CMD-STACK-OUTPUTS, CMD-DEPLOYED-COMMIT) | `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --query 'Stacks[0].Outputs[?OutputKey==\`ApiUrl\`].[OutputKey,OutputValue]' --output json` then the CMD-DEPLOYED-COMMIT tag/tree check from `seit.json` |
| PF-7 | App identity on stick (only after lease release) | `adb -s <stick_serial> shell dumpsys package com.afc.companion \| grep -E 'versionCode\|versionName'` and record APK sha256 from the build that produced it; serial comes from the operator's private note, never committed |
| PF-8 | Event re-check 401873010 | `python3 spikes/sp5-espn-feed/capture.py capture --date 20261022 --event 401873010 --provenance live --out evidence/e2e/2026-10-19/capture-401873010` then `python3 spikes/sp5-espn-feed/capture.py verify --out evidence/e2e/2026-10-19/capture-401873010` (CMD-ESPN-CAPTURE bound inside the X10 evidence write set; never the default fixture path, so the historical fixture corpus stays untouched); record status/state from the summary header before any scenario |
| PF-9 | PF-8 capture integrity | `python3.12 spikes/sp5-espn-feed/capture.py verify --out evidence/e2e/2026-10-19/capture-401873010` (exit 0 required before any scenario reads the PF-8 capture; verifies only the evidence-directory capture) |
| PF-10 | Gates | `bash tools/ci/gate.sh hygiene` and `bash tools/ci/gate.sh docs` |

## Scenario matrix

Common preconditions for S1–S5: preflight PF-1..PF-10 recorded; stick
linked (manual mode; OA-10 confirmation by the owner if re-link is
needed); followed team/league set with at least one starter in event
401873010; alert types enabled; panel in
`PanelMode.fullScreen` (P2-X04 verdict). Each scenario fills one
run-record entry from `run-record.template.json`.

### S1 — Correction applied across alerts and panel

- Exercises: AFC-PR-026, AFC-PR-046; VCASE-AFC-PR-026,
  VCASE-AFC-PR-046; SEIT-AFC-PR-026, SEIT-AFC-PR-046.
- Preconditions: a scoring fact already emitted as an alert and shown
  on the panel; a later ESPN summary revision that corrects it
  (live post-game edit only; replay is `GAP PROCEDURE_UNBOUND` below).
- Steps: (1) capture baseline `GET /v1/alerts` and `GET /v1/panel`;
  (2) ingest the corrected summary (live poll);
  (3) re-read both surfaces; (4) screencap the panel.
- Expected observable: the existing alert record is revised in place
  (no new alert id) and the panel value carries the same corrected
  fact; matcher revises in place per `backend/src/matcher/`.
- Failure behavior: stale value on either surface, or a second alert
  id for the correction, is a defect → `PROC-BUG-TRIAGE`; record
  typed FAIL with both payloads; never hand-edit evidence to match.

### S2 — Starter change across alerts and panel

- Exercises: AFC-PR-046; VCASE-AFC-PR-046; SEIT-AFC-PR-046.
- Preconditions: manual lineup with two eligible players at one slot;
  panel visible; alert cursor at head.
- Steps: (1) with the panel visible, record panel rows, team total,
  and the `GET /v1/panel` revision/fact (`R1`); (2) swap the starter
  in the manual lineup; (3) hide the panel and confirm it is hidden;
  (4) while it stays hidden, wait at least one 30 s refresh cycle and
  let a later update arrive — confirm via `GET /v1/panel` that the
  revision/fact advanced to `R2` (`R2 != R1`, new-starter fact);
  (5) show the panel again; (6) compare the shown row, total, and
  revision/fact against `R2`; (7) confirm the next qualifying event
  alerts for the new starter only; (8) screencap before-hide and
  on-show. Waiting for a refresh while the panel stays visible does
  not satisfy this scenario.
- Expected observable: on show, the panel row, total, progress, and
  revision/fact equal `R2` (the update that arrived while hidden),
  not stale `R1`; no alert fact references the benched player after
  the swap; both surfaces agree (VCASE-AFC-PR-046: hidden panel
  refreshes on show).
- Failure behavior: a shown panel carrying `R1`, the benched player,
  or a revision/fact that differs from `GET /v1/panel` is a defect →
  `PROC-BUG-TRIAGE` with both payloads and screencaps. If no later
  update arrives while hidden (`R2` never observed), or hide/show
  was not performed, the scenario is `PENDING-LIVE`/`not_run`, never
  a pass. A missing qualifying alert event likewise leaves that half
  PENDING-LIVE.

### S3 — Duplicate suppression

- Exercises: AFC-PR-025; VCASE-AFC-PR-025; SEIT-AFC-PR-025.
- Preconditions: one resolved event that already emitted an alert.
- Steps: (1) record alert count/cursor; (2) re-poll the unchanged
  event twice (live poll cycle);
  (3) re-read `GET /v1/alerts`; (4) restart AlertService on the stick
  and confirm history does not replay.
- Expected observable: at most one alert per resolved event; repeated
  retrieval emits nothing further (`backend/tests/unit/matcher/test_matcher_dedup.py`).
- Failure behavior: any second alert for the same resolved event is a
  defect; preserve both records and triage.

### S4 — Stale/unavailable behavior

- Exercises: AFC-PR-040; VCASE-AFC-PR-040; SEIT-AFC-PR-040.
- Preconditions: panel showing fresh values; ability to withhold the
  feed (pause ingest / unreachable endpoint in dev only) and a player
  with no statistic (unavailable case).
- Steps: (1) capture fresh panel; (2) withhold updates past 60 s
  (`stale_after`, DEC-AFC-SD-035); (3) screencap stale labels;
  (4) show the unavailable value; (5) restore feed and confirm values
  go fresh again.
- Expected observable: stale values labeled stale, missing values
  labeled unavailable (null with reason, never zero); no silently old
  or silently missing value (`backend/tests/unit/panel/test_panel_freshness.py`).
- Failure behavior: an unlabeled old value or a zero-for-unknown is a
  defect; if the feed cannot be withheld safely in the live window,
  keep the scenario PENDING-LIVE (replay is `GAP PROCEDURE_UNBOUND`,
  not a substitute).

### S5 — Sunday defect re-check

- Exercises: every defect filed from the P2-X09 run record
  (`evidence/e2e/2026-10-18/`); requirements per defect.
- Preconditions: P2-X09 run record merged and each defect triaged;
  fix (if any) deployed via the L03 command set outside an in-progress
  game, never during this run.
- Steps: per defect — (1) replay the recorded repro steps verbatim;
  (2) record observed vs. original outcome; (3) screencap/geometry
  where the original evidence had them.
- Expected observable: each defect marked fixed-still-fixed,
  still-failing, or not-reproducible-in-window with evidence.
- Failure behavior: a still-failing defect stays open with the new
  evidence attached; no silent fix inside this slice (defects route
  through bug-triager).

## Labeled replay — `GAP PROCEDURE_UNBOUND`

Labeled replay is not currently executable as a repeatability
procedure for S1–S4, and no repeatability is promised from it.
Static inspection at this revision found:

- `backend/src/feed_ingest/replay.py` loaders return only the latest
  captured summary, normalized; nothing ingests or selects a
  baseline-to-correction sequence, so S1's before/after cannot be
  driven from them as written.
- The deployed suite (`backend/tests/deployed`, 26 test functions)
  has zero node names matching a replay filter and no replay
  markers, so a deployed replay-filter command selects nothing —
  an empty selection is a gap, never a pass.

Binding an executable sequence (baseline ingest, correction ingest,
named nodes) is future work outside this slice's write set. Until
then: record `GAP PROCEDURE_UNBOUND` wherever a scenario would have
used replay, keep every live row `PENDING-LIVE`, and label nothing
`historical-replay` from this run book. The historical fixture
corpus stays untouched (PF-8/PF-9 write and verify only inside
`evidence/e2e/2026-10-19/capture-401873010/`). Even once bound,
replay could never prove live notification timing, provider
handoff, or on-stick presentation during a game (RISK-AFC-P2-08).

## Acceptance-to-evidence map

| Scenario | Evidence file | Producing command |
|---|---|---|
| All | `evidence/e2e/2026-10-19/run-record.json` (from `run-record.template.json`) | operator-filled during the run; one entry per scenario |
| All | `evidence/e2e/2026-10-19/deployed.xml` | PF-4 (CMD-DEPLOYED-TESTS) |
| Replay | none (`GAP PROCEDURE_UNBOUND`) | no bound command; do not fabricate a replay artifact |
| S1 | `evidence/e2e/2026-10-19/s1-alerts-before.json`, `s1-alerts-after.json`, `s1-panel-before.json`, `s1-panel-after.json` (sanitized API reads, no credentials) | `GET /v1/alerts`, `GET /v1/panel` via the deployed helpers |
| S1, S2, S4 | `evidence/visual/e2e-2026-10-19/s1-panel-corrected.png`, `s2-panel-before.png`, `s2-panel-after.png`, `s4-panel-stale.png`, `s4-panel-unavailable.png` | `adb -s <stick_serial> exec-out screencap -p > <file>` (CMD-ADB-SCREENCAP / PROC-E2E-LIVE) |
| S1–S5 | `evidence/visual/e2e-2026-10-19/<scenario>-window.txt`, `<scenario>-display.txt` | CMD-ADB-GEOMETRY (`dumpsys window`, `wm size`) via a private capture dir, sanitized copy only |
| S3 | `evidence/e2e/2026-10-19/s3-alert-counts.txt` | alert count/cursor before and after each re-poll |
| S5 | `evidence/e2e/2026-10-19/s5-defect-recheck.md` | per-defect table linked to the P2-X09 record |
| Preflight | `evidence/e2e/2026-10-19/PREFLIGHT.md` | PF-1..PF-10 with exits (this unit's copy is preparation-time) |

Stop rule: stop at the run record. Defects go to bug-triager; no fix,
deploy, or review inside the live run.
