"""Bug: deployed panel shows every value "statistics unavailable".

Ingest stored per-play GameEvents but never the boxscore, so the panel's
player_statistics seam always returned None in production (P2-B07T R1
shortcut). These tests ingest a committed replay summary (401872981,
PHI at JAX, Final) and read points back through the real seam and
panel.snapshot — no seam injection.
"""

import json
from pathlib import Path

import pytest

from feed_ingest.ingest import ingest_summary

GAME = "401872981"
HURTS = "4040715"  # passing 220/1/0, rushing 2/0, fumblesLost 0
COOPER = "4715355"  # receiving 2 rec, 71 yds, 1 TD
FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "replay"


def fresh_summary():
    return json.loads((FIXTURES / GAME / "001-summary.json").read_text())


def seed(api, profile="owner", starters=None, source="manual"):
    import store
    store.put_profile(profile, {}, 0, "2026-10-11T13:00:00Z")
    row = {"profileId": profile, "source": source, "team": "team-7", "league": "league-a",
           "starters": starters or [{"athlete_id": HURTS, "name": "Jalen Hurts",
                                      "team": "PHI", "slot": "QB"}],
           "updatedAt": "2026-10-11T13:00:00Z"}
    if source == "yahoo":
        from decimal import Decimal
        row["scoring"] = {"league_key": "nfl.l.1001",
                          "stat_modifiers": {"receptions": Decimal("1.5"),
                                             "receiving_yards": Decimal("0.2"),
                                             "receiving_touchdowns": Decimal("4")},
                          "roster_slots": ["QB", "WR", "BN"]}
    store.put_lineup(row)


def test_ingested_record_matches_seam_contract(api):
    import panel
    ingest_summary(fresh_summary(), GAME, source="replay")
    record = panel.player_statistics(HURTS)
    assert record is not None
    assert record["gameId"] == GAME
    assert record["gameState"] == "post"
    assert record["gameStatus"] == "Final"
    assert record["source"] == "replay"
    assert record["asOf"] == "2026-10-11T17:13:41Z"
    stats = {k: float(v) for k, v in record["stats"].items()}
    assert stats == {"passing_yards": 220, "passing_touchdowns": 1,
                     "interceptions_thrown": 0, "rushing_yards": 2,
                     "rushing_touchdowns": 0, "fumbles_lost": 0}


def test_snapshot_half_ppr_points(api, monkeypatch):
    import panel
    seed(api)
    ingest_summary(fresh_summary(), GAME, source="replay")
    _pin_now(panel, monkeypatch, "2026-10-11T18:13:41Z")
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    [row] = data["rows"]
    # 220*0.04 + 1*4 + 0*(-1) + 2*0.1 + 0*6 + 0*(-2) = 13.0
    assert row["points"]["value"] == 13.0
    assert row["points"]["reason"] is None
    assert row["points"]["source"] == "replay"
    assert row["gameStatus"] == "Final"
    assert data["teamTotal"]["value"] == 13.0
    assert data["progress"]["value"] == 1.0


def test_later_summary_replaces_stats(api, monkeypatch):
    import panel
    _pin_now(panel, monkeypatch, "2026-10-11T18:13:41Z")
    seed(api)
    ingest_summary(fresh_summary(), GAME, source="replay")
    corrected = fresh_summary()
    for team in corrected["boxscore"]["players"]:
        for cat in team["statistics"]:
            if cat["name"] == "passing":
                for entry in cat["athletes"]:
                    if entry["athlete"]["id"] == HURTS:
                        entry["stats"][cat["keys"].index("passingYards")] = "300"
    ingest_summary(corrected, GAME, source="replay")
    record = panel.player_statistics(HURTS)
    assert float(record["stats"]["passing_yards"]) == 300
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    assert data["rows"][0]["points"]["value"] == 16.2  # 300*0.04 + 4 + 0.2


def test_absent_athlete_stays_unavailable(api):
    import panel
    seed(api, starters=[{"athlete_id": "9999999", "name": "Nobody", "team": "PHI", "slot": "QB"}])
    ingest_summary(fresh_summary(), GAME, source="replay")
    assert panel.player_statistics("9999999") is None
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    assert data["rows"][0]["points"] == {"value": None, "reason": "statistics unavailable",
                                          "source": None, "asOf": None, "stale": True}


