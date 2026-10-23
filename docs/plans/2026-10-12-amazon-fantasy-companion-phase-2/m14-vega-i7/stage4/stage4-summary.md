# M14 Stage 4 — NBA alerts and Watch on the VVD during a live game (P2-V01, attempt 1)

Outcome: PASS. An NBA alert from #156 reached the VVD as the in-app banner.
Watch from that banner reported one routing outcome, and the panel kept
refreshing live.

Observer: Claude Code (Test Implementer, M14 frozen route), 2026-10-22.
Game: ESPN 401909093, CLE @ PHI, tip 23:00Z (ESPN went in progress at
23:14Z). Observed on the VVD from 23:15Z to 23:47Z (1st quarter). Backend:
afc-dev at `c12f3ac` (#156). App: built in the sandbox from this worktree
(`vega-app/src` unchanged since `a89b2b2`). The x86_64 `.vpkg` sha256 is in
the [receipt](stage4-receipt.json).

## Setup

- Lineup: `vega-app/vvd-checks/put-lineup.sh` replaced the Stage 3 lineup
  for `afc-vega-vvd-synthetic`, `vvd-league/vvd-team`, sport nba. The
  starters are Mitchell G, Harden G, Mobley C, Maxey G and Embiid C
  ([lineup.json](lineup.json)). All calls returned 200 ([api/](api/)).
- The profile's `alertTypes` was `["RedZone"]`, which gates out every NBA
  alert (PlayerScore). `put-lineup.sh` gained an optional alert-types
  argument; the same profile PUT wrote `["RedZone", "PlayerScore"]`
  (profile revision 8, presentation HeadsUp, no quiet hours or game-day
  periods, frequency 120 s).
- Cold start: the lineup was written and `poll-live-api.py` was polling at
  30 s from 20:36Z, before tip ([api-poll.jsonl](api-poll.jsonl)). The log
  now records each alert's id, type, game, event, starters and phrase.
- The sandbox was re-created before this run. The Stage 3 runtime change was
  re-applied and gave the same sha256 values (`run.py` `8c3aca75…`,
  `outer.py` `7a48b1fa…`, `node` `fde6a4bf…`). Xvfb `:91` was restarted.
  The VVD was linked with code `LXE4RY7C`
  ([confirm](device-confirm/), [linked screen](S1/s1-02-main.png),
  [pre-game panel](S1/s1-03-panel.png)).

## Verdicts

| Feature | Verdict | Evidence |
|---|---|---|
| Alerts | PASS | [verify-alerts-live.txt](verify-alerts-live.txt) exit 0. On the Stage 3 zero-alert log the same check exits 1 (fails closed). |
| Watch | PASS (`accessUnknown`, no playback) | [L2 03](L2/l2-03-watch-armed.png), [L2 04](L2/l2-04-watch-outcome.png) |
| Panel live | PASS | [verify-panel-live.txt](verify-panel-live.txt) exit 0, all 5 checks, R-3 included |

### Alerts

The backend emitted two PlayerScore alerts for game 401909093, both for
Donovan Mitchell:

| Alert (emittedAt) | Phrase | First in the API log | On the VVD |
|---|---|---|---|
| 23:20:45Z | +8.7 fantasy pts | 23:21:45Z | Banner on the app's first long poll after L2 launch, [23:25:49](L2/l2-01-launch.png) |
| 23:43:20Z | reaches 10 pts | 23:45:48Z | Delivered while the app was open in L3: [23:45:08](L3/l3-top-03.png) shows the first alert, [23:45:48](L3/l3-top-04.png) the new one |

The banner renders at the top of the main screen, directly under
"Profile/Settings". It shows "Score update", "Donovan Mitchell — <phrase>",
"Access: unknown" and the Watch and Dismiss buttons. The VVD shows the app
in a 960×540 area of the 1920×1080 root capture. The panel sits below the
profile controls, so the Stage 3 panel captures (scrolled down) never
showed this area.

### Watch

With Watch focused ([L2 02](L2/l2-02-focus.png)), the first press showed
"Press Watch again to switch apps." (switching confirmation on). The second
press showed "Watch: could not confirm the game is playing.", which the app
shows for `accessUnknown`. The alert's route has no verified
`platform_routes.vega` entry, so the launcher started nothing and reported
`accessUnknown` through `POST /v1/routing-outcome`. Watch was pressed only
for this one alert, so exactly one outcome was reported. The message held
unchanged to [23:32:48](L2/l2-top-10.png). The backend has no read-back for
stored outcomes, so the on-device message is the evidence. No playback is
claimed.

### Panel live

L2 scrolled to the panel at 23:34Z. The backend's `asOf` stood at 23:32:25
until 23:36:48, and the VVD held 42.9 with the stale label growing from
113 s to 278 s. It then showed 43.7 (stale 70 s) and 46.7 (stale 71 s) at
the next captures ([L2 p01–p06](L2/)). With the guest forwarder refusing
afc-dev (768 refusals), 46.7 held and the stale label grew 117 s → 147 s →
177 s ([p08–p10](L2/l2-p08-fault40.png)). After recovery it showed 144 s
([p11](L2/l2-p11-recovered.png)). Readings:
[device-readings.json](device-readings.json).

## Synthetic identifiers and afc-dev writes

Profile `afc-vega-vvd-synthetic` only. The writes were:

- 1 × `PUT /v1/lineup/manual`;
- 1 × `PUT /v1/profile` (teamLeague and alertTypes);
- the app's `POST /v1/link` and its confirm for code `LXE4RY7C`;
- the app's 1 × `POST /v1/routing-outcome`.

The workstation reused the Stage 3 session, so it made no new link. No
other profile, league, team or endpoint was written.

## Containment

All six sandbox runs passed the six proofs
([containment-proofs.txt](containment-proofs.txt)). Every CONNECT went to
afc-dev or an existing SDK allowlist entry. The only DENY was the expected
`example.com` canary ([proxy-connects.txt](proxy-connects.txt)). L2 and L3
stopped the VVD cleanly. L1 was killed by the wall clock without the stop
steps (see Frictions). The next session's start removed the stale locks.
No VVD process remained at the end.

## Frictions

- L1 ran from `work/stage4` and was killed at 300 s (`WALL_CLOCK_LIMIT`).
  Only `work/stage2c/drive-vvd.sh` is on the runtime's long-run list. L2
  and L3 ran the same driver from `work/stage2c` and got the 1200 s limit.
  L1 ended at 23:19:46, before the first alert existed, so no observation
  was lost.
- Alerts reached the API log 1 to 2.5 min after their `emittedAt`,
  which is the boxscore clock, not the delivery time.
- There is no OCR, so the banner, outcome and panel values were read
  visually into [alert-readings.json](alert-readings.json) and
  [device-readings.json](device-readings.json).

## Not observed

- A heads-up banner over provider playback (the VVD has no provider apps).
- Alerts for PHI starters. Before tip, their rows had no `gameStatus` while
  the CLE rows showed the tip time. In game, both teams had values.
