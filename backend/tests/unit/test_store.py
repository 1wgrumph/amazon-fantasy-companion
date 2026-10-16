"""DES-AFC-P2-BACKEND store accessors against fresh in-process Moto tables (host-pytest)."""

import pytest
from botocore.exceptions import ClientError


@pytest.fixture
def store(api):
    import store as module
    return module


def test_profile_writes_require_the_current_revision(store):
    first = store.put_profile("owner", {"scoringPreset": "ppr"}, 0, "2026-10-14T00:00:00Z")
    assert first == {"profileId": "owner", "settings": {"scoringPreset": "ppr"}, "revision": 1,
                     "updatedAt": "2026-10-14T00:00:00Z"}
    assert store.put_profile("owner", {"voice": "x"}, 0, "t") is None
    assert store.put_profile("owner", {"voice": "x"}, 2, "t") is None
    assert store.put_profile("owner", {"voice": "x"}, 1, "t2")["revision"] == 2
    stored = store.get_profile("owner")
    assert stored["revision"] == 2 and stored["settings"] == {"voice": "x"} and stored["updatedAt"] == "t2"
    assert store.get_profile("nobody") is None


def test_link_codes_confirm_once_complete_once_and_respect_expiry(store):
    assert store.put_link("ABCD2345", "hash-1", 100) is True
    assert store.put_link("ABCD2345", "hash-2", 100) is False
    link = store.find_link("hash-1")
    assert link == {"pk": "code#ABCD2345", "code": "ABCD2345", "handleHash": "hash-1",
                    "state": "codePending", "expiresAt": 100}
    assert store.find_link("hash-unknown") is None
    assert store.complete_link("ABCD2345") is False, "Only a confirmed code completes"
    assert store.confirm_link("ABCD2345", "owner", 99) is True
    assert store.find_link("hash-1")["state"] == "confirmed"
    assert store.find_link("hash-1")["profileId"] == "owner"
    assert store.confirm_link("ABCD2345", "foreign", 99) is False
    assert store.complete_link("ABCD2345") is True
    assert store.find_link("hash-1")["state"] == "linked"
    assert store.complete_link("ABCD2345") is False
    assert store.put_link("EFGH6789", "hash-3", 100) is True
    assert store.confirm_link("EFGH6789", "owner", 100) is False, "Expiry is exclusive"
    assert store.confirm_link("UNKNOWN2", "owner", 1) is False


def test_sessions_are_keyed_by_hash(store):
    store.put_session("session-hash", "owner", "2026-10-14T00:00:00Z")
    assert store.get_session("session-hash") == {
        "pk": "session#session-hash", "sessionHash": "session-hash", "profileId": "owner",
        "linkedAt": "2026-10-14T00:00:00Z"}
    assert store.get_session("other") is None


def test_events_keep_the_game_event_shape(store):
    event = {"gameId": "g1", "eventId": "e1", "revision": 2, "source": "live", "score": "7-3",
             "fieldPosition": "OPP 12", "possession": "KC", "playerIds": "1,2",
             "eventTime": "2026-10-14T01:00:00Z", "correctionOf": "e0"}
    store.put_event(event)
    assert store.get_event("g1", "e1") == event
    assert store.get_event("g1", "e2") is None
    with pytest.raises(ValueError) as error:
        store.put_event({"gameId": "g1", "eventId": "e3", "zz": 1, "bogus": 2})
    assert str(error.value) == "Unknown item attributes: bogus, zz"
    assert store.get_event("g1", "e3") is None


def test_alerts_page_by_cursor_per_profile(store):
    for cursor in ["c", "a", "b"]:
        store.put_alert({"profileId": "owner", "cursor": cursor, "eventId": "e" + cursor,
                         "revision": 1, "alertType": "redZone", "triggerContext": "t",
                         "providerRoute": "r", "commentary": "m", "emittedAt": "x"})
    store.put_alert({"profileId": "other", "cursor": "a"})
    assert [a["cursor"] for a in store.list_alerts("owner", None, 10)] == ["a", "b", "c"]
    assert [a["cursor"] for a in store.list_alerts("owner", "a", 10)] == ["b", "c"]
    assert [a["cursor"] for a in store.list_alerts("owner", None, 1)] == ["a"]
    assert store.list_alerts("owner", "c", 10) == []
    assert store.list_alerts("owner", None, 10)[0]["alertType"] == "redZone"
    with pytest.raises(ValueError):
        store.put_alert({"profileId": "owner", "cursor": "d", "unknown": 1})


def test_lineups_and_panels_keep_their_shapes(store):
    lineup = {"profileId": "owner", "source": "manual", "team": "T", "league": "L",
              "starters": ["1"], "scoring": "halfPpr", "updatedAt": "u"}
    store.put_lineup(lineup)
    assert store.get_lineup("owner") == lineup
    assert store.get_lineup("other") is None
    panel = {"profileId": "owner", "teamLeague": "T/L", "visible": True, "teamTotal": "12.5",
             "progress": "50%", "freshness": "live", "rows": [], "updatedAt": "u"}
    store.put_panel(panel)
    assert store.get_panel("owner", "T/L") == panel
    assert store.get_panel("owner", "X/L") is None
    with pytest.raises(ValueError):
        store.put_lineup({"profileId": "owner", "extra": 1})
    with pytest.raises(ValueError):
        store.put_panel({"profileId": "owner", "teamLeague": "T/L", "extra": 1})


def test_only_conditional_failures_become_false(store):
    def fail(code):
        def write(**request):
            raise ClientError({"Error": {"Code": code, "Message": "m"}}, "PutItem")
        return write

    assert store._written(fail("ConditionalCheckFailedException"), Item={}) is False
    with pytest.raises(ClientError):
        store._written(fail("ProvisionedThroughputExceededException"), Item={})
