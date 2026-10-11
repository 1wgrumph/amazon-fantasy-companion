# Planning and Design correction round 1 (run 2 resume)

Round 1 of 2. Source: Plan Integrator findings TE-F03 and TE-F04 (`plan-integrator-receipt.md`), both marked "design (Planning node)".

- `design.md`: DES-AFC-GATE gains the `check_paths.py --files <path>...` mode (TE-F03). DES-AFC-TV gains the Kover and PIT test-only Gradle plugins. DES-AFC-INFRA gains the backend test dependencies coverage, diff-cover and mutmut. Each is admitted through CMD-SCAN (TE-F04). Diff: `pd-r1-applied-design.diff`.
- `seit.json` and `implementation.json`: the design.md sha256 was rebound mechanically from d972faa0… to d83150f7…; no other seit.json change.
- `implementation.json`: DoD risk rows TE-F03 (closed) and TE-F04 (dependencies closed; thresholds open for integrated review) updated; candidate_digest rebound from 6fd4c72e… to 87fa2433….
- Freeze `plan-package.cjs`: PASS, manifest_digest 87fa24334fda312e61582c169cfe9b3c205f989ff30cd6edc7017bf4a9ee78f3, findings []. Both schemas valid. Render: RENDER_WRITE / RENDER_CHECK_PASS sha256:93c42a72c2e9d8bf806d743f80729a925cd792205b7db50260426261bc0a56c9. `evaluatePlanningReview`: NEEDS_MORE_EVIDENCE / review_round_pending (expected before the review).

Not changed here: TE-F05 (visual-evidence storage) is an owner item. TE-F07 needs an Integration Engineer delta to `integration_plan.configuration_identity` (stack tags); the S18 packet already carries the tag form. TE-F08 (scrub absolute home paths from `specialists/` before the commit) is for the Orchestrator.
