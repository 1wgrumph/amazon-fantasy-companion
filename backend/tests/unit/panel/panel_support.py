"""Import-safe seams, fixtures and Moto seeding for the P2-B07 panel red tests.

Missing modules and AFC-STUB bodies fail by assertion so CMD-RED shows
behavioral red, never collection errors, import errors or skips.

Handoff contract (frozen with this suite; DES-AFC-P2-PANELSVC, spec 4.1.11,
4.1.12, 4.3; TV wire shape frozen by P2-A05T PanelFixtures.kt):
- panel.project(game_event, matches): game_event is the stored GameEvent
  (store.put_event shape, with period and scoringPlay); matches follow
  P2-B04T {profileId, eventId, revision, starters, cursor}. It recomputes and
  stores PanelState for every matched profile and never writes Alerts.
- panel.snapshot(profile_id, team_league) returns the GET /v1/panel envelope:
  schemaVersion (int), opaque id (stable per profile and team/league),
  revision (int, unchanged on a re-read, strictly greater whenever the panel
  content changes), source = the active lineup source (yahoo | manual),
  updatedAt (RFC 3339 UTC) and data.
- team/league key: "<league>/<team>" of the Lineups row. team_league None
  selects Settings.teamLeague {league, team}, else the active lineup's pair.
  A pair other than the active lineup's shows no rows and an unknown total.
- data: teamLeague (str), scoringBasis (yahooLeague | ppr | halfPpr: Yahoo
  league scoring for a Yahoo lineup, else Settings.scoringPreset, default
  halfPpr), visible (Settings.panelPrefs.visible, default True), rows
  [{playerId, name, points, gameStatus}], teamTotal, progress and games.
  playerId is the ESPN athlete id (Yahoo starters map through
  matcher.PLAYER_MAP_PATH); an unmatched Yahoo starter keeps a row whose
  points are unknown. gameStatus is the statistics gameStatus, or None.
- value object (points, teamTotal, progress): {value, reason, source, asOf,
  stale}. value is a number or None; None always carries a non-empty reason
  and a known zero is 0 with no reason. source is the statistics source
  (live | replay), asOf the statistics source timestamp (never the read or
  projection time), stale is True when asOf is missing or panel.now() - asOf
  >= 60 s (stale_after, evaluated at snapshot time). teamTotal sums the row
  points under the basis, asOf = oldest row asOf; with any unknown row it is
  None or carries a non-empty reason. progress is 0 when every starter's game
  is pre, 1 when every one is post.
- games: {gameId: {eventId, revision, score, source}} from the projected
  GameEvents: a later revision of the same eventId replaces the facts in
  place, an equal or lower revision never does, so the panel agrees with the
  alert record (revision, triggerContext.score/source) for the same event.
- Seams read at call time through the panel module: panel.player_statistics
  (athlete_id) -> None (unknown) or {gameId, gameState (pre | in | post),
  gameStatus, source, asOf, stats {CONTRACT-AFC-P2-PRESETS stat name:
  number}}; panel.now() -> RFC 3339 UTC string. Tests replace both.
- Manual points apply lineup.presets.TABLES[preset]; a statistic without a
  table row awards no points. Yahoo points apply the league stat_modifiers; a
  statistic without a modifier scores nothing. A stored preset outside the
  two presets is never scored.
"""

import importlib
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from numbers import Number
from types import SimpleNamespace

import pytest

KICKOFF = datetime(2026, 10, 18, 20, 0, 0, tzinfo=timezone.utc)
GAME = "401999001"
OTHER_GAME = "401999002"
LEAGUE, TEAM = "league-a", "team-7"
TEAM_LEAGUE = LEAGUE + "/" + TEAM
OTHER_PAIR = {"league": "league-b", "team": "team-2"}
BASES = ("yahooLeague", "ppr", "halfPpr")
STALE_AFTER = 60
STAT_NAMES = ("receptions", "rushing_yards", "receiving_yards", "rushing_touchdowns",
              "receiving_touchdowns", "passing_yards", "passing_touchdowns",
              "interceptions_thrown", "fumbles_lost")

# Synthetic ESPN identities shared with P2-B04T/B05T; names belong to no real athlete.
RECEIVER = {"athlete_id": "9000001", "name": "Sample Receiver", "team": "PHI", "slot": "WR"}
PASSER = {"athlete_id": "9000005", "name": "Sample Passer", "team": "PHI", "slot": "QB"}
RUNNER = {"athlete_id": "9000011", "name": "Sample Runner", "team": "DAL", "slot": "RB"}
TIGHT_END = {"athlete_id": "9000013", "name": "Sample Tight End", "team": "DAL", "slot": "TE"}

PLAYER_MAP = {"schemaVersion": 1, "players": [
    {"espn_athlete_id": "9000001", "name": "Sample Receiver", "team": "PHI",
     "position": "WR", "confidence": "exact"},
    {"espn_athlete_id": "9000005", "name": "Sample Passer", "team": "PHI",
     "position": "QB", "confidence": "exact"},
]}
YAHOO_RECEIVER = {"player_key": "nfl.p.7001", "name": "Sample Receiver", "team": "PHI",
                  "positions": ["WR"], "slot": "WR"}
