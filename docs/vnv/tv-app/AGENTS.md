# TV app review guidance

## Scope

Repository-relative paths: `tv-app/**` and `docs/vnv/tv-app/**`. The Fire TV
Kotlin/Gradle app (one APK, min SDK API 25): its UI, panel, alert and Watch
flows, the API client and its unit and instrumented tests. Spike apps under
`spikes/**` belong to [device integration](../device-integration/AGENTS.md).

## Tools

- `tools/ci/gate.sh tvapp docs hygiene`: Gradle unit tests, Android lint and
  debug assemble under `tv-app/`.
- `./tv-app/gradlew -p tv-app testDebugUnitTest --tests <selector>` for one
  named test (red/green receipts).
- `./tv-app/gradlew -p tv-app connectedDebugAndroidTest` with the slice's
  test class, on the stick, for instrumented cases.
- `bash tools/ci/coverage/tvapp.sh <base_sha> <evidence_dir>` and
  `bash tools/ci/mutation/tvapp.sh <base_sha> <evidence_dir>` where declared.
- `reverify` for any claim about a built APK (signature, version, contents).

P2-G01 adds the `tvapp` area. Until it lands, `gate.sh tvapp` is a usage error
(exit 2), and a missing JDK, Android SDK or Gradle is GAP (exit 3), never PASS.
`PASS no tv-app/ tree` closes no product requirement. See the
[index](../AGENTS.md) for exit codes and evidence rules.

## Review Focus

- TDD pairs: the test slice's red receipt fails on a named behavioral
  assertion, and the same test IDs and hashes pass on the product slice. An
  import, build or tool failure is not a red receipt.
- Visual review (rule 16): every changed screen and state is driven on the
  stick by D-pad key events and captured with its window geometry. The 1080p
  output is the only viewport. Captures use sanitized fixture profiles.
- Panel and alerts: per-value source and freshness, null-with-reason for
  unknown points, legible text sizes, and no overlap with provider video.
  Protected video captures show black; geometry evidence must back layout.
- Leases: `AndroidManifest.xml` and `build.gradle.kts`/`libs.versions.toml`
  change one slice at a time under `tv-app-manifest` and `tv-app-gradle`.
- Security: no secrets, API keys or signing material in source or the APK; the
  API base URL comes from a build property. No account names in fixtures.
- Supply chain: new Gradle plugins, libraries and wrapper versions carry a
  scan receipt before first use.

## Findings target

GitHub issues in `1wgrumph/amazon-fantasy-companion`, label `vnv`, through the
issue-label policy tool under the [index](../AGENTS.md) rules. Defects found
during work route to bug triage and are fixed in the current round.
