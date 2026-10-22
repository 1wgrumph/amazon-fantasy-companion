# Independent side-panel review receipt

**Latest implementation status: F01–F04 REPAIR_IMPLEMENTED; Fire OS overlay mechanics verified; required physical protected-video observation remains pending (G01 below).** The original review and intermediate stops below are preserved as historical evidence.

What this change does: adds a remote-reachable side panel over another app and a separate top-right alert card. Both use app-private foreground-service commands and nonfocusable overlay windows.

**Original independent verdict: REPAIR_REQUIRED — F01, F02 and F03.** At the review stop, no repair, product/test-source edit, commit, push, issue filing or device activation was performed. This receipt freezes the findings; the reviewer stops here under `reviewer-repairs-own-findings`. The dispatching orchestrator must accept the reproductions and authorize any repair transition.

Observer: Independent Reviewer, 2026-10-22 UTC. Review completed approximately 01:53Z. Review subject: `git diff a82157f..5b62b60` in `1wgrumph/amazon-fantasy-companion`, branch `afc/tv-side-panel`.

| Frozen item | Value |
| --- | --- |
| Base | `a82157f160c61889ab73df96a82ba0a66dff070a` |
| Candidate, checked before and after execution | `5b62b60867b74243bfda657e5dbeada0254c64a1` |
| SHA256 of `git diff a82157f..5b62b60 --binary` | `947aa848794e8410861a86aff6d94a92970ae14989073a3e74a53fe242258fb8` |
| Selected binding | `profile-binding-frontend-20261021b.json` |
| Binding file SHA256 | `6864e2aa7fc9c004df95b71e209b7dfbed304653622e5089a9d0fe83ed8088bb` |
| Binding snapshot digest | `31662d160cf4cde814b50bd9c1b73ca0f21b90951fb9060e9f91f05e704861e9` |
| Coverage assist | Enabled and required; resolved to OpenCodeReview 1.13.2 (`55450a9`), available and executed |
| OCR execution | Delegation, explicitly selected by this review packet; this overrides the binding's `own_engine` execution setting for this review only |
| Reverify | Enabled in binding; **not applicable — no binary subject: the APK was built from reviewed source, signature verified and run natively on its pinned hash** |
| BRAN | Unavailable: no repository policy; ordinary source discovery used |

The private binding was read and verified, not changed or copied into this public repository. No live profile replacement or route fallback occurred. The packet's explicit source-review boundary and delegation method were preserved.

## Must fix

### F01 — P1: card-only monitoring lacks the required number and sport

**Location:** `tv-app/app/src/main/java/com/afc/companion/panel/OverlayService.kt:95`; `panel/OverlayModel.kt:148`; `panel/AlertCardOverlay.kt:139` (the latter two paths share the same Java package root).

**Reachability/problem:** Start monitoring with the overlay permission granted, without opening the side panel. `ACTION_ALERTS` starts cards but does not load the selected profile or panel; the controller starts with a null snapshot. Current committed starter payloads have neither `points` nor `sport`. `alertCardNotice` returns `value=NaN, sport=""`; `AlertCardContent` displays only the name. This misses the required player/number and NBA/NFL mark. The same missing-data case applies to an alert whose starter is absent from a previously loaded panel. Hiding a previously shown panel also cancels its data updates, so an old snapshot is not a complete current-data solution.

**Reproducer:** Run the evidence harness `SidePanelReview#independentRuntimeReview`, which sends the real `ACTION_ALERTS` path to a fresh host and then publishes a modeled current `PlayerScore` envelope with `athlete_id`, `name`, `team` and `slot`, without speculative optional fields. Its direct mapping assertions confirm `NaN` and an empty sport; the real window displays `Receiver` alone. The committed `backend/fixtures/alerts/player-score.json` has this same relevant shape. This is a reproduced feature gap, not an environment/network failure.

**Evidence:** [runtime mapping receipt](review/side-panel-review/runtime.txt), [name-only card](review/side-panel-review/card-no-panel-current-envelope.png), [window/focus](review/side-panel-review/card-no-panel-window.txt). The optional NBA fields used in the implementer's screenshot and in this review's queue exercise demonstrate formatting only; they do not establish today's backend delivery.

**Repair target:** Connect card-only delivery to the existing selected-profile/panel data owner, independently of window visibility, and obtain a matching authoritative current player value and sport. Add direct mapping/delivery regression checks for the committed NFL envelope, NBA-compatible envelope, hidden panel, missing/mismatched row, stale snapshot, and selected-team/sport changes. Do not fabricate a number or quietly treat a name-only card as completion. If the existing authority cannot supply a required alert, return `AUTHORITATIVE_NUMBER_SOURCE_UNCONNECTED` as a dependency/owner-decision gap; a new backend contract needs separate authority.

**Bounded repair write set:** `tv-app/app/src/main/java/com/afc/companion/panel/{OverlayService,OverlayModel,AlertCardOverlay,LineupPanel}.kt`; direct regression tests under `tv-app/app/src/test/java/com/afc/companion/panel/`; this slice's evidence. Backend/API changes are excluded from this repair set. The orchestrator must explicitly include the regression tests in the repair packet; this review does not grant writes.

**If skipped:** The primary card-only viewing path does not deliver the owner's requested alert information. This is already declared as an open typed gap in implementation notes, not an accepted residual risk.

### F02 — P1: the nonfocusable panel clips the team total and later players

**Location:** `tv-app/app/src/main/java/com/afc/companion/panel/LineupPanel.kt:260` and `:317`; `panel/OverlayService.kt:155`.

**Reachability/problem:** Compact mode reuses a vertically scrolling column with the total after all rows. The service passes `focused=null`, and the window cannot receive input; the customer cannot scroll it. At 1920x1080 a nine-player lineup shows only about six rows and no team total. Even three rows plus one alert clip the total when the top-right card reduces the panel height. The window rectangles are correct, but required content is inaccessible inside them.

**Reproducer:** In `SidePanelReview#independentRuntimeReview`, load the synthetic nine-row NFL panel, return to the synthetic game with the real remote button, and inspect `panel-nine-rows.png`. D-pad Down and OK increment the game's counter rather than revealing the hidden rows/total. Then switch to three rows and inject two alerts: `card-and-panel.png` clips the total while the card reserves its slot; `panel-restored.png` exposes it again after expiry. No provider app or video is involved.

**Evidence:** [nine rows](review/side-panel-review/panel-nine-rows.png), [remote input still goes to game](review/side-panel-review/panel-input-to-game.png), [three rows plus card](review/side-panel-review/card-and-panel.png), [restored total](review/side-panel-review/panel-restored.png). The implementer's committed `card-and-panel.png` independently exhibits clipping with four rows.

