# P2-A02 repair notes (one REPAIR_REQUIRED round)

Base candidate: `2ca71d6aa8f6e52350d7f5cd1e5f99bbeb03494b` on `afc/p2-a02t`.
Role/route: Bearing Lite Product Implementer, Muse Code / muse-wonder-full-1.0 / high.

## A02-R-F01 — remote-reachable editors

`ProfileSettingsScreen.kt` now renders editors for Selections (leagues, teams,
players, favorite teams: add by name, remove per entry), TeamLeague (league +
team name entry, set/clear), AlertTypes (one toggle per type), QuietHours and
GameDay periods (add window, ±30m start/end, remove), and ProviderPreference
(provider order move-up/remove/add, per-provider access confirmation,
detected-app override cycle automatic/installed/not-installed plus add-by-package,
local market set/clear). Every editor writes into the draft `ProfileState`
(`selections=`, `teamLeague=`, `alertTypes=`, `quietHours=`, `providerPref=`,
`periods=`) that the existing Save button submits through `ProfileStore.save`.
Edit logic lives in pure helpers in `ProfileEdits.kt` so host tests exercise the
same operations the buttons invoke.

Evidence: reviewer `reproduce-ui-contract.py` exit 0 (`repair-reproducers.txt`);
`ProfileRepairTest#editorOperationsChangeEveryFieldAndSurviveSaveReload` and
`#editorOperationsRejectBlankInputAndCycleOverrides` pass.

## A02-R-F02 — detection bound to verified capability

The screen binding is now `profileControls(detectionSupported = false, ...)`.
No verified installed-app detection route exists until P2-X07, so the
DetectionOptIn control is hidden and its stated limit is shown.
`DEVICE_INSTALL_PENDING` and `X07_VERDICT_PENDING` remain open typed gaps; the
comment at the binding names both. When X07 verifies a route, this one literal
flips.

Evidence: reviewer `ReviewBehaviorReproducer detection` exit 0
(`repair-reproducers.txt`);
`ProfileRepairTest#screenBindsDetectionUnsupportedUntilX07AndWritesEveryEditedField` passes.

## A02-R-F03 — in-flight save cannot replace a newer draft

The Save callback no longer assigns the response over the draft. It saves the
submitted draft, then re-saves while the current draft differs from what was
submitted, so an edit made during the PUT is submitted too and only then is
"Profile saved." reported. If the draft changed again after the last submit,
the message says the newer edits are not saved yet. On failure the draft is
left untouched (previously reset to the captured pre-save state).

Evidence: reviewer `ReviewBehaviorReproducer save-race` exit 0 — after the
in-flight edit, excitement stays `Mild`, server PUT count is 2 and the stored
excitement is `Mild` (`repair-reproducers.txt`);
`ProfileRepairTest#saveInFlightEditIsResavedNotOverwritten` and
`#failedSavePreservesNewerDraft` pass (success and stale-revision failure).

## Frozen tests and gate

All five frozen A02T test files are byte-identical to
`../P2-A02T/receipt.json` (sha256 reverified this session). The 26 frozen
profile/detect tests still pass; 5 new repair tests pass (31 in the
profile/detect scope, 115 TV unit tests total). `bash tools/ci/gate.sh`
exits 0 (`repair-gate.txt`: spec/docs/hygiene/tvapp/backend PASS, backend 380).

## Remaining gaps (unchanged, never PASS)

- `DEVICE_INSTALL_PENDING`: no Fire TV stick; D-pad focus/order and on-screen
  keyboard entry for the new name fields are not device-verified.
- `VISUAL_EMULATOR_UNAVAILABLE`: no emulator/AVD in the configured SDK; no
  layout, legibility, or focus claim.
- `X07_VERDICT_PENDING`: detection stays hidden with its stated limit.
- `REVERIFY_CAPABILITY_GAP`: unchanged from the author receipt.
