"""Input-validation and DoS regressions for boxscore statistics ingest."""

import json
from decimal import Decimal
from pathlib import Path

import pytest
from botocore.exceptions import ClientError

from feed_support import FIXTURES, GAME, OTHER_GAME, fresh_scoreboard, fresh_summary, plays_in

HURTS = "4040715"
COOPER = "4715355"
BASE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/"


def test_boxscore_bound_constants_are_exposed_and_enforced():
    from feed_ingest import normalize

    assert normalize.MAX_ATHLETE_ID_LENGTH == 20
    assert normalize.MAX_BOXSCORE_ATHLETES == 200
    assert normalize.MAX_ATHLETE_STATS == 64
    assert normalize.MAX_STAT_VALUE_LENGTH == 16
    with pytest.raises(AttributeError):
        _ = normalize.NO_SUCH_CONSTANT
    with pytest.raises(ValueError, match="live or replay"):
        normalize.boxscore_statistics({}, GAME, source="bad")
    assert normalize.boxscore_statistics({}, GAME) == []
    bad_state = fresh_summary()
    bad_state["header"]["competitions"][0]["status"]["type"]["state"] = "unknown"
    assert normalize.boxscore_statistics(bad_state, GAME) == []
    malformed = fresh_summary()
    malformed["boxscore"]["players"] = [
        "not-a-team",
        {"statistics": [
            "not-a-category",
            {"name": 123, "keys": []},
            {"name": "passing", "keys": "not-a-list"},
            {"name": "passing", "keys": ["passingYards", "passingTouchdowns"], "athletes": [
                "not-an-entry",
                {"athlete": {"id": HURTS}, "stats": "not-a-list"},
                {"athlete": {"id": HURTS}, "stats": ["215", "abc"]},
            ]},
        ]},
    ]
    assert [r["athleteId"] for r in normalize.boxscore_statistics(malformed, GAME)] == [HURTS]


@pytest.mark.parametrize("bad_id", [
    "",
    "9" * 2049,
    "9" * 21,
    "4040715a",
    "../4040715",
    " 4040715",
    "4040715 ",
    "-4040715",
    "\uff11\uff12\uff13",
    None,
    4040715,
    ["4040715"],
])
def test_invalid_athlete_id_is_skipped_and_logged_without_aborting_ingest(caplog, bad_id):
    from feed_ingest.normalize import boxscore_statistics

    payload = fresh_summary()
    passing = payload["boxscore"]["players"][0]["statistics"][0]
    assert passing["name"] == "passing"
    passing["athletes"].insert(0, {
        "athlete": {"id": bad_id},
        "stats": ["10/10", "300", "30.0", "3", "0", "0-0", "90.0", "120.0"],
    })
    boundary_id = "9" * 20
    passing["athletes"].append({
        "athlete": {"id": boundary_id},
        "stats": ["1/1", "15", "15.0", "0", "0", "0-0", "50.0", "80.0"],
    })
    with caplog.at_level("WARNING", logger="feed_ingest.normalize"):
        records = boxscore_statistics(payload, GAME, source="live")
    by_id = {r["athleteId"]: r for r in records}
    assert all(r["athleteId"] != bad_id for r in records)
    assert HURTS in by_id
    assert by_id[boundary_id]["stats"]["passing_yards"] == Decimal("15")
    assert any("athleteId" in rec.getMessage() for rec in caplog.records)


def test_hostile_athlete_id_in_first_game_does_not_block_later_game_or_alerts(api, monkeypatch):
    import alert_policy
    import feed_ingest
    import matcher
    import panel
    import store

    # Set up profile and starter in OTHER_GAME so events produce an alert.
    other_summary = fresh_summary(OTHER_GAME)
    scoring_play = next(p for p in plays_in(other_summary) if p.get("scoringPlay"))
    other_athlete = next(
        entry["athlete"]["id"]
        for team in other_summary["boxscore"]["players"]
        for cat in team["statistics"]
        for entry in cat.get("athletes", [])
    )
    scoring_play["participants"] = [{"athlete": {"id": other_athlete}}]

    store.put_profile("owner", {
        "fantasySelections": {"favoriteTeamIds": ["30", "34"]},
        "alertTypes": ["PlayerScore", "RedZone", "CloseGame"],
        "excitement": "Mild",
    }, 0, "2026-10-11T12:00:00Z")
    store.put_lineup({
        "profileId": "owner",
        "source": "manual",
        "team": "team-1",
        "league": "league-1",
        "starters": [{"athlete_id": other_athlete, "name": "Starter", "team": "HOU", "slot": "QB"}],
        "scoring": {"preset": "Half-PPR"},
        "updatedAt": "2026-10-11T12:00:00Z",
    })

    bad_first = fresh_summary(GAME)
    bad_first["boxscore"]["players"][0]["statistics"][0]["athletes"].insert(0, {
        "athlete": {"id": "9" * 2049},
        "stats": ["10/10", "300", "30.0", "3", "0", "0-0", "90.0", "120.0"],
    })
    bad_first["boxscore"]["players"][0]["statistics"][0]["athletes"].insert(1, {
        "athlete": {"id": ""},
        "stats": ["10/10", "300", "30.0", "3", "0", "0-0", "90.0", "120.0"],
    })

    board = fresh_scoreboard()
    board["events"] = [g for g in board["events"] if g["id"] in (GAME, OTHER_GAME)]
    for game in board["events"]:
        game["status"]["type"]["state"] = "in"

    bodies = {
        BASE + "scoreboard": board,
        BASE + "summary?event=" + GAME: bad_first,
        BASE + "summary?event=" + OTHER_GAME: other_summary,
    }
    import io
    from types import SimpleNamespace
    monkeypatch.setattr(
        feed_ingest, "_opener",
        lambda: SimpleNamespace(open=lambda url, timeout: io.BytesIO(json.dumps(bodies[url]).encode())))

    result = feed_ingest.lambda_handler({}, None)
    assert result["failed"] == []
    assert result["stored"] == len(plays_in(bad_first)) + len(plays_in(other_summary))
    assert panel.player_statistics(HURTS)["stats"]["passing_yards"] == Decimal("220")
    assert panel.player_statistics(other_athlete) is not None

    # Verify the stored scoring event in OTHER_GAME resolves and emits an alert.
    stored_scoring = store.get_event(OTHER_GAME, scoring_play["id"])
    assert stored_scoring is not None
    matches = matcher.resolve(stored_scoring)
    assert matches
    emitted = alert_policy.evaluate(stored_scoring, matches)
    assert len(emitted) == 1


