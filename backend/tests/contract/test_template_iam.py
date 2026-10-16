"""DES-AFC-P2-BACKEND least-privilege IAM: expanded DynamoDB actions per function.

Every function grants only the table operations its callers use (get, put,
update, query, scan); the API reads but never writes Alerts; only ApiFunction
holds DeleteItem, solely on LinksTable to supersede a prior session of the
same link; no function holds BatchWriteItem or any other unneeded DynamoDB
action. The Links handle-index Query resource and the Events stream consumer
stay intact.
"""

import ast
import json

import pytest

from conftest import BACKEND, document

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
    "ApiFunction": {"ProfilesTable": {"GetItem", "PutItem"},
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


def test_each_function_grants_only_its_store_operations():
    template = document("template.yaml")
    for function, expected in EXPECTED.items():
        policies = template["Resources"][function]["Properties"]["Policies"]
        assert not any(set(e) & set(EXPANDED) for e in policies), \
            f"{function} still uses a broad DynamoDB policy template"
        actions, _ = grants(policies)
        assert actions == expected, f"{function} DynamoDB grants changed: {actions}"
        assert set().union(*actions.values()) <= {"GetItem", "PutItem", "UpdateItem", "Query",
                                                 "DeleteItem", "Scan"}


def test_policy_grants_matcher_operations_on_exact_table_arns():
    template = document("template.yaml")
    policy = template["Resources"]["PolicyFunction"]["Properties"]
    assert policy["Handler"] == "pipeline.handler.lambda_handler"
    environment = template["Globals"]["Function"]["Environment"]["Variables"]
    # Other pipeline stages keep their existing grants; matcher reads are derived
    # from source because moto does not enforce deployed IAM permissions.
    expected = {"ProfilesTable": {"GetItem"}, "EventsTable": {"GetItem"},
                "AlertsTable": {"PutItem"}, "LineupsTable": {"GetItem", "PutItem"},
                "PanelsTable": {"GetItem", "PutItem"}}
    module = ast.parse((BACKEND / "src/matcher/__init__.py").read_text())
    for function in module.body:
        if not isinstance(function, ast.FunctionDef):
            continue
        for node in ast.walk(function):
            if not (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "_table"):
                continue
            argument = node.value.args[0]
            if isinstance(argument, ast.Constant):
                variables = [argument.value]
            else:
                assert isinstance(argument, ast.Name)
                assert argument.id == function.args.args[0].arg
                variables = [ast.literal_eval(call.args[0]) for call in ast.walk(module)
                             if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                             and call.func.id == function.name]
                assert variables, f"No table binding found for {function.name}"
            action = "".join(part.title() for part in node.attr.split("_"))
            for variable in variables:
                expected.setdefault(environment[variable]["Ref"], set()).add(action)
    table_arns = [{"Fn::GetAtt": arn} for table in expected
                  for arn in (table + ".Arn", [table, "Arn"])]
    for entry in policy["Policies"]:
        for statement in entry["Statement"]:
            assert all("*" not in action for action in statement["Action"])
            if any(action.startswith("dynamodb:") for action in statement["Action"]):
                assert all(resource in table_arns for resource in statement["Resource"])
    actions, _ = grants(policy["Policies"])
    assert actions == expected, f"PolicyFunction must grant matcher calls: {expected}; got {actions}"


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
