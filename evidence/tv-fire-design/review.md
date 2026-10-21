# Independent review of the TV design candidate

Reviewed on 2026-10-21. Candidate: `582a030d52e8e697618443907d58c808db33a188`.
Base: `72b6c359729721fa3db96ec1e352ab895d51e753`. Later main changes were excluded.

Verdict: **PASS** for the independent source and device visual review. No introduced actionable defect was found; no product repair was made.
Overall typed outcome: **ENVIRONMENT_FAILURE**, solely because the required OpenCodeReview own-engine assist could not start. This is an outstanding coverage gap, not passing OCR evidence. The orchestrator must supply that assist before treating the complete review contract as satisfied.

| ID | Severity | File:line | Failure scenario | Fix commit |
| --- | --- | --- | --- | --- |
| None | — | — | No introduced actionable defect identified | Not applicable |

The source review covered all 24 changed files and the relevant callers. The six production Kotlin changes are styling/layout: the navigation callbacks, focus key handling, backend calls, profile state updates, notification commands, and watch continuation/cancellation paths are unchanged. The WatchActivity additions change dialog geometry, colors, text and button drawing; the confirmation result callbacks remain unchanged.

The safe zone is applied once by AppShell and inherited by its children, and directly by standalone composables. Focus expansion has interior clearance. Body styles are 32/28/28 pixels at the tested density of 2; weights are Normal or heavier. Actual custom-button and field contrast was independently calculated, including the custom focused button pair which the existing default-button test descriptions do not describe: [contrast evidence](review-contrast.txt).

The public-boundary review found no introduced real home paths, device addresses, credentials, account data, or provider/broadcast imagery. The five design captures contain synthetic fixtures and AFC UI only. The author screenshot manifest verifies 6/6. Prose/logs were inspected as evidence rather than source assertions; the changelog describes the delivered visual changes, and the restoration record states its backend-readback limitation.

## OpenCodeReview

Installed tool: OpenCodeReview `v1.13.2`, commit `55450a9`, linux/amd64, built `2026-10-20T03:06:03Z`.
Required mode: own engine. Exact command:

```text
ocr review --from 72b6c35 --to 582a030 --effort high --audience agent --timeout 5 --format json
```

Exit 1, **ENVIRONMENT_FAILURE**, before any engine review:

```text
Error: resolve LLM endpoint: resolve OCR config file: provider "deepseek" has no api_key or api_key_cmd configured and no environment variable fallback found
```

The exact output is in [review-ocr.txt](review-ocr.txt). No provider or credential configuration was changed, and no substitute engine route was invented.

Delegation preview and rule resolution also exited 0. They selected 14 of the 24 changed files; the reviewer applied the resolved default/Kotlin rules manually. This additional inspection does **not** satisfy or replace the required own-engine run. [Selection evidence](review-ocr-preview.txt).

| File | Manual inspection with OCR rules | Required own-engine result |
| --- | --- | --- |
| `evidence/tv-fire-design/capture.init.gradle` | Opt-in androidTest source set; production build unaffected | ENVIRONMENT_FAILURE / not run |
| `evidence/tv-fire-design/capture/FireDesignCapture.kt` | Synthetic HTTP peer; target composables; screenshot assertions; inbox/notification cleanup | ENVIRONMENT_FAILURE / not run |
| `evidence/visual/tv-fire-design/SHA256SUMS` | All six author digests matched | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/main/java/com/afc/companion/MainActivity.kt` | Shared safe zone applied once; destination and linking callbacks preserved | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/main/java/com/afc/companion/link/LinkScreen.kt` | Layout and color only; polling/retry logic preserved | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/main/java/com/afc/companion/panel/LineupPanel.kt` | Focus drawings, spacing and safe-zone constraints; controller and command logic preserved | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/main/java/com/afc/companion/profile/ProfileSettingsScreen.kt` | Focus/field drawing and text style; form/editing traversal preserved | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/main/java/com/afc/companion/ui/theme/Theme.kt` | Palette, color math, type scale, button states, focus scale, inherited safe-zone logic | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/main/java/com/afc/companion/watch/WatchActivity.kt` | Native dialog styling; callbacks and cancellation remain intact | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemeContrastTest.kt` | Role pairs and thresholds; actual custom button pairs checked separately | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemeLayoutAndFocusTest.kt` | Shared-value and source-wiring checks; actual geometry checked on device | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemePaletteTest.kt` | Reference HSL and dark-background checks | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemeTestSupport.kt` | Composition disposal, theme snapshot and reflective assertions | ENVIRONMENT_FAILURE / not run |
| `tv-app/app/src/test/java/com/afc/companion/ui/theme/ThemeTypographyTest.kt` | Entire scale weight check and density-2 body pixel check | ENVIRONMENT_FAILURE / not run |

OCR excluded CHANGELOG.md, the red/green logs, restoration.txt, and the six binary screenshots by extension/type. These were manually reviewed, including image inspection; they have no own-engine coverage claim.

Reverify: not applicable — the APK was built from the reviewed source in this worktree, its signing certificate was checked, and it ran on the native device. No acquired binary was a review subject. BRAN was unavailable because this repository has no native policy; ordinary repository discovery was used.

## Device visual review

The leased Fire TV device ran at 1920×1080, density 320 (2 pixels/dp). Safe content rectangle: x=96..1824, y=54..1026. The committed opt-in instrumentation fixture renders the production composables inside the same available shell content area, with synthetic HTTP responses; no real account or provider was used for the candidate review. The production APK and instrumentation APK were rebuilt locally. Source, APK and original APK hashes are in [review-build.json](review-build.json).

