# P2-X10 visual evidence index (preparation unit, issue #44)

No capture exists yet and none is claimed. This index names what the
live run (at or after 2026-10-23T03:30Z, after P2-X09 releases the
stick) must capture, per `evidence/e2e/2026-10-19/RUNBOOK.md`.

## Expected captures

Produced with CMD-ADB-SCREENCAP / PROC-E2E-LIVE
(`adb -s <stick_serial> exec-out screencap -p > <file>`) and
CMD-ADB-GEOMETRY (`dumpsys window`, `wm size`; sanitize the private
capture before copying here — no device address, serial, or local
path in the repository).

| Scenario | Capture | Shows |
|---|---|---|
| S1 | `s1-panel-corrected.png`, `s1-window.txt`, `s1-display.txt` | corrected panel value after ingest |
| S2 | `s2-panel-before.png`, `s2-panel-after.png`, `s2-window.txt`, `s2-display.txt` | starter swap reflected on the panel |
| S3 | `s3-window.txt`, `s3-display.txt` (screencap only if a duplicate appears) | geometry baseline; duplicate card if the defect fires |
| S4 | `s4-panel-stale.png`, `s4-panel-unavailable.png`, `s4-window.txt`, `s4-display.txt` | stale (past 60 s) and unavailable labels, never zero-for-unknown |
| S5 | `s5-<defect-id>.png` + geometry where the P2-X09 record had them | same state as the original defect evidence |

## Labeling

- Every capture entry in `run-record.json` carries scenario id,
  UTC timestamps, `provenance` (`live` or `historical-replay`),
  event id, and app/APK identity. Replay-state captures are labeled
  `historical-replay` and never presented as live.
- File names stay exactly as tabled above; a capture that could not
  be taken is recorded as a typed gap in the run record, not omitted.

## Protected-video limitation (RISK-AFC-P2-09)

`screencap`/`screenrecord` may return black or blank frames for
protected provider video (secure surfaces). Mitigation per
OD-AFC-P2-02 = A: companion UI captures plus `dumpsys` window
geometry here; owner camera capture of the TV screen (OA-9) for
shots that must show provider video, marked owner-filmed. A black
frame is recorded as such with its geometry pair — never replaced
with stand-in footage, and the fullScreen panel (AFC-PR-047) means
X10 panel captures are companion-UI frames in any case.
