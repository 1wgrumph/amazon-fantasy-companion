# Developer feedback — observations index (Phase 2, assembled 2026-10-20)

Slice P2-SCR1, issue #51, acceptance `AC-AFC-P2-DX-02`. Assembled by the Scribe
from the `developer_feedback` sections of Phase 2 packets, returns, receipts and
spike verdicts, plus the three earlier Scribe notes. Feedback stays local;
sending it to Amazon, Yahoo or anyone else is owner action OA-8.

Counts (verified 2026-10-20 by counting rows): 87 observation rows (OBS-IDs in
sections A-K), 25 friction entries (`friction-log.md`), 24 feature requests
(`feature-requests.md`).

Rules for this index:

- Every entry cites the source observation ID where one exists (`src`). A field
  the source did not state is written "not observed in available evidence".
- Durations appear only where a source recorded them. Spike windows are the
  `started_at`/`ended_at` front matter of a verdict and include waiting.
- Class: **product** = behavior of a vendor tool, API, SDK, service or device;
  **process** = behavior of this project's own workflow, packets, gates or
  agent routing. A failed request alone is not a vendor defect; nothing here is
  filed as a vendor bug.
- Type: positive, doc-gap, prereq (expected prerequisite), env (configuration or
  environment), limit (platform limitation), defect-candidate (not reproduced
  as a vendor defect).

Path prefixes used in evidence pointers:

| Prefix | Expands to |
|---|---|
| `P2/` | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/` |
| `P1/` | `docs/plans/2026-10-11-amazon-fantasy-companion/` |
| `REC/` | `P2/recovery-m03-m05/` |
| `FB/` | `docs/developer-feedback/` |
| `SP-n` | `spikes/<spike>/VERDICT.md` (sp1-device, sp2-notify, sp3-provider-links, sp4-panel-video, sp5-espn-feed, sp6-yahoo, sp7-detection) |

Pointers marked **(branch-only)** live on the M03-M05 recovery coordinator branch
and are not on `main` at baseline `350ef51`; they resolve once that branch lands.
Pointers marked **source_not_durable** were checked against `git ls-files` on this
branch (HEAD `960ffe2` plus base `350ef51`) and exist only as local or untracked
files or as transient notices; they are not on any inspected ref. No path was
substituted for them (see the typed gap under "Gaps and pending sources").
The earlier Scribe notes remain in place and are indexed here, not replaced (see
"Reconciliation with earlier notes").

## A. Fire TV stick, Fire OS and ADB

| ID | Tool / device | Observation | Class · type | Evidence | src |
|---|---|---|---|---|---|
| OBS-001 | Fire TV Stick 4K (model AFTKM, Fire OS 8.1.8.5, API 30), network ADB | Starter installed and launched over network ADB; the on-TV RSA prompt had to be accepted by the owner; display reports physical 3840x2160 with a 1920x1080 override. Spike window 2026-10-14 to 2026-10-16T12:20Z. | product · positive | `spikes/sp1-device/VERDICT.md` | SP-1 |
| OBS-002 | `adb shell monkey` | In the repair re-check, `monkey` launch exited 251 without resuming the activity; `am start` then resumed it. | product · defect-candidate | `spikes/sp1-device/VERDICT.md` route 3 | SP-1 |
| OBS-003 | Fire OS notifications | A foreground-service notification (high-importance channel, Watch/Dismiss actions, `PRIORITY_HIGH`, sound and vibrate, full-screen intent) posts, but no heads-up banner appears over Prime Video playback or elsewhere. Spike window 2026-10-16T19:35Z to 20:36Z. | product · limit | `spikes/sp2-notify/VERDICT.md` routes 1-4 | SP-2 |
| OBS-004 | Fire OS Notification Center | The Notification Center shows the foreground-service card, not the alert, and offers only its own Dismiss/Manage buttons, not the alert's actions. | product · limit | `spikes/sp2-notify/VERDICT.md` route 5 | SP-2 |
| OBS-005 | Android `Toast` on Fire OS | A toast renders over Prime Video playback as documented but is display-only (no actions). | product · positive | `spikes/sp2-notify/VERDICT.md` route 6 | SP-2 |
| OBS-006 | Fire OS multi-window, PiP, overlay | No supported route puts a third-party panel beside playing Prime Video: Prime declares no PiP and HOME stops playback; panel PiP (384x216) covers the video; overlay needs a Settings grant and still overlaps; split-screen and freeform launch full-screen. Spike window 2026-10-16T19:07Z to 19:25Z. | product · limit | `spikes/sp4-panel-video/VERDICT.md`; `evidence/visual/sp4-panel-video/commands.txt` | SP-4 |
| OBS-007 | `adb screencap` on provider playback | Playing video captures as a black secure surface; only player chrome and `dumpsys media_session` state evidence playback. | product · limit | `spikes/sp4-panel-video/VERDICT.md` (playback evidence note); `spikes/sp3-provider-links/VERDICT.md` | SP-4, SP-3 |
| OBS-008 | Prime Video deep links on Fire OS | `VIEW https://watch.amazon.com/search` opens Prime Video search; query parameters are ignored; `amzn://avod` and `YAC_LAUNCH` open home; `VIEW .../detail?gti=<title id>` opens a title page. No public deep-link document was found and no mapping from an ESPN event to a Prime title id exists. Game arrival (`gameOpened`) not observed; live check pending X03 PR 2. | product · doc-gap | `spikes/sp3-provider-links/VERDICT.md` | SP-3 |
| OBS-009 | Android intent resolution | A bare `MAIN` intent with only the package set does not resolve; the filter needs the `LEANBACK_LAUNCHER` category. | product · prereq | `spikes/sp3-provider-links/VERDICT.md` | SP-3 |
| OBS-010 | Provider apps on the stick | ESPN, DirecTV Stream and YouTube TV are not installed; their https links open only the Silk browser; the Live TV package exposes no launcher activity and `dumpsys tv_input` lists no broadcast tuner. | product · env | `spikes/sp3-provider-links/VERDICT.md` routes 2-5 | SP-3 |
| OBS-011 | `pm` / `PackageManager` detection | `pm path` shows installed vs absent packages; `pm disable` from the shell fails with `SecurityException: Shell cannot change component state`; in-app `PackageManager` reported installed-enabled, absent and installed-disabled (own fixture package only). Spike window 2026-10-19T11:04Z to 11:26Z. | product · limit | `spikes/sp7-detection/VERDICT.md` | SP-7 |
| OBS-012 | Fire TV input in UI automation | Touch/mouse taps do not click tv-material buttons; D-pad focus plus CENTER does. The Amazon keyboard "Previous" action is the only reliable exit from multiline text fields ("Next" is a no-op). After about 10 minutes idle the screensaver needs WAKEUP+CENTER before a UI dump is meaningful. | product · limit | `REC/landing-projection/records/evidence/device-alert-continuation/receipt.json`; `REC/evidence/device-1/wonder-completion/receipt.json` (source_not_durable) | device-alert-continuation, wonder-completion |
| OBS-013 | `uiautomator dump`, `adb` | `uiautomator dump` text plus focused bounds made D-pad navigation deterministic without screenshots of private surfaces; `flock --close` around each adb client call (daemon started outside the lock) gave zero hangs; logcat worked as a text oracle for a probe flow. | process · positive | `REC/landing-projection/records/evidence/device-1/receipt.json` | device-1 |
| OBS-014 | Companion TV app (own code) | Profile fields are multiline, which forces the keyboard-Previous workaround; D-pad focus order in the nav is non-linear (LEFT/UP cycling). Suggested fix: single-line fields with `ImeAction.Next`, through the normal test-first route. | process · defect-candidate | `REC/landing-projection/records/evidence/device-alert-continuation/receipt.json`; `REC/evidence/device-1/wonder-continuation/receipt.json` (source_not_durable) | device-alert-continuation |
| OBS-015 | `adb install -r` | A same-signer reinstall over the old candidate preserved the synthetic session; the app resumed directly to the profile screen. | product · positive | `REC/evidence/device-1/wonder-continuation/receipt.json` (source_not_durable) | wonder-continuation |
| OBS-016 | Device availability | The owner's stick could not be found on 2026-10-14; the orchestrator noted newer Fire TV Stick models may ship Vega OS, which an Android APK cannot target. The stick was found and qualified on 2026-10-16 (OBS-001). | process · env | `FB/scribe-2026-10-14-catchup.md` O7; `spikes/sp1-device/VERDICT.md` | O7 |
| OBS-017 | Link-code expiry on device | Showing an honest expired state needed a real wait of about 10 minutes; a shorter development TTL fixture would speed future passes. | process · env | `REC/landing-projection/records/evidence/device-1/receipt.json` | device-1 |

