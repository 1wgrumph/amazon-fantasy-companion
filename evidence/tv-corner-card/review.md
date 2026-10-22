# Independent corner-card review receipt

The original review below describes `5f8073a` before repair authorization. Current partial-repair status, verification and remaining F01 contract decision are recorded in the Repair section.

**Verdict: REPAIR_REQUIRED — F01–F06.** Candidate `5f8073a539a90cad3ac74b92c33b5166de501e3c` remains unchanged. No product/test-source edits, repairs, commits, pushes, issue filing, stick access, provider launches or publication were performed. The reviewer stops at this receipt under `reviewer-repairs-own-findings`; proposed write sets below are for the dispatching orchestrator, not authority exercised by this session.

BUG_ROUTE: not-a-bug independent review of an owner-requested UI change, under the supplied frontend binding; no nested bug-triage workflow.

Observer: independent Codex reviewer, 2026-10-22 UTC. Subject: `git diff a22031f..5f8073a`, branch `afc/tv-corner-card`.

| Frozen item | Value |
| --- | --- |
| Base | `a22031f21b176ad0f0be49d0eade048f9d0e2576` |
| Candidate | `5f8073a539a90cad3ac74b92c33b5166de501e3c` |
| Binary diff SHA256 | `18c4df3f6ecef288ca8ed87d7ae390c498c3d3e3f2a3e9f1207e581206aae7a5` |
| Binding | `profile-binding-frontend-20261021b.json` |
| Binding file SHA256 | `6864e2aa7fc9c004df95b71e209b7dfbed304653622e5089a9d0fe83ed8088bb` |
| Frozen snapshot digest | `31662d160cf4cde814b50bd9c1b73ca0f21b90951fb9060e9f91f05e704861e9` |
| Reviewer route | Supplied primary Codex CLI / GPT-6.1 Sol / high; no route fallback |
| Test authorship | Separate author skipped by explicit owner decision; accepted as process authority, **not** evidence of independent test oracles |
| Coverage assist | Frozen enabled/required; OpenCodeReview `v1.13.3 (375f64c)` available, executed in delegation mode as this packet explicitly requires |
| Reverify | Frozen enabled; **Reverify: not applicable — APK built from reviewed source, signature verified, hashed and run natively.** |
| BRAN | Unavailable: no native repository policy; ordinary source discovery used |
| Native resource | Owned AVD `afc-tv-review2`, console port 5630, Android 34 TV x86, 1920×1080 at 320 dpi |

The private binding was read without copying or changing it. Its live catalog was not substituted. The packet's delegation instruction takes precedence over the snapshot's `own_engine` OCR mode for this review. Full source/acceptance coverage includes key sequences, state transitions, real window focus/geometry, opacity, the accessibility manifest/configuration, fallback, league identity, and the #157 regressions.

## Findings

### F01 — P1: consuming Menu up after forwarding down leaves the foreground app repeating after release

**Location:** `tv-app/app/src/main/java/com/afc/companion/access/MenuHoldFilter.kt:22` and `:30`; service delivery at `access/MenuHoldService.kt:28`.

**Reachability and reproducer:** Enable the service on the owned AVD, leave the overlay Off, and foreground the synthetic game. Register a uinput remote, send Linux KEY_MENU down, hold 1000 ms, send up, and keep the device registered for another 4000 ms. Run the review harness method `CornerReview#wireShapeAndRelease`; its `hardwareMenu(1000, 4000)` records the exact input. This exercises the compiled candidate, not injected `input keyevent` or a fake filter call.

**Observed:** The card appears, but the foreground receives **93 Menu downs**, including repeat 92 at **5007 ms** after down. Its only up is cancelled (`flags=40`) at **5018 ms**, when the synthetic device disconnects. Physical up was scheduled at 1000 ms. See [event trace](review/release-reproducer-events.txt), [summary](review/release-reproducer.json), [input commands](review/corner-review/remote.jsonl), and [screenshot](review/corner-review/18-nfl-wire-card-after-release.png). This independently confirms a foreground action leak and a stuck key interval, beyond the implementer's reported double handling. The synthetic foreground needs no special behavior: it records ordinary `dispatchKeyEvent` callbacks.

**Cause:** Initial down returns false; held up returns true. Resetting the filter's own fields does not balance the foreground input sequence. Directly feeding repeat events to the pure filter does not model Android's actual dispatch/repeat behavior. The code also consumes repeat events before 700 ms (`:27`), despite the promise that a shorter press passes untouched.

**Repair target:** Preserve a balanced foreground key sequence, unchanged short-Menu behavior, and exclusive ownership of an AFC hold. Prove no action/repeat leakage after physical release with a persistent input device. Merely allowing held up through trades this for a foreground release action and does not satisfy the approved contract. The orchestrator must resolve any route/contract limitation explicitly; this reviewer does not silently accept down leakage or consume all short presses. The timing constant and event-relative timer are 700 ms in source; a fresh native latency measurement was not substituted for this sequence proof.

**Proposed write set:** `tv-app/app/src/main/java/com/afc/companion/access/{MenuHoldFilter,MenuHoldService}.kt`, necessary overlay-control integration under `panel/`, key-delivery regression tests under `src/test` and `src/androidTest`, and the handoff/copy that claims repeats are consumed. Any different input route or fallback needs the orchestrator's contract disposition before repair.

### F02 — P2: the league switcher invents team/league associations

**Location:** `tv-app/app/src/main/java/com/afc/companion/panel/OverlayModel.kt:119`.

