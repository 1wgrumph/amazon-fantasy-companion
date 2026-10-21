# Product feedback — Amazon Fantasy Companion (Phase 2, assembled 2026-10-20)

Built from `observations.md` (same directory); observation IDs in brackets.
Primary track: Fire TV (Fire OS target). Mini challenge: AWS Builder (see the
AWS section). Vega is a paused stretch experiment (owner pause 2026-10-20) and
is reported only as such. Open Source mini challenge: not decided in available
evidence.

Fields follow the official Devpost submission rules extract: tools used and for
what; what worked well; what needs work; onboarding from zero to hello world;
would build again (Yes/No and why). "Not observed in available evidence" means
no source stated it; nothing is filled by guessing. Entries marked PENDING wait
on live evidence that does not exist yet.

## Fire TV Stick 4K (AFTKM, Fire OS 8.1.8.5 / Android 11, API 30) and ADB

- **Used for:** the only target device: install, launch, notification, provider-link, panel-composition, detection and end-to-end checks over network ADB.
- **Worked well:** the starter installed and launched over network ADB and rendered at 1920x1080 [OBS-001]; same-signer reinstall preserved app state [OBS-015]; `uiautomator dump` with D-pad navigation made on-device checks deterministic [OBS-013]; toasts render over playback [OBS-005]; shell-level installed/absent package detection works [OBS-011].
- **Needs work:** no heads-up banner over playback despite the documented priority, importance and full-screen-intent inputs, and the Notification Center does not show or act on the alert [OBS-003, OBS-004]; no supported way to show a third-party panel beside playing video [OBS-006]; video captures black so playback is provable only by media-session state [OBS-007]; touch taps do not click TV buttons and multiline fields trap focus [OBS-012]; `monkey` launch returned 251 once [OBS-002].
- **Onboarding (zero to hello world):** pinned Amazon hello-world starter built and installed in one spike window (2026-10-14 to 2026-10-16T12:20Z, includes waiting for the owner to locate the device and accept the on-TV RSA prompt) [OBS-001, OBS-016]. Active-time cost: not observed in available evidence.
- **Build again with this device and OS:** Yes, for the alert-and-lineup companion that runs full-screen with alerts routed to the real provider apps; the unmet beside-the-video and heads-up goals came from platform limits, not from the device being hard to use [OBS-003, OBS-006].
- **AWS services:** none (device side).

## Android, Gradle and JDK build toolchain

- **Used for:** building the TV app and spikes, host unit tests, lint, dependency scans.
- **Worked well:** a manual `aapt2`/`d8`/`apksigner` build gave an offline recipe [OBS-029]; strict dependency verification was achievable after the owner upgrade [OBS-020].
- **Needs work:** the starter's AGP 8.2.2 / Kotlin 1.9.0 closure scanned INDETERMINATE and the instrumented-test runner pulls an unadmitted netty closure [OBS-020, OBS-021]; lint compiler bundles vulnerable protobuf/JLine classes [OBS-023]; merged passive closures hide per-configuration versions [OBS-024]; `android.jar` lacks some JVM APIs in host tests [OBS-025]; the SDK location is not found without `ANDROID_HOME`/`JAVA_HOME` [OBS-028]; evidence logs need whitespace and path normalization [OBS-027].
- **Onboarding:** pinned starter built with the Gradle wrapper offline in the SP-1 window [OBS-001]. Zero-to-hello-world time: not observed in available evidence.
- **Build again:** Yes for Android/Kotlin on Fire OS (host tests and signed APKs were achievable); the cost was dependency-supply-chain triage, not the build itself.
- **AWS services:** none.

## TV app stack (Kotlin, tv-material, JUnit 4)

- **Used for:** the companion app: link screen, profile, alert feed, Watch launcher, lineup panel.
- **Worked well:** the red/green host-test seams made launcher and alert logic testable without a device [OBS-031].
- **Needs work:** a Kotlin `@Test` with a non-Unit last expression becomes a collection error [OBS-026]; focus order and multiline fields need fixing [OBS-014]; the panel wire contract was untyped until pinned [OBS-030].
- **Onboarding:** not observed in available evidence.
- **Build again:** Yes, with the typed panel contract and single-line fields.
- **AWS services:** none (the app calls the AWS-hosted API).

