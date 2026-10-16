# P2-L03 interim deployment receipt

Outcome: **PASS** for this execute packet. Label: interim (c194dee). Light Implementer return: **CANDIDATE_READY**. This is author execution evidence, not independent review or complete later-slice acceptance.

Issue #41 stays open. Route: Cursor Agent / Grok 4.7 / high. Checkout `amazon-fantasy-companion-p2-l03`, branch `afc/p2-l03`, evidence parent `c10ec4fa20566a5462ef4fb1072b30d30a703696`. Deployed commit `c194deefe0273f76d4a1e430de94a4c7a163aad2`. Local `origin/main` is `d2208908e856809357885bab3561ddfb80e495e3`, three docs-only commits ahead. Both commits have backend tree `841926d39a111803203383f46ad6d63133583c11`.

ApiUrl: https://le3r79003f.execute-api.us-east-2.amazonaws.com

Live `describe-stacks`: **UPDATE_COMPLETE**, LastUpdatedTime `2026-10-16T15:10:44.013000+00:00`, GitCommit tag `c194deefe0273f76d4a1e430de94a4c7a163aad2`. SAM 1.169.0, AWS CLI 2.38.0, Python 3.12.3, pytest 8.4.2. No tools installed.

lineup_source: manual (X06 VERDICT SHA pending from session amazon-fantasy-companion-08).

## Owner decision

OWNER DECISION (2026-10-16, in the orchestrating session): approved executing changeset `samcli-deploy1792162052` on stack afc-dev (us-east-2), including the ApiFunctionRole removal of `ssm:GetParameter` on the Yahoo client-secret and token parameters. Basis: the removal comes from merged PR #68 (a0c86eb, "limit API secrets access"); no backend/src code calls SSM; the PolicyFunctionRole grant stays.

The earlier interim commit `c10ec4f` refused this changeset pending the owner. This run executed that same changeset after the decision above.

## Changeset comparison before execution

`describe-change-set --include-property-values` for `samcli-deploy1792162052` was compared with the saved `changeset.txt` before execute. Live status **CREATE_COMPLETE**, execution **AVAILABLE**. The Changes array is identical to the saved array after the same `<acct>` redaction of 12-digit ARN account ids. Every other top-level field matches. Resource actions remain **0 Add, 21 Modify, 0 Remove**, Replacement False on all 21. The changeset tag is GitCommit `c194deefe0273f76d4a1e430de94a4c7a163aad2`. The comparison is in changeset-compare.txt. The classification in changeset-review.txt still describes this array, including the approved ApiFunctionRole `ssm:GetParameter` removal. No drift. Execute proceeded.

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

## Commands and exit codes

Repo-root commands unless noted. AWS commands used `--profile afc-dev --region us-east-2`, with AWS_PAGER empty. `python3.12` for pytest was the L02 backend-tests interpreter on PATH (`$HOME/.local/share/afc-tools/backend-tests/bin`). Command streams redacted home segments as `<home>` before evidence persistence. Credentials, SSM values, and secret values were never printed or retrieved.

| Command | Exit | Evidence |
| --- | --- | --- |
| `aws cloudformation describe-change-set --stack-name afc-dev --change-set-name samcli-deploy1792162052 --include-property-values --profile afc-dev --region us-east-2 --output json` | 0 | changeset-compare.txt; Changes identical to changeset.txt |
| `aws cloudformation execute-change-set --change-set-name samcli-deploy1792162052 --stack-name afc-dev --profile afc-dev --region us-east-2` | 0 | execute-change-set.txt; 2026-10-16T15:10:44Z |
| `aws cloudformation wait stack-update-complete --stack-name afc-dev --profile afc-dev --region us-east-2` | 0 | execute-change-set.txt; 2026-10-16T15:12:21Z |
| `aws cloudformation describe-stacks` status, LastUpdatedTime, GitCommit | 0 | stack-status-execute.txt |
| CMD-STACK-OUTPUTS | 0 | stack-outputs.txt; ApiUrl unchanged |
| CMD-DEPLOYED-COMMIT | 0 | deployed-commit.txt; tag equals c194dee; both backend trees `841926d39a111803203383f46ad6d63133583c11` |
| CMD-DEPLOYED-SMOKE | 0 | deployed-smoke.txt; deployed-smoke.xml; 4 passed, 22 deselected |
| CMD-DEPLOYED-TESTS | 0 | deployed-tests.txt; deployed.xml; 26 passed |
| `TMPDIR=/var/tmp/az-p2-l03 bash tools/ci/gate.sh hygiene` | 0 | gate-hygiene-execute.txt |
| `bash tools/ci/gate.sh docs` | 0 | gate-docs-execute.txt |

Plan command text, plus the L02 conventions this packet requires:

- CMD-STACK-OUTPUTS: `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].[OutputKey,OutputValue]' --output json`, with `--region us-east-2`.
- CMD-DEPLOYED-COMMIT: `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --query 'Stacks[0].Tags[?Key==`GitCommit`].Value' --output text && git rev-parse c194deefe0273f76d4a1e430de94a4c7a163aad2:backend d2208908e856809357885bab3561ddfb80e495e3:backend`, with `--region us-east-2`. The second tree is origin/main, which the packet states shares the deployed backend tree.
- CMD-DEPLOYED-SMOKE: `AFC_DEPLOYED_API_URL=https://le3r79003f.execute-api.us-east-2.amazonaws.com python3.12 -m pytest backend/tests/deployed -k link -v -rs --tb=short --junitxml=docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L03/deployed-smoke.xml`. Plan text is `-k link` plus junitxml. `-rs --tb=short` and `AFC_DEPLOYED_API_URL` are the L02 conventions. Without the URL every deployed case skips.
- CMD-DEPLOYED-TESTS: same URL and flags, without `-k link`, junitxml `deployed.xml`.

The prior refusal run (build exit 0, deploy answered `n`, stub-scan exit 1, hygiene exit 0 on `TMPDIR=/var/tmp/az-p2-l03`, docs exit 0) stays in build.txt, deploy.txt, changeset.txt, changeset-review.txt, stub-scan.txt, stack-status.txt, gate-hygiene.txt and gate-docs.txt. CMD-STUB-SCAN was not re-run. Its recorded finding is unchanged: `backend/src/api/handler.py` line 5 (docstring mentions AFC-STUB) and line 37 (`except NotImplementedError`), and `tv-app` `WatchActivity.kt` line 6 (AFC-STUB comment for P2-A04).

## Boundaries and remaining work

All mutation stayed on stack afc-dev in us-east-2 with profile afc-dev, and only changeset `samcli-deploy1792162052`. No other changeset, no new `sam deploy`, no stack or changeset delete. No IAM user, billing, secret value, SSM read, other stack, other region, product code, template, or samconfig change. No branch switch, push, PR or issue mutation.

The final L03 redeploy still has to cover: R1 (player-stats panel), the P2-X06 verdict SHA, and the stub-scan finding. Issue #41 stays open. B04, B05, B06 and B07 are merged. The three docs commits on local origin/main do not change the backend tree.

OCR remains required at independent review and is NOT_RUN by this worker. Reverify is not applicable: no compiled-binary claim. BRAN is unavailable: no native policy. No full phase or SEIT closure is claimed.
