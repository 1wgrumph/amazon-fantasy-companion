---
type: evidence
title: P2-X05 PR 1 receipt (SP-5 ESPN feed, historical capture)
okf_status: draft
tags: [P2-X05, SP-5, espn, fixtures]
---

# P2-X05 PR 1 receipt

Slice P2-X05, PR 1 of 2 (CP-X05-HIST), issue #27, milestone M04. Baseline
origin/main 75afca0. Route Claude Code / Claude Opus 5.5 / medium.

## Commands and exits

Commands run from the repository root unless noted. Logs are next to this file,
with home paths replaced by `$HOME`.

| Command id | Command | Exit | Log |
|---|---|---|---|
| CMD-ESPN-CAPTURE | `python3 spikes/sp5-espn-feed/capture.py capture --date 20261011 --date 20261012 --provenance historical` | 0 | [capture-run.txt](capture-run.txt) |
| (tool tests) | `cd spikes/sp5-espn-feed && python3 -m unittest -v test_capture` | 0 (10 tests) | [unittest.txt](unittest.txt) |
| CMD-FIXTURE-INDEX-CHECK (step 1-2) | `python3 spikes/sp5-espn-feed/capture.py verify` | 0 | [verify.txt](verify.txt) |
| CMD-GATE-ALL | `bash tools/ci/gate.sh` | 0 | [gate.txt](gate.txt) |

The ESPN requests were 16 public GETs to `site.api.espn.com` with no auth,
spaced at least 1 s apart: 2 scoreboards and 14 summaries. Three probe GETs
(2 scoreboards and 1 summary) ran earlier at 2026-10-14T14:47Z to confirm the
endpoints. Their bodies are not committed.

Negative case: malformed JSON is rejected with a `CaptureError` and nothing
is written (`test_malformed_json_is_rejected_and_nothing_written`). The CLI
exits 1 (`test_cli_rejects_malformed_feed_with_exit_1`). A scratch mutant
that let unparseable bodies through failed exactly those 2 tests, and the
candidate passes them.

CMD-FIXTURE-INDEX-CHECK step 3 (append-only against prior landed fixtures)
has nothing to compare: this PR adds the first fixtures. CMD-VERDICT-CHECK
(`git show <sha>:spikes/sp5-espn-feed/VERDICT.md`) runs on the commit; the
author return records the result.

## Fixture inventory

The capture ran with 14 games and 28 raw files, all `provenance:
historical-replay` and all games `STATUS_FINAL`. Each sha256 below was
recomputed from the file and matches `index.json`.

