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
    summary = _set(summary, WING, points=30, rebounds=2, assists=1, steals=0, blocks=0)
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
    """Both athletes have observed same-game baselines, but only guard is a starter."""
    _seed("hoops", sports={"nba": True, "nfl": True})
    _seed("nba-off", sports={"nba": False, "nfl": True})
    _prior(GUARD, GAME, {"points": 8, "rebounds": 9, "assists": 4, "steals": 1,
                         "blocks": 0, "turnovers": 2})
    _prior(WING, GAME, {"points": 29, "rebounds": 2, "assists": 1, "steals": 0,
                       "blocks": 0, "turnovers": 3})
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
    guard_ids = {f"{GAME}00000001{GUARD}{code}" for code in ("10", "20", "40", "05")}
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
    assert wing_ids == {f"{GAME}00000001{WING}30"}
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

    assert allows("EventsTable", ["dynamodb:PutItem"])
    assert allows("PlayerStatsTable", ["dynamodb:GetItem", "dynamodb:PutItem"])


def _observation(points, second, **stats):
    summary = _load()
    for athlete in (GUARD, WING, CENTER):
        _set(summary, athlete, points=0, rebounds=0, assists=0, steals=0,
             blocks=0, turnovers=0)
    _set(summary, GUARD, points=points, **stats)
    for play in summary["plays"]:
        play["wallclock"] = f"2026-10-21T00:00:{second:02d}Z"
    return summary


def _guard_events(api):
    return [event for event in _events(api) if event["playerIds"] == [GUARD]]


@pytest.mark.parametrize("same_clock", [False, True])
def test_r01_distinct_swings_are_deliverable_after_a_milestone(api, monkeypatch, same_clock):
    import alert_policy
    import provider_resolver
    _seed("hoops", sports={"nba": True})
    _poll(monkeypatch, _observation(0, 0))
    for points, second in ((5, 1), (10, 2)):
        _poll(monkeypatch, _observation(points, 1 if same_clock else second))
        _deliver(_events(api))
    cursor = max(alert["cursor"] for alert in _alerts(api, "hoops"))
    latest = _observation(15, 1 if same_clock else 3)
    _poll(monkeypatch, latest)
    _deliver(_events(api))
    swings = [alert for alert in _alerts(api, "hoops")
              if "fantasy" in alert["commentary"]]
    assert len(swings) == 3
    assert len({alert["eventId"] for alert in swings}) == 3
    assert all(alert["revision"] == 1 for alert in swings)
    assert all(provider_resolver.event_channel(event["eventId"]) == "SAMPLE-TV"
               for event in _guard_events(api))
    pending = alert_policy.pending("hoops", cursor)["alerts"]
    assert len(pending) == 1
    assert pending[0]["data"]["commentary"] == "Sample Guard +5 fantasy pts"
    before = _events(api)
    _poll(monkeypatch, latest)
    assert sorted(_events(api), key=lambda e: e["eventId"]) == sorted(before, key=lambda e: e["eventId"])


def test_r02_stale_boxscore_does_not_publish_events(api, monkeypatch):
    import store
    _prior(GUARD, GAME, {"points": 9}, "2026-10-21T00:00:03Z")
    _poll(monkeypatch, _observation(20, 2))
    assert store.get_player_statistics(GUARD)["stats"]["points"] == 9
    assert _guard_events(api) == []


def test_r02_interleaved_ingest_uses_the_accepted_previous_record(api, monkeypatch):
    import store
    _poll(monkeypatch, _observation(0, 0))
    get_table = store._table
    fired = False

    class InterleavedTable:
        def __init__(self, table):
            self.table = table

        def __getattr__(self, name):
            return getattr(self.table, name)

        def get_item(self, **request):
            nonlocal fired
            previous = self.table.get_item(**request)
            if request["Key"] == {"athleteId": GUARD} and not fired:
                fired = True
                _poll(monkeypatch, _observation(5, 1))
            return previous

    def table(variable, *args, **kwargs):
        result = get_table(variable, *args, **kwargs)
        return InterleavedTable(result) if variable == "PLAYER_STATS_TABLE" else result

    monkeypatch.setattr(store, "_table", table)
    _poll(monkeypatch, _observation(7, 2))
    assert fired
    events = _guard_events(api)
    assert [event["matchup"] for event in events] == ["+5 fantasy pts"]
    assert events[0]["revision"] == 1
    assert store.get_player_statistics(GUARD)["stats"]["points"] == 7


