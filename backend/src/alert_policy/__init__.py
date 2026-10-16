"""DES-AFC-P2-POLICY alert gates and commentary (P2-B05).

Gate order: relevance (matches) -> enabled types -> game-day periods ->
quiet hours -> alert_min_gap per game -> spoiler delay -> emit. Red zone is
possession strictly inside 20 yards by a matched starter's team; player
score is a scoring play listing a matched starter; close game is margin
<= 8 in period 4 (Q4) or >= 5 (OT), once per game while the state lasts.
Commentary is a fixed template per excitement level, filled only from the
event, and names no player or team, so it cannot claim on-field position.
"""

import json
import re
from datetime import datetime, timedelta, timezone

import store

_TYPES = ("RedZone", "PlayerScore", "CloseGame")
_RED_ZONE_YARDS = 20
_CLOSE_MARGIN = 8
_PENDING_BUDGET = 60000  # serialized bytes; the API envelope limit is 65536

# ESPN teamParticipant ids are numeric; starters carry abbreviations. Both
# sides canonicalize to the ESPN abbreviation at this boundary (R01).
_ESPN_TEAMS = {"1": "ATL", "2": "BUF", "3": "CHI", "4": "CIN", "5": "CLE", "6": "DAL",
               "7": "DEN", "8": "DET", "9": "GB", "10": "TEN", "11": "IND", "12": "KC",
               "13": "LV", "14": "LAR", "15": "MIA", "16": "MIN", "17": "NE", "18": "NO",
               "19": "NYG", "20": "NYJ", "21": "PHI", "22": "ARI", "23": "PIT", "24": "LAC",
               "25": "SF", "26": "SEA", "27": "TB", "28": "WSH", "29": "CAR", "30": "JAX",
               "33": "BAL", "34": "HOU"}
_TEAM_ALIASES = {"WAS": "WSH", "JAC": "JAX", "LA": "LAR", "STL": "LAR", "SD": "LAC",
                 "OAK": "LV"}

# shortcut: close-game exit is tracked in-process (the pipeline evaluates a
# game's events in order per invocation) plus score evidence in stored
# alerts; upgrade to a stored per-game state row if evaluations split across
# processes mid-game.
_close_exited = {}


def _team(value):
    text = str(value or "").upper()
    text = _ESPN_TEAMS.get(text, text)
    return _TEAM_ALIASES.get(text, text)


def _parse(stamp):
    return datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))


def _iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _all_alerts(profile_id):
    alerts, after = [], None
    while True:
        page = store.list_alerts(profile_id, after, 100)
        alerts.extend(page)
        if len(page) < 100:
            return alerts
        after = page[-1]["cursor"]


def _in_window(minute, window):
    start, end = _int(window.get("startMinute")), _int(window.get("endMinute"))
    if start <= end:
        return start <= minute < end or (start == end and minute == start)
    return minute >= start or minute < end


def _commentary(level, alert_type, game_event):
    if level not in ("Mild", "Hype"):
        return None
    score = game_event.get("score") or {}
    away, home = _int(score.get("away")), _int(score.get("home"))
    margin, period = abs(home - away), _int(game_event.get("period"))
    yards = _int(game_event.get("fieldPosition"))
    if level == "Mild":
        text = {
            "RedZone": f"Red-zone chance: ball at the {yards}, inside the 20. Score {away}-{home}.",
            "PlayerScore": f"A score on a play listing your starter. Score {away}-{home}.",
            "CloseGame": f"Close game in period {period}: margin {margin}. Score {away}-{home}.",
        }
    else:
        text = {
            "RedZone": f"Red-zone alert! Ball at the {yards}, inside the 20! Score {away}-{home}!",
            "PlayerScore": f"Big score play listing your starter! Score {away}-{home}!",
            "CloseGame": f"Nail-biter! Margin {margin} in period {period}! Score {away}-{home}!",
        }
    return text[alert_type]