**Repair target:** Make the compact layout keep the team total visible and provide the required lineup information within the actual available height without relying on remote scrolling. Preserve nonfocusability, safe-zone geometry, stale/unavailable formatting and the full-screen default. Add a rendered layout assertion for a realistic lineup, long/stale labels, and card-active height; checking `Box` rectangles or source tokens cannot prove text visibility.

**Bounded repair write set:** `tv-app/app/src/main/java/com/afc/companion/panel/{LineupPanel,OverlayService}.kt`; panel layout regression tests under `tv-app/app/src/{test,androidTest}/`; slice evidence. No full-screen behavior redesign or new input interception.

**If skipped:** The panel cannot show the team total during ordinary use, and clipped content cannot be recovered while watching the game.

### F03 — P2: stopping monitoring leaves an idle foreground overlay service

**Location:** `tv-app/app/src/main/java/com/afc/companion/alerts/AlertService.kt:90`; `panel/OverlayService.kt:108`; `panel/AlertCardOverlay.kt:84`.

**Reachability/problem:** Monitoring starts the card host, but monitoring destruction only detaches the inbox. It never stops the card owner. `cards.active` stays true as long as permission is granted, so the service, ongoing notification, 250 ms timer and inbox collector survive with no panel and no monitoring. Existing queued/current notices are not cleared at that session boundary either. `cards.stop()` is reached only when the overlay service itself is destroyed.

**Reproducer:** `SidePanelReview#monitoringShutdown` starts the real `AlertService`, waits for two synthetic delivered alerts, then calls the real `AlertServiceControl.stop()`. It asserts the inbox is empty. After waiting beyond a card interval with the panel never shown, the filtered service dump still reports `.panel.OverlayService`, `isForeground=true`, `startRequested=true`. A card remains briefly visible after monitoring stops; the queue eventually drains, but the service persists.

**Evidence:** [service/inbox receipt](review/side-panel-review/monitor-stop.txt), [card after stop](review/side-panel-review/after-monitor-stop.png), [idle game after timeout](review/side-panel-review/queued-card-after-monitor-stop.png), [native observation run](review/monitor-instrumentation.txt).

**Repair target:** Pair monitoring's card start with an app-private card-stop/session reset. Clear current/pending cards and dedup state at the monitoring boundary; stop the host when neither cards nor panel need it. Preserve a deliberately visible side panel. Add a lifecycle regression covering stop with the panel hidden and stop with the panel shown.

**Bounded repair write set:** `tv-app/app/src/main/java/com/afc/companion/alerts/AlertService.kt`; `tv-app/app/src/main/java/com/afc/companion/panel/{OverlayService,AlertCardOverlay}.kt`; panel/alert lifecycle regression tests under `tv-app/app/src/{test,androidTest}/`; slice evidence.

**If skipped:** A background foreground-service notification and timer remain after the customer has stopped monitoring. The implementer's declaration documents this behavior but does not approve it.

## Verification and visual observations

Observer for all runs below: Independent Reviewer, 2026-10-22 UTC.

| Check | Result / evidence |
| --- | --- |
| `bash tools/ci/gate.sh tvapp` | PASS, exit 0; [output](review/gate-tvapp.txt) |
| `cd tv-app && ./gradlew :app:testDebugUnitTest --rerun-tasks` | PASS, exit 0; 344 tests, 0 failures/errors/skips, JUnit XML counted; [output](review/unit-tests.txt) |
| Review APK and instrumentation build | PASS; [initial build](review/build.txt), subsequent builds in the same evidence directory |
| `apksigner verify` on installed source APK | PASS, exit 0 |
| Native observational harness | Three separate selected-method runs: `independentRuntimeReview` 61.196 s, `monitoringShutdown` 16.184 s, `fullScreenWithoutOverlay` 5.868 s; each `OK (1 test)`; these assert observations, not overall product acceptance |
| Candidate screenshot checksums | All six original PNGs matched their committed SHA256SUMS |
| `git diff --check a82157f..5b62b60` | PASS, exit 0 |
| OCR delegation | Preview plus rule retrieval for every one of the 26 changed files; supported selection 14 files; per-file application below |

Environment: dedicated AVD `afc-tv-review`, emulator serial `emulator-5596`, Android TV API 34 x86 system image revision 3, 1920x1080 at 320 dpi. This AVD was created for the review; no other agent's AVD or physical stick was operated. The review APK used only `-PafcApiBaseUrl=https://review.invalid`; the instrumentation intercepts URL connections in-process with synthetic responses. Product sources, production manifest, transport policy and committed test sources were unchanged. No cleartext exception, backend service, real credential or provider app was used.

Installed source APK SHA256: `845ade9e9eff71e0c8be4685f5dcdbd7bb9e1869a25be2b3a1cfd1d119656643`. It was signature checked, then run with the evidence-only test APK. The test APK's exported synthetic game Activity is not part of the product manifest or source APK.

Reproduction commands, after normal Android/JDK environment setup:

```sh
cd tv-app
./gradlew -I ../evidence/tv-side-panel/review/review.init.gradle \
  -PafcApiBaseUrl=https://review.invalid :app:assembleDebug :app:assembleDebugAndroidTest
cd ..
adb -s emulator-5596 install -r tv-app/app/build/outputs/apk/debug/app-debug.apk
adb -s emulator-5596 install -r tv-app/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
adb -s emulator-5596 shell am instrument -w -r \
  -e class 'com.afc.companion.review.SidePanelReview#independentRuntimeReview' \
  com.afc.companion.test/androidx.test.runner.AndroidJUnitRunner
```

Run `#monitoringShutdown` and `#fullScreenWithoutOverlay` in separate instrumentation invocations. Output files are written to the target app's external files directory under `side-panel-review`; pull that directory into `review/`. The harness itself grants/revokes overlay permission through emulator appops. This is a manual observation harness, not a committed product regression suite or a repeated/concurrent engine qualification.

