---
spike: SP-3
slice: P2-X03
verdict: PARTIAL
device:
  model: AFTKM
  fire_os: Fire OS 8.1.8.5 (RS8185/3891)
  android_release: "11"
  api_level: 30
started_at: 2026-10-16T20:00:12Z
ended_at: 2026-10-16T20:10:13Z
first_install_at: not applicable (SP-1 and SP-4 only)
unblocks: [AFC-PR-029, AFC-PR-030, AFC-PR-031, AFC-PR-048, AC-AFC-P2-SPIKE-03]
conditional: none
---

# SP-3 provider links: interim verdict (PR 1 of 2)

**Verdict: PARTIAL.** Desk evidence only. The live Prime Video Thursday Night
Football check is **pending** (PR 2; next TNF game 2026-10-22, Patriots at
Bears, ESPN event 401873010 — matchup and 2026-10-23T00:15Z kickoff per
`espn-summary-receipt.json` in this directory), so `gameOpened` is not
claimed for any provider.
ESPN, DirecTV Stream and YouTube TV are not installed on the stick (typed
gap, `appAbsent` observed), and local broadcast has no carrying app. This
interim verdict blocks only the still-unproven routes: the Prime Video
`gameOpened` route and every route of the absent providers plus all `vega`
routes (`REGISTRY_ROUTE_GAP`).

All observations below are in `device-log.txt` (this directory) with
screenshots under `evidence/visual/sp3-provider-links/`, each inspected for
account data before retention (none is shown).

## Routes tried

