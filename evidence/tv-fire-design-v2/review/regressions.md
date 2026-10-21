# TV design v2 repair regressions

Observer: same-session Repair Implementer, 2026-10-21. Synthetic fixtures only; no backend credentials, provider launches or real fantasy data.

The frozen source candidate is `a5c844f331aa1344ba69a480d13e15bd613a70a1`. Its failing loading/local-toggle assertions are in [candidate-regressions-red.txt](candidate-regressions-red.txt); its focused-navigation screenshot and [pixel failure](navigation-safe-zone-red.raw.txt) establish V2-R03. The exact original capture source remains in [candidate-capture](candidate-capture/IndependentV2Capture.kt), loaded by `candidate-capture.init.gradle` when exercising that source revision.

The durable capture source is `capture/IndependentV2Capture.kt`, loaded by `review.init.gradle`. Use the user-scope `afc-tv-v2` emulator at 1920×1080 / 320dpi, with `ANDROID_USER_HOME` and `ANDROID_HOME` set to the configured tools directories. `ANDROID_AVD_HOME` points to the configured Android user home's `avd` directory when starting the emulator. The runner targets `emulator-5584` only.

Build from the repository root:

```sh
cd tv-app
./gradlew :app:assembleDebug :app:assembleDebugAndroidTest -I ../evidence/tv-fire-design-v2/review/review.init.gradle
```

From the repository root, run:

```sh
python3 evidence/tv-fire-design-v2/review/run-repair-captures.py
python3 evidence/tv-fire-design-v2/review/check-navigation-safe-zone.py evidence/tv-fire-design-v2/review/repair/emulator-profile-nav-focus.png
```

The runner checks that its shell fixture uses the production navigation inset, installs the source-built app/test APKs on the emulator, runs 19 tests, captures 20 states and writes SHA256SUMS and app/test logcat under `repair/`. It fails unless all instrumentation tests pass. It is an emulator runner, not a Fire TV route.

The accepted reproducer cases are `panelDataLoaderIsScreenCentered`, `panelProfileLoaderIsScreenCentered` and `localToggleRemainsAvailableWhileLoading`; the first two protect V2-R01. Centring checks the label's actual layout bounds against the default type-ramp group geometry. The local-toggle check additionally operates the control while the profile GET remains held and restores its preference afterward. `panelDataLoadingWithAlert` protects centred loading with an alert, visible D-pad Dismiss focus and successful dismissal. `ProfileDpadFocusTest` remains unchanged.

The pixel checker accepts an image path. With no argument it checks the frozen candidate screenshot and intentionally exits 1; passing the repaired image exits 0. It checks fully opaque accent pixels, so the candidate's x=95 breach is independent of antialiasing.

No repository tests were weakened. No second independent review is claimed. The accepted one-round repair closes through the orchestrator's deterministic verification.