- Permission denial: D-pad/OK opened Android TV's overlay settings; returning showed the manual instructions. The host did not crash. Background card arrival did not request permission or launch an activity. Missing-handler protection was reviewed in source (`runCatching`); a handler-less Fire OS build was not available.
- Focus/task return: Show over game returned to the Java synthetic game Activity. Its visible key counter increased from 0 to 2 under the side panel, and to 3 under the card. Filtered window records retain game focus and both windows' `NOT_FOCUSABLE | NOT_TOUCHABLE` flags.
- Geometry: card `[1644,54,1824,234]` (180 square), normal panel `[1344,54,1824,1026]`, reserved panel `[1344,245,1824,1026]`. All lie in the 5% safe zone, panel width 25%, card-panel gap 11 px. No window overlap observed; F02 concerns content clipping inside the panel.
- Queue/timeout: observed NFL first, optional-field synthetic NBA second, one card at a time, disappearance and panel restoration. Unit tests establish exact 5,000 ms boundary, full interval after delayed promotion, current/queued/expired ID deduplication, and `clear` reset. Runtime tick granularity is 250 ms, so wall-clock removal can lag expiry by a tick.
- Compose lifecycle: both window types install lifecycle/saved-state owners before attachment and advance their registry; successful normal add/remove cycles worked. `onDestroy` hides panel/cards and cancels scope. The card's failed-add branch does not destroy its newly constructed owner, but no attached view/composition or retained resource leak was demonstrated; no speculative finding is raised for that path. Display-loss/remove-failure paths were read, not fault-injected.
- Security: `.panel.OverlayService` is unexported, unbound, and invoked by explicit class-targeted intents with fixed actions. No external extras/new network endpoint or credential logging was introduced. Both windows are nontouchable and cannot capture game input. No demonstrated exported-service or intent-injection defect was found.
- Full-screen panel: the extracted refresh loop retains prior fetching, cancellation/error handling and one-second stale ticks; `compact=false` retains the existing team selector, horizontal rows and Watch/Dismiss. [Clean native screenshot](review/side-panel-review/full-screen-clean.png) and 310 pre-existing passing tests support preservation. `full-screen-panel.png` from the earlier observation deliberately still has the separate overlay enabled; it is not the clean renderer comparison. Provider Watch execution was not attempted.
- The declared toggle/profile-load race did not reproduce with a three-second delayed profile load plus `ACTION_ALERTS` while permission was granted; no finding is based on that declaration alone.

## Test validity and detection gaps

The new pure controller, geometry, queue and text tests are meaningful for their stated boundaries. Reflection makes the original feature-red assertions compile before implementation. No tests were weakened. The 34 new tests all pass, as do the 310 existing tests.

The source-contract tests prove named wiring exists; they do not execute its values or rendered visibility. In particular, `cardRendersOnlyPlayerNumberAndASmallSportMark` counts two `Text` calls and a formatter token: it passes when the actual number is `NaN` and sport is empty. `overlayUsesTheSameSnapshotAndFormattingForNflAndNba` checks identity of a supplied pure controller, not the service's card-only data loading. The renderer contract finds a team-total source token even when that node is offscreen. The destroy contract checks overlay-service destruction, not monitoring-to-overlay ownership. These are the escape paths for F01–F03. Direct `alertCardNotice` and rendered compact-layout regressions are required with their repairs; their absence is not hidden by the green gate.

The original red evidence is explicitly an expected feature-red run on the base, not a candidate defect. No nested bug-triage workflow or issue was opened by this assigned reviewer.

## OCR per-file application

`ocr delegate preview --from a82157f --to 5b62b60` is saved as [ocr-preview.txt](review/ocr-preview.txt). `ocr delegate rule <file>` was executed for all 26 paths, with exit 0, saved as `review/ocr-rule-01.txt` through `-26.txt` in diff order. OCR supplies rules, not an independent verdict. Kotlin rules covered null safety, coroutines, resource ownership, collection behavior, interoperability and tests; default rules covered correctness, security, performance, maintainability and coverage. Unsupported prose/binaries in the preview were manually reviewed; default rule output does not turn them into supported OCR coverage.

### `CHANGELOG.md`

Manual prose/default-rule application: entry matches the intended feature and uses packet-required `PR TBD`. Actual acceptance is blocked by F01–F03, not established by the entry.

### `evidence/tv-side-panel/green.txt`

Manual evidence review: passing test/gate claims are dated and observer-labeled. No private home path or credential was found. Passing source contracts do not close F01–F03.

### `evidence/tv-side-panel/handoff.md`

Manual prose review: baseline and expected-red status distinguish historical from current facts. Complete item-7 data obligation remains explicit; no permission to omit number/sport is inferred.

### `evidence/tv-side-panel/implementation.md`

Manual prose review: accurately discloses missing data and service lifetime. Its optional-backend-fields table is a proposal, not verified wire authority or acceptance of the missing feature.

### `evidence/tv-side-panel/red.txt`

Manual evidence review: assertion-red baseline, not compile failure or new bug. Commands/results align with the handoff; no secret/private home path found.

### `evidence/tv-side-panel/visual-check.md`

Manual prose review: emulator/synthetic limits are explicit. The temporary cleartext-enabled evidence APK is disclosed. Screenshots are not proof of Fire OS or actual NBA payload delivery.

### `evidence/visual/tv-side-panel/SHA256SUMS`

Default rules applied: six relative screenshot paths resolve and every hash verifies. No source APK hash is implied by these image checksums.

### `evidence/visual/tv-side-panel/alert-card-over-game.png`

Manual visual review: compact top-right NBA card, safe-zone placement, synthetic game label. Optional-number payload is insufficient evidence for current envelopes (F01).

### `evidence/visual/tv-side-panel/card-and-panel.png`

Manual visual review: card and window rectangles avoid overlap; lower lineup/total content is clipped (F02).

### `evidence/visual/tv-side-panel/panel-restored-after-card.png`

Manual visual review: panel returns upward; team total appears near the bottom, progress is clipped. Short lineup example does not cover realistic row counts (F02).

### `evidence/visual/tv-side-panel/permission-missing-hint.png`

Manual visual review: permission instructions and remote button are legible. No credential, link code or customer data appears.

### `evidence/visual/tv-side-panel/permission-settings-route.png`

Manual visual review: real Android TV special-access screen, Companion selected, permission denied. Fire OS remains pending.

### `tv-app/app/src/main/AndroidManifest.xml`

Default correctness/security rules applied: permission declared; service unexported with dataSync type and required foreground permissions. No new exported product component.

### `tv-app/app/src/main/java/com/afc/companion/MainActivity.kt`

Kotlin rules applied: explicit control path and permission-aware task return. D-pad/OK activation and denial instructions exercised without a crash. Settings fallback is bounded and explicit.

### `tv-app/app/src/main/java/com/afc/companion/alerts/AlertPresenter.kt`

Kotlin rules applied: visibility expansion of the existing safety predicate; its implementation is unchanged. Card name/number formatting reuses the existing unsafe-claim boundary.

### `tv-app/app/src/main/java/com/afc/companion/alerts/AlertService.kt`

Kotlin coroutine/resource rules applied: start is contained against synchronous overlay-start failure, but no paired card stop exists at monitoring destruction (F03).

### `tv-app/app/src/main/java/com/afc/companion/panel/AlertCardOverlay.kt`

Kotlin resource/null-safety rules applied: separate nonfocusable window, monotonic queue ticks, installed Compose owners, and successful normal removal. Name-only fallback violates F01; session stop is unpaired in F03.

### `tv-app/app/src/main/java/com/afc/companion/panel/LineupPanel.kt`

