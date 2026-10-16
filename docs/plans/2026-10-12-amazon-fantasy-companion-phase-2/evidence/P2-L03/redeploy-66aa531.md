# P2-L03 redeploy receipt

Outcome: **PASS**. afc-dev runs `66aa5314b2a3f3f56b066e338b5f223db7bd0db2`. This is a routine redeploy of merged fixes. No product code changed in this worktree.

Prior live commit `af0e0ac1520ce5b9e7de186fd83df23bc92d6a5e` (UPDATE_COMPLETE at 2026-10-16T15:49:42Z). Since then, main merged #101 (G3 panel wire contract: `lineupVersion` is a non-key attribute, strongly consistent reads), #103 (boxscore ingest bounds: IngestFunction code and `schema/summary.json`), #99 (TV app only, not deployed by SAM), and #100 and #102 (docs and CI only).

`git diff af0e0ac1520ce5b9e7de186fd83df23bc92d6a5e 66aa5314b2a3f3f56b066e338b5f223db7bd0db2 -- backend/template.yaml` was empty. Deployed backend tree of `66aa5314b2a3f3f56b066e338b5f223db7bd0db2` and of `HEAD` are both `3ba68085287cc5acd9aafd914645fc00a8a606c1`. The prior deploy's backend tree was `aa7333fe57c9f52b001551a0e91d5ed961b6f229`.

ApiUrl: https://le3r79003f.execute-api.us-east-2.amazonaws.com

Live `describe-stacks`: **UPDATE_COMPLETE**, LastUpdatedTime `2026-10-16T18:21:02.896000+00:00`, GitCommit tag `66aa5314b2a3f3f56b066e338b5f223db7bd0db2`. SAM 1.169.0, AWS CLI 2.38.0, Python 3.12.3, pytest 8.4.2. No tools installed.

Parameter overrides were empty. This deploy did not change the lineup source.

## Changeset reviewed before execution

Changeset `samcli-deploy1792174771` was created with `sam deploy --no-execute-changeset` and inspected with `describe-change-set --include-property-values` before execute. Live status **CREATE_COMPLETE**, execution **AVAILABLE**. Resource actions **0 Add, 22 Modify, 0 Remove**. The changeset tag is GitCommit `66aa5314b2a3f3f56b066e338b5f223db7bd0db2`. The saved array is changeset-redeploy.txt after `<acct>` redaction. The classification is changeset-review-redeploy.txt.

Lambda code, Replacement=False, RequiresRecreation Never. The only property change is the Code S3 key, plus the GitCommit tag. Environment, role, handler, runtime, memory and timeout are unchanged.

- `ApiFunction`
- `IngestFunction`
- `PolicyFunction` (the three functions share one packaged source tree, so the policy artifact key changes with the api and ingest code)

Tag-only, Replacement=False, scope Tags, RequiresRecreation Never. GitCommit `af0e0ac1520ce5b9e7de186fd83df23bc92d6a5e` to `66aa5314b2a3f3f56b066e338b5f223db7bd0db2`. Structural properties are identical.

- DynamoDB tables: Alerts, Events, Lineups, Links, Panels, PlayerStats, Profiles. No table was replaced.
- IAM roles: `ApiFunctionRole`, `IngestFunctionRole`, `IngestScheduleRole`, `PolicyFunctionRole`. No statement, action, or resource was added or removed.
- `ApiFunctionDefaultRoutePermission`, the three log groups, `HttpApi`, `HttpApiApiGatewayDefaultStage`, `IngestSchedule`.

No SSM parameter resource is in the changeset. SSM values were not read. No resource Action Remove. No Replacement=True. No Replacement=Conditional on a stateful resource.

`PolicyFunctionEventStream`: the SAM summary table printed Replacement Conditional. `describe-change-set` with property values says Replacement=False, scope Tags, RequiresRecreation Never. It is an event-source mapping, not a DynamoDB table or SSM parameter.

Execute proceeded. `execute-change-set` exited 0 at 2026-10-16T18:21:03Z. `wait stack-update-complete` exited 0 at 2026-10-16T18:22:34Z.

## Smoke counts and suite

CMD-DEPLOYED-SMOKE: **26 collected, 4 selected, 4 passed, 0 failed, 0 skipped, 22 deselected**, exit 0. The 22 deselections are the `-k link` filter. None is counted as a smoke pass. No NOT_RUN case.

