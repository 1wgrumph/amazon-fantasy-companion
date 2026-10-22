# AZ Fantasy branding — independent review

**Verdict: PASS. No actionable findings.**

What this change does: names the TV app **AZ Fantasy**, replaces the Amazon starter launcher artwork with original vector artwork and regenerated legacy icons, and makes the existing setup and lineup copy friendlier. It retains the purple theme, loading animation, data contracts and overlay service behavior.

Independent Reviewer, frontend profile, fresh session, 2026-10-22 UTC. The reviewer did not author the candidate. No repairs, product or repository-suite edits, commits, pushes, issue mutations, stick access or provider-app launches were performed. The review is complete; no Repair Implementer transition was taken.

## Frozen subject and method

| Item | Recorded value |
| --- | --- |
| Branch | `afc/tv-branding` |
| Base | `a22031f21b176ad0f0be49d0eade048f9d0e2576` |
| Candidate | `6980df3023a382ea4ef4fdb964a13a5b2b03495f` |
| SHA256 of `git diff a22031f..6980df3 --binary` | `f0e413513b1192aca20042facb38ac0ae12b3c206c073c0a32ed77f5ddb46389` |
| Binding | `profile-binding-frontend-20261021b.json`; SHA256 `6864e2aa7fc9c004df95b71e209b7dfbed304653622e5089a9d0fe83ed8088bb` |
| Reviewer route | Codex CLI / GPT-6.1 Sol / high; installed `codex-cli 0.163.0`; no fallback used |
| Coverage assist | Frozen `review.coverage_assist.enabled=true`, `required=true`; OCR available, `open-code-review v1.13.3 (375f64c)` |
| OCR execution | Current review packet explicitly selects delegation, overriding the binding's `own_engine` execution mode for this review. `ocr delegate preview --from a22031f --to 6980df3`, then `ocr delegate rule <file>` for **all 45 changed files**, each exit 0. Reviewer applied the rules; OCR is an assist, not the verdict. |
| Reverify | Frozen `deterministic_verification.reverify.enabled=true` retained in accounting. **Not applicable for this review**, as explicitly directed: APK built from the reviewed source. No binary Reverify run or passing result is claimed. |
| Hold | `reviewer-repairs-own-findings` retained. No findings require acceptance or repair. |
| BRAN | **Unavailable**: no native `.bran/policy.yaml`; ordinary repository discovery used. |

[OCR preview](review/ocr-preview.txt) reports 25 supported files / 45 changed files. Unsupported prose, logs and binaries were reviewed manually as well; obtaining default rules does not turn them into supported OCR coverage. [Rule index](review/ocr-rule-index.tsv) maps every path to its rule output and exit code. The per-file sections below record the application of those rules.

Read the implementation packet and both advisor responses. Scope traced through the shell callers, shared profile editor and device preference, panel decoder/controller/renderers, overlay service and geometry, resource references, original-art scripts, unit and device tests, notices and changelog. Assumed load: one TV UI and the existing bounded lineup (maximum 32 accepted rows), with the existing refresh and paging cadence. No new data writes, provider routing, credentials, permissions or external assets were introduced.

## Verification and visual result

All commands operated on the pinned candidate. Gates used `TMPDIR=~/.cache/afc-gate-tmp ANDROID_HOME=~/.local/share/afc-tools/android-sdk`.

