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
The same high term adds each row's store-allocated statistics content version,
so corrections advance even when the source timestamp is unchanged or missing.
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
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import matcher
import store
from lineup import presets

STALE_AFTER = 60
FINAL_RECORD_WINDOW = 12 * 60 * 60  # a final record older than this is a previous game's
MAX_ROWS = 32  # frozen panel row bound the TV decoder enforces
MAX_PROJECTION_COUNTER = (1 << 24) - 1
LINEUP_REVISION_SCALE = (
    MAX_ROWS * store.MAX_STATS_VERSION
    + 2 * store.MAX_PREGAME_SEQUENCE + 1
    + MAX_PROJECTION_COUNTER + 1
)
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
            for key in ("gameId", "gameState", "gameStatus", "source", "asOf", "stats", "statsVersion")}


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


def _nba_pregame(lineup):
    """Team game status text ({team: text}), its asOf, and the monotonic revision
    contribution, including expiry. NBA (flag on) and NFL lineups each read their sport's slate."""
    if not lineup:
        return {}, 0
    if _nba_lineup(lineup):
        item = store.get_nba_pregame()
    elif (lineup.get("sport") or "nfl") == "nfl":
        item = store.get_nba_pregame(store.NFL_STATUS_ID)
    else:
        return {}, 0
    if not item:
        return {}, 0
    age = _age_seconds(item.get("asOf"))
    expired = age is None or age > store.NBA_PREGAME_WINDOW
    pregame_seq = 2 * int(item.get("sequence", 0)) + int(expired)
    if expired:
        return {}, pregame_seq
    teams = item.get("teams")
    return (dict(teams, **{_SLATE_AS_OF: item.get("asOf")}) if isinstance(teams, dict) else {}), pregame_seq


_SLATE_AS_OF = "asOf"  # not a team abbreviation (those are upper case)
_NOT_LIVE = ("Tips ", "Kicks ", "Final")


def _pair_rank(lineup, slate):
    """0 when a starter's game is live, 1 when one is still to start, else 2."""
    texts = [slate.get(s.get("team")) for s in lineup.get("starters") or [] if isinstance(s, dict)]
    texts = [t for t in texts if isinstance(t, str) and t.strip()]
    if any(not t.startswith(_NOT_LIVE) for t in texts):
        return 0
    return 1 if any(t.startswith(_NOT_LIVE[:2]) for t in texts) else 2


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


def _nfl_week_start(now_at):
    """Start of the current NFL fantasy week: the latest Tuesday 09:00 UTC, after Monday night's game."""
    start = (now_at - timedelta(days=(now_at.weekday() - 1) % 7)).replace(hour=9, minute=0, second=0, microsecond=0)
    return start if start <= now_at else start - timedelta(days=7)


def _stale_final(record, weekly=False):
    """A final record older than the window belongs to a previous game (#94):
    no schedule source names the starter's next game before an event does.
    Owner 2026-10-23: NFL fantasy points last the fantasy week (Thursday to Monday
    night), so an NFL final stays current until the week rolls over on Tuesday.
    A final with no usable asOf cannot be shown to be current: fail closed."""
    if record.get("gameState") != "post" and not str(record.get("gameStatus") or "").startswith("Final"):
        return False
    age = _age_seconds(record.get("asOf"))
    if age is None:
        return True
    if weekly:
        return _parse(record["asOf"]) < _nfl_week_start(_parse(now()))
    return age > FINAL_RECORD_WINDOW


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
    event_sport = game_event.get("sport") or "nfl"
    for match in matches:
        profile_id = match["profileId"]
        _, settings = _settings(profile_id)
        lineups, _version = store.get_lineups(profile_id)
        targets = []
        for team_league, entry in lineups.items():
            if not team_league:
                continue  # no pair, no panel key
            lineup = dict(entry, profileId=profile_id)
            if (lineup.get("sport") or "nfl") != event_sport:
                continue
            _basis(lineup, settings)  # refuse an unknown preset before storing anything
            targets.append((team_league, _fingerprint(lineup)))
        for team_league, fingerprint in targets:
            # Conditional write on the counter we read: a lost race re-reads and
            # re-decides against the winner's games instead of erasing them.
            pair_facts = dict(facts)
            for _attempt in range(3):
                games, counter, _projected = _stored(profile_id, team_league)
                current = games.get(game_event["gameId"])
                replace = (current is None
                           or (current["eventId"] == pair_facts["eventId"]
                               and pair_facts["revision"] > int(current["revision"]))
                           or (current["eventId"] != pair_facts["eventId"]
                               and str(pair_facts["eventTime"] or "") > str(current.get("eventTime") or "")))
                if not replace:
                    break
                if current is not None:  # a starter stays linked to the game all game long
                    pair_facts = dict(pair_facts, playerIds=sorted(
                        set(pair_facts["playerIds"]) | {str(p) for p in current.get("playerIds") or []}))
                if (counter or 0) >= MAX_PROJECTION_COUNTER:
                    raise RuntimeError("panel projection counter exhausted")
                panel = {"profileId": profile_id, "teamLeague": team_league,
                         "freshness": {"games": dict(games, **{game_event["gameId"]: pair_facts}),
                                       "counter": (counter or 0) + 1, "lineup": fingerprint},
                         "updatedAt": now()}
                if store.put_panel_conditional(panel, counter):
                    break
            else:
                raise RuntimeError(f"panel projection for {profile_id} kept losing races")


