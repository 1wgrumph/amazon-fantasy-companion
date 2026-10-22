# Side panel and alert card: implementation notes

Observer: Implementer (Claude Code / Claude Opus 5.5 / high), 2026-10-22 UTC.
Branch `afc/tv-side-panel` from `a82157f`. Gate output: [green.txt](green.txt).
Emulator check: [visual-check.md](visual-check.md).

## What was built

- `panel/OverlayModel.kt` (JVM-pure): `OverlayController`, `OverlayGeometry`
  (a quarter of the width on the safe right edge, full safe height; moved below a
  showing card with a 1% gap), `AlertCardGeometry`, `AlertCardNotice`,
  `AlertCardText`, `AlertCardQueue`, and `alertCardNotice(alert, panel)`.
- `panel/OverlayService.kt`: foreground host (type `dataSync`) for both windows,
  `OverlayServiceControl.toggle()` / `startAlerts()`. The panel window renders the
  shared `PanelContent` in a compact form (stacked rows, no team/league switch, the
  newest alert's headline and player without Watch/Dismiss) at 0.65 density.
- `panel/AlertCardOverlay.kt`: the card window, its queue timer hooks and
  `AlertCardContent` (label plus a 14 sp NBA/NFL mark on a sport-accent band).
  Alerts already retained when the host first reads the inbox do not pop up.
- `LineupPanel.kt`: the fetch loop moved unchanged into `runPanelUpdates`, now
  shared with the overlay; `PanelContent` is `internal` with a `compact` flag
  (default off, so the full-screen panel is unchanged).
- `MainActivity.kt`: "Show over game" button. `AlertService` starts the card host.
  Manifest: `SYSTEM_ALERT_WINDOW` and the app-private `.panel.OverlayService`.
- No build-file or dependency change.

## Permission flow decision

The button sends the toggle intent. With the permission, Companion moves to the
back and the previous app returns with the panel over it. Without it,
`OverlayService` opens `Settings.ACTION_MANAGE_OVERLAY_PERMISSION` for
`package:com.afc.companion`, stops itself, and Companion stays in front with the
manual path ("Settings > Applications > Special app access > Display over other
apps"). That text also covers a Fire OS build that has no handler for the
settings screen (`startActivity` failure is caught). Background alert delivery never
asks for the permission; without it no card is drawn.

## Alert payload fields the backend should add (optional, not changed here)

Read by `alertCardNotice` when present; absent fields fall back as described.

| Field | Type | Use | Fallback today |
| --- | --- | --- | --- |
| `data.triggerContext.sport` | `"nba"` or `"nfl"` | card mark | the overlay panel snapshot's sport when the starter is one of its rows, else no mark |
| `data.triggerContext.starters[0].shortName` | string, at most 14 characters | card name | the last word of `starters[0].name` |
| `data.triggerContext.starters[0].points` | number, fantasy points on the profile's scoring basis | card number | the matching row's points in the overlay panel snapshot, else no number (name only) |

`AUTHORITATIVE_NUMBER_SOURCE_UNCONNECTED` stays open until the backend sends
`points`: with the panel hidden, today's alerts show the name and mark only, never a
made-up number.

## Remaining risks

- Fire OS 8 is unverified: whether its settings handler exists, whether
  `SYSTEM_ALERT_WINDOW` can be granted there without adb, and starting a
  foreground service from `AlertService`.
- After monitoring stops, `OverlayService` stays in the foreground while the card
  host is active (low-importance "Fantasy overlay ready" notification) until the
  process ends.
- A toggle and a monitoring start arriving within one profile load could let
  `stopIfIdle` stop the service before the toggle completes; the next press works.
- Overlays are hidden by Android over screens that set
  `HIDE_NON_SYSTEM_OVERLAY_WINDOWS` (for example TV Settings).
