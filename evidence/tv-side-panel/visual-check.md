# Side panel and alert card: emulator visual check

Observer: Implementer (Claude Code / Claude Opus 5.5 / high), 2026-10-22 UTC.
Device: local Android TV emulator only, AVD `afc-tv-sidepanel`
(`system-images;android-34;android-tv;x86`, 1920x1080, 320 dpi), console port 5594.
No Fire TV stick, provider app or live data was used.

## Setup

- Data: a synthetic loopback stub (fictional players, outside the repository)
  served `/v1/profile`, `/v1/panel` and `/v1/alerts`, reached through
  `adb reverse tcp:8787 tcp:8787`.
- Build: `assembleDebug -PafcApiBaseUrl=http://127.0.0.1:8787`. The committed
  manifest blocks cleartext traffic, so the evidence APK alone was built with
  `usesCleartextTraffic="true"` and the manifest restored in the same step.
  The shipped manifest is unchanged by this check.
- Foreground app: the system HTML viewer showing a synthetic, CSS-drawn field
  (`game.html`, labelled "Synthetic game feed"). TV Settings cannot serve as the
  foreground app: it sets `HIDE_NON_SYSTEM_OVERLAY_WINDOWS`, and
  `dumpsys window` showed `mForceHideNonSystemOverlayWindow=true` for the overlay.
- Permission: `adb shell appops set com.afc.companion SYSTEM_ALERT_WINDOW allow`
  (or `default` for the missing-permission flow).

## Screenshots

All are 1920x1080 PNGs in [../visual/tv-side-panel/](../visual/tv-side-panel/SHA256SUMS).

| File | What it shows |
| --- | --- |
| `side-panel-over-game.png` | Panel over the game after "Show over game": NFL sport chip, rows with points, a stale label, Unavailable, team total. |
| `card-and-panel.png` | NFL card top-right (`Receiver 6.5`, the number from the overlay's own panel row) with the panel moved below it; no overlap. |
| `alert-card-over-game.png` | NBA card alone (`Stone 20`, from the proposed optional alert fields) with the panel hidden. |
| `panel-restored-after-card.png` | After the card expires, the panel is back at the safe top. |
| `permission-settings-route.png` | Without the grant, "Show over game" opens Android TV's "Allow display over other apps" with Companion selected. |
| `permission-missing-hint.png` | Back in Companion: the manual steps under the button; Companion stays in front. |

## Observed behaviour

- After the button, `topResumedActivity` was the previous app (HTML viewer):
  `moveTaskToBack(true)` returned to it.
- With a card showing, `mCurrentFocus` stayed on the HTML viewer window; both
  overlay windows are `FLAG_NOT_FOCUSABLE | FLAG_NOT_TOUCHABLE`.
- About 5 s after an alert, the card window was gone (`dumpsys window`: no
  overlay window left while the panel was hidden).
- Without the permission, `OverlayService` was not running after the attempt (it
  stops itself), and nothing crashed.

Not verified here: Fire OS 8 behaviour (whether the settings screen exists,
foreground-service start from monitoring, provider-app video continuity) and
real NBA/NFL alert payloads.
