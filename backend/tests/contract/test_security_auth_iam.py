"""SEC-2: the public API does not need access to Yahoo credentials."""

import json

import pytest

from conftest import document

pytestmark = pytest.mark.contract


def test_api_has_no_ssm_parameter_read_grant():
    policies = document("template.yaml")["Resources"]["ApiFunction"]["Properties"]["Policies"]
    policy = json.dumps(policies).lower()
    assert "ssm:" not in policy and "ssmparameter" not in policy, \
        "ApiFunction must not read Yahoo SSM parameters; it has no secret-reading caller"