def _ordered_pairs(lineups, profile_id):
    """Pairs for the remote's cycle: live games first, then upcoming, then the rest."""
    slates = {}
    ranked = []
    for key, entry in lineups.items():
        if not key:
            continue
        lineup = dict(entry, profileId=profile_id)
        sport = "nba" if _nba_lineup(lineup) else (lineup.get("sport") or "nfl")
        if sport not in slates:
            slates[sport] = _nba_pregame(lineup)[0]
        ranked.append((_pair_rank(lineup, slates[sport]), key))
    return [key for _, key in sorted(ranked)]


def snapshot(profile_id, team_league):
    """GET /v1/panel body: enveloped PanelState with scoring basis."""
    profile, settings = _settings(profile_id)
    lineups, lineup_version = store.get_lineups(profile_id)
    if team_league is None:
        selected = settings.get("teamLeague") or {}
        real = [key for key in lineups if key]
        if selected.get("league") and selected.get("team"):
            team_league = f"{selected['league']}/{selected['team']}"
        elif len(real) == 1:
            team_league = real[0]
        else:
            team_league = "unassigned/unassigned"
    # Preserve sole-lineup metadata for empty selections; rows still require a matching pair.
    entry = lineups.get(team_league) or store._sole_entry(lineups)
    lineup = dict(entry, profileId=profile_id) if entry else None
    basis, table = _basis(lineup, settings)
    games, counter, projected = _stored(profile_id, team_league)
    rows, states, source_ids = [], [], []
    expired_finals = 0
    stats_version_sum = 0
    pregame, pregame_seq = (_nba_pregame(lineup) if lineup and _pair(lineup) == team_league
                            else ({}, 0))
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
            if record is not None:
                stats_version_sum += int(record.get("statsVersion") or 0)
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
            if record and not wrong_game and _stale_final(record, weekly=not _nba_lineup(lineup)):
                wrong_game = True
                expired_finals += 1
            value = _value(None if wrong_game else record, table)
            if wrong_game:
                record, value = None, dict(value, reason="no statistics for current game")
            status = record.get("gameStatus") if record else None
            if record is None:
                # No stats for the team's game today: 0.0 with that game's status.
                text = pregame.get(starter.get("team"))
                if isinstance(text, str) and text.strip():
                    status = text
                    if espn_id is not None:
                        age = _age_seconds(pregame.get(_SLATE_AS_OF))
                        value = {"value": 0.0, "reason": None, "source": None,
                                 "asOf": pregame.get(_SLATE_AS_OF),
                                 "stale": age is None or age >= STALE_AFTER}
                elif (not _nba_lineup(lineup) and starter.get("team")
                      and any(key != _SLATE_AS_OF for key in pregame)):
                    # Owner 2026-10-23: an NFL team missing from the week's slate is on bye.
                    status = "BYE"
                    if espn_id is not None:
                        age = _age_seconds(pregame.get(_SLATE_AS_OF))
                        value = {"value": 0.0, "reason": None, "source": None,
                                 "asOf": pregame.get(_SLATE_AS_OF),
                                 "stale": age is None or age >= STALE_AFTER}
            if espn_id is None:
                value = dict(value, reason="no matching ESPN athlete")
            rows.append({"playerId": espn_id or str(starter.get("player_key") or ""),
                         "name": starter.get("name") or "", "points": value,
                         "gameStatus": status,
                         # Lineup position (QB, FLEX, UTIL); null for a legacy row without one.
                         "slot": starter.get("slot") if isinstance(starter.get("slot"), str) else None})
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
    # The total sums what is known; one player without a value never hides it.
    if known:
        source, as_of = _oldest(known)
        # A sum that leaves out a player says so; the TV shows the number either way.
        total = {"value": round(sum(p["value"] for p in known), 2),
                 "reason": None if len(known) == len(rows) else "partial total",
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
    # A profile or lineup step outruns losing all stats, pregame (2*seq + expiry),
    # and the selected pair's counter. Keep raw stats versions through filtering.
    # The +1 generation beats the deployed formula even for legacy lineup v0;
    # x128 outruns all 96 low-field units. With lineupVersion + profile revision
    # <=100,000 and bounded inputs, revision <=7,516,267,507,523,552 < 2^53.
    # shortcut: migrate before 2^24-1 per-record/pair writes or 100,000 combined
    # lineup/profile changes; exhausted counters preserve their last stored row.
    current = _fingerprint(lineup) if lineup and _pair(lineup) == team_league else ""
    revision = (128 * (1 + (counter or 0)
                       + (int(profile.get("revision", 0)) + lineup_version) * LINEUP_REVISION_SCALE
                       + stats_version_sum + pregame_seq)
                + 64 * (current != projected) + expired_finals)
    data = {"teamLeague": team_league, "scoringBasis": basis,
            "visible": bool((settings.get("panelPrefs") or {}).get("visible", True)),
            "rows": rows, "teamTotal": total, "progress": progress,
            "games": {gid: {"eventId": f["eventId"], "revision": f["revision"],
                             "score": f["score"], "source": f["source"]}
                      for gid, f in games.items()},
            "teamLeagues": _ordered_pairs(lineups, profile_id)}
    if _nba_lineup(lineup):
        data["sport"] = "nba"
    return {"schemaVersion": 1, "id": f"panel/{profile_id}/{team_league}",
            "revision": revision,
            "source": lineup.get("source", "manual") if lineup else "manual",
            "updatedAt": now(),
            "data": data}
