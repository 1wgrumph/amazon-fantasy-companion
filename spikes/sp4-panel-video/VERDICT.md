---
spike: SP-4
slice: P2-X04
verdict: FAILS
device:
  model: AFTKM
  fire_os: Fire OS 8.1.8.5 (RS8185/3891)
  android_release: "11"
  api_level: 30
  display: physical 3840x2160, override 1920x1080
started_at: 2026-10-16T19:07:25Z
ended_at: 2026-10-16T19:25:29Z
first_install_at: 2026-10-16T12:19:31Z
unblocks: [AFC-PR-041, AFC-PR-047, AC-AFC-P2-SPIKE-01, AC-AFC-P2-SPIKE-02, RISK-AFC-P2-04, RISK-AFC-P2-09, RISK-AFC-P2-10]
conditional: C5
---

# SP-4 panel beside provider video verdict

**Verdict: FAILS.** No supported composition route on this stick shows the
panel *beside* playing Prime Video with no overlap and no crop, so
`PanelMode.modeB` is not selectable. Selected fallback: `PanelMode.fullScreen`
— the lineup panel full-screen in the companion app (AFC-PR-047), with alerts
and Watch still routed to the real provider apps (AFC-PR-048). AFC-PR-041's
positive case is not unblocked; C5 selects the fallback.

