# P2-L02 resume-3 deployment receipt

Outcome: **CONTRACT_FAILURE**; Light Implementer return **NEEDS_MORE_EVIDENCE**, `reclassify: judgement`. Issue #29 remains incomplete. Reviewed changeset differs from the owner packet's expected additions. Deployment was declined before execution; no runtime update occurred. No code/config repair, push, PR, issue mutation or nested triage.

Owner packet dated 2026-10-14; DEC-AFC-SD-056. Route Codex CLI / GPT-6.1 Sol / high. Checkout amazon-fantasy-companion-p2-l02, branch afc/p2-l02. Initial HEAD `9434d14`; merge `083e1bfd447e96ef55a954e0913b9dbf8b72eeda`. Target origin/main: `2d973bd66182364a69b5a3088286e88c08f1107d`. Backend equals origin/main (`git diff --exit-code origin/main -- backend`, exit 0). SAM 1.169.0; AWS CLI 2.38.0; Python 3.12.3. No tools installed.

ApiUrl: https://le3r79003f.execute-api.us-east-2.amazonaws.com

Observed stack status: **UPDATE_COMPLETE**, unchanged. Actual deployed GitCommit remains `220c8193be354ba65cc7da00e5261092cd5d8095`. The target SHA is **not deployed**.

## Changeset review before execution

Changeset `samcli-deploy1792025781`: **1 Add, 20 Modify, 11 Remove**. Detailed replacements all False (the SAM summary initially showed the event stream mapping as Conditional). All 20 modifications include the requested GitCommit tag update; HttpApi additionally adds `$default`. Existing API paths and integrations are identical before and after. No Lambda code artifact or IAM-role policy changes appear in the changeset.

Expected addition: `ApiFunctionDefaultRoutePermission`, principal `apigateway.amazonaws.com`, action `lambda:InvokeFunction`, scoped to `arn:aws:execute-api:us-east-2:<acct>:le3r79003f/*/*`. The `$default` route uses the existing API Lambda.

**Unexpected relative to packet:** deletion of these 11 route-specific Lambda permissions:

- ApiFunctionAlertsPermission
- ApiFunctionInstalledAppsPermission
- ApiFunctionLinkConfirmPermission
- ApiFunctionLinkIssuePermission
- ApiFunctionLinkPagePermission
- ApiFunctionLinkPollPermission
- ApiFunctionPanelPermission
- ApiFunctionProfileGetPermission
- ApiFunctionProfilePutPermission
- ApiFunctionProvidersPermission
- ApiFunctionRoutingOutcomePermission

The packet expected only the default route and its permission, and asked that anything else be flagged. The assigned light role cannot choose an unprovided disposition. The exact reviewed delta was presented to the owner; no authorization to execute the deletions was received before cancellation. No assertion that these deletions are a product defect is made. A parent/owner decision to accept this transformed changeset, or a revised packet, is the remaining dependency.

SAM was answered `n`. SAM exited **0 on cancellation**; this is not deployment success. Post-cancellation describe-change-set reports `CREATE_COMPLETE`, `ExecutionStatus: AVAILABLE` (unexecuted). The changeset and uploaded template remain; neither stack was deleted or changed by executing it. No paid-plan prompt or AWS-session expiration occurred.

## Commands and exit codes

Commands were run in the named worktree, in sequence. AWS calls always used `--profile afc-dev --region us-east-2`; only afc-dev and the authorized aws-sam-cli-managed-default artifact stack were in scope. All command log streams replace twelve-digit sequences with `<acct>` before persistence. Credentials were not printed or retrieved.