| Check | Result / evidence |
| --- | --- |
| `git diff --check a22031f..6980df3` | PASS, exit 0 |
| `bash tools/ci/gate.sh tvapp` | PASS, exit 0; unit test/lint/debug build and UTP resolution. [Log](review/gate-tvapp.txt). |
| Fresh `:app:cleanTestDebugUnitTest :app:testDebugUnitTest` | PASS, exit 0; **349 tests, 0 failures/errors, 56 suites**. Executed separately to avoid relying on the gate's up-to-date test result. [Log](review/unit-tests-fresh.txt). |
| `bash tools/ci/gate.sh hygiene` | PASS, exit 0; **119 tests**, 334.489 s. [Log](review/gate-hygiene.txt). Expected negative fixtures print `fatal: not a git repository` and typed coverage/mutation GAP examples; the complete suite passes. Those examples are not candidate coverage claims. |
| `bash tools/ci/gate.sh docs` | PASS, exit 0. [Log](review/gate-docs.txt). |
| Source-built debug + review instrumentation APK | PASS, exit 0, built with `-PafcApiBaseUrl=https://le3r79003f.execute-api.us-east-2.amazonaws.com`; all review HTTP responses intercepted in-process, synthetic data only. [Build](review/build.txt), [APK hashes](review/apk-sha256.txt), [manifest inspection](review/apk-manifest.txt). |
| Independent capture / real OK navigation | PASS, **1 test**, 39.686 s. [Native result](review/native-capture.txt), [review-only harness](review/capture/IndependentBrandingReview.kt). The synthetic response fixture and stand-in Activity were adapted from the candidate evidence; focus navigation and the verdict were independently checked. |
| Profile D-pad and compact-panel device regressions | PASS: `ProfileDpadFocusTest` **3 tests**, `CompactPanelLayoutTest` **1 test**. [Native result](review/native-regressions.txt). |
| #157 device regressions | PASS: all **4** `OverlayLifecycleTest` tests in that same **8-test** run, 44.185 s overall. Current team/sport card data, stopping monitoring with hidden/visible overlays, card replacement/expiry and non-overlap passed. [Compositor frames](review/f04-frames.txt). |
| Asset audit | PASS. No `FF9900`, `232F3E` or Amazon copyright header anywhere in `res/`; all five old webp hashes absent from candidate icons. All five decoded images exactly match the supplied renderer; banner text paths exactly match the original letter generator. [Audit with old/new hashes](review/asset-audit.txt). |
| Candidate screenshot hashes | All seven author screenshots match their committed `SHA256SUMS`; reviewed alongside independent captures. [Summary](review/verification-summary.json). |

Review-only AVD **afc-tv-review3**, serial `emulator-5640`, API 34 Android TV x86, **1920×1080 / density 320**, on a free port. Other AVDs and the physical device were not used. The owned AVD was shut down after capture. Stock YouTube/YouTube Music/Play Games packages were disabled on this new AVD to avoid their recommendation imagery; none was launched. The Apps screenshot includes the platform's stock TV/Play Store/Settings tiles; these are launcher UI, not artwork shipped by this change.

The review harness focuses the actual focusable button ancestor, asserts focus, then sends real `KEYCODE_DPAD_CENTER`. It never activates a rail item through semantic OnClick. **LEFT from the populated lineup transfers actual focus to the rail's Show over game button; OK activates it.** [Focus tree](review/tv-branding-review/focus-after-left.txt), [result](review/tv-branding-review/rail-path-result.txt), [screenshot](review/tv-branding-review/lineup-left-to-rail.png). The panel's painted internal focus outline can remain visible after focus leaves; the actual focus tree and successful activation establish the route. No broken OK path was reproduced.

The compact overlay screenshot shows **four complete rows, team total 52.5 and Lineup progress 50%** within its bounds. The smaller card-reserved layout regression also passes with a long surname and stale points, reaching the last row without remote scrolling while keeping the total visible. A real OK press over the overlay increments the synthetic foreground app's key counter from 0 to 1, preserving #157's input behavior.

Independent captures, all **1920×1080 and uncropped**, are hashed in [SHA256SUMS](review/SHA256SUMS):