**Reproducer:** Supply leagues LeagueA and LeagueB, selected pair LeagueA/TeamA, and distinct actual teams TeamA and TeamB. Hold for the menu, select League, and inspect [requests](review/corner-review/requests.txt) and [the result](review/corner-review/10-league-switched.png). Candidate requests `teamLeague=LeagueB%2FTeamA`, never LeagueB/TeamB, and displays Unavailable. The fixture's known associations are independent of the implementation's cross product.

**Cause/evidence:** Every league is mapped to `selected.team`. `ProfileState` holds one paired selection plus unpaired sets; `LineupPanel.kt:114` already documents why those sets cannot establish more pairs. Backend `panel/__init__.py:297` supplies lineup rows only for a matching stored pair and `:366` explicitly labels a missing lineup. Thus the same-team assumption is not a functional implementation of the requested switcher. A `shortcut:` comment discloses the limit but does not approve it. The new tests assert this same assumption.

**Repair target:** Use actual supported team/league associations and prove a switch between distinct teams. If existing APIs cannot provide them within the no-backend-change contract, return that precise scope decision to the orchestrator; do not manufacture associations or silently drop the requested switcher.

**Proposed write set:** `panel/OverlayModel.kt`, `panel/OverlayService.kt`, relevant switcher tests and evidence. Changing profile storage or backend APIs exceeds the original packet and requires an explicit scope disposition.

### F03 — P2: Expand has no service-off in-app route

**Location:** `tv-app/app/src/main/java/com/afc/companion/panel/OverlayModel.kt:79`; `panel/OverlayService.kt:170`.

**Reproducer:** Disable the accessibility service, use the real in-app Show over game button, then revisit Panel. The card and switch hint work ([card](review/corner-review/01-service-off-card.png)); [the in-app panel](review/corner-review/02-service-off-in-app-panel.png) offers no Expand action. Source search finds the only Expand selection in the held-Menu overlay menu, which cannot be opened by this nonfocusable/non-touchable card with the service disabled.

**Expected:** The packet explicitly requires Expand reachable from the in-app panel, and the service-off path to retain the existing over-game functionality. At base, Show over game opened the lineup side panel. At candidate, a user who cannot enable accessibility can only show/hide the small card; the old over-game lineup is unreachable.

**Repair target:** Provide the required remote-reachable in-app Expand route through the existing overlay host while retaining card as the default. Prove the entire service-off flow with D-pad/OK, including return to the game.

**Proposed write set:** `panel/OverlayModel.kt`, `panel/OverlayService.kt`, an in-app control in `panel/LineupPanel.kt` and/or `MainActivity.kt`, and fallback/device tests. `MainActivity.kt` was outside the original author packet: the parent should record a bounded write-set correction if that placement is chosen, not waive this requirement.

### F04 — P2: actual card opacity and small-text contrast fail over bright video

**Location:** `tv-app/app/src/main/java/com/afc/companion/panel/CornerCardOverlay.kt:44`; `panel/OverlayService.kt:245`; nominal constants in `panel/OverlayModel.kt:168`.

**Reproducer:** Show the card over the bright synthetic game, as in [04-card-bright.png](review/corner-review/04-card-bright.png), and inspect [the actual window](review/corner-review/04-card-bright-window.txt). Android reports `alpha=0.8` for the non-touchable card window. The composition therefore applies the 72% content background through another alpha layer.

**Observed:** Background RGB `(117,122,149)` over fixture `(240,246,251)` and source surface `(27,30,75)` implies about **57.7% effective opacity**, below the requested 60–75%. Solid text pixels are `(243,243,254)`. Their WCAG contrast against that actual background is **3.832:1**, below the test's 4.5:1 small-text target. Pixel samples and formula result are in [native-contrast.json](review/native-contrast.json). The smaller freshness label uses the same colors. The menu's focus border and layout are clear; this finding concerns the plain card.

**Repair target:** Account for actual window/compositor alpha on supported Android versions and preserve the owner-requested final opacity and legibility. Test/render the final composition, not just the Compose background constant over a synthetic color. Avoid fixing Android 34 by making the card opaque on older supported hosts.

**Proposed write set:** `panel/OverlayService.kt`, `panel/CornerCardOverlay.kt`, `panel/OverlayModel.kt`, related contrast/opacity tests, and bright/dark native evidence.

### F05 — P2: wiring tests survive broken focus and service-off behavior; key/league tests encode the defects

**Location:** `tv-app/app/src/test/java/com/afc/companion/panel/CornerCardIntegrationContractTest.kt:31`, `:98`; `access/MenuHoldFilterTest.kt:28`, `:35`; `panel/OverlayModeTest.kt:141`.

**Reproducer/evidence:** Run [mutation-probe.py](review/mutation-probe.py). It changes only review-owned source copies: card `render()` is wired to focusable `menuParams`, while the actual in-app `overlay.toggle()` is put behind `if (false)`. All **16** tests in `CornerCardIntegrationContractTest` and `OverlayIntegrationContractTest` still pass ([log](review/mutation-tests.txt)). This is a source-contract mutation experiment: unchanged compiled product classes are intentional because these tests claim to verify their source wiring. It proves their source predicates do not distinguish these wrong implementations; it is not a claimed full PIT run.

The key tests deliberately expect forwarded held down and swallowed pre-threshold repeats. They never observe the foreground application's input state after real release (F01). The switcher test asserts same-team pair fabrication (F02). Constant-only contrast ignores the native compositor (F04). Enum and pure-model checks do not constitute actual WindowManager focus evidence.

