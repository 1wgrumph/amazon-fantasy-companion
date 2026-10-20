# BUG-38-UTP: GRADLE_UTP_VERIFICATION_GAP

## Reproduction

`./gradlew -p tv-app :app:connectedDebugAndroidTest` with
`-Pandroid.testInstrumentationRunnerArguments.class=com.afc.companion.profile.ProfileDpadFocusTest,com.afc.companion.alerts.AlertNotifierDeviceTest`
on base `fb6ab2f` fails before any test executes (`red.txt`, exit 1):

> Dependency verification failed for configuration
> ':app:unified-test-platform-android-test-plugin-host-additional-test-output'
> — 29 artifacts failed verification

Iterating configuration by configuration (scan, admit, re-run) exposed 12
incomplete UTP configurations and 201 missing artifacts in total; every batch
is recorded in `artifacts.md`. No `--tests` option exists on the connected
task, so the class filter rides the instrumentation-runner argument above.

## Origin

`tv-app/gradle/verification-metadata.xml` was generated at P2-A01
(`90e7654`, extended by `f50dd5a`) from the configurations that host work
resolved then: compile, unit test, lint, PIT. No `androidTest` source existed
yet, so no `unified-test-platform-*` configuration was ever resolved and AGP's
UTP host plugins (version 32.3.1, matching AGP 9.3.1) never entered the
metadata. The file already contained exactly one UTP component
(`gradle-work-action-api`), admitted incidentally through another resolution.

## Escape

Device tests arrived later (`455e87c` P2-A03T, `2911c57` for
`ProfileDpadFocusTest`) and were executed on the stick via `adb install` +
`am instrument`, bypassing Gradle's connected task and therefore UTP
resolution. The `tvapp` gate (`tools/ci/gate.sh`) runs
`testDebugUnitTest lintDebug assembleDebug` only; none of those resolves a
UTP configuration, so STRICT verification had nothing to fail on. The gap was
first recorded as `GRADLE_UTP_VERIFICATION_GAP` in
`evidence/P2-A03/device-receipt.json`.

## Classification

Test-only toolchain. All 201 artifacts are host-side UTP / gRPC / Netty /
protobuf runtime pieces and metadata files for the connected-test runner;
none is packaged into the app APK (the APK dependency graph is unchanged —
only `gradle/verification-metadata.xml` changed). No product source edit.

## Fix

Admitted each missing artifact into `gradle/verification-metadata.xml`
(811 added lines, append/augment in the file's existing manual-admission
style, origin "Verified against published checksum (BUG-38-UTP)"). Every
artifact passed `scan-software-supply-chain` before first execution:
official-repo re-download hash match plus published `.sha256`/`.sha1`
match, `clamscan` clean, jar listings free of traversal entries
(`artifacts.md`). Verification stays STRICT with `verify-metadata=true`;
nothing was weakened, trusted, or removed.

One environment defect was found and fixed in place during the first green
attempt: the shared SDK's `build-tools/36.0.0/aapt` lacked the execute bit
(`-rw-rw-r--`), so UTP's APK-installer plugin failed with
`Exec failed, error: 13` and the Compose test activity never launched
(`No compose hierarchies found`). `chmod +x` on that one host file (not a
repository change) plus waking the stick made the identical UTP run pass;
the same class independently passed via `am instrument` (OK, 3 tests),
confirming the failure was environmental, not a test or product defect.

## Prevention check

`resolve-utp.init.gradle.kts` (in this directory) registers
`:app:resolveUtpConfigurations`, which resolves every
`unified-test-platform-*` configuration — resolving artifacts is what
STRICT verification checks. Demonstrated both ways:
`prevention-resolve-utp.txt` (fixed metadata: 13 configurations verified,
BUILD SUCCESSFUL) and `prevention-negative-control.txt` (pre-fix metadata
restored from HEAD: exit 1, verification failure).

GAP `PREVENTION_GATE_OUTSIDE_WRITE_SET`: wiring this into
`tools/ci/gate.sh tvapp` (e.g. adding
`-I <init> :app:resolveUtpConfigurations`, or registering the task in
`tv-app/app/build.gradle.kts` and calling it from the gate) is outside this
packet's write set (`tools/` prohibited; build config only if strictly
needed for UTP execution, which the fix itself does not need). Recommended
follow-up: register the task in `tv-app/app/build.gradle.kts` and add it to
the tvapp gate line so an AGP/UTP version bump fails host CI instead of the
next device session.

## Verification

- 5 consecutive `connectedDebugAndroidTest` runs (both classes, 4 tests)
  on the Fire TV stick: `green-run-{1..5}.txt`, all BUILD SUCCESSFUL exit 0.
- `:app:testDebugUnitTest` BUILD SUCCESSFUL.
- Gates and device restore recorded in the packet return.