| Game id | File | Endpoint | Bytes | sha256 (recomputed = index) | retrieved_at | HTTP | provenance |
|---|---|---|---|---|---|---|---|
| 401872981 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872981 | 001-summary.json | summary | 597774 | `b067f153ddd2b8134a4f7c5b295093a1ac516303908f7cc55fdef6a94221297b` | 2026-10-14T14:48:45Z | 200 | historical-replay |
| 401872982 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872982 | 001-summary.json | summary | 577372 | `bbf6213a19cd0f430c5dbb2294fdb3b1f1eae345eef992a2c7d7717fac374203` | 2026-10-14T14:48:49Z | 200 | historical-replay |
| 401872983 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872983 | 001-summary.json | summary | 624582 | `41e936830c8c8484cf9bef33ae629a945e2e91017f76aec8a2d00fe261151002` | 2026-10-14T14:48:53Z | 200 | historical-replay |
| 401872984 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872984 | 001-summary.json | summary | 543171 | `3c3894ab78e1ec01be1180dfb28e65dff00acf21ce7d5cc5e8e7343f9491777c` | 2026-10-14T14:48:48Z | 200 | historical-replay |
| 401872985 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872985 | 001-summary.json | summary | 573304 | `557e309f20e5d4f6345df52022a3cd375a47a5dfa8cc0835794319c77c357e9c` | 2026-10-14T14:48:54Z | 200 | historical-replay |
| 401872986 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872986 | 001-summary.json | summary | 584777 | `ddf12eb8d097a8978514872434a4f0bd6d25a3eaa4d38f50cb41bd39ad197300` | 2026-10-14T14:48:50Z | 200 | historical-replay |
| 401872987 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872987 | 001-summary.json | summary | 530832 | `8298fe380e65ef2ff7a48ebb24470e7f0af7485ec877136e24d143e29cb48bdf` | 2026-10-14T14:48:52Z | 200 | historical-replay |
| 401872988 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872988 | 001-summary.json | summary | 651500 | `40b4a69301fa5bcbaa0421149e6dae3b48f9cf566069b6c6ac8aca01122e4971` | 2026-10-14T14:48:56Z | 200 | historical-replay |
| 401872989 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872989 | 001-summary.json | summary | 601548 | `384fd865f6e2a3b04cebdfefcff7c7fd8976fdd8c5d433b91a3c16eea592f987` | 2026-10-14T14:48:57Z | 200 | historical-replay |
| 401872990 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872990 | 001-summary.json | summary | 587474 | `de1a43c2d8492c18262ddd06a1dbb70d6eeaf00a8a11a689f1e6224eaa718cf2` | 2026-10-14T14:48:46Z | 200 | historical-replay |
| 401872991 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872991 | 001-summary.json | summary | 609978 | `35f8dc1792ec7fd12f3ea4eafcff60915e8450d00f3bba373d375734d31acfdc` | 2026-10-14T14:48:58Z | 200 | historical-replay |
| 401872992 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872992 | 001-summary.json | summary | 591538 | `8fc6c1e7529afb6956f3cf7b099cdb0f0c8c95de808efd8be8e5bfc0506ff415` | 2026-10-14T14:49:00Z | 200 | historical-replay |
| 401872993 | 001-scoreboard.json | scoreboard | 117614 | `ceff06301077135ee734f8e0cde0c5cd4c7f0367d606ab11fbd5fc097adb95e8` | 2026-10-14T14:48:44Z | 200 | historical-replay |
| 401872993 | 001-summary.json | summary | 612319 | `7c90bc1c2263d54944c2508a2ec778adcc8cf7e7e4c75577d615c756d427e71c` | 2026-10-14T14:49:01Z | 200 | historical-replay |
| 401872994 | 001-scoreboard.json | scoreboard | 23199 | `49bad06c9ea7198e35b99c50e2233999e3dc742e78fbe86fd92c168543a036de` | 2026-10-14T14:49:02Z | 200 | historical-replay |
| 401872994 | 001-summary.json | summary | 679842 | `50b2f2ddbb6adabc2ccad1c65fcefae2da85450e460af6a999c4613f2e143811` | 2026-10-14T14:49:03Z | 200 | historical-replay |

## Repair round 1: F1–F5 and permissions advisory (2026-10-14)

Author deterministic outcome: PASS / CANDIDATE_READY. This is the single
parent-authorized repair of P2-X05 PR 1, after REPAIR_REQUIRED. Route:
Bug-triager Implementer, Codex CLI / GPT-6.1 Sol / high; profile bug-triager.
Packet baseline: `3ab96da2e34f18c635a8a6c21248ee8b68a95746`; repair commit:
`53a71f45b48aab1342fa69cd1f90f61c08e4989c`. Worktree `$HOME/alphazede/worktrees/amazon-fantasy-companion-p2-x05`,
branch `afc/p2-x05`; identity checked before commit. Writes are confined to
`spikes/sp5-espn-feed/` and this P2-X05 evidence directory. No network requests,
branch changes, pushes or PR actions were made in this repair.

Next action: commit this receipt after the immutable repair-commit verdict
readback below, then return to the parent for landing. The follow-up changes
only this receipt; the verified tool, tests and verdict remain byte-identical.
BRAN: unavailable (no native policy); ordinary repository discovery used.
The supplied packet is the repair authority; Lifecycle control state is owned
by the parent and was not edited here. No new independent review or assurance
round was started. OCR belongs to the already-completed independent review;
this receipt is author verification only. Reverify: not applicable — Python
source and retained JSON bodies, no compiled-binary claim.

### Finding, fix, test and evidence