**Repair target:** Replace the missing behavioral proof with regressions that fail for consumed short Menu, long-hold foreground leakage/post-release repeats, card focus leakage/Back focus restoration, wrong host geometry, disabled-service control failure, distinct league/team associations and final rendered contrast. Keep useful pure geometry, state and parser tests. Do not treat the owner-approved same-author exception as approval for these wrong or missing oracles.

**Proposed write set:** The four new test files, relevant existing `OverlayIntegrationContractTest.kt` / `OverlayLifecycleTest.kt`, and bounded native fixtures/evidence. No product guards or gate changes are required by this finding.

### F06 — P2: the corner card omits sport for the current NFL wire shape

**Location:** `tv-app/app/src/main/java/com/afc/companion/panel/OverlayModel.kt:186`; `panel/CornerCardOverlay.kt:39`.

**Reproducer:** `CornerReview#wireShapeAndRelease` uses a valid NFL `halfPpr` response without a `sport` property. This matches current backend `panel/__init__.py:395`, which adds `sport` only for NBA, and the existing decoder accepts it. [18-nfl-wire-card-after-release.png](review/corner-review/18-nfl-wire-card-after-release.png) shows 112.5 and freshness, but no NFL mark. [wire-shape.txt](review/corner-review/wire-shape.txt) records the fixture difference.

**Cause:** The new card reads only optional `snapshot.sport`. The original visual fixtures and positive sport test explicitly add `sport="nfl"`, masking the integration gap. The owner asked for sport on the default card; an NFL response accepted by the current application is not an unknown-sport test case that can silently omit it.

**Repair target:** Derive the correct sport from authoritative supported scoring/profile context for existing NFL responses, or provide an explicitly agreed wire adaptation. Prove both current NFL and NBA shapes without adding a backend change by assumption.

**Proposed write set:** `panel/OverlayModel.kt`, `panel/CornerCardOverlay.kt` as needed, card/decoder integration tests and native fixtures. Any backend contract change must be separately scoped by the parent.

## Verification and visual coverage

Commands ran with the packet's `TMPDIR` and `ANDROID_HOME`; the local JDK was selected for Gradle. The evidence APK uses `-PafcApiBaseUrl=https://review.invalid` with an in-process synthetic HTTPS peer. **No cleartext manifest edit, deployed backend, real session, production database, credential read or provider app was used.** Review harness sources and their Gradle init live only in `review/` and add test-APK fixtures; product source is the pinned candidate.

| Verification | Result / evidence |
| --- | --- |
| `bash tools/ci/gate.sh tvapp` | Exit 0; UTP resolution, unit/lint/build gate; [log](review/gate-tvapp.txt) |
| Independent full `testDebugUnitTest` during native build | **386 passed**, actual test execution; [log](review/native-build.txt) |
| `bash tools/ci/gate.sh hygiene docs` | Exit 0; 119 hygiene tests; [log](review/gate-hygiene-docs.txt). GAP strings in this log belong to expected negative gate fixtures, not candidate failures. |
| Native build and APK signature | Builds exit 0; [signature](review/apk-signature.txt), [product/test APK hashes](review/apk-hashes-final.txt) |
| `OverlayLifecycleTest` on owned AVD | **4/4 passed**; [instrumentation](review/overlay-lifecycle.txt), [real compositor samples](review/f04-frames.txt) |
| Independent native UI flows | Captured via uinput and real D-pad navigation; [runner](review/native-flows.txt), [captures](review/corner-review/) |
| Persistent-remote/NFL wire reproduction | Completed; [runner](review/wire-and-release.txt); establishes F01/F06, not an acceptance pass |
| Source-contract mutant run | **16/16 survived** wrong wiring, exit 0; F05, not successful assurance |
| Implementer image manifest | All 11 existing image hashes verified from their manifest's directory |
| SHA and diff at close | Rechecked; see [candidate-check.txt](review/candidate-check.txt) |

Native flow capture uses collection-style observations, not assertions for every verdict. UiAutomator does not reliably expose the nonfocusable card's text: the three failed text-presence observations are contradicted by screenshots/window rectangles, and are harness limitations, not product findings. Its net “Panel remains hidden” observation also cannot prove absence of transient toggles: real repeated Menu downs establish F01. The runner's `OK` is collection completion, not blanket UI acceptance. Attempts 1/2 were excluded due to touch-based TV activation / accessibility suppression and an insufficient bound-service check; final runs use D-pad, `FLAG_DONT_SUPPRESS_ACCESSIBILITY_SERVICES`, and a bounded capability-8 binding assertion. The corrected service binding is recorded in `corner-review/access-on.txt`.

Reviewed screenshots: `01` service-off card/hint; `02` service-off in-app panel; `03` short Menu; `04/05` bright/dark card; `06` menu; `07` expanded; `08/09` Back then OK into game; `10` league switch; `11` Back from menu; `12` card plus alert; `13` expiry; `14–17` real Companion panel short/hold/Back; `18` persistent-remote and actual NFL wire shape. All are 1920×1080 and hashed in [SHA256SUMS](review/SHA256SUMS).

