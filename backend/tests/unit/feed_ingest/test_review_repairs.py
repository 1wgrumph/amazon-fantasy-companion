"""F2–F6: production polling over committed ESPN bodies; Moto, no network.

HTTP errors, contract drift and the configured interval are review-packet inputs.
Resource group: host-pytest; injected Lambda clock, no real waits or servers.
"""

import importlib
import io
import json
from email.message import Message
from types import SimpleNamespace
from urllib import request, response

import pytest

from feed_support import (FIXTURES, GAME, OTHER_GAME, fresh_scoreboard,
                          fresh_summary, plays_in)

BASE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/"


def board_for(*ids):
    board = fresh_scoreboard()
    board["events"] = [g for g in board["events"] if g["id"] in ids]
    assert [g["id"] for g in board["events"]] == list(ids)
    for game in board["events"]:
        game["status"]["type"]["state"] = "in"
    return board


def select_teams(api, *ids):
    board = board_for(*ids)
    teams = [g["competitions"][0]["competitors"][0]["team"]["id"] for g in board["events"]]
    api.table("Profiles").put_item(Item={"profileId": "owner", "settings": {
        "fantasySelections": {"favoriteTeamIds": teams}}})


@pytest.fixture
def feed(api, monkeypatch):
    module = importlib.import_module("feed_ingest")
    bodies, calls = {}, []

    def open_url(url, timeout):
        calls.append((url, timeout))
        value = bodies[url]
        if callable(value):
            value = value()
        if isinstance(value, Exception):
            raise value
        return io.BytesIO(json.dumps(value).encode())

    # The same tests run on the pinned urlopen baseline and the guarded opener.
    monkeypatch.setattr(module.request, "urlopen", open_url)
    if hasattr(module, "_opener"):
        monkeypatch.setattr(module, "_opener", lambda: SimpleNamespace(open=open_url))
    return module, bodies, calls


class Clock:
    def __init__(self, seconds):
        self.remaining = seconds
        self.sleeps = []

    def get_remaining_time_in_millis(self):
        return self.remaining * 1000

    def sleep(self, seconds):
        assert seconds > 0, "Polling must advance the clock"
        self.sleeps.append(seconds)
        self.remaining -= seconds
        assert self.remaining >= 10, "Polling exceeded the Lambda deadline margin"


def run_loop(feed, monkeypatch, seconds=51, interval=15):
    module, _, _ = feed
    clock = Clock(seconds)
    monkeypatch.setenv("FEED_POLL_INTERVAL_SECONDS", str(interval))
    # Monkeypatch the standard clock, including on the baseline that has no loop.
    monkeypatch.setattr("time.sleep", clock.sleep)
    return module.lambda_handler({}, clock), clock


@pytest.mark.parametrize("failure", [{"drives": {}}, OSError("feed down")])
def test_f2_bad_game_does_not_abort_later_valid_game(api, feed, failure):
    module, bodies, calls = feed
    select_teams(api, GAME, OTHER_GAME)
    bodies[BASE + "scoreboard"] = board_for(GAME, OTHER_GAME)
    bodies[BASE + "summary?event=" + GAME] = failure
    bodies[BASE + "summary?event=" + OTHER_GAME] = fresh_summary(OTHER_GAME)
    result = module.lambda_handler({}, None)
    assert result == {"stored": len(plays_in(fresh_summary(OTHER_GAME))), "failed": [GAME]}
    assert calls[-1] == (BASE + "summary?event=" + OTHER_GAME, 10)
    assert {row["gameId"] for row in api.table("Events").scan()["Items"]} == {OTHER_GAME}


@pytest.mark.parametrize("failure", [OSError("feed down"), {"drives": {}}])
def test_f3_three_failures_replace_live_with_labeled_replay(api, feed, monkeypatch, failure):
    module, bodies, calls = feed
    select_teams(api, GAME)
    importlib.import_module("feed_ingest.ingest").ingest_summary(fresh_summary(), GAME)
    bodies[BASE + "scoreboard"] = board_for(GAME)
    attempts = []

    def fail():
        rows = api.table("Events").scan()["Items"]
        assert {row["source"] for row in rows} == {"live"}
        attempts.append(1)
        return failure

    bodies[BASE + "summary?event=" + GAME] = fail
    result, clock = run_loop(feed, monkeypatch)
    rows = api.table("Events").scan()["Items"]
    assert len(attempts) == 3
    assert len(rows) == len(plays_in(fresh_summary()))
    assert {row["source"] for row in rows} == {"replay"}
    assert {int(row["revision"]) for row in rows} == {2}
    assert {int(row["correctionOf"]) for row in rows} == {1}
    assert result["failed"] == [GAME]
    assert result["stored"] == len(rows)
    assert clock.sleeps == [15, 15]


