"""CONTRACT-AFC-P2-PRESETS red tests (VCASE-AFC-PR-065).

Exactly two manual scoring tables, default Half-PPR, points equal to the
selected table applied to feed statistics. The register table is the sole
authority for coefficients; this file restates it as the frozen expectation.
"""

import pytest

from lineup_support import attempt, require_module


def presets():
    return require_module("lineup.presets")


BASE_ROWS = {
    "rushing_yards": 0.1,
    "receiving_yards": 0.1,
    "rushing_touchdowns": 6,
    "receiving_touchdowns": 6,
    "passing_yards": 0.04,
    "passing_touchdowns": 4,
    "interceptions_thrown": -1,
    "fumbles_lost": -2,
}
EXPECTED_TABLES = {
    "PPR": dict(BASE_ROWS, receptions=1.0),
    "Half-PPR": dict(BASE_ROWS, receptions=0.5),
}


def test_exactly_two_preset_tables():
    tables = attempt(lambda: presets().TABLES)
    assert set(tables) == {"PPR", "Half-PPR"}
    assert len(tables) == 2


def test_preset_tables_match_the_contract():
    assert attempt(lambda: presets().TABLES) == EXPECTED_TABLES


def test_tables_cover_only_contract_stats():
    tables = attempt(lambda: presets().TABLES)
    assert set(tables["PPR"]) == set(EXPECTED_TABLES["PPR"])
    assert set(tables["Half-PPR"]) == set(EXPECTED_TABLES["Half-PPR"])


def test_default_preset_is_half_ppr():
    assert attempt(lambda: presets().DEFAULT_PRESET) == "Half-PPR"


@pytest.mark.parametrize(("preset", "stats", "expected"), [
    ("PPR", {"receptions": 3}, 3.0),
    ("Half-PPR", {"receptions": 3}, 1.5),
    ("PPR", {"rushing_yards": 10}, 1.0),
    ("Half-PPR", {"rushing_yards": 10}, 1.0),
    ("PPR", {"receiving_yards": 10}, 1.0),
    ("Half-PPR", {"receiving_yards": 10}, 1.0),
    ("PPR", {"rushing_touchdowns": 2}, 12),
    ("Half-PPR", {"rushing_touchdowns": 2}, 12),
    ("PPR", {"receiving_touchdowns": 1}, 6),
    ("Half-PPR", {"receiving_touchdowns": 1}, 6),
    ("PPR", {"passing_yards": 25}, 1.0),
    ("Half-PPR", {"passing_yards": 25}, 1.0),
    ("PPR", {"passing_touchdowns": 2}, 8),
    ("Half-PPR", {"passing_touchdowns": 2}, 8),
    ("PPR", {"interceptions_thrown": 2}, -2),
    ("Half-PPR", {"interceptions_thrown": 2}, -2),
    ("PPR", {"fumbles_lost": 1}, -2),
    ("Half-PPR", {"fumbles_lost": 1}, -2),
])
def test_each_table_row_scores_in_isolation(preset, stats, expected):
    assert attempt(presets().score, preset, stats) == pytest.approx(expected)


def test_combined_stats_sum_every_row():
    stats = {"receptions": 5, "receiving_yards": 80, "receiving_touchdowns": 1,
             "rushing_yards": 20, "passing_yards": 250, "passing_touchdowns": 2,
             "interceptions_thrown": 1, "fumbles_lost": 1, "rushing_touchdowns": 0}
    assert attempt(presets().score, "PPR", stats) == pytest.approx(36.0)
    assert attempt(presets().score, "Half-PPR", stats) == pytest.approx(33.5)


def test_missing_stats_count_as_zero():
    assert attempt(presets().score, "PPR", {}) == 0
    assert attempt(presets().score, "Half-PPR", {"receptions": 0}) == 0


@pytest.mark.parametrize("preset", ["Standard", "ppr", "half-ppr", "Half_PPR", ""])
def test_a_third_preset_is_rejected(preset):
    with pytest.raises(ValueError):
        attempt(presets().score, preset, {"receptions": 1})


def test_a_stat_without_a_table_row_is_rejected():
    with pytest.raises(ValueError):
        attempt(presets().score, "PPR", {"receptions": 1, "kick_return_yards": 50})
