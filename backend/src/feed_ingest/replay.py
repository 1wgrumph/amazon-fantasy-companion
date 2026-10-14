"""Captured-fixture replay with `source: replay` on every value (AFC-PR-013).

Fixtures follow CONTRACT-AFC-P2-FIXTURE; every indexed file must match its sha256.
"""

import hashlib
import json
import re
from pathlib import Path

from feed_ingest.normalize import normalize_summary
from feed_ingest.validation import validate_summary


def _index(game_id, fixtures_dir):
    if not isinstance(game_id, str) or not re.fullmatch(r"[0-9]{1,20}", game_id):
        raise ValueError("Replay game id must be an ESPN event id")
    path = Path(fixtures_dir) / game_id / "index.json"
    if not path.is_file():
        raise ValueError(f"No captured replay for game {game_id}")
    index = json.loads(path.read_text())
    if index.get("game_id") != game_id or index.get("schema") != "afc.replay-index.v1":
        raise ValueError(f"Replay index does not describe game {game_id}")
    return index


def load_events(game_id, fixtures_dir):
    """The latest captured summary of `game_id`, verified and normalized as replay."""
    index = _index(game_id, fixtures_dir)
    game_dir = Path(fixtures_dir) / game_id
    for entry in index["files"]:
        raw = (game_dir / Path(entry["file"]).name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry["sha256"]:
            raise ValueError(f"Replay fixture {entry['file']} fails its index hash")
    summaries = [entry for entry in index["files"] if entry["endpoint"] == "summary"]
    if not summaries:
        raise ValueError(f"No captured summary for game {game_id}")
    latest = max(summaries, key=lambda entry: entry["seq"])
    payload = json.loads((game_dir / Path(latest["file"]).name).read_bytes())
    # The envelope needs an event time; a captured play without wallclock (one in
    # 401872986) is left out of replay rather than given an invented time.
    for drive in payload.get("drives", {}).get("previous", []):
        drive["plays"] = [play for play in drive.get("plays", []) if "wallclock" in play]
    validate_summary(payload, game_id)
    return normalize_summary(payload, game_id, source="replay")
