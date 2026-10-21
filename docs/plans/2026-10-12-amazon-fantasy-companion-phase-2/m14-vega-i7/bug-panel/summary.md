# BUG AFC-M14-PANEL-DEFAULT — implementer return

Credential scan: the scan before adding the hash receipt passed. The subsequent generic-key findings were all verified digest-only JSON values, not credentials; see [classification](credential-findings.json). No real credential was found.

Result: **PASS** (implementer verification). Observer: Codex implementer, 2026-10-21 UTC. Return to Claude Code session amazon-fantasy-companion-47. No agents started; no commits, pushes, PR edits, issue mutations, or independent review performed.

BUG_ROUTE: frozen-lifecycle-profile owner 2026-10-16 hackathon bug fixes use the opensource-hackathon implementer.

`PanelController.onFetched` now adopts the decoded snapshot's team/league only when the controller has no selection. Its existing explicit-selection mismatch guard, visibility guard, revision handling, refresh interval and decoding remain unchanged. `App.tsx` already reads the controller's field, so no view change was necessary.

Changed product/check paths:

- `vega-app/src/panel/panel.ts`: one added line.
- `vega-app/vvd-checks/drive-vvd.sh`: additive `panel` command sends PAGEDOWN after Save profile, captures twice ten seconds apart, and captures the app log.
- `vega-app/vvd-checks/verify-panel-default.py` and `panel-default.png`: compare both captures to a visually checked reference showing the default identity, basis, no player rows and unavailable total. Existing checks are untouched.
- Evidence in this directory. Supplied untracked regression and fixture remain unmodified; their hashes are in the receipt.

| Check | Evidence | Result |
| --- | --- | --- |
| Supplied regression on HEAD `d408a06` before editing | [red-jest.txt](red-jest.txt) | Default adoption fails with null snapshot; explicit-selection negative case passes |
| `npm test -- --runInBand` in `vega-app` | [green-jest.txt](green-jest.txt) | 21 suites, 166/166 tests pass |
| `npx --no-install tsc --noEmit` | [tsc.txt](tsc.txt) | Exit 0 |
| Configured sandbox `npm run build:app` | [build.txt](build.txt), [build-stderr.txt](build-stderr.txt) | Exit 0, all three architectures built |
| Package integrity | [package-integrity.json](package-integrity.json) | 12 relative regular archive files; all six non-stub SHA-384 payload digests verified |
| Baseline on VVD | [before-panel.png](before-panel.png), [before-steps.txt](before-steps.txt) | Shows Team/league: none and Panel unavailable; 47/47 steps pass |
| Candidate on VVD | [panel-default.png](panel-default.png), [held capture](panel-default-held.png), [steps.txt](steps.txt) | Default identity, Half-PPR, no player rows, Total: Unavailable; 47/47 steps pass, driver exit 0 |
| Capture verifier against baseline/candidate | [red](red-panel-check.txt), [green](green-panel-check.txt) | Old screen rejected, exit 1; both candidate captures accepted, exit 0 |
| Sandbox containment | [runtime-summary.json](runtime-summary.json) | Baseline, build and candidate: six proofs each pass, no proxy abort, no outside-allowlist destination beyond the expected denied canary |
| Shutdown | [vvd-status.txt](vvd-status.txt) | VVD stopped |

Candidate installed x86_64 vpkg SHA-256: `877e6546620094c793f22c0b1df6cf91b875a89f9e00db95ae2134ac6c1dcbd0`.

The candidate reused the persisted synthetic-profile link. No phone confirmation or profile save was needed. Native app installation succeeded on that exact package. The two candidate PNGs are byte-identical. Author visual inspection confirmed the entire panel state and absence of player rows; this is not independent visual review.

Device command: sandbox `run.py <authorized-work-copy> -- /usr/bin/bash vega-app/vvd-checks/drive-vvd.sh <authorized-run-dir>`. [commands.txt](commands.txt) records the candidate navigation. After XWD-to-PNG conversion, run `python3 vega-app/vvd-checks/verify-panel-default.py <private-run-dir>` on the workstation. The reference requires the same synthetic profile, 1920x1080 VVD root capture, scroll, focus and converter; intentionally changed rendering needs a new visually checked reference.

Refresh evidence: the unchanged regression exercises the production controller with the recorded server body and verifies no fetch at 1,000 or 29,999 ms, then a fetch at 30,000 ms. The pinned-source device run independently shows snapshot adoption and a held default screen. The app log contains no HTTP request counter, so request cadence is established by controller regression and code, rather than independent on-device HTTP counts. No additional network instrumentation or credential inspection was introduced.

Attempts and classification: the first baseline capture stopped at Save profile and did not show the panel. A staging helper then failed with a shell-quoting SyntaxError before invoking the sandbox; it supplied no device evidence. The second actual baseline run used documented PAGEDOWN input and captured the failure. Candidate build/device each succeeded on their first attempt. A full source comparison initially differed only on `config.generated.json`: Metro intentionally regenerates it from the configured build endpoint. All 16 other source/package files match; the generated endpoint was separately verified equal to the existing allowlisted development guest-forward endpoint. No runtime configuration or proxy allowlist was changed. No review/repair budget was spent.

Origin/prevention: the Vega controller port compared every response to an explicit identity; its tests always selected a team/league. Retain the supplied recorded-body regression, including its explicit-selection negative case and refresh assertions, and the new default-panel VVD capture check. Backend defaults remain intentional.

Remaining risks: the synthetic profile has no lineup, so this run proves the empty default state, not populated rows or real fantasy-provider data. Native application-data-root errors remain in the [redacted app-log excerpt](app-log-excerpt.txt); [counts](log-checks.json) record them without claiming a clean log or a fix. Screenshot matching is deliberately specific to this VVD setup. Full Stage 2c link/settings checks and independent review were not rerun by this packet. BRAN is unavailable here; direct discovery and evidence were used.

All artifact, relevant source/check, supplied regression and selected private-raw SHA-256 values are in [receipt.json](receipt.json). Private raw captures, logs and package remain outside the repository; repository evidence is sanitized. No backend, other product source, dependencies, runtime service activation, production data mutation or publication was changed or performed.
