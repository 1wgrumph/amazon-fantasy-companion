# P2-A03 device run (2026-10-20)

APK `ad9b0435…0ea880`, androidTest APK `a0c8aeb7…64dc4`, AFTKM Fire OS
8.1.8.5. P2-X02 verdict on main is FAILS (`spikes/sp2-notify/VERDICT.md`):
Fire OS posts the high-importance notification but never presents a
heads-up banner, so the pending steps 3-4 (heads-up over provider playback,
D-pad to Watch/Dismiss in the banner) are not claimable; panel-only is the
fallback. The instrumented test passed on the stick via `am instrument`
(`OK (1 test)`); the Gradle `connectedDebugAndroidTest` entry point fails
dependency verification for the UTP configuration before running anything
(`GRADLE_UTP_VERIFICATION_GAP`, candidate build-config bug for the
orchestrator; verification metadata is outside this write set).

Panel-only alert-card states (card, Watch, Dismiss, panel-only suppressing
the notification post) need a synthetic alert in the dev backend. The AWS
CLI session for afc-dev is expired and reauthentication (`aws login`) is
owner-only, so no fixture was written: `FIXTURE_AWS_SESSION_EXPIRED`.
Re-run after reauthentication with the earlier session's fixture procedure
(guarded helper, own profile only, delete after). The test APK was
uninstalled after the run (`com.afc.companion.test` removed, exit 0).

## 2026-10-20 fixture rerun

AWS session valid again. Only the former `FIXTURE_AWS_SESSION_EXPIRED`
step (index 2) was rerun; every other recorded result above stands.
APK as found on the stick, sha256 `1d80c6822182399794bbe4cec27198a0a31da58e3533ebcb9acf431a2729b988`.
Guarded synthetic fixture (own dev test profile only, manual lineup
Sample Receiver 9000001, one PlayerScore alert
`afc-fixrerun-20261020T163802Z-01`): the panel showed the delivered
panel-only card with Watch and Dismiss
(`evidence/visual/P2-A03/fixture-rerun-alert-card.png`), D-pad
focused Watch (`fixture-rerun-watch-focused.png`), and Dismiss
removed exactly that card (`fixture-rerun-dismissed.png`): **PASS**.
Receipt: `device-receipt-fixture-rerun.json`. Fixture alert and
lineup removed afterwards; stick restored (see receipt).
