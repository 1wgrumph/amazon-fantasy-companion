# Corner card and held-≡ remote control: implementation handoff

Historical implementer record for `5f8073a`; its SUCCESS is not current acceptance.
The independent review found F01–F06. The same-session repair status and current
behavioral evidence are in [review.md](review.md#repair--same-session-transition-authorized-2026-10-22).
F01 requires a contract decision; the original design, screenshots and claims below
must not be used as proof of a completed repair.
Observer: Implementer (Claude Code / Claude Opus 5.5 / high), 2026-10-22 UTC.
Base: `main` at `a22031f`, branch `afc/tv-corner-card`. No Fire TV stick,
provider app, live data, push or backend change was used.

## Design

- **Default surface.** "Show over game" and the first held ≡ show a corner card,
  not the side panel. The card shows the team total, its freshness ("Updated 12s
  ago", "Stale 75s", "Replay, …") and an opaque NFL/NBA mark. It is never
  focusable or touchable.
- **Key timing.** `access/MenuHoldFilter` decides per key event. The ≡ down
  always passes, because it cannot yet be known as long. A timer fires at
  700 ms after the down, measured from the event time. The filter consumes the
  auto-repeats and the up of that ≡ only. A late timer still fires from a repeat
  or from an up that arrives at 700 ms or later. A short ≡ and every other key
  pass through untouched.
- **State machine.** `OverlayController.mode` is Off, Card, Menu or Expanded.
  - A hold moves Off → Card, Card → Menu, and Menu or Expanded → Card.
  - The menu rows are Expand, League and Hide. D-pad Up and Down move between
    rows; OK selects.
  - League calls the existing `PanelAction.NextTeamLeague` and the menu stays
    open.
  - OK on the expanded panel opens the menu. Back on the menu or the panel
    returns to the card. Hide turns the surface off.
  - Only Menu and Expanded are focusable. "Show over game" toggles Off ↔ Card,
    and hides from any open surface.
- **League list.** `overlayTeamLeagues(profile)` puts the selected pair first,
  then the profile's other leagues with the same team. This is a `shortcut:`:
  the profile stores one team.
- **Geometry (1080p).** All boxes stay inside the 5% safe zone.
  - Card: 16% × 12% at the safe top-right, `[1517,54]` 307×129.
  - An alert keeps the corner, `[1644,54]` 180×180. The card moves 1% below it,
    to `[1517,245]`.
  - The menu sits 1% below the card: 20% × 24%, right-aligned.
  - Expanded uses the existing side-panel geometry.
- **Opacity.** The card background is `TvPalette.surface` at 72%; the menu is at
  90%. Text uses `onSurface` at full strength. The unit tests check 4.5:1 text
  contrast over white, pale yellow, sky blue, field green and black video. The
  sport mark uses the opaque accent with its `onSportAccent` text.
- **Service-off fallback.** Without the switch, everything works through "Show
  over game". The card adds one line: "Hold ≡ needs Accessibility"
  (`MenuHold.enabled` reads `ENABLED_ACCESSIBILITY_SERVICES`).
  `MainActivity.kt` is outside this write set, so the hint lives on the card.

## Tests (red first, then green)

- Red: 38 new tests against signature-only stubs gave 37 failures and 1 pass (an
  enum-shape check). See [red.txt](red.txt). This was an expected feature red,
  not a defect.
- Green: the full JVM suite passed (`:app:testDebugUnitTest`, exit 0). The three
  gate runs are listed in the commit's return.
- #157 tests changed only where the default surface moved. The
  `OverlayIntegrationContractTest` check for the non-focusable flag now looks for
  the tested `overlayWindowFlags(focusable = false)`. `OverlayLifecycleTest`
  (device test, not run here) waits for the card's "112.5" instead of
  "Team total: 112.5".

## Emulator visual check

The check ran on AVD `afc-tv-corner` (android-34 TV x86, 1920x1080, 320 dpi) on
console port 5620.

- **Data.** A synthetic loopback stub, outside the repository, served
  `/v1/profile`, `/v1/panel` and `/v1/alerts` with fictional players, through
  `adb reverse tcp:8787 tcp:8787`.
- **Build.** The evidence APK used `-PafcApiBaseUrl=http://127.0.0.1:8787` with
  cleartext allowed for that build only. The manifest was restored and verified.
  An emulator without a linked session has no data from the deployed URL.
- **Session.** A synthetic token was written with `run-as`.
- **Overlay permission.** `appops set com.afc.companion SYSTEM_ALERT_WINDOW
  allow`.
- **Accessibility service.** Enabled on this emulator only, with
  `settings put secure enabled_accessibility_services
  com.afc.companion/com.afc.companion.access.MenuHoldService`. `dumpsys
  accessibility` showed it bound with `capabilities=8` (key filtering). The
  manifest declares it `exported="false"` behind `BIND_ACCESSIBILITY_SERVICE`.
- **Game.** The system HTML viewer showed a synthetic CSS "game" page, bright or
  dark, through a `data:` URI.
- **Key injection.**
  - `input keyevent --longpress KEYCODE_MENU` does not reach an accessibility
    key filter. A probe build logged nothing for any `input keyevent`, which
    matches Android's rule that injected events skip the filter.
  - `adb emu event send` produced no input events on this image, even with
    `hw.keyboard=yes`.
  - The holds were sent from a real input device instead: Android's
    `uinput -` shell tool registered a synthetic remote and sent KEY_MENU down,
    waited 150 ms or 1000 ms, then sent up. The probe build logged
    `key=82 action=0`, then `action=1 t=999`. The hold fired 702 ms after the
    down, and `ActivityManager` reported `Background started FGS: Allowed …
    uidState: BFGS`.

Screenshots: [../visual/tv-corner-card/](../visual/tv-corner-card/SHA256SUMS),
all 1920x1080.

| File | Shows |
| --- | --- |
| `service-off-hint.png` | Switch off; "Show over game" put the card over the bright game, with "Hold ≡ needs Accessibility". Focus stayed on the game. |
| `card-bright.png` | Switch on; the card over bright video, with no hint. |
| `card-dark.png` | The same card over dark video. |
| `card-and-alert.png` | An alert takes the corner (`[1644,54][1824,234]`) and the card stacks below it (`[1517,245][1824,374]`) with no overlap. |
| `menu-open.png` | After a 1 s hold: the menu below the card. `mCurrentFocus` is the Companion overlay. |
| `menu-league-switched.png` | League pressed: the card shows the Office League total (88.0) and the menu stays open. |
| `expanded-panel.png` | Expand: the existing side panel, which has focus. |
| `pt-0-panel.png` → `pt-1-after-short.png` | Over Companion's own full-screen Panel, a 150 ms ≡ reached the app (the Panel hid). This proves a short ≡ passes through. |
| `pt-2-after-hold.png` | A 1 s ≡ over that Panel opened the overlay menu, and the Panel also toggled back (see the risk). |
| `pt-3-after-back.png` | Back closed the menu; focus returned to the app (`MainActivity`). |

Back on the expanded panel over the HTML game returned focus to the
`HTMLViewerActivity` window, leaving only the card window.

## Risks

- **A held ≡ also delivers the ≡ down to the playing app.** A filter must answer
  for each event as it arrives, and no accessibility API can re-send a key
  later. So the down passes before the hold is known; only the repeats and the
  up are consumed.
  - Apps that act on ≡ release, such as Android options menus, see nothing.
  - Apps that act on ≡ press also run their own action. Companion's own Panel is
    one (`pt-2-after-hold.png`).
  - When the menu takes focus, Android sends the app a cancel for the held key.
  - Prime Video and other provider apps were not checked.
- **Fire OS was not tested.** These points are unverified on the stick:
  - whether Settings > Accessibility lists third-party services on that Fire OS
    build;
  - whether VoiceView or the system uses a ≡ hold;
  - the foreground-service start from the service (Android 11 has no
    background-start limit).
- **League switching** pairs every profile league with the one stored team. A
  league without a backend lineup shows the panel's usual unavailable state.
- **Emulator-only proof.** Holds used a synthetic uinput remote, not the Fire TV
  remote.

## Owner steps on Fire OS (when you choose to enable it)

1. Install the build and allow "Display over other apps" as before.
2. Open Settings > Accessibility on the Fire TV.
3. Select "Fantasy remote: hold Menu" (Companion), then turn it on and confirm
   the Fire OS prompt.
4. In any app, hold ≡ for about a second to show the card. Hold ≡ again for the
   menu. Press Back to return to the game.

To turn it off, repeat steps 2 and 3. "Show over game" in Companion keeps
working either way.