The verdict was reached on 2026-10-16, inside `first_install_at` +
`spike_panel_max` (24 h from SP-1's first install, 2026-10-16T12:19:31Z), so
this is a FAILS verdict on evidence, not TIMEBOX.

Test article: the leased stick above running Prime Video
(`com.amazon.firebat`, PVFTV-324.0104-L) signed in by the owner (OA-4),
playing Prime-included content started over ADB (owner-authorized
2026-10-16; no purchase, rental, or account change). Spike probe:
`com.afc.spike.sp4` from this directory (APK sha256
`08aa7e8401d0649f9811895067cec05d3744165f078ceea712e40000fc24e089`), installed
for the sweep and uninstalled after it. Full commands with exit codes:
`evidence/visual/sp4-panel-video/commands.txt`.

## Routes tried

1. **Picture-in-picture of the provider** (Prime Video shrinks, panel app
   full-screen behind it). Supported trigger tried: HOME key during playback
   (R1). Prime Video's activity declares no PiP support
   (`mSupportsPictureInPicture=false` in `r1-provider-pip-home-geometry.txt`),
   and HOME stopped playback (media session state 3 → 0) and resumed the
   launcher; no pinned task appeared. A third-party app cannot force another
   app into PiP, so there is no other supported entry to this route.
   Sources: Android developer docs, "Picture-in-picture"
   (https://developer.android.com/develop/ui/views/picture-in-picture);
   Amazon Fire TV developer docs, "Connect to Fire TV Through ADB"
   (https://developer.amazon.com/docs/fire-tv/connecting-adb-to-device.html).
   Outcome: **fails (blocked by platform/provider)**.
2. **Picture-in-picture of the panel** (spike panel pinned, Prime Video
   full-screen). This works mechanically: `enterPictureInPictureMode`
   returned true (`r2-spike-pip-entered-logcat.txt`) and the panel stayed
   pinned over the full-screen player with playback running
   (`r2b-spike-pip-over-player.png`, media state=3 in
   `r2b-spike-pip-over-player-geometry.txt`). But the geometry is decisive
   against modeB: the pinned panel occupies `Rect(1424, 54 - 1808, 270)`
   (384x216 px) *inside* the unchanged 1920x1080 full-screen video window —
   it covers the top-right of the broadcast and the video is not re-fitted
   beside it. Any overlap fails AFC-PR-041's negative case.
   Source: Android developer docs, "Picture-in-picture" (URL in route 1).
   Outcome: **works as PiP; fails modeB (overlap)**.
3. **Overlay window** (`TYPE_APPLICATION_OVERLAY`, window type 2038). Without
   a grant, `Settings.canDrawOverlays` is false and `WindowManager.addView`
   threw `BadTokenException: permission denied for window type 2038`
   (`r3-overlay-no-grant-logcat.txt`); `appops get` reports
   `SYSTEM_ALERT_WINDOW: default` with a reject record. The only supported
   grant path is the system Settings screen
   (`ACTION_MANAGE_OVERLAY_PERMISSION`), i.e. a device-settings change,
   which this spike's authority excludes — granting it is an owner decision,
   not something Fire OS offers an app in-flow. Even if granted, an overlay
   composites *over* the unchanged full-screen video, so it would still
   overlap the broadcast unless Prime Video shrank, which no route here can
   make it do.
   Source: Android developer docs, "SYSTEM_ALERT_WINDOW"
   (https://developer.android.com/reference/android/Manifest.permission#SYSTEM_ALERT_WINDOW).
   Outcome: **fails (permission needs a settings change; geometry would
   overlap anyway)**.
4. **Split-screen multi-window**: spike launched fresh with
   `--windowingMode 3` (split-screen-primary). The task came up
   `mode=fullscreen` and the spike logged `multiWindow=false`
   (`r4-split-windowingmode-geometry.txt`, `-logcat.txt`). Fire OS 8 on this
   stick does not place TV activities side by side.
   Source: Android developer docs, "Multi-window support"
   (https://developer.android.com/guide/topics/large-screens/multi-window-support).
   Outcome: **fails (blocked by platform)**.
5. **Freeform windowing**: spike launched fresh with `--windowingMode 5`.
   Same result as route 4: `mode=fullscreen`, `multiWindow=false`
   (`r5-freeform-windowingmode-*`).
   Source: Android developer docs, "Multi-window support" (URL in route 4).
   Outcome: **fails (blocked by platform)**.

No other supported composition route exists for a third-party app over
another app's playback on Fire OS 8: the platform offers no public API to
resize or reposition Prime Video's window, and Prime Video exposes no
embedding surface to third parties.

## Observed result

The only route that puts panel and provider video on screen at the same time
is panel picture-in-picture (route 2), and it does so by covering part of
the video. ModeB's bar — simultaneous video and panel with no overlap, no
crop, preserved aspect (AFC-PR-041, AC-AFC-P2-SPIKE-02) — cannot be met:
every route either does not run (1, 3, 4, 5) or overlaps (2, and 3 if it
were granted). Per AFC-PR-047 and RISK-AFC-P2-04 the panel is therefore
built as `PanelMode.fullScreen`.

Playback evidence note (RISK-AFC-P2-09): the playing video itself captures
black in every screencap (secure/DRM surface); player chrome (the pre-roll
"Ad 0:32" badge) and the media-session state confirm real playback.
Geometry in the `*-geometry.txt` files is the sanitized `dumpsys`
projection; raw dumps stayed off-repo.

## Evidence

All under `evidence/visual/sp4-panel-video/`: `commands.txt` (every attempt
with exit codes), and per attempt a screenshot plus `-geometry.txt` and
`-logcat.txt`: `r0-playback`, `r1-provider-pip-home-geometry.txt` and
`r1-provider-pip-home-logcat.txt` (screenshot withheld (provider content):
`evidence/visual/PRIVATE-EVIDENCE.md` (Fire TV home after the provider
picture-in-picture attempt)), screenshot only (withheld (provider content):
`evidence/visual/PRIVATE-EVIDENCE.md` (Prime Video home screen with team
logos)), `r2-spike-pip-entered-geometry.txt` and
`r2-spike-pip-entered-logcat.txt` (screenshot withheld (provider content):
`evidence/visual/PRIVATE-EVIDENCE.md` (Fire TV home with the spike panel
over it)), `r2-spike-pip-over-prime-geometry.txt` and
`r2-spike-pip-over-prime-logcat.txt` (screenshot withheld (provider content):
`evidence/visual/PRIVATE-EVIDENCE.md` (Prime Video title screen with the
spike panel over it)), `r2b-spike-pip-over-player`, `r3-overlay-no-grant`,
`r4-split-windowingmode`, `r5-freeform-windowingmode`,
`r6-final-prime-geometry.txt` (screenshot withheld (provider content):
`evidence/visual/PRIVATE-EVIDENCE.md` (Prime Video title screen at the end
of the panel sweep)).
The spike source is this directory (`app/`); `.gitignore` excludes
`local.properties`, `.gradle/`, and `build/`.

## Limits

- One provider (Prime Video) on one stick and one Fire OS build. Other
  provider apps could declare PiP support, but provider-PiP geometry still
  floats the video over the panel app rather than fitting it beside the
  panel, so the modeB conclusion does not depend on re-probing each app.
- The overlay route was not re-tried with the permission granted: granting
  it requires a Settings change outside this spike's authority. If the owner
  ever grants it, route 3 still overlaps the video (see above), so the
  verdict would not change.
- Video pixels are not provable from screencap (black secure surface). The
  overlap conclusion rests on window geometry plus the capture of the panel
  over the player surface, not on decoded video content. No owner camera
  capture (OA-9) was taken; none is needed because the verdict is negative.
- `first_install_at` is SP-1's value (the `spike_panel_max` clock start),
  per CONTRACT-AFC-P2-VERDICT for SP-1 and SP-4.
- Screenshots show provider browse artwork and the spike's fixture text
  only; no account name, email, stick address, or serial is recorded
  anywhere in this spike's files.
- The spike APK was uninstalled at the end (`commands.txt`); the companion
  app and all provider apps were left untouched.

## developer_feedback

none
