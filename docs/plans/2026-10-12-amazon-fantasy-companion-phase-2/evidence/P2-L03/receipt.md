# P2-L03 final deployment receipt

Outcome: **PASS** for this final redeploy packet. Label: final (`af0e0ac`). Light Implementer return: **CANDIDATE_READY**. This is author execution evidence, not independent review or complete later-slice acceptance.

Issue #41 stays open. Route: Cursor Agent / Grok 4.7 / high. Checkout `amazon-fantasy-companion-p2-l03`, branch `afc/p2-l03`. Interim receipt commit `515690df0857ab629eafa4eccef8fb17d46c6e24` stays in history (c194dee deployed at 15:10:44Z). This run merged `origin/main` and deployed that head.

Merge commit `f825d64586d8e47a9fed277c3521de7cbda3fffe`. Parents `515690df0857ab629eafa4eccef8fb17d46c6e24` and `af0e0ac1520ce5b9e7de186fd83df23bc92d6a5e`. Deployed commit `af0e0ac1520ce5b9e7de186fd83df23bc92d6a5e` (merge of #95, R1 per-player ESPN boxscore stats). Backend tree of `HEAD` and of `af0e0ac` are both `aa7333fe57c9f52b001551a0e91d5ed961b6f229`. `git diff --exit-code af0e0ac -- backend` exited 0.

ApiUrl: https://le3r79003f.execute-api.us-east-2.amazonaws.com

Live `describe-stacks`: **UPDATE_COMPLETE**, LastUpdatedTime `2026-10-16T15:49:42.403000+00:00`, GitCommit tag `af0e0ac1520ce5b9e7de186fd83df23bc92d6a5e`. SAM 1.169.0, AWS CLI 2.38.0, Python 3.12.3, pytest 8.4.2. No tools installed.

lineup_source: manual. P2-X06's Yahoo route fails (Yahoo 403 for unapproved apps). Its VERDICT commit is in progress on branch `afc/p2-x06`. There is no deploy parameter for the lineup source.

## Changeset reviewed before execution

Changeset `samcli-deploy1792165669` was created with `sam deploy --no-execute-changeset` and inspected with `describe-change-set --include-property-values` before execute. Live status **CREATE_COMPLETE**, execution **AVAILABLE**. Resource actions **1 Add, 21 Modify, 0 Remove**. The changeset tag is GitCommit `af0e0ac1520ce5b9e7de186fd83df23bc92d6a5e`. The saved array is changeset-final.txt after `<acct>` redaction. The classification is changeset-review-final.txt.

Add: `PlayerStatsTable` (`AWS::DynamoDB::Table`, PAY_PER_REQUEST, hash key `athleteId`). Expected.

IAM changes are additions only. No statement, action, or resource was removed.

- `ApiFunctionRole`: added Allow `dynamodb:GetItem` on the new table.
- `IngestFunctionRole`: added Allow `dynamodb:PutItem` on the new table.
- `PolicyFunctionRole` and `IngestScheduleRole`: GitCommit tag only.

Existing DynamoDB tables (Alerts, Events, Lineups, Links, Panels, Profiles) are Modify, Replacement=False, scope Tags only. No SSM parameter resource is in the changeset. SSM values were not read. No resource Action Remove. No Replacement=True. No Replacement=Conditional on a stateful resource.

`PolicyFunctionEventStream`: the SAM summary table printed Replacement Conditional. `describe-change-set` with property values says Replacement=False, scope Tags, RequiresRecreation Never. It is an event-source mapping, not a DynamoDB table or SSM parameter.

Execute proceeded. `execute-change-set` exited 0 at 2026-10-16T15:49:42Z. `wait stack-update-complete` exited 0 at 2026-10-16T15:51:13Z.

## Smoke counts and suite

CMD-DEPLOYED-SMOKE: **26 collected, 4 selected, 4 passed, 0 failed, 0 skipped, 22 deselected**, exit 0. The 22 deselections are the `-k link` filter. None is counted as a smoke pass.

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

CMD-DEPLOYED-TESTS: **26 collected, 26 selected, 26 passed, 0 failed, 0 skipped, 0 deselected**, exit 0. No NOT_RUN case in this run. No deployed failure to record. The 22 smoke deselections passed here as selected cases. That does not relabel them as smoke passes.

The deployed suite has no player-stats case. Creating `PlayerStatsTable` is not asserted by these 26 cases.

## Stub scan

CMD-STUB-SCAN was re-run on this tree. `git grep` exited 0 because it found matches. The wrapper `test` that the scan is empty exited 1. Finding, not fixed here:

- `backend/src/api/handler.py` line 5 (docstring mentions AFC-STUB)
- `backend/src/api/handler.py` line 37 (`except NotImplementedError`)
- `tv-app` `WatchActivity.kt` line 6 (AFC-STUB comment for P2-A04)

No other AFC-STUB or NotImplementedError match in `backend/src` or `tv-app/app/src/main`.

## Commands and exit codes

Repo-root commands unless noted. AWS commands used `--profile afc-dev --region us-east-2`, with AWS_PAGER empty. `python3.12` for pytest was the L02 backend-tests interpreter on PATH (`$HOME/.local/share/afc-tools/backend-tests/bin`). `TMPDIR=/var/tmp/az-p2-l03`. Command streams redacted home segments as `<home>` and twelve-digit sequences as `<acct>` before evidence persistence. Credentials, SSM values, and secret values were never printed or retrieved.

| Command | Exit | Evidence |
| --- | --- | --- |
| `git fetch origin && git merge --no-edit origin/main` | 0 | merge-final.txt |
| `timeout --foreground 1500 sam build` (backend) | 0 | build-final.txt |
| `sam deploy --config-env default --profile afc-dev --region us-east-2 --no-execute-changeset --tags GitCommit=af0e0ac1520ce5b9e7de186fd83df23bc92d6a5e` | 0 | deploy-final.txt; changeset `samcli-deploy1792165669` |
| `aws cloudformation describe-change-set --include-property-values` | 0 | changeset-final.txt; changeset-review-final.txt |
| `aws cloudformation execute-change-set --change-set-name samcli-deploy1792165669 --stack-name afc-dev` | 0 | execute-change-set-final.txt; 2026-10-16T15:49:42Z |
| `aws cloudformation wait stack-update-complete --stack-name afc-dev` | 0 | execute-change-set-final.txt; 2026-10-16T15:51:13Z |
| `aws cloudformation describe-stacks` status, LastUpdatedTime, GitCommit | 0 | stack-status-final.txt |
| CMD-STACK-OUTPUTS | 0 | stack-outputs-final.txt; ApiUrl unchanged |
| CMD-DEPLOYED-COMMIT | 0 | deployed-commit-final.txt; tag equals af0e0ac; both backend trees `aa7333fe57c9f52b001551a0e91d5ed961b6f229` |
| CMD-DEPLOYED-SMOKE | 0 | deployed-smoke-final.txt; deployed-smoke-final.xml; 4 passed, 22 deselected |
| CMD-DEPLOYED-TESTS | 0 | deployed-tests-final.txt; deployed-final.xml; 26 passed |
| CMD-STUB-SCAN | 1 | stub-scan-final.txt; finding, not fixed |
| `bash tools/ci/gate.sh docs` | 0 | gate-docs-final.txt |
| `TMPDIR=/var/tmp/az-p2-l03 bash tools/ci/gate.sh hygiene` | 0 | gate-hygiene-final.txt |

Plan command text, plus the L02 conventions this packet requires:

- CMD-STACK-OUTPUTS: `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].[OutputKey,OutputValue]' --output json`, with `--region us-east-2`.
- CMD-DEPLOYED-COMMIT: `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --query 'Stacks[0].Tags[?Key==`GitCommit`].Value' --output text && git rev-parse af0e0ac1520ce5b9e7de186fd83df23bc92d6a5e:backend HEAD:backend`, with `--region us-east-2`. Both trees are the deployed backend tree.
- CMD-DEPLOYED-SMOKE: `AFC_DEPLOYED_API_URL=https://le3r79003f.execute-api.us-east-2.amazonaws.com python3.12 -m pytest backend/tests/deployed -k link -v -rs --tb=short --junitxml=docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L03/deployed-smoke-final.xml`. Plan text is `-k link` plus junitxml. `-rs --tb=short` and `AFC_DEPLOYED_API_URL` are the L02 conventions.
- CMD-DEPLOYED-TESTS: same URL and flags, without `-k link`, junitxml `deployed-final.xml`.
- CMD-STUB-SCAN: `git grep -n -e AFC-STUB -e NotImplementedError -- backend/src tv-app/app/src/main`.

The interim refusal logs stay in build.txt, deploy.txt, changeset.txt, changeset-review.txt, stub-scan.txt, stack-status.txt, gate-hygiene.txt and gate-docs.txt. The interim execute logs stay in execute-change-set.txt, stack-status-execute.txt, deployed-smoke.txt, deployed-tests.txt, deployed-smoke.xml, deployed.xml, gate-hygiene-execute.txt and gate-docs-execute.txt.

## Boundaries and remaining work

All mutation stayed on stack afc-dev in us-east-2 with profile afc-dev, and only changeset `samcli-deploy1792165669`. No stack or changeset delete. No IAM user, billing, secret value, SSM read, other stack, other region, product code, template, or samconfig change. No branch switch, push, PR or issue mutation.

Remaining: the stub-scan finding above; lineup_source stays manual until the X06 verdict; the deployed suite does not cover player stats. Issue #41 stays open. Draft PR #96 is unchanged by this worker.

OCR remains required at independent review and is NOT_RUN by this worker. Reverify is not applicable: no compiled-binary claim. BRAN is unavailable: no native policy. No full phase or SEIT closure is claimed.
