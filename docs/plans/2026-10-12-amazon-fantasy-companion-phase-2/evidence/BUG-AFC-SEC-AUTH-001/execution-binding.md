# BUG-AFC-SEC-AUTH-001 execution binding

Owner-assigned Bug-triager Implementer packet, 2026-10-15. Baseline:
`2d973bd66182364a69b5a3088286e88c08f1107d`; branch `afc/bug-auth-hardening`.
Route: Codex CLI / GPT-6.1 Sol / high; profile `bug-triager`.
This packet supplies authority; the historical Lifecycle is not resumed and
live profile defaults are not imported. No branch changes, push, PR, AWS calls,
credential access, or production mutation. Commit with existing Codex author
environment and hooks enabled. SEC-1 is already fixed by `d5ceee9` and excluded.

Next action: reproduce SEC-2 and SEC-3 warning omissions with new tests, make
the minimal IAM/text changes, run the same tests green plus existing link
checks, full gate, local SAM lint, receipt and local commit. Method=test:
committed SAM/YAML and the real Lambda handler with the existing offline Moto
fixture. No new fake, server or shared resource. Expected focused cost <5 s.

Write scope: template IAM statements; device_auth; API link-page text; backend
tests; this evidence directory; CHANGELOG. Frozen test exception required:
`test_backend_template.py::test_template_uses_ssm_parameter_names_instead_of_embedded_secret_values`
currently mandates ApiFunction SSM access. Retarget only that grant assertion
to the retained PolicyFunction; the new SEC-2 regression forbids API access.
The first focused run also exposed the same obsolete assertion in
`test_template_iam.py::test_links_index_query_and_events_stream_are_preserved`;
invert only its API SSM assertion and retain its existing PolicyFunction SSM,
DynamoDB and stream assertions. This bounded correction is necessary for the
IAM fix.

Scope inventory: ApiFunction IAM and its direct/transitive imports; Yahoo
client; device issue/confirm/poll and store condition; rendered /link warning;
template contract, auth/router tests, changelog and evidence. No exports or
fixtures require changes. Preserve routes, throttling, ten-minute default
TTL, atomic expiry/single-confirm checks, CSP and working code-only linking.

Author checks are diagnostic and do not establish independent assurance.
Selected review route from the packet context: Claude Code / Claude Opus 5.5 /
medium; no route substitutions. OCR/review.coverage_assist is required for
any code-review session, in delegation mode, never substitutes for review.
Reverify/deterministic_verification.reverify: not applicable, no compiled
binary claim. BRAN: unavailable (no native policy); direct discovery used.
The Lifecycle's frozen capability selection was not supplied (NOT_SUPPLIED),
so no live selection is inferred as disabled or imported. Parent retains its
formal review/assurance settings and spent budgets; the focused security-skill
review and author checks do not replace those gates.
