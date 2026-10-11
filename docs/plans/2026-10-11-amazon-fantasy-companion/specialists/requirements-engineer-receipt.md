---
type: specialist-receipt
title: Requirements Engineer gate — AFC-2026-10-11
okf_status: draft
tags: [requirements, planning, afc]
---

verdict: **REPAIRABLE_FAILURE**

candidate_ref: `plan/2026-10-11-amazon-fantasy-companion` at `2c13a6bf560e87d11864cc6234f48e40dd9cf529` (`2c13a6b`) plus untracked `docs/plans/2026-10-11-amazon-fantasy-companion/`.

technical-plan sha256: `b3b23146b59109ba83f89600d5b601076b348998235ad722cd0348d60e45d461`.

changed_paths: `docs/plans/2026-10-11-amazon-fantasy-companion/specialists/requirements-engineer-receipt.md` only.

rows_checked: **81 = 65 AC + 16 RISK; 46 failing rows, 35 PASS rows**. Failures include wording/metadata repairs, not 46 independent product defects. No plan row was edited.

blocker: The candidate register needs the exact statement/metadata repairs below before a PASS. No confirmed owner decision must change; no owner question or capability blocker prevents these repairs. This is one initial gate, not a correction rerun, author realization, implementation assurance, or integrated acceptance.

mechanical_receipt: Supplied `specialists/ac-mechanical-lint-r0.txt` lines 1–66, reproduced against the hashed candidate: **65 rows; 3 flags; exit 0**. This adapter reports findings without failing its exit status. It imports library constants from `lint-sdoc.py`; it is not a full `lint-sdoc.py --profile library` execution, cannot establish SDoc conformance, and its regex skips RISK rows. The authorized Markdown register takes precedence over the skill’s draft-SDoc input assumption. Supplemental read-only risk inventory is recorded below.

## Failing rows — per-row findings table

Each section is one failing row. Quoted phrases are candidate evidence at the stated technical-plan line. Metadata-only repairs repeat the exact existing statement. Grouped clauses are retained where they form one observable interaction, record schema or deliverable acceptance contract; “and” alone is not a defect. Proposed controls for risk rows preserve their original risk text as rationale.

### AC-AFC-FEED-01

Checklist: CHK-RE-17 INCOMPLETE; CHK-RE-24 CONTRADICTION; CHK-RE-39 INTERFACE_INCONSISTENT. Evidence: technical plan line 143.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-FEED-01 | wording; traceability | “normalize each ESPN play” into the six listed event types has no disposition for an ordinary non-triggering play and excludes the correction type required by FEED-02 and CONTRACT-AFC-EVENT. | The backend shall emit GameEvents for ESPN plays and game-state changes that meet the event definitions in DES-AFC-FEED, and for corrections required by AC-AFC-FEED-02, using CONTRACT-AFC-EVENT with source game id, source play id, event type, involved ESPN athlete ids, possession team, field position, period, game clock, source timestamp and ingest timestamp; it shall emit no GameEvent for a play that meets none of those definitions and shall reject a schema-invalid response without changing stored GameEvents. |

Metadata repair: Keep the existing Source, Verification and Allocation.

### AC-AFC-FEED-02

Checklist: CHK-RE-24 CONTRADICTION; CHK-RE-48 NO_PASS_FAIL. Evidence: technical plan line 144.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-FEED-02 | wording; measurability | “at most one GameEvent per source game id and source play id” forbids the additional correction GameEvent required by the same sentence; “exactly one correction” does not distinguish repeated retrieval from successive corrections. | The backend shall emit at most one original GameEvent per source game id and source play id; when the recorded scoring content for that play changes, it shall emit one correction GameEvent for that change referencing the original event, and repeated retrieval of unchanged scoring content shall emit no additional event. |

Metadata repair: Keep the existing Source, Verification and Allocation.

### AC-AFC-ALERT-04

Checklist: CHK-RE-24 CONTRADICTION; CHK-RE-30 INCORRECT; CHK-RE-35 UNREALISTIC_PERFORMANCE. Evidence: technical plan line 154.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-ALERT-04 | traceability; measurability | “show each released alert as a heads-up notification” ignores CTRL-01’s panel-only setting; “within one alert_poll_wait” reuses a server request-wait bound as a physical-device latency guarantee despite #1’s explicit exclusion of hardware performance verification. | While a provider app plays video in the foreground and the customer is in an enabled viewing period with heads-up presentation selected, the TV app shall retrieve and present each released alert as a heads-up notification with Watch and Dismiss actions without bringing the companion app to the foreground; while panel-only presentation is selected, it shall suppress heads-up notifications. |

Metadata repair: Keep the existing Source, Verification and Allocation.

### AC-AFC-ALERT-05

Checklist: CHK-RE-25 GLOSSARY_MISMATCH; CHK-RE-49 VAGUE_TERM. Evidence: technical plan line 155.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-ALERT-05 | undefined term; measurability | “wording intensity follows the customer’s excitement level” supplies no observable mapping; DES-AFC-POLICY says three levels but does not define their template mapping. | The backend shall select alert text through a documented mapping from each customer-selectable excitement level to a fixed template, substituting only GameEvent fields and matched player data; no generative model shall determine an event, score or player identity. |

Metadata repair: Keep the existing Source, Verification and Allocation.

### AC-AFC-PANEL-01

Checklist: CHK-RE-25 GLOSSARY_MISMATCH; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 177.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-PANEL-01 | undefined term; measurability | “a labeled default scoring” has no rule table or coefficients in the Glossary, DES-AFC-LINEUP or CONTRACT-AFC-LINEUPSOURCE; a label alone cannot establish correct points. | The lineup panel shall show the selected team’s starters, each player’s fantasy points and game status, and the team total using the league’s Yahoo scoring rules or, for a manual lineup, a documented default scoring table that specifies each counted statistic and its point coefficient; it shall label manual scoring “Default scoring,” mark each value older than stale_after “Stale,” and mark each unavailable value “Unavailable.” |

Metadata repair: Keep the existing Source, Verification and Allocation.

### AC-AFC-PANEL-03

