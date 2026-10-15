# B06 review repair: author verification PASS

Candidate readiness: CANDIDATE_READY after one repair of B06-REV-001 and B06-REV-002. Baseline 9bfa17a50469c2d1725c9db8b03ab3e9b4839817 on afc/p2-b06t; repair commit is the containing commit. No second review or independent assurance is claimed.

| Acceptance | Evidence | Result |
| --- | --- | --- |
| B06-REV-001 malformed preferences preserve unknown resolution | repair-probes-before.txt, repair-probes-after.txt; scalar PUT remains 200, GET changes 503 to 200 unknown | PASS |
| Confirmation requires a provider-ID list naming the selected provider | malformed dict/string become unknown; empty/other-provider lists remain unknown; valid list remains customerConfirmed; mixed lists fail closed | PASS |
| Nested preference fields cannot crash or fabricate detection | repair-red.txt / repair-green.txt cover order, overrides, localMarket and malformed confirmations | PASS |
| B06-REV-002 exact 65536-byte input persists with bounded success | same 253 packages; HTTP changes 503 to 200 with {"profileId":"owner"}; persistence asserted | PASS |
| Frozen tests/support/fixture unchanged | repair-frozen-hashes.txt, 8/8 SHA-256 matches | PASS |
| Full gate | repair-gate.txt, exit 0; spec/docs/hygiene/tvapp/backend PASS, 447 backend cases | PASS |
| Write set and whitespace | explicit path inventory and git diff --check; B06T/gate.txt differs only by trailing whitespace | PASS |

## Commands

- Reviewer script, before and after: `PYTHONDONTWRITEBYTECODE=1 "$HOME/.local/share/afc-tools/backend-tests/bin/python3.12" docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B06/repair-reviewer-probes.py`. Both commands exit 0 because the unchanged reviewer script prints observations; assertions are in pytest. Its unchanged final label "stored despite 503" means "stored equals submitted"; the repaired response above that label is 200.
- Red and green: `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$HOME/.local/share/afc-tools/backend-tests/bin/python3.12" -m pytest backend/tests/unit/provider_resolver/test_resolver_preference_shapes.py backend/tests/unit/test_router.py -k 'opaque or explicit_provider or malformed_nested or non_boolean or maximum_size or stub_routes_receive' -v -p no:cacheprovider --tb=short --show-capture=no`. Red exit 1: 21 failed, 5 passed; green exit 0: 26 passed. Same case IDs, no assertion weakening. Twenty-five additive cases plus the existing caller test; focused run 2.78 seconds, no server/shared resource.
- Frozen verification: SHA-256 every path in B06T receipt `frozen_test_sha256` and `frozen_fixture_sha256`, assert eight matches.
- Gate: `JAVA_HOME="$HOME/.local/share/afc-tools/jdk-17.0.20.1+1" ANDROID_HOME="$HOME/.local/share/afc-tools/android-sdk" GRADLE_USER_HOME="$HOME/.gradle/afc-p2-b06t" PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 timeout 900 bash tools/ci/gate.sh`. Exit 0; backend 447 passed in 23.73 seconds.
- `git diff --check 71d3e64`; exit 0.

## Scope and prevention

The resolver checks the opaque preference mapping, string market, string-list order and confirmation, and Boolean override entries. Invalid values are ignored without changing saved Settings. Only an explicit list containing the selected provider yields customerConfirmed; no automated entitlement verification is added. The API acknowledges detector persistence with profileId, preserving the resolver direct-call package return contract. The TV client already ignores the response body. API acceptance and package limits are unchanged. The existing unfrozen caller test now expects the bounded acknowledgement and still checks every forwarded argument.

Original fault/escape: B06 assumed well-shaped opaque preferences and tested well-shaped access claims; it also echoed a valid detector request after mutation without accounting for response overhead. New malformed-input cases and the exact observed HTTP boundary guard those assumptions. The baseline red failures are expected product-defect evidence, not harness/configuration failures. Gate hygiene tests emit intentional negative-test messages; dependency deprecation warnings are not failures.

Pre-existing limitations remain: production broadcast source and registry/deployed route proof, the earlier typed mutation GAP, and formal deployed assurance. Previous coverage/mutation receipts are historical and do not certify this repair. Frozen coverage_assist stays enabled/required; the consumed independent review used available OpenCodeReview delegation. No new review ran. Reverify stays enabled and is not applicable to these Python source changes; no compiled-binary properties are claimed. BRAN unavailable (no native policy). No live AWS/device check, push, PR, credentials, issue mutation, runtime deployment, or publication.
