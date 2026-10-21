# M14 Stage 2 — on-VVD feature verification of the Vega port (P2-V01)

Outcome: OWNER_DECISION_REQUIRED.

The AFC app installs, launches and renders on the Vega Virtual Device. Its
offline Link path behaves as specified and accepts remote input. Every other
feature, and the online half of linking, needs a session token. The app can
only obtain one through `POST /v1/link` and the phone/browser confirm, and
both are backend writes outside this packet's authority. Those features are
`NEEDS_OWNER_DECISION`. No app defect was found.

## Verdicts

| Feature | Verdict | Observed on the VVD | Blocking request |
|---|---|---|---|
| Device linking | NEEDS_OWNER_DECISION (offline path observed working) | Launch → "Link this TV / Requesting a code…" → after the 10 s API timeout, "Network error. Check the connection, then select Get code." with Get code focused. KEY_ENTER on Get code reruns the request and repeats both states exactly. | A tokenless launch issues `POST /v1/link {}` (creates a pending link), then polls `GET /v1/link?handle=…`. Completion needs the confirm `POST /v1/link/confirm` from a phone/browser. |
| Profile settings with detection | NEEDS_OWNER_DECISION | Not reachable: the main screen needs a token. | Read is `GET /v1/profile` (read-only once linked). Save is `PUT /v1/profile`; with detection opted in, save also sends `POST /v1/installed-apps`. Both are writes. |
| Alerts | NEEDS_OWNER_DECISION | Not reachable without a token. | `GET /v1/alerts` long poll (read-only once linked). A banner needs an alert to be pending for the profile. |
| Watch | NEEDS_OWNER_DECISION | Not reachable without a token. | Reached from an alert banner. Records the outcome with `POST /v1/routing-outcome` (write). |
| Lineup panel | NEEDS_OWNER_DECISION | Not reachable without a token. | `GET /v1/panel?teamLeague=…` (read-only once linked). |

## Why the afc-dev host was not allowlisted

The packet allowed adding `le3r79003f.execute-api.us-east-2.amazonaws.com`
to the proxy allowlist. With no token stored, the app's first request on
launch is `POST /v1/link`, a write. Allowlisting the host would have let the
unauthorised write happen on the first launch, so `config.json` was left
unchanged (no diff). The guest's request failed inside the sandbox network
namespace, and the proxy log has no afc-dev CONNECT.

Origin/main has no synthetic-token or read-only fixture for afc-dev. The
earlier live checks (P2-X09) ran on the stick with a real linked profile.
Planting a token in app storage was probed and is not possible: the
dev-shell user is `app_user` and cannot see the app's private storage
(`probe-guest-storage.sh`).

## Owner options (pick one to unblock the four features)

1. Authorise one link session on afc-dev: one `POST /v1/link`, one confirm,
   then only read-only GETs (`/v1/profile`, `/v1/alerts`, `/v1/panel`).
   Settings save, detection reporting and the Watch outcome stay
   NEEDS_OWNER_DECISION unless writes are also authorised.
2. Provide a synthetic test token for a test profile. This is credential
   access, which only the owner can grant.
3. Accept the offline Link evidence and the 162/162 Jest suite as the Vega
   verdict basis, and keep the four features `unknown` on device.

## Check and run

- `vega-app/vvd-checks/check-link-offline.sh` (with `lib.sh`), run inside
  the sandbox as `run.py <work> -- /usr/bin/bash check-link-offline.sh <evidence-dir>`.
  Exit 0: all 19 steps exited 0 (`check-link-offline-steps.txt`).
- `vega-app/vvd-checks/verify-link-offline.py <evidence-dir>` passed 4/4
  (`verify-link-offline.txt`): the app screen differs from VVD home, the
  error state differs from the requesting state, and Get code repeats both
  states byte for byte.
- Run of record A2, 2026-10-21T00:16:56Z to 00:18:05Z. An earlier run, A1
  (2026-10-20T23:51Z, same script before the log fix), produced
  byte-identical app captures `01`–`04`.
- `.vpkg` x86_64 sha256 `7093fd58…f33044`, the same as the recorded P2-V01
  build at `8c1e4b4`. `vega-app/` has no change since that commit, so no
  rebuild was needed.
- VVD status: `running:true` (qemu 77) before input and before stop, then
  `running:false` after stop (`vvd-status.txt`).

## Containment

- Proxy: only the allowlisted `k-artifactory-external.labcollab.net` (14)
  and `kepler-static-artifacts.kepler.labcollab.net` (1) were allowed. The
  canary `example.com` was denied, and one incomplete CONNECT was rejected
  before a host was parsed (`proxy-connects.txt`).
- strace: the only non-loopback `connect` calls were the sandbox's own
  network proof (`outer.py` and `/proof network`), and both returned
  ENETUNREACH. Nothing contacted afc-dev.
- All six containment proofs exited 0.
- The allowlist also lists `registry.npmjs.org`. It was present before this
  stage, and no connection to it occurred.

## Frictions (for the developer-feedback log)

- `vega device run-cmd ... journalctl` is rejected in the developer-mode
  shell ("journalctl is not supported in developer mode shell"). Use
  `loggingctl log -v <package>` instead.
- The app's log carries only KeplerScript surface telemetry. Its
  `commitTime={:.2f}ms` fields are unformatted placeholders, a logging bug
  in the runtime. RN `console` output from the release bundle does not appear.
- The developer shell runs as `app_user` and cannot inspect an app's private
  storage. There is no supported way to seed or inspect AsyncStorage on the
  VVD for test fixtures.

## Remaining risks

- The four token-gated features and the online link are not observed on the
  VVD.
- Legibility at 1080p (AFC-PR-045) is measurable now that `xwd` capture
  works. The guest surface is 960x540 in a 1920x1080 Xvfb, so measurement
  needs scaling, and it was not done.
