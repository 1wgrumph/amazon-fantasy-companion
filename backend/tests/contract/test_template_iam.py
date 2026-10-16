"""DES-AFC-P2-BACKEND least-privilege IAM: expanded DynamoDB actions per function.

Every function grants only the table operations its callers use (get, put,
update, query, scan); the API reads but never writes Alerts; only ApiFunction
holds DeleteItem, solely on LinksTable to supersede a prior session of the
same link; no function holds BatchWriteItem or any other unneeded DynamoDB
action. The Links handle-index Query resource and the Events stream consumer
stay intact.
"""

import json

import pytest

from conftest import BACKEND, document
from iam_source import required_actions

pytestmark = pytest.mark.contract
# SAM 1.169.0 DynamoDB policy template expansions (offline policy template
# data); the template must no longer reference these broad grants.
EXPANDED = {
    "DynamoDBCrudPolicy": {"dynamodb:GetItem", "dynamodb:DeleteItem", "dynamodb:PutItem",
                           "dynamodb:Scan", "dynamodb:Query", "dynamodb:UpdateItem",
                           "dynamodb:BatchWriteItem", "dynamodb:BatchGetItem",
                           "dynamodb:DescribeTable", "dynamodb:ConditionCheckItem"},
    "DynamoDBReadPolicy": {"dynamodb:GetItem", "dynamodb:Scan", "dynamodb:Query",
                           "dynamodb:BatchGetItem", "dynamodb:DescribeTable"},
}
EXPECTED = {
    "ApiFunction": {"ProfilesTable": {"GetItem", "PutItem", "UpdateItem"},
                    "LinksTable": {"GetItem", "PutItem", "UpdateItem", "Query", "DeleteItem"},
                    "AlertsTable": {"Query"},
                    "LineupsTable": {"GetItem", "PutItem"},
                    "EventsTable": {"GetItem"},
                    "PanelsTable": {"GetItem"}},
    "IngestFunction": {"EventsTable": {"GetItem", "PutItem"},
                       "ProfilesTable": {"GetItem", "Scan"},
                       "LineupsTable": {"GetItem"}},
    "PolicyFunction": {"ProfilesTable": {"GetItem"},
                       "EventsTable": {"GetItem"},
                       "AlertsTable": {"PutItem", "Query"},
                       "LineupsTable": {"GetItem", "PutItem", "Scan"},
                       "PanelsTable": {"GetItem", "PutItem"}},
}


def grants(policies):
    """Expanded ({table: actions}, {table: resource kinds}) for one function."""
    actions, resources = {}, {}
    for entry in policies:
        [(kind, value)] = entry.items()
        if kind in EXPANDED:
            table = value["TableName"]["Ref"]
            actions.setdefault(table, set()).update(a.split(":")[1] for a in EXPANDED[kind])
            resources.setdefault(table, set()).update({"table", "index"})
        else:
            assert kind == "Statement", f"Unexpected policy entry: {kind}"
            for statement in value:
                assert statement.get("Effect") == "Allow"
                for resource in statement["Resource"]:
                    text = resource.get("Fn::GetAtt", resource.get("Fn::Sub", ""))
                    text = ".".join(text) if isinstance(text, list) else text
                    table = text.split("/index/")[0].strip("${}").split(".")[0]
                    index = "/index/" in text
                    if table.endswith("Table"):
                        actions.setdefault(table, set()).update(
                            a.split(":")[1] for a in statement["Action"]
                            if a.startswith("dynamodb:"))
                        resources.setdefault(table, set()).add("index" if index else "table")
    return actions, resources


def assert_required_grants(actions, required, function):
    missing = {table: operations - actions.get(table, set())
               for table, operations in required.items() if operations - actions.get(table, set())}
    assert not missing, f"{function} missing table-scoped DynamoDB grants: {missing}"


