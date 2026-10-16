"""Customer gate red tests (VCASE-AFC-PR-008, -016, -017, -018, -019, -020).

DES-AFC-P2-POLICY gate order: relevance -> enabled alert types -> game-day
periods -> quiet hours -> alert_min_gap per game -> spoiler delay -> emit. The
order is observable: an alert suppressed by an earlier gate is never released,
so it never consumes the alert_min_gap of a later alert. Minutes of day are
read in UTC from eventTime (KICKOFF is 20:00 UTC, minute 1200).
"""

import pytest

from policy_support import (deliver, evaluate, for_profile, game_event, match,  # noqa: F401
                            OTHER_GAME, parse, policy, seed_profile, types_of)


def window(start, end):
    return {"startMinute": start, "endMinute": end}


def scoring(event_id, seconds=0, game="401999001"):
    return game_event(event_id, seconds=seconds, game=game, field_position=35, scoring=True)


def red_zone(event_id, seconds=0):
    return game_event(event_id, seconds=seconds, field_position=12)


def released(policy, event, profile="fan"):
    return for_profile(deliver(policy, event, [match(profile, event)]), profile)


@pytest.mark.parametrize("event", [
    red_zone("401999001201"),
    scoring("401999001202"),
    game_event("401999001203", period=4, score=(20, 24), field_position=60),
], ids=["red-zone", "player-score", "close-game"])
def test_afc_pr_016_no_enabled_types_emit_nothing(policy, event):
    """AFC-PR-016 negative: with every type disabled no matching event emits."""
    seed_profile("fan", alertTypes=[])
    assert evaluate(policy, event, [match("fan", event)]) == []


def test_afc_pr_016_only_the_enabled_type_fires(policy):
    """AFC-PR-016: PlayerScore on, RedZone off: red zone is silent, a score fires."""
    seed_profile("fan", alertTypes=["PlayerScore"])
    rz = red_zone("401999001204")
    assert evaluate(policy, rz, [match("fan", rz)]) == []
    score = scoring("401999001205")
    alerts = evaluate(policy, score, [match("fan", score)])
    assert [types_of(alert) for alert in alerts] == [{"PlayerScore"}]


def test_afc_pr_019_outside_game_day_periods_emits_nothing(policy):
    """AFC-PR-019 negative: 20:00 is outside a 21:00-23:00 game-day period."""
    seed_profile("fan", gameDayPeriods={"enabled": True, "periods": [window(1260, 1380)]})
    event = scoring("401999001206")
    assert evaluate(policy, event, [match("fan", event)]) == []


def test_afc_pr_019_inside_game_day_period_emits(policy):
    """AFC-PR-019 positive: 21:30 inside the 21:00-23:00 period emits."""
    seed_profile("fan", gameDayPeriods={"enabled": True, "periods": [window(1260, 1380)]})
    event = scoring("401999001207", seconds=90 * 60)
    assert len(evaluate(policy, event, [match("fan", event)])) == 1


def test_afc_pr_018_quiet_hours_suppress_inside_game_day(policy):
    """AFC-PR-018 and AFC-PR-008: quiet hours 19:00-21:00 silence a 20:00 score even
    inside a game-day period."""
    seed_profile("fan", quietHours=[window(1140, 1260)])
    event = scoring("401999001208")
    assert evaluate(policy, event, [match("fan", event)]) == []


def test_afc_pr_018_quiet_hours_wrap_past_midnight(policy):
    """AFC-PR-018: a 22:00-06:00 window silences 23:30 and leaves 20:00 alone."""
    seed_profile("fan", quietHours=[window(1320, 360)])
    late = scoring("401999001209", seconds=210 * 60)
    assert evaluate(policy, late, [match("fan", late)]) == []
    early = scoring("401999001210")
    assert len(evaluate(policy, early, [match("fan", early)])) == 1


