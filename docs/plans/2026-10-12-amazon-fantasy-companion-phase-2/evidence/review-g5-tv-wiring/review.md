# Independent review: G5 TV wiring (afc/g5-tv-wiring @ a03a760)

- Reviewer: Claude Code (bug-triager reviewer route, binding bug-triager-sd073). Not the author.
- Candidate: `afc/g5-tv-wiring` at `a03a760` (one commit, 13 files, author Cursor Agent).
- Base: `origin/main` at `7d97a33` (merge base `7d97a3314f05be12047fe98c209bfc920f3d9d27`).
- Mode: static review. The host unit tests could not run (gap GAP-1 below).

## Verdict: REPAIR_REQUIRED

Two fixable Medium bugs block acceptance:

- **F1.** The alert cards overflow the fullScreen panel. This pushes the lineup and some Watch/Dismiss actions off-screen, and D-pad focus still moves onto those hidden actions.
- **F2.** Dismissed alerts come back, along with the whole alert history, every time AlertService restarts. This change adds the stop/start cycle, and it is the first change to show the feed's queue on the panel.

The invariant checks on the Watch path pass:

- only a verified `fire_os` registry route launches, never a bare MAIN;
- an uncertain outcome never relaunches;
- each attempt reports exactly one outcome;
- alert text stays sanitized;
- the service runs only with a session;
- no token is logged.

## Findings (most severe first)

### F1 (Medium): Alert cards overflow the fullScreen panel and hide the lineup and focusable actions

- **Where:**
  - `tv-app/app/src/main/java/com/afc/companion/panel/LineupPanel.kt:222`: `alerts.forEach { AlertCard(...) }` sits in a plain, non-scrolling `Column`.
  - `LineupPanel.kt:247-248`: the lineup is a `LazyColumn` with `Modifier.weight(1f)`.
  - `LineupPanel.kt:290-303`: `AlertCard`.
  - `tv-app/app/src/main/java/com/afc/companion/panel/PanelModel.kt:216`: `PANEL_ALERTS_MAX = 3`.
- **Failure scenario:**
  1. A 1080p Fire TV (xhdpi, density 2.0) has a 960×540 dp window. The fullScreen panel adds 32 dp padding on each side, which leaves about 476 dp of height.
  2. One `AlertCard` holds:
     - 24 dp of card padding;
     - a 32 sp headline (about 43 dp);
     - context and access lines at 24 sp (about 32 dp each);
     - a Watch row and a Dismiss row, each 24 sp text plus 24 dp padding (about 56 dp each);
     - 4 × 8 dp of spacing;
     - an optional commentary line.

     That is about 275–310 dp per card, plus 16 dp of column spacing.
  3. With two retained alerts, the cards alone (about 580 dp or more) are taller than the panel. The `weight(1f)` LazyColumn then gets 0 height. The Team/league switch, header, player rows and Total, and with three alerts also the last card's Watch/Dismiss, are laid out below the window.
  4. `PanelController.focusTargets()` still lists all of these targets. DOWN therefore moves focus onto controls the customer cannot see: the focus border disappears.
  5. OK on an invisible `AlertWatch` arms it, and a second OK launches the provider. OK on an invisible Dismiss dismisses an alert the customer never saw.
  6. The lineup is the panel's main content. It becomes unreadable whenever two or more alerts are held, and they stay held until each one is dismissed.
- **Why the tests miss it:** `PanelAlertsTest.kt:42` claims "bounded so the lineup stays on screen", but it only checks the list cap. No test measures the layout. Compose code is not run by host tests (a known risk), so nothing catches this.
- **Fix:** Pick one:
  - (a) Render alerts and lineup in one scrollable container that scrolls the focused target into view (`LazyColumn` with `LazyListState.animateScrollToItem` on focus change, or `Modifier.bringIntoViewRequester`).
  - (b) Make the alert card compact: one headline line, with Watch and Dismiss side by side on one row. Then derive the cap from a height budget, for example `PANEL_ALERTS_MAX = 1–2`, or show "+N more".

  Either way, add a check that the cards' height leaves room for the lineup, for example a pure height-budget function in `PanelModel` with a unit test, or a Compose UI test. Also correct the misleading assertion message.

