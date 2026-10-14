# P2-B01 independent review

**REPAIR_REQUIRED — six introduced actionable findings.**

Candidate `f71f72ba975d3c5218fe0ad0f2cbe9932bc5a537`; base `884df103e1ee7f8b53c674864db349cd00875283`. Review unit IE-P2-5, issue #20, lease P2-B01-review. Route: Codex CLI / GPT-6 Astra / high, fresh independent session on the owner-approved fallback. One review; no repair performed.

The candidate remained unchanged. All requested local checks passed in the provisioned test environment: 141 backend tests, 82 tools tests, SAM validation, actionlint, 100% changed-line coverage, and 99.49% native mutation score. Those passes do not negate the reproductions below.

## Findings

### B01-R01 — P1: Provision native tools in the hygiene CI job

**test-only / CI · `tools/ci/tests/test_bug2_mutenv.py:108` · introduced by `f71f72b`.

The new top-level unittest-discovered mutation and coverage regressions require mutmut and diff-cover, but the hygiene Actions job installs only graphviz, python3-yaml and python3-pytest. The new requirements install is in the separate backend job and cannot provision hygiene.

**Reproducer / observed result:** A clean hygiene runner discovers these new tests and fails before exercising their behavior. With PATH=/usr/bin:/bin and the already installed Python test runner, the candidate produces 3 failed / 1 passed: missing mutmut, missing diff-cover, and the expected semantic coverage GAP replaced by missing-tool GAP.

**Evidence:** ci-hygiene-repro.log; .github/workflows/ci.yml:107; .github/workflows/ci.yml:121; tools/ci/tests/test_bug3_covempty.py:58.

**Repair:** Provision the required native-tool closure, pinned and hash-verified, in the job that executes these tests; preserve the native positive and negative cases rather than skipping them. Keep the quick hygiene gate's added cost explicit.

**Repair write set:** `.github/workflows/ci.yml`, `tools/ci/tests/test_bug2_mutenv.py`, `tools/ci/tests/test_bug3_covempty.py`, `a checked-in hash-pinned CI tool requirements file`.

**Origin and escape:** The repair's clean environment simulation exercised gate backend, while full hygiene was run only on an already provisioned host.

**Contract / SEIT:** P2-B01 / CMD-GATE-HYGIENE, DES-AFC-P2-GATE, AC-AFC-P2-LAND-01.

**Deterministic closure:** In a fresh isolated environment with only declared CI dependencies, hygiene and the native mutation/coverage regression tests pass; missing-tool negative checks still fail closed.

### B01-R02 — P2: Make linked-token delivery recoverable on poll retry

**product · `backend/src/device_auth/__init__.py:47` · introduced by `9cd216c`.

The first GET poll irrevocably completes the link and returns the only copy of the bearer token. Every later poll returns linked without a token. The completion write also precedes session persistence.

**Reproducer / observed result:** Confirm a device, let the first GET /v1/link execute but discard its response (ordinary connection loss), then repeat the same GET. It returns HTTP 200 {state: linked} with no token, while a TV that never received the token still gets 401 from GET /v1/profile. The user must start a new link flow despite the server reporting success.

**Evidence:** behavior-repro.log; backend/src/store/__init__.py:85; backend/tests/unit/test_device_auth_units.py:48; backend/src/api/openapi.yaml:31.

**Repair:** Make completion and token delivery retryable while preserving one-time customer confirmation and hash-only credential storage. Ensure persistence cannot leave a completed link without a usable session; revise the test and OpenAPI wording that codify one-shot delivery.

**Repair write set:** `backend/src/device_auth/__init__.py`, `backend/src/store/__init__.py`, `backend/src/api/openapi.yaml`, `backend/tests/unit/test_device_auth_units.py`, `backend/tests/unit/test_device_auth.py`.

**Origin and escape:** Tests retain the first response and explicitly assert that later polls omit the token; no dropped-response/retry scenario is exercised.

**Contract / SEIT:** SEIT-AFC-PR-038, SEIT-AFC-PR-058, DES-AFC-P2-AUTH, CONTRACT-AFC-P2-API.

**Deterministic closure:** Discard a successful linked poll response and retry; the same authorized device can still obtain a usable session, with no raw secret persisted and no confirm replay or foreign-profile access.

### B01-R03 — P2: Enforce the response-size contract before saving a profile

**product · `backend/src/api/handler.py:183` · introduced by `9cd216c`.

Only request size is checked. The profile envelope adds bytes after a maximum-size accepted request, and _respond serializes without any response bound.

**Reproducer / observed result:** PUT /v1/profile with revision 0 and fantasySelections='x'*65490 serialized with compact separators is exactly 65,536 bytes. It returns 200 with a 65,632-byte body, persists revision 1, and GET returns the same oversized body. This violates CONTRACT-AFC-P2-API's request and response limit.

**Evidence:** behavior-repro.log; backend/src/api/handler.py:115; backend/tests/conftest.py:180; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/design.md:416.

**Repair:** Validate the serialized profile envelope's byte length before mutation, and enforce the response cap consistently. Reject an update that cannot be returned within the contract without persisting it. Cover escaping/UTF-8 expansion as well as ASCII.

**Repair write set:** `backend/src/api/handler.py`, `backend/tests/unit/test_router.py`.

