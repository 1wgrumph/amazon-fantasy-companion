# BUG-AFC-SEC-AUTH-001 receipt

Outcome: **PASS** for the assigned local Implementer packet. Candidate is on
`afc/bug-auth-hardening`, based on `origin/main`
`2d973bd66182364a69b5a3088286e88c08f1107d`. No remote writes or deployment.
Implementation route: Codex CLI / GPT-6.1 Sol / high, profile `bug-triager`.
Authority and next-action record: [execution-binding.md](execution-binding.md).

## Classification and bounded fix

| Finding | Route | Disposition |
| --- | --- | --- |
| SEC-1 passphrase brute force | already-fixed | `d5ceee9` removed the passphrase under DEC-AFC-SD-048. Reconfirmed from history and current code; excluded from this fix. |
| SEC-2 over-broad-grant | valid-actionable | Removed only ApiFunction's unused `ssm:GetParameter` statement for YahooClientSecretParameter and YahooTokenParameter. PolicyFunction's grant is retained exactly. |
| SEC-3 device-code phishing | valid-actionable | Added visible ownership and phishing instructions before the /link form. Existing expired/used-code rejection and short TTL already work; no auth/state-machine change needed. This is mitigation, not elimination of phishing. |

## Reproduction and source boundary

SEC-2 is a template permission defect, not an AWS/harness failure. The baseline
SAM template grants both named Yahoo parameters to ApiFunction at lines 88–93.
Its handler binding is `api.handler.lambda_handler` at `backend/template.yaml:66`.
[source-trace.txt](source-trace.txt) records reproducible grep commands with
file:line and exit codes. In particular:

- `rg -n 'get_parameter|GetParameter|YAHOO_CLIENT_SECRET_PARAMETER|YAHOO_TOKEN_PARAMETER' backend/src`
  returns no matches (exit 1, expected no-match result). **No backend handler
  currently reads either Yahoo parameter**, including PolicyFunction.
- `backend/src/api/handler.py:17-21` imports alert_policy, device_auth, panel,
  provider_resolver and store; its route map at lines 66–79 and handlers at
  lines 142–226 reach only those modules. No dynamic Yahoo/SSM path exists.
- `backend/src/store/__init__.py:18-23` creates only a DynamoDB resource/table.
  The API modules' other public functions are local logic or explicit stubs.
- `backend/src/lineup/yahoo.py:39-45` accepts a caller-provided token and
  injected transport; lines 70–116 expose Yahoo GET operations, not SSM reads.
  `backend/src/pipeline/handler.py:8-29` also has no SSM reader. Retaining its
  grant is the packet's explicit scope constraint, not a claim it is needed.

The new IAM regression failed against the actual baseline template with
`ApiFunction must not read Yahoo SSM parameters`; no fixture or credential
change was needed to reproduce it.

SEC-3's attacker supplies a real issued code to another person. Anonymous
`POST /v1/link/confirm` (`backend/src/api/handler.py:150-155`) passes the
user-supplied code/profile through `device_auth.confirm`
(`backend/src/device_auth/__init__.py:61-65`) to the atomic store update
(`backend/src/store/__init__.py:74-82`). The holder of the separately issued
polling handle can then receive a session for that profile. Existing end-to-end
link tests exercise the same issue → confirm → poll → authenticated profile
path; the server cannot distinguish a persuaded victim from the TV's owner.