| Node id | Reason |
| --- | --- |
| `tests/deployed/alert_policy/test_alert_policy_deployed.py::test_served_alerts_have_registered_types_and_context` | deselected by `-k link`; keyword does not match |
| `tests/deployed/alert_policy/test_alert_policy_deployed.py::test_served_alerts_are_released` | deselected by `-k link`; keyword does not match |
| `tests/deployed/alert_policy/test_alert_policy_deployed.py::test_served_red_zone_text_is_team_level` | deselected by `-k link`; keyword does not match |
| `tests/deployed/api/test_profile.py::test_profile_roundtrip_preserves_revision` | deselected by `-k link`; keyword does not match |
| `tests/deployed/api/test_profile.py::test_foreign_profile_is_forbidden` | deselected by `-k link`; keyword does not match |
| `tests/deployed/api/test_profile.py::test_malformed_body_is_a_structured_400` | deselected by `-k link`; keyword does not match |
| `tests/deployed/api/test_profile.py::test_unknown_route_is_a_structured_404` | deselected by `-k link`; keyword does not match |
| `tests/deployed/feed_ingest/test_feed_labels.py::test_panel_values_carry_a_source_label` | deselected by `-k link`; keyword does not match |
| `tests/deployed/feed_ingest/test_feed_labels.py::test_panel_revision_never_moves_backwards` | deselected by `-k link`; keyword does not match |
| `tests/deployed/feed_ingest/test_feed_labels.py::test_alerts_carry_the_envelope` | deselected by `-k link`; keyword does not match |
| `tests/deployed/lineup/test_source_labels.py::test_panel_reports_exactly_one_lineup_source` | deselected by `-k link`; keyword does not match |
| `tests/deployed/lineup/test_source_labels.py::test_panel_source_is_stable_across_reads` | deselected by `-k link`; keyword does not match |
| `tests/deployed/lineup/test_source_labels.py::test_preset_selection_roundtrip` | deselected by `-k link`; keyword does not match |
| `tests/deployed/matcher/test_matcher_deployed.py::test_alert_ids_are_unique_per_profile` | deselected by `-k link`; keyword does not match |
| `tests/deployed/matcher/test_matcher_deployed.py::test_alert_revision_never_moves_backwards` | deselected by `-k link`; keyword does not match |
| `tests/deployed/panel/test_panel_deployed.py::test_panel_data_carries_basis_rows_and_value_objects` | deselected by `-k link`; keyword does not match |
| `tests/deployed/panel/test_panel_deployed.py::test_panel_rereads_keep_id_and_never_lower_revision` | deselected by `-k link`; keyword does not match |
| `tests/deployed/panel/test_panel_deployed.py::test_preset_change_reaches_the_panel` | deselected by `-k link`; keyword does not match |
| `tests/deployed/panel/test_panel_deployed.py::test_panel_game_facts_agree_with_alerts` | deselected by `-k link`; keyword does not match |
| `tests/deployed/provider_resolver/test_providers_deployed.py::test_installed_report_is_accepted` | deselected by `-k link`; keyword does not match |
| `tests/deployed/provider_resolver/test_providers_deployed.py::test_providers_reads_an_access_basis_never_verified_from_install` | deselected by `-k link`; keyword does not match |
| `tests/deployed/provider_resolver/test_providers_deployed.py::test_invented_routing_outcome_is_rejected` | deselected by `-k link`; keyword does not match |

The four selected smoke cases all passed: `test_issue_returns_a_pending_code`, `test_pending_poll_cannot_authorize_the_device`, `test_confirmed_device_polls_a_usable_session`, `test_unknown_session_is_rejected_on_protected_routes`.

CMD-DEPLOYED-TESTS: **26 collected, 26 selected, 26 passed, 0 failed, 0 skipped, 0 deselected**, exit 0. No NOT_RUN case. No deployed failure to record. The 22 smoke deselections passed here as selected cases. That does not relabel them as smoke passes.

## Stub scan

CMD-STUB-SCAN was re-run on this tree. `git grep` exited 0 because it found matches. The wrapper `test` that the scan is empty exited 1. Finding, not fixed here:

- `backend/src/api/handler.py` line 5 (docstring mentions AFC-STUB)
- `backend/src/api/handler.py` line 37 (`except NotImplementedError`)
- `tv-app` `WatchActivity.kt` line 6 (AFC-STUB comment for P2-A04)