def test_yahoo_modifiers_score_from_boxscore(api, monkeypatch, tmp_path):
    import matcher
    import panel
    player_map = tmp_path / "player_map.json"
    player_map.write_text(json.dumps({"schemaVersion": 1, "players": [
        {"espn_athlete_id": COOPER, "name": "Darius Cooper", "team": "PHI",
         "position": "WR", "confidence": "exact"}]}))
    monkeypatch.setattr(matcher, "PLAYER_MAP_PATH", player_map)
    seed(api, source="yahoo", starters=[{"player_key": "nfl.p.1", "name": "Darius Cooper",
                                          "team": "PHI", "positions": ["WR"], "slot": "WR"}])
    ingest_summary(fresh_summary(), GAME, source="replay")
    _pin_now(panel, monkeypatch, "2026-10-11T18:13:41Z")
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    # 2*1.5 + 71*0.2 + 1*4 = 21.2
    assert data["rows"][0]["points"]["value"] == 21.2


def _project(panel, game, event_id, event_time):
    event = {"gameId": game, "eventId": event_id, "revision": 1, "source": "live",
             "score": {"away": 0, "home": 0}, "fieldPosition": 50, "possession": None,
             "playerIds": [HURTS], "eventTime": event_time, "period": 1,
             "scoringPlay": False}
    panel.project(event, [{"profileId": "owner", "eventId": event_id, "revision": 1,
                           "starters": [], "cursor": None}])


def test_prior_game_record_not_served_for_current_game(api):
    # R1 F1: game A final stats must not show as points once the panel has
    # projected a later game B for the starter and B has no Hurts boxscore.
    import panel
    seed(api)
    ingest_summary(fresh_summary(), GAME, source="replay")
    _project(panel, GAME, "a-1", "2026-10-11T17:13:41Z")
    later = fresh_summary()
    later["header"]["id"] = "401872999"
    status = later["header"]["competitions"][0]["status"]["type"]
    status.update({"state": "in", "shortDetail": "Q1 15:00", "detail": "Q1 15:00"})
    for team in later["boxscore"]["players"]:
        for cat in team["statistics"]:
            cat["athletes"] = [e for e in cat["athletes"] if e["athlete"]["id"] != HURTS]
    for drive in later["drives"]["previous"]:
        for play in drive.get("plays", []):
            play["id"] = "b-" + play["id"]
            if play.get("wallclock"):
                play["wallclock"] = "2026-10-18T17:00:00Z"
    ingest_summary(later, "401872999", source="live")
    _project(panel, "401872999", "b-1", "2026-10-18T17:00:00Z")
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    row = data["rows"][0]
    assert row["points"]["value"] is None
    assert row["points"]["reason"] == "no statistics for current game"
    assert row["gameStatus"] is None
    assert data["teamTotal"]["value"] is None
    assert data["progress"]["value"] is None


def test_malformed_boxscore_values_are_skipped(api):
    # R1 F2: NaN/Infinity/overflow values and an unhashable key must not crash.
    from feed_ingest.normalize import boxscore_statistics
    payload = fresh_summary()
    for team in payload["boxscore"]["players"]:
        for cat in team["statistics"]:
            if cat["name"] == "passing":
                cat["keys"] = list(cat["keys"]) + [["unhashable"]]
                for entry in cat["athletes"]:
                    entry["stats"] = list(entry["stats"]) + ["7"]
                    if entry["athlete"]["id"] == HURTS:
                        entry["stats"][cat["keys"].index("passingYards")] = "NaN"
                        entry["stats"][cat["keys"].index("passingTouchdowns")] = "1e999999"
                        entry["stats"][cat["keys"].index("interceptions")] = "Infinity"
    [record] = [r for r in boxscore_statistics(payload, GAME) if r["athleteId"] == HURTS]
    assert {k: float(v) for k, v in record["stats"].items()} == {
        "rushing_yards": 2, "rushing_touchdowns": 0, "fumbles_lost": 0}
    # The same bad values as plain strings pass the schema; ingest must store
    # the remaining good stats instead of crashing the poll.
    clean_keys = fresh_summary()
    for team in clean_keys["boxscore"]["players"]:
        for cat in team["statistics"]:
            if cat["name"] == "passing":
                for entry in cat["athletes"]:
                    if entry["athlete"]["id"] == HURTS:
                        entry["stats"][cat["keys"].index("passingYards")] = "NaN"
    ingest_summary(clean_keys, GAME, source="replay")


