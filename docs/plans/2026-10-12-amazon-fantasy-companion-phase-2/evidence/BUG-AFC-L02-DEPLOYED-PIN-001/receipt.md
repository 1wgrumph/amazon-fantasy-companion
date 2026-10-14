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


## Single repair round after independent REPAIR_REQUIRED — 2026-10-14

Outcome: **PASS** for this assigned repair packet, ready for the parent to
consume deterministic verification. Review candidate/baseline:
`17398092553e2ec963b2e8c521a3dbcd9a072a00`; same branch, worktree and
bug-triager Implementer route (Codex CLI / GPT-6.1 Sol / high). This is the
single authorized repair round, not a second independent review. The commit
containing this receipt identifies the candidate. Earlier snapshot-only DNS
behavior and its stated rotation limitation above are superseded by this repair.

| Finding | Fix | Regression | Evidence |
| --- | --- | --- | --- |
| F1: urllib/create_connection re-resolves a rotating API host, but new IPs were absent from the setup snapshot | Wrap getaddrinfo for the session; add returned AF_INET/AF_INET6 pairs only when queried_host equals the configured API host | Real create_connection with a stub resolver returning a new IPv4 or IPv6 address on call two succeeds; resolving a different host still cannot authorize its IP | repair-red.txt: four rotation failures; repair-green.txt: all six rotation/foreign-host cases pass |
| F2: session linked setup ran before the function guard | Session autouse offline fixture uses pytest.MonkeyPatch.context(); deployed explicitly depends on offline; direct unit harness starts/closes the generator | Isolated real pytest scheduler runs actual offline/deployed/linked fixtures; the stub HTTP helper probes allowed and forbidden connections during all three link calls | repair-red.txt: test_guard_precedes_session_link_flow fails because the forbidden connect does not raise; repair-green.txt: it passes |
| Hardening: destination sends bypassed the guard | Apply the same family/address check to sendto and addressed sendmsg; no URL blocks all four socket methods | Configured API IPv4/IPv6 sends succeed, foreign IPv4/IPv6 and Unix destinations fail, and no URL rejects every destination for both methods | repair-red.txt: 32 send failures; repair-green.txt: all 40 addressed-send cases pass |

The installed standard library calls `getaddrinfo(host, port, 0, SOCK_STREAM)`
inside create_connection on every invocation, and only catches socket errors
when connecting. That explains the AssertionError escape. Its real source and
sendto/sendmsg destination signatures are captured in
[repair-dependency.txt](repair-dependency.txt). Stub inputs are the owner-required
DNS rotation and destinations using reserved documentation IPs and .invalid
hosts. No live DNS, network, AWS or credential calls were made. The isolated
pytest child disables plugin autoload and cache writes; its DNS, connection
methods and link helper are stubbed before fixture setup.

The initial deployed harness introduced the pinning problem; this review
identified two escapes in the first repair's tests: they exercised only a
stable DNS snapshot and invoked the guard directly, bypassing pytest ordering.
The new regressions exercise those real standard-library and pytest boundaries.
The original 26 tests and their assertions remain; the only post-red test-harness
adaptation starts the new fixture generator and registers close for teardown.
No backend behavior, requirements, plan scope, models or frozen routes changed.
Normal gate discovery automatically includes every regression, preventing
recurrence without new configuration or dependencies.

| Command | Exit | Result/evidence |
| --- | --- | --- |
| `PATH="$HOME/.local/share/afc-tools/backend-tests/bin:$PATH" timeout 600 python3.12 -m pytest backend/tests/unit/test_deployed_guard.py -v --tb=short --show-capture=no` before repair | 1, expected | [repair-red.txt](repair-red.txt): 37 failed, 36 passed on unchanged 1739809 fixture |
| Same focused command after repair | 0 | [repair-green.txt](repair-green.txt): 73 passed, including all 26 original guard cases |
| `UV_OFFLINE=1 PATH="$HOME/.local/share/afc-tools/backend-tests/bin:$PATH" timeout 600 bash tools/ci/gate.sh` | 0 | [repair-gate.txt](repair-gate.txt): all five gate areas PASS; 231 backend tests passed |
| Ordered test-ID and baseline/source/log hash assertions | 0 | [repair-binding.json](repair-binding.json): identical 73 red/green IDs, all original 26 IDs retained, unchanged baseline fixture hash and candidate source/log hashes |

UV_OFFLINE prevents dependency fetching; gate diagnostics from intentional
negative CI tests and pre-existing botocore deprecations remain in the log.
Focused green took 0.29 seconds (including isolated pytest scheduling); backend
suite took 18.25 seconds in the final full gate. Resource group remains host-pytest: no bound port,
server, engine, display or external shared resource. Temporary child files use
pytest's per-test tmp_path; sockets are context-managed. Session monkeypatches
are restored at fixture teardown, including direct unit-harness teardown.

Authority remains exactly the two allowed test files and this evidence directory.
No push, PR, branch switch, source/tools/workflow/changelog edits or issue action.
Commit uses Codex author/committer environment, active repository hooks and no
Co-Authored-By. BRAN remains unavailable. OCR is the parent's independent review
capability; no additional review was run or claimed here. Reverify: not applicable
— Python fixture changes make no compiled-binary claim. Live smoke and deployed
acceptance remain outside this no-network repair packet.

Red output has trailing whitespace stripped for repository hygiene; the raw
and stored log hashes are both retained in repair-binding.json. Test output,
IDs and failure details are otherwise unchanged.

The first commit attempt exited 1: the active pre-commit path-hygiene check
found private home paths in newly staged raw test logs. No commit was created.
Logs now use <home>, <repo> and <pytest-tmp> placeholders, matching prior evidence;
raw hashes remain recorded. This evidence-only correction changes no test or
guard code. Full gate and commit hook are rerun after normalization.

Final full gate after evidence normalization: exit 0, all five areas PASS,
61 CI tests and 231 backend tests passed. The next commit retry retains hooks.
