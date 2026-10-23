"""NBA Yahoo lineup import red tests (issue #137, M16 NBA stretch).

Behind AFC_ENABLE_NBA, nba.yahoo reads NBA leagues (Yahoo game code `nba`),
teams, a team roster by date (`roster;date=YYYY-MM-DD`, not `week`) and the
league stat_modifiers (Yahoo NBA stat ids) over the same injected transport
as lineup.yahoo. import_lineup stores the starters (BN/IL/IL+ excluded),
each mapped by name and team to an ESPN NBA athlete, with sport "nba" and
the league scoring as the yahooLeague basis, or nbaPoints when the league has
no fully mappable points modifiers. GET /v1/panel then carries "sport": "nba".
With the flag off nothing NBA is requested, returned, imported or served,
and the NFL Yahoo client is unchanged. Every payload is a synthetic fixture.
"""

import copy
import json
import secrets
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "nba"
YAHOO = FIXTURES / "yahoo"
NFL_RECORDED = Path(__file__).resolve().parents[1] / "lineup" / "recorded"
YAHOO_HOST = "https://fantasysports.yahooapis.com/"
LEAGUE_KEY, TEAM_KEY, DATE = "nba.l.2001", "nba.l.2001.t.3", "2026-10-21"
CATEGORY_LEAGUE = "nba.l.2002"
TEAM_LEAGUE = f"{LEAGUE_KEY}/{TEAM_KEY}"
GAME = "401999101"
GUARD, WING, CENTER = "9100001", "9100002", "9100003"
# Yahoo NBA stat ids 12 PTS, 15 REB, 16 AST, 17 ST, 18 BLK, 19 TO -> ESPN keys.
LEAGUE_TABLE = {"points": 1.0, "rebounds": 1.0, "assists": 2.0, "steals": 2.0,
                "blocks": 2.0, "turnovers": -0.5}
# settings_points.json: Guard 20+9+8+2+0-1, Wing 12+5+14+4+2-1.5, Center 8+12+2+0+6-0.5
LEAGUE_POINTS = {GUARD: 38.0, WING: 35.5, CENTER: 27.5}
# nba.scoring.NBA_POINTS_TABLE: Center 8+14.4+1.5+0+9-1
NBA_POINTS = {GUARD: 37.8, WING: 34.5, CENTER: 31.9}
NOW = "2026-10-21T00:05:30Z"


def load(path):
    return json.loads(path.read_text())


def token():
    return secrets.token_urlsafe(8)


def nba_on(monkeypatch):
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")


def nba_off(monkeypatch):
    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)


def nba_yahoo():
    """The module under test; a missing module is an assertion failure (behavioral red)."""
    import importlib

    try:
        return importlib.import_module("nba.yahoo")
    except ImportError as exc:
        raise AssertionError(f"NBA Yahoo import is not implemented: {exc}") from None


class Recorder:
    """Synthetic-response transport: first matching URL marker wins; audits calls."""

    def __init__(self, routes=None):
        self.routes = list((routes or {}).items())
        self.calls = []

    def request(self, method, url, headers=None):
        self.calls.append({"method": method, "url": url, "headers": dict(headers or {})})
        for marker, payload in self.routes:
            if marker in url:
                return copy.deepcopy(payload)
        raise AssertionError(f"unrecorded Yahoo resource: {method} {url}")

    def assert_read_only(self, bearer):
        assert self.calls, "expected Yahoo requests"
        for call in self.calls:
            assert call["method"] == "GET", call
            assert call["url"].startswith(YAHOO_HOST), call
            assert call["headers"].get("Authorization") == "Bearer " + bearer, call


def routes(settings="settings_points.json", roster=None):
    return {"roster;date=": roster or load(YAHOO / "roster_2026-10-21.json"),
            "/settings": load(YAHOO / settings),
            "/teams": load(YAHOO / "teams.json"),
            "/leagues": load(YAHOO / "leagues.json")}


def espn_roster():
    return load(YAHOO / "espn_roster.json")


# -- client reads (flag on) ---------------------------------------------------

def test_get_leagues_requests_the_nba_game_code_only(monkeypatch):
    nba_on(monkeypatch)
    bearer, transport = token(), Recorder(routes())
    leagues = nba_yahoo().get_leagues(transport, bearer)
    assert leagues == [
        {"league_key": "nba.l.2001", "name": "Synthetic Hoops Points", "season": 2026},
        {"league_key": "nba.l.2002", "name": "Synthetic Hoops Categories", "season": 2026}]
    transport.assert_read_only(bearer)
    assert [c["url"] for c in transport.calls] == [
        YAHOO_HOST + "fantasy/v2/users;use_login=1/games;game_keys=nba/leagues"]


