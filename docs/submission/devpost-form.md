## Inspiration

Fantasy sports spread your attention across games. You can be watching one game while a player on your fantasy team scores somewhere else. We wanted to keep that connection on the TV, where we were already watching, instead of making another screen part of every play.

AZ Fantasy is a Fire TV companion built around that idea. A small corner card keeps your fantasy team in view over the broadcast. Alerts bring your players' scoring moments to you, including moments from a different sport. The game stays on screen while you check your team.

## What it does

While you watch any live game, AZ Fantasy shows your fantasy team in a corner card. It supports NFL and NBA, so the sport on the television does not have to match the sport that produces an alert. A basketball player scoring can matter to your fantasy team even while you are watching football.

The remote handles the main controls. Double-tap the menu button, ≡, to switch teams. Hold it to open a menu with Expand, League and Hide. Choose Expand for a larger view of your lineup. These interactions keep you with the game.

Lineups are entered manually today. Yahoo Fantasy API access has been approved, but connection setup is still pending. The live demonstration uses manual lineups.

## How we built it

The TV app uses Kotlin and Jetpack Compose on Fire OS. Its corner card, alert cards and expanded panel put fantasy information over the viewing experience, with the remote as the main input.

The backend is defined with AWS SAM. AWS Lambda runs the application logic, Amazon API Gateway HTTP API connects the TV to the backend, and Amazon DynamoDB stores the application data. Amazon EventBridge Scheduler triggers feed polling. AWS Systems Manager Parameter Store is part of the backend configuration.

We use ESPN public feeds for live NFL and NBA statistics. The backend connects those updates to the players in a manual fantasy lineup and sends the relevant information to the TV. ESPN's live play feed omits player identifiers, so matching scoring plays requires parsing the play text.

## Challenges we ran into

The live run exposed a timing problem: alerts reached the TV about 70–90 seconds after the play. That is the observed delay, and reducing it is planned work. Parsing player names from play text is another limitation; the feed does not give us player identifiers on those plays.

Fire OS does not list our accessibility switch, which makes setup harder. Prime Video also blocks screenshots on some frames, so a screen capture does not always show the whole viewing experience. We had to distinguish a capture limitation from what was visible on the television.

We rebuilt the UI during the live game in response to feedback from the person using it. The Watch flow was not tested live, and we do not claim that it opened a live game.

## Accomplishments we're proud of

On October 22, 2026, the Fire TV stick's own screen recording captured the companion working during live Thursday Night Football on Prime Video. A “D. Maye · SCORE” alert appeared. Later, “C. Holmgren · SCORE” arrived from Denver at Oklahoma City while the NFL game was still on screen. An “A. Gordon · SCORE” alert appeared too.

That cross-sport moment is the clearest demonstration of the idea: the viewer stayed with football while the companion followed basketball. The same night's corner card showed NE at CHI, the fourth-quarter clock, a fantasy total and D. Maye's points. The expanded panel also showed an NBA lineup for CLE at PHI.

## What we learned

A live game answers questions that a static layout cannot. The card has to be readable without taking over the picture, and the remote controls have to be simple enough to use while following play. Rebuilding the UI during the game made those choices concrete.

We also learned to separate useful live behavior from finished behavior. Seeing the right player's alert arrive proved the connection from a scoring event to the TV. The 70–90 second delay showed why that connection still needs work. Capturing an alert and testing the Watch flow are separate checks; one does not prove the other.

## What's next

First, reduce the observed alert delay and check the result during another live game. Improve play-text matching, make the accessibility setup clearer, and test the Watch flow live. We also need another live pass through the rebuilt UI and a capture approach that accounts for Prime Video's blocked frames.

Then finish the pending Yahoo connection setup so we can move beyond manual lineups. The next version should make the experience easier to set up and faster to follow while preserving the simple corner card and remote controls.

## Built with

Fire TV, Fire OS, Kotlin, Jetpack Compose, Python, AWS SAM, AWS Lambda, Amazon API Gateway HTTP API, Amazon DynamoDB, Amazon EventBridge Scheduler, AWS Systems Manager Parameter Store, ESPN public feeds
