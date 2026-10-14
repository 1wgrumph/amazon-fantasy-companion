"""P2-B02 implementer tests for feed paths the frozen B02T suite does not reach.

Live polling runs offline: urlopen is replaced, so no socket opens. Inputs are
deep copies of the captured fixtures (CONTRACT-AFC-P2-FIXTURE).
"""

import hashlib
import io
import json
import shutil

import pytest

import feed_ingest
from feed_ingest import monitoring, normalize, replay, validation
from feed_support import (FIXTURES, GAME, OTHER_GAME, fresh_scoreboard,
                          fresh_summary, plays_in)


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def espn(monkeypatch):
    """Serve captured bodies for the allowlisted URLs and record each request."""
    calls = []
    bodies = {}

    def urlopen(url, timeout):
        calls.append((url, timeout))
        return Response(bodies[url])

    monkeypatch.setattr(feed_ingest.request, "urlopen", urlopen)
    return calls, bodies


BASE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/"


def in_progress_scoreboard():
    board = fresh_scoreboard()
    for event in board["events"]:
        event["status"]["type"]["state"] = "in" if event["id"] == GAME else "post"
    return board


def test_handler_polls_only_in_progress_games_from_the_allowlisted_host(api, espn):
    calls, bodies = espn
    bodies[BASE + "scoreboard"] = json.dumps(in_progress_scoreboard()).encode()
    bodies[BASE + "summary?event=" + GAME] = json.dumps(fresh_summary()).encode()
    result = feed_ingest.lambda_handler({}, None)
    assert result == {"stored": len(plays_in(fresh_summary()))}
    assert calls == [(BASE + "scoreboard", 10), (BASE + "summary?event=" + GAME, 10)]
    items = api.table("Events").scan()["Items"]
    assert len(items) == result["stored"]
    assert {item["source"] for item in items} == {"live"}


def test_handler_accepts_the_scheduler_source(api, espn):
    calls, bodies = espn
    board = in_progress_scoreboard()
    for event in board["events"]:
        event["status"]["type"]["state"] = "pre"
    bodies[BASE + "scoreboard"] = json.dumps(board).encode()
    assert feed_ingest.lambda_handler({"source": "aws.scheduler"}, None) == {"stored": 0}
    assert len(calls) == 1


@pytest.mark.parametrize("event", [None, [], "aws.scheduler", {"source": "aws.events"}])
def test_handler_rejects_non_schedule_events(event):
    with pytest.raises(ValueError, match="only its schedule event"):
        feed_ingest.lambda_handler(event, None)


def test_invalid_scoreboard_stores_nothing(api, espn):
    _, bodies = espn
    bodies[BASE + "scoreboard"] = json.dumps({"events": [{"id": "../x"}]}).encode()
    with pytest.raises(ValueError, match="scoreboard fails the pinned schema"):
        feed_ingest.lambda_handler({}, None)
    assert api.table("Events").scan()["Items"] == []


@pytest.mark.parametrize("url", ["http://site.api.espn.com/x", "https://evil.example/x",
                                 "https://site.api.espn.com.evil.example/x"])
def test_requests_outside_the_allowlist_are_refused(espn, url):
    calls, _ = espn
    with pytest.raises(ValueError, match="only to https://site.api.espn.com"):
        feed_ingest._get_json(url)
    assert calls == []


def test_oversize_body_is_refused(espn):
    _, bodies = espn
    bodies[BASE + "x"] = b" " * (4 * 1024 * 1024) + b"1"
    with pytest.raises(ValueError, match="size bound"):
        feed_ingest._get_json(BASE + "x")
    bodies[BASE + "y"] = b" " * (4 * 1024 * 1024 - 1) + b"1"
    assert feed_ingest._get_json(BASE + "y") == 1


def test_validation_messages_name_the_failure():
    with pytest.raises(ValueError, match="^ESPN summary fails the pinned schema: "):
        validation.validate_summary([], GAME)
    with pytest.raises(ValueError, match="^ESPN summary is for another game$"):
        validation.validate_summary(fresh_summary(), OTHER_GAME)


def test_inline_participants_count_only_when_they_name_a_boxscore_athlete():
    summary = fresh_summary()
    known = sorted(athlete["athlete"]["id"] for team in summary["boxscore"]["players"]
                   for stat in team["statistics"] for athlete in stat.get("athletes") or [])
    plays_in(summary)[0]["participants"] = [
        {"athlete": {"id": known[0]}}, {"athlete": {"id": "invented"}}, {"type": "x"}]
    events = normalize.normalize_summary(summary, GAME)
    assert events[0]["playerIds"] == [known[0]]
    assert all(event["playerIds"] == [] for event in events[1:])


def test_a_summary_without_boxscore_names_no_players():
    summary = fresh_summary()
    del summary["boxscore"]
    plays_in(summary)[0]["participants"] = [{"athlete": {"id": "1"}}]
    assert normalize.normalize_summary(summary, GAME)[0]["playerIds"] == []


