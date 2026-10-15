"""B02-R2/R3/R4 regressions: scoreboard outage, cross-invocation failures, deadline.

Resource group: host-pytest; Moto store, controlled transport/clock, no network.
Transport charges elapsed seconds to the Lambda clock, unlike the older fakes
whose requests were instant.
"""

import importlib
import io
import json
from types import SimpleNamespace

import pytest

from feed_support import GAME, OTHER_GAME, fresh_scoreboard, fresh_summary, plays_in

BASE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/"


def board_for(*ids):
    board = fresh_scoreboard()
    board["events"] = [g for g in board["events"] if g["id"] in ids]
    for game in board["events"]:
        game["status"]["type"]["state"] = "in"
    return board


def select_teams(api, *ids):
    teams = [g["competitions"][0]["competitors"][0]["team"]["id"]
             for g in board_for(*ids)["events"]]
    api.table("Profiles").put_item(Item={"profileId": "owner", "settings": {
        "fantasySelections": {"favoriteTeamIds": teams}}})


class Clock:
    def __init__(self, seconds=60):
        self.remaining = seconds
        self.sleeps = []

    def get_remaining_time_in_millis(self):
        return self.remaining * 1000

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.remaining -= seconds


@pytest.fixture
def feed(api, monkeypatch):
    module = importlib.import_module("feed_ingest")
    bodies, calls, clock = {}, [], {"current": None}

    def open_url(url, timeout):
        calls.append((url, timeout))
        value = bodies[url]
        if callable(value):
            value = value(clock["current"], timeout)
        if isinstance(value, Exception):
            raise value
        return io.BytesIO(json.dumps(value).encode())

    monkeypatch.setattr(module, "_opener", lambda: SimpleNamespace(open=open_url))
    return module, bodies, calls, clock


def run(feed, monkeypatch, seconds=60, interval=15):
    module, _, _, clock = feed
    current = Clock(seconds)
    clock["current"] = current
    monkeypatch.setenv("FEED_POLL_INTERVAL_SECONDS", str(interval))
    monkeypatch.setattr(module.time, "sleep", current.sleep)
    return module.lambda_handler({}, current), current


def seed_live(api):
    importlib.import_module("feed_ingest.ingest").ingest_summary(fresh_summary(), GAME)
    return api.table("Events").scan()["Items"]


def test_r2_scoreboard_outage_reaches_labeled_replay(api, feed, monkeypatch):
    _, bodies, calls, _ = feed
    select_teams(api, GAME)
    seed_live(api)
    bodies[BASE + "scoreboard"] = OSError("scoreboard down")
    result, _ = run(feed, monkeypatch, seconds=51)
    rows = api.table("Events").scan()["Items"]
    assert calls == [(BASE + "scoreboard", 10)] * 3
    assert result["failed"] == [GAME]
    assert result["stored"] == len(rows) == len(plays_in(fresh_summary()))
    assert {row["source"] for row in rows} == {"replay"}
    assert {int(row["revision"]) for row in rows} == {2}


def _timing_out_summary(feed, bodies):
    bodies[BASE + "scoreboard"] = board_for(GAME)

    def timeout(clock, timeout_seconds):
        clock.remaining -= timeout_seconds
        return TimeoutError("summary timed out")

    bodies[BASE + "summary?event=" + GAME] = timeout


def test_r3_failures_persist_across_invocations_until_threshold(api, feed, monkeypatch):
    _, bodies, _, _ = feed
    select_teams(api, GAME)
    seed_live(api)
    _timing_out_summary(feed, bodies)
    run(feed, monkeypatch)  # two 10s attempts fit one 60s invocation
    assert {r["source"] for r in api.table("Events").scan()["Items"]} == {"live"}
    result, _ = run(feed, monkeypatch)  # third consecutive failure, next invocation
    rows = api.table("Events").scan()["Items"]
    assert result["failed"] == [GAME]
    assert {row["source"] for row in rows} == {"replay"}


def test_r3_success_in_later_invocation_resets_the_count(api, feed, monkeypatch):
    _, bodies, _, _ = feed
    select_teams(api, GAME)
    seed_live(api)
    _timing_out_summary(feed, bodies)
    run(feed, monkeypatch)  # count reaches 2
    bodies[BASE + "summary?event=" + GAME] = fresh_summary()
    run(feed, monkeypatch, seconds=20)  # one successful poll resets the count
    _timing_out_summary(feed, bodies)
    run(feed, monkeypatch)  # count reaches 2 again, below the threshold
    assert {r["source"] for r in api.table("Events").scan()["Items"]} == {"live"}


def _slow_success(bodies, seconds=8):
    bodies[BASE + "scoreboard"] = lambda clock, _: (
        setattr(clock, "remaining", clock.remaining - seconds),
        board_for(GAME, OTHER_GAME))[1]
    for game in (GAME, OTHER_GAME):
        bodies[BASE + "summary?event=" + game] = (
            lambda clock, _t, g=game: (
                setattr(clock, "remaining", clock.remaining - seconds),
                fresh_summary(g))[1])


def test_r4_second_poll_not_started_when_it_cannot_finish(api, feed, monkeypatch):
    _, bodies, calls, _ = feed
    select_teams(api, GAME, OTHER_GAME)
    _slow_success(bodies)
    result, clock = run(feed, monkeypatch)
    # One poll costs 24s; 36s left cannot hold the 15s interval plus another poll.
    assert clock.sleeps == []
    assert clock.remaining == 36
    assert len(calls) == 3
    assert result["stored"] == len(api.table("Events").scan()["Items"])


def test_r4_poll_stops_before_a_request_that_cannot_finish(api, feed, monkeypatch):
    _, bodies, calls, _ = feed
    select_teams(api, GAME, OTHER_GAME)
    _slow_success(bodies)
    _, clock = run(feed, monkeypatch, seconds=20)
    assert clock.remaining >= 0
    assert [url for url, _ in calls] == [BASE + "scoreboard",
                                         BASE + "summary?event=" + GAME]
