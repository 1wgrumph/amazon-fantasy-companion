# P2-L02 deployment receipt

Outcome: **REPAIRABLE_FAILURE**. Deployment succeeded; deployed smoke acceptance did not. No code/config changes or repair attempted.

Lifecycle AFC-2026-10-11 Phase 2; issue #29; milestone M05; authority AUTH-AFC-2026-10-12-P2-001 plus owner resume amendment on 2026-10-14. Branch `afc/p2-l02`; resumed at `3f6adce68bd8325159241c3f536dc4072c9fec03`. Intended and deployed SHA `75afca022f967945a70bf715beb2a7c98e65ed9d`; backend tree `7c0a94484ed1ace448fbefdf3dcae0412f13134d` matches both revisions. Previous blocked-run logs remain historical evidence; this receipt supersedes their outcome. Route Codex CLI / GPT-6.1 Sol / medium (DEC-AFC-SD-043/045), unchanged; no live profile catalog read.

Owner amendment authorizes create/update of `afc-dev` and `aws-sam-cli-managed-default` only, in `us-east-2` with profile `afc-dev`, including SAM resolve_s3 artifact provisioning. All other packet limits remain. Checkout matches owner binding; pre-existing untracked Python caches outside the write set were left untouched. BRAN unavailable (no native policy). Root AGENTS.md and CLAUDE.md absent. Next action is orchestrator triage of the deployed fixture failure and authorized non-printing passphrase setup before another smoke run. Do not repeat deployment solely to repair test preparation.

## Deployment result

- `afc-dev`: **CREATE_COMPLETE**; SAM deploy exit **0**.
- ApiUrl: `https://le3r79003f.execute-api.us-east-2.amazonaws.com`.
- Stack GitCommit tag: `75afca022f967945a70bf715beb2a7c98e65ed9d`.
- `aws-sam-cli-managed-default`: **CREATE_COMPLETE**, one S3 artifact bucket plus its bucket policy.
- Changeset reviewed before answering `y` for afc-dev: additions only, matching the planned template. Confirmation/CloudFormation events are in deploy-resume-foreground.txt. No paid-plan/billing prompt or upgrade accepted.
- First deploy attempt created managed artifacts and an unexecuted afc-dev changeset, then stopped on terminal access because timeout used a separate process group. Terminated with exit 143. Retry after this new harness evidence used `timeout --foreground 900` with identical SAM arguments. See resume-authority.txt; no route change.

## Commands and exits

All AWS calls below use `--profile afc-dev --region us-east-2`; all processes bounded to 900 seconds. PATH includes the existing backend-tests venv. Logs redact every twelve-digit sequence as `<acct>` and home paths as `<home>`. No credential values retrieved, printed or committed.

| Command | Exit/result | Evidence |
| --- | --- | --- |
| `sam validate --region us-east-2` in backend (prior run) | 0 | validate.txt |
| `sam build` in backend (prior run, reused unchanged artifact) | 0 | build.txt, build-identity.txt |
| `sam deploy --config-env default --profile afc-dev --region us-east-2 --tags GitCommit=75afca022f967945a70bf715beb2a7c98e65ed9d` in backend, timeout wrapper | 143; interrupted terminal harness, changeset not executed | deploy-resume.txt |
| Same deploy under `timeout --foreground 900`, reviewed changeset then `y` | 0 | deploy-resume-foreground.txt |
| `aws cloudformation describe-stacks --stack-name afc-dev --query 'Stacks[0].{Status:StackStatus,ApiUrl:Outputs[?OutputKey==`ApiUrl`].OutputValue,GitCommit:Tags[?Key==`GitCommit`].Value}' --profile afc-dev --region us-east-2 --output json` | 0; COMPLETE, URL and expected tag | stack-status-resume.txt |
| `aws cloudformation list-stack-resources --stack-name afc-dev --query 'StackResourceSummaries[].{LogicalId:LogicalResourceId,Type:ResourceType,PhysicalId:PhysicalResourceId,Status:ResourceStatus}' --profile afc-dev --region us-east-2 --output json` | 0; 31 resources COMPLETE | stack-resources-resume.txt |
| Same resource query for `aws-sam-cli-managed-default` | 0; bucket and bucket policy COMPLETE | managed-resources-resume.txt |
| `aws cloudformation describe-stacks --stack-name aws-sam-cli-managed-default --query 'Stacks[0].{Status:StackStatus}' --profile afc-dev --region us-east-2 --output json` | 0; CREATE_COMPLETE | managed-status-resume.txt |
| `git rev-parse 75afca0:backend HEAD:backend` | 0; both trees equal | backend-tree-resume.txt |
| `sha256sum backend/template.yaml backend/.aws-sam/build/template.yaml backend/samconfig.toml` | 0; all match prior build receipt | build-digests-resume.txt |
| `AFC_DEPLOYED_API_URL=https://le3r79003f.execute-api.us-east-2.amazonaws.com AFC_DEPLOYED_TEST_PROFILE=p2-l02-resume-smoke python3.12 -m pytest backend/tests/deployed/device_auth -v -rs --tb=short --show-capture=no` | **1; 4 collected, 3 failed, 1 skipped, 0 passed** | deployed-link-resume.txt |
| Same environment, `python3.12 -m pytest backend/tests/deployed/api -v -rs --tb=short --show-capture=no` | **0; 4 collected, 4 skipped, 0 passed; NOT_RUN** | deployed-profile-resume.txt |
| `bash tools/ci/gate.sh` with venv PATH | 0; 61 CI tests and 158 backend tests passed | gate-resume.txt, gate-resume-staged.txt |

