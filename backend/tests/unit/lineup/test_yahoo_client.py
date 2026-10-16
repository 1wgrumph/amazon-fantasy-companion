"""Yahoo read-only client red tests (VCASE-AFC-PR-001).

The client reads leagues, teams, rosters by week and league scoring settings
through recorded responses. Every request is an authenticated read; starting
slots come from the recorded slot facts, never from eligibility values.
Recorded payloads are synthetic fixtures under recorded/.
"""

import json
import secrets
from pathlib import Path

import pytest

from lineup_support import attempt, require_module

RECORDED = Path(__file__).resolve().parent / "recorded"
YAHOO_HOST = "https://fantasysports.yahooapis.com/"
LEAGUE_KEY = "nfl.l.1001"
TEAM_KEY = "nfl.l.1001.t.1"
BENCH_SLOTS = {"BN", "IR", "NA"}


def yahoo():
    return require_module("lineup.yahoo")


def recorded(name):
    return json.loads((RECORDED / name).read_text())


def token():
    return secrets.token_urlsafe(8)


class Recorder:
    """Recorded-response transport: serves fixtures by URL marker, audits requests."""

    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    def request(self, method, url, headers=None):
        self.calls.append({"method": method, "url": url, "headers": dict(headers or {})})
        for marker, payload in self.routes.items():
            if marker in url:
                return payload
        raise AssertionError(f"Yahoo client requested an unrecorded resource: {method} {url}")

    def assert_read_only(self, bearer):
        assert self.calls, "expected the client to issue Yahoo requests"
        for call in self.calls:
            assert call["method"] == "GET", f"client attempted a non-read call: {call}"
            assert call["url"].startswith(YAHOO_HOST), f"client left the Yahoo host: {call}"
            assert call["headers"].get("Authorization") == "Bearer " + bearer, call


class StrictRecorder(Recorder):
    """Refuses any write-scope call outright; the client must complete without one."""

    def request(self, method, url, headers=None):
        assert method == "GET", f"client attempted a write-scope call: {method} {url}"
        return super().request(method, url, headers)


def full_routes():
    return {"leagues": recorded("leagues.json"), "teams": recorded("teams.json"),
            "settings": recorded("settings.json"), "week=5": recorded("roster_week5.json"),
            "week=6": recorded("roster_week6.json")}


def drive_all(client, transport, bearer):
    leagues = attempt(client.get_leagues, transport, bearer)
    teams = attempt(client.get_teams, transport, bearer, LEAGUE_KEY)
    week5 = attempt(client.get_roster, transport, bearer, TEAM_KEY, 5)
    week6 = attempt(client.get_roster, transport, bearer, TEAM_KEY, 6)
    settings = attempt(client.get_settings, transport, bearer, LEAGUE_KEY)
    return leagues, teams, week5, week6, settings


def test_leagues_lists_the_recorded_leagues():
    transport = Recorder({"leagues": recorded("leagues.json")})
    leagues = attempt(yahoo().get_leagues, transport, token())
    assert [(entry["league_key"], entry["name"], entry["season"]) for entry in leagues] == [
        ("nfl.l.1001", "Red League Alpha", 2026), ("nfl.l.1002", "Red League Beta", 2026)]


def test_teams_lists_the_recorded_teams():
    transport = Recorder({"teams": recorded("teams.json")})
    teams = attempt(yahoo().get_teams, transport, token(), LEAGUE_KEY)
    assert [(entry["team_key"], entry["name"]) for entry in teams] == [
        ("nfl.l.1001.t.1", "Red Testers"), ("nfl.l.1001.t.2", "Synthetic Subs")]


@pytest.mark.parametrize("week", [5, 6])
def test_roster_distinguishes_starting_slots_from_bench(week):
    fixture = recorded(f"roster_week{week}.json")
    transport = Recorder({f"week={week}": fixture})
    roster = attempt(yahoo().get_roster, transport, token(), TEAM_KEY, week)
    assert roster["team_key"] == TEAM_KEY
    assert roster["week"] == week
    expected_starters = [p for p in fixture["players"] if p["slot"] not in BENCH_SLOTS]
    expected_bench = [p for p in fixture["players"] if p["slot"] in BENCH_SLOTS]
    assert [p["player_key"] for p in roster["starters"]] == [p["player_key"] for p in expected_starters]
    assert [p["player_key"] for p in roster["bench"]] == [p["player_key"] for p in expected_bench]
    assert [p["slot"] for p in roster["starters"]] == [p["slot"] for p in expected_starters]


