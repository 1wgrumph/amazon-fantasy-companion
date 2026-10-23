# Devpost paste package — AFC

Prepared by Codex on 2026-10-21 against `bbeb6ad`. **PREPARED_WITH_GAPS**;
not a submission or an eligibility determination. William performs OA-7.
Use the timed procedure and gap register in [email-review.md](email-review.md).

**Form visibility:** the public [My projects page](https://devpost.com/submit-to/30992-build-ship-shape-amazon-developer-hackathon/manage/submissions)
shows a registration/sign-in boundary, not the entry editor. Actual field order,
labels, limits, required image sizes, dropdown values and conditional questions
are **UNKNOWN_FORM_FIELDS**. The sequence below follows the owner's requested
field sequence; it is not represented as an observed Devpost form. William must
compare it with the signed-in form before submitting. Copy field bodies, not
preparation notes or HTML evidence comments. Bracketed placeholders must be
resolved, never pasted as final answers.

Public [overview](https://amazonappdev2026.devpost.com/),
[rules](https://amazonappdev2026.devpost.com/rules),
[resources](https://amazonappdev2026.devpost.com/resources) and
[FAQ](https://amazonappdev2026.devpost.com/details/faqs) were read on 2026-10-21.
Public requirements are mapped below; account-only requirements remain a gap.

## 1. Project title

Amazon Fantasy Companion

<!-- Evidence: README.md (project name). Independent entrant project; naming is not Amazon authorship. -->

## 2. Tagline

Your fantasy starters, NFL moment alerts, and a full-screen lineup panel on Fire TV.

<!-- Evidence: README.md; tv-app/app/src/main/java/com/afc/companion/alerts/; tv-app/app/src/main/java/com/afc/companion/panel/. Draft tagline, not a measured benefit claim. -->

## 3. Project story

### Inspiration

Fantasy sports spread your attention across games. You can be watching one game while a player on your fantasy team scores somewhere else. We wanted to keep that connection on the TV, where we were already watching, instead of making another screen part of every play.

AZ Fantasy is a Fire TV companion built around that idea. A small corner card keeps your fantasy team in view over the broadcast. Alerts bring your players' scoring moments to you, including moments from a different sport. The game stays on screen while you check your team.

### What it does

While you watch any live game, AZ Fantasy shows your fantasy team in a corner card. It supports NFL and NBA, so the sport on the television does not have to match the sport that produces an alert. A basketball player scoring can matter to your fantasy team even while you are watching football.

The remote handles the main controls. Double-tap the menu button, ≡, to switch teams. Hold it to open a menu with Expand, League and Hide. Choose Expand for a larger view of your lineup. These interactions keep you with the game.

Lineups are entered manually today. Yahoo Fantasy API access has been approved, but connection setup is still pending. The live demonstration uses manual lineups.

### How we built it

The TV app uses Kotlin and Jetpack Compose on Fire OS. Its corner card, alert cards and expanded panel put fantasy information over the viewing experience, with the remote as the main input.

The backend is defined with AWS SAM. AWS Lambda runs the application logic, Amazon API Gateway HTTP API connects the TV to the backend, and Amazon DynamoDB stores the application data. Amazon EventBridge Scheduler triggers feed polling. AWS Systems Manager Parameter Store is part of the backend configuration.

We use ESPN public feeds for live NFL and NBA statistics. The backend connects those updates to the players in a manual fantasy lineup and sends the relevant information to the TV. ESPN's live play feed omits player identifiers, so matching scoring plays requires parsing the play text.

### Challenges we ran into

The live run exposed a timing problem: alerts reached the TV about 70–90 seconds after the play. That is the observed delay, and reducing it is planned work. Parsing player names from play text is another limitation; the feed does not give us player identifiers on those plays.

Fire OS does not list our accessibility switch, which makes setup harder. Prime Video also blocks screenshots on some frames, so a screen capture does not always show the whole viewing experience. We had to distinguish a capture limitation from what was visible on the television.

We rebuilt the UI during the live game in response to feedback from the person using it. The Watch flow was not tested live, and we do not claim that it opened a live game.

### Accomplishments we're proud of

On October 22, 2026, the Fire TV stick's own screen recording captured the companion working during live Thursday Night Football on Prime Video. A “D. Maye · SCORE” alert appeared. Later, “C. Holmgren · SCORE” arrived from Denver at Oklahoma City while the NFL game was still on screen. An “A. Gordon · SCORE” alert appeared too.

That cross-sport moment is the clearest demonstration of the idea: the viewer stayed with football while the companion followed basketball. The same night's corner card showed NE at CHI, the fourth-quarter clock, a fantasy total and D. Maye's points. The expanded panel also showed an NBA lineup for CLE at PHI.

### What we learned

A live game answers questions that a static layout cannot. The card has to be readable without taking over the picture, and the remote controls have to be simple enough to use while following play. Rebuilding the UI during the game made those choices concrete.

We also learned to separate useful live behavior from finished behavior. Seeing the right player's alert arrive proved the connection from a scoring event to the TV. The 70–90 second delay showed why that connection still needs work. Capturing an alert and testing the Watch flow are separate checks; one does not prove the other.

### What's next

First, reduce the observed alert delay and check the result during another live game. Improve play-text matching, make the accessibility setup clearer, and test the Watch flow live. We also need another live pass through the rebuilt UI and a capture approach that accounts for Prime Video's blocked frames.

Then finish the pending Yahoo connection setup so we can move beyond manual lineups. The next version should make the experience easier to set up and faster to follow while preserving the simple corner card and remote controls.

## 4. Built-with tags

Fire TV, Fire OS, Kotlin, Jetpack Compose, Python, AWS SAM, AWS Lambda, Amazon API Gateway HTTP API, Amazon DynamoDB, Amazon EventBridge Scheduler, AWS Systems Manager Parameter Store, ESPN public feeds

## 5. Links and media

| Field | Paste value / owner action |
|---|---|
| GitHub repository | https://github.com/1wgrumph/amazon-fantasy-companion |
| Setup / testing instructions, if separate | https://github.com/1wgrumph/amazon-fantasy-companion#judge-access |
| Demo video | **[OWNER: public YouTube or Vimeo URL after upload and processing]** |
| Live website, if requested | No public demo endpoint. Use the repository setup and demo video; do not paste the development API endpoint or credentials. |
| Thumbnail / image gallery, if required | **UNKNOWN_FORM_FIELDS**. William selects an existing clean AFC-only image or a plain text title card; no Amazon/AWS logos or provider screens. Required size and count are unknown. |
| Devpost project URL | **[OWNER: record the URL after creating the entry]** |

<!-- Evidence: README.md (Judge access); LICENSE; docs/submission/demo-plan.md; tools/demo/README.md. No hosted demo URL or public video receipt exists in this baseline. -->

Video: publicly visible YouTube/Vimeo, under three minutes, showing the app
functioning on Fire TV hardware or a permitted simulator. English captions;
clear manual/replay labels. These follow the [rules](https://amazonappdev2026.devpost.com/rules)
and [FAQ](https://amazonappdev2026.devpost.com/details/faqs).
The planned main cut is 156 seconds; the optional NBA segment can bring it to
170 seconds. Exclude provider frames, music without permission, Yahoo data,
link codes, personal information and device addresses. Synthetic color plates
are pipeline tests, not acceptable app-demonstration footage.

<!-- Evidence: docs/submission/demo-plan.md (Duration; Rules for every shot); tools/demo/cuts.json; tools/demo/README.md. Content exclusions also reflect the current owner instruction. -->

## 6. Track, category and mini-challenge

Recommended selections, for William to confirm:

- Primary track: **Fire TV**.
- Priority category: **sports**, if the form offers a category selector.
- Mini-challenge: **AWS Builder**.
- Open Source mini-challenge: **OWNER_DECISION_REQUIRED**. Public source alone
  does not establish the required additional contribution. If entering, William
  must supply its contribution URL, repository URL, GitHub username and explanation.
- No Alexa+, Bee or Ring entry is supported by this package.

These names and the additional-contribution condition come from the
[event overview](https://amazonappdev2026.devpost.com/).

<!-- Evidence: docs/submission/writeup.md (Fire TV; AWS Builder); backend/template.yaml; spikes/sp8-alexa/VERDICT.md. Category selector existence is unverified. -->

## 7. AWS Builder answer

Our backend is defined in AWS SAM and deployed through CloudFormation. The
template has four Python 3.12 Lambda functions: API routing, NFL ESPN ingest,
independent NBA statistics ingest, and the DynamoDB Streams policy pipeline.
API Gateway exposes the HTTP API. Seven on-demand DynamoDB tables store
profiles, link state, events, alerts, lineups, panels and player statistics.
Two EventBridge Scheduler resources target NFL and NBA ingest separately;
both default to disabled. Four CloudWatch log groups retain function logs.
IAM grants scope access by function and restrict scheduler invocation. SSM
Parameter Store holds the pending Yahoo integration's credentials outside source.
The API function does not receive Yahoo SSM read permission.

Recorded deployments and smoke tests prove the earlier deployed backend paths;
the current template is not evidence of fresh live NBA polling. NBA's feature
flag defaults on, independently of the disabled schedule defaults. No Bedrock,
AgentCore, Strands, Kiro Crew or SageMaker integration is claimed. Authentication
and credential-tool compatibility caused setup friction; the serverless design
fits the event-driven backend. We would use these services again.

<!-- Evidence: backend/template.yaml; docs/submission/writeup.md (AWS Builder); docs/developer-feedback/product-feedback.md (AWS section, OBS-060..067); CHANGELOG.md PRs #68/#96/#104/#107/#138. Older feedback's three-function/one-schedule inventory is superseded by the template. -->

The public requirement is service names and use in Product Feedback. Include
the answer above with the AWS rows below. Any account ID, Builder profile URL,
credit-use question or separate AWS field is **UNKNOWN_FORM_FIELDS**, not a
known requirement. William supplies a personal answer only if the signed-in
form actually requests it; no credential belongs in the entry.

## 8. Product Feedback — paste body

Feedback describes our recorded project experience as of October 21, 2026.
**Not observed** means the evidence does not contain that observation; it does
not mean the tool failed. **Pending owner opinion** requires a Yes/No and reason
from William before submission if the form requires that choice. Shared rows
name related tools explicitly; split the same text if the form uses one card
per tool. Onboarding durations are not measured unless stated. Earlier Scribe
summaries are secondary evidence: their `source_not_durable` receipts have not
been independently rechecked. In particular, the Muse completion observation
below is a reported result with an unavailable primary receipt.

### Device, application and data tools

<!-- Evidence for the following rows: docs/developer-feedback/product-feedback.md; docs/developer-feedback/observations.md OBS-001..031, OBS-070..082; spikes/sp1-device/VERDICT.md; spikes/sp2-notify/VERDICT.md; spikes/sp3-provider-links/VERDICT.md; spikes/sp4-panel-video/VERDICT.md; spikes/sp5-espn-feed/VERDICT.md; spikes/sp6-yahoo/VERDICT.md; backend/src/provider_resolver/registry.json; spikes/sp8-alexa/VERDICT.md. -->

| Tool/service | Use | Worked well | Needs work / limits | Onboarding | Build again and why |
|---|---|---|---|---|---|
| Fire TV / Fire OS | Primary TV target | App installed and rendered on the tested stick | No actionable heads-up alert or beside-video panel on this device | Starter built and installed; active time unmeasured | Yes; full-screen companion works |
| ADB / UI Automator | Install, inspect and drive TV UI | D-pad navigation made checks repeatable | Touch input is not a substitute for TV focus navigation | Device setup and owner pairing required; duration unmeasured | Yes; supports device evidence |
| Android SDK / Gradle / Android Gradle Plugin / JDK | Build, sign and test APKs | Offline starter build and strict dependency verification achieved | Dependency closure analysis and SDK environment setup took work; historical UTP issue was subsequently repaired | Pinned starter built; duration unmeasured | Yes; reproducible Android builds |
| Kotlin / Jetpack Compose / AndroidX / TV Material / coroutines | TV screens and asynchronous app work | Host-test seams supported launcher and alert logic | Focus behavior needed device checks; separate coroutine-specific feedback not observed | Not observed separately | Yes for the TV stack; evidence supports testable UI logic |
| Prime Video | Watch handoff target | Verified search route opened | Specific live-game route unproven; protected video not used in demo | Provider sign-in is an owner step | Yes for the verified search handoff; not a guaranteed game deep link |
| YouTube TV | Additional Watch target | Verified app-home route recorded October 21 | Home opening does not prove game access | Not measured | Pending owner opinion |
| ESPN public JSON | NFL feed; NBA statistics | Historical NFL payloads captured and replayed | Unofficial contract, payload variation, public-use terms unresolved; live timing pending | NFL capture spike window about eight minutes | Yes, subject to owner terms decision and validating ingest |
| Yahoo Fantasy API / OAuth | Attempted lineup import | OAuth succeeded | Fantasy API returned 403 for the unapproved app; no live Yahoo data obtained | About 1.5-hour spike window, including console diagnosis | No until approval; manual lineups are active |
| Alexa voice surfaces / Video Skills Kit documentation | Read-only feasibility investigation | Documented routes helped bound the investigation | No supported speak/tune route established for this app; no Alexa feature offered | No skill or runtime integration onboarded | No for this unproven route; reconsider only with a supported interface |

<!-- Current build sources: tv-app/app/build.gradle.kts; tv-app/gradle/libs.versions.toml; CHANGELOG.md PR #134 (UTP repair), PR #148 (YouTube TV). Prime Video and Alexa recommendations are draft conclusions from the named verdicts, for owner confirmation. -->

### Vega experiment and its toolchain

<!-- Evidence: vega-app/package.json; CHANGELOG.md PR #118; docs/developer-feedback/friction-log.md F-037..058; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/bug-token/summary.md; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/bug-panel/summary.md; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/review-repair/summary.md. -->

| Tool/service | Use | Worked well | Needs work / limits | Onboarding | Build again and why |
|---|---|---|---|---|---|
| Vega / Kepler SDK and CLI / Vega Virtual Device | Experimental port on SDK 0.24.12112 | Limited linking/settings, persistence and default-panel evidence after repairs | Host graphics/network setup was difficult; no physical Vega, populated lineup, provider playback or DRM proof | Multiple virtual-device setup attempts; no single measured duration | Pending owner opinion; Fire OS remains primary |
| React / React Native / Kepler runtime | Experimental TV UI | Repaired app flows ran on VVD; host regressions passed | Later wiring repairs were host-tested, not rerun on VVD | Not measured separately | Pending owner opinion |
| Amazon React Native AsyncStorage binding | Experimental session persistence | Replacement production binding survived relaunch in the recorded repair | Legacy binding did not retain session; native data-root log messages remain unexplained | Migration plus relaunch check | Pending owner opinion |
| TypeScript / Node.js / npm / Babel / Metro / React Native CLI | Vega build and type-check toolchain | Type-check passed in the recorded repair | No separate per-tool experience recorded | Not measured | Pending owner opinion |
| Jest / babel-jest / js-yaml | Vega tests and contract mirror | Recorded host regressions passed | Mock-based checks cannot establish native persistence or playback | Not measured | Pending owner opinion |

### AWS services and developer tools

<!-- Evidence: backend/template.yaml; docs/developer-feedback/product-feedback.md AWS section and OBS-060..067; backend/src/store/__init__.py; docs/submission/writeup.md AWS Builder. Per-service onboarding and latency were not measured. -->

| Tool/service | Use | Worked well | Needs work / limits | Onboarding | Build again and why |
|---|---|---|---|---|---|
| AWS CLI | Sign-in and deployment operations | Recorded stack updates completed | Browser sign-in and session expiry caused friction | Setup documented; elapsed time unmeasured | Yes; required operational tooling worked with documented setup |
| AWS SAM | Backend build and deployment definition | Validation/build supported hash pins | Global profile configuration and interactive prompts needed care | Setup documented; duration unmeasured | Yes; compact serverless packaging |
| AWS CloudFormation | Manage backend stack | Recorded UPDATE_COMPLETE deployments | No separate service defect observed | Via SAM; duration unmeasured | Yes; repeatable stack definition |
| AWS Lambda | API, NFL ingest, NBA ingest, stream pipeline | Earlier deployed smoke checks passed | Live end-to-end behavior and current NBA polling remain pending | Four functions defined; duration unmeasured | Yes; event-driven functions fit |
| Amazon API Gateway HTTP API | Device and companion HTTP routes | Recorded deployed route checks passed | No service-specific defect observed; not a public judge endpoint | SAM resource; duration unmeasured | Yes; fits app-to-backend calls |
| Amazon DynamoDB / Streams | Seven tables and event pipeline | Deployed tables and recorded smoke evidence | Moto does not prove IAM; no throughput benchmark claimed | SAM resources; duration unmeasured | Yes; keyed state and stream fit |
| Amazon EventBridge Scheduler | Two independent ingest triggers | Schedules declared in template | Both default disabled; live schedule behavior not established by template | Declaration only in this evidence | Yes as a design choice; live behavior still needs checking |
| Amazon CloudWatch Logs | Four function log groups | Groups declared with seven-day retention | No independent log-service performance observation | Declaration only in this evidence | Yes as a design choice; diagnostics required |
| AWS Systems Manager Parameter Store | Pending Yahoo credential storage | Secrets kept outside source in recorded setup | Yahoo approval remains a separate blocker | Owner provisioning; time unmeasured | Yes; separates credentials from code |
| AWS IAM | Function grants and scheduler roles | Grant contract checks; scoped template permissions | Mock tests do not enforce IAM | Template setup; time unmeasured | Yes; required access control |
| boto3 / botocore | Python AWS access and tests | Backend integration uses DynamoDB clients | Historical login-credential compatibility friction | Not measured separately | Yes with compatible credential setup |

### Testing, security, documentation and delivery tools

<!-- Evidence for these rows: docs/developer-feedback/product-feedback.md and observations.md OBS-020..029, OBS-040..049, OBS-090..106; tools/ci/gate.sh; tv-app/app/build.gradle.kts; backend/requirements.txt; backend/requirements-dev.txt; backend/src/feed_ingest/validation.py; tools/ci/mutation/; vega-app/package.json. Historical feedback is not a fresh tool run. -->

| Tool/service | Use | Worked well | Needs work / limits | Onboarding | Build again and why |
|---|---|---|---|---|---|
| Python 3.12 / pytest / Moto | Backend and offline tests | Reusable fixture suites ran in seconds in recorded slices | Test fixture shadowing; Moto does not enforce IAM | Foundation suites, no single duration | Yes; fast repeatable backend checks |
| jsonschema | Validate incoming ESPN payloads | Validation is wired before ingest writes | No standalone library experience recorded | Pinned dependency; no duration | Pending owner opinion |
| JUnit 4 / AndroidX Test / Compose UI Test | Host and instrumented TV tests | Launcher and alert seams testable | Kotlin test return type and dependency setup needed care | Not measured | Yes for the test stack; catches behavior regressions |
| org.json / SnakeYAML / PyYAML | JSON/YAML parsing in checks | Used by test/gate sources | No separate usability observation | Not observed | Pending owner opinion |
| coverage / diff-cover | Coverage measurement | Recorded reports available | Modules without executable lines could be omitted | Not measured | Yes with explicit report-completeness checks |
| mutmut | Python mutation checks | Recorded foundation score after timeout calibration | Copy paths and loaded-host timeouts needed adjustments | Not measured | Yes with those caveats |
| JaCoCo / PIT / Gradle PIT plugin | TV coverage and mutation checks | Configured report and mutation tasks | Legacy Gradle API compatibility needs explicit settings | Not measured | Pending owner opinion |
| responses | Backend HTTP test doubles | Declared in test dependency set | No separate tool observation | Not observed | Pending owner opinion |
| Android lint / Trivy | Build and dependency analysis | Build closure could be inspected | Per-configuration versions and bundled dependencies complicate analysis | Not measured | Pending owner opinion |
| ClamAV / gitleaks / pip-audit | Security scanner tools recorded as exercised | No per-tool result claimed here | Receipts do not provide complete individual experience | Not observed | Pending owner opinion for each |
| Bandit | Python static analysis | Explicit interpreter invocation worked | Use output-file mode for machine-readable JSON | Not measured | Yes with explicit interpreter binding |
| cfn-lint | CloudFormation validation | Recorded template lint exit 0 | No separate friction observed | Not measured | Yes; validates template |
| Repository gate / shell hooks | Local and CI checks | Shared check entrypoint | Tool availability and noisy output caused friction | Not measured | Yes; consistent checks |
| Git / GitHub / GitHub CLI / GitHub Actions | Version control, PRs and hosted checks | Recorded readbacks and check queries | CLI fields and hook environments needed care | Not measured | Yes; reviewable change history |
| OpenCodeReview | Assisted source review | Delegation rule inspection completed in recorded work | Markdown coverage excluded | Not measured | Yes as an assist; not independent proof |
| Reverify | Binary-check capability evaluation | Help and backend discovery were usable | APK manifest semantics not established | Not measured | Pending owner opinion for this project use |
| Codex CLI | Development and review assistance | Recorded author/review checks completed | No separate product defect established by these notes | Not measured | Yes; useful development assistance |
| Muse Code | Development assistance | Scribe reported headless completion; primary receipt unavailable | CLI invocation naming needed care; source gap limits the positive claim | Not measured | Earlier draft says Yes; William must confirm this opinion against the limited evidence |
| Claude Code | Development assistance | No positive result claimed for the cited limited run | Usage limit interrupted work; local hook friction is not a vendor-defect claim | Not measured | Yes with usage-limit caveats |
| Cursor Agent | Attempted development assistance | Not observed in cited run | Usage limit ended run before work | Not observed | Pending owner opinion |
| Deep Code | Recorded project workflow tool | No usable individual observation | Evidence insufficient for an experience claim | Not observed | Pending owner opinion |
| Bearing Lite | Project planning tooling | Recorded checks found an artifact collision | Document rendering and validation needed care | Not measured | Yes with recorded workflow fixes |
| spec-authoring / vendored spec tools / uv / Graphviz | Build specification documents and diagrams | Deterministic offline spec builds recorded | No separate uv/Graphviz evaluation | Not measured | Yes for the specification workflow |
| Requirements System | Requirements workflow | No separate success observation | Local guard integration needed care | Not measured | Pending owner opinion |
| SysON | Model import | Precise import diagnostics | Import requires the correct editing context | Not measured | Yes with explicit context |
| BRAN | Attempted repository knowledge checks | No native policy here | Unavailable for this repository; ordinary discovery used | Not applicable in this repo | Pending owner opinion |
| FFmpeg / ffprobe / Bash demo scripts | Captioned video cuts and validation | Two synthetic builds produced identical output hashes | Requires seven correctly sized source clips; real capture still pending | Scripted pipeline proof, no measured onboarding | Pending owner opinion |

<!-- FFmpeg evidence: tools/demo/README.md; tools/demo/build_cuts.sh; docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-X12/pipeline-proof-2026-10-21.md. Tool names are disclosed without model routes, prompts, budgets, accounts or private machine details. -->

Coverage reconciles the existing feedback inventory's 38 groups, adds the demo
pipeline and explicit app/test dependencies, and updates AWS, provider, Alexa and
Vega facts from newer evidence. Dependency closures in lockfiles are not claimed
as independently evaluated products. If the form separately lists a transitive
package, William can use: “Indirect dependency of the listed stack; no separate
onboarding or usability observation; build-again opinion not assessed.” Do not
invent a favorable review to fill a required Yes/No. Resolve such answers with
William in the preflight below.

## 9. Optional feedback fields

**Feature request, ready to paste:** Please document a supported Fire OS route
for actionable alerts over other apps' playback, or state the limitation and
recommended alternative. Our high-priority notification posted but was not
actionable in the tested notification UI, so alerts moved into our full-screen
panel. Priority: Critical for the original viewing experience.

**Friction log, ready to paste:** Fire OS 8.1.8.5; task: deliver a Watch/Dismiss
alert during playback. Steps: post a foreground-service high-importance
notification, try high priority and full-screen intent, inspect the notification
UI. Expected: reachable alert actions. Observed: no heads-up banner and no
reachable alert actions on the tested device. Severity: blocked the intended
interaction. Workaround: panel-only alerts. Suggestion: publish the supported
third-party interaction and a tested example. This is a device observation, not
a claim that every Fire TV behaves identically.

<!-- Evidence: docs/developer-feedback/feature-requests.md FR-005; spikes/sp2-notify/VERDICT.md; docs/developer-feedback/product-feedback.md OBS-003/004. Optional fields are named in https://amazonappdev2026.devpost.com/rules. -->

## 10. Owner preflight — do not paste unchecked assertions

**OWNER_DECISION_REQUIRED:** William settles eligibility/conflicts, ownership
and third-party terms (including ESPN/OA-6), team versus solo participation and
representative, and final track/mini-challenge choices. Registration is not an
eligibility ruling. William confirms the draft feedback recommendations and
supplies missing build-again opinions. Any unsupported required field remains
an explicit gap until answered. The [gap register](email-review.md#open-gaps-and-accountable-actions)
assigns actions and times; none is silently treated as complete.

<!-- Evidence: docs/submission/owner-checklist.md (Hackathon-admin items; OA-6/OA-7/OA-8); docs/developer-feedback/friction-log.md (Pending owner input). -->
