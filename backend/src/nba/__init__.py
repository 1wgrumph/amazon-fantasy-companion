"""Stretch spike (DEC-AFC-NBA-STRETCH-20261020): ESPN NBA ingest behind AFC_ENABLE_NBA.

Off by default: poll() returns without fetching unless the flag is on, and
every hook in an existing module checks the same flag before importing here.
"""

import functools
import logging
import os
import signal
import time
from contextlib import contextmanager

from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

FEED = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/"
_TRUE = ("1", "true", "yes")
_RUN_SECONDS = 20
_REQUEST_SECONDS = 5
_WRITE_SECONDS = 3


class _DeadlineExceeded(Exception):
    """Separate from OSError/ValueError so poll cannot swallow an expired run."""


def _expired(signum, frame):
    raise _DeadlineExceeded("NBA ingest deadline exceeded")


@contextmanager
def _deadline(seconds):
    """Lambda runs this on Linux's main thread; bound blocking I/O as well as loops."""
    if seconds <= 0:
        raise _DeadlineExceeded("NBA ingest deadline exceeded")
    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    started = time.monotonic()
    delay = min(seconds, previous_timer[0]) if previous_timer[0] else seconds
    signal.signal(signal.SIGALRM, _expired)
    signal.setitimer(signal.ITIMER_REAL, delay)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        left = previous_timer[0] - (time.monotonic() - started)
        if left > 0:
            signal.setitimer(signal.ITIMER_REAL, left, previous_timer[1])


def _fetch(deadline, url):
    from feed_ingest import _get_json

    with _deadline(min(_REQUEST_SECONDS, deadline - time.monotonic())):
        return _get_json(url)


@functools.cache
def _write_config():
    return Config(connect_timeout=1, read_timeout=1,
                  retries={"mode": "standard", "total_max_attempts": 1})


def _write_records(records, channel=None):
    import store
    from feed_ingest.ingest import store_player_statistics

    write = functools.partial(store.put_nba_statistics, channel=channel)
    for record in records:
        with _deadline(_WRITE_SECONDS):
            store_player_statistics([record], config=_write_config(), write=write)


def lambda_handler(event, context):
    """One NBA-only scheduled run, isolated from the NFL IngestFunction."""
    if not isinstance(event, dict) or event.get("source", "aws.scheduler") != "aws.scheduler":
        raise ValueError("NbaIngestFunction accepts only its schedule event")
    result = {"stored": 0, "failed": []}
    if not enabled():
        return result
    seconds = _RUN_SECONDS
    if context is not None:
        seconds = min(seconds, context.get_remaining_time_in_millis() / 1000 - 2)
    try:
        with _deadline(seconds):
            deadline = time.monotonic() + seconds
            return poll(functools.partial(_fetch, deadline))
    except Exception as exc:
        logging.getLogger(__name__).warning("NBA poll failed: %.200s", exc)
        return result


def enabled():
    return os.environ.get("AFC_ENABLE_NBA", "").lower() in _TRUE


def _store_pregame(teams):
    """Persist even an empty slate; a write failure must not drop boxscores."""
    if not os.environ.get("PLAYER_STATS_TABLE"):
        return
    from store import put_nba_pregame

    try:
        put_nba_pregame(teams, config=_write_config())
    except (BotoCoreError, ClientError) as exc:
        logging.getLogger(__name__).warning("NBA pregame status not stored: %.200s", exc)


def poll(get_json, store_records=None):
    """Fetch the NBA scoreboard and store each game's boxscore statistics.

    A not-yet-started game also stores its ESPN status text per team
    abbreviation. `get_json` is an allowlisted ESPN getter. A scoreboard
    failure is logged and returns the empty result. One game's failure
    never blocks the others.
    """
    result = {"stored": 0, "failed": []}
    if not enabled():
        return result
    from nba.normalize import boxscore_statistics_nba, pregame_status_by_team, scoreboard_games

    try:
        board = get_json(FEED + "scoreboard")
        games = scoreboard_games(board)
    except (ValueError, OSError):
        logging.getLogger(__name__).warning("NBA scoreboard unavailable")
        return result
    _store_pregame(pregame_status_by_team(board))
    for game in games:
        game_id = game["gameId"]
        try:
            summary = get_json(FEED + "summary?event=" + game_id)
            records = boxscore_statistics_nba(summary, game_id)
        except (ValueError, OSError):
            result["failed"].append(game_id)
            continue
        if store_records is None:
            from feed_ingest.normalize import _channel
            _write_records(records, channel=_channel(summary))
        else:
            store_records(records)
        result["stored"] += len(records)
    return result
