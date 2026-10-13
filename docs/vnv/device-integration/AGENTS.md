# Device integration review guidance

## Scope

Repository-relative paths: `spikes/**`, `evidence/visual/**`, `evidence/e2e/**`,
`evidence/demo/**` and `docs/vnv/device-integration/**`. Spike apps and their
`VERDICT.md` files, on-device captures, live end-to-end run records and the
demo clip manifest. The provider registry and replay fixtures a spike writes
under `backend/` are reviewed with the [backend](../backend/AGENTS.md) area.

## Tools

- `git show <spike_merge_sha>:spikes/<sp>/VERDICT.md` for each verdict.
- `adb -s <stick_serial> install -r <apk>`, `exec-out screencap -p`,
  `shell dumpsys window` and `shell wm size`, under the `fire-tv-stick` lease.
- `tools/ci/gate.sh docs hygiene` for committed Markdown, paths and secrets.

No gate area builds spike apps; each spike records its own build and install
output. No stick, no adb or no lease is a typed gap, never PASS. See the
[index](../AGENTS.md) for exit codes and evidence rules.

## Review Focus

- Verdicts: each `VERDICT.md` states the verdict, the evidence for it and every
  limitation. A panel-beside-video verdict needs geometry and capture evidence
  of no overlap or crop; otherwise the fallback mode applies.
- Spikes are evidence-only: no spike app code ships in `tv-app/` or
  `backend/`; only the registry and fixtures named above cross over.
- Evidence: text output uses the `.txt` suffix; captures and records name the
  slice and state. Video clips stay out of git; the manifest lists name and
  sha256.
- Sanitization: no account names, serials, tokens, private paths or customer
  data in captures, logs or verdicts. Protected video shows black; owner camera
  shots stand in where listed.
- Live windows: live-game runs hold `live-game-window` only for the game window
  and record start, end and any missed observation.
- Supply chain: Android SDK tools, the starter commit and any spike dependency
  carry a scan receipt before first use.

## Findings target

GitHub issues in `1wgrumph/amazon-fantasy-companion`, label `vnv`, through the
issue-label policy tool under the [index](../AGENTS.md) rules. A spike verdict
is not a finding; defects in the product path route to bug triage.
