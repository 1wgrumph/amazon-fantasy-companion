"""ESPN summary plays to GameEvents in the store.put_event shape (AFC-PR-012)."""

from decimal import Decimal, InvalidOperation

# ESPN boxscore (category, key) -> CONTRACT-AFC-P2-PRESETS stat name. The
# defensive "interceptions" category is deliberately absent: only a passer's
# interceptions score as interceptions_thrown.
_BOX = {
    ("passing", "passingYards"): "passing_yards",
    ("passing", "passingTouchdowns"): "passing_touchdowns",
    ("passing", "interceptions"): "interceptions_thrown",
    ("rushing", "rushingYards"): "rushing_yards",
    ("rushing", "rushingTouchdowns"): "rushing_touchdowns",
    ("receiving", "receptions"): "receptions",
    ("receiving", "receivingYards"): "receiving_yards",
    ("receiving", "receivingTouchdowns"): "receiving_touchdowns",
    ("fumbles", "fumblesLost"): "fumbles_lost",
}


def _sources():
    return ("live", "replay")


def _plays(payload):
    return [play for drive in payload["drives"]["previous"] for play in drive.get("plays", [])]


def _athletes(payload):
    return {entry["athlete"]["id"]
            for team in payload.get("boxscore", {}).get("players", [])
            for stat in team.get("statistics", [])
            for entry in stat.get("athletes", [])}


def _offense(play):
    return next((team["id"] for team in play.get("teamParticipants", [])
                 if team.get("type") == "offense"), None)


def _facts(play, known, source):
    # Participants are usually $ref links; only inline ids naming a boxscore athlete count.
    players = [entry["athlete"]["id"] for entry in play.get("participants", [])
               if entry.get("athlete", {}).get("id") in known]
    return {"source": source, "score": {"away": play["awayScore"], "home": play["homeScore"]},
            "fieldPosition": play["start"]["yardsToEndzone"], "possession": _offense(play),
            "playerIds": players, "eventTime": play.get("wallclock"),
            "period": play["period"]["number"], "scoringPlay": play["scoringPlay"]}


def normalize_summary(payload, game_id, source="live", prior=None):
    """New or changed plays of a validated summary as GameEvents.

    `prior` maps eventId to the stored event: an unchanged play emits nothing and a
    changed play emits the next revision with correctionOf naming the superseded one.
    """
    if source not in _sources():
        raise ValueError(f"Feed events must be labeled live or replay, not {source!r}")
    prior = prior or {}
    known = _athletes(payload)
    events = []
    for play in _plays(payload):
        facts = _facts(play, known, source)
        before = prior.get(play["id"])
        if before is None:
            revision, correction_of = 1, None
        elif any(key in before and before[key] != value for key, value in facts.items()):
            correction_of = int(before["revision"])
            revision = correction_of + 1
        else:
            continue
        events.append({"gameId": game_id, "eventId": play["id"], "revision": revision,
                       "correctionOf": correction_of, **facts})
    return events


def boxscore_statistics(payload, game_id, source="live"):
    """Per-athlete preset statistics from a validated summary's boxscore.

    One record per athlete with at least one mapped stat, in the panel
    player_statistics seam shape plus athleteId. Values are Decimal (never
    float) for DynamoDB; asOf is the latest play wallclock in the summary.
    """
    if source not in _sources():
        raise ValueError(f"Feed events must be labeled live or replay, not {source!r}")
    try:
        status = payload["header"]["competitions"][0]["status"]["type"]
    except (KeyError, IndexError, TypeError):
        return []
    state = status.get("state") if isinstance(status, dict) else None
    if state not in ("pre", "in", "post"):
        return []
    detail = status.get("shortDetail") or status.get("detail")
    clocks = [play.get("wallclock") for play in _plays(payload)]
    clocks = [clock for clock in clocks if isinstance(clock, str)]
    by_athlete = {}
    for team in payload.get("boxscore", {}).get("players", []) or []:
        if not isinstance(team, dict):
            continue
        for category in team.get("statistics", []) or []:
            if not isinstance(category, dict):
                continue
            name, keys = category.get("name"), category.get("keys")
            if not isinstance(name, str) or not isinstance(keys, list):
                continue
            for entry in category.get("athletes", []) or []:
                if not isinstance(entry, dict) or not isinstance(entry.get("stats"), list):
                    continue
                athlete_id = (entry.get("athlete") or {}).get("id")
                if not isinstance(athlete_id, str):
                    continue
                stats = by_athlete.setdefault(athlete_id, {})
                for key, value in zip(keys, entry["stats"]):
                    if not isinstance(key, str):
                        continue
                    mapped = _BOX.get((name, key))
                    if mapped is None:
                        continue
                    try:
                        number = Decimal(str(value))
                    except (InvalidOperation, ArithmeticError, ValueError):
                        continue
                    # Untrusted body: DynamoDB rejects non-finite Decimals, and
                    # no real boxscore stat needs more than five digits.
                    if number.is_finite() and abs(number) <= 99999:
                        stats[mapped] = number
    return [{"athleteId": athlete_id, "gameId": game_id, "gameState": state,
             "gameStatus": detail if isinstance(detail, str) else None,
             "source": source, "asOf": max(clocks) if clocks else None, "stats": stats}
            for athlete_id, stats in by_athlete.items() if stats]


def broadcast_networks(payload):
    """Network short names from header.competitions[0].broadcasts (X05-OBS-001)."""
    competition = payload["header"]["competitions"][0]
    return [entry["media"]["shortName"] for entry in competition.get("broadcasts", [])]
