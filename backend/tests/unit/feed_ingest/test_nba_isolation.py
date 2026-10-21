"""NBA work behind AFC_ENABLE_NBA must not change the NFL poll result or schedule.

The hook runs after NFL work. These tests compare one scenario with the flag
on against the same scenario with the flag off. Clocks are fake: nothing here
sleeps.
"""

import builtins
import io
import json
import sys
from types import SimpleNamespace

import pytest

import feed_ingest
from feed_support import fresh_scoreboard

NFL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/"
NBA = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/"
BUDGET_SECONDS = 15  # the per-poll cap the NFL window can spare under a 60s Lambda
GAMES = 6


def _pregame_board():
    board = fresh_scoreboard()
    for event in board["events"]:
        event["status"]["type"]["state"] = "pre"
    return board


def _nba_board(count=GAMES):
    board = fresh_scoreboard()
    event = board["events"][0]
    clones = []
    for offset in range(count):
        clone = json.loads(json.dumps(event))
        clone["id"] = str(800000000 + offset)
        clone["status"]["type"]["state"] = "in"
        clones.append(clone)
    board["events"] = clones
    return board


def _silence_profiles(monkeypatch):
    monkeypatch.setattr(feed_ingest.store, "monitoring_profiles", lambda: [])


def _view(result):
    """NFL fields the hook is not allowed to change. Missing stale stays missing."""
    view = {"stored": result["stored"], "failed": list(result["failed"])}
    if "stale" in result:
        view["stale"] = list(result["stale"])
    return view


class _Clock:
    """Callable remaining() plus the Lambda millis view. `left` is seconds."""

    def __init__(self, seconds):
        self.left = seconds
        self.mono = 0.0
        self.sleeps = []

    def remaining(self):
        return self.left

    def get_remaining_time_in_millis(self):
        return self.left * 1000

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.left -= seconds

    def monotonic(self):
        return self.mono

    def advance(self, seconds):
        self.left -= seconds
        self.mono += seconds


def _install_clock(monkeypatch, clock):
    monkeypatch.setattr(feed_ingest.time, "sleep", clock.sleep)
    monkeypatch.setattr(feed_ingest.time, "monotonic", clock.monotonic)


@pytest.mark.parametrize("error", [KeyError("nba-scoreboard"), RuntimeError("nba down")])
def test_nba_non_oserror_leaves_the_nfl_result_unchanged(monkeypatch, caplog, error):
    _silence_profiles(monkeypatch)
    board = _pregame_board()
    seen = []

    def get_json(url):
        seen.append(url)
        if url.startswith(NBA):
            raise error
        return board

    monkeypatch.setattr(feed_ingest, "_get_json", get_json)
    # Room for one NBA request, so the getter must actually attempt the fetch.
    clock = _Clock(51)
    _install_clock(monkeypatch, clock)

    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    off = feed_ingest.poll({}, clock.remaining)
    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    with caplog.at_level("WARNING", logger="feed_ingest"):
        on = feed_ingest.poll({}, clock.remaining)

    assert _view(on) == _view(off)
    assert on == off
    assert any(url.startswith(NBA) for url in seen)
    assert any("NBA poll failed" in record.getMessage() for record in caplog.records)


def test_nba_hang_stops_within_budget_and_leaves_the_nfl_result(monkeypatch):
    _silence_profiles(monkeypatch)
    nfl_board = _pregame_board()
    nba_board = _nba_board()
    clock = _Clock(51)
    _install_clock(monkeypatch, clock)
    nba_calls = []

    def get_json(url):
        if url.startswith(NBA):
            # A hung urlopen runs until its timeout, then the next game would start.
            clock.advance(feed_ingest._REQUEST_SECONDS)
            nba_calls.append(url)
            return nba_board if url.endswith("scoreboard") else {"not": "a summary"}
        return nfl_board

    monkeypatch.setattr(feed_ingest, "_get_json", get_json)
    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    started = clock.mono
    off = feed_ingest.poll({}, clock.remaining)
    flag_off_added = clock.mono - started

    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    started = clock.mono
    on = feed_ingest.poll({}, clock.remaining)
    added = clock.mono - started

    assert flag_off_added == 0
    assert 0 < added <= BUDGET_SECONDS
    assert len(nba_calls) < 1 + GAMES
    assert _view(on) == _view(off)
    assert on == off


