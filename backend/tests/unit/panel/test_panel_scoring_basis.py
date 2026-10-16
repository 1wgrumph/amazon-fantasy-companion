"""Scoring basis and points (VCASE-AFC-PR-065, VCASE-AFC-PR-039 negative; CONTRACT-AFC-P2-PRESETS).

Manual lineups score under the selected preset (PPR or Half-PPR, default
Half-PPR) applied by reference to lineup.presets.TABLES; Yahoo lineups score
under Yahoo league stat_modifiers. Every value is shown with its basis; no
third preset and no point without a table row.
"""

import pytest

from panel_support import (RECEIVER, STAT_NAMES, YAHOO_RECEIVER, check_value,  # noqa: F401
                           game_event, match, number, panel_env, points, row, seed_lineup,
                           seed_profile, statistics)

# Coefficient-isolating quantities, one statistic per case.
QUANTITY = {"receptions": 3, "rushing_yards": 30, "receiving_yards": 40, "rushing_touchdowns": 1,
            "receiving_touchdowns": 2, "passing_yards": 100, "passing_touchdowns": 1,
            "interceptions_thrown": 2, "fumbles_lost": 1}
PRESETS = {"ppr": "PPR", "halfPpr": "Half-PPR"}


def manual(env, stats, **settings):
    seed_profile("fan", **settings)
    seed_lineup("fan", [RECEIVER])
    env.stats["9000001"] = statistics(**stats)
    event = game_event("401999001201")
    env.project(event, [match("fan", event)])
    return env.data("fan")


def yahoo(env, stats, **settings):
    seed_profile("fan", **settings)
    seed_lineup("fan", [YAHOO_RECEIVER], source="yahoo")
    env.stats["9000001"] = statistics(**stats)
    event = game_event("401999001201")
    env.project(event, [match("fan", event)])
    return env.data("fan")


def test_default_basis_is_half_ppr(panel_env):
    data = manual(panel_env, {"receptions": 4})
    assert data["scoringBasis"] == "halfPpr"
    assert points(data, "9000001") == pytest.approx(2.0)


def test_ppr_selection_scores_a_full_point_per_reception(panel_env):
    data = manual(panel_env, {"receptions": 4}, scoringPreset="ppr")
    assert data["scoringBasis"] == "ppr"
    assert points(data, "9000001") == pytest.approx(4.0)


def test_half_ppr_selection_scores_half_a_point_per_reception(panel_env):
    data = manual(panel_env, {"receptions": 4}, scoringPreset="halfPpr")
    assert data["scoringBasis"] == "halfPpr"
    assert points(data, "9000001") == pytest.approx(2.0)


@pytest.mark.parametrize("stat", STAT_NAMES)
@pytest.mark.parametrize("preset", sorted(PRESETS))
def test_each_statistic_scores_its_preset_table_row(panel_env, preset, stat):
    from lineup import presets
    expected = presets.TABLES[PRESETS[preset]][stat] * QUANTITY[stat]
    data = manual(panel_env, {stat: QUANTITY[stat]}, scoringPreset=preset)
    assert data["scoringBasis"] == preset
    assert points(data, "9000001") == pytest.approx(expected, abs=0.005), (preset, stat)


def test_yahoo_lineup_scores_under_league_stat_modifiers(panel_env):
    # Modifiers 1.5/rec, 0.2/yd, 4/TD: 6 + 10 + 4 = 20 (PPR would be 15, Half-PPR 13).
    data = yahoo(panel_env, {"receptions": 4, "receiving_yards": 50, "receiving_touchdowns": 1})
    assert data["scoringBasis"] == "yahooLeague"
    assert points(data, "9000001") == pytest.approx(20.0, abs=0.005)


def test_yahoo_lineup_ignores_the_manual_preset(panel_env):
    data = yahoo(panel_env, {"receptions": 4}, scoringPreset="ppr")
    assert data["scoringBasis"] == "yahooLeague", "a preset table never scores a Yahoo league"
    assert points(data, "9000001") == pytest.approx(6.0)


def test_yahoo_statistic_without_a_modifier_scores_nothing(panel_env):
    data = yahoo(panel_env, {"receptions": 2, "passing_yards": 100})
    assert points(data, "9000001") == pytest.approx(3.0)


def test_yahoo_rows_use_espn_identity(panel_env):
    data = yahoo(panel_env, {"receptions": 2})
    assert row(data, "9000001")["name"] == "Sample Receiver"


def test_manual_statistic_without_a_table_row_awards_no_points(panel_env):
    data = manual(panel_env, {"receptions": 2, "two_point_conversions": 1})
    value = points(data, "9000001")
    assert value is None or value == pytest.approx(1.0), \
        f"a manual point without a preset table row was awarded: {value!r}"


def test_third_preset_is_never_scored(panel_env):
    seed_profile("fan", scoringPreset="standard")
    seed_lineup("fan", [RECEIVER])
    panel_env.stats["9000001"] = statistics(receptions=4)
    event = game_event("401999001201")
    try:
        panel_env.project(event, [match("fan", event)])
        envelope = panel_env.snapshot("fan")
    except AssertionError:
        raise
    except Exception:
        return  # refused outright: nothing scored under an unknown preset
    data = envelope["data"]
    assert data.get("scoringBasis") != "standard"
    for item in data.get("rows", []):
        assert check_value(item["points"], "points") is None, \
            f"a third preset scored a value: {item!r}"
    assert number(data["teamTotal"]["value"]) is None


@pytest.mark.parametrize("source,basis", [("manual", "halfPpr"), ("yahoo", "yahooLeague")])
def test_every_point_value_travels_with_its_basis(panel_env, source, basis):
    data = (manual if source == "manual" else yahoo)(panel_env, {"receptions": 2})
    assert points(data, "9000001") is not None
    assert data["scoringBasis"] == basis
