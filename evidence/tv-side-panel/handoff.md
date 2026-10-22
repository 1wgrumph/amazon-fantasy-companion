# Side-panel and alert-card overlay TDD handoff

Outcome: SUCCESS (red contract delivered; product implementation remains pending).
Observer: Test Implementer, 2026-10-22 UTC. Product baseline: `a82157f`, branch `afc/tv-side-panel`.

Only JVM test sources and this evidence directory changed. No product/build edits,
commit, push, device access, permission grant or live-path activation occurred.
This is an expected feature red run, not a newly discovered defect.

## Evidence

From `tv-app`:

```sh
JAVA_HOME=~/.local/share/afc-tools/jdk-17.0.20.1+1 \
TMPDIR=~/.cache/afc-gate-tmp \
ANDROID_HOME=~/.local/share/afc-tools/android-sdk \
./gradlew :app:testDebugUnitTest
```

Exit **1**: **344 tests, 34 assertion failures, 310 passes**. Both product and test
compilation succeeded. All 34 failures belong to the overlay/card tests: missing controller/queue/
text/geometry APIs, missing permission/service, or missing integration source.
The individual failing names and messages are in [red.txt](red.txt).
JUnit XML independently confirms 34 `java.lang.AssertionError` failures and zero errors.

The original packet produced 18 red tests; this addendum adds 16 more. The
expanded run compiled and completed without a Gradle environment retry. A final
red run after tightening permission/render/window-removal wiring checks retained
the same 344/34/310 result.
`PYTHONDONTWRITEBYTECODE=1 bash tools/ci/gate.sh hygiene` exited **0**:
**119 tests in 368.695 s**, `gate: hygiene: PASS checks completed`. The
final added/updated files also passed the explicit private-path/credential scan
and staged whitespace check.

The module has JUnit 4 and source-contract conventions, without Robolectric.
The reflection approach follows `ui/theme/ThemeTestSupport.kt`: missing APIs throw
`AssertionError` so the red suite compiles before the product exists.
BRAN: unavailable (no repository policy); ordinary source discovery used.
No review or acceptance PASS is claimed by this test-authoring packet.

## Intended API

Package: `com.afc.companion.panel`.

```kotlin
enum class OverlayOutcome { Shown, Hidden, PermissionNeeded }

class OverlayController(
    val panel: PanelController,
    hasPermission: () -> Boolean,
    requestPermission: () -> Unit,
    addWindow: () -> Unit,
    removeWindow: () -> Unit,
) {
    fun show(): OverlayOutcome
    fun hide(): OverlayOutcome
    fun toggle(): OverlayOutcome
}

object OverlayGeometry {
    fun layout(screenWidth: Int, screenHeight: Int): Box
}
```

`OverlayController` must be JVM-pure. Tests supply operation counters, not an
Android window mock. Permission denial/grant are the owner's required inputs;
no on-device permission behavior is claimed. Begin with a hidden existing
`PanelController`; `show` synchronizes its visibility, checks permission, and
adds one window. Repeated `show` does not add another. Denial invokes the
permission route, returns `PermissionNeeded`, and leaves it hidden. A later
show rechecks permission. `hide` is safe before show and repeatedly afterward;
only one removal occurs, refresh stops, and a subsequent show refreshes immediately.
`toggle` uses those same paths.

`panel` is the supplied controller itself, preserving its current immutable
`PanelSnapshot`, subsequent revisions and existing refresh policy. Geometry is
in screen pixels, positive, at most 30% of full screen width, entirely inside
ceil(5%)/floor(95%) safe bounds, touching either safe left or safe right edge.
Cases cover 720p, 1080p, 4K and odd dimensions to expose rounding mistakes.

## Product wiring expected by source contracts

- Manifest: `SYSTEM_ALERT_WINDOW`; app-private `.panel.OverlayService` with a
  foreground service type. Host extends `Service` and calls `startForeground`.
- `panel/OverlayService.kt`: check `Settings.canDrawOverlays`; implement the
  permission callback with `ACTION_MANAGE_OVERLAY_PERMISSION` for this package.
  The source tests select the settings route rather than an instruction screen.
- Use `WindowManager.LayoutParams`, `TYPE_APPLICATION_OVERLAY`,
  `FLAG_NOT_FOCUSABLE`, and `OverlayGeometry.layout`. Apply the returned width,
  height, left/top offsets with `Gravity.TOP` and `Gravity.LEFT`; add/remove the
  real view. The offsets are absolute pixels, not END-relative offsets.
- Reuse the existing `PanelContent` renderer from `LineupPanel.kt`, making it
  callable across files. Pass `snapshot = controller.panel.snapshot` and
  `alerts = controller.panel.panelAlerts` in the host. The renderer already
  uses `PanelText` for points, unavailable/stale labels, total and sport header.
- Reuse/extract the existing profile/panel update owner from `LineupPanel`;
  do not duplicate its fetch loop in the overlay service. Tests reject direct
  `ApiClient`, `getPanel` and `getAlerts` calls in that service. Existing
  session-scoped, selected-team calls remain the data authority; add no endpoint,
  session source, external payload or network path. Snapshot identity and live
  update checks prevent a separate overlay model from drifting.