Discovery/check commands: pwd, branch, HEAD and status checks exit 0; missing root AGENTS.md cat exit 1; reading supplied skills/workspace rules and existing tests/config/logs exit 0; slice/SEIT JSON extraction exit 0; passphrase-presence-only check exit 0 (absent); template rg, process-state checks and fd reads exit 0. Attempted terminal tcsetpgrp recovery exited 1 (ENOTTY), then process termination commands exited 0. No AWS error or authentication expiry occurred in this resume. Exact substantive command lines and exit codes are in each named log.

## Smoke failure and missing prerequisite

Device-auth tests fail at `backend/tests/deployed/conftest.py:38` with `AssertionError: Deployed test may only contact le3r79003f.execute-api.us-east-2.amazonaws.com`. The fixture compares `address[0]` passed to socket.connect with the URL hostname; Python socket.create_connection resolves DNS before socket.connect. This is deployed test-harness evidence, not evidence of an API response failure. The tests did not complete HTTPS requests. Do not weaken the network containment guard; orchestrator owns triage/repair and regression/prevention checks. No nested bug workflow or GitHub action performed by this assigned worker.

`AFC_DEPLOYED_LINK_PASSPHRASE` is absent in this process. The shared linked fixture skips the confirmed-link test and every profile test. No SSM credential retrieval or secret creation attempted. Exit 0 from an all-skipped profile group is **not PASS**. Both requested deployed groups were invoked separately; the frozen `-k link` selection alone was not used.

## Acceptance to evidence

| Acceptance | Result | Evidence |
| --- | --- | --- |
| 1. Validate/build exit 0 | PASS, prior run reused with identical tree/template/config digests | validate.txt, build.txt, build-identity.txt, build-digests-resume.txt |
| 2. Reviewed changeset, deploy exit 0 | PASS | deploy-resume-foreground.txt |
| 3. ApiUrl and COMPLETE stack | PASS | stack-status-resume.txt |
| 4. Link and profile smoke pass | **NOT_MET: link 3 failed/1 skipped; profile 4 skipped** | deployed-link-resume.txt, deployed-profile-resume.txt |
| 5. Sanitized receipt, resources, cost note | Receipt/inventories supplied; eligibility caveat below | this receipt, stack-resources-resume.txt, managed-resources-resume.txt |
| 6. Gate and local evidence commit | 0; 61 CI tests and 158 backend tests passed | gate-resume-staged.txt and local Git commit |

## Resources and cost boundary

Observed afc-dev inventory: six DynamoDB tables, three Lambda functions, four service roles, eleven Lambda permissions, three CloudWatch log groups, HTTP API and stage, disabled-by-default ingestion scheduler, one stream event source mapping (31 total). Managed artifact stack contains one S3 bucket and its bucket policy. No other stacks queried, modified or deleted. Source template declares DynamoDB PAY_PER_REQUEST, seven-day logs and scheduler default DISABLED. No IAM users/keys or account/billing changes.

