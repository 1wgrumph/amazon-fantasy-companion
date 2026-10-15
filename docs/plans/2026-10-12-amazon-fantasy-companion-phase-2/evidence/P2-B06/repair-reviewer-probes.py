import sys, json, logging
from pathlib import Path
from contextlib import contextmanager

sys.path[:0] = [
    str(Path("backend/src").resolve()),
    str(Path("backend/tests").resolve()),
]
import pytest, conftest

logging.disable(logging.CRITICAL)

@contextmanager
def offline_api():
    with pytest.MonkeyPatch.context() as patch:
        conftest.offline.__wrapped__(patch)
        fixture = conftest.api.__wrapped__(patch, None)
        api = next(fixture)
        try:
            _, token = conftest.link_device(api)
            yield api, token, patch
        finally:
            fixture.close()

with offline_api() as (api, token, patch):
    print("F1 scalar PUT:", api.request(
        "PUT", "/v1/profile",
        {"revision": 0, "data": {"providerPref": "x"}}, token=token)[0])
    print("F1 scalar GET:", api.request(
        "GET", "/v1/providers", token=token))

with offline_api() as (api, token, patch):
    import provider_resolver
    patch.setattr(provider_resolver, "event_channel", lambda event: "ESPN")
    patch.setattr(provider_resolver, "REGISTRY_PATH",
                  Path("backend/tests/unit/provider_resolver/registry/example.json"))
    api.request("POST", "/v1/installed-apps",
                {"packages": ["test.alpha.firetv"]}, token=token)
    for revision, claim in enumerate([
        {"alpha_stream": False}, "not_alpha_stream", [], ["alpha_stream"],
    ]):
        pref = {"order": ["alpha_stream"], "confirmedAccess": claim,
                "appOverrides": {}, "localMarket": None}
        print("F1 claim PUT:", api.request(
            "PUT", "/v1/profile",
            {"revision": revision, "data": {"providerPref": pref}}, token=token)[0])
        status, result = api.request(
            "GET", "/v1/providers", token=token, query={"eventId": "fixture-event"})
        print("F1 claim result:", repr(claim), status, result["accessBasis"])

with offline_api() as (api, token, patch):
    packages = ["x" * 255] * 252 + ["y" * 250]
    body = {"packages": packages}
    print("F2 request bytes:", len(json.dumps(body).encode()))
    print("F2 echoed response bytes:", len(json.dumps(
        {"profileId": "owner", "packages": packages}).encode()))
    print("F2 response:", api.request(
        "POST", "/v1/installed-apps", body, token=token))
    stored = api.table("Profiles").get_item(
        Key={"profileId": "providerState#owner"}).get("Item", {})
    print("F2 stored despite 503:", stored.get("installedPackages") == packages)
