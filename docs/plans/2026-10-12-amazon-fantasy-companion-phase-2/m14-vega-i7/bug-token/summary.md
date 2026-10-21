# AFC-M14-TOKEN-PERSIST — implementer return

**CREDENTIAL FINDINGS:** Three generic-key scan matches were verified source/evidence SHA-256 values, not credentials. Discard as false positives; [classification](credential-findings.json). No real credentials found.

Result: **PASS** for the packet objective. Observer: Codex implementer, 2026-10-21 UTC. Return to Claude Code session <orchestrator-session>. No other agents started; no commits, pushes, PR edits, or issue mutations.

`appTokenStore()` now lazily loads the default export of the supported app-private AsyncStorage package. The `TokenStore` interface, session key, and read/write/clear behavior are unchanged. The misleading mmkv comment is corrected. The package is pinned to `2.1.9000000001`.

Changed product paths: `vega-app/src/auth/tokenStore.ts`, `vega-app/package.json`, and `vega-app/package-lock.json`. The lock adds 81 dependency entries and promotes necessary existing development dependencies; no existing package version changed and no entry was removed. The supplied untracked regression remains unmodified. Evidence is confined to this directory; raw captures, logs, archives, and scan inputs remain in the packet's authorized private evidence area and sandbox work directory.

| Check | Evidence | Result |
| --- | --- | --- |
| Red regression on HEAD 36b154d | [red-jest.txt](red-jest.txt) | 2/2 fail: legacy binding and lost token |
| Full Jest suite after fix | [green-jest.txt](green-jest.txt) | 20 suites, 164/164 tests pass; exit 0 |
| TypeScript | [tsc.txt](tsc.txt) | exit 0 |
| Dependency admission | [supply-chain.json](supply-chain.json), [artifact identities](supply-chain-artifacts.json) | PASS; 75 unique archives verified before installation |
| Exact installation | [install.json](install.json) | npm 11.15.0, scripts disabled; exit 0 |
| Configured sandbox build | [build.txt](build.txt), [build-stderr.txt](build-stderr.txt) | SDK 0.24.12112; all three architectures build; exit 0 |
| Built x86_64 package admission | [vpkg-scan.json](vpkg-scan.json) | PASS; non-stub payload digests, malware and secret checks |
| VVD driver/install/relaunch/shutdown | [steps.txt](steps.txt), [driver.txt](driver.txt), [VVD status](vvd-status.txt) | 74/74 steps exit 0; driver exit 0; device stopped |
| Existing online verifier | [verify-link-online.txt](verify-link-online.txt) | 5/5 PASS; exit 0 |
| Containment | [runtime-summary.json](runtime-summary.json) | six proofs pass for build and device; no proxy abort or outside-allowlist destination |

Commands: `npm install --ignore-scripts --save-exact --no-audit --no-fund @amazon-devices/react-native-async-storage__async-storage@2.1.9000000001`; `npm test -- --runInBand`; `npx --no-install tsc --noEmit`; sandboxed `npm run build:app` with the existing `AFC_API_BASE_URL` build setting; sandboxed `drive-vvd.sh`; workstation `confirm-link.sh` for the existing synthetic profile; unchanged `verify-link-online.py` against the private run captures. npm cache and scan inputs were directed to the authorized private evidence area for acquisition.

Final installed vpkg SHA-256: `ff609f31ce07d4eaa1e2d735f02a5081ebbef8b6b1355e1418b596115d8a8c2c`.

Dependency archive SHA-256: `35d6f686f74bf3c5eb3015fc392731e8e53ca56b3525544278324befdd85346b`.

Registry integrity: `sha512-uMXS2o77o7HytYYP18jlAXEYGCm4qUIKrx56tmFk+WVcJfkuP6Is6tJAY7OFiQa4B7Q/qNniCokYUN79jjY76w==`.

The linked [before](04-main-loaded.png) and [after relaunch](09-reload-top.png) screens both have SHA-256 `35e0d198e6d8b77118a7b6a366d6c4196e068be76398eb4795ac58778f90199f`. Both visibly show Profile/Settings. No second code or confirmation was needed. The saved RedZone state also matches byte-for-byte before and after relaunch. The existing verifier's historical filenames `11-relinked-top` and `12-relinked-redzone` are retained; this run did not relink. The initial code screen remains private because it contains the development endpoint. Its hash is in the receipt.

The app performed one initial link and one profile save; workstation confirmation returned HTTP 200 for the already existing `afc-vega-vvd-synthetic` profile. No additional profile was created. Other write endpoints were not exercised.

The first build omitted `AFC_API_BASE_URL`, and its first device run correctly showed “Backend not configured.” Classified as build configuration, not a product defect. The second build supplied the already allowlisted endpoint and passed. [First build](build-attempt1.txt) and [first package scan](vpkg-scan-attempt1.json) are retained. No proxy, allowlist, manifest source, or unrelated app source was changed. Two build/device attempts were used; no repair or review budget was spent.

Log disposition: all captured snapshots have zero legacy AsyncStorage deprecation warnings. Native “Application data root path is not set” messages still occur; see [excerpt](app-log-excerpt.txt) and [counts](log-checks.json). Persistence and authenticated profile reload pass despite these messages. Their remaining origin is unresolved; this packet does not claim a clean native log or a fix for those messages.

Supply-chain residual: npm audit reports inherited high flags through the code-generation dependency to existing micromatch/braces. The storage runtime entry loads only TurboModuleRegistry and invariant; it does not load that code-generation path or accept untrusted glob patterns. No critical or reachable new high was identified in this integration. Existing dependency advisories remain outside this packet; no automatic audit repair or unrelated upgrade was attempted. The archive manifest includes the vendor build suffix `+1.23.1`; the registry and lock use the exact published version above.

Origin/prevention: P2-V01 selected legacy storage, and fake-storage unit tests did not exercise the production binding. The supplied regression now checks the production factory, forbids legacy calls, and simulates a relaunch. Retain the VVD terminate/launch persistence check with future storage or SDK changes; mock-only tests cannot prove native persistence. BRAN is unavailable for this worktree; ordinary discovery and direct evidence were used.

All in-directory artifact hashes, relevant source/check hashes, and selected private raw artifact hashes are in [receipt.json](receipt.json). This is implementer verification, not independent review or formal release acceptance. Panel behavior was not investigated; no publication or runtime activation was performed.