The baseline page only said to enter the code shown on the TV. The new warning
test failed on that actual handler response; it now passes. The warning says to
use only a code on one's own TV physically in front of the user, explains that
linking grants that TV profile access, and rejects the pretext of codes sent by
others or by supposed support. This follows the possession/user-interaction
mitigation in [RFC 8628 §5.4](https://www.rfc-editor.org/rfc/rfc8628.html#section-5.4).
It requires no change to SD-048's code-only confirmation decision.

`store.confirm_link` already requires `codePending AND expiresAt > now`, so
expired, unknown, confirmed and completed codes are rejected with 410. Poll
checks expiry before minting any session (`device_auth/__init__.py:39-48`).
The configured default TTL remains 600 seconds, with existing bounds and HTTP
throttling. A new pre-poll replay test proves a second confirmation cannot
rebind an already-confirmed code, even before the device's first poll, and that
the original profile can still be reached. That preservation test passed on
both baseline and candidate; no red claim is made for already-working guards.

## Origin and escape

SEC-2 originated in `9cd216c` (P2-B01 foundation), which provisioned Yahoo
permission before a reachable secret reader existed. Requirements
`AFC-PR-055` / DES-AFC-P2-BACKEND required SSM containment of Yahoo secrets;
they did not establish an API caller needing read access. The contract in
`test_backend_template.py` positively required API SSM access, and the IAM
repair test introduced in `7eaa700` repeated that assumption. Its otherwise
precise DynamoDB checks did not measure SSM least privilege. Both obsolete
assertions are corrected; the new contract prevents reintroducing API SSM
access. Existing model/plan secret-storage guidance did not supply evidence
of API reachability; a storage requirement was treated as function authority.

SEC-3's original page (`9cd216c`) had no explicit remote-phishing warning.
`d5ceee9` implemented owner decision SD-048 and removed the passphrase, keeping
the existing local-TV instruction. This made code-only linking the relevant
boundary; SD-048 is preserved. The plan's older DES-AFC-P2-AUTH passphrase/OAuth
text is historical and does not override that owner decision. Tests checked
form/code presence and absence of a password (`test_api_contract.py:119-123`),
expiry/replay and normal linking, but never asserted ownership/phishing
instructions. The new response test covers that missed user-interaction
control. No unsupported claim is made about which author/model caused it;
the historical implementation/review rounds did not have these assertions.

No reported AWS failure, dependency failure or negative test is misclassified
as a product defect here. The first post-fix focused run found one further
obsolete API-SSM assertion (116 passed, 1 failed), retained in
[focused-first.txt](focused-first.txt). Correcting that assertion is necessary
test-contract repair, not a new product finding. Frozen-file exception:
`test_backend_template.py` retargets its positive grant assertion to the
retained PolicyFunction; `test_template_iam.py` inverts only the API grant
assertion while retaining PolicyFunction, DynamoDB and stream checks.

## Verification and prevention

Method=test. Real inputs: committed template/YAML and actual Lambda response,
using the existing offline Moto fixture and network guard. No new fake,
dependency, test engine, shared port or service-backed test. The three new
tests add roughly 0.3 seconds to host-pytest; no gate changes were needed.
Both regressions are automatically collected by the repository backend gate.

All Python commands below use
`PATH=$HOME/.local/share/afc-tools/backend-tests/bin:$PATH` and
`PYTHONDONTWRITEBYTECODE=1`. `NEW` means
`backend/tests/contract/test_security_auth_iam.py backend/tests/unit/test_security_auth_link.py`.

| Command/check | Exit | Evidence/result |
| --- | --- | --- |
| Baseline `python3.12 -m pytest -q -p no:cacheprovider NEW` | 1 expected | [red.txt](red.txt): both finding regressions fail; existing one-confirm guard passes (2 failed, 1 passed). |
| Candidate same test IDs | 0 | 3 passed in 0.28 s; identical command and tests, only authorized product changes. |
| `python3.12 -m pytest -q -p no:cacheprovider NEW backend/tests/unit/test_device_auth.py backend/tests/unit/test_device_auth_units.py backend/tests/unit/test_bug_auth002.py backend/tests/unit/test_router.py backend/tests/contract/test_backend_template.py backend/tests/contract/test_template_iam.py` | 0 | [green.txt](green.txt): 117 passed; expiry, replay, short TTL, token retry, cross-profile rejection, CSP and valid linking stay green. |
| `bash tools/ci/gate.sh` | 0 | [gate.txt](gate.txt): spec/docs/hygiene/backend PASS, 61 CI-tool tests, 379 backend tests; tvapp PASS (no tree). Nested negative git diagnostics are expected gate fixtures, not a gate failure. |
| `sam validate --lint --template backend/template.yaml --region us-east-2` | 0 | [sam.txt](sam.txt): valid SAM template; telemetry/metadata disabled and credential/config file access pointed at /dev/null; local only. |
| Semantic YAML and HTML comparison to origin/main; new-test AST parse | 0 | Only ApiFunction's two-resource SSM statement removed; every other template value identical. HTML differs only in the instruction paragraphs, preserving form, script and CSP. |
| `git diff --check` | 0 | No whitespace errors. |
| First commit hook | 1 | [commit-hook.txt](commit-hook.txt): hygiene rejected trailing whitespace / extra EOF blank line in captured logs. All 379 backend tests still passed. Evidence whitespace was trimmed; no hook bypass or product/test change. |
| Final `git diff --name-only origin/main HEAD` scope check | 0 | Only the authorized template, API page, tests, changelog and this evidence directory. |

New regression test IDs:
`test_api_has_no_ssm_parameter_read_grant` and
`test_link_page_warns_before_authorizing_a_device`. Both are red on baseline
and green on candidate. Additional preservation:
`test_confirmation_cannot_rebind_a_code_before_the_first_poll`.
Retained logs normalize home-directory paths, volatile function addresses and
trailing whitespace; test IDs, failure assertions and outcomes are preserved.

## Review, visual evidence and limits

A fresh read-only boundary investigator independently corroborated the import
graph, store condition and smallest compatible warning. A single fresh
candidate review ran Claude Code 2.1.300 / `claude-opus-5-5` / medium, with no
edits or tests, and found no introduced bypass/regression. See
[security-review.txt](security-review.txt). Reviewer ran OCR in delegation
workspace mode (`ocr delegate preview --format json`, then `ocr delegate rule`
for both listed files); its per-file sections cover link.html and template.yaml,
with manual review of tests and changelog. The initial author probe using
`--from` without `--to` returned a usage error; correct workspace mode ran in
the reviewer session. This was not a product failure or a route substitution.
This focused security review is not formal Lifecycle assurance/owner acceptance.
Invocation: `claude -p --model claude-opus-5-5 --effort medium
--permission-mode plan --no-session-persistence` with only Read and bounded
read-only Bash tools, stdin /dev/null; exit 0. One review, no review repair.
Tool versions: Python 3.12.3, SAM CLI 1.169.0. No tool installs.

The reviewer did not drive a browser. The Implementer separately checked the
real Lambda-rendered /link page and headers on an ephemeral loopback-only
server with Chrome via CUA: [desktop](link-desktop.png),
[phone](link-phone.png). The warning is visible before the fields, wraps without
horizontal clipping, and the labels/button remain readable. Phone viewport
override was reset; tab and owned server were closed. Only the changed initial
state was inspected visually; API/unit tests cover linking/error states.
The in-app browser was unavailable, so the available Chrome browser was used;
no runtime/model route was switched.

BRAN: unavailable (no native policy). Reverify: not applicable; no compiled
binary claim. Dependency deprecation warnings remain non-failing. The user's
required `(PR #TBD)` changelog placeholder remains for the landing agent to
replace, since push/PR/branch changes are prohibited in this packet.

Residual risk: a user who ignores the warning can still approve an attacker's
fresh code within its TTL. Code-only linking does not authenticate the person
confirming or prove device possession. This is the preserved SD-048 test-device
design; do not interpret this receipt as eliminating remote phishing or as
authorizing a customer-facing activation. No live IAM/deployment validation,
AWS calls, credential access, production DB change or remote issue action was
performed. Any separate change to stronger authentication needs owner intent.

## Acceptance

| Objective | Result |
| --- | --- |
| 1. SEC-2 caller evidence, remove API grant only, red/green contract | PASS |
| 2. SEC-3 bounded mitigation, red/green warning regression, valid/negative linking preserved | PASS |
| 3. Full gate and local SAM lint exit 0 | PASS |
| 4. Reproduction, origin, escape, classification, red/green, prevention receipt | PASS |
| 5. Unreleased Security changelog entry with PR #TBD | PASS |

Local commit uses Codex author environment, hooks on, no Co-Authored-By.
No branch switch, push, PR or merge. Cleanup removes only untracked Python
caches generated during verification. The final response supplies commit SHA.
