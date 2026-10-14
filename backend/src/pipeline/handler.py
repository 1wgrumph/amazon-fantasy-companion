"""PolicyFunction: Events stream consumer (DES-AFC-P2-BACKEND).

Chain per stored GameEvent: matcher.resolve -> alert_policy.evaluate ->
provider_resolver.resolve -> panel.project. Heavy work stays on the backend
(AFC-PR-059); the TV only reads the resulting alerts and panels.
"""

from boto3.dynamodb.types import TypeDeserializer

import alert_policy
import matcher
import panel
import provider_resolver
import store


def lambda_handler(event, context):  # pragma: no mutate block
    """Run the policy chain for each inserted or modified event.

    Not mutated: the frozen contract test inspects this body's call order, which
    mutmut's trampoline rewrite would hide; its behavior is covered by tests.
    """
    for game_event in _game_events(event):
        matches = matcher.resolve(game_event)
        alerts = alert_policy.evaluate(game_event, matches)
        for alert in alerts:
            route = provider_resolver.resolve(alert["profileId"], game_event["eventId"])
            store.put_alert(dict(alert, providerRoute=route))
        panel.project(game_event, matches)


def _game_events(event):
    deserialize = TypeDeserializer().deserialize
    return [{name: deserialize(value) for name, value in record["dynamodb"]["NewImage"].items()}
            for record in event.get("Records", [])
            if record.get("eventName") in ("INSERT", "MODIFY")]