| Capture | Observation |
| --- | --- |
| [Loading](review/tv-branding-review/loading.png) | New title/helper; existing animation and local toggle remain visible. Theme/loading implementation unchanged in the diff. |
| [My setup](review/tv-branding-review/my-setup.png) | Friendly heading/helper, labelled list fields, Add buttons, immediate local toggle and scope note. |
| [Sport glyph](review/tv-branding-review/my-setup-sports.png) | Generic football next to retained sport text. Both sport vectors inspected; neither adds a focus target or content description. |
| [My lineup with data](review/tv-branding-review/my-lineup.png) | New title, scoring/source chip and synthetic rows. Full-screen rows scroll as before; total is below the initial viewport. |
| [Empty lineup](review/tv-branding-review/my-lineup-empty.png) | Original illustration and exact requested guidance; no clipping. |
| [Side panel over synthetic app](review/tv-branding-review/side-panel-over-game.png) | Four complete rows, total and progress visible. |
| [Remote key through overlay](review/tv-branding-review/side-panel-remote-key.png) | Foreground synthetic app receives OK; counter becomes 1. |
| [Full Apps screen / focused banner](review/apps-row-banner.png) | Actual launcher-rendered vector banner and AZ Fantasy label, complete screen retained. This independently addresses the implementer's cropped launcher evidence. |

The first review build attempt used a relative Gradle init-script path, which `-p tv-app` resolved under the project directory. It failed before compilation; the corrected absolute invocation passed. [Setup failure](review/build-initial-path-error.txt) is harness evidence, not a product defect.

## Copy semantics and assertion strength

`backend/src/panel/__init__.py:365` computes progress as the lineup's mean coarse game state: pre=0, in=0.5, post=1. `Lineup progress: 50%` faithfully formats that value as requested; it does **not** claim elapsed game time. The decoder already rejects non-finite values and makes out-of-range progress unavailable. Both renderers use the same formatter; stale age, replay labels and Unavailable survive unchanged. Existing `PanelText` behavior is unchanged; the added formatter tests cover percent rounding, stale, replay and null.

Compared every changed test hunk with the base:

- `ProfileDpadFocusTest`: only the expected Add-button string changed; all focus assertions, actual key events, editing and IME checks remain.
- `ShellContractTest`: only the exact expected three navigation strings changed; exact set equality remains.
- `PanelRevealTest`: both exact on/off label assertions remain; the separated exact TV-scope note assertion is added.
- `ProfileRepairTest`: only the initial message and its corresponding wait sentinel changed; save-race checks and timeout remain.
- `PanelTextTest`: existing assertions untouched; four new exact-result assertions added.
- `CompactPanelLayoutTest`: byte-for-byte unchanged; its real rendered bounds, total visibility and automatic last-row checks all pass.

No assertion removed, relaxed, ignored or replaced by mere existence. No provider/team marks, downloaded images or font files appear in the new artwork. Original simple geometry and matching generation scripts support the notices' authorship statement; retained starter theme attribution remains correctly separate from the replaced assets. This is source/provenance review, not trademark clearance.

## Per-file OCR application

Each section records the reviewer applying its linked OCR output. PASS means no actionable defect found in that file within this diff.

### 1. `CHANGELOG.md`

**PASS.** [Applied OCR rules](review/ocr-rule-01.txt). Default rules: entry matches delivered branding/copy, is under Unreleased/Changed and retains the packet-requested PR TBD placeholder for the landing agent.

### 2. `THIRD_PARTY_NOTICES.md`

**PASS.** [Applied OCR rules](review/ocr-rule-02.txt). Default rules: original art is assigned the repository Apache-2.0 licence, generator paths exist, and MIT-0 attribution for the retained starter theme is preserved. No font or third-party glyph claim is introduced.

### 3. `evidence/visual/tv-branding/SHA256SUMS`

**PASS.** [Applied OCR rules](review/ocr-rule-03.txt). Default rules: all seven named candidate images exist and their SHA256 values match.

### 4. `evidence/visual/tv-branding/capture-native.txt`

**PASS.** [Applied OCR rules](review/ocr-rule-04.txt). Default rules: parsed OK (1 test); does not substitute for independent review or real remote-key evidence.

### 5. `evidence/visual/tv-branding/capture.init.gradle`

**PASS.** [Applied OCR rules](review/ocr-rule-05.txt). Default rules: adds capture sources/manifest to androidTest only; main APK source sets remain unchanged.

### 6. `evidence/visual/tv-branding/capture.txt`

**PASS.** [Applied OCR rules](review/ocr-rule-06.txt). Default rules: correctly discloses synthetic responses, semantic rail clicks, Android TV environment and the launcher crop. Review independently closes the latter two method gaps on an AVD.

