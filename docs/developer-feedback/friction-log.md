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
