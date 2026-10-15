---
type: evidence
title: P2-V01 planning delta sources (Vega documentation)
okf_status: draft
tags: [evidence, vega, p2-v01, planning]
---

# P2-V01 planning delta: Vega documentation sources

These are read-only HTTP GETs to developer.amazon.com, retrieved 2026-10-14
(UTC). Nothing was downloaded or installed. The docs label 0.24 as "LATEST".

| # | URL | Retrieved | Established |
|---|---|---|---|
| S1 | https://developer.amazon.com/docs/vega/latest/install-vega-sdk.html | 2026-10-14 | Redirects to 0.24 (current docs version). |
| S2 | https://developer.amazon.com/docs/vega/0.24/install-vega-sdk.html | 2026-10-14 | Node.js 18.x or later. Ubuntu dependencies: native (non-snap) curl, lz4, `libpython3.8-dev` from the deadsnakes PPA, Watchman, KVM. Installer `curl -fsSL https://sdk-installer.vega.labcollab.net/get_vvm.sh \| bash`, default `~/vega/sdk`, CLI in `~/vega/bin`. The VVD is installed with the SDK. Verify with `vega --version`. The page names no license or account step. |
| S3 | https://developer.amazon.com/docs/vega/0.24/continuous-integration.html | 2026-10-14 | Host configurations: Ubuntu 20.04, 22.04 or 24.04, x86_64. Environment variables `NONINTERACTIVE`, `SKIP_VVD_INSTALL`, `SKIP_SDK_INSTALL` and `VEGA_SDK_VERSION` (example 0.24.9311). |
| S4 | https://developer.amazon.com/docs/vega/0.24/vega-release-notes.html | 2026-10-14 | SDK 0.24: React Native 0.83 for Vega in early access, RN 0.72 still supported. The VVD supports copy and paste and PCON. Intel Mac support ends 2026-12-15 ("Apple Silicon Mac or Ubuntu x86_64"). No Ubuntu version is named. |
| S5 | https://developer.amazon.com/docs/vega/0.24/sdk-install-issues.html | 2026-10-14 | At least 20 GB free disk. The snap curl warning. |
| S6 | https://developer.amazon.com/docs/vega/0.24/cli-tools.html | 2026-10-14 | `npx react-native build-vega`; `vega virtual-device start/stop/status`; `vega device list`; `vega device install-app -p <vpkg> --device <name>`; `vega device launch-app`; `vega run-app`; log stream and `copy-logs`; `vega device is-app-installed`; `vega device installed-apps`. Screenshots and input are not on this page. |
| S7 | https://developer.amazon.com/docs/vega/0.24/run-apps.html (last modified 2026-10-13) | 2026-10-14 | `vega virtual-device start --timeout 120`; `vega run-app <vpkg> <component-id> -d VirtualDevice`; `.vpkg` at `build/<ARCH>-<BUILD_TYPE>/<APP>_<ARCH>.vpkg` (x86_64 for the VVD, armv7 for Fire TV); limited `inputd-cli` until `vsm developer-mode enable`; `--no-gl-accel` on Ubuntu. Physical device: developer mode, `vega devmode login` (browser), `vega devmode enable-device --code <code>`. |
| S8 | https://developer.amazon.com/docs/vega/0.24/build-an-app.html (last modified 2026-09-15) | 2026-10-14 | `vega project generate --template helloWorld ...`; `npm install`; `npm run build:app`; architecture list. No test or lint command. |
| S9 | https://developer.amazon.com/docs/vega/0.24/hello-world.html (last modified 2026-07-30) | 2026-10-14 | Vega Studio GUI flow only. |
| S10 | https://developer.amazon.com/docs/adbt/port-fire-os-app-to-vega (last modified 2026-09-30) | 2026-10-14 | A native Fire OS app needs a full rewrite to React Native for Vega. A physical device is recommended because "screenshot support and performance tooling analysis aren't available on a VVD". |
| S11 | https://developer.amazon.com/docs/vega-api/0.24/supported-libraries | 2026-10-14 | Jest 29.7.0; react-native-mmkv; async-storage; expo-linking; expo-notifications (RN 0.72 only); react-native-axios; netinfo; TVFocusGuideView. No keychain or secure-storage library, no Testing Library and no installed-apps library. |
| S12 | https://developer.amazon.com/docs/vega/0.21/vda-tools | 2026-10-14 (search result) | VDA shell `gwsi-tool-screenshooter <file.png>` screenshot route. This conflicts with S10. |
| S13 | https://developer.amazon.com/docs/vega/0.21/inputdcli | 2026-10-14 (search result) | `inputd-cli button_press KEY_*`; developer mode is needed on the VVD for the full set. |
| S14 | https://developer.amazon.com/docs/vega/0.22/kvd-issues.html | 2026-10-14 (search result) | KVM must be enabled. WebView is unsupported on the VVD on Ubuntu. Low-memory warning. |
| S15 | https://developer.amazon.com/docs/vega/0.22/media-player-device.html | 2026-10-14 (search result) | DRM playback on the VVD is L3 only and only on Apple Silicon Macs. |
| S16 | https://developer.amazon.com/docs/react-native-vega/0.72/linking | 2026-10-14 (search result) | `Linking.canOpenURL` and `openURL`; the `{amzns/amzn}://apps` package-manager scheme. |
| S17 | https://developer.amazon.com/docs/vega-api/0.24/expo-notifications | 2026-10-14 (search result) | Local notifications only. No push or triggers. |
| S18 | https://developer.amazon.com/docs/react-native-vega/0.72/asyncstorage | 2026-10-14 (search result) | AsyncStorage is unencrypted. |

Rows marked "search result" were read from search-result extracts of
developer.amazon.com pages, not from a full page fetch. The 0.24 equivalents
are rechecked at P2-V01 dispatch.
