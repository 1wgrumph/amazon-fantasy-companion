"""Labeled manual entry red tests (VCASE-AFC-PR-006).

Without Yahoo approval at T_yahoo the backend accepts manual lineups built
from ESPN rosters as the active source, always labeled manual and never
presented as Yahoo values.
"""

import pytest

from lineup_support import attempt, require_module

T_YAHOO = "2026-10-16T19:00:00Z"
ROSTER = [
    {"athlete_id": "espn.1", "name": "Sample Quarterback", "team": "SYN", "positions": ["QB"]},
    {"athlete_id": "espn.2", "name": "Sample Runner", "team": "SYN", "positions": ["RB"]},
    {"athlete_id": "espn.3", "name": "Sample Catcher", "team": "SYN", "positions": ["WR"]},
]
ENTRIES = [
    {"athlete_id": "espn.1", "slot": "QB"},
    {"athlete_id": "espn.2", "slot": "RB"},
    {"athlete_id": "espn.3", "slot": "WR"},
]


def manual():
    return require_module("lineup.manual")


def test_t_yahoo_constant_matches_the_plan():
    assert attempt(lambda: manual().T_YAHOO) == T_YAHOO


@pytest.mark.parametrize("now", ["2026-10-16T18:59:59Z", "2026-10-01T00:00:00Z"])
def test_activation_before_t_yahoo_is_pending(now):
    assert attempt(manual().activation, now, False) == "pending"


def test_activation_at_t_yahoo_without_approval_is_manual():
    assert attempt(manual().activation, T_YAHOO, False) == "manual"


@pytest.mark.parametrize("now", ["2026-10-16T19:00:01Z", "2026-10-20T00:00:00Z"])
def test_activation_after_t_yahoo_without_approval_is_manual(now):
    assert attempt(manual().activation, now, False) == "manual"


@pytest.mark.parametrize("now", [T_YAHOO, "2026-10-16T18:59:59Z", "2026-10-16T19:00:01Z"])
def test_approved_yahoo_stays_yahoo_across_t_yahoo(now):
    assert attempt(manual().activation, now, True) == "yahoo"


@pytest.mark.parametrize("now", ["not-a-time", "", "2026-13-45T99:99:99Z"])
def test_malformed_timestamp_is_rejected(now):
    with pytest.raises(ValueError):
        attempt(manual().activation, now, False)


def test_build_labels_the_entry_manual_with_its_preset():
    lineup = attempt(manual().build, ROSTER, ENTRIES, "Half-PPR")
    assert lineup["source"] == "manual"
    assert lineup["scoring"] == {"preset": "Half-PPR"}
    assert [(s["athlete_id"], s["name"], s["slot"]) for s in lineup["starters"]] == [
        ("espn.1", "Sample Quarterback", "QB"), ("espn.2", "Sample Runner", "RB"),
        ("espn.3", "Sample Catcher", "WR")]


def test_build_applies_the_selected_preset():
    lineup = attempt(manual().build, ROSTER, ENTRIES, "PPR")
    assert lineup["scoring"] == {"preset": "PPR"}


def test_build_rejects_an_unknown_preset():
    with pytest.raises(ValueError):
        attempt(manual().build, ROSTER, ENTRIES, "Standard")


def test_build_rejects_players_outside_the_espn_roster():
    entries = ENTRIES + [{"athlete_id": "espn.404", "slot": "FLEX"}]
    with pytest.raises(ValueError):
        attempt(manual().build, ROSTER, entries, "Half-PPR")


def test_build_rejects_a_malformed_espn_roster():
    roster = [{"name": "Nameless Entry", "team": "SYN", "positions": ["QB"]}]
    with pytest.raises(ValueError):
        attempt(manual().build, roster, ENTRIES, "Half-PPR")


def test_manual_values_are_never_presented_as_yahoo():
    lineup = attempt(manual().build, ROSTER, ENTRIES, "Half-PPR")
    assert lineup["source"] == "manual"

    def walk(value):
        if isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
        elif isinstance(value, str):
            assert value != "yahoo", "manual lineup carries a Yahoo value"

    walk(lineup)