Focus/geometry observations: Card is actually `NOT_FOCUSABLE NOT_TOUCHABLE`; menu and expanded window use `NOT_TOUCH_MODAL` without `NOT_FOCUSABLE`. Menu/expanded take focus; Back returns it to `ReviewGameActivity`. Card rectangle is `[1517,54,1824,183]`; an alert occupies `[1644,54,1824,234]`, with card moved to `[1517,245,1824,374]`. Menu is `[1440,194,1824,453]`. These fit the five-percent safe zone and the sampled card/alert transitions do not overlap. Existing FIFO, replacement, five-second expiry, hidden monitoring, current selected profile/team/sport and stop-monitoring ownership tests pass; their four device tests were run rather than accepted as an implementer claim. Expand/Back works with the service enabled; this does not resolve F03.

Accessibility/security inspection: `MenuHoldService` and `OverlayService` are explicitly nonexported; accessibility binding requires `BIND_ACCESSIBILITY_SERVICE`. Bound capabilities are exactly `8` (key filtering); configuration denies window-content retrieval and requests no gesture/global-action capability. The callback reads no event or screen data and no new external component accepts commands. Configuration still subscribes to `TYPE_WINDOW_STATE_CHANGED` although the callback is empty; that subscription is unnecessary and should be minimized in an appropriate repair, but no event/content snooping or external disclosure was observed. No security control was weakened for evidence collection.

## Every new test: independent oracle and mutation assessment

“Useful” means a real test that can fail on a wrong result within its named unit. It does **not** imply independent authorship or complete platform coverage. “Limited” means useful for the narrower property stated. “Weak/wrong” is F05. All tests were authored by the implementer under the owner-approved deviation; this review independently judges their expectations.

### `access/MenuHoldFilterTest.kt` (10)

| Test | Judgment; wrong behavior it can/cannot catch |
| --- | --- |
| `holdIsSevenHundredMilliseconds` | Useful constant check; fails a changed threshold, does not exercise timer scheduling. |
| `shortMenuPressPassesThroughUntouched` | Useful pure down/up check; fails a filter consuming a 300-ms short press. Does not prove service or foreground delivery. |
| `pressJustUnderTheHoldPassesItsUp` | **Wrong oracle:** explicitly requires swallowing a repeat at 500 ms in a 699-ms press. Violates untouched short sequence. |
| `longMenuPressFiresOnceWhileHeldAndConsumesTheRestOfTheSequence` | Limited one-shot/threshold unit proof, **wrong/incomplete platform oracle**: requires forwarding initial down and manually supplies repeats; misses F01. |
| `lateTimerStillFiresFromTheRepeatOrTheUp` | Useful unit fallback and one-shot check; misses foreground balancing. |
| `nextShortPressAfterAHoldPassesAgain` | Useful internal-state reset check; foreground dispatcher state is not observed (F01). |
| `otherKeysAreNeverConsumedEvenWhileMenuIsHeld` | Useful key whitelist regression; fails consuming Back/D-pad/media/volume/Enter in the filter. |
| `repeatWithoutASeenDownPassesBecauseItsDownReachedTheAppUnfiltered` | Useful unseen-down boundary; no synthetic platform repeat proof. |
| `resetDropsAHalfSeenHold` | Useful filter cancellation check; does not establish service lifecycle or delivery. |
| `serviceOffFallbackReadsTheSecureSettingList` | Useful exact component-list parser test, **not a fallback-flow test**. Cannot catch a disabled Show over game action. |

### `panel/CornerCardTest.kt` (8)

| Test | Judgment; wrong behavior it can/cannot catch |
| --- | --- |
| `cardIsSmallAtTheSafeTopRightCorner` | Useful independent safe-zone/area/exact-HD oracle, four resolutions including odd dimensions. Fails moved/oversized returned boxes. |
| `anAlertTakesTheCornerAndTheCardStacksJustBelowWithoutOverlap` | Useful independent rectangle-disjointness and gap oracle; fails overlapping geometry results. Does not prove host uses them. |
| `menuStacksBelowTheCardInBothCornerStatesWithoutOverlap` | Useful independent disjointness/safe-zone oracle with and without alert. Host wiring still needs native proof. |
| `backgroundOpacityIsBetweenSixtyAndSeventyFivePercent` | Limited raw constant range; **insufficient final-opacity oracle**, misses F04. |
| `cardTextStaysLegibleOverBrightAndDarkVideo` | Real contrast math over several colors and sport accents, but omits actual window alpha; **misses F04**. |
| `cardTextIsTheTotalStatusAndSport` | Useful fresh/stale/replay/undated text checks; its explicit NFL tag and expected null badge miss actual NFL response F06. |
| `unknownTotalsAreLabeledNeverZero` | Useful independent unknown/no-team/loading expectations; fails rendering zero for missing value. |
| `serviceOffShowsAOneLineHintAndServiceOnShowsNone` | Useful hint formatter check; cannot prove displayed hint/button/Expand usability. |

### `panel/OverlayModeTest.kt` (12)

