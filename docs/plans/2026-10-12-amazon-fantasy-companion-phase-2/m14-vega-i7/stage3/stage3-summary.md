# M14 Stage 3 — live NBA game on the VVD (P2-V01, attempt 1)

Outcome: REPAIRABLE_FAILURE. The panel never refreshes its values during a
live game, because the backend serves new values under an unchanged
revision and the app drops equal revisions.

Observer: Claude Code (Test Implementer, M14 frozen route), 2026-10-21/22.
Game: ESPN 401909834, ATL @ ORL, tip 2026-10-21T23:00Z. It was observed on
the VVD from 23:16Z (1st quarter, 11:27) to 00:02Z (2nd quarter, 7:08).

## Setup

- Lineup: `PUT /v1/lineup/manual` for `afc-vega-vvd-synthetic`, sport nba,
  league `vvd-league`, team `vvd-team`. Starters: Bane G, Daniels G,
  Banchero F, Carter C, Alexander-Walker UTIL ([lineup.json](lineup.json)).
  The profile's teamLeague was set with `PUT /v1/profile`. Both returned
  200, and the panel read back 5 rows with `nbaPoints` / `nba`
  ([api/](api/)). The check is
  `vega-app/vvd-checks/put-lineup.sh`. It links a workstation session
  through `confirm-link.sh` and keeps the token private.
- App: built in the sandbox from `a89b2b2` with the afc-dev ApiUrl as the
  only injected value. The x86_64 `.vpkg` sha256 is in the
  [receipt](stage3-receipt.json). The VVD was linked with code `A8LVHQZB`
  ([confirm](device-confirm/)).
- Backend log: `vega-app/vvd-checks/poll-live-api.py` read the panel,
  alerts and ESPN status every 60 s with read-only GETs
  ([api-poll.jsonl](api-poll.jsonl)).
- i7 runtime: the recreated sandbox needed three repairs before a proof
  could pass. These are restoring the `aa-exec` user-namespace wrapper and
  the work-root path in `run.py`, copying the workstation `node` (as in
  Stage 1) and starting Xvfb `:91`. A fault switch was also added to the
  guest forwarder in `outer.py` for R-3. Diffs and sha256 values are in
  [runtime-change.diff](runtime-change.diff).

## Verdicts

| Feature | Verdict | Evidence |
|---|---|---|
| Panel populated, NBA label | PASS | [pre-game](S1/s1-04-panel.png), [Q1](L1/l1-01-live.png), [Q2](L3/l3-01-q2.png): "Team/league: vvd-league/vvd-team", "NBA · Points", 5 starters, total |
| Live values refreshing | **FAIL (defect)** | [verify-panel-live.txt](verify-panel-live.txt) exit 1; [L1](L1/), [L2](L2/), [L3](L3/) |
| R-1 saved settings reach the live controller | PASS | Saving "Panel visible: off" hid the panel and saving "on" restored it ([S1](S1/)). A profile Save in a live game showed current values ([L2 05](L2/l2-05-after-save.png)). |
| R-2 no overlapping refreshes | not observable on the VVD | `api_timeout` is 10 s and the refresh interval is 30 s, so a request never outlives an interval. Coverage stays with the source regression. |
| R-3 failed refresh re-renders stale | PASS | While the forwarder refused afc-dev, the app logged fetch errors ([log](app-log-excerpt.txt)). The held value re-rendered at stale 599 s → 639 s → 669 s → 699 s ([L1 09–12](L1/)). |
| Alerts | limited (backend/data) | 0 alerts for the profile on every in-game poll (HTTP 200). NBA ingest stores only boxscore statistics and creates no game events, so the alert pipeline has nothing to evaluate. The in-app banner renders at the top of the screen; the live captures show the panel at the bottom, so its absence on the VVD rests on the backend's 0 alerts. |
| Watch | limited (backend/data); not exercised | Watch is reachable only from an alert banner (`App.tsx`), and no alert exists. The panel has no Watch entry. No `POST /v1/routing-outcome` was sent and no playback is claimed. |

## Defect: live panel values freeze within a controller lifetime (red evidence)

- Expected: values refresh during the game (AFC-PR-039..-048; DES-AFC-P2-PANELSVC).
- Observed: the backend total moved 4.5 → 6.5 → 12.0 → … → 36.4 in the
  first quarter and 54.6 → 70.6 in the second. Each VVD capture kept the
  first value it fetched, with a growing stale label, for up to 13 minutes.
  The values changed only when a new controller was created, at launch, a
  profile Save or a relaunch (L2: 36.4, then 46.2, then 48.2).
- Cause, at code level: `panel.snapshot` derives values at read time. The
  revision advances only through `project()` or a lineup change, and the
  NBA ingest never calls `project()`. The API log shows revision 960 for 12
  different totals, and 1088 for the next 11. `PanelController.onFetched`
  (`vega-app/src/panel/panel.ts`) ignores `snapshot.revision <=
  previous.revision`.
- Class: product defect at the backend/app revision contract, in the NBA
  path. The verifier's backend check fails on the API log alone. Which side
  to fix is a triage decision. The Fire TV panel is not checked here.

## Synthetic identifiers and afc-dev writes

Profile `afc-vega-vvd-synthetic` only. The writes were 1 × `POST /v1/link`
and `POST /v1/link/confirm` from the workstation, the app's `POST /v1/link`
plus a confirm for code `A8LVHQZB`, 1 × `PUT /v1/lineup/manual`, 1 ×
`PUT /v1/profile` from the workstation, and 2 × app `PUT /v1/profile`
(the R-1 off/on) plus 1 in L2. No other profile, league, team or endpoint
was written.

## Containment

All sandbox runs after the runtime repairs passed the six proofs, and no
run aborted ([containment-proofs.txt](containment-proofs.txt)). Every
CONNECT went to afc-dev or an existing SDK allowlist entry. The only DENY
was the expected `example.com` canary during the proofs
([proxy-connects.txt](proxy-connects.txt)). The VVD was stopped at the end
of every session ([steps](L3/steps.txt)).

## Frictions

- The sandbox's 1200 s wall clock limits each session to about 18 minutes
  of device time, so a game needs several boots.
- With no OCR, values are read visually from the captures into
  [device-readings.json](device-readings.json).
- When the forwarder refuses connections, the app retries about 7 times per
  second (740 refusals in 100 s).

## Lesson learned (for attempt 2, GS @ LAL 02:00Z)

Cause: the setup and harness worked. The failure is in the product, so
another observation pass would show the same freeze. For attempt 2, keep
the same lineup flow and drivers. Run one L1-style session (Q1) and one
Q2 session. Run them only after a fix that advances the panel revision
when statistics change (or relaxes the app's equal-revision drop) is
deployed to afc-dev and built into a new `.vpkg`. Without that fix,
attempt 2 is only a re-run of this red result. Alerts and Watch stay
limited until NBA ingest emits game events.