In spike order (AC-AFC-P2-SPIKE-03). `adb` is CMD-ADB-SCREENCAP /
Android developer docs, "Android Debug Bridge (adb)"
(https://developer.android.com/tools/adb); launches use `am start`
(Amazon Fire TV developer docs, "Install and Run Your App",
https://developer.amazon.com/docs/fire-tv/installing-and-running-your-app.html).
No spike APK was needed or installed.

### 1. Prime Video (`com.amazon.firebat`, system app, PVFTV-324.0104-L)

Documentation source: the app's own intent filters as reported by
`dumpsys package com.amazon.firebat` on the device (device-log.txt,
"Prime Video package identity"): `VIEW` over `https` for
`watch.amazon.com` / `app.primevideo.com` with paths `/search`, `/detail`,
`/landing` (plus `/collections`, `/settings`), `VIEW amzn://avod`,
`MAIN`+`LEANBACK_LAUNCHER`, and `com.amazon.firebat.action.YAC_LAUNCH`,
all on `com.amazon.pyrocore.IgnitionActivity`. No public Prime Video
deep-link document was found in the repo, so no URI form beyond these
filters was invented.

- Cold `MAIN`+`LAUNCHER` launch after `am force-stop`: exit 0, foreground
  `IgnitionActivity`, Prime Video home with a Continue watching row
  (signed in). Outcome `appHomeOpened`.
  Evidence: `evidence/visual/sp3-provider-links/prime-video-home.png`.
- `VIEW https://watch.amazon.com/search` with package
  `com.amazon.firebat`: exit 0, foreground `IgnitionActivity`, Prime Video
  search screen. Outcome `searchOpened`. This exact URI is the registered
  `fire_os` launch. Query parameters (`?query=…`, `?k=…`) were also tried
  and are ignored: the keyboard opens empty, so no `{channel}` or `{event}`
  placeholder is registered — none is documented.
  Evidence: `evidence/visual/sp3-provider-links/prime-video-search.png`.
- `VIEW amzn://avod` and action `com.amazon.firebat.action.YAC_LAUNCH`
  (package set, the exact form the TV Watch launcher builds for an
  `intent` launch): both exit 0, Prime Video home (`appHomeOpened`).
- Bare `android.intent.action.MAIN` with only the package set does not
  resolve ("unable to resolve Intent"): the `MAIN` filter requires the
  `LEANBACK_LAUNCHER` category, which the current Watch launcher does not
  add. A bare `MAIN` intent value must therefore not be registered.
- On-demand playback (desk evidence): selecting "Watch now" on the
  Included-with-Prime hero title started playback; the screencap is the
  black secure surface with an "Ad 0:35" overlay, and
  `dumpsys media_session` shows an active `com.amazon.firebat` session in
  `PlaybackState state=3` (STATE_PLAYING). The picture itself is not
  capturable (RISK-AFC-P2-09), only the playback state is evidenced.
  Evidence: `evidence/visual/sp3-provider-links/prime-video-ondemand-play.png`.
- Investigation result (review lead, not registered):
  `VIEW https://watch.amazon.com/detail?gti=<title GTI>` with package
  `com.amazon.firebat`, cold after `am force-stop`, with the public GTI of
  the 2026-10-15 TNF replay (`amzn1.dv.gti.0519bea8-4415-4b18-b309-d06ff66617cf`,
  ESPN event 401872995). Exit 0, foreground `IgnitionActivity`, logcat
  `[deeplink] Entering Rust NavigationGateway`. With no key input, the
  "Seahawks vs. Broncos" replay title detail page opened, not search.
  Nothing was selected or played. A per-title `/detail` link therefore
  reaches the title page. It is not registered: the launch needs a Prime
  title GTI, and no documented mapping from an ESPN event to a GTI exists.
  Evidence: `device-log.txt` (repair probe section),
  `evidence/visual/sp3-provider-links/prime-video-detail-cold.png`.

### 2. ESPN — `appAbsent`

`pm list packages` (289 packages, device-log.txt) contains no ESPN
package; third-party packages are only the SP-1 starter and Netflix.
`VIEW https://www.espn.com/watch/` resolves only to the Silk browser
(`com.amazon.cloud9`) and opens it as foreground. No package name, launch
intent or URI is registered: inventing one would fail CMD-REGISTRY-CHECK.
Registry: `espn` entry with no `platform_routes` entries, i.e.
`REGISTRY_ROUTE_GAP` on both platforms.
Evidence: `evidence/visual/sp3-provider-links/espn-view-browser.png`.

### 3. DirecTV Stream — `appAbsent`

Same package inventory: no DirecTV Stream package.
`VIEW https://stream.directv.com/` resolves only to Silk, which became
foreground on a "Loading, please wait." page. Nothing was signed in.
Registry: `directv_stream` with no `platform_routes` entries
(`REGISTRY_ROUTE_GAP`); `channels_carried` is empty because carriage on
this device is unverified.
Evidence: `evidence/visual/sp3-provider-links/directv-stream-view-browser.png`.

### 4. YouTube TV — `appAbsent`

Same package inventory: no YouTube TV package.
`VIEW https://tv.youtube.com/` resolves only to Silk, which became
foreground on the public marketing page (generic SIGN IN button, no
account data). Nothing was signed in or purchased.
Registry: `youtube_tv` with no `platform_routes` entries
(`REGISTRY_ROUTE_GAP`); `channels_carried` empty as unverified.
Evidence: `evidence/visual/sp3-provider-links/youtube-tv-view-browser.png`.

### 5. Local broadcast (CBS / Fox / NBC) — channel only, no deep link

`com.amazon.tv.livetv` exists but exposes no `LAUNCHER` activity
(`resolve-activity`: "No activity found"; `monkey` exit 252, foreground
stayed Fire TV Home). `dumpsys tv_input` lists HDMI/ARC, STB and
Prime Video (`FirebatTvInputService`) inputs and no broadcast tuner.
No installed app carries CBS, Fox or NBC, so per AFC-PR-029 the result is
the channel with no deep link. Registry: `local_broadcast` with
`channels_carried: [CBS, Fox, NBC]` (ESPN feed `media.shortName` casing)
and no `platform_routes` entries.
Evidence: `evidence/visual/sp3-provider-links/local-broadcast-home.png`.

## Observed result

| Provider | Attempted link / intent | Foreground after attempt | Observed outcome | Registered `fire_os` route |
|---|---|---|---|---|
| Prime Video | `VIEW https://watch.amazon.com/search` pkg `com.amazon.firebat` | `com.amazon.firebat/com.amazon.pyrocore.IgnitionActivity` | `searchOpened` (query ignored) | `uri` `https://watch.amazon.com/search`, `verified_outcome: searchOpened` |
| Prime Video | `MAIN`+`LAUNCHER`, `amzn://avod`, `YAC_LAUNCH` | `IgnitionActivity` | `appHomeOpened` | not registered (weaker than search) |
| ESPN | `VIEW https://www.espn.com/watch/` | `com.amazon.cloud9` (Silk) | `appAbsent` | none — `REGISTRY_ROUTE_GAP` |
| DirecTV Stream | `VIEW https://stream.directv.com/` | `com.amazon.cloud9` (Silk) | `appAbsent` | none — `REGISTRY_ROUTE_GAP` |
| YouTube TV | `VIEW https://tv.youtube.com/` | `com.amazon.cloud9` (Silk) | `appAbsent` | none — `REGISTRY_ROUTE_GAP` |
| Local broadcast | launch `com.amazon.tv.livetv` | Fire TV Home (unchanged) | no carrying app; channel only | none — `REGISTRY_ROUTE_GAP` |

Game arrival was not observed for any provider (no `gameOpened`).
`backend/src/provider_resolver/registry.json` keeps the landed schema
(`schemaVersion`, top-level `currentAttemptObservation: "none"`) and lists
the five providers in spike order. A missing `platform_routes` entry is
`REGISTRY_ROUTE_GAP` per CONTRACT-AFC-P2-PROVIDER-REGISTRY; that covers
every `vega` route (this Fire OS packet cannot verify Vega) and all
routes of the absent providers. Setting a `verified_outcome` (for
example `appAbsent`) without a verified package and launch would make the
resolver hand out unverified launch data as a verified route, so absent
providers record the gap instead; their observed `appAbsent` is recorded
here and in device-log.txt. Prime Video's channel is `Prime Video`, the
ESPN summary `header.competitions[0].broadcasts[].media.shortName` for
TNF event 401873010 (likewise the 2026-10-15 TNF game 401872995);
endpoint, retrieval time, HTTP status and the event/date/broadcast
fields for both are committed in `espn-summary-receipt.json` (this
directory, retrieved 2026-10-16T20:59:23Z).

## Evidence

- `device-log.txt` — every command, exit code and foreground activity
  (sanitized: no stick IP, serial or account data).
- `evidence/visual/sp3-provider-links/prime-video-home.png` (1920x1080).
- `evidence/visual/sp3-provider-links/prime-video-search.png`.
- `evidence/visual/sp3-provider-links/prime-video-ondemand-play.png`.
- `evidence/visual/sp3-provider-links/espn-view-browser.png`.
- `evidence/visual/sp3-provider-links/directv-stream-view-browser.png`.
- `evidence/visual/sp3-provider-links/youtube-tv-view-browser.png`.
- `evidence/visual/sp3-provider-links/local-broadcast-home.png`.
- `evidence/visual/sp3-provider-links/prime-video-detail-cold.png` — the
  `/detail?gti=` investigation probe.
- `probe.sh` — the probe harness used (serial supplied by environment).
- `espn-summary-receipt.json` — sanitized ESPN summary receipt for
  events 401873010 and 401872995 (channel, date and matchup claims).

## Limits

- Interim verdict: the live Prime Video TNF check is PENDING (PR 2,
  2026-10-22 TNF window). Until then the Prime Video route is proven only
  to the search screen plus on-demand playback; AFC-PR-030's
  game-or-channel arrival is unproven. PR 2 amends only the Prime Video
  entry's `verified_outcome` / `verified_at` and this verdict.
- OA-4 is only partly met on this stick: Prime Video is signed in, but
  ESPN, DirecTV Stream and YouTube TV are not installed. Per the packet
  they were not installed or signed in; the gap is typed, not passed.
  Their registry entries need a fresh on-device pass (package identity,
  documented launch, live-channel or on-demand outcome) before any route
  can be registered.
- The registered Prime Video search URI ignores any query, and no
  documented form carrying `{channel}` or `{event}` was found; the Watch
  action therefore lands the customer on the search screen, not the game.
  A `/detail?gti=` link opens a title page (see Prime Video above), but
  only with a Prime title GTI; ESPN events carry no GTI, so it is not
  registered.
- No current-attempt observation mechanism exists
  (`currentAttemptObservation: "none"`): the historical
  `verified_outcome` never establishes what a new launch did; the TV
  launcher's `accessUnknown` reporting stands (RISK-AFC-P2-10).
- Provider video captures black (secure surface, RISK-AFC-P2-09): the
  on-demand proof is the media-session playback state plus the ad
  countdown overlay, not the picture.
- Timebox (design.md SP-3 row) is 10 h plus the TNF window; this desk
  session ran 2026-10-16T20:00:12Z to 20:10:13Z, well inside it. The TNF
  window is spent in PR 2.
- `am start` exits 0 even on the "unable to resolve Intent" error; every
  outcome above rests on the `dumpsys activity` foreground readback, not
  the shell exit code.
- Silk browser was left on public pages only; no sign-in, sign-out,
  purchase, rental, subscription, account or settings change was made,
  and no app was installed or uninstalled. Prime Video and Silk were
  force-stopped at the end (data and sign-in untouched).

## developer_feedback

- SP3-DX-001: Prime Video's `MAIN` filter requires `LEANBACK_LAUNCHER`;
  the TV Watch launcher's intent form (action + package, no category)
  cannot use a bare `MAIN` value. Registry authors need this constraint
  next to the `intent` launch form, or the launcher needs a category
  field. Evidence: device-log.txt "prime-main-pkgonly".
- SP3-DX-002: `am start` returning exit 0 on an unresolved intent makes
  exit codes alone misleading for CMD-ADB evidence; the probe harness
  pairs every launch with a `dumpsys activity` foreground readback.