## Python backend, pytest, Moto, mutmut, coverage and the repository gate

- **Used for:** the backend (Python 3.12), offline unit/contract suites, formal mutation and coverage scoring, a CI gate.
- **Worked well:** pytest + Moto ran red suites in about 2 to 27 s offline with reusable fixtures [OBS-040]; mutation reached 99.49% on the foundation slice after timeout calibration [OBS-045]; the gate's expected-failure convention for red commits held [OBS-048].
- **Needs work:** JUnit output omits failure type [OBS-041]; conftest shadowing across unit and deployed dirs [OBS-042]; Moto does not enforce IAM [OBS-044]; mutmut copy, trampoline and timeout behavior, and a GAP that makes a mutation PASS unreachable [OBS-045]; diff-cover drops files without executable lines [OBS-046]; the gate is noisy and slow in places and lacks tools in the cloud container [OBS-048, OBS-049].
- **Onboarding:** not observed as a single time; the backend foundation was a red suite then green over the B01 slices [OBS-040]. Zero-to-hello-world time: not observed in available evidence.
- **Build again:**
  - pytest + Moto: Yes, because red suites ran offline in seconds with reusable fixtures [OBS-040].
  - mutmut: Yes with caveats, because it reached 99.49% on the foundation slice but needed copy-path and timeout workarounds on a loaded host [OBS-045].
  - diff-cover and coverage: Yes with caveats, because files without executable lines were dropped as REPORT_INCOMPLETE [OBS-046].
- **AWS services:** DynamoDB is stubbed by Moto in tests only.

## AWS CLI, SAM, CloudFormation, Lambda, API Gateway, DynamoDB, SSM, IAM (profile and stack `afc-dev`, us-east-2)

- **AWS Builder mini challenge: services used and how.** The SAM template (`backend/template.yaml`) declares: **Lambda** (three Python 3.12 functions: `ApiFunction` for the TV and phone-link routes, `IngestFunction` for the ESPN feed poll and `PolicyFunction` for the alert pipeline); **API Gateway** (one HTTP API with a throttling burst of 10 and rate of 5); **DynamoDB** (seven on-demand tables: Profiles, Links, Events, Alerts, Lineups, Panels, PlayerStats); **EventBridge Scheduler** (one schedule, `rate(1 minute)`, that invokes the ingest function, with its own role); **CloudWatch Logs** (three log groups, one per function); **IAM** (per-function least-privilege grants asserted by a contract test); **SSM Parameter Store** (Yahoo client id, client secret and refresh token, secrets as SecureString); **CloudFormation** (deployed through SAM).
- **Used for:** the cloud backend that links a device by code, ingests ESPN events, matches starters, resolves provider routes, and serves alerts and the lineup panel to the stick.
- **Worked well:** stack deploys reached UPDATE_COMPLETE for L02, L03 (interim and final) and two redeploys, with deployed smoke suites passing and some cases deferred or skipped and never counted as PASS [OBS-065, OBS-066]; `sam validate --lint` and `sam build` ran offline and honoured hash pins [OBS-063]; SSM held the Yahoo secrets [OBS-067].
- **Needs work:** `aws login` sign-in 400 on "Continue with an active session" and breakage with two concurrent logins [OBS-060]; session expiry mid-deploy [OBS-061]; boto3 could not use login credentials [OBS-062]; `samconfig.toml` profile under global parameters breaks builds elsewhere [OBS-063]; interactive SAM under `timeout` stops at the prompt [OBS-064].
- **Onboarding:** documented in the repository setup note; sign-in, SSM parameters and a one-command token flow [OBS-060, OBS-067]. Zero-to-hello-world time: not observed in available evidence.
- **Build again:** Yes. The serverless pieces fit the event-driven design; the friction was credential handling, not the services.

## ESPN public JSON endpoints (scoreboard and summary)