### 7. `evidence/visual/tv-branding/capture/AndroidManifest.xml`

**PASS.** [Applied OCR rules](review/ocr-rule-07.txt). Default rules: androidTest manifest adds only the plain synthetic exported Activity; not merged into the production APK. No provider route or permission added.

### 8. `evidence/visual/tv-branding/capture/BrandingCapture.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-08.txt). Kotlin rules: bounded synthetic fixtures, stream factory intercept, scenario cleanup and screenshots inspected. Semantic click means this capture cannot prove OK activation; independent real-key capture proves that route. This is evidence code, not a shipped data path.

### 9. `evidence/visual/tv-branding/capture/ReviewGameActivity.java`

**PASS.** [Applied OCR rules](review/ocr-rule-09.txt). Java rules: original plain-color/text stand-in, bounded key counter, no network/provider dependency; foreground input received under the actual overlay in independent capture.

### 10. `evidence/visual/tv-branding/gate-docs.txt`

**PASS.** [Applied OCR rules](review/ocr-rule-10.txt). Default rules: author log shows docs PASS; independently executed docs gate also passes.

### 11. `evidence/visual/tv-branding/gate-hygiene.txt`

**PASS.** [Applied OCR rules](review/ocr-rule-11.txt). Default rules: author log shows 119 tests and PASS; negative fixture output is expected. Independent complete hygiene run passes.

### 12. `evidence/visual/tv-branding/gate-tvapp.txt`

**PASS.** [Applied OCR rules](review/ocr-rule-12.txt). Default rules: author log contains passing unit/lint/build results; private home names are placeholders. Independent gate and fresh unit execution verify source rather than relying on the log.

### 13. `evidence/visual/tv-branding/instrumented.txt`

**PASS.** [Applied OCR rules](review/ocr-rule-13.txt). Default rules: author result is OK (4 tests); independent run covers those same four plus all four #157 lifecycle regressions.

### 14. `evidence/visual/tv-branding/launcher-banner-tile.png`

**PASS.** [Applied OCR rules](review/ocr-rule-14.txt). Default/manual binary review: accurately labelled crop of original banner and launcher label; independently supplemented by the full focused Apps screen.

### 15. `evidence/visual/tv-branding/loading.png`

**PASS.** [Applied OCR rules](review/ocr-rule-15.txt). Default/manual binary review: title, helper, toggle and retained spinner correspond to source and independent capture; no mark or clipping introduced.

### 16. `evidence/visual/tv-branding/my-lineup-empty.png`

**PASS.** [Applied OCR rules](review/ocr-rule-16.txt). Default/manual binary review: requested empty sentence and original roster/add illustration visible; matches independent runtime rendering.

### 17. `evidence/visual/tv-branding/my-lineup.png`

**PASS.** [Applied OCR rules](review/ocr-rule-17.txt). Default/manual binary review: title, chip and synthetic populated rows match source; full-screen scrolling is preserved.

### 18. `evidence/visual/tv-branding/my-setup-sports.png`

**PASS.** [Applied OCR rules](review/ocr-rule-18.txt). Default/manual binary review: generic football beside the existing NFL label; no league logo or provider mark.

### 19. `evidence/visual/tv-branding/my-setup.png`

**PASS.** [Applied OCR rules](review/ocr-rule-19.txt). Default/manual binary review: labelled fields, friendly list/add copy and immediate local setting match the approved text; scrolled form behavior retained.

### 20. `evidence/visual/tv-branding/side-panel-over-game.png`

**PASS.** [Applied OCR rules](review/ocr-rule-20.txt). Default/manual binary review: four rows, total and percentage fit in the compact window. Independent capture also proves foreground remote input.

### 21. `evidence/visual/tv-branding/tools/block_letters.py`

**PASS.** [Applied OCR rules](review/ocr-rule-21.txt). Python rules: deterministic polygons for exactly the needed letters, no font/download/evaluation of user code; both emitted banner words exactly reproduce the resource path data.

