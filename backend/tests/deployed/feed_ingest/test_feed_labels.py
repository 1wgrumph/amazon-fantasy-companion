"""Deployed feed labels (SEIT-AFC-PR-013, SEIT-AFC-PR-012; L03 execution).

Panel values served from ingested or replayed events keep their source
label and monotonic revision end to end. Without AFC_DEPLOYED_API_URL these
skip (NOT_RUN) like every deployed case.
"""

from deployed_helpers import call


def test_panel_values_carry_a_source_label(linked):
    status, body = call(linked.base, "GET", "/v1/panel", token=linked.token)
    assert status == 200, body
    assert body.get("source") in ("live", "replay", "yahoo", "manual"), body


def test_panel_revision_never_moves_backwards(linked):
    _, first = call(linked.base, "GET", "/v1/panel", token=linked.token)
    _, second = call(linked.base, "GET", "/v1/panel", token=linked.token)
    assert isinstance(first.get("revision"), int), first
    assert second.get("revision", 0) >= first["revision"], (first, second)


def test_alerts_carry_the_envelope(linked):
    status, body = call(linked.base, "GET", "/v1/alerts", token=linked.token)
    assert status == 200, body
    for alert in body.get("data", {}).get("alerts", []):
        assert alert.get("source") in ("live", "replay"), alert
        assert isinstance(alert.get("revision"), int), alert