All regression test names below are in `test_capture.CaptureTest`.
Origin for F1/F2 is P2-X05 PR 1: external feed input crossed the spike tool's
trust boundary. Redirects and non-dict shapes escaped because the original
tests omitted them. The new offline cases are the prevention checks; the
host allowlist, bounded read, size validation and JSON validation remain.

| Finding | Fix | Test / inspection | Evidence |
|---|---|---|---|
| F1 | Disable redirects with `HTTPRedirectHandler.redirect_request` returning `None`; reject a response whose scheme or host differs from the request before reading its body. | `test_http_get_rejects_302_without_following_redirect`, `test_http_get_checks_response_scheme_and_host`; positive control `test_http_get_accepts_same_origin_response`. | [Baseline red](repair-red.txt): missing CaptureError; [candidate green](repair-green.txt): all pass. The redirect case uses urllib's real opener, redirect handler and error processor with an in-memory 302 and Location header; only HTTPS/HTTP transport is replaced, so no network is possible. |
| F2 | Use strict `\A`/`\Z` ID/date anchors; reject non-dict events and status values; remove `event.get` from exception handling; report non-dict index headers and file entries without crashing. | `test_non_object_event_is_rejected`, `test_non_object_status_type_is_rejected`, `test_event_state_rejects_non_object_values`, `test_event_id_with_trailing_newline_is_rejected`, `test_date_with_trailing_newline_is_rejected_before_fetch`, `test_verify_reports_non_object_index_header`, `test_verify_reports_non_object_file_entries`. | [Baseline red](repair-red.txt): AttributeError / missing CaptureError; [candidate green](repair-green.txt): same test IDs pass. Covers events `[1]`, status.type `"x"`, id `"101\n"`, date newline, index `[]`, and non-dict file entries. |
| F3 | Summary size range is now 530,832 to 679,842 bytes each. | Inspect committed summary index entries: min 530832, max 679842. | Existing fixture inventory above and immutable verdict readback below; no fixture changes. |
| F4 | Both HTTP header observations are labeled “observed during the 2026-10-14 probe, not retained”. | Inspect both route rows; no claim of retained header evidence and no recapture. | Immutable verdict readback below. |
| F5 | Run CMD-VERDICT-CHECK against the immutable repaired commit; retain its full output and exit. | `git show 53a71f45b48aab1342fa69cd1f90f61c08e4989c:spikes/sp5-espn-feed/VERDICT.md`; required fields and PARTIAL limitations inspected below. | Full output below, exit 0. Merge readback remains a parent landing obligation; this is the authorized author candidate check. |
| Permissions advisory | Chmod the temporary file to `0o644 & ~umask` before replace. | `test_atomic_write_uses_readable_permissions_subject_to_umask`: with umask 0027 the result is 0640 with unchanged body bytes. | [Baseline red](repair-red.txt): 0600 differs from 0640; [candidate green](repair-green.txt): passes. |

### Repair commands and exit codes

`PYTHONDONTWRITEBYTECODE=1` was set for tests/gates to prevent untracked caches.
`UV_OFFLINE=1` was set for the gates to forbid dependency network requests.

| Command | Exit | Result / evidence |
|---|---|---|
| Inline Python baseline runner: load `git show 3ab96da:spikes/sp5-espn-feed/capture.py` into module `capture`, then run the ten new regression IDs listed below | 1 (expected red) | [repair-red.txt](repair-red.txt): 10 tests, 6 failures and 8 errors including subtests. |
| `cd spikes/sp5-espn-feed && python3 -m unittest -v test_capture` | 0 | [repair-green.txt](repair-green.txt): all 21 tests pass, including the same ten regression IDs. |
| `python3 spikes/sp5-espn-feed/capture.py verify` | 0 | [repair-verify.txt](repair-verify.txt): `verify: OK`. |
| `git diff --stat 3ab96da -- backend/fixtures/replay` | 0 | [repair-fixture-diff.txt](repair-fixture-diff.txt): empty diff. |
| `PATH=$HOME/.local/share/afc-tools/backend-tests/bin:$PATH bash tools/ci/gate.sh` | 0 | [repair-gate.txt](repair-gate.txt): all areas PASS; 61 hygiene tests and 158 backend tests. |
| First `git commit` attempt with hooks enabled | 1 | The hook caught trailing whitespace emitted by unittest in the new untracked red log (lines 3, 8, 13). Trimmed trailing whitespace only; preserved result content. No commit was created by that attempt. |
| Repair `git commit` retry with Codex author/committer environment, hooks enabled | 0 | `53a71f45b48aab1342fa69cd1f90f61c08e4989c`; docs, hygiene and backend hook checks pass. No Co-Authored-By. |
| CMD-VERDICT-CHECK, immutable repaired commit binding | 0 | Full output below; identical to working verdict. |

