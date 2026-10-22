"""A statistics write never calls project(), so the snapshot revision has to
move off the row records (#137). The TV drops a revision that is not strictly
newer. Same reads stay put. A lineup swap onto older asOf stamps must not
fall backwards either.
"""

import json
from pathlib import Path

import pytest
from botocore.client import BaseClient

from panel_support import (LEAGUE, PASSER, RECEIVER, TEAM, at,
                           seed_lineup, seed_profile, statistics)

WING = {"athlete_id": "9000001", "name": "Sample Wing", "team": "MIN", "slot": "SG"}


@pytest.fixture
def panel_env(api, monkeypatch):
    """Exercise real statistics writes/reads, not a dictionary replacing the reader."""
    from types import SimpleNamespace
    import panel
    monkeypatch.setattr(panel, "now", lambda: at(5))
    return SimpleNamespace(module=panel, api=api,
                           snapshot=lambda profile: panel.snapshot(profile, None))


def write_statistics(athlete, record):
    import store
    return store.put_player_statistics(dict(record, athleteId=athlete))


def test_nfl_stats_only_change_raises_revision(panel_env):
    # The older row moves. A max-of-asOf term would ignore it.
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    assert write_statistics("9000001", statistics(receptions=1, as_of=at(10)))
    assert write_statistics("9000005", statistics(passing_yards=10, as_of=at(100)))
    before = panel_env.snapshot("fan")
    assert write_statistics("9000001", statistics(receptions=4, as_of=at(50)))
    after = panel_env.snapshot("fan")
    assert after["data"]["rows"][0]["points"]["value"] == 2.0
    assert after["data"]["rows"][0]["points"]["asOf"] == at(50)
    assert after["revision"] > before["revision"], (
        f"stats-only change left revision {before['revision']}")
    assert panel_env.snapshot("fan")["revision"] == after["revision"]


def test_nba_stats_only_change_raises_revision(panel_env, monkeypatch):
    import store
    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    seed_profile("fan")
    store.put_lineup({"profileId": "fan", "source": "manual", "sport": "nba",
                      "team": TEAM, "league": LEAGUE, "starters": [dict(WING)],
                      "updatedAt": at(0)})
    assert write_statistics("9000001", statistics(points=2, as_of=at(10)))
    before = panel_env.snapshot("fan")
    assert write_statistics("9000001", statistics(points=8, as_of=at(70)))
    after = panel_env.snapshot("fan")
    assert after["data"].get("sport") == "nba"
    assert after["data"]["rows"][0]["points"]["value"] == 8.0
    assert after["revision"] > before["revision"], (
        f"stats-only change left revision {before['revision']}")
    assert panel_env.snapshot("fan")["revision"] == after["revision"]


