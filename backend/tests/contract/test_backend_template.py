"""DES-AFC-P2-BACKEND/AUTH; SEIT-AFC-PR-054/-055/-059 supporting red cases.

Source/template inspections support, but never close, the deployed Free-plan,
secret containment or implemented-heavy-work rows. No SAM/AWS invocation here.
"""

import ast
import json

import pytest

from conftest import BACKEND, document

pytestmark = pytest.mark.contract
TABLES = {"Profiles", "Links", "Events", "Alerts", "Lineups", "Panels", "PlayerStats"}
FUNCTIONS = {"ApiFunction", "IngestFunction", "PolicyFunction"}
ALLOWED_RESOURCES = {
    "AWS::Serverless::Function", "AWS::Serverless::HttpApi", "AWS::DynamoDB::Table",
    "AWS::Scheduler::Schedule", "AWS::Scheduler::ScheduleGroup",
    "AWS::IAM::Role", "AWS::IAM::Policy", "AWS::Logs::LogGroup", "AWS::SSM::Parameter",
}


def test_template_declares_only_the_approved_free_plan_service_set():
    template = document("template.yaml")
    assert template["Transform"] == "AWS::Serverless-2016-10-31"
    resources = template["Resources"]
    assert resources and all(r["Type"] in ALLOWED_RESOURCES for r in resources.values())
    assert any(r["Type"] == "AWS::Serverless::HttpApi" for r in resources.values())
    assert any(r["Type"] == "AWS::Scheduler::Schedule" for r in resources.values())


def test_template_declares_every_function_and_on_demand_table():
    template = document("template.yaml")
    resources = template["Resources"]
    assert FUNCTIONS <= set(resources)
    for name in FUNCTIONS:
        assert resources[name]["Type"] == "AWS::Serverless::Function"
        props = dict(template.get("Globals", {}).get("Function", {}),
                     **resources[name]["Properties"])
        assert props["Runtime"] == "python3.12"
        assert props.get("Handler") and props.get("CodeUri")
    tables = {name.removesuffix("Table"): value for name, value in resources.items()
              if value["Type"] == "AWS::DynamoDB::Table"}
    assert set(tables) == TABLES
    assert all(t["Properties"]["BillingMode"] == "PAY_PER_REQUEST" for t in tables.values())
    links = tables["Links"]["Properties"]["TimeToLiveSpecification"]
    assert links["Enabled"] is True and links["AttributeName"]
    assert tables["Events"]["Properties"]["StreamSpecification"]["StreamViewType"] in {
        "NEW_IMAGE", "NEW_AND_OLD_IMAGES"}


def test_template_routes_tv_and_link_page_and_bounds_link_attempts():
    template = document("template.yaml")
    resources = template["Resources"]
    events = resources["ApiFunction"]["Properties"]["Events"]
    routes = [(str(v["Properties"].get("Method", "ANY")).upper(),
               v["Properties"].get("Path", "$default"))
              for v in events.values() if v["Type"] == "HttpApi"]
    assert routes
    assert {("POST", "/v1/link"),
               ("GET", "/v1/link"), ("POST", "/v1/link/confirm"),
               ("GET", "/link"), ("GET", "/v1/profile"), ("PUT", "/v1/profile"),
               ("GET", "/v1/alerts"), ("GET", "/v1/panel"), ("GET", "/v1/providers"),
               ("POST", "/v1/routing-outcome"), ("POST", "/v1/installed-apps")} <= set(routes)
    apis = [r["Properties"] for r in resources.values() if r["Type"] == "AWS::Serverless::HttpApi"]
    assert any(a.get("DefaultRouteSettings", {}).get("ThrottlingBurstLimit") and
               a.get("DefaultRouteSettings", {}).get("ThrottlingRateLimit") for a in apis)


def test_unknown_routes_reach_the_api_router_for_the_error_envelope():
    router = document("template.yaml")["Resources"]["ApiFunction"]["Properties"]
    assert router["Handler"] == "api.handler.lambda_handler"
    defaults = [event["Properties"] for event in router["Events"].values()
                if event["Type"] == "HttpApi"
                and "Path" not in event["Properties"]
                and "Method" not in event["Properties"]]
    assert len(defaults) == 1, "Unknown paths need a SAM $default route to ApiFunction"
    assert defaults[0]["ApiId"] == {"Ref": "HttpApi"}


def test_template_uses_ssm_parameter_names_instead_of_embedded_secret_values():
    template = document("template.yaml")
    params = template.get("Parameters", {})
    names = {name for name in params if any(w in name.lower() for w in ["secret", "token"])}
    assert any("yahoo" in n.lower() and "secret" in n.lower() for n in names)
    assert any("yahoo" in n.lower() and "token" in n.lower() for n in names)
    for name in names:
        assert "Value" not in params[name]
        assert str(params[name].get("Default", "/owner-supplied/path")).startswith("/")
    function = template["Resources"]["PolicyFunction"]["Properties"]
    policy = json.dumps(function.get("Policies", {}))
    assert "ssm:GetParameter" in policy or "SSMParameterReadPolicy" in policy
    assert "secretsmanager" not in json.dumps(template).lower()


@pytest.mark.parametrize("module", [])
def test_future_backend_modules_have_explicit_unimplemented_public_interfaces(module):
    files = list((BACKEND / "src" / module).rglob("*.py"))
    assert files, f"Backend must contain the future {module} interface"
    public_stubs = []
    for file in files:
        source = file.read_text()
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                raises = [x for x in ast.walk(node) if isinstance(x, ast.Raise)]
                if "AFC-STUB" in ast.get_source_segment(source, node) and any(
                    isinstance(x.exc, ast.Call) and isinstance(x.exc.func, ast.Name) and
                    x.exc.func.id == "NotImplementedError" for x in raises):
                    public_stubs.append(node.name)
    assert public_stubs, "Future behavior must remain explicit AFC-STUB/NotImplementedError"


def test_complete_store_and_policy_chain_stay_backend_side():
    files = list((BACKEND / "src/store").rglob("*.py"))
    assert files, "P2-B01 must realize shared store accessors"
    assert any(isinstance(node, ast.FunctionDef) for file in files
               for node in ast.walk(ast.parse(file.read_text()))), "Store needs callable accessors"
    pipeline = BACKEND / "src/pipeline/handler.py"
    assert pipeline.is_file(), "PolicyFunction must have its backend pipeline entry point"
    tree = ast.parse(pipeline.read_text())
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    handler_name = document("template.yaml")["Resources"]["PolicyFunction"]["Properties"]["Handler"].rsplit(".", 1)[1]
    assert handler_name in functions
    calls = sorted((n.lineno, n.col_offset, n.func.value.id + "." + n.func.attr)
                   for n in ast.walk(functions[handler_name]) if isinstance(n, ast.Call) and
                   isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name))
    required = ["matcher.resolve", "alert_policy.evaluate", "provider_resolver.resolve", "panel.project"]
    assert [name for _, _, name in calls if name in required] == required
