"""F5: manual team identity follows the ESPN roster, with shape-only validation.

Input: committed PHI capture and the owner team-shape contract. No shared resources.
"""

import json
from pathlib import Path

import pytest

from lineup import manual


def captured_roster():
    path = Path(__file__).resolve().parents[3] / "fixtures/replay/401872981/001-summary.json"
    summary = json.loads(path.read_text())
    team = next(t for t in summary["boxscore"]["players"]
                if t["team"]["abbreviation"] == "PHI")
    athlete = next(a["athlete"] for stat in team["statistics"]
                   for a in stat.get("athletes", []) if a["athlete"]["id"] == "4715355")
    return [{"athlete_id": athlete["id"], "name": athlete["displayName"],
             "team": team["team"]["abbreviation"]}]


def test_manual_retains_team_from_roster_instead_of_untrusted_selection():
    roster = captured_roster()
    built = manual.build(roster, [{"athlete_id": roster[0]["athlete_id"],
                                   "slot": "FLEX", "team": "DAL"}], "PPR")
    assert built["starters"] == [{**roster[0], "slot": "FLEX"}]


@pytest.mark.parametrize("team", ["PHI", "SYN", "12", "A1B2"])
def test_manual_accepts_team_shape_without_nfl_membership_check(team):
    roster = captured_roster()
    roster[0]["team"] = team
    built = manual.build(roster, [{"athlete_id": roster[0]["athlete_id"], "slot": "FLEX"}], "PPR")
    assert built["starters"][0]["team"] == team


@pytest.mark.parametrize("team", [None, 1, True, [], {}, "", "P", "ABCDE", "phi", "PH-", " PHI", "PHI\n", "ÄBC"])
def test_manual_rejects_invalid_roster_team(team):
    roster = captured_roster()
    roster[0]["team"] = team
    with pytest.raises(ValueError, match="team"):
        manual.build(roster, [{"athlete_id": roster[0]["athlete_id"], "slot": "FLEX"}], "PPR")


def test_manual_rejects_missing_roster_team():
    roster = captured_roster()
    del roster[0]["team"]
    with pytest.raises(ValueError, match="team"):
        manual.build(roster, [{"athlete_id": roster[0]["athlete_id"], "slot": "FLEX"}], "PPR")