def test_unchanged_stats_keep_the_revision(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    assert write_statistics("9000001", statistics(receptions=2, as_of=at(10)))
    first = panel_env.snapshot("fan")
    second = panel_env.snapshot("fan")
    assert first["revision"] == second["revision"]


def test_lineup_change_to_older_asof_does_not_regress(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    assert write_statistics("9000001", statistics(receptions=3, as_of=at(5000)))
    before = panel_env.snapshot("fan")
    seed_lineup("fan", [PASSER])
    assert write_statistics("9000005", statistics(passing_yards=10, as_of=at(1)))
    after = panel_env.snapshot("fan")
    assert after["data"]["rows"][0]["playerId"] == "9000005"
    assert after["data"]["rows"][0]["points"]["asOf"] == at(1)
    assert after["revision"] > before["revision"]
    assert panel_env.snapshot("fan")["revision"] == after["revision"]


@pytest.mark.parametrize("sport", ["nfl", "nba"])
@pytest.mark.parametrize("dated", [True, False])
def test_r01_values_and_status_change_without_a_new_timestamp(panel_env, monkeypatch, sport, dated):
    import store
    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    seed_profile("fan")
    store.put_lineup({"profileId": "fan", "source": "manual", "sport": sport,
                      "team": TEAM, "league": LEAGUE, "starters": [RECEIVER], "updatedAt": at(0)})
    record = statistics(**({"points": 2} if sport == "nba" else {"receptions": 2}))
    if not dated:
        record["asOf"] = None
    assert write_statistics("9000001", record)
    before = panel_env.snapshot("fan")
    record["stats"] = {"points": 8} if sport == "nba" else {"receptions": 8}
    assert write_statistics("9000001", record)
    after = panel_env.snapshot("fan")
    assert after["data"]["teamTotal"]["value"] > before["data"]["teamTotal"]["value"]
    assert after["revision"] > before["revision"]
    record["gameStatus"] = "Halftime"
    assert write_statistics("9000001", record)
    status_changed = panel_env.snapshot("fan")
    assert status_changed["data"]["rows"][0]["gameStatus"] == "Halftime"
    assert status_changed["revision"] > after["revision"]
    assert not write_statistics("9000001", record)
    assert panel_env.snapshot("fan")["revision"] == status_changed["revision"]


def test_r01_real_nba_boxscore_correction_keeps_last_play_time(panel_env, monkeypatch):
    from nba.normalize import boxscore_statistics_nba
    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    import store
    seed_profile("fan")
    store.put_lineup({"profileId": "fan", "source": "manual", "sport": "nba",
                      "team": TEAM, "league": LEAGUE,
                      "starters": [dict(WING, athlete_id="9100001")], "updatedAt": at(0)})
    payload = json.loads((Path(__file__).parents[2] / "fixtures/nba/summary.json").read_text())
    original = boxscore_statistics_nba(payload, "401999101")[0]
    assert write_statistics("9100001", original)
    before = panel_env.snapshot("fan")
    payload["boxscore"]["players"][0]["statistics"][0]["athletes"][0]["stats"][1] = "26"
    corrected = boxscore_statistics_nba(payload, "401999101")[0]
    assert corrected["asOf"] == original["asOf"]
    assert write_statistics("9100001", corrected)
    after = panel_env.snapshot("fan")
    assert before["data"]["teamTotal"]["value"] == 37.8
    assert after["data"]["teamTotal"]["value"] == 43.8
    assert after["revision"] > before["revision"]


def test_r01_real_nfl_ingest_correction_keeps_last_play_time(panel_env, monkeypatch):
    from feed_ingest.ingest import ingest_summary
    seed_profile("fan")
    seed_lineup("fan", [dict(PASSER, athlete_id="4040715")])
    monkeypatch.setattr(panel_env.module, "now", lambda: "2026-10-11T18:13:41Z")
    game = "401872981"
    path = Path(__file__).parents[3] / "fixtures/replay" / game / "001-summary.json"
    payload = json.loads(path.read_text())
    ingest_summary(payload, game)
    before = panel_env.snapshot("fan")
    for team in payload["boxscore"]["players"]:
        for category in team["statistics"]:
            if category["name"] == "passing":
                for entry in category["athletes"]:
                    if entry["athlete"]["id"] == "4040715":
                        entry["stats"][category["keys"].index("passingYards")] = "300"
    ingest_summary(payload, game)
    after = panel_env.snapshot("fan")
    assert before["data"]["teamTotal"]["value"] == 13.0
    assert after["data"]["teamTotal"]["value"] == 16.2
    assert before["data"]["teamTotal"]["asOf"] == after["data"]["teamTotal"]["asOf"]
    assert after["revision"] > before["revision"]


@pytest.mark.parametrize("missing", [False, True])
def test_r02_lagging_replica_cannot_lower_the_revision(panel_env, monkeypatch, missing):
    import os
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    assert write_statistics("9000001", statistics(receptions=1, as_of=at(10)))
    table = panel_env.api.table("PlayerStats")
    old_response = table.meta.client.get_item(TableName=table.name, Key={"athleteId": "9000001"})
    assert write_statistics("9000001", statistics(receptions=4, as_of=at(70)))
    before = panel_env.snapshot("fan")
    real_call = BaseClient._make_api_call
    requests = []

    def lagging_read(client, operation, params):
        if operation == "GetItem" and params.get("TableName") == os.environ["PLAYER_STATS_TABLE"]:
            requests.append(params)
            if not params.get("ConsistentRead"):
                return {} if missing else old_response
        return real_call(client, operation, params)

    monkeypatch.setattr(BaseClient, "_make_api_call", lagging_read)
    after = panel_env.snapshot("fan")
    assert after["revision"] == before["revision"]
    assert after["data"] == before["data"]
    assert requests and all(request.get("ConsistentRead") is True for request in requests)


@pytest.mark.parametrize("version", [0, 11])
@pytest.mark.parametrize("profile_version", [0, 1])
def test_r03_deploy_dominates_old_formula_even_for_legacy_zero(panel_env, version, profile_version):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    profile_table = panel_env.api.table("Profiles")
    profile_row = profile_table.get_item(Key={"profileId": "fan"})["Item"]
    profile_table.put_item(Item=dict(profile_row, revision=profile_version))
    table = panel_env.api.table("Lineups")
    row = table.get_item(Key={"profileId": "fan"})["Item"]
    if version:
        row["lineupVersion"] = version
    else:
        row.pop("lineupVersion")
    table.put_item(Item=row)
    panel_env.api.table("Panels").put_item(Item={"profileId": "fan", "teamLeague": LEAGUE + "/" + TEAM,
                                                 "freshness": {"counter": 50000}})
    # Include the conservative maximum of all old low fields, even with no stats now.
    deployed_revision = 128 * (50000 + profile_version + version) + 96
    assert panel_env.snapshot("fan")["revision"] > deployed_revision


def test_r04_final_expiry_survives_js_number_round_trip_at_v512(panel_env, monkeypatch):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    table = panel_env.api.table("Lineups")
    row = table.get_item(Key={"profileId": "fan"})["Item"]
    table.put_item(Item=dict(row, lineupVersion=512))
    assert write_statistics("9000001", statistics(state="post", status="Final", receptions=2))
    monkeypatch.setattr(panel_env.module, "now", lambda: at(43200))
    before = panel_env.snapshot("fan")
    monkeypatch.setattr(panel_env.module, "now", lambda: at(43201))
    after = panel_env.snapshot("fan")
    assert before["data"]["teamTotal"]["value"] == 1.0
    assert after["data"]["teamTotal"]["value"] is None
    # JSON numbers use binary64 in Vega, matching Python float's integer precision.
    assert float(after["revision"]) > float(before["revision"])
    assert panel_env.snapshot("fan")["revision"] == after["revision"]


def test_maximum_sequence_drop_and_documented_js_history_bound(panel_env):
    seed_profile("fan")
    starters = [dict(RECEIVER, athlete_id=str(9000001 + i)) for i in range(32)]
    seed_lineup("fan", starters)
    table = panel_env.api.table("Lineups")
    row = table.get_item(Key={"profileId": "fan"})["Item"]
    table.put_item(Item=dict(row, lineupVersion=99998))
    for starter in starters:
        panel_env.api.table("PlayerStats").put_item(Item=dict(
            statistics(receptions=2), athleteId=starter["athlete_id"], statsVersion=(1 << 24) - 1))
    # Include the maximum pair counter; the final lineup + profile sum is 100,000.
    panel_env.api.table("Panels").put_item(Item={"profileId": "fan", "teamLeague": LEAGUE + "/" + TEAM,
                                                 "freshness": {"counter": (1 << 24) - 1}})
    before = panel_env.snapshot("fan")
    seed_lineup("fan", [])
    after = panel_env.snapshot("fan")
    assert after["revision"] > before["revision"]
    assert after["revision"] <= (1 << 53) - 1
    assert int(float(after["revision"])) == after["revision"]


@pytest.mark.parametrize("change", ["lineup_sport", "lineup_pair", "profile_pair", "profile_visibility"])
def test_combined_maximum_contributions_survive_selection_changes(panel_env, monkeypatch, change):
    import store
    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    monkeypatch.setattr(panel_env.module, "now", lambda: at(43201))
    seed_profile("fan")
    starters = [dict(WING, athlete_id=str(9000001 + i)) for i in range(32)]
    lineup = {"profileId": "fan", "source": "manual", "sport": "nba", "team": TEAM,
              "league": LEAGUE, "starters": starters, "updatedAt": at(0)}
    store.put_lineup(lineup)
    cap = (1 << 24) - 1
    for starter in starters:
        panel_env.api.table("PlayerStats").put_item(Item=dict(
            statistics(state="post", status="Final", points=2),
            athleteId=starter["athlete_id"], statsVersion=cap))
    panel_env.api.table("PlayerStats").put_item(Item={
        "athleteId": "pregame", "sequence": cap, "teams": {"MIN": "tip"}, "asOf": at(0)})
    panel_env.api.table("Panels").put_item(Item={"profileId": "fan", "teamLeague": LEAGUE + "/" + TEAM,
                                                 "freshness": {"counter": cap}})
    before = panel_env.snapshot("fan")
    if change == "lineup_sport":
        store.put_lineup(dict(lineup, sport="nfl", starters=[]))
    elif change == "lineup_pair":
        store.put_lineup(dict(lineup, team="other", sport="nfl", starters=[]))
    else:
        settings = ({"teamLeague": {"league": LEAGUE, "team": "other"}}
                    if change == "profile_pair" else {"panelPrefs": {"visible": False}})
        assert store.put_profile("fan", settings, 1, at(1))
    after = panel_env.snapshot("fan")
    assert after["revision"] > before["revision"]
    assert panel_env.snapshot("fan")["revision"] == after["revision"]
    if change.endswith("pair") or change == "lineup_sport":
        assert after["data"]["rows"] == []
    else:
        assert after["data"]["visible"] is False
    # Returning to the old selection must allocate another distinct revision.
    if change.startswith("lineup"):
        store.put_lineup(lineup)
    else:
        assert store.put_profile("fan", {}, 2, at(2))
    restored = panel_env.snapshot("fan")
    assert restored["revision"] > after["revision"]
    assert panel_env.snapshot("fan")["revision"] == restored["revision"]


def test_combined_documented_js_bound_includes_profile_and_pregame(panel_env, monkeypatch):
    import store
    monkeypatch.setenv("AFC_ENABLE_NBA", "1")
    monkeypatch.setattr(panel_env.module, "now", lambda: at(43201))
    seed_profile("fan")
    starters = [dict(WING, athlete_id=str(9000001 + i)) for i in range(32)]
    store.put_lineup({"profileId": "fan", "source": "manual", "sport": "nba", "team": TEAM,
                      "league": LEAGUE, "starters": starters, "updatedAt": at(0)})
    for table_name, key, field, value in [
        ("Lineups", {"profileId": "fan"}, "lineupVersion", 90000),
        ("Profiles", {"profileId": "fan"}, "revision", 10000),
    ]:
        table = panel_env.api.table(table_name)
        row = table.get_item(Key=key)["Item"]
        table.put_item(Item=dict(row, **{field: value}))
    cap = (1 << 24) - 1
    for starter in starters:
        panel_env.api.table("PlayerStats").put_item(Item=dict(
            statistics(state="post", status="Final", points=2),
            athleteId=starter["athlete_id"], statsVersion=cap))
    panel_env.api.table("PlayerStats").put_item(Item={
        "athleteId": "pregame", "sequence": cap, "teams": {}, "asOf": at(0)})
    panel_env.api.table("Panels").put_item(Item={"profileId": "fan", "teamLeague": LEAGUE + "/" + TEAM,
                                                 "freshness": {"counter": cap}})
    value = panel_env.snapshot("fan")["revision"]
    # 32 statistic sequences, twice the slate sequence plus expiry, and pair counter.
    scale = 35 * cap + 2
    assert value == 128 * (1 + 100000 * scale + 35 * cap + 1) + 96
    assert value <= (1 << 53) - 1
    assert int(float(value)) == value
    assert int(float(value + 1)) == value + 1


def test_projection_counter_exhaustion_preserves_last_snapshot(panel_env):
    from panel_support import game_event, match
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    cap = (1 << 24) - 1
    panel_env.api.table("Panels").put_item(Item={"profileId": "fan", "teamLeague": LEAGUE + "/" + TEAM,
                                                 "freshness": {"counter": cap - 1}})
    event = game_event("first")
    panel_env.module.project(event, [match("fan", event)])
    before = panel_env.snapshot("fan")
    panel_env.module.project(event, [match("fan", event)])
    assert panel_env.snapshot("fan")["revision"] == before["revision"]
    correction = dict(event, revision=2)
    with pytest.raises(RuntimeError, match="projection.*exhausted"):
        panel_env.module.project(correction, [match("fan", correction)])
    assert panel_env.snapshot("fan") == before