- Collect `AlertInbox.alerts` in the host; send `panelAlerts(alerts)` to
  `controller.panel.onAlerts`, without a sport filter. The tests retain each
  title, `PanelAlert.id`, watchability and `AlertCommand.Watch(alertId)` reference.
  The existing `AlertInbox.find` / `AlertNotifier.watchEventId` resolves that
  reference to its event; it does not infer an event from display text.
- `onDestroy`: `controller.hide()` and cancel host-owned collectors.

These source contracts pin the named integration points, not just token presence
in a new model. Android runtime behavior still requires device verification.

## Remote toggle decision

Choose an **in-app D-pad/OK button, "Show over game"**, backed by an explicit
app-private foreground-service intent. In `panel/OverlayService.kt`:

```kotlin
class OverlayServiceControl(context: Context) {
    fun toggle() // ContextCompat.startForegroundService with explicit OverlayService target
}
// OverlayService.ACTION_TOGGLE = "com.afc.companion.panel.TOGGLE_OVERLAY"
```

`toggle()` sends `.setAction(OverlayService.ACTION_TOGGLE)`; `onStartCommand`
reads `intent?.action` and dispatches `controller.toggle()`.
`MainActivity.kt` constructs `OverlayServiceControl`; the button's `onClick`
calls its `.toggle()` then `moveTaskToBack(true)` on the activity. User path:
open Companion from the playing app, press the button, and return to the previous
task. Reopen Companion and press the same button to hide the overlay. When the
permission route is opened, grant permission and retry the action.

Rationale: this is testable and uses ordinary app/service entry points without
accessibility interception or a dependency on Fire OS notification visibility.
`FLAG_NOT_FOCUSABLE` leaves remote input with the playing app. The app's Menu
handler cannot globally toggle over another focused app; no such capability is
claimed. A previous playing task must exist, and actual task return needs device
verification. Overlay Watch references remain available through the existing
Companion alert path; the nonfocusable overlay cannot capture D-pad/OK itself.

## Coverage and remaining verification

| Owner item | New tests / evidence |
| --- | --- |
| 1. Permission + foreground host | Two manifest/service tests |
| 2. Safe denial; idempotent show/hide/toggle | Six pure controller lifecycle tests |
| 3. Nonfocusable side window; width and safe zone | Geometry test plus Android window wiring test |
| 4. Same rows/points/stale/total/sport | Shared controller snapshot/revision test plus shared-renderer test |
| 5. Newly arriving NFL and NBA alerts + Watch reference | Two alert-arrival tests plus inbox/render wiring test |
| 6. Documented remote entry point | Intent/control/button source contract and decision above |
| 7. Independent top-right alert card | `AlertCardContractTest` and `AlertCardIntegrationContractTest`: geometry, minimal label/mark, FIFO queue, 5-second timeout, deduplication, background delivery and Watch path |
| Trust boundary / lifecycle | App-private service, reuse existing data paths, destroy cleanup |

Inputs reuse `PanelFixtures.kt` / `NbaPanelTest.kt` and committed backend alert
fixtures. NFL uses `backend/fixtures/alerts/red-zone.json` verbatim. The NBA
case uses the committed `PlayerScore` envelope with the NBA starter fields from
`backend/tests/unit/nba/test_nba_sport_toggle.py` (`NBA_STARTER`). This is a modeled
NBA-compatible wire input, not a captured live NBA alert: `alert_policy._alert`
and `pending` emit the same sport-neutral client envelope for both sports.
The tests do not invent a client sport discriminator or change the backend.

Remaining for the product implementer/acceptance role: implement the APIs and
integration, make the suite green, verify actual foreground startup/permission
flow, composition updates and stale ticking, lifecycle cleanup, legibility and
safe-zone placement on Fire OS 8, gameplay input/video continuity across provider
apps, task-return behavior, and arrival of real NBA/NFL alerts. JVM source
contracts cannot establish those device outcomes. No notification-action path,
accessibility handler, global hotkey or stick verification was added.


## Item 7: independent alert-card surface (owner addendum)

Decision: a separate, nonfocusable overlay window containing exactly two text
nodes: a compact player/number label (for example `Edwards 20`) and a 14 sp
`NBA`/`NFL` mark. Do not reuse the full alert card's headline, commentary,
matchup, Watch button or lineup content in this window. The existing richer
side-panel alert presentation remains available.

Size: an exact square of `min(screenWidth, screenHeight) / 6` integer pixels:
180 x 180 at 1920 x 1080, 120 x 120 at 1280 x 720, 360 x 360 at 3840 x 2160.
Its top is ceil(5% of height), its right edge floor(95% of width). Tested
landscape sizes including odd dimensions keep it inside the safe zone and below
2% of screen area. It overlays those corner pixels; "does not cover the game"
is interpreted as no full-screen cover, resize, navigation or playback pause.
A visible overlay cannot literally obscure zero game pixels.