**Origin and escape:** The added exact-limit test uses POST /v1/link, whose response is small, rather than a profile that echoes user data inside a larger envelope.

**Contract / SEIT:** SEIT-AFC-PR-057, SEIT-AFC-PR-058, CONTRACT-AFC-P2-API, CONTRACT-AFC-P2-ENVELOPE.

**Deterministic closure:** Boundary-sized updates either return a <=65,536-byte envelope or return a structured 400 with the prior profile unchanged; subsequent GET responses stay within the limit.

### B01-R04 — P2: Validate profile selector types before set construction

**product · `backend/src/api/handler.py:57` · introduced by `9cd216c`.

An authenticated request's body.profileId is inserted into a Python set before validation. JSON arrays and objects are unhashable and fall into the generic service-unavailable handler.

**Reproducer / observed result:** An authenticated PUT /v1/profile with {profileId: [], revision: 1, data: {}} (or profileId: {}) returns 503 unavailable instead of the required 400 malformed input. The service logs TypeError and a client may retry a permanently invalid request.

**Evidence:** behavior-repro.log; backend/src/api/handler.py:39.

**Repair:** Validate explicitly supplied profile selectors against the ProfileId string contract before comparing them, and compare values without requiring caller-controlled values to be hashable.

**Repair write set:** `backend/src/api/handler.py`, `backend/tests/unit/test_router.py`.

**Origin and escape:** Foreign-profile tests only pass strings; malformed JSON tests validate the top-level object but not selector types.

**Contract / SEIT:** SEIT-AFC-PR-058, CONTRACT-AFC-P2-API.

**Deterministic closure:** Array/object/null/non-string selectors return structured 400 without mutation; a valid foreign string remains 403 and a valid own-profile request still succeeds.

### B01-R05 — P2: Restrict DynamoDB grants to each function's operations

**product / security configuration · `backend/template.yaml:76` · introduced by `9cd216c`.

DynamoDBCrudPolicy gives ApiFunction write/delete/batch-write access to Alerts although its alerts route only reads. Every CRUD grant also includes deletion even though the shared store exposes only get, put, update and query and no current or declared delete operation.

**Reproducer / observed result:** The generated execution role authorizes ApiFunction to forge or delete any profile's alert records, and gives other CRUD roles unnecessary delete capability. If code or a dependency in a function is compromised, IAM does not contain it to its assigned data operations. Offline inspection of SAM 1.169.0's actual policy template proves these Allow actions; this is not a claim of a demonstrated remote code-execution exploit.

**Evidence:** iam-policy-proof.json; iam-repro.log; backend/template.yaml:74; backend/template.yaml:107; backend/template.yaml:119; docs/vnv/backend/AGENTS.md:39.

**Repair:** Replace broad CRUD templates with explicit per-function action/resource statements derived from the table-operation inventory. Give the API only read access to Alerts, remove unneeded DeleteItem/BatchWriteItem grants, and preserve the required Links index and stream permissions.

**Repair write set:** `backend/template.yaml`, `backend/tests/contract/test_backend_template.py`.

**Origin and escape:** Template tests validate service types, routes and SSM presence, but never inspect expanded DynamoDB actions by function.

**Contract / SEIT:** DES-AFC-P2-BACKEND, SEIT-AFC-PR-055, backend VnV guidance / least-privilege IAM.

**Deterministic closure:** Offline expanded-role inspection proves required operations remain allowed and unrelated writes/deletes are absent; SAM lint and backend tests remain green.

### B01-R06 — P2: Deliver the deployed auth/API test allocation owned by B01T

**test-only / plan conformance · `backend/tests/conftest.py:1` · introduced by `c0fdaaa (omitted slice deliverables)`.

Only the offline Moto fixture and unit/contract suites were delivered. The shared deployed fixture and device_auth/api test directories explicitly assigned to P2-B01T are absent, without an owner scope amendment deferring their authorship.

**Reproducer / observed result:** The next deployed verification command cannot collect B01's auth/API cases: python3.12 -m pytest --collect-only -q -p no:cacheprovider backend/tests/deployed exits 4 with 'file or directory not found' and no tests. Deferring actual deployed execution to L02/L03 does not deliver the test artifacts those slices must execute.

**Evidence:** deployed-collection.log; inventory.json; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/design.md:390; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/seit.json:planned_evidence_ownership; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/implementation.json:P2-B01T.write_set.

**Repair:** Author the allocated deployed conftest and auth/API cases against the declared contracts, keep them separate from the offline gate, and record execution as NOT_RUN until the authorized dev-stack lease and owner actions are available. Do not replace deployed evidence with Moto results.

**Repair write set:** `backend/tests/deployed/conftest.py`, `backend/tests/deployed/device_auth/`, `backend/tests/deployed/api/`, `B01T/B01 evidence inventory`, `backend/tests/conftest.py (only if needed to scope offline fixtures)`.

**Origin and escape:** The red inventory froze 65 offline assertions but did not reconcile the explicit deployed-path allocation in the approved planning package.

**Contract / SEIT:** SEIT-AFC-PR-038, SEIT-AFC-PR-055, SEIT-AFC-PR-058, TE-P2-F01, seit.planned_evidence_ownership.