The gate's deliberate negative-test diagnostics (`fatal: not a git repository`,
mutation/coverage adapter GAP samples) are expected test inputs; both suites
and every gate area pass. Existing botocore UTC deprecation warnings remain.
No engine/server/browser starts in the new regression tests; their resource
group is none, and the full spike suite took 0.021 seconds. No dependencies
were added. Logs normalize private root/home paths and trailing whitespace.

Candidate source bindings (unchanged by this receipt-only follow-up):

- `spikes/sp5-espn-feed/capture.py` sha256: `45b21bbe646eb1575d41e78effc5859e7bc86b801fb4e6749e60a1904f9b2729`
- `spikes/sp5-espn-feed/test_capture.py` sha256: `80fc95cacdcc21352ca3a08bb17900d3705e61dde01a4953606db4b20d231868`

### Baseline red runner reproduction

The source is loaded in memory from the pinned commit, without checkout or
fixture mutation. Use the current `test_capture.py` with this exact test set:

```python
import subprocess
import sys
import types
import unittest
from pathlib import Path
baseline = '3ab96da2e34f18c635a8a6c21248ee8b68a95746'
print('Baseline:', baseline, flush=True)
source = subprocess.check_output(['git', 'show', baseline + ':spikes/sp5-espn-feed/capture.py'])
module = types.ModuleType('capture')
exec(compile(source, 'baseline/capture.py', 'exec'), module.__dict__)
sys.modules['capture'] = module
sys.path.insert(0, str(Path('spikes/sp5-espn-feed').resolve()))
tests = [
    'test_http_get_rejects_302_without_following_redirect',
    'test_http_get_checks_response_scheme_and_host',
    'test_non_object_event_is_rejected',
    'test_non_object_status_type_is_rejected',
    'test_event_state_rejects_non_object_values',
    'test_event_id_with_trailing_newline_is_rejected',
    'test_date_with_trailing_newline_is_rejected_before_fetch',
    'test_verify_reports_non_object_index_header',
    'test_verify_reports_non_object_file_entries',
    'test_atomic_write_uses_readable_permissions_subject_to_umask',
]
suite = unittest.defaultTestLoader.loadTestsFromNames(['test_capture.CaptureTest.' + name for name in tests])
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
```

### CMD-VERDICT-CHECK inspection

Required fields: spike SP-5, slice P2-X05, verdict PARTIAL, device none,
started_at/ended_at, first_install_at not applicable, unblocks AFC-PR-064
and AFC-PR-013, conditional none — all present. Capture interval
14:47:19Z–14:55:01Z on 2026-10-14 is historical backend evidence; no hardware
proof or live timing is claimed. Both route URLs target the allowlisted ESPN host; retained capture and
fixture evidence and receipt links resolve locally. ESPN has no published contract;
the header observations are expressly not retained. The interim PARTIAL blocks
live timing/feed_poll_interval and correction behaviour of AFC-PR-012;
TNF 2026-10-15 live capture and later-sequence correction evidence remain PR 2.
The 15 s interval is unchecked, and owner terms/public-submission action OA-6
(C3) remains open. This repair does not close the whole spike or issue #27.

Command: `git show 53a71f45b48aab1342fa69cd1f90f61c08e4989c:spikes/sp5-espn-feed/VERDICT.md`

Exit code: `0`

Full command output:

```text
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
```