def test_get_teams_lists_the_league_teams(monkeypatch):
    nba_on(monkeypatch)
    bearer, transport = token(), Recorder(routes())
    assert nba_yahoo().get_teams(transport, bearer, LEAGUE_KEY) == [
        {"team_key": "nba.l.2001.t.3", "name": "Synthetic Dunkers"},
        {"team_key": "nba.l.2001.t.4", "name": "Synthetic Rebounders"}]
    transport.assert_read_only(bearer)
    assert transport.calls[0]["url"] == YAHOO_HOST + f"fantasy/v2/league/{LEAGUE_KEY}/teams"


def test_get_roster_reads_by_date_and_excludes_bn_il_and_il_plus(monkeypatch):
    nba_on(monkeypatch)
    bearer, transport = token(), Recorder(routes())
    roster = nba_yahoo().get_roster(transport, bearer, TEAM_KEY, DATE)
    transport.assert_read_only(bearer)
    assert transport.calls[0]["url"] == YAHOO_HOST + f"fantasy/v2/team/{TEAM_KEY}/roster;date={DATE}"
    assert "week" not in transport.calls[0]["url"]
    assert roster["team_key"] == TEAM_KEY and roster["date"] == DATE
    assert [p["player_key"] for p in roster["starters"]] == ["nba.p.6001", "nba.p.6002", "nba.p.6003"]
    assert {p["slot"] for p in roster["bench"]} == {"BN", "IL", "IL+"}
    assert [p["player_key"] for p in roster["bench"]] == ["nba.p.6004", "nba.p.6005", "nba.p.6006"]
    center = roster["starters"][2]
    assert center == {"player_key": "nba.p.6003", "name": "Sample Center", "team": "SAW",
                      "positions": ["C"], "slot": "Util"}


@pytest.mark.parametrize("date", ["20261021", "2026-13-01", "2026-10-32", "10/21/2026",
                                  "", 20261021, None, "2026-10-21T00:00:00Z"])
def test_get_roster_refuses_a_non_calendar_date_before_requesting(monkeypatch, date):
    nba_on(monkeypatch)
    transport = Recorder(routes())
    with pytest.raises(ValueError):
        nba_yahoo().get_roster(transport, token(), TEAM_KEY, date)
    assert transport.calls == []


@pytest.mark.parametrize("field,value", [("team_key", "nba.l.2001.t.4"), ("date", "2026-10-22")])
def test_get_roster_refuses_a_response_for_another_team_or_date(monkeypatch, field, value):
    nba_on(monkeypatch)
    roster = dict(load(YAHOO / "roster_2026-10-21.json"), **{field: value})
    with pytest.raises(ValueError):
        nba_yahoo().get_roster(Recorder(routes(roster=roster)), token(), TEAM_KEY, DATE)


def test_get_roster_refuses_a_repeated_player_key(monkeypatch):
    nba_on(monkeypatch)
    roster = load(YAHOO / "roster_2026-10-21.json")
    roster["players"][1]["player_key"] = roster["players"][0]["player_key"]
    with pytest.raises(ValueError):
        nba_yahoo().get_roster(Recorder(routes(roster=roster)), token(), TEAM_KEY, DATE)


def test_get_settings_carries_yahoo_stat_ids_and_allows_a_category_league(monkeypatch):
    nba_on(monkeypatch)
    bearer, transport = token(), Recorder(routes())
    settings = nba_yahoo().get_settings(transport, bearer, LEAGUE_KEY)
    transport.assert_read_only(bearer)
    assert settings["league_key"] == LEAGUE_KEY
    assert settings["stat_modifiers"] == {"12": 1.0, "15": 1.0, "16": 2.0, "17": 2.0,
                                          "18": 2.0, "19": -0.5}
    assert "IL+" in settings["roster_slots"]
    categories = nba_yahoo().get_settings(
        Recorder(routes(settings="settings_categories.json")), bearer, CATEGORY_LEAGUE)
    assert categories["stat_modifiers"] == {}


def test_league_scoring_maps_yahoo_stat_ids_or_falls_back():
    client = nba_yahoo()
    points = load(YAHOO / "settings_points.json")["stat_modifiers"]
    assert client.league_scoring(points) == LEAGUE_TABLE
    assert client.league_scoring({}) is None  # category league: nbaPoints fallback
    # An id the ESPN boxscore keys cannot score (10 = 3PTM) is not silently dropped.
    assert client.league_scoring(dict(points, **{"10": 0.5})) is None


def test_get_calls_refuse_a_missing_token(monkeypatch):
    nba_on(monkeypatch)
    transport = Recorder(routes())
    with pytest.raises(ValueError):
        nba_yahoo().get_leagues(transport, "")
    with pytest.raises(ValueError):
        nba_yahoo().get_roster(transport, None, TEAM_KEY, DATE)
    assert transport.calls == []