**Deterministic closure:** Offline collection finds the named deployed cases without contacting AWS; actual execution remains a separately recorded L02/L03 obligation, with absent prerequisites a typed gap rather than PASS.

## Required lead classifications

**(a) Device/user-code brute force — not a defect.** backend/template.yaml:64-66 configures DefaultRouteSettings at rate 5 and burst 10, and the frozen template test checks both are nonzero. device_auth.issue selects eight characters independently from 32 symbols (40 bits), expires the pending code after 600 s, and creates a separate 256-bit polling handle. confirm validates the SSM passphrase before it can bind a code. Guessing a displayed code alone cannot retrieve the bearer session. API Gateway limits are best-effort targets, not a strict per-code attempt counter; real deployed enforcement is still unverified.

**Evidence:** backend/template.yaml:64; backend/src/device_auth/__init__.py:29; backend/src/device_auth/__init__.py:54; backend/tests/contract/test_backend_template.py:53; behavior-repro.log.

Primary reference: [official source](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-throttling.html).

**(b) Remote device-code phishing — not a defect.** This manual, single-owner design necessarily grants access to the client whose code the authenticated owner confirms. /link says 'Link your TV', explicitly tells the user to enter the code shown on their TV, leaves the code empty, and requires a deliberate submit plus the SSM passphrase; it does not prefill or auto-confirm a query-supplied code. A victim deliberately entering an attacker's code can still authorize that client, an inherent social-engineering risk of device flows rather than a demonstrated bypass of this contract. The current possession instruction is meaningful mitigation. Stronger warnings/device context could harden it, but are not treated as a missing normative requirement or fixable product defect in B01.

**Evidence:** backend/src/api/link.html:16; backend/src/api/link.html:20; backend/src/api/link.html:25; backend/src/device_auth/__init__.py:54; link-page.html.