### F2 (Medium): Dismissed alerts and the full alert history reappear after every AlertService restart

- **Where:**
  - `tv-app/app/src/main/java/com/afc/companion/alerts/AlertService.kt:65-66`: each poll start creates a new in-memory `AlertFeed(client)` (cursor `null`, empty `dismissed` map) and attaches it to `AlertInbox`.
  - `tv-app/app/src/main/java/com/afc/companion/Shell.kt:28-33`: `syncMonitoring` stops and starts the service.
  - `AlertService.kt:83`: `START_STICKY` restarts the service after the process is killed.
  - Backend: `backend/src/store/__init__.py:158` (`None = from the start`) and `backend/src/alert_policy/__init__.py:259-277` (`pending`, with no age or TTL filter).
- **Failure scenario:**
  1. The customer has dismissed alerts a1–a5 on the panel.
  2. Either of these then happens:
     - (i) The customer turns off every alert type, navigates, turns one back on and navigates again. `syncMonitoring` calls stop() and later start().
     - (ii) The customer presses Watch, Prime Video takes the foreground, and Fire OS kills the companion process under memory pressure, which is common on a Stick. `START_STICKY` then restarts the service.
  3. The new `AlertFeed` polls `GET /v1/alerts` with no cursor. The backend replays the profile's whole alert history from the start.
  4. The `dismissed` revisions are gone, so every alert counts as new. a1–a5 return to the inbox, the newest three show at the top of the panel again, and each offers Watch for a past event.
  5. With heads-up presentation, `PresentationGate` also re-posts all of them as notifications.

  Before this commit nothing started AlertService and the panel showed no alerts, so this change makes the problem reachable for customers.
- **Fix:** Persist the feed's progress and dismissed state across `AlertFeed` instances:
  - store the cursor, plus the dismissed id→revision map bounded to `QUEUE_MAX`, in app-private `SharedPreferences`;
  - restore them when `onStartCommand` builds the feed;
  - add a host test that dismisses, builds a new feed from the persisted state, polls a page that replays the history, and asserts the dismissed alert is not delivered.

  A backend-side bound on what a no-cursor poll returns would also help, but the client fix is still needed.

### F3 (Low): `AlertInbox.publish` can overwrite a newer snapshot with a stale one, so a dismissed alert reappears briefly

- **Where:** `tv-app/app/src/main/java/com/afc/companion/alerts/AlertService.kt:152-153`. Callers are the poll loop on `Dispatchers.IO` (`:74`), the notification Dismiss (`:53`) and the panel Dismiss on Main (`AlertInbox.dismiss`).
- **Failure scenario:**
  1. The IO poll thread reads `feed.queue` = [a1, a2].
  2. On Main, the customer dismisses a1, and that publish writes [a2].
  3. The IO thread then writes its stale [a1, a2].
  4. a1 shows on the panel again until the next poll that delivers something, which can be a full long-poll interval or longer. Pressing Dismiss on it a second time clears it.

  The window is small but real, because the read of the queue and the write of the state are not one atomic step.
- **Fix:** Make `publish` `@Synchronized`, using the same lock in `dismiss` and `attach`. Alternatively, have `AlertFeed` expose a `StateFlow` it updates inside its own lock.

### F4 (Low): The panel Watch report runs in the composition scope, so it can be cancelled after the launch

- **Where:** `tv-app/app/src/main/java/com/afc/companion/panel/LineupPanel.kt:90` and `:110-113`: `rememberCoroutineScope()` runs `watchAlert`.
- **Failure scenario:**
  1. `launchOnce` starts the provider, so the companion activity goes to the background.
  2. If the activity is destroyed before `client.reportRoutingOutcome` gets to `withContext(IO)` (for example with "Don't keep activities" or a low-memory activity teardown), the scope is cancelled.
  3. `withContext` throws `CancellationException` on entry, and `watch()` rethrows it. The attempt launched, but no outcome is reported. That breaks the invariant of exactly one routing outcome per attempt.

  `WatchActivity.kt:33` deliberately uses a detached scope for this reason ("the outcome report must outlive it"). The panel path does not.
