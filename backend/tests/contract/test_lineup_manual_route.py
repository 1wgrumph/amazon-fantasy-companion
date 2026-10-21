"""BUG AFC-LINEUP-MANUAL-ROUTE: PUT /v1/lineup/manual red contract cases.

AC-AFC-PROF-04 / C6: without Yahoo approval the device writes a labeled manual
lineup built from an ESPN roster. The bearer device session scopes the write
to its own profile; the body never selects another profile. Validation reuses
lineup.manual / nba.manual limits (200 roster entries, 32 starters).

Request body: {"sport"?: "nfl"|"nba", "league", "team", "preset" (nfl only),
"roster": [{athlete_id, name, team}], "entries": [{athlete_id, slot}]}.
"""

import re

import pytest

from conftest import assert_error, document, link_device

pytestmark = pytest.mark.contract
PATH = "/v1/lineup/manual"
ROSTER = [
    {"athlete_id": "9000001", "name": "Sample Receiver", "team": "PHI"},
    {"athlete_id": "9000002", "name": "Sample Runner", "team": "PHI"},
    {"athlete_id": "9000003", "name": "Sample Passer", "team": "JAX"},
]
ENTRIES = [{"athlete_id": "9000001", "slot": "WR"}, {"athlete_id": "9000002", "slot": "RB"}]


def body(**overrides):
    value = {"league": "league-a", "team": "team-7", "preset": "Half-PPR",
             "roster": ROSTER, "entries": ENTRIES}
    value.update(overrides)
    return {k: v for k, v in value.items() if v is not None}


def lineups(api):
    return api.table("Lineups").scan()["Items"]


def test_write_stores_the_token_profile_manual_lineup_and_returns_its_envelope(api):
    import store
    _, token = link_device(api)
    status, data = api.request("PUT", PATH, body(), token=token)
    assert status == 200, data
    assert {"schemaVersion", "id", "revision", "source", "updatedAt", "data"} <= set(data)
    assert data["id"] == "owner" and data["source"] == "manual"
    assert type(data["revision"]) is int and data["revision"] >= 1
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", data["updatedAt"])
    assert data["data"]["label"] == "Manual lineup"
    assert data["data"]["source"] == "manual"
    assert data["data"]["scoring"] == {"preset": "Half-PPR"}
    assert [s["athlete_id"] for s in data["data"]["starters"]] == ["9000001", "9000002"]
    stored = store.get_lineup("owner")
    assert stored["source"] == "manual" and stored["league"] == "league-a"
    assert stored["team"] == "team-7"
    assert stored["starters"] == [
        {"athlete_id": "9000001", "name": "Sample Receiver", "team": "PHI", "slot": "WR"},
        {"athlete_id": "9000002", "name": "Sample Runner", "team": "PHI", "slot": "RB"}]
    assert data["revision"] == store.get_lineup_version("owner")


def test_after_a_write_the_panel_serves_rows_for_those_starters(api):
    _, token = link_device(api)
    status, data = api.request("PUT", PATH, body(), token=token)
    assert status == 200, data
    status, panel = api.request("GET", "/v1/panel", token=token)
    assert status == 200, panel
    rows = panel["data"]["rows"]
    assert [(r["playerId"], r["name"]) for r in rows] == [
        ("9000001", "Sample Receiver"), ("9000002", "Sample Runner")]


@pytest.mark.parametrize("token", [None, "not-a-session-token"])
def test_missing_or_invalid_token_is_401_and_writes_nothing(api, token):
    link_device(api)
    status, data = api.request("PUT", PATH, body(), token=token)
    assert_error(status, data, 401, "unauthenticated")
    assert lineups(api) == []


@pytest.mark.parametrize("where", ["body", "query"])
def test_a_named_other_profile_cannot_be_written(api, where):
    import store
    _, token = link_device(api, profile="owner")
    link_device(api, profile="victim")
    request = body(profileId="victim") if where == "body" else body()
    query = {"profileId": "victim"} if where == "query" else None
    status, data = api.request("PUT", PATH, request, token=token, query=query)
    assert_error(status, data, 403, "forbidden")
    assert store.get_lineup("victim") is None and store.get_lineup("owner") is None


ROSTER_201 = [{"athlete_id": str(9100000 + i), "name": f"P{i}", "team": "PHI"}
              for i in range(201)]
ENTRIES_33 = [{"athlete_id": p["athlete_id"], "slot": "BN"} for p in ROSTER_201[:33]]


