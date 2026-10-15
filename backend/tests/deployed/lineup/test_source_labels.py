"""Deployed lineup source labels (SEIT-AFC-PR-007, SEIT-AFC-PR-065; L03 execution).

The panel envelope carries the profile's one active lineup source; the
profile API persists the preset selection the manual source resolves.
Without AFC_DEPLOYED_API_URL these skip (NOT_RUN) like every deployed case.
"""

from deployed_helpers import call


def test_panel_reports_exactly_one_lineup_source(linked):
    status, body = call(linked.base, "GET", "/v1/panel", token=linked.token)
    assert status == 200, body
    assert body.get("source") in ("yahoo", "manual"), body


def test_panel_source_is_stable_across_reads(linked):
    _, first = call(linked.base, "GET", "/v1/panel", token=linked.token)
    _, second = call(linked.base, "GET", "/v1/panel", token=linked.token)
    assert first.get("source") in ("yahoo", "manual"), (first, second)
    assert second.get("source") == first.get("source"), (first, second)


def test_preset_selection_roundtrip(linked):
    status, body = call(linked.base, "GET", "/v1/profile", token=linked.token)
    assert status == 200, body
    for preset in ("ppr", "halfPpr"):
        status, body = call(linked.base, "PUT", "/v1/profile", token=linked.token,
                            body={"revision": body["revision"], "data": {"scoringPreset": preset}})
        assert status == 200, body
        status, body = call(linked.base, "GET", "/v1/profile", token=linked.token)
        assert status == 200 and body["data"].get("scoringPreset") == preset, body
