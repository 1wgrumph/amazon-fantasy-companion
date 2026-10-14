"""CONTRACT-AFC-P2-PRESETS: exactly two manual scoring tables, default Half-PPR."""

_BASE = {
    "rushing_yards": 0.1,
    "receiving_yards": 0.1,
    "rushing_touchdowns": 6,
    "receiving_touchdowns": 6,
    "passing_yards": 0.04,
    "passing_touchdowns": 4,
    "interceptions_thrown": -1,
    "fumbles_lost": -2,
}
TABLES = {
    "PPR": dict(_BASE, receptions=1.0),
    "Half-PPR": dict(_BASE, receptions=0.5),
}
DEFAULT_PRESET = "Half-PPR"


def score(preset, stats):
    """Points for feed statistics under one preset; missing stats count as zero."""
    if preset not in TABLES:
        raise ValueError(f"Unknown scoring preset: {preset!r}")
    table = TABLES[preset]
    unknown = set(stats) - set(table)
    if unknown:
        raise ValueError("Statistics without a preset row: " + ", ".join(sorted(unknown)))
    return sum(table[stat] * value for stat, value in stats.items())