# -- starter mapping ----------------------------------------------------------

def test_map_starters_adds_the_espn_athlete_by_name_and_team():
    roster = load(YAHOO / "roster_2026-10-21.json")["players"]
    starters = [p for p in roster if p["slot"] not in ("BN", "IL", "IL+")]
    unmatched = dict(starters[0], player_key="nba.p.6099", name="Sample Rookie")
    other_team = dict(starters[1], player_key="nba.p.6098", team="SAW")  # same name, other team
    mapped = nba_yahoo().map_starters(starters + [unmatched, other_team], espn_roster())
    assert [s["player_key"] for s in mapped] == [
        "nba.p.6001", "nba.p.6002", "nba.p.6003", "nba.p.6099", "nba.p.6098"]
    assert [s.get("athlete_id") for s in mapped] == [GUARD, WING, CENTER, None, None]
    assert mapped[0]["slot"] == "PG" and mapped[0]["name"] == "Sample Guard"


# -- import + panel (flag on) ---------------------------------------------------

@pytest.fixture
def nba_store(api, monkeypatch):
    """Moto tables, real store and panel, statistics seam from the ESPN NBA fixture."""
    import panel
    import store
    from nba.normalize import boxscore_statistics_nba

    summary = load(FIXTURES / "summary.json")
    records = {r["athleteId"]: {k: r[k] for k in ("gameId", "gameState", "gameStatus",
                                                   "source", "asOf", "stats")}
               for r in boxscore_statistics_nba(summary, GAME)}
    monkeypatch.setattr(panel, "player_statistics", records.get)
    monkeypatch.setattr(panel, "now", lambda: NOW)
    return store, panel


def rows(data):
    return {r["playerId"]: r for r in data["rows"]}


def test_import_stores_an_nba_yahoo_lineup_with_league_scoring(monkeypatch, nba_store):
    store, _ = nba_store
    nba_on(monkeypatch)
    bearer, transport = token(), Recorder(routes())
    nba_yahoo().import_lineup(transport, bearer, "hoops", LEAGUE_KEY, TEAM_KEY, DATE,
                              espn_roster())
    transport.assert_read_only(bearer)
    urls = [c["url"] for c in transport.calls]
    assert any(f"team/{TEAM_KEY}/roster;date={DATE}" in u for u in urls)
    assert any(f"league/{LEAGUE_KEY}/settings" in u for u in urls)
    row = store.get_lineup("hoops")
    assert row["sport"] == "nba"
    assert row["source"] == "yahoo"
    assert row["league"] == LEAGUE_KEY and row["team"] == TEAM_KEY
    assert [s["player_key"] for s in row["starters"]] == ["nba.p.6001", "nba.p.6002", "nba.p.6003"]
    assert [s["athlete_id"] for s in row["starters"]] == [GUARD, WING, CENTER]
    assert {k: float(v) for k, v in row["scoring"]["stat_modifiers"].items()} == LEAGUE_TABLE
    assert bearer not in json.dumps(row, default=str)  # the token is never stored


def test_panel_scores_the_imported_lineup_on_the_yahoo_league_basis(monkeypatch, nba_store):
    _, panel = nba_store
    nba_on(monkeypatch)
    nba_yahoo().import_lineup(Recorder(routes()), token(), "hoops", LEAGUE_KEY, TEAM_KEY,
                              DATE, espn_roster())
    data = panel.snapshot("hoops", TEAM_LEAGUE)["data"]
    assert data["scoringBasis"] == "yahooLeague"
    assert data["sport"] == "nba"
    got = rows(data)
    assert set(got) == {GUARD, WING, CENTER}
    for athlete, expected in LEAGUE_POINTS.items():
        assert got[athlete]["points"]["value"] == pytest.approx(expected, abs=0.005)
    assert got[CENTER]["name"] == "Sample Center"
    assert data["teamTotal"]["value"] == pytest.approx(sum(LEAGUE_POINTS.values()), abs=0.005)


def test_category_league_falls_back_to_nba_points(monkeypatch, nba_store):
    store, panel = nba_store
    nba_on(monkeypatch)
    nba_yahoo().import_lineup(Recorder(routes(settings="settings_categories.json")), token(),
                              "hoops", CATEGORY_LEAGUE, TEAM_KEY, DATE, espn_roster())
    assert store.get_lineup("hoops")["sport"] == "nba"
    data = panel.snapshot("hoops", f"{CATEGORY_LEAGUE}/{TEAM_KEY}")["data"]
    assert data["scoringBasis"] == "nbaPoints"
    assert data["sport"] == "nba"
    got = rows(data)
    for athlete, expected in NBA_POINTS.items():
        assert got[athlete]["points"]["value"] == pytest.approx(expected, abs=0.005)


