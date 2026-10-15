# BUG-AFC-L02-404-ENVELOPE-001 execution binding

Owner-assigned Implementer packet, 2026-10-14; profile bug-triager;
Codex CLI / GPT-6.1 Sol / high. Baseline and origin/main:
`220c8193be354ba65cc7da00e5261092cd5d8095`; branch
`afc/bug-404-envelope`; checkout `amazon-fantasy-companion-bug-404`.
Initial checkout clean and matches the packet. No separate current checkout
lease was supplied or found. The explicit owner packet controls this work;
no Lifecycle state or live profile selection is invented or changed.

Next action: write and run the route-table regression red on the baseline,
add one default HttpApi event to ApiFunction, run the same test green,
confirm the router's unknown-path envelope, run the full gate and local SAM
lint validation, write the receipt, check the write set and commit with hooks.
No AWS calls, branch changes, push, PR, issue mutation or nested triage.

Allowed writes: backend/template.yaml routes; backend/src/api only if needed;
backend/tests/contract; new backend/tests/unit tests; this evidence directory;
CHANGELOG.md. Scope reaches the gateway event table, template contract,
router regression, changelog and receipt. Existing routes, IAM, throttling,
CORS, authentication and functions must be preserved.

V&V method: test, explicitly required by the packet. Real inputs are the
committed SAM template, installed YAML loader and existing Lambda router.
Pass: the same route-table test fails without a default route and passes with
one targeting the existing HttpApi/router; unknown paths return structured
404; existing unit/contract checks, full gate and SAM lint exit 0.
Resource group: offline host-pytest; no engine, server, ports or real AWS.

BRAN unavailable: no native policy; ordinary discovery used. Author checks
are diagnostic, not independent assurance. OCR/review.coverage_assist is
NOT_RUN by this worker; its frozen selection was not supplied and is not
inferred as disabled. Parent retains independent review settings and budget.
Reverify/deterministic_verification.reverify: not applicable to this template
and Python test change; no compiled-binary property claim. No route switching.
