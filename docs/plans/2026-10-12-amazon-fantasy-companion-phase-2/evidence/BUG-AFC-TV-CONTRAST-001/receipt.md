# BUG-AFC-TV-CONTRAST-001 author verification

Assignment: bounded Bug-triager Implementer packet, lifecycle AFC-2026-10-11,
branch `afc/bug-tv-contrast`, baseline `fc206b4af01120cf378fa7063ce7e29b9707c3b0`.
Frozen binding SHA-256: `4950987be8ea55c2525e7f4ab05226712e7720d734ade5b516bee76502308041`.
The owner packet authorizes the regression, theme fix, screenshots and local commit.
OCR remains required for the separately dispatched reviewer; no author review is claimed.
Reverify remains enabled; its narrow binary-symbol checks are in `reverify.json`.
BRAN: unavailable (no native policy); ordinary source discovery used.

## Cause and scope

Product defect, introduced by P2-A01 commit `90e7654`: `AfcTheme` set a dark
background but did not provide TV Material's `LocalContentColor`, whose inherited
default was black. The same root text path is used by NotConfigured, Link,
Profile/Settings and panel headings. Explicit white panel values and Settings
input colors were already legible. The `surfaceVariant = LightGray` override
also made default unfocused button text illegible. Both causes are corrected
in `ui/theme/Theme.kt`; no screen overrides, layout changes or dependencies.

The design's Couch UI check requires 1080p legibility. Historical P2-A01 coverage
reported Theme.kt at 0%; host tests exercised client/contracts rather than the
composed theme. This regression composes the actual theme and reads the actual
inherited color and color scheme. TV Material 1.0.0 ButtonDefaults bytecode was
inspected to confirm its 80% onSurface/surfaceVariant normal-state colors and
onSurface/inverseOnSurface focused and pressed colors.

## Method and regression

Method: test. Pass rule: each active text/color pair >= 4.5:1, also exceeding the
3:1 large-text requirement from [WCAG SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
The test uses Compose's sRGB luminance and alpha compositing, not antialiased
edge pixels. Inactive controls have the standard's inactive-control exemption.
No engine or network is started by the host test; no shared resource group.
Focused green test runtime: 0.620 seconds; no runtime dependency was added.

Test ID (identical red/green):
`com.afc.companion.ui.theme.ThemeContrastTest.inheritedTextOnAppBackgroundMeetsBodyContrast`.
Red executes baseline production source plus only the new test and trace shim;
green executes the unchanged test plus the theme fix. See `red-test.xml` and
`green-test.xml`. Only Android performance tracing is disabled in test sources;
no UI colors, Compose logic or application behavior is mocked.

| Active text | Before | After | Minimum |
| --- | ---: | ---: | ---: |
| Inherited text / NotConfigured / Link / Settings / panel headings | 1.0182116 | 15.97518 | 4.5 |
| Settings input | 15.97518 | 15.97518 | 4.5 |
| Explicit white panel values | 20.624395 | 20.624395 | 4.5 |
| Unfocused button (alpha composited) | 1.7163252 | 6.3519793 | 4.5 |
| Focused button | 10.158843 | 10.158843 | 4.5 |
| Pressed button | 10.158843 | 10.158843 | 4.5 |

## Failure classification

- Test environment: initial host composition hit the Android Trace stub. Added a
  test-only no-op performance trace shim; the same test then exposed the product
  assertion failure. No global Gradle return-default-values setting was enabled.
- Test authoring: TV ButtonColors fields are internal. Test now computes the
  actual pinned defaults from public theme colors and the inspected alpha values.
- Emulator environment: existing test APK had another debug signature. Removed
  only that emulator test installation and installed this worktree's debug APK.
- Reverify targeting: first selected DEX held a ThemeKt reference but not its
  implementation. Inspection located the implementation and provider symbols in
  `classes7.dex`; corrected verification passed with three grounded symbol claims.
  This is binary presence evidence, not semantic contrast proof; the composed
  test and emulator captures supply behavioral evidence.

## Execution status

Focused red: exit 1, assertion reports inherited 1.0182116:1 and button 1.7163252:1.
Focused green plus `assembleDebug`: exit 0. Reverify 0.11.0: exit 0.
Unconfigured APK SHA-256:
`16505dce8c02e102b6d384c029dcf1e57db2e98024548f47d752ad25f8d6e0df`.
Reverify target `classes7.dex` SHA-256:
`ae935f91afefeebb66382fa5a714a17b0aeafb93dc8ab3d4b6f10e3a313c8571`.

Captured and visually inspected all backend-free states at 1920x1080:

- `not-configured-before.png`: reproduced unreadable baseline text.
- `not-configured-after.png`: legible headline and body on the default build.
- `link-offline-after.png`: readable link failure and focused/unfocused buttons.
- `profile-offline-after.png`: readable unavailable profile state and navigation.
- `panel-offline-after.png`: readable panel heading and unavailable message.

For the latter three, built only with `-PafcApiBaseUrl=https://127.0.0.1:1`;
no service was started and no real backend, session or customer data was used.
UI hierarchy assertions confirmed the unavailable messages after D-pad navigation.
The unreachable backend errors are expected negative states, not product failures.
Offline APK SHA-256:
`6c26b699d5d274e0d774230153f528dd70a92ef219218bc63dd4842072ee916b`.
Its `classes7.dex` hash equals the default APK's Reverify target hash above.
The owned emulator was stopped using `adb -s emulator-5554 emu kill` (exit 0).

Full `bash tools/ci/gate.sh`: exit 0; spec, docs, hygiene, tvapp and backend
all PASS. The backend ran 668 passing tests; existing deprecation warnings were
non-fatal. Emulator process exited 0 and `adb devices` reported no devices.

## Commands and exits

Run from the worktree root with the existing user JDK 17 and Android SDK:

| Command | Exit |
| --- | ---: |
| `tv-app/gradlew -p tv-app testDebugUnitTest --tests com.afc.companion.ui.theme.ThemeContrastTest --console=plain` (baseline production) | 1, expected product assertion |
| `tv-app/gradlew -p tv-app testDebugUnitTest --tests com.afc.companion.ui.theme.ThemeContrastTest assembleDebug --console=plain` (fixed) | 0 |
| `bash tools/ci/gate.sh` | 0 |
| `tv-app/gradlew -p tv-app -PafcApiBaseUrl=https://127.0.0.1:1 assembleDebug --console=plain` | 0 |
| `reverify verify <extracted-classes7.dex> --claims-file <claims.json> --json` | 0 |
| `adb -s emulator-5554 install -r tv-app/app/build/outputs/apk/debug/app-debug.apk` (fixed builds) | 0 |
| `adb -s emulator-5554 shell am start -W -n com.afc.companion/.MainActivity` | 0 |
| `adb -s emulator-5554 shell input keyevent 20`, then `23` (each navigation) | 0 |
| `adb -s emulator-5554 exec-out screencap -p` (each PNG) | 0 |
| PNG metadata assertion for all five files | 0, each 1920x1080 |
| `adb -s emulator-5554 emu kill` | 0 |
| `git diff --check` | 0 |

Next action: commit the verified candidate with the normal hook. Independent review and landing remain with the
orchestrator under the packet's explicit stop boundary.


## Limits

These are author verification receipts, not independent review or assurance.
No push, PR, issue mutation or deployment was performed. Backend-connected data
screens, system notification rendering and physical TV hardware were not
exercised; shared text/button colors are covered by the host regression. The
button alpha mapping is pinned to TV Material 1.0.0 and must be rechecked on an
upgrade. No layout or typography redesign was attempted.
