# P2-A05 repair (A05-R01..R04)

Candidate parent: 6ad508df604df8f37ab0545a2b3535f9d4a80dcb. One bounded repair after REPAIR_REQUIRED; coordinator verifies deterministically, no second review.

## Per-finding

- A05-R01 (PanelContent skips later scores/focus): PanelContent no longer takes the remembered PanelController. The parent passes immutable snapshot, teamLeague, focused, fetchAttempted and nowMs, so a fetched snapshot or focus move changes child parameters and Compose cannot take the skip branch. Proof limit: compiled-source inspection (same class as the review's render proof); no host Compose renderer exists. Device render stays DEVICE_INSTALL_PENDING.
- A05-R02 (wired switch has only the current selection): ProfileState stores exactly one team/league pair; FantasySelections leagues/teams are unpaired sets, so no additional pair exists to wire without inventing one. The switch list remains that one actual profile selection, and PanelController.NextTeamLeague is now a no-op when the next choice equals the current one: held rows are kept and the shown team is not refetched. Red then green: PanelRepairTest.switchingWithOneTeamLeagueKeepsRowsAndDoesNotRefetch (snapshot was null on the parent, retained after).
- A05-R03 (60 s boundary does not invalidate): the LineupPanel effect now increments tick after every 1 s delay, outside shouldFetch, so nowMs re-renders within 1 s of the stale boundary while the 30 s fetch cadence is unchanged. Proof limit: compiled-source inspection as R01.
- A05-R04 (invalid timezone offsets become fresh): parseInstantMs validates RFC3339 time-numoffset ranges (hour 00-23, minute 00-59); an out-of-range offset yields null asOfMs, which PanelText renders stale, never fresh. Red then green: PanelRepairTest.invalidTimezoneOffsetIsUndatedAndNeverFresh (parent parsed -99:99 to epoch ms 1792456740000; after, null) and validTimezoneOffsetsStillParse (-05:00 control).

## Verification

- Review reproducer on the parent observed the invalid-offset and freshness-timeline child failures (exit 1 each) before the fix; the runner pins the parent HEAD and committed sources, so it is a red-only instrument after this commit.
- PanelRepairTest on the parent: 2 failed, 1 passed. After the fix: `testDebugUnitTest --tests 'com.afc.companion.panel.*'` green, 37 panel tests, 0 failures/errors (34 frozen + 3 repair).
- Frozen hashes: sha256sum -c against P2-A05/frozen-hash-check.txt, all five OK (MATCH).
- Repository gate: `bash tools/ci/gate.sh` exit 0 (run before commit; recorded in the repair result packet).

Typed gaps unchanged: REVERIFY_CAPABILITY_GAP, VISUAL_EMULATOR_UNAVAILABLE, DEVICE_INSTALL_PENDING, X04_VERDICT_PENDING, PANEL_WIRE_UNFROZEN.
