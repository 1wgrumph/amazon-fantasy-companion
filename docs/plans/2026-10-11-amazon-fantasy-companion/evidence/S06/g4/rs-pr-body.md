## What changed

- Exclude Markdown section-sourced specifications built to one file from use-requirements-system routing, naming spec-authoring as their owner.

## Why

AFC S06 introduces portable Markdown assembly in Alphazedehq. The reciprocal non-trigger prevents that skill from colliding with SDoc/StrictDoc authoring and publication. Only the description changes (DEC-AFC-SD-028).

## Validation

- CMD-SKILL-TRIGGER-RECIPROCAL: exit 0 on this committed candidate. A fresh Claude session with Read as its only allowed tool classified the Markdown request NO_MATCH and the SDoc publication request MATCH.
- `git diff --check`: exit 0.
- Exact evaluator command, harness version, session, result JSON and candidate SHA are retained in the planning worktree at evidence/S06/g4.

## Residual risk

- Draft awaits the configured phase review and this repository's full local merge gate; neither is claimed here. Implementer authority ends at the draft PR.
- No host, SDoc document, publication, deployment or runtime change was performed. Reverify is not applicable: description-only edit.