| Capture under `evidence/visual/tv-fire-design/review/` | Visual assessment and author comparison | SHA-256 |
| --- | --- | --- |
| [link.png](../visual/tv-fire-design/review/link.png) | Clear heading/code/body hierarchy, cool accent, generous spacing; byte-identical to author | `2116c0f376c4e16a49a549f00aeb9d486fd8664a140a0ca1a4fe99d70498697c` |
| [profile-field.png](../visual/tv-fire-design/review/profile-field.png) | Distinct blue outline around focused League field, readable regular text, focus fully visible after scroll; byte-identical to author | `b1a9886d7ae6273276a3411a58a8424c301f8b9fff1ca69d6ff39693a2920f3a` |
| [profile-button.png](../visual/tv-fire-design/review/profile-button.png) | Blue focused fill/dark text clearly distinguishes the active button; no clipping; byte-identical to author | `e32c306a6eb62ad499207702f0cb97f592ee92af89fc24ec5923e6e803a994c5` |
| [lineup.png](../visual/tv-fire-design/review/lineup.png) | Focused row outline remains inside safe zone, readable scores/status, long second player name wraps; same geometry as author, advanced replay-age text | `75930621700eac80f407f092c7115761aec47770ef4860b81d3514c1d3e66a00` |
| [alert.png](../visual/tv-fire-design/review/alert.png) | Alert grouping and Watch focus are unambiguous, Watch/Dismiss and headline fit inside safe zone; same geometry as author, advanced replay-age text | `f1e6aee5c020012979b6680c9bd30b99c2a944b05d9aed0dc358b58d61644456` |
| [restored-panel.png](../visual/tv-fire-design/review/restored-panel.png) | Original installed app restored, panel ON, no team/league selection; byte-identical to author's restoration image | `469e13e6951c1b2b3ff00cc1e3da432b8c8ecd034028755644bacf620f8f4e19` |

[Screenshot checksum manifest](../visual/tv-fire-design/review/SHA256SUMS). All screenshots were opened and inspected. The partially visible nonfocused text at the scroll viewport edges is clipped inside the safe content area; the focused control stays fully visible. No Amazon branding or provider/broadcast content appears.

Readability was assessed from native 1080p captures and verified pixel sizes/contrast. There was no physical couch-distance observer. WatchActivity's native confirmation dialog received source review; the five requested visual states did not launch a provider or that activity.

## Verification

The four requested commands used TMPDIR under the user cache and ANDROID_HOME pointing to the installed SDK. Raw output, with home paths replaced by `<home>`, is in [review-green.txt](review-green.txt).

| Command | Exit | Result |
| --- | --- | --- |
| `cd tv-app && ./gradlew :app:testDebugUnitTest` | 0 | 272 tests, zero failures/errors/skips |
| `bash tools/ci/gate.sh tvapp` | 0 | PASS, including unit tests, lint and assembly |
| `bash tools/ci/gate.sh hygiene` | 0 | PASS |
| `bash tools/ci/gate.sh docs` | 0 | PASS |
| `cd tv-app && ./gradlew :app:assembleDebug :app:assembleDebugAndroidTest -I ../evidence/tv-fire-design/capture.init.gradle` | 0 | Candidate and opt-in capture test APKs built |
| `adb shell am instrument -w -r -e class com.afc.companion.visual.FireDesignCapture,com.afc.companion.profile.ProfileDpadFocusTest com.afc.companion.test/androidx.test.runner.AndroidJUnitRunner` | 0 | `OK (7 tests)`: four capture cases and all three existing #129 D-pad/IME cases |
| `git diff --check 72b6c35..582a030` | 0 | PASS |

All device calls were serialized with the designated flock and a valid lease. The initial ADB server inherited the lock descriptor; the local wrapper was corrected to close that descriptor in the child. An initial candidate install exited 1 with `INSTALL_FAILED_UPDATE_INCOMPATIBLE`; the default build had used a different debug key. Rebuilding with the device harness Android user directory produced the original public debug certificate (`24ba72469642c32f76d0e1ac293817117e6466835b5e75ebe33e38f53eba2d77`), and both installs then exited 0. No uninstall/data reset was used for the AFC app. These were harness/environment corrections, not candidate defects. [Build/device raw output](review-device.txt).

## Restoration and remaining obligations

The original APK was reinstalled and pulled back from the device; its bytes match SHA-256 `1d80c6822182399794bbe4cec27198a0a31da58e3533ebcb9acf431a2729b988`. Only `com.afc.companion` remains installed among AFC packages. Active AFC notification count is zero. Synthetic screenshot cache and temporary device XML files were removed. The original profile UI is unlinked/unavailable; the restored panel explicitly shows no team/league selection and is ON/visible. The local show-on-new-alert setting reads ON. The final panel image matches the author's restoration image. The lease was deleted after verification, with no later device calls. [Restoration checks](../visual/tv-fire-design/review/restoration.json).

No backend profile or lineup row readback was performed and no profile/lineup mutation was made. Relaunching the original unlinked app requested a new device-link code through its normal startup flow; no claim is made that all remote authentication state remained unchanged. Candidate device tests used only an in-process synthetic peer. Existing untracked Python caches were left untouched. Production source, tests, build files, other branches and main were not changed. PR #143 remains unmerged.

Outstanding: the required OCR own-engine assist remains unavailable and must be supplied by the orchestrator. Physical TV-distance observation and native Watch confirmation screenshots were not performed. No product repair commit is required; the follow-up commit contains review evidence only.
