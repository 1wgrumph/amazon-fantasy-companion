# P2-L02 resume-4 deployment receipt

Outcome: **PASS** for this owner packet: current origin/main deployed, link/profile smoke passed, all eleven known routes answered. Light Implementer return: **CANDIDATE_READY**. This is author execution evidence, not independent review or complete later-slice acceptance.

Owner resume-4 packet, issue #29, DEC-AFC-SD-056. Route: Codex CLI / GPT-6.1 Sol / high, unchanged. Checkout `amazon-fantasy-companion-p2-l02`, branch `afc/p2-l02`. Initial HEAD `98bdb9c08b07fc19b39773f07305bc6096cb0475`. Fetch and merge exited 0, already up to date. Backend diff against origin/main exited 0.

ApiUrl: https://le3r79003f.execute-api.us-east-2.amazonaws.com

Deployed origin/main SHA: `2d973bd66182364a69b5a3088286e88c08f1107d`. Live `describe-stacks`: **UPDATE_COMPLETE**, GitCommit tag equals that SHA. Source/build router digests match; SAM reused the existing current backend artifact. SAM 1.169.0, AWS CLI 2.38.0, Python 3.12.3, pytest 8.4.2. No tools installed.

## Changeset reviewed before execution

Changeset `samcli-deploy1792026572`: **1 Add, 20 Modify, 11 Remove**. Its full Changes array is identical to resume-3. The owner explicitly authorized its eleven permission removals in resume-4. Detailed replacements are all False; the initial SAM summary calls the event-stream mapping Conditional, but its detailed change is tag-only.

Added `ApiFunctionDefaultRoutePermission`: principal `apigateway.amazonaws.com`, action `lambda:InvokeFunction`, source `arn:aws:execute-api:us-east-2:<acct>:le3r79003f/*/*`. HttpApi adds `$default` to the existing Lambda router. Existing paths and integrations remain identical. Other modifications are GitCommit tag updates. Eleven route-specific ApiFunction permissions are removed as authorized SAM consolidation; their names and full review are in changeset-review-resume-4.txt. No code artifact, IAM policy, schedule-state or resource replacement change. No unexpected delta.

The live changeset was inspected with property values and compared before answering `y` to SAM. The first local inspection parser exited 1 with KeyError Tags because stack tags are represented in Scope/Details, not resource contexts; corrected inspection exited 0. This inspection error did not mutate AWS. Foreground deploy used `timeout --foreground 1500`, completed successfully and exited 0. No paid-plan prompt or expired session occurred.

## Smoke counts and route coverage

Final scoped smoke: **11 collected, 9 selected, 9 passed, 0 failed, 0 skipped, 2 deselected**, exit 0. The two deselections are the documented later-slice panel cases, not passing evidence.

| Group | Final selected | Passed | Deferred / acceptance |
| --- | --- | --- | --- |
| device_auth / link | 4 | 4 | PASS |
| api / profile | 4 | 4 | PASS, including structured unknown-route 404 |
| lineup preset roundtrip | 1 | 1 | PASS |
| lineup panel source | 0 | 0 | 2 NOT_RUN for acceptance: panel.snapshot is P2-B07 AFC-STUB; L03 execution |
| feed_ingest | 0 | 0 | NOT_RUN: no deployed cases exist at this revision; later-slice ingest/data coverage |

**Preserved initial full run:** 11 executed, 9 passed, 2 failed, 0 skipped, exit 1. Initial command-only deselections used the wrong node prefix (`backend/tests/...`); pytest rootdir is backend and requires `tests/...`. Thus both deferred panel cases ran and failed with the known `503 not_implemented` stub. Exact output is retained in smoke-resume-4.txt. Corrected selection is retained in smoke-scoped-resume-4.txt. No source or config was changed. These expected later-slice failures are not relabelled as passed. No in-scope failure needed a code repair.

Separate invoke-permission smoke matched all eleven explicit router routes by AST inventory and asserted expected responses: POST /v1/link 201; GET /v1/link 400; POST /v1/link/confirm 400; GET /link 200; GET and PUT /v1/profile, GET /v1/alerts, GET /v1/panel, GET /v1/providers, POST /v1/routing-outcome and POST /v1/installed-apps all 401 without a session. Error responses carried the router envelope. **11/11 answered, no API Gateway 500/403**, exit 0. This proves invoke reachability and does not claim deferred feature implementation. The profile smoke's foreign-profile 403 is the expected structured application denial.