- **Fix:** Run the report in a scope that is not tied to the composition, such as an application-level scope, with `NonCancellable` around the report step in `WatchLauncher.watch`. Then send `watchOutcome` back to the UI only while it is still composed.

### F5 (Low): WatchActivity's detached coroutine and dialog can leak when the activity is recreated

- **Where:** `tv-app/app/src/main/java/com/afc/companion/watch/WatchActivity.kt:33-37` and `:42-48`.
- **Failure scenario:**
  1. The switching-confirmation dialog is showing, and a configuration change (or the system) destroys and recreates the activity.
  2. The new instance correctly finishes without a second attempt (`savedInstanceState != null`).
  3. The old dialog's window leaks (`WindowLeaked`). Its cancel listener never fires, so `suspendCancellableCoroutine` never resumes, and the detached coroutine and the old Activity are held forever.

  No attempt and no report happen, so there is no invariant breach, only a leak.
- **Fix:** Dismiss the dialog and resume with `false` in `onDestroy` when it is still pending. Keep the detached scope only for the steps after the confirmation.

### F6 (Info): Select is bound only to `KEYCODE_DPAD_CENTER`

- **Where:** `tv-app/app/src/main/java/com/afc/companion/panel/PanelModel.kt:287`.
- **Failure scenario:** On a Fire TV game controller (`KEYCODE_BUTTON_A`) or a keyboard or Fire TV app remote that sends `KEYCODE_ENTER` / `KEYCODE_NUMPAD_ENTER`, Watch and Dismiss cannot be activated. The stock Fire TV remote is unaffected.
- **Fix:** Also bind `KEYCODE_ENTER`, `KEYCODE_NUMPAD_ENTER` and `KEYCODE_BUTTON_A` to `Select`.

## Hunt checklist (what was attacked and found clean)

- **Service lifecycle.**
  - **No double start.** `onStartCommand` returns early while polling is active (`AlertService.kt:63`), so repeated `startForegroundService` calls on navigation start no second loop. They also cannot hit `ForegroundServiceDidNotStartInTimeException`: the service is already in the foreground, so the system clears `fgRequired`.
  - **stopService race.** A `stopService` that lands before the first `startForeground` would crash on API 28+. That needs a second navigation's profile load to finish before the service's main-thread `onStartCommand` runs, and `LaunchedEffect(destination)` cancels the earlier effect. I judge it not practically reachable, and list it under remaining risks.
  - **No polling without a session.** The shell starts the service only with a session, and `SessionStore.clear()` has no caller, so a running service always has its token.
  - **`client()` null path.** `stopSelf` without `startForeground` is unreachable from the shell: the same config makes `MainActivity` show NotConfigured.
- **Watch launch.**
  - `verifiedLaunch` requires `status == "verified"`, a package that matches the regex, and a `uri` or `intent` type.
  - `launchSpec` drops a bare `MAIN`, an empty action and unknown types. `AndroidLaunchPlatform.start` re-validates the same way.
  - The launch is a single pass with no relaunch.
  - The panel `watching` flag blocks a double OK while an attempt is in flight.
  - A recreated `WatchActivity` never runs a second attempt.
  - A declined switch reports nothing, which is correct because no attempt happened.
- **Routing reports.** `watch()` reports exactly once, even when the report itself fails (`WatchLauncher.kt` report block). The one exception is the cancellation case in F4.
- **D-pad focus.**
  - An arriving alert does not steal focus.
  - `keepFocus` moves focus off a dismissed target.
  - Moving focus disarms a pending confirmation.
  - LEFT leaves the panel for the shell navigation, so there is no trap.
  - The hidden-target problem is F1.
