"""DEC-AFC-SD-067: the GameEvent allowlist preserves the policy's play facts."""

import pytest


def test_store_accepts_period_and_scoring_from_a_captured_play(api):
    import json
    from pathlib import Path

    import store
    from feed_ingest.normalize import normalize_summary

    path = Path(__file__).resolve().parents[2] / "fixtures/replay/401872981/001-summary.json"
    summary = json.loads(path.read_text())
    play = summary["drives"]["previous"][0]["plays"][0]
    event = dict(normalize_summary(summary, summary["header"]["id"])[0],
                 period=play["period"]["number"], scoringPlay=play["scoringPlay"])
    try:
        store.put_event(event)
    except ValueError as error:
        raise AssertionError(f"Store rejected ESPN GameEvent facts: {error}") from error
    assert store.get_event(event["gameId"], event["eventId"]) == event
    with pytest.raises(ValueError, match="Unknown item attributes: bogus"):
        store.put_event(dict(event, bogus=True))