Primary reference: [official source](https://www.rfc-editor.org/rfc/rfc8628.html#section-5.4).

**(c) DynamoDB least privilege — confirmed defect.** The table resources are scoped, but actions are broader than each function needs. SAM's installed policy template expands DynamoDBCrudPolicy to Allow DeleteItem and BatchWriteItem, including ApiFunction on Alerts. No API operation writes/deletes generated alerts and no store accessor deletes any item.

**Evidence:** backend/template.yaml:76; iam-policy-proof.json; iam-repro.log.

Primary reference: [official source](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-template-list.html#dynamodbcrudpolicy).

**(d) Pipeline no-mutate pragma — not a defect.** The exclusion is explicit and narrowly justified by the frozen AST contract in test_backend_template.py:107-122, which requires direct calls in the handler body that mutmut replaces with a trampoline. The added behavioral test executes INSERT/MODIFY/REMOVE and empty batches, verifies call order/arguments and verifies routed alerts in Moto DynamoDB. The four future-module substitutes are explicit monkeypatches and do not pretend to be deployed module evidence. Thus this is not hidden untested wiring. Its limitation remains real: the native mutation inventory measures _game_events but contains zero lambda_handler mutants, so the reported score must not be described as native mutation coverage of the pipeline orchestration. Revisit this exemption when the stubs are realized.

**Evidence:** backend/src/pipeline/handler.py:17; backend/tests/contract/test_backend_template.py:107; backend/tests/unit/test_pipeline_and_stubs.py:17; coverage-result.json; rerun-mutation-result.json.

**(e) Inline-script Content-Security-Policy — not a defect.** unsafe-inline is replaceable with a hash/nonce or a separate same-origin script; it is not intrinsically necessary. However the handler returns a constant local HTML file, never interpolates request/secret content, the script writes responses with textContent, code is manually entered, and framing is denied. No reachable HTML/script injection was found. The current policy is a defense-in-depth weakness, not an evidenced XSS defect; a script hash would be a small optional hardening change.

**Evidence:** backend/src/api/handler.py:154; backend/src/api/link.html:29; backend/src/api/link.html:41; link-page.html.

**(f) Disabled ingest schedule default — not a defect.** The complete minute schedule exists and its State references an ENABLED/DISABLED parameter. B01 deliberately ships an unimplemented ingest stub, while live activation is separately controlled. Starting with DISABLED avoids invoking that stub continuously and is consistent with only running for relevant live games after B02/activation. It is not evidence that game-window activation is implemented or accepted.

**Evidence:** backend/template.yaml:33; backend/template.yaml:158; backend/src/feed_ingest/__init__.py:11; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/receipt.json.

**(g) Mutation retries and loaded-host timeouts — not a defect.** The final adapter changes the documented timeout_constant/timeout_multiplier from defaults to 5/30. Earlier exit-3 runs were not accepted as passes; timeouts remain UNRESOLVED. An independent final-config run on the exact candidate exited 0 in 641.745 seconds, scoring 1376 killed / 1383 with 7 survivors and zero timeouts or unresolved states; observed host load immediately afterward was about 19.5/24.4/20.5 (1/5/15 min), not a controlled stress qualification. This supports a repaired timeout calibration, not a confirmed continuing flaky gate. The first two raw logs are absent from the committed evidence, so their disjoint-timeout explanation remains author-reported, and this is one verification run rather than a statistical reliability claim.

**Evidence:** tools/ci/mutation/backend.sh:47; tools/ci/mutation/evaluate.py:178; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/receipt.json; mutation-command.json.

## Commands and exits

Unless stated otherwise, gate/pytest/coverage used the packet's backend-tests PATH. Bytecode/cache writes were disabled. Credential files were redirected to /dev/null; the required validation runner disabled metadata and SAM telemetry and removed credential/profile environment variables. Temporary directories were owned and removed.

| Command | Exit | Wall time | Evidence |
|---|---:|---:|---|
| `bash tools/ci/gate.sh` | 0 | 93.098 s | [gate.log](gate.log) |
| `python3.12 -m pytest -q -p no:cacheprovider tools` | 0 | 111.402 s | [tools-pytest.log](tools-pytest.log) |
| `sam validate --lint -t backend/template.yaml` | 0 | 3.721 s | [sam-validate.log](sam-validate.log) |
| `actionlint` | 0 | 0.016 s | [actionlint.log](actionlint.log) |
| `bash tools/ci/coverage/backend.sh 884df10 <owned tmpdir>/coverage` | 0 | 58.346 s | [coverage.log](coverage.log) |
| `PATH=$HOME/.local/share/afc-tools/mutmut-backend/bin:$PATH bash tools/ci/mutation/backend.sh 884df10 <owned tmpdir>/out` | 0 | 641.745 s | [mutation-wrapper.log](mutation-wrapper.log) |
| `ocr delegate preview --from 884df103e1ee7f8b53c674864db349cd00875283 --to f71f72ba975d3c5218fe0ad0f2cbe9932bc5a537` | 0 | — s | [ocr-preview.log](ocr-preview.log) |
| `ocr delegate rule <each of all 92 changed paths>` | 0 | — s | [ocr-index.json](ocr-index.json) |
| `PATH=/usr/bin:/bin $HOME/.local/share/afc-tools/backend-tests/bin/python3.12 -m pytest -q -p no:cacheprovider tools/ci/tests/test_bug2_mutenv.py tools/ci/tests/test_bug3_covempty.py` | 1 | — s | [ci-hygiene-repro.log](ci-hygiene-repro.log) |
| `python3.12 -m pytest --collect-only -q -p no:cacheprovider backend/tests/deployed` | 4 | — s | [deployed-collection.log](deployed-collection.log) |
| `In-process HTTP API v2 handler demonstration via committed offline Moto fixture; GET /link written to link-page.html; lost poll response, 65536-byte profile PUT and malformed profile selectors` | 0 | — s | [behavior-repro.log](behavior-repro.log) |
| `Offline inspection of installed SAM 1.169.0 DynamoDBCrudPolicy and candidate store/router operations` | 0 | — s | [iam-repro.log](iam-repro.log) |
| `Read-only source/hash/JSON/frozen-red inventory inspection` | 0 | — s | [inventory.json](inventory.json) |

Coverage: **281 changed executable lines, 100%**, with only the docstring-only API package recorded as nothing to cover. Mutation: **1,376 killed / 1,383 scored**, seven survivors, zero timeouts/unresolved, **641.745 s**. The old timeout-run rationale is author-reported; the final-config rerun is independent.

## Test quality and evidence limits

The frozen four B01T files and three G01T files retain their recorded hashes. The red XML has 65 tests, 65 AssertionError failures, zero errors and zero skips. Moto/SSM instrumentation and monkeypatches are explicit; no hidden real AWS dependency was found. The pipeline test proves wiring and Moto alert persistence while substituting the not-yet-implemented module contracts. Fixture assert-True stubs are only setup controls in disposable gate repositories, not product behavior evidence.

All seven native survivor diffs were inspected in the owned mutation workspace before cleanup; see [survivor-diffs.log](survivor-diffs.log).

- `api.handler.x__bearer__mutmut_10`: **equivalent API behavior for reachable requests**. Absent header defaults to XXXX instead of empty; neither is bearer, so the returned token is still empty.

- `api.handler.x__bearer__mutmut_18`: **equivalent authorization result, extra DynamoDB lookup**. A non-bearer scheme returns XXXX instead of empty; sessions are created from 256-bit random tokens, so this cannot authenticate a legitimately issued session. It does add a pointless lookup and is not byte-for-byte behavior equivalence.

- `device_auth.x_issue__mutmut_18`, `device_auth.x_poll__mutmut_38`: **equivalent in this pinned Python 3.12 runtime**. secrets.token_urlsafe(None) uses DEFAULT_ENTROPY=32 bytes in the installed standard library. The production code correctly requests 32 explicitly.

- `store.x_complete_link__mutmut_22`: **keyword-case equivalent**. Changes DynamoDB update-expression SET to set; the observed update semantics remain unchanged.

- `store.x_get_session__mutmut_14`, `store.x_get_session__mutmut_5`: **non-equivalent in real DynamoDB; emulator coverage limitation**. False or omitted ConsistentRead permits eventual reads, unlike the candidate's required strongly consistent immediate session lookup. Moto does not model that propagation delay. These survivors are not proof of production equivalence; they remain in the scored denominator, so the 99.49% threshold arithmetic is conservative.

The source correctly keeps ConsistentRead=True; the two consistency survivors are not a defect in the current implementation. They are not production-equivalent mutants, despite the author receipt's broad “equivalent here” wording. They were retained in the score denominator, so they do not inflate the reported score.

Runtime/dev requirements contain six/42 exact pins with six/824 SHA-256 entries. Existing supply receipts were inspected, not rerun as new admissions. No absolute user-home path was found in changed backend, tools or workflow files. Private plan evidence remains private; no export was performed.

- **VISUAL_REVIEW_NOT_RUN:** Only the requested handler-rendered link-page.html was produced. Browser desktop/phone flow and screenshots remain with the orchestrator as specified in the packet; HTML generation is not visual acceptance.
- **DEPLOYED_VERIFICATION_NOT_RUN:** No credentials, AWS account calls, device calls, installs or GitHub actions were performed. Real API Gateway throttling/429 payloads, IAM enforcement, DynamoDB consistency/TTL and deployment behavior are not closed by Moto or SAM lint.
- **MUTATION_SCOPE_LIMIT:** The pipeline lambda_handler is deliberately excluded from native mutation for the frozen AST contract; its behavioral wiring and real Moto persistence are tested. The 99.49% score covers generated mutants, not every behavior or runtime boundary.
- **HISTORICAL_EVIDENCE_LIMIT:** Author receipts describe the first two timeout runs, but their complete native raw logs are not committed. This review independently reran the final timeout configuration once, successfully.
- **SUPPLY_REVIEW_LIMIT:** Existing supply-scan receipts and hash-pin structures were inspected; no new acquisition, install, full advisory refresh, compiled-extension analysis or fresh artifact download was performed.
- **BRAN_UNAVAILABLE:** No native .bran/policy.yaml; ordinary bounded repository discovery used.

**Reverify: not applicable — Python Lambda source, tests, SAM and CI configuration; no compiled-binary claim.** The frozen selected capability is retained, not silently disabled. BRAN is unavailable because no native policy exists.

## OCR per-file coverage

OCR assists this independent review; it is not the verdict. Preview exited 0 (51 reviewable / 92 changed). Rule lookup was deliberately run on **all 92 paths**, including preview exclusions; every call exited 0. The complete rule text is retained in the linked per-file logs. Python rules covered error/boundary handling, trust boundaries and shared state; default rules covered correctness/security/resources/tests; YAML/JSON rules were applied alongside the independent domain review, and workflow rules covered permissions, pins, injection and job dependencies. Generated evidence/hash files were inspected in groups.

| File | Rule log | Applied result |
|---|---|---|
| `.github/workflows/ci.yml` | [ocr-rule-000.log](ocr-rule-000.log) | Workflow security/pins unchanged; new backend dependency install is hash-verified. Hygiene dependency omission: B01-R01. |
| `backend/.gitignore` | [ocr-rule-001.log](ocr-rule-001.log) | SAM/bytecode/pytest build artifacts ignored; no sensitive path or credential. |
| `backend/pyproject.toml` | [ocr-rule-002.log](ocr-rule-002.log) | Offline unit/contract selection and src import path are explicit; deployed allocation is absent (B01-R06). |
| `backend/requirements-dev.txt` | [ocr-rule-003.log](ocr-rule-003.log) | 42 exact pins, 824 SHA-256 entries; compared with dependency/supply receipts. No new download or install. |
| `backend/requirements.txt` | [ocr-rule-004.log](ocr-rule-004.log) | Six exact runtime pins and wheel hashes; AWS SDK comes from Lambda runtime as explicitly documented. |
| `backend/samconfig.toml` | [ocr-rule-005.log](ocr-rule-005.log) | afc-dev stack and deploy-only profile; validate remains credential-free; no embedded secrets. |
| `backend/src/alert_policy/__init__.py` | [ocr-rule-006.log](ocr-rule-006.log) | Explicit AFC-STUB/final-signature module (or docstring-only package); no future feature completion claimed. Stub behavior tested; no secrets or absolute home paths. |
| `backend/src/api/__init__.py` | [ocr-rule-007.log](ocr-rule-007.log) | Explicit AFC-STUB/final-signature module (or docstring-only package); no future feature completion claimed. Stub behavior tested; no secrets or absolute home paths. |
| `backend/src/api/handler.py` | [ocr-rule-008.log](ocr-rule-008.log) | Router/auth/envelope/validation reviewed with callers. B01-R03 (response cap), B01-R04 (selector type); R02 affects polling contract. CSP lead (e) assessed. |
| `backend/src/api/link.html` | [ocr-rule-009.log](ocr-rule-009.log) | Static manual code/passphrase form, textContent rendering, no query auto-confirm; leads (b)/(e). Rendered output saved. |
| `backend/src/api/openapi.yaml` | [ocr-rule-010.log](ocr-rule-010.log) | Route/security/error/entity shape reviewed against design. One-shot poll wording contributes to B01-R02; response bound relates to B01-R03. |
| `backend/src/device_auth/__init__.py` | [ocr-rule-011.log](ocr-rule-011.log) | 40-bit code/256-bit handle/session, SSM compare, expiry/confirm replay and bearer binding inspected. B01-R02; leads (a)/(b). |
| `backend/src/feed_ingest/__init__.py` | [ocr-rule-012.log](ocr-rule-012.log) | Explicit AFC-STUB/final-signature module (or docstring-only package); no future feature completion claimed. Stub behavior tested; no secrets or absolute home paths. |
| `backend/src/lineup/__init__.py` | [ocr-rule-013.log](ocr-rule-013.log) | Explicit AFC-STUB/final-signature module (or docstring-only package); no future feature completion claimed. Stub behavior tested; no secrets or absolute home paths. |
| `backend/src/matcher/__init__.py` | [ocr-rule-014.log](ocr-rule-014.log) | Explicit AFC-STUB/final-signature module (or docstring-only package); no future feature completion claimed. Stub behavior tested; no secrets or absolute home paths. |
| `backend/src/panel/__init__.py` | [ocr-rule-015.log](ocr-rule-015.log) | Explicit AFC-STUB/final-signature module (or docstring-only package); no future feature completion claimed. Stub behavior tested; no secrets or absolute home paths. |
| `backend/src/pipeline/handler.py` | [ocr-rule-016.log](ocr-rule-016.log) | Explicit ordered chain, real Moto alert persistence test, documented no-mutate exception. Lead (d); no claim of native orchestration mutation coverage. |
| `backend/src/provider_resolver/__init__.py` | [ocr-rule-017.log](ocr-rule-017.log) | Explicit AFC-STUB/final-signature module (or docstring-only package); no future feature completion claimed. Stub behavior tested; no secrets or absolute home paths. |
| `backend/src/provider_resolver/registry.json` | [ocr-rule-018.log](ocr-rule-018.log) | Empty contract-shaped registry; no invented provider URI. |
| `backend/src/requirements.txt` | [ocr-rule-019.log](ocr-rule-019.log) | Relative include points SAM at pinned parent runtime requirements; no absolute-home dependency. |
| `backend/src/store/__init__.py` | [ocr-rule-020.log](ocr-rule-020.log) | Conditional profile/link writes, hashes, consistent session read, table key operations and field whitelists reviewed. Non-atomic completion contributes to B01-R02; IAM operation inventory supports R05. |
| `backend/template.yaml` | [ocr-rule-021.log](ocr-rule-021.log) | Routes, tables/index/TTL, env names, stream, schedule and policy templates inspected; SAM lint passes. B01-R05; leads (a)/(c)/(f). |
| `backend/tests/conftest.py` | [ocr-rule-022.log](ocr-rule-022.log) | Explicit in-process Moto with real botocore protocol, fresh synthetic state, network/credential-file guards; deployed fixture allocation omitted (B01-R06). |
| `backend/tests/contract/test_api_contract.py` | [ocr-rule-023.log](ocr-rule-023.log) | Frozen hash unchanged; meaningful positive/negative API and envelope assertions. No deployed/rate-limit enforcement claim. |
| `backend/tests/contract/test_backend_template.py` | [ocr-rule-024.log](ocr-rule-024.log) | Frozen hash unchanged; service, route, throttle and structural chain assertions. IAM verb coverage missing (R05); AST constraint explains lead (d). |
| `backend/tests/unit/test_device_auth.py` | [ocr-rule-025.log](ocr-rule-025.log) | Frozen hash unchanged; 65-case red inventory includes auth/expiry/replay/foreign-profile behavior; no dropped-response coverage (R02). |
| `backend/tests/unit/test_device_auth_units.py` | [ocr-rule-026.log](ocr-rule-026.log) | Additional edge cases; explicit substitutes for collisions/clock. First-poll-only assertion codifies R02. |
| `backend/tests/unit/test_pipeline_and_stubs.py` | [ocr-rule-027.log](ocr-rule-027.log) | Explicit future-module monkeypatches, ordered call/argument assertions and Moto persistence; honest wiring-only evidence, not implemented future-module proof. |
| `backend/tests/unit/test_router.py` | [ocr-rule-028.log](ocr-rule-028.log) | Behavioral validation/revision/stub routing checks; lacks response-size and malformed-selector boundaries (R03/R04). Explicit substitutes are visible. |
| `backend/tests/unit/test_store.py` | [ocr-rule-029.log](ocr-rule-029.log) | Moto-backed conditional/table operation assertions; no IAM/real consistency equivalence claim. Two consistency survivors remain genuine emulator limits. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/CMD-COVERAGE-BACKEND.txt` | [ocr-rule-030.log](ocr-rule-030.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/CMD-MUTATION-BACKEND.txt` | [ocr-rule-031.log](ocr-rule-031.log) | Historical native diagnostic/receipt distinguished from final exact-candidate rerun; timeout failures not promoted to PASS; survivor/scope limits stated. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/backend-tests-freeze.txt` | [ocr-rule-032.log](ocr-rule-032.log) | Generated dependency evidence grouped: key/pin/hash structure and declared provenance inspected; no fresh acquisition/scan claim. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/closure.txt` | [ocr-rule-033.log](ocr-rule-033.log) | Generated dependency evidence grouped: key/pin/hash structure and declared provenance inspected; no fresh acquisition/scan claim. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/coverage-result.json` | [ocr-rule-034.log](ocr-rule-034.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/hashes.json` | [ocr-rule-035.log](ocr-rule-035.log) | Generated dependency evidence grouped: key/pin/hash structure and declared provenance inspected; no fresh acquisition/scan claim. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/mutation-result.json` | [ocr-rule-036.log](ocr-rule-036.log) | Historical native diagnostic/receipt distinguished from final exact-candidate rerun; timeout failures not promoted to PASS; survivor/scope limits stated. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/mutmut-backend-freeze.txt` | [ocr-rule-037.log](ocr-rule-037.log) | Generated dependency evidence grouped: key/pin/hash structure and declared provenance inspected; no fresh acquisition/scan claim. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/mutmut-backend-hashes.json` | [ocr-rule-038.log](ocr-rule-038.log) | Generated dependency evidence grouped: key/pin/hash structure and declared provenance inspected; no fresh acquisition/scan claim. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/mutmut-backend-requirements.txt` | [ocr-rule-039.log](ocr-rule-039.log) | Generated dependency evidence grouped: key/pin/hash structure and declared provenance inspected; no fresh acquisition/scan claim. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/mutmut-cicd-stats.json` | [ocr-rule-040.log](ocr-rule-040.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/pip-audit-backend.json` | [ocr-rule-041.log](ocr-rule-041.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/pip-audit-mutmut-only.json` | [ocr-rule-042.log](ocr-rule-042.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/receipt.json` | [ocr-rule-043.log](ocr-rule-043.log) | Bounded evidence/receipt inspected against frozen hashes, 65 all-assertion red cases and actual final commands; acceptance/deferred authorship distinction yields R06. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/BUG-AFC-B01-TOOL-001/supply-scan.json` | [ocr-rule-044.log](ocr-rule-044.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/CMD-COVERAGE-BACKEND-base-884df10.txt` | [ocr-rule-045.log](ocr-rule-045.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/CMD-COVERAGE-BACKEND.txt` | [ocr-rule-046.log](ocr-rule-046.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/CMD-GATE-ALL.txt` | [ocr-rule-047.log](ocr-rule-047.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/CMD-GATE-BACKEND.txt` | [ocr-rule-048.log](ocr-rule-048.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/CMD-GATE-HYGIENE.txt` | [ocr-rule-049.log](ocr-rule-049.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/CMD-MUTATION-BACKEND-shim.txt` | [ocr-rule-050.log](ocr-rule-050.log) | Historical native diagnostic/receipt distinguished from final exact-candidate rerun; timeout failures not promoted to PASS; survivor/scope limits stated. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/CMD-MUTATION-BACKEND.txt` | [ocr-rule-051.log](ocr-rule-051.log) | Historical native diagnostic/receipt distinguished from final exact-candidate rerun; timeout failures not promoted to PASS; survivor/scope limits stated. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/CMD-SAM-VALIDATE.txt` | [ocr-rule-052.log](ocr-rule-052.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/PROC-GATE-TOOL-QUALIFY.txt` | [ocr-rule-053.log](ocr-rule-053.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/cfn-lint.txt` | [ocr-rule-054.log](ocr-rule-054.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/coverage-result-base-884df10.json` | [ocr-rule-055.log](ocr-rule-055.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/coverage-result.json` | [ocr-rule-056.log](ocr-rule-056.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/frozen-tests.json` | [ocr-rule-057.log](ocr-rule-057.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/mutation-diagnostic-cicd-stats.json` | [ocr-rule-058.log](ocr-rule-058.log) | Historical native diagnostic/receipt distinguished from final exact-candidate rerun; timeout failures not promoted to PASS; survivor/scope limits stated. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/mutation-diagnostic-result.json` | [ocr-rule-059.log](ocr-rule-059.log) | Historical native diagnostic/receipt distinguished from final exact-candidate rerun; timeout failures not promoted to PASS; survivor/scope limits stated. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/mutation-result.json` | [ocr-rule-060.log](ocr-rule-060.log) | Historical native diagnostic/receipt distinguished from final exact-candidate rerun; timeout failures not promoted to PASS; survivor/scope limits stated. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/mutmut-shim.sh` | [ocr-rule-061.log](ocr-rule-061.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/receipt.json` | [ocr-rule-062.log](ocr-rule-062.log) | Bounded evidence/receipt inspected against frozen hashes, 65 all-assertion red cases and actual final commands; acceptance/deferred authorship distinction yields R06. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/supply-scan.json` | [ocr-rule-063.log](ocr-rule-063.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/tools-pytest.txt` | [ocr-rule-064.log](ocr-rule-064.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/CMD-GATE-HYGIENE.txt` | [ocr-rule-065.log](ocr-rule-065.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/CMD-RED.txt` | [ocr-rule-066.log](ocr-rule-066.log) | Bounded evidence/receipt inspected against frozen hashes, 65 all-assertion red cases and actual final commands; acceptance/deferred authorship distinction yields R06. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/CMD-RED.xml` | [ocr-rule-067.log](ocr-rule-067.log) | Bounded evidence/receipt inspected against frozen hashes, 65 all-assertion red cases and actual final commands; acceptance/deferred authorship distinction yields R06. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/afc-red-receipt/SKILL.md` | [ocr-rule-068.log](ocr-rule-068.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/afc-red-receipt/agents/openai.yaml` | [ocr-rule-069.log](ocr-rule-069.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/afc-red-receipt/scripts/verify_receipt.py` | [ocr-rule-070.log](ocr-rule-070.log) | Bounded evidence/receipt inspected against frozen hashes, 65 all-assertion red cases and actual final commands; acceptance/deferred authorship distinction yields R06. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/collect.txt` | [ocr-rule-071.log](ocr-rule-071.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/commands.json` | [ocr-rule-072.log](ocr-rule-072.log) | Bounded evidence/receipt inspected against frozen hashes, 65 all-assertion red cases and actual final commands; acceptance/deferred authorship distinction yields R06. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/dependency-audit.json` | [ocr-rule-073.log](ocr-rule-073.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/dependency-protocol-proof.json` | [ocr-rule-074.log](ocr-rule-074.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/harness-selfcheck.txt` | [ocr-rule-075.log](ocr-rule-075.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/path-check.txt` | [ocr-rule-076.log](ocr-rule-076.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/qualify-coverage.txt` | [ocr-rule-077.log](ocr-rule-077.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/qualify-mutation.txt` | [ocr-rule-078.log](ocr-rule-078.log) | Historical native diagnostic/receipt distinguished from final exact-candidate rerun; timeout failures not promoted to PASS; survivor/scope limits stated. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/receipt.json` | [ocr-rule-079.log](ocr-rule-079.log) | Bounded evidence/receipt inspected against frozen hashes, 65 all-assertion red cases and actual final commands; acceptance/deferred authorship distinction yields R06. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/record_receipt.py` | [ocr-rule-080.log](ocr-rule-080.log) | Bounded evidence/receipt inspected against frozen hashes, 65 all-assertion red cases and actual final commands; acceptance/deferred authorship distinction yields R06. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/repo-suite-staged.txt` | [ocr-rule-081.log](ocr-rule-081.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/repo-suite.txt` | [ocr-rule-082.log](ocr-rule-082.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/skill-validation.json` | [ocr-rule-083.log](ocr-rule-083.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/supply-scan.json` | [ocr-rule-084.log](ocr-rule-084.log) | Evidence/helper artifact reviewed under its returned rules; JSON/XML structure or log claims checked in grouped context, no product/production acceptance inferred. |
| `tools/ci/coverage/evaluate.py` | [ocr-rule-085.log](ocr-rule-085.log) | New AST classification only excludes statement-free modules; stale/binding/denominator guards retained. Final exact-candidate wrapper passes 281 changed lines. |
| `tools/ci/mutation/backend.sh` | [ocr-rule-086.log](ocr-rule-086.log) | Interpreter selection, top-level also_copy, cleanup and calibrated timeout reviewed; exact-candidate native run passes, unresolved timeouts still fail closed. |
| `tools/ci/tests/gate_support.py` | [ocr-rule-087.log](ocr-rule-087.log) | Fixture copies exclude real product trees but retain gate tools/docs; own fresh temporary repositories, no candidate mutation. |
| `tools/ci/tests/test_bug1_cideps.py` | [ocr-rule-088.log](ocr-rule-088.log) | Static pin/install ordering assertions useful for backend; omission of hygiene job qualification escapes these checks (R01). |
| `tools/ci/tests/test_bug2_mutenv.py` | [ocr-rule-089.log](ocr-rule-089.log) | Fake executable is explicitly labeled and paired with native end-to-end data-copy check. Native tool needed in hygiene CI (R01). |
| `tools/ci/tests/test_bug3_covempty.py` | [ocr-rule-090.log](ocr-rule-090.log) | Native positive and negative coverage fixtures, fresh temp roots and fail-closed assertions. Missing CI native dependency (R01). |
| `tools/ci/tests/test_gate_support.py` | [ocr-rule-091.log](ocr-rule-091.log) | Real fixture repo with explicit REPO rebinding; verifies product-tree isolation. |

## Developer feedback

- **B01-REV-DX-01:** A provisioned local host masked the hygiene job's new native-tool dependencies. Clean-environment qualification must follow the actual job that owns each test, not just gate backend. Evidence: ci-hygiene-repro.log.
- **B01-REV-DX-02:** 141 passing backend tests, 100% changed-line coverage and 99.49% generated-mutant score did not catch lost poll responses, response-envelope expansion or malformed profile selector types. Evidence: behavior-repro.log.
- **B01-REV-DX-03:** The pipeline AST contract constrains mutmut's trampoline transformation. The explicit handler exclusion preserves that contract, but native mutation coverage of orchestration must not be claimed; its present evidence is behavioral wiring plus line coverage. Evidence: backend/src/pipeline/handler.py:17; survivor-diffs.log; rerun-mutation-result.json.
- **B01-REV-DX-04:** The deployed B01T test allocation was lost between the planning write set and the red inventory. Distinguish authoring a test from executing it later under a dev-stack lease. Evidence: deployed-collection.log; design.md:390; seit.planned_evidence_ownership.
- **B01-REV-DX-05:** Two surviving consistency mutants are not production equivalents. Moto makes them indistinguishable; keep that simulator limit visible even though the mutation score clears its threshold. Evidence: survivor-diffs.log.

## Handoff

Return the frozen REPAIR_REQUIRED receipt to the parent. One bounded repair may address all six findings through the configured bug-triager authority; deterministic verification then closes this review unit. No second independent review or publication authority is granted.

The rendered [link-page.html](link-page.html) is ready for the orchestrator's browser visual review. No live/device/browser acceptance or publication is granted by this receipt.
