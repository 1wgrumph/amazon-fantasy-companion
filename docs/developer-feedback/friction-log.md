# Friction log — Amazon Fantasy Companion (Phase 2, sanitized, assembled 2026-10-20)

One entry per sourced friction, in the Devpost optional-entry fields: task
attempted, steps taken, expected vs. actual, severity, workaround, actionable
suggestion, plus tool/version and time cost. Severity: Blocker, Major, Minor.
Time cost is given only where a source recorded it; spike windows are the
verdict's `started_at`/`ended_at` and include waiting. "Not observed in available
evidence" means no source stated it. Each entry cites `observations.md` IDs
(path prefixes are defined there). Private values (accounts, device address,
credentials, local paths) are replaced by `<owner-account>`, `<device>` and
`<worktree>` or omitted. Feedback stays local; sending is owner action OA-8.

## Platform and vendor frictions

### F-001 — No heads-up banner on Fire OS (OBS-003, OBS-004)
- **Tool/version:** Fire OS 8.1.8.5 notifications, Android 11 / API 30, device AFTKM.
- **Task attempted:** show a Watch/Dismiss alert over Prime Video playback.
- **Steps taken:** posted from a foreground service on a high-importance channel; retried with sound and vibrate, `PRIORITY_HIGH` (per the Fire TV notification guide) and a full-screen intent; checked the Notification Center.
- **Expected vs actual:** expected a heads-up banner with focusable actions; actual: the notification posted (`importance=4`, two actions) but never appeared as a banner, and the Notification Center showed only the service card.
- **Severity:** Major (the heads-up alert route is unusable).
- **Workaround:** alerts shown panel-only inside the companion app; toast kept as display-only awareness.
- **Actionable suggestion:** document that Fire OS 8 does not present third-party heads-up notifications, or provide a supported presentation API (FR-005).
- **Time cost:** spike window about 1 hour (2026-10-16T19:35Z to 20:36Z).

### F-002 — No supported way to show a panel beside playing video (OBS-006)
- **Tool/version:** Fire OS 8.1.8.5 windowing (PiP, overlay, split-screen, freeform), Prime Video.
- **Task attempted:** a lineup panel beside unobscured, uncropped video.
- **Steps taken:** provider PiP via HOME, panel PiP, `TYPE_APPLICATION_OVERLAY`, `--windowingMode 3` and `5`.
- **Expected vs actual:** expected side-by-side composition; actual: provider PiP unsupported (HOME stopped playback), panel PiP covered a 384x216 corner, overlay needed a Settings grant and still overlaps, split and freeform launched full-screen.
- **Severity:** Major.
- **Workaround:** panel runs full-screen in the companion app; alerts and Watch route to the provider app.
- **Actionable suggestion:** a supported composition mechanism or provider PiP guidance (FR-006).
- **Time cost:** spike window about 18 minutes (2026-10-16T19:07Z to 19:25Z).

### F-003 — Provider deep links stop short of a specific game (OBS-008, OBS-009, OBS-010)
- **Tool/version:** Prime Video (PVFTV-324.0104-L), Android intents, `am start`.
- **Task attempted:** open the correct live game from an alert.
- **Steps taken:** tried `MAIN`/`LAUNCHER`, `amzn://avod`, an action intent, `https://watch.amazon.com/search` (with and without query parameters) and a per-title `/detail` link; probed ESPN, DirecTV Stream, YouTube TV and local broadcast.
- **Expected vs actual:** expected a documented game or channel link; actual: home, search (query ignored) and title pages only; a bare `MAIN` intent did not resolve without `LEANBACK_LAUNCHER`; three other providers were not installed and opened only the browser. Live `gameOpened` check PENDING (X03 PR 2, kickoff 2026-10-23T00:15Z).
- **Severity:** Major.
- **Workaround:** register only the verified search route; report `appAbsent`, `searchOpened` or `accessUnknown` honestly.
- **Actionable suggestion:** publish provider game deep-link contracts and an event-to-title mapping (FR-007).
- **Time cost:** spike window about 10 minutes (2026-10-16T20:00Z to 20:10Z) for the desk pass.

### F-004 — `adb shell monkey` launch exited 251 (OBS-002)
- **Tool/version:** Android `monkey` on Fire OS 8.1.8.5.
- **Task attempted:** launch the starter activity.
- **Steps taken:** repeated the SP-1 launch during the repair re-check.
- **Expected vs actual:** expected the activity to resume; actual: exit 251, nothing resumed, while `am start` worked.
- **Severity:** Minor.
- **Workaround:** `am start` and a `dumpsys activity` check.
- **Actionable suggestion:** document `am start` as the supported launch path.
- **Time cost:** not observed in available evidence.

### F-005 — Playing video captures black (OBS-007)
- **Tool/version:** `adb exec-out screencap` on Prime Video.
- **Task attempted:** screenshot evidence of playback and layout.
- **Steps taken:** captured during playback in the SP-3 and SP-4 sweeps.
- **Expected vs actual:** expected video pixels; actual: a black secure surface with player chrome only.
- **Severity:** Minor.
- **Workaround:** prove playback with `dumpsys media_session` state and window geometry.
- **Actionable suggestion:** document the secure-surface limit for test tooling.
- **Time cost:** not observed in available evidence.

### F-006 — Shell cannot create a disabled package state (OBS-011)
- **Tool/version:** `pm disable` on Fire OS 8.1.8.5.
- **Task attempted:** exercise installed-disabled detection.
- **Steps taken:** `pm disable` on an installed provider package.
- **Expected vs actual:** expected the package disabled; actual: `SecurityException: Shell cannot change component state`.
- **Severity:** Minor.
- **Workaround:** prove the state in-app with an own fixture package that self-disables; state restored and verified.
- **Actionable suggestion:** document the supported way to test disabled apps (FR-009).
- **Time cost:** spike window about 22 minutes (2026-10-19T11:04Z to 11:26Z).

### F-007 — Taps do not click TV buttons; multiline fields trap focus (OBS-012, OBS-014)
- **Tool/version:** Fire OS 8.1.8.5 input, tv-material components, Amazon keyboard.
- **Task attempted:** drive the profile and link screens during device checks.
- **Steps taken:** touch and mouse taps, D-pad, keyboard actions, `uiautomator dump`.
- **Expected vs actual:** expected taps to click; actual: only D-pad focus plus CENTER works; keyboard "Next" did nothing in multiline fields, "Previous" exited; the screensaver after about 10 minutes idle needed WAKEUP+CENTER.
- **Severity:** Minor.
- **Workaround:** D-pad navigation read through `uiautomator dump`; planned fix is single-line fields with `ImeAction.Next`.
- **Actionable suggestion:** document Fire TV UI-automation guidance (FR-010).
- **Time cost:** not observed in available evidence.