def test_f3_no_fixture_reports_stale_without_changing_values(api, feed, monkeypatch, tmp_path):
    module, bodies, _ = feed
    select_teams(api, GAME)
    importlib.import_module("feed_ingest.ingest").ingest_summary(fresh_summary(), GAME)
    before = api.table("Events").scan()["Items"]
    bodies[BASE + "scoreboard"] = board_for(GAME)
    bodies[BASE + "summary?event=" + GAME] = OSError("feed down")
    monkeypatch.setattr(module, "_fixtures", lambda: tmp_path, raising=False)
    result, _ = run_loop(feed, monkeypatch)
    assert result == {"stored": 0, "failed": [GAME], "stale": [GAME]}
    assert api.table("Events").scan()["Items"] == before


@pytest.mark.parametrize("interval,seconds,expected", [(5, 26, [5, 5, 5]),
                                                      (15, 51, [15, 15]),
                                                      (60, 60, [])])
def test_f4_configured_interval_and_lambda_deadline(api, feed, monkeypatch, interval, seconds, expected):
    _, bodies, calls = feed
    bodies[BASE + "scoreboard"] = board_for()
    result, clock = run_loop(feed, monkeypatch, seconds, interval)
    assert result == {"stored": 0, "failed": []}
    assert clock.sleeps == expected
    assert calls == [(BASE + "scoreboard", 10)] * (len(expected) + 1)


def test_f5_irrelevant_in_progress_game_is_never_fetched(api, feed):
    module, bodies, calls = feed
    select_teams(api, GAME)
    bodies[BASE + "scoreboard"] = board_for(GAME, OTHER_GAME)
    bodies[BASE + "summary?event=" + GAME] = fresh_summary()
    # Supplying this body proves a baseline failure on relevance, not a fake KeyError.
    bodies[BASE + "summary?event=" + OTHER_GAME] = fresh_summary(OTHER_GAME)
    module.lambda_handler({}, None)
    assert calls == [(BASE + "scoreboard", 10), (BASE + "summary?event=" + GAME, 10)]
    assert {row["gameId"] for row in api.table("Events").scan()["Items"]} == {GAME}


def test_f5_no_profiles_fetches_no_summary(api, feed):
    module, bodies, calls = feed
    bodies[BASE + "scoreboard"] = board_for(GAME)
    bodies[BASE + "summary?event=" + GAME] = fresh_summary()
    module.lambda_handler({}, None)
    assert calls == [(BASE + "scoreboard", 10)]
    assert api.table("Events").scan()["Items"] == []


@pytest.mark.parametrize("code", [301, 302, 307, 308])
def test_f6_redirect_is_refused_before_any_second_request(api, monkeypatch, code):
    module = importlib.import_module("feed_ingest")
    calls = []

    class Redirect(request.HTTPSHandler):
        handler_order = 100

        def https_open(self, req):
            calls.append(req.full_url)
            headers = Message()
            headers["Location"] = "https://elsewhere.example/summary"
            reply = response.addinfourl(io.BytesIO(b"{}"), headers, req.full_url,
                                       code=code if len(calls) == 1 else 200)
            reply.msg = "redirect" if len(calls) == 1 else "OK"
            return reply

    factory = getattr(module, "_opener", None)
    opener = factory() if factory else None
    if opener is None:
        monkeypatch.setattr(request, "_opener", request.build_opener(Redirect()))
    else:
        opener.add_handler(Redirect())
    with pytest.raises(ValueError, match="^ESPN redirects are refused$"):
        module._get_json(BASE + "scoreboard")
    assert calls == [BASE + "scoreboard"]


@pytest.mark.parametrize("game_dir", sorted(p for p in FIXTURES.iterdir() if p.is_dir()),
                         ids=lambda path: path.name)
def test_f1_every_captured_summary_validates_for_live_ingest(game_dir):
    module = importlib.import_module("feed_ingest.validation")
    module.validate_summary(fresh_summary(game_dir.name), game_dir.name)


def test_f3_success_resets_consecutive_failures(api, feed, monkeypatch):
    _, bodies, _ = feed
    select_teams(api, GAME)
    bodies[BASE + "scoreboard"] = board_for(GAME)
    sequence = iter([OSError("down"), {"drives": {}}, fresh_summary(),
                     OSError("down"), {"drives": {}}, fresh_summary()])
    bodies[BASE + "summary?event=" + GAME] = lambda: next(sequence)
    result, clock = run_loop(feed, monkeypatch, seconds=36, interval=5)
    rows = api.table("Events").scan()["Items"]
    assert clock.sleeps == [5] * 5
    assert result == {"stored": len(rows), "failed": [GAME]}
    assert {row["source"] for row in rows} == {"live"}
    assert {int(row["revision"]) for row in rows} == {1}


def test_f3_repeated_fallback_keeps_revisions_stable(api, feed, monkeypatch):
    _, bodies, _ = feed
    select_teams(api, GAME)
    ingest = importlib.import_module("feed_ingest.ingest")
    ingest.ingest_summary(fresh_summary(), GAME)
    bodies[BASE + "scoreboard"] = board_for(GAME)
    bodies[BASE + "summary?event=" + GAME] = OSError("down")
    result, clock = run_loop(feed, monkeypatch, seconds=66)
    rows = api.table("Events").scan()["Items"]
    assert clock.sleeps == [15] * 3
    assert result == {"stored": len(rows), "failed": [GAME]}
    assert {int(row["revision"]) for row in rows} == {2}
    assert {row["source"] for row in rows} == {"replay"}


