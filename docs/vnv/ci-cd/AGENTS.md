# CI/CD review guidance

## Scope

Repository-relative paths: `tools/ci/**`, `.githooks/**`, `.github/workflows/**`,
`docs/**`, and root `*.md`. Exclude `docs/developer-feedback/**` and
`docs/vnv/spec/**` and `docs/vnv/developer-feedback/**`, owned by those areas.
This includes the Vnv index and `docs/vnv/ci-cd/**`.

## Tools

- `tools/ci/gate.sh docs hygiene`

This runs documentation checks, path/credential hygiene, workflow checks and
the gate's own tests. The entrypoint is delivered by S09; until present, report
a typed gap. Use the exit and evidence rules in the [index](../AGENTS.md).

## Review Focus

- Contract-first: the same entrypoint runs locally, in git hooks and Actions;
  changed-path selection always includes hygiene, and failures propagate.
- Parallel-safe CI: pull requests and pushes to `main`, concurrency cancellation,
  path-filtered jobs, SHA-pinned actions, `contents: read`, no secret references,
  and GitHub-hosted runners.
- Security controls: shape-based home-path checks and credential detection
  report `file:line:rule-id`, never sensitive matched text.
- Spec discipline: each area has all four required headings; relative Markdown
  links resolve. External URLs and anchors are not checked by the docs gate.
- Owner boundary: do not turn guidance into deployment, activation or publication
  authority; no changes to shared skills are owned by this area.

## Findings target

GitHub issues in `1wgrumph/amazon-fantasy-companion`, label `vnv`, through the
issue-label policy tool. Apply the [index](../AGENTS.md) reproduction, duplicate,
sanitization and authority rules; retain unfileable findings in the review output.