- **Used for:** NFL schedule, game state, plays, scoring and broadcast networks.
- **Worked well:** HTTP 200 without authentication for all 14 sampled games; rich per-play data [OBS-070].
- **Needs work:** unofficial with no published contract; empty top-level `broadcasts`; `$ref`-only participants; a play without `wallclock`; 89% of plays edited after the game with minute-precision `modified`; body variation on final games; public-use terms unresolved [OBS-071 to OBS-074].
- **Onboarding:** two GET URLs and a stdlib capture tool; one 8-minute spike window [OBS-070].
- **Build again:** Yes, behind a validating ingest with replay fixtures. **PENDING:** live update timing and live correction behavior wait for X05 PR 2 and X09 (kickoff 2026-10-23T00:15Z); until then this entry covers historical replay only.
- **AWS services:** the poller runs on Lambda via EventBridge Scheduler (see the AWS section).

## Yahoo Fantasy API

- **Used for:** attempting to read leagues, rosters and settings (no live Yahoo data was obtained).
- **Worked well:** the OAuth refresh-token grant returned HTTP 200 on both attempts [OBS-080].
- **Needs work:** the Fantasy API returned 403 "This application is not authorized to perform this action" for the unapproved app with and without the `fspt-r` scope, so the product fell back to labeled manual lineup entry [OBS-080]; console rules (https redirect, no "Yahoo" in the description) were learned by failing [OBS-081]. The access application (2026-10-16) has no recorded outcome [OBS-082].
- **Onboarding:** a one-command token helper after console setup; elapsed spike window about 1.5 hours (2026-10-16T14:18Z to 15:48Z), mostly console setup and diagnosis [OBS-080].
- **Build again:** No, until access is approved; the manual-entry fallback is a deliberate design, not a preference.
- **AWS services:** SSM Parameter Store held the Yahoo credentials [OBS-067].

## Security and quality scanners (ClamAV, gitleaks, pip-audit, Bandit)

Sources: `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/receipt.json` (`tools_exercised`, line 316) and `.../P2-B01/receipt.json` (`tools_exercised`, line 342).

- **Used for:** listed as exercised in the P2-B01T and P2-B01 slices (the Bandit observation concerns a scan of the backend packet); the receipts do not state each scan's subject, so per-tool purpose beyond the tool class (malware scan, secret scan, dependency audit, static analysis) is not observed in available evidence. Per-tool versions: pip-audit 2.10.0 (P2-B01 receipt); ClamAV, gitleaks and Bandit versions not observed in available evidence.
- **Worked well:** not observed in available evidence for ClamAV, gitleaks and pip-audit (the receipts list them as exercised without a stated observation). Bandit: see Needs work.
- **Needs work:** Bare scanner launchers bound a different Python environment than the backend one; explicit `python3.12 -m` binding worked, and Bandit stdout progress text is not JSON, so `-o` is needed for machine-readable output [P2B01T-DX-001]. Nothing stated for ClamAV, gitleaks or pip-audit: not observed in available evidence.
- **Onboarding:** not observed in available evidence.
- **Build again:** ClamAV, gitleaks, pip-audit: not observed in available evidence (no stated verdict); Bandit: Yes with caveats, because it ran but needs explicit interpreter binding and `-o` for JSON [P2B01T-DX-001].
- **AWS services:** none.

## PyYAML and cfn-lint

Sources: the same two receipts (`tools_exercised`, P2-B01T line 316, P2-B01 line 342); cfn-lint output in `.../P2-B01/cfn-lint.txt`.

- **Used for:** PyYAML is listed in the P2-B01T `tools_exercised`; its use is not observed in available evidence. cfn-lint 1.57.2 output is recorded with exit 0 for the P2-B01 slice; the lint subject is not stated in that file.
- **Worked well:** cfn-lint 1.57.2 exited 0 on the template [P2-B01/cfn-lint.txt]. PyYAML: not observed in available evidence.
- **Needs work:** not observed in available evidence for either tool.
- **Onboarding:** not observed in available evidence.
- **Build again:** cfn-lint: Yes, because it exited 0 in the recorded run (no friction stated). PyYAML: not observed in available evidence.
- **AWS services:** cfn-lint targets CloudFormation (see the AWS section); PyYAML none.

