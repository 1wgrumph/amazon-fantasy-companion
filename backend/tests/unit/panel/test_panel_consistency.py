"""Panel and alerts are two views of one truth (VCASE-AFC-PR-046; DES-AFC-P2-MATCH, -PANELSVC).

A scoring correction is a later revision of the same event id: it revises
the panel facts in place (no duplicate rows, no regression on a stale
revision) exactly as it revises the alert record. A starter change reaches
the panel; a hidden panel keeps projecting and is current when shown.
"""

import pytest

from panel_support import (PASSER, RECEIVER, TIGHT_END, game_event, match, number,  # noqa: F401
                           panel_env, player_ids, points, seed_alert, seed_lineup, seed_profile,
                           statistics, update_profile)

EVENT = "401999001501"
# Half-PPR: TD catch 1 rec 12 yd = 0.5 + 1.2 + 6 = 7.7; corrected to no TD = 1.7.
SCORED = dict(receptions=1, receiving_yards=12, receiving_touchdowns=1)
CORRECTED = dict(receptions=1, receiving_yards=12)


def first_delivery(env, profile="fan", starters=(RECEIVER,)):
    seed_profile(profile)
    seed_lineup(profile, list(starters))
    env.stats["9000001"] = statistics(**SCORED)
    event = game_event(EVENT, score=(7, 3), scoring=True)
    env.project(event, [match(profile, event)])
    return event


def correction(players=("9000001",), revision=2, score=(0, 3)):
    return game_event(EVENT, players, score=score, revision=revision,
                      correction_of=revision - 1, seconds=30)


def test_first_event_facts_reach_the_panel(panel_env):
    event = first_delivery(panel_env)
    facts = panel_env.data("fan")["games"].get(event["gameId"])
    assert facts is not None, "the projected event's game facts must be on the panel"
    assert facts["eventId"] == EVENT and number(facts["revision"]) == 1
    assert {k: number(v) for k, v in facts["score"].items()} == {"away": 7, "home": 3}
    assert facts["source"] == "live"


def test_correction_revises_points_in_place(panel_env):
    first_delivery(panel_env)
    before = panel_env.snapshot("fan")
    assert points(before["data"], "9000001") == pytest.approx(7.7, abs=0.005)
    panel_env.stats["9000001"] = statistics(as_of="2026-10-18T20:00:30Z", **CORRECTED)
    event = correction()
    panel_env.project(event, [match("fan", event, cursor="c-0001")])
    after = panel_env.snapshot("fan")
    data = panel_env.data("fan")
    assert [r["playerId"] for r in data["rows"]] == ["9000001"], "a correction adds no row"
    assert points(data, "9000001") == pytest.approx(1.7, abs=0.005)
    assert after["id"] == before["id"]
    assert after["revision"] > before["revision"]


def test_correction_replaces_the_game_facts(panel_env):
    first_delivery(panel_env)
    event = correction()
    panel_env.project(event, [match("fan", event, cursor="c-0001")])
    facts = panel_env.data("fan")["games"][event["gameId"]]
    assert facts["eventId"] == EVENT and number(facts["revision"]) == 2
    assert {k: number(v) for k, v in facts["score"].items()} == {"away": 0, "home": 3}


def test_correction_reassigning_the_play_still_revises_the_panel(panel_env):
    # P2-B04T: the correction still matches the profile with no credited starter.
    first_delivery(panel_env)
    panel_env.stats["9000001"] = statistics(**CORRECTED)
    event = correction(players=("9000077",))
    panel_env.project(event, [match("fan", event, starters=(), cursor="c-0001")])
    data = panel_env.data("fan")
    assert points(data, "9000001") == pytest.approx(1.7, abs=0.005)
    assert number(data["games"][event["gameId"]]["revision"]) == 2


def test_stale_revision_does_not_regress_the_panel(panel_env):
    first = first_delivery(panel_env)
    event = correction()
    panel_env.project(event, [match("fan", event, cursor="c-0001")])
    settled = panel_env.snapshot("fan")
    panel_env.project(first, [match("fan", first)])
    again = panel_env.snapshot("fan")
    facts = panel_env.data("fan")["games"][first["gameId"]]
    assert number(facts["revision"]) == 2, "an older revision must never replace corrected facts"
    assert {k: number(v) for k, v in facts["score"].items()} == {"away": 0, "home": 3}
    assert again["revision"] >= settled["revision"], "the panel revision never moves backwards"


