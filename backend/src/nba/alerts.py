"""Boxscore transitions as PlayerScore GameEvents (issue #137).

Compared with the previous stored record for the same athlete and game.
A different game, or no record, only establishes the baseline. Accepted
statistics versions identify transitions; retained milestones survive corrections.
"""

from decimal import Decimal

from nba.scoring import NBA_POINTS_TABLE, score

_MARKS = (10, 20, 30)
_DOUBLE = ("points", "rebounds", "assists", "steals", "blocks")
_SWING = 5


def _stat(stats, key):
    if not isinstance(stats, dict):
        return Decimal(0)
    try:
        return Decimal(str(stats.get(key, 0)))
    except (ArithmeticError, ValueError):
        return Decimal(0)


def _fantasy(stats):
    kept = {key: value for key, value in (stats or {}).items() if key in NBA_POINTS_TABLE}
    return score(kept)


def _format_delta(delta):
    text = f"{delta:.1f}"
    return text[:-2] if text.endswith(".0") else text


def transitions(previous, record):
    """(event-id code, factual phrase) for lines this boxscore newly crosses."""
    same = isinstance(previous, dict) and previous.get("gameId") == record.get("gameId")
    if not same:
        return []
    before = previous.get("stats")
    after = record.get("stats") or {}
    found = []
    for mark in _MARKS:
        if _stat(before, "points") < mark <= _stat(after, "points"):
            found.append((f"{mark:02d}", f"reaches {mark} pts"))
    before_lines = sum(_stat(before, key) >= 10 for key in _DOUBLE)
    after_lines = sum(_stat(after, key) >= 10 for key in _DOUBLE)
    if before_lines < 2 <= after_lines:
        found.append(("40", "reaches a double-double"))
    # round: score() is binary float; a true 5.0 must not fall short.
    delta = round(_fantasy(after) - _fantasy(before), 4)
    if delta >= _SWING:
        found.append(("05", f"+{_format_delta(delta)} fantasy pts"))
    return found


def milestones(record):
    """Reached milestones, also consumed by a game's initial observation."""
    stats = record.get("stats") or {}
    found = {f"{mark:02d}" for mark in _MARKS if _stat(stats, "points") >= mark}
    if sum(_stat(stats, key) >= 10 for key in _DOUBLE) >= 2:
        found.add("40")
    return found


def game_events(record, previous, *, version, channel=None):
    """Stored GameEvent shape, sport nba, one event per crossed line."""
    game_id = str(record.get("gameId") or "")
    athlete_id = str(record.get("athleteId") or "")
    if not game_id.isdigit() or not athlete_id.isdigit():
        return []
    when = record.get("asOf")
    if not isinstance(when, str) or not when:
        return []
    source = record.get("source") if record.get("source") in ("live", "replay") else "live"
    seen = set(previous.get("nbaMilestones", [])) | milestones(previous) if (
        previous and previous.get("gameId") == game_id) else set()
    events = []
    for code, phrase in transitions(previous, record):
        if code in seen:
            continue
        # Version first keeps later transitions after earlier cursors at the same clock.
        event = {"gameId": game_id, "eventId": f"{game_id}{version:08d}{athlete_id}{code}",
                 "revision": 1, "correctionOf": None, "source": source,
                 "playerIds": [athlete_id], "eventTime": when, "scoringPlay": True,
                 "sport": "nba", "matchup": phrase}
        if isinstance(channel, str) and channel:
            event["channel"] = channel
        events.append(event)
    return events
