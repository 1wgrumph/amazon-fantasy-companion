# P2-L03 interim deployment receipt

Outcome: **OWNER_DECISION_REQUIRED**. Label: interim (c194dee). Deploy was not executed. Light Implementer return: **OWNER_DECISION_REQUIRED**. This is author execution evidence, not independent review or complete later-slice acceptance.

Issue #41 stays open. Route: Cursor Agent / Grok 4.7 / high. Checkout `amazon-fantasy-companion-p2-l03`, branch `afc/p2-l03`, HEAD `c194deefe0273f76d4a1e430de94a4c7a163aad2`. Local `origin/main` is `d2208908e856809357885bab3561ddfb80e495e3`, three docs-only commits ahead. Both commits have backend tree `841926d39a111803203383f46ad6d63133583c11`. This run deploys neither past c194dee nor a different backend tree.

ApiUrl unchanged: https://le3r79003f.execute-api.us-east-2.amazonaws.com

Live deployed SHA remains `2d973bd66182364a69b5a3088286e88c08f1107d`. Live `describe-stacks`: **UPDATE_COMPLETE**, last updated 2026-10-15T01:10:30.108000+00:00, GitCommit tag equals that SHA. SAM 1.169.0, AWS CLI 2.38.0, Python 3.12.3. No tools installed.

## Changeset reviewed before execution

Changeset `samcli-deploy1792162052`: **0 Add, 21 Modify, 0 Remove**. Stack tag in the changeset is GitCommit `c194deefe0273f76d4a1e430de94a4c7a163aad2`. The full Changes array is in changeset.txt. The classification is in changeset-review.txt.

Answered `n`. One IAM permission removal:

- `ApiFunctionRole` policy path `/Properties/Policies/1`, AttributeChangeType `Remove`. The removed policy is `ApiFunctionRolePolicy1`, action `ssm:GetParameter`, on the YahooClientSecretParameter and YahooTokenParameter ARNs. The live stack template already grants that action on both `ApiFunctionRole` and `PolicyFunctionRole`. The changeset template keeps the `PolicyFunctionRole` grant and does not change it. ApiFunction loses `ssm:GetParameter`.

Checked and not used as the stop:

- All six DynamoDB tables are Modify, Replacement False, tags only. No SSM parameter resource is in the changeset. No resource Remove. No Replacement True.
- The SAM summary table printed `PolicyFunctionEventStream` Replacement Conditional. `describe-change-set --include-property-values` says Replacement False, scope Tags, RequiresRecreation Never, GitCommit tag only.
- Permission additions only: ApiFunctionRole gains `dynamodb:UpdateItem` on ProfilesTable; IngestFunctionRole gains `dynamodb:Scan` on ProfilesTable; PolicyFunctionRole gains `dynamodb:Scan` on LineupsTable.
- ApiFunction, IngestFunction and PolicyFunction change their code S3 key, Replacement False.

The changeset remains CREATE_COMPLETE / AVAILABLE. It was not executed and must not be executed.

## Smoke counts and suite

CMD-DEPLOYED-SMOKE and CMD-DEPLOYED-TESTS are **NOT_RUN**. Deploy did not execute, so nothing was counted as passing. No deselected case is counted as passing.

CMD-STUB-SCAN exit 1. Three matches, recorded in stub-scan.txt and not fixed here: `backend/src/api/handler.py` line 5 (docstring mentions AFC-STUB) and line 37 (`except NotImplementedError`), and `tv-app` `WatchActivity.kt` line 6 (AFC-STUB comment for P2-A04).

## Commands and exit codes

Repo-root commands unless noted. AWS commands used `--profile afc-dev --region us-east-2`, with AWS_PAGER empty. `sam` was on PATH via `$HOME/.local/bin`. Command streams redacted twelve-digit sequences as `<acct>` and local home segments as `<home>` before evidence persistence. Credentials and secret values were never printed or retrieved from SSM.

| Command | Exit | Evidence |
| --- | --- | --- |
| `git grep -n -e AFC-STUB -e NotImplementedError -- backend/src tv-app/app/src/main; afc_rc=$?; test "$afc_rc" -eq 1` | 1 | stub-scan.txt; finding, not fixed |
| `(cd backend && timeout --foreground 1500 sam build)` | 0 | build.txt |
| `(cd backend && timeout --foreground 1500 sam deploy --config-env default --profile afc-dev --region us-east-2 --tags GitCommit=c194deefe0273f76d4a1e430de94a4c7a163aad2)` | 0 after answering `n`; stack not updated | deploy.txt |
| `aws cloudformation describe-change-set --stack-name afc-dev --change-set-name samcli-deploy1792162052 --include-property-values --profile afc-dev --region us-east-2 --output json` | 0 | changeset.txt |
| `aws cloudformation describe-stacks` status query, before and after the decline | 0 | stack-status.txt |
| CMD-STACK-OUTPUTS on the unchanged stack | 0 | stack-status.txt; ApiUrl unchanged |
| CMD-DEPLOYED-COMMIT | NOT_RUN | deploy not executed |
| CMD-DEPLOYED-SMOKE | NOT_RUN | deploy not executed |
| CMD-DEPLOYED-TESTS | NOT_RUN | deploy not executed |
| `TMPDIR=/var/tmp/az-p2-l03 bash tools/ci/gate.sh hygiene` | 0 | gate-hygiene.txt; first run on the default temp exited 1 with Errno 122 |
| `bash tools/ci/gate.sh docs` | 0 | gate-docs.txt |

Plan command CMD-SAM-DEPLOY does not include `--region`. This run added `--region us-east-2` from the packet's AWS convention. `samconfig.toml` names stack `afc-dev` and sets `confirm_changeset = true`.

The first `gate.sh hygiene` exited 1: a unittest copy hit `OSError: [Errno 122] Disk quota exceeded` on the default temp. The retry set `TMPDIR` to `/var/tmp/az-p2-l03` on the root filesystem and exited 0. `gate.sh docs` exited 0. The committed hygiene log is the passing retry.

## Boundaries and remaining work

All inspection stayed on stack afc-dev in us-east-2 with profile afc-dev. No stack resource was deleted or replaced. No IAM user, billing, secret value, other stack, other region, product code, template, or samconfig change. No branch switch, push, PR or issue mutation. The unexecuted changeset `samcli-deploy1792162052` is still AVAILABLE.

The final L03 redeploy still has to cover: an owner decision on the ApiFunction `ssm:GetParameter` removal before any execute; R1 (player-stats panel) and P2-X06 lineup_source, which are still in flight; the stub-scan finding; deployed smoke and the deployed suite with every NOT_RUN or deselected case listed and not counted as passing. Issue #41 stays open. B04, B05, B06 and B07 are merged. The three docs commits on local origin/main do not change the backend tree.

OCR remains required at independent review and is NOT_RUN by this worker. Reverify is not applicable: no compiled-binary claim. BRAN is unavailable: no native policy. No full phase or SEIT closure is claimed.