The card stays top-right even with a right-side panel. While active, reserve its
slot and move the right panel below `card.bottom + ceil(1% of screenHeight)`;
retain the panel's safe right edge, positive height and at-most-30% width.
Tests prove disjoint rectangles. The host must apply the new panel parameters
with `updateViewLayout`, and restore its usual layout once the card disappears.
No switch to a different corner or overlap is permitted.

### Additional intended APIs

All in `com.afc.companion.panel`:

```kotlin
data class AlertCardNotice(
    val alertId: String,
    val player: String,
    val value: Double,
    val sport: String, // NBA or NFL, small mark separate from label
    val watchEventId: String,
)
object AlertCardText {
    fun label(player: String, value: Double): String?
}
object AlertCardGeometry {
    fun layout(screenWidth: Int, screenHeight: Int): Box
}
// Add to the existing intended OverlayGeometry object:
fun layoutWithAlertCard(screenWidth: Int, screenHeight: Int, card: Box): Box

class AlertCardQueue {
    val current: AlertCardNotice?
    fun offer(notice: AlertCardNotice, nowMs: Long)
    fun advance(nowMs: Long)
    fun clear()
}
```

Queue semantics: the first arrival appears immediately. Each displayed card
gets 5,000 ms from when it becomes current; expiry at the boundary removes it
and promotes exactly one next arrival. Later arrivals do not replace the current
card or consume their own display time while queued. Duplicate alert IDs are
ignored while current, queued and after expiry, for this queue's session;
duplicates do not extend the timeout. A delayed timer gives the next card its
full five seconds. `clear` removes current/pending cards and resets deduplication
at the session boundary. All timing tests inject monotonic values, with no waits
or shared engine resources.

`AlertCardText.label` drops integral `.0`, retains decimals, negative points and
real zero, and returns null for nonfinite values or existing unsafe on-field /
will-score claims. No long sentence or fabricated number may be displayed.
The numeric examples are owner-required presentation inputs, not captured NBA
statistics. `+6.5` is not inferred as a delta; a delta requires a known basis.

### Host wiring and remote Watch path

Implement `panel/AlertCardOverlay.kt` as a separate window owner with
`start`, `onAlerts`, `tick`, `showCard`, `hideCard`, and `stop` integration points,
and a minimal `AlertCardContent` composable. It owns the tested queue and uses
`SystemClock.elapsedRealtime()` for offers and expiry. `OverlayService` owns
this as `cards`, ticks it on a coroutine timer, moves the panel around the card
slot, and calls `cards.stop()` on destruction. `stop` clears the queue and
removes the card. Card arrivals must not start activities, take audio focus or
send media-control keys. Both surfaces remain `TYPE_APPLICATION_OVERLAY` with
`FLAG_NOT_FOCUSABLE`.

Add `OverlayServiceControl.startAlerts()` with an explicit foreground-service
intent carrying `OverlayService.ACTION_ALERTS`. The existing monitoring
service invokes `OverlayServiceControl(this).startAlerts()` even when the panel
has never been opened. The `ACTION_ALERTS -> { cards.start() }` branch must not
show or toggle the panel. The shared inbox collection also calls
`cards.onAlerts(alerts)` outside any panel-visible condition. No new network
calls belong in either overlay host. Permission handling must remain fail-safe;
background delivery must not steal game focus to request permission. Source
contracts require a card-host `Settings.canDrawOverlays` check, the real
`AlertCardContent` call in `showCard`, and removal of its window in `hideCard`.

Watch path: use the Fire TV app switcher/Apps to reopen Companion, navigate with
D-pad/OK to **Panel**, focus the retained alert's **Watch**, and press OK (twice
when switching confirmation is enabled). This is the existing WatchLauncher
path and preserves the actual alert/event identity. It is available after the
five-second card expires because card timeout never calls `AlertInbox.dismiss`.
Press Menu first if the full-screen panel is hidden. No remote input is
intercepted while the game has focus. Actual app-switcher
behavior, Watch navigation and playback continuity require device validation.

### Typed data gap for the product implementer

`AUTHORITATIVE_NUMBER_SOURCE_UNCONNECTED`: current committed alert envelopes
carry starters and team score, but no per-player numeric stat/fantasy-point
field or delta, and no client sport tag. `backend/fixtures/alerts/player-score.json`
is evidence. `backend/src/panel/__init__.py` projects own-lineup rows using the
starter's ESPN `athlete_id` as `playerId`; `PanelSnapshot` has row points and an
optional sport label. Reuse an already available, matching, authoritative own
row/sport to create the notice. A hidden panel must not gate delivery or cause
numbers to be invented, and a mismatched selected team/sport cannot supply the
value. The product implementer must resolve missing/current cross-sport inputs
within the existing data authority or return a typed gap; these tests do not
approve a new endpoint, schema field, backend edit, or silently skipped alert.
The pure notice/queue/format contracts are red and implementable, but they do
not prove that every live alert can yet produce a valid notice. This obligation
remains part of item 7, not a scope exclusion.
