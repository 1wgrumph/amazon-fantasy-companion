#!/usr/bin/env python3
"""Stage 3 workstation side: log the synthetic profile's panel and alerts and the ESPN game status during a live game.

usage: poll-live-api.py <base-url> <session-file> <league/team> <espn-event-id> <out.jsonl> [interval-s]
Read-only GETs. One JSON line per tick: UTC, game status, panel status/revision/rows, alert status/count/types.
The session token is read from <session-file> and never written. Ends when the game reports STATUS_FINAL.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ESPN = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary?event="


def get(url, token=None):
    request = urllib.request.Request(url, headers={"authorization": f"Bearer {token}"} if token else {})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, None
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        return f"error:{type(error).__name__}", None


def alert_row(alert):
    """The fields the alert verdict needs: id, revision, type, sport-bearing event, starters, phrase, route basis."""
    data = alert.get("data") or {}
    context = data.get("triggerContext") or {}
    return {"id": alert.get("id"), "revision": alert.get("revision"), "updatedAt": alert.get("updatedAt"),
            "alertType": data.get("alertType"), "gameId": context.get("gameId"), "eventId": context.get("eventId"),
            "starters": [s.get("name") for s in context.get("starters") or []], "matchup": context.get("matchup"),
            "accessBasis": (data.get("route") or {}).get("accessBasis")}


def tick(base, token, pair, event):
    row = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    status, summary = get(ESPN + event)
    competition = ((summary or {}).get("header") or {}).get("competitions") or [{}]
    game = (competition[0].get("status") or {}).get("type") or {}
    row["game"] = {"http": status, "name": game.get("name"), "detail": game.get("shortDetail")}
    status, panel = get(f"{base}/v1/panel?teamLeague={urllib.parse.quote(pair, safe='')}", token)
    data = (panel or {}).get("data") or {}
    row["panel"] = {"http": status, "revision": (panel or {}).get("revision"), "sport": data.get("sport"),
                    "basis": data.get("scoringBasis"), "total": (data.get("teamTotal") or {}).get("value"),
                    "rows": [[r["name"], r["points"]["value"], r["points"]["asOf"], r["points"]["stale"],
                              r.get("gameStatus")] for r in data.get("rows") or []]}
    status, alerts = get(f"{base}/v1/alerts", token)
    items = (alerts or {}).get("alerts") or []
    row["alerts"] = {"http": status, "count": len(items),
                     "types": [((a.get("data") or {}).get("alertType"), a.get("updatedAt")) for a in items],
                     "items": [alert_row(a) for a in items]}
    return row


def main():
    base, session, pair, event, out = sys.argv[1:6]
    interval = int(sys.argv[6]) if len(sys.argv) > 6 else 30
    token = open(session).read().strip()
    while True:
        row = tick(base.rstrip("/"), token, pair, event)
        with open(out, "a") as handle:
            handle.write(json.dumps(row) + "\n")
        print(row["utc"], row["game"]["detail"], row["panel"]["http"], row["panel"]["total"],
              row["alerts"]["http"], row["alerts"]["count"], flush=True)
        if row["game"]["name"] == "STATUS_FINAL":
            return 0
        time.sleep(interval)


if __name__ == "__main__":
    sys.exit(main())
