"""One active source red tests (VCASE-AFC-PR-007, VCASE-AFC-PR-065 resolution).

active_lineup returns the profile's one active Lineup: stored Yahoo rows use
Yahoo league scoring, stored manual rows use the profile preset (default
Half-PPR). Setup without a stored lineup is None, never a second source.
"""

from decimal import Decimal

import pytest

from lineup_support import attempt, require_module

PROFILE = "owner"
MANUAL_STARTERS = [
    {"athlete_id": "espn.1", "name": "Sample Quarterback", "slot": "QB"},
    {"athlete_id": "espn.2", "name": "Sample Runner", "slot": "RB"},
]
YAHOO_STARTERS = [
    {"player_key": "nfl.p.5001", "name": "Sample Quarterback", "slot": "QB"},
    {"player_key": "nfl.p.5002", "name": "Sample Runner One", "slot": "RB"},
]
YAHOO_SCORING = {"league_key": "nfl.l.1001",
                 "stat_modifiers": {"receptions": Decimal("1.0"), "passing_yards": Decimal("0.04")}}


def seed_lineup(source, starters, scoring=None, team="Red Testers", league="Red League Alpha"):
    import store
    row = {"profileId": PROFILE, "source": source, "team": team, "league": league,
           "starters": starters, "updatedAt": "2026-10-14T12:00:00Z"}
    if scoring is not None:
        row["scoring"] = scoring
    store.put_lineup(row)


def seed_profile(settings):
    import store
    store.put_profile(PROFILE, settings, 0, "2026-10-14T12:00:00Z")


def active():
    return attempt(require_module("lineup").active_lineup, PROFILE)


def test_no_stored_lineup_returns_none(api):
    assert active() is None


def test_profile_without_a_lineup_is_not_a_source(api):
    seed_profile({"scoringPreset": "ppr"})
    assert active() is None


def test_manual_lineup_defaults_to_half_ppr(api):
    seed_lineup("manual", MANUAL_STARTERS)
    lineup = active()
    assert lineup["source"] == "manual"
    assert lineup["scoring"] == {"preset": "Half-PPR"}
    assert lineup["starters"] == MANUAL_STARTERS
    assert (lineup["team"], lineup["league"]) == ("Red Testers", "Red League Alpha")


@pytest.mark.parametrize(("stored", "label"), [("ppr", "PPR"), ("halfPpr", "Half-PPR")])
def test_manual_lineup_uses_the_profile_preset(api, stored, label):
    seed_profile({"scoringPreset": stored})
    seed_lineup("manual", MANUAL_STARTERS)
    lineup = active()
    assert lineup["source"] == "manual"
    assert lineup["scoring"] == {"preset": label}


def test_manual_lineup_rejects_an_unknown_stored_preset(api):
    seed_profile({"scoringPreset": "standard"})
    seed_lineup("manual", MANUAL_STARTERS)
    with pytest.raises(ValueError):
        active()


def test_yahoo_lineup_uses_yahoo_league_scoring(api):
    seed_lineup("yahoo", YAHOO_STARTERS, scoring=YAHOO_SCORING)
    lineup = active()
    assert lineup["source"] == "yahoo"
    assert lineup["scoring"] == YAHOO_SCORING
    assert "preset" not in lineup["scoring"]
    assert lineup["starters"] == YAHOO_STARTERS


def test_yahoo_lineup_ignores_the_profile_preset(api):
    seed_profile({"scoringPreset": "ppr"})
    seed_lineup("yahoo", YAHOO_STARTERS, scoring=YAHOO_SCORING)
    lineup = active()
    assert lineup["source"] == "yahoo"
    assert lineup["scoring"] == YAHOO_SCORING
    assert "preset" not in lineup["scoring"]


def test_an_unknown_stored_source_is_rejected(api):
    seed_lineup("espn", MANUAL_STARTERS)
    with pytest.raises(ValueError):
        active()


def test_source_switch_keeps_exactly_one_active(api):
    seed_lineup("manual", MANUAL_STARTERS)
    assert active()["source"] == "manual"
    assert active()["source"] == "manual"
    seed_lineup("yahoo", YAHOO_STARTERS, scoring=YAHOO_SCORING)
    assert active()["source"] == "yahoo"
    assert active()["source"] == "yahoo"
    seed_lineup("manual", MANUAL_STARTERS)
    assert active()["source"] == "manual"


def test_last_writer_wins_without_duplication(api):
    seed_lineup("manual", MANUAL_STARTERS)
    other = [{"athlete_id": "espn.3", "name": "Sample Catcher", "slot": "WR"}]
    seed_lineup("manual", other)
    lineup = active()
    assert isinstance(lineup, dict)
    assert lineup["source"] == "manual"
    assert lineup["starters"] == other