| Test | Judgment; wrong behavior it can/cannot catch |
| --- | --- |
| `firstHoldShowsTheNonFocusableCard` | Useful Off→Card/feed/count assertions; `focusable` is model metadata, not actual focus. |
| `holdOnTheCardOpensTheFocusableMenuAndHoldAgainReturnsToTheCard` | Useful Card→Menu→Card and lifecycle counter oracle; native windows still untested here. |
| `menuOffersHideExpandAndTheLeagueSwitcher` | Useful small enum-membership requirement check, narrow rather than behavioral. |
| `dpadMovesMenuFocusWithinBoundsAndOkSelects` | Useful clamping/OK state oracle; first/last order is obtained from enum, so does not independently specify ordering. |
| `backFromMenuOrExpandedReturnsToTheCardAndReleasesFocus` | Useful mode/feed regression; actual WindowManager focus leakage can survive (F05 mutant). |
| `okOnTheExpandedPanelOpensTheMenuAndHoldReturnsToTheCard` | Useful model transition oracle. |
| `cardModeIgnoresFocusedKeysSoTheyBelongToTheGame` | Useful return-value/mode check; no foreground key-delivery assertion. |
| `hideRemovesTheSurfaceAndStopsTheFeed` | Useful Off/feed/remove-count and subsequent hold check; callback is a fake counter, not native cleanup. |
| `inAppButtonTogglesTheCardAndHidesFromAnyOpenSurface` | Useful controller toggle check; no actual in-app button, service-off, or Expand route tested. |
| `deniedHoldAsksForTheOverlayPermissionWithoutAWindow` | Useful deny/request/count boundary; no Android settings interaction. |
| `leagueSwitcherCyclesTheProfileLeaguesThroughThePanelAndWraps` | Useful clearing/refetch/wrap/menu-retention behavior on supplied pairs; same-team fixture cannot catch F02. |
| `overlayLeaguesComeFromTheProfileSelectedPairFirst` | **Wrong product oracle:** asserts manufactured pairs with the same team across all leagues. Missing/null handling is useful but does not rescue association validity. |

### `panel/CornerCardIntegrationContractTest.kt` (8)

| Test | Judgment; wrong behavior it can/cannot catch |
| --- | --- |
| `cardWindowFlagsNeverTakeFocusWhileMenuAndPanelFlagsDo` | Useful bitmask helper check; does not prove flags applied to actual windows. |
| `hostPlacesTheCardMenuAndPanelFromTestedGeometryAndFlags` | **Weak wiring oracle:** focusable card mutation survives; strings remain in unused `cardParams`. Does not prove no overlap in the host. |
| `holdIntentRoutesToTheStateMachine` | Limited source-shape check; fails deleting named routing tokens, accepts unreachable/misrouted equivalents with tokens present. |
| `overlayReadsTheProfileLeaguesForTheSwitcher` | **Weak identity oracle:** checks helper call names, not valid associations. F02 remains green. |
| `manifestDeclaresTheKeyFilterServiceBehindTheSystemBindPermission` | Useful real XML parser/security permission+intent+metadata check. Missing explicit exported assertion; source was independently checked. |
| `accessibilityConfigRequestsKeyFilteringAndNothingElse` | Limited key-filter/content flag check; name overclaims exclusivity: does not reject every extra capability/event subscription. |
| `keyFilterServiceConsumesOnlyThroughTheTestedFilterAndControlsNothingElse` | Limited source call/forbidden-token check; no native sequence, callback timing or returned-result proof. F01 remains green. |
| `serviceOffFallbackKeepsTheInAppButtonAndShowsTheHintOnTheCard` | **Weak flow oracle:** dead in-app toggle mutant survives; also fails to require service-off Expand. |

The existing `OverlayIntegrationContractTest` was adjusted for default card flags, without deleting unrelated checks; nevertheless its source predicate also survives the focus mutant. `OverlayLifecycleTest` retained its real compositor/monitoring assertions while changing expected default text, and its four device cases passed. Neither is evidence for physical key release handling. The recorded initial red run against signature-only stubs establishes a feature-red claim, not mutation resistance or independent test authorship.

## Per-file OCR application

`ocr delegate preview --from a22031f --to 5f8073a` listed 16 reviewable files; **every listed file** received `ocr delegate rule <file>` and exit 0. [Preview](review/ocr-preview.txt), rules `ocr-rule-01.txt` through `ocr-rule-16.txt`. Kotlin rules (null safety, dead code, coroutine/resource ownership, collection/state behavior and maintainability) and default rules (correctness/security/resources/testing) were applied by this reviewer; they were not treated as another independent reviewer.

### `evidence/visual/tv-corner-card/SHA256SUMS` — rule 01

All 11 image entries resolve relative to their directory and hashes match. Screenshots were treated as implementer evidence and independently rerun, not accepted as proof of remote behavior.

### `tv-app/app/src/androidTest/java/com/afc/companion/panel/OverlayLifecycleTest.kt` — rule 02

Default-text updates are appropriate. Existing cleanup, fresh selected-profile card source and real overlap/expiry checks remain. Ran all four natively; pass. No key-filter/focus/platform-alpha coverage is claimed by these tests.

### `tv-app/app/src/main/AndroidManifest.xml` — rule 03

Nonexported services and system bind permission inspected; metadata resolves. No unrelated component/permission change. The system successfully binds on this AVD with only capability 8. Cleartext remains false.

### `tv-app/app/src/main/java/com/afc/companion/access/MenuHoldFilter.kt` — rule 04

Nullable down state and one-shot flag reset are straightforward. The cross-boundary event ownership is wrong, despite pure-state reset: F01. Pre-threshold repeat assertion conflicts with untouched short input.

### `tv-app/app/src/main/java/com/afc/companion/access/MenuHoldService.kt` — rule 05

Timer uses event uptime+700 and callbacks are removed on interrupt/destroy. No screen reads, global action, input replay, or credential path added. Delivery to flawed filter is F01; swallowing service-start exceptions supplies no user-facing failure proof, but no additional unobserved failure is invented.

### `tv-app/app/src/main/java/com/afc/companion/panel/AlertCardOverlay.kt` — rule 06