def test_each_function_grants_only_its_store_operations():
    template = document("template.yaml")
    for function, expected in EXPECTED.items():
        policies = template["Resources"][function]["Properties"]["Policies"]
        assert not any(set(e) & set(EXPANDED) for e in policies), \
            f"{function} still uses a broad DynamoDB policy template"
        actions, _ = grants(policies)
        environment = template["Globals"]["Function"]["Environment"]["Variables"]
        handler = template["Resources"][function]["Properties"]["Handler"]
        assert_required_grants(actions, required_actions(BACKEND / "src", handler, environment), function)
        assert actions == expected, f"{function} DynamoDB grants changed: {actions}"
        assert set().union(*actions.values()) <= {"GetItem", "PutItem", "UpdateItem", "Query",
                                                 "DeleteItem", "Scan"}


def test_policy_grants_matcher_operations_on_exact_table_arns():
    template = document("template.yaml")
    policy = template["Resources"]["PolicyFunction"]["Properties"]
    assert policy["Handler"] == "pipeline.handler.lambda_handler"
    environment = template["Globals"]["Function"]["Environment"]["Variables"]
    expected = required_actions(BACKEND / "src", policy["Handler"], environment)
    table_arns = [{"Fn::GetAtt": arn} for table in EXPECTED["PolicyFunction"]
                  for arn in (table + ".Arn", [table, "Arn"])]
    for entry in policy["Policies"]:
        for statement in entry["Statement"]:
            assert all("*" not in action for action in statement["Action"])
            if any(action.startswith("dynamodb:") for action in statement["Action"]):
                assert all(resource in table_arns for resource in statement["Resource"])
    actions, _ = grants(policy["Policies"])
    assert_required_grants(actions, expected, "PolicyFunction")


def test_api_grants_provider_resolver_operations_on_profiles_table():
    template = document("template.yaml")
    properties = template["Resources"]["ApiFunction"]["Properties"]
    environment = template["Globals"]["Function"]["Environment"]["Variables"]
    required = required_actions(BACKEND / "src", properties["Handler"], environment)
    actions, resources = grants(properties["Policies"])
    assert_required_grants(actions, required, "ApiFunction")
    assert resources["ProfilesTable"] == {"table"}


def test_api_never_writes_alerts_and_only_supersedes_link_sessions():
    template = document("template.yaml")
    policies = template["Resources"]["ApiFunction"]["Properties"]["Policies"]
    actions, _ = grants(policies)
    assert actions["AlertsTable"] == {"Query"}, "ApiFunction must be read-only on Alerts"
    assert "BatchWriteItem" not in json.dumps(template["Resources"])
    for function in EXPECTED:
        granted, _ = grants(template["Resources"][function]["Properties"]["Policies"])
        deleters = {table for table, ops in granted.items() if "DeleteItem" in ops}
        assert deleters == ({"LinksTable"} if function == "ApiFunction" else set()), \
            f"{function} must not delete outside superseding a link session"


def test_links_index_query_and_events_stream_are_preserved():
    template = document("template.yaml")
    _, resources = grants(template["Resources"]["ApiFunction"]["Properties"]["Policies"])
    assert resources["LinksTable"] == {"table", "index"}
    events = template["Resources"]["EventsTable"]["Properties"]
    assert events["StreamSpecification"]["StreamViewType"] in {"NEW_IMAGE", "NEW_AND_OLD_IMAGES"}
    sources = template["Resources"]["PolicyFunction"]["Properties"]["Events"].values()
    assert any(e["Type"] == "DynamoDB" and e["Properties"]["Stream"] ==
               {"Fn::GetAtt": "EventsTable.StreamArn"} for e in sources)
    assert "ssm:GetParameter" not in json.dumps(
        template["Resources"]["ApiFunction"]["Properties"]["Policies"])
    assert "ssm:GetParameter" in json.dumps(
        template["Resources"]["PolicyFunction"]["Properties"]["Policies"])


