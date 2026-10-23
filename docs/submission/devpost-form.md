# Devpost paste package — AZ Fantasy

Updated October 23, 2026 from the October 22 live run, the current backend
template and the submission feedback package. Video production and submission
remain owner actions; this document is not a submission or an eligibility
determination. Follow the owner preflight in §10.

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

AZ Fantasy

<!-- Evidence: owner-selected product name, confirmed October 23, 2026. -->

## 2. Tagline

Your fantasy team over the live game, for every sport you play.

<!-- Evidence: owner live-night report, October 22, 2026; NFL and NBA support described in §3. -->

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
| Thumbnail / image gallery, if required | **UNKNOWN_FORM_FIELDS**. William selects an existing clean AZ Fantasy-only image or a plain text title card; no Amazon/AWS logos or provider screens. Required size and count are unknown. |
| Devpost project URL | **[OWNER: record the URL after creating the entry]** |

<!-- Evidence: README.md (Judge access); demo-plan.md. Public video upload and the Devpost project URL remain owner actions as of October 23, 2026. -->

Video: publicly visible YouTube/Vimeo, under three minutes, showing the app
functioning on Fire TV hardware or a permitted simulator. English captions;
clear manual/replay labels. These follow the [rules](https://amazonappdev2026.devpost.com/rules)
and [FAQ](https://amazonappdev2026.devpost.com/details/faqs).
The current voiceover plan targets 140 seconds (2:20), including NFL and NBA
alerts. The owner still needs to film the remote controls, record the narration
and check the finished runtime. Exclude provider frames, music without permission, Yahoo data,
link codes, personal information and device addresses. Synthetic color plates
are pipeline tests, not acceptable app-demonstration footage.

<!-- Evidence: demo-plan.md, current storyboard and capture notes. Content exclusions reflect owner instructions. -->

## 6. Track, category and mini-challenge

The current [feedback package](developer-feedback.md) identifies:

- Primary track: **Fire TV**.
- Mini-challenge: **AWS Builder**.
- Open Source mini-challenge: **not selected** in this package.
- Priority category: **sports**, if the form offers a category selector.

William confirms the final form selections. No Alexa+, Bee or Ring entry is
supported by this package. The category selector itself has not been observed.

<!-- Evidence: developer-feedback.md opening scope; backend/template.yaml; historical public event overview. -->

## 7. AWS Builder answer

Our backend is defined in AWS SAM and deployed through CloudFormation. The
current template defines four Python 3.12 Lambda functions: the HTTP API router,
NFL ESPN ingest, NBA ESPN ingest, and the DynamoDB Streams policy pipeline.
API Gateway exposes the HTTP API. Seven on-demand DynamoDB tables store
profiles, device links, events, alerts, lineups, panels and player statistics.
CloudWatch log groups retain the four functions' logs. IAM scopes the functions'
data access and the schedules' invocation permissions. SSM Parameter Store
supports the Yahoo integration setup without putting credentials in source.

Two EventBridge Scheduler resources invoke NFL and NBA ingest separately at
rate(1 minute). Both template parameters default to DISABLED. For the October 22,
2026 live run, both schedules were ENABLED on afc-dev at that one-minute rate.
The deployed ingest fixes use team-level game status and resolve NFL player IDs
by parsing play text when the feed omits play participants. The live TV run
captured NFL and NBA scoring alert cards over Prime Video. Alerts reached the
TV about 70–90 seconds after the play; reducing that delay remains planned work.

Lineups are manual today. Yahoo Fantasy API access has been approved, but
connection setup remains pending; no live Yahoo data is used in this package.
The function and resource inventory above comes from the repository template.
The live-night schedule state and deployment results come from the owner's
October 22 report, rather than from the template defaults.

<!-- Evidence: backend/template.yaml at 8ffc648; owner live-night deployment report, October 22–23, 2026; §3 live alert observations. -->

Use this answer with the AWS service descriptions in
[Product Feedback](developer-feedback.md#product-feedback). William compares it
with the signed-in form; any separate AWS field, account ID or Builder profile
question remains unverified. No credential belongs in the submission.

## 8. Product Feedback — paste body

The current paste bodies are in
[developer-feedback.md — Product Feedback](developer-feedback.md#product-feedback),
with 13 entries. Use those entries instead of the earlier tables. Historical
experiments are dated there; they do not negate the corner card and alert cards
that ran over live Prime Video on October 22, 2026.

## 9. Optional feedback fields

The current optional paste bodies are in
[developer-feedback.md — Feature Requests](developer-feedback.md#feature-requests)
(20 requests) and
[developer-feedback.md — Friction Log](developer-feedback.md#friction-log)
(32 entries). Use those sections for the form's optional fields.

## 10. Owner preflight — do not paste unchecked assertions

William completes these steps:

1. Record the voiceover from [demo-plan.md](demo-plan.md) and film the
   double-tap ≡ team switch and hold ≡ → Expand sequence.
2. Assemble the video using the live-run companion UI and the new control
   shots. Check the finished runtime, English captions and manual-lineup
   labels. Keep provider footage, Yahoo data, link codes, personal information
   and device addresses out of the submission edit.
3. Upload the finished video as a **public YouTube or Vimeo video**, confirm
   that it plays publicly, and paste its URL into §5.
4. Compare this package with the signed-in form. Paste the story, AWS answer
   and the applicable feedback bodies from [developer-feedback.md](developer-feedback.md).
   Confirm eligibility, ownership, third-party terms, team/representative
   details and final track/mini-challenge selections. Resolve required fields
   and placeholders before submitting.
5. Submit by **2026-10-23 19:00Z (2:00 PM CDT)** and record the resulting
   Devpost project URL.

The video and submission remain pending owner actions. The Watch flow was not
tested live; do not describe it as a verified live-game launch. Yahoo connection
setup remains pending, and the current live examples use manual lineups.

<!-- Evidence: owner submission instructions, October 23, 2026; demo-plan.md; developer-feedback.md. -->
