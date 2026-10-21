# Independent review: REPAIR_REQUIRED

Current repair state: **PASS** for the three accepted findings; see the Repair section below. The original review and frozen receipt are retained as historical evidence.

Observer: Independent Reviewer, fresh session, 2026-10-21. This review did not author the candidate. No repairs, commits, pushes or issue mutations were performed. The reviewer-repairs-own-findings hold is active: stop after this receipt; the dispatching orchestrator accepts findings before resuming this same session for repair.

What this change does: replaces the TV palette, type ramp and focus treatment with a dark gradient, vivid accents and NFL/NBA colours. It adds a shared animated loading presentation and applies colours to the panel, notifications and switching dialog.

## Frozen subject and contract

- Candidate: `a5c844f331aa1344ba69a480d13e15bd613a70a1`, branch `afc/tv-fire-design-v2`.
- Base: `f05bf4bf4b6534646d69a4df7b55ae48d8949796`.
- SHA256 of `git diff --binary f05bf4b..a5c844f`: `954d0ccb7f863574e7246df847b151aaa75f3c90c07f70e7b6ee8c7ab1cdbba6`.
- Frozen binding: `profile-binding-frontend-20261021b.json`, SHA256 `6864e2aa7fc9c004df95b71e209b7dfbed304653622e5089a9d0fe83ed8088bb`. Selected frontend reviewer route retained; no fallback used. Coverage assist enabled/required, executed in delegation mode as explicitly requested by this dispatch. Reverify enabled, with the applicability disposition below.
- Reviewed `packet-v2b-tests.md`, `packet-v2b-impl.md`, and [handoff.md](handoff.md). Owner acceptance: bold colours, dark gradient, distinct NFL/NBA accents, centred loading, unchanged behaviour outside loading presentation, retained 5% safe zone, no added brand assets or implied authorship.
- Machine-readable receipt: [review/receipt.json](review/receipt.json).

## Findings

### V2-R01 — P2, product defect: panel loaders are centred in content fragments

**Locations:** `tv-app/app/src/main/java/com/afc/companion/panel/LineupPanel.kt:267` and `:379` (profile-loading call at `:89`).

**Reachability and proof:** enter Panel while the profile GET or panel GET is pending. `PanelContent` puts the data loader inside a vertically scrolling column, after the alerts and team row, with a 240dp minimum height. Scrolling supplies an unbounded vertical constraint, so the shared `fillMaxSize` cannot make this the viewport. The profile-loading path similarly places the loader after a heading in a Column. Neither centres the loading group in the screen content viewport. The position also changes when alerts are present.

**Reproducer:** build the reviewer capture source through `review/review.init.gradle`, then run `IndependentV2Capture#panelDataLoaderIsScreenCentered` and `#panelProfileLoaderIsScreenCentered`. Both fail on the candidate. At 1920×1080 / density 2, the shared group would put its label centre at y=644px when centred in the viewport: the actual centres are y=567px for panel data and y=701px for panel profile. These assertions allow 8px tolerance. The settings loader supplies the correctly centred comparison.

**Visual evidence:** [panel data loading](review/emulator-panel-data-loading.png), [panel profile loading](review/emulator-panel-profile-loading.png), [panel data with an alert](review/emulator-panel-data-loading-alert.png), [settings loading comparison](review/emulator-loading.png). An alert moves the data loader substantially down the viewport.

**Repair target:** give loading a bounded, viewport-centred layer outside scrolling content. Keep alert actions, team selection, error states and the shared indicator's accessible labels intact. Preserve the defined type ramp and existing navigation.

**Repair write set:** `tv-app/app/src/main/java/com/afc/companion/panel/LineupPanel.kt`; reviewer regression/capture evidence under `evidence/tv-fire-design-v2/review/`. No existing staged test needs weakening.

### V2-R02 — P2, product defect: a local setting now waits for the server

**Location:** `tv-app/app/src/main/java/com/afc/companion/profile/ProfileSettingsScreen.kt:80`–`:88`.

**Reachability and proof:** open Profile/Settings while the profile GET is slow. The new exclusive `if (shown == null) ... else Column` removes `DeviceSettingsControls` from composition until that request completes. On the base, that local control was rendered before `state ?: return@Column`, including while loading. `DeviceSettings.showPanelOnNewAlert` reads/writes app-private preferences and requires no server profile. A customer can no longer change that setting during the pending request. It returns after failure, so this is a loading-time availability regression, not permanent loss of the setting.

