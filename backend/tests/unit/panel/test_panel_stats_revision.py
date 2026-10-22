"""A statistics write never calls project(), so the snapshot revision has to
move off the row records (#137). The TV drops a revision that is not strictly
newer. Same reads stay put. A lineup swap onto older asOf stamps must not
fall backwards either.
"""

from panel_support import (LEAGUE, PASSER, RECEIVER, TEAM, at, panel_env,  # noqa: F401
                           seed_lineup, seed_profile, statistics)

WING = {"athlete_id": "9000001", "name": "Sample Wing", "team": "MIN", "slot": "SG"}


def test_nfl_stats_only_change_raises_revision(panel_env):
    # The older row moves. A max-of-asOf term would ignore it.
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    panel_env.stats["9000001"] = statistics(receptions=1, as_of=at(10))
    panel_env.stats["9000005"] = statistics(passing_yards=10, as_of=at(100))
    before = panel_env.snapshot("fan")
    panel_env.stats["9000001"] = statistics(receptions=4, as_of=at(50))
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
    panel_env.stats["9000001"] = statistics(points=2, as_of=at(10))
    before = panel_env.snapshot("fan")
    panel_env.stats["9000001"] = statistics(points=8, as_of=at(70))
    after = panel_env.snapshot("fan")
    assert after["data"].get("sport") == "nba"
    assert after["data"]["rows"][0]["points"]["value"] == 8.0
    assert after["revision"] > before["revision"], (
        f"stats-only change left revision {before['revision']}")
    assert panel_env.snapshot("fan")["revision"] == after["revision"]


def test_unchanged_stats_keep_the_revision(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    panel_env.stats["9000001"] = statistics(receptions=2, as_of=at(10))
    first = panel_env.snapshot("fan")
    second = panel_env.snapshot("fan")
    assert first["revision"] == second["revision"]


def test_lineup_change_to_older_asof_does_not_regress(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    panel_env.stats["9000001"] = statistics(receptions=3, as_of=at(5000))
    before = panel_env.snapshot("fan")
    seed_lineup("fan", [PASSER])
    panel_env.stats["9000005"] = statistics(passing_yards=10, as_of=at(1))
    after = panel_env.snapshot("fan")
    assert after["data"]["rows"][0]["playerId"] == "9000005"
    assert after["data"]["rows"][0]["points"]["asOf"] == at(1)
    assert after["revision"] > before["revision"]
    assert panel_env.snapshot("fan")["revision"] == after["revision"]