YAHOO_PASSER = {"player_key": "nfl.p.7005", "name": "Sample Passer", "team": "PHI",
                "positions": ["QB"], "slot": "QB"}
YAHOO_UNMAPPED = {"player_key": "nfl.p.7099", "name": "Unmapped Back", "team": "NYJ",
                  "positions": ["RB"], "slot": "RB"}
YAHOO_MODIFIERS = {"receptions": Decimal("1.5"), "receiving_yards": Decimal("0.2"),
                   "receiving_touchdowns": Decimal("4"), "rushing_yards": Decimal("0.1")}


def iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def at(seconds):
    """RFC 3339 UTC `seconds` after KICKOFF."""
    return iso(KICKOFF + timedelta(seconds=seconds))


def parse(stamp):
    assert isinstance(stamp, str), f"timestamp must be an RFC 3339 string, got {stamp!r}"
    assert stamp.endswith("Z") or stamp.endswith("+00:00"), f"timestamp must be UTC: {stamp!r}"
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def require_module(name):
    """Import a module under test; a missing module is an assertion failure."""
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        raise AssertionError(f"panel behavior is not implemented: cannot import {name}: {exc}")


def attempt(func, *args, **kwargs):
    """Call product code; an AFC-STUB NotImplementedError is an assertion failure."""
    try:
        return func(*args, **kwargs)
    except NotImplementedError as exc:
        raise AssertionError(f"panel behavior is not implemented (AFC-STUB): {exc}")


def number(value):
    """A JSON-able number (int, float or DynamoDB Decimal) as float; None stays None."""
    if value is None:
        return None
    assert isinstance(value, Number) and not isinstance(value, bool), \
        f"panel value must be a number or None, got {value!r}"
    return float(value)


def game_event(event_id, players=("9000001",), *, game=GAME, seconds=0, score=(7, 3),
               revision=1, correction_of=None, source="live", scoring=False, period=2):
    """A stored GameEvent (store.put_event shape) plus ESPN period and scoringPlay."""
    return {"gameId": game, "eventId": event_id, "revision": revision,
            "correctionOf": correction_of, "source": source,
            "score": {"away": score[0], "home": score[1]}, "fieldPosition": 35,
            "possession": "PHI", "playerIds": list(players), "eventTime": at(seconds),
            "period": period, "scoringPlay": scoring}


def match(profile_id, event, starters=(RECEIVER,), cursor=None):
    """One P2-B04T match for this profile and event."""
    return {"profileId": profile_id, "eventId": event["eventId"],
            "revision": event["revision"], "starters": [dict(s) for s in starters],
            "cursor": cursor}


def statistics(game=GAME, state="in", status="Q2 08:14", source="live", as_of=None, **stats):
    """One player_statistics record; as_of defaults to KICKOFF."""
    return {"gameId": game, "gameState": state, "gameStatus": status, "source": source,
            "asOf": at(0) if as_of is None else as_of, "stats": dict(stats)}


def seed_profile(profile_id, **settings):
    import store
    assert store.put_profile(profile_id, dict(settings), 0, at(0)), "profile seed must succeed"


def update_profile(profile_id, **settings):
    """Replace the profile's Settings at its next revision (as PUT /v1/profile does)."""
    import store
    current = store.get_profile(profile_id)
    assert current is not None, "profile must exist before an update"
    merged = dict(current.get("settings", {}), **settings)
    assert store.put_profile(profile_id, merged, int(current["revision"]), at(1)), \
        "profile update must succeed"


def seed_lineup(profile_id, starters, source="manual", league=LEAGUE, team=TEAM):
    import store
    row = {"profileId": profile_id, "source": source, "team": team, "league": league,
           "starters": [dict(s) for s in starters], "updatedAt": at(0)}
    if source == "yahoo":
        row["scoring"] = {"league_key": "nfl.l.1001", "stat_modifiers": dict(YAHOO_MODIFIERS),
                          "roster_slots": ["QB", "WR", "RB", "TE", "BN"]}
    store.put_lineup(row)


def seed_alert(profile_id, cursor, event, starters=(RECEIVER,), basis="profile-assumption"):
    """The Alerts row the P2-B05T policy contract stores for this event revision."""
    import store
    store.put_alert({"profileId": profile_id, "cursor": cursor, "eventId": event["eventId"],
                     "revision": event["revision"], "alertType": "PlayerScore",
                     "triggerContext": {"gameId": event["gameId"], "eventId": event["eventId"],
                                        "source": event["source"], "score": event["score"],
                                        "starters": [dict(s) for s in starters],
                                        "alertTypes": ["PlayerScore"], "basis": basis},
                     "commentary": None, "emittedAt": event["eventTime"]})