No other AFC-STUB or NotImplementedError match in `backend/src` or `tv-app/app/src/main`.

## Commands and exit codes

Repo-root commands unless noted. AWS commands used `--profile afc-dev --region us-east-2`, with AWS_PAGER empty. `python3.12` for pytest was the backend-tests interpreter on PATH (`$HOME/.local/share/afc-tools/backend-tests/bin`). `TMPDIR=/var/tmp/az-l03r`. Command streams redacted home segments as `<home>` and twelve-digit sequences as `<acct>` before evidence persistence. Credentials, SSM values, and secret values were never printed or retrieved.

| Command | Exit | Evidence |
| --- | --- | --- |
| `timeout --foreground 1500 sam build` (backend) | 0 | build-redeploy.txt |
| `sam deploy --config-env default --profile afc-dev --region us-east-2 --no-execute-changeset --tags GitCommit=66aa5314b2a3f3f56b066e338b5f223db7bd0db2` | 0 | deploy-redeploy.txt; changeset `samcli-deploy1792174771` |
| `aws cloudformation describe-change-set --include-property-values` | 0 | changeset-redeploy.txt; changeset-review-redeploy.txt |
| `aws cloudformation execute-change-set --change-set-name samcli-deploy1792174771 --stack-name afc-dev` | 0 | execute-change-set-redeploy.txt; 2026-10-16T18:21:03Z |
| `aws cloudformation wait stack-update-complete --stack-name afc-dev` | 0 | execute-change-set-redeploy.txt; 2026-10-16T18:22:34Z |
| `aws cloudformation describe-stacks` status, LastUpdatedTime, GitCommit | 0 | stack-status-redeploy.txt |
| CMD-STACK-OUTPUTS | 0 | stack-outputs-redeploy.txt; ApiUrl unchanged |
| CMD-DEPLOYED-COMMIT | 0 | deployed-commit-redeploy.txt; tag equals 66aa531; both backend trees `3ba68085287cc5acd9aafd914645fc00a8a606c1` |
| CMD-DEPLOYED-SMOKE | 0 | deployed-smoke-redeploy.txt; deployed-smoke-redeploy.xml; 4 passed, 22 deselected |
| CMD-DEPLOYED-TESTS | 0 | deployed-tests-redeploy.txt; deployed-redeploy.xml; 26 passed |
| CMD-STUB-SCAN | 1 | stub-scan-redeploy.txt; finding, not fixed |
| `bash tools/ci/gate.sh docs` | 0 | gate-docs-redeploy.txt |
| `TMPDIR=/var/tmp/az-l03r bash tools/ci/gate.sh hygiene` | 0 | gate-hygiene-redeploy.txt |

Plan command text:

- CMD-STACK-OUTPUTS: `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].[OutputKey,OutputValue]' --output json`, with `--region us-east-2`.
- CMD-DEPLOYED-COMMIT: `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --query 'Stacks[0].Tags[?Key==`GitCommit`].Value' --output text && git rev-parse 66aa5314b2a3f3f56b066e338b5f223db7bd0db2:backend HEAD:backend`, with `--region us-east-2`.
- CMD-DEPLOYED-SMOKE: `AFC_DEPLOYED_API_URL=https://le3r79003f.execute-api.us-east-2.amazonaws.com python3.12 -m pytest backend/tests/deployed -k link -v -rs --tb=short --junitxml=docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L03/deployed-smoke-redeploy.xml`.
- CMD-DEPLOYED-TESTS: same URL and flags, without `-k link`, junitxml `deployed-redeploy.xml`.
- CMD-STUB-SCAN: `git grep -n -e AFC-STUB -e NotImplementedError -- backend/src tv-app/app/src/main`.

## Boundaries and remaining work

All mutation stayed on stack afc-dev in us-east-2 with profile afc-dev, and only changeset `samcli-deploy1792174771`. No stack or changeset delete. No IAM user, billing, secret value, SSM read, other stack, other region, product code, template, or samconfig change. No branch switch, push, PR or issue mutation.

Remaining: the stub-scan finding above. #99 is TV app only and was not deployed by SAM. The deployed suite has no new player-stats or G3-wire case beyond the existing panel cases, which passed.

OCR remains required at independent review and is NOT_RUN by this worker. Reverify is not applicable: no compiled-binary claim. BRAN is unavailable: no native policy. No full phase or SEIT closure is claimed.
