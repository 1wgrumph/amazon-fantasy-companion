"""Unavailable and stale values (VCASE-AFC-PR-040; spec 4.1.11, 4.3, 4.5).

A missing value is null with a reason, never zero; a known zero is zero.
Each value carries its statistics source (live or replay) and source
timestamp; stale_after is 60 s, evaluated per value at read time from that
timestamp (age >= 60 s is stale, matching the P2-A05T TV boundary).
"""

import pytest

from panel_support import (PASSER, RECEIVER, STALE_AFTER, YAHOO_RECEIVER, YAHOO_UNMAPPED, at,  # noqa: F401
                           game_event, match, number, panel_env, parse, points, row, row_named,
                           seed_lineup, seed_profile, statistics)


def project_receiver(env, record, starters=(RECEIVER,)):
    seed_profile("fan")
    seed_lineup("fan", list(starters))
    if record is not None:
        env.stats["9000001"] = record
    event = game_event("401999001301")
    env.project(event, [match("fan", event)])


def test_missing_statistics_are_null_with_reason_not_zero(panel_env):
    project_receiver(panel_env, None)
    value = row(panel_env.data("fan"), "9000001")["points"]
    assert value["value"] is None, f"a missing value must stay unknown, never zero: {value!r}"
    assert isinstance(value["reason"], str) and value["reason"].strip()


def test_missing_statistics_leave_game_status_unknown(panel_env):
    project_receiver(panel_env, None)
    assert row(panel_env.data("fan"), "9000001")["gameStatus"] is None


def test_known_zero_is_zero_without_a_reason(panel_env):
    project_receiver(panel_env, statistics(receptions=0, receiving_yards=0))
    value = row(panel_env.data("fan"), "9000001")["points"]
    assert number(value["value"]) == 0.0, f"a known zero is a valid score: {value!r}"
    assert value["reason"] is None


def test_total_with_an_unknown_row_is_not_a_confirmed_sum(panel_env):
    project_receiver(panel_env, statistics(receptions=10), starters=(RECEIVER, PASSER))
    total = panel_env.data("fan")["teamTotal"]
    assert total["value"] is None or (isinstance(total["reason"], str) and total["reason"]), \
        f"a total over an unknown row must not read as a confirmed score: {total!r}"
    assert number(total["value"]) in (None, pytest.approx(5.0)), \
        f"an unknown row must not be counted as anything but unknown: {total!r}"


def test_as_of_is_the_statistics_source_timestamp(panel_env):
    project_receiver(panel_env, statistics(receptions=2, as_of=at(3)))
    panel_env.set_now(20)
    value = row(panel_env.data("fan"), "9000001")["points"]
    assert parse(value["asOf"]) == parse(at(3)), \
        "asOf is the source timestamp, not the projection or response time"


def test_team_total_as_of_is_the_oldest_row(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    panel_env.stats["9000001"] = statistics(receptions=2, as_of=at(0))
    panel_env.stats["9000005"] = statistics(passing_yards=100, as_of=at(30))
    event = game_event("401999001301")
    panel_env.project(event, [match("fan", event)])
    panel_env.set_now(35)
    assert parse(panel_env.data("fan")["teamTotal"]["asOf"]) == parse(at(0))


@pytest.mark.parametrize("age,stale", [(0, False), (59, False), (60, True), (61, True)])
def test_stale_boundary_is_sixty_seconds(panel_env, age, stale):
    project_receiver(panel_env, statistics(receptions=2, as_of=at(0)))
    panel_env.set_now(age)
    value = row(panel_env.data("fan"), "9000001")["points"]
    assert value["stale"] is stale, f"age {age} s (stale_after {STALE_AFTER} s): {value!r}"


def test_stale_value_keeps_its_number(panel_env):
    project_receiver(panel_env, statistics(receptions=2, as_of=at(0)))
    panel_env.set_now(61)
    value = row(panel_env.data("fan"), "9000001")["points"]
    assert number(value["value"]) == pytest.approx(1.0), "a stale value is labeled, not dropped"
    assert value["stale"] is True


def test_staleness_is_evaluated_at_read_time(panel_env):
    project_receiver(panel_env, statistics(receptions=2, as_of=at(0)))
    panel_env.set_now(10)
    assert row(panel_env.data("fan"), "9000001")["points"]["stale"] is False
    panel_env.set_now(75)
    assert row(panel_env.data("fan"), "9000001")["points"]["stale"] is True, \
        "a withheld feed must age into stale without a new projection"


def test_total_is_stale_when_any_row_is_stale(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [RECEIVER, PASSER])
    panel_env.stats["9000001"] = statistics(receptions=2, as_of=at(0))
    panel_env.stats["9000005"] = statistics(passing_yards=100, as_of=at(50))
    event = game_event("401999001301")
    panel_env.project(event, [match("fan", event)])
    panel_env.set_now(65)
    data = panel_env.data("fan")
    assert row(data, "9000005")["points"]["stale"] is False
    assert data["teamTotal"]["stale"] is True


def test_value_without_a_timestamp_is_never_fresh(panel_env):
    record = statistics(receptions=2)
    record["asOf"] = None
    project_receiver(panel_env, record)
    value = row(panel_env.data("fan"), "9000001")["points"]
    assert value["stale"] is True, f"an undated value is never shown as fresh: {value!r}"


@pytest.mark.parametrize("source", ["live", "replay"])
def test_value_source_follows_the_statistics_source(panel_env, source):
    project_receiver(panel_env, statistics(receptions=2, source=source))
    assert row(panel_env.data("fan"), "9000001")["points"]["source"] == source


def test_unmatched_yahoo_starter_is_unavailable_not_guessed(panel_env):
    seed_profile("fan")
    seed_lineup("fan", [YAHOO_RECEIVER, YAHOO_UNMAPPED], source="yahoo")
    panel_env.stats["9000001"] = statistics(receptions=2)
    event = game_event("401999001301")
    panel_env.project(event, [match("fan", event)])
    data = panel_env.data("fan")
    assert points(data, "9000001") == pytest.approx(3.0)
    unmatched = row_named(data, "Unmapped Back")["points"]
    assert unmatched["value"] is None and unmatched["reason"], unmatched
