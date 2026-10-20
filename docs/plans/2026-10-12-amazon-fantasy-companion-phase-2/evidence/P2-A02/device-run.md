# P2-A02 device run (2026-10-20)

APK `ad9b0435…0ea880` (configured) on AFTKM, Fire OS 8.1.8.5, API 30,
1920x1080 override. Loopback variant `3b4bd340…be3eb` for the unavailable
state. Captures in `evidence/visual/P2-A02/`; verdicts in
`device-receipt.json` (this directory).

States inspected at 1080p: profile-loaded (all controls with persisted
values, focus visible as filled pill, overscan margins fine), voice-hidden
(limit text, not focusable), preset-switch (halfPpr -> ppr -> save -> kill ->
relaunch shows ppr, API revision 4 agrees; restored to halfPpr, revision 5),
profile-unavailable (loopback: unavailable message, no stale values).
Detection opt-in cannot be exercised: the row shows its stated limit only
(`X07_DETECTION_NOT_ACTIVATED`, P2-X07 PARTIAL on main).

## CANDIDATE-BUG-A02-1: profile text fields trap D-pad focus

Reproduction (exact steps): Profile/Settings, D-pad RIGHT into the form,
DOWN until focus reaches the League `BasicTextField`. The Amazon IME opens
on focus. DPAD_DOWN/UP then move only the keyboard cursor; the keyboard
Next button is a no-op (frame identical after OK); BACK closes the IME but
DOWN from the neighbouring buttons cannot cross the field geometrically.
Escape used here: keyboard Previous (IME_ACTION_PREVIOUS) or BACK plus
RIGHT+DOWN geometric traversal to the buttons beside/below the field.
Evidence: `evidence/visual/P2-A02/focus-trap-keyboard.png`. Logcat tail at
capture time held no app lines (buffer had rotated). Same behavior was
noted by the earlier device session; routing is the orchestrator's call.
No product source was changed in this packet.

## 2026-10-20 D-pad fix recapture

PR #129 merged (`44a7e06`). The CANDIDATE-BUG-A02-1 reproduction
was rerun on a debug APK built from that merge commit (sha256
`01cc1be16d5353bd43eb871fc6855a9d31d9757b2bf723c72dc7162c42ad71d3`):
plain DOWN traverses League field -> Team field -> Set
team/league with no keyboard trap
(`evidence/visual/P2-A02/dpad-recapture-league-focus.png`,
`dpad-recapture-team-focus.png`, `dpad-recapture-set-focus.png`):
**PASS**. Receipt: `device-receipt-dpad-recapture.json`. The APK
found at the start of the day was reinstalled afterwards.
