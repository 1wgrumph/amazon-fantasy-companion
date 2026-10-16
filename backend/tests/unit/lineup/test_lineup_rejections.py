"""P2-B03 extra rejection coverage: untrusted Yahoo payloads, manual input, stored rows."""

from decimal import Decimal

import pytest

import lineup
from lineup import manual, yahoo

TEAM_KEY = "nfl.l.1001.t.1"
LEAGUE_KEY = "nfl.l.1001"
ROSTER = [{"athlete_id": "espn.1", "name": "Sample Quarterback", "team": "SYN"},
          {"athlete_id": "espn.2", "name": "Sample Runner", "team": "SYN"}]


class Fixed:
    def __init__(self, payload):
        self.payload, self.calls = payload, []

    def request(self, method, url, headers=None):
        self.calls.append(url)
        return self.payload


PLAYER = {"player_key": "nfl.p.1", "name": "P", "team": "SYN", "positions": ["QB"], "slot": "QB"}


@pytest.mark.parametrize("key", ["", "nfl.l.1/../x", None, "a" * 65])
def test_bad_keys_are_rejected_before_any_request(key):
    transport = Fixed({})
    with pytest.raises(ValueError):
        yahoo.get_teams(transport, "tok", key)
    with pytest.raises(ValueError):
        yahoo.get_roster(transport, "tok", key, 5)
    assert transport.calls == []


@pytest.mark.parametrize("week", [0, -1, True])
def test_non_positive_or_bool_week_is_rejected(week):
    with pytest.raises(ValueError):
        yahoo.get_roster(Fixed({}), "tok", TEAM_KEY, week)


@pytest.mark.parametrize("payload", [
    {"team_key": "nfl.l.9.t.9", "week": 5, "players": [PLAYER]},
    {"team_key": TEAM_KEY, "week": 6, "players": [PLAYER]},
    {"team_key": TEAM_KEY, "week": 5, "players": [dict(PLAYER, positions=["QB", 1])]},
    {"team_key": TEAM_KEY, "week": 5, "players": [dict(PLAYER, name=True)]},
])
def test_roster_payload_mismatch_or_bad_types_is_rejected(payload):
    with pytest.raises(ValueError):
        yahoo.get_roster(Fixed(payload), "tok", TEAM_KEY, 5)


def test_roster_at_the_size_bound_is_accepted():
    players = [dict(PLAYER, player_key=f"nfl.p.{i}", slot="BN") for i in range(yahoo.MAX_ITEMS)]
    roster = yahoo.get_roster(Fixed({"team_key": TEAM_KEY, "week": 5, "players": players}),
                              "tok", TEAM_KEY, 5)
    assert len(roster["bench"]) == yahoo.MAX_ITEMS and roster["starters"] == []


@pytest.mark.parametrize("payload", [
    {"league_key": "nfl.l.2", "stat_modifiers": {}, "roster_slots": []},
    {"league_key": LEAGUE_KEY, "stat_modifiers": {"receptions": True}, "roster_slots": []},
    {"league_key": LEAGUE_KEY, "stat_modifiers": {"receptions": "1"}, "roster_slots": []},
    {"league_key": LEAGUE_KEY, "stat_modifiers": {}},
    {"league_key": LEAGUE_KEY, "stat_modifiers": {}, "roster_slots": ["QB", 2]},
    {"league_key": LEAGUE_KEY, "stat_modifiers": {}, "roster_slots": ["BN"] * 201},
])
def test_settings_with_bad_shapes_are_rejected(payload):
    with pytest.raises(ValueError):
        yahoo.get_settings(Fixed(payload), "tok", LEAGUE_KEY)


@pytest.mark.parametrize("payload", [{"leagues": "x"}, {"leagues": [{"league_key": "k"}]},
                                     {"leagues": [{"league_key": "k", "name": "n", "season": "2026"}]}])
def test_leagues_with_bad_shapes_are_rejected(payload):
    with pytest.raises(ValueError):
        yahoo.get_leagues(Fixed(payload), "tok")


def test_non_string_timestamp_is_rejected():
    with pytest.raises(ValueError):
        manual.activation(1760641200, False)


@pytest.mark.parametrize("approved", [None, 1, "yes"])
def test_non_boolean_approval_is_rejected(approved):
    with pytest.raises(ValueError):
        manual.activation(manual.T_YAHOO, approved)


@pytest.mark.parametrize(("roster", "entries"), [
    ("not-a-list", [{"athlete_id": "espn.1", "slot": "QB"}]),
    ([{"athlete_id": "", "name": "Empty"}], []),
    ([{"athlete_id": "espn.1", "name": 7}], []),
    (ROSTER, "not-a-list"),
    (ROSTER, [{"athlete_id": "espn.1"}]),
    (ROSTER, [{"athlete_id": "espn.1", "slot": ""}]),
    (ROSTER, ["espn.1"]),
    (ROSTER, [{"athlete_id": "espn.1", "slot": "QB"}, {"athlete_id": "espn.1", "slot": "FLEX"}]),
    (ROSTER, [{"athlete_id": "espn.2", "slot": "RB"}] * (manual.MAX_ENTRIES + 1)),
])
def test_manual_build_rejects_malformed_input(roster, entries):
    with pytest.raises(ValueError):
        manual.build(roster, entries, "PPR")


def test_manual_build_keeps_entry_order_and_roster_names():
    entries = [{"athlete_id": "espn.2", "slot": "RB"}, {"athlete_id": "espn.1", "slot": "QB"}]
    built = manual.build(ROSTER, entries, "PPR")
    assert built["starters"] == [{"athlete_id": "espn.2", "name": "Sample Runner", "team": "SYN", "slot": "RB"},
                                 {"athlete_id": "espn.1", "name": "Sample Quarterback", "team": "SYN", "slot": "QB"}]


@pytest.mark.parametrize("profile_id", ["", None, 7])
def test_active_lineup_rejects_a_bad_profile_id(profile_id):
    with pytest.raises(ValueError):
        lineup.active_lineup(profile_id)


def test_stored_yahoo_row_without_scoring_is_rejected(api):
    import store
    store.put_lineup({"profileId": "owner", "source": "yahoo", "team": "T", "league": "L",
                      "starters": [], "updatedAt": "2026-10-14T12:00:00Z"})
    with pytest.raises(ValueError):
        lineup.active_lineup("owner")


def test_profile_without_a_preset_setting_defaults_to_half_ppr(api):
    import store
    store.put_profile("owner", {"excitement": "mild"}, 0, "2026-10-14T12:00:00Z")
    store.put_lineup({"profileId": "owner", "source": "manual", "team": "T", "league": "L",
                      "starters": [], "updatedAt": "2026-10-14T12:00:00Z",
                      "scoring": {"ignored": Decimal("1")}})
    assert lineup.active_lineup("owner")["scoring"] == {"preset": "Half-PPR"}


@pytest.mark.parametrize("module", ["lineup.presets", "lineup.manual", "lineup.yahoo"])
def test_unknown_module_attributes_still_raise_attribute_error(module):
    import importlib
    with pytest.raises(AttributeError):
        importlib.import_module(module).NOT_A_CONSTANT


def test_module_constants_keep_their_values():
    from lineup import presets
    assert presets.DEFAULT_PRESET in presets.TABLES
    assert manual.T_YAHOO == "2026-10-16T19:00:00Z" and manual.MAX_ENTRIES == 200
    assert yahoo.MAX_ITEMS == 200
