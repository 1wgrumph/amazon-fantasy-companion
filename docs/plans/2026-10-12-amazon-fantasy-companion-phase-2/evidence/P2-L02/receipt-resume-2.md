# P2-L02 resume-2 deployment receipt

Outcome: **REPAIRABLE_FAILURE**. Backend deployment passed; required profile smoke acceptance failed. No code or configuration repair attempted. Assigned worker returns evidence to the orchestrator; no nested triage, filing, push or PR.

Issue #29; owner resume-2 packet dated 2026-10-14. Route Codex CLI / GPT-6.1 Sol / medium unchanged. Branch afc/p2-l02; merge commit e0d2112af4ade6f3636daa9a21fa24737a408550. Source and deployed GitCommit: `220c8193be354ba65cc7da00e5261092cd5d8095`. Backend matches origin/main (`git diff --exit-code origin/main -- backend`, exit 0). SAM 1.169.0; AWS CLI 2.38.0; Python 3.12.3; pytest 8.4.2. No tool installations.

ApiUrl: https://le3r79003f.execute-api.us-east-2.amazonaws.com

Stack: **UPDATE_COMPLETE**. describe-stacks confirms expected GitCommit and absence of LinkPassphraseParameter. See stack-status-resume-2.txt.

## Commands and exit codes

All AWS calls used profile afc-dev and region us-east-2. No other stacks touched; SAM reused the authorized aws-sam-cli-managed-default artifact bucket. Deployment ran in a foreground PTY with `timeout --foreground 1500` (25 minutes). No paid-plan prompt appeared. Logs redact twelve-digit sequences as <acct> before persistence; no credential values accessed or printed.

| Command | Exit | Evidence |
| --- | --- | --- |
| `git fetch origin && git merge --no-edit origin/main` | 0 | Merge commit above |
| `sam build` in backend, existing backend-tests PATH, timeout 1500 | 0 | build-resume-2.txt |
| `sam deploy --config-env default --profile afc-dev --region us-east-2 --tags GitCommit=220c8193be354ba65cc7da00e5261092cd5d8095` in backend, foreground timeout 1500 | 0 | deploy-resume-2.txt |
| `aws cloudformation describe-change-set --stack-name afc-dev --change-set-name samcli-deploy1792022935 --include-property-values --profile afc-dev --region us-east-2 --output json` | 0 | changeset-review-resume-2.txt |
| `aws cloudformation get-template --stack-name afc-dev --template-stage Processed --profile afc-dev --region us-east-2 --output json` (before execution; names and role only persisted) | 0 | changeset-review-resume-2.txt |
| `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --region us-east-2 --query 'Stacks[0].{Status:StackStatus,ApiUrl:Outputs[?OutputKey==`ApiUrl`].OutputValue,GitCommit:Tags[?Key==`GitCommit`].Value,ParameterNames:Parameters[].ParameterKey}' --output json` | 0 | stack-status-resume-2.txt |
| `PATH="$HOME/.local/share/afc-tools/backend-tests/bin:$PATH" AFC_DEPLOYED_API_URL=https://le3r79003f.execute-api.us-east-2.amazonaws.com python3.12 -m pytest backend/tests/deployed -v -rs --tb=short` (timeout 1500) | 1 | smoke-resume-2.txt |

Changeset reviewed before entering y: 31 modifications, no additions/removals, detailed replacements all False. Removed ApiFunctionRole's SSM link-passphrase grant; removed global LINK_PASSPHRASE_PARAMETER environment entry from three functions; updated three Lambda code artifacts and GitCommit tags. No unexpected changes. The initial SAM table marked stream mapping replacement Conditional; detailed AWS changeset resolved False, tag-only. Parameter removal confirmed after deployment. This did not delete an SSM parameter or retrieve its value.

## Smoke results

Raw suite: **11 collected, 8 passed, 3 failed, 0 skipped**; exit 1. Actual failures remain recorded even where coverage is deferred.

| Group | Passed | Failed | Skipped | Acceptance |
| --- | --- | --- | --- | --- |
| device_auth / link | 4 | 0 | 0 | PASS |
| api / profile | 3 | 1 | 0 | FAIL; unknown-route structured 404 |
| lineup | 1 | 2 | 0 | NOT_RUN for later panel acceptance; preset roundtrip passed, two attempted panel cases failed on stub |
| feed_ingest | 0 | 0 | 0 | NOT_RUN; no deployed group exists in this revision; later-slice coverage |

Profile failure exact output:

```text
____________________ test_unknown_route_is_a_structured_404 ____________________
backend/tests/deployed/api/test_profile.py:30: in test_unknown_route_is_a_structured_404
    assert_error(status, body, 404)
backend/tests/deployed/deployed_helpers.py:26: in assert_error
    assert isinstance(body["error"]["code"], str) and body["error"]["code"]
E   KeyError: 'error'
```

The test reached the error-envelope assertion after the status assertion. Code/config repair is outside this packet. No root-cause or duplicate-issue claim made. Full exact pytest output in smoke-resume-2.txt.

The two lineup panel cases received `503` with `{'error': {'code': 'not_implemented', 'message': 'This feature is not available yet.'}}`. Source backend/src/panel/__init__.py explicitly defers snapshot to P2-B07. These are visible deferred later-slice gaps, not passes; no data seeding or additional runtime mutation attempted. Full suite command was run as requested, without excluding tests.

## Completion and boundaries

Acceptance 1-2 passed. Acceptance 3 not met because profile has one failure. Evidence/gate/commit results follow in verification-resume-2.txt and gate-resume-2.txt. Stop condition reached: smoke failure needs a code/config change. Runtime remains deployed; no rollback requested. No production DB mutation, IAM user/key, account, billing or other region/stack operation. Test-created development link/profile state comes from the explicitly authorized smoke suite.

OCR coverage_assist remains required for independent phase review, NOT_RUN by this worker. Reverify: not applicable — Python deployment/API observations, no compiled-binary property claim. BRAN unavailable (no native policy). No formal assurance, issue closure, publication or full SEIT closure asserted. Existing untracked Python caches are preserved and excluded.
