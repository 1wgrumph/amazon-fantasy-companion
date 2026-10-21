# P2-V01 per-feature verdicts (PROC-VEGA-FEATURE-VERDICT)

Vega is a compatibility target on the Vega Virtual Device only. Fire OS is
primary. Physical Vega (AC-AFC-P2-VEGA-05 / OA-12) is NOT_APPLICABLE by
owner decision; no armv7 or physical path was attempted. M14 Stage 2
(2026-10-21) ran the app on the VVD inside the sandbox. The offline Link
path was observed working. Every other feature needs a session token,
which only the link write flow issues, so those features are
`NEEDS_OWNER_DECISION` ([stage 2 summary](../../m14-vega-i7/stage2/stage2-summary.md)). Every feature is proven
by the frozen Jest suite (162/162 green, CMD-VEGA-UNIT) against the
unchanged backend contract; on-device behavior stays unverified.

| Feature | Verdict | Fire OS register UIDs mirrored | Evidence | Limit |
|---|---|---|---|---|
| Device linking | REPAIRABLE_FAILURE: online link observed (Stage 2c); token lost on relaunch | AFC-PR-038, AC-AFC-P2-VEGA-04 | `vega-app/__tests__/link/linkScreen.test.ts`, `auth/tokenStore.test.ts`, `cmd-vega-unit.txt` | Code shown/expired/linked and token persistence are unit-proven over a real loopback HTTP peer. On the VVD: launch, "Requesting a code…", the network-error state with Get code focused, and the Get code retry were observed ([`01`](../../m14-vega-i7/stage2/01-link-requesting.png)–[`04`](../../m14-vega-i7/stage2/04-link-error-again.png), `vega-app/vvd-checks/check-link-offline.sh` exit 0, `verify-link-offline.py` 4/4). Stage 2c observed the online flow (`drive-vvd.sh`, `confirm-link.sh`, `verify-link-online.py` 4/5). The token is not persisted across a relaunch, which is an app defect. |
| Profile settings with detection | PASS on the VVD for load/change/save/reload (Stage 2c); detection not exercised | AFC-PR-002, -003, -005, -009, -010, -015..-023, -057, -066, AFC-PR-037 | `__tests__/profile/*.test.ts`, `__tests__/detect/appDetector.test.ts` | Every control round-trips and persists across a simulated restart. Detection is `Linking.canOpenURL('pkg://…')`, a documented candidate only — never observed on the VVD; provider availability truth is not established there. Voice is hidden with a stated limit (no verified voice route, AFC-PR-022). |
| Alerts | limited (backend/data), Stage 2c | AFC-PR-015, -021, -027, -028, -032, -033, -061, -062 | `__tests__/alerts/*.test.ts` | Long-poll feed, presenter and notifier content are unit-proven. RN 0.83 has no verified local-notification route on Vega, so delivery is an in-app banner; heads-up display over provider playback is not supported on the VVD and was never observed. |
| Watch | limited (backend/data), Stage 2c | AFC-PR-030, -031, -035, -036, -048 | `__tests__/watch/watchLauncher.test.ts` | Only a verified `platform_routes.vega` launch executes, exactly one outcome is reported, and a started launch is honestly `accessUnknown`. Provider apps, DRM and entitlement are not supported/unknown on the VVD, so no playback claim exists; the launch itself was never observed on device. |
| Lineup panel | NEEDS_MORE_EVIDENCE: "Panel unavailable" observed (Stage 2c); rows limited (backend/data) | AFC-PR-039..-048, -061, -062 | `__tests__/panel/*.test.ts` | Decode, text/stale labels, focus, refresh and change-only updates are unit-proven. modeB composition is not supported on Vega (DES-AFC-P2-VEGA); the shipped mode is fullScreen. On-screen legibility at 1080p (AFC-PR-045 pixel measurement) needs a working capture path, which is unqualified (c17). |

## Stage 2 blocker (2026-10-21)

The main screen (profile, alerts, Watch, panel) renders only with a stored
session token. A token comes only from `POST /v1/link` plus the
phone/browser confirm. Both are afc-dev writes outside the Stage 2
authority, and origin/main has no synthetic-token fixture. Owner options are
in the [stage 2 summary](../../m14-vega-i7/stage2/stage2-summary.md#owner-options-pick-one-to-unblock-the-four-features).

## Stage 2b result (2026-10-21)

The owner allowed the app's afc-dev writes for one synthetic profile
(DEC-AFC-M14-STAGE2-WRITES-20261021), and the afc-dev host was added to the
sandbox proxy allowlist. The app still cannot reach afc-dev from the VVD.
The guest's network goes through QEMU user-mode networking, not the proxy,
and the VVD launcher has no proxy option (0 afc-dev CONNECTs, network error
observed again). No synthetic profile was created and no backend write
occurred. The four features stay unobserved on device. Alerts, Watch and
panel rows are additionally limited: no public API writes a lineup, so a
synthetic profile cannot receive an alert or panel rows. The owner options
are in the [stage 2b summary](../../m14-vega-i7/stage2b/stage2b-summary.md#owner-options).

## Stage 2c result (2026-10-21)

The guest's afc-dev traffic now goes through the allowlisting proxy: a
sandbox resolver answers only the afc-dev host with the namespace's dummy
address, and a forwarder there sends each connection as
`CONNECT <afc-dev host>:443`. No route was added. On the VVD, a code was
shown, confirmed for profile `afc-vega-vvd-synthetic`, and the TV linked
([01](../../m14-vega-i7/stage2c/01-link-code.png), [04](../../m14-vega-i7/stage2c/04-main-loaded.png)). RedZone was turned
on, saved, and read back from afc-dev after a restart
([05](../../m14-vega-i7/stage2c/05-redzone-on.png), [12](../../m14-vega-i7/stage2c/12-relinked-redzone.png)). App defect:
after a relaunch the app was unlinked again, and Kepler logs "Application
data root path is not set" on each legacy AsyncStorage call
([09](../../m14-vega-i7/stage2c/09-reload-top.png)). The panel showed "Panel unavailable" for a
profile with no team/league, and no alert appeared. Details are in the
[stage 2c summary](../../m14-vega-i7/stage2c/stage2c-summary.md).

## Environment state behind the earlier verdicts

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
