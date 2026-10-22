"""NBA starter alerts from boxscore transitions (issue #137).

When a newer boxscore is stored, NbaIngest writes sport "nba" GameEvents for
point milestones (10/20/30), a new double-double, and a fantasy-point rise of
5 or more versus the previous record for that athlete and game. The existing
pipeline maps them to PlayerScore. Re-polling the same boxscore does not
duplicate. NBA off suppresses. An athlete outside the lineup does not alert.
An untagged NFL scoring play still alerts with its existing commentary.
"""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from boto3.dynamodb.types import TypeSerializer

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "nba"
GAME = "401999101"
GUARD, WING, CENTER = "9100001", "9100002", "9100003"
WHEN = "2026-10-21T00:00:00Z"
SETTINGS = {"alertTypes": ["RedZone", "PlayerScore", "CloseGame"], "frequency": 0,
            "quietHours": [], "gameDayPeriods": {"enabled": False, "periods": []},
            "spoilerDelay": 0, "excitement": "Mild", "detectionOptIn": False}


def _load():
    return json.loads((FIXTURES / "summary.json").read_text())


def _set(summary, athlete_id, **stats):
    for team in summary["boxscore"]["players"]:
        for category in team.get("statistics") or []:
            keys = category.get("keys") or []
            for entry in category.get("athletes") or []:
                if (entry.get("athlete") or {}).get("id") != athlete_id:
                    continue
                for name, value in stats.items():
                    entry["stats"][keys.index(name)] = str(value)
    return summary


def _summary():
    """Guard crosses 10, 20, a double-double and +13.2 fantasy; wing hits 30."""
    summary = _set(_load(), GUARD, points=20, rebounds=10)
    summary = _set(summary, WING, points=35, rebounds=2, assists=1, steals=0, blocks=0)
    return _set(summary, CENTER, points=4, rebounds=3, assists=1, steals=0, blocks=1)


def _prior(athlete_id, game_id, stats, as_of="2026-10-21T00:00:00Z"):
    import store
    assert store.put_player_statistics({
        "athleteId": athlete_id, "gameId": game_id, "gameState": "in",
        "gameStatus": "12:00 - 1st", "source": "live", "asOf": as_of,
        "stats": {key: Decimal(str(value)) for key, value in stats.items()}})


def _seed(profile_id, sports=None, athlete_id=GUARD):
    import store
    settings = dict(SETTINGS)
    if sports is not None:
        settings["sports"] = sports
    assert store.put_profile(profile_id, settings, 0, WHEN)
    store.put_lineup({
        "profileId": profile_id, "source": "manual", "sport": "nba",
        "team": "team-9", "league": "nba-league",
        "starters": [{"athlete_id": athlete_id, "name": "Sample Guard",
                      "team": "SHO", "slot": "PG"}],
        "updatedAt": WHEN})


def _poll(monkeypatch, summary):
    import nba
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    board = json.loads((FIXTURES / "scoreboard.json").read_text())

    def get_json(url):
        return board if url.endswith("scoreboard") else summary

    return nba.poll(get_json)


def _events(api):
    return api.table("Events").scan()["Items"]


def _deliver(events):
    import pipeline.handler
    serialize = TypeSerializer().serialize
    records = [{"eventName": "INSERT", "dynamodb": {"NewImage": {
        key: serialize(value) for key, value in event.items() if value is not None}}}
               for event in events]
    pipeline.handler.lambda_handler({"Records": records}, None)


def _alerts(api, profile_id):
    return [item for item in api.table("Alerts").scan()["Items"]
            if item.get("profileId") == profile_id]


def _phrases(alerts):
    return sorted(alert["triggerContext"]["matchup"] for alert in alerts)


@pytest.fixture
def crossed(api, monkeypatch):
    """Prior guard boxscore is same game and below the lines; wing's is another game."""
    _seed("hoops", sports={"nba": True, "nfl": True})
    _seed("nba-off", sports={"nba": False, "nfl": True})
    _prior(GUARD, GAME, {"points": 8, "rebounds": 9, "assists": 4, "steals": 1,
                         "blocks": 0, "turnovers": 2})
    _prior(WING, "401999100", {"points": 40, "rebounds": 12})
    summary = _summary()
    assert _poll(monkeypatch, summary)["stored"] == 3
    stored = _events(api)
    _deliver(stored)
    return stored


