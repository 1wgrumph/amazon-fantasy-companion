# AZ Fantasy — demo talking points

Target runtime: **2:30**; hard limit: **under 3:00**. Speak naturally from the bullets, not word for word. Use captions for dates, source attribution and supporting roadmap detail; rehearse to the time ranges. Live examples are from October 22, 2026, with manual lineups. New phone, app and remote shots are owner captures still to be filmed.

QR linking is being built for today's release and was absent from the inspected build. Film and describe it as working only after it lands and is verified on the TV and phone. Typed-code linking is the existing fallback. Confirm the corner-card fields, including the top two players, in the capture build before filming; the inspected source does not establish that layout. The card overlays a corner of the picture, so describe it as keeping the game in view rather than covering none of the picture.

## 1. Hook — 0:00–0:20

**On screen:** AZ Fantasy title, then the clean corner card. Brief source captions: “FSGA · 2022 · U.S. adults 18+” and “Pew · May 2020 report · 2019 survey.”

- About 50 million American adults play fantasy sports — FSGA's 2022 estimate.
- About half of partnered adults report phone distraction during conversation — Pew.
- “I'm one of those people.” Be present with family and friends; still follow my team.
- “That's why I built AZ Fantasy Companion.”

## 2. What it is — 0:20–0:35

**On screen:** Fire TV app: Connect, My setup and My lineup. Caption: “Kotlin · Python · AWS.” Cut to the live-run companion UI over the watching context, labeled “Thursday Night Football · Prime Video · October 22, 2026.”

- Fire TV companion: Kotlin app, Python backend on AWS.
- Runs over whatever I'm watching — here, Thursday Night Football on Prime Video.
- Runs on Fire TV today; Vega OS version built and tested on Amazon's Vega virtual device.
- Physical Vega hardware remains untested.

## 3. Setup — 0:35–0:55

**On screen:** Owner films phone scanning the TV QR, phone confirm page and confirmation action, then TV becoming linked. Quick cuts through My setup (NFL/NBA toggles, alert types, quiet hours, Open lineup on alerts and provider preferences), My lineup, then Show over game. Mask QR contents and link codes in the edit.

- Scan the TV's QR on my phone; confirm; connected.
- My setup: sports and alert preferences.
- My lineup: teams and points; Show over game returns to watching.
- Built toward Yahoo's Fantasy API; approval missed the deadline, so enter lineups by hand for now.

## 4. Watching — 0:55–1:10

**On screen:** Clean corner-card shot. Retain the legible “NE @ CHI” matchup, fourth-quarter clock, total 90.0 and D. Maye 26.6. Owner films the updated card if needed to show both leading players. Caption: “Live run · Manual lineup”; label any new capture separately.

- Matchup and game clock.
- Fantasy team total and top two players — verify in the capture build.
- Small corner card keeps the game in view.

## 5. Alerts — 1:10–1:40

**On screen:** “D. Maye · SCORE” alert, followed by “C. Holmgren · SCORE” from DEN @ OKC during the NFL watching context. Keep each card readable. Label the cut between separate live-run moments; they were not seconds apart. Caption the observed delay: “Alerts arrived 70–90 seconds after the play.”

- Maye scores; his alert card pops up.
- Cross-sport: Holmgren's NBA alert arrives while I'm watching football.
- “Every sport you play, whatever game is on.” NFL and NBA today.
- Live proof from the stick's own recording; faster alerts are next.

## 6. Controls and value — 1:40–2:15

**On screen:** Owner films double-tapping ≡ and the card switching from an NFL team to an NBA team. Then hold ≡, show Expand / League / Hide, and choose Expand. Show the full lineup; use “NBA · CLE @ PHI · Total 195.3” if available in the new capture.

- Double-tap ≡ switches teams — NFL to NBA.
- Hold ≡ opens the menu; choose Expand.
- Every starter's live fantasy points and the team total.
- “Everything my phone told me, without picking up my phone.”

## 7. What's next and close — 2:15–2:30

**On screen:** Return to the corner card, then AZ Fantasy title. Roadmap captions: “Yahoo · More leagues and sports · Faster alerts” and “Future idea: bet tracking only · No bet placement · No partnership implied.” No working bet-tracking UI is claimed.

- Next: Yahoo, more leagues and sports, faster alerts.
- Prime Video already has FanDuel bet tracking during Thursday Night Football.
- Future: bets beside fantasy on any game; tracking only, never placing bets. No partnership implied.
- “Every sport. One glance. Never leave the game.”

## Shot sources and owner filming

The private clip list holds the live-run source filenames, offsets and visual checks: Maye, Holmgren, a clean corner card, and A. Gordon as an alternate NBA alert. Keep it and all source media outside the public repository.

The owner still needs to film:

- The phone scanning the TV QR and the phone confirm page, followed by the TV linked state, after QR verification.
- My setup, My lineup and Show over game; verify the current corner-card layout and capture its top two players if available.
- The double-tap ≡ NFL-to-NBA team switch, hold ≡ menu and Expand sequence.

Record the voiceover from these talking points and check the finished runtime against 2:30. If QR verification or the two-player card is still pending, retain that capture gap rather than presenting a mockup as delivered behavior. The owner assembles, uploads and submits the video.

Keep provider footage private. Crop or mask to isolate the companion UI over a neutral background for the submission edit, with the watching context described in speech and captions. Never imply that a masked or black provider surface means playback stopped. Prime Video blocks screenshots on some frames. Do not show account details, QR contents, link codes, device addresses or Yahoo data. The Watch flow was not tested live and is outside this storyboard.

## Sources

- [FSGA industry demographics](https://thefsga.org/industry-demographics/) now redirects to its research index. The [industry figures page](https://thefsga.org/fantasy-sports-gaming-industry/) lists **50.4 million U.S. fantasy players aged 18+ in 2022**, not a current-year estimate or the combined U.S./Canada total.
- [Pew Research Center, “Dating and Relationships in the Digital Age”](https://www.pewresearch.org/internet/2020/05/08/dating-and-relationships-in-the-digital-age/), May 8, 2020: **51% of partnered U.S. adults** said their partner was often or sometimes distracted by a cellphone during conversation. Survey: October 16–28, 2019. This is not a finding about fantasy players specifically.
- [Front Office Sports, “Amazon's Prime Video Antes Up on Sports Betting”](https://frontofficesports.com/article/amazons-prime-video-antes-up-on-sports-betting/), February 9, 2023, covers SportsGrid distribution on Prime Video; it is background, not evidence of personalized TNF bet tracking.
- [Covers, “FanDuel Adds Live Bet Tracking to Prime Video's Thursday Night Football”](https://www.covers.com/industry/fanduel-adds-live-bet-tracking-to-prime-video-thursday-night-football-sept-16-2026), September 16, 2026, supports the TNF tracking example and distinguishes tracking from placing bets. That existing service implies no partnership with AZ Fantasy.
