# M14 Stage 2c — VVD guest traffic through the allowlist proxy; online features (P2-V01)

Outcome: REPAIRABLE_FAILURE (one app defect: the session token does not
survive an app relaunch).

Observer: Claude Code (Test Implementer, M14 frozen route), 2026-10-21.

The VVD guest now reaches afc-dev only through the allowlisting CONNECT
proxy. Device linking worked end to end. A settings change was saved and
then read back from afc-dev after a full app restart. The app loses its
session token on relaunch. The panel showed "Panel unavailable", and no
alert appeared for the synthetic profile.

## Routing method that worked (hypothesis 2)

Hypothesis 1 (emulator `-http-proxy` or `http_proxy`) was rejected before
any run. The emulator binary does support a proxy, but its connector sends
`CONNECT %s HTTP/1.1` with the guest's destination address, which is an IP.
The proxy matches CONNECT by host name, so it would deny that request and
abort the run. The guest also cannot resolve any name in the sandbox, so it
never reaches a TCP connect at all.

Hypothesis 2 was added to the sandbox `outer.py` and switched on by a
`guest_forward` entry in `config.json`
([runtime-change.diff](runtime-change.diff)). It starts after the six
containment proofs pass:

- A resolver on `127.0.0.1:53` inside the namespace. It answers an A query
  for the afc-dev host with `<private-ip>`, the namespace's existing dummy
  address. AAAA gets an empty answer, and every other name gets NXDOMAIN.
  The emulator's slirp DNS (`-dns-server auto`) already reads this resolver
  from the sandbox `resolv.conf`.
- A listener on `<private-ip>:443` that sends each connection to the proxy
  as `CONNECT <afc-dev host>:443`. TLS stays end to end between the app
  and afc-dev.
- No route, interface or allowlist entry was added. `outer.py` asserts that
  the forward host is on the allowlist and that the address is the d0
  address. The namespace still has no default route.

Smoke run (2026-10-21T02:51:39Z, exit 0), using the sandboxed SDK node:
`example.com` returned ENOTFOUND, the afc-dev host resolved to
`<private-ip>`, and a read-only `GET /link` returned 200 through
`CONNECT afc-dev:443` ([guest-forward.txt](guest-forward.txt)).

## Run C1 (2026-10-21T02:52:41Z to 03:00:18Z, exit 0, no abort)

`vega-app/vvd-checks/drive-vvd.sh` starts the VVD, installs and launches
the app, then runs the remote-key commands in
[drive-commands.txt](drive-commands.txt). All 138 steps exited 0
([check-drive-vvd-steps.txt](check-drive-vvd-steps.txt)). The phone side
is `vega-app/vvd-checks/confirm-link.sh`, run on the workstation. The codes
were read from the captures.

| Step | Observed | Capture |
|---|---|---|
| Launch, no token | `POST /v1/link` succeeded: code `P8UL6AUP`, link page URL, expiry | [01](01-link-code.png) |
| Phone confirm, profile `afc-vega-vvd-synthetic` | HTTP 200 `{"state": "linked"}` at 02:53:36Z | [confirm-results.txt](confirm-results.txt) |
| Poll after confirm | The TV switched to Profile/Settings, and the profile loaded (all selections none) | [04](04-main-loaded.png) |
| Change one control | Alert types: RedZone off, then on | [05a](05a-redzone-off.png), [05](05-redzone-on.png) |
| Save | Save profile focused, then "Saved" at the top | [05b](05b-save-focused.png), [08](08-top-after-save.png) |
| Panel (visible, team/league none) | "Lineup panel / Team/league: none / Panel unavailable", 35 s after save | [07](07-panel-section.png) |
| App relaunch | **Defect:** the app showed "Link this TV" with a new code `B7BUDVMF` instead of Profile/Settings | [09](09-reload-top.png) |
| Second confirm, same profile | HTTP 200 linked at 02:59:18Z; Profile/Settings again | [11](11-relinked-top.png) |
| Reload check | Alert types: RedZone, RedZone on. Byte-identical to the pre-save capture, so the saved setting came back from afc-dev | [12](12-relinked-redzone.png) |

`verify-link-online.py`: 4 PASS, 1 FAIL, exit 1
([verify-link-online.txt](verify-link-online.txt)). The FAIL is the
relaunch defect.

## Verdicts

