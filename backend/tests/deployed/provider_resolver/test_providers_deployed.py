"""Deployed provider resolver cases (SEIT-AFC-PR-004, -029, -032, -033; L03 execution).

The deployed API resolves an access basis from the frozen enum and never
reads verified from an installed-app report alone. Without
AFC_DEPLOYED_API_URL these skip (NOT_RUN) like every deployed case.
"""

from deployed_helpers import assert_error, call

BASES = ("verified", "customerConfirmed", "unknown")


def test_installed_report_is_accepted(linked):
    status, body = call(linked.base, "POST", "/v1/installed-apps", token=linked.token,
                        body={"packages": ["test.deployed.absent"]})
    assert status == 200, body


def test_providers_reads_an_access_basis_never_verified_from_install(linked):
    call(linked.base, "POST", "/v1/installed-apps", token=linked.token,
         body={"packages": ["test.deployed.absent"]})
    status, body = call(linked.base, "GET", "/v1/providers", token=linked.token)
    assert status == 200, body
    assert body.get("accessBasis") in BASES, body
    assert body.get("accessBasis") != "verified", body


def test_invented_routing_outcome_is_rejected(linked):
    status, body = call(linked.base, "POST", "/v1/routing-outcome", token=linked.token,
                        body={"eventId": "evt-deployed", "outcome": "launched"})
    assert_error(status, body, 400)
