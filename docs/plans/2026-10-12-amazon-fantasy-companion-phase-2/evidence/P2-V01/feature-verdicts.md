# P2-V01 per-feature verdicts (PROC-VEGA-FEATURE-VERDICT)

Vega is a compatibility target on the Vega Virtual Device only. Fire OS is
primary. Physical Vega (AC-AFC-P2-VEGA-05 / OA-12) is NOT_APPLICABLE by
owner decision; no armv7 or physical path was attempted. Current VVD verdicts
include the [token-persistence repair](../../m14-vega-i7/bug-token/summary.md)
and [default-panel repair](../../m14-vega-i7/bug-panel/summary.md), both
observed on 2026-10-21. Earlier Stage 2/2b/2c results below are historical;
the token-persistence defect and missing default panel were subsequently
repaired. The [review repair](../../m14-vega-i7/review-repair/summary.md)
covers saved-panel wiring, pending requests and stale labels with source
regressions; that round did not rerun the VVD.

| Feature | Verdict | Fire OS register UIDs mirrored | Evidence | Limit |
|---|---|---|---|---|
| Device linking | PASS on the VVD: online linking and persistence after relaunch (bug-token) | AFC-PR-038, AC-AFC-P2-VEGA-04 | [repair run](../../m14-vega-i7/bug-token/summary.md), [receipt](../../m14-vega-i7/bug-token/receipt.json), [relaunch](../../m14-vega-i7/bug-token/09-reload-top.png); `__tests__/auth/appTokenStore.test.ts` | Replacement storage binding retained the session after terminate/launch without a new code, and the saved RedZone state reloaded. The Stage 2 offline requesting/error/retry captures remain valid negative-state evidence. Native data-root messages remain unexplained (F-055); no clean-log claim. |
| Profile settings with detection | PASS on the VVD for load/change/save/reload (bug-token); detection not exercised | AFC-PR-002, -003, -005, -009, -010, -015..-023, -057, -066, AFC-PR-037 | [repair run](../../m14-vega-i7/bug-token/summary.md), [saved state](../../m14-vega-i7/bug-token/saved.png), `__tests__/profile/*.test.ts`, `__tests__/detect/appDetector.test.ts` | Every control round-trips and persists across a simulated restart. Detection is `Linking.canOpenURL('pkg://…')`, a documented candidate only — never observed on the VVD; provider availability truth is not established there. Voice is hidden with a stated limit (no verified voice route, AFC-PR-022). |
| Alerts | limited (backend/data), Stage 2c | AFC-PR-015, -021, -027, -028, -032, -033, -061, -062 | `__tests__/alerts/*.test.ts` | Long-poll feed, presenter and notifier content are unit-proven. RN 0.83 has no verified local-notification route on Vega, so delivery is an in-app banner; heads-up display over provider playback is not supported on the VVD and was never observed. |
| Watch | limited (backend/data), Stage 2c | AFC-PR-030, -031, -035, -036, -048 | `__tests__/watch/watchLauncher.test.ts` | Only a verified `platform_routes.vega` launch executes, exactly one outcome is reported, and a started launch is honestly `accessUnknown`. Provider apps, DRM and entitlement are not supported/unknown on the VVD, so no playback claim exists; the launch itself was never observed on device. |
| Lineup panel | PASS on the VVD for the empty default state (bug-panel); populated rows limited (backend/data) | AFC-PR-039..-048, -061, -062 | [repair run](../../m14-vega-i7/bug-panel/summary.md), [receipt](../../m14-vega-i7/bug-panel/receipt.json), [default](../../m14-vega-i7/bug-panel/panel-default.png), [held](../../m14-vega-i7/bug-panel/panel-default-held.png); `__tests__/panel/*.test.ts` | The no-selection profile shows the server identity, Half-PPR and Total: Unavailable, with no fabricated rows. Saved settings, serialized refresh and stale labels are additionally covered by `appPanelIntegration.test.ts` in the [review repair](../../m14-vega-i7/review-repair/summary.md); those new changes have no fresh device confirmation. Populated rows, live values and pixel-size qualification remain unobserved. modeB is not supported; fullScreen is used. |

## Historical Stage 2 blocker (2026-10-21)

The main screen (profile, alerts, Watch, panel) renders only with a stored
session token. A token comes only from `POST /v1/link` plus the
phone/browser confirm. Both are afc-dev writes outside the Stage 2
authority, and origin/main has no synthetic-token fixture. Owner options are
in the [stage 2 summary](../../m14-vega-i7/stage2/stage2-summary.md#owner-options-pick-one-to-unblock-the-four-features).

## Historical Stage 2b result (2026-10-21)

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

## Historical Stage 2c result (2026-10-21)

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
