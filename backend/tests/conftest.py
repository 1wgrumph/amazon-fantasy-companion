"""Offline host-pytest fixtures, no server, shared resource or real AWS.

Inputs: committed DES-AFC-P2-BACKEND/AUTH and CONTRACT-AFC-P2-API/ENVELOPE.
Moto exercises the installed botocore DynamoDB/SSM protocols in-process.
The product template owns key schemas and environment names; fresh tables,
sessions and synthetic secrets belong to one test and are discarded on exit.
"""

import importlib
import json
import socket
import sys
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode

import boto3
import pytest
import yaml
from botocore.client import BaseClient
from moto import mock_aws

BACKEND = Path(__file__).resolve().parents[1]


class SamLoader(yaml.SafeLoader):
    """Keep SAM intrinsic tags as data for offline fixture resolution."""


def intrinsic(loader, tag, node):
    value = (loader.construct_scalar(node) if isinstance(node, yaml.ScalarNode)
             else loader.construct_sequence(node) if isinstance(node, yaml.SequenceNode)
             else loader.construct_mapping(node))
    return {tag if tag == "Ref" else "Fn::" + tag: value}


SamLoader.add_multi_constructor("!", intrinsic)


def document(relative):
    path = BACKEND / relative
    assert path.is_file(), f"Required backend contract artifact is absent: {relative}"
    result = yaml.load(path.read_text(), Loader=SamLoader)
    assert isinstance(result, dict), f"{relative} must be a YAML mapping"
    return result


def scalar_values(value):
    if isinstance(value, dict):
        return [v for x in value.values() for v in scalar_values(x)]
    if isinstance(value, list):
        return [v for x in value for v in scalar_values(x)]
    return [value]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def reject_network(*args, **kwargs):
        raise AssertionError("Offline test attempted a real socket connection")

    monkeypatch.setattr(socket.socket, "connect", reject_network)
    monkeypatch.setattr(socket.socket, "connect_ex", reject_network)
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.delenv("AWS_SESSION_TOKEN", raising=False)
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    # Never inspect the owner's credential/config files, even during import.
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", "/dev/null")
    monkeypatch.setenv("AWS_CONFIG_FILE", "/dev/null")


