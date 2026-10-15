# BUG-AFC-L02-404-ENVELOPE-001 implementer receipt

Outcome: **PASS** for the assigned local implementer packet. Local candidate
only; no deployment,
independent review, formal assurance, PR or issue closure claimed.
Owner-assigned bug-triager Implementer; Codex CLI / GPT-6.1 Sol / high.
Baseline: `220c8193be354ba65cc7da00e5261092cd5d8095` (origin/main and the
P2-L02 resume-2 deployed GitCommit). Branch: `afc/bug-404-envelope`.
The candidate is the commit containing this receipt. Authority and next
action are recorded in [execution-binding.md](execution-binding.md).

## Reproduction and classification

P2-L02 resume-2's `receipt-resume-2.md`, read from branch `afc/p2-l02`,
records one profile smoke failure at this exact baseline: GET
`/v1/unknown-path` returned 404, then the error-envelope assertion raised
`KeyError: 'error'`. This worker made no live API request or AWS call.

The baseline SAM template declares eleven explicit HttpApi method/path
events and no fallback. None match that path. The new contract test reads
the real committed template through the existing SAM-aware YAML loader,
requires a default event on the existing router and checks its API binding.
It fails on the unchanged baseline with `assert 0 == 1`: no default route.
The same test ID passes after adding one event.

[API Gateway routing documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-routes.html)
confirms unmatched routes are answered by Gateway with a message object;
explicit routes take priority over `$default`. The deployed failure,
baseline route table and documented routing behavior establish the cause.
This is a product contract defect, not a harness/configuration fault or an
expected negative-test failure: status 404 is correct, its shape is wrong.
This packet addresses the assigned defect only; no duplicate search or
issue filing is claimed.

Contract association: owner bug ID `CONTRACT-AFC-P2-ENVELOPE`; concrete
error shape is also defined by `components.schemas.Error` in
`backend/src/api/openapi.yaml` and the existing structured-404 unit and
deployed tests. The design's ENVELOPE section describes entity fields;
this repair preserves both entity and error contracts.

## Origin and missed detection

Introducing product change: `9cd216ce2164c5981c389cc7e8dfdf658827b986`,
P2-B01 backend foundation (PR #60). Its template already had the same
explicit-only route table. History/blame confirms those routes survive in
the pinned deployment; later IAM and code-only-linking edits did not add a
fallback. P2-B01's receipt identifies Claude Code / Claude Opus 5.5 / medium
as Product Implementer. This is provenance, not an attribution of fault.

The faulty assumption was that correct Lambda unknown-route behavior
established the deployed API behavior. The existing unit test invokes the
router directly with DELETE `/v1/profile`; it never exercises Gateway
selection. The existing template contract accepts either catch-all routing
or the full explicit known-route set, so it permits this defect. The
deployed profile smoke is the first cited failing evidence crossing that
boundary. The prevention test closes that template coverage gap in the
existing backend gate without changing its tooling or weakening tests.

## Fix and preserved behavior

One template line adds `DefaultRoute` with type HttpApi and `ApiId: !Ref
HttpApi` to ApiFunction. [SAM's HttpApi documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-property-function-httpapi.html)
defines a default route when both Path and Method are omitted.
The existing router handles the forwarded path and continues to reject
unknown routes with 404 and `error.code=not_found`.

No router change or function added. The semantic template comparison in
[template-preservation.txt](template-preservation.txt) removes only that
event from the candidate and checks equality with origin/main: explicit
routes, IAM, throttling, CORS and all other settings are unchanged.
Unknown-path unit checks cover the smoke path with GET/POST, a nested path,
root and OPTIONS without a session. Existing unsupported-method and
protected-route tests also pass (36 focused checks total); missing/unknown
sessions and foreign-profile requests remain rejected.
Existing request-body guards are unchanged.

## Commands and evidence

Pytest, gate and SAM commands bounded by `timeout 600`. Python/gate commands use
`PATH="$HOME/.local/share/afc-tools/backend-tests/bin:$PATH"`.
Tools: Python 3.12.3, pytest 8.4.2, SAM 1.169.0, Codex CLI 0.162.1.

| Command | Exit | Result / evidence |
| --- | --- | --- |
| `python3.12 -m pytest backend/tests/contract/test_backend_template.py::test_unknown_routes_reach_the_api_router_for_the_error_envelope -v --tb=short` before fix | 1 | Expected red, 1 failed; [red.txt](red.txt) |
| Identical command after fix | 0 | Green, 1 passed; [green.txt](green.txt) |
| `python3.12 -m pytest backend/tests/unit/test_unknown_route_envelope.py backend/tests/unit/test_router.py::test_unknown_route_is_a_structured_404 backend/tests/unit/test_device_auth.py -v --tb=short` | 0 | 36 passed; [router-auth.txt](router-auth.txt) |
| Semantic YAML comparison to origin/main | 0 | Only default route differs; [template-preservation.txt](template-preservation.txt) |
| `bash tools/ci/gate.sh` | 0 | 376 backend checks, 61 CI tooling checks; spec/docs/hygiene/backend PASS; tvapp PASS (no tree); [gate.txt](gate.txt) |
| `sam validate --lint --template backend/template.yaml --region us-east-2` | 0 | Valid SAM template; [sam-validate.txt](sam-validate.txt) |

SAM validation is local; telemetry and metadata lookup disabled and shared
credential/config files bound to `/dev/null`. No credentials accessed.
The gate's git-not-a-repository messages come from passing negative tooling
tests; its terminal verdict is exit 0. Botocore deprecation warnings do not
fail the suite.

## Acceptance and prevention

| Packet objective | Status | Evidence |
| --- | --- | --- |
| 1. Reproduce template routing gap with a failing contract test | PASS | Same baseline/deployed pin; red.txt |
| 2. Minimal existing-router route; structured 404; preserve guards/IAM | PASS | One-line route diff, router-auth.txt, template-preservation.txt |
| 3. Same regression green; full gate and local SAM lint exit 0 | PASS | green.txt, gate.txt, sam-validate.txt |
| 4. Receipt includes reproduction, origin, escape, classification, prevention | PASS | This receipt and execution binding |
| 5. Unreleased Fixed changelog entry with `(PR #TBD)` | PASS | CHANGELOG.md |

Regression/prevention is permanently in `backend/tests/contract`, already
discovered by the backend gate; removing or misbinding the default route
fails the test. New checks have no engine/server/port resource. Measured
contract call: red 0.06 s, green 0.04 s; five new router cases reuse the
existing isolated fixture and add ordinary host-test work only.

Parent obligations: independent review with its frozen OCR settings,
landing/PR placeholder update, redeploy, and rerun the deployed profile
smoke. Deployed acceptance remains NOT_RUN by this worker. BRAN unavailable
(no native policy). OCR NOT_RUN by this worker, not passing evidence;
Reverify not applicable (template/Python tests, no binary property claim).

## Commit boundary

Before staging, branch and HEAD still matched the binding. The staged write
set is confined to the packet: template route, contract test, one new unit
test file, CHANGELOG.md and this evidence directory. No backend source,
tools or workflow changes. Generated untracked Python caches removed.
Commit uses Codex author/committer environment and the normal
`.githooks/pre-commit` (`gate.sh --changed`); no hook bypass or coauthor line.
Final commit SHA, hook result and `git diff --name-only origin/main HEAD`
verification are returned to the orchestrator after commit.
