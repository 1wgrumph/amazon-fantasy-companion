"""ESPN summary plays to GameEvents in the store.put_event shape (AFC-PR-012)."""

from decimal import Decimal, InvalidOperation
import logging
import re

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


_SUFFIXES = {"Jr.", "Jr", "Sr.", "Sr", "II", "III", "IV", "V"}
# ESPN play text: "D.Swift", "J.Hines-Allen", "C.Rodriguez Jr."
_PLAY_NAME = re.compile(
    r"(?<![A-Za-z])([A-Z]\.[A-Za-z]+(?:-[A-Za-z]+)?)(?: Jr\.)?(?![A-Za-z])")


def _abbrev(display_name):
    # shortcut: a multi-word last name keeps its final token, upgrade for "A.St. Brown"
    if not isinstance(display_name, str):
        return None
    parts = display_name.split()
    if len(parts) < 2 or not parts[0][:1].isalpha():
        return None
    if parts[-1] in _SUFFIXES and len(parts) > 2:
        parts = parts[:-1]
    return f"{parts[0][0].upper()}.{parts[-1]}"


def _athletes(payload):
    known, owners = set(), {}
    for team in payload.get("boxscore", {}).get("players", []):
        for stat in team.get("statistics", []):
            for entry in stat.get("athletes", []):
                athlete = entry["athlete"]
                athlete_id = athlete["id"]
                known.add(athlete_id)
                abbrev = _abbrev(athlete.get("displayName"))
                if abbrev:
                    owners.setdefault(abbrev, set()).add(athlete_id)
    # shortcut: two athletes sharing F.Last are skipped, upgrade when the play names the team
    names = {abbrev: next(iter(ids)) for abbrev, ids in owners.items() if len(ids) == 1}
    return known, names


def _ids_from_text(text, names, known):
    if not isinstance(text, str) or not names:
        return []
    found = []
    for match in _PLAY_NAME.finditer(text):
        athlete_id = names.get(match.group(1))
        if athlete_id in known and athlete_id not in found:
            found.append(athlete_id)
    return found


MAX_MATCHUP_LENGTH = 80  # the TV alert context bound


def _matchup(payload):
    """Sourced "AWY at HOM" label from header competitors, or None; never fabricated."""
    try:
        competitors = payload["header"]["competitions"][0]["competitors"]
    except (KeyError, IndexError, TypeError):
        return None
    if not isinstance(competitors, list):
        return None
    sides = {}
    for competitor in competitors:
        if not isinstance(competitor, dict):
            return None
        team = competitor.get("team") or {}
        abbreviation = team.get("abbreviation") if isinstance(team, dict) else None
        side = competitor.get("homeAway")
        if (side not in ("away", "home") or side in sides
                or not isinstance(abbreviation, str)
                or not re.fullmatch(r"[A-Z0-9]{1,8}", abbreviation)):
            return None
        sides[side] = abbreviation
    if set(sides) != {"away", "home"}:
        return None
    label = f"{sides['away']} at {sides['home']}"
    return label if len(label) <= MAX_MATCHUP_LENGTH else None


MAX_CHANNEL_LENGTH = 32
_CHANNEL = re.compile(
    rf"[A-Za-z0-9](?:[A-Za-z0-9 .&'+/-]{{0,{MAX_CHANNEL_LENGTH - 2}}}[A-Za-z0-9+])?")


def _channel(payload):
    """First valid broadcast media.shortName in ESPN's listed order, or None.

    Display-only: a malformed or oversize entry is skipped, never rejecting the game.
    """
    try:
        entries = payload["header"]["competitions"][0].get("broadcasts")
    except (KeyError, IndexError, TypeError, AttributeError):
        return None
    for entry in entries if isinstance(entries, list) else []:
        media = entry.get("media") if isinstance(entry, dict) else None
        name = media.get("shortName") if isinstance(media, dict) else None
        if isinstance(name, str) and _CHANNEL.fullmatch(name):
            return name
    return None


def _offense(play):
    return next((team["id"] for team in play.get("teamParticipants", [])
                 if team.get("type") == "offense"), None)


def _facts(play, known, names, source):
    # Inline ids win. ESPN live often sends participants null and names the players in text.
    participants = play.get("participants") or []
    players = [entry["athlete"]["id"] for entry in participants
               if isinstance(entry, dict) and (entry.get("athlete") or {}).get("id") in known]
    if not players:
        players = _ids_from_text(play.get("text"), names, known)
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
    known, names = _athletes(payload)
    matchup = _matchup(payload)
    channel = _channel(payload)
    events = []
    for play in _plays(payload):
        facts = _facts(play, known, names, source)
        before = prior.get(play["id"])
        if before is None:
            revision, correction_of = 1, None
        elif any(key in before and before[key] != value for key, value in facts.items()):
            correction_of = int(before["revision"])
            revision = correction_of + 1
        else:
            continue
        event = {"gameId": game_id, "eventId": play["id"], "revision": revision,
                 "correctionOf": correction_of, **facts}
        if matchup is not None:
            event["matchup"] = matchup
        if channel is not None:
            event["channel"] = channel
        events.append(event)
    return events