| Feature | Verdict | Basis |
|---|---|---|
| Device linking | PASS for code → confirm → linked; FAIL for persistence (app defect) | Code shown, confirm 200, TV moved to the profile. After an app relaunch the TV is unlinked again. |
| Profile settings | PASS (load, change, save, reload) | RedZone saved, then shown on after a restart and re-link to the same profile. Detection was not toggled, so `POST /v1/installed-apps` was not exercised. |
| Alerts | limited (backend/data) | No banner appeared in about 6 linked minutes. No public API writes a lineup, so the synthetic profile cannot match an event. |
| Watch | limited (backend/data) | Reached only from an alert banner, and no alert can exist (above). `POST /v1/routing-outcome` was not exercised. |
| Lineup panel | NEEDS_MORE_EVIDENCE; rows limited (backend/data) | The UI showed "Panel unavailable". Backend code (`panel.snapshot`) would return an empty `unassigned/unassigned` state for this profile, which `decodePanel` accepts, so an empty panel was expected. TLS hides the API status, and the app logs no requests, so the cause (app or backend) is not established. |

## App defect: session token not persisted (red evidence)

- Expected: a linked TV opens Profile/Settings after the app restarts
  (AFC-PR-038; `auth/tokenStore.test.ts` claims persistence).
- Observed: after `terminate-app` and `launch-app`, the Link screen appeared
  with a new code ([09](09-reload-top.png)).
- Log ([app-log-excerpt.txt](app-log-excerpt.txt)): every token read and
  write logs `Legacy AsyncStorage is on a deprecation path. Please migrate
  to using @amzn/react-native-async-storage__async-storage`, followed by
  `ERROR … [KeplerScript-Native] Application data root path is not set.`
- Code: `vega-app/src/auth/tokenStore.ts` uses
  `require('react-native').AsyncStorage`. Its header says the store is
  react-native-mmkv. The unit test runs over an in-memory fake, so it
  cannot see the platform failure.
- Class: app defect, with residual doubt. Whether the "data root path"
  error also affects the supported async-storage package on the VVD is not
  established. The token stayed usable within a session (profile load and
  save worked).

## Synthetic identifiers created on afc-dev

- Profile `afc-vega-vvd-synthetic`. The owner's name for it, "AFC Vega VVD
  synthetic", is not a valid profileId (the pattern is
  `[A-Za-z0-9_-]{1,64}`). The profile now holds one saved Settings revision
  (RedZone on).
- Device links: codes `P8UL6AUP` and `B7BUDVMF`, both confirmed and both
  now used. Two device sessions were minted. No token was read, printed or
  stored outside the guest.
- afc-dev writes, all inside the amendment: 2 × `POST /v1/link` (app),
  2 × `POST /v1/link/confirm` (workstation), 1 × `PUT /v1/profile` (app).
  No `POST /v1/installed-apps` and no `POST /v1/routing-outcome`.

## Containment

- All six containment proofs exited 0 ([containment-proofs.txt](containment-proofs.txt)).
- Proxy ([proxy-connects.txt](proxy-connects.txt)): afc-dev was allowed
  twice (one keep-alive TLS connection per app process). The other
  connections were the existing SDK hosts, the `example.com` canary denial
  during the proofs, and one host-less incomplete CONNECT (also seen in
  Stage 2). There was no other DENY and no abort.
- Resolver ([guest-dns.txt](guest-dns.txt)): the guest OS asked for 10
  other Amazon, captive-portal and Google names. All got NXDOMAIN, and none
  were connected.
- strace ([strace-connects.txt](strace-connects.txt)): the only
  non-loopback connects were the two proof ENETUNREACH probes and two
  connects to `<private-ip>:443` (the in-namespace forwarder).
- VVD `running:true` before stop and `running:false` after stop
  ([vvd-status.txt](vvd-status.txt)). `.vpkg` sha256 `7093fd58…f33044`
  is unchanged.
- The runtime change is left in place, with sha256 values in
  [runtime-change.diff](runtime-change.diff).

## Frictions

- The emulator's HTTP proxy connector sends CONNECT with an IP, so it
  cannot work with a host-name allowlist. A DNS-plus-forwarder shim was
  needed.
- The link code and every setting can only be read from screen captures.
  There is no OCR and no app-side state dump, so a person or agent must
  read the code and drive the screen.
- Reaching Save takes about 30 DOWN presses from the top of the screen.
  Focus starts on nothing, and text inputs take focus silently.
