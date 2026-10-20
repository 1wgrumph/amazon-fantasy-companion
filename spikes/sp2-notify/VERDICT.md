---
spike: SP-2
slice: P2-X02
verdict: FAILS
device:
  model: AFTKM
  fire_os: Fire OS 8.1.8.5 (RS8185/3891)
  android_release: "11"
  api_level: 30
started_at: 2026-10-16T19:35:47Z
ended_at: 2026-10-16T20:36:16Z
first_install_at: not applicable (SP-1 and SP-4 only)
unblocks: [AFC-PR-021, RISK-AFC-P2-02]
conditional: none
---

# SP-2 heads-up notification verdict

**Verdict: FAILS** for the heads-up route. A foreground service can post a
high-importance notification with Watch and Dismiss actions on this stick, and
Prime Video playback continues undisturbed — but Fire OS never shows it as a
heads-up banner, over playback or anywhere else, so there is no on-screen
moment at which D-pad focus could reach Watch or Dismiss. AFC-PR-015's
positive case (heads-up with Watch/Dismiss during third-party playback) is
not unblocked. Selected fallback: the panel-only presentation of AFC-PR-021 /
DES-AFC-P2-ALERTPATH ("heads-up notification … via the route P2-X02 verifies,
or panel-only"). RISK-AFC-P2-02 is realized for the Fire OS target as tested.

Test article: the leased stick above, Prime Video (`com.amazon.firebat`,
owner-signed-in, Prime-included title started over ADB; no purchase, rental,
or account/settings change). Spike probe: `com.afc.spike.sp2` from this
directory (first-sweep APK sha256
`009f0b9fd52d03cfeea273b2052c037b2140e45c2fe594136e5020e86a3d3bf8`; repair-sweep
APK with `PRIORITY_HIGH` and the full-screen-intent variant sha256
`81d840c9cf23b5044bd8890d990ff01d28983da8868481a205cbf1bf2afc83fa`), installed
for each sweep and uninstalled after it. Full commands with exit codes,
logcat, and screenshots: `evidence/visual/sp2-notify/` (`attempts.txt`,
`logcat.txt`). Device address, serial, and account data are deliberately not
recorded; no screenshot shows an account name or email.

## Routes tried

1. **Heads-up notification, plain high-importance channel** (attempts 1, 3).
   A foreground service posts a `CATEGORY_EVENT` notification on an
   IMPORTANCE_HIGH channel with Watch (activity `PendingIntent`) and Dismiss
   (service `PendingIntent`) actions — the DES-AFC-P2-ALERTPATH shape.
   Source: Android developer docs, "Create a notification" and
   "Notifications on TV"
   (https://developer.android.com/develop/ui/views/notifications/build-notification;
   the TV guidance relies on the notification appearing in the tray/heads-up).
   The notification posts (`dumpsys notification`: `importance=4`,
   `actions=2`, Watch→`startActivity`, Dismiss→`startService` in
   `attempts.txt`), on API 30 with no runtime notification permission needed
   (logcat `postNotifGranted=true`; `POST_NOTIFICATIONS` is an API 33+
   runtime permission). But no banner peeks: not over the spike's own
   activity (`attempt1-headsup.png`, 1 s after posting) and not over Prime
   Video playback (`attempt3-headsup-1s.png`, `-3s.png`; the ad pre-roll
   timer runs 1:25 → 1:23 across the post, media session `state=3`
   throughout, `ResumedActivity` stays `com.amazon.firebat` — playback
   continues and our app is never foregrounded, which is the one part of
   AFC-PR-015 that behaved as wanted).
   Outcome: **fails (blocked by platform presentation)**.
2. **Heads-up retry with sound + vibrate** (attempt 5B). Android's peek rule
   historically also wants a sound or vibration, so the retry set
   `DEFAULT_SOUND | DEFAULT_VIBRATE` on the notification and a sound +
   vibration pattern on a fresh channel (`sp2-alerts-v2`; channel settings
   are immutable once created). `dumpsys` confirms `vibrate=default
   sound=default defaults=0x3 importance=4 actions=2`. Still no banner over
   playback at 1 s or 3 s (`attempt5-headsup-1s.png`, `-3s.png`), and
   DPAD_UP reaches nothing (`evidence/visual/PRIVATE-EVIDENCE.md` (Prime Video player after DPAD_UP, withheld)). (`headsUpContentView=null`
   in the dump is not used as evidence: since Android N that field can be
   null while SystemUI builds a heads-up view from Builder inputs; the
   screenshots are the absence evidence.)
   Source: Android developer docs, "Heads-up notifications"
   (https://developer.android.com/develop/ui/views/notifications#Heads-up).
   Outcome: **fails (blocked by platform presentation)**.
3. **Heads-up retry with `PRIORITY_HIGH`** (repair attempt 8).
   Documented behavior: Amazon's Fire TV notification guide requires
   notification priority HIGH for a heads-up notification, on top of the
   channel importance. Source: Amazon Fire TV developer docs,
   "Notifications" — heads-up notifications
   (https://developer.amazon.com/docs/fire-tv/notifications.html#heads-up-notifications).
   Procedure tested: the alert builder now sets
   `setPriority(Notification.PRIORITY_HIGH)` (channel stays
   IMPORTANCE_HIGH; the foreground-service notification is explicitly
   `PRIORITY_LOW` so it does not compete), posted from the foreground
   service over Prime Video playback. Observation: `dumpsys` records
   `pri=1 importance=4 actions=2` (attempts.txt, repair attempt 8), but
   still no banner at 1 s or 3 s (`repair8-headsup-1s.png`, `-3s.png`;
   the ad pre-roll timer runs 0:52 → 0:49 across the post, media
   `state=3`, `ResumedActivity` stays `com.amazon.firebat`). The
   documented priority input does not change the outcome on this build.
   Outcome: **fails (blocked by platform presentation)**.
4. **Full-screen intent** (repair attempt 9). Documented behavior: before
   API 33, SystemUI may show a full-screen-intent notification as a
   heads-up while the device is in use instead of launching the intent;
   `USE_FULL_SCREEN_INTENT` is a normal permission, granted at install
   with no customer settings change. Sources: Android API reference,
   `Notification.Builder.setFullScreenIntent`
   (https://developer.android.com/reference/android/app/Notification.Builder#setFullScreenIntent(android.app.PendingIntent,%20boolean))
   and `USE_FULL_SCREEN_INTENT`
   (https://developer.android.com/reference/android/Manifest.permission#USE_FULL_SCREEN_INTENT).
   Procedure tested: same alert plus `setFullScreenIntent(..., true)`
   (category stays `CATEGORY_EVENT`, the intended sports-alert
   semantics), posted over Prime Video playback. Observation: the record
   carries the intent (`fullscreenIntent=PendingIntent{...}`, system
   boosts `pri=2`), yet neither documented branch happens — no heads-up
   banner at 1 s or 3 s (`repair9-fsi-1s.png`, `-3s.png`; ad timer
   0:15 → 0:12) and the spike is not foregrounded (`ResumedActivity`
   stays `com.amazon.firebat`, media `state=3`; DPAD_UP afterwards
   reaches only Prime Video's own player controls,
   `evidence/visual/PRIVATE-EVIDENCE.md` (Prime Video player controls after DPAD_UP, withheld)). Negative result recorded as observed.
   Outcome: **fails (neither heads-up nor full-screen branch taken)**.
5. **Fire OS notification center** (attempts 2, 6, 7; repair attempt 10).
   Documented behavior: standard notifications are reachable in the
   Notification Center under Settings > Notifications. Source: Amazon
   Fire TV developer docs, "Notifications" — standard notifications
   (https://developer.amazon.com/docs/fire-tv/notifications.html#standard-notifications).
   Procedure tested: first the Android shade shortcuts — `cmd statusbar
   expand-notifications` opens nothing on this leanback SystemUI
   (`attempt2-notif-center.png`), `KEYCODE_NOTIFICATION` on Home changes
   nothing (`evidence/visual/PRIVATE-EVIDENCE.md` (Fire TV home after KEYCODE_NOTIFICATION, withheld)), and a fresh post while Home is
   foreground does not peek (`evidence/visual/PRIVATE-EVIDENCE.md` (Fire TV home during a heads-up post, withheld)). Then the
   documented path itself, read-only: Settings grid → Notifications tile
   (badge "2", `repair10-notifications-tile.png`) →
   `com.amazon.tv.notificationcenter/.NotificationCenterActivity`.
   Observation: the center exists and shows one card for the spike app —
   but it presents the foreground-service notification ("SP2 spike
   service running"), not the alert, even though `dumpsys` shows the
   alert (`id=2002`, `actions=2`) still posted at that moment
   (`repair10-notification-center.png`). Selecting the card offers only
   the center's own Dismiss / Manage / Dismiss All buttons, not the
   alert's Watch/Dismiss actions (`repair10-center-card-actions.png`);
   none was pressed. So a customer-reachable surface exists, contrary to
   the first sweep's shortcut-only search, but it neither presents the
   alert nor exposes its actions.
   Outcome: **fails AFC-PR-015 (alert and its actions unreachable there)**.
6. **Toast fallback** (attempt 4; tried because heads-up failed).
   Documented behavior: a toast is a small non-interactive popup that
   takes no focus and carries no actions. Source: Android developer
   docs, "Toasts overview"
   (https://developer.android.com/guide/topics/ui/notifiers/toasts).
   Procedure tested: a long toast from the same foreground service
   during playback. Observation: it does render over Prime Video
   playback (`attempt4-toast.png`, bottom banner; ad timer and
   `state=3` continue), exactly as documented — display-only, so it
   cannot deliver Watch/Dismiss; at most it is an awareness hint.
   It is not selected as the AFC-PR-015 route.
   Outcome: **works as display-only; fails AFC-PR-015 (no actions)**.
7. **Action targets behind the (unreachable) actions** (attempt 6).
   Documented behavior: notification actions deliver their
   `PendingIntent` when the user presses them in the notification UI.
   Source: Android developer docs, "Create a notification" — actions
   (https://developer.android.com/develop/ui/views/notifications/build-notification#Actions).
   Procedure tested: with no UI surface presenting the actions, the
   PendingIntent targets were invoked directly over ADB. Observation:
   the Dismiss intent cancels the alert (`dumpsys` count of `id=2002`
   → 0; logcat `DISMISS pressed: alert cancelled`) and the Watch intent
   launches the spike activity (logcat `activity launched via=WATCH`;
   `attempt6-watch-target.png`). This proves the PendingIntent wiring,
   not a customer press through notification UI; it does not rescue
   the route.

## Observed result

Posting works; peeking never happens. On Fire OS 8.1.8.5 / API 30 the
leanback SystemUI accepts the third-party high-importance notification into
the notification manager (with both actions attached) but presents no
heads-up banner in any foreground context tried (own activity, Home,
full-screen Prime Video playback including its ad pre-roll), with or
without the documented `PRIORITY_HIGH` input or a full-screen intent.
The Notification Center under Settings > Notifications is reachable, but
it presents only the foreground-service notification and its own
Dismiss/Manage buttons — not the alert or its Watch/Dismiss actions.
Playback was never interrupted and the companion process was never
foregrounded by a post. DRM video captured black on its secure surface,
as in P2-X04; the player chrome (ad countdown) is the visible playback
evidence.

Within the 6 h SP-2 timebox (design table) this is a FAILS verdict on
evidence, not TIMEBOX.

## Limits

- One stick, one Fire OS build (8.1.8.5), one provider app version; a
  different Fire OS build could present heads-up differently.
- Not tried: `CATEGORY_CALL` / `CATEGORY_ALARM` variants of the
  full-screen-intent probe. They could only be a presentation-path
  diagnostic; neither is the intended sports-alert semantics, so neither
  could be the shipped route, and the `CATEGORY_EVENT` FSI probe already
  shows this build taking neither documented branch. Also not tried, by
  authority: any Settings change (e.g. per-app notification or DND
  settings, or the center's Manage button) — if a customer-side setting
  gates peeking on this build, enabling it is an owner decision, and no
  such gate was visible in `dumpsys`.
- The Vega contingency for this slice is `dispatchable=false` and was not
  probed; nothing here is Vega evidence.
- Sound audibility of the attempt-5B post was not assessed (no listener at
  the stick); the verdict rests on the absent visual banner.

## developer_feedback

- DX-SP2-01: Rebuilds under a different `ANDROID_USER_HOME` silently change
  the debug keystore; `adb install -r` then fails
  `INSTALL_FAILED_UPDATE_INCOMPATIBLE` (attempt 5) and the old APK keeps
  answering. Uninstall-then-install recovered (attempt 5B). Evidence:
  `evidence/visual/sp2-notify/attempts.txt`.
- DX-SP2-02: `dumpsys media_session` for `com.amazon.firebat` reports a
  frozen `updated` timestamp and `position=0` while playing; the ad
  countdown in screencaps is the reliable playback-progress signal.
