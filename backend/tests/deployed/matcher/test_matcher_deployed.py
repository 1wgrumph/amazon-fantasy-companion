"""Deployed alert identity (SEIT-AFC-PR-025, SEIT-AFC-PR-026; P2-X10/L03 execution).

Alert envelopes served for one profile never repeat an alert id, and a
re-read never moves an alert's revision backwards: corrections revise in
place. Without AFC_DEPLOYED_API_URL these skip (NOT_RUN) like every
deployed case.
"""

from deployed_helpers import call


def alert_envelopes(linked):
    status, body = call(linked.base, "GET", "/v1/alerts", token=linked.token)
    assert status == 200, body
    alerts = body.get("alerts")
    assert isinstance(alerts, list), body
    return alerts


def test_alert_ids_are_unique_per_profile(linked):
    ids = [alert.get("id") for alert in alert_envelopes(linked)]
    assert all(isinstance(alert_id, str) and alert_id for alert_id in ids), ids
    assert len(ids) == len(set(ids)), f"one alert id served twice: {ids}"


def test_alert_revision_never_moves_backwards(linked):
    first = {alert["id"]: alert["revision"] for alert in alert_envelopes(linked)}
    second = {alert["id"]: alert["revision"] for alert in alert_envelopes(linked)}
    for alert_id, revision in first.items():
        assert second.get(alert_id, revision) >= revision, (alert_id, first, second)