def test_milestone_and_swing_events_alert_the_lineup_starter(crossed, api):
    phrases = sorted(event["matchup"] for event in crossed
                     if GUARD in event["eventId"])
    assert phrases == ["+13.2 fantasy pts", "reaches 10 pts", "reaches 20 pts",
                       "reaches a double-double"]
    assert {event["sport"] for event in crossed} == {"nba"}
    assert all(event["scoringPlay"] is True for event in crossed)
    guard_ids = {f"{GAME}{GUARD}{code}" for code in ("10", "20", "40", "05")}
    assert guard_ids <= {event["eventId"] for event in crossed}
    alerts = _alerts(api, "hoops")
    assert _phrases(alerts) == phrases
    assert {alert["alertType"] for alert in alerts} == {"PlayerScore"}
    assert {tuple(alert["triggerContext"]["alertTypes"]) for alert in alerts} == {("PlayerScore",)}
    by_phrase = {alert["triggerContext"]["matchup"]: alert["commentary"] for alert in alerts}
    assert by_phrase["reaches 20 pts"] == "Sample Guard reaches 20 pts"
    assert by_phrase["+13.2 fantasy pts"] == "Sample Guard +13.2 fantasy pts"
    assert all("score on a play" not in (alert.get("commentary") or "") for alert in alerts)


def test_repoll_of_the_same_boxscore_does_not_duplicate(crossed, api, monkeypatch):
    before = sorted(event["eventId"] for event in crossed)
    assert before
    assert _poll(monkeypatch, _summary())["stored"] == 3
    again = _events(api)
    assert sorted(event["eventId"] for event in again) == before
    assert [int(event["revision"]) for event in again] == [1] * len(before)


def test_nba_off_suppresses_and_a_non_lineup_athlete_does_not_alert(crossed, api):
    assert _alerts(api, "hoops"), "lineup starter must alert when NBA is on"
    assert _alerts(api, "nba-off") == []
    wing_ids = {event["eventId"] for event in crossed if WING in event["eventId"]}
    assert wing_ids == {f"{GAME}{WING}{code}" for code in ("10", "20", "30")}
    alerted = {alert["eventId"] for alert in _alerts(api, "hoops")}
    assert wing_ids.isdisjoint(alerted)


def test_nfl_untagged_scoring_play_still_alerts(api, monkeypatch):
    import alert_policy
    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    import store
    assert store.put_profile("fan", dict(SETTINGS), 0, WHEN)
    event = {"gameId": "401999001", "eventId": "401999001771", "revision": 1,
             "source": "live", "score": {"away": 10, "home": 3}, "fieldPosition": 35,
             "possession": "PHI", "playerIds": ["9000001"], "eventTime": WHEN,
             "period": 2, "scoringPlay": True}
    match = {"profileId": "fan", "eventId": event["eventId"], "revision": 1,
             "starters": [{"athlete_id": "9000001", "name": "Sample Receiver",
                           "team": "PHI", "slot": "WR"}],
             "cursor": None}
    alerts = alert_policy.evaluate(event, [match])
    assert len(alerts) == 1
    assert alerts[0]["alertType"] == "PlayerScore"
    assert alerts[0]["commentary"] == "A score on a play listing your starter. Score 10-3."
    assert "sport" not in event


def test_nba_ingest_can_read_prior_stats_and_write_events():
    from conftest import document
    statements = document("template.yaml")["Resources"]["NbaIngestFunction"]["Properties"]["Policies"]
    found = []
    for policy in statements:
        found.extend(policy.get("Statement") or [])

    def allows(table, actions):
        for statement in found:
            if statement.get("Effect") != "Allow":
                continue
            action = statement.get("Action") or []
            action = action if isinstance(action, list) else [action]
            resource = json.dumps(statement.get("Resource"))
            if table in resource and set(actions) <= set(action):
                return True
        return False

    assert allows("EventsTable", ["dynamodb:GetItem", "dynamodb:PutItem"])
    assert allows("PlayerStatsTable", ["dynamodb:GetItem", "dynamodb:PutItem"])
