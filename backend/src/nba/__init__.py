"""Stretch spike (DEC-AFC-NBA-STRETCH-20261020): ESPN NBA ingest behind AFC_ENABLE_NBA.

Off by default: poll() returns without fetching unless the flag is on, and
every hook in an existing module checks the same flag before importing here.
"""

import logging
import os

FEED = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/"
_TRUE = ("1", "true", "yes")


def enabled():
    return os.environ.get("AFC_ENABLE_NBA", "").lower() in _TRUE


def poll(get_json, store_records=None):
    """Fetch the NBA scoreboard and store each game's boxscore statistics.

    `get_json` is feed_ingest's allowlisted ESPN getter. A scoreboard
    failure is logged and returns the empty result, so it cannot discard
    an NFL result already stored by feed_ingest.poll. One game's failure
    never blocks the others.
    """
    result = {"stored": 0, "failed": []}
    if not enabled():
        return result
    from nba.normalize import boxscore_statistics_nba, scoreboard_games

    if store_records is None:
        from feed_ingest.ingest import store_player_statistics as store_records
    try:
        games = scoreboard_games(get_json(FEED + "scoreboard"))
    except (ValueError, OSError):
        logging.getLogger(__name__).warning("NBA scoreboard unavailable")
        return result
    for game in games:
        game_id = game["gameId"]
        try:
            summary = get_json(FEED + "summary?event=" + game_id)
            records = boxscore_statistics_nba(summary, game_id)
        except (ValueError, OSError):
            result["failed"].append(game_id)
            continue
        store_records(records)
        result["stored"] += len(records)
    return result
