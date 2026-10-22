# NBA panel on the Fire TV stick, 2026-10-21

Observer: Claude Code (NBA watcher session, M16 #137), on the AFTKM Fire TV
stick. Games: MIN@MIA (tip 23:30Z) and GS@LAL (tip 02:00Z). All times UTC.
Every image here is AFC UI only, with no broadcast, provider or title art.
The `SHA256SUMS` file lists each image hash.

## Build and backend

- APK: debug build from commit `f05bf4b` (origin/main at or after `7643079`),
  default properties apart from the afc-dev API base URL. The APK sha256 is
  `0a9bc06b019252278719c2a3bae557ae2d00d6b04f487eae81c692cf53342d78`, checked
  against the copy installed on the stick.
- Backend: afc-dev `a82157f` for captures up to 02:16Z, then `8fed6f5`
  (PR #155, panel stats revision fix and NBA pregame start time) from 02:35Z.
- Profile `afc-device1-synthetic`, manual lineup, no Yahoo data.

## Lineups used

| Version | Written | Starters | Why |
|---|---|---|---|
| v10 | 2026-10-21 13:39Z | 10 (demo-lineup.json starters) | The handoff demo lineup |
| v11 | 2026-10-21 23:49Z | 5: Curry, Edwards, Antetokounmpo, Doncic, Adebayo | Orchestrator option (b): only players in MIN@MIA or GS@LAL, so the team total can resolve |
| v12 | 2026-10-22 02:40Z | none (content-empty) | Restore to the pre-session state |

Both lineups pair with `nba-demo/afc-nba`, and the profile `teamLeague` was set
to that pair for the session. Lineups were written with `store.put_lineup`
under the deploy profile. This lane did not exercise the
`PUT /v1/lineup/manual` route; the route smoke from other lanes covers it.

## Acceptance and evidence

| # | Acceptance | Evidence | Result |
|---|---|---|---|
| 1 | APK from main, sha256 and commit recorded | Build section above | Met |
| 2 | Header, non-null rows, team total, freshness label, one capture per game, points changing | [MIN@MIA Q1](20261021T234714Z-panel-min-mia-q1-top.png), [points changed](20261021T235635Z-panel-min-mia-tonight-lineup-points-changed.png), [MIN@MIA Q4](20261022T021602Z-panel-min-mia-q4-after-relaunch.png), [GS@LAL Q1](20261022T023724Z-panel-gs-lal-q1-auto-refresh-after-fix.png), [team total 179.5](20261022T023743Z-panel-team-total-resolved.png), [live refresh](20261022T024045Z-panel-gs-lal-live-refresh-fresh.png) | Met after PR #155 |
| 3 | Settings capture with NFL and NBA alert toggles | [Settings](20261021T134314Z-settings-sport-toggles.png) | Met |
| 4 | Watch outcome capture or a typed gap | [Focused row, no Watch control](20261021T234746Z-panel-min-mia-q1-row-focus-total.png) | Typed gap G1 |
| 5 | AFC UI only, each sha256 listed | `SHA256SUMS` | Met |
| 6 | Stick restored, lease released, lineup restored | Restore section below | Met |

Other frames: [pregame panel](20261021T133949Z-panel-pregame.png),
[freeze before the fix](20261022T001647Z-panel-min-mia-freeze-before-fix.png),
[team total pending GS@LAL](20261022T021614Z-panel-min-mia-q4-total-pending-gs-lal.png).

## Defect found and fixed during the session

At 23:56Z the TV showed MIN@MIA values from "9:20 - 1st" with a growing stale
label, while PlayerStats matched ESPN at "5:59 - 1st". At 00:16Z the label had
reached 1744 s. Cause: the panel revision rose only on game-event projections,
lineup or profile changes (`backend/src/panel/__init__.py`), and NBA ingest
stores statistics without game events. The TV drops snapshots whose revision is
not higher than the one it holds (`tv-app/.../panel/PanelModel.kt`).

The bug-triager route fixed it in PR #155. After the deploy at 02:35Z, the same
app instance showed GS@LAL values with no relaunch, and at 02:40Z it moved from
"2:50 - 1st" to "1:55 - 1st" with no stale label. Before the fix, the 02:16Z
frames needed an app force-stop and relaunch to load a fresh snapshot.

## Typed gaps

- G1, Watch not reachable for NBA: Watch exists only on alerts, panel rows have
  no Watch action, and no NBA alert was generated on 2026-10-21. NBA alerts are
  added after this session in PR #156 (merged 2026-10-22), so a later run can test an NBA alert Watch.
- G2, YouTube TV route needs access settings: `installedPackages` is absent for
  this profile, and the stick reports "Installed-app detection is not supported
  on this device". An NBA Watch would need `appOverrides` or `confirmedAccess`
  before it could resolve to YouTube TV. No override was set.
- G3, team total fails closed: the team total stays Unavailable while any
  starter has no statistics. This is intended, but a real lineup with
  non-playing starters shows Unavailable all night (v10 did).

## Restore

Readbacks at 2026-10-22 02:41Z, compared field by field with the pre-session
readbacks (lineup v8 content-empty, profile revision 8):

- Lineup: v12, content-empty. Only `lineupVersion` and `updatedAt` differ.
- Profile: revision 10, `teamLeague` null. Only `revision` and `updatedAt`
  differ; every setting matches, including panel visible on.
- Stick: on the Fire TV home screen. The only AFC notification is the ongoing
  alert-monitoring service status, with no alert notifications. This lane left
  no temporary packages. Earlier, at 14:32Z, it removed a test package left by
  a previous review session (orchestrator-approved).
- Lease: released at 02:42Z.
- YouTube TV was opened at the owner's request to view the game. The existing
  profile was selected and no account setting changed. Those frames stay
  private.

## Verification

Run by the NBA watcher session on the evidence branch:

| Command | Exit |
|---|---|
| `bash tools/ci/gate.sh hygiene` (includes the provider-art check) | 0 |
| `bash tools/ci/gate.sh docs` | 0 |
| `AFC_DEPLOYED_API_URL=<ApiUrl> python3.12 -m pytest backend/tests/deployed -k link`, in the backend test environment, 2026-10-22 about 11:51Z: 4 passed | 0 |
