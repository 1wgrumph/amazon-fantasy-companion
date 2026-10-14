# P2-L02 deployment receipt

Outcome: **CONTRACT_FAILURE**. Deployment and deployed smoke are NOT_RUN.

Lifecycle AFC-2026-10-11 Phase 2; issue #29; milestone M05; authority AUTH-AFC-2026-10-12-P2-001 and the explicit 2026-10-14 dispatch. Branch `afc/p2-l02`; baseline and intended deploy SHA `75afca022f967945a70bf715beb2a7c98e65ed9d`. Backend tree `7c0a94484ed1ace448fbefdf3dcae0412f13134d`. Dispatch route Codex CLI / GPT-6.1 Sol / medium under DEC-AFC-SD-043/045; no route switch or live profile read. Initial checkout clean and matches dispatched branch/revision. No separate checkout lease artifact was supplied for this slice; the current owner dispatch is the checkout binding. BRAN unavailable (no native policy); repository discovery used. Neither repository-root AGENTS.md nor CLAUDE.md exists at this revision; supplied session and workspace instructions apply.

Next action for the orchestrator: supply an explicitly authorized existing artifact bucket and an amended exact deploy command disabling S3 auto-resolution, or amend authority to cover SAM-managed infrastructure. No config or product repair was attempted. The worker does not choose either alternative.

## Blocker

`backend/samconfig.toml` sets `resolve_s3 = true` without an `s3_bucket`. Installed SAM help states this creates a managed default S3 bucket. AWS documents the managed deployment infrastructure under the `aws-sam-cli-managed-default` naming. This provisioning is outside the dispatch's afc-dev-only stack boundary. The deploy was stopped before invocation, so there is no changeset to review or execute, no mutation, no deployment exit code, and no assertion that the managed stack exists or is absent. No other stack was queried.

References: [AWS deployment guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/using-sam-cli-deploy.html), [SAM deploy reference](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html). Installed CLI evidence: `deploy-preflight.txt`.

## Commands and exits

All AWS commands use profile `afc-dev` and region `us-east-2`. PATH includes the authorized backend-tests venv. Logs replace home paths with `<home>` and every twelve-digit numeric sequence with `<acct>`. No credential retrieval, account/config dump, or token output occurred. Command processes were bounded to at most 900 seconds.

| Command | Exit/result | Evidence |
| --- | --- | --- |
| `git branch --show-current`; `git rev-parse HEAD`; `git status --short` | 0 each; expected branch/SHA, clean | dispatch checkout check; build-identity.txt binds SHA |
| `sam --version`; `aws --version`; `python3.12 --version` | 0 each | build-identity.txt |
| `(cd backend && sam validate --region us-east-2)` | 0 | validate.txt |
| `(cd backend && sam build)` | 0 | build.txt; build-identity.txt template/config digests |
| `sam deploy --help` | 0 | deploy-preflight.txt (relevant excerpt) |
| `(cd backend && sam deploy --config-env default --profile afc-dev --region us-east-2 --tags GitCommit=75afca022f967945a70bf715beb2a7c98e65ed9d)` | NOT_RUN: contract boundary | deploy-preflight.txt |
| `aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --region us-east-2 --query 'Stacks[0].{Status:StackStatus,ApiUrl:Outputs[?OutputKey==`ApiUrl`].OutputValue,GitCommit:Tags[?Key==`GitCommit`].Value}' --output json` | 254: ValidationError, stack does not exist | stack-status.txt |
| `python3.12 -m pytest backend/tests/deployed -k link -v --junitxml=<evidence_dir>/deployed-smoke.xml` | NOT_RUN: no deployed stack; 0 executed, no pass/skip claim | this receipt |
| Deployed profile smoke (`backend/tests/deployed/api/test_profile.py`) | NOT_RUN: no deployed stack; 0 executed | this receipt |
| CMD-DEPLOYED-COMMIT tag/tree comparison | NOT_RUN: no deployed stack/tag | local backend tree only in build-identity.txt |
| Stack resource inventory | NOT_RUN: afc-dev does not exist | stack-status.txt |
| `bash tools/ci/gate.sh` (twice, second run with completed receipt) | 0 each; 61 CI tests and 158 backend tests passed each run | gate.txt, gate-final.txt |

