# Verification and validation guidance

## Scope

Phase 1 guidance for AC-AFC-VNV-01 and DES-AFC-VNV. Read the area files
in this order; the first matching repository-relative scope owns a path:

1. [CI/CD](ci-cd/AGENTS.md): gates, hooks, workflows and general documentation.
2. [Specifications](spec/AGENTS.md): section sources and vendored spec tools.
3. [Developer feedback](developer-feedback/AGENTS.md): the observation log.

The CI/CD scope excludes the paths owned by the other two areas. Report
unmatched paths as `(unmapped)` rather than inventing coverage. Product areas
(`tv-app`, `backend`, `device-integration`) are added in Phase 2 when they exist.

## Tools

The area files list commands from CONTRACT-AFC-GATE, run from the repository
root. The gate and spec kit are delivered by S09 and S42; their absence before
those slices land is a typed gap, never passing evidence. Guidance does not
claim those commands have run.

The gate accepts `--list`, `--changed[=<base>]` and area names. No area selects
all areas; changed mode always includes hygiene and defaults to the merge base
with `origin/main`. Exit codes: 0 PASS, 1 check failure, 2 usage error, 3 required
tool missing (GAP). Each area prints `gate: <area>: PASS|FAIL|GAP <detail>`.

## Review Focus

- Bind results to the exact candidate SHA, diff scope, command, exit code and
  output. Author checks do not establish independent review or assurance.
- Use an explicit commit range for `vnv-review`; this repository uses `main`.
- Reviewer packets preserve the frozen OCR delegation requirement and Reverify
  setting. OCR assists the independent reviewer; unavailable tools are typed
  gaps with their exact errors. Reverify is not applicable to this docs slice:
  no compiled binary is built or claimed.
- Preserve raw SARIF unchanged. Format findings as
  `rule_id | path | severity | status | date` and attach reproducible evidence.
- Sanitize findings and evidence: no credentials, personal account details,
  absolute local home paths, proprietary prompts, model names or scoring formulas.
- `REFUSED_NO_VNV` is a non-pass row, not itself a merge block (OD-AFC-10).

## Findings target

All areas target GitHub issues in `1wgrumph/amazon-fantasy-companion` with the
existing `vnv` label, filed through the issue-label policy tool. Reproduce and
check duplicates first; use the mandated sections (Origin, Harness / version,
What, Current evidence, Expected, Acceptance). Dry-run before submission and
preserve reporting and publication authority. Do not create labels or file
upstream reports implicitly. If filing is unavailable or unauthorized, retain
the finding in the active review output with the exact gap.

`docs/vnv/` is the guidance root, not a raw-evidence store. No separate evidence
root is declared; link sanitized command receipts from the review or issue.