def test_afc_pr_017_min_gap_suppresses_a_second_alert_in_the_same_game(policy):
    """AFC-PR-017: alert_min_gap 120 s holds back a score 60 s after a released alert."""
    seed_profile("fan", frequency=120)
    assert len(released(policy, scoring("401999001211"))) == 1
    assert released(policy, scoring("401999001212", seconds=60)) == []


def test_afc_pr_017_shorter_gap_releases_the_second_alert(policy):
    """AFC-PR-017: alert_min_gap 30 s lets the same score 60 s later through."""
    seed_profile("fan", frequency=30)
    assert len(released(policy, scoring("401999001213"))) == 1
    assert len(released(policy, scoring("401999001214", seconds=60))) == 1


def test_afc_pr_017_min_gap_is_per_game(policy):
    """AFC-PR-017: a released alert in one game does not hold back another game."""
    seed_profile("fan", frequency=120)
    assert len(released(policy, scoring("401999001215"))) == 1
    assert len(released(policy, scoring("401999002216", seconds=60, game=OTHER_GAME))) == 1


def test_afc_pr_017_restrictive_setting_yields_fewer_alerts(policy):
    """AFC-PR-017: an identical stream gives fewer alerts under 600 s than 0 s, and no
    two released alerts of one game are closer than the setting."""
    seed_profile("tight", frequency=600)
    seed_profile("loose", frequency=0)
    counts = {"tight": [], "loose": []}
    for step in range(5):
        event = scoring(f"40199900122{step}", seconds=30 * step)
        alerts = deliver(policy, event, [match("tight", event), match("loose", event)])
        for profile in counts:
            counts[profile] += for_profile(alerts, profile)
    assert len(counts["loose"]) == 5
    assert len(counts["tight"]) == 1
    times = sorted(parse(alert["emittedAt"]) for alert in counts["tight"])
    assert all((b - a).total_seconds() >= 600 for a, b in zip(times, times[1:]))


@pytest.mark.parametrize("delay", [0, 45, 120])
def test_afc_pr_020_release_is_at_least_the_spoiler_delay(policy, delay):
    """AFC-PR-020: emittedAt minus eventTime is at least the spoiler delay."""
    seed_profile("fan", spoilerDelay=delay)
    event = scoring("401999001230")
    alerts = evaluate(policy, event, [match("fan", event)])
    assert len(alerts) == 1, alerts
    held = (parse(alerts[0]["emittedAt"]) - parse(event["eventTime"])).total_seconds()
    assert held >= delay, f"released {held} s after the event; spoiler delay is {delay} s"


def test_gate_order_disabled_type_does_not_consume_the_min_gap(policy):
    """Gate order AFC-PR-016 before AFC-PR-017: a disabled-type event 30 s earlier is
    never released, so the next score is not held back by alert_min_gap."""
    seed_profile("fan", alertTypes=["PlayerScore"], frequency=120)
    assert released(policy, red_zone("401999001231")) == []
    assert len(released(policy, scoring("401999001232", seconds=30))) == 1


def test_gate_order_quiet_hours_do_not_consume_the_min_gap(policy):
    """Gate order AFC-PR-018 before AFC-PR-017: a score at 20:00:30 inside quiet hours
    (19:00-20:01) is never released, so 20:02:30 is not held back by a 180 s gap."""
    seed_profile("fan", quietHours=[window(1140, 1201)], frequency=180)
    assert released(policy, scoring("401999001233", seconds=30)) == []
    assert len(released(policy, scoring("401999001234", seconds=150))) == 1


def test_gate_order_game_day_does_not_consume_the_min_gap(policy):
    """Gate order AFC-PR-019 before AFC-PR-017: a score before the 20:02 game-day
    period is never released, so 20:02:30 is not held back by a 180 s gap."""
    seed_profile("fan", gameDayPeriods={"enabled": True, "periods": [window(1202, 1439)]},
                 frequency=180)
    assert released(policy, scoring("401999001235", seconds=30)) == []
    assert len(released(policy, scoring("401999001236", seconds=150))) == 1
