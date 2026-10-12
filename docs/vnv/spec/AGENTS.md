# Specification review guidance

## Scope

Repository-relative paths: `spec/**`, `tools/spec/**`, `docs/vnv/spec/**`.
Markdown section-sourced specifications and their vendored build/lint kit.
SDoc/StrictDoc documents in the Requirements System use `use-requirements-system`;
this guidance does not replace that workflow.

## Tools

- `tools/ci/gate.sh spec docs hygiene`

The spec area lints section sources and figures, rebuilds the output and checks
for a stale built file. While no specification exists, it builds and lints the
vendored template in a temporary directory and removes it. Missing `tools/spec/`
or Graphviz `dot` is GAP (exit 3), never PASS. S42 supplies the kit; S09 supplies
the gate. See the [index](../AGENTS.md) for evidence rules.

## Review Focus

- Spec discipline: section grammar, requirement UID references, traceability,
  generated numbering, figure layout and byte-identical rebuilds. Requirement
  quality remains owned by `requirements-engineering`.
- Repo-agnostic tools: no source-project names, absolute local paths or unrelated
  project dependencies; inspect source commit, skill tree ID and MIT notice in
  `tools/spec/VENDORED.md`.
- Owner boundary: the single `spec-authoring` skill owns this Markdown workflow;
  S07 neither authors the product specification nor vendors tools. Draft review,
  formal acceptance and publication remain distinct outcomes.

## Findings target

GitHub issues in `1wgrumph/amazon-fantasy-companion`, label `vnv`, through the
issue-label policy tool. Follow the [index](../AGENTS.md) for sanitized evidence,
duplicate checks and authority; retain filing gaps in the active review output.