@pytest.mark.parametrize("double_double", [False, True])
@pytest.mark.parametrize("turn_off", [False, True])
def test_r03_milestone_recovery_never_republishes(api, monkeypatch, double_double, turn_off):
    import store
    _seed("hoops", sports={"nba": True})
    low = {"points": 10, "rebounds": 9} if double_double else {"points": 9}
    high = {"points": 10, "rebounds": 10} if double_double else {"points": 10}
    _poll(monkeypatch, _observation(second=0, **low))
    _poll(monkeypatch, _observation(second=1, **high))
    _deliver(_events(api))
    before_events, before_alerts = _events(api), _alerts(api, "hoops")
    assert len(before_events) == len(before_alerts) == 1
    _poll(monkeypatch, _observation(second=2, **low))
    if turn_off:
        profile = store.get_profile("hoops")
        settings = dict(SETTINGS, sports={"nba": False})
        assert store.put_profile("hoops", settings, int(profile["revision"]), WHEN)
    _poll(monkeypatch, _observation(second=3, **high))
    _deliver(_events(api))
    assert _events(api) == before_events
    assert _alerts(api, "hoops") == before_alerts
    if turn_off:
        _poll(monkeypatch, _observation(15, 4, rebounds=high.get("rebounds", 0)))
        _deliver(_events(api))
        assert any(event["matchup"] == "+5 fantasy pts" for event in _guard_events(api))
        assert all(event["revision"] == 1 for event in _guard_events(api))
        assert _alerts(api, "hoops") == before_alerts


@pytest.mark.parametrize("previous_game", [None, "401999100"])
def test_cold_start_only_sets_baseline_even_after_downward_correction(api, monkeypatch, previous_game):
    if previous_game:
        _prior(GUARD, previous_game, {"points": 0})
    _seed("hoops", sports={"nba": True})
    _poll(monkeypatch, _observation(30, 1, rebounds=10))
    assert _guard_events(api) == []
    _poll(monkeypatch, _observation(9, 2, rebounds=9))
    _poll(monkeypatch, _observation(10, 3, rebounds=10))
    assert _guard_events(api) == []


def test_missing_clock_keeps_the_baseline_until_the_crossing_can_be_published(api, monkeypatch):
    import store
    baseline = _observation(0, 0)
    baseline.pop("plays")
    _poll(monkeypatch, baseline)
    changed = _observation(5, 1)
    changed.pop("plays")
    _poll(monkeypatch, changed)
    assert store.get_player_statistics(GUARD)["stats"]["points"] == 0
    _poll(monkeypatch, _observation(5, 2))
    assert [event["matchup"] for event in _guard_events(api)] == ["+5 fantasy pts"]


@pytest.mark.parametrize("after_commit", [False, True])
def test_r02_transaction_failure_or_lost_ack_recovers_on_retry(api, monkeypatch, after_commit):
    import store
    from botocore.client import BaseClient
    _poll(monkeypatch, _observation(0, 0))
    call = BaseClient._make_api_call
    fired = False

    def fail_once(client, operation, params):
        nonlocal fired
        if operation == "TransactWriteItems" and not fired:
            fired = True
            if after_commit:
                call(client, operation, params)
            raise OSError("synthetic lost transaction response" if after_commit else "synthetic write outage")
        return call(client, operation, params)

    monkeypatch.setattr(BaseClient, "_make_api_call", fail_once)
    latest = _observation(5, 1)
    with pytest.raises(OSError, match="synthetic"):
        _poll(monkeypatch, latest)
    assert fired
    assert store.get_player_statistics(GUARD)["stats"]["points"] == (5 if after_commit else 0)
    assert len(_guard_events(api)) == int(after_commit)
    _poll(monkeypatch, latest)
    assert store.get_player_statistics(GUARD)["stats"]["points"] == 5
    assert len(_guard_events(api)) == 1
    assert _guard_events(api)[0]["revision"] == 1