### F-008 — Yahoo Fantasy API 403 for an unapproved app (OBS-080, OBS-081, OBS-082)
- **Tool/version:** Yahoo OAuth 2.0 token endpoint and Fantasy API v2.
- **Task attempted:** read leagues, rosters and settings for the lineup panel.
- **Steps taken:** refresh-token grant, then the user-games and leagues reads; repeated after a consent URL requesting `fspt-r`; then submitted the access application on 2026-10-16.
- **Expected vs actual:** expected league data; actual: token refresh HTTP 200, Fantasy API HTTP 403 "This application is not authorized to perform this action" both times; no league, roster or settings body read. No Yahoo payload is stored here.
- **Severity:** Major (single largest data-source loss).
- **Workaround:** labeled manual lineup entry as the active source.
- **Actionable suggestion:** publish approval criteria and turnaround, and document the 403 behavior for unapproved apps (FR-008).
- **Time cost:** spike window about 1.5 hours (2026-10-16T14:18Z to 15:48Z).

### F-009 — Yahoo developer console rules learned by failing (OBS-081)
- **Tool/version:** Yahoo developer console, OAuth client settings.
- **Task attempted:** register a read-only app.
- **Steps taken:** configured the redirect and description; created then deleted a duplicate app.
- **Expected vs actual:** expected a plain `oob` redirect and free description text; actual: `oob` rejected (https required) and the word "Yahoo" not allowed in the description.
- **Severity:** Minor.
- **Workaround:** https localhost redirect; reworded description.
- **Actionable suggestion:** list these constraints on the app-creation form.
- **Time cost:** not observed in available evidence.

### F-010 — `aws login` sign-in 400 and mid-deploy expiry (OBS-060, OBS-061, OBS-062)
- **Tool/version:** AWS CLI 2.38.0 `aws login` for profile `afc-dev` (IAM user, region us-east-2), boto3.
- **Task attempted:** sign in and deploy slice L02.
- **Steps taken:** "Continue with an active session" on the sign-in page; two concurrent `aws login` runs; deploy; later local boto3 use.
- **Expected vs actual:** expected sign-in and a stable session; actual: HTTP 400 Bad Request on the active-session path, a broken flow with concurrent runs, "Your session has expired. Please reauthenticate using 'aws login'" during L02, and local boto3 could not use the login credentials.
- **Severity:** Minor (each had a workaround; L02 waited on the owner to sign in).
- **Workaround:** "Sign in to new session"; one login at a time; go through the AWS CLI instead of boto3 (documented in the repository setup note).
- **Actionable suggestion:** fix the active-session path and document session lifetime (FR-012).
- **Time cost:** not observed in available evidence.

### F-011 — SAM configuration and prompts (OBS-063, OBS-064)
- **Tool/version:** SAM CLI 1.169.0.
- **Task attempted:** build offline and deploy.
- **Steps taken:** `sam build` without the profile; interactive deploy under a `timeout` wrapper.
- **Expected vs actual:** expected both to run; actual: `profile=afc-dev` under global parameters failed builds on a machine without it; the deploy stopped at the confirmation prompt under `timeout`.
- **Severity:** Minor.
- **Workaround:** profile only under deploy parameters; foreground process-group retry.
- **Actionable suggestion:** note both in the SAM configuration docs.
- **Time cost:** not observed in available evidence.

### F-012 — ESPN schema surprises and post-game edits (OBS-071, OBS-072, OBS-073)
- **Tool/version:** ESPN public scoreboard and summary JSON (unofficial).
- **Task attempted:** normalize plays, broadcasts and corrections.
- **Steps taken:** captured 14 completed games and re-captured one.
- **Expected vs actual:** expected a top-level `broadcasts` and stable final bodies; actual: `broadcasts` empty (data under the competition), participants as `$ref` links, one play without `wallclock`, 89% of plays edited after the game with minute-precision `modified`, and different hashes for equal-length final bodies.
- **Severity:** Minor so far; live correction behavior PENDING (X05 PR 2, X09).
- **Workaround:** a validating ingest that rejects bad polls before any write, with labeled replay.
- **Actionable suggestion:** publish a contract and change notes (FR-011).
- **Time cost:** spike window about 8 minutes (2026-10-14T14:47Z to 14:55Z).

### F-013 — Dependency-supply-chain triage of the Android build (OBS-020, OBS-021, OBS-022, OBS-023)
- **Tool/version:** Gradle closure (AGP 8.2.2, Kotlin 1.9.0), instrumented-test runner (UTP), lint compiler 32.4.1, Trivy.
- **Task attempted:** admit the build and test toolchain.
- **Steps taken:** scanned the starter's closure, the runner closure and the newest lint compiler; tried filesystem and rootfs Trivy modes.
- **Expected vs actual:** expected a clean scan; actual: INDETERMINATE for the starter closure, HIGH/CRITICAL findings in the runner's netty closure (not admitted), bundled protobuf/JLine classes with HIGH findings in the newest lint compiler, and zero language files from Trivy filesystem mode on a JAR-only tree.
- **Severity:** Major (on-device instrumented tests blocked pending an owner decision whose outcome is not in available evidence).
- **Workaround:** owner upgraded tv-app to AGP 9.3.1 / KGP 2.4.21 / Gradle 9.7.0 with strict verification and accepted residual build-host risk; archive-aware Trivy mode.
- **Actionable suggestion:** ship patched, non-vulnerable test-runner and compiler dependency closures.
- **Time cost:** not observed in available evidence.

### F-014 — Android and Kotlin test surface gaps (OBS-025, OBS-026, OBS-028)
- **Tool/version:** `android.jar` host-test compile, Kotlin with JUnit 4, Gradle with the Android SDK.
- **Task attempted:** write and compile host unit tests.
- **Steps taken:** used `JSONObject.keySet()`, `similar`, `Files.readString`; wrote `= runBlocking { use { ... } }` tests; ran the packet's Gradle command.
- **Expected vs actual:** expected JVM behavior; actual: missing APIs, a JUnit 4 `initializationError` ("should be void") from a non-Unit last expression, and "SDK location not found" without environment variables.
- **Severity:** Minor.
- **Workaround:** `keys()`, `Files.readAllBytes`, a Unit-typed test body, exported `ANDROID_HOME`/`JAVA_HOME`.
- **Actionable suggestion:** document these in Android TV testing guidance.
- **Time cost:** not observed in available evidence.

