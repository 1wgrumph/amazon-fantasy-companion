## What changed

- Call the shared gate with positional areas in workflow templates and fixtures, and reject incompatible gate calls in the checker.
- Accept workflow files or directories, checking every immediate `.yml`/`.yaml` file and failing on empty directories or any invalid workflow.
- Add regressions discoverable by unittest and preserve the existing pytest cases.

## Why

The merged template passed an unsupported area option to the shared gate, while the workflow checker rejected the directory input required by the integration plan. This bounded S02 repair aligns both interfaces with the shared contracts.

## Validation

The trigger-results environment variable pointed to the author's matching/non-matching classification receipt.

- `python3 -m unittest discover -s skills/setup-a-repo/tests -v` — exit 0; 5 tests, including stock size and installed creator validation.
- `! git grep -n -- '--area' skills/setup-a-repo` — exit 0; no matches.
- `python3 skills/setup-a-repo/scripts/check-workflows.py skills/setup-a-repo/templates` — exit 0; template PASS.
- `python3 -m pytest skills/setup-a-repo/tests -q -p no:cacheprovider` — exit 0; 39 passed, 4 subtests passed.
- `bash tools/ci/local-gates.sh` — exit 0; 17 gates passed before commit; committed candidate rerun passed 2 applicable gates with 15 not applicable and wrote its receipt.
- BRAN strict validation — passed. Skill remains 59 lines and 421 words.

Regression evidence: new cases failed against the original checker before the repair and passed afterward.

## Residual risk

Draft pending configured independent phase review and OCR; author checks are diagnostic, not assurance. Reverify is not applicable: no compiled binary is changed or claimed. Directory scanning is intentionally non-recursive. This packet authorizes a draft PR only; merge and downstream vendor-pin integration remain with the orchestrator.
