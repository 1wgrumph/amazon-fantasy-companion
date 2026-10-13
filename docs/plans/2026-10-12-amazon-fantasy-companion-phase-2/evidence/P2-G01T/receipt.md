# P2-G01T red receipt

Outcome: **ENVIRONMENT_FAILURE** (blocking qualification gaps); behavioral red half ready.
Lease: `P2-G01T-g1`, generation 2, active. Branch `afc/p2-g01`.
Baseline: `4994aad44ace64f3c9434f73461f3fe2d12f694b`.

CMD-RED: exit 1, 50 tests, 39 existing cases PASS, 11 new cases,
24 behavioral assertion failures, zero collection/import/tool errors.
All FAIL records belong to `test_product_gate`; missing areas exit 2 instead of
contract 0/1/3 and workflow jobs/filters/setup pins are absent.
Frozen bytes: `test-sha256.json`; dirty test patch: `test-diff.json`.
Product green must retain these IDs and hashes. No author assurance PASS.

Native coverage.py 7.13.5 under Python 3.12.3 qualified: all four statements
covered passes, deliberate uncovered return yields 75% and exit 2 at threshold
90%, absent native data rejects without producing XML. This is aggregate
reporter qualification only, never changed-line coverage or adapter PASS.
`PROC-GATE-TOOL-QUALIFY` exits 1. Its `&&` prevents mutation execution;
separate mutation diagnostic also exits 1. Exact errors and bindings are in
`tool-binding.json`; every remaining qualification control is listed in
`receipt.json`. No package installed. Neither unavailable mutmut nor manually
edited source provides killed/surviving native-mutant evidence.

Gate child-command fixtures execute observed shell exit 0/1 and real Python
3.12 pytest. They prove command invocation/status contracts only; they are
not native Android or SAM lint evidence. No engine is started. Unique owned
fixture roots are removed on every path. Timing is in `runs.json`.

Two recorded corrections: the explicit dispatch authorizes a local red commit
using `--no-verify`; legacy area membership now permits extensions while exact
gate/job/filter correspondence and the new five-area assertions remain enforced.
Existing 39 test IDs still pass. No hook/config or product gate edited.

Review: frozen OCR delegate remains required for independent review by parent.
Reverify: not applicable — source/test receipts, no binary attribute claim.
All nine SEIT rows are supporting evidence only; closing slices are named in
`receipt.json`. No lifecycle/issue acceptance or publication claim.

## developer_feedback

- G01T-DX-01: native coverage binding and missing tools; `tool-binding.json`,
  `PROC-GATE-TOOL-QUALIFY.txt`, `mutation-diagnostic.txt`.
- G01T-DX-02: active controller lease; `lease-validation.json`.
- G01T-DX-03: legacy-set extension correction; `test-diff.json` and the three
  passing legacy logs.

BUG_ROUTE: not-a-bug expected TDD red and dispatched tool gaps; no nested triage.
BRAN unavailable; ordinary repository discovery used.

Create Lean Skill: BLOCKED. No skill target/write authority in this packet;
installed Implementer already owns the behavior. No duplicate skill authored.

Skipped: product implementation, native Android/SAM tests, independent review.
Risk: diff_cover/mutmut/cfn-lint and adapter/Android/shell qualification gaps
remain blocking; this red commit must not be landed on its own.