**Reproducer:** `IndependentV2Capture#localToggleRemainsAvailableWhileLoading` holds the synthetic profile response and checks for the local toggle. It fails with `Local device toggle must remain reachable while profile GET is pending`. See [candidate regression failures](review/candidate-regressions-red.txt). [Loading](review/emulator-loading.png) has no toggle; [profile error](review/emulator-profile-error.png) shows the same independent control after the request completes.

**Repair target:** preserve the local control's availability while presenting the centred loading indicator for the server-backed portion. Do not change profile data flow or persistence.

**Repair write set:** `tv-app/app/src/main/java/com/afc/companion/profile/ProfileSettingsScreen.kt`; reviewer regression/capture evidence under `evidence/tv-fire-design-v2/review/`.

### V2-R03 — P3, product defect: widest navigation focus crosses the safe zone

**Location:** `tv-app/app/src/main/java/com/afc/companion/ui/theme/Theme.kt:135`; affected caller `tv-app/app/src/main/java/com/afc/companion/MainActivity.kt:84`.

**Reachability and proof:** use the D-pad to focus the left navigation's Profile/Settings button. The new 1.1 scale and 4dp focus treatment exceed the caller's existing inset. At 1920px width the required 5% left boundary is x=96; fully opaque gold pixels begin at x=95. This is a small, one-pixel contract breach, not a claim of unreadable text or substantial clipping. The focused settings-content pill extending left of its own column is otherwise clear of navigation and within the display safe zone.

**Reproducer:** capture `IndependentV2Capture#profileNavFocus`, then run `python3 evidence/tv-fire-design-v2/review/check-navigation-safe-zone.py`. Exit 1: `Focused navigation solid gold left edge: 95px; required safe-zone boundary: 96.0px`. See [screenshot](review/emulator-profile-nav-focus.png) and [assertion output](review/navigation-safe-zone-red.raw.txt).

**Repair target:** reserve sufficient layout space for the rendered navigation focus outline and enlargement, including rounding. Retain the required 1.1 scale and 5% fraction.

**Repair write set:** `tv-app/app/src/main/java/com/afc/companion/MainActivity.kt` (navigation inset); reviewer regression/capture evidence under `evidence/tv-fire-design-v2/review/`. The shared scale contract must remain unchanged.

## Verification and test validity

The candidate source and tracked working tree remained unchanged throughout review. Reviewer Gradle assembly and the JVM test task exited 0; that JVM invocation was UP-TO-DATE, so it is not claimed as a new 310-test execution. The orchestrator's supplied green run and the candidate's red/green records were inspected.

Independent emulator execution passed 14 checks: eleven synthetic capture cases plus the three existing `ProfileDpadFocusTest` cases. Additional alert/loading and navigation-focus captures each passed. The three new behavioural/geometry regression checks intentionally fail on the candidate; the separate safe-zone pixel assertion also fails. [Regression output](review/candidate-regressions-red.txt), [successful run](review/emulator-instrumentation-signed.raw.txt).

The palette/type tests execute the real Compose theme and read real tokens; they are not trivial assertions. Loading tests intentionally inspect source, as allowed by the packet. They prove API/call-site shape, not parent constraints or runtime centring, explaining why V2-R01 escaped. `ProfileLoadingTest` does not assert the local control remains composed, explaining V2-R02. Existing safe-zone tests inspect the inset fraction, not enlarged rendered bounds, explaining V2-R03. The existing compiler-generated lambda-name dependency remains brittle but currently passes; no new failure is established for it.

## OCR: delegation and per-file application

`ocr delegate preview --from f05bf4b --to a5c844f` exited 0: 18 supported files out of 32 changed files. `ocr delegate rule <file>` exited 0 for every listed supported file. [Preview](review/ocr-preview.txt), [complete rules](review/ocr-rules.txt). No OCR tool error or unavailable backend was observed. OCR supplied rules; this reviewer applied them.

Kotlin group K covers null safety/dead code, concise expressions, collections, coroutine lifetimes/error handling, class design, resource closure, allocation costs, Java interop and immutability/string handling. Default group D covers correctness, security, performance, maintainability and test coverage.

