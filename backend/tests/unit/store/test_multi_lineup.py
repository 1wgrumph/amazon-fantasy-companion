"""One profile holds every lineup at once, one per "<league>/<team>" pair.

Approved design: recovery-m03-m05/multisport/arch-review.md (sections 2, 3, 7).
The Lineups row keeps one profileId key and one row-level lineupVersion and
holds a `lineups` map keyed by pair. A legacy top-level row reads as one
lineup and migrates on the next write. A PUT for one pair leaves every other
pair byte-equal.

Intended API (does not exist on a22031f):
- store.get_lineups(profile_id) -> ({"<league>/<team>": lineup}, lineupVersion),
  one consistent read.
- store.get_lineup(profile_id) with one stored lineup still returns it.
"""

import re

import store
from conftest import link_device

WHEN = "2026-10-22T18:00:00Z"
NFL_LEAGUE, NFL_TEAM = "league-a", "team-7"
NBA_LEAGUE, NBA_TEAM = "nba-demo", "afc-nba"
NFL_PAIR, NBA_PAIR = f"{NFL_LEAGUE}/{NFL_TEAM}", f"{NBA_LEAGUE}/{NBA_TEAM}"
# Synthetic ESPN identities; names belong to no real athlete.
RECEIVER = {"athlete_id": "9000001", "name": "Sample Receiver", "team": "PHI", "slot": "WR"}
RUNNER = {"athlete_id": "9000002", "name": "Sample Runner", "team": "PHI", "slot": "RB"}
GUARD = {"athlete_id": "9100001", "name": "Sample Guard", "team": "SHO", "slot": "PG"}
CENTER = {"athlete_id": "9100003", "name": "Sample Center", "team": "SHO", "slot": "C"}


def nfl(starters=(RECEIVER,), profile_id="fan"):
    return {"profileId": profile_id, "source": "manual", "league": NFL_LEAGUE,
            "team": NFL_TEAM, "starters": [dict(s) for s in starters], "updatedAt": WHEN}


def nba(starters=(GUARD,), profile_id="fan"):
    return {"profileId": profile_id, "source": "manual", "sport": "nba", "league": NBA_LEAGUE,
            "team": NBA_TEAM, "starters": [dict(s) for s in starters], "updatedAt": WHEN}


def raw(api, profile_id="fan"):
    return api.table("Lineups").get_item(Key={"profileId": profile_id},
                                         ConsistentRead=True).get("Item")


def stored_pairs(item):
    """Pair -> lineup content as stored: the `lineups` map, or a legacy top-level row."""
    if not item:
        return {}
    if "lineups" in item:
        return item["lineups"]
    if item.get("league") and item.get("team"):
        return {f"{item['league']}/{item['team']}": {
            k: v for k, v in item.items() if k not in ("profileId", "lineupVersion")}}
    return {}


def get_lineups(profile_id="fan"):
    # Intended API: store.get_lineups(profile_id) -> (lineups by pair, lineupVersion).
    get = getattr(store, "get_lineups", None)
    assert get is not None, "store.get_lineups(profile_id) is not implemented"
    return get(profile_id)


def content(lineup):
    return {k: lineup.get(k) for k in ("source", "sport", "league", "team", "starters")}


def test_put_nfl_then_nba_keeps_both_and_nfl_byte_equal(api):
    store.put_lineup(nfl())
    nfl_before = stored_pairs(raw(api))[NFL_PAIR]
    store.put_lineup(nba())
    pairs = stored_pairs(raw(api))
    assert NFL_PAIR in pairs, f"the NBA PUT erased the NFL lineup: stored pairs {sorted(pairs)}"
    assert pairs[NFL_PAIR] == nfl_before, "an NBA PUT must leave the NFL lineup byte-equal"
    assert sorted(pairs) == sorted([NFL_PAIR, NBA_PAIR])
    lineups, version = get_lineups()
    assert sorted(lineups) == sorted([NFL_PAIR, NBA_PAIR])
    assert content(lineups[NFL_PAIR]) == content(nfl())
    assert content(lineups[NBA_PAIR]) == content(nba())
    assert version == 2


def test_re_put_nba_leaves_nfl_untouched_and_bumps_version_by_one(api):
    store.put_lineup(nfl())
    store.put_lineup(nba())
    before = raw(api)
    nfl_before = stored_pairs(before).get(NFL_PAIR)
    assert nfl_before is not None, "the NBA PUT erased the NFL lineup"
    store.put_lineup(nba([GUARD, CENTER]))
    after = raw(api)
    assert stored_pairs(after).get(NFL_PAIR) == nfl_before, "re-PUT NBA changed the NFL lineup"
    assert int(after["lineupVersion"]) == int(before["lineupVersion"]) + 1
    store.put_lineup(nba([GUARD, CENTER]))
    assert int(raw(api)["lineupVersion"]) == int(after["lineupVersion"]), \
        "an identical re-PUT is not a content change"
    lineups, version = get_lineups()
    assert [s["athlete_id"] for s in lineups[NBA_PAIR]["starters"]] == ["9100001", "9100003"]
    assert version == int(after["lineupVersion"])