### 22. `evidence/visual/tv-branding/tools/render_legacy_icons.py`

**PASS.** [Applied OCR rules](review/ocr-rule-22.txt). Python rules: existing Pillow used, fixed five densities, no new dependency or runtime path; independent pixel comparison matches all committed webp assets. Generator deliberately repeats the documented vector geometry.

### 23. `tv-app/app/src/androidTest/java/com/afc/companion/profile/ProfileDpadFocusTest.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-23.txt). Kotlin rules: one expected button-string swap only; original focus/editing/IME assertions intact. All three device tests pass.

### 24. `tv-app/app/src/main/AndroidManifest.xml`

**PASS.** [Applied OCR rules](review/ocr-rule-24.txt). Default rules: only android:banner changes to the new drawable. Icon/label references, leanback entry, permissions and service/component boundaries remain intact. Packaged manifest and actual launcher rendering verified.

### 25. `tv-app/app/src/main/java/com/afc/companion/MainActivity.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-25.txt). Kotlin rules: wordmark and permission sentence only; navigation/service callbacks unchanged. Actual focusable rail ancestor accepts OK after LEFT from lineup; overlay permission grant is confined to the owned emulator.

### 26. `tv-app/app/src/main/java/com/afc/companion/Shell.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-26.txt). Kotlin rules: enum labels only; destination identities, start route and monitoring behavior preserved. Exact destination-set test passes.

### 27. `tv-app/app/src/main/java/com/afc/companion/panel/LineupPanel.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-27.txt). Kotlin rules: both formatter callers traced, finite/range checks upstream retained, no new coroutine owner. Decorative empty image is nonfocusable; compact heading leaves four rows plus total/progress visible; smaller card-reserved layout and #157 runtime checks pass.

### 28. `tv-app/app/src/main/java/com/afc/companion/profile/DeviceSettings.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-28.txt). Kotlin rules: preference key/default/persistence unchanged; on/off and scope copy exact. Exact scope-note assertion added.

### 29. `tv-app/app/src/main/java/com/afc/companion/profile/ProfileSettingsScreen.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-29.txt). Kotlin rules: all NameListEditor callers updated, list mutations/save/error behavior preserved. Text labels remain adjacent to fields; glyphs have null contentDescription and no focus modifier. Focus, IME and save-race regressions pass.

### 30. `tv-app/app/src/main/res/drawable/ic_launcher_foreground.xml`

**PASS.** [Applied OCR rules](review/ocr-rule-30.txt). Default rules: original TV/panel/dot geometry within adaptive mask-safe center; no starter colors, play triangle or branding. Legacy imagery agrees with its geometry.

### 31. `tv-app/app/src/main/res/drawable/ic_lineup_empty.xml`

**PASS.** [Applied OCR rules](review/ocr-rule-31.txt). Default rules: original roster/add geometry, no imported image/font, valid vector with decorative null description at caller. Runtime empty screen fits.

### 32. `tv-app/app/src/main/res/drawable/ic_sport_basketball.xml`

**PASS.** [Applied OCR rules](review/ocr-rule-32.txt). Default rules: generic circle/seam paths, no team/provider/league mark; caller tints with existing sport token and keeps sport text.

### 33. `tv-app/app/src/main/res/drawable/ic_sport_football.xml`

**PASS.** [Applied OCR rules](review/ocr-rule-33.txt). Default rules: generic outlined oval/lace paths, no team/provider/league mark; caller keeps sport text. Independently observed glyph.

### 34. `tv-app/app/src/main/res/drawable/tv_banner.xml`

**PASS.** [Applied OCR rules](review/ocr-rule-34.txt). Default rules: 320x180 viewport, 160x90dp native size at xhdpi; original vector glyph and polygon letters, no font. Both letter paths regenerated exactly and actual Android TV launcher rendering verified.

### 35. `tv-app/app/src/main/res/mipmap-hdpi/ic_launcher.webp`

**PASS.** [Applied OCR rules](review/ocr-rule-35.txt). Default/manual binary review: old hash removed, correct density dimensions and exact decoded-pixel match to original generation script; no Amazon play art.

