"""DES-AFC-P2-POLICY alert gates and commentary (P2-B05).

Gate order: relevance (matches) -> enabled types -> game-day periods ->
quiet hours -> alert_min_gap per game -> spoiler delay -> emit. Red zone is
possession strictly inside 20 yards by a matched starter's team; player
score is a scoring play listing a matched starter; close game is margin
<= 8 in period 4 (Q4) or >= 5 (OT), once per game while the state lasts.
Commentary is a fixed template per excitement level, filled only from the
event, and names no player or team, so it cannot claim on-field position.
"""

from datetime import datetime, timedelta, timezone

import store

_TYPES = ("RedZone", "PlayerScore", "CloseGame")
_RED_ZONE_YARDS = 20
_CLOSE_MARGIN = 8


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
                and game_event.get("possession") in {s.get("team") for s in starters}):
            matched.append("RedZone")
        if game_event.get("scoringPlay") and any(
                str(s.get("athlete_id")) in player_ids for s in starters):
            matched.append("PlayerScore")
        if _int(game_event.get("period")) >= 4 and margin <= _CLOSE_MARGIN:
            matched.append("CloseGame")
        enabled = [t for t in _TYPES if t in matched and t in (settings.get("alertTypes") or [])]
        if not enabled:
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
        if "CloseGame" in enabled and any(
                "CloseGame" in ((a.get("triggerContext") or {}).get("alertTypes") or [a.get("alertType")])
                for a in prior):
            enabled = [t for t in enabled if t != "CloseGame"]
            if not enabled:
                continue
        gap = _int(settings.get("frequency"))
        if gap > 0 and not match.get("cursor") and any(
                0 <= (release - _parse(a["emittedAt"])).total_seconds() < gap
                for a in prior if a.get("emittedAt")):
            continue
        emitted_at = _iso(release)
        context = {"gameId": game_event.get("gameId"), "eventId": game_event.get("eventId"),
                   "source": game_event.get("source"), "score": dict(score),
                   "starters": starters, "alertTypes": enabled,
                   "basis": "observed-playback" if settings.get("detectionOptIn")
                   else "profile-assumption"}
        alerts.append({
            "profileId": profile_id,
            "cursor": match.get("cursor") or f"{emitted_at}#{game_event.get('eventId')}",
            "eventId": game_event.get("eventId"),
            "revision": _int(game_event.get("revision"), _int(match.get("revision"), 1)),
            "alertType": enabled[0], "triggerContext": context,
            "commentary": _commentary(settings.get("excitement"), enabled[0], game_event),
            "emittedAt": emitted_at})
    return alerts


def pending(profile_id, cursor):
    """GET /v1/alerts body: {"alerts": [enveloped Alert], "cursor": str}, after cursor (None = start)."""
    now = datetime.now(timezone.utc)
    served, current = [], cursor or ""
    after = cursor
    while True:
        page = store.list_alerts(profile_id, after, 100)
        for alert in page:
            if _parse(alert["emittedAt"]) > now:
                return {"alerts": served, "cursor": current}
            context = alert.get("triggerContext") or {}
            served.append({
                "schemaVersion": 1, "id": alert["cursor"], "revision": alert.get("revision"),
                "source": context.get("source"), "updatedAt": alert.get("emittedAt"),
                "data": {"alertType": alert.get("alertType"), "triggerContext": context,
                         "commentary": alert.get("commentary"),
                         "route": alert.get("providerRoute")}})
            current = alert["cursor"]
        if len(page) < 100:
            return {"alerts": served, "cursor": current}
        after = page[-1]["cursor"]
