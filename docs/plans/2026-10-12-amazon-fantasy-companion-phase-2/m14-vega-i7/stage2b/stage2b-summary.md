# M14 Stage 2b — on-VVD verification of the token-gated features (P2-V01)

Outcome: OWNER_DECISION_REQUIRED (environment/sandbox limit).

The owner amendment (DEC-AFC-M14-STAGE2-WRITES-20261021) allows the app's
writes on afc-dev, and the afc-dev host is now on the sandbox proxy
allowlist. The app still cannot reach afc-dev from inside the VVD. The
guest's network goes through QEMU user-mode networking, not the allowlist
proxy. No feature beyond the offline Link path could be observed, and no
synthetic profile or device was created. No app defect was found.

## What was observed (run N1, 2026-10-21T02:35:16Z to 02:36:16Z, exit 0)

- The app installed and launched. After the 10 s API timeout it showed
  "Network error. Check the connection, then select Get code." with Get code
  focused ([capture](01-link-network-error-allowlisted.png)), the same as the
  Stage 2 offline run.
- The proxy log has 0 CONNECTs to afc-dev and no abort
  ([proxy-connects.txt](proxy-connects.txt)). The guest never asked the
  proxy. strace shows no non-loopback connect apart from the sandbox's two
  network proofs (ENETUNREACH).
- Guest view ([guest-network.txt](guest-network.txt)): `resolv.conf` lists
  `127.0.0.1` and the QEMU slirp resolver `<private-ip>`. The guest has no proxy
  variable. Slirp forwards guest DNS and TCP from the emulator process
  itself. In the sandbox namespace that means the sandbox `resolv.conf`
  (`127.0.0.1`) and direct connects with no route, never the proxy.
  Whether a resolver answers there was not probed.
- `vega virtual-device start` has no proxy or emulator-argument option. The
  emulator is started with `-dns-server auto` and no `-http-proxy`.
- afc-dev itself is up: a read-only `GET /link` from the workstation
  returned 200 `text/html` at 02:37:06Z.
- Backend code (origin/main) confirms that linking needs no secret.
  `POST /v1/link/confirm` takes only `{code, profileId}`, so a synthetic
  profile works once the app can show a code.

## Verdicts

| Feature | Verdict | Reason |
|---|---|---|
| Device linking | NOT_RUN online (offline path observed again) | The app cannot reach afc-dev from the VVD in this sandbox, so no code is shown and confirm cannot run. |
| Profile settings with detection | NOT_RUN | Needs a linked session; blocked by the same network limit. |
| Alerts | limited (backend/data limit) + NOT_RUN | Blocked by the network limit. Even when linked, no public API writes a lineup (`store.put_lineup` has no caller in `backend/src`), so a synthetic manual-lineup profile can never match an event or receive an alert. |
| Watch | limited (backend/data limit) + NOT_RUN | Reached only from an alert banner. No alert can exist for a synthetic profile (above). |
| Lineup panel | NOT_RUN; rows limited (backend/data limit) | Blocked by the network limit. Once linked, the panel can render only its empty state ("no lineup for this team/league"), because no public API writes a lineup. |

## Attempts on the shared blocker

1. Allowlist the afc-dev host, then launch (N1). Result: network error, 0 afc-dev CONNECTs.
2. Guest-level proxy setting. The guest shell runs as `app_user`. It has no
   proxy variable, and no supported proxy or DNS setting was found.
3. VVD launcher option. None exists (`vega virtual-device start --help`).

Any further step changes the sandbox containment, so it goes to the owner.

## Owner options

1. Authorise one sandbox change that gives the guest a path to the proxy.
   For example, a DNS responder in the sandbox namespace that answers only
   the afc-dev host plus a transparent CONNECT forwarder, or a wrapper that
   starts the emulator with `-http-proxy`. Either one also needs guest DNS
   to resolve, and the proxy matches CONNECT by host name, so an IP CONNECT
   would be DENIED and abort the run.
2. Run the token-gated checks on a host where the VVD has normal
   networking, outside this sandbox. That relaxes containment.
3. Accept the Jest suite (162/162) plus the offline on-VVD evidence as the
   Vega basis, and keep the four features `unknown` on device.

For alerts, Watch and panel rows, a public lineup write path (or an owner
fixture) is also needed, whichever option is chosen.

## Check and run

- `vega-app/vvd-checks/probe-guest-network.sh` (with `lib.sh`), run inside
  the sandbox as `run.py <work> -- /usr/bin/bash probe-guest-network.sh <evidence-dir>`.
  Steps in [check-probe-guest-network-steps.txt](check-probe-guest-network-steps.txt).
  `getent` and `ip` exit 1 because those tools are absent in the guest.
  Every app and VVD step exited 0.
- `.vpkg` x86_64 sha256 `7093fd58…f33044`, unchanged.
- Allowlist change: [allowlist-diff.txt](allowlist-diff.txt). It is left
  in place for the next attempt.

## Containment

All six containment proofs exited 0. The proxy allowed only
`k-artifactory-external.labcollab.net` (20) and
`kepler-static-artifacts.kepler.labcollab.net` (1). The canary
`example.com` was denied. No afc-dev or other host was contacted from the
sandbox, and no backend write occurred.
