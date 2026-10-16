# P2-B07T result: panel service red suite (issue #36)

**Outcome: PASS.** The frozen red suite is committed on `cloud/p2-b07t`
(baseline `origin/main` fc206b4). One open item needs an owner decision
before the panel can show real points in production (see Remaining risks,
R1). It does not block this red slice or the P2-B07 green slice.

## CMD-RED summary

Command (from `backend/`): `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $VENV/bin/python -m pytest tests/unit/panel tests/deployed/panel -v -p no:cacheprovider --tb=short --junitxml=../docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B07T/CMD-RED.xml`

| Collected | Failed | Passed | Errors | Skipped | Exit |
|---|---|---|---|---|---|
| 84 | 80 | 0 | 0 | 4 | 1 |

- All 80 failures are `AssertionError: panel behavior is not implemented (AFC-STUB)`.
  `panel_support.attempt` converts the stub's `NotImplementedError`. No
  collection or import errors (`collect.txt`: 84 collected).
- The 4 skips are the deployed cases. With no `AFC_DEPLOYED_API_URL` they
  skip as `NOT_RUN` and open no connection.
- Satisfiability: a scratch reference panel, never committed, passes all 80
  tests. Seven single-change mutants each fail tests (3/1/13/1/3/6/3): zero
  for missing values, `>` instead of `>=` 60 s, preset ignored, no revision
  guard, `asOf` set to read time, preset table applied to a Yahoo league,
  and a settings change that does not raise the revision.
- `verify_receipt.py receipt.json` returns PASS. It rejects a tampered
  frozen hash and a tampered test file (exit 1).
- `git diff --check` is clean. The diff stays inside
  `backend/tests/unit/panel/`, `backend/tests/deployed/panel/` and
  `evidence/P2-B07T/`.
- Gate (`gate.sh spec docs hygiene backend`, exit 3):
  - docs: PASS.
  - backend: FAIL, with exactly the 80 red tests plus 24 IPv6 failures in
    the unchanged `test_deployed_guard.py`. The container has no AF_INET6.
    644 tests passed.
  - spec and hygiene: GAP/FAIL only because `dot`, `mutmut` and
    `diff-cover` are missing in this container.

## Acceptance to test

| Requirement | Tests (backend/tests/unit/panel unless noted) |
|---|---|
| AFC-PR-039: lineup rows, points, game status, total, progress, scoring basis | `test_panel_rows.py`: one row per starter, points under the basis, game status, total = sum, no duplicate rows, progress 0 / 1 / partial, envelope source and team/league, stable re-read, no lineup gives no fabricated total, `GET /v1/panel` |
| AFC-PR-039 negative: no value without its basis | `check_envelope` on every snapshot; `test_every_point_value_travels_with_its_basis[*]` |
| AFC-PR-065: two presets by reference, default Half-PPR, Yahoo league scoring | `test_panel_scoring_basis.py`: default/PPR/Half-PPR; 18 per-statistic cases against `lineup.presets.TABLES`; Yahoo `stat_modifiers`; preset never used for Yahoo; no point without a table row; third preset never scored |
| AFC-PR-040: unavailable vs zero, stale at 60 s, replay label | `test_panel_freshness.py`: null with reason (never 0), known zero, unknown game status, total over an unknown row, `asOf` = source timestamp, oldest-row total `asOf`, 0/59/60/61 s boundary, stale keeps its number, staleness evaluated at read time, undated value never fresh, live/replay source, unmatched Yahoo starter unavailable |
| AFC-PR-044: settings reflected | `test_panel_settings.py`: preset change (store and `PUT /v1/profile`), revision rises, `Settings.teamLeague` selects the panel, active lineup by default, query echoed, foreign pair shows no rows, team/league change, `GET /v1/panel?teamLeague=`, visibility from `panelPrefs`, default shown, unrelated change keeps facts |
| AFC-PR-046: one truth with alerts across corrections and starter changes | `test_panel_consistency.py`: first-event facts, correction revises points in place, game facts replaced, reassigned play still revises, stale revision never regresses, facts equal the alert record, replay agreement, all matched profiles share facts, benched row replaced and total recomputed, alerted starters are rows, hidden panel current on show |
| Deployed (SEIT-AFC-PR-039/-040/-044/-046/-065 execution) | `backend/tests/deployed/panel/test_panel_deployed.py`: data shape and value objects, re-read identity, preset change reaches the panel, game facts agree with `/v1/alerts`. NOT_RUN here |
| AC-AFC-P2-DX-01, PATH-01, LAND-01, REL-01, REV-01, RISK-AFC-P2-10 | `receipt.json` `proof_rows`, `developer_feedback`, `hygiene`, `route`/`route_basis`. Not closed by a red slice |

## Contract choices

These are recorded in full under `handoff_contract_choices` in
`receipt.json`:

1. **Wire shape.** The suite follows the P2-A05T TV wire shape
   (`PanelFixtures.kt`, gap `PANEL_WIRE_UNFROZEN`). It adds three keys that
   the TV decoder ignores: `stale` on each value object, `data.visible` and
   `data.games`.
2. **Statistics seam.** `panel.player_statistics(athlete_id)` returns
   `None` or `{gameId, gameState, gameStatus, source, asOf, stats}`. A
   clock seam, `panel.now()`, is added as well. The landed store carries
   no per-player statistics.
3. **Stale boundary.** A value is stale when its age is 60 s or more. This
   matches P2-A05T and the register.
4. **Team/league key.** The key is `<league>/<team>`. When none is given,
   the panel uses `Settings.teamLeague`, then the active lineup. Any other
   pair shows no rows.
5. **Envelope source.** The envelope `source` is the lineup source. The
   frozen P2-B03T deployed tests already require this.
6. **Alert agreement.** `games` facts `{eventId, revision, score, source}`
   are compared with the alert record (P2-B05T `triggerContext`). Only a
   later revision of the same event replaces them.
7. **Settings and starters.** A settings change shows on the next read with
   a higher revision. A starter change is tested as a lineup change
   followed by the next projected event.
8. **Totals and progress.** A total over an unknown row is `None` or carries
   a reason. Progress is pinned only at 0, at 1 and strictly between.

## Remaining risks

- **R1 (owner decision): no production statistics source.** Stored
  GameEvents carry no per-player statistics, and `store.put_event` rejects
  extra attributes. P2-B07 can go green through the seam, but every
  production point will read "unavailable" until a slice stores ESPN
  boxscore statistics. That slice needs a feed_ingest/store change under
  the backend-template lease. The AFC-PR-039 stick demonstration (P2-X09)
  needs this allocated.
- **R2: API cannot write panels.** ApiFunction has only Panels `GetItem`. A
  settings-driven revision bump must be derived rather than written on
  read. Moto does not enforce IAM.
- **R3: TV pairing.** P2-A05 must accept or reconcile the three additive
  keys. The TV reads with `opt()`, so extra keys are harmless.
- **R4: Older-play corrections.** Which `games` facts win when an older
  play of the same game is corrected is not pinned.
- **R5: Stub registry.** P2-B07 must retire the panel rows of `STUBS` in
  `backend/tests/unit/test_pipeline_and_stubs.py`. B04 did the same for
  the matcher.
- **R6: Route.** The route is the dispatch packet's Claude Code route, the
  second ordered fallback in `implementation.json`. No usage-limit evidence
  was produced here, and P2-6 inspects this (RISK-AFC-P2-10).
- **R7: Container gaps.** The gate ran with tools missing and without
  IPv6. A full gate run on a provisioned host is still owed.
