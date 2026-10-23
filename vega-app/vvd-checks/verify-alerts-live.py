#!/usr/bin/env python3
"""Stage 4 live NBA alert and Watch verdicts: verify-alerts-live.py <api-poll.jsonl> <alert-readings.json> <espn-event-id>.

api-poll.jsonl is poll-live-api.py's log (with "alerts.items") for the synthetic profile. alert-readings.json lists
the VVD captures read visually from each PNG (there is no OCR on the VVD):
  {"capture", "utc", "banner": {"headline", "context"} | null, "watch_message": str | null}
Checks, one PASS/FAIL line each; exit 0 only if all pass. Zero alerts fails closed:
- backend: the alerts long poll returned 200 and at least one NBA PlayerScore alert for this game, each naming
  exactly one starter and a #156 phrase (10/20/30 pts, double-double, +N fantasy pts);
- device: a capture shows the "Score update" banner whose context is "<starter> — <phrase>" of a logged alert,
  taken no earlier than that alert first appeared in the log;
- device: exactly one Watch attempt shows a local app-absent or access-unknown outcome; a held message is one
  attempt, a new switching confirmation followed by an outcome is another (a playback claim fails).
The routing-outcome POST is attempted per app code trace; backend receipt is unverified (no read-back).
"""
import json
import re
import sys

PHRASE = re.compile(r"^(reaches (10|20|30) pts|reaches a double-double|\+\d+(\.\d)? fantasy pts)$")
OUTCOMES = {"Watch: the provider app is not installed.": "appAbsent",
            "Watch: could not confirm the game is playing.": "accessUnknown",
            "Watch: the provider app refused the launch.": "playbackDenied"}

ticks = [json.loads(line) for line in open(sys.argv[1])]
readings = json.load(open(sys.argv[2]))
event = sys.argv[3]

first_seen = {}
for t in ticks:
    for item in t["alerts"].get("items") or []:
        first_seen.setdefault(item["id"], (t["utc"], item))
alerts = [item for _, item in first_seen.values()]
nba = [a for a in alerts if a["alertType"] == "PlayerScore" and a["gameId"] == event
       and len(a["starters"]) == 1 and PHRASE.match(a["matchup"] or "")]

checks = {}
checks["backend: alert polls 200 and >= 1 NBA PlayerScore alert for this game (zero fails)"] = bool(ticks) and all(
    t["alerts"]["http"] == 200 for t in ticks) and bool(nba) and len(nba) == len(alerts)
banner = [r for r in readings if r.get("banner")
          and r["banner"]["headline"] == "Score update"
          and any(r["banner"]["context"] == f"{a['starters'][0]} — {a['matchup']}"
                  and first_seen[a["id"]][0] <= r["utc"] for a in nba)]
checks["device: a capture shows the Score update banner for a logged alert"] = bool(banner)
# A held result is one attempt; a confirmation or cleared message separates attempts.
outcomes = []
previous_message = None
for r in readings:
    message = r.get("watch_message")
    if (message or "").startswith("Watch:") and message != previous_message:
        outcomes.append(OUTCOMES.get(message))
    previous_message = message
checks["device: exactly one Watch attempt shows a local app-absent or access-unknown outcome (backend receipt unverified)"] = bool(banner) and \
    len(outcomes) == 1 and outcomes[0] in ("appAbsent", "accessUnknown")
for name, ok in checks.items():
    print(("PASS " if ok else "FAIL ") + name)
print(f"alerts: {len(alerts)} logged, {len(nba)} NBA PlayerScore; banner captures: "
      f"{[r['capture'] for r in banner]}; local outcomes: {outcomes}")
print("routing-outcome POST: attempted per app code trace when Watch completes; backend receipt unverified (no read-back)")
sys.exit(0 if all(checks.values()) else 1)