Checklist: CHK-RE-02 UNOWNED_SUBJECT; CHK-RE-03 WRONG_FORM; CHK-RE-07 OPERATIONS_MIXED. Evidence: technical plan line 179.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-PANEL-03 | wording | “The customer shall show and hide” obligates the customer rather than the allocated TV component. | The TV app shall let the customer show and hide the lineup panel and select the followed team and league using only the remote’s D-pad, select and back keys, with a visible focus indicator on every focusable element. |

Metadata repair: Keep the existing Source, Verification and Allocation.

### AC-AFC-PANEL-04

Checklist: CHK-RE-24 CONTRADICTION; CHK-RE-48 NO_PASS_FAIL. Evidence: technical plan line 180.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-PANEL-04 | wording; measurability | “the panel shall show it within one panel_refresh” applies even when the panel is hidden, although LW-01 stops hidden-panel requests; “panel totals shall agree with the alerts” does not define agreement when alert types, quiet hours or frequency suppress events. | When a starter change or scoring correction reaches the backend, the backend shall include it in subsequent panel responses, and the visible panel shall request those responses every panel_refresh and apply each received response; after being hidden, the panel shall request updated state when shown, and any panel value and released alert referring to the same event shall use the same corrected source facts, irrespective of whether other events produced alerts. |

Metadata repair: Keep the existing Source, Verification and Allocation.

### AC-AFC-SPIKE-01

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 187.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SPIKE-01 | allocation | Allocation “M2; device-integration-spikes” names a lane, checkpoint or slice without the satisfying component.  | The SP-1 spike shall record the stick's model, Fire OS version and Android API level; if the API level is below min_sdk, the OS is Fire OS 5 or older, or the provider apps cannot run, then device work shall stop and the finding shall return to the owner without any purchase or platform switch. |

Metadata repair: Allocation → `M2; SP-1 device compatibility verdict (`docs/spikes/`), TV app build configuration`. Retain the statement and Verification.

### AC-AFC-SPIKE-02

Checklist: CHK-RE-20 WRONG_LEVEL; CHK-RE-24 CONTRADICTION. Evidence: technical plan line 188.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SPIKE-02 | allocation; wording | “each spike SP-1..SP-6” is allocated wholly to “M2,” which ends 2026-10-15, while SP-6 is explicitly at T_yahoo (2026-10-16) in DES-AFC-SPIKES; the Allocation names lanes only. | The program shall record a verdict file `docs/spikes/SP-<n>-<topic>.md` for each spike SP-1..SP-6, containing the route tried, exact steps, evidence paths, verdict and limits, with SP-1..SP-5 complete by M2 exit and SP-6 recorded at T_yahoo. |

Metadata repair: Allocation → `M2 (SP-1..SP-5), M3 entry at T_yahoo (SP-6); spike verdict records, DeviceAuth/LineupConnector access check`. Keep Source and Verification. This corrects timing; it does not redefine T_yahoo.

### AC-AFC-SEC-01

Checklist: CHK-RE-20 WRONG_LEVEL; CHK-RE-39 INTERFACE_INCONSISTENT. Evidence: technical plan line 189.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SEC-01 | allocation | “keep OAuth tokens only in its DynamoDB table” conflicts with the placement receipt’s LineupConnector constraint “Tokens and client secret are server-side only, in SSM SecureString (TB2).” Neither storage choice is an owner decision. | The APK and every tracked file shall contain no Yahoo client secret, OAuth token, AWS credential or device token; the backend shall read the Yahoo client secret from SSM Parameter Store SecureString and shall keep Yahoo OAuth tokens exclusively in backend storage, without returning them to the TV app. |

Metadata repair: Keep Source, Verification and Allocation. Bind the storage mechanism in the author’s placement/design reconciliation; the requirement fixes the backend-only trust boundary without selecting between the two competing implementation choices. A device bearer token obtained at runtime is not an embedded APK credential.

### AC-AFC-D5-02

Checklist: CHK-RE-24 CONTRADICTION; CHK-RE-30 INCORRECT. Evidence: technical plan line 200.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-D5-02 | wording; traceability | “no GridMarket identifier (product name …)” also bans the provenance/copyright notice D5-01 and SD-022 require retaining. | The spec-authoring skill’s operational text, templates and tool invocation shall contain no GridMarket product name, document id or `--project backend` flag; GridMarket references shall occur only in retained license, attribution and provenance records, and the skill shall contain no absolute local path; building and linting its shipped template in a temporary directory outside any git repository shall exit 0. |

Metadata repair: Keep the existing Source, Verification and Allocation.

### AC-AFC-D5-05

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 203.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-D5-05 | allocation | Allocation “M1 (S06, S06L); M2 (S11)” names a lane, checkpoint or slice without the satisfying component.  | The program shall land the spec-authoring skill in Alphazedehq through its own pull request merged by rebase or merge commit, shall then link it into every harness skill directory that already links the shared skills, and shall have the D4 hook installer link it for the remaining harnesses of SD-021 or record each as a typed gap. |

Metadata repair: Allocation → `M1; D5 shared spec-authoring skill and shared-skill links; M2; shared harness hook installer and harness skill-directory configurations`. Retain the statement and Verification.

### AC-AFC-SPEC-01

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 209.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SPEC-01 | allocation | Allocation “M2; spec-and-docs (S19)” names a lane, checkpoint or slice without the satisfying component.  | When the D5 pull request (AC-AFC-D5-01..05) is merged, the D1 slice shall vendor `tools/spec/` with the D5 vendor step, with `VENDORED.md` naming the merged Alphazedehq commit and `THIRD_PARTY_NOTICES.md` carrying the GridMarket MIT notice, and no D1 authoring shall start before that merge. |

Metadata repair: Allocation → `M2; D1 specification sources, vendored spec tools and license/provenance records (S19)`. Retain the statement and Verification.

### AC-AFC-SPEC-02

Checklist: CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-30 INCORRECT. Evidence: technical plan line 210.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SPEC-02 | traceability; measurability; allocation | “every COE-ASA-001 floor subsection the template carries” would pass a template that omits part of the floor; COE-ASA-001 instead requires every element of the library’s floor. “spec-and-docs” is a lane, not the D1 component. | The specification under `spec/amazon-fantasy-companion/` shall contain every structural-floor element required by COE-ASA-001, bind every product AC-AFC row in at least one section, pass the spec lint and figure lint with zero findings, and produce a byte-identical built file on a second build from unchanged sources. |

