"""DES-AFC-P2-FEED ESPN ingest and labeled replay (IngestFunction).

One scheduled invocation polls the ESPN scoreboard, then validates, normalizes and
stores every in-progress game's summary. The schedule itself is enabled only while
a profile-relevant game is in progress (IngestScheduleState).
"""

import json
from urllib import parse, request

from feed_ingest.ingest import ingest_summary
from feed_ingest.validation import validate_scoreboard


def _feed():
    return "https://site.api.espn.com/apis/site/v2/sports/football/nfl/"


def _max_bytes():
    return 4 * 1024 * 1024  # above the largest captured summary (680 KB); bounds hostile bodies


def _get_json(url):
    """GET a JSON body from the allowlisted ESPN host only, size-bounded."""
    parts = parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "site.api.espn.com":
        raise ValueError("Feed requests go only to https://site.api.espn.com")
    with request.urlopen(url, timeout=10) as response:
        body = response.read(_max_bytes() + 1)
    if len(body) > _max_bytes():
        raise ValueError("ESPN response exceeds the size bound")
    return json.loads(body)


def poll():
    """Ingest every in-progress game on the current scoreboard; return the stored events."""
    scoreboard = _get_json(_feed() + "scoreboard")
    validate_scoreboard(scoreboard)
    stored = []
    for game in scoreboard["events"]:
        if game.get("status", {}).get("type", {}).get("state") == "in":
            summary = _get_json(_feed() + "summary?event=" + game["id"])
            stored += ingest_summary(summary, game["id"])
    return stored


def lambda_handler(event, context):
    """IngestFunction entry: one poll per EventBridge Scheduler invocation."""
    if not isinstance(event, dict) or event.get("source", "aws.scheduler") != "aws.scheduler":
        raise ValueError("IngestFunction accepts only its schedule event")
    return {"stored": len(poll())}
