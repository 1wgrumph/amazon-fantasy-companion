"""Issue #137: NFL scheduling isolation and bounded NBA I/O, offline only.

Committed ESPN fixtures; socketpair/HTTPResponse exercises actual read semantics.
Fault delays model the socket trickle and slow writes reproduced in review.
"""

import builtins
import io
import json
import signal
import socket
import threading
import time
from http.client import HTTPResponse
from pathlib import Path
from types import SimpleNamespace

import pytest

from feed_support import fresh_scoreboard

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "nba"


def _board():
    board = fresh_scoreboard()
    for event in board["events"]:
        event["status"]["type"]["state"] = "pre"
    return board


def _load(name):
    return json.loads((FIXTURES / name).read_text())


def _entry(nba):
    import feed_ingest

    # Run the same behavioral regression on the original inline-hook candidate.
    return getattr(nba, "lambda_handler", feed_ingest.lambda_handler)


def test_f1_variable_nfl_cost_keeps_poll_starts_identical(monkeypatch):
    import feed_ingest

    monkeypatch.setattr(feed_ingest.store, "monitoring_profiles", lambda: [])
    monkeypatch.setenv("FEED_POLL_INTERVAL_SECONDS", "15")
    imports = []
    real_import = builtins.__import__

    def spy(name, *args, **kwargs):
        if name == "nba" or name.startswith("nba."):
            imports.append(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", spy)

    def run(flag):
        clock = SimpleNamespace(left=51, elapsed=0)
        starts = []

        def advance(seconds):
            clock.left -= seconds
            clock.elapsed += seconds

        def get_json(url):
            if "/basketball/" in url:
                advance(10)
                raise OSError("NBA request timeout")
            starts.append(round(clock.elapsed, 1))
            advance(.1 if len(starts) == 1 else 1)
            return _board()

        monkeypatch.setenv("AFC_ENABLE_NBA", str(int(flag)))
        monkeypatch.setattr(feed_ingest, "_get_json", get_json)
        monkeypatch.setattr(feed_ingest.time, "monotonic", lambda: clock.elapsed)
        monkeypatch.setattr(feed_ingest.time, "sleep", advance)
        context = SimpleNamespace(get_remaining_time_in_millis=lambda: clock.left * 1000)
        return feed_ingest.lambda_handler({}, context), starts

    off, off_starts = run(False)
    on, on_starts = run(True)
    assert off_starts == [0, 15.1, 31.1]
    assert on_starts == off_starts
    assert on == off == {"stored": 0, "failed": []}
    assert imports == [], "NFL ingest must never import NBA, even with its flag on"


def test_f2_trickling_response_has_absolute_deadline(monkeypatch, caplog):
    import feed_ingest
    import nba

    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    monkeypatch.setattr(nba, "_REQUEST_SECONDS", .15, raising=False)
    monkeypatch.setattr(feed_ingest.store, "monitoring_profiles", lambda: [])
    reader, writer = socket.socketpair()
    reader.settimeout(10)
    body = b" " * 20 + b"null"
    writer.sendall(f"HTTP/1.1 200 OK\r\nContent-Length: {len(body)}\r\n\r\n".encode())
    response = HTTPResponse(reader)
    response.begin()
    stop = threading.Event()

    def trickle():
        try:
            for byte in body:
                if stop.wait(.04):
                    break
                writer.sendall(bytes([byte]))
        except OSError:
            pass  # The deadline closes this test's reader while the writer is active.
        finally:
            writer.close()

    thread = threading.Thread(target=trickle)
    thread.start()

    def open_url(url, timeout):
        if "/basketball/" in url:
            return response
        return io.BytesIO(json.dumps(_board()).encode())

    monkeypatch.setattr(feed_ingest, "_opener", lambda: SimpleNamespace(open=open_url))
    old_handler = signal.getsignal(signal.SIGALRM)
    try:
        started = time.monotonic()
        result = _entry(nba)({}, None)
        elapsed = time.monotonic() - started
        assert elapsed < .6, f"trickling NBA read exceeded its absolute deadline: {elapsed:.3f}s"
        assert result == {"stored": 0, "failed": []}
        assert "deadline" in caplog.text.lower()
        assert signal.getsignal(signal.SIGALRM) == old_handler
        assert signal.getitimer(signal.ITIMER_REAL) == (0, 0)
    finally:
        stop.set()
        response.close()
        reader.close()
        thread.join(timeout=2)
    assert not thread.is_alive()


@pytest.mark.parametrize("run_seconds,write_seconds", [(1, .15), (.15, 1)])
def test_f3_slow_write_is_interrupted_by_deadline(monkeypatch, caplog, run_seconds, write_seconds):
    import feed_ingest
    import nba

    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    monkeypatch.setattr(nba, "_RUN_SECONDS", run_seconds, raising=False)
    monkeypatch.setattr(nba, "_WRITE_SECONDS", write_seconds, raising=False)
    monkeypatch.setattr(feed_ingest.store, "monitoring_profiles", lambda: [])
    writes = []

    def get_json(url):
        if "/basketball/" not in url:
            return _board()
        return _load("scoreboard.json" if url.endswith("scoreboard") else "summary.json")

    def slow_write(record, **kwargs):
        writes.append(record["athleteId"])
        threading.Event().wait(.6)

    monkeypatch.setattr(feed_ingest, "_get_json", get_json)
    monkeypatch.setattr(feed_ingest.store, "put_nba_statistics", slow_write)
    started = time.monotonic()
    result = _entry(nba)({}, None)
    elapsed = time.monotonic() - started
    assert elapsed < .5, f"NBA persistence exceeded its deadline: {elapsed:.3f}s"
    assert len(writes) == 1, "No later write may start after the deadline"
    assert result == {"stored": 0, "failed": []}
    assert "deadline" in caplog.text.lower()
    assert signal.getitimer(signal.ITIMER_REAL) == (0, 0)


def test_nba_handler_flag_off_does_no_io(monkeypatch):
    import feed_ingest
    import nba

    monkeypatch.delenv("AFC_ENABLE_NBA", raising=False)

    def forbidden(*args, **kwargs):
        raise AssertionError("Disabled NBA handler attempted I/O")

    monkeypatch.setattr(feed_ingest, "_get_json", forbidden)
    monkeypatch.setattr(feed_ingest.store, "put_nba_statistics", forbidden)
    assert nba.lambda_handler({}, None) == {"stored": 0, "failed": []}


@pytest.mark.parametrize("error", [KeyError("nba-scoreboard"), RuntimeError("nba down"),
                                   ValueError("ESPN response exceeds the size bound"),
                                   json.JSONDecodeError("Expecting value", "doc", 0)])
def test_nba_handler_contains_and_logs_errors(monkeypatch, caplog, error):
    import feed_ingest
    import nba

    monkeypatch.setenv("AFC_ENABLE_NBA", "1")

    def get_json(url):
        raise error

    monkeypatch.setattr(feed_ingest, "_get_json", get_json)
    assert nba.lambda_handler({}, None) == {"stored": 0, "failed": []}
    assert "NBA" in caplog.text
    assert signal.getitimer(signal.ITIMER_REAL) == (0, 0)


def test_nba_handler_uses_bounded_client_without_changing_nfl_client(api, monkeypatch):
    import feed_ingest
    import nba
    import store

    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    nfl_client = store._dynamodb()
    nfl_config = nfl_client.meta.client.meta.config
    monkeypatch.setattr(feed_ingest, "_get_json", lambda url:
                        _load("scoreboard.json" if url.endswith("scoreboard") else "summary.json"))
    assert nba.lambda_handler({}, None) == {"stored": 3, "failed": []}
    rows = api.table("PlayerStats").scan()["Items"]
    # The slate now carries each team's live game status, not only pregame text.
    assert [row["teams"] for row in rows if row["athleteId"] == "pregame"] == [
        {"SHO": "10:00 - 3rd", "SAW": "10:00 - 3rd"}]
    rows = [row for row in rows if row["athleteId"] != "pregame"]
    assert {row["athleteId"] for row in rows} == {"9100001", "9100002", "9100003"}
    assert all(row["gameId"] == "401999101" for row in rows)
    nba_client = store._dynamodb(nba._write_config())
    config = nba_client.meta.client.meta.config
    assert config.connect_timeout == config.read_timeout == 1
    assert config.retries["total_max_attempts"] == 1
    assert nba_client is not nfl_client
    assert store._dynamodb() is nfl_client
    assert nfl_client.meta.client.meta.config is nfl_config


def test_nba_schedule_targets_only_the_separate_function():
    import nba
    from conftest import document

    template = document("template.yaml")
    resources = template["Resources"]
    function = resources["NbaIngestFunction"]["Properties"]
    assert function["Handler"] == "nba.lambda_handler"
    assert function["Timeout"] > nba._RUN_SECONDS
    schedule = resources["NbaIngestSchedule"]["Properties"]
    assert schedule["ScheduleExpression"] == "rate(1 minute)"
    assert schedule["State"] == {"Ref": "NbaIngestScheduleState"}
    assert template["Parameters"]["NbaIngestScheduleState"]["Default"] == "DISABLED"
    assert schedule["Target"]["Arn"] == {"Fn::GetAtt": "NbaIngestFunction.Arn"}
    assert schedule["Target"]["RoleArn"] == {"Fn::GetAtt": "NbaIngestScheduleRole.Arn"}
    role = resources["NbaIngestScheduleRole"]["Properties"]["Policies"]
    assert role[0]["PolicyDocument"]["Statement"] == [{
        "Effect": "Allow", "Action": "lambda:InvokeFunction",
        "Resource": {"Fn::GetAtt": "NbaIngestFunction.Arn"}}]