### F-015 — pytest, Moto and IAM blind spots (OBS-041, OBS-042, OBS-044)
- **Tool/version:** pytest 8.4.2, Moto, boto3.
- **Task attempted:** run unit and deployed suites together; check IAM grants.
- **Steps taken:** collected both directories in one call; classified red failures from JUnit XML.
- **Expected vs actual:** expected independent conftest modules and typed failures; actual: the deployed `conftest` shadowed `from conftest import ...`, JUnit failures lacked `type`, and missing IAM grants were invisible because Moto does not enforce IAM.
- **Severity:** Minor.
- **Workaround:** inline helpers, run deployed tests separately, classify by message, pair template and contract-test changes.
- **Actionable suggestion:** document the shadowing and an offline IAM test path (FR-013).
- **Time cost:** not observed in available evidence.

### F-016 — mutmut timeouts and structural GAPs (OBS-045)
- **Tool/version:** mutmut 3.8.0.
- **Task attempted:** formal mutation scoring on a shared, loaded host.
- **Steps taken:** repeated full runs; wrapper with copy and timeout options.
- **Expected vs actual:** expected a stable score; actual: runs 1 and 2 timed out and exited 3, two runs timed out disjoint mutant sets (14 then 8) at host load 12 to 20, clean runs failed on a missing template (`also_copy` is top-level only), trampolines broke AST tests, and a changed module-level assignment forced a GAP (raw score 214/231).
- **Severity:** Major for slice B06 (mutation PASS unreachable); Minor elsewhere.
- **Workaround:** calibrated timeouts (later 99.49% on the foundation slice), wrapper-written `also_copy`, `pragma: no mutate`.
- **Actionable suggestion:** nested `also_copy`, documented loaded-host timeouts, constant-assignment handling (FR-014).
- **Time cost:** not observed in available evidence.

### F-017 — diff-cover drops files with no executable lines (OBS-046)
- **Tool/version:** diff-cover 10.6.0.
- **Task attempted:** coverage on a changed docstring-only module.
- **Steps taken:** ran the coverage evaluator against the base commit.
- **Expected vs actual:** expected the file excluded with evidence; actual: absent from `src_stats`, reported REPORT_INCOMPLETE.
- **Severity:** Minor.
- **Workaround:** explicit exclusion evidence in the receipt.
- **Actionable suggestion:** report such files as excluded (FR-015).
- **Time cost:** not observed in available evidence.

## Agent-harness and review-tool frictions

### F-018 — Subscription usage limits end dispatches (OBS-090, OBS-091)
- **Tool/version:** Claude Code (weekly limit, 2026-10-13), Cursor Agent CLI ("You're out of usage", 2026-10-14).
- **Task attempted:** resume test work, planning and a reviewer route.
- **Steps taken:** dispatched on each primary route.
- **Expected vs actual:** expected the run to start; actual: exit 1 with a limit message and no artifacts (two Claude Code dispatches; one Cursor reviewer route).
- **Severity:** Blocker for the primary route; no work lost.
- **Workaround:** the next approved fallback route.
- **Actionable suggestion:** a machine-readable limit signal and visible remaining budget (FR-001).
- **Time cost:** run durations not observed in available evidence; reset times are vendor-reported.

### F-019 — Muse Code model naming and flags (OBS-092)
- **Tool/version:** Muse Code CLI (`muse exec`).
- **Task attempted:** headless run with a named model.
- **Steps taken:** tried three name variants.
- **Expected vs actual:** expected the profile display name to work; actual: "does not exist or you lack access" for all three; `--prompt` does not exist.
- **Severity:** Minor.
- **Workaround:** the CLI model id; positional prompt or `--prompt-file`.
- **Actionable suggestion:** accept or list display names in `muse models`.
- **Time cost:** not observed in available evidence.

### F-020 — Claude Code worktree guard rejects compound commands (OBS-095)
- **Tool/version:** Claude Code isolated-worktree guard.
- **Task attempted:** scratch runs with loops and variables.
- **Steps taken:** compound shell commands.
- **Expected vs actual:** expected execution; actual: refusal.
- **Severity:** Minor.
- **Workaround:** a separate script file.
- **Actionable suggestion:** document the allowed shell forms.
- **Time cost:** not observed in available evidence.

### F-021 — OCR and Reverify coverage limits (OBS-099, OBS-100)
- **Tool/version:** OpenCodeReview 1.13.0 (delegation mode), Reverify 0.11.0.
- **Task attempted:** per-file rule review of planning and code diffs; verify an APK claim.
- **Steps taken:** `ocr delegate preview` and `rule`; `reverify --version`, `--help`, `backends`.
- **Expected vs actual:** expected Markdown coverage and a version flag; actual: `.md` excluded as `unsupported_ext` (62 reviewable vs 164 unsupported in one review), a planning review returned a typed capability BLOCK later corrected under an owner exception, `--version` was a usage error, and no claim covers APK manifest semantics.
- **Severity:** Minor.
- **Workaround:** direct reading of excluded files; version from package metadata; the APK gap stayed typed, never PASS.
- **Actionable suggestion:** Markdown support in OCR; a Reverify version flag and APK claim (FR-016, FR-017).
- **Time cost:** not observed in available evidence.

### F-022 — Bearing Lite hooks and renderer (OBS-096, OBS-097, OBS-101)
- **Tool/version:** Bearing Lite 1.1.6 and 1.1.7 (write-lock hook, plan-package hook, manifest renderer 1.0.1, SEIT schema).
- **Task attempted:** write plan files from a subagent; render the DoD Manifest; validate SEIT.
- **Steps taken:** named-path write from an in-process subagent; render with a failing model embed; schema validation.
- **Expected vs actual:** expected the packet role to reach the hook, partial render output, and schema-level coverage checks; actual: write denied for a missing `assigned_role`, whole render aborted, coverage unenforced.
- **Severity:** Minor.
- **Workaround:** separate processes with the role variable; deactivate affected models; a bounded cross-check script.
- **Actionable suggestion:** FR-018, FR-019, FR-020.
- **Time cost:** not observed in available evidence.

