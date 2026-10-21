# M14 — "Panel unavailable" on the VVD (P2-V01 lineup panel)

Outcome: PASS (classified). Classification: **app defect**.

Observer: Claude Code (Test Implementer, M14 frozen route), 2026-10-21 UTC
(backend `updatedAt` 03:57:03Z). Attempt 1 of 3.

## What the app receives

`vega-app/vvd-checks/probe-panel.py` linked profile `afc-vega-vvd-synthetic`
from the workstation (`POST /v1/link` 201, `POST /v1/link/confirm` 200,
`GET /v1/link` 200 linked) and held the session token in memory only.

| Call | Status | Body |
|---|---|---|
| `GET /v1/profile` | 200 | `teamLeague: null`, all `fantasySelections` empty, `panelPrefs.visible: true`, `scoringPreset: halfPpr` ([04](04-profile.json)) |
| `GET /v1/panel` (no query, as the app sends it) | 200 | `teamLeague: "unassigned/unassigned"`, `scoringBasis: "halfPpr"`, `rows: []`, total and progress null with reasons ([05](05-panel-no-teamleague.json)) |
| `GET /v1/panel?teamLeague=unassigned/unassigned` | 200 | Same state ([06](06-panel-teamleague-explicit.json)) |

The app sends no `teamLeague`. With `teamLeague: null` and no selections,
`App.tsx` `load()` builds `PanelController([], '', true)`, so
`controller.teamLeague` is `''` and `getPanel(undefined)` is called.

## Which rule rejects it

`vega-app/vvd-checks/__tests__/decode-panel-live.test.ts` replays the
recorded bodies through the app's own modules, unchanged
([decode-harness.txt](decode-harness.txt), exit 0):

| Body | `decodeEnvelope` | `decodePanel` | Team/league match | Snapshot held |
|---|---|---|---|---|
| 05, controller `''` (the VVD case) | accepts | accepts | `"unassigned/unassigned"` ≠ `''` | **no** |
| 06, controller `unassigned/unassigned` | accepts | accepts | equal | yes |

No `decodePanel` rule rejects the body. The rejection is
`PanelController.onFetched` (`vega-app/src/panel/panel.ts`):
`if (snapshot.teamLeague !== this.teamLeague) return PANEL_DELTA_NONE;`.
`controller.snapshot` stays null, so `PanelSection` renders
"Panel unavailable". `needsFetch` also stays true, so the app repeats
`GET /v1/panel` every second while the panel is visible.

The backend behaves as `snapshot()` documents: it picks the team/league
itself when the query omits it.

## Proposed minimal fix (separate packet)

App side, `vega-app/src/panel/panel.ts` `PanelController.onFetched`: when
the controller has no team/league (`''`), adopt the server's
`snapshot.teamLeague` instead of dropping the snapshot. A regression test
would feed the 05 body with controller `([], '')` and expect a held
snapshot. Changing the backend to echo `''` is not proposed: the server
default is part of the panel contract.

## Remaining risks

- Rows, totals and progress stay empty for this profile: no public API
  writes a lineup (Stage 2c, backend/data limit).
- The probe made a new link for the synthetic profile; if a new link
  supersedes an older session, the VVD's stored token may need a relink.
- The profile's `updatedAt` is 03:35:47Z, after the Stage 2c save
  (about 02:55Z). This probe did not write the profile; the later write is
  not explained here.
- Not rechecked on the VVD; the app's request path is derived from code.
