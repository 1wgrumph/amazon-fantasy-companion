# M14 Stage 3 attempt 2 — GS @ LAL live refresh after the panel revision fix

Outcome: PASS. Live panel values refresh on the VVD without a relaunch.

Observer: Claude Code (Test Implementer, M14 frozen route), 2026-10-22.
Game: ESPN 401909092, GS @ LAL, tip 02:00Z. Backend: afc-dev at `8fed6f5`
(PR #155, deployed by the M03–M13 orchestrator). App: the attempt 1 `.vpkg`
(x86_64 `fb16c460…`), unchanged. The API kept the same panel fields;
only the revision values grew larger (about 7.5e11, inside the JavaScript
safe-integer range).

## Setup

`vega-app/vvd-checks/put-lineup.sh` replaced attempt 1's lineup for
`afc-vega-vvd-synthetic`, `vvd-league/vvd-team`, sport nba. The starters
were Curry G, Doncic G, Butler F, Green F and Kessler C
([lineup.json](lineup.json)). All calls returned 200 ([api/](api/)).
ESPN lists Jimmy Butler III as Out (injured). His row stays "statistics
unavailable", so the team total is "Unavailable" all game. The verifier
therefore compares row values when the total is null. Attempt 1's log has
numeric totals and still fails on the same checks
([verify-panel-live.txt](verify-panel-live.txt)).
`poll-live-api.py` logged the panel every 30 s from 02:37Z to 03:48Z
([api-poll.jsonl](api-poll.jsonl)).

## Live refresh (objective)

[verify-panel-live.txt](verify-panel-live.txt): all 6 checks PASS, exit 0,
on the new log. Attempt 1's log stays at exit 1.

The backend revision advanced on every change of values or `asOf` (for
example 02:40:54Z, `…235520` → `…236032`, Doncic 15.7 → 14.7). The device
showed each new value at its next 60 s capture, and the stale label reset
each time:

| Session | Capture (UTC) | Shown | Stale |
|---|---|---|---|
| A1 (late Q1–Q2) | [02:40:15](A1/a1-02.png) | Doncic 15.7, clock 2:50 1st | 283 s |
| A1 | [02:41:15](A1/a1-03.png) | Doncic 14.7, clock 1:55 1st | 82 s |
| A1 | [02:49:16](A1/a1-11.png) → [02:52:16](A1/a1-14.png) | Curry 17.2 → 22.2, Kessler 9.2 → 15.6 | 99 s → 68 s |
| A2 (Q3) | [03:35:57](A2/a2-01.png) → [03:43:57](A2/a2-09.png) | Doncic 32.2 → 41.4, Kessler 22.2 → 30.6 | 115 s → 79 s, and no label at [03:40:57](A2/a2-06.png) |

The longest stale labels (265 s to 285 s) appeared only while the backend's
own `asOf` stood still (ESPN gaps around quarter breaks and timeouts). The
ages shown broadly follow the backend's `asOf`; capture and display timing
uncertainty prevents a one-second accuracy claim.

## R-3 fault (repeated once)

From 03:44:57 to 03:46:37 the guest forwarder refused afc-dev (732
refusals). The app logged "Could not fetch url" ([log](app-log-excerpt.txt)).
It kept 41.4 and the other values, and the stale label grew 117 s → 157 s
→ 187 s → 217 s ([A2 10–13](A2/)). After the fault cleared, the app
reconnected (two forwarded connections, 13.5 kB down). The shown age (263 s)
then matched the backend's unchanged `asOf` of 03:42:59; new data arrived at
03:47:49, after the session ended.

## Containment

Both sessions passed the six proofs, with no abort
([containment-proofs.txt](containment-proofs.txt)). CONNECTs went only to
afc-dev and the existing SDK allowlist; the only DENY was the expected
`example.com` canary ([proxy-connects.txt](proxy-connects.txt)). The VVD
was stopped after each session ([A1](A1/steps.txt), [A2](A2/steps.txt)).

## Not observed

- The new pregame start time in `gameStatus`: the game was already live
  when the lineup was written. The app renders `gameStatus` as plain text.
- Alerts and Watch: unchanged from attempt 1; 0 alerts on every poll.

## Frictions

- An injured starter makes the team total unavailable for the whole game.
- ESPN `asOf` gaps of 3–5 minutes show up as long stale labels even when
  refresh works.
- There is no OCR, so values are read visually into
  [device-readings.json](device-readings.json).
