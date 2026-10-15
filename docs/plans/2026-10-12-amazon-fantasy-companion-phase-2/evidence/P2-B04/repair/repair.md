# P2-B04 repair — B04-RV-001

Base candidate: `ed34a4f4c7c993ac5a22bf73f78e467bb067d75e` (branch `afc/p2-b04t`).

Fix: `_alert_for` in `backend/src/matcher/__init__.py` now puts
`ConsistentRead=True` in the initial Query request dict, so it persists across
pages. After a committed alert write, a retry can no longer read an omitted or
older row and treat an already-stored revision as a new match.

Regression: `backend/tests/unit/matcher/test_matcher_consistency.py` (new,
non-frozen) models both lag outcomes with a botocore after-call hook that only
tampers with non-consistent Query responses, and asserts every alert Query
sets `ConsistentRead=True`. Fresh read at stored revision 2 vs event revision
2 still yields no match.

Red-then-green (same test id):
- Red: review reproducer `review/reproduce_query_lag.py` exit 1 without
  traceback (committed rev 2, event rev 2, both lag cases produced 1 match);
  new regression test failed with AssertionError (match returned, cursor None).
- Green: `pytest backend/tests/unit/matcher/` — 25 passed (24 frozen + 1 new).
  Post-fix the review reproducer exits 1 with AssertionError at its line 71
  bug assertion (`len(missing) == 1`) because `missing` is now `[]`: the script
  is written to return 1 only when the violation reproduces, so a clean exit 0
  is not reachable after repair. The new regression test is the green proof.

Verification:
- `verify_receipt.py` on the P2-B04T receipt: PASS (24 failed_cases, 2 skipped,
  5 frozen_files) — frozen files byte-identical.
- `bash tools/ci/gate.sh`: exit 0; backend 627 passed (626 baseline + 1 new).

Not checked: live AWS behavior; pagination beyond one page is covered by the
request dict persisting, not by a multi-page fixture.