def test_unmatched_starter_keeps_a_row_without_points(monkeypatch, nba_store):
    _, panel = nba_store
    nba_on(monkeypatch)
    roster = load(YAHOO / "roster_2026-10-21.json")
    roster["players"][2] = dict(roster["players"][2], name="Sample Rookie")
    nba_yahoo().import_lineup(Recorder(routes(roster=roster)), token(), "hoops", LEAGUE_KEY,
                              TEAM_KEY, DATE, espn_roster())
    data = panel.snapshot("hoops", TEAM_LEAGUE)["data"]
    rookie = rows(data)["nba.p.6003"]
    assert rookie["name"] == "Sample Rookie"
    assert rookie["points"]["value"] is None
    assert rookie["points"]["reason"] == "no matching ESPN athlete"
    # Owner design 2026-10-23: the total sums the known values and says it is partial.
    assert data["teamTotal"]["value"] is not None
    assert data["teamTotal"]["reason"] == "partial total"


def link(api, profile_id):
    """A device session for profile_id through the landed link API."""
    status, device = api.request("POST", "/v1/link")
    assert status in (200, 201), device
    status, _ = api.request("POST", "/v1/link/confirm", {"code": device["code"],
                                                          "profileId": profile_id})
    assert status == 200
    status, polled = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and polled.get("sessionToken"), polled
    return polled["sessionToken"]


def test_get_v1_panel_serves_sport_nba_for_an_nba_lineup(api, monkeypatch, nba_store):
    nba_on(monkeypatch)
    session = link(api, "hoops")
    nba_yahoo().import_lineup(Recorder(routes()), token(), "hoops", LEAGUE_KEY, TEAM_KEY,
                              DATE, espn_roster())
    status, body = api.request("GET", "/v1/panel", token=session,
                               query={"teamLeague": TEAM_LEAGUE})
    assert status == 200, body
    assert body["data"]["sport"] == "nba"
    assert body["data"]["scoringBasis"] == "yahooLeague"
    assert body["source"] == "yahoo"


# -- flag off negatives -----------------------------------------------------------

def test_flag_off_never_requests_or_returns_nba_leagues(monkeypatch):
    nba_off(monkeypatch)
    transport = Recorder(routes())
    assert nba_yahoo().get_leagues(transport, token()) == []
    assert transport.calls == []


@pytest.mark.parametrize("call", ["get_teams", "get_roster", "get_settings"])
def test_flag_off_refuses_every_nba_read_without_requesting(monkeypatch, call):
    nba_off(monkeypatch)
    transport = Recorder(routes())
    args = {"get_teams": (LEAGUE_KEY,), "get_roster": (TEAM_KEY, DATE),
            "get_settings": (LEAGUE_KEY,)}[call]
    with pytest.raises(ValueError):
        getattr(nba_yahoo(), call)(transport, token(), *args)
    assert transport.calls == []


def test_flag_off_cannot_import_an_nba_lineup(monkeypatch, nba_store):
    store, _ = nba_store
    nba_off(monkeypatch)
    transport = Recorder(routes())
    with pytest.raises(ValueError):
        nba_yahoo().import_lineup(transport, token(), "hoops", LEAGUE_KEY, TEAM_KEY, DATE,
                                  espn_roster())
    assert transport.calls == []
    assert store.get_lineup("hoops") is None


@pytest.mark.parametrize("flag", [None, "true"])
def test_nfl_yahoo_client_requests_only_the_nfl_game_code(monkeypatch, flag):
    from lineup import yahoo

    if flag is None:
        nba_off(monkeypatch)
    else:
        monkeypatch.setenv("AFC_ENABLE_NBA", flag)
    transport = Recorder({"/leagues": load(NFL_RECORDED / "leagues.json")})
    leagues = yahoo.get_leagues(transport, token())
    assert [c["url"] for c in transport.calls] == [
        YAHOO_HOST + "fantasy/v2/users;use_login=1/games;game_keys=nfl/leagues"]
    assert all(not league["league_key"].startswith("nba.") for league in leagues)


@pytest.mark.parametrize("flag", [None, "true"])
def test_nfl_panel_never_carries_a_sport_key(monkeypatch, nba_store, flag):
    store, panel = nba_store
    if flag is None:
        nba_off(monkeypatch)
    else:
        monkeypatch.setenv("AFC_ENABLE_NBA", flag)
    store.put_lineup({"profileId": "gridiron", "source": "manual", "team": "team-7",
                      "league": "league-a", "updatedAt": "2026-10-20T22:00:00Z",
                      "starters": [{"athlete_id": "9000001", "name": "Sample Receiver",
                                    "team": "SYN", "slot": "WR"}]})
    data = panel.snapshot("gridiron", "league-a/team-7")["data"]
    assert "sport" not in data
