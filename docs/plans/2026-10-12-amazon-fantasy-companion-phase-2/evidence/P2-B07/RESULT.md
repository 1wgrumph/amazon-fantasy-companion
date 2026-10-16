# P2-B07 result: panel service (issue #36)

**Outcome: PASS.** The frozen P2-B07T suite is green on `afc/p2-b07t`
(origin/main f838dc3 merged in; merge commit 4292a15). Ready for
independent review.

## What was built

`backend/src/panel/__init__.py` implements `project` and `snapshot` per the
P2-B07T `handoff_contract_choices`:

- `project(game_event, matches)` stores only the game facts
  `{eventId, revision, score, source}` per matched profile in the Panels
  row `freshness` map (the one free-form PanelState attribute in the landed
  store shape). A later revision of the same event replaces them; an equal
  or lower revision never does. It never writes Alerts.
- `snapshot(profile_id, team_league)` derives rows, points, team total and
  progress at read time from the stored Lineup, the profile Settings and
  the statistics seam, so preset, team/league, visibility and starter
  changes appear on the next read with a higher revision (stored projection
  counter + profile revision) and no write on the read path (P2-B07T R2).
  Manual points apply `lineup.presets.TABLES` by reference; Yahoo points
  apply the league `stat_modifiers`; an unknown stored preset is refused
  with `ValueError`. Yahoo starters map through `matcher.PLAYER_MAP_PATH`
  (exact name + team + position); unmatched starters keep a row with
  unknown points and a reason. Missing statistics are null with a reason,
  never zero; staleness is age >= 60 s from the statistics `asOf`,
  evaluated at read time through the `panel.now()` seam.
- Seams: `panel.player_statistics(athlete_id)` returns None in production
  (stored GameEvents carry no per-player statistics, P2-B07T R1), so every
  production point reads unavailable until a stats slice lands.
  `panel.now()` returns RFC 3339 UTC.
- `GET /v1/panel` already routed to `panel.snapshot` in
  `backend/src/api/handler.py`, and `/v1/panel` was already declared in
  `backend/src/api/openapi.yaml` with the Envelope schema, so neither file
  needed a change.
- Retired the panel stub pins: the two panel rows of `STUBS` in
  `backend/tests/unit/test_pipeline_and_stubs.py`, the panel module in
  `test_backend_template.py`, and `/v1/panel` in the 503-stub test of
  `test_api_contract.py` (B04/B05/B06 precedent; the openapi-declares-503
  row stays, since 503 `unavailable` remains a declared response).

## Commands

| Command | Exit | Result |
|---|---|---|
| `git merge origin/main --no-edit` | 0 | merge commit 4292a15 |
| `$HOME/.local/share/afc-tools/backend-tests/bin/python3.12 -m pytest backend/tests/unit/panel backend/tests/deployed/panel -q -p no:cacheprovider` | 0 | 80 passed, 4 skipped (deployed NOT_RUN, no stack) — `CMD-GREEN.txt` |
| `bash tools/ci/gate.sh` | 0 | spec/docs/hygiene/tvapp/backend PASS; backend 816 passed, 3 skipped; mutation 100%, changed-line coverage 100% — `gate.txt` |
| `verify_receipt.py` (P2-B07T receipt) | 0 | PASS, 7 frozen files byte-identical — `frozen-hash-check.txt` |

## Acceptance to evidence

| Requirement | Evidence |
|---|---|
| AFC-PR-039 rows, points, status, total, progress, basis labels | `test_panel_rows.py` green (CMD-GREEN.txt) |
| AFC-PR-065 two presets + Yahoo league scoring | `test_panel_scoring_basis.py` green |
| AFC-PR-040 unavailable vs zero, 60 s stale, replay label | `test_panel_freshness.py` green |
| AFC-PR-044 settings reflected | `test_panel_settings.py` green |
| AFC-PR-046 one truth with alerts across corrections | `test_panel_consistency.py` green |
| Frozen B07T tests byte-identical | `frozen-hash-check.txt` PASS |
| Repository gate | `gate.txt`, exit 0 |
| Deployed panel tests | NOT_RUN (4 skipped, no stack) |

## Remaining risks

- R1 (unchanged, owner decision): no production statistics source; every
  production point reads unavailable until a feed/store stats slice lands.
- The Panels `freshness` map carries the projected game facts and revision
  counter because the landed `store.put_panel` shape has no dedicated
  fields; a future PanelState schema revision should name them.
- Deployed panel tests remain NOT_RUN without a stack.
