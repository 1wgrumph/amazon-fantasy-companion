"""G4 backend wire contract: sourced optional matchup and cursor <= 256."""

from datetime import datetime, timedelta, timezone

import pytest
import store

from policy_support import (attempt, deliver, evaluate, game_event, iso, match,
                            policy, seed_alert, seed_profile)  # noqa: F401


def past(minutes):
    return iso(datetime.now(timezone.utc) - timedelta(minutes=minutes))


def pending(policy, profile_id, cursor=None):
    body = attempt(policy.pending, profile_id, cursor)
    assert len(body["cursor"]) <= 256, body
    return body


def scoring(event_id, **fields):
    return game_event(event_id, field_position=35, scoring=True, **fields)


def test_sourced_matchup_reaches_trigger_context(policy):
    seed_profile("fan")
    event = dict(scoring("401999001501"), matchup="PHI at JAX")
    alerts = evaluate(policy, event, [match("fan", event)])
    assert len(alerts) == 1
    assert alerts[0]["triggerContext"]["matchup"] == "PHI at JAX"


def test_matchup_absent_when_unknown_never_fabricated(policy):
    seed_profile("fan")
    event = scoring("401999001502")
    alerts = evaluate(policy, event, [match("fan", event)])
    assert "matchup" not in alerts[0]["triggerContext"]


def test_oversize_or_blank_matchup_is_omitted_not_truncated(policy):
    seed_profile("fan")
    for index, bad in enumerate(("x" * 81, "   ", 123)):
        event = dict(scoring(f"40199900151{index}"), matchup=bad)
        alerts = evaluate(policy, event, [match("fan", event)])
        assert "matchup" not in alerts[0]["triggerContext"], bad


def test_long_event_id_cursor_fits_256_and_resumes(policy):
    seed_profile("fan", alertTypes=["RedZone"],
                 gameDayPeriods={"enabled": True, "periods": []})
    long_id = "9" * 236
    event = game_event(long_id, field_position=9, period=4, score=(24, 27))
    event["eventTime"] = past(5)
    alerts = deliver(policy, event, [match("fan", event)])
    assert len(alerts) == 1
    assert len(alerts[0]["cursor"]) <= 256
    assert alerts[0]["eventId"] == long_id
    assert alerts[0]["triggerContext"]["eventId"] == long_id

    body = pending(policy, "fan")
    assert [a["id"] for a in body["alerts"]] == [alerts[0]["cursor"]]
    again = pending(policy, "fan", body["cursor"])
    assert again["alerts"] == [] and again["cursor"] == body["cursor"]

    # A higher revision of the consumed long-id alert is delivered again.
    revised_event = dict(event, revision=2, correctionOf=1)
    revised = evaluate(policy, revised_event,
                         [match("fan", revised_event, cursor=alerts[0]["cursor"])])
    assert len(revised) == 1 and revised[0]["revision"] == 2
    store.put_alert(dict(revised[0], providerRoute=None, emittedAt=past(4)))
    redelivered = pending(policy, "fan", body["cursor"])
    assert [a["revision"] for a in redelivered["alerts"]] == [2]
    assert redelivered["cursor"].endswith("~r2")
    assert pending(policy, "fan", redelivered["cursor"])["alerts"] == []


def test_legacy_long_key_row_is_served_once_with_bounded_resume(policy):
    legacy_cursor = "2026-10-15T00:19:30Z#" + "9" * 236
    assert len(legacy_cursor) == 257
    seed_alert("fan", legacy_cursor, past(5), event_id="9" * 236)

    body = pending(policy, "fan")
    assert [a["id"] for a in body["alerts"]] == [legacy_cursor], body
    assert body["cursor"] != legacy_cursor

    # Resuming from the bounded token must not redeliver or loop.
    again = pending(policy, "fan", body["cursor"])
    assert again["alerts"] == [] and again["cursor"] == body["cursor"]

    # A higher revision at the legacy key is still delivered via the token.
    seed_alert("fan", legacy_cursor, past(4), event_id="9" * 236, revision=2)
    redelivered = pending(policy, "fan", body["cursor"])
    assert [a["revision"] for a in redelivered["alerts"]] == [2]
    assert redelivered["cursor"].endswith("~r2")
    assert pending(policy, "fan", redelivered["cursor"])["alerts"] == []

    # Alerts after the legacy row remain reachable and are not lost.
    seed_alert("fan", "z-0001", past(3), event_id="401999001599")
    rest = pending(policy, "fan", redelivered["cursor"])
    assert [a["id"] for a in rest["alerts"]] == ["z-0001"]


@pytest.mark.parametrize("length", [254, 255, 256])
@pytest.mark.parametrize("revision", [2, 10])
def test_near_limit_legacy_cursor_revision_resumes_without_replay(policy, length, revision):
    legacy_cursor = "2026-10-15T00:19:30Z#" + "9" * (length - 21)
    assert len(legacy_cursor) == length
    seed_alert("fan", "2026-10-15T00:00:00Z#1", past(6), event_id="1")
    seed_alert("fan", legacy_cursor, past(5), event_id="9" * 20)

    body = pending(policy, "fan")
    assert [a["id"] for a in body["alerts"]] == ["2026-10-15T00:00:00Z#1", legacy_cursor], body

    seed_alert("fan", legacy_cursor, past(4), event_id="9" * 20, revision=revision)
    redelivered = pending(policy, "fan", body["cursor"])
    assert [a["revision"] for a in redelivered["alerts"]] == [revision], redelivered
    assert redelivered["cursor"].endswith(f"~r{revision}")

    # A second resume must return nothing, not replay the whole history (F1).
    again = pending(policy, "fan", redelivered["cursor"])
    assert again["alerts"] == [] and again["cursor"] == redelivered["cursor"], again
