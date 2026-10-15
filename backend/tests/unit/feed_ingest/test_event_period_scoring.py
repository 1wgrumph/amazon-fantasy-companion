"""DEC-AFC-SD-067: ESPN period/scoring facts survive validation and storage.

Offline captured summaries and fresh per-test Moto tables; no shared resource.
Malformed and correction variants change only the contract field under test.
"""

import pytest

from feed_support import GAME, fresh_summary, plays_in


@pytest.mark.parametrize("game,kind", [
    (GAME, "q4"), ("401872988", "ot"),
    (GAME, "touchdown"), (GAME, "non-scoring"),
])
def test_captured_period_and_scoring_are_stored(api, game, kind):
    import store
    from feed_ingest.ingest import ingest_summary

    summary = fresh_summary(game)
    plays = plays_in(summary)
    selected = {
        "q4": lambda p: p["period"]["number"] == 4,
        "ot": lambda p: p["period"]["number"] >= 5,
        "touchdown": lambda p: p["scoringPlay"] and "Touchdown" in p["type"]["text"],
        "non-scoring": lambda p: p["scoringPlay"] is False,
    }
    play = next(p for p in plays if selected[kind](p))
    events = ingest_summary(summary, game)
    event = next(e for e in events if e["eventId"] == play["id"])
    stored = store.get_event(game, play["id"])
    for item in (event, stored):
        assert "period" in item and "scoringPlay" in item
        assert item["period"] == play["period"]["number"] >= 1
        assert item["scoringPlay"] is play["scoringPlay"]
    assert type(event["period"]) is int
    if kind == "touchdown":
        assert stored["scoringPlay"] is True


@pytest.mark.parametrize("field,value", [
    ("period", None), ("scoringPlay", None),
    ("period", {}), ("period", {"number": 0}),
    ("period", {"number": "4"}), ("period", {"number": True}),
    ("scoringPlay", "false"), ("scoringPlay", 1),
])
@pytest.mark.parametrize("existing", [False, True], ids=["first-poll", "repoll"])
def test_missing_or_invalid_play_facts_are_rejected_before_writes(api, field, value, existing):
    from feed_ingest.ingest import ingest_summary

    summary = fresh_summary()
    if existing:
        ingest_summary(summary, GAME)
    before = api.table("Events").scan()["Items"]
    # The last play proves validation is complete before earlier plays can be written.
    play = plays_in(summary)[-1]
    if value is None:
        del play[field]
    else:
        play[field] = value
    rejected = False
    try:
        ingest_summary(summary, GAME)
    except ValueError:
        rejected = True
    assert rejected, f"Untrusted {field} was accepted: {value!r}"
    assert api.table("Events").scan()["Items"] == before


@pytest.mark.parametrize("field", ["period", "scoringPlay"])
def test_changed_play_fact_revises_once_in_normalizer_and_store(api, field):
    import store
    from feed_ingest.ingest import ingest_summary
    from feed_ingest.normalize import normalize_summary

    summary = fresh_summary()
    first = ingest_summary(summary, GAME)
    prior = {event["eventId"]: event for event in first}
    play = plays_in(summary)[0]
    if field == "period":
        play[field]["number"] += 1
        expected = play[field]["number"]
    else:
        play[field] = not play[field]
        expected = play[field]
    normalized = normalize_summary(summary, GAME, prior=prior)
    assert len(normalized) == 1, "Changed ESPN fact must emit a correction"
    changed = ingest_summary(summary, GAME)
    assert len(changed) == 1
    for event in (normalized[0], changed[0], store.get_event(GAME, play["id"])):
        assert event["eventId"] == play["id"]
        assert event[field] == expected
        assert event["revision"] == 2 and event["correctionOf"] == 1
    assert ingest_summary(summary, GAME) == []
    assert len(api.table("Events").scan()["Items"]) == len(first)
