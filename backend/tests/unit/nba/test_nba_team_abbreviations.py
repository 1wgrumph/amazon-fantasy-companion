"""Yahoo/ESPN NBA team-abbreviation matching (issue #137).

ESPN abbreviations were read from the public teams endpoint on 2026-10-20:
GS, NO, NY, SA, UTAH, WSH (and LAL, which matches Yahoo). The fixture is
synthetic. map_starters keeps the Yahoo team code and adds the ESPN athlete.
"""

import json
from pathlib import Path


FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "nba" / "yahoo" / "abbrev_roster.json"
PAIRS = {
    "nba.p.6101": "9100101",  # GSW -> GS
    "nba.p.6102": "9100102",  # NOP -> NO
    "nba.p.6103": "9100103",  # NYK -> NY
    "nba.p.6104": "9100104",  # SAS -> SA
    "nba.p.6105": "9100105",  # UTA -> UTAH
    "nba.p.6106": "9100106",  # WAS -> WSH
    "nba.p.6107": "9100107",  # LAL == LAL
    "nba.p.6108": None,       # Sample Warrior on NOP is not the GS athlete
}


def test_map_starters_normalizes_yahoo_team_abbreviations_to_espn():
    from nba.yahoo import map_starters

    body = json.loads(FIXTURE.read_text())
    mapped = map_starters(body["yahoo"], body["espn"])
    assert [row["player_key"] for row in mapped] == list(PAIRS)
    assert [row.get("athlete_id") for row in mapped] == list(PAIRS.values())
    assert mapped[0]["team"] == "GSW"
    assert mapped[1]["team"] == "NOP"
