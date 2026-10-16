"""Normalization to GameEvent (VCASE-AFC-PR-012, DES-AFC-P2-FEED).

Scores, field position, possession, player identifiers and timestamps from
the captured summary land in the store.put_event shape. Expectations are
derived from the fixture itself, never restated from product code.
"""

import pytest

from feed_support import (GAME, attempt, boxscore_athlete_ids,
                          competitor_team_ids, fresh_summary, offense_team_id,
                          plays_in, require_attr, require_module)

EVENT_FIELDS = {"gameId", "eventId", "revision", "source", "score",
                "fieldPosition", "possession", "playerIds", "eventTime",
                "correctionOf", "period", "scoringPlay", "matchup"}


def normalize_module():
    return require_module("feed_ingest.normalize")


def normalize(payload, game_id=GAME, **kwargs):
    func = require_attr(normalize_module(), "normalize_summary")
    return attempt(func, payload, game_id, **kwargs)


def test_every_captured_play_becomes_one_event():
    summary = fresh_summary()
    events = normalize(summary)
    assert [event["eventId"] for event in events] == [play["id"] for play in plays_in(summary)]


def test_events_carry_only_the_stored_game_event_fields():
    for event in normalize(fresh_summary()):
        assert set(event) == EVENT_FIELDS, event
        assert event["gameId"] == GAME


def test_score_comes_from_each_play():
    summary = fresh_summary()
    by_id = {event["eventId"]: event for event in normalize(summary)}
    for play in plays_in(summary):
        assert by_id[play["id"]]["score"] == {
            "away": play["awayScore"], "home": play["homeScore"]}, play["id"]


def test_field_position_comes_from_each_play_start():
    summary = fresh_summary()
    by_id = {event["eventId"]: event for event in normalize(summary)}
    for play in plays_in(summary):
        assert by_id[play["id"]]["fieldPosition"] == play["start"]["yardsToEndzone"], play["id"]


def test_possession_is_the_offense_team():
    summary = fresh_summary()
    by_id = {event["eventId"]: event for event in normalize(summary)}
    for play in plays_in(summary):
        assert by_id[play["id"]]["possession"] == offense_team_id(play), play["id"]
        assert by_id[play["id"]]["possession"] in competitor_team_ids(summary)


def test_event_time_comes_from_each_play_wallclock():
    summary = fresh_summary()
    by_id = {event["eventId"]: event for event in normalize(summary)}
    for play in plays_in(summary):
        assert by_id[play["id"]]["eventTime"] == play["wallclock"], play["id"]


def test_player_ids_never_invent_an_athlete():
    # Play participants are $ref links, not inline ids (VERDICT.md), so a
    # play may list none; any id listed must be a captured boxscore athlete.
    summary = fresh_summary()
    known = boxscore_athlete_ids(summary)
    assert known, "the captured boxscore must name athletes"
    for event in normalize(summary):
        assert isinstance(event["playerIds"], list), event
        assert set(event["playerIds"]) <= known, event


def test_first_seen_events_start_at_revision_one_without_correction():
    for event in normalize(fresh_summary()):
        assert event["revision"] == 1, event
        assert event["correctionOf"] is None, event
        assert event["source"] == "live", event


def test_scoring_plays_carry_the_score_they_produced():
    summary = fresh_summary()
    by_id = {event["eventId"]: event for event in normalize(summary)}
    scoring = [play for play in plays_in(summary) if play.get("scoringPlay")]
    assert scoring, "the captured game must contain scoring plays"
    for play in scoring:
        assert by_id[play["id"]]["score"] == {
            "away": play["awayScore"], "home": play["homeScore"]}, play["id"]


def test_ingest_stores_every_normalized_event(api):
    ingest_summary = require_attr(require_module("feed_ingest.ingest"), "ingest_summary")
    stored = attempt(ingest_summary, fresh_summary(), GAME)
    items = api.table("Events").scan()["Items"]
    assert len(items) == len(stored) == len(plays_in(fresh_summary()))
    assert {item["eventId"] for item in items} == {event["eventId"] for event in stored}


def test_broadcast_networks_come_from_the_header_competition():
    # X05-OBS-001: the top-level broadcasts list is empty in the capture;
    # the networks live in header.competitions[0].broadcasts.
    summary = fresh_summary()
    assert summary["broadcasts"] == []
    expected = [entry["media"]["shortName"]
                for entry in summary["header"]["competitions"][0]["broadcasts"]]
    assert expected, "the captured competition must name a network"
    func = require_attr(normalize_module(), "broadcast_networks")
    assert attempt(func, summary) == expected


def test_broadcast_networks_ignore_the_top_level_field():
    summary = fresh_summary()
    summary["header"]["competitions"][0]["broadcasts"] = []
    summary["broadcasts"] = [{"media": {"shortName": "Invented TV"}}]
    func = require_attr(normalize_module(), "broadcast_networks")
    assert attempt(func, summary) == []


@pytest.mark.parametrize("source", ["yahoo", "manual", ""])
def test_a_non_feed_source_is_rejected(source):
    with pytest.raises(ValueError):
        normalize(fresh_summary(), source=source)


def expected_matchup(summary):
    competitors = summary["header"]["competitions"][0]["competitors"]
    away = next(c["team"]["abbreviation"] for c in competitors
                if c["homeAway"] == "away")
    home = next(c["team"]["abbreviation"] for c in competitors
                if c["homeAway"] == "home")
    return f"{away} at {home}"


def test_matchup_comes_from_header_competitors():
    summary = fresh_summary()
    label = expected_matchup(summary)
    assert 0 < len(label) <= 80
    for event in normalize(summary):
        assert event["matchup"] == label, event


def test_matchup_absent_without_valid_competitors():
    summary = fresh_summary()
    del summary["header"]["competitions"][0]["competitors"]
    for event in normalize(summary):
        assert "matchup" not in event, event


@pytest.mark.parametrize("abbreviation", ["x" * 9, "PHI PHI", "", None])
def test_matchup_absent_for_invalid_abbreviation(abbreviation):
    summary = fresh_summary()
    summary["header"]["competitions"][0]["competitors"][0]["team"]["abbreviation"] = (
        abbreviation)
    for event in normalize(summary):
        assert "matchup" not in event, event


def test_matchup_survives_ingest_storage(api):
    summary = fresh_summary()
    ingest_summary = require_attr(require_module("feed_ingest.ingest"),
                                  "ingest_summary")
    stored = attempt(ingest_summary, summary, GAME)
    assert stored and all(item["matchup"] == expected_matchup(summary)
                          for item in api.table("Events").scan()["Items"])
