# Vega app review guidance

## Scope

Repository-relative paths: `vega-app/**` and `docs/vnv/vega-app/**`. The Vega
OS compatibility client (React Native for Vega, DES-AFC-P2-VEGA): linking,
profile/settings, alerts, Watch and the lineup panel against the unchanged
CONTRACT-AFC-P2-API. Fire OS under `tv-app/` is the primary target and belongs
to [TV app](../tv-app/AGENTS.md).

## Tools

Every npm/node/vega/VVD command runs through the Vega sandbox wrapper
(`vega-sandbox.sh <worktree> -- <command>`) on this host.

- `bash tools/ci/gate.sh vegaapp`: `npm --prefix vega-app ci` then the Jest
  suite (`npm --prefix vega-app test -- --ci`, CMD-VEGA-UNIT).
- `npm --prefix vega-app run typecheck`: `tsc --noEmit`, exit 0.
- `AFC_API_BASE_URL=<ApiUrl> npm --prefix vega-app run build:app`: the x86_64
  `.vpkg` for the Vega Virtual Device (CMD-VEGA-BUILD). No armv7 or physical
  path exists (owner decision, AC-AFC-P2-VEGA-05 NOT_APPLICABLE).
- VVD install, launch, input and capture are SEIT procedures
  (CMD-VVD-START/INSTALL/INPUT/SCREENCAP), never gate checks.

`PASS no vega-app/ tree` closes no product requirement. A missing node or npm
is GAP (exit 3) naming the tool, never PASS. See the [index](../AGENTS.md) for
exit codes and evidence rules.

## Review Focus

- TDD pair P2-V01T/P2-V01: the frozen red suite's test-file hashes
  (`evidence/P2-V01T/frozen-hashes.json`) are unchanged and the same 162 test
  IDs pass. A changed digest returns the slice to the red boundary.
- The session token lives only behind `src/auth/tokenStore.ts`, is sent only
  as the Bearer credential, and never reaches a logger, screen or capture.
- Visual review is VVD-only: every changed state driven with `inputd-cli` and
  captured under `evidence/visual/P2-V01/`. Provider apps, DRM and entitlement
  are not supported or unknown on the VVD; never PASS them from the VVD. The
  per-feature verdict table (works / limited by simulator / not supported /
  unknown) is the qualification record.
- Leases: `vega-virtual-device`, `vega-app-config`, `aws-afc-dev`.
- Security: the API base URL is build-time configuration only; the `.vpkg`
  carries no token or credential. Empty configuration shows
  "Backend not configured".
- Supply chain: the pinned SDK template files and npm dependencies carry scan
  receipts from P2-V01T preparation; new dependencies need a scan first.

## Findings target

GitHub issues in `1wgrumph/amazon-fantasy-companion`, label `vnv`, through the
issue-label policy tool under the [index](../AGENTS.md) rules. Defects found
during work route to bug triage and are fixed in the current round.