Kotlin correctness/coroutine rules applied: shared update extraction preserves prior loop semantics. Compact branch needs actual visibility testing; its inaccessible scroll content is F02. Default full-screen branch retained.

### `tv-app/app/src/main/java/com/afc/companion/panel/OverlayModel.kt`

Kotlin boundary/collection rules applied: geometry and pure queue satisfy tested supported display sizes/times. The untested alert-to-notice mapping accepts absent authority as NaN/empty sport (F01).

### `tv-app/app/src/main/java/com/afc/companion/panel/OverlayService.kt`

Kotlin lifecycle/coroutine rules applied: explicit intents, main-owned windows and cancellable panel refresh. Card-only path never obtains a snapshot (F01); card activity never ends with monitoring (F03); compact renderer cannot recover overflow through input (F02).

### `tv-app/app/src/test/java/com/afc/companion/panel/AlertCardContractTest.kt`

Kotlin/test rules applied: meaningful pure geometry, numeric safety, FIFO, boundary, delayed timer, dedup and reset assertions. Constructed notices bypass real alert mapping; F01 requires a separate mapping regression.

### `tv-app/app/src/test/java/com/afc/companion/panel/AlertCardIntegrationContractTest.kt`

Kotlin/test rules applied: useful source-level safety/wiring checks, but text-node/token assertions miss blank sport/NaN and monitoring shutdown (F01/F03). No runtime layout proof is claimed.

### `tv-app/app/src/test/java/com/afc/companion/panel/OverlayControllerTest.kt`

Kotlin/test rules applied: denied/granted/idempotent paths and supplied-controller state tested without sleeps/shared resources. Snapshot identity assertion does not demonstrate background service data acquisition (F01).

### `tv-app/app/src/test/java/com/afc/companion/panel/OverlayIntegrationContractTest.kt`

Kotlin/test rules applied: manifest/explicit-intent/nonfocusability/shared-renderer/destruction tokens are anchored to relevant blocks. Total-source token does not prove compact visibility; monitoring-to-host stop not covered (F02/F03).

### `tv-app/app/src/test/java/com/afc/companion/panel/OverlayTestSupport.kt`

Kotlin/null-safety rules applied: exact reflective API lookup, target exceptions unwrapped, relative repository fixture paths. No new shared engine resource, nondeterministic wait or fixture mutation.

## Evidence hygiene and limits

Mixed-change prose checklist: (1) observer/evidence labels reviewed, (2) action/pending actor distinguished, (3) time-bound statements dated, (4) candidate prose/logs checked for credentials, private home paths and personal contacts, (5) plain technical language, (6) commands read and relevant ones executed on the isolated emulator, (7) local relative evidence links/checksums resolve, (8) panel/card/monitoring terminology checked. No raw session transcript, private binding contents or production data was saved. Existing attribution emails in Git history were not copied into evidence.

Initial capture failure was **harness-only**: a Kotlin Activity in the separate test APK could not load `kotlin.jvm.internal.Intrinsics`; pointer clicks also did not activate TV buttons. The corrected Java Activity and D-pad/OK path passed. Initial screenshots were discarded; no product finding or issue is based on that failure. The unrelated Link screen's synthetic unexpected-response text in permission captures is because this harness does not implement link-code responses; it is not a reported Link defect. The evidence-only harness is retained for reproducibility.

The reviewer-created emulator was stopped after collection. Screenshot hashes and evidence-file hashes are in [review/SHA256SUMS](review/SHA256SUMS); verify from `evidence/tv-side-panel/review/`. No candidate tracked file changed.

**Pending, actor: orchestrator/device acceptance operator:** Fire OS 8 permission routing, foreground start from real monitoring, actual NBA/NFL payloads and real provider playback/remote continuity. The stick was unavailable under the separate watcher lease until 03:30Z; it was not accessed. This is an explicit later device step, not an emulator PASS or a new requirement to obtain the stick now. Long-session soak, permission revocation during add/remove and display-loss fault injection were not run. No new security gate or protection is requested by this review.

**Stop disposition:** receipt persisted; await orchestrator finding acceptance and explicit same-session repair transition. No repair budget was spent by this review.


## Repair — authorized same-session Repair Implementer transition

Owner/orchestrator acceptance dated 2026-10-22 approximately 02:25Z explicitly accepted F01, F02 and F03, included the regression tests under `tv-app/app/src/{test,androidTest}/` and `AlertService.kt`, and authorized this same reviewer session to transition to **Repair Implementer**. That transition is now exercised. The frozen frontend binding and spent review budget remain unchanged; backend/API remain excluded. This section is implementation evidence, not a new independent-review PASS. No push or stick operation is authorized or performed.

**Prior stop at `e23a71c`: F01–F03 REPAIR_IMPLEMENTED; REPAIR_REQUIRED for newly observed F04.** See the authorized F04 continuation below for the latest implementation status. The historical review findings above remain intact for independent acceptance of the repair. F04 is the additional observed transition case below; no extra product repair was undertaken.

| Finding | Implemented repair | Regression proof |
| --- | --- | --- |
| F01 | Hidden-card delivery loads the selected profile and its matching panel snapshot through the shared panel endpoint/decoder, independently of panel visibility. The selected team/sport is re-read on delivery. Optional `triggerContext.sport`, `starters[0].shortName` and finite `points` are accepted; otherwise only fresh, dated, matching row points and a known sport are used. No missing number becomes a name-only card. Unresolved notices produce `AUTHORITATIVE_NUMBER_SOURCE_UNCONNECTED` without payload logging. | `AlertCardMappingTest`: committed NFL fixture, optional NBA fields, absent/mismatched authority and stale/undated data. `OverlayLifecycleTest`: real hidden-window service delivery across selected team and sport changes. |
| F02 | Compact mode has its own bounded layout: fixed visible team total/progress and automatically rotating five-second lineup pages sized to the measured remaining height. Two-line names and stale/unavailable formatting are retained. Remote input and the full-screen default branch are unchanged. | `CompactPanelLayoutTest`: nine rows, long name, stale points, active alert and the observed card-reserved 480×780 px bounds at density 1.3; total remains visible and the last row appears without input. |
| F03 | Monitoring destruction sends an explicit app-private card-stop command. The host clears current/pending cards and session dedup state, removes the card window, and stops when no panel remains; a visible panel survives until deliberately toggled off. | `OverlayLifecycleTest`: real monitoring shutdown with a hidden panel, plus preservation and eventual shutdown of a visible panel. Existing pure queue tests cover clear/reset. |

Product write set used: `tv-app/app/src/main/java/com/afc/companion/alerts/AlertService.kt` and `tv-app/app/src/main/java/com/afc/companion/panel/{OverlayService,OverlayModel,AlertCardOverlay,LineupPanel}.kt`. Regression additions: `panel/AlertCardMappingTest.kt` under `test`, and `panel/{CompactPanelLayoutTest,OverlayLifecycleTest}.kt` under `androidTest`. No product manifest, exported surface, backend, API, dependency, profile binding or full-screen renderer change.

