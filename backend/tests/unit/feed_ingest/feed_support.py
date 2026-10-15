"""Import-safe loading and captured-fixture access for the P2-B02 red tests.

Missing modules, missing attributes and AFC-STUB bodies fail by assertion so
CMD-RED shows behavioral red, never collection or import errors. Fixtures are
the P2-X05 captures under backend/fixtures/replay (CONTRACT-AFC-P2-FIXTURE);
they are read, never edited — malformed variants are deep copies in tests.

Handoff surface the tests name for P2-B02 (DES-AFC-P2-FEED):
- feed_ingest.validation.validate_summary(payload, game_id) /
  validate_scoreboard(payload): return None when valid, raise ValueError
  otherwise, before any store write (AFC-PR-064).
- feed_ingest.normalize.normalize_summary(payload, game_id, source="live",
  prior=None): one GameEvent dict per play in drives.previous[].plays[],
  in the store.put_event shape (gameId, eventId, revision, source, score,
  fieldPosition, possession, playerIds, eventTime, correctionOf); `prior`
  maps eventId -> stored event, unchanged plays emit nothing, a changed
  play emits revision+1 with correctionOf set to the superseded revision.
  feed_ingest.normalize.broadcast_networks(payload): network short names
  from header.competitions[0].broadcasts (X05-OBS-001).
- feed_ingest.ingest.ingest_summary(payload, game_id, source="live"):
  validate, then store every normalized event; returns the stored events.
- feed_ingest.replay.load_events(game_id, fixtures_dir): verify the fixture
  index sha256, then normalized events with source "replay" on every value.
- feed_ingest.monitoring.monitored_decisions(games, selected_player_ids,
  favorite_team_ids, enabled, basis): one decision per game,
  {"gameId", "monitored", "basis"}; basis is "observed-playback" or
  "profile-assumption" (AFC-PR-008, AFC-PR-011).
"""

import functools
import importlib
import json
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[3]
FIXTURES = BACKEND / "fixtures" / "replay"
GAME = "401872981"
OTHER_GAME = "401872982"


def require_module(name):
    """Import a module under test; a missing module is an assertion failure."""
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        raise AssertionError(f"feed behavior is not implemented: cannot import {name}: {exc}")


def require_attr(module, name):
    """Fetch a named behavior; a missing attribute is an assertion failure."""
    try:
        return getattr(module, name)
    except AttributeError:
        raise AssertionError(
            f"feed behavior is not implemented: {module.__name__} has no {name}")


def attempt(func, *args, **kwargs):
    """Call product code; an AFC-STUB NotImplementedError is an assertion failure."""
    try:
        return func(*args, **kwargs)
    except NotImplementedError as exc:
        raise AssertionError(f"feed behavior is not implemented (AFC-STUB): {exc}")


@functools.lru_cache(maxsize=None)
def _fixture(game_id, kind):
    return json.loads((FIXTURES / game_id / f"001-{kind}.json").read_text())


def fresh_summary(game_id=GAME):
    """A deep-copied captured summary a test may mutate freely."""
    return json.loads(json.dumps(_fixture(game_id, "summary")))


def fresh_scoreboard(game_id=GAME):
    """A deep-copied captured scoreboard a test may mutate freely."""
    return json.loads(json.dumps(_fixture(game_id, "scoreboard")))


def fixture_index(game_id=GAME):
    return json.loads((FIXTURES / game_id / "index.json").read_text())


def plays_in(summary):
    """Every play at the observed path (spikes/sp5-espn-feed/VERDICT.md)."""
    return [play for drive in summary["drives"]["previous"]
            for play in drive.get("plays") or []]


def boxscore_athlete_ids(summary):
    return {athlete["athlete"]["id"]
            for team in summary["boxscore"]["players"]
            for stat in team["statistics"]
            for athlete in stat.get("athletes") or []}


def competitor_team_ids(summary):
    return {c["team"]["id"] for c in summary["header"]["competitions"][0]["competitors"]}


def offense_team_id(play):
    for entry in play.get("teamParticipants") or []:
        if entry.get("type") == "offense":
            return entry["id"]
    return None