### F-023 — Requirements System guard, SysON and spec tooling (OBS-102, OBS-103, OBS-104)
- **Tool/version:** Requirements System guard hook; local SysON workbench; vendored `tools/spec`; uv 0.11.6 with Python 3.14.4 vs 3.12.3.
- **Task attempted:** persist a draft `.sdoc`; import SysML; build the specification.
- **Steps taken:** wrote the draft in the plan directory; GraphQL project create and multipart upload; default-interpreter build.
- **Expected vs actual:** expected the write allowed, upload to accept the project id and spec-form `map`, and the default interpreter to build; actual: write refused outside managed roots, upload needed the editing-context id and a string-form `map`, and the default Python lacked a cached wheel.
- **Severity:** Minor (the draft was preserved in the receipt; the others had workarounds).
- **Workaround:** none for the refused write (preserved in the receipt); editing-context id; `UV_PYTHON=3.12`.
- **Actionable suggestion:** reconcile the guard's managed roots with the owner-approved draft path; better upload errors (no feature request filed for this).
- **Time cost:** not observed in available evidence.

### F-024 — git, GitHub CLI and hooks (OBS-105)
- **Tool/version:** git, `gh`, repository pre-push gate, workspace issue-label hook.
- **Task attempted:** push, open issues and set milestone dates.
- **Steps taken:** pushes with output discarded; unsupported `gh pr view` field; milestone `due_on` PATCH.
- **Expected vs actual:** expected visible failures and supported fields; actual: silent push failures for several commits, an unsupported `baseRefOid`, hooks failing without the backend venv on PATH, the label hook refusing this repository, and `due_on` stored as midnight UTC.
- **Severity:** Minor.
- **Workaround:** `git ls-remote` verification; supported fields; venv on PATH; direct `gh` filing; calendar-day check on readback.
- **Actionable suggestion:** none for the products; keep push output visible.
- **Time cost:** not observed in available evidence.

