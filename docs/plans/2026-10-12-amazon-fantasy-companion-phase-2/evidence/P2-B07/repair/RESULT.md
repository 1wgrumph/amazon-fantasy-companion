# P2-B07 repair: B07-R01 and B07-R02

Base candidate: `6477dc7f21afbe7f91fbdf578100f121f9a3489f` (`afc/p2-b07t`).
Repair of the independent review's REPAIR_REQUIRED verdict. No second review.

## Fix

- **R01** (`backend/src/panel/__init__.py`): `project()` stores a SHA-256
  fingerprint of the projected lineup (starters + scoring inputs) in the
  panel row's `freshness` map. `snapshot()` computes the current lineup's
  fingerprint and spends the revision's low bit when it differs from the
  projected one, with the counter/profile base doubled so every projection
  or settings bump stays strictly above a spent low bit. No write on the
  read path (the API function holds only `GetItem` on Panels).
  Known limits, recorded as a `shortcut:` comment at the site: a second
  lineup change, or a change back to the projected lineup, before the next
  projection reuses a revision; a stored lineup revision counter would be
  needed to outrun arbitrary sequences, and the read path cannot write one.
- **R02** (`backend/src/store/__init__.py`, `panel.project`): projections now
  write through the narrow `store.put_panel_conditional` helper, conditioned
  on `freshness.counter` still equal to the read value (`attribute_not_exists`
  when no row exists). A lost race re-reads the row and re-decides the
  replacement against the winner's games map, up to three attempts, then
  raises so the stream retries instead of silently dropping facts.

## Red then green

Red (base candidate, review reproducer): 2 failed, 1 passed
(`test_r01...` revision 2 -> 2; `test_r02_overlapping...` game erased;
sequential control passed).

Green after the fix, same test ids: the three review reproducer cases and
the five new regressions in `backend/tests/unit/panel/test_panel_repair_b07.py`
all pass (8 passed). The new file adds a re-read stability case and a
projection-after-change case beside the reproducer's R01, R02 and control.

## Verification

| Check | Result |
|---|---|
| Review reproducer `review/test_b07_repro.py` | red: 2 failed, 1 passed -> green: 3 passed |
| New regressions `test_panel_repair_b07.py` | 5 passed |
| Frozen panel unit suite + `test_store.py` | 92 passed (80 frozen) |
| `verify_receipt.py` on the P2-B07T receipt | PASS, 7 frozen files |
| `bash tools/ci/gate.sh` | exit 0, backend 821 passed, 3 skipped |

Commands used `$HOME/.local/share/afc-tools/backend-tests/bin/python3.12`
with the flags recorded in `review/receipt.md`.

## Not repaired / unchanged

- R1 (production per-player statistics unavailable) stays a typed gap.
- The seven frozen B07T files are byte-identical (receipt PASS, empty diff).
- `origin/main` was not merged; landing does that later.
- Residual risk: the R01 low-bit limit above; `get_panel` is still
  eventually consistent in production, so an overlapped projection may need
  a stream retry if all three conditional attempts read stale counters.