@pytest.mark.parametrize("raw", [
    "{", "[]", '"text"',
    # unknown player, duplicate player, bad roster team, bad entry shape
    body(entries=[{"athlete_id": "9999999", "slot": "WR"}]),
    body(entries=[{"athlete_id": "9000001", "slot": "WR"}, {"athlete_id": "9000001", "slot": "FLEX"}]),
    body(roster=[{"athlete_id": "9000001", "name": "Sample Receiver", "team": "phi!"}]),
    body(entries=[{"athlete_id": "9000001"}]),
    body(entries="9000001"), body(roster=None), body(entries=None),
    # bounds from lineup.manual
    body(roster=ROSTER_201, entries=ENTRIES_33[:1]),
    body(roster=ROSTER_201[:40], entries=ENTRIES_33),
    # preset and team/league selectors
    body(preset="Standard"), body(preset=7),
    body(league=None), body(team=None), body(team=""), body(league=["league-a"]),
    body(sport="mlb"),
], ids=lambda raw: raw if isinstance(raw, str) else None)
def test_malformed_or_invalid_body_is_400_and_writes_nothing(api, raw):
    _, token = link_device(api)
    if isinstance(raw, str):
        status, data = api.request("PUT", PATH, token=token, raw=raw)
    else:
        status, data = api.request("PUT", PATH, raw, token=token)
    assert_error(status, data, 400, "invalid_request")
    assert lineups(api) == []


def test_33_starters_is_rejected_but_32_is_accepted(api):
    _, token = link_device(api)
    roster = ROSTER_201[:40]
    entries = [{"athlete_id": p["athlete_id"], "slot": "BN"} for p in roster[:32]]
    status, data = api.request("PUT", PATH, body(roster=roster, entries=entries), token=token)
    assert status == 200, data
    assert len(data["data"]["starters"]) == 32


def test_body_over_64_kib_is_rejected_before_any_lineup_write(api):
    # Guard regression: the router's raw-size check runs before route lookup.
    _, token = link_device(api)
    raw = '{"padding":"' + "x" * 65536 + '"}'
    status, data = api.request("PUT", PATH, token=token, raw=raw)
    assert_error(status, data, 400, "payload_too_large")
    assert lineups(api) == []


def test_a_rewrite_replaces_the_lineup_and_advances_the_revision(api):
    import store
    _, token = link_device(api)
    status, first = api.request("PUT", PATH, body(), token=token)
    assert status == 200, first
    status, second = api.request(
        "PUT", PATH, body(entries=[{"athlete_id": "9000003", "slot": "QB"}]), token=token)
    assert status == 200, second
    assert second["revision"] > first["revision"]
    assert [s["athlete_id"] for s in store.get_lineup("owner")["starters"]] == ["9000003"]


def test_nba_manual_lineup_is_labeled_manual_and_sport_nba_when_enabled(api, monkeypatch):
    import store
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    _, token = link_device(api)
    request = body(sport="nba", preset=None,
                   roster=[{"athlete_id": "4000001", "name": "Sample Guard", "team": "BOS"}],
                   entries=[{"athlete_id": "4000001", "slot": "G"}])
    status, data = api.request("PUT", PATH, request, token=token)
    assert status == 200, data
    assert data["source"] == "manual" and data["data"]["label"] == "Manual lineup"
    assert data["data"]["sport"] == "nba"
    stored = store.get_lineup("owner")
    assert stored["source"] == "manual" and stored["sport"] == "nba"
    assert stored["starters"][0]["athlete_id"] == "4000001"


def test_nba_manual_lineup_is_400_while_the_nba_flag_is_off(api, monkeypatch):
    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    _, token = link_device(api)
    request = body(sport="nba", preset=None,
                   roster=[{"athlete_id": "4000001", "name": "Sample Guard", "team": "BOS"}],
                   entries=[{"athlete_id": "4000001", "slot": "G"}])
    status, data = api.request("PUT", PATH, request, token=token)
    assert_error(status, data, 400, "invalid_request")
    assert lineups(api) == []


def test_openapi_declares_the_bearer_protected_manual_lineup_put():
    doc = document("src/api/openapi.yaml")
    operation = doc["paths"][PATH]["put"]
    schemes = doc["components"]["securitySchemes"]
    bearer = {name for name, value in schemes.items()
              if value.get("type") == "http" and value.get("scheme", "").lower() == "bearer"}
    security = operation.get("security", doc.get("security", []))
    assert security and all(set(option) & bearer for option in security)
    assert {"200", "400", "401", "403"} <= set(map(str, operation["responses"]))