| File | Applied rules and result |
|---|---|
| `evidence/tv-fire-design-v2/capture.init.gradle` | D: opt-in test source injection; no production source mutation or new issue. |
| `evidence/tv-fire-design-v2/capture/FireDesignV2Capture.kt` | K: synthetic peers and cleanup traced; captures use direct focus for several states, so additional D-pad checks were run. No independent centring proof in author captures. |
| `evidence/visual/tv-fire-design-v2/SHA256SUMS` | D: all eight author PNG hashes verify; no issue. |
| `tv-app/app/src/main/java/com/afc/companion/MainActivity.kt` | K: shell/client/navigation traced; V2-R03 at the enlarged button's caller. |
| `tv-app/app/src/main/java/com/afc/companion/alerts/AlertNotifier.kt` | K: colour-only notification change; IDs, routes, privacy and cancellation retained. |
| `tv-app/app/src/main/java/com/afc/companion/panel/LineupPanel.kt` | K: fetch cancellation/focus/alert actions preserved; V2-R01. Sport decode normalizes wire values to matching uppercase labels. |
| `tv-app/app/src/main/java/com/afc/companion/profile/ProfileSettingsScreen.kt` | K: callbacks/save race logic preserved; V2-R02. Field traversal passed on emulator. |
| `tv-app/app/src/main/java/com/afc/companion/ui/theme/AfcLoadingIndicator.kt` | K: lifecycle-scoped infinite transition, visible label, finite 80dp drawing; default Android frame-clock motion and disabled-animation checks passed. Parent constraints cause V2-R01. |
| `tv-app/app/src/main/java/com/afc/companion/ui/theme/Theme.kt` | K: shared callers, token contrast, type sizes and focus inspected; V2-R03. No added dependency/font. |
| `tv-app/app/src/main/java/com/afc/companion/watch/WatchActivity.kt` | K: dialog dismissal/continuation and provider-launch flow retained; colour/drawable changes only. Native dialog not visually exercised. |
| `tv-app/app/src/test/java/com/afc/companion/panel/PanelLoadingTest.kt` | K: branch-scoped source checks valid for stated limited contract; no runtime geometry assertion. |
| `tv-app/app/src/test/java/com/afc/companion/profile/ProfileLoadingTest.kt` | K: source-call check valid; does not protect availability of local controls. |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/AfcLoadingIndicatorTest.kt` | K: checks drawing, animation consumption and accessible label in source; parent geometry remains untested. |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemeContrastTest.kt` | K: real colour calculations inspected; extra rendered-background pairs calculated separately below. |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemePaletteTest.kt` | K: real theme values, opacity, luminance, saturation and hue separation; no actionable test defect. |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemeTestSupport.kt` | K: composition/recomposer cleanup retained; reflection missing-API failures explicit; source parser limitations documented. |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemeTypographyTest.kt` | K: actual ramp/family/weight and font-file checks; no actionable defect. |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemeV2FocusTest.kt` | K: actual tokens checked; does not test rendered focus bounds, which allowed V2-R03. |

Unsupported Markdown/text and PNG files were inspected manually. Documentation checklist: observer/evidence labels distinguished; actors for actions identified; dated observations; no credentials, home paths or device address found in changed evidence; prose understandable; capture/build commands are authorized development operations; local evidence links resolve; terminology distinguishes author red-test PASS, green realization and independent acceptance. The unlinked changelog `PR pending` entry needs its real PR link during landing; no PR exists at this review point, so it is not a fabricated or currently broken link.

BRAN: unavailable — no native policy; direct discovery used. BRAN strict was not represented as passing.

## Visual review

### Emulator

AVD `afc-tv-v2`, Android TV API 34 x86, 1920×1080 at 320dpi. Candidate built from the pinned source. First boot attempt failed with `ERROR        | Unknown AVD name [afc-tv-v2], use -list-avds to see valid list.` Explicit `ANDROID_AVD_HOME` resolved discovery. Initial install failed with `INSTALL_FAILED_UPDATE_INCOMPATIBLE`; rebuilding with the configured `ANDROID_USER_HOME` resolved the debug-signer mismatch. The subsequent installs succeeded. These are resolved environment/configuration failures, not candidate defects.

The [review capture source](review/capture/IndependentV2Capture.kt) uses synthetic in-process HTTP responses and mirrors the AppShell content area. Actual D-pad events exercise link/navigation focus, League↔Team traversal, sport focus/toggling, panel row focus and alert focus. Existing edit/IME/Back traversal tests passed. No provider was launched and no account sign-in was performed.

Inspected link, focused settings field/button/navigation, NFL/NBA sport toggles, NFL/NBA panels, an alert, profile loading, both panel loading states, panel loading with an alert, missing-team state, panel error and profile error. All 24 reviewer PNGs have verified [SHA256SUMS](review/SHA256SUMS). Author screenshots are consistent with the candidate's matching synthetic states; reviewer captures are independently generated, not copies of the author's images.