def check_value(obj, where):
    """A PanelState value object; returns its value as float or None."""
    assert isinstance(obj, dict), f"{where} must be a value object, got {obj!r}"
    for key in ("value", "reason", "source", "asOf", "stale"):
        assert key in obj, f"{where} lacks {key!r}: {obj!r}"
    value = number(obj["value"])
    if value is None:
        assert isinstance(obj["reason"], str) and obj["reason"].strip(), \
            f"{where}: an unknown value needs a reason, never a silent gap: {obj!r}"
    assert obj["source"] in ("live", "replay", None), f"{where} source: {obj!r}"
    if obj["asOf"] is not None:
        parse(obj["asOf"])
    assert isinstance(obj["stale"], bool), f"{where} stale must be a boolean: {obj!r}"
    if obj["asOf"] is None and value is not None:
        assert obj["stale"] is True, f"{where}: a value without a timestamp is never fresh"
    return value


def check_envelope(envelope):
    """CONTRACT-AFC-P2-ENVELOPE plus the P2-A05T panel data shape; returns data."""
    assert isinstance(envelope, dict), f"snapshot must return an envelope, got {envelope!r}"
    for key in ("schemaVersion", "id", "revision", "source", "updatedAt", "data"):
        assert key in envelope, f"panel envelope lacks {key!r}: {envelope!r}"
    assert isinstance(envelope["schemaVersion"], int), envelope
    assert isinstance(envelope["id"], str) and envelope["id"], envelope
    revision = number(envelope["revision"])
    assert revision is not None and revision >= 0 and revision == int(revision), envelope
    assert envelope["source"] in ("yahoo", "manual"), \
        f"panel source is the active lineup source: {envelope['source']!r}"
    parse(envelope["updatedAt"])
    data = envelope["data"]
    assert isinstance(data, dict), envelope
    assert isinstance(data.get("teamLeague"), str) and data["teamLeague"], data
    assert data.get("scoringBasis") in BASES, f"no value without its scoring basis: {data!r}"
    assert isinstance(data.get("visible"), bool), data
    rows = data.get("rows")
    assert isinstance(rows, list) and len(rows) <= 32, data
    ids = []
    for row in rows:
        assert isinstance(row, dict), row
        assert isinstance(row.get("playerId"), str) and row["playerId"], row
        assert isinstance(row.get("name"), str), row
        assert "gameStatus" in row and (row["gameStatus"] is None
                                        or isinstance(row["gameStatus"], str)), row
        check_value(row.get("points"), "row " + row["playerId"] + " points")
        ids.append(row["playerId"])
    assert len(ids) == len(set(ids)), f"one row per starter: {ids}"
    check_value(data.get("teamTotal"), "teamTotal")
    progress = check_value(data.get("progress"), "progress")
    assert progress is None or 0.0 <= progress <= 1.0, data
    assert isinstance(data.get("games"), dict), data
    return data


def row(data, player_id):
    rows = [r for r in data["rows"] if r["playerId"] == player_id]
    assert len(rows) == 1, f"expected one row for {player_id}: {data['rows']!r}"
    return rows[0]


def row_named(data, name):
    rows = [r for r in data["rows"] if r["name"] == name]
    assert len(rows) == 1, f"expected one row named {name}: {data['rows']!r}"
    return rows[0]


def points(data, player_id):
    return number(row(data, player_id)["points"]["value"])


def player_ids(data):
    return {r["playerId"] for r in data["rows"]}


def link(api, profile_id):
    """A device session for profile_id through the landed link API."""
    status, device = api.request("POST", "/v1/link")
    assert status in (200, 201), device
    status, _ = api.request("POST", "/v1/link/confirm", {"code": device["code"],
                                                          "profileId": profile_id})
    assert status == 200
    status, polled = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and polled.get("sessionToken"), polled
    return polled["sessionToken"]


@pytest.fixture
def panel_env(api, monkeypatch, tmp_path):
    """Fresh panel bound to per-test statistics, clock, player map and Moto tables."""
    module = require_module("panel")
    matcher = require_module("matcher")
    player_map = tmp_path / "player_map.json"
    player_map.write_text(json.dumps(PLAYER_MAP))
    monkeypatch.setattr(matcher, "PLAYER_MAP_PATH", player_map, raising=False)
    stats = {}
    clock = {"now": at(5)}
    monkeypatch.setattr(module, "player_statistics", stats.get, raising=False)
    monkeypatch.setattr(module, "now", lambda: clock["now"], raising=False)

    def project(event, matches):
        import store
        store.put_event(event)
        before = len(api.table("Alerts").scan()["Items"])
        attempt(module.project, event, list(matches))
        after = len(api.table("Alerts").scan()["Items"])
        assert after == before, "the panel must never write alert records"

    def snapshot(profile_id, team_league=None):
        return attempt(module.snapshot, profile_id, team_league)

    def data(profile_id, team_league=None):
        return check_envelope(snapshot(profile_id, team_league))

    def set_now(seconds):
        clock["now"] = at(seconds)

    return SimpleNamespace(module=module, api=api, stats=stats, project=project,
                           snapshot=snapshot, data=data, set_now=set_now)