MAX_ATHLETE_ID_LENGTH = 20
MAX_BOXSCORE_ATHLETES = 200
MAX_ATHLETE_STATS = 64
MAX_STAT_VALUE_LENGTH = 16
MAX_LOGGED_VALUE_LENGTH = 40


def _valid_athlete_id(athlete_id):
    return (isinstance(athlete_id, str)
            and bool(re.fullmatch(rf"[0-9]{{1,{MAX_ATHLETE_ID_LENGTH}}}", athlete_id)))


def _sample(value):
    """A log-safe, length-bounded repr of an untrusted value."""
    text = value[:MAX_LOGGED_VALUE_LENGTH] if isinstance(value, str) else value
    return repr(text)[:MAX_LOGGED_VALUE_LENGTH]


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
        plays = _plays(payload)
    except (KeyError, IndexError, TypeError):
        return []
    state = status.get("state") if isinstance(status, dict) else None
    if state not in ("pre", "in", "post"):
        return []
    detail = status.get("shortDetail") or status.get("detail")
    clocks = [play.get("wallclock") for play in plays if isinstance(play, dict)]
    clocks = [clock for clock in clocks if isinstance(clock, str) and clock]
    max_athletes, max_stats = MAX_BOXSCORE_ATHLETES, MAX_ATHLETE_STATS
    max_value_len = MAX_STAT_VALUE_LENGTH
    boxscore = payload.get("boxscore")
    players = boxscore.get("players") if isinstance(boxscore, dict) else None
    by_athlete, stat_counts = {}, {}
    # One aggregated log line per payload: a hostile body must not amplify log volume.
    invalid_ids, excess_athletes, excess_stats, oversize, first_invalid = 0, 0, 0, 0, None
    for team in players if isinstance(players, list) else []:
        if not isinstance(team, dict):
            continue
        categories = team.get("statistics")
        for category in categories if isinstance(categories, list) else []:
            if not isinstance(category, dict):
                continue
            name, keys = category.get("name"), category.get("keys")
            if not isinstance(name, str) or not isinstance(keys, list):
                continue
            entries = category.get("athletes")
            for entry in entries if isinstance(entries, list) else []:
                if not isinstance(entry, dict) or not isinstance(entry.get("stats"), list):
                    continue
                athlete = entry.get("athlete")
                athlete_id = athlete.get("id") if isinstance(athlete, dict) else None
                if not _valid_athlete_id(athlete_id):
                    if not invalid_ids:
                        first_invalid = _sample(athlete_id)
                    invalid_ids += 1
                    continue
                if athlete_id not in by_athlete:
                    if len(by_athlete) >= max_athletes:
                        excess_athletes += 1
                        continue
                    by_athlete[athlete_id] = {}
                    stat_counts[athlete_id] = 0
                stats = by_athlete[athlete_id]
                raw_stats = entry["stats"]
                remaining = max_stats - stat_counts[athlete_id]
                if len(keys) > remaining or len(raw_stats) > remaining:
                    excess_stats += 1
                pairs = list(zip(keys[:remaining], raw_stats[:remaining]))
                stat_counts[athlete_id] += len(pairs)
                for key, value in pairs:
                    if not isinstance(key, str):
                        continue
                    mapped = _BOX.get((name, key))
                    if mapped is None:
                        continue
                    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
                        continue
                    if isinstance(value, int) and abs(value) > 99999:
                        continue
                    text = value if isinstance(value, str) else str(value)
                    if len(text) > max_value_len:
                        oversize += 1
                        continue
                    try:
                        number = Decimal(text)
                    except (InvalidOperation, ArithmeticError, ValueError):
                        continue
                    # Untrusted body: DynamoDB rejects non-finite, subnormal or clamped
                    # (positive-exponent) Decimals, and no real boxscore stat needs more
                    # than five integer or four fractional digits.
                    if (number.is_finite() and abs(number) <= 99999
                            and -4 <= number.as_tuple().exponent <= 0):
                        stats[mapped] = number
    if invalid_ids or excess_athletes or excess_stats or oversize:
        logging.getLogger(__name__).warning(
            "Boxscore %s: skipped %d entries with invalid athleteId (first %s); dropped %d "
            "excess boxscore athlete entries beyond %d; dropped excess boxscore stats for %d "
            "entries beyond %d; skipped %d oversize boxscore stat values over %d chars",
            _sample(game_id), invalid_ids, first_invalid, excess_athletes, max_athletes,
            excess_stats, max_stats, oversize, max_value_len)
    return [{"athleteId": athlete_id, "gameId": game_id, "gameState": state,
             "gameStatus": detail if isinstance(detail, str) else None,
             "source": source, "asOf": max(clocks) if clocks else None, "stats": stats}
            for athlete_id, stats in by_athlete.items() if stats]


def broadcast_networks(payload):
    """Network short names from header.competitions[0].broadcasts (X05-OBS-001)."""
    competition = payload["header"]["competitions"][0]
    return [entry["media"]["shortName"] for entry in competition.get("broadcasts", [])]
