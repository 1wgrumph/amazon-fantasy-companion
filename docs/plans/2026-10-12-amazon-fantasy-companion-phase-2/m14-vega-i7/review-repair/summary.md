# M14 accepted-review repair round (R-1 through R-6)

Baseline: `2a1093581c26f179bd0a7e71bb57c4ccc52c4e35`, PR #118.
This is the accepted findings' implementation round in the same reviewer
lineage. It does not constitute another independent review.

| Finding | Repair | Regression |
| --- | --- | --- |
| R-1 | Apply saved panel visibility and team/league to the live controller; clear the old snapshot and ignore a response for a replaced controller. | [MainScreen regressions](../../../../../vega-app/__tests__/panel/appPanelIntegration.test.ts): saved visibility and saved identity, including the next request's query. |
| R-2 | Permit one pending panel request, releasing the guard in `finally`; suppress callbacks after cleanup. | Same test file: two timer ticks while the real client's request is pending produce one panel request. |
| R-3 | Re-render held visible values as time passes, independently of request completion or failure. | Same test file: a failed refresh at 61 seconds renders the stale label on the held value. |
| R-4 | Supply the probe hostname through `AFC_API_HOST`; reject shell metacharacters. Redact development endpoints, private/simulator addresses and orchestration identifiers from public evidence. Blank the endpoint region in the two historical Stage 2c link PNGs. | [check-evidence.py](check-evidence.py) `hygiene`; original review reproducer. Exact originals are retained privately. Artifact/check digests are reconciled in dependent receipts. |
| R-5 | Require the reviewed Settings/RedZone screen hashes as well as the existing transition, persistence and HTTP checks. | [online-checker tests](../../../../../vega-app/vvd-checks/test_verify_link_online.py): recorded success accepted, recorded requesting/error sequence rejected, wrong relink screen rejected. [Reference](../../../../../vega-app/vvd-checks/link-online-reference.json). |
| R-6 | Incorporate the token and default-panel device repair runs into the current feature table, visual index and F-056 resolution. | [check-evidence.py](check-evidence.py) `verdict`; original review reproducer. |

All four MainScreen regressions failed at behavior assertions on the baseline
before product edits. The online checker passed the recorded-success fixture
but incorrectly accepted both negative fixtures; those two assertions failed
before its repair. Both evidence regressions and all seven original reproducer
cases exited 1 before repair. Private repair evidence records the complete
red/green outputs and SHA-256 values.

MainScreen, ApiClient, ProfileStore and PanelController run from their actual
source in the integration regressions. Native view elements, React hooks and
scheduling are controlled, and HTTP transport returns contract-shaped fixtures.
These tests do not establish native rendering or device request cadence.

Historical device runs remain authoritative for their original source:
[token persistence](../bug-token/summary.md) and
[empty default panel](../bug-panel/summary.md). Receipt `executed_*` fields
retain the hashes of source/checks actually used there; published digest tables
identify the current repaired public files. Existing runtime results and package
hashes are unchanged. Redaction does not establish a fresh device run.

Optional device confirmation was skipped. No new `.vpkg` was built or installed.
The screenshot checker deliberately requires the recorded VVD viewport, focus,
synthetic profile and converter; a rendering change needs a visually checked
reference. Populated lineup data, Watch playback, app detection and the native
data-root messages remain outside the verification established by this round.
BRAN is unavailable; repository discovery was used.

Verification result: **PASS** for this bounded repair round.

- Jest: 22 suites, 170 tests pass, including the existing 166 tests and four new MainScreen regressions.
- TypeScript: `npx tsc --noEmit --incremental false` exits 0.
- Online-checker regression: three tests pass. The negative screenshot fixture is rejected by the checker, as required.
- All seven original review reproducer cases and both evidence checks exit 0.
- Documentation links, probe shell syntax and `git diff --check` pass.
- 126 published receipt digest entries match their files. Exact originals for all 22 hygiene write-set files are retained privately; decoded PNG pixels outside the endpoint region are unchanged.
- The final changed files are confined to the authorized write set. No backend, Fire OS or dependency file changed.