### Repair verification

Observer: Repair Implementer, 2026-10-22 UTC. Owned AVD `afc-tv-review`, `emulator-5596`; same isolated Android TV API 34 environment as the review. A cross-process host lock serializes native runs. Synthetic HTTPS responses use the current committed alert shape and selected-profile/panel authority; no provider app, credential or real backend is used. The synthetic game Activity belongs only to the evidence test APK.

| Command/check | Result |
| --- | --- |
| Candidate `5b62b60`: `./gradlew :app:testDebugUnitTest --tests com.afc.companion.panel.AlertCardMappingTest` | Expected red, exit **1**, 4 tests / 2 assertion failures; [red mapping](repair/red-mapping.txt). |
| Candidate `5b62b60`: build APKs with final regression fixtures; install and instrument the two new native classes | Build exit **0**; 4 tests / **4 assertion failures**, covering missing total, hidden-card number and both host shutdown cases; [red build](repair/red-build.txt), [red native](repair/red-native.txt). Product files were restored from the pinned commit for this build, then the repair was reapplied before green compilation. |
| Repair `./gradlew -I ../evidence/tv-side-panel/repair/capture.init.gradle -PafcApiBaseUrl=https://review.invalid :app:testDebugUnitTest :app:assembleDebug :app:assembleDebugAndroidTest` | Exit **0**; 348 unit tests, 0 failures/errors/skips; [green build](repair/green-build.txt). |
| Repair `adb -s emulator-5596 shell am instrument -w -r -e class com.afc.companion.panel.CompactPanelLayoutTest,com.afc.companion.panel.OverlayLifecycleTest com.afc.companion.test/androidx.test.runner.AndroidJUnitRunner` | Shell exit **0**, parsed `OK (4 tests)`; [green native](repair/green-native.txt). Android's final instrumentation code is -1 for both JUnit outcomes, so the receipt uses assertion counts, not that code as a PASS. |
| `TMPDIR=~/.cache/afc-gate-tmp ANDROID_HOME=~/.local/share/afc-tools/android-sdk bash tools/ci/gate.sh tvapp` | Exit **0**; strict dependency verification, unit tests, lint and APK build; [TV gate](repair/gate-tvapp.txt). |
| Same environment, `bash tools/ci/gate.sh docs` | Exit **0**; [docs gate](repair/gate-docs.txt). |
| Same environment, `bash tools/ci/gate.sh hygiene` | Exit **0**, 119 host tests; [hygiene gate](repair/gate-hygiene.txt). |
| Signature verification of the installed source APK | Exit **0**; SHA256 `e7dc5633ed1d675466c1e852d49516f6133d8f478609d810504b408ea88f33b1`; [APK receipt](repair/apk.txt). Reverify remains not applicable: the subject is reviewed source, not a supplied binary. |

The executed native fixture was replayed on the pinned candidate after correcting test setup: overlay density, Compose semantics access and the profile's valid Half-PPR setting (NBA scoring basis belongs to the panel response). A later test comment documents the same required build flag. These setup corrections are not product findings; the retained red run has four product-behavior assertion failures. No failed harness run is counted as passing.

Reproduction: build using `repair/capture.init.gradle` and `-PafcApiBaseUrl=https://review.invalid`, install both APKs, grant `appops set com.afc.companion SYSTEM_ALERT_WINDOW allow`, and run `com.afc.companion.review.SidePanelRepairCapture`. It uses the actual remote “Show over game” action, returns to the independent synthetic game, injects a current-shape alert with no optional number fields while the panel is hidden, captures card/panel coexistence and timeout, and checks the full-screen default. Source and native output live under [repair/](repair/).

### Repair residual risks and handoff

Fire OS 8 permission/lifecycle behavior and real provider playback/remote continuity remain **pending** for the separate stick acceptance operator; no stick was accessed. The existing toggle-during-profile-load race and long-session/permission-revocation/display-loss cases were not broadened into this bounded repair. Missing, mismatched or stale own-row authority remains an explicit `AUTHORITATIVE_NUMBER_SOURCE_UNCONNECTED` gap until optional sibling-backend fields supply it; no number is invented. A selected-profile/panel fetch failure suppresses the unresolved card. The sibling backend/API change is not implemented here.

BRAN is unavailable (no repository policy); ordinary repository discovery was used. The original per-file OCR delegation remains review evidence; these repairs require the orchestrator's subsequent independent acceptance, not self-issued review assurance. The repaired APK is source built and does not create a Reverify binary subject. No new review engine round or fallback is claimed.


### F04 — P2: card arrival can overlap the panel during the window move

**Location on repaired source:** `tv-app/app/src/main/java/com/afc/companion/panel/AlertCardOverlay.kt:119`–`:121` and `tv-app/app/src/main/java/com/afc/companion/panel/OverlayService.kt:181`.

**New observation, outside accepted F01–F03:** The card is added before the panel's separate window-layout transaction completes. Android animates the panel move; a capture taken as soon as card semantics exist shows the card covering the old panel header. The immediately following compositor dump has the card at `[1644,54,1824,234]` and panel in transit at `[1344,220,1824,1001]`, despite the requested panel y=245. This is rendered window geometry, not a missing backend field or test assertion/configuration failure. Settled rectangles have the correct gap. The placement callbacks themselves are unchanged from `5b62b60`; this is observed on the repaired source, not claimed to be newly introduced by F01–F03.

**Reproducer:** Run `SidePanelRepairCapture#repairedOverlay` on the owned API 34 AVD with a visible panel and a fresh matching alert. At the `both` alert, capture immediately after `awaitText("Receiver 2.5")`, before `settle()` (as the first capture implementation did). The card's first visible frame overlaps the panel header. The final harness now waits for settling for the requested stable screenshots; the earlier frame and window dump are preserved separately, not discarded or represented as a settled PASS.

**Evidence:** [arrival frame](repair/visual/card-arrival-transition.png), [in-flight compositor geometry](repair/visual/card-arrival-transition-window.txt). This qualifies the earlier review's settled-only no-overlap observation.

**Repair target:** Coordinate card presentation and panel placement so every visible transition frame remains disjoint, including card replacement and dismissal. Verify frame-level arrival/expiry geometry in addition to settled screenshots. Preserve the visible total, safe zone and nonfocusability.

**Proposed bounded write set:** `tv-app/app/src/main/java/com/afc/companion/panel/{OverlayService,AlertCardOverlay}.kt`, direct panel/alert tests under `tv-app/app/src/{test,androidTest}/`, and this slice's evidence. Backend/API remain excluded. At the `e23a71c` stop, F04 had not yet been accepted for repair. The orchestrator accepted it into the same round at approximately 03:18Z; the authorized continuation is below. Accepted F01–F03 repairs and their green results remain delivered.


