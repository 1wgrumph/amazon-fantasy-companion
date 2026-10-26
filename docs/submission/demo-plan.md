# AZ Fantasy — demo talking points

William submitted the project on October 23, 2026 with [the demo video](https://youtu.be/-K53tzSCKC4). These are the pre-submission talking points and capture instructions, not a verification that every planned shot appears in the submitted video. William is the observer for the October 22 live-run examples and the October 23 TV-and-phone QR verification.

Target runtime and maximum for this edit: **2:30**; the platform limit is **under 3:00**. Speak naturally from the bullets, not word for word. Use captions for dates, source attribution and supporting roadmap detail; rehearse to the time ranges and trim rather than running past 2:30. Segment 2 gets 35 seconds for the added sports context; the other cues are shorter. Live examples are from October 22, 2026, with manual lineups. The phone, app and remote shots below were assigned to William for capture.

QR linking shipped and William verified it on the TV stick and phone on October 23, 2026. Typed-code linking remains the fallback. The current corner-card source renders the top two players with available points; William's capture check below remains separate from this source inspection. The card overlays a corner of the picture, so describe it as keeping the game in view rather than covering none of the picture.

## 1. Hook — 0:00–0:18

**On screen:** AZ Fantasy title, then the clean corner card. Brief source captions: “FSGA · 2022 · U.S. adults 18+” and “Pew · May 2020 report · 2019 survey.”

- About 50 million U.S. adults played fantasy sports in 2022 — FSGA.
- About half of partnered U.S. adults said their partner was often or sometimes distracted by their phone during conversation — Pew, 2020.
- “I'm one of those people.” Family, friends and my fantasy team.
- “That's why I built AZ Fantasy Companion.”

## 2. What it is — 0:18–0:53

**On screen:** Fire TV app: Connect, My setup and My lineup. Caption: “Kotlin · Python · AWS.” Cut to the live-run companion UI over the watching context, labeled “Thursday Night Football · Prime Video · October 22, 2026.”

- Fire TV companion over whatever I watch: Kotlin app; Python on AWS.
- “Amazon now carries two of America's most popular sports, and fantasy players follow both. AZ Fantasy puts their fantasy teams right where they watch.”
- Fire TV today; Vega virtual device tested; physical Vega hardware untested.

## 3. Setup — 0:53–1:13

**On screen:** Owner films phone scanning the TV QR, phone confirm page and confirmation action, then TV becoming linked. Quick cuts through My setup (NFL/NBA toggles, alert types, quiet hours, Open lineup on alerts and provider preferences), My lineup, then Show over game. Mask QR contents and link codes in the edit.

- You start by Scan QR; confirm on my phone; connected.
- Linking uses a one-time code that expires, so the TV never sees a password.
- My setup; My lineup; Show over game.
- Built toward Yahoo's Fantasy API; approval missed the deadline. Manual lineups for now.

## 4. Watching — 1:13–1:23

**On screen:** Clean corner-card shot. Retain the legible “NE @ CHI” matchup, fourth-quarter clock, total 90.0 and D. Maye 26.6. Owner films the updated card if needed to show both leading players. Caption: “Live run · Manual lineup”; label any new capture separately.

- Matchup and game clock.
- Fantasy team total and top two players — verify in the capture build.
- Small corner card keeps the game in view.

## 5. Alerts — 1:23–1:45

**On screen:** “D. Maye · SCORE” alert, followed by “C. Holmgren · SCORE” from DEN @ OKC during the NFL watching context. Keep each card readable. Label the cut between separate live-run moments; they were not seconds apart. Caption William's live-run estimate: “Alerts arrived about 70–90 seconds after the play.” This is an owner-observed end-to-end estimate, not an isolated EventBridge or Lambda measurement.

- Maye scores; his card pops up.
- Holmgren's NBA alert during football.
- “Every sport you play, whatever game is on.” NFL and NBA today.
- Live recording from the stick; faster alerts next.

## 6. Controls and value — 1:45–2:10

**On screen:** Owner films double-tapping ≡ and the card switching from an NFL team to an NBA team. Then hold ≡, show Expand / League / Hide, and choose Expand. Show the full lineup; use “NBA · CLE @ PHI · Total 195.3” if available in the new capture.

- Double-tap ≡ switches teams — NFL to NBA.
- Hold ≡; choose Expand.
- Every starter's live points; team total.
- “Everything my phone told me, without picking up my phone.”

## 7. What's next and close — 2:10–2:30

**On screen:** Return to the corner card, then AZ Fantasy title. Roadmap captions: “Real accounts and sign-in · Yahoo · More leagues and sports · Faster alerts” and “Future idea: bet tracking only · No bet placement · No partnership implied.” No working bet-tracking UI is claimed.

- Next: real accounts and sign-in; Yahoo; more leagues and sports; faster alerts.
- Prime already tracks FanDuel bets during TNF.
- Future: bets beside fantasy, any game. Tracking only; no bet placement or partnership.
- “Every sport. One glance. Never leave the game.”

## Shot sources and owner filming

The private clip list holds the live-run source filenames, offsets and visual checks: Maye, Holmgren, a clean corner card, and A. Gordon as an alternate NBA alert. Keep it and all source media outside the public repository.

The pre-submission plan assigned William these shots:

- The phone scanning the TV QR and the phone confirm page, followed by the TV linked state; William completed QR verification on October 23, 2026.
- My setup, My lineup and Show over game; verify the current corner-card layout and capture its top two players if available.
- The double-tap ≡ NFL-to-NBA team switch, hold ≡ menu and Expand sequence.

William was responsible for recording the voiceover, checking the finished runtime against 2:30, assembling, uploading and submitting the video. QR verification is complete; this reviewer has not verified the final two-player-card capture or the finished edit.

Keep provider footage private. Crop or mask to isolate the companion UI over a neutral background for the submission edit, with the watching context described in speech and captions. Never imply that a masked or black provider surface means playback stopped. Prime Video blocks screenshots on some frames. Do not show account details, QR contents, link codes, device addresses or Yahoo data. The Watch flow was not tested live and is outside this storyboard.

## Sources

- [FSGA industry demographics](https://thefsga.org/industry-demographics/) redirected to its research index when checked by Codex on October 23, 2026. The [industry figures page](https://thefsga.org/fantasy-sports-gaming-industry/) lists **50.4 million U.S. fantasy players aged 18+ in 2022**, not a current-year estimate or the combined U.S./Canada total.
- [Pew Research Center, “Dating and Relationships in the Digital Age”](https://www.pewresearch.org/internet/2020/05/08/dating-and-relationships-in-the-digital-age/), May 8, 2020: **51% of partnered U.S. adults** said their partner was often or sometimes distracted by a cellphone during conversation. Survey: October 16–28, 2019. This is not a finding about fantasy players specifically.
- [Front Office Sports, “Amazon's Prime Video Antes Up on Sports Betting”](https://frontofficesports.com/article/amazons-prime-video-antes-up-on-sports-betting/), February 9, 2023, covers SportsGrid distribution on Prime Video; it is background, not evidence of personalized TNF bet tracking.
- [Covers, “FanDuel Adds Live Bet Tracking to Prime Video's Thursday Night Football”](https://www.covers.com/industry/fanduel-adds-live-bet-tracking-to-prime-video-thursday-night-football-sept-16-2026), September 16, 2026, supports the TNF tracking example and distinguishes tracking from placing bets. That existing service implies no partnership with AZ Fantasy.
- [NBC Sports Bay Area, NBA viewership and the new media-rights deal](https://www.nbcsportsbayarea.com/nba/nba-viewership-up-last-season-new-media-rights-deal/1931466/): owner-supplied context link; Codex received HTTP 200 on October 23, 2026, superseding the earlier HTTP 403 result. The NBA announcement and AP report below supply the deal dates and total value.
- [Advanced Television, “NBA on Prime sees significant global audience growth”](https://www.advanced-television.com/2026/07/03/nba-on-prime-sees-significant-global-audience-growth/), July 3, 2026, describes the first season under Prime's global NBA agreement. Its international growth figures are not U.S. opening-weekend audiences.
- [Amazon's February 2022 results announcement](https://ir.aboutamazon.com/news-release/news-release-details/2022/Amazon.com-Announces-Fourth-Quarter-Results/) confirms TNF exclusivity beginning in September 2022 under an 11-year NFL agreement.
- [NBA's media-agreements announcement](https://pr.nba.com/nba-walt-disney-company-nbcuniversal-amazon-prime-video-media-agreements/) confirms the 2025–26 start and 11-year term. [AP's October 2025 viewing guide](https://apnews.com/article/7f3902ad6affb56790958149e75b9acc) reports about $76 billion across the partners, not Amazon's payment alone. The optional opening-weekend audience number is omitted to keep the cues short.
