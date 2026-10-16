"""B04-RV-001 regression: the alert lookup must read strongly consistently.

After a committed alert write, an eventually-consistent Query may omit the
row or return an older revision; a retry must not then treat the event as a
new match. The lag outcomes are modelled with a botocore after-call hook
that only tampers with non-consistent Query responses.
"""

import copy

from matcher_support import MANUAL_RECEIVER, game_event, match_env, seed_alert, seed_lineup  # noqa: F401

EVENT = "401999001301"


def test_committed_alert_suppresses_retry_under_query_lag(match_env):
    seed_lineup("fan", "manual", [MANUAL_RECEIVER])
    event = game_event(EVENT, ["9000001"], revision=2)
    seed_alert("fan", "c-0001", EVENT, 2)
    assert match_env.resolve(event) == [], "fresh read must suppress equal revision"

    client = match_env.module._table("ALERTS_TABLE").meta.client
    captured, stale = [], {"kind": "missing"}

    def observe(params, **kwargs):
        captured.append(params.get("ConsistentRead", False))

    def delayed(parsed, **kwargs):
        if captured[-1]:
            return
        if stale["kind"] == "missing":
            parsed["Items"], parsed["Count"] = [], 0
        else:
            parsed["Items"] = copy.deepcopy(parsed["Items"])
            parsed["Items"][0]["revision"] = {"N": "1"}

    client.meta.events.register("before-parameter-build.dynamodb.Query", observe)
    client.meta.events.register("after-call.dynamodb.Query", delayed)
    try:
        assert match_env.resolve(event) == [], "omitted recent alert must not rematch"
        stale["kind"] = "older"
        assert match_env.resolve(event) == [], "older revision must not rematch"
    finally:
        client.meta.events.unregister("after-call.dynamodb.Query", delayed)
        client.meta.events.unregister("before-parameter-build.dynamodb.Query", observe)
    assert captured and all(captured), f"every alert Query must set ConsistentRead=True, got {captured}"
