"""Deployed panel service (SEIT-AFC-PR-039/-040/-044/-046/-065; P2-L03/X09/X10 execution).

GET /v1/panel on the deployed stack serves the P2-B07 PanelState envelope:
every value with its scoring basis, unknown values null with a reason,
stale flags from source timestamps, settings reflected with a higher
revision, and game facts that agree with the alert records. Without
AFC_DEPLOYED_API_URL these skip (NOT_RUN) like every deployed case.
"""

from deployed_helpers import call

BASES = ("yahooLeague", "ppr", "halfPpr")


def panel(linked):
    status, body = call(linked.base, "GET", "/v1/panel", token=linked.token)
    assert status == 200, body
    for key in ("schemaVersion", "id", "revision", "source", "updatedAt", "data"):
        assert key in body, (key, body)
    return body


def values(data):
    for row in data.get("rows", []):
        yield row["points"]
    yield data["teamTotal"]
    yield data["progress"]


def test_panel_data_carries_basis_rows_and_value_objects(linked):
    data = panel(linked)["data"]
    assert isinstance(data.get("teamLeague"), str) and data["teamLeague"], data
    assert data.get("scoringBasis") in BASES, data
    assert isinstance(data.get("visible"), bool), data
    assert isinstance(data.get("rows"), list) and len(data["rows"]) <= 32, data
    assert isinstance(data.get("games"), dict), data
    for value in values(data):
        assert {"value", "reason", "source", "asOf", "stale"} <= set(value), value
        if value["value"] is None:
            assert isinstance(value["reason"], str) and value["reason"], value
        if value["asOf"] is None and value["value"] is not None:
            assert value["stale"] is True, value


def test_panel_rereads_keep_id_and_never_lower_revision(linked):
    first, second = panel(linked), panel(linked)
    assert second["id"] == first["id"], (first, second)
    assert second["revision"] >= first["revision"], (first, second)


def test_preset_change_reaches_the_panel(linked):
    status, profile = call(linked.base, "GET", "/v1/profile", token=linked.token)
    assert status == 200, profile
    original = dict(profile["data"])
    before = panel(linked)
    try:
        for preset in ("ppr", "halfPpr"):
            status, profile = call(linked.base, "PUT", "/v1/profile", token=linked.token, body={
                "revision": profile["revision"], "data": dict(original, scoringPreset=preset)})
            assert status == 200, profile
            after = panel(linked)
            expected = "yahooLeague" if before["source"] == "yahoo" else preset
            assert after["data"]["scoringBasis"] == expected, after
            if expected == preset:
                assert after["revision"] > before["revision"], (before, after)
            before = after
    finally:
        status, current = call(linked.base, "GET", "/v1/profile", token=linked.token)
        if status == 200:
            call(linked.base, "PUT", "/v1/profile", token=linked.token,
                 body={"revision": current["revision"], "data": original})


def test_panel_game_facts_agree_with_alerts(linked):
    status, body = call(linked.base, "GET", "/v1/alerts", token=linked.token)
    assert status == 200, body
    games = panel(linked)["data"]["games"]
    for alert in body.get("alerts", []):
        context = alert["data"]["triggerContext"]
        facts = games.get(context.get("gameId"))
        if facts is None or facts["eventId"] != context.get("eventId"):
            continue
        assert facts["revision"] >= alert["revision"], (facts, alert)
        if facts["revision"] == alert["revision"]:
            assert facts["score"] == context["score"], (facts, alert)
            assert facts["source"] == context["source"], (facts, alert)