### F-026 — OpenCodeReview skips test files by default (2026-10-20)
- **Tool/version:** OpenCodeReview 1.13.x.
- **Task attempted:** OCR-assisted independent review of Kotlin and Python changes.
- **Steps taken:** compared `ocr delegate preview` selections with and without a project rule file.
- **Expected vs actual:** expected every changed code file reviewed; actual: the built-in default path filter excluded all test files (`src/test/**/*.kt`, `test_*.py`, `*.test.ts` and similar, reason `default_path`), 7 of 16 code files on one commit.
- **Severity:** Major for a test-first lifecycle: test code was silently unreviewed.
- **Workaround:** `.opencodereview/rule.json` with an `include` list ([#127](https://github.com/1wgrumph/amazon-fantasy-companion/pull/127)). The next review's first actionable OCR finding was in a test file.
- **Actionable suggestion:** report default-path exclusions prominently in the preview summary, or default to including tests.
- **Time cost:** not observed in available evidence.

### F-027 — Subscription quota exhaustion cascades through fallbacks (2026-10-20)
- **Tool/version:** Muse Code CLI, AGY CLI, Codex CLI.
- **Task attempted:** one bug-fix dispatch on its frozen route.
- **Steps taken:** the primary stopped mid-run on HTTP 429 with partial uncommitted work; the first fallback returned 429 with an 84-hour reset; the second fallback finished.
- **Expected vs actual:** expected the primary to finish; actual: three launches and two quota receipts for one fix. The route guard accepts only the literal signatures `quota` or `rate-limit`, so a receipt carrying the raw error text was refused until rewritten.
- **Severity:** Moderate: about 30 minutes lost; a scheduled unattended driver had the same receipt defect and was fixed before its run.
- **Workaround:** write receipts with the literal labels and keep the raw text in a separate field.
- **Actionable suggestion:** expose remaining quota before dispatch, and document the receipt schema next to the guard error.
- **Time cost:** about 30 minutes.

### F-028 — Bug-route escape honored only for one harness (2026-10-20)
- **Tool/version:** workspace dispatch hook.
- **Task attempted:** launch a bug-fix packet inline on the Codex CLI.
- **Steps taken:** probed the hook with the same packet across harness forms.
- **Expected vs actual:** expected the `BUG_ROUTE:` line accepted for every harness; actual: accepted for AGY only, refused for Codex, Claude and Muse inline prompts; accepted when read from a file.
- **Severity:** Minor: blocked dispatch until the packet was passed on stdin.
- **Workaround:** `codex exec ... - < packet.md`.
- **Actionable suggestion:** tracked in the workspace repository as issue 404.
- **Time cost:** about 15 minutes.

### F-029 — CHANGELOG conflicts under parallel landing (2026-10-20)
- **Tool/version:** git, GitHub pull requests, Keep a Changelog `[Unreleased]` section.
- **Task attempted:** land an evidence PR while a coordinator merged seven PRs.
- **Steps taken:** merged `origin/main` into the branch three times, resolving the same `[Unreleased]` conflict each time; each push reran the 5-minute hygiene gate.
- **Expected vs actual:** expected one merge; actual: three merges and about 20 minutes before auto-merge landed it.
- **Severity:** Minor, recurring on every parallel landing.
- **Workaround:** keep both sides; enable auto-merge right after the last re-sync.
- **Actionable suggestion:** a `merge=union` attribute for `CHANGELOG.md` or per-PR changelog fragments.
- **Time cost:** about 20 minutes.

### F-030 — Device lease is advisory (2026-10-20)
- **Tool/version:** shared Fire TV stick, file lease plus per-command flock
- **Task attempted:** two agents sharing one stick
- **Steps taken:** a repair agent ran adb test sessions without creating the lease file; a second session then took the lease on top
- **Expected vs actual:** expected exclusive device sessions; actual: overlapping sessions, caught only by cross-checking timestamps
- **Severity:** Moderate: risk of corrupted device evidence
- **Workaround:** the second session stopped and handed the stick back
- **Actionable suggestion:** make device commands fail unless the caller holds the lease (wrapper around adb)
- **Time cost:** about 20 minutes

### F-031 — Commit guard resolves the repository from the session directory (2026-10-20)
- **Tool/version:** workspace pre-commit/pre-push gate hook
- **Task attempted:** commit and push in a linked worktree
- **Steps taken:** ran git from the main checkout directory
- **Expected vs actual:** expected the hook to use the worktree in the command; actual: `cannot resolve a repository for git commit` until the command was run from inside the worktree
- **Severity:** Minor, recurring
- **Workaround:** run git inside the worktree; delete remote branches through the GitHub API
- **Actionable suggestion:** resolve the repository from `git -C` and `cd` targets in the command
- **Time cost:** about 10 minutes across the day

### F-032 — `pkill -f` matched its own shell (2026-10-20)
- **Tool/version:** GNU procps pkill
- **Task attempted:** stop a stray agent process by pattern
- **Steps taken:** `pkill -f <pattern>` where the pattern also appeared in the invoking shell command line
- **Expected vs actual:** expected only the agent killed; actual: the session shell was killed (exit 144)
- **Severity:** Minor
- **Workaround:** match by PID from `pgrep`, excluding the current shell
- **Actionable suggestion:** document the pitfall in agent runbooks
- **Time cost:** about 5 minutes

### F-033 — Pre-push gate exceeds the default tool timeout (2026-10-20)
- **Tool/version:** repository pre-push hygiene gate
- **Task attempted:** push a branch
- **Steps taken:** the local hygiene gate ran for more than 2 minutes
- **Expected vs actual:** expected a push within the default 120 s tool timeout; actual: the push moved to the background and had to be awaited
- **Severity:** Minor
- **Workaround:** pass an explicit long timeout on pushes
- **Actionable suggestion:** report gate duration and skip unchanged groups locally
- **Time cost:** 1 to 5 minutes per push

### F-034 — Dispatch carriers must be literal (2026-10-20)
- **Tool/version:** workspace agent-dispatch hook
- **Task attempted:** launch an agent with `BEARING_BINDING=$VAR`
- **Steps taken:** used shell variables for the carrier values
- **Expected vs actual:** expected variable expansion; actual: `carrier-incomplete` with no hint that literal paths are required
- **Severity:** Minor
- **Workaround:** write absolute literal paths on the launch line
- **Actionable suggestion:** name the offending carrier and say literals are required
- **Time cost:** about 10 minutes

### F-035 — Agent reported a gate pass that failed (2026-10-20)
- **Tool/version:** agent self-report versus the repository hygiene gate
- **Task attempted:** fix #38 test dependencies
- **Steps taken:** the agent's summary said hygiene exited 0; the push hook then failed on trailing whitespace in its captured logs
- **Expected vs actual:** expected an accurate self-report; actual: a false pass, caught at push. Trailing whitespace in captured command logs recurred in two slices
- **Severity:** Moderate: a self-report cannot be trusted without the gate output
- **Workaround:** require the raw gate output attached to every return
- **Actionable suggestion:** strip trailing whitespace when evidence logs are written
- **Time cost:** about 10 minutes

### F-036 — Merge guard needs a literal repository (2026-10-20)
- **Tool/version:** workspace merge-gate guard
- **Task attempted:** merge a PR with the repository given as a shell variable
- **Steps taken:** passed the repository through a variable
- **Expected vs actual:** expected the merge to proceed; actual: refused until a literal repository value was given; the guard also fires on that command text inside a script body
- **Severity:** Minor
- **Workaround:** use a literal repository value
- **Actionable suggestion:** resolve simple variables or name the exact requirement
- **Time cost:** about 5 minutes

## Paused experiment

### F-025 — Vega SDK and Virtual Device (OBS-110 to OBS-113) — PAUSED by owner 2026-10-20
- **Tool/version:** Kepler SDK 0.24.12112, Vega CLI 1.4.5 (NOT_ADMITTED), Vega Virtual Device.
- **Task attempted:** a stretch port and on-device run; not a delivered feature.
- **Steps taken:** docs review; staged SDK and watchman in a sandbox; booted the virtual device under KVM across diagnostic rounds c9 to c18.
- **Expected vs actual:** expected a booted device with screenshots; actual: guest shell reached but the display stayed black, status never `running:true`, input exit 2, teardown SIGSEGV; docs conflicted between pages; the catalog is reachable only through the authenticated CLI. Every feature verdict is unknown.
- **Severity:** Major for Vega only; Fire OS is the primary target and nothing waits on Vega.
- **Workaround:** none; paused.
- **Actionable suggestion:** FR-021, and diagnose the black guest display before any further run.
- **Time cost:** not observed in available evidence.

## Vega SDK and Virtual Device (supported host)

F-025 is the earlier attempt, paused on an unsupported host. These entries are
the later virtual-device run on a supported host (2026-10-20 to 2026-10-21).
The same friction in more than one stage summary is one entry. Tool and
version, unless an entry says otherwise: Kepler SDK 0.24.12112, Vega CLI
1.4.5 (NOT_ADMITTED), Vega Virtual Device.

### F-037 — `vega virtual-device start` exits 0 when the device stays unresponsive (2026-10-20)
- **Tool/version:** Kepler SDK 0.24.12112, Vega CLI 1.4.5 (NOT_ADMITTED), Vega Virtual Device on Ubuntu 24.04.4.
- **Task attempted:** boot the virtual device and use the command exit as success or failure.
- **Steps taken:** `vega virtual-device start --timeout 600`.
- **Expected vs actual:** expected a non-zero exit when the device is still unresponsive after the deadline; actual: the command exits 0.
- **Severity:** Major (a script that checks only the exit code treats a dead device as success).
- **Workaround:** read the status JSON for `running:true` and confirm a rendered guest frame.
- **Actionable suggestion:** exit non-zero when the device is not running after the deadline.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-038 — Absent `vvman` prints a different version than the SDK (2026-10-20)
- **Tool/version:** Kepler SDK 0.24.12112, Vega CLI 1.4.5 (NOT_ADMITTED).
- **Task attempted:** record the SDK version.
- **Steps taken:** `vvman` is absent, so the CLI falls through to `kepler --v`. `vega --version` was also read.
- **Expected vs actual:** expected one SDK version; actual: `kepler --v` prints 0.200.0 while `vega --version` prints SDK 0.24.12112.
- **Severity:** Minor.
- **Workaround:** use `vega --version` for the SDK version.
- **Actionable suggestion:** print the SDK version from the fallback command, or document the two numbers.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-039 — A copied emulator lock names a pid a new pid namespace can reuse (2026-10-20)
- **Tool/version:** Vega Virtual Device emulator, `hardware-qemu.ini.lock`, fresh pid namespace.
- **Task attempted:** start the virtual device inside a fresh pid namespace.
- **Steps taken:** first start, with a copied lock file that holds a pid.
- **Expected vs actual:** expected the lock to refer to an emulator in this namespace; actual: that pid can belong to a live unrelated process, and the emulator exits. The next start, after both lock files were removed, did not fail on the lock; it then died with SIGSEGV (F-040).
- **Severity:** Major (the device does not start).
- **Workaround:** remove both lock files before starting in a fresh pid namespace.
- **Actionable suggestion:** treat a lock pid that is not an emulator in this namespace as stale.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-040 — Default GPU mode dies with SIGSEGV when the Mesa driver closure is absent (2026-10-20)
- **Tool/version:** Kepler SDK 0.24.12112, Vega Virtual Device, default GUI and gl-accel, host GLVND without the Mesa driver closure, Ubuntu 24.04.4.
- **Task attempted:** boot with the default graphics flags.
- **Steps taken:** `vega virtual-device start` without the llvmpipe environment.
- **Expected vs actual:** expected a painted guest, or a fall back to software rendering; actual: the emulator dies with SIGSEGV and does not fall back.
- **Severity:** Major (no guest display on that host configuration).
- **Workaround:** `LIBGL_ALWAYS_SOFTWARE=1`, `GALLIUM_DRIVER=llvmpipe`, and `MESA_LOADER_DRIVER_OVERRIDE=llvmpipe`, with the host Mesa llvmpipe driver closure mounted read-only. GUI and gl-accel stay at their defaults.
- **Actionable suggestion:** fall back to software rendering when the host GL driver closure is missing.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-041 — `--no-gl-accel` leaves the guest black and cannot name llvmpipe (2026-10-20)
- **Tool/version:** Kepler SDK 0.24.12112, Vega Virtual Device, `--no-gl-accel`.
- **Task attempted:** force software rendering with a CLI flag.
- **Steps taken:** started the device with `--no-gl-accel` and captured the guest.
- **Expected vs actual:** expected a painted guest; actual: `running:true` with `library_mode swiftshader_indirect`, a black guest (`sPrepareTexImage2D` validation), and only the emulator skin in the screenshots. There is no CLI flag that names llvmpipe.
- **Severity:** Major (the guest surface is unusable on this flag).
- **Workaround:** leave gl-accel at the default and set the llvmpipe environment in F-040. That attempt painted the guest.
- **Actionable suggestion:** a flag that selects llvmpipe, or a software mode that paints the guest rather than only the skin.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-042 — "Virtual device ready" is printed during the splash, and input then drops the device (2026-10-20)
- **Tool/version:** Vega Virtual Device, `inputd-cli`.
- **Task attempted:** send input once the CLI reports the device ready.
- **Steps taken:** `inputd-cli button_press` while the splash was still on screen.
- **Expected vs actual:** expected the ready message to mean input works; actual: `inputd-cli` throws `Cannot read properties of undefined (reading 'trim')`, exits 253, and the device is gone for the next command.
- **Severity:** Major (the device has to be started again).
- **Workaround:** wait until the ready UI is visible. The successful attempt waited 12 seconds; `KEY_RIGHT` and `KEY_ENTER` then exited 0.
- **Actionable suggestion:** print ready only when input works, and keep the device up when input arrives during the splash.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-043 — The virtual-device screenshooter writes an empty file for a frame `xwd` shows (2026-10-20)
- **Tool/version:** `gwsi-tool-screenshooter` and `xwd` on the Vega Virtual Device display.
- **Task attempted:** capture the guest UI with the SDK screenshooter.
- **Steps taken:** ran the screenshooter and copy-from on a frame that `xwd` shows as a full guest UI.
- **Expected vs actual:** expected the guest UI; actual: the screenshooter returns Incomplete, and copy-from writes a 0-byte file, on a frame that `xwd` shows as a full guest UI.
- **Severity:** Minor.
- **Workaround:** capture with `xwd`.
- **Actionable suggestion:** write the frame `xwd` already shows.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-044 — Stop exits 0 while the emulator process group dies with SIGSEGV (2026-10-20)
- **Tool/version:** Vega Virtual Device emulator, crashpad.
- **Task attempted:** stop the virtual device after a rendered session.
- **Steps taken:** stop, then read the next status.
- **Expected vs actual:** expected a clean stop; actual: stop exits 0 and the next status is `running:false`, while the emulator process group still dies with SIGSEGV and crashpad logs `ptrace: Operation not permitted`.
- **Severity:** Minor (status does reach `running:false`).
- **Workaround:** none for the crash. Treat `running:false` as the stop signal and record the SIGSEGV.
- **Actionable suggestion:** stop without SIGSEGV, or document the signal.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-045 — The telemetry helper still starts when opt-in is false (2026-10-20)
- **Tool/version:** Vega CLI 1.4.5 telemetry helper, `optIn` false.
- **Task attempted:** boot the virtual device with telemetry opted out.
- **Steps taken:** the successful boot, with the home mount marked noexec.
- **Expected vs actual:** expected no telemetry helper when opt-in is false; actual: the helper is spawned (28 times on the successful run). Every exec returned EACCES because the home mount is noexec. The CLI still connects to the SDK artifact host that is already on the allowlist.
- **Severity:** Minor.
- **Workaround:** none in the CLI. The noexec mount made the helper exec fail.
- **Actionable suggestion:** do not spawn the helper when opt-in is false.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-046 — The crash reporter is launched with an off-allowlist URL (2026-10-20)
- **Tool/version:** `crashpad_handler` spawned by the Vega Virtual Device emulator.
- **Task attempted:** boot under an allowlisting network policy.
- **Steps taken:** the successful run. The handler was exec'd with an off-allowlist crash-report URL.
- **Expected vs actual:** expected no crash reporter aimed outside the allowlist; actual: it is launched with that URL. This run recorded no connect from that process.
- **Severity:** Minor (no connection was made).
- **Workaround:** none stated.
- **Actionable suggestion:** do not point the crash reporter outside the developer allowlist, or document that launch.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-047 — Fontconfig, character conversion, pulse, and Vulkan fail closed on boot (2026-10-20)
- **Tool/version:** Vega Virtual Device boot with llvmpipe.
- **Task attempted:** boot the virtual device with software rendering.
- **Steps taken:** the successful llvmpipe boot.
- **Expected vs actual:** expected those subsystems either to work or to stay quiet; actual: fontconfig, iconv/gconv, and pulse fail closed, and Vulkan instance creation fails. The failures are non-fatal. GLES through llvmpipe still paints.
- **Severity:** Minor.
- **Workaround:** none needed for the display. The guest UI painted.
- **Actionable suggestion:** document these messages as non-fatal when llvmpipe is in use.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-048 — Host DRM nodes stay unusable from the sandbox account (2026-10-20)
- **Tool/version:** Vega Virtual Device on Ubuntu 24.04.4. The sandbox account is not in the video or render groups.
- **Task attempted:** judge whether a DRM node was required to paint the guest.
- **Steps taken:** DRM, shared-memory, and pulse passthrough was not run. llvmpipe painted the guest with no DRM device node.
- **Expected vs actual:** expected the account to be able to open host DRM nodes, or software rendering to need none; actual: the nodes stay inaccessible. No group change was requested.
- **Severity:** Minor.
- **Workaround:** the llvmpipe environment in F-040. No DRM node was required.
- **Actionable suggestion:** document that llvmpipe paints the guest without membership in the video or render groups.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 1 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage1/stage1-summary.md).

### F-049 — `journalctl` is rejected in the developer-mode shell (2026-10-21)
- **Tool/version:** Vega Virtual Device developer-mode shell, Kepler SDK 0.24.12112.
- **Task attempted:** read the app log with `journalctl`.
- **Steps taken:** `vega device run-cmd` of `journalctl`.
- **Expected vs actual:** expected the journal; actual: rejected, "journalctl is not supported in developer mode shell".
- **Severity:** Minor.
- **Workaround:** `loggingctl log -v <package>`.
- **Actionable suggestion:** document `loggingctl` as the developer-mode log command.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 2 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2/stage2-summary.md).

