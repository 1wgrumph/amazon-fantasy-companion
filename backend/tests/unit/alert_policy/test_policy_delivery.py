"""Relevance, basis labels, opt-in and alert delivery red tests
(VCASE-AFC-PR-008, -011, -020, -026, -037, -060).

The policy emits only for profiles the matcher concerned, labels every alert
with exactly one monitoring basis, and never uses a detection basis while the
customer is opted out. GET /v1/alerts (alert_policy.pending) serves only the
caller's own released alerts, in cursor order, and never moves its cursor past
an alert still held for the spoiler delay.
"""

from datetime import datetime, timedelta, timezone

from policy_support import (BASES, PASSER, RECEIVER, attempt, evaluate,  # noqa: F401
                            for_profile, game_event, iso, link_device, match, policy,
                            seed_alert, seed_profile)


def scoring(event_id, **fields):
    return game_event(event_id, field_position=35, scoring=True, **fields)


def pending(policy, profile_id, cursor=None):
    body = attempt(policy.pending, profile_id, cursor)
    assert isinstance(body, dict) and set(body) >= {"alerts", "cursor"}, body
    assert isinstance(body["alerts"], list), body
    assert isinstance(body["cursor"], str), f"cursor must be a string: {body!r}"
    return body


def past(minutes):
    return iso(datetime.now(timezone.utc) - timedelta(minutes=minutes))


def future(minutes):
    return iso(datetime.now(timezone.utc) + timedelta(minutes=minutes))


def test_afc_pr_060_only_matched_profiles_receive_alerts(policy):
    """AFC-PR-060 / AFC-PR-008: an all-types bystander the event does not concern gets
    nothing; the concerned profile gets its alert."""
    seed_profile("fan")
    seed_profile("bystander")
    event = scoring("401999001401")
    alerts = evaluate(policy, event, [match("fan", event)])
    assert [alert["profileId"] for alert in alerts] == ["fan"]


def test_afc_pr_060_no_match_emits_nothing(policy):
    """AFC-PR-060 negative: an event that concerns no profile emits no alert."""
    seed_profile("fan")
    assert evaluate(policy, scoring("401999001402"), []) == []


def test_afc_pr_011_every_alert_carries_exactly_one_basis_label(policy):
    """AFC-PR-011: each emitted decision is labeled observed-playback or profile-assumption."""
    seed_profile("fan", detectionOptIn=True)
    seed_profile("other")
    event = scoring("401999001403")
    alerts = evaluate(policy, event, [match("fan", event), match("other", event)])
    assert len(alerts) == 2, alerts
    for alert in alerts:
        assert alert["triggerContext"].get("basis") in BASES, alert


def test_afc_pr_037_opted_out_profile_never_gets_a_detection_basis(policy):
    """AFC-PR-037 negative: no detection-basis decision while opted out (labels per
    AFC-PR-011)."""
    seed_profile("fan", detectionOptIn=False)
    event = scoring("401999001404")
    alerts = evaluate(policy, event, [match("fan", event)])
    assert alerts, "the opted-out profile still has a labeled decision for this event"
    for alert in alerts:
        assert alert["triggerContext"].get("basis") == "profile-assumption", alert


def test_afc_pr_026_correction_revises_the_existing_alert(policy):
    """AFC-PR-026 policy half: a match carrying a cursor revises that alert in place."""
    seed_profile("fan")
    seed_alert("fan", "c-0007", past(5), event_id="401999001405")
    event = scoring("401999001405", revision=2, correction_of=1)
    alerts = evaluate(policy, event, [match("fan", event, cursor="c-0007")])
    assert len(alerts) == 1, alerts
    assert alerts[0]["cursor"] == "c-0007" and alerts[0]["revision"] == 2, alerts


def test_afc_pr_060_pending_serves_only_the_callers_alerts_in_order(policy):
    """AFC-PR-060: pending lists this profile's alerts, in cursor order, never another's."""
    seed_alert("fan", "c-0002", past(5), event_id="401999001412")
    seed_alert("fan", "c-0001", past(6), event_id="401999001411")
    seed_alert("other", "c-0003", past(5), event_id="401999001413")
    body = pending(policy, "fan")
    assert [alert.get("id") for alert in body["alerts"]] == ["c-0001", "c-0002"], body
    assert body["cursor"] == "c-0002"


def test_afc_pr_060_pending_resumes_after_the_cursor(policy):
    """AFC-PR-060: an alert already read is not served again."""
    seed_alert("fan", "c-0001", past(6), event_id="401999001421")
    seed_alert("fan", "c-0002", past(5), event_id="401999001422")
    body = pending(policy, "fan", "c-0001")
    assert [alert.get("id") for alert in body["alerts"]] == ["c-0002"], body
    again = pending(policy, "fan", body["cursor"])
    assert again["alerts"] == [] and again["cursor"] == "c-0002", again


def test_afc_pr_020_pending_holds_an_alert_until_its_release(policy):
    """AFC-PR-020 negative: no alert is delivered early, and the cursor never passes a
    held alert, so it is delivered once released."""
    seed_alert("fan", "c-0001", past(5), event_id="401999001431")
    seed_alert("fan", "c-0002", future(30), event_id="401999001432")
    body = pending(policy, "fan")
    assert [alert.get("id") for alert in body["alerts"]] == ["c-0001"], body
    assert body["cursor"] == "c-0001", "the cursor must not skip the held alert"


def test_afc_pr_027_pending_envelope_carries_the_alert(policy):
    """AFC-PR-027 / CONTRACT-AFC-P2-ENVELOPE: the served envelope carries the alert's
    type, trigger context, route and replay label."""
    route = {"provider": "Example", "channel": "EX", "route": "app", "accessBasis": "unknown"}
    stored = seed_alert("fan", "c-0001", past(5), event_id="401999001441", revision=3,
                        route=route, source="replay")
    body = pending(policy, "fan")
    assert len(body["alerts"]) == 1, body
    envelope = body["alerts"][0]
    assert envelope.get("schemaVersion") == 1
    assert envelope.get("id") == "c-0001"
    assert envelope.get("revision") == 3
    assert envelope.get("source") == "replay"
    assert envelope.get("updatedAt") == stored["emittedAt"]
    data = envelope.get("data")
    assert isinstance(data, dict), envelope
    assert data.get("alertType") == stored["alertType"]
    assert data.get("triggerContext") == stored["triggerContext"]
    assert data.get("route") == route


def test_afc_pr_060_alerts_api_serves_only_the_linked_profile(api, policy):
    """AFC-PR-060 through GET /v1/alerts: the linked device sees its own alerts only."""
    token = link_device(api, "fan")
    seed_alert("fan", "c-0001", past(5), event_id="401999001451")
    seed_alert("intruder", "c-0002", past(5), event_id="401999001452")
    status, body = api.request("GET", "/v1/alerts", token=token)
    assert status == 200, body
    assert [alert.get("id") for alert in body.get("alerts", [])] == ["c-0001"], body
