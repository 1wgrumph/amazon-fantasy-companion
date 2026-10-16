"""P2-B03 review F1-F4/A1-A2: input validation and exact contract boundaries."""

from decimal import Decimal

import pytest
from boto3.dynamodb.types import TypeDeserializer

from lineup import manual, presets, yahoo
from test_active_lineup import active, seed_lineup, YAHOO_STARTERS
from test_yahoo_client import Recorder, recorded, LEAGUE_KEY, TEAM_KEY


@pytest.mark.parametrize("athlete_id", [[], {}])
def test_manual_unhashable_athlete_id_is_value_error(athlete_id):
    roster = [{"athlete_id": "espn.1", "name": "A", "team": "SYN"}]
    with pytest.raises(ValueError):
        manual.build(roster, [{"athlete_id": athlete_id, "slot": "QB"}], "PPR")


def test_manual_espn_roster_at_size_limit_is_accepted():
    roster = [{"athlete_id": f"espn.{i}", "name": "A", "team": "SYN"} for i in range(200)]
    assert manual.build(roster, [], "PPR")["starters"] == []


def test_manual_oversize_espn_roster_is_rejected_without_duplicates():
    roster = [{"athlete_id": f"espn.{i}", "name": "A", "team": "SYN"} for i in range(201)]
    with pytest.raises(ValueError):
        manual.build(roster, [], "PPR")


def test_yahoo_week_one_is_accepted():
    payload = dict(recorded("roster_week5.json"), week=1)
    transport = Recorder({"week=1": payload})
    roster = yahoo.get_roster(transport, "synthetic-token", TEAM_KEY, 1)
    assert roster["week"] == 1
    assert transport.calls[0]["url"] == (
        "https://fantasysports.yahooapis.com/fantasy/v2/team/" + TEAM_KEY + "/roster;week=1")
    transport.assert_read_only("synthetic-token")


def test_yahoo_leagues_url_is_exact():
    transport = Recorder({"leagues": recorded("leagues.json")})
    assert yahoo.get_leagues(transport, "synthetic-token") == [
        {field: league[field] for field in ("league_key", "name", "season")}
        for league in recorded("leagues.json")["leagues"]]
    assert transport.calls[0]["url"] == (
        "https://fantasysports.yahooapis.com/fantasy/v2/"
        "users;use_login=1/games;game_keys=nfl/leagues")
    transport.assert_read_only("synthetic-token")


@pytest.mark.parametrize("field", ["stat_modifiers", "roster_slots"])
def test_yahoo_settings_at_size_limit_is_accepted(field):
    payload = recorded("settings.json")
    payload[field] = ({f"stat_{i}": 1 for i in range(200)} if field == "stat_modifiers"
                      else ["BN"] * 200)
    assert yahoo.get_settings(Recorder({"settings": payload}), "synthetic-token", LEAGUE_KEY)[
        field] == payload[field]


@pytest.mark.parametrize("field", ["stat_modifiers", "roster_slots"])
def test_yahoo_settings_above_size_limit_is_rejected(field):
    payload = recorded("settings.json")
    payload[field] = ({f"stat_{i}": 1 for i in range(201)} if field == "stat_modifiers"
                      else ["BN"] * 201)
    with pytest.raises(ValueError):
        yahoo.get_settings(Recorder({"settings": payload}), "synthetic-token", LEAGUE_KEY)


@pytest.mark.parametrize("key", [".", "..", ".nfl.l.1", "nfl..l.1", "nfl.l.1."])
def test_yahoo_empty_dot_segments_are_rejected_before_request(key):
    transport = Recorder({"teams": recorded("teams.json")})
    with pytest.raises(ValueError):
        yahoo.get_teams(transport, "synthetic-token", key)
    with pytest.raises(ValueError):
        yahoo.get_settings(transport, "synthetic-token", key)
    with pytest.raises(ValueError):
        yahoo.get_roster(transport, "synthetic-token", key, 1)
    assert transport.calls == []


def test_yahoo_valid_dot_separated_keys_are_accepted():
    transport = Recorder({"teams": recorded("teams.json"),
                          "week=5": dict(recorded("roster_week5.json"), team_key="449.l.1.t.3")})
    assert yahoo.get_teams(transport, "synthetic-token", "nfl.l.12345")
    assert yahoo.get_roster(transport, "synthetic-token", "449.l.1.t.3", 5)[
        "team_key"] == "449.l.1.t.3"
    assert transport.calls[0]["url"].endswith("/league/nfl.l.12345/teams")
    assert transport.calls[1]["url"].endswith("/team/449.l.1.t.3/roster;week=5")
    transport.assert_read_only("synthetic-token")


@pytest.mark.parametrize("scoring", [{"preset": "PPR"},
                                     {"preset": "Half-PPR", "stat_modifiers": {"receptions": 1}}])
def test_stored_yahoo_scoring_rejects_manual_preset(api, scoring):
    seed_lineup("yahoo", YAHOO_STARTERS, scoring=scoring)
    with pytest.raises(ValueError):
        active()


@pytest.mark.parametrize(("preset", "expected"), [("PPR", 36.0), ("Half-PPR", 33.5)])
def test_dynamodb_decimal_stats_score_like_int_and_float(preset, expected):
    stats = {"receptions": 5, "receiving_yards": 80, "receiving_touchdowns": 1,
             "rushing_yards": 20, "passing_yards": 250, "passing_touchdowns": 2,
             "interceptions_thrown": 1, "fumbles_lost": 1, "rushing_touchdowns": 0}
    deserializer = TypeDeserializer()
    stored = {stat: deserializer.deserialize({"N": str(value)}) for stat, value in stats.items()}
    assert all(isinstance(value, Decimal) for value in stored.values())
    assert presets.score(preset, stored) == presets.score(preset, stats) == presets.score(
        preset, {stat: float(value) for stat, value in stats.items()}) == expected
