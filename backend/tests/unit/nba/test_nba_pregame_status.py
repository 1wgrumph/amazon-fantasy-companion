"""NBA scoreboard pregame status is stored per team abbreviation (issue #137).

A starter whose game has not started has no boxscore row. The scoreboard
already carries that game's ESPN shortDetail. In-progress games stay on the
statistics path and clear the reserved slate item's teams map.
"""

import copy
import json
from pathlib import Path

import pytest
from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "nba"
TIP = "10/21 - 10:00 PM EDT"


def _board(state, detail=TIP):
    board = json.loads((FIXTURES / "scoreboard.json").read_text())
    status = board["events"][0]["status"]["type"]
    status["state"] = state
    status["shortDetail"] = detail
    status["detail"] = detail + " Quarter" if state != "pre" else detail
    return board


def test_pregame_status_is_the_scoreboard_short_detail_per_team():
    import nba.normalize as normalize

    fn = getattr(normalize, "pregame_status_by_team", None)
    assert callable(fn), "scoreboard pregame status is not parsed per team"
    assert fn(_board("pre")) == {"SHO": TIP, "SAW": TIP}
    assert fn(_board("in")) == {}
    assert fn(_board("post")) == {}


def test_poll_stores_pregame_status_for_a_not_started_game(api, monkeypatch):
    import nba

    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    board = _board("pre")
    summary = json.loads((FIXTURES / "summary.json").read_text())

    def get_json(url):
        return board if url.endswith("scoreboard") else summary

    result = nba.poll(get_json)
    assert result["failed"] == []
    item = api.table("PlayerStats").get_item(Key={"athleteId": "pregame"}).get("Item")
    # Owner design 2026-10-23: the start time is shown in Central as "Tips h:mm".
    assert item is not None and item.get("teams") == {"SHO": "Tips 9:00 PM", "SAW": "Tips 9:00 PM"}
    assert isinstance(item.get("asOf"), str) and item["asOf"]


def test_poll_stores_the_live_clock_for_an_in_progress_scoreboard(api, monkeypatch):
    import nba

    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    board = json.loads((FIXTURES / "scoreboard.json").read_text())
    summary = json.loads((FIXTURES / "summary.json").read_text())

    def get_json(url):
        return board if url.endswith("scoreboard") else summary

    assert nba.poll(get_json)["stored"] == 3
    # Owner design 2026-10-23: a started game's status is stored too.
    assert api.table("PlayerStats").get_item(Key={"athleteId": "pregame"})["Item"]["teams"] == {
        "SHO": "10:00 - 3rd", "SAW": "10:00 - 3rd"}
    ids = {row["athleteId"] for row in api.table("PlayerStats").scan()["Items"]}
    assert ids == {"pregame", "9100001", "9100002", "9100003"}


@pytest.mark.parametrize("state", ["in", "post", "empty"])
def test_successful_poll_replaces_the_previous_pregame_slate(api, monkeypatch, state):
    import nba
    import store

    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    board = _board("pre")
    summary = json.loads((FIXTURES / "summary.json").read_text())
    summary["boxscore"]["players"] = []
    get = lambda url: board if url.endswith("scoreboard") else summary
    nba.poll(get)
    assert store.get_nba_pregame()["teams"]
    status = {"in": "Q1 12:00", "post": "Final"}.get(state)
    if state == "empty":
        board["events"] = []
    else:
        board["events"][0]["status"]["type"].update(state=state, shortDetail=status)
    nba.poll(get)
    # Owner design 2026-10-23: a started or finished game replaces the start time with its status.
    assert store.get_nba_pregame()["teams"] == ({"SHO": status, "SAW": status} if status else {})


@pytest.mark.parametrize("error", [
    EndpointConnectionError(endpoint_url="https://dynamodb.test.invalid"),
    BotoCoreError(),
    ClientError({"Error": {"Code": "ProvisionedThroughputExceededException"}}, "PutItem"),
])
def test_slate_write_errors_do_not_drop_started_boxscores(api, monkeypatch, caplog, error):
    import nba
    import store

    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    board = _board("in")
    pre = copy.deepcopy(board["events"][0])
    pre["id"] = "401999102"
    pre["status"]["type"]["state"] = "pre"
    board["events"].append(pre)
    summary = json.loads((FIXTURES / "summary.json").read_text())
    def get(url):
        if url.endswith("scoreboard"):
            return board
        body = copy.deepcopy(summary)
        body["header"]["id"] = url.split("event=")[1]
        return body
    def fail(*args, **kwargs):
        raise error
    monkeypatch.setattr(store, "put_nba_pregame", fail)
    records = []
    assert nba.poll(get, records.extend)["stored"] == 6
    assert len(records) == 6
    assert any(row["gameId"] == "401999101" for row in records)
    assert "NBA pregame status not stored" in caplog.text


@pytest.mark.parametrize("reverse", [False, True])
def test_duplicate_team_uses_the_earliest_pregame_date(reverse):
    from nba.normalize import pregame_status_by_team

    board = _board("pre", "early tip")
    early = board["events"][0]
    early["date"] = "2026-10-22T00:00:00Z"
    late = copy.deepcopy(early)
    late["id"] = "401999102"
    late["date"] = "2026-10-21T22:00:00-04:00"
    late["status"]["type"]["shortDetail"] = "late tip"
    board["events"] = [early, late] if not reverse else [late, early]
    assert pregame_status_by_team(board) == {"SHO": "early tip", "SAW": "early tip"}


@pytest.mark.parametrize("date", [None, "invalid", "2026-10-22T00:00:00"])
def test_undated_or_malformed_pregame_does_not_displace_a_dated_game(date):
    from nba.normalize import pregame_status_by_team

    board = _board("pre")
    bad = copy.deepcopy(board["events"][0])
    bad["id"] = "401999102"
    bad["date"] = date
    bad["status"]["type"]["shortDetail"] = "unknown tip"
    board["events"].append(bad)
    assert pregame_status_by_team(board) == {"SHO": TIP, "SAW": TIP}
