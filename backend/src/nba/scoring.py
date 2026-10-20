"""NBA points-league scoring basis for the stretch spike (DEC-AFC-NBA-STRETCH-20261020).

Stat names are the ESPN NBA boxscore keys (nba.normalize maps only these).
Mirrors lineup.presets.score: a statistic without a table row is refused.
"""

NBA_POINTS_TABLE = {
    "points": 1,
    "rebounds": 1.2,
    "assists": 1.5,
    "steals": 3,
    "blocks": 3,
    "turnovers": -1,
}


def score(stats):
    """Fantasy points for one athlete's box-score stats; missing stats count zero."""
    unknown = set(stats) - set(NBA_POINTS_TABLE)
    if unknown:
        raise ValueError("Statistics without an NBA table row: " + ", ".join(sorted(unknown)))
    return sum(NBA_POINTS_TABLE[stat] * float(value) for stat, value in stats.items())
