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
