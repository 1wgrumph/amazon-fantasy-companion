# P2-A03 repair (A03-R01/R02/R03)

Base candidate: a046304688016c28e5e61df2f6300e1191b41a98. One bounded repair; no second review.

## Red (before fix, on base HEAD)

- Review probe `review/run-probes.py`: R01 context emitted the on-field/will-score
  player string; R01 commentary `will  score` emitted; R03 Aa/BB both
  notificationId 2112 and Watch requestCode 65473; R02 PanelOnly then HTTP 500
  profile load returned null and the old service predicate selected notify.
- New `AlertRepairRegressionTest` (6 tests): 5 failed as designed (unsafe player,
  unsafe matchup, whitespace-variant commentary, hyphen-variant commentary,
  Aa/BB notification id collision); benign text passed.
- New `PresentationGateTest`: failed to compile (gate absent), matching the R02
  behavioral red from the probe above.

## Fix

- R01 `AlertPresenter`: every displayed untrusted field (player, matchup, the
  combined context, commentary) is checked with `isUnsafe`, which normalizes
  non-alphanumerics to single spaces before matching, so whitespace/punctuation
  variants cannot slip through. Unsafe player/matchup returns no text; unsafe
  commentary is dropped whole. Headline and access labels remain app-owned.
- R02 `AlertService` + `PresentationGate`: a null profile never means heads-up.
  The last validated presentation decides; with none validated, alerts are
  deferred in a bounded pending set and flushed only when a loaded profile is
  heads-up. Panel-only clears the notifier backlog (the feed retains alerts
  for the panel).
- R03 `AlertNotifier`: notifications are posted/cancelled with a full-identity
  tag (`alert:<id>`) plus a SHA-256-derived int id; Watch and Dismiss
  PendingIntents carry a per-alert/per-action data URI and SHA-256-derived
  request codes, so distinct ids (including hashCode-colliding Aa/BB) never
  share a notification or action token.

## Green

- `testDebugUnitTest --tests "com.afc.companion.alerts.*"`: all pass — frozen
  AlertFeedTest (7), frozen AlertPresenterTest (11), AlertRepairRegressionTest
  (7), PresentationGateTest (4).
- `assembleDebugAndroidTest`: BUILD SUCCESSFUL (compilation only;
  DEVICE_INSTALL_PENDING and VISUAL_EMULATOR_UNAVAILABLE remain typed gaps).
- Frozen SHA-256 all MATCH: AlertFeedTest 5ed136e2…, AlertFixtures f6c42298…,
  AlertPresenterTest d5e9fe12…, AlertNotifierDeviceTest 807f8036….
- Old defect predicates absent from alert sources (null-profile heads-up
  comparison; String.hashCode identity).
- Repository gate: see the repair result receipt for the final exit code.
