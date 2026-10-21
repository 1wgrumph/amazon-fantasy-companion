"""Per-sport notification toggle red tests (issue #137, M16 NBA stretch).

Contract for the Implementer (flag AFC_ENABLE_NBA, the only switch):
- Settings field `sports`: an object whose keys are a subset of {"nfl", "nba"}
  and whose values are JSON booleans. A missing field or a missing key means ON,
  so NFL defaults on and NBA defaults on with the flag on; GET /v1/profile
  injects no default. Flag on: PUT /v1/profile accepts a valid `sports` and
  rejects any other shape with 400 invalid_request. Flag off: `sports` is an
  unknown field, rejected exactly as today.
- An event's sport is game_event["sport"] when present, else "nfl" (every
  event ingested today is NFL and carries no sport). Flag on:
  alert_policy.evaluate emits no new alert for a profile whose sports[sport]
  is False. Flag off: a stored `sports` value is ignored.
- A lineup's sport is lineup["sport"] when present, else "nfl". Flag on:
  panel.snapshot serves no rows (and an unknown team total) for a lineup whose
  sport is off. Flag off: a stored `sports` value is ignored.
- An NBA alert while watching NFL is intended and is not tested as a defect.
"""

import pytest

KICKOFF = "2026-10-18T20:00:00Z"
NFL_STARTER = {"athlete_id": "9000001", "name": "Sample Receiver", "team": "PHI", "slot": "WR"}
NBA_STARTER = {"athlete_id": "9100001", "name": "Sample Guard", "team": "SHO", "slot": "PG"}
BASE_SETTINGS = {"alertTypes": ["RedZone", "PlayerScore", "CloseGame"], "frequency": 0,
                 "quietHours": [], "gameDayPeriods": {"enabled": False, "periods": []},
                 "spoilerDelay": 0, "excitement": "Off", "detectionOptIn": False}


@pytest.fixture
def flag(monkeypatch):
    """Set AFC_ENABLE_NBA after the api fixture has loaded the template environment."""
    def set_flag(on):
        if on:
            monkeypatch.setenv("AFC_ENABLE_NBA", "true")
        else:
            monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    return set_flag


def seed_profile(profile_id, sports=None):
    import store
    settings = dict(BASE_SETTINGS)
    if sports is not None:
        settings["sports"] = sports
    assert store.put_profile(profile_id, settings, 0, KICKOFF), "profile seed"


def scoring_event(event_id, sport=None):
    """A scoring play listing the matched starter; sport None is today's untagged (NFL) event."""
    event = {"gameId": "401999001", "eventId": event_id, "revision": 1, "correctionOf": None,
             "source": "live", "score": {"away": 10, "home": 3}, "fieldPosition": 35,
             "possession": "PHI", "playerIds": ["9000001"], "eventTime": KICKOFF,
             "period": 2, "scoringPlay": True}
    if sport is not None:
        event["sport"] = sport
    return event


def alerts_for(profile_id, event):
    import alert_policy
    match = {"profileId": profile_id, "eventId": event["eventId"], "revision": 1,
             "starters": [dict(NFL_STARTER)], "cursor": None}
    return [a for a in alert_policy.evaluate(event, [match]) if a["profileId"] == profile_id]


# Alert policy, flag on.

@pytest.mark.parametrize("sport", [None, "nfl", "nba"], ids=["untagged", "nfl", "nba"])
def test_every_sport_alerts_by_default(api, flag, sport):
    flag(True)
    seed_profile("fan")
    assert len(alerts_for("fan", scoring_event("401999001001", sport))) == 1


@pytest.mark.parametrize("sport", [None, "nfl"], ids=["untagged", "nfl"])
def test_nfl_off_suppresses_nfl_alerts(api, flag, sport):
    flag(True)
    seed_profile("fan", sports={"nfl": False, "nba": True})
    assert alerts_for("fan", scoring_event("401999001002", sport)) == [], \
        "Missing behavior: NFL off suppresses NFL (and untagged) alerts"


def test_nba_off_suppresses_alerts_tagged_nba(api, flag):
    flag(True)
    seed_profile("fan", sports={"nfl": True, "nba": False})
    assert alerts_for("fan", scoring_event("401999001003", "nba")) == [], \
        "Missing behavior: NBA off suppresses alerts tagged sport nba"


def test_one_sport_off_leaves_the_other_alerting(api, flag):
    flag(True)
    seed_profile("nba-off", sports={"nba": False})
    seed_profile("nfl-off", sports={"nfl": False})
    assert len(alerts_for("nba-off", scoring_event("401999001004"))) == 1
    assert len(alerts_for("nfl-off", scoring_event("401999001005", "nba"))) == 1


def test_a_missing_sport_key_defaults_on(api, flag):
    flag(True)
    seed_profile("fan", sports={"nba": False})
    assert len(alerts_for("fan", scoring_event("401999001006", "nfl"))) == 1


# Alert policy, flag off: byte-identical to today.

@pytest.mark.parametrize("sport", [None, "nba"], ids=["untagged", "nba"])
def test_flag_off_ignores_a_stored_sports_value_for_alerts(api, flag, sport):
    flag(False)
    seed_profile("toggled", sports={"nfl": False, "nba": False})
    seed_profile("plain")
    toggled = alerts_for("toggled", scoring_event("401999001007", sport))
    plain = alerts_for("plain", scoring_event("401999001007", sport))
    assert len(plain) == 1
    assert [dict(a, profileId=None) for a in toggled] == [dict(a, profileId=None) for a in plain]


# Panel.

