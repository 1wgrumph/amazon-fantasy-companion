# Developer feedback — Scribe session, AFC catch-up observations (2026-10-14)

Scope: event transcription only (scribe packet scr-catchup). Records the orchestrator's verified observations O1-O10 from 2026-10-13 to 2026-10-14, each as the source list states it. No product edits, no external sending.
Tracks: Fire TV track + AWS Builder mini challenge (per DEC-AFC-SD-008). No AWS services used in this Scribe session.
Field rules: docs/plans/2026-10-11-amazon-fantasy-companion/evidence/devpost-feedback-rules.md (DEC-AFC-SD-025). Friction entries use the house field set: Tool, Task, Steps taken, Expected vs actual, Classification, Severity, Evidence, Impact, Workaround used, Actionable suggestion, Uncertainty. Severity is Blocker, Major, Minor, None, or unknown. A field is filled only from the source list; otherwise it reads unknown. Durations, costs, and versions appear only where the source list gives them.

## Product feedback: Claude Code scribe catch-up session

- Tools used and for what: Claude Code (scribe role) with shell reads of the two 2026-10-13 scribe entries, the feedback rules, and the gate script; one new file written.
- What worked well: the packet, the 2026-10-13 entries, and the rules file were enough to match the house format without further lookup.
- What needs work: none observed in this session. The observations below come from the orchestrator's list, not from this session.
- Onboarding (zero to hello world): unknown; not assessed by this packet.
- Would you build with this again: unknown; not assessed by this packet.

## Friction log

Every entry below is one observation from the orchestrator's verified list O1-O10. This session added no observations of its own.

### O1 — Cursor Agent usage limit made the planned reviewer route unavailable

- Tool: Cursor Agent CLI.
- Task: planned reviewer route.
- Steps taken: unknown.
- Expected vs actual: expected unknown; actual: Cursor Agent CLI usage limit made the planned reviewer route unavailable; the configured fallback reviewer route (Codex CLI) was used. The message was "You're out of usage" on 2026-10-14.
- Classification: unknown.
- Severity: unknown.
- Evidence: journey DEC-AFC-SD-043.
- Impact: the planned reviewer route did not run.
- Workaround used: the configured fallback reviewer route (Codex CLI).
- Actionable suggestion: unknown.
- Uncertainty: reset time and run duration are not stated in the source list.

### O2 — git push to the journey branch failed silently

- Tool: git push and the repository pre-push hygiene gate.
- Task: push commits to the journey branch.
- Steps taken: push output was sent to /dev/null, so failures were not shown; the pre-push hygiene gate rejected absolute home paths and DOC-LINKs to gitignored .log files.
- Expected vs actual: expected unknown; actual: git push to the journey branch failed silently for several commits.
- Classification: unknown.
- Severity: unknown.
- Evidence: journey 4ed6753.
- Impact: the failed pushes were not reported by the command output.
- Workaround used: $HOME redaction and .log to .txt rename, applied in journey 4ed6753.
- Actionable suggestion: verify pushes with git ls-remote (lesson recorded in the source list).
- Uncertainty: the exact number of failed commits is not stated.

### O3 — Repository git hooks need the backend test venv on PATH

- Tool: repository git hooks (commit and push).
- Task: commit and push.
- Steps taken: unknown.
- Expected vs actual: expected unknown; actual: commits and pushes fail unless the backend test venv is on PATH.
- Classification: unknown.
- Severity: unknown.
- Evidence: issue #61 (repository not named in the source list).
- Impact: commits and pushes fail without the backend test venv on PATH.
- Workaround used: backend test venv bin directory placed on PATH before commit or push.
- Actionable suggestion: unknown.
- Uncertainty: unknown.

### O4 — Android Gradle closure scanned INDETERMINATE

- Tool: Android build toolchain (Fire TV starter Gradle closure) and software supply-chain scan.
- Task: supply-chain scan of the Fire TV starter's Gradle closure.
- Steps taken: unknown.
- Expected vs actual: expected unknown; actual: the starter's Gradle closure (AGP 8.2.2 / Kotlin 1.9.0) scanned INDETERMINATE.
- Classification: unknown.
- Severity: unknown.
- Evidence: owner decisions SD-041 and SD-042 (location not named in the source list).
- Impact: the tv-app toolchain was changed by owner decision. Kotlin-compiler-embedded CVEs (protobuf 2.6.1, jline 3.24.1) were accepted as build-host residual risk.
- Workaround used: owner decision SD-041 upgraded tv-app to AGP 9.3.1 / KGP 2.4.21 / Gradle 9.7.0 with strict dependency verification; owner decision SD-042 patched bcprov, jose4j, and jdom2.
- Actionable suggestion: unknown.
- Uncertainty: unknown.