## B. Android, Gradle and JDK build toolchain

| ID | Tool | Observation | Class · type | Evidence | src |
|---|---|---|---|---|---|
| OBS-020 | Gradle closure of the Fire TV starter | The starter's closure (AGP 8.2.2, Kotlin 1.9.0) scanned INDETERMINATE; the owner then moved tv-app to AGP 9.3.1, KGP 2.4.21, Gradle 9.7.0 with strict dependency verification and accepted residual build-host risk. | product · env | `FB/scribe-2026-10-14-catchup.md` O4; `P2/evidence/P2-A01T/receipt.json` | O4, DX-P2-A01T-004 |
| OBS-021 | Android instrumented-test runner (UTP) | UTP pulls a netty closure with HIGH/CRITICAL advisories; not admitted on 2026-10-14. Owner decision outcome: not observed in available evidence. | product · env | `FB/scribe-2026-10-14-catchup.md` O5 | O5 |
| OBS-022 | Trivy | Filesystem mode reported zero language files for a JAR-only tree; archive-aware rootfs mode found 98 package identities and 10 HIGH/CRITICAL. Configuration cause, not a product defect. | product · env | `P2/evidence/P2-A01T/receipt.json` | DX-P2-A01T-001 |
| OBS-023 | Android lint compiler 32.4.1 | The newest stable compiler still embeds protobuf/JLine classes tied to 5 HIGH findings; a version constraint cannot replace bundled classes. | product · limit | `P2/evidence/P2-A01T/receipt.json` | DX-P2-A01T-002 |
| OBS-024 | Gradle dependency resolution | One merged passive closure hides versions chosen in separate Kotlin DSL/compiler/lint configurations; split configurations match the real execution graphs. | product · doc-gap | `P2/evidence/P2-A01T/receipt.json` | DX-P2-A01T-004 |
| OBS-025 | `android.jar` for host tests | Host-test compile lacks `JSONObject.keySet()`, JVM-only `JSONObject.similar` and `Files.readString`; workarounds kept the assertions. | product · limit | `P2/evidence/P2-A02T/receipt.json`; `P2/evidence/P2-A01T/receipt.json` | DX-P2-A02T-01, DX-P2-A01T-005 |
| OBS-026 | Kotlin + JUnit 4 | A `@Test` written as `= runBlocking { use { ... } }` takes its last expression's type; a non-Unit result makes JUnit 4 raise `initializationError` ("should be void"), a collection error rather than a red test. | product · prereq | `P2/evidence/P2-A03T/receipt.json` | DX-P2-A03T-01 |
| OBS-027 | Gradle output hygiene | Gradle logs carry a trailing-space line, a CRLF wrapper and an absolute worktree path in the failing-test report; each trips the repository whitespace/private-path gates until normalized at capture. | process · env | `P2/evidence/P2-A03T/receipt.json`; `P2/evidence/P2-A03/receipt.json`; `P2/evidence/P2-A05/receipt.json`; `P2/evidence/P2-A01T/receipt.json` | DX-P2-A03T-02, DX-A03-01, DX-P2-A05-01, DX-P2-A01T-006 |
| OBS-028 | Gradle / Android SDK discovery | The packet's red command fails with "SDK location not found" unless `ANDROID_HOME`/`JAVA_HOME` point at the tool installs the gate discovers itself. | process · prereq | `P2/evidence/P2-A03/receipt.json` | DX-A03-02 |
| OBS-029 | `aapt2` / `d8` / `apksigner` | A manual build with these tools avoided a Gradle/AGP download and became the offline recipe for an APK. | process · positive | `REC/evidence/wonder-trial-x07-offline/receipt.json` (source_not_durable) | wonder-trial-x07-offline |