Focusable windows route key-downs through a FrameLayout before Compose; lifecycle owners remain attached. Reattachment retains composition and cleanup behavior. Existing real alert source, FIFO/timeout and overlap tests pass. No unrelated source-policy relaxation.

### `tv-app/app/src/main/java/com/afc/companion/panel/CornerCardOverlay.kt` — rule 07

Small card/menu content, text truncation and focus appearance visually inspected. Nullable snapshot gets unknown labels. F04 rendered opacity/contrast and F06 missing NFL badge remain; no wrapper abstraction or style-only rewrite is requested.

### `tv-app/app/src/main/java/com/afc/companion/panel/OverlayModel.kt` — rule 08

Model transitions, clamped navigation, no-team and safe-zone geometry exercised. F02 invented associations; F03 no in-app expansion path; F04 raw opacity assumptions; F06 sport dependency. Core alert queue/authoritative-value logic unchanged.

### `tv-app/app/src/main/java/com/afc/companion/panel/OverlayService.kt` — rule 09

Scoped jobs cancel, profile is reread on show, real windows use tested rectangles, and removal follows mode. Native focus return and alert displacement confirmed. F03/F04 apply. No speculative lifecycle-race finding was substituted for a reproducer.

### `tv-app/app/src/main/res/values/strings.xml` — rule 10

Only the new service label/description were added; sibling branding keys are unchanged. Strings resolve. No privacy or credential content.

### `tv-app/app/src/main/res/xml/menu_hold_service.xml` — rule 11

Filter flag/capability, content denial and description checked against bound native service. Window-state subscription is unnecessary with the empty callback; no actual content read observed. No gesture capability.

### `tv-app/app/src/test/java/com/afc/companion/access/MenuHoldFilterTest.kt` — rule 12

Ten tests evaluated individually above. Useful pure state/key-list tests, but incorrect sequence expectations and no foreground-release oracle: F05, exposing F01.

### `tv-app/app/src/test/java/com/afc/companion/panel/CornerCardIntegrationContractTest.kt` — rule 13

Eight tests evaluated above. XML assertions offer useful narrow checks; source wiring predicates survive concrete mutations: F05. Not accepted as native UI proof.

### `tv-app/app/src/test/java/com/afc/companion/panel/CornerCardTest.kt` — rule 14

Eight tests evaluated above. Geometry/property checks are real and independently fail wrong rectangles. Contrast/opacity ignores compositor and fixture misses actual NFL shape: F04/F06, accounted for in F05.

### `tv-app/app/src/test/java/com/afc/companion/panel/OverlayIntegrationContractTest.kt` — rule 15

Default-surface adjustment preserves unrelated assertions. Both new/old contract suites pass the bad focus/fallback source mutations; F05. Real focus evidence comes from native captures.

### `tv-app/app/src/test/java/com/afc/companion/panel/OverlayModeTest.kt` — rule 16

Twelve tests evaluated above. Most are meaningful model oracles, distinct from OS focus proof. Last association test asserts the implementation's unsupported same-team assumption: F02/F05.

## Prose/evidence review and closeout

For mixed-change prose (`CHANGELOG.md`, handoff, red evidence), the eight-subject docs checklist was applied: observer labels; actors; dates; credential/private-path hygiene; plain wording; command correctness/context; resolving local links; and terminology. The handoff's claim that the filter consumes repeats is contradicted by F01; the opacity and fallback completion claims are qualified by F03/F04. “Red first” and author “SUCCESS” remain attributed claims, not independent acceptance. Changelog PR TBD is the packet-authorized placeholder pending landing. Existing screenshots are static evidence, not a physical Fire OS claim.

No Fire TV stick, provider playback/Amazon behavior or physical remote was checked, as prohibited by the packet. No full PIT mutation score was run; the bounded mutation experiment is described exactly. Native timings/opacity here apply to the owned Android 34 AVD; Fire OS remains unqualified. All F01–F06 obligations remain open, and no repair/acceptance/landing/publication is implied by the passing mechanical gates.

## Repair — same-session transition authorized 2026-10-22

The orchestrator accepted F01–F06 and their bounded write sets, including behavioral regressions. This is Repair Implementer work by Codex, following the frozen review/repair route. It is not a second independent review or a new PASS verdict. The original review above remains the immutable description of candidate `5f8073a`.

### F01 contract gap (decision pending)

