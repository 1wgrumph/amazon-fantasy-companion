"""CONTRACT-AFC-P2-API/ENVELOPE; SEIT-AFC-PR-057/-058 supporting red cases."""

import pytest

from conftest import assert_error, document, link_device

pytestmark = pytest.mark.contract
OPERATIONS = {
    "/v1/link": {"get", "post"}, "/v1/link/confirm": {"post"},
    "/v1/profile": {"get", "put"}, "/v1/alerts": {"get"},
    "/v1/panel": {"get"}, "/v1/providers": {"get"},
    "/v1/routing-outcome": {"post"}, "/v1/installed-apps": {"post"},
}


def dereference(doc, schema):
    while "$ref" in schema:
        ref = schema["$ref"]
        assert ref.startswith("#/"), "OpenAPI references must stay in the frozen offline artifact"
        schema = doc
        for part in ref[2:].split("/"):
            schema = schema[part.replace("~1", "/").replace("~0", "~")]
    return schema


def properties(doc, schema):
    schema = dereference(doc, schema)
    props, required = dict(schema.get("properties", {})), set(schema.get("required", []))
    for part in schema.get("allOf", []):
        more, names = properties(doc, part)
        props.update(more)
        required.update(names)
    return props, required


def response_schema(doc, path, method, status):
    response = dereference(doc, doc["paths"][path][method]["responses"][str(status)])
    return response["content"]["application/json"]["schema"]


def test_openapi_contains_exact_tv_operations_without_excluded_social_endpoints():
    doc = document("src/api/openapi.yaml")
    assert str(doc.get("openapi", "")).startswith("3.")
    paths = doc["paths"]
    assert set(paths) <= set(OPERATIONS) | {"/link"}, "No undocumented/social API surface"
    for path, methods in OPERATIONS.items():
        assert methods == set(paths[path]) & {"get", "post", "put", "delete", "patch", "options", "head"}


@pytest.mark.parametrize("path,methods", list(OPERATIONS.items())[2:])
def test_openapi_protected_operations_require_http_bearer_auth(path, methods):
    doc = document("src/api/openapi.yaml")
    schemes = doc["components"]["securitySchemes"]
    bearer = {name for name, value in schemes.items()
              if value.get("type") == "http" and value.get("scheme", "").lower() == "bearer"}
    assert bearer
    for method in methods:
        security = doc["paths"][path][method].get("security", doc.get("security", []))
        assert security and all(set(option) & bearer for option in security), "No anonymous alternative"


@pytest.mark.parametrize("path", ["/v1/profile", "/v1/alerts", "/v1/panel"])
def test_entity_response_schemas_preserve_the_versioned_envelope(path):
    doc = document("src/api/openapi.yaml")
    schema = dereference(doc, response_schema(doc, path, "get", 200))
    # Alerts can be a bounded collection of enveloped entities plus its cursor.
    if path == "/v1/alerts":
        if schema.get("type") == "array":
            schema = schema["items"]
        elif "alerts" in schema.get("properties", {}):
            schema = dereference(doc, schema["properties"]["alerts"])["items"]
    props, required = properties(doc, schema)
    fields = {"schemaVersion", "id", "revision", "source", "updatedAt", "data"}
    assert fields <= required and fields <= set(props)
    assert dereference(doc, props["id"])["type"] == "string"
    assert dereference(doc, props["revision"])["type"] == "integer"
    assert dereference(doc, props["updatedAt"])["format"] == "date-time"
    sources = set(dereference(doc, props["source"])["enum"])
    assert sources and sources <= {"live", "replay", "yahoo", "manual"}


@pytest.mark.parametrize("path,method,status", [
    ("/v1/link", "post", 400), ("/v1/profile", "get", 401),
    ("/v1/profile", "get", 403), ("/v1/profile", "put", 409),
    ("/v1/link/confirm", "post", 410), ("/v1/link", "post", 429),
    ("/v1/panel", "get", 503),
])
def test_openapi_declares_safe_structured_errors_for_all_contract_statuses(path, method, status):
    doc = document("src/api/openapi.yaml")
    props, required = properties(doc, response_schema(doc, path, method, status))
    assert "error" in props and "error" in required
    fields, names = properties(doc, props["error"])
    assert {"code", "message"} <= names
    assert all(dereference(doc, fields[key])["type"] == "string" for key in ["code", "message"])


@pytest.mark.parametrize("path,raw", [("/v1/link", "{"), ("/v1/link/confirm", "[]")])
def test_malformed_body_returns_400_without_partial_link_mutation(api, path, raw):
    before = {k: table.scan()["Items"] for k, table in api.tables.items()}
    status, body = api.request("POST", path, raw=raw)
    assert_error(status, body, 400)
    assert {k: table.scan()["Items"] for k, table in api.tables.items()} == before


def test_body_larger_than_64_kib_is_rejected_before_any_link_mutation(api):
    before = {k: table.scan()["Items"] for k, table in api.tables.items()}
    status, body = api.request("POST", "/v1/link", raw='{"padding":"' + "x" * 65536 + '"}')
    assert_error(status, body, 400)
    assert {k: table.scan()["Items"] for k, table in api.tables.items()} == before


@pytest.mark.parametrize("path", [])
def test_future_module_stubs_surface_503_not_implemented(api, path):
    _, token = link_device(api)
    status, body = api.request("GET", path, token=token, query={"profileId": "owner"})
    assert_error(status, body, 503, "not_implemented")


def test_phone_link_page_exposes_customer_confirmation_form(api):
    status, page = api.request("GET", "/link")
    assert status == 200 and isinstance(page, str)
    assert "<form" in page and 'name="code"' in page
    assert 'type="password"' not in page, "Code-only linking (DEC-AFC-SD-048) has no secret field"