- **Ordering and cap.** `asReversed()` of the feed's insertion-ordered queue gives newest first (a new revision is re-inserted at the end). Unsafe text is filtered before `take(3)`, so an unsafe alert never takes a slot. Reappearing alerts are covered in F2 and F3.
- **PendingIntent.** `FLAG_IMMUTABLE | FLAG_UPDATE_CURRENT` (unchanged), which is correct for target 34 and API 31+. Distinct data URIs and request codes keep each alert's intents separate.
- **Exported components.** The manifest is unchanged. `WatchActivity` and `AlertService` are `exported="false"`.
- **Text and access claims.** The panel uses `AlertPresenter.text` (sanitized; unsafe alerts are dropped whole). `PanelText.watchOutcome` never claims the game opened, because the launcher returns only `AccessUnknown`, `AppAbsent` or `PlaybackDenied`. The access label stays "Access: unknown".
- **Token logging.** The diff adds no logging.
- **Tests.**
  - The replaced StubContractTest assertion (stub returns `AccessUnknown`) is not a weakening. `AccessUnknown` on a started launch is now asserted on the real path (`WatchAlertTest.kt:37,40`).
  - `registryBareMainIntentIsNeverLaunched` would fail on the old code: `RecordingPlatform` has `PROVIDER_PACKAGE` installed by default, so the old code would record a start.
  - The weak tests are:
    - `PanelAlertsTest.kt:40-42` (F1);
    - `dismissedAlertMovesFocusToAnExistingElement`, which asserts only membership and not which target gets focus;
    - `StubContractTest.stubLaunchWithoutAReportIsRemovedAfterP2A04`, which checks a method name only.

## OCR

- `npm view @alibaba-group/open-code-review@1.13.0 dist.integrity` exited 0 and returned `sha512-H35yl2HwU7rAIcsnSa/CaDUAUJ3yZKLBpQU5XXwtBEeB8RVAXYrzqDVb+7QQmKTLMuzBO9N3v9dSibGv5NIo9w==`. That **equals** the pinned integrity.
- `npm install -g @alibaba-group/open-code-review@1.13.0` exited 0 ("added 2 packages in 2s").
- `ocr --version` exited 0 and printed `open-code-review v1.13.0 (1672852) linux/amd64`, built 2026-10-13T09:55:57Z.
- `ocr delegate preview --from 7d97a33 --to a03a760` exited 0. It listed 7 reviewable files out of 13. It excluded `CHANGELOG.md` (unsupported_ext) and the 5 test files (default_path).
- `ocr delegate rule <file>` exited 0 for each of the 7 files. Each returned the same 141-line rule set: "Rule Group 1: system / `**/*.{kt,kts}`", with only the "Applies to" line differing. The sections are:
  1. Null safety / dead code
  2. Conciseness
  3. Collections
  4. Coroutines
  5. Class design
  6. Resource and scope functions
  7. Performance
  8. Java interop
  9. Other key points

### Per-file OCR section