Discovery reads also found absent AGENTS.md/CLAUDE.md (cat exit 1), absent backend/README glob (rg exit 2), and no installed SAM Python source match (rg exit 1). These are discovery gaps, not product failures. Official pinned-source web fetches were unavailable; no upstream software was downloaded or executed for this inspection.

## Acceptance to evidence

| Acceptance | Result | Evidence |
| --- | --- | --- |
| 1. Validate/build exit 0 | PASS (local preparation only) | validate.txt, build.txt, build-identity.txt |
| 2. Reviewed changeset, afc-dev deploy exit 0 | NOT_RUN / blocked | deploy-preflight.txt |
| 3. ApiUrl and COMPLETE stack | NOT_MET: no stack, no ApiUrl, no deployed SHA | stack-status.txt |
| 4. Deployed link/profile smoke | NOT_RUN, zero executed | no deployed endpoint |
| 5. Sanitized receipt, resources and cost note | Partial: receipt present; no stack inventory possible | this receipt and text logs |
| 6. Gate and local evidence commit | Final exit/commit reported in worker return | gate-final.txt; Git commit |

## Cost boundary

Not established that all resources are free tier eligible. Inspected the source template only: HTTP API, three Python Lambda functions, six DynamoDB PAY_PER_REQUEST tables with an index/stream, EventBridge Scheduler with schedule DISABLED, IAM service roles, and seven-day CloudWatch log groups. SSM SecureString entries are references to owner-created parameters. SAM additionally needs an S3 artifact bucket. The template's Free-plan wording is a claim, not account eligibility proof. No billing/account query was authorized or made; no payment/plan change or paid prompt was accepted. No resources were created by this slice. Service quotas, free-tier credit balance, usage and account eligibility remain unverified. SEIT-AFC-PR-054 and SEIT-RISK-AFC-P2-07 are not closed by this receipt.

## Proof rows and later obligations

- SEIT-AFC-P2-DX-01: supporting developer feedback below supplied; aggregate closure stays with P2-SCR1.
- SEIT-AFC-P2-PATH-01: local hygiene gate is supporting evidence only; aggregate closure remains P2-G01.
- SEIT-AFC-P2-LAND-01 and SEIT-AFC-P2-REL-01: not satisfied; orchestrator owns independent review, landing and changelog under P2-R5 aggregate closure. Worker does not push or access GitHub.
- SEIT-AFC-P2-REV-01: OCR delegate mode remains required at independent review; NOT_RUN here. Reverify: not applicable — no compiled-binary attribute claim. Aggregate closure remains P2-L05.
- SEIT-AFC-PR-038: NOT_RUN. Full registered demonstration needs real stick plus owner phone/browser action; no stick is available. HTTP smoke cannot close it.
- SEIT-AFC-PR-054 and SEIT-RISK-AFC-P2-07: NOT_RUN for deployed eligibility/inventory; P2-L03 closure remains. The boundary was preserved locally by stopping before provisioning.
- SEIT-RISK-AFC-P2-10: no route change or fallback occurred; no independent aggregate assurance claim.

No full SEIT proof row is claimed closed by this blocked run. A deploy retry still needs the corrected infrastructure contract, authorized owner linking setup, deployed smoke and account eligibility evidence. Frozen `-k link` selects the link-flow module but excludes the separate profile module; mapped expiry/replay and owner phone confirmation also require their registered demonstration evidence.

## developer_feedback

- AFC-L02-OBS-001: SAM artifact provisioning conflicts with the one-stack execution contract. Evidence: backend/samconfig.toml, installed SAM 1.169.0 help excerpt in deploy-preflight.txt, official AWS guide. This is a dispatch prerequisite gap, not a reproduced product bug.
- AFC-L02-OBS-002: Frozen CMD-DEPLOYED-SMOKE uses `-k link`; separate deployed profile tests require an additional explicit invocation. Existing deployed link module has four cases; full expiry/replay and owner phone demonstration remain outside those four HTTP cases. Evidence: seit.json command entry and backend/tests/deployed/{device_auth/test_link_flow.py,api/test_profile.py,conftest.py}. No code/test changes made.

Tools exercised: Git, Python, SAM 1.169.0, AWS CLI 2.38.0, repository gate, official AWS documentation lookup. Output hashes are in log-digests.txt. All changes stay under this evidence directory; build artifacts remain ignored and uncommitted.
