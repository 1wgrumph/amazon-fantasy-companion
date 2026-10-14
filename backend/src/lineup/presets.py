"""CONTRACT-AFC-P2-PRESETS: exactly two manual scoring tables, default Half-PPR.

Values live in functions, not module statements, so the mutation gate can
mutate them; TABLES and DEFAULT_PRESET stay readable as module attributes.
"""


def _tables():
    base = {
        "rushing_yards": 0.1,
        "receiving_yards": 0.1,
        "rushing_touchdowns": 6,
        "receiving_touchdowns": 6,
        "passing_yards": 0.04,
        "passing_touchdowns": 4,
        "interceptions_thrown": -1,
        "fumbles_lost": -2,
    }
    return {"PPR": dict(base, receptions=1.0), "Half-PPR": dict(base, receptions=0.5)}


def __getattr__(name):
    if name == "TABLES":
        return _tables()
    if name == "DEFAULT_PRESET":
        return "Half-PPR"
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def score(preset, stats):
    """Points for feed statistics under one preset; missing stats count as zero."""
    tables = _tables()
    if preset not in tables:
        raise ValueError(f"Unknown scoring preset: {preset!r}")
    table = tables[preset]
    unknown = set(stats) - set(table)
    if unknown:
        raise ValueError("Statistics without a preset row: " + ", ".join(sorted(unknown)))
    return sum(table[stat] * value for stat, value in stats.items())
