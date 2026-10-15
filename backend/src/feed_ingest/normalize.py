"""ESPN summary plays to GameEvents in the store.put_event shape (AFC-PR-012)."""


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
            "playerIds": players, "eventTime": play.get("wallclock")}


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
        elif any(before.get(key) != value for key, value in facts.items()):
            correction_of = int(before["revision"])
            revision = correction_of + 1
        else:
            continue
        events.append({"gameId": game_id, "eventId": play["id"], "revision": revision,
                       "correctionOf": correction_of, **facts})
    return events


def broadcast_networks(payload):
    """Network short names from header.competitions[0].broadcasts (X05-OBS-001)."""
    competition = payload["header"]["competitions"][0]
    return [entry["media"]["shortName"] for entry in competition.get("broadcasts", [])]