### Final repair captures and checksums

`SidePanelRepairCapture` completed with shell/verification exit **0**, parsed `OK (1 test)`; [native capture output](repair/capture-native.txt). The final harness advances Compose's test clock for the second lineup page and waits for Android window transitions before the stable geometry captures. Normal card expiry uses monotonic wall time in the service. The transient F04 frame remains separately preserved above. Full-screen team/league and player assertions passed.

Captured on the repair source APK in the owned AVD, 2026-10-22 UTC. Eight affected/new PNGs were captured in this round. The two permission PNGs retain the previously verified candidate captures because permission behavior was unchanged. The total is visible in both normal compact and card-reserved panel captures; the hidden-panel card shows `Receiver 2.5` and NFL from the matching selected-profile row, without optional backend number fields. The game receives the D-pad key while the card is visible. Stable card `[1644,54,1824,234]` and panel `[1344,245,1824,1026]` remain inside the safe zone and disjoint; this does not close F04's in-flight case.

Verify from `evidence/visual/tv-side-panel/` using `sha256sum -c SHA256SUMS`:

```text
61d07d88bb2c48d93347affcc70dd307758e11deffaca24d75fc8e83db54cb0f  alert-card-over-game.png
a715fdcacc7a26e61c8271488534d44ced08f6d26ca97bb567186cf79c7c92f6  card-and-panel.png
87b8e450230e3e59f22926c402b52a14e047d65e0c1edfa3931128b9ca01380d  card-expired.png
b898330857483f2a79d0fedca420173e486a3e8ea583be8d977d1dd008115e1b  card-remote-focus.png
f1552735768853775763ae31636f7c3c977c2f4f2557f30b6baf67f498ac492c  compact-lineup-page-2.png
949263fc5b8cad68da40bb3196827469d0a36b136b1738c5ad29999076b7fc83  full-screen-panel.png
b93e0a236def80f0b51a654b94456e8e675eb37dc6b3eb35c890a35cccab682d  panel-restored-after-card.png
923bedaf3e4e66009434226fdef210fc501d86257c4d0a0060d5dab42f2c161a  permission-missing-hint.png
1ba8e03f518a1a01cbedc449b457ff3cb61de5814f8e475b7685b00fb253eb3e  permission-settings-route.png
d3ed913eaeaba07670fa90db1e5cd6231ccb7ac45199052218dfdf86a54231fb  side-panel-over-game.png
```

Evidence logs were scrubbed of absolute home/worktree paths. No credentials, profile binding copy, raw agent session or provider data were added. Gate hygiene's printed negative-fixture GAP examples are expected assertions inside its 119 passing tests, not unresolved gate outcomes. Original review evidence hashes remain intact; new repair evidence has its own `repair/SHA256SUMS`. Commit identity is Codex, with no Co-Authored-By trailer; normal configured hooks apply. No push was performed. The owned emulator is stopped after collection.

**Historical repair stop at `e23a71c`:** F01–F03 implementation and regressions were delivered for orchestrator acceptance. At that stop, newly observed F04 remained REPAIR_REQUIRED under the finding hold; no fourth repair had started. The accepted continuation below supersedes that implementation status. Fire OS/stick acceptance remains pending with the separately authorized operator.


## Repair continuation — F04 accepted in the same round

**Authority:** Orchestrator acceptance, 2026-10-22 approximately 03:18Z, explicitly accepts F04 and its recorded bounded write set. The same frozen frontend review/repair pair continues as Repair Implementer; this is not a new review, profile selection or review-budget reset. No push or stick access is authorized or performed.

**Current implementation status: F04 REPAIR_IMPLEMENTED; all requested gates exit 0.** The independent-review stop and earlier evidence remain historical records; this continuation supplies repair implementation evidence for orchestrator acceptance.

**Fix:** `AlertCardOverlay.showCard` reserves the card rectangle before adding the card. `OverlayService.onCard` immediately removes and reattaches the existing nonfocusable panel view at its final rectangle, avoiding a move animation through the card's area. Replacement keeps the slot reserved and skips an unnecessary panel reattachment. Final expiry removes the card immediately before restoring the panel. Permission denial/add failure releases the reservation and destroys an uninstalled Compose owner; a panel reattachment failure uses the existing panel cleanup path. The existing view, lifecycle/saved-state owner, panel controller and data-update job are reused. No hidden API, timer delay, animation-scale setting or new resource/dependency is used. The full-screen renderer and input flags are unchanged.

