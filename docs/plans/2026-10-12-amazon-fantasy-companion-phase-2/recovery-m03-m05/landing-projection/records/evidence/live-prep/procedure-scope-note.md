# R-T-LIVE-PREP — future live procedure scope note (historical/replay provenance only)

This note closes no live proof row. All outputs in this folder are `historical-replay`.

## X05 future live capture (not executed here)
- Bound command from `seit.json` (private frozen source reference) `procedures_and_commands[CMD-ESPN-CAPTURE].recovery_binding`: `python3 spikes/sp5-espn-feed/capture.py capture --date 20261022 --event 401873010 --provenance live`, then `capture.py verify`. Tool tests: `(cd spikes/sp5-espn-feed && python3 -m unittest -v test_capture)`.
- Require requalification at dispatch: re-confirm ESPN scoreboard date for the event (kickoff 2026-10-23T00:15Z per landed receipt; scoreboard date may differ), event id, in-progress state, and live-window lease. Never infer live evidence from date alone. Do not execute this live capture in R-T-LIVE-PREP.
- Each live run appends the next sequence; repeat at a bounded interval during the window only under R-T-LIVE-CAPTURE authority.

## X03 future amendment — frozen scope
- Limited to the Prime Video entry and verdict only (per `implementation.json` (private frozen source reference) R-T-LIVE-PREP stop condition): the Prime Video `fire_os` registry entry / `verified_outcome` and the SP-3 verdict update for the live TNF `gameOpened` check.
- No other provider entries, routes, or verdicts may change in that amendment. Absent providers (ESPN, DirecTV Stream, YouTube TV, local broadcast) and all `vega` routes remain `REGISTRY_ROUTE_GAP` until separately proven.
- No live/device/Watch/Vega acceptance is claimed by this historical qualification.
