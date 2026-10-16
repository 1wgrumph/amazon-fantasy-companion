"""DES-AFC-P2-PANELSVC PanelState per profile and team/league (P2-B07).

project() persists only the projected game facts per profile (in the Panels
row `freshness` map, the one free-form PanelState attribute): a later
revision of the same event replaces them, an equal or lower revision never
does, so the panel agrees with the alert record. snapshot() derives rows,
points, total and progress at read time from the stored Lineup, the profile
Settings and the statistics seam, so a settings or starter change shows on
the next read with a higher revision and no panel write on the read path.
project() records a fingerprint of the lineup it projected; snapshot()
spends the revision's low bit when the current lineup differs from that
fingerprint, so a starter change outruns the last projected revision.
Projections write conditionally on the stored counter and re-read and
merge on a lost race, so overlapping games never erase each other.

Seams, read at call time through this module: player_statistics(athlete_id)
-> None (unknown) or {gameId, gameState pre|in|post, gameStatus, source
live|replay, asOf, stats}; now() -> RFC 3339 UTC. Stored GameEvents carry no
per-player statistics yet, so production statistics are unknown until a
stats slice lands (P2-B07T R1).
"""

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import matcher
import store
from lineup import presets

STALE_AFTER = 60
_PRESETS = {"ppr": "PPR", "halfPpr": "Half-PPR"}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def player_statistics(athlete_id):
    # shortcut: no per-player statistics are stored yet (P2-B07T R1); every
    # production point reads unknown until a feed slice stores boxscores.
    return None