def test_nba_request_timeout_stays_the_shared_urlopen_bound(monkeypatch):
    """One in-flight NBA request cannot outlive _REQUEST_SECONDS: that is the timeout."""
    _silence_profiles(monkeypatch)
    board = _pregame_board()
    timeouts = []

    def open_url(url, timeout):
        timeouts.append((url, timeout))
        if url.startswith(NBA):
            raise OSError("nba unavailable")
        return io.BytesIO(json.dumps(board).encode())

    monkeypatch.setattr(feed_ingest, "_opener", lambda: SimpleNamespace(open=open_url))
    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    feed_ingest.poll({})
    nba_timeouts = [timeout for url, timeout in timeouts if url.startswith(NBA)]
    assert nba_timeouts == [feed_ingest._REQUEST_SECONDS]
    assert feed_ingest._REQUEST_SECONDS == 10


@pytest.mark.parametrize("kind", ["scoreboard-shape", "summary-shape", "malformed-json"])
def test_malformed_nba_payload_leaves_the_nfl_result_unchanged(monkeypatch, kind):
    _silence_profiles(monkeypatch)
    nfl_board = _pregame_board()
    nba_board = _nba_board(1)
    order = []

    def get_json(url):
        order.append("nba" if url.startswith(NBA) else "nfl")
        if not url.startswith(NBA):
            return nfl_board
        if kind == "malformed-json":
            raise json.JSONDecodeError("Expecting value", "doc", 0)
        if kind == "scoreboard-shape" or url.endswith("scoreboard"):
            return {"events": [{"id": "not-numeric"}]} if kind == "scoreboard-shape" else nba_board
        return {"boxscore": "nope"}

    monkeypatch.setattr(feed_ingest, "_get_json", get_json)
    clock = _Clock(51)
    _install_clock(monkeypatch, clock)
    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    off = feed_ingest.poll({}, clock.remaining)
    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    on = feed_ingest.poll({}, clock.remaining)

    assert order[0] == "nfl"
    assert "nba" in order
    assert _view(on) == _view(off)
    assert on == off


def test_slow_nba_does_not_reduce_the_number_of_nfl_polls(monkeypatch):
    _silence_profiles(monkeypatch)
    nfl_board = _pregame_board()
    nba_board = _nba_board()
    monkeypatch.setenv("FEED_POLL_INTERVAL_SECONDS", "15")

    def run(flag):
        clock = _Clock(51)
        _install_clock(monkeypatch, clock)
        feed_ingest._FAILURES.clear()
        nfl_polls = []

        def get_json(url):
            if url.startswith(NBA):
                clock.advance(feed_ingest._REQUEST_SECONDS)
                return nba_board if url.endswith("scoreboard") else {"not": "a summary"}
            if url.endswith("scoreboard"):
                nfl_polls.append(url)
            return nfl_board

        monkeypatch.setattr(feed_ingest, "_get_json", get_json)
        if flag:
            monkeypatch.setenv("AFC_ENABLE_NBA", "1")
        else:
            monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
        result = feed_ingest.lambda_handler({}, clock)
        return nfl_polls, result

    off_polls, off = run(False)
    on_polls, on = run(True)
    assert len(off_polls) == 3
    assert len(on_polls) == len(off_polls)
    assert _view(on) == _view(off)


def test_flag_off_poll_does_not_import_nba(monkeypatch):
    _silence_profiles(monkeypatch)
    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)
    monkeypatch.setattr(feed_ingest, "_get_json", lambda url: _pregame_board())
    saved = {name: sys.modules.pop(name) for name in list(sys.modules)
             if name == "nba" or name.startswith("nba.")}
    imported = []
    real_import = builtins.__import__

    def spy(name, *args, **kwargs):
        if name == "nba" or name.startswith("nba."):
            imported.append(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", spy)
    try:
        feed_ingest.poll({})
        assert imported == []
        assert "nba" not in sys.modules
    finally:
        sys.modules.update(saved)