Metadata repair: Allocation → `M2 (rev 0.1), M4 (rev 1.0); D1 specification sources and build (S19, S35)`. Add `COE-ASA-001` to Source; retain SD-012 and SD-022 and Verification=test. Clause identity checked in `Alphazedehq:docs/coe/architecture-specification-authoring/architecture-specification-authoring.sdoc:292`; this receipt claims no publication status for that library.

### AC-AFC-SPEC-03

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 211.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SPEC-03 | allocation | Allocation “M4; spec-and-docs (S35)” names a lane, checkpoint or slice without the satisfying component.  | The specification revision 1.0 shall record the SP-1..SP-6 verdicts, the panel mode, the SP-3 provider route and every recorded limitation. |

Metadata repair: Allocation → `M4; D1 specification revision 1.0 (S35)`. Retain the statement and Verification.

### AC-AFC-PLAN-01

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 217.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-PLAN-01 | allocation | Allocation “Planning (this package)” names a lane, checkpoint or slice without the satisfying component. Planning precedes the milestones, so M1 entry is the checkpoint, not a requirement to defer planning work until M1. | The program plan shall define milestones M1..M5, each with title, due date, entry criteria, exit criteria and slices; every slice shall belong to exactly one milestone and one wave, and no wave shall schedule more than impl_agent_cap concurrent implementation agents. |

Metadata repair: Allocation → `Planning, checked at M1 entry; D2 program plan and milestone/wave table`. Retain the statement and Verification.

### AC-AFC-PLAN-02

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 218.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-PLAN-02 | allocation | Allocation “M1; light work” names a lane, checkpoint or slice without the satisfying component.  | When the owner approves this package, the Orchestrator shall create milestones M1..M5 in `1wgrumph/amazon-fantasy-companion` with the planned titles, due dates and descriptions, and the `gh api` readback shall equal the milestone table. |

Metadata repair: Allocation → `M1; D3 GitHub milestone records`. Retain the statement and Verification.

### AC-AFC-CI-03

Checklist: CHK-RE-25 GLOSSARY_MISMATCH; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 226.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-CI-03 | undefined term; measurability | “a credential pattern” names neither credential classes nor an identifiable rule set; DES-AFC-GATE repeats the phrase without resolving it. | The `hygiene` area shall reject tracked files matching an absolute user-home path shape or the repository’s documented credential-detection rules for Yahoo client secrets, OAuth tokens, AWS credentials and device tokens, and shall identify each finding by file and rule identifier without printing the matched secret. |

Metadata repair: Retain Source, Verification and Allocation. Preserve the existing Linux, macOS and Windows home-shape examples using placeholder user segments, and document the scanner rule identities with the gate; this is scanner evidence, not proof that every possible secret string can be recognized.

### AC-AFC-VNV-01

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 227.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-VNV-01 | allocation | Allocation “M1; spec-and-docs” names a lane, checkpoint or slice without the satisfying component.  | The repository shall contain the Vnv guidance tree: `docs/vnv/AGENTS.md` and one `docs/vnv/<area>/AGENTS.md` per area (tv-app, backend, device-integration, ci-cd, spec, developer-feedback), each naming Scope, Tools, Review Focus and findings target. |

Metadata repair: Allocation → `M1; Vnv guidance tree (`docs/vnv/AGENTS.md` and area guidance files)`. Retain the statement and Verification.

### AC-AFC-DX-01

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 244.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-DX-01 | allocation | Allocation “All milestones” names a lane, checkpoint or slice without the satisfying component.  | The program shall give every dispatch packet and every return in this Lifecycle a `developer_feedback` section that lists observations with IDs and evidence, or states "no new observations" and names the tools exercised. |

Metadata repair: Allocation → `M1–M5; Lifecycle dispatch/return records and Scribe observation log`. Retain the statement and Verification.

### AC-AFC-DX-02

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 245.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-DX-02 | allocation | Allocation “M1 (log), M5 (summary, friction log)” names a lane, checkpoint or slice without the satisfying component.  | The repository shall contain the running observation log, a per-tool summary (purpose, onboarding, what worked, what needs work, willingness to reuse) and a sanitized friction log (task, reproduction steps, expected and actual behavior, severity, workaround, suggestion) that cover every tool, API, SDK and device used and carry DX-001..DX-007. |

Metadata repair: Allocation → `M1; developer-feedback observation log; M5; per-tool summary and friction log`. Retain the statement and Verification.

### AC-AFC-DX-03

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 246.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-DX-03 | allocation | Allocation “M5” names a lane, checkpoint or slice without the satisfying component.  | The per-tool summary and the friction log shall contain no credential, personal account detail or absolute local path, and shall be checked against the current official rules before submission. |

Metadata repair: Allocation → `M5; developer-feedback per-tool summary and friction log`. Retain the statement and Verification.