The gradient, gold focus, sport chips and pink alert stripe meet the bold colour direction. Typography and focus are visibly distinct at 1080p; a physical 3m viewing test was not possible. Dense row/field outlines stay unscaled. The focused profile content pill remains within the display safe zone without colliding with navigation; the widest navigation item has V2-R03. Scroll clipping of nonfocused content at the viewport edge is expected.

Independent sRGB calculations give 14.66–14.98:1 for panel text on the 72% surface composited over the gradient stops, 9.97:1 for dense focused text, and 12.59:1 for focused-button text: [contrast.json](review/contrast.json). No contrast defect was found in those rendered combinations.

[LiveLoadingCapture](review/capture/LiveLoadingCapture.kt) uses the real Android frame clock, outside the Compose test clock. At system animator scale 1, three frames differ; at scale 0, all three are identical. Both instrumentation runs pass, and the original setting was restored. [Motion summary](review/emulator-motion-summary.json). This establishes motion/reduced-motion behaviour, not a Fire TV frame-time benchmark.

App/test UID-filtered warning/error logcat was inspected: [emulator-app-logcat.txt](review/emulator-app-logcat.txt). It contains emulator renderer, instrumentation reflection and framework warnings; no AndroidRuntime fatal exception was found. No provider/broadcast frame appears in captured evidence.

### Fire TV — ENVIRONMENT/HARNESS_GAP

The watcher release receipt existed and no active lease existed. An exclusive `v2-review` lease was created atomically, expiring at 22:50Z. Every ADB call ran through the required flock. Candidate and capture APK installs used `-r`; there was no uninstall, data clear or backend/profile-row mutation.

The harness failed all 14 cases with this exact error:

> java.lang.IllegalStateException: No compose hierarchies found in the app. Possible reasons include: (1) the Activity that calls setContent did not launch; (2) setContent was not called; (3) setContent was called before the ComposeTestRule ran. If setContent is called by the Activity, make sure the Activity is launched after the ComposeTestRule runs

[Hardware instrumentation result](review/stick-instrumentation.txt). No review screenshots were produced. The harness did not establish a product failure, hardware visual acceptance, performance acceptance or clean app logcat. No identical retry was made.

Before releasing the lease, the watcher APK was restored with `adb install -r`. Its on-device APK bytes hashed to `0a9bc06b019252278719c2a3bae557ae2d00d6b04f487eae81c692cf53342d78`, matching the required pin. Home was sent and the lease deleted only after verification. [Restoration receipt](review/stick-run.txt).

## Reverify and residual risks

Reverify: not applicable — reviewed subject is source; the APK was built from that source for native exercise, not a vendored/downloaded/shipped binary under independent binary review. The frozen enabled setting was preserved; no Reverify execution is claimed.

No introduced navigation, save-data, provider-routing or credential defect was established. Native notification chrome and the WatchActivity confirmation dialog were reviewed in code but not visually exercised. Fire TV visuals, animation smoothness and physical 3m readability remain unverified because of the hardware harness gap. Compiler lambda-name coupling remains a pre-existing fragility. The orchestrator must replace `PR pending` during landing.

Verdict: **REPAIR_REQUIRED** for V2-R01, V2-R02 and V2-R03. Await orchestrator acceptance and the explicit same-session Repair Implementer transition. No product or repository test edits, commits, pushes or repairs were made.

## Repair — same-session Repair Implementer transition

**Outcome: PASS (realization and deterministic verification).** On 2026-10-21 the dispatching orchestrator accepted V2-R01, V2-R02 and V2-R03, confirmed their reproducers failed on `a5c844f`, and authorized this same reviewer session to perform one repair round. The initial review and [frozen receipt](review/receipt.json) above remain historical records; this is the authorized repair, not another independent review or a publication decision.

| Finding | Implemented fix | Red → green evidence |
|---|---|---|
| V2-R01 | `PanelMessage` now has a bounded full-size Box. `PanelContent` draws its loading layer outside the scrolling Column. During a pending data fetch, controls scroll within the upper quarter, clear of the centred indicator. Focused alert actions scroll themselves into view in that smaller region; normal panels retain whole-card reveal. | The original profile/data label-centre assertions failed at y=701/567px instead of y=644px in [candidate-regressions-red.txt](review/candidate-regressions-red.txt). Both pass in the repaired [19-test run](review/repair/instrumentation.txt). See [profile loader](review/repair/emulator-panel-profile-loading.png), [data loader](review/repair/emulator-panel-data-loading.png), and [loader with alert](review/repair/emulator-panel-data-loading-alert.png). |
| V2-R02 | The pending-profile view keeps the local panel toggle visible above the centred loader. Existing loaded/error settings, callbacks and persistence are unchanged. | The original pending-profile toggle assertion failed in the candidate red run. The repaired test both finds the control and operates it with the D-pad while the GET remains held, verifies the preference changed, and restores the original preference. [Loading with local toggle](review/repair/emulator-loading.png). |
| V2-R03 | Navigation now uses 12dp horizontal and 8dp vertical padding, reserving space for the unchanged 1.1 scale and 4dp outline. | [Candidate pixel assertion](review/navigation-safe-zone-red.raw.txt): x=95, required x≥96, exit 1. [Repaired assertion](review/repair/navigation-safe-zone-green.txt): x=103, exit 0. [Repaired navigation focus](review/repair/emulator-profile-nav-focus.png). The capture runner asserts its navigation inset matches production. |