def test_athletes_per_payload_capped_deterministically_and_logged(caplog):
    from feed_ingest.normalize import MAX_BOXSCORE_ATHLETES, boxscore_statistics

    payload = fresh_summary()
    passing_athletes = [
        {"athlete": {"id": str(100000 + i)}, "stats": ["1/1", str(i), "1.0", "0", "0", "0-0", "50.0", "50.0"]}
        for i in range(1, MAX_BOXSCORE_ATHLETES + 6)
    ]
    rushing_athletes = [
        {"athlete": {"id": "100001"}, "stats": ["1", "17", "17.0", "1", "17"]},
        {"athlete": {"id": str(100000 + MAX_BOXSCORE_ATHLETES + 1)}, "stats": ["1", "99", "99.0", "1", "99"]},
    ]
    payload["boxscore"]["players"] = [{
        "statistics": [
            {
                "name": "passing",
                "keys": ["completions/passingAttempts", "passingYards", "yardsPerPassAttempt",
                         "passingTouchdowns", "interceptions", "sacks-sackYardsLost", "adjQBR", "QBRating"],
                "athletes": passing_athletes,
            },
            {
                "name": "rushing",
                "keys": ["rushingAttempts", "rushingYards", "yardsPerRushAttempt",
                         "rushingTouchdowns", "longRushing"],
                "athletes": rushing_athletes,
            },
        ]
    }]
    with caplog.at_level("WARNING", logger="feed_ingest.normalize"):
        records = boxscore_statistics(payload, GAME)
    assert len(records) == MAX_BOXSCORE_ATHLETES
    assert [r["athleteId"] for r in records] == [str(100000 + i) for i in range(1, MAX_BOXSCORE_ATHLETES + 1)]
    assert records[0]["stats"]["passing_yards"] == Decimal("1")
    assert records[0]["stats"]["rushing_yards"] == Decimal("17")
    assert records[0]["stats"]["rushing_touchdowns"] == Decimal("1")
    assert any("excess boxscore athlete" in rec.getMessage() for rec in caplog.records)


def test_stats_per_athlete_capped_deterministically_and_logged(caplog):
    from feed_ingest.normalize import MAX_ATHLETE_STATS, boxscore_statistics

    payload = fresh_summary()
    # 64th item (index 63) is rushingYards=42 (kept); 65th item (index 64) is passingTouchdowns=9 (dropped).
    keys = ["passingYards"] + ["unmappedKey"] * (MAX_ATHLETE_STATS - 2) + ["interceptions", "passingTouchdowns"]
    stats = ["250"] + ["1"] * (MAX_ATHLETE_STATS - 2) + ["2", "9"]
    assert len(keys) == len(stats) == MAX_ATHLETE_STATS + 1

    payload["boxscore"]["players"] = [{
        "statistics": [
            {
                "name": "passing",
                "keys": keys,
                "athletes": [{"athlete": {"id": HURTS}, "stats": stats}],
            },
            {
                "name": "rushing",
                "keys": ["rushingYards"],
                "athletes": [{"athlete": {"id": HURTS}, "stats": ["88"]}],
            },
        ]
    }]
    with caplog.at_level("WARNING", logger="feed_ingest.normalize"):
        [record] = boxscore_statistics(payload, GAME)
    assert record["athleteId"] == HURTS
    assert record["stats"] == {
        "passing_yards": Decimal("250"),
        "interceptions_thrown": Decimal("2"),
    }
    assert any("excess boxscore stats" in rec.getMessage() for rec in caplog.records)


