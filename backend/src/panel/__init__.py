"""DES-AFC-P2-PANELSVC PanelState per profile and team/league (P2-B07).

project() persists only the projected game facts per profile (in the Panels
row `freshness` map, the one free-form PanelState attribute): a later
revision of the same event replaces them, an equal or lower revision never
does, so the panel agrees with the alert record. snapshot() derives rows,
points, total and progress at read time from the stored Lineup, the profile
Settings and the statistics seam, so a settings or starter change shows on
the next read with a higher revision and no panel write on the read path.
project() records a fingerprint of the lineup it projected; snapshot()
spends a low revision field when the current lineup differs from that
fingerprint, so a starter change outruns the last projected revision,
and another low field counts finals expired at read time, so expiration
also outruns the revision a consumer already holds.
The revision also carries the store-allocated lineupVersion, which
advances on every lineup content change (including a change back and an
empty/removal row), so distinct content never reuses a revision and a
served revision never goes backwards for one profile/pair (every revision
input is read strongly consistent, so no lagging replica serves an older one).
Projections write conditionally on the stored counter and re-read and
merge on a lost race, so overlapping games never erase each other.

Seams, read at call time through this module: player_statistics(athlete_id)
-> None (unknown) or {gameId, gameState pre|in|post, gameStatus, source
live|replay, asOf, stats}; now() -> RFC 3339 UTC. Production statistics are
the per-athlete boxscore records feed_ingest stores at ingest.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import matcher
import store
from lineup import presets

STALE_AFTER = 60
FINAL_RECORD_WINDOW = 12 * 60 * 60  # a final record older than this is a previous game's
MAX_ROWS = 32  # frozen panel row bound the TV decoder enforces
_PRESETS = {"ppr": "PPR", "halfPpr": "Half-PPR"}


class InvalidLineupError(ValueError):
    """The stored lineup cannot produce a contract-valid panel (legacy rows)."""


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def player_statistics(athlete_id):
    record = store.get_player_statistics(str(athlete_id))
    if record is None:
        return None
    return {key: record.get(key)
            for key in ("gameId", "gameState", "gameStatus", "source", "asOf", "stats")}


def _parse(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def _pair(lineup):
    """Team/league key, or None when a stored row lacks either half."""
    if not lineup or not lineup.get("league") or not lineup.get("team"):
        return None
    return f"{lineup['league']}/{lineup['team']}"


def _settings(profile_id):
    profile = store.get_profile(profile_id) or {}
    return profile, profile.get("settings") or {}


def _nba_enabled():
    """AFC_ENABLE_NBA is the only switch; off is the shipped default."""
    return os.environ.get("AFC_ENABLE_NBA", "").lower() in ("1", "true", "yes")


def _nba_lineup(lineup):
    return bool(lineup) and lineup.get("sport") == "nba" and _nba_enabled()


def _sport_off(lineup, settings):
    """Flag on: this lineup's sport was set False, so snapshot serves no rows.

    The lineup sport defaults to nfl. A missing sports field or key stays on.
    Flag off ignores a stored sports value.
    """
    if not lineup or not _nba_enabled():
        return False
    sport = lineup.get("sport") or "nfl"
    sports = settings.get("sports")
    if type(sports) is not dict:
        return False
    return sports.get(sport) is False


def _nba_table():
    from nba.scoring import NBA_POINTS_TABLE

    return "nbaPoints", dict(NBA_POINTS_TABLE)


def _basis(lineup, settings):
    """(wire basis, scoring table); an unknown stored preset is refused.

    An NBA lineup (sport nba, flag on) uses its Yahoo league table when that
    table mapped, and nbaPoints for a manual lineup or a category league.
    NFL lineups keep the preset or yahooLeague path they had before.
    """
    if lineup and lineup.get("source") == "yahoo":
        modifiers = (lineup.get("scoring") or {}).get("stat_modifiers") or {}
        if modifiers or not _nba_lineup(lineup):
            return "yahooLeague", {k: float(v) for k, v in modifiers.items()}
        return _nba_table()
    if _nba_lineup(lineup):
        return _nba_table()
    preset = settings.get("scoringPreset") or "halfPpr"
    if preset == "nbaPoints" and _nba_enabled():
        return _nba_table()
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


def _age_seconds(as_of):
    """Seconds since an asOf stamp, or None when it is missing, unparseable
    or timezone-naive, so a malformed date never reaches an uncaught parser."""
    if not isinstance(as_of, str):
        return None
    try:
        parsed = _parse(as_of)
    except ValueError:
        return None
    if parsed.utcoffset() is None:
        return None
    return (_parse(now()) - parsed).total_seconds()


def _value(record, table):
    """One points value object from a statistics record (or unknown)."""
    if record is None:
        return {"value": None, "reason": "statistics unavailable", "source": None,
                "asOf": None, "stale": True}
    points = sum(table[s] * float(v) for s, v in (record.get("stats") or {}).items()
                 if s in table)
    as_of = record.get("asOf")
    age = _age_seconds(as_of)
    stale = age is None or age >= STALE_AFTER
    return {"value": round(points, 2), "reason": None, "source": record.get("source"),
            "asOf": as_of, "stale": stale}


def _stale_final(record):
    """A final record older than the window belongs to a previous game (#94):
    no schedule source names the starter's next game before an event does.
    A final with no usable asOf cannot be shown to be current: fail closed."""
    if record.get("gameState") != "post" and not str(record.get("gameStatus") or "").startswith("Final"):
        return False
    age = _age_seconds(record.get("asOf"))
    return age is None or age > FINAL_RECORD_WINDOW


def _oldest(points):
    """(source, asOf) of the oldest contributor; unknown if any is undated,
    so a mixed dated/undated aggregate can never look fresh."""
    if not points or any(p["asOf"] is None for p in points):
        return None, None
    oldest = min(points, key=lambda p: p["asOf"])
    return oldest["source"], oldest["asOf"]


def _fingerprint(lineup):
    """Digest of the lineup content the rows derive from (starters + basis inputs)."""
    if not lineup:
        return ""
    content = {"source": lineup.get("source"), "starters": lineup.get("starters") or [],
               "scoring": lineup.get("scoring")}
    # Absent on every NFL lineup, so those fingerprints stay what they were.
    if lineup.get("sport") is not None:
        content["sport"] = lineup.get("sport")
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
             "source": game_event.get("source"), "eventTime": game_event.get("eventTime"),
             # Internal only (never in the wire games map): which starters this
             # game concerns, so snapshot can tell a starter's current game.
             "playerIds": [str(p) for p in game_event.get("playerIds") or []]}
    for match in matches:
        profile_id = match["profileId"]
        _, settings = _settings(profile_id)
        lineup = store.get_lineup(profile_id)
        _basis(lineup, settings)  # refuse an unknown preset before storing anything
        if not lineup:
            continue
        team_league = _pair(lineup)
        if not team_league:
            continue  # no pair, no panel key
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
            if current is not None:  # a starter stays linked to the game all game long
                facts = dict(facts, playerIds=sorted(
                    set(facts["playerIds"]) | {str(p) for p in current.get("playerIds") or []}))
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
    lineup, lineup_version = store.get_lineup_with_version(profile_id)
    if team_league is None:
        selected = settings.get("teamLeague") or {}
        team_league = (f"{selected['league']}/{selected['team']}"
                       if selected.get("league") and selected.get("team")
                       else _pair(lineup) or "unassigned/unassigned")
    basis, table = _basis(lineup, settings)
    games, counter, projected = _stored(profile_id, team_league)
    rows, states, source_ids = [], [], []
    expired_finals = 0
    if lineup and _pair(lineup) == team_league:
        if len(lineup.get("starters") or []) > MAX_ROWS:
            raise InvalidLineupError(
                "stored lineup violates the panel row contract (count, blank or duplicate id)")
        source_key = "player_key" if lineup.get("source") == "yahoo" else "athlete_id"
        for starter in lineup.get("starters") or []:
            raw_id = starter.get(source_key) if isinstance(starter, dict) else None
            if not isinstance(raw_id, str) or not raw_id.strip():
                raise InvalidLineupError(
                    "stored lineup violates the panel row contract (count, blank or duplicate id)")
            source_ids.append(raw_id)
            espn_id = _espn_id(starter)
            record = player_statistics(espn_id) if espn_id else None
            # The starter's current game is the latest projected game whose
            # events concern them (Panels games map). A statistics record
            # from an earlier game is not this game's points: fail closed.
            # Rows projected before playerIds were stored carry no link, so
            # they impose no current game and the record stands as before.
            mine = [gid for gid, f in games.items()
                    if espn_id and espn_id in {str(p) for p in f.get("playerIds") or []}]
            current_game = (max(mine, key=lambda gid: (str(games[gid].get("eventTime") or ""), gid))
                            if mine else None)
            wrong_game = bool(record and current_game
                              and record.get("gameId") != current_game)
            if record and not wrong_game and _stale_final(record):
                wrong_game = True
                expired_finals += 1
            value = _value(None if wrong_game else record, table)
            if wrong_game:
                record, value = None, dict(value, reason="no statistics for current game")
            if espn_id is None:
                value = dict(value, reason="no matching ESPN athlete")
            rows.append({"playerId": espn_id or str(starter.get("player_key") or ""),
                         "name": starter.get("name") or "", "points": value,
                         "gameStatus": record.get("gameStatus") if record else None})
            states.append(record.get("gameState") if record else None)
    ids = [row["playerId"] for row in rows]
    if (len(rows) > MAX_ROWS or len(set(source_ids)) != len(source_ids)
            or any(not player_id.strip() for player_id in ids)
            or len(set(ids)) != len(ids)):
        raise InvalidLineupError(
            "stored lineup violates the panel row contract (count, blank or duplicate id)")
    # Hide after the row contract check so a bad lineup still fails closed.
    # Empty rows make the team total unknown; the profile revision still rises.
    if _sport_off(lineup, settings):
        rows, states = [], []
    known = [r["points"] for r in rows if r["points"]["value"] is not None]
    if rows and len(known) == len(rows):
        source, as_of = _oldest(known)
        total = {"value": round(sum(p["value"] for p in known), 2), "reason": None,
                 "source": source, "asOf": as_of,
                 "stale": any(p["stale"] for p in known)}
    else:
        source, as_of = _oldest(known)
        total = {"value": None,
                 "reason": "team total unavailable" if rows else "no lineup for this team/league",
                 "source": source, "asOf": as_of,
                 "stale": not known or any(p["stale"] for p in known)}
    scored = [{"pre": 0.0, "in": 0.5, "post": 1.0}[s] for s in states if s in ("pre", "in", "post")]
    if scored and len(scored) == len(rows):
        source, as_of = _oldest([r["points"] for r in rows])
        progress = {"value": round(sum(scored) / len(scored), 4), "reason": None,
                    "source": source, "asOf": as_of,
                    "stale": any(r["points"]["stale"] for r in rows)}
    else:
        progress = {"value": None, "reason": "game progress unavailable", "source": None,
                    "asOf": None, "stale": True}
    # lineupVersion (allocated by store.put_lineup at the write boundary)
    # makes every lineup content change strictly advance this sum, so the
    # low fields can never reuse or regress a revision. The x128 keeps
    # every bump strictly above the fingerprint field (64) plus the
    # expired-final count (at most MAX_ROWS), so read-time expiration
    # advances the revision the TV consumes and stable rereads do not.
    current = _fingerprint(lineup) if lineup and _pair(lineup) == team_league else ""
    revision = (128 * ((counter or 0) + int(profile.get("revision", 0))
                       + lineup_version)
                + 64 * (current != projected) + expired_finals)
    data = {"teamLeague": team_league, "scoringBasis": basis,
            "visible": bool((settings.get("panelPrefs") or {}).get("visible", True)),
            "rows": rows, "teamTotal": total, "progress": progress,
            "games": {gid: {"eventId": f["eventId"], "revision": f["revision"],
                             "score": f["score"], "source": f["source"]}
                      for gid, f in games.items()}}
    if _nba_lineup(lineup):
        data["sport"] = "nba"
    return {"schemaVersion": 1, "id": f"panel/{profile_id}/{team_league}",
            "revision": revision,
            "source": lineup.get("source", "manual") if lineup else "manual",
            "updatedAt": now(),
            "data": data}