def test_live_record_survives_replay_fallback(api):
    # R1 F3/F4: load_statistics + store must not replace a live record.
    import panel
    from feed_ingest.ingest import store_player_statistics
    from feed_ingest.replay import load_statistics
    live = fresh_summary()
    for team in live["boxscore"]["players"]:
        for cat in team["statistics"]:
            if cat["name"] == "passing":
                for entry in cat["athletes"]:
                    if entry["athlete"]["id"] == HURTS:
                        entry["stats"][cat["keys"].index("passingYards")] = "400"
    ingest_summary(live, GAME, source="live")
    store_player_statistics(load_statistics(GAME, FIXTURES))
    record = panel.player_statistics(HURTS)
    assert record["source"] == "live"
    assert float(record["stats"]["passing_yards"]) == 400


def test_older_statistics_do_not_replace_newer(api):
    # R1 F3: an older asOf must not overwrite a newer record for the game.
    import panel
    newer = fresh_summary()
    for drive in newer["drives"]["previous"]:
        for play in drive.get("plays", []):
            if play.get("wallclock"):
                play["wallclock"] = "2026-10-11T18:00:00Z"
    ingest_summary(newer, GAME, source="live")
    stale = fresh_summary()
    for team in stale["boxscore"]["players"]:
        for cat in team["statistics"]:
            if cat["name"] == "passing":
                for entry in cat["athletes"]:
                    if entry["athlete"]["id"] == HURTS:
                        entry["stats"][cat["keys"].index("passingYards")] = "100"
    ingest_summary(stale, GAME, source="live")
    record = panel.player_statistics(HURTS)
    assert record["asOf"] == "2026-10-11T18:00:00Z"
    assert float(record["stats"]["passing_yards"]) == 220


def _pin_now(panel, monkeypatch, stamp):
    monkeypatch.setattr(panel, "now", lambda: stamp)


def test_stale_final_record_not_served_as_current(api, monkeypatch):
    # #94: only stored record is a Final from a previous NFL fantasy week (asOf Sunday
    # 2026-10-11T17:13:41Z, now after the Tuesday 09:00Z rollover); no new-game event
    # mentions the starter, so the panel must start unknown.
    import panel
    seed(api)
    ingest_summary(fresh_summary(), GAME, source="replay")
    _pin_now(panel, monkeypatch, "2026-10-13T09:00:01Z")
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    row = data["rows"][0]
    assert row["points"]["value"] is None
    assert row["points"]["reason"] == "no statistics for current game"
    assert row["gameStatus"] is None
    assert data["teamTotal"]["value"] is None
    assert data["progress"]["value"] is None


def test_nfl_final_lasts_the_fantasy_week(api, monkeypatch):
    # Owner 2026-10-23: NFL points last Thursday to Monday night; a Sunday final is
    # still current on Monday night, 13h and more after the game.
    import panel
    seed(api)
    ingest_summary(fresh_summary(), GAME, source="replay")
    _pin_now(panel, monkeypatch, "2026-10-13T08:59:59Z")
    row = panel.snapshot("owner", "league-a/team-7")["data"]["rows"][0]
    assert row["points"]["value"] == 13.0
    assert row["gameStatus"] == "Final"


def test_final_record_inside_window_still_served(api, monkeypatch):
    # #94: a Final inside the 12h window is still current.
    import panel
    seed(api)
    ingest_summary(fresh_summary(), GAME, source="replay")
    _pin_now(panel, monkeypatch, "2026-10-12T05:13:41Z")  # exactly 12h after asOf
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    row = data["rows"][0]
    assert row["points"]["value"] == 13.0
    assert row["gameStatus"] == "Final"
    assert data["progress"]["value"] == 1.0


