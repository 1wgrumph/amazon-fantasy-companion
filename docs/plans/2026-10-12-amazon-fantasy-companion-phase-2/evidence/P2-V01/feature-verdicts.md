# P2-V01 per-feature verdicts (PROC-VEGA-FEATURE-VERDICT)

Vega is a compatibility target on the Vega Virtual Device only. Fire OS is
primary. Physical Vega (AC-AFC-P2-VEGA-05 / OA-12) is NOT_APPLICABLE by
owner decision; no armv7 or physical path was attempted. No verdict below
is `works`: that needs observed VVD evidence, and the VVD does not boot in
the current environment state (see the receipt). Every feature is proven
by the frozen Jest suite (162/162 green, CMD-VEGA-UNIT) against the
unchanged backend contract; on-device behavior stays unverified.

| Feature | Verdict | Fire OS register UIDs mirrored | Evidence | Limit |
|---|---|---|---|---|
| Device linking | unknown | AFC-PR-038, AC-AFC-P2-VEGA-04 | `vega-app/__tests__/link/linkScreen.test.ts`, `auth/tokenStore.test.ts`, `cmd-vega-unit.txt` | Code shown/expired/linked and token persistence are unit-proven over a real loopback HTTP peer. On-VVD launch and the phone/browser confirm step were never observed: the VVD exits on a pending snapshot operation (`virtual_device.err.txt`). |
| Profile settings with detection | unknown | AFC-PR-002, -003, -005, -009, -010, -015..-023, -057, -066, AFC-PR-037 | `__tests__/profile/*.test.ts`, `__tests__/detect/appDetector.test.ts` | Every control round-trips and persists across a simulated restart. Detection is `Linking.canOpenURL('pkg://…')`, a documented candidate only — never observed on the VVD; provider availability truth is not established there. Voice is hidden with a stated limit (no verified voice route, AFC-PR-022). |
| Alerts | unknown | AFC-PR-015, -021, -027, -028, -032, -033, -061, -062 | `__tests__/alerts/*.test.ts` | Long-poll feed, presenter and notifier content are unit-proven. RN 0.83 has no verified local-notification route on Vega, so delivery is an in-app banner; heads-up display over provider playback is not supported on the VVD and was never observed. |
| Watch | unknown | AFC-PR-030, -031, -035, -036, -048 | `__tests__/watch/watchLauncher.test.ts` | Only a verified `platform_routes.vega` launch executes, exactly one outcome is reported, and a started launch is honestly `accessUnknown`. Provider apps, DRM and entitlement are not supported/unknown on the VVD, so no playback claim exists; the launch itself was never observed on device. |
| Lineup panel | unknown | AFC-PR-039..-048, -061, -062 | `__tests__/panel/*.test.ts` | Decode, text/stale labels, focus, refresh and change-only updates are unit-proven. modeB composition is not supported on Vega (DES-AFC-P2-VEGA); the shipped mode is fullScreen. On-screen legibility at 1080p (AFC-PR-045 pixel measurement) needs a working capture path, which is unqualified (c17). |

## Environment state behind the verdicts

- `.vpkg` x86_64 built from commit `8c1e4b4` with the aws-afc-dev ApiUrl
  as the only injected value: `vpkg-sha256.txt`, `cmd-vega-build.txt`.
- VVD attempts 1–3 (`vvd-run.txt`, `vvd-run2.txt`, `vvd-run3.txt`): the
  emulator exits before boot completes; `vega device list` finds no
  device, so install/launch/input/capture could not run. The c16
  preparation lifecycle reached `running:true` twice earlier the same
  day, so this is an environment regression in instance state, not an
  app failure.
- Screen capture: `vvd-screencap.sh` exits 78 `NEEDS_MORE_EVIDENCE`
  (c17); c16 recorded the SDK screenshooter failing (VDA exit 139).
