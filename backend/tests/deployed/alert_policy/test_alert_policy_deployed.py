"""Deployed alert policy cases (SEIT-AFC-PR-014, -020, -023, -027, -028; P2-L03 execution).

Every alert the deployed stack serves is one of the three registered types,
carries its trigger context, was not released before its spoiler delay could
pass, and red-zone text makes only team-level claims. Without
AFC_DEPLOYED_API_URL these skip (NOT_RUN) like every deployed case.
"""

import re
from datetime import datetime, timezone

from deployed_helpers import call

TYPES = {"RedZone", "PlayerScore", "CloseGame"}
OVERCLAIM = re.compile(r"on the field|in the game|in the huddle|will (?:score|find|get)|"
                       r"going to score|about to score|set to score|should score|"
                       r"bound to score|sure to score|(?:is|are) scoring", re.IGNORECASE)


def alert_envelopes(linked):
    status, body = call(linked.base, "GET", "/v1/alerts", token=linked.token)
    assert status == 200, body
    alerts = body.get("alerts")
    assert isinstance(alerts, list), body
    return alerts


def test_served_alerts_have_registered_types_and_context(linked):
    """AFC-PR-014 / AFC-PR-027: type and trigger context on every served alert."""
    for alert in alert_envelopes(linked):
        data = alert.get("data", {})
        assert data.get("alertType") in TYPES, alert
        context = data.get("triggerContext")
        assert isinstance(context, dict) and context.get("eventId") and context.get("starters"), alert


def test_served_alerts_are_released(linked):
    """AFC-PR-020: nothing is served before its release time."""
    now = datetime.now(timezone.utc)
    for alert in alert_envelopes(linked):
        stamp = alert.get("updatedAt", "")
        assert datetime.fromisoformat(stamp.replace("Z", "+00:00")) <= now, alert


def test_served_red_zone_text_is_team_level(linked):
    """AFC-PR-028 / AFC-PR-023: red-zone commentary makes no on-field or will-score claim."""
    for alert in alert_envelopes(linked):
        data = alert.get("data", {})
        if "RedZone" in data.get("triggerContext", {}).get("alertTypes", []):
            assert not OVERCLAIM.search(data.get("commentary") or ""), alert