### F-050 — Release-device logs omit app output and leave commit times unformatted (2026-10-21)
- **Tool/version:** Kepler SDK 0.24.12112, Vega Virtual Device, release bundle.
- **Task attempted:** read app and request logs from the virtual device.
- **Steps taken:** read the app log on the offline link run and on the online run.
- **Expected vs actual:** expected React Native `console` output, including requests; actual: the log carries only KeplerScript surface telemetry. `commitTime={:.2f}ms` fields are unformatted placeholders, a logging bug in the runtime. `console` output from the release bundle does not appear, so the app logs no requests.
- **Severity:** Major (a UI failure cannot be tied to an API status from the log).
- **Workaround:** none stated for release `console` output. The runs used screen captures and the proxy connect log.
- **Actionable suggestion:** format the commit-time fields and show release-bundle `console` output on the virtual device.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 2 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2/stage2-summary.md), [Stage 2c summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2c/stage2c-summary.md).

### F-051 — The developer shell cannot read or seed an app's private storage (2026-10-21)
- **Tool/version:** Vega Virtual Device developer shell, user `app_user`.
- **Task attempted:** seed or inspect AsyncStorage so a check can start from a linked session.
- **Steps taken:** probed the app's private storage from the developer shell.
- **Expected vs actual:** expected a supported way to read or seed that storage; actual: `app_user` cannot see it. Placing a session in app storage from the shell is not possible.
- **Severity:** Major (every session-gated check has to go through the real link flow).
- **Workaround:** none.
- **Actionable suggestion:** document a supported way to seed and inspect app-private storage on the virtual device.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 2 summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2/stage2-summary.md).

