---
spike: SP-5 ESPN feed
slice: P2-X05
verdict: PARTIAL
device: none (backend feed spike; no Fire TV device used)
started_at: 2026-10-14T14:47:19Z
ended_at: 2026-10-14T14:55:01Z
first_install_at: not applicable (SP-1 and SP-4 only)
unblocks: [AFC-PR-064, AFC-PR-013]
conditional: none
---

# SP-5 ESPN feed: interim verdict (PR 1 of 2)

**Verdict: PARTIAL.** Endpoints, schema shape, the capture tool and
historical replay fixtures are proven. Live update timing and correction
evidence wait for the TNF capture on 2026-10-15 (PR 2). This interim verdict
blocks only the live-timing route: the feed_poll_interval check and live
correction behaviour of AFC-PR-012.

## Routes tried

| Route | Documentation source | Observed result |
|---|---|---|
| Scoreboard `GET https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=YYYYMMDD` | ESPN unofficial public JSON (SD-004); no published contract | HTTP 200, no auth. Header `application/json;charset=UTF-8`: observed during the 2026-10-14 probe, not retained. 2026-10-11: 13 events, 117,614 bytes. 2026-10-12: 1 event, 23,199 bytes. Every event `STATUS_FINAL`. |
| Summary `GET https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event=<id>` | ESPN unofficial public JSON (SD-004) | HTTP 200 for all 14 events. 530,832 to 679,842 bytes each. `header.id` equals the event id. Header `cache-control: max-age=1`: observed during the 2026-10-14 probe, not retained. |

## Observed result

- **Capture tool:** [`capture.py`](capture.py) is stdlib only. It accepts
  only https GETs to `site.api.espn.com`, reads at most `--max-bytes`
  (default 4 MiB) and checks the HTTP status. The body must parse as JSON
  with the expected shape: scoreboard `events` list, summary `header.id`
  equal to the event id. It validates every body for a game before writing
  any of them. It never overwrites a fixture; a re-capture appends the next
  sequence number. It waits 1 s between requests. `capture.py verify`
  recomputes every indexed sha256. Offline tests are in
  [`test_capture.py`](test_capture.py), including malformed-JSON,
  oversize, non-200, wrong-shape, unsafe-id, wrong-host, append-only and
  tamper cases.
- **Fixtures:** `backend/fixtures/replay/`
  holds 14 completed games in the CONTRACT-AFC-P2-FIXTURE layout. Each game
  has `001-scoreboard.json` (the raw date scoreboard) and
  `001-summary.json` (the raw summary), each byte-identical to the response
  body. `index.json` records `url`, `retrieved_at` (UTC), `http_status`,
  `sha256`, `bytes`, `game_status` and `provenance: historical-replay`. None
  of these fixtures is labeled live.
- **Schema facts needed by P2-B02 (DES-AFC-P2-FEED):**
  - Plays sit under `drives.previous[].plays[]`; there is no top-level
    `plays` key. Each play has `id` (game id plus play suffix),
    `sequenceNumber`, `type`, `text`, `awayScore`/`homeScore`, `period`,
    `clock`, `scoringPlay`, `wallclock` and `modified`. Play participants
    and statistics are `$ref` links to an internal host, not inline data.
  - `scoringPlays[]` lists the scoring events.
  - Player ids are in `boxscore.players[].statistics[].athletes[].athlete.id`.
  - Game state is in `header.competitions[0].status.type`
    (`name`, `state`, `completed`).
  - The top-level `broadcasts` was `[]`. The broadcast networks are in
    `header.competitions[0].broadcasts[].media.shortName`.
- **Post-game edits exist:** 2,367 of 2,656 plays (89%) carry a `modified`
  time more than one hour after their `wallclock`. ESPN edits plays after
  the fact. A historical capture shows only the final state, so it cannot
  show when or how a correction arrived.

## Evidence paths

- Receipt with commands, exits and the fixture inventory with hashes:
  [`P2-X05 receipt`](../../docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-X05/receipt.md)
- Capture log:
  [`capture-run.txt`](../../docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-X05/capture-run.txt)

## Capture command (CMD-ESPN-CAPTURE binding)

```
python3 spikes/sp5-espn-feed/capture.py capture --date 20261011 --date 20261012 --provenance historical
python3 spikes/sp5-espn-feed/capture.py verify
```

PR 2 (TNF 2026-10-15) captures the game repeatedly with
`--date 20261015 --event <id> --provenance live`. Each run appends the next
sequence file, so update timing is read from the successive `retrieved_at`
values and the play `wallclock`/`modified` fields.

## Limits and what waits for PR 2

- **Live update timing:** not measured. It needs in-progress polling during
  TNF 2026-10-15. Until then, feed_poll_interval (15 s) is unchecked.
- **Correction evidence:** this capture only infers corrections from
  `modified`. A correction seen as a later sequence file is pending PR 2.
- **Replay versus live:** replay fixtures prove parsing and validation only.
  They never stand in for live behaviour (RISK-AFC-P2-08).
- **Terms:** ESPN's JSON is unofficial. The fixtures hold raw bodies,
  including ESPN news, article and video metadata, as the contract requires.
  The repository is private. The terms question for public submission is
  owner action OA-6 (C3) and is still open.
- **Size:** the fixtures total about 9.7 MB. The largest file is 679,842
  bytes.

## developer_feedback

- X05-OBS-001: the summary `broadcasts` field is empty at the top level. The
  data is in `header.competitions[0].broadcasts`, and design.md cites the
  "ESPN summary broadcast field".
- X05-OBS-002: ESPN edits most plays after the game, and `modified` has only
  minute precision. Correction detection needs a live sequence; it cannot be
  derived from a final snapshot.