## Alexa / voice route

- PENDING: X11 disposition. No Alexa observation exists in available evidence.

## Muse Code, Claude Code, Codex, Cursor Agent, Deep Code (agent harnesses)

- **Used for:** authoring, review and orchestration across Phase 2 roles.
- **Worked well:** Codex planning/author/review routes passed their checkers without route switches [OBS-094]; Muse Code headless contributor mode exited 0 with clean device restoration and native completion notification [OBS-093].
- **Needs work:** subscription usage limits ended runs before any work (Claude Code, Cursor Agent) with no machine-readable signal [OBS-090, OBS-091]; a Muse profile display name differs from its CLI model id and `muse exec` has no `--prompt` flag [OBS-092]; the Claude Code worktree guard rejects compound shell commands [OBS-095]. Deep Code: used only as a coordinator route; no usable observation in available evidence.
- **Onboarding:** not observed in available evidence.
- **Build again (per tool):**
  - Codex CLI: Yes, because its planning, author and review routes passed their checkers without route switches [OBS-094].
  - Muse Code: Yes, because headless contributor mode exited 0 with clean device restoration [OBS-093]; the display-name versus model-id mismatch needs care [OBS-092].
  - Claude Code: Yes with caveats, because a subscription usage limit ended one run before any work and the worktree guard rejects compound shell commands [OBS-090, OBS-095].
  - Cursor Agent: not assessed; the only observation is a usage limit that ended a run before any work [OBS-091].
  - Deep Code: not observed in available evidence.
- **AWS services:** none.

## OpenCodeReview (OCR) 1.13.0 and Reverify 0.11.0

- **Used for:** per-file rule review in delegation mode; Reverify only for binary subjects.
- **Worked well:** delegation preview and rule runs completed cleanly on exact ranges, with an accurate reviewable/excluded split [OBS-099]; Reverify `--help` and `backends` are clear [OBS-100].
- **Needs work:** `.md` is excluded, so planning-only diffs get no coverage [OBS-099]; no `--version`; no claim for APK manifest semantics [OBS-100].
- **Onboarding:** not observed in available evidence.
- **Build again:** Yes for OCR as an assist; Reverify only where a claim type fits.
- **AWS services:** none.

## GitHub, git, `gh` and PR workflow

- **Used for:** issues and milestones, branches, PRs, hosted checks, hooks.
- **Worked well:** readbacks, hosted-check queries and merge-tree scoping behaved as documented [coverage ledger in `scribe-2026-10-13-g2-progress.md`].
- **Needs work:** unsupported `gh` field; silent push failure when output is discarded; hooks that need a venv on PATH; the issue-label hook refused this repository; milestone `due_on` stored as midnight UTC [OBS-105].
- **Onboarding:** not observed in available evidence.
- **Build again:** Yes, because readbacks, hosted-check queries and merge-tree scoping behaved as documented; the silent push failure is avoided by keeping push output visible [OBS-105].
- **AWS services:** none.

## Planning and agent tooling (Bearing Lite, spec-authoring, Requirements System, SysON, BRAN)

- **Used for:** the plan package, SEIT, DoD Manifest, specification builds, requirements registers, models.
- **Worked well:** typed freeze codes found a collision in one run [OBS-097]; spec builds were deterministic and offline [OBS-104]; SysON import diagnostics were precise [OBS-103].
- **Needs work:** write-lock hook without role context [OBS-096]; all-or-nothing manifest render and rewriting verifiers [OBS-097]; SEIT schema leaves coverage unenforced [OBS-101]; release dependencies tied to table membership [OBS-098]; guard hook blocked a draft register [OBS-102]; SysON upload needs the editing-context id [OBS-103]; no native BRAN policy for this repository [OBS-106].
- **Onboarding:** not observed in available evidence.
- **Build again:** Yes, with the fixes in `feature-requests.md`.
- **AWS services:** none.