@pytest.fixture
def panel_seams(api, monkeypatch):
    import panel
    monkeypatch.setattr(panel, "player_statistics", lambda athlete_id: None)
    monkeypatch.setattr(panel, "now", lambda: "2026-10-18T20:05:00Z")
    return panel


def seed_lineup(profile_id, sport=None):
    import store
    row = {"profileId": profile_id, "source": "manual", "team": "team-7", "league": "league-a",
           "starters": [dict(NBA_STARTER if sport == "nba" else NFL_STARTER)],
           "updatedAt": KICKOFF}
    if sport is not None:
        row["sport"] = sport
    store.put_lineup(row)


def toggle(profile_id, sports):
    import store
    current = store.get_profile(profile_id)
    settings = dict(current.get("settings") or {}, sports=sports)
    assert store.put_profile(profile_id, settings, int(current["revision"]), KICKOFF)


def test_nba_off_hides_nba_panel_rows(panel_seams, flag):
    flag(True)
    seed_profile("hoops", sports={"nfl": True, "nba": False})
    seed_lineup("hoops", "nba")
    data = panel_seams.snapshot("hoops", "league-a/team-7")["data"]
    assert data["rows"] == [], "Missing behavior: NBA off hides NBA panel rows"
    assert data["teamTotal"]["value"] is None


def test_nfl_off_hides_nfl_panel_rows_and_on_again_restores_them(panel_seams, flag):
    flag(True)
    seed_profile("fan")
    seed_lineup("fan")
    shown = panel_seams.snapshot("fan", "league-a/team-7")
    assert [r["playerId"] for r in shown["data"]["rows"]] == ["9000001"]
    toggle("fan", {"nfl": False, "nba": True})
    hidden = panel_seams.snapshot("fan", "league-a/team-7")
    assert hidden["data"]["rows"] == [], "Missing behavior: NFL off hides NFL panel rows"
    assert hidden["data"]["teamTotal"]["value"] is None
    assert hidden["revision"] > shown["revision"]
    toggle("fan", {"nfl": True, "nba": True})
    again = panel_seams.snapshot("fan", "league-a/team-7")
    assert again["data"]["rows"] == shown["data"]["rows"]
    assert again["revision"] > hidden["revision"]


def test_the_other_sport_off_keeps_panel_rows(panel_seams, flag):
    flag(True)
    seed_profile("fan", sports={"nba": False})
    seed_lineup("fan")
    seed_profile("hoops", sports={"nfl": False})
    seed_lineup("hoops", "nba")
    assert len(panel_seams.snapshot("fan", "league-a/team-7")["data"]["rows"]) == 1
    assert len(panel_seams.snapshot("hoops", "league-a/team-7")["data"]["rows"]) == 1


@pytest.mark.parametrize("sport", [None, "nba"], ids=["nfl-lineup", "nba-lineup"])
def test_flag_off_ignores_a_stored_sports_value_for_the_panel(panel_seams, flag, sport):
    flag(False)
    seed_profile("toggled", sports={"nfl": False, "nba": False})
    seed_lineup("toggled", sport)
    seed_profile("plain")
    seed_lineup("plain", sport)
    toggled = panel_seams.snapshot("toggled", "league-a/team-7")
    plain = panel_seams.snapshot("plain", "league-a/team-7")
    assert toggled["data"] == plain["data"]
    assert toggled["revision"] == plain["revision"]
    assert len(plain["data"]["rows"]) == 1


# Profile API.

def linked(api):
    status, device = api.request("POST", "/v1/link")
    assert status in (200, 201), device
    status, _ = api.request("POST", "/v1/link/confirm", {"code": device["code"], "profileId": "owner"})
    assert status == 200
    status, polled = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and polled.get("sessionToken"), polled
    return polled["sessionToken"]


def put_profile(api, token, data):
    return api.request("PUT", "/v1/profile", {"revision": 0, "data": data}, token=token)


@pytest.mark.parametrize("sports", [{"nfl": True, "nba": False}, {"nfl": False}, {}],
                         ids=["both", "nfl-only", "empty"])
def test_flag_on_profile_accepts_and_returns_sports(api, flag, sports):
    flag(True)
    token = linked(api)
    status, body = put_profile(api, token, {"scoringPreset": "halfPpr", "sports": sports})
    assert status == 200, f"Missing behavior: flag on accepts Settings.sports: {body}"
    status, body = api.request("GET", "/v1/profile", token=token)
    assert status == 200 and body["data"]["sports"] == sports


@pytest.mark.parametrize("sports", [{"mlb": True}, {"nba": "off"}, {"nba": 1}, {"nfl": None},
                                    ["nfl"], "nfl", None],
                         ids=["unknown-sport", "string", "int", "null", "list", "text", "none"])
def test_flag_on_profile_rejects_malformed_sports(api, flag, sports):
    flag(True)
    token = linked(api)
    status, body = put_profile(api, token, {"sports": sports})
    assert status == 400 and body["error"]["code"] == "invalid_request", body


def test_flag_on_default_profile_injects_no_sports(api, flag):
    flag(True)
    status, body = api.request("GET", "/v1/profile", token=linked(api))
    assert status == 200 and body["data"] == {"scoringPreset": "halfPpr"}


def test_flag_off_profile_rejects_sports_as_today(api, flag):
    flag(False)
    token = linked(api)
    status, body = put_profile(api, token, {"sports": {"nfl": True, "nba": True}})
    assert status == 400 and body["error"]["code"] == "invalid_request", body
    status, body = api.request("GET", "/v1/profile", token=token)
    assert status == 200 and body["revision"] == 0 and "sports" not in body["data"]