## Commands and exit codes

Repo-root commands unless noted; PATH prepended `$HOME/.local/share/afc-tools/backend-tests/bin`. AWS commands always used `--profile afc-dev --region us-east-2`, with AWS_PAGER empty. Command streams redacted twelve-digit sequences as `<acct>` before evidence persistence; local home segments replaced with `<home>`. Credentials and device sessions were never printed or retrieved from secret storage.

| Command | Exit | Evidence |
| --- | --- | --- |
| `git fetch origin && git merge --no-edit origin/main` | 0 | already up to date; authority-resume-4.txt |
| `git diff --exit-code origin/main -- backend` | 0 | identity-resume-4.txt |
| `timeout --foreground 1500 sam build` (backend directory) | 0 | build-resume-4.txt |
| `timeout --foreground 1500 sam deploy --config-env default --profile afc-dev --region us-east-2 --tags GitCommit=2d973bd66182364a69b5a3088286e88c08f1107d` (backend, foreground PTY) | 0 | deploy-resume-4.txt; confirmed after review |
| `aws cloudformation describe-change-set --stack-name afc-dev --change-set-name samcli-deploy1792026572 --include-property-values --profile afc-dev --region us-east-2 --output json` | 0 | changeset-resume-4.txt |
| Python changeset comparison/context assertions | 1 initial parser; 0 corrected | changeset-review-resume-4.txt |
| `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --region us-east-2 --query 'Stacks[0].{Status:StackStatus,ApiUrl:Outputs[?OutputKey==`ApiUrl`].OutputValue,GitCommit:Tags[?Key==`GitCommit`].Value}' --output json` | 0 pre/post | preflight-resume-4.txt; stack-status-resume-4.txt |
| Python stdlib HTTPS known-route probe, inventory checked against router AST, 30-second request timeout | 0 | known-routes-resume-4.txt |
| `AFC_DEPLOYED_API_URL=https://le3r79003f.execute-api.us-east-2.amazonaws.com python3.12 -m pytest backend/tests/deployed -v -rs --tb=short` (timeout 1500; initial unmatched PYTEST_ADDOPTS deselections) | 1 | smoke-resume-4.txt; full 9 pass / 2 known deferred failures |
| Same smoke command with corrected PYTEST_ADDOPTS below | 0 | smoke-scoped-resume-4.txt; 9 pass / 2 deselected |
| `bash tools/ci/gate.sh` with test-tools PATH | 0 | gate-resume-4.txt; 61 hygiene and 376 backend tests passed |

Corrected `PYTEST_ADDOPTS` (command-only selection, no file configuration change):

```text
--deselect=tests/deployed/lineup/test_source_labels.py::test_panel_reports_exactly_one_lineup_source --deselect=tests/deployed/lineup/test_source_labels.py::test_panel_source_is_stable_across_reads
```

## Boundaries and remaining work

All runtime mutations stayed in afc-dev and authorized artifact stack aws-sam-cli-managed-default, region us-east-2. No IAM user/key, billing/account, secret, other-stack/region, code/config/CHANGELOG, branch switch, push, PR or issue mutation. Existing untracked Python caches are preserved and excluded. Next handoff: parent consumes this deployment receipt; later P2-B07/L03 supplies panel/ingest acceptance, and parent owns phase review/assurance and issue disposition. No full phase or SEIT closure claimed.

The owner packet supplies checkout authority and next action, recorded in authority-resume-4.txt within the approved plan evidence write set; no numeric lease invented. Router and Light Implementer skills loaded; no nested orchestration. OCR `review.coverage_assist` remains required at independent phase review and is NOT_RUN by this worker. Reverify not applicable to Python deployment/HTTPS observations; no compiled-binary property claim, no ATE substitute. BRAN unavailable because no native policy exists. Final gate, redaction, evidence-only and hook checks are in verification-resume-4.txt.