Why reattachment is used: the public movement-animation switch is only available from API 34, while the app also supports older Fire OS versions ([Android LayoutParams API](https://developer.android.com/reference/android/view/WindowManager.LayoutParams#setCanPlayMoveAnimation(boolean))). A synchronous remove/add sequence avoids relying on that newer API or a guessed animation duration.

**Regression:** Added `OverlayLifecycleTest#cardArrivalReplacementAndExpiryNeverOverlapThePanel` to the existing native test class. It uses the real services, selected-profile/current-alert fixtures and the owned API 34 TV compositor, samples only this app's overlay rectangles, injects two queued alerts and follows arrival, replacement and final expiry under a bounded 20 s deadline. It asserts disjoint rectangles and restoration after both five-second cards. Actual owned-frame samples and the baseline failure screenshot are retained. The existing source wiring assertion now recognizes panel reattachment rather than requiring the unsafe live-window move.

**Red proof on pinned `e23a71c05a8aafff8e16c3e2714436de3c239709`:** Product code was unchanged when the regression was built and run. At 503 ms it failed with `card/panel compositor overlap: [[1344, 185, 1824, 966], [1644, 54, 1824, 234]]`. This reproduces accepted F04 using actual compositor output, not an expected negative fixture or network/configuration failure. [Assertion output](repair-f04/red-native.txt), [frame trace](repair-f04/red-frames.txt), [baseline screenshot](repair-f04/red-overlap.png).

**Green proof:** The repair passes all five native panel/layout/lifecycle regressions. The F04 trace contains 357 samples over approximately 10.5 s: 344 two-window samples, all disjoint; six one-window samples and seven samples during surface replacement with no visible owned rectangle. The restored full panel is `[1344,54,1824,1026]`; the card-visible panel remains `[1344,245,1824,1026]` below `[1644,54,1824,234]`. Reattachment can briefly refresh the panel surface during a transition; the test does not claim frame-by-frame video proof or zero rendering interruption. [Native result](repair-f04/green-native.txt), [sample trace](repair-f04/green-frames.txt).

| Command/check | Exit/result |
| --- | --- |
| Baseline build: `./gradlew -PafcApiBaseUrl=https://review.invalid :app:assembleDebug :app:assembleDebugAndroidTest` | **0**; [baseline build](repair-f04/red-build.txt). |
| Baseline instrumentation: `adb -s emulator-5596 shell am instrument -w -r -e class 'com.afc.companion.panel.OverlayLifecycleTest#cardArrivalReplacementAndExpiryNeverOverlapThePanel' com.afc.companion.test/androidx.test.runner.AndroidJUnitRunner` | Shell **0**, JUnit **1 assertion failure** (expected red). |
| Repair build: `./gradlew -I ../evidence/tv-side-panel/repair/capture.init.gradle -PafcApiBaseUrl=https://review.invalid :app:testDebugUnitTest :app:assembleDebug :app:assembleDebugAndroidTest` | **0**, 348 unit tests passed; [build](repair-f04/green-build.txt). |
| Repair instrumentation: `adb -s emulator-5596 shell am instrument -w -r -e class com.afc.companion.panel.CompactPanelLayoutTest,com.afc.companion.panel.OverlayLifecycleTest com.afc.companion.test/androidx.test.runner.AndroidJUnitRunner` | Shell/parsing **0**, `OK (5 tests)`. |
| `TMPDIR=~/.cache/afc-gate-tmp ANDROID_HOME=~/.local/share/afc-tools/android-sdk bash tools/ci/gate.sh tvapp` | **0**; [TV gate](repair-f04/gate-tvapp.txt). |
| Same environment, `bash tools/ci/gate.sh docs` | **0**; [docs gate](repair-f04/gate-docs.txt). |
| Same environment, `bash tools/ci/gate.sh hygiene` | **0**, 119 host tests; [hygiene gate](repair-f04/gate-hygiene.txt). |

Write set used: `panel/{OverlayService,AlertCardOverlay}.kt`, existing `panel/AlertCardIntegrationContractTest.kt` and `panel/OverlayLifecycleTest.kt`, plus the slice's receipt and visual/repair evidence. No backend/API, manifest, configuration, dependency or full-screen source changes.

Fire OS 8 and real-provider/stick acceptance remain pending with the separate operator. The existing selected-profile-load toggle race, long-session soak and permission/display-loss fault cases remain outside this bounded continuation. Missing/stale card authority retains the earlier typed-gap behavior. BRAN remains unavailable; ordinary repository discovery was used. Reverify remains not applicable to the source-built APK, and no additional independent OCR review is claimed for this repair continuation.


### F04 capture and artifact identity

`SidePanelRepairCapture#repairedOverlay` passed (`OK (1 test)`, shell/parsing exit **0**), using the same owned AVD, synthetic non-provider game, real remote button and current-envelope number fallback as the preceding round. [Capture output](repair-f04/capture-native.txt). `evidence/visual/tv-side-panel/card-and-panel.png` was pulled again and the complete visual `SHA256SUMS` was recomputed and checked. Its settled pixels are byte-identical to the prior correct settled frame; the F04 change removes the in-flight overlap rather than changing the final layout.

- Re-captured `card-and-panel.png` SHA256: `a715fdcacc7a26e61c8271488534d44ced08f6d26ca97bb567186cf79c7c92f6`.
- Installed repair source APK SHA256: `3684110e1eff2c5fc08a752e292bd537722a89b8ce21193dba4979defb8b0168`; `apksigner verify` exit **0** ([APK receipt](repair-f04/apk.txt)).
- Fresh settled [card/panel compositor output](repair-f04/card-and-panel-window.txt) and [restored panel output](repair-f04/panel-restored-window.txt) accompany the sampled transition trace. Team total `112.5` remains visible.

No permission/provider/device behavior is inferred from this source-built emulator result. Original review and earlier repair evidence are retained with their existing checksums. The continuation evidence is separately covered by `repair-f04/SHA256SUMS` after sanitizing absolute home/worktree paths. No raw session, credential, private binding or unrelated evidence is included.


### F04 evidence preparation checks

The first full hygiene attempt failed three isolated-fixture tests because their `git ls-files` copies omitted newly untracked evidence linked by this tracked receipt. An initial targeted retry then detected absolute home paths in the retained failed-run tracebacks. These are evidence preparation failures, not product findings. The new evidence was staged and its paths sanitized; the same three tests then passed (exit **0**, `Ran 3 tests`, `OK`). No gate/test implementation or policy was changed. The full gate is rerun on the prepared evidence; failed attempts remain visible as [initial full run](repair-f04/gate-hygiene-attempt1.txt) and [initial targeted run](repair-f04/hygiene-fixture-recheck-attempt1.txt), alongside the [passing targeted recheck](repair-f04/hygiene-fixture-recheck.txt). No failed run is counted as passing.


**F04 repair stop disposition:** REPAIR_IMPLEMENTED for orchestrator acceptance in the same repair round. The full hygiene retry passed all 119 tests (exit **0**); its printed negative-fixture GAP examples are expected assertions, not unresolved outcomes. TV and docs gates also exit **0**. The continuation uses the accepted bounded write set and normal configured commit hooks, with Codex author/committer identity and no Co-Authored-By trailer. No push was performed. The owned AVD is stopped; no stick was accessed. Fire OS 8/provider acceptance and the brief panel surface refresh remain the stated residual limits, not a self-issued independent PASS.


## On-stick visual continuation — PR #157 at `d4fd965`

**Observer and authority:** Codex, same frontend Reviewer session, 2026-10-22 UTC. The orchestrator requested this on-stick continuation of the existing review/repair pair, not a new code-review round. Subject: `d4fd96574f33ab113ba7176c1dd0fefff1d6066c` (the accepted repair plus main). No product or test source was changed for this step.

**Typed outcome: OWNER_DECISION_REQUIRED — G01, required physical protected-video observation unavailable.** The completed Fire OS overlay checks below pass and no new product defect was reproduced. A full visual PASS is withheld because the owner explicitly requested a by-eye check of live video on the physical TV. Fire OS did **not** block overlays: both the panel and alert card rendered, including the panel over YouTube TV. This disposition concerns the remaining observation, not an overlay prohibition.

### Device, lease and preservation

AFTKM / API 30 were read from the stick; Fire OS 8 is the owner-provided platform identity. Its existing 1920×1080 display override and density 320 were retained. The lease was acquired with exclusive creation and a conflict check at **04:21:40Z**, expiry **05:36:40Z**, and released at **04:44:18Z**, well before the 19:30Z hard stop. The active lease was renamed to `stick-lease-sidepanel-review-released.json`, with release time and restoration note. No further stick access followed release.

Before replacement, `pm path` and `dumpsys package` were recorded privately and the installed base APK was pulled to the authorized local restore cache. Installed version: **0.1.0**, versionCode **1**. Its SHA256 was `0a9bc06b019252278719c2a3bae557ae2d00d6b04f487eae81c692cf53342d78`. Original overlay app-op: **default / ungranted**; the original alert monitoring service was running. No account credential, profile or lineup was exported or changed.

The pinned source was built using `-PafcApiBaseUrl=https://review.invalid`. An isolated, locally held instrumentation fixture intercepts HTTPS in memory, using the same synthetic panel/current-alert data as the earlier review; it forwards no request to the real backend and invokes no profile/lineup save. It uses a separate test-only application ID, `com.afc.companion.sidepanel.review`, and the independent synthetic game Activity. The real remote button, overlay service, renderer, queue and timeout remain the source-built candidate's implementations.

Candidate APK SHA256: `f455713c7ac141d76b21f3a2cd34795f1c47537b65b172f1522d4bc624b7f97e`. `apksigner verify --print-certs` succeeded, and both original and candidate signer SHA256 digests matched: `24ba72469642c32f76d0e1ac293817117e6466835b5e75ebe33e38f53eba2d77`. Replacement used `adb install -r`; the owner's app was never uninstalled. Reverify remains **not applicable — source-built candidate verified by signature, pinned hash and native execution**; the preserved original APK is a restoration artifact, not a review subject.

### Observed flows

| Check | Observation |
| --- | --- |
| Permission, before any grant | The real D-pad focused and pressed “Show over game”. Companion remained responsive and showed the manual permission instructions. Fire OS resolved `android.settings.action.MANAGE_OVERLAY_PERMISSION` to `com.amazon.tv.settings.v2/.compliance.CTSDummyIntentHandler`; no “Display over other apps” UI appeared. The native Applications menu had no “Special app access” entry. No crash or grant occurred. [Permission fallback](../visual/tv-side-panel/stick/permission-request.png). |
| Grant | The authorized fallback `appops set com.afc.companion SYSTEM_ALERT_WINDOW allow` worked. The native `Settings.canDrawOverlays` check then passed. This device requires permission provisioning outside the displayed standard Android settings route; UI granting was not demonstrated. |
| Panel over a non-provider app | The actual button returned to the synthetic game with a compact panel at `[1344,54,1824,1026]`. Team total **112.5** remained visible. [Panel](../visual/tv-side-panel/stick/side-panel-over-game.png). |
| Remote input | The foreground game's key counter advanced from 0 to 1 with the panel visible, then to 2 with the card visible. Window focus remained on the game. Both overlay windows had `NOT_FOCUSABLE` and `NOT_TOUCHABLE`. [Panel remote](../visual/tv-side-panel/stick/panel-remote-focus.png), [card remote](../visual/tv-side-panel/stick/card-remote-focus.png). |
| Synthetic alert | An in-memory current-envelope alert, with no optional backend points fields and no production event, displayed **Receiver 2.5 / NFL**. Card rect `[1644,54,1824,234]`; panel rect `[1344,245,1824,1026]`; 11 px gap, inside the safe zone. The total remained visible. No overlap appeared in the captured arrival/coexistence states. [Card and panel](../visual/tv-side-panel/stick/card-and-panel.png). |
| Timeout | The card disappeared **4822 ms after first observed visible**, consistent with its five-second queue timeout. The panel returned to its full compact height without a remote action. [Expired card](../visual/tv-side-panel/stick/card-expired.png). |
| YouTube TV | Opened the existing signed-in viewer, navigated Home → Live guide and opened an available live channel. The panel remained visible over the guide and live player; the D-pad moved the provider selection and opened player controls. No account settings, subscriptions or purchase controls were changed. All provider frames, including the account chooser, remain private and are excluded from this repository. |
| Playback evidence and limit | With the panel over the live player, YouTube TV reported playback state 3 / speed 1.0. SurfaceView presentation samples advanced from `491368321593747` to `491374415606300` ns over approximately six seconds. Protected video was black in ADB captures; these observations support continued playback but do not establish the requested physical by-eye judgment. **G01 remains pending.** |

### G01 — required physical video observation pending

**Classification:** verification gap, not a product repair finding. **Location:** this receipt's YouTube TV playback row; owner-requested on-stick check 5. **Reproducer:** open a live YouTube TV channel with the panel visible and capture through ADB; the panel/player controls are visible but protected video pixels are black. No physical observer supplied a confirmation during this run. The reviewer requested that observation while the live player and panel were on screen; no response was available before restoration.

**Completion target and actor:** the owner/orchestrator arranges a separately leased physical-TV observation confirming that live video continues normally under the panel, or explicitly amends the acceptance method. MediaSession and presentation timestamps are retained as supporting evidence, not silently substituted for the owner's by-eye requirement. **Write set:** this receipt and, if needed, owner-safe non-provider visual evidence only; no product/test/backend/API change is indicated. No repair budget or new review round is claimed.

### Execution validity and restoration

The final `SidePanelStickReview#onStick` instrumentation run parsed **`OK (1 test)`**, 409.336 s, shell exit **0**. It used real D-pad focus through the button's focusable ancestor, actual service-owned windows via the public API-30 `WindowInspector`, and independent screenshot judgment. Early setup probes were excluded: the initially sleeping display, a competing UI Automation connection, checking focus on a text child instead of its button, and a foreground-only accessibility text lookup for a nonfocusable overlay. They are not product failures or passing evidence. The final native window count, screenshots and remote counter establish the panel/card results; the JUnit result does not close G01.

`assembleDebug` / `assembleDebugAndroidTest`, APK signature verification, installation, final instrumentation and restoration all exited **0**. `TMPDIR=~/.cache/afc-gate-tmp ANDROID_HOME=~/.local/share/afc-tools/android-sdk bash tools/ci/gate.sh docs` exited **0** after receipt finalization. Normal configured commit checks apply. The original per-file OCR delegation remains the source-review evidence; this is the separately requested physical-device visual continuation. BRAN remains unavailable (no native repository policy), so ordinary discovery and the documentation review checklist were used. The added prose identifies its observer, pending actor and UTC dates; commands/links and terminology were checked, and public evidence was checked for account identities, credentials, private paths and device addresses.

Restoration used `adb install -r -d` with the exact pulled original APK. A second pull of the restored installation matched SHA256 `0a9bc06b019252278719c2a3bae557ae2d00d6b04f487eae81c692cf53342d78`; versionName **0.1.0** / versionCode **1** matched BEFORE. Overlay app-op was restored to **default / ungranted**. The original monitoring service was resumed and confirmed running. The review-only APK and generated app-private review files were removed; the owner's app, profile and lineup were retained. Home was confirmed with no overlay window before the lease release. No push was performed.

Public additions are limited to these six non-provider PNGs and their [SHA256SUMS](../visual/tv-side-panel/stick/SHA256SUMS), plus this receipt. Provider images, raw device output, the original APK and the private harness are not committed. No device network address appears in committed evidence.