def _parse(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def _pair(lineup):
    return f"{lineup['league']}/{lineup['team']}"


def _settings(profile_id):
    profile = store.get_profile(profile_id) or {}
    return profile, profile.get("settings") or {}


def _basis(lineup, settings):
    """(wire basis, scoring table); an unknown stored preset is refused."""
    if lineup and lineup.get("source") == "yahoo":
        modifiers = (lineup.get("scoring") or {}).get("stat_modifiers") or {}
        return "yahooLeague", {k: float(v) for k, v in modifiers.items()}
    preset = settings.get("scoringPreset") or "halfPpr"
    if preset not in _PRESETS:
        raise ValueError(f"Unknown scoring preset: {preset!r}")
    return preset, presets.TABLES[_PRESETS[preset]]


def _espn_id(starter):
    if starter.get("athlete_id"):
        return str(starter["athlete_id"])
    try:
        players = json.loads(Path(matcher.PLAYER_MAP_PATH).read_text()).get("players") or []
    except (OSError, ValueError):
        players = []
    positions = starter.get("positions") or []
    entries = [p for p in players if p.get("name") == starter.get("name")
               and p.get("team") == starter.get("team") and p.get("position") in positions]
    return str(entries[0]["espn_athlete_id"]) if len(entries) == 1 else None


def _value(record, table):
    """One points value object from a statistics record (or unknown)."""
    if record is None:
        return {"value": None, "reason": "statistics unavailable", "source": None,
                "asOf": None, "stale": True}
    points = sum(table[s] * float(v) for s, v in (record.get("stats") or {}).items()
                 if s in table)
    as_of = record.get("asOf")
    stale = as_of is None or (_parse(now()) - _parse(as_of)).total_seconds() >= STALE_AFTER
    return {"value": round(points, 2), "reason": None, "source": record.get("source"),
            "asOf": as_of, "stale": stale}


def _fingerprint(lineup):
    """Digest of the lineup content the rows derive from (starters + basis inputs)."""
    if not lineup:
        return ""
    content = {"source": lineup.get("source"), "starters": lineup.get("starters") or [],
               "scoring": lineup.get("scoring")}
    return hashlib.sha256(json.dumps(content, sort_keys=True, default=str).encode()).hexdigest()


def _stored(profile_id, team_league):
    """(games, counter or None when no row exists, projected lineup fingerprint)."""
    row = store.get_panel(profile_id, team_league)
    if row is None:
        return {}, None, ""
    freshness = row.get("freshness") or {}
    return (freshness.get("games") or {}, int(freshness.get("counter", 0)),
            freshness.get("lineup") or "")


def project(game_event, matches):
    """Store the event's game facts for each matched profile; never writes Alerts."""
    facts = {"eventId": game_event["eventId"], "revision": int(game_event.get("revision", 1)),
             "score": {k: (Decimal(str(v)) if isinstance(v, float) else v)
                       for k, v in (game_event.get("score") or {}).items()},
             "source": game_event.get("source"), "eventTime": game_event.get("eventTime")}
    for match in matches:
        profile_id = match["profileId"]
        _, settings = _settings(profile_id)
        lineup = store.get_lineup(profile_id)
        _basis(lineup, settings)  # refuse an unknown preset before storing anything
        if not lineup:
            continue
        team_league = _pair(lineup)
        fingerprint = _fingerprint(lineup)
        # Conditional write on the counter we read: a lost race re-reads and
        # re-decides against the winner's games instead of erasing them.
        for _attempt in range(3):
            games, counter, _projected = _stored(profile_id, team_league)
            current = games.get(game_event["gameId"])
            replace = (current is None
                       or (current["eventId"] == facts["eventId"]
                           and facts["revision"] > int(current["revision"]))
                       or (current["eventId"] != facts["eventId"]
                           and str(facts["eventTime"] or "") > str(current.get("eventTime") or "")))
            if not replace:
                break
            panel = {"profileId": profile_id, "teamLeague": team_league,
                     "freshness": {"games": dict(games, **{game_event["gameId"]: facts}),
                                   "counter": (counter or 0) + 1, "lineup": fingerprint},
                     "updatedAt": now()}
            if store.put_panel_conditional(panel, counter):
                break
        else:
            raise RuntimeError(f"panel projection for {profile_id} kept losing races")


def snapshot(profile_id, team_league):
    """GET /v1/panel body: enveloped PanelState with scoring basis."""
    profile, settings = _settings(profile_id)
    lineup = store.get_lineup(profile_id)
    if team_league is None:
        selected = settings.get("teamLeague") or {}
        team_league = (f"{selected['league']}/{selected['team']}"
                       if selected.get("league") and selected.get("team")
                       else _pair(lineup) if lineup else "unassigned/unassigned")
    basis, table = _basis(lineup, settings)
    games, counter, projected = _stored(profile_id, team_league)
    rows, states = [], []
    if lineup and _pair(lineup) == team_league:
        for starter in lineup.get("starters") or []:
            espn_id = _espn_id(starter)
            record = player_statistics(espn_id) if espn_id else None
            value = _value(record, table)
            if espn_id is None:
                value = dict(value, reason="no matching ESPN athlete")
            rows.append({"playerId": espn_id or str(starter.get("player_key") or ""),
                         "name": starter.get("name") or "", "points": value,
                         "gameStatus": record.get("gameStatus") if record else None})
            states.append(record.get("gameState") if record else None)
    known = [r["points"] for r in rows if r["points"]["value"] is not None]
    if rows and len(known) == len(rows):
        dated = [p for p in known if p["asOf"]]
        oldest = min(dated, key=lambda p: p["asOf"]) if dated else None
        total = {"value": round(sum(p["value"] for p in known), 2), "reason": None,
                 "source": oldest["source"] if oldest else None,
                 "asOf": oldest["asOf"] if oldest else None,
                 "stale": any(p["stale"] for p in known)}
    else:
        dated = [p for p in known if p["asOf"]]
        oldest = min(dated, key=lambda p: p["asOf"]) if dated else None
        total = {"value": None,
                 "reason": "team total unavailable" if rows else "no lineup for this team/league",
                 "source": oldest["source"] if oldest else None,
                 "asOf": oldest["asOf"] if oldest else None,
                 "stale": not dated or any(p["stale"] for p in known)}
    scored = [{"pre": 0.0, "in": 0.5, "post": 1.0}[s] for s in states if s in ("pre", "in", "post")]
    if scored and len(scored) == len(rows):
        dated = [r["points"] for r in rows if r["points"]["asOf"]]
        oldest = min(dated, key=lambda p: p["asOf"]) if dated else None
        progress = {"value": round(sum(scored) / len(scored), 4), "reason": None,
                    "source": oldest["source"] if oldest else None,
                    "asOf": oldest["asOf"] if oldest else None,
                    "stale": not dated or any(r["points"]["stale"] for r in rows)}
    else:
        progress = {"value": None, "reason": "game progress unavailable", "source": None,
                    "asOf": None, "stale": True}
    # shortcut: the low bit only distinguishes "lineup as projected" from
    # "lineup changed since", so a second change (or a change back) before the
    # next projection reuses a revision; a stored lineup revision would fix
    # that, but the read path cannot write one. The x2 keeps every counter
    # or profile bump strictly above a spent low bit.
    current = _fingerprint(lineup) if lineup and _pair(lineup) == team_league else ""
    revision = 2 * ((counter or 0) + int(profile.get("revision", 0))) + (current != projected)
    return {"schemaVersion": 1, "id": f"panel/{profile_id}/{team_league}",
            "revision": revision,
            "source": lineup.get("source", "manual") if lineup else "manual",
            "updatedAt": now(),
            "data": {"teamLeague": team_league, "scoringBasis": basis,
                     "visible": bool((settings.get("panelPrefs") or {}).get("visible", True)),
                     "rows": rows, "teamTotal": total, "progress": progress,
                     "games": {gid: {"eventId": f["eventId"], "revision": f["revision"],
                                      "score": f["score"], "source": f["source"]}
                               for gid, f in games.items()}}}