def evaluate(game_event, matches):
    """Alert items (store.put_alert shape) the policy gates admit for the matched profiles."""
    event_time = _parse(game_event["eventTime"])
    minute = event_time.hour * 60 + event_time.minute
    score = game_event.get("score") or {}
    margin = abs(_int(score.get("home")) - _int(score.get("away")))
    player_ids = {str(p) for p in game_event.get("playerIds") or []}
    alerts = []
    for match in matches or []:
        profile_id = match.get("profileId")
        profile = store.get_profile(profile_id) if profile_id else None
        if not profile:
            continue
        settings = profile.get("settings") or {}
        starters = [dict(s) for s in match.get("starters") or []]
        matched = []
        yards = game_event.get("fieldPosition")
        if (yards is not None and _int(yards, 99) < _RED_ZONE_YARDS
                and _team(game_event.get("possession"))
                in {_team(s.get("team")) for s in starters}):
            matched.append("RedZone")
        if game_event.get("scoringPlay") and any(
                str(s.get("athlete_id")) in player_ids for s in starters):
            matched.append("PlayerScore")
        is_close = _int(game_event.get("period")) >= 4 and margin <= _CLOSE_MARGIN
        if is_close:
            matched.append("CloseGame")
        close_key = (profile_id, game_event.get("gameId"))
        exited = _close_exited.get(close_key, False)
        if _int(game_event.get("period")) >= 4:
            _close_exited[close_key] = not is_close
        revision = bool(match.get("cursor"))
        enabled = [t for t in _TYPES if t in matched and t in (settings.get("alertTypes") or [])]
        if revision and not enabled:
            # A correction revises the stored alert even when its trigger is
            # gone (R02); it keeps the stored alert's type.
            stored = next((a for a in _all_alerts(profile_id)
                           if a.get("cursor") == match.get("cursor")), None)
            enabled = [stored["alertType"]] if stored and stored.get("alertType") else matched[:1]
        if not enabled:
            continue
        if revision:
            # Revisions bypass the new-alert gates below (R02).
            release = event_time + timedelta(seconds=_int(settings.get("spoilerDelay")))
            alerts.append(_alert(profile_id, match, game_event, settings, starters,
                                 enabled, score, release))
            continue
        game_day = settings.get("gameDayPeriods") or {}
        periods = game_day.get("periods") or []
        if game_day.get("enabled", True) and periods and not any(
                _in_window(minute, w) for w in periods):
            continue
        if any(_in_window(minute, w) for w in settings.get("quietHours") or []):
            continue
        release = event_time + timedelta(seconds=_int(settings.get("spoilerDelay")))
        prior = [a for a in _all_alerts(profile_id)
                 if a.get("eventId") != game_event.get("eventId")
                 and (a.get("triggerContext") or {}).get("gameId") == game_event.get("gameId")]
        if "CloseGame" in enabled:
            close_prior = [a for a in prior if "CloseGame" in
                           ((a.get("triggerContext") or {}).get("alertTypes")
                            or [a.get("alertType")])]
            # Once per entry (R06): an observed exit, or a later stored alert
            # whose score is no longer close, re-arms the trigger.
            left = exited or (close_prior and any(
                a.get("emittedAt", "") > max(p.get("emittedAt", "") for p in close_prior)
                and abs(_int(((a.get("triggerContext") or {}).get("score") or {}).get("home"))
                        - _int(((a.get("triggerContext") or {}).get("score") or {}).get("away")))
                > _CLOSE_MARGIN for a in prior))
            if close_prior and not left:
                enabled = [t for t in enabled if t != "CloseGame"]
                if not enabled:
                    continue
        gap = _int(settings.get("frequency"))
        if gap > 0 and not match.get("cursor") and any(
                0 <= (release - _parse(a["emittedAt"])).total_seconds() < gap
                for a in prior if a.get("emittedAt")):
            continue
        alerts.append(_alert(profile_id, match, game_event, settings, starters,
                             enabled, score, release))
    return alerts


def _alert(profile_id, match, game_event, settings, starters, enabled, score, release):
    emitted_at = _iso(release)
    # Consent is not observation (R05): observed-playback needs evidence
    # carried on the match or event, plus opt-in.
    observed = settings.get("detectionOptIn") and "observed-playback" in (
        match.get("basis"), game_event.get("basis"))
    context = {"gameId": game_event.get("gameId"), "eventId": game_event.get("eventId"),
               "source": game_event.get("source"), "score": dict(score),
               "starters": starters, "alertTypes": enabled,
               "basis": "observed-playback" if observed else "profile-assumption"}
    return {
        "profileId": profile_id,
        "cursor": match.get("cursor") or f"{emitted_at}#{game_event.get('eventId')}",
        "eventId": game_event.get("eventId"),
        "revision": _int(game_event.get("revision"), _int(match.get("revision"), 1)),
        "alertType": enabled[0], "triggerContext": context,
        "commentary": _commentary(settings.get("excitement"), enabled[0], game_event),
        "emittedAt": emitted_at}


def _progress(alert):
    """Delivery-progress token for an alert: cursor, plus its revision when > 1 (R03)."""
    revision = _int(alert.get("revision"), 1)
    return f"{alert['cursor']}~r{revision}" if revision > 1 else alert["cursor"]


def pending(profile_id, cursor):
    """GET /v1/alerts body: {"alerts": [enveloped Alert], "cursor": str}, after cursor (None = start).

    The returned cursor is a progress token: the last served alert's cursor,
    suffixed with ~r<revision> when that revision is above 1, so a later
    correction of an already-consumed alert is served again (R03). A plain
    cursor means revision 1 was consumed. Responses stay under the 64 KiB
    API envelope and resume from the last served alert (R04).
    """
    now = datetime.now(timezone.utc)
    served, current, size = [], cursor or "", 64
    token = re.match(r"^(.*)~r(\d+)$", cursor or "")
    base, consumed = (token.group(1), int(token.group(2))) if token else (cursor, 1)
    base = base or None  # an empty cursor is the start, never a Dynamo key
    after, include = base, base is not None
    while True:
        page = store.list_alerts(profile_id, after, 100, include_after=include)
        include = False
        for alert in page:
            if alert["cursor"] == base and _int(alert.get("revision"), 1) <= consumed:
                continue
            if _parse(alert["emittedAt"]) > now:
                return {"alerts": served, "cursor": current}
            context = alert.get("triggerContext") or {}
            envelope = {
                "schemaVersion": 1, "id": alert["cursor"], "revision": alert.get("revision"),
                "source": context.get("source"), "updatedAt": alert.get("emittedAt"),
                "data": {"alertType": alert.get("alertType"), "triggerContext": context,
                         "commentary": alert.get("commentary"),
                         "route": alert.get("providerRoute")}}
            size += len(json.dumps(envelope, default=str).encode()) + 1
            if served and size > _PENDING_BUDGET:
                return {"alerts": served, "cursor": current}
            served.append(envelope)
            current = _progress(alert)
        if len(page) < 100:
            return {"alerts": served, "cursor": current}
        after = page[-1]["cursor"]
