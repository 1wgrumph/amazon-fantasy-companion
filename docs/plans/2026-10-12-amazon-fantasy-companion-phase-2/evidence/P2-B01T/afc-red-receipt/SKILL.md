---
name: afc-red-receipt
description: Validate an existing frozen AFC CMD-RED artifact handoff against its JUnit failures and file hashes. Use for receipt validation only; do not use to author tests, implement green behavior, review code, change Lifecycle state, or land work.
---

# AFC Red Receipt

Validate one supplied receipt; return typed evidence without changing product files.
This evidence-local skill is not installed in the global catalog.

## Preconditions

Require the repository root, receipt path, baseline, active slice lease, and
an authorized red boundary. Read the receipt's declared test inventory.
Leave test authoring and authority decisions with Bearing Implementer and Write Tests.

## Procedure

1. Check the receipt identity against the supplied packet and active lease.
   A changed route, branch, generation or baseline returns `CONTRACT_FAILURE`.
2. From the repository root, run `python3.12 <skill>/scripts/verify_receipt.py <receipt>`.
   The verifier reads only the declared test files and local CMD-RED JUnit artifact.
3. Require pytest exit 1, a nonempty all-failing test inventory, no errors/skips,
   exclusively AssertionError failures, exact test IDs, and unchanged SHA-256s.
4. Preserve the raw red exit as expected-red evidence; never call the backend green.
   Successful receipt validation cannot close registered system/deployed proof rows.
5. Return the verifier outcome and command exit. Missing artifacts return
   `NEEDS_EVIDENCE`; changed hashes, IDs or failure classes return `VALIDATION_FAILED`.
   Do not repair tests or rerun the backend under this skill. Return to the assigned role.

## Bounds and outputs

Run once per frozen artifact set; repeat only after a new supplied artifact.
Return `PASS`, `VALIDATION_FAILED`, `NEEDS_EVIDENCE`, `CONTRACT_FAILURE`,
or `NOT_APPLICABLE`. A nonmatching request returns `NOT_APPLICABLE` with no writes.
Never install tools, dispatch reviewers, modify a lease, push, publish or close issues.