### AC-AFC-SUB-01

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 252.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SUB-01 | allocation | Allocation “M5; spec-and-docs” names a lane, checkpoint or slice without the satisfying component.  | The README shall give setup steps (build the APK, deploy the backend to the reader's own AWS Free-plan account, link Yahoo or enter a manual lineup, run replay), footage credits, the panel-mode and voice limitation statements, and the judge-access arrangement through T_judge_access. |

Metadata repair: Allocation → `M5; README and judge-access setup documentation`. Retain the statement and Verification.

### AC-AFC-SUB-02

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 253.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SUB-02 | allocation | Allocation “M5” names a lane, checkpoint or slice without the satisfying component.  | The submission checklist shall list every owner-only action (license choice, visibility flip, ESPN terms decision, video upload, reviewer access, Devpost submission, external feedback) with its due time before T_deadline, and agents shall perform none of them. |

Metadata repair: Allocation → `M5; submission checklist and owner-action records`. Retain the statement and Verification.

### AC-AFC-SUB-03

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 254.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SUB-03 | allocation | Allocation “M5” names a lane, checkpoint or slice without the satisfying component.  | The demo material shall consist of clips recorded from the device for the storyboard segments of #1, with every replay segment labeled as replay and every Mode A segment labeled as sample footage. |

Metadata repair: Allocation → `M5; device clips and storyboard/clip index`. Retain the statement and Verification.

### AC-AFC-SUB-04

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 255.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-SUB-04 | allocation | Allocation “M5” names a lane, checkpoint or slice without the satisfying component.  | The demo material and the submission text shall show voice or Alexa behavior only if it is implemented and verified on the device. |

Metadata repair: Allocation → `M5; device clips and submission text`. Retain the statement and Verification.

### AC-AFC-LAND-01

Checklist: CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE. Evidence: technical plan line 261.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-LAND-01 | allocation; traceability | Allocation “All milestones” names a lane, checkpoint or slice without the satisfying component. The cited “CLAUDE.md” does not exist in this checkout. | The program shall land each phase's lane branches on `main` through pull requests merged by rebase or merge commit after one Reviewer review, at most one repair round and a green gate entrypoint run, with no squash merge, force-push or commit on local `main`. |

Metadata repair: Allocation → `M1–M5; phase landing records, Reviewer/repair receipts and gate entrypoint evidence`. Source → Workspace cross-repo rules 4 and 9, Worktrees “Never squash-merge,” and this plan’s Program plan / Rollback or repair sections. Retain the statement and Verification.

### AC-AFC-REV-01

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 262.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-REV-01 | allocation | Allocation “All milestones” names a lane, checkpoint or slice without the satisfying component.  | The program shall put OCR in delegation mode (`ocr delegate preview`, `ocr delegate rule`) into every Reviewer packet together with either Reverify (claims about the built APK) or `Reverify: not applicable — <reason>`, and shall record an OCR or Reverify run that cannot complete as a typed gap with its exact error. |

Metadata repair: Allocation → `M1–M5; Reviewer dispatch packets, OCR/Reverify capability records and execution receipts`. Retain the statement and Verification.

### AC-AFC-VIS-01

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 263.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-VIS-01 | allocation | Allocation “M3, M4” names a lane, checkpoint or slice without the satisfying component.  | When a change alters rendered TV UI, the program shall review it on the stick with screenshots captured by `adb exec-out screencap -p` for each changed screen and state, kept with the review evidence and containing no customer data. |

Metadata repair: Allocation → `M3, M4; TV app visual-review screenshots and review records`. Retain the statement and Verification.

### AC-AFC-PATH-01

Checklist: CHK-RE-20 WRONG_LEVEL. Evidence: technical plan line 264.

| ID | class | defect | proposed statement |
|---|---|---|---|
| AC-AFC-PATH-01 | allocation | Allocation “All milestones” names a lane, checkpoint or slice without the satisfying component.  | The program shall commit no file in this Lifecycle that contains an absolute local home path; plan artifacts shall use repository-relative paths or `<PLANNING_WORKTREE>` / `$HOME` placeholders. |

Metadata repair: Allocation → `Planning and M1–M5; tracked artifacts and repo hygiene gate`. Retain the statement and Verification.

### RISK-AFC-01

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 270.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-01 | wording; traceability; measurability; allocation | “Stop device work and return to the owner” is an imperative response, not a bound obligation. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If the stick cannot be located, its API level is below min_sdk, its OS is Fire OS 5 or older, or the provider apps cannot run, then the program shall stop device work and record the condition for the owner without purchasing a device or switching platforms. |

Metadata repair: Source → `SD-001, SD-003, C1, AC-AFC-SPIKE-01`. Verification → `inspection`. Allocation → `M2; SP-1 device compatibility verdict and device-work entry control`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-02

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 271.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-02 | wording; traceability; measurability; allocation | “panel-only presentation remains; owner scope decision” must not silently waive ALERT-04. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If SP-2 cannot demonstrate a heads-up notification over provider playback, then the program shall record the exact device and route limitation, retain panel-only presentation, and record AC-AFC-ALERT-04 as unmet pending an owner scope decision. |

Metadata repair: Source → `#1 Development setup, AC-AFC-ALERT-04`. Verification → `inspection`. Allocation → `M2; SP-2 notification verdict and AlertNotifier; M3; integration acceptance record`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-03

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 272.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-03 | wording; traceability; measurability; allocation | “Ship the best verified outcome (details or app home)” would silently substitute a weaker result for WATCH-02; #1 explicitly says app launch alone does not satisfy specific-game acceptance. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If SP-3 finds no supported content-level link for a specific game, then the program shall record the verified details-page or app-home outcome and its limitation, prepare the missing-interface proposal for the owner, and retain AC-AFC-WATCH-02 as unmet until a specific-game route is demonstrated or the owner changes its acceptance condition. |

Metadata repair: Source → `#1 App launch and game/channel routing research, AC-AFC-WATCH-01, AC-AFC-WATCH-02`. Verification → `inspection`. Allocation → `M2; SP-3 provider-route verdict and ProviderResolver registry; M3; WatchLauncher integration acceptance record`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-04

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 273.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-04 | wording; traceability; measurability; allocation | “Mode A with labeled footage” does not name an obligated subject. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If SP-4 fails to verify Mode B within spike_panel_max, then the system shall use Mode A under AC-AFC-PANEL-05 and the submission materials shall state that the panel is beside the companion’s sample footage rather than provider playback. |

Metadata repair: Source → `SD-006, SD-006a, C5, AC-AFC-PANEL-05`. Verification → `inspection, demonstration`. Allocation → `M2; SP-4 verdict; M3; CompanionPlayer/LineupPanel; M5; submission materials`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-05

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 274.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-05 | wording; traceability; measurability; allocation | “Switch to labeled replay for the demo” has no binding subject or verification field. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If ESPN responses become unavailable or schema-invalid, then the backend shall apply the rejection and stale-data rules of AC-AFC-FEED-01 and AC-AFC-FEED-03 and use labeled replay for the affected demo segments; the submission checklist shall retain the ESPN-terms decision as an owner-only action. |

Metadata repair: Source → `SD-004, C2, C3, AC-AFC-FEED-01, AC-AFC-FEED-03, AC-AFC-SUB-02`. Verification → `test, inspection`. Allocation → `M3; FeedIngest/ReplaySource; M5; submission checklist and demo material`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-06

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 275.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-06 | wording; traceability; measurability; allocation | “Labeled manual lineup” is not a statement of duty. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If Yahoo access is not approved at T_yahoo, then the system shall provide manual lineup entry from ESPN rosters and label every display of that lineup “Manual lineup” under AC-AFC-PROF-04. |

Metadata repair: Source → `SD-007, C6, AC-AFC-PROF-04`. Verification → `test`. Allocation → `M3; LineupConnector (ManualSource), ProfileSettings and LineupPanel`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-07

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 276.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-07 | wording; traceability; measurability; allocation | “Activate the next approved fallback” needs the confirmed-limit condition and the frozen route/capability boundary. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If a selected route reaches a confirmed usage or rate limit, then the Orchestrator shall record the limit evidence and activate only the next approved fallback in the frozen profile with a class B receipt preserving the selected coverage-assist and Reverify settings, or queue the slice when no approved fallback remains; other invocation, configuration, authentication or runtime errors shall not trigger a route switch. |

Metadata repair: Source → `DEC-AFC-PROFILE-001, frozen profile fallback order, owner route-preservation instructions`. Verification → `inspection`. Allocation → `M1–M5; frozen lifecycle binding, dispatch packets and route-activation receipts`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-08

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 277.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-08 | wording; traceability; measurability; allocation | “Hosted runs stop” does not assign the required response. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If private-repository Actions usage exhausts gh_private_minutes, then the program shall stop hosted workflow runs and retain local gate evidence without enabling paid overage unless the owner authorizes it. |

Metadata repair: Source → `SD-017, C11, AC-AFC-CI-02`. Verification → `inspection`. Allocation → `M1–M5; GitHub Actions workflow/budget control and repo gate evidence`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-09

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 278.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-09 | wording; traceability; measurability; allocation | “Stop the scheduler” does not bind the response to the budget condition or identify verification/allocation. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If the AWS Free-plan limits or credits are exhausted or a deployment would introduce a resource outside AC-AFC-SEC-03, then the program shall stop the affected scheduled work or reject that deployment before a change, and shall make no paid-plan change without the owner’s decision. |

Metadata repair: Source → `SD-005, C4, AC-AFC-SEC-03`. Verification → `test, inspection`. Allocation → `M2–M5; backend infrastructure deployment guard and EventBridge scheduler control`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-10

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 279.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-10 | wording; traceability; measurability; allocation | “Manual mapping override …; correction alert” leaves behavior before a verified identity match implicit. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If the Matcher cannot establish a Yahoo-to-ESPN player identity, then the system shall label that player “Unmatched” and withhold player-attributed points and alerts until a verified mapping is available; when a mapping correction changes an already released player attribution, it shall apply the correction to the affected alert and panel state. |

Metadata repair: Source → `#1 item 3 and Right-side fantasy lineup panel; DES-AFC-LINEUP; AC-AFC-ALERT-03`. Verification → `test`. Allocation → `M3; Matcher identity map and LineupPanel; M4; AlertPolicy/PanelService corrections`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-11

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 280.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-11 | wording; traceability; measurability; allocation | “reaches the public repository” followed by “Remove before merge” describes a response that is already too late for the stated condition. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | When a secret, personal account detail or absolute local path is detected in material intended for the public repository, the program shall block its merge or publication until sanitized; if exposure has already occurred, it shall record the affected artifact without reproducing the sensitive value and notify the owner for credential rotation or other protected remediation. |

Metadata repair: Source → `Cross-repo rules 2 and 12, SD-010, C7, AC-AFC-SEC-01, AC-AFC-CI-03, AC-AFC-PATH-01`. Verification → `test, inspection`. Allocation → `M1–M5; repo hygiene gate, publication checklist and incident record`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-12

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 281.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-12 | wording; traceability; measurability; allocation | “Record the gap; git hooks still run” is not a bound capability-gap disposition. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If Muse or AGY exposes no supported pre-tool hook, then the D4 installer shall record that harness as a typed gap with exact capability evidence and retain local git hooks invoking the shared gate, without treating those hooks as proof of the missing harness integration. |

Metadata repair: Source → `SD-021, C13, AC-AFC-D4-04`. Verification → `inspection, demonstration`. Allocation → `M2; shared harness hook installer, harness configurations and local git hooks`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-13

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 282.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-13 | wording; traceability; measurability; allocation | “Fail closed on BLOCK or INDETERMINATE” lacks a bound subject and verification/allocation fields. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | The program shall obtain a scan-software-supply-chain receipt before first use of each external software acquisition, refuse use on BLOCK or INDETERMINATE, and verify the pinned distribution checksum for the Gradle wrapper before executing the downloaded distribution. |

Metadata repair: Source → `Cross-repo rule 10; RISK-AFC-13 Control`. Verification → `inspection`. Allocation → `M1–M5; software acquisition receipts and TV app build configuration`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-15

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 283.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-15 | wording; traceability; measurability; allocation | “Narrow the descriptions …; never merge two skills” is not a binding control and cites an unapproved reciprocal edit as though it were settled. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If matching and non-matching request checks expose a trigger collision between the D5 skill and `use-requirements-system`, then the program shall record the failing requests and repair the D5 trigger boundary under AC-AFC-D5-03; any reciprocal edit to `use-requirements-system` shall follow the OD-AFC-07 disposition recorded at integrated review. |

Metadata repair: Source → `SD-022, C10, AC-AFC-D5-03, OD-AFC-07 (pending, not confirmed)`. Verification → `inspection`. Allocation → `M1; D5 skill description and trigger-check receipts; shared Requirements System skill description only if OD-AFC-07 authorizes its edit`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-16

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 284.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-16 | wording; traceability; measurability; allocation | “M2 exit records the slip” cannot establish M2 exit while the required D1 rev 0.1 is absent. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If D5 lands later than planned, then the program shall reschedule D1 after that merge, record the schedule impact, and leave the D1 revision 0.1 M2 exit criterion unmet until delivered, without reverting to the superseded project-local GridMarket kit. |

Metadata repair: Source → `SD-022 superseding SD-013, AC-AFC-SPEC-01, M2 exit criterion`. Verification → `inspection`. Allocation → `M1; D5 landing receipt; M2; D1 specification and milestone exit record`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

### RISK-AFC-14

Checklist: CHK-RE-01 AMBIGUOUS_MODALITY; CHK-RE-17 INCOMPLETE; CHK-RE-20 WRONG_LEVEL; CHK-RE-28 UNTRACEABLE; CHK-RE-47 UNVERIFIABLE. Evidence: technical plan line 285.

| ID | class | defect | proposed statement |
|---|---|---|---|
| RISK-AFC-14 | wording; traceability; measurability; allocation | “Fall back to labeled replay for any segment that misses its window” must not silently count replay as the separately required simultaneous-live-games evidence. The actual row schema is Risk / Control / Response, with no Source, Verification or Allocation cells. | If a planned live-game capture or demonstration window is missed, then the program shall use labeled replay for affected demo segments and record any unmet live-integration obligation separately, without presenting replay as the M3 simultaneous-live-games demonstration. |

Metadata repair: Source → `C2, #1 Judging alignment and Development setup, M3 exit criterion`. Verification → `inspection`. Allocation → `M2; FeedIngest fixture capture; M3; live integration record; M5; demo clips`. Preserve the original risk description as rationale; promote the proposed control to the Statement field.

## PASS rows

Every row below was checked for binding subject/EARS form, necessity, defined terms and quantities, internal consistency, source, observable verification and allocation. Notes identify its observable or source disposition; PASS is requirement quality only.

| UID | Result | Note |
|---|---|---|

| AC-AFC-PROF-01 | PASS | Plan line 130: Device-link display/bind flow, device_code_ttl and backend-only Yahoo token boundary are observable; M3 components match placement. |

| AC-AFC-PROF-02 | PASS | Plan line 131: League/team selection and starter/bench/unknown classification use current-week selected positions; observable backend/TV outputs. |

| AC-AFC-PROF-03 | PASS | Plan line 132: Package detection, Unknown subscription default and customer overrides have distinct observable states; no entitlement inference. |

| AC-AFC-PROF-04 | PASS | Plan line 133: T_yahoo condition and Manual lineup label are exact; source and M3 ManualSource/ProfileSettings allocation agree. |

| AC-AFC-MON-01 | PASS | Plan line 139: Followed-player/game/viewing-period conditions bound eligible fetches; feed_poll_interval is defined; backend request record is observable. |

| AC-AFC-MON-02 | PASS | Plan line 140: Per-game maximum fetch count over feed_poll_interval is independent of follower count and observable. |

| AC-AFC-MON-03 | PASS | Plan line 141: Opt-in, unsupported detection message and profile-derived labeling are explicit; SP-2 includes current-playback context. |

| AC-AFC-MON-04 | PASS | Plan line 142: No alert requests outside enabled viewing periods is observable at AlertService; schedule definition is in Glossary. |

| AC-AFC-FEED-03 | PASS | Plan line 145: feed_fail_limit, stale state and exact replay label are defined; failure and replay are separately observable conditions. |

| AC-AFC-ALERT-01 | PASS | Plan line 151: Event relevance and truthful red-zone wording are observable; red_zone_entry/close_game meanings resolve through GameEvent and DES-AFC-FEED. |

| AC-AFC-ALERT-02 | PASS | Plan line 152: Duplicate, spoiler-delay, quiet-hour and per-game gap rules are observable in release records; zero alert_min_gap means no minimum spacing. |

| AC-AFC-ALERT-03 | PASS | Plan line 153: A correction references a released alert and changes its panel state; “release” remains subject to ALERT-02 policy, not an unconditional immediate bypass. |

| AC-AFC-WATCH-01 | PASS | Plan line 161: Launch-target alternatives and unknown-access labeling are explicit; ProviderResolver matches placement. |

| AC-AFC-WATCH-02 | PASS | Plan line 162: Confirmation and allow-listed intent are observable; GAME_OPENED requires one actual specific-game demonstration. RISK-03 is repaired, not this accepted need. |

| AC-AFC-WATCH-03 | PASS | Plan line 163: Absent package/failed intent requires an outcome plus reason and forbids success; test can observe both. |

| AC-AFC-CTRL-01 | PASS | Plan line 169: All listed remote controls and next-decision effect are observable; M4 requires the complete set, with M3 core elaborated by the plan. |

| AC-AFC-CTRL-02 | PASS | Plan line 170: Restart and reboot persistence has a directly comparable before/after settings state. |

| AC-AFC-CTRL-03 | PASS | Plan line 171: Conditional visibility requires implemented and device-verified voice; C8 is preserved. |

| AC-AFC-PANEL-02 | PASS | Plan line 178: Remote device demonstration/inspection can establish simultaneous panel/video, aspect ratio and no crop/overlap; no benchmark required. |

| AC-AFC-PANEL-05 | PASS | Plan line 181: Bounded Mode B/Mode A verdict, exact footage label, license and README credit are observable; planned fallback matches C5. |

| AC-AFC-SEC-02 | PASS | Plan line 190: Named public bootstrap routes are exceptions; protected-route missing/invalid token response and absence of mutation are observable. This is not an authorization-design certification. |

| AC-AFC-SEC-03 | PASS | Plan line 191: Named resource families and refusal before deploy mutation give an observable allow-list check; Free-plan cost is separately controlled by RISK-09. |

| AC-AFC-SEC-04 | PASS | Plan line 192: Requested Yahoo read scope is inspectable; LineupConnector allocation and read-only source agree. |

| AC-AFC-LW-01 | PASS | Plan line 193: Thread placement, changed-row rendering and hidden-panel polling cessation are inspectable; publication excludes physical-device performance figures. |

| AC-AFC-D5-01 | PASS | Plan line 199: Shared skill contents, size bounds, script invocation, environment independence and MIT notice are observable deliverable properties. |

| AC-AFC-D5-03 | PASS | Plan line 201: Matching/non-matching requests and the non-trigger/checklist-reference text are observable; lint line 37 is inapplicable library-neutrality advice. |

| AC-AFC-D5-04 | PASS | Plan line 202: Vendor destination, provenance and refusal to overwrite modified files are explicit and observable. |

| AC-AFC-CI-01 | PASS | Plan line 224: One entrypoint and same area selection across callers, with nonzero failing areas, can be demonstrated by the named test method. |

| AC-AFC-CI-02 | PASS | Plan line 225: Workflow fields, check names, pins, permissions, fork isolation and runner selection are observable; lint line 46 does not override SD-017/021. |

| AC-AFC-D4-01 | PASS | Plan line 233: Gate contract/template/installer, common Actions entrypoint, absence of TODO and skill size are observable; lint line 49 does not override SD-017/021. |

| AC-AFC-D4-02 | PASS | Plan line 234: Guide/checker and size are observable; its budget rule concerns workflow configuration and C11 response, not a claim that a static checker measures account consumption. |

| AC-AFC-D4-03 | PASS | Plan line 235: Presence/absence of either Vnv root gives run/REFUSED_NO_VNV; GATES rows are lookup data, not repository exclusions (DES-AFC-D4). |

| AC-AFC-D4-04 | PASS | Plan line 236: C13 ordering, actual hook capability, exact typed-gap evidence and Muse skill exposure are observable; absent capability is never passing evidence. |

| AC-AFC-D4-05 | PASS | Plan line 237: PR merge form and matching/non-matching skill exercise receipts are inspectable; D4/M1 allocation is a defined component group. |

| AC-AFC-D4-06 | PASS | Plan line 238: No repository/owner/pilot/exclusion may scope D4 capability; text inspection distinguishes lookup data from scope restrictions. |


## Owner questions

None needed to repair these rows. Existing OD-AFC decisions remain for the integrated review; this gate neither answers nor reopens them. In particular SD-022 supersedes SD-013, while future SP-2/SP-3 failures cannot be accepted as equivalent product outcomes without their specified owner disposition. The expected Mode A and manual-lineup fallbacks are already decided.

## Decision coverage

uncovered: none at the topic/disposition level across the register, plan, design guidance and explicit exclusions. The register has the row-quality gaps above; this is not a claim that every source item already has a passing acceptance row.

Source inventory reconciled: issue #1’s profile/lineup, enabled monitoring, personalized alerts/corrections, provider handoff, customer controls, simultaneous right-side panel/video, device/data spikes, developer feedback, lightweight design and no-benchmark boundary, storyboard, submission/judge access and owner publication; SD-001..SD-021, SD-006a, SD-022 and C1..C14; D1..D5; shared Vnv/CI/harness scope. Earlier platform candidates, hardware comparison tiers and vendor claims remain research/guidance, not mandated support or certified feasibility. Messaging, device purchases, other tracks and unverified voice remain excluded/conditional as decided. Optional AI commentary and D4/D5 shape questions retain their existing integrated-review dispositions.

## Method and evidence limits

Applied the installed `requirements-engineer` 1.1.6 role and `references/gate-report.md`, plus `requirements-engineering` authoring, NASA-adapted checklist (CHK-RE-01..50), quality-gate and interface-completeness references. S8 receipts were read from `Alphazedehq:skills/engineering-methods/references/standards-receipts.md`: SRC-EMV-NASA-SEH (2016 Rev2, informative/full-text receipt), SRC-EMV-COE (tailored; recorded historical digest mismatch retained), SRC-EMV-29148 (2018 edition 2, metadata-only; no clause claims). COE-ASA-001 identity and duty were checked in the native local SDoc at line 292. No external vendor capability, current event rule, financial quota or standard publication status was newly certified.

The user’s five-column Lifecycle-local register and gate scope govern: rationale/assumptions resolve through cited decisions and surrounding plan text; prospective case IDs and V&V implementation belong to the later Test Engineer, so absence of authored SEIT is not a blanket failure here. Check types used here are inspection and analysis; listed product verification methods were assessed for their ability to yield evidence, not executed. Interface names and existing contract consistency were inspected; no new interface profile, design, model, slice or V&V case was authored and no compatibility/runtime verdict is claimed.

Checklist applicability: CHK-RE-12’s separate-register-layer condition is N/A because the owner explicitly designates these Markdown rows as the register. CHK-RE-06/07/21/22/23 do not forbid process duties in the explicit Lifecycle/D4/D5/spike deliverables or owner-selected platforms. CHK-RE-10/31 do not require resolving owner-confirmed future spikes or OD-AFC-05 before this pre-approval gate: their closure points remain visible. Hardware performance quantities/claims (CHK-RE-34..36), runtime reliability/maintainability (CHK-RE-40/42), fault/continuity/flag concerns (CHK-RE-43/44/46/50) and interface concerns (CHK-RE-37..39) are N/A on purely document/record/process rows unless that row explicitly imposes the corresponding obligation; applicable product/data/failure rows were checked. No numeric platform feasibility or binary behavior is claimed. Reverify: not applicable — requirement text only. OCR: not applicable — this is a requirements gate, not a code review.

### Mechanical finding dispositions

| Evidence | Finding | Disposition |
|---|---|---|
| `specialists/ac-mechanical-lint-r0.txt:37` | AC-AFC-D5-03, `agnostic term: requirements system` | Not a failing row. It names the actual non-trigger and handoff boundary required to keep D5 distinct from Requirements System work (SD-022/C10). |
| `specialists/ac-mechanical-lint-r0.txt:46` | AC-AFC-CI-02, `agnostic term: github` | Not a failing row. SD-017 explicitly selects GitHub-hosted runners; SD-021 selects Actions workflow authoring. |
| `specialists/ac-mechanical-lint-r0.txt:49` | AC-AFC-D4-01, `agnostic term: github` | Not a failing row. SD-021 requires the same gate for local hooks and Actions. Repo-agnostic is not platform-agnostic. |
| `specialists/ac-mechanical-lint-r0.txt:66` and adapter regex | `rows=65 flagged=3`; regex matches `AC-AFC-` only | Coverage limit, not risk-row evidence. The 16 risk rows were checked separately below and manually against their cited controls. |

The Planning node’s platform-neutrality position is accepted for these three occurrences. `lint-sdoc.py` describes AGNOSTIC_TERM as a COE library-authoring rule and explicitly skips it under its project-specification profile. The adapter’s three flags are preserved, not erased or called a clean mechanical run.

### Supplemental risk mechanical inventory (read-only stdout)

Each numbered line below reports absence of a binding `shall` across that original row and its missing register fields. The judgment table above adds the exact defective phrase, control meaning and repair; these lines are not a claim that risk descriptions alone ought to be EARS requirements.

```text

01 RISK-AFC-01 plan:L270 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

02 RISK-AFC-02 plan:L271 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

03 RISK-AFC-03 plan:L272 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

04 RISK-AFC-04 plan:L273 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

05 RISK-AFC-05 plan:L274 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

06 RISK-AFC-06 plan:L275 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

07 RISK-AFC-07 plan:L276 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

08 RISK-AFC-08 plan:L277 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

09 RISK-AFC-09 plan:L278 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

10 RISK-AFC-10 plan:L279 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

11 RISK-AFC-11 plan:L280 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

12 RISK-AFC-12 plan:L281 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

13 RISK-AFC-13 plan:L282 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

14 RISK-AFC-15 plan:L283 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

15 RISK-AFC-16 plan:L284 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

16 RISK-AFC-14 plan:L285 no_binding_shall=True fields=Risk,Control,Response missing=Verification,Allocation

```

For every RISK mechanical finding, cite the line carrying that ID in this block (01–16 in plan order). Their Source field is also absent; Control contains partial trace links, retained and completed in the proposed metadata.

### Quantities and terms

All nine Scope Definition quantity rows match the plan verbatim. The ten additional design-quantity names are defined in the plan’s Glossary and remain proposals for OD-AFC-05. The read-only quantity-reference scan found one quantity-like token outside those tables, `red_zone_entry`; it is an event enum, defined through GameEvent/CONTRACT-AFC-EVENT and DES-AFC-FEED, not an undefined quantity. The judgment failures for default scoring and excitement-level mapping above concern absent semantic definitions, not absent quantity-name declarations. The alert_poll_wait finding concerns misuse of an existing definition, not an undefined name.

All 65 AC Verification cells use supported methods. The actual Risk table has no Verification cells. Components named as D4/D5 or repo gate are accepted as defined component groups with placements; bare lane names, slice IDs and milestone-only cells receive explicit component repairs. Process/document allocations use existing plan/design artifacts rather than inventing runtime components. The token-store placement mismatch is explicitly returned to the author without choosing architecture.

## Commands run

All commands except the final receipt write were read-only; no credentials or external APIs were accessed. Paths below use portable placeholders. No `codex exec`, commits, pushes, branch operations or GitHub mutations ran.

- `pwd`; `git status --short`; `git branch --show-current`; `git rev-parse HEAD`.
- `cat`, `sed -n`, `nl -ba`, and `rg -n` on the named role/method skills and references, workspace rules, technical plan, scope decision batch, issue-body snapshot, systems-modeler receipt, design, lint adapter/output, local lint rule constants and COE-ASA SDoc. `rg --files` located rule files and the canonical S8 receipt after the linked path was absent. One discovery command returned exit 2 because the optional `.bran` path did not exist; the method-reference read returned exit 1 for the missing linked S8 path. Both causes were identified and ordinary discovery/canonical-target reads supplied the needed evidence.
- `PYTHONDONTWRITEBYTECODE=1 python3 PLAN/specialists/ac_mechanical_lint.py "$HOME/alphazede/Alphazedehq/tools/coe/lint-sdoc.py" PLAN/amazon-fantasy-companion-technical-plan.md` → identical 65-row/3-flag output. Bytecode writes disabled so imports did not modify Alphazedehq.
- Read-only `python3 -B` inline inspections: JSON decision extraction, technical-plan SHA-256, 81-row identity inventory, 9/9 verbatim Scope quantity comparison, ancestor-rule existence, allocation inventory, supplemental risk schema/modal inventory and quantity-reference comparison.
- `python3 -B` receipt rendering → only `PLAN/specialists/requirements-engineer-receipt.md`; candidate hash asserted before writing. Exact replacement statements for metadata-only findings are copied from the hashed input.
- Read-only `python3 -B` final self-check → complete/disjoint row dispositions, exact row counts and candidate hash, required return fields, no absolute home paths and empty tracked diff. A proposed RISK-AFC-13 sentence initially began with “Before”; the receipt-only proposal was corrected to the supported “The … shall” EARS form and rechecked. This did not edit or re-gate the technical-plan candidate.

## developer_feedback

- **RE-OBS-001 — tooling coverage limit.** `specialists/ac_mechanical_lint.py` claims AC/RISK checks in its docstring but its matching regex accepts only AC IDs; supplied output line 66 reports 65, versus 81 register/risk rows inventoried. All 16 omitted rows are now visibly assessed in this receipt. This is an observation about the adapter’s coverage, not a defect report or a full SDoc-linter result.
- **RE-OBS-002 — known configuration friction, corroborates SM2-OBS-002.** The method’s sibling S8 reference was absent under the linked skill catalog; the read failed with “No such file or directory.” The canonical `Alphazedehq:skills/engineering-methods/references/standards-receipts.md` existed and was read. No capability gap remains and no issue was filed.
- **RE-OBS-003 — applicability of the extra create-lean-skill instruction.** `create-lean-skill` and the installed `skill-creator` peer were read. The existing Requirements Engineer skill already owns this exact gate; the creator peer explicitly preserves request scope, and create-lean-skill forbids duplicate owners. Applicability result: **NO_CHANGE**. Matching request checked by inspection: “Gate these Lifecycle-local requirement rows” → existing Requirements Engineer. Non-matching request checked by inspection: “Publish an SDoc revision” → excluded/Requirements System handoff. These are routing inspections, not a generated-skill execution test. No skill-authoring target or write authority exists in this packet; no skill, initializer output, metadata or duplicate helper was created, and no creator-script validation is claimed.
- **BRAN status:** unavailable — no native `.bran/policy.yaml` in this checkout or its parents; ordinary repository discovery was used. No BRAN coverage is claimed.
- **Tools exercised:** shell filesystem reads, `git` read-only identity/status, `rg`, `cat`, `sed`, `nl`, Python stdlib (`pathlib`, `json`, `hashlib`, `re`, `importlib`), existing Markdown lint adapter and imported SDoc rule constants. No product runtime, browser, device, hosted service, OCR or Reverify execution.

Skipped: implementation, V&V execution, plan edits, skill creation and publication, as outside this gate. Remaining risk: the candidate is not requirement-quality PASS until its author applies and verifies the listed repairs; physical-device and provider feasibility remain scheduled work, not proven behavior.