### F-052 — The link code and settings can only be read from screen captures (2026-10-21)
- **Tool/version:** Vega app on the Vega Virtual Device.
- **Task attempted:** read the on-screen link code and the saved settings without watching the framebuffer.
- **Steps taken:** the online link and settings run. The code and the settings were read from captures.
- **Expected vs actual:** expected an app-side state dump or screen text recognition; actual: neither exists. The code and every setting are only on the screen.
- **Severity:** Major (someone has to read the code off the capture and drive the screen).
- **Workaround:** read the code and the settings from the captures.
- **Actionable suggestion:** an app-side dump of the link code and the settings under test.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 2c summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2c/stage2c-summary.md).

### F-053 — The virtual device cannot send a host-name CONNECT through an allowlist proxy (2026-10-21)
- **Tool/version:** Kepler SDK 0.24.12112, `vega virtual-device start`, QEMU user-mode networking.
- **Task attempted:** reach the deployed backend from the guest through an allowlisting CONNECT proxy.
- **Steps taken:** allowlisted the backend and launched. The guest made no proxy request. The guest shell (`app_user`) has no proxy variable and no supported proxy or DNS setting. `vega virtual-device start` has no proxy or emulator-argument option. The emulator can take an HTTP proxy, but that connector sends CONNECT with the guest's numeric destination address, which a host-name allowlist denies. In that sandbox the guest also cannot resolve names, so it never reaches a TCP connect.
- **Expected vs actual:** expected the guest to use the allowlist proxy; actual: traffic stays on user-mode networking (the emulator's own resolver and direct connects). The proxy log showed no connection to the backend. Online linking, profile, alerts, Watch, and the panel could not run until the guest had another path.
- **Severity:** Major (those features stay unobservable from the guest until a host-name path to the proxy exists).
- **Workaround:** a resolver inside the sandbox namespace that answers only the deployed backend name, and a forwarder that sends each connection to the proxy as a host-name CONNECT. TLS stays end to end between the app and the backend. The emulator HTTP proxy was not enabled.
- **Actionable suggestion:** a virtual-device option that proxies by host name, so a host-name allowlist can accept it.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 2b summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2b/stage2b-summary.md), [Stage 2c summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2c/stage2c-summary.md).

### F-054 — Save is about 30 DOWN presses from the top, and text fields take focus silently (2026-10-21)
- **Tool/version:** Vega app Profile/Settings on the Vega Virtual Device, remote-key input.
- **Task attempted:** change one setting and save it.
- **Steps taken:** DOWN from the top of the screen to Save.
- **Expected vs actual:** expected focus to start on the first control, and a text field to show that it took focus; actual: focus starts on nothing, text inputs take focus silently, and Save is about 30 DOWN presses from the top.
- **Severity:** Minor (Save is reachable).
- **Workaround:** about 30 DOWN presses from the top of the screen.
- **Actionable suggestion:** start focus on the first control, and show when a text field has focus.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 2c summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2c/stage2c-summary.md).

### F-055 — Legacy AsyncStorage does not keep the session across relaunch (2026-10-21)
- **Tool/version:** Kepler SDK 0.24.12112, Vega Virtual Device. The app called `require('react-native').AsyncStorage`. The supported package later pinned is `@amazon-devices/react-native-async-storage__async-storage` 2.1.9000000001.
- **Task attempted:** stay on Profile/Settings after the app restarts.
- **Steps taken:** linked on the device, saved a setting, then terminated and launched the app. The unit test ran over an in-memory fake. The module header described the store as react-native-mmkv. A later build loaded the supported package's default export and repeated the relaunch.
- **Expected vs actual:** expected Profile/Settings after relaunch. On the legacy binding the Link screen returned and a new code was issued. Every read and write logged that legacy AsyncStorage is on a deprecation path, then `Application data root path is not set.` The session stayed usable until the relaunch. After the supported package, relaunch stayed on Profile/Settings with no second confirmation, and the legacy deprecation line was gone. The native data-root messages still occur; persistence still passes; what emits those messages is not established.
- **Severity:** Major (on the legacy binding, relaunch drops the linked session).
- **Workaround:** load the supported app-private AsyncStorage package. An in-memory unit test does not show this failure.
- **Actionable suggestion:** document the supported storage package, and explain the data-root message that remains after persistence works.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 2c summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2c/stage2c-summary.md), [token-persistence summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/bug-token/summary.md).