@pytest.fixture
def api(monkeypatch, offline):
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        template = (document("template.yaml") if (BACKEND / "template.yaml").exists()
                    else {})
        refs = {k: v.get("Default", "test-" + k)
                for k, v in template.get("Parameters", {}).items()}
        refs.update({"AWS::Region": "us-east-1", "AWS::AccountId": "123456789012",
                     "AWS::StackName": "afc-test", "AWS::Partition": "aws"})

        def resolve(value):
            if isinstance(value, list):
                return [resolve(x) for x in value]
            if not isinstance(value, dict):
                return value
            if "Ref" in value:
                return refs[value["Ref"]]
            if "Fn::Sub" in value:
                sub = value["Fn::Sub"]
                text, extra = (sub, {}) if isinstance(sub, str) else sub
                for key, val in dict(refs, **{k: resolve(v) for k, v in extra.items()}).items():
                    text = text.replace("${" + key + "}", str(val))
                return text
            if "Fn::GetAtt" in value:
                att = value["Fn::GetAtt"]
                target, attr = att.split(".", 1) if isinstance(att, str) else att
                return f"arn:aws:dynamodb:us-east-1:123456789012:table/{refs[target]}"
            return {k: resolve(v) for k, v in value.items()}

        resources = template.get("Resources", {})
        for name, resource in resources.items():
            if resource["Type"] == "AWS::DynamoDB::Table":
                refs[name] = resolve(resource["Properties"].get("TableName", name))
        tables = {}
        ttls = {}
        for name, resource in resources.items():
            if resource["Type"] != "AWS::DynamoDB::Table":
                continue
            props = resolve(resource["Properties"])
            args = {k: props[k] for k in ["KeySchema", "AttributeDefinitions",
                                          "GlobalSecondaryIndexes", "LocalSecondaryIndexes"]
                    if k in props}
            table = dynamodb.create_table(TableName=refs[name], BillingMode="PAY_PER_REQUEST",
                                          **args)
            tables[name] = table
            ttl = props.get("TimeToLiveSpecification", {})
            if ttl.get("Enabled"):
                ttls[name] = ttl["AttributeName"]

        env = template.get("Globals", {}).get("Function", {}).get("Environment", {}).get("Variables", {})
        function = resources.get("ApiFunction", {}).get("Properties", {})
        env = dict(env, **function.get("Environment", {}).get("Variables", {}))
        env = resolve(env)
        for key, value in env.items():
            monkeypatch.setenv(key, str(value))
        ssm_reads = []
        original_call = BaseClient._make_api_call

        def observe_ssm(client, operation, params):
            if client.meta.service_model.service_name == "ssm" and operation == "GetParameter":
                ssm_reads.append({"Name": params.get("Name"),
                                  "WithDecryption": params.get("WithDecryption")})
            return original_call(client, operation, params)

        monkeypatch.setattr(BaseClient, "_make_api_call", observe_ssm)
        # Each invocation sees only this test's clients/table state, never a cached prior session.
        for name in list(sys.modules):
            module = sys.modules[name]
            file = getattr(module, "__file__", None)
            if file and Path(file).is_relative_to(BACKEND / "src"):
                monkeypatch.delitem(sys.modules, name)

        def request(method, path, body=None, token=None, query=None, raw=None):
            headers = {"content-type": "application/json"}
            if token is not None:
                headers["authorization"] = "Bearer " + token
            event = {"version": "2.0", "routeKey": method + " " + path,
                     "rawPath": path, "rawQueryString": urlencode(query or {}),
                     "headers": headers, "queryStringParameters": query or {},
                     "requestContext": {"requestId": "afc-test", "http": {
                         "method": method, "path": path, "sourceIp": "127.0.0.1",
                         "protocol": "HTTP/1.1", "userAgent": "afc-offline-test"}},
                     "body": raw if raw is not None else json.dumps(body or {}),
                     "isBase64Encoded": False}
            entry = function.get("Handler", "api.handler.lambda_handler")
            module, name = entry.rsplit(".", 1)
            handler = getattr(importlib.import_module(module), name)
            try:
                response = handler(event, SimpleNamespace(aws_request_id="afc-test"))
            except NotImplementedError:
                assert False, f"{method} {path}: API behavior is not implemented (AFC-STUB)"
            assert isinstance(response, dict), "Lambda proxy response must be a mapping"
            assert isinstance(response.get("statusCode"), int), "HTTP statusCode is required"
            payload = response.get("body", "")
            content_type = {k.lower(): v for k, v in response.get("headers", {}).items()}.get(
                "content-type", "")
            if "text/html" in content_type:
                return response["statusCode"], payload
            assert isinstance(payload, str), "HTTP API proxy body must be serialized JSON"
            assert len(payload.encode()) <= 65536, "Response body exceeds the 64 KiB contract"
            try:
                data = json.loads(payload)
            except (ValueError, TypeError):
                assert False, "API response must contain valid JSON"
            return response["statusCode"], data

        def table(logical_name):
            name = logical_name if logical_name in tables else logical_name + "Table"
            assert name in tables, f"Template must declare {logical_name} table"
            return tables[name]

        yield SimpleNamespace(request=request, table=table, tables=tables, ttls=ttls,
                              ssm_reads=ssm_reads)


def assert_error(status, body, expected, code=None):
    assert status == expected, f"Expected HTTP {expected}, received {status}"
    assert isinstance(body, dict) and isinstance(body.get("error"), dict)
    error = body["error"]
    assert isinstance(error.get("code"), str) and error["code"]
    assert isinstance(error.get("message"), str) and error["message"]
    if code is not None:
        assert error["code"] == code


def issue(api):
    status, body = api.request("POST", "/v1/link")
    assert status in (200, 201), "Device-code initiation must succeed without a session"
    assert isinstance(body, dict)
    assert all(isinstance(body.get(key), str) and body[key] for key in ["code", "expires", "handle"])
    return body


def confirm(api, code, profile="owner"):
    return api.request("POST", "/v1/link/confirm", {"code": code, "profileId": profile})


def link_device(api, profile="owner"):
    device = issue(api)
    status, confirmation = confirm(api, device["code"], profile=profile)
    assert status in (200, 201), "Authenticated customer confirmation must link the device"
    status, polled = api.request("GET", "/v1/link", query={"handle": device["handle"]})
    assert status == 200 and polled.get("state") == "linked"
    # The design permits delivery in confirmation or polling; the TV polling path remains observable.
    token = polled.get("sessionToken", confirmation.get("sessionToken"))
    assert isinstance(token, str) and token, "Linking must issue an opaque device session token"
    return device, token