@pytest.mark.parametrize("starter", ["athlete", "team"])
def test_f5_selected_starter_game_is_monitored_without_favorites(api, feed, starter):
    module, bodies, calls = feed
    game = board_for(GAME)["events"][0]
    leader = game["competitions"][0]["leaders"][0]["leaders"][0]["athlete"]
    selected = ({"athlete_id": leader["id"]} if starter == "athlete"
                else {"player_key": "nfl.p.selected", "team": "JAX"})
    api.table("Profiles").put_item(Item={"profileId": "owner", "settings": {}})
    api.table("Lineups").put_item(Item={"profileId": "owner", "starters": [selected]})
    bodies[BASE + "scoreboard"] = board_for(GAME, OTHER_GAME)
    bodies[BASE + "summary?event=" + GAME] = fresh_summary()
    bodies[BASE + "summary?event=" + OTHER_GAME] = fresh_summary(OTHER_GAME)
    module.lambda_handler({}, None)
    assert calls == [(BASE + "scoreboard", 10), (BASE + "summary?event=" + GAME, 10)]


def test_f5_profile_accessor_follows_scan_pages_and_reads_starters(api, monkeypatch):
    store = importlib.import_module("store")
    for i in range(3):
        api.table("Profiles").put_item(Item={"profileId": str(i), "settings": {
            "fantasySelections": {"favoriteTeamIds": [str(i)]}}})
    api.table("Lineups").put_item(Item={"profileId": "2", "starters": [{"athlete_id": "4360310"}]})
    client = store._dynamodb().meta.client
    original = client._make_api_call
    pages = []

    def bounded_scan(operation, params):
        if operation == "Scan":
            params["Limit"] = 1
            pages.append(params.get("ExclusiveStartKey"))
        return original(operation, params)

    monkeypatch.setattr(client, "_make_api_call", bounded_scan)
    profiles = store.monitoring_profiles()
    assert len(profiles) == len(pages) == 3
    assert pages[0] is None and all(pages[1:])
    assert {p["settings"]["fantasySelections"]["favoriteTeamIds"][0] for p in profiles} == {"0", "1", "2"}
    assert [p["starters"] for p in profiles].count([]) == 2
    assert {p["starters"][0]["athlete_id"] for p in profiles if p["starters"]} == {"4360310"}


def test_f5_monitoring_decisions_carry_profile_assumption_basis(api, feed, caplog):
    module, bodies, _ = feed
    select_teams(api, GAME)
    bodies[BASE + "scoreboard"] = board_for(GAME, OTHER_GAME)
    bodies[BASE + "summary?event=" + GAME] = fresh_summary()
    bodies[BASE + "summary?event=" + OTHER_GAME] = fresh_summary(OTHER_GAME)
    with caplog.at_level("INFO", logger="feed_ingest"):
        module.lambda_handler({}, None)
    decisions = [record.args for record in caplog.records if record.msg == "Monitoring decision: %s"]
    assert decisions == [{"gameId": GAME, "monitored": True, "basis": "profile-assumption"},
                         {"gameId": OTHER_GAME, "monitored": False, "basis": "profile-assumption"}]


def test_f5_malformed_relevance_fields_are_rejected_before_store_access(feed, monkeypatch):
    module, bodies, _ = feed
    board = board_for(GAME)
    board["events"][0]["competitions"] = "untrusted"
    bodies[BASE + "scoreboard"] = board

    def reject():
        pytest.fail("Invalid scoreboard accessed the profile store")

    monkeypatch.setattr(module.store, "monitoring_profiles", reject)
    with pytest.raises(ValueError, match="pinned schema"):
        module.lambda_handler({}, None)


def test_f4_invalid_interval_is_rejected_without_a_poll(feed, monkeypatch):
    module, _, calls = feed
    monkeypatch.setenv("FEED_POLL_INTERVAL_SECONDS", "0")
    with pytest.raises(ValueError, match="interval must be positive"):
        module.lambda_handler({}, None)
    assert calls == []


def test_f3_tampered_replay_is_stale_and_mutates_nothing(api, feed, monkeypatch, tmp_path):
    import shutil
    module, bodies, _ = feed
    select_teams(api, GAME)
    importlib.import_module("feed_ingest.ingest").ingest_summary(fresh_summary(), GAME)
    before = api.table("Events").scan()["Items"]
    shutil.copytree(FIXTURES / GAME, tmp_path / GAME)
    (tmp_path / GAME / "001-summary.json").write_text("{}")
    monkeypatch.setattr(module, "_fixtures", lambda: tmp_path, raising=False)
    bodies[BASE + "scoreboard"] = board_for(GAME)
    bodies[BASE + "summary?event=" + GAME] = OSError("feed down")
    result, _ = run_loop(feed, monkeypatch)
    assert result == {"stored": 0, "failed": [GAME], "stale": [GAME]}
    assert api.table("Events").scan()["Items"] == before
