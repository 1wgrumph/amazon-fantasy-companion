# Repair notes for PR #141

Review receipt verdict: REPAIR_REQUIRED.
Candidate before this repair: a498ecc8739647484d37e601a6ed2eaf73d4fc0d.

## R1

The SP-4 evidence inventory cited five deleted screenshots by extensionless stem and did not name their rows in `evidence/visual/PRIVATE-EVIDENCE.md`.

Each screenshot citation now names that row and is marked withheld (provider content). Surviving geometry and logcat files stay named: `r1-provider-pip-home-geometry.txt`, `r1-provider-pip-home-logcat.txt`, `r2-spike-pip-entered-geometry.txt`, `r2-spike-pip-entered-logcat.txt`, `r2-spike-pip-over-prime-geometry.txt`, `r2-spike-pip-over-prime-logcat.txt`, and `r6-final-prime-geometry.txt`. The return-to-Prime capture has no geometry or logcat file; its citation is the withheld screenshot record only.

`tools/ci/check_provider_art.py` rejects a paragraph that says "screenshot" and cites a withheld image by its extensionless stem (`PROVIDER-ART-TEXT`). A geometry or logcat filename that only prefixes the stem, and a state line outside a screenshot inventory, stay allowed.

## R2

The Unreleased Security entry for BUG-PROVIDER-ART in `CHANGELOG.md` links [PR #141](https://github.com/1wgrumph/amazon-fantasy-companion/pull/141).

## Red

Command: `python3 -m unittest discover -s tools/ci/tests -p test_check_provider_art.py -v`

Exit: 1. The new inventory test failed before the check change because the check returned 0. `test_geometry_prefix_and_state_line_stay_allowed` passed in the same run.

```
FAIL: test_extensionless_screenshot_inventory_stem_fails
AssertionError: 0 != 1
Ran 13 tests in 0.114s
FAILED (failures=1)
```

The traceback frame is `tools/ci/tests/test_check_provider_art.py`, line 138. The absolute checkout path is omitted from this record.

## Green

Same command after the check change. Exit: 0.

```
Ran 13 tests in 0.129s
OK
```

## Gates

Trailing whitespace was stripped on the four edited sources before the gates. None was present. `TMPDIR` was a private directory outside any git work tree. Full output is in `repair-gates.txt`.

- spec exit 0, last line: `gate: spec: PASS checks completed`
- docs exit 0, last line: `gate: docs: PASS checks completed`
- hygiene exit 0, last line: `gate: hygiene: PASS checks completed`