def test_panel_facts_agree_with_the_alert_record(panel_env):
    first_delivery(panel_env)
    event = correction()
    seed_alert("fan", "c-0001", event)
    panel_env.project(event, [match("fan", event, cursor="c-0001")])
    alert = panel_env.api.table("Alerts").scan()["Items"][0]
    facts = panel_env.data("fan")["games"][alert["triggerContext"]["gameId"]]
    assert facts["eventId"] == alert["eventId"]
    assert number(facts["revision"]) == number(alert["revision"])
    assert facts["source"] == alert["triggerContext"]["source"]
    assert ({k: number(v) for k, v in facts["score"].items()}
            == {k: number(v) for k, v in alert["triggerContext"]["score"].items()})


def test_replay_event_is_labeled_replay_on_the_panel(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER])
    panel_env.stats["9000001"] = statistics(source="replay", **SCORED)
    event = game_event(EVENT, source="replay")
    seed_alert("fan", "c-0001", event)
    panel_env.project(event, [match("fan", event)])
    data = panel_env.data("fan")
    assert data["games"][event["gameId"]]["source"] == "replay"
    assert data["rows"][0]["points"]["source"] == "replay"


def test_every_matched_profile_gets_the_same_facts(panel_env):
    seed_profile("fan-one")
    seed_profile("fan-two")
    seed_lineup("fan-one", [RECEIVER])
    seed_lineup("fan-two", [RECEIVER, PASSER])
    panel_env.stats["9000001"] = statistics(**SCORED)
    event = game_event(EVENT, score=(7, 3), scoring=True)
    panel_env.project(event, [match("fan-one", event), match("fan-two", event)])
    one, two = panel_env.data("fan-one"), panel_env.data("fan-two")
    assert points(one, "9000001") == points(two, "9000001") == pytest.approx(7.7, abs=0.005)
    assert one["games"][event["gameId"]] == two["games"][event["gameId"]]


def test_starter_change_replaces_the_benched_row(panel_env):
    first_delivery(panel_env, starters=(RECEIVER, PASSER))
    panel_env.stats["9000005"] = statistics(passing_yards=100)
    before = panel_env.snapshot("fan")
    seed_lineup("fan", [RECEIVER, TIGHT_END])
    panel_env.stats["9000013"] = statistics(game="401999002", receptions=2, receiving_yards=20)
    event = game_event("401999002101", ("9000013",), game="401999002", seconds=40)
    panel_env.project(event, [match("fan", event, starters=(TIGHT_END,))])
    after = panel_env.snapshot("fan")
    data = panel_env.data("fan")
    assert player_ids(data) == {"9000001", "9000013"}, "a benched player must leave the panel"
    # 7.7 + (1.0 + 2.0): the benched passer no longer counts toward the total.
    assert number(data["teamTotal"]["value"]) == pytest.approx(10.7, abs=0.01)
    assert after["revision"] > before["revision"]


def test_alerted_starters_are_panel_rows(panel_env):
    first_delivery(panel_env, starters=(RECEIVER, PASSER))
    seed_lineup("fan", [RECEIVER, TIGHT_END])
    panel_env.stats["9000013"] = statistics(game="401999002", receptions=1)
    event = game_event("401999002102", ("9000013",), game="401999002", seconds=50)
    seed_alert("fan", "c-0002", event, starters=(TIGHT_END,))
    panel_env.project(event, [match("fan", event, starters=(TIGHT_END,))])
    data = panel_env.data("fan")
    for alert in panel_env.api.table("Alerts").scan()["Items"]:
        for starter in alert["triggerContext"]["starters"]:
            assert starter["athlete_id"] in player_ids(data), \
                f"alerted starter {starter['athlete_id']} is missing from the panel"


def test_hidden_panel_is_current_when_shown(panel_env):
    seed_profile("fan", panelPrefs={"visible": False})
    seed_lineup("fan", [RECEIVER])
    panel_env.stats["9000001"] = statistics(**SCORED)
    first = game_event(EVENT, score=(7, 3), scoring=True)
    panel_env.project(first, [match("fan", first)])
    hidden = panel_env.snapshot("fan")
    panel_env.stats["9000001"] = statistics(**CORRECTED)
    event = correction()
    panel_env.project(event, [match("fan", event, cursor="c-0001")])
    update_profile("fan", panelPrefs={"visible": True})
    shown = panel_env.snapshot("fan")
    data = panel_env.data("fan")
    assert data["visible"] is True
    assert points(data, "9000001") == pytest.approx(1.7, abs=0.005)
    assert number(data["games"][event["gameId"]]["revision"]) == 2
    assert shown["revision"] > hidden["revision"]
