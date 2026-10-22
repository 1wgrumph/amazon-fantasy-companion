#!/usr/bin/env python3
"""Stage 3 live-panel verdicts: verify-panel-live.py <api-poll.jsonl> <device-readings.json>.

api-poll.jsonl is poll-live-api.py's log for the synthetic profile. device-readings.json lists the VVD captures
as {"capture", "utc", "session", "label", "total", "stale_s", "fault"}, read visually from each PNG (there is no
OCR on the VVD). "session" is one panel controller lifetime: launch, or the next profile Save or relaunch.
When the team total is unavailable (a starter without statistics), the row values stand in for it: the reading's
"total" is then the list of shown row values, null for an unavailable row. stale_s is null when no stale label shows.
Checks, one PASS/FAIL line each; exit 0 only if all pass:
- backend: every in-game panel read is 200, NBA, nbaPoints, and its total changes during the game;
- backend: a panel whose rows changed carries a higher revision (the app drops equal revisions);
- device: every capture shows the NBA · Points label;
- device: within one controller lifetime the shown total changes while the backend total changes, and the stale
  label resets at least once instead of growing on every capture (live refresh);
- device: captures taken while the guest forwarder refused afc-dev show a stale label that keeps growing (R-3).
"""
import json
import sys

ticks = [json.loads(line) for line in open(sys.argv[1])]
readings = json.load(open(sys.argv[2]))
live = [t for t in ticks if t["game"]["name"] == "STATUS_IN_PROGRESS"]


def value(total, rows=()):
    """The total, or the row values when the total is unavailable; hashable either way."""
    if total is None and rows:
        return tuple(r[1] for r in rows)
    return tuple(total) if isinstance(total, list) else total


def window(session):
    rows = [r for r in readings if r["session"] == session]
    return min(r["utc"] for r in rows), max(r["utc"] for r in rows)


checks = {}
checks["backend: in-game panel reads are 200, NBA, nbaPoints and the total changes"] = bool(live) and all(
    t["panel"]["http"] == 200 and t["panel"]["sport"] == "nba" and t["panel"]["basis"] == "nbaPoints"
    for t in live) and len({value(t["panel"]["total"], t["panel"]["rows"]) for t in live}) > 1
checks["backend: changed panel rows carry a higher revision"] = all(
    b["panel"]["revision"] > a["panel"]["revision"]
    for a, b in zip(live, live[1:])
    if [r[:2] for r in a["panel"]["rows"]] != [r[:2] for r in b["panel"]["rows"]])
checks["device: every capture shows NBA · Points"] = bool(readings) and all(
    r["label"] == "NBA · Points" for r in readings)
refresh_covered = False
for session in sorted({r["session"] for r in readings}):
    start, end = window(session)
    backend = {value(t["panel"]["total"], t["panel"]["rows"]) for t in live if start <= t["utc"] <= end}
    own = [r for r in readings if r["session"] == session and not r.get("fault")]
    shown = {value(r["total"]) for r in own}
    stale = [r["stale_s"] or 0 for r in own]
    if len(backend) > 1:
        refresh_covered = True
        checks[f"device {session}: shown total changes while the backend total changes ({len(backend)} values)"] = \
            len(shown) > 1 and any(b < a for a, b in zip(stale, stale[1:]))
if not refresh_covered:
    checks["device: live refresh coverage"] = False
fault = [r for r in readings if r.get("fault")]
checks["device: during refused refreshes the held value re-renders with a growing stale label (R-3)"] = len(fault) >= 2 and all(
    b["stale_s"] > a["stale_s"] and b["total"] == a["total"] for a, b in zip(fault, fault[1:]))
for name, ok in checks.items():
    print(("PASS " if ok else "FAIL ") + name)
sys.exit(0 if all(checks.values()) else 1)
