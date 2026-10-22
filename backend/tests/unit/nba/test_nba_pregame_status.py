"""NBA scoreboard pregame status is stored per team abbreviation (issue #137).

A starter whose game has not started has no boxscore row. The scoreboard
already carries that game's ESPN shortDetail. In-progress games stay on the
statistics path and do not write the reserved slate item.
"""

import json
from pathlib import Path

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
    assert item is not None and item.get("teams") == {"SHO": TIP, "SAW": TIP}
    assert isinstance(item.get("asOf"), str) and item["asOf"]


def test_poll_does_not_write_a_slate_for_an_in_progress_scoreboard(api, monkeypatch):
    import nba

    monkeypatch.setenv("AFC_ENABLE_NBA", "true")
    board = json.loads((FIXTURES / "scoreboard.json").read_text())
    summary = json.loads((FIXTURES / "summary.json").read_text())

    def get_json(url):
        return board if url.endswith("scoreboard") else summary

    assert nba.poll(get_json)["stored"] == 3
    assert "Item" not in api.table("PlayerStats").get_item(Key={"athleteId": "pregame"})
    ids = {row["athleteId"] for row in api.table("PlayerStats").scan()["Items"]}
    assert ids == {"9100001", "9100002", "9100003"}