def test_oversize_and_underflow_stat_strings_rejected_before_decimal(api, caplog):
    from feed_ingest.ingest import ingest_summary
    from feed_ingest.normalize import MAX_STAT_VALUE_LENGTH, boxscore_statistics

    payload = fresh_summary()
    payload["boxscore"]["players"] = [{
        "statistics": [
            {
                "name": "passing",
                "keys": ["passingYards", "passingTouchdowns", "interceptions"],
                "athletes": [
                    {
                        "athlete": {"id": HURTS},
                        # Oversize string with small magnitude ("1.000..."), underflow "1e-200",
                        # and exact 16-char valid string ("0"*13 + "2").
                        "stats": ["1." + "0" * 50000, "1e-200", "0" * (MAX_STAT_VALUE_LENGTH - 1) + "2"],
                    },
                    {
                        "athlete": {"id": COOPER},
                        # 17-char string (1 over MAX_STAT_VALUE_LENGTH), exponent -5, and valid "-99999".
                        "stats": ["0" * MAX_STAT_VALUE_LENGTH + "5", "1.23456", "-99999"],
                    },
                    {
                        "athlete": {"id": "4000001"},
                        # Boundary exponent -4 ("1.2345"), boundary magnitude "99999", overflow "100000".
                        "stats": ["1.2345", "99999", "100000"],
                    },
                    {
                        "athlete": {"id": "4000002"},
                        # Non-numeric types: bool True, huge int 10**100, negative overflow -100000.
                        "stats": [True, 10**100, -100000],
                    },
                    {
                        "athlete": "not-a-dict",
                        "stats": ["100", "1", "0"],
                    },
                ],
            }
        ]
    }]
    with caplog.at_level("WARNING", logger="feed_ingest.normalize"):
        records = boxscore_statistics(payload, GAME)
    by_id = {r["athleteId"]: r["stats"] for r in records}
    assert by_id[HURTS] == {"interceptions_thrown": Decimal("2")}
    assert by_id[COOPER] == {"interceptions_thrown": Decimal("-99999")}
    assert by_id["4000001"] == {"passing_yards": Decimal("1.2345"), "passing_touchdowns": Decimal("99999")}
    assert "4000002" not in by_id
    assert any("oversize boxscore stat" in rec.getMessage() for rec in caplog.records)

    # Also verify that `"1e-200"` and `"1." + "0"*50000` in a schema-valid summary do not crash ingest_summary.
    schema_valid = fresh_summary()
    for team in schema_valid["boxscore"]["players"]:
        for cat in team["statistics"]:
            if cat["name"] == "passing":
                for entry in cat["athletes"]:
                    if entry["athlete"]["id"] == HURTS:
                        entry["stats"][cat["keys"].index("passingYards")] = "1." + "0" * 50000
                        entry["stats"][cat["keys"].index("passingTouchdowns")] = "1e-200"
    events = ingest_summary(schema_valid, GAME, source="replay")
    assert len(events) == len(plays_in(schema_valid))


def test_failing_single_record_write_does_not_abort_batch_or_ingest(api, monkeypatch, caplog):
    import panel
    import store
    from feed_ingest.ingest import ingest_summary, store_player_statistics

    real_put = store.put_player_statistics
    calls = []

    def flaky_put(record):
        calls.append(record.get("athleteId"))
        if len(calls) == 1:
            raise ClientError(
                {"Error": {"Code": "ValidationException", "Message": "bad item"}},
                "PutItem",
            )
        if len(calls) == 2:
            raise ValueError("corrupt record")
        return real_put(record)

    monkeypatch.setattr(store, "put_player_statistics", flaky_put)
    with caplog.at_level("WARNING", logger="feed_ingest.ingest"):
        events = ingest_summary(fresh_summary(), GAME, source="replay")
    assert len(events) == len(plays_in(fresh_summary()))
    assert len(calls) > 2
    assert panel.player_statistics(COOPER) is not None
    assert len(caplog.records) >= 2


def test_all_14_replay_fixtures_produce_identical_statistics():
    from feed_ingest.normalize import boxscore_statistics
    from feed_ingest.replay import load_statistics

    game_dirs = sorted(p for p in FIXTURES.iterdir() if p.is_dir())
    assert len(game_dirs) == 14
    for game_dir in game_dirs:
        gid = game_dir.name
        summary = json.loads((game_dir / "001-summary.json").read_text())
        live = boxscore_statistics(summary, gid, source="live")
        replayed = load_statistics(gid, FIXTURES)
        assert live and len(live) == len(replayed) <= 200
        for rec_live, rec_replay in zip(live, replayed):
            assert rec_live["athleteId"] == rec_replay["athleteId"]
            assert rec_live["athleteId"].isdigit() and 1 <= len(rec_live["athleteId"]) <= 20
            assert rec_live["stats"] == rec_replay["stats"]
            assert rec_live["source"] == "live" and rec_replay["source"] == "replay"