def test_roster_weeks_are_independent():
    transport = Recorder({"week=5": recorded("roster_week5.json"),
                          "week=6": recorded("roster_week6.json")})
    client, bearer = yahoo(), token()
    week5 = attempt(client.get_roster, transport, bearer, TEAM_KEY, 5)
    week6 = attempt(client.get_roster, transport, bearer, TEAM_KEY, 6)
    starters5 = {p["player_key"] for p in week5["starters"]}
    starters6 = {p["player_key"] for p in week6["starters"]}
    assert starters5 != starters6
    assert "nfl.p.5007" in starters5 and "nfl.p.5007" not in starters6
    assert "nfl.p.5010" not in starters5 and "nfl.p.5010" in starters6


def test_settings_returns_the_league_scoring():
    transport = Recorder({"settings": recorded("settings.json")})
    settings = attempt(yahoo().get_settings, transport, token(), LEAGUE_KEY)
    assert settings["league_key"] == LEAGUE_KEY
    assert settings["stat_modifiers"]["receptions"] == 1.0
    assert settings["stat_modifiers"]["passing_yards"] == 0.04
    assert "FLEX" in settings["roster_slots"]


def test_client_issues_only_authenticated_reads():
    transport, bearer = Recorder(full_routes()), token()
    drive_all(yahoo(), transport, bearer)
    transport.assert_read_only(bearer)


def test_client_completes_when_writes_are_refused():
    transport, bearer = StrictRecorder(full_routes()), token()
    leagues, _, week5, _, _ = drive_all(yahoo(), transport, bearer)
    assert len(leagues) == 2 and len(week5["starters"]) == 9


def test_eligibility_is_never_used_as_a_starting_slot():
    fixture = recorded("roster_week5.json")
    transport = Recorder({"week=5": fixture})
    roster = attempt(yahoo().get_roster, transport, token(), TEAM_KEY, 5)
    recorded_slot = {p["player_key"]: p["slot"] for p in fixture["players"]}
    for entry in roster["starters"]:
        assert entry["slot"] == recorded_slot[entry["player_key"]]
        assert entry["slot"] not in BENCH_SLOTS
    bench_keys = {p["player_key"] for p in roster["bench"]}
    assert "nfl.p.5010" in bench_keys  # eligible RB/WR, recorded on the bench
    flex = [p for p in roster["starters"] if p["player_key"] == "nfl.p.5007"]
    assert len(flex) == 1 and flex[0]["slot"] == "FLEX"


@pytest.mark.parametrize("bad_token", ["", None])
def test_empty_token_is_rejected_before_any_request(bad_token):
    transport = Recorder(full_routes())
    with pytest.raises(ValueError):
        attempt(yahoo().get_roster, transport, bad_token, TEAM_KEY, 5)
    assert transport.calls == []


def test_non_integer_week_is_rejected_before_any_request():
    transport = Recorder(full_routes())
    with pytest.raises(ValueError):
        attempt(yahoo().get_roster, transport, token(), TEAM_KEY, "five")
    assert transport.calls == []


def test_roster_with_a_non_mapping_payload_is_rejected():
    transport = Recorder({"week=5": [{"not": "a roster"}]})
    with pytest.raises(ValueError):
        attempt(yahoo().get_roster, transport, token(), TEAM_KEY, 5)


def test_roster_missing_its_players_is_rejected():
    transport = Recorder({"week=5": {"team_key": TEAM_KEY, "week": 5}})
    with pytest.raises(ValueError):
        attempt(yahoo().get_roster, transport, token(), TEAM_KEY, 5)


def test_roster_with_a_non_mapping_player_is_rejected():
    payload = {"team_key": TEAM_KEY, "week": 5, "players": ["nfl.p.5001"]}
    with pytest.raises(ValueError):
        attempt(yahoo().get_roster, Recorder({"week=5": payload}), token(), TEAM_KEY, 5)


def test_roster_with_unexpected_player_types_is_rejected():
    payload = {"team_key": TEAM_KEY, "week": 5, "players": [
        {"player_key": "nfl.p.5001", "name": "Sample Quarterback", "team": "SYN",
         "positions": "QB", "slot": ["QB"]}]}
    with pytest.raises(ValueError):
        attempt(yahoo().get_roster, Recorder({"week=5": payload}), token(), TEAM_KEY, 5)


def test_settings_missing_its_modifiers_is_rejected():
    transport = Recorder({"settings": {"league_key": LEAGUE_KEY}})
    with pytest.raises(ValueError):
        attempt(yahoo().get_settings, transport, token(), LEAGUE_KEY)


def test_absurdly_oversize_roster_is_rejected():
    players = [{"player_key": f"nfl.p.{i}", "name": f"Generated Player {i}",
                "team": "SYN", "positions": ["BN"], "slot": "BN"} for i in range(20000)]
    payload = {"team_key": TEAM_KEY, "week": 5, "players": players}
    with pytest.raises(ValueError):
        attempt(yahoo().get_roster, Recorder({"week=5": payload}), token(), TEAM_KEY, 5)