### 36. `tv-app/app/src/main/res/mipmap-mdpi/ic_launcher.webp`

**PASS.** [Applied OCR rules](review/ocr-rule-36.txt). Default/manual binary review: old hash removed, correct density dimensions and exact decoded-pixel match to original generation script; no Amazon play art.

### 37. `tv-app/app/src/main/res/mipmap-xhdpi/ic_launcher.webp`

**PASS.** [Applied OCR rules](review/ocr-rule-37.txt). Default/manual binary review: old hash removed, correct density dimensions and exact decoded-pixel match to original generation script; no Amazon play art.

### 38. `tv-app/app/src/main/res/mipmap-xxhdpi/ic_launcher.webp`

**PASS.** [Applied OCR rules](review/ocr-rule-38.txt). Default/manual binary review: old hash removed, correct density dimensions and exact decoded-pixel match to original generation script; no Amazon play art.

### 39. `tv-app/app/src/main/res/mipmap-xxxhdpi/ic_launcher.webp`

**PASS.** [Applied OCR rules](review/ocr-rule-39.txt). Default/manual binary review: old hash removed, correct density dimensions and exact decoded-pixel match to original generation script; no Amazon play art.

### 40. `tv-app/app/src/main/res/values/ic_launcher_background.xml`

**PASS.** [Applied OCR rules](review/ocr-rule-40.txt). Default rules: original existing-theme surface color replaces the starter background; Amazon copyright header removed from res while retained theme attribution remains in notices.

### 41. `tv-app/app/src/main/res/values/strings.xml`

**PASS.** [Applied OCR rules](review/ocr-rule-41.txt). Default rules: exact owner-approved AZ Fantasy app_name; manifest reference resolves in the built APK and launcher.

### 42. `tv-app/app/src/test/java/com/afc/companion/ShellContractTest.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-42.txt). Kotlin rules: exact expected set swaps only its three labels; endpoint/social exclusions untouched. Fresh unit run passes.

### 43. `tv-app/app/src/test/java/com/afc/companion/panel/PanelRevealTest.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-43.txt). Kotlin rules: exact true/false label checks retained; exact separated TV-scope assertion added. Reveal behavior tests unchanged and pass.

### 44. `tv-app/app/src/test/java/com/afc/companion/panel/PanelTextTest.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-44.txt). Kotlin rules: existing stale/provenance/game-status/basis/font assertions untouched; four formatter expectations added and pass.

### 45. `tv-app/app/src/test/java/com/afc/companion/profile/ProfileRepairTest.kt`

**PASS.** [Applied OCR rules](review/ocr-rule-45.txt). Kotlin rules: initial-message string and wait sentinel changed together; save concurrency/error assertions unchanged and pass.

## Findings, limits and closeout

**Finding IDs: none. Repair write set: none.** No candidate product defect, weakened assertion or #157 regression was reproduced. No issue filing or repair was attempted.

**V-LIMIT-01 — Fire OS launcher rendering: not run.** The actual Android TV Apps row passes, but it is not Fire OS. The packet forbids stick access; this receipt does not claim physical Fire OS acceptance, trademark clearance, live-backend behavior, provider playback or closure of the historical #157 physical-video observation gap. These limits do not prevent PASS of this specified AVD/source review.

Reverify remains **not applicable — source-built APK**, rather than missing evidence counted as PASS. BRAN remains unavailable. OCR delegation is complete for the reviewable diff, with manual review of the excluded file types.

The only retained review changes are this receipt and `evidence/tv-branding/review/`. Existing untracked CI Python caches were left alone. Review-generated artwork-script Python caches were removed. The owned emulator was stopped; other agents' AVDs and device state were untouched. No tracked product/test file differs from the candidate. Candidate SHA checked again at closeout; a different SHA would invalidate this receipt and stop the review.

Skipped physical Fire OS/stick and provider-app checks, per the packet. Remaining risk: Fire OS launcher rendering needs its own authorized device observation.
