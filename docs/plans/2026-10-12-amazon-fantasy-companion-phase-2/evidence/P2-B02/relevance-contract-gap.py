"""Offline proof: a valid manual starter outside scoreboard leaders loses its game."""

import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(root / "backend" / "src"))
import feed_ingest
from lineup.manual import build

fixtures = root / "backend" / "fixtures" / "replay" / "401872981"
summary = json.loads((fixtures / "001-summary.json").read_text())
board = json.loads((fixtures / "001-scoreboard.json").read_text())
game = next(game for game in board["events"] if game["id"] == "401872981")
game["status"]["type"]["state"] = "in"
leaders = {leader["athlete"]["id"] for competition in game["competitions"]
           for category in competition.get("leaders", []) for leader in category["leaders"]}
for team in summary["boxscore"]["players"]:
    candidates = [entry["athlete"] for stat in team["statistics"]
                  for entry in stat.get("athletes", []) if stat["name"] == "receiving"]
    selected = next((a for a in candidates if a["id"] not in leaders), None)
    if selected:
        break
assert selected is not None
# Even an enriched roster input loses its NFL-team identity in the current builder.
roster = [{"athlete_id": selected["id"], "name": selected["displayName"],
           "team": team["team"]["abbreviation"]}]
lineup = build(roster, [{"athlete_id": selected["id"], "slot": "FLEX"}], "PPR")
actual = feed_ingest._monitored(game, [{"settings": {}, "starters": lineup["starters"]}])
proof = {"outcome": "CONTRACT_FAILURE", "finding": "F5", "game_id": game["id"],
         "captured_athlete_id": selected["id"], "captured_athlete_name": selected["displayName"],
         "captured_team": team["team"]["abbreviation"], "manual_starter": lineup["starters"][0],
         "athlete_is_scoreboard_leader": selected["id"] in leaders,
         "expected_monitored": True, "actual_monitored": actual,
         "required_authority": ["backend/src/lineup/manual.py and its team-identity input/output contract", "associated lineup tests / any affected frozen test authority"],
         "iam": "No additional IAM grant is needed beyond the granted Profiles Scan and existing Lineups GetItem.",
         "scope": "F5 negative irrelevant-game case is repaired; complete selected-manual-player relevance remains blocked. Full AFC-PR-008 cannot be claimed."}
assert actual is False, "The recorded contract gap no longer reproduces"
print(json.dumps(proof, indent=2))
