"""DES-AFC-P2-LINEUP lineup sources (Yahoo read-only or labeled manual) and scoring presets.

One stored Lineups row per profile holds one active source per team/league
(AFC-PR-007). With no pair, the sole stored lineup is that source.
Manual rows score under the profile's preset (default Half-PPR); Yahoo rows
carry the Yahoo league scoring verbatim (AFC-PR-065).
"""

import store


def _preset_label(stored):
    """Settings.scoringPreset enum (frozen openapi) to a CONTRACT-AFC-P2-PRESETS label."""
    labels = {"ppr": "PPR", "halfPpr": "Half-PPR"}
    if stored not in labels:
        raise ValueError(f"Unknown stored scoring preset: {stored!r}")
    return labels[stored]


def active_lineup(profile_id, team_league=None):
    """One pair's Lineup, or the sole Lineup when team_league is omitted. None if absent."""
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError("profile_id must be a non-empty string")
    row = store.get_lineup(profile_id, team_league)
    if row is None:
        return None
    source = row.get("source")
    if source == "manual":
        profile = store.get_profile(profile_id) or {}
        stored = profile.get("settings", {}).get("scoringPreset", "halfPpr")
        scoring = {"preset": _preset_label(stored)}
    elif source == "yahoo":
        scoring = row.get("scoring")
        if not isinstance(scoring, dict) or "preset" in scoring:
            raise ValueError("Stored Yahoo lineup has no league scoring")
    else:
        raise ValueError(f"Unknown stored lineup source: {source!r}")
    return {"source": source, "team": row.get("team"), "league": row.get("league"),
            "starters": row.get("starters", []), "scoring": scoring}
