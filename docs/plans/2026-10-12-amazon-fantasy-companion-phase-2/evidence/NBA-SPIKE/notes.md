# NBA spike notes (DEC-AFC-NBA-STRETCH-20261020)

Stretch goal only. NFL stays the product. Nothing here runs unless
`AFC_ENABLE_NBA` is set to `1`, `true`, or `yes`. The flag is not set in
`backend/template.yaml`, so deployed behavior is unchanged.

## What was built

- `backend/src/nba/scoring.py`: `NBA_POINTS_TABLE`, a standard points-league
  basis: PTS 1, REB 1.2, AST 1.5, STL 3, BLK 3, TO -1. `score()` mirrors
  `lineup.presets.score` and refuses a statistic with no table row.
- `backend/src/nba/normalize.py`: `scoreboard_games()` (validates with the
  pinned NFL scoreboard schema, whose read fields match the ESPN basketball
  shape), `validate_nba_summary()`, and `boxscore_statistics_nba()`, which
  emits the same per-athlete record shape as the NFL `boxscore_statistics`
  (Decimal values, `asOf` is the latest play wallclock, invalid athlete ids
  and unparseable or non-finite values are skipped, 200-athlete bound).
- `backend/src/nba/__init__.py`: `FEED`
  (`https://site.api.espn.com/apis/site/v2/sports/basketball/nba/`),
  `enabled()`, and `poll(get_json, store_records=None)`. With the flag off,
  `poll` returns `{stored: 0, failed: []}` without fetching. With it on, it
  fetches the scoreboard, then each game's `summary?event=`, and stores the
  boxscore records through `feed_ingest.ingest.store_player_statistics`, so
  they land in the same player-statistics table the panel seam reads.
- Flag-gated hooks, inert when off:
  - `feed_ingest.poll()` calls `nba.poll(_get_json)` after the NFL loop.
  - `panel._basis()` accepts a stored `scoringPreset` of `nbaPoints` and
    returns the NBA table, so `panel.snapshot()` produces rows, team total
    and progress for an NBA lineup through the existing panel path. With
    the flag off, `nbaPoints` raises "Unknown scoring preset" exactly as
    any unknown preset did before this spike.

## Fixtures and verification

- Fixtures in `backend/tests/fixtures/nba/` are synthetic and trimmed,
  hand-written from the real ESPN shape captured on 2026-10-20 (scoreboard
  and a completed game's summary). Observed real shape: scoreboard events
  carry `status.type.state`, `competitions[].competitors[].team` and
  `leaders`; the summary has `header.id`,
  `header.competitions[0].status.type`, a top-level `plays[]` list with
  inline participants and `wallclock`, and
  `boxscore.players[].statistics[]` with a null `name`, `keys`
  `[minutes, points, fieldGoalsMade-fieldGoalsAttempted, ..., rebounds,
  assists, turnovers, steals, blocks, ...]`, and positional string `stats`.
- The new normalization was also run once against that real capture before
  trimming: 15 scoreboard games parsed, 27 athlete records extracted from
  the completed game, and one athlete's hand-computed points (20 PTS,
  9 REB, 4 AST, 2 TO = 34.8) matched `nba.scoring.score` exactly.
- Unit tests: `backend/tests/unit/nba/test_nba_spike.py` (17 tests,
  test-first). NFL panel basis: the panel scores manual lineups with
  `lineup.presets.TABLES` (PPR / Half-PPR, settings `scoringPreset`,
  default Half-PPR) and Yahoo lineups with the stored league
  `stat_modifiers`. NBA reuses that same seam, adding one more basis.

## What the TV app would need next (not built)

- `GET /v1/panel` already returns rows for an NBA lineup when the backend
  flag is on and the profile's stored preset is `nbaPoints`, but the API
  cannot store that preset yet: `backend/src/api/openapi.yaml` and
  `handler.py` restrict `scoringPreset` to `ppr`/`halfPpr`, and
  `lineup.active_lineup()` refuses other stored presets. Widening those
  enums, plus a panel `scoringBasis` wire value the TV decoder accepts,
  is required before any screen work.
- TV side: accept `scoringBasis: nbaPoints` in the panel decoder and its
  fixtures, label the basis on the panel, and add NBA slots (PG/SG/SF/PF/C)
  to manual lineup entry. No `tv-app/` change was made in this spike.
- Alerts are out of scope: NBA summaries are not normalized into
  GameEvents, so the matcher/alert-policy/provider chain never sees NBA
  plays. That needs an NBA play mapping (scoring plays, periods) and an
  athlete map before it can reuse the pipeline.

## Risks and shortcuts

- `shortcut:` NBA summary validation is hand-checked pinned fields, not a
  pinned JSON Schema file like the NFL feed. Add a schema file if NBA
  leaves spike scope.
- The NBA poll runs inside the NFL poll invocation when enabled; it has no
  replay fallback and no deadline guard of its own (the NFL `_get_json`
  10-second bound applies per request). Fine for a flag-off spike; not
  production shape.
- ESPN's API is unofficial and unpinned for basketball; shapes were
  observed once (2026-10-20) and may drift.
