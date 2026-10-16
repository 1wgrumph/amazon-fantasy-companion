"""Cross-provider identity red tests (VCASE-AFC-PR-024; DES-AFC-P2-MATCH).

The canonical player id is the ESPN athlete id. Manual starters carry it;
Yahoo starters map by name + team + position through the explicit mapping
table. One entity never splits into two identities and distinct entities
never merge; an unmatched or ambiguous player is left unmatched, not guessed.
"""

import json
from pathlib import Path

from matcher_support import (MANUAL_PASSER, MANUAL_RECEIVER, YAHOO_PASSER,  # noqa: F401
                             YAHOO_RECEIVER, YAHOO_TWIN, athlete_ids, for_profile,
                             game_event, match_env, require_module, seed_lineup)

BACKEND = Path(__file__).resolve().parents[3]


def test_manual_starter_resolves_by_espn_athlete_id(match_env):
    seed_lineup("manual-fan", "manual", [MANUAL_RECEIVER])
    matches = match_env.resolve(game_event("401999001101", ["9000001"]))
    assert [m["profileId"] for m in matches] == ["manual-fan"]
    assert athlete_ids(matches[0]) == {"9000001"}


def test_yahoo_starter_resolves_to_its_espn_athlete_id(match_env):
    seed_lineup("yahoo-fan", "yahoo", [YAHOO_RECEIVER])
    matches = match_env.resolve(game_event("401999001102", ["9000001"]))
    assert [m["profileId"] for m in matches] == ["yahoo-fan"]
    assert athlete_ids(matches[0]) == {"9000001"}


def test_same_player_across_providers_is_one_identity(match_env):
    seed_lineup("yahoo-fan", "yahoo", [YAHOO_RECEIVER])
    seed_lineup("manual-fan", "manual", [MANUAL_RECEIVER])
    matches = match_env.resolve(game_event("401999001103", ["9000001"]))
    assert sorted(m["profileId"] for m in matches) == ["manual-fan", "yahoo-fan"]
    assert [athlete_ids(m) for m in matches] == [{"9000001"}, {"9000001"}]


def test_same_name_on_another_team_is_a_distinct_player(match_env):
    seed_lineup("yahoo-fan", "yahoo", [YAHOO_RECEIVER])
    # 9000002 is the DAL "Sample Receiver"; the Yahoo starter plays for PHI.
    assert match_env.resolve(game_event("401999001104", ["9000002"])) == []


def test_position_mismatch_is_not_matched(match_env):
    misplaced = dict(YAHOO_RECEIVER, positions=["TE"], slot="TE")
    seed_lineup("yahoo-fan", "yahoo", [misplaced])
    assert match_env.resolve(game_event("401999001105", ["9000001"])) == []


def test_ambiguous_mapping_is_unmatched_not_guessed(match_env):
    seed_lineup("yahoo-fan", "yahoo", [YAHOO_TWIN])
    # Two mapping entries share name, team and position: neither may be guessed.
    for event_id, athlete in (("401999001106", "9000003"), ("401999001107", "9000004")):
        assert match_env.resolve(game_event(event_id, [athlete])) == [], athlete


def test_unmapped_yahoo_starter_is_unmatched(match_env):
    unknown = {"player_key": "nfl.p.7999", "name": "Unlisted Kicker", "team": "PHI",
               "positions": ["K"], "slot": "K"}
    seed_lineup("yahoo-fan", "yahoo", [unknown, YAHOO_PASSER])
    matches = match_env.resolve(game_event("401999001108", ["9000005", "9000099"]))
    assert [m["profileId"] for m in matches] == ["yahoo-fan"]
    assert athlete_ids(matches[0]) == {"9000005"}


def test_event_without_starters_matches_no_profile(match_env):
    seed_lineup("manual-fan", "manual", [MANUAL_RECEIVER])
    seed_lineup("yahoo-fan", "yahoo", [YAHOO_RECEIVER])
    assert match_env.resolve(game_event("401999001109", ["9000077"])) == []


def test_only_concerned_profiles_match(match_env):
    seed_lineup("receiver-fan", "manual", [MANUAL_RECEIVER])
    seed_lineup("passer-fan", "manual", [MANUAL_PASSER])
    matches = match_env.resolve(game_event("401999001110", ["9000005"]))
    assert [m["profileId"] for m in matches] == ["passer-fan"]
    assert for_profile(matches, "receiver-fan") == []


def test_landed_player_map_is_the_default_table(api):
    module = require_module("matcher")
    default = getattr(module, "PLAYER_MAP_PATH", None)
    assert default is not None, "matcher.PLAYER_MAP_PATH must name the mapping table"
    landed = BACKEND / "src" / "matcher" / "player_map.json"
    assert Path(default).resolve() == landed.resolve()
    assert landed.is_file(), "the landed mapping table must exist"
    document = json.loads(landed.read_text())
    assert document.get("schemaVersion") == 1
    assert isinstance(document.get("players"), list)
