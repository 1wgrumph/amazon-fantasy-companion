# P2-A04 repair — A04-REV-001

Finding: a report transport exception escaped `WatchLauncher.watch()`, swallowing the already
computed outcome and skipping the full-screen `leaveApp()` after a started provider launch.

Fix (`tv-app/app/src/main/java/com/afc/companion/watch/WatchLauncher.kt`): the single
`reportRoutingOutcome` call is now best-effort — `Exception` is swallowed so the known local
outcome is returned and the leave still runs; `CancellationException` is rethrown. Still one
launch and one report invocation per attempt.

Regression: `tv-app/app/src/test/java/com/afc/companion/watch/WatchReportFailureTest.kt`
(new file; frozen `WatchLauncherTest.kt` / `WatchFixtures.kt` untouched).

Red-then-green, same test ids (`WatchReportFailureTest`, 3 tests):

- Baseline (reviewed HEAD): 2 failed — `ConnectException` propagated from `watch()`; cancellation
  test already passed. Review diagnostic likewise exit 1
  (`OFFLINE: outcome=null, calls=[start]`, `AssertionError: report transport failure suppressed
  accessUnknown return and full-screen leave`).
- After fix: all `watch.*` tests pass (17 frozen + 3 new). Review diagnostic rerun against the
  fixed sources (only the reviewed-HEAD byte pin removed): `source-report-repro.txt` exit 0,
  `OFFLINE: outcome=AccessUnknown, calls=[start, leave], exception=none`; frozen JUnit 17/17
  (`source-frozen-junit.txt`).

Frozen hashes (MATCH reviewed values): `WatchLauncherTest.kt`
`00a9a1cb4f2a6a3a5a2960ae69af96e54f12ccdea3f19a7b52a5d94c25e068bb`; `WatchFixtures.kt`
`c9ae38d9ed4450bd0cdc018af1fecb80c82b55f2ab64745f5dc36bb08b4f114f`.

Negative check intact: prior `gameOpened` plus unconfirmed current app stays `accessUnknown`
(frozen test, green). Repository gate result recorded in the handoff result.
