# Developer feedback — Scribe session, AFC catch-up observations (2026-10-14)

Scope: event transcription only (scribe packet scr-catchup). Records the orchestrator's verified observations O1-O10 from 2026-10-13 to 2026-10-14, each as the source list states it. No product edits, no external sending.
Tracks: Fire TV track + AWS Builder mini challenge (per DEC-AFC-SD-008). No AWS services used in this Scribe session.
Field rules: docs/plans/2026-10-11-amazon-fantasy-companion/evidence/devpost-feedback-rules.md (DEC-AFC-SD-025). Durations, costs, and versions are stated only where the source list gives them; any other field is marked unknown, never estimated.

## Product feedback: Claude Code scribe catch-up session

- Tools used and for what: Claude Code (Claude Haiku 5.5, scribe role) with shell reads of the two 2026-10-13 scribe entries, the feedback rules, and the gate script; one new file written.
- What worked well: the packet, the 2026-10-13 entries, and the rules file were enough to match the house format without further lookup.
- What needs work: none observed in this session. The observations below come from the orchestrator's list, not from this session.
- Onboarding (zero to hello world): unknown; not assessed by this packet.
- Would you build with this again: unknown; not assessed by this packet.

## Friction log

Every entry below is one observation from the orchestrator's verified list O1-O10. This session added no observations of its own.

### O1 — Cursor Agent usage limit blocked the planned Grok reviewer route

- Tool: Cursor Agent CLI, planned Grok 4.7 reviewer route.
- Observation: on 2026-10-14 Cursor Agent returned "You're out of usage". The planned Grok 4.7 reviewer route was unavailable.
- Measured cost: unknown.
- Impact: the planned reviewer route did not run.
- Workaround used: Codex GPT-6 Astra fallback reviewer route.
- Evidence pointer: journey DEC-AFC-SD-043.
- Unknown: reset time, run duration.

### O2 — git push to the journey branch failed silently

- Tool: git push and the repository pre-push hygiene gate.
- Observation: git push to the journey branch failed silently for several commits because its output went to /dev/null. The pre-push hygiene gate rejected absolute home paths and DOC-LINKs to gitignored .log files.
- Measured cost: several commits (exact count unknown).
- Impact: the failed pushes were not shown by the command output.
- Workaround used: $HOME redaction and .log to .txt rename, fixed in journey 4ed6753.
- Evidence pointer: journey 4ed6753.
- Lesson recorded in source: always verify pushes with git ls-remote.
- Unknown: exact number of failed commits.

### O3 — Repository git hooks need the backend test venv on PATH

- Tool: repository git hooks (commit and push).
- Observation: commits and pushes fail unless the backend test venv is on PATH.
- Measured cost: unknown.
- Impact: commits and pushes fail without the venv on PATH.
- Workaround used: put the backend test venv bin directory on PATH before commit or push.
- Evidence pointer: issue #61 (repository not named in the source list).

### O4 — Android Gradle closure scanned INDETERMINATE

- Tool: Android build toolchain (Fire TV starter Gradle closure) and software supply-chain scan.
- Observation: the starter's Gradle closure (AGP 8.2.2 / Kotlin 1.9.0) scanned INDETERMINATE. Kotlin-compiler-embedded CVEs (protobuf 2.6.1, jline 3.24.1) were accepted as build-host residual risk.
- Measured cost: unknown.
- Impact: the tv-app toolchain was changed by owner decision.
- Workaround used: owner decision SD-041 upgraded tv-app to AGP 9.3.1 / KGP 2.4.21 / Gradle 9.7.0 with strict dependency verification. Owner decision SD-042 patched bcprov, jose4j, and jdom2.
- Evidence pointer: owner decisions SD-041 and SD-042 (location not named in the source list).

### O5 — Android instrumented-test runner pulls a netty closure with HIGH/CRITICAL CVEs

- Tool: Android instrumented-test runner (UTP).
- Observation: UTP pulls a netty closure with HIGH and CRITICAL CVEs, including CVE-2026-75595. The closure is not admitted.
- Measured cost: unknown.
- Impact: on-device tests cannot run until the owner decides; owner decision pending.
- Workaround used: none stated.
- Evidence pointer: not named in the source list.

### O6 — mutmut runs timed out under machine load

- Tool: mutmut mutation runs.
- Observation: runs 1 and 2 timed out under machine load and exited 3. A later run passed after calibrated timeouts.
- Measured cost: exit 3 on runs 1 and 2; result 99.49% after calibrated timeouts (B01).
- Impact: runs 1 and 2 did not complete.
- Workaround used: calibrated timeouts.
- Evidence pointer: B01.

### O7 — Fire TV test device not found; newer models may ship a different OS

- Tool: Fire TV device (owner's stick).
- Observation: the owner's stick could not be found on 2026-10-14. Newer Fire TV Stick models may ship Vega OS instead of Fire OS, which an Android APK cannot target.
- Measured cost: unknown.
- Impact: device steps are blocked: ADB install, on-device visual review, and the panel-beside-video spike.
- Workaround used: none stated.
- Evidence pointer: not named in the source list (orchestrator verified list, 2026-10-14).

### O8 — Muse Code profile name does not match the CLI model id

- Tool: Muse Code CLI (muse exec).
- Observation: the profile name "Muse WonderFull" maps to CLI model id muse-wonder-full-1.0. The ids muse-wonderfull, muse-wonderful, and muse-wonder-full return "does not exist or you lack access". muse exec takes the prompt positionally or via --prompt-file; there is no --prompt flag.
- Measured cost: unknown.
- Impact: calls using the three other ids returned the access error.
- Workaround used: unknown; the source list gives the working id (muse-wonder-full-1.0) and the prompt forms (positional or --prompt-file).
- Evidence pointer: not named in the source list.

### O9 — AWS CLI SSO session for afc-dev expired

- Tool: AWS CLI, afc-dev SSO profile.
- Observation: the afc-dev SSO session expired. The CLI returned "Your session has expired. Please reauthenticate using 'aws login'".
- Measured cost: unknown.
- Impact: deploy slice L02 waits for the owner to log in.
- Workaround used: none; L02 waits for the owner to log in.
- Evidence pointer: deploy slice L02 (no receipt path given in the source list).

### O10 — Issue-label hook refuses this repository

- Tool: Alphazedehq/hooks/issue-labels.py.
- Observation: the hook refuses this repository. Issues were filed with gh directly.
- Measured cost: unknown.
- Impact: issues were filed outside the hook.
- Workaround used: direct gh filing.
- Evidence pointer: not named in the source list.
- Unknown: the refusal reason.

## Feature requests

None recorded in this catch-up. The source list carries no feature request, and this entry adds none.
