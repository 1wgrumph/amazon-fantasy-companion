"""P2-B05 repair regressions for AFC-B05-R01..R06 (non-frozen; repair packet)."""

import json
from datetime import datetime, timedelta, timezone

from policy_support import (RECEIVER, attempt, deliver, evaluate, game_event, iso,
                            match, policy, seed_alert, seed_profile, types_of)  # noqa: F401


def past(minutes=5):
    return iso(datetime.now(timezone.utc) - timedelta(minutes=minutes))


def pending(policy, profile_id, cursor=None):
    return attempt(policy.pending, profile_id, cursor)


def test_r01_redzone_espn_team_id_possession_matches_starter_abbreviation(policy):
    seed_profile("fan", alertTypes=["RedZone"])
    event = game_event("r01", field_position=9, possession="21")  # ESPN id for PHI
    alerts = evaluate(policy, event, [match("fan", event)])
    assert len(alerts) == 1 and types_of(alerts[0]) == {"RedZone"}, alerts
    other = game_event("r01b", field_position=9, possession="6")  # DAL, not the starter's team
    assert evaluate(policy, other, [match("fan", other)]) == []


def test_r02_correction_removing_trigger_revises_existing_alert(policy):
    import store
    seed_profile("fan", starters=(RECEIVER,), alertTypes=["PlayerScore"])
    first = game_event("r02", scoring=True)
    original = deliver(policy, first, [match("fan", first)])
    corrected = game_event("r02", players=["9000077"], scoring=True, revision=2,
                           correction_of=1, score=(3, 3))
    update = deliver(policy, corrected,
                     [match("fan", corrected, starters=(), cursor=original[0]["cursor"])])
    assert len(update) == 1 and update[0]["revision"] == 2, update
    stored = store.list_alerts("fan", None, 100)
    assert len(stored) == 1 and int(stored[0]["revision"]) == 2, stored
    assert stored[0]["triggerContext"]["score"] == {"away": 3, "home": 3}, stored


def test_r03_pending_delivers_higher_revision_of_consumed_alert(policy):
    seed_profile("fan")
    seed_alert("fan", "c-1", past(), event_id="r03", revision=1)
    first = pending(policy, "fan")
    assert [int(a["revision"]) for a in first["alerts"]] == [1], first
    seed_alert("fan", "c-1", past(), event_id="r03", revision=2)
    second = pending(policy, "fan", first["cursor"])
    assert [int(a["revision"]) for a in second["alerts"]] == [2], second
    third = pending(policy, "fan", second["cursor"])
    assert third["alerts"] == [], third


def test_r04_pending_is_bounded_below_64kib_and_resumable(policy):
    seed_profile("fan")
    for i in range(150):
        seed_alert("fan", f"c-{i:04}", past(), event_id=f"e-{i:04}")
    seen, cursor = [], None
    for _ in range(10):
        body = pending(policy, "fan", cursor)
        assert len(json.dumps(body, default=int).encode()) < 65536, len(body["alerts"])
        seen.extend(a["id"] for a in body["alerts"])
        cursor = body["cursor"]
        if not body["alerts"]:
            break
    assert seen == [f"c-{i:04}" for i in range(150)], seen[:5]


def test_r05_optin_without_observation_evidence_is_profile_assumption(policy):
    seed_profile("fan", starters=(RECEIVER,), alertTypes=["PlayerScore"], detectionOptIn=True)
    event = game_event("r05", scoring=True)
    alerts = evaluate(policy, event, [match("fan", event)])
    assert alerts[0]["triggerContext"]["basis"] == "profile-assumption", alerts
    observed = dict(match("fan", event), basis="observed-playback")
    alerts = evaluate(policy, game_event("r05b", scoring=True), [observed])
    assert alerts[0]["triggerContext"]["basis"] == "observed-playback", alerts


def test_r06_close_game_fires_again_after_exit_and_reentry(policy):
    seed_profile("fan", alertTypes=["CloseGame"])
    counts = []
    for event_id, seconds, score in (("r06a", 0, (17, 20)), ("r06b", 60, (17, 30)),
                                     ("r06c", 120, (24, 30))):
        event = game_event(event_id, period=4, score=score, seconds=seconds)
        counts.append(len(deliver(policy, event, [match("fan", event)])))
    assert counts == [1, 0, 1], counts