Owner explicitly confirmed the SAM artifact bucket is within free tier. This run checked template types/defaults, actual resource inventory and deploy output for paid-only/upgrade prompts; none appeared. It did **not** query billing/account eligibility, credits, service usage, quotas or free-tier balances. Therefore it does not establish that all deployed usage is free or close AFC-PR-054/RISK-AFC-P2-07. These remain P2-L03 obligations. The source template Free-plan wording alone is not eligibility proof.

## Proof rows and later obligations

No full SEIT row is closed by this worker receipt. Deployment and tree/tag identity are supporting evidence only.

| Proof row | Supplied now / remaining closure |
| --- | --- |
| SEIT-AFC-P2-DX-01 | Feedback supplied; aggregate P2-SCR1 closure later |
| SEIT-AFC-P2-PATH-01 | Local hygiene/gate support; aggregate P2-G01 closure later |
| SEIT-AFC-P2-LAND-01, SEIT-AFC-P2-REL-01 | Not satisfied; independent review, landing/changelog remain orchestrator/P2-R5 |
| SEIT-AFC-P2-REV-01 | OCR delegation required at independent review, NOT_RUN here; aggregate P2-L05 later. Reverify not applicable: no compiled-binary attribute claim |
| SEIT-AFC-PR-038 | Not satisfied; smoke failure plus missing passphrase; full expiry/replay, real stick and owner phone/browser demonstration still required |
| SEIT-AFC-PR-054, SEIT-RISK-AFC-P2-07 | Deployment inventory and boundary record supplied; account eligibility and registered P2-L03 proof remain |
| SEIT-RISK-AFC-P2-10 | No route switch, capabilities retained; no independent aggregate assurance claim |

No Fire TV stick is available. No APK/ApiUrl equivalence or end-to-end owner confirmation claimed. Runtime remains deployed; no rollback/deletion authorized or attempted.

## developer_feedback

- AFC-L02-OBS-001: prior stack-authority prerequisite resolved by explicit owner amendment; see resume-authority.txt. No product change.
- AFC-L02-OBS-002: both groups now invoked separately; profile acceptance remains NOT_RUN, not silently excluded. Evidence: deployed-link-resume.txt and deployed-profile-resume.txt.
- AFC-L02-OBS-003: deployed network fixture rejects resolved socket addresses before HTTPS reaches API. Three device-auth failures at conftest.py:38; evidence deployed-link-resume.txt. Assigned worker reports to orchestrator for bounded triage, does not repair.
- AFC-L02-OBS-004: authenticated deployed tests require an environment passphrase not supplied at dispatch; five skipped tests total. Evidence both smoke logs and shared conftest. No credential access attempted.
- AFC-L02-OBS-005: interactive SAM under timeout requires foreground process-group handling; first attempt stopped at confirmation, foreground retry succeeded. Evidence deploy-resume.txt, deploy-resume-foreground.txt, resume-authority.txt. Local invocation issue, no reproduced SAM product defect claimed.

Tools exercised: Git, Python 3.12/pytest, existing SAM 1.169.0 and AWS CLI 2.38.0, process/terminal diagnostics, repository gate/hooks. No tool installation. All committed changes stay in P2/evidence/P2-L02; .aws-sam and pre-existing caches excluded. Evidence output hashes recorded in resume-log-digests.txt.

Final pre-commit verification: full gate exit 0 (61 CI tests, 158 backend tests); fixture negative-control GAP/fatal lines in gate output are expected test cases, not failing gate results. Receipt twelve-digit scan empty; git diff --check exit 0. No product changes. Commit hook and committed-head verification reported in worker return.

Evidence formatting correction: first git commit attempt exited 1 because the enabled hygiene hook rejected SAM table trailing spaces (WS-CHECK in both deploy logs). Removed only trailing whitespace and normalized terminal line endings in those logs; no substantive output removed. The earlier full gate ran before new logs were staged and therefore did not cover them; staged full gate rerun follows. Hooks remain enabled.

Staged full-gate rerun after evidence formatting correction: exit 0; 61 CI tests and 158 backend tests passed (gate-resume-staged.txt). First commit attempt exit 1; final commit exit and SHA reported in return. No skipped deployed case is counted as PASS.
