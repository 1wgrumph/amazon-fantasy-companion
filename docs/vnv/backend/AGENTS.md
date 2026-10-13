# Backend review guidance

## Scope

Repository-relative paths: `backend/**` and `docs/vnv/backend/**`. The AWS SAM
application: API (`backend/src/api/openapi.yaml`), store, pipeline, panel and
provider resolver modules, `template.yaml`, replay fixtures and the unit and
deployed tests.

## Tools

- `tools/ci/gate.sh backend docs hygiene`: pytest and SAM template validation
  under `backend/`.
- `sam validate --template-file backend/template.yaml --lint` and
  `cfn-lint backend/template.yaml`.
- `python3.12 -m pytest <test_paths> -v` for named tests (red/green receipts).
- `python3.12 -m pytest backend/tests/deployed -v` against the dev stack, only
  under the `aws-afc-dev` lease.
- `bash tools/ci/coverage/backend.sh <base_sha> <evidence_dir>` and
  `bash tools/ci/mutation/backend.sh <base_sha> <evidence_dir>` where declared.

P2-G01 adds the `backend` area. Until it lands, `gate.sh backend` is a usage
error (exit 2), and a missing Python 3.12, SAM CLI or cfn-lint is GAP (exit 3),
never PASS. `PASS no backend/ tree` closes no product requirement. See the
[index](../AGENTS.md) for exit codes and evidence rules.

## Review Focus

- TDD pairs: the red receipt fails on a named behavioral assertion; the same
  test IDs and hashes pass on the product slice.
- Contracts: OpenAPI, template, store and pipeline, provider registry and
  replay fixtures change only under the `backend-template` lease, and frozen
  contract paths stay unchanged after their contract merge.
- Fixtures: replay fixtures keep their provenance and append later captures as
  new sequence files; no fixture is rewritten in place.
- Deployed evidence binds to the stack's `GitCommit` tag and the candidate
  `backend/` tree. A deploy, smoke run or stack read is not a unit-test PASS.
- Security: secrets live in SSM and are read by role; none appear in code,
  templates, `samconfig.toml`, fixtures, logs or evidence. Least-privilege IAM.
- Supply chain: new Python dependencies, SAM CLI and cfn-lint versions carry a
  scan receipt before first use.

## Findings target

GitHub issues in `1wgrumph/amazon-fantasy-companion`, label `vnv`, through the
issue-label policy tool under the [index](../AGENTS.md) rules. Defects found
during work route to bug triage and are fixed in the current round.