F01's accepted target requires both unchanged short presses and exclusive global ownership of a 700 ms hold. A key-only AccessibilityService cannot implement that combination: each event requires an immediate consume/pass result, and the Android 14 dispatcher times out that result after 500 ms. A service cannot modify the forwarded event or replay a consumed short press through this API. See [Android's onKeyEvent contract](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService#onKeyEvent(android.view.KeyEvent)), [Android 14 dispatcher source](https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/services/accessibility/java/com/android/server/accessibility/KeyEventDispatcher.java), and the [pinned timing excerpt](review/android14-key-filter-timeout.txt).

A material contract decision was requested through the question box: preserve all balanced foreground events and allow the foreground to react to a hold as well, or retain exclusive ownership and scope a different input architecture/gesture. Neither a privileged injector nor another accessibility capability was silently added. F01 product code remains unchanged pending that decision. Merely forwarding up would not satisfy the accepted repair target, as the original receipt explicitly states.

The new native regression independently reproduces release at 5032 ms, although physical up is scheduled at 1000 ms and the device remains present another 4000 ms: [red runner](review/repair-red-native.txt), [foreground trace](review/repair-red-key-events.txt). A subsequent full flow reaches its final F01 assertion and fails at about 5 seconds: [runner](review/repair-native.txt). These are genuine product assertion failures, not runner exit-code mistakes: [run-native.py](review/run-native.py) maps Android's textual failure status to exit 1.

### Implemented repair targets

| Finding | Implementation and behavioral evidence | Write set |
| --- | --- | --- |
| F02 | Only the selected, explicit profile pair is supplied to the overlay. Unpaired league/team sets never establish associations. League is hidden unless the panel has at least two distinct known pairs; navigation skips the hidden row. Pure tests cycle `league-a/team-7` → `league-b/team-8` → `league-c/team-9`, clear/refetch, and wrap. Native rendering has Expand/Hide and makes no fabricated LeagueB/TeamA request. | `panel/OverlayModel.kt`, `PanelModel.kt`, `CornerCardOverlay.kt`, `OverlayService.kt`; `OverlayModeTest.kt`; native fixture |
| F03 | Panel navigation exposes **Expand over game**, using the same overlay host via ACTION_EXPAND. The default button continues to toggle the card. The native test disables accessibility, selects the real Expand button by D-pad/OK, observes shared expanded content taking focus, then Back returning focus to the synthetic game. | `MainActivity.kt`, `panel/OverlayService.kt`; native fixture |
| F04 | Card window alpha is explicitly the platform's maximum obscuring opacity on API 31+, and 1 on older hosts. The Compose surface compensates to retain 72% effective background opacity; older hosts retain the translucent surface. A native screenshot pixel assertion measures **6.053:1** text contrast over the bright fixture, versus **3.832:1** when compensation is mutated away. Pure tests include both window-alpha paths and final foreground/background composition. | `panel/OverlayModel.kt`, `CornerCardOverlay.kt`, `OverlayService.kt`; `CornerCardTest.kt`; native fixture |
| F05 | Five source-token wiring tests were removed. Real WindowManager focus, actual service-off button execution, persistent uinput release, final rendered pixels, live window rectangles, and current NFL wire shape now supply the behavioral oracles. Useful model, geometry, parser and XML checks remain. The new XML checks assert exported=false, exactly the key-filter flag, no unnecessary event subscription, and no extra declared capabilities. The unused window-state event subscription was removed. Native mutation results are detailed below. F01-specific semantics remain pending its contract decision. | `CornerCardIntegrationContractTest.kt`, `CornerCardTest.kt`, `OverlayModeTest.kt`, `AlertCardMappingTest.kt`; `src/androidTest/AndroidManifest.xml`, `CornerCardLifecycleTest.kt`, `CornerGameActivity.java`, `OverlayTestPeer.kt`, `OverlayLifecycleTest.kt`; `res/xml/menu_hold_service.xml` |
| F06 | Card and fallback alert sport use an explicit snapshot sport when present; otherwise `NbaPoints` supplies NBA and the supported NFL scoring bases supply NFL. A declared alert sport retains precedence. Tests decode the current untagged NFL wire and tagged NBA wire; fresh matching untagged NFL panel points can supply an alert without inventing a sport. Native card evidence uses an untagged halfPpr response. | `panel/OverlayModel.kt`; `CornerCardTest.kt`, `AlertCardMappingTest.kt`; native fixture |

**F02 follow-up:** the current client API cannot list real league/team pairs. The sibling multisport-lineups backend slice does not add that listing field. A listing API/client integration remains follow-up work; the current profile supplies one explicit pair, so the shipped League row remains hidden. No backend, fabricated associations or speculative persistence was added.

### Regression validity and verification

`CornerCardLifecycleTest` uses a synthetic HTTPS peer in-process, a separate foreground Activity in the test APK, the production host and accessibility service, and Linux uinput. UIAutomator preserves enabled accessibility services. The test observes down/up on a still-connected remote, not `input keyevent` (which bypasses the filter). Its no-root semantics query explicitly permits absence when proving no card after a short press. Setup was corrected before accepting evidence; the initial no-compose-root harness failure is not counted as product red evidence.

The proposed regression fixture is exercised on the owned `afc-tv-review2`, port 5630, 1920×1080 Android 34. Other AVDs, the stick and provider applications are untouched. A test-only exported synthetic game Activity is declared only in the androidTest manifest; the product service security boundary is unchanged.

[Native mutation results](review/repair-mutations.json) identify each mutant APK hash, observed failure and expected assertion. Focus leakage, a dead in-app button and missing opacity compensation are rejected by actual UI/pixel assertions. The original held-up bug is rejected by actual foreground release timing. The tests do not claim source-string presence as end-to-end proof.

The four existing `OverlayLifecycleTest` device tests pass after the repair source changes: [runner](review/repair-overlay-lifecycle.txt), **exit 0, OK (4 tests)**. This retains #157 monitoring ownership, current selected team/sport, queued card replacement/expiry, and sampled non-overlap coverage. The new full native flow passes service-off expansion, sport, focus/Back, rendered contrast and actual safe-zone/non-overlap assertions, then fails the still-open F01 release assertion (**exit 1**). It is not reported as an overall pass.

The first hygiene invocation exited 1 because its fixture copies `git ls-files`: the edited, tracked handoff linked the new review receipt before that receipt was staged. Its sole failure was `handoff.md:5:DOC-LINK`, not a product failure. The focused check passed after staging; a second full run exposed the nested copy fixture dropping ignored `.log` files on its own commit. Repair logs were therefore renamed to ordinary tracked `.txt` evidence, without any gate change. Both affected focused checks and the complete gate were rerun. [Initial log](review/repair-gate-hygiene-first.txt), [focused check](review/repair-hygiene-prerequisite.txt).

Both device suites now use `OverlayTestPeer`, because Android permits only one URL factory per instrumentation process. A combined invocation reports **five tests, one failure (F01 only)**, proving that the four #157 tests also work alongside the new fixture: [combined runner](review/repair-combined-native.txt). The final new-flow run also asserts the exact overlay window owns focus (rather than merely asserting that the game does not): [runner](review/repair-native.txt).

One further hygiene attempt was terminated (exit 143) after reproducing evidence-handling failures: an earlier, still-running tracked log acquired unsanitized local paths as its traceback was appended. This was not a product defect or a passing gate. Evidence was frozen, path-sanitized and whitespace-normalized; the final gate captures output outside the repository and copies back only the completed, sanitized result. No gate or gate-test implementation was edited.

### Final command results

All commands ran from the worktree root. The gates use `TMPDIR=$HOME/.cache/afc-gate-tmp ANDROID_HOME=$HOME/.local/share/afc-tools/android-sdk`.

| Command | Exit / result | Evidence |
| --- | --- | --- |
| `./tv-app/gradlew -p tv-app testDebugUnitTest --tests '*CornerCardTest' --tests '*OverlayModeTest'` before product repairs | 1; 20 tests, three intended assertion failures (F02/F04/F06) | [red](review/repair-red-unit.txt) |
| `./tv-app/gradlew -p tv-app -PafcApiBaseUrl=https://review.invalid :app:assembleDebug :app:assembleDebugAndroidTest testDebugUnitTest` | 0; 383 JVM tests, debug and test APKs built | [build](review/repair-build.txt) |
| `python3 evidence/tv-corner-card/review/run-native.py com.afc.companion.panel.OverlayLifecycleTest` | 0; four device tests | [runner](review/repair-overlay-lifecycle.txt) |
| `python3 evidence/tv-corner-card/review/run-native.py com.afc.companion.panel.CornerCardLifecycleTest,com.afc.companion.panel.OverlayLifecycleTest` | 1; five tests, only F01 fails | [runner](review/repair-combined-native.txt) |
| `python3 evidence/tv-corner-card/review/run-native.py com.afc.companion.panel.CornerCardLifecycleTest` | 1; final physical-release assertion fails at 5018 ms; preceding assertions pass | [runner](review/repair-native.txt) |
| `python3 evidence/tv-corner-card/review/repair-mutations.py` (bounded batches) | 0; five wrong implementations rejected by their intended assertions | [results and APK hashes](review/repair-mutations.json) |
| `bash tools/ci/gate.sh tvapp` | 0 | [gate](review/repair-gate-tvapp.txt) |
| `bash tools/ci/gate.sh hygiene` (final frozen-evidence invocation) | 0; 119 tests | [gate](review/repair-gate-hygiene.txt) |
| `bash tools/ci/gate.sh docs` | 0 | [gate](review/repair-gate-docs.txt) |
| `apksigner verify --verbose` on the source-built fixture APK | 0; APK v2 signature valid | [verification](review/repair-apk-signature.txt) |

The rendered-opacity self-check also exits 0: `python3 evidence/tv-corner-card/review/check-rendered-card.py`, [measurement](review/repair-native-opacity.json). Actual background RGB `(86, 90, 124)` over the known bright fixture implies **72.2%** effective opacity, within 60–75%.

### Evidence, remaining work and disposition

Affected screenshots and actual window records are in `review/corner-repair/`: `repair-01-service-off-card`, `repair-02-service-off-expand`, `repair-04-card-bright`, `repair-05-card-dark`, `repair-06-menu`, `repair-07-expanded`, `repair-08-back-to-game`, and `repair-09-card-plus-alert`. Pixel sampling is in [rendered-contrast.txt](review/corner-repair/rendered-contrast.txt). The actual card and alert frames are disjoint and within the five-percent safe zone. The owned emulator was shut down after capture.

[repair-artifacts.json](review/repair-artifacts.json) binds the fixture APK hashes to the reviewed/repaired source-file hashes and synthetic HTTPS build parameter. [SHA256SUMS](review/SHA256SUMS) covers all review evidence and this receipt. Reverify remains not applicable under the supplied packet: these APKs were built from the source under review; no externally supplied binary was substituted.

**Partial repair disposition: REPAIR_REQUIRED.** F02, F03, F04 and F06 are implemented and verified as described. F05 has real native oracles and five rejected mutations, but its key-ownership expectations and F01 cannot be closed until the owner amends the impossible input contract. Existing pure-filter tests that assert consumed held up are not acceptance of that behavior. This remains the same open repair round; no review/repair budget is reset. The local repair commit contains the unblocked changes, evidence and a deliberately failing native regression for the still-present F01; it is not a completed repair or authority to land a passing claim. No push, stick check, provider launch, backend change or publication was performed. Fire OS behavior and provider reactions remain unverified.

An extra post-capture rebuild completed with exit 0 but an added exact-hash comparison exited 1: it did not reproduce the captured APK bytes. The capture hashes are retained; later rebuilt hashes are separately labeled as not executed in `repair-artifacts.json`. Those later outputs were never installed or substituted for runtime evidence. Source hashes still match all 15 repair source files. Binary reproducibility was not established and is not a requirement claimed by this packet. The original native capture build remains the provenance for screenshots and device results.