An added loading-alert prevention check initially exposed competing whole-card and action scroll requests in the smaller loading viewport: [initial failure](review/repair/alert-controls-initial.txt). The same repair round corrected that conflict. The [targeted check](review/repair/alert-controls.txt) and final 19-test run both pass. D-pad focus brings Dismiss fully into view and OK dismisses the alert while loading remains centred: [focused Dismiss](review/repair/emulator-panel-loading-dismiss-focus.png), [after dismissal](review/repair/emulator-panel-loading-dismissed.png). No provider is launched.

The original candidate harness is preserved under [candidate-capture](review/candidate-capture/IndependentV2Capture.kt); the durable repaired regression/capture source is [IndependentV2Capture.kt](review/capture/IndependentV2Capture.kt), with [run instructions](review/regressions.md) and a [machine-readable repair receipt](review/repair/receipt.json). The existing repository JVM and instrumentation test files were not edited. Shared focus scale, palette/type ramp, navigation targets and data-flow code are unchanged. `CHANGELOG.md` retains `PR pending` because no PR number was supplied.

Final verification used `TMPDIR=~/.cache/afc-gate-tmp`, `ANDROID_HOME=~/.local/share/afc-tools/android-sdk`, the configured Android user home and installed JDK 17:

| Command | Result |
|---|---|
| `cd tv-app && ./gradlew :app:testDebugUnitTest --rerun-tasks` | Exit 0; 310 tests, zero failures/errors; all 27 tasks executed. [Log](review/repair-unit.raw.txt). |
| `bash tools/ci/gate.sh tvapp` | Exit 0. [Log](review/repair-gate-tvapp.raw.txt). |
| `bash tools/ci/gate.sh hygiene` | Exit 0; 118 tests. [Log](review/repair-gate-hygiene.raw.txt). Its printed negative-fixture GAP examples are expected test cases, not actual gate gaps. |
| `bash tools/ci/gate.sh docs` | Exit 0. [Log](review/repair-gate-docs.raw.txt). |
| `cd tv-app && ./gradlew :app:assembleDebug :app:assembleDebugAndroidTest -I ../evidence/tv-fire-design-v2/review/review.init.gradle` | Exit 0. [Final source build](review/repair-controls-build-2.raw.txt). |
| `python3 evidence/tv-fire-design-v2/review/run-repair-captures.py` | Exit 0; 19 emulator tests, 20 captures, including the three accepted reproducer tests and existing D-pad edit/IME/Back tests. |
| `python3 evidence/tv-fire-design-v2/review/check-navigation-safe-zone.py evidence/tv-fire-design-v2/review/repair/emulator-profile-nav-focus.png` | Exit 0, x=103px. |
| `cd evidence/tv-fire-design-v2/review/repair && sha256sum -c SHA256SUMS` | Exit 0 for all 20 repaired screenshots. |

Repaired loading, navigation focus and alert-action captures were visually inspected. [Repaired screenshot hashes](review/repair/SHA256SUMS). App/test UID-filtered [logcat](review/repair/app-logcat.txt) has no AndroidRuntime fatal exception; remaining warnings are emulator/framework/instrumentation diagnostics.

**Remaining gap:** the optional Fire TV visual was not run: the stick had an active lease. No device call, hardware instrumentation retry or test-APK install occurred during repair. The prior on-stick test package remains installed as reported by the orchestrator. The original hardware harness gap, physical 3m readability and Fire TV frame-time qualification remain unverified. [Hardware disposition](review/repair/hardware-disposition.json). Reverify applicability remains unchanged: source-built APK exercise, not independent binary review.

Only the three accepted product paths, this receipt, and reviewer evidence were changed. The repair is committed on `afc/tv-fire-design-v2` as directed, without a push. Landing and any later publication remain with the dispatching orchestrator.