### O5 — Android instrumented-test runner pulls a netty closure with HIGH/CRITICAL CVEs

- Tool: Android instrumented-test runner (UTP).
- Task: resolve the runner's dependency closure before on-device tests.
- Steps taken: unknown.
- Expected vs actual: expected unknown; actual: UTP pulls a netty closure with HIGH and CRITICAL CVEs (including CVE-2026-75595). The closure is not admitted.
- Classification: unknown.
- Severity: unknown.
- Evidence: CVE-2026-75595 as cited in the source list; no receipt path given.
- Impact: on-device tests cannot run until the owner decides; owner decision pending.
- Workaround used: unknown.
- Actionable suggestion: unknown.
- Uncertainty: the owner decision outcome is pending.

### O6 — mutmut runs timed out under machine load

- Tool: mutmut mutation runs.
- Task: mutation runs under machine load.
- Steps taken: runs 1 and 2 timed out and exited 3; a later run passed after calibrated timeouts with result 99.49% (B01).
- Expected vs actual: expected unknown; actual: runs 1 and 2 timed out under machine load and exited 3.
- Classification: unknown.
- Severity: unknown.
- Evidence: B01 as cited in the source list.
- Impact: runs 1 and 2 did not complete.
- Workaround used: calibrated timeouts.
- Actionable suggestion: unknown.
- Uncertainty: unknown.

### O7 — Fire TV test device not found; newer models may ship a different OS

- Tool: Fire TV device (owner's stick).
- Task: device steps: ADB install, on-device visual review, and the panel-beside-video spike.
- Steps taken: unknown.
- Expected vs actual: expected unknown; actual: the owner's stick could not be found on 2026-10-14. Per the orchestrator's observation, newer Fire TV Stick models may ship Vega OS instead of Fire OS, which an Android APK cannot target.
- Classification: unknown.
- Severity: unknown.
- Evidence: not named in the source list (orchestrator verified list, 2026-10-14).
- Impact: the device steps are blocked.
- Workaround used: unknown.
- Actionable suggestion: unknown.
- Uncertainty: unknown.

### O8 — Muse Code profile display name does not match the CLI model id

- Tool: Muse Code CLI (muse exec).
- Task: headless exec with a Muse Code model.
- Steps taken: three name variants were tried as the CLI model id.
- Expected vs actual: expected unknown; actual: the profile display name for a Muse Code model differs from its CLI model id; three name variants returned "does not exist or you lack access".
- Classification: unknown.
- Severity: unknown.
- Evidence: not named in the source list.
- Impact: calls using the three name variants returned the access error.
- Workaround used: the CLI model id that the source list maps to the profile name (id not reproduced here). Prompt passed positionally or via --prompt-file, since muse exec has no --prompt flag.
- Actionable suggestion: unknown.
- Uncertainty: unknown.

### O9 — AWS CLI SSO session expired

- Tool: AWS CLI (the project's AWS CLI login profile).
- Task: deploy slice L02.
- Steps taken: unknown.
- Expected vs actual: expected unknown; actual: the login session expired, and the CLI returned "Your session has expired. Please reauthenticate using 'aws login'".
- Classification: unknown.
- Severity: unknown.
- Evidence: deploy slice L02 (no receipt path given in the source list).
- Impact: deploy slice L02 waits for the owner to log in.
- Workaround used: unknown.
- Actionable suggestion: unknown.
- Uncertainty: when the session expired is not stated.

### O10 — Issue-label hook refuses this repository

- Tool: the workspace issue-label hook.
- Task: file GitHub issues for this repository through the issue-label hook.
- Steps taken: the hook refused this repository; issues were filed with gh directly.
- Expected vs actual: expected unknown; actual: the hook refuses this repository.
- Classification: unknown.
- Severity: unknown.
- Evidence: not named in the source list.
- Impact: issues were filed outside the hook.
- Workaround used: direct gh filing.
- Actionable suggestion: unknown.
- Uncertainty: the refusal reason is not stated.

## Feature requests

None recorded in this catch-up. The source list carries no feature request, and this entry adds none.