## Vega / Kepler SDK and Vega Virtual Device — PAUSED stretch experiment

- Paused by the owner on 2026-10-20; Fire OS is primary. A port compiled and its host tests ran, but no on-device Vega evidence exists and every feature verdict is unknown; none is a PASS or a delivered feature (RISK-AFC-P2-14).
- **Observed limits:** documentation conflicts and gaps [OBS-110]; catalog behind an authenticated CLI before any scan point, CLI not admitted [OBS-111]; the virtual device booted but the guest display stayed black [OBS-112]; static analysis findings on the CLI [OBS-113].
- **Build again:** not assessed (paused).

## Coverage count

Enumeration of every tool, API and device found across the sources:

| # | Tool / API / device | Section | Status |
|---|---|---|---|
| 1 | Fire TV Stick 4K / Fire OS / ADB | above | observed |
| 2 | Android / Gradle / JDK toolchain (incl. Trivy, lint) | above | observed |
| 3 | TV app stack (Kotlin, JUnit 4, tv-material) | above | observed |
| 4 | Python backend, pytest, Moto | above | observed |
| 5 | mutmut, diff-cover, coverage, repository gate | above | observed |
| 6 | AWS CLI | above | observed |
| 7 | SAM / CloudFormation | above | observed |
| 8 | Lambda | above | observed (deploy and smoke; runtime performance not observed in available evidence) |
| 9 | API Gateway (HTTP API) | above | observed (deploy and smoke) |
| 10 | DynamoDB | above | observed (tables deployed; Moto in tests) |
| 11 | SSM Parameter Store | above | observed |
| 12 | IAM | above | observed (grant contract test; Moto limit) |
| 13 | EventBridge Scheduler | above | declared in the template; behavior not observed in available evidence |
| 14 | CloudWatch Logs | above | declared in the template; behavior not observed in available evidence |
| 15 | ESPN public JSON | above | observed (historical); live PENDING |
| 16 | Yahoo Fantasy API | above | observed (403) |
| 17 | Muse Code | above | observed |
| 18 | Claude Code | above | observed |
| 19 | Codex CLI | above | observed |
| 20 | Cursor Agent CLI | above | observed (usage limit only) |
| 21 | Deep Code CLI | above | not observed in available evidence (coordinator route) |
| 22 | OCR | above | observed |
| 23 | Reverify | above | observed |
| 24 | GitHub / git / `gh` / hooks | above | observed |
| 25 | Bearing Lite plugin and hooks | above | observed |
| 26 | spec-authoring and vendored `tools/spec`, uv, Graphviz | above | observed |
| 27 | Requirements System guard hook | above | observed |
| 28 | SysON workbench | above | observed |
| 29 | BRAN | above | observed (unavailable for this repository) |
| 30 | Vega SDK / CLI / Virtual Device | above | paused; limits observed |
| 31 | Alexa / voice | above | PENDING (X11) |
| 32 | Prime Video app as a provider target | folded into the Fire TV section | observed |
| 33 | ClamAV | scanners section | exercised; no observation stated in available evidence |
| 34 | gitleaks | scanners section | exercised; no observation stated in available evidence |
| 35 | pip-audit 2.10.0 | scanners section | exercised; no observation stated in available evidence |
| 36 | Bandit | scanners section | observed (P2B01T-DX-001) |
| 37 | PyYAML | PyYAML and cfn-lint section | exercised; no observation stated in available evidence |
| 38 | cfn-lint 1.57.2 | PyYAML and cfn-lint section | observed (exit 0 only) |

Total enumerated: 38. Observed with usable observations: 29 (the earlier 27, Bandit
and cfn-lint); exercised with no stated observation: 4 (ClamAV, gitleaks,
pip-audit, PyYAML); not observed in available evidence: 1 (Deep Code); declared
but behavior not observed: 2 (EventBridge Scheduler, CloudWatch Logs); PENDING: 1
(Alexa); paused: 1 (Vega, limits observed). 29 + 4 + 1 + 2 + 1 + 1 = 38.