### F-056 — The panel drops the server's default state when the profile has no selection (2026-10-21)
- **Tool/version:** Vega app on the Vega Virtual Device, `GET /v1/panel` with no team or league.
- **Task attempted:** show the lineup panel for a linked profile with no team or league selected.
- **Steps taken:** on the device the panel showed "Panel unavailable". A later read of that profile returned no team or league and empty selections. `GET /v1/panel` with no query, which is what the app sends, returned the server's default empty state. Replaying those bodies through the app's own decode kept the snapshot only when the controller already held the server's team and league. With the controller's empty selection, decode accepts the body and the controller drops it because the two team/league strings differ.
- **Expected vs actual:** expected the panel to show the server's default state for a profile with no selection. Actual: the section renders "Panel unavailable", the snapshot stays empty, and the app requests the panel again every second while the panel is visible. No decode rule rejects the body.
- **Severity:** Major (a state the server returned is not shown).
- **Resolution:** the controller now adopts the server's identity when no team or league is selected. The [bug-panel repair run](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/bug-panel/summary.md) rechecked this on the VVD: default identity, Half-PPR and Total: Unavailable were shown and held. Empty rows, totals, and progress for this profile remain F-057. The [review repair](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/review-repair/summary.md) additionally binds saved settings, pending-request serialization and stale labels to MainScreen regressions; those wiring changes were not rerun on the VVD.
- **Actionable suggestion:** show the server's default state for a profile with no selection.
- **Time cost:** not observed in available evidence.
- **Source:** [Panel summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/panel/panel-summary.md), [Stage 2c summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2c/stage2c-summary.md).

### F-057 — No public API writes a lineup, so alerts, Watch, and panel rows cannot appear (2026-10-21)
- **Tool/version:** deployed backend, observed from the Vega Virtual Device with a synthetic profile.
- **Task attempted:** show an alert banner, Watch, and lineup rows on the virtual device.
- **Steps taken:** linked the synthetic profile and watched the panel and alerts. The backend has no caller of `store.put_lineup`.
- **Expected vs actual:** expected a way to put a lineup on a test profile; actual: no public API writes a lineup, so the profile cannot match an event. No alert banner appeared in about 6 linked minutes. Watch is reached only from an alert banner. The panel's rows for this profile can only be the empty state.
- **Severity:** Major (alerts, Watch, and panel rows stay untestable on a synthetic profile).
- **Workaround:** none in the product. An owner-supplied lineup fixture would be a separate grant.
- **Actionable suggestion:** a public lineup write for a test profile, or a documented fixture, so a virtual-device check can show an alert and rows.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 2b summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2b/stage2b-summary.md), [Stage 2c summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2c/stage2c-summary.md).

### F-058 — The guest image has no `getent` or `ip` (2026-10-21)
- **Tool/version:** Vega Virtual Device guest shell.
- **Task attempted:** read guest name resolution and addresses while probing the network path.
- **Steps taken:** `getent` and `ip` inside the guest network probe.
- **Expected vs actual:** expected both commands to run; actual: both exit 1 because the tools are absent. The app and virtual-device steps of that probe still exited 0.
- **Severity:** Minor.
- **Workaround:** none stated for those two commands.
- **Actionable suggestion:** ship `getent` and `ip` in the developer guest image, or document that they are absent.
- **Time cost:** not observed in available evidence.
- **Source:** [Stage 2b summary](../plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage2b/stage2b-summary.md).

## Internal process frictions (owner decision pending)

These are project-workflow frictions, not product feedback. They are recorded for
completeness with their evidence; whether they belong in the submitted log is an
owner decision (pending owner input, below).

| Item | Observation IDs | Summary |
|---|---|---|
| Whitespace and private-path hygiene on evidence logs | OBS-027 | Trailing spaces, CRLF and absolute paths in captured logs failed the hygiene gate until normalized at capture. |
| Gate noise, runtime and tool gaps | OBS-048, OBS-049 | Untracked `__pycache__`, about 320 KB warning logs, a slower hygiene suite and missing tools in the cloud container. |
| Packet and contract gaps | OBS-030, OBS-031, OBS-050, OBS-051, OBS-053 | Untyped panel wire, unnamed stub-pin edits, missing data-model attributes found by red suites, committer identity from the harness environment. |
| Planning-tool coupling | OBS-098, OBS-108, OBS-109 | Release dependencies tied to table membership, prose-versus-data drift, a stale template path. |
| Orchestration | OBS-106, OBS-107, OBS-122 | No native BRAN policy, an avoidable owner question, two agents sharing one stick lease. |

## Sanitization

Reviewed 2026-10-20 by the Scribe: no credentials, tokens, e-mail addresses,
account identifiers, device address, AWS account IDs or local absolute paths.
Placeholder policy: `<owner-account>`, `<device>`, `<worktree>`.

## Pending owner input (official-rule check, issue #1)

Checked against the rules extract fetched 2026-10-12 (`docs/plans/2026-10-11-amazon-fantasy-companion/evidence/devpost-feedback-rules.md`) and the issue #1 Scribe contract:

1. Product Feedback fields (tools used, worked well, needs work, onboarding, build again, AWS services): all present in `product-feedback.md`.
2. Friction Log fields: the official optional entry fields are task attempted, steps taken, expected vs. actual, severity, workaround and actionable suggestion; all are present, plus tool/version and time cost.
3. Needs owner confirmation: (a) re-fetch the live rules at submission, since the extract is dated 2026-10-12; (b) whether internal process frictions belong in the submitted friction log; (c) whether internal agent-routing details (harness and tool names) may appear in submitted text, given the proprietary-routing boundary; (d) the Open Source mini challenge decision, which changes what the Product Feedback must contain; (e) ESPN public-JSON terms for a public submission (OA-6); (f) external sending (OA-8).