def test_a_play_without_an_offense_has_no_possession():
    summary = fresh_summary()
    del plays_in(summary)[0]["teamParticipants"]
    assert normalize.normalize_summary(summary, GAME)[0]["possession"] is None


def test_a_relabel_from_replay_to_live_is_a_new_revision():
    prior = {event["eventId"]: event for event in normalize.normalize_summary(
        fresh_summary(), GAME, source="replay")}
    emitted = normalize.normalize_summary(fresh_summary(), GAME, prior=prior)
    assert len(emitted) == len(prior)
    assert all(e["revision"] == 2 and e["correctionOf"] == 1 and e["source"] == "live"
               for e in emitted)


def test_a_drive_without_plays_emits_nothing():
    summary = fresh_summary()
    for drive in summary["drives"]["previous"]:
        del drive["plays"]
    assert normalize.normalize_summary(summary, GAME) == []


def test_a_competition_without_broadcasts_names_no_network():
    summary = fresh_summary()
    del summary["header"]["competitions"][0]["broadcasts"]
    assert normalize.broadcast_networks(summary) == []


def test_source_rejection_names_the_allowed_labels():
    with pytest.raises(ValueError, match="^Feed events must be labeled live or replay, not 'x'$"):
        normalize.normalize_summary(fresh_summary(), GAME, source="x")


def test_replay_leaves_out_only_a_play_without_wallclock():
    summary = json.loads((FIXTURES / "401872986" / "001-summary.json").read_text())
    expected = [play["id"] for play in plays_in(summary) if "wallclock" in play]
    assert len(expected) == len(plays_in(summary)) - 1
    events = replay.load_events("401872986", FIXTURES)
    assert [event["eventId"] for event in events] == expected
    assert all(isinstance(event["eventTime"], str) for event in events)


@pytest.mark.parametrize("game_id", [None, "", "../401872981", "40187298a", "1" * 21])
def test_replay_rejects_an_unsafe_game_id(game_id):
    with pytest.raises(ValueError, match="must be an ESPN event id"):
        replay.load_events(game_id, FIXTURES)


def copy_game(tmp_path):
    shutil.copytree(FIXTURES / GAME, tmp_path / GAME)
    return tmp_path / GAME / "index.json"


@pytest.mark.parametrize("field,value", [("game_id", OTHER_GAME), ("schema", "other")])
def test_replay_rejects_an_index_for_another_game_or_schema(tmp_path, field, value):
    path = copy_game(tmp_path)
    index = json.loads(path.read_text())
    index[field] = value
    path.write_text(json.dumps(index))
    with pytest.raises(ValueError, match="does not describe game"):
        replay.load_events(GAME, tmp_path)


def test_replay_needs_a_captured_summary(tmp_path):
    path = copy_game(tmp_path)
    index = json.loads(path.read_text())
    index["files"] = [entry for entry in index["files"] if entry["endpoint"] != "summary"]
    path.write_text(json.dumps(index))
    with pytest.raises(ValueError, match="No captured summary"):
        replay.load_events(GAME, tmp_path)


def test_replay_uses_the_latest_summary_sequence(tmp_path):
    path = copy_game(tmp_path)
    summary = fresh_summary()
    plays_in(summary)[0]["homeScore"] = 42
    raw = json.dumps(summary).encode()
    (tmp_path / GAME / "002-summary.json").write_bytes(raw)
    index = json.loads(path.read_text())
    # Listed first, so only the seq ordering (not list position) selects it.
    index["files"].insert(0, {"endpoint": "summary", "file": "002-summary.json", "seq": 2,
                              "sha256": hashlib.sha256(raw).hexdigest()})
    path.write_text(json.dumps(index))
    assert replay.load_events(GAME, tmp_path)[0]["score"]["home"] == 42


def test_replay_hash_failure_names_the_file(tmp_path):
    copy_game(tmp_path)
    (tmp_path / GAME / "001-scoreboard.json").write_text("{}")
    with pytest.raises(ValueError, match="^Replay fixture 001-scoreboard.json fails its index hash$"):
        replay.load_events(GAME, tmp_path)


def test_monitoring_requires_an_enabled_period_even_for_a_favorite_team():
    games = [{"gameId": GAME, "teamIds": ["1"], "playerIds": []}]
    assert monitoring.monitored_decisions(games, [], ["1"], False, "observed-playback") == [
        {"gameId": GAME, "basis": "observed-playback", "monitored": False}]
    assert monitoring.monitored_decisions(games, [], ["1"], True, "observed-playback")[0][
        "monitored"] is True


def test_monitoring_basis_rejection_lists_the_labels():
    with pytest.raises(ValueError, match="observed-playback.*profile-assumption.*'x'"):
        monitoring.monitored_decisions([], [], [], True, "x")