| File | OCR rule group | Rule-driven observations |
|---|---|---|
| `MainActivity.kt` | system kt rules | Coroutines (§4): the sync runs in `LaunchedEffect`, which is structured. `ProfileStore.load`'s `runCatching` also swallows `CancellationException`, which is harmless here (a null profile is a no-op). §7: a new `AlertServiceControl` is created on every recomposition; trivial, but `remember` would be cleaner. No null-safety issues. |
| `Shell.kt` | system kt rules | `syncMonitoring` is a clean `when`. Sealed/interface design is fine (§5). No findings. |
| `alerts/AlertService.kt` | system kt rules | §4 / §5: `AlertInbox` is a global singleton holding mutable state that both threads write without atomicity (F3). `AlertFeed` lifetime and state handling is F2. `@Volatile` feed is fine. |
| `panel/LineupPanel.kt` | system kt rules | §4: `rememberCoroutineScope` ties the routing report to the composition (F4). Layout overflow is F1 (outside OCR's rule set). Dead code: none. |
| `panel/PanelModel.kt` | system kt rules | §3: `asReversed().mapNotNull{}.take(3)` runs `AlertPresenter.text` on up to 20 items; that is fine at this size, though `asSequence()` would avoid it. §5: sealed `AlertCommand` / `FocusTarget` use is good, and the `when` is exhaustive. Key-binding coverage is F6. |
| `watch/WatchActivity.kt` | system kt rules | §4: the ad-hoc `CoroutineScope(SupervisorJob()+Main)` is never cancelled, which is the leak in F5. The intentional detach is documented. |
| `watch/WatchLauncher.kt` | system kt rules | §1: null handling is safe throughout, with no `!!`. §4: `CancellationException` is rethrown correctly in `watchAlert` and in the report. §7: the `PACKAGE` regex is a companion constant, not built in a loop. Dead code: none. `launchSpec` runs twice per launch (in `verifiedLaunch` and `start`); that is intentional defence-in-depth. |

## Commands and exit codes

| Command | Exit | Note |
|---|---|---|
| `git fetch origin afc/g5-tv-wiring main` | 0 | |
| `git diff --stat 7d97a33 a03a760` | 0 | 13 files, +640/−35 |
| `npm view @alibaba-group/open-code-review@1.13.0 dist.integrity` | 0 | integrity matches |
| `npm install -g @alibaba-group/open-code-review@1.13.0` | 0 | |
| `ocr --version` | 0 | `open-code-review v1.13.0` |
| `ocr delegate preview --from 7d97a33 --to a03a760` | 0 | 7/13 reviewable |
| `ocr delegate rule <file>` (×7) | 0 each | |
| `./tv-app/gradlew -p tv-app testDebugUnitTest --offline` | 1 | No cached version of `compose-compiler-gradle-plugin:2.4.21` / `gradle-pitest-plugin:0.2.27` for offline mode |
| `./tv-app/gradlew -p tv-app testDebugUnitTest` | 1 | See GAP-1 |

### GAP-1 (typed): TOOL_UNAVAILABLE / NETWORK_POLICY, so tv-app unit tests were not run

- The exact command `./tv-app/gradlew -p tv-app testDebugUnitTest` failed with exit 1:

  ```
  Could not resolve com.android.tools.build:gradle:9.3.1.
    Could not GET 'https://dl.google.com/dl/android/maven2/com/android/tools/build/gradle/9.3.1/gradle-9.3.1.pom'. Received status code 403 from server: Forbidden
  ```

  The same 403 came back for `kotlin-gradle-plugin:2.4.21` and `compose-compiler-gradle-plugin:2.4.21`.
- The environment also has no Android SDK (`ANDROID_HOME` / `ANDROID_SDK_ROOT` are unset, there is no `tv-app/local.properties`, and no SDK under `/opt` or `~/Android`).
- The JDK is 21.0.12, not the requested 17.
- I therefore did not run the tests. The review is static, and I make no claim that the tests pass.

## Remaining risks (not findings)

- The author's known risks still stand:
  - the backend serves no route yet, so every live Watch reports `accessUnknown` with no launch;
  - Compose, Activity, Service and Intent code is not exercised by host tests;
  - monitoring re-syncs only on navigation;
  - a hidden panel hides alerts, which is the only surface under P2-X02.
- A `startForegroundService` followed by `stopService` before the service reaches `startForeground` would crash on API 28+ (see the hunt checklist). I judge it unreachable in practice, but no test guards it.
- A `uri` registry launch accepts any URI scheme for the named package, with no scheme check. This is pre-existing behaviour, and the backend registry's `verified` status is the only gate.
- `watchOutcome` text is never cleared and stays on the panel after later attempts or alerts. This is cosmetic.
- When the profile is unreadable, `PanelController` is built with `visible = true`, whatever the stored `panel.visible` is.
- The device behaviour of `moveTaskToBack` after a fullScreen launch from `WatchActivity` (noHistory, translucent) is not verified on a device.
