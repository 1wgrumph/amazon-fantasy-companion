# Developer feedback review guidance

## Scope

Repository-relative paths: `docs/developer-feedback/**`,
`docs/vnv/developer-feedback/**`. S08 owns the running observation log;
submission-time assembly belongs to Phase 2.

## Tools

- `tools/ci/gate.sh docs hygiene`

The S09 gate checks document structure/links and sanitization; it does not prove
observation completeness or accuracy. Inspect the schema and evidence manually
against AC-AFC-DX-02 and AC-AFC-DX-04. See the [index](../AGENTS.md) for gap and
candidate-bound evidence rules.

## Review Focus

- Developer feedback: `docs/developer-feedback/observations.md` has Observations
  and Feature requests tables, retaining DX-001..DX-007 and every Phase 1
  observation as one complete row each.
- Observations carry ID, timestamp, reporting role, task or packet, tool/API/SDK,
  version, device/OS, evidence and classification.
- Product feedback covers used for, what worked well, what needs work, onboarding
  from zero to hello world, would build again (Yes/No and why), and AWS services
  used and how (only for AWS tools).
- Friction entries carry task attempted, steps taken, expected result, actual
  result, severity (Blocker/Major/Minor/None), workaround and actionable suggestion.
- Feature requests carry ID, tool, description, why it matters to this project,
  and priority (Critical/Important/Nice-to-have).
- Every cell holds evidence, `n/a` or `unknown`; never invent measurements or
  leave cells blank. Preserve positive experiences as well as friction.
- Owner boundary: the log is intended for public use. Remove secrets, account
  details, private paths and proprietary material before committing. Recording
  feedback grants no authority to submit it externally or publish a release.

## Findings target

GitHub issues in `1wgrumph/amazon-fantasy-companion`, label `vnv`, through the
issue-label policy tool under the [index](../AGENTS.md) rules. Keep developer
observations in the S08 log; reproducible review defects need sanitized evidence
and a duplicate check before authorized filing. Unavailable filing is a gap.