def test_legacy_row_reads_as_one_lineup_and_next_write_keeps_both(api):
    legacy = dict(nfl(), lineupVersion=3)
    api.table("Lineups").put_item(Item=legacy)
    expected = {k: v for k, v in legacy.items() if k != "lineupVersion"}
    assert store.get_lineup("fan") == expected, "a legacy row must still read through get_lineup"
    store.put_lineup(nba())
    pairs = stored_pairs(raw(api))
    assert NFL_PAIR in pairs, f"migrating a legacy row dropped its NFL lineup: {sorted(pairs)}"
    assert content(pairs[NFL_PAIR]) == content(legacy)
    assert int(raw(api)["lineupVersion"]) == 4
    lineups, version = get_lineups()
    assert sorted(lineups) == sorted([NFL_PAIR, NBA_PAIR])
    assert version == 4


def test_legacy_row_reads_through_get_lineups_as_its_one_pair(api):
    api.table("Lineups").put_item(Item=dict(nfl(), lineupVersion=3))
    lineups, version = get_lineups()
    assert list(lineups) == [NFL_PAIR]
    assert content(lineups[NFL_PAIR]) == content(nfl())
    assert version == 3


def test_monitoring_profiles_returns_the_union_of_starters(api):
    assert store.put_profile("fan", {}, 0, WHEN)
    store.put_lineup(nfl([RECEIVER]))
    store.put_lineup(nba([GUARD]))
    profiles = store.monitoring_profiles()
    assert len(profiles) == 1, profiles
    ids = sorted(s["athlete_id"] for s in profiles[0]["starters"])
    assert ids == ["9000001", "9100001"], f"starters must span every lineup, got {ids}"


def test_nfl_unchanged_legacy_row_through_manual_put_panel_and_matcher(api):
    """Passes on a22031f and must still pass after: same outputs for an NFL-only profile."""
    import matcher
    import panel

    _, token = link_device(api)
    api.table("Lineups").put_item(Item=dict(nfl(profile_id="owner"), lineupVersion=2))

    status, before = api.request("GET", "/v1/panel", token=token)
    assert status == 200, before
    assert before["data"]["teamLeague"] == NFL_PAIR
    assert [r["playerId"] for r in before["data"]["rows"]] == ["9000001"]

    status, put = api.request("PUT", "/v1/lineup/manual", {
        "league": NFL_LEAGUE, "team": NFL_TEAM, "preset": "Half-PPR",
        "roster": [{k: s[k] for k in ("athlete_id", "name", "team")} for s in (RECEIVER, RUNNER)],
        "entries": [{"athlete_id": "9000001", "slot": "WR"},
                    {"athlete_id": "9000002", "slot": "RB"}]}, token=token)
    assert status == 200, put
    assert put["id"] == "owner" and put["source"] == "manual" and put["revision"] == 3
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", put["updatedAt"])
    assert put["data"] == {"label": "Manual lineup", "source": "manual",
                           "starters": [RECEIVER, RUNNER], "scoring": {"preset": "Half-PPR"}}
    assert store.get_lineup("owner")["starters"] == [RECEIVER, RUNNER]

    event = {"gameId": "401999001", "eventId": "401999001201", "revision": 1,
             "correctionOf": None, "source": "live", "score": {"away": 7, "home": 3},
             "fieldPosition": 35, "possession": "PHI", "playerIds": ["9000002"],
             "eventTime": WHEN, "period": 2, "scoringPlay": True}
    store.put_event(event)
    matches = matcher.resolve(event)
    assert matches == [{"profileId": "owner", "eventId": "401999001201", "revision": 1,
                        "starters": [RUNNER], "cursor": None}]
    panel.project(event, matches)
    assert [p["teamLeague"] for p in api.table("Panels").scan()["Items"]] == [NFL_PAIR]

    status, after = api.request("GET", "/v1/panel", token=token,
                                query={"teamLeague": NFL_PAIR})
    assert status == 200, after
    data = after["data"]
    assert after["id"] == f"panel/owner/{NFL_PAIR}" and after["source"] == "manual"
    assert after["revision"] > before["revision"]
    assert data["teamLeague"] == NFL_PAIR and data["scoringBasis"] == "halfPpr"
    assert "sport" not in data
    assert [(r["playerId"], r["name"]) for r in data["rows"]] == [
        ("9000001", "Sample Receiver"), ("9000002", "Sample Runner")]
    assert data["teamTotal"]["value"] is None
    assert data["games"] == {"401999001": {"eventId": "401999001201", "revision": 1,
                                           "score": {"away": 7, "home": 3}, "source": "live"}}
