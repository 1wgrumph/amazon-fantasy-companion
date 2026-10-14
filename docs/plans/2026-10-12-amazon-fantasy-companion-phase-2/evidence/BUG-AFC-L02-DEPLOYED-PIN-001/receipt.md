# BUG-AFC-L02-DEPLOYED-PIN-001

Outcome: **PASS** for the assigned Implementer packet; candidate ready for the
parent's independent review. This is author realization evidence, not assurance
or deployed acceptance. Baseline `3ff9a3560cc3c00bf471a1429e35352faf78768f`;
branch `afc/bug-deployed-pin`; route Codex CLI / GPT-6.1 Sol / high;
profile bug-triager. No route or profile change. Commit identity is the Git
commit containing this receipt; code/log hashes and identical red/green IDs
are bound in [verification-binding.json](verification-binding.json).

## Reproduction, origin and escape

**Test-only harness defect, not a backend product defect.** P2-B01T/B01 introduced
the deployed harness; `7eaa700` introduced this conftest. It compared the URL's
hostname to an already-resolved numeric socket address, preventing HTTPS from
reaching the configured API. The prior P2-L02 device-auth smoke on local branch
`afc/p2-l02` recorded three failures and one skip; that evidence was inspected
read-only, with no network replay. The escape was lack of a normal unit case
for this guard: the gate excludes deployed tests, and unconfigured deployed
runs skip. [reproduction.txt](reproduction.txt) binds the installed standard
library resolution/connection boundary and the prior source evidence.

The new ordinary unit file invokes the real fixture with owner-authorized DNS
and connection stubs. On the original fixture, allowed IPv4/IPv6 destinations
fail with `Deployed test may only contact api.example.invalid`. The same tests
also expose configured `connect_ex` lacking containment. [red.txt](red.txt):
**11 failed, 15 passed**, exit 1, before editing the fixture. No frozen tests
were edited and no backend product code changed.

## Fix and regression

Resolve the configured host once per fixture setup with `getaddrinfo`, retaining
its IPv4/IPv6 family/address pairs. Pin both `connect` and `connect_ex` to that
set, preserving each original method's result. Reject other families before
indexing their address, so Unix addresses fail with an assertion rather than a
guard crash. A missing URL retains rejection of both methods without DNS; a
URL without a hostname fails closed before resolution.

[green.txt](green.txt): **26 passed**, exit 0, over the identical 26 test IDs.
The tests cover two allowed IPv4 addresses, one allowed IPv6 address, foreign
IPv4/IPv6 addresses, foreign and unresolved hostnames, Unix string/bytes and
address-family mismatch, and no-URL rejection for IPv4/IPv6/Unix. All connect
and connect_ex calls terminate in stubs or guard assertions; no real DNS,
network connection or AWS call occurred. Sockets are closed by context managers;
no bound port, server, engine or shared resource was created. Focused green
runtime: 0.03 seconds.

## Commands and prevention

For verification, PATH contains `$HOME/.local/share/afc-tools/backend-tests/bin`.
Every substantive command is bounded with `timeout 600`. `UV_OFFLINE=1` disables
package fetching during the full gate. Gate diagnostic lines from intentional
negative CI cases and existing botocore deprecation warnings are retained;
these are not new defects or missing evidence.

| Command | Exit | Result/evidence |
| --- | --- | --- |
| `python3.12 -m pytest backend/tests/unit/test_deployed_guard.py -v --tb=short --show-capture=no` before fix | 1, expected | [red.txt](red.txt): 11 failed, 15 passed |
| Same command after fix | 0 | [green.txt](green.txt): 26 passed |
| `UV_OFFLINE=1 PATH="$HOME/.local/share/afc-tools/backend-tests/bin:$PATH" timeout 600 bash tools/ci/gate.sh` | 0 | [gate.txt](gate.txt): all areas PASS; 61 CI tests, 184 backend tests |
| Red/green test-ID and output assertions | 0 | [verification-binding.json](verification-binding.json): identical ordered IDs and code/log SHA-256 |

Exact normal prevention command:
`PATH="$HOME/.local/share/afc-tools/backend-tests/bin:$PATH" bash tools/ci/gate.sh`.
Its backend area invokes
`python3.12 -m pytest backend/tests/unit backend/tests/contract`, which discovers
the new file without configuration changes. The 184 backend cases comprise
all 158 existing tests plus 26 new cases, all passing. Full backend time was
18.39 seconds; CI tests took 34.801 seconds. No tool or dependency added.

## Acceptance to evidence

| Acceptance | Result | Evidence |
| --- | --- | --- |
| 1. Configured API resolved addresses allowed; all other destinations blocked; non-INET families safe | PASS | Fixture diff; green positive, negative and Unix cases |
| 2a. Allowed resolved address passes | PASS, red then green | Same six IPv4/IPv6/method cases in red.txt and green.txt |
| 2b. Different destination rejected | PASS | Fourteen negative IP/hostname/Unix/method cases in green.txt |
| 2c. No URL rejects every connection | PASS | Six no-URL/family/method cases; stub records no connection or DNS |
| 3. Regression runs in normal unit suite | PASS | gate.txt includes test_deployed_guard.py with 26 passes; exact command above |
| 4. Full gate exits 0; existing backend tests pass | PASS | gate.txt: 184 backend and 61 CI tests; exit_code=0 |
| 5. Receipt includes reproduction, origin/escape, classification, red/green and prevention | PASS | This receipt; reproduction.txt; red.txt; green.txt; verification-binding.json |

## Authority and limits

Only the deployed conftest, one new unit file, and this evidence directory belong
to the candidate. The final write-set check compares `3ff9a35` with the commit.
No src, frozen red tests, tools, workflows or changelog edits. Commit uses Codex
author environment with the repository pre-commit hook active; no Co-Authored-By.
No branch switch, push, PR, GitHub, credential or AWS action. BRAN unavailable;
[execution-binding.md](execution-binding.md) records the packet and next action.

OCR: independent review not run by this worker; parent review settings were not
inferred or altered. Reverify: not applicable, no compiled-binary claim.
Live smoke remains outside this packet. DNS is snapshotted per fixture: if a
later resolution changes to an IP absent from that snapshot, the guard rejects
it; this preserves containment. A passing local harness fix does not claim
live-stack API acceptance or resolve the separate linking-passphrase prerequisite.