## C. TV app stack and cross-tier contracts

| ID | Tool | Observation | Class · type | Evidence | src |
|---|---|---|---|---|---|
| OBS-030 | OpenAPI contract (`openapi.yaml`) | `/v1/panel` data was typed as a free object, so the TV and backend suites each assumed a PanelState shape (`PANEL_WIRE_UNFROZEN`); fixtures pinned it on both sides. | process · defect-candidate | `P2/evidence/P2-A05T/receipt.json`; `P2/evidence/P2-B07T/receipt.json`; `P2/evidence/P2-A05/receipt.json` | DX-P2-A05T-01, P2B07T-DX-005, DX-P2-A05-02 |
| OBS-031 | TV Watch launcher design | The route type carried no event id, a stub test pinned the old `launch()`, the activity finished immediately for lack of a caller contract, and an intent `?query` suffix had no documented Android mapping. | process · doc-gap | `P2/evidence/P2-A04T/receipt.json`; `P2/evidence/P2-A04/receipt.json` | DX-P2-A04T-01/02, DX-P2-A04-01/02/03 |

## D. Python backend, pytest, Moto, mutation, coverage, SAM, repository gate

| ID | Tool | Observation | Class · type | Evidence | src |
|---|---|---|---|---|---|
| OBS-040 | pytest + Moto | Red suites of 24 to 80 cases ran offline in about 2 to 27 s (65 cases in 3.57 s) with fresh in-process tables; shared fixtures needed no change. | product · positive | `P2/evidence/P2-B01T/receipt.json`; `P2/evidence/P2-B02T/receipt.json`; `P2/evidence/P2-B03T/receipt.json`; `P2/evidence/P2-B04T/receipt.json`; `P2/evidence/P2-B05T/receipt.json`; `P2/evidence/P2-B07T/receipt.json` | P2B01T-DX-002, P2B02T-DX-001, P2B03T-DX-001, P2B04T-DX-001, P2B05T-DX-001, P2B07T-DX-001 |
| OBS-041 | pytest 8.4.2 JUnit | Failures omit the `type` attribute, so a classifier must read the AssertionError-prefixed message and explicit error/skipped nodes. | product · doc-gap | `P2/evidence/P2-B01T/receipt.json`; `P2/evidence/P2-B02T/receipt.json`; `P2/evidence/P2-B03T/receipt.json` | P2B01T-DX-004, P2B02T-DX-003, P2B03T-DX-002 |
| OBS-042 | pytest conftest import mode | Collecting unit and deployed directories in one call makes `from conftest import ...` resolve to the deployed `conftest.py` (ImportError); suites inline the helper and run deployed tests separately. | product · limit | `P2/evidence/P2-B06T/receipt.json`; `P2/evidence/P2-B05T/receipt.json`; `P2/evidence/P2-B05/receipt.json` | P2B06T-DX-002, P2B05T-DX-002, P2B05-DX-003 |
| OBS-043 | boto3 / Moto | boto3 rejects float seeds (use `Decimal`); a red-seed `TypeError` is a harness defect, not a behavioral signal. | product · prereq | `P2/evidence/P2-B03T/receipt.json` | P2B03T-DX-003 |
| OBS-044 | Moto vs IAM | Moto does not enforce IAM, so the unit suite cannot catch a missing `Scan` or `PutItem` grant; the template's exact-grant contract test needs a paired template change for any new table operation. | product · limit | `P2/evidence/P2-B04T/receipt.json`; `P2/evidence/P2-B04/receipt.json`; `P2/evidence/P2-B07T/receipt.json` | P2B04T-DX-002, P2B04-DX-003, P2B07T-DX-003 |
| OBS-045 | mutmut 3.8.0 | `also_copy` copies only top-level entries; mutated functions become trampolines (AST tests fail in `mutants/`); the default per-mutant timeout trips on a loaded shared host (two full runs timed out disjoint mutant sets while host load was 12 to 20); a calibrated run later scored 99.49% (B01). The evaluator returns a GAP for any changed module-level assignment, making a mutation PASS unreachable for slice B06 (raw score 214/231 reported). | product · limit | `P2/evidence/P2-B01/receipt.json`; `P2/evidence/BUG-AFC-B01-TOOL-001/receipt.json`; `P2/evidence/P2-B06/receipt.json`; `FB/scribe-2026-10-14-catchup.md` O6 | P2B01-DX-001/003, DX-B01T-007/008/009, P2B06-DX-001, O6 |
| OBS-046 | diff-cover 10.6.0 | A changed file with no executable lines (docstring-only `__init__.py`) is absent from `src_stats` and reported REPORT_INCOMPLETE instead of excluded with evidence; the tool has no `__main__`, so `python -m` probes cannot pass. | product · defect-candidate | `P2/evidence/P2-B01/receipt.json`; `P2/evidence/P2-G01/receipt.json` | P2B01-DX-004, G01-DX-02 |
| OBS-047 | Scanner CLIs | Bare launchers bound a different Python environment (explicit `python3.12 -m` worked); Bandit stdout progress is not JSON (use `-o`); latest `setup-java`/`setup-python` bundle HIGH DoS advisories, so the PASS rests on not enabling `cache:`. | product · env | `P2/evidence/P2-B01T/receipt.json`; `P2/evidence/P2-G01/receipt.json` | P2B01T-DX-001, G01-DX-04 |
| OBS-048 | Repository gate (`tools/ci/gate.sh`) | Leaves `__pycache__` directories untracked; prints about 17k warnings (about 320 KB log); product gate tests raised the hygiene suite from 18.8 s to about 35-47 s; measured full gate 41.412 s; in the cloud container the spec area gaps (no `dot`), mutmut/diff-cover/dot are absent and 24 IPv6 guard cases fail (no `AF_INET6`). | process · env | `P2/evidence/P2-A05T/receipt.json`; `P2/evidence/P2-B05T/receipt.json`; `P2/evidence/P2-G01/receipt.json`; `P2/evidence/P2-G01/review/receipt.json`; `P2/evidence/P2-B07T/receipt.json` | DX-P2-A05T-02, P2B05T-DX-004, G01-DX-01, G01-REVIEW-DX-03, P2B07T-DX-004 |
| OBS-049 | Gate qualification | Native coverage is available only under python3.12; passing fixtures did not cover report completeness or changed-scope correctness; native mutation completion leaked its archive; tools appeared mid-run with provenance arriving only by coordinator message. | process · defect-candidate | `P2/evidence/P2-G01T/receipt.json`; `P2/evidence/P2-G01/review/receipt.json`; `P2/evidence/P2-G01/receipt.json` | G01T-DX-01, G01-REVIEW-DX-01/02/04, G01-DX-03 |
| OBS-050 | Stub-pin tests in packets | Product packets did not name the stub-pin test files whose retirement gate exit 0 requires (B04, B05, B06), forcing an unlisted write or a contract failure. | process · defect-candidate | `P2/evidence/P2-B06/receipt.json`; `P2/evidence/P2-B04/receipt.json`; `P2/evidence/P2-B05/receipt.json` | P2B06-DX-002, P2B04-DX-001, P2B05-DX-002 |
| OBS-051 | Data-model gaps found by red suites | `GameEvent` carried no broadcast channel, quarter/scoring flag or per-player statistics, and the store allow-list rejected extra attributes, so resolver, alert and panel logic had no production source at red time; the resolver failed closed. The broadcast channel was later stored and resolved per event (commit c3f459b, PR #114 in the changelog); disposition of quarter and statistics gaps: see changelog entries for the alert policy, panel service and boxscore ingest. | process · defect-candidate | `P2/evidence/P2-B06T/receipt.json`; `P2/evidence/P2-B05T/receipt.json`; `P2/evidence/P2-B07T/receipt.json`; `CHANGELOG.md` | P2B06T-DX-001, P2B05T-DX-003, P2B07T-DX-002, P2B06-DX-004 |
| OBS-052 | Store accessor design | `monitoring_profiles()` returns no profile id or lineup source, so the matcher scans the table directly; an accessor returning id, source and starters would serve both ingest and matcher. | process · positive | `P2/evidence/P2-B04/receipt.json` | P2B04-DX-002 |
| OBS-053 | Harness git environment | The launch environment exported an agent committer identity, so the first commit's committer differed from the repository config owner. Disposition: not observed in available evidence. | process · env | `P2/evidence/P2-B06/receipt.json` | P2B06-DX-003 |

## E. AWS (`afc-dev` profile and stack, region us-east-2)

| ID | Tool / service | Observation | Class · type | Evidence | src |
|---|---|---|---|---|---|
| OBS-060 | AWS CLI `aws login` | Choosing "Continue with an active session" ended on a sign-in page with 400 Bad Request; "Sign in to new session" worked; two concurrent `aws login` runs also broke the flow. Observed 2026-10-16. | product · doc-gap | `docs/operations/aws-and-yahoo-setup.md` | setup note |
| OBS-061 | AWS CLI login session | The session expired during the L02 deploy ("Your session has expired. Please reauthenticate using 'aws login'"); the slice waited for the owner to sign in. Time to expiry not recorded. | product · env | `FB/scribe-2026-10-14-catchup.md` O9 | O9 |
| OBS-062 | boto3 vs `aws login` credentials | Local boto3 could not use the login credentials; going through the AWS CLI kept credentials inside the normal session. | product · limit | `REC/landing-projection/records/evidence/device-alert-continuation/receipt.json` | device-alert-continuation |
| OBS-063 | SAM CLI 1.169.0 | `samconfig.toml` with `profile` under global parameters makes `sam build` fail on a machine without that profile (moved to deploy parameters); SAM reads `requirements.txt` from `CodeUri` and honours `--hash` pins via a one-line include; `sam validate --lint` and `sam build` ran offline. | product · doc-gap | `P2/evidence/P2-B01/receipt.json` | P2B01-DX-005/006 |
| OBS-064 | SAM deploy under a timeout | Interactive SAM under `timeout` stopped at the confirmation prompt; a foreground process-group retry succeeded. Local invocation issue, no SAM defect reproduced. | product · prereq | `P2/evidence/P2-L02/receipt.md` | AFC-L02-OBS-005 |
| OBS-065 | CloudFormation / Lambda / API Gateway / DynamoDB deploys | Stack deploys to `afc-dev` reached UPDATE_COMPLETE for L02 (`2d973bd`), L03 interim (`c194dee`) and final (`af0e0ac`, new PlayerStatsTable), then two later redeploys; deployed smoke and suite counts are in the changelog. Deploy durations: not observed in available evidence. | product · positive | `CHANGELOG.md` (L02, L03, #104, #107 entries); `P2/evidence/P2-L02/receipt.md` | L02 receipt |
| OBS-066 | Deployed smoke tests | A network fixture rejected resolved socket addresses (three device-auth failures), and authenticated deployed tests needed a passphrase environment variable not supplied at dispatch (five skipped, never counted as PASS). | process · env | `P2/evidence/P2-L02/receipt.md` | AFC-L02-OBS-003/004 |
| OBS-067 | SSM Parameter Store | Yahoo client id, client secret and refresh token live as SSM parameters (SecureString for the secret and token); the token version incremented from 1 to 2 across SP-6 attempts. Opinion on the service: not observed in available evidence. | product · positive | `docs/operations/aws-and-yahoo-setup.md`; `spikes/sp6-yahoo/VERDICT.md` | SP-6 |

## F. ESPN public JSON endpoints

| ID | Tool | Observation | Class · type | Evidence | src |
|---|---|---|---|---|---|
| OBS-070 | ESPN scoreboard and summary JSON | Both endpoints answered HTTP 200 without authentication for 14 completed games (summary bodies 530,832 to 679,842 bytes); the API is unofficial with no published contract and `cache-control: max-age=1` was seen during the probe. Spike window 2026-10-14T14:47Z to 14:55Z. | product · positive | `spikes/sp5-espn-feed/VERDICT.md` | SP-5 |
| OBS-071 | ESPN schema shape | Top-level `broadcasts` is empty (data is under `header.competitions[0].broadcasts`); plays sit under `drives.previous[].plays[]`; play participants and statistics are `$ref` links to an internal host; one play in game 401872986 has no `wallclock`. | product · doc-gap | `P2/evidence/P2-X05/receipt.md`; `P2/evidence/P2-B02/receipt.json` | X05-OBS-001, P2B02-DX-001 |
| OBS-072 | ESPN play edits | 2,367 of 2,656 plays (89%) carry a `modified` time over an hour after `wallclock`; `modified` has minute precision, so correction timing cannot be derived from a final snapshot. Live correction evidence pending X05 PR 2 and X09 (2026-10-23T00:15Z). | product · limit | `spikes/sp5-espn-feed/VERDICT.md`; `P2/evidence/P2-X05/receipt.md` | X05-OBS-002 |
| OBS-073 | ESPN body stability | Two captures minutes apart had equal byte lengths but different hashes for a STATUS_FINAL game. | product · limit | `REC/landing-projection/records/evidence/live-prep/receipt.json` | live-prep |
| OBS-074 | ESPN terms | Terms of use for the unofficial JSON in a public submission is an open owner question (OA-6). | process · prereq | `spikes/sp5-espn-feed/VERDICT.md` (limits) | SP-5 |

## G. Yahoo Fantasy API (no live Yahoo data used)

| ID | Tool | Observation | Class · type | Evidence | src |
|---|---|---|---|---|---|
| OBS-080 | Yahoo OAuth + Fantasy API | The OAuth refresh-token grant returned HTTP 200 on both attempts, but the Fantasy API returned 403 "This application is not authorized to perform this action" for the unapproved app, with and without the `fspt-r` scope; no league, roster or settings body was read. Spike window 2026-10-16T14:18Z to 15:48Z. Public reports cited in the verdict describe the same 403 since July 2026. | product · doc-gap | `spikes/sp6-yahoo/VERDICT.md` | SP-6 |
| OBS-081 | Yahoo developer console | The redirect URI must be https (`oob` is rejected); the app description may not contain the word "Yahoo"; a duplicate app had to be deleted. | product · prereq | `docs/operations/aws-and-yahoo-setup.md` | setup note |
| OBS-082 | Yahoo API access program | An access application was submitted 2026-10-16; approval is not recorded in available evidence. | process · prereq | `spikes/sp6-yahoo/VERDICT.md` | SP-6 |

## H. Agent harnesses, review tooling and planning tooling

| ID | Tool | Observation | Class · type | Evidence | src |
|---|---|---|---|---|---|
| OBS-090 | Claude Code | The weekly usage limit ended two dispatches with exit 1 before any work (2026-10-13); the primary route could not start and the next approved route was used. | product · env | `FB/scribe-2026-10-13-g1-resume.md` F1, F2 | G1 F1, F2 |
| OBS-091 | Cursor Agent CLI | "You're out of usage" made the planned reviewer route unavailable on 2026-10-14; the configured fallback was used. | product · env | `FB/scribe-2026-10-14-catchup.md` O1 | O1 |
| OBS-092 | Muse Code CLI | The profile display name of a model differs from its CLI model id (three name variants returned "does not exist or you lack access"); `muse exec` has no `--prompt` flag (positional or `--prompt-file`). Dispatch logs for the C2 packets show `Agent delegation: auto unavailable: workspace is untrusted.`; its effect on the work is not observed in available evidence. | product · doc-gap | `FB/scribe-2026-10-14-catchup.md` O8; `REC/coordinator-parallel-20261020/c2/logs/P2-D03.log` (source_not_durable) | O8 |
| OBS-093 | Muse Code (contributor, headless) | A headless worker run exited 0 with honest gap attribution and clean device restoration; the native completion notification allowed deterministic wakeup without polling. | product · positive | `REC/coordinator-rw1/receipt.json` (source_not_durable) | coordinator-rw1 |
| OBS-094 | Codex CLI | Planning and author routes (TE fallback, IE correction, ST-4 g5) and the B2 review route completed with passing checkers and no route switch. | product · positive | `FB/scribe-2026-10-13-g2-progress.md` (coverage ledger); `P2/specialists/te-p2-codex-receipt.md`; `P2/specialists/ie-p2-codex-delta-receipt.md` | G2 ledger |
| OBS-095 | Claude Code worktree guard | The isolated-worktree guard refuses compound shell commands with loops or variables; scratch runs needed a separate script file. | product · limit | `P2/evidence/P2-B04T/receipt.json` | P2B04T-DX-003 |
| OBS-096 | Bearing Lite 1.1.7 `orchestrator-write-lock` hook | The hook denied a named-path write from an in-process subagent because the envelope carried no `assigned_role`; writes ran as separate processes with the role environment variable. | product · defect-candidate | `P2/evidence/P2-V01-plan/receipt.md` | P2V01PD-OBS-001 |
| OBS-097 | Bearing Lite plan-package hook 1.1.6 / renderer 1.0.1 | Typed freeze codes located a key collision in one run (positive). One model embed failure aborts the whole manifest render with no output and no digest-bound non-embedded mode. `verify_delta.py` writes `conservation.json` on every run (no `--check-only`); author evidence scripts that verify by rewriting cannot be rerun read-only by a reviewer. | product · positive and defect-candidate | `P2/specialists/pi-p2-codex-receipt.md`; `P2/specialists/pi-chronology-041-receipt.md`; `P2/evidence/P2-review-repair/review-gate-input.json` | PI-P2-OBS-001/002/003, PI-CHR-OBS-001, P2R-OBS-001 |
| OBS-098 | Planning generator | Release dependencies derive from milestone-table membership, so regrouping silently drops prerequisites (suggest keying on `wave`). | process · defect-candidate | `P2/specialists/chronology-opus-review.md` | CHR-OBS-002 |
| OBS-099 | OpenCodeReview (OCR) 1.13.0 | Delegation mode excludes `.md` as `unsupported_ext` (planning-only diffs get no rule coverage; 62 reviewable vs 164 unsupported files in one review); one planning review returned a typed capability BLOCK later corrected under an owner exception; an RW1 own-engine run completed 51 identities across ten groups but excluded mutation tests, prose and PNG needed manual work. Standalone `ocr review` was never used. | product · limit | `P2/specialists/chronology-opus-review.md`; `P2/evidence/P2-review-repair/review-gate-input.json`; `REC/landing-projection/records/planning-review-receipt.json`; `REC/landing-projection/records/planning-review-capability-correction.json`; `REC/evidence/rw1-review/receipt.json` (source_not_durable) | CHR-OBS-001, P2R-OBS-002 |
| OBS-100 | Reverify 0.11.0 | `reverify --version` is a usage error (version from package metadata); `--help` and `backends` are clear; the advertised claim inventory does not establish APK manifest semantics, and an APK/DEX gap stayed typed, never PASS. | product · doc-gap | `FB/scribe-2026-10-13-g2-progress.md` F9; `P2/specialists/te-p2-codex-receipt.md` | TE-P2-OBS-001 |
| OBS-101 | Bearing Lite SEIT schema | The schema admits contentful proof objects but does not enforce register coverage, one-ID traceability, command resolution, source hashes or frozen capability preservation; a bounded cross-check script compensated. | product · limit | `P2/specialists/te-p2-codex-receipt.md` | TE-P2-OBS-002 |
| OBS-102 | Requirements System guard hook | The hook refused writing a draft `.sdoc` outside its managed roots, blocking ST-2 persistence and host binding; a missing standards ledger path was also noted. | product · env | `P2/specialists/re-st2-receipt.md` | RE-ST2-001/002 |
| OBS-103 | SysON workbench (local) | Textual `.sysml` import gave precise per-file diagnostics; `uploadDocument` needs the editing-context id (not the project id), the multipart `map` must use the string form, and project creation needs an explicit template id and empty library list. | product · doc-gap | `P2/specialists/sm-syson-receipt.md` | sm-syson |
| OBS-104 | spec-authoring skill and vendored `tools/spec` | Builds were deterministic and offline; the default Python 3.14 lacked a cached wheel (use 3.12); lint is syntactic so UID/link/scope checks stay manual; revision `changes` accepts source headings only; `check-vendor.py` trips on reviewer-owned `__pycache__`; Appendix A lacks a withdrawal-status field. | product · positive and doc-gap | `P2/evidence/ST-4/receipt.md`; `P2/evidence/ST-4/g3/receipt.json`; `P2/evidence/ST-4/g4/receipt.json`; `P2/evidence/ST-4/g5/receipt.json`; `FB/scribe-2026-10-13-g2-progress.md` F2-F4 | DX-ST4-01..06, G2 F2/F3/F4 |
| OBS-105 | git / GitHub CLI / hooks | `gh pr view` has no `baseRefOid` field; a push with output sent to `/dev/null` failed silently while the pre-push hygiene gate rejected absolute home paths and DOC-LINKs to ignored `.log` files (verify with `git ls-remote`); repository hooks fail unless the backend test venv is on PATH; the workspace issue-label hook refused this repository (issues filed with `gh`); GitHub stored a milestone `due_on` of `2026-10-17T12:00:00Z` as `2026-10-17T00:00:00Z` (calendar day preserved). | product · defect-candidate | `FB/scribe-2026-10-13-g2-progress.md` F7; `FB/scribe-2026-10-14-catchup.md` O2, O3, O10; `P2/evidence/P2-L01/date-fix-receipt.json` | G2 F7, O2, O3, O10 |
| OBS-106 | BRAN | No native BRAN policy exists for this repository, so ordinary discovery was used; no gap in the work. | process · env | `FB/scribe-2026-10-13-g1-resume.md` F3; `FB/scribe-2026-10-13-g2-progress.md` F12 | G1 F3, G2 F12 |
| OBS-107 | Orchestration (route policy) | A lead-route question reached the owner although profiles existed; closed by DEC-AFC-SD-039. | process · env | `FB/scribe-2026-10-13-g2-progress.md` F1 | G2 F1 |
| OBS-108 | Authoring evidence | Prose counts drifted from data (28 stated vs 27 actual findings) and assembly prose repaired semantics while literal conditions stayed stale. | process · defect-candidate | `FB/scribe-2026-10-13-g2-progress.md` F10, F11 | G2 F10, F11 |
| OBS-109 | Packet template | The test-engineering preparation reference path in the packet template did not exist; `jsonschema` CLI deprecation warnings polluted gate output. | process · env | `FB/scribe-2026-10-13-g2-progress.md` F5, F6 | G2 F5, F6 |

## I. Vega / Kepler SDK (PAUSED by owner 2026-10-20; stretch experiment, not delivered)

Vega is paused (`REC/vega-paused-20261020.json`, branch-only). Observations below
describe a paused experiment and its limits (RISK-AFC-P2-14); every Vega feature
verdict is unknown and nothing here is a PASS.

| ID | Tool | Observation | Class · type | Evidence | src |
|---|---|---|---|---|---|
| OBS-110 | Vega documentation | Docs give conflicting screenshot support on the Vega Virtual Device, supported Ubuntu versions differ between the install and CI pages (26.04 not mentioned), and no secure credential store for React Native for Vega nor Jest/Testing Library guide was found. | product · doc-gap | `P2/evidence/P2-V01-plan/receipt.md` | P2V01PD-OBS-002/003/004 |
| OBS-111 | Vega SDK catalog and CLI | The SDK catalog is exposed only through the authenticated CLI while the installer executes before any scan point; CLI 1.4.5 stayed NOT_ADMITTED with INDETERMINATE scans (owner accepted sandbox use). | product · limit | `REC/evidence/vega-staging-continuation/receipt.json` (source_not_durable); `REC/vega-paused-20261020.json` (source_not_durable) | vega-staging-continuation |
| OBS-112 | Vega Virtual Device preparation | The device booted under KVM to a guest shell but the guest display stayed black over QMP, the emulator console and Xvfb; start exit 0 was not boot success (status `running:true`, a valid screenshot and clean stop are required); teardown ended with SIGSEGV. Feature verdicts unknown. | product · defect-candidate | `REC/evidence/vega-prepare-c18-20261020/receipt.json` (source_not_durable); `REC/vega-paused-20261020.json` (source_not_durable) | vega-prepare-c12..c18 |
| OBS-113 | Vega CLI static analysis | The compiled CLI retains pre-fix zero-size behavior of an upstream fix (CL 794100); telemetry and update checks are not controlled by `--json`. | product · defect-candidate | `REC/landing-projection/records/evidence/wonder-trial-vega-static/receipt.json`; `REC/evidence/vega-cli-static-closure/receipt.json` (source_not_durable) | wonder-trial-vega-static |

## J. No new observations (coverage of exercised tools)

These sources returned "no new observations" or "none"; the tools they exercised
count toward coverage.

| Source | Tools exercised | Evidence |
|---|---|---|
| Systems-modeler ST-3a and ST-3b/c | `read_skill`, `gh api`, file reads, `sha256sum`, `grep`, `xml.etree` | `P2/specialists/sm-st3a-receipt.md`; `P2/specialists/sm-st3bc-receipt.md` |
| Requirements engineering deltas | `read_skill`, `edit_file`, `grep`, `git` | `P2/specialists/re-p2-delta-receipt.md`; `P2/specialists/re-sd035-receipt.md`; `P2/evidence/chronology-profile-delta/re-regate.json` |
| SVG prolog repair | `python3`, `xml.etree.ElementTree`, `hashlib` | `P2/evidence/svg-prolog/receipt.json` |
| Task-route projection | `gen_impl.py`, `plan-package.cjs`, `render-dod-manifest.mjs`, `sha256sum` | `P2/evidence/task-route-projection/receipt.json` |
| P2-D01 review | `ocr delegate preview/rule`, `gate.sh docs`, `gate.sh`, `git diff` | `P2/evidence/P2-D01/review/receipt.json` |
| TE filing binding | Python/jsonschema, `git`, local files; helper refusal of an out-of-scope repository was expected policy | `P2/specialists/te-p2-filing-binding-receipt.md` |
| Backend prep | `gate.sh`, `sam build`, `sha256sum` | `REC/landing-projection/records/evidence/backend-prep/receipt.json` |
| Release-draft early preflight | not named | `REC/evidence/release-draft/early-preflight/receipt.json` (branch-only) |
| Yahoo spike | `developer_feedback: none` | `spikes/sp6-yahoo/VERDICT.md` |
| Earlier Scribe sessions (Muse Code, Claude Code) | file reads, `git`; one file written | `FB/scribe-2026-10-13-g1-resume.md`; `FB/scribe-2026-10-13-g2-progress.md`; `FB/scribe-2026-10-14-catchup.md` |
| This Scribe session (P2-SCR1) | Claude Code (Scribe, Sonnet 5.5), shell reads, `gh issue view 1`, `git`, `rg`, `tools/ci/gate.sh hygiene` | this directory |

## K. Observations by the P2-SCR1 Scribe session itself

| ID | Tool | Observation | Class · type | Evidence |
|---|---|---|---|---|
| OBS-120 | Receipt formats | `developer_feedback` appears as a string, list, dict or Markdown section across receipts (and the key is absent from some), so assembly needed a custom extractor; one shared shape would make the coverage check mechanical. | process · defect-candidate | the sources cited in sections A-I |
| OBS-121 | Packet and path references | Several receipts cite paths relative to other worktrees or to the coordinator branch, so some pointers do not resolve on `main` until that branch lands (marked branch-only). | process · env | marked entries above |
| OBS-122 | Shared Fire TV stick | On 2026-10-20 two agents (an M06-M09 device sweep and the X11 agent) held the one stick at once; ADB commands were serialized with a file lock and the owner-facing coordinators were asked to order the two. Outcome: not observed in available evidence. | process · env | source_not_durable: transient cross-session notice, no repository path |
| OBS-123 | Worktree lifecycle | During this slice the assigned worktree and branch `afc/p2-scr1-feedback` disappeared (only the new feedback files remained in a bare directory); the Scribe recreated the worktree at `350ef51` and restored the files. Cause not observed in available evidence. | process · env | source_not_durable: the Scribe's own return, no repository path |

## Reconciliation with earlier notes

- `FB/scribe-2026-10-13-g1-resume.md`, `FB/scribe-2026-10-13-g2-progress.md` and
  `FB/scribe-2026-10-14-catchup.md` stay unchanged. They are the transcribed
  originals with the house friction-entry field set; none is deleted or
  superseded in place.
- Their friction entries map into this index: G1 F1-F3 to OBS-090, OBS-106;
  G2 F1-F12 to OBS-104..109, OBS-100, OBS-101, OBS-105; O1-O10 to OBS-091, OBS-105,
  OBS-020, OBS-021, OBS-045, OBS-016, OBS-092, OBS-061 and OBS-105. Their
  feature requests (g1 FR1; g2 FR1-FR4) are carried into `feature-requests.md` as FR-001 to FR-004 rather than repeated.
- This assembly (`observations.md`, `product-feedback.md`, `friction-log.md`,
  `feature-requests.md`) is the submission-facing set. The earlier notes are the
  source record; where wording differs, the earlier note is the source.

## Gaps and pending sources

| Gap | Waits on | Date |
|---|---|---|
| `source_not_durable` evidence pointers: OBS-012, OBS-014, OBS-015, OBS-029, OBS-092, OBS-093, OBS-099, OBS-111, OBS-112, OBS-113, OBS-122, OBS-123 (10 unresolved paths plus 2 transient notices) | the owner or coordinator committing the sanitized receipts to a tracked branch, or a PR citation | not scheduled in available evidence |
| Live Prime Video game open, alert over playback and panel on a live game | X09 live end-to-end (C3) | 2026-10-23T00:15Z kickoff |
| ESPN live update timing and correction sequence | X05 PR 2 | 2026-10-23T00:15Z |
| Provider link `gameOpened` evidence | X03 PR 2 | 2026-10-23T00:15Z |
| Live hardening observations | X10 | not scheduled in available evidence |
| Alexa / voice route | X11 disposition | not recorded in available evidence |
| M13 slices | M13 | not recorded in available evidence |
| Phase 1 returns (S01-S09, B2, S06, S43) | out of scope for this assembly; indexed only through the earlier Scribe notes | not planned |
| P2-D03, D04, D05 and X10-prep returns | dispatched 2026-10-20; returns not in available evidence | pending |