| Command | Exit | Evidence |
| --- | --- | --- |
| `git fetch origin && git merge --no-edit origin/main` | 0 | Merge SHA above; no rebase/reset/switch |
| `git diff --exit-code origin/main -- backend` | 0 | Backend matches target |
| `sam build` from backend, test-tools PATH, `timeout --foreground 1500` | 0 | build-resume-3.txt |
| `sam deploy --config-env default --profile afc-dev --region us-east-2 --tags GitCommit=2d973bd66182364a69b5a3088286e88c08f1107d` from backend, test-tools PATH, foreground PTY, `timeout --foreground 1500` | 0, **declined** | deploy-resume-3.txt; not executed |
| `aws cloudformation describe-change-set --stack-name afc-dev --change-set-name samcli-deploy1792025781 --include-property-values --profile afc-dev --region us-east-2 --output json` | 0 | changeset-resume-3.txt; changeset-command-resume-3.txt |
| Python assertions on changeset contexts: existing paths/integrations unchanged, only `$default` added, other modifications tag-only, all replacements False | 0 | Author diagnostic, not independent assurance |
| `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --region us-east-2 --query 'Stacks[0].{Status:StackStatus,ApiUrl:Outputs[?OutputKey==`ApiUrl`].OutputValue,GitCommit:Tags[?Key==`GitCommit`].Value}' --output json` | 0 before and after cancellation | preflight-resume-3.txt; stack-status-resume-3.txt |
| `aws cloudformation describe-change-set --stack-name afc-dev --change-set-name samcli-deploy1792025781 --profile afc-dev --region us-east-2 --query '{ChangeSetName:ChangeSetName,Status:Status,ExecutionStatus:ExecutionStatus}' --output json` | 0 | changeset-status-resume-3.txt |
| `PATH="$HOME/.local/share/afc-tools/backend-tests/bin:$PATH" AFC_DEPLOYED_API_URL=https://le3r79003f.execute-api.us-east-2.amazonaws.com python3.12 -m pytest backend/tests/deployed -v -rs --tb=short` | **NOT_RUN** | Target revision was not deployed; no smoke acceptance claimed |
| `PATH="$HOME/.local/share/afc-tools/backend-tests/bin:$PATH" bash tools/ci/gate.sh` | 0 | gate-final-resume-3.txt; all gate areas passed, 61 hygiene tests and 376 backend tests |

## Smoke results

**0 executed, 0 passed, 0 failed, 0 pytest skips.** No pytest session or collection was started. The case counts below are the source inventory, not a test run. NOT_RUN is distinct from pytest skips and PASS.

| Group | Source cases | Executed | Result / reason |
| --- | --- | --- | --- |
| device_auth / link | 4 | 0 | NOT_RUN: target deployment was declined |
| api / profile | 4 | 0 | NOT_RUN: target deployment was declined; repaired 404 remains unverified in deployment |
| lineup | 3 | 0 | NOT_RUN: target deployment declined; two panel cases additionally depend on P2-B07's unimplemented panel snapshot, allocated to L03; preset case not attempted |
| feed_ingest | 0 | 0 | NOT_RUN: no deployed test group exists at this revision; later-slice coverage |

No resume-2 smoke results are reused as current acceptance. Source `backend/src/panel/__init__.py` explicitly defers snapshot to P2-B07.

## Completion and boundaries

Build and changeset preparation passed; target deployment, deployed-SHA acceptance and smoke acceptance did not complete. Remaining obligations: disposition of the 11 permission deletions; execute approved deployment; verify UPDATE_COMPLETE with target GitCommit; run the exact deployed suite and report current counts; record any genuinely deferred groups without PASS claims. Final gate, redaction and evidence-only commit checks are recorded in verification-resume-3.txt.

Owner packet supplies the exact checkout and next action; no separate numeric lease generation was invented. Authority and next action are recorded in authority-resume-3.txt within the approved evidence write set. No code/config/CHANGELOG edits beyond the explicitly authorized merge from main. Existing untracked Python caches are excluded.

review.coverage_assist / OCR remains required for independent phase review and is NOT_RUN by this worker. Reverify: not applicable to this Python deployment/API packet; no compiled-binary property claim. BRAN unavailable (no native policy). No independent review, formal assurance, issue closure, release or publication claimed.