def test_live_record_outside_window_still_served(api, monkeypatch):
    # #94: the window only retires finals; a live game is still served.
    import panel
    seed(api)
    live = fresh_summary()
    status = live["header"]["competitions"][0]["status"]["type"]
    status.update({"state": "in", "shortDetail": "Q3 04:12", "detail": "Q3 04:12"})
    ingest_summary(live, GAME, source="live")
    _pin_now(panel, monkeypatch, "2026-10-12T06:13:42Z")
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    row = data["rows"][0]
    assert row["points"]["value"] == 13.0
    assert row["gameStatus"] == "Q3 04:12"
    assert data["progress"]["value"] == 0.5


def test_expiration_advances_panel_revision(api, monkeypatch):
    # #94 F1: the TV consumer discards a snapshot whose revision is not
    # greater than the one it holds, so read-time expiration must advance
    # the revision; stable rereads must not churn it.
    import panel
    seed(api)
    ingest_summary(fresh_summary(), GAME, source="replay")
    _pin_now(panel, monkeypatch, "2026-10-12T05:13:41Z")  # exactly 12h after asOf
    before = panel.snapshot("owner", "league-a/team-7")
    assert before["data"]["rows"][0]["points"]["value"] == 13.0
    assert panel.snapshot("owner", "league-a/team-7")["revision"] == before["revision"]
    _pin_now(panel, monkeypatch, "2026-10-13T09:00:01Z")  # NFL week rolled over: expired
    after = panel.snapshot("owner", "league-a/team-7")
    assert after["data"]["rows"][0]["points"]["value"] is None
    assert after["revision"] > before["revision"], "consumer ignores equal/older revisions"
    assert panel.snapshot("owner", "league-a/team-7")["revision"] == after["revision"]


def _summary_with_wallclock(wallclock):
    payload = fresh_summary()
    for drive in payload["drives"]["previous"]:
        for play in drive.get("plays", []):
            play["wallclock"] = wallclock
    return payload


@pytest.mark.parametrize("wallclock", [None, "not-a-date", "2026-10-11T17:13:41"])
def test_undatable_final_not_served_as_current(api, monkeypatch, wallclock):
    # #94 F2: a final whose asOf is missing, unparseable or timezone-naive
    # cannot be shown to be current; it must fail closed, never crash.
    import panel
    seed(api)
    ingest_summary(_summary_with_wallclock(wallclock), GAME, source="replay")
    _pin_now(panel, monkeypatch, "2026-10-20T05:13:41Z")
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    row = data["rows"][0]
    assert row["points"]["value"] is None
    assert row["points"]["reason"] == "no statistics for current game"
    assert row["gameStatus"] is None
    assert data["teamTotal"]["value"] is None
    assert data["progress"]["value"] is None


def test_aware_offset_final_inside_window_still_served(api, monkeypatch):
    # #94 F2: an aware non-UTC asOf is usable: 12:13:41-05:00 is 17:13:41Z,
    # so exactly 12h later in UTC the final is still inside the window.
    import panel
    seed(api)
    ingest_summary(_summary_with_wallclock("2026-10-11T12:13:41-05:00"), GAME, source="replay")
    _pin_now(panel, monkeypatch, "2026-10-12T05:13:41Z")
    data = panel.snapshot("owner", "league-a/team-7")["data"]
    assert data["rows"][0]["points"]["value"] == 13.0
    assert data["rows"][0]["gameStatus"] == "Final"


def test_no_floats_stored(api):
    ingest_summary(fresh_summary(), GAME, source="replay")
    def floats(value):
        if isinstance(value, float):
            return [value]
        if isinstance(value, dict):
            return [f for v in value.values() for f in floats(v)]
        if isinstance(value, list):
            return [f for v in value for f in floats(v)]
        return []
    for item in api.table("PlayerStats").scan()["Items"]:
        assert floats(item) == [], f"float stored in DynamoDB item: {item!r}"
