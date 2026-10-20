# Feature requests (optional submission section; assembled 2026-10-20)

Each request cites a source observation in `observations.md`. Priority is the
Scribe's reading of the observed impact on this project (Critical / Important /
Nice-to-have); the owner may re-rank before any external use. Format follows the
Devpost optional section: description, why it matters, priority. Nothing here has
been sent anywhere (OA-8 owner action).

## Platform and vendor requests

| ID | Request | Why it matters to this project | Priority | Source |
|---|---|---|---|---|
| FR-005 | A supported way for a third-party Fire TV app to show an actionable heads-up notification over other apps' playback, or documentation that Fire OS 8 does not, with the intended alternative. | A foreground-service high-priority notification with Watch/Dismiss actions posted but never peeked on Fire OS 8.1.8.5, so the alert shipped panel-only. | Critical | OBS-003, OBS-004 |
| FR-006 | A supported split-view or "companion panel beside video" mechanism for Fire TV, or guidance for provider apps to declare PiP so a companion can fit beside them. | No supported route placed a panel beside Prime Video without overlap; the panel runs full-screen instead. | Important | OBS-006 |
| FR-007 | Public deep-link documentation for live sports events in provider apps (Prime Video first), including a mapping from a schedule event to a provider title or channel id. | Only app home, search and per-title pages were reachable; no documented way reaches a specific game. | Important | OBS-008 |
| FR-008 | Published timeline and criteria for the Yahoo Fantasy API access program, and documented behavior for unapproved apps (403 while OAuth succeeds). | The lineup source fell back to manual entry because approval could not arrive in time. | Important | OBS-080, OBS-082 |
| FR-012 | Fix the AWS CLI `aws login` browser flow for the "Continue with an active session" path (400 Bad Request) and for concurrent logins. | Each sign-in needed a documented workaround; a session expired mid-deploy. | Important | OBS-060, OBS-061 |
| FR-009 | Document how to detect an installed-but-disabled package on Fire OS, and that `pm disable` is unavailable to the ADB shell. | Disabled-state detection was provable only in-app with a fixture package. | Nice-to-have | OBS-011 |
| FR-010 | Document UI-automation guidance for Fire TV (D-pad focus versus touch, keyboard "Previous" in multiline fields). | On-device checks needed trial and error to find a reliable oracle. | Nice-to-have | OBS-012 |
| FR-011 | A published contract and change notes for ESPN's public JSON, and finer-than-minute `modified` precision on plays. | Correction timing cannot be derived from a final snapshot and the schema has surprising shapes. | Nice-to-have | OBS-071, OBS-072 |
| FR-013 | Document a supported way to exercise IAM grants offline (Moto does not enforce IAM). | A missing `Scan`/`PutItem` grant is invisible to unit tests. | Nice-to-have | OBS-044 |
| FR-014 | mutmut: allow nested `also_copy` paths and a documented loaded-host timeout setting. | Clean runs failed on a missing template; two runs timed out under load. | Nice-to-have | OBS-045 |
| FR-015 | diff-cover: report files with no executable lines as excluded rather than missing. | A docstring-only module produced REPORT_INCOMPLETE. | Nice-to-have | OBS-046 |
| FR-022 | Gradle/AGP: a per-configuration dependency resolution report that matches the real Kotlin, compiler and lint graphs. | A merged closure hid versions chosen in separate configurations. | Nice-to-have | OBS-024 |
| FR-021 | Vega documentation: reconcile screenshot support and supported Ubuntu versions between pages; document a secure credential store and a Jest setup. (Paused experiment.) | Conflicting pages slowed planning. | Nice-to-have | OBS-110 |

## Project-tooling requests (internal; owner decides whether to include)

| ID | Request | Why it matters | Priority | Source |
|---|---|---|---|---|
| FR-001 | Usage-limit refusals carry a machine-readable marker (distinct exit code or field). | The orchestrator currently matches log text to tell "account exhausted" from "task failed". Carried from FR1 of the g1-resume note and FR4 of the g2-progress note. | Nice-to-have | OBS-090, OBS-091 |
| FR-002 | `check-vendor.py` ignores `__pycache__` in its file-set assertion. Carried from FR1 of the g2-progress note. | Reviewers re-running lint need manual cleanup. | Nice-to-have | OBS-104 |
| FR-003 | Allow generated-section identities in revision `changes`, or document the summary convention. Carried from FR2 of the g2-progress note. | Keeps every rendered change traceable. | Nice-to-have | OBS-104 |
| FR-004 | Update the packet template's preparation-reference path. Carried from FR3 of the g2-progress note. | Removes a stale lookup. | Nice-to-have | OBS-109 |
| FR-016 | OCR delegation support for Markdown planning documents. | Planning-only diffs get no rule coverage. | Nice-to-have | OBS-099 |
| FR-017 | Reverify: a `--version` flag and a claim for APK manifest semantics. | Version came from package metadata; an APK/DEX gap stayed typed. | Nice-to-have | OBS-100 |
| FR-018 | Plan renderer: a digest-bound non-embedded fallback when one model fails; verifiers with a `--check-only` mode. | One failed embed aborted a whole render; verifiers rewrite outputs. | Nice-to-have | OBS-097 |
| FR-019 | Pass the packet's assigned role to the orchestrator write-lock hook envelope for in-process subagents. | The hook denied a legitimate planning write. | Important | OBS-096 |
| FR-020 | SEIT schema checks for register coverage, one-ID traceability and command resolution. | A per-artifact script had to compensate. | Nice-to-have | OBS-101 |
| FR-023 | A shared `developer_feedback` shape (id, tool, observation, class, evidence) across receipts. | Assembly needed a custom extractor for five shapes. | Nice-to-have | OBS-120 |
| FR-024 | Name stub-pin test files as expected retirement edits in product packets. | Three product slices hit the same unlisted-write conflict. | Nice-to-have | OBS-050 |
