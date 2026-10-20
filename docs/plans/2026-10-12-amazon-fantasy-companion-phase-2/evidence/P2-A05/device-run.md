# P2-A05 device run (2026-10-20)

APK `ad9b0435…0ea880`, AFTKM Fire OS 8.1.8.5, 1920x1080 override, density
320. P2-X04 verdict on main is FAILS, so the panel was reviewed in its
FullScreen fallback (`panelModeFor(null)` in `MainActivity`); no modeB
geometry exists to verify.

D-pad run on the Panel destination: initial focus border on the
Team/league switch row, DPAD_DOWN moves it to Team total (Compose focus
traversal confirmed on device), Menu hides to the hint text and shows
again byte-identically, fast-forward with one selected team/league is a
no-op. With the selected team/league and an empty stored lineup, Team
total and Progress render `Unavailable` — never zero. The stale-labeled
state needs a stored lineup/statistics fixture and was blocked by the
expired AWS session (`FIXTURE_AWS_SESSION_EXPIRED`).

Text sizes (CMD-TEXT-SIZE-MEASURE) on `legibility.png`: source 24 sp body /
32 sp scores at density factor 2.0 give 48/64 px; measured text boxes
57/75 px and glyph ink 46-47/49 px, above the 24/32 px floors. The owner
couch-legibility decision in the SEIT pass text was not taken:
`OWNER_EVIDENCE_PENDING`.

## 2026-10-20 fixture rerun

AWS session valid again. Only the former
`FIXTURE_AWS_SESSION_EXPIRED` step (index 2, stale labeled) was
rerun; `OWNER_EVIDENCE_PENDING` and the other results stand. APK
as found, sha256 `1d80c6822182399794bbe4cec27198a0a31da58e3533ebcb9acf431a2729b988`. A guarded statistics
fixture for synthetic athlete 9000001 with `asOf` one hour old
rendered `13.0 (replay, stale 3725s)` on the starter row, team
total and progress after relaunch and Panel re-entry
(`evidence/visual/P2-A05/fixture-rerun-stale-labeled.png`):
**PASS**. A 35 s in-place wait did not refresh the displayed
panel; the value appeared on the next fetch. Receipt:
`device-receipt-fixture-rerun.json`. Fixture record deleted.
