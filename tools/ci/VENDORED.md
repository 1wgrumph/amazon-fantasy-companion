# CI provenance

Source repository: [AlphazedeHQ](https://github.com/alphazede/Alphazedehq).

- D4-A merge commit: `448d40c3dbb6fd9dceb66d575c66ee89fb45f6e4`.
  Adapt `skills/setup-pre-commit/templates/gate.sh` to the Phase 1 areas.
  This repository keeps only the pre-push hook.
- D4-B merge commit: `120dee00207425201aa77d1f42f3756ee6bc406e`
  (PR #308, including directory input and positional area invocation).
  Copy `skills/setup-a-repo/scripts/check-workflows.py` byte for byte into
  `check_workflows.py`; SHA256:
  `5919f62d98b566dc4428eed1e5262b50877f274e5ea4dc7fa48f07aa85cd4d3f`.

Local checkers implement DES-AFC-GATE. A spec's generated file is
`spec/<name>/<name>.md`, including
`spec/amazon-fantasy-companion/amazon-fantasy-companion.md`. Rebuilding must
match the committed file; an untracked build fails until committed.

The workflow uses the reviewed full-SHA Action pins. The shared gate and
workflow select both spec and docs on CI or hook changes; hygiene always runs.
The spec and hygiene runners provision Graphviz and uv because hygiene's
hermetic gate tests exercise the spec area too.
