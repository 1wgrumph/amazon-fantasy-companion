---
type: evidence
title: Vega-primary documentation and repository sources
okf_status: draft
tags: [vega, planning, sources]
---

# Source ledger — retrieved 2026-10-14 UTC

Read-only documentation GETs through the web tool. No installer, SDK,
package or account downloaded or accessed. Summaries establish documented
capability, never proof that this application runs. Each URL below was
requested on this date; repeated `find` reads use the same retrieved page.

| ID | URL requested | Result / planning evidence |
|---|---|---|
| VP-S01 | https://developer.amazon.com/docs/vega/0.24/install-vega-sdk.html | Redirect to suffixless URL. User-home CLI/SDK; Node >=18, native curl, KVM, Watchman; Python 3.8 is for native debugging. Installer can edit user shell profiles. Inspect before execution; no SDK terms acceptance inferred. |
| VP-S02a | https://developer.amazon.com/docs/vega/0.24/continuous-integration.html | Fetch failed; no evidence taken from this request. |
| VP-S02 | https://developer.amazon.com/docs/vega/0.24/continuous-integration | Ubuntu 20.04/22.04/24.04 x86_64 listed. NONINTERACTIVE skips prompts; SDK example 0.24.9311 is a candidate, not a qualified pin. |
| VP-S03 | https://developer.amazon.com/docs/vega/0.24/run-apps.html | Redirect to suffixless URL. VVD x86_64 package, bounded startup, remote controls; optional Amazon-services registration. Physical developer mode requires browser login. Full VVD input requires developer mode. |
| VP-S04 | https://developer.amazon.com/docs/vega-api/0.24/expo-notifications | Local methods only; no push, triggers or badges; explicitly does not work on VVD. Version table names RN 0.72 / SDK 0.23 and earlier, conflicting with the 0.24 library overview. Exact SDK/RN/package/device combination must be qualified. |
| VP-S05 | https://developer.amazon.com/docs/react-native-vega/0.72/linking | canOpenURL/openURL available; an open promise does not establish game arrival or entitlement. |
| VP-S06 | https://developer.amazon.com/docs/vega-api/0.24/supported-libraries | RN 0.72 notifications listed; RN 0.83 notifications not supported. MMKV, AsyncStorage, Jest and TVFocusGuideView listed. Presence in a list does not prove credential containment or provider detection. |
| VP-S07 | https://developer.amazon.com/docs/adbt/port-fire-os-app-to-vega | Native Fire OS code requires rewrite; physical device recommended; VVD screenshot/performance tooling limitations stated. No performance claims planned. |
| VP-S08 | https://developer.amazon.com/docs/vega/0.24/kvd-issues | WebView unavailable on Ubuntu VVD. Phone/browser linking avoids needing TV WebView. |
| VP-S09 | https://developer.amazon.com/docs/vega/0.24/media-player-device | VVD DRM limited to L3 on Apple Silicon; Ubuntu VVD cannot establish provider playback. No companion video player proposed. |
| VP-S10 | https://developer.amazon.com/docs/react-native-vega/0.72/asyncstorage | Fetch failed. No new storage claim from this request. App-private storage requires runtime/inspection evidence; no encryption claim. |
| VP-S11 | https://developer.amazon.com/docs/vega/0.24/vda-tools | Documents gwsi-tool-screenshooter and VDA pull. Does not settle VP-S07's VVD capture limitation; qualify or use labeled host-window capture. |
| VP-S12 | https://developer.amazon.com/docs/vega-api/0.24/expo-linking | Example uses pkg:// component URI with canOpenURL/openURL. Does not verify any sports-provider component or game URI. Version guidance also needs exact pin qualification. |
| VP-S13 | https://developer.amazon.com/docs/vega-api/0.24/react-native-async-storage__async-storage | Fetch inaccessible. No capability inferred. |
| VP-S14 | https://developer.amazon.com/docs/react-native-vega/0.72/network | Fetch cache miss. fetch/AbortController remain design candidates, not runtime proof. |
| VP-S15 | https://developer.amazon.com/docs/vega/0.24/build-an-app | SDK build and manifest OS version declaration documented; generated build configuration must select architecture explicitly. |

## Local evidence and precedence

- Branch baseline `5097585` includes V01 commits `2d243df` and `5097585`.
  [Prior receipt](../P2-V01-plan/receipt.md): CHANGE_REQUESTED, F2–F8
  exact-text applied, F1 still open; none is reclassified as approved here.
- Local `origin/main` read at `42b8be9`: `backend/src/api/openapi.yaml`
  requires code, passphrase and profileId at `/v1/link/confirm`.
  This contradicts the supplied SD-048 decision, not an authorization to
  restore a passphrase. SD-048 reconciliation must precede linked-system proof.
- A01 branch tip `caa93d0`: supplied owner status is code green but unlanded;
  no independent acceptance inferred. A02–A05 unstarted per task packet.
- B01 live on `afc-dev`, B03 in review, X05 PR1 landed: owner-supplied state;
  no AWS call or credential access in this session. X05 merge is visible in
  local `origin/main`; deployment correctness is not reverified here.
- [Prior host check](../P2-V01-plan/host-check.txt): Ubuntu 26.04.1,
  KVM accessible, Node 22, Watchman absent, python3.8 absent, SDK absent.
  These are prior same-day observations, not a new install qualification.
- BRAN unavailable (no native policy); repository discovery used instead.

## Source-to-deliverable coverage

| Owner objective / input topic | Delivered authority / evidence |
|---|---|
| 1. Re-sequence A01–A05 and X01–X04/X07/X09/X12/L05; reuse V01T/V01 | Technical-plan disposition table; each existing slice's additive `vega_primary_contingency`; effective dependency projection in this evidence directory |
| 2. SDK, VVD, physical device, dated submission critical path | Technical-plan critical path; SEIT primary-contingency procedures; install, host, device and deadline risks |
| 3. Linking, all profile settings, alerts, Watch, lineup panel parity | Design parity table; existing register mappings plus additive primary validation cases; no feature declared proven |
| 4. Unchanged backend; necessary backend work | Design contract boundary and SD-048 reconciliation; existing B01–B07/L02/L03 bindings, provider registry data only through X03 |
| 5. License, Ubuntu matrix, Watchman, account and platform choice | Owner-decision batch VP-OD-01..05; risk controls; selected capabilities retained |
| 6. Additive house-schema delta; gate; commit only | Mechanical additive/schema/graph receipts, package freeze, rendered Manifest and repository gate log |
| Prior V01 review F1 and F2–F8 | F1 unresolved explicitly; existing corrected fields preserved byte-for-value; no spent review round reset |
| SD-040 and SD-048 | Fire OS remains active until explicit switch; code-only linking is settled, no repeated question |
| Submission scope beyond TV | Backend, documentation, feedback, final assurance, owner publication/submission remain; downstream release/spec slices receive conditional target bindings |

Research caveats remain visible: docs conflicts, missing fetches, simulator
limitations and unqualified SDK/host APIs are not product failures or PASS.