@pytest.mark.parametrize("case,relative,before,after,check", [
    ("F1-api-helper", "provider_resolver/__init__.py", ".get_item(Key=_state_key(profile_id))",
     ".query(KeyConditionExpression='review-drift')",
     test_api_grants_provider_resolver_operations_on_profiles_table),
    ("F1-policy-helper", "provider_resolver/__init__.py", ".get_item(Key=_state_key(profile_id))",
     ".query(KeyConditionExpression='review-drift')",
     test_policy_grants_matcher_operations_on_exact_table_arns),
    ("F2-helper-alias", "provider_resolver/__init__.py", "    packages = list(packages)",
     "    _replace_state(profile_id, packages)\n    packages = list(packages)",
     test_api_grants_provider_resolver_operations_on_profiles_table),
    ("F3-matcher-alias", "matcher/__init__.py", '    event_id = game_event["eventId"]',
     '    profiles = _table("PROFILES_TABLE")\n    profiles.scan()\n'
     '    event_id = game_event["eventId"]',
     test_policy_grants_matcher_operations_on_exact_table_arns),
    ("F4-store-helper", "store/__init__.py", '_table("LINEUPS_TABLE").get_item(',
     '_table("LINEUPS_TABLE").query(',
     test_each_function_grants_only_its_store_operations),
], ids=["F1-api-helper", "F1-policy-helper", "F2-helper-alias", "F3-matcher-alias",
        "F4-store-helper"])
def test_source_drift_requires_a_table_scoped_grant(monkeypatch, case, relative, before, after, check):
    """Review M1/M2/M3 and the store gap must trip the real IAM contract."""
    path = BACKEND / "src" / relative
    original = path.read_text()
    assert original.count(before) == 1
    changed = original.replace(before, after)
    if case == "F2-helper-alias":
        # Replace the whole writer, as in review M3, retaining record_outcome.
        changed = original[:original.index(before)] + '    return _replace_state(profile_id, packages)\n'
        changed += ('\n\ndef _replace_state(profile_id, packages):\n'
                    '    state = _state_table()\n'
                    '    remove = state.delete_item\n'
                    '    remove(Key=_state_key(profile_id))\n'
                    '    state.put_item(Item=_state_key(profile_id))\n')
    read_text = type(path).read_text
    monkeypatch.setattr(type(path), "read_text",
                        lambda self, *a, **kw: changed if self == path else read_text(self, *a, **kw))
    with pytest.raises(AssertionError, match="(Query|DeleteItem|Scan)"):
        check()


@pytest.mark.parametrize("expression", [
    '_table("UNBOUND_TABLE").scan()',
    '_table(variable_from_request).scan()',
    'unknown_table.scan()',
    'scan = unknown_table.scan; scan()',
], ids=["missing-environment", "dynamic-table", "unknown-receiver", "unknown-method-alias"])
def test_unknown_table_resolution_fails_closed(monkeypatch, expression):
    path = BACKEND / "src/matcher/__init__.py"
    changed = path.read_text().replace('    event_id = game_event["eventId"]',
                                       '    ' + expression + '\n    event_id = game_event["eventId"]')
    read_text = type(path).read_text
    monkeypatch.setattr(type(path), "read_text",
                        lambda self, *a, **kw: changed if self == path else read_text(self, *a, **kw))
    with pytest.raises(AssertionError, match="Unknown DynamoDB table resolution"):
        test_policy_grants_matcher_operations_on_exact_table_arns()


def test_table_and_operation_aliases_keep_valid_grants(monkeypatch):
    path = BACKEND / "src/matcher/__init__.py"
    changed = path.read_text().replace(
        '        page = _table(variable).scan(**request)',
        '        table = _table(variable)\n        scan = table.scan\n        page = scan(**request)')
    read_text = type(path).read_text
    monkeypatch.setattr(type(path), "read_text",
                        lambda self, *a, **kw: changed if self == path else read_text(self, *a, **kw))
    test_policy_grants_matcher_operations_on_exact_table_arns()
