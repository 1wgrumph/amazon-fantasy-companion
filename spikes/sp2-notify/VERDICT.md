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
ended_at: 2026-10-16T19:46:55Z
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
directory (final APK sha256
`009f0b9fd52d03cfeea273b2052c037b2140e45c2fe594136e5020e86a3d3bf8`), installed
for the sweep and uninstalled after it. Full commands with exit codes,
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
   DPAD_UP reaches nothing (`attempt5-dpad-up.png`). `dumpsys notification`
   shows `headsUpContentView=null` for every record.
   Source: Android developer docs, "Heads-up notifications"
   (https://developer.android.com/develop/ui/views/notifications#Heads-up).
   Outcome: **fails (blocked by platform presentation)**.
3. **Fire OS notification center** (attempts 2, 6, 7). `cmd statusbar
   expand-notifications` opens nothing on this leanback SystemUI
   (`attempt2-notif-center.png`); `KEYCODE_NOTIFICATION` on Home changes
   nothing (`attempt6-notif-key.png`); the Home top bar exposes no
   notification entry, and a fresh post while Home is foreground also does
   not peek (`attempt7-home-headsup.png`). The posted notification is only
   visible via `dumpsys`, i.e. there is no customer-reachable surface on
   this stick where Watch/Dismiss could be pressed.
   Outcome: **fails (no reachable notification surface)**.
4. **Toast fallback** (attempt 4; tried because heads-up failed). A long
   toast from the same foreground service does render over Prime Video
   playback (`attempt4-toast.png`, bottom banner; ad timer and
   `state=3` continue). A toast takes no focus and carries no actions, so
   it cannot deliver Watch/Dismiss; at most it is an awareness hint.
   It is not selected as the AFC-PR-015 route.
   Outcome: **works as display-only; fails AFC-PR-015 (no actions)**.
5. **Action targets behind the (unreachable) actions** (attempt 6). With no
   UI surface to press them, the PendingIntent targets were verified
   directly: the Dismiss intent cancels the alert (`dumpsys` count of
   `id=2002` → 0; logcat `DISMISS pressed: alert cancelled`) and the Watch
   intent launches the spike activity (logcat `activity launched
   via=WATCH`; `attempt6-watch-target.png`). This proves the PendingIntent
   wiring, not a customer press; it does not rescue the route.

## Observed result

Posting works; peeking never happens. On Fire OS 8.1.8.5 / API 30 the
leanback SystemUI accepts the third-party high-importance notification into
the notification manager (with both actions attached) but presents no
heads-up banner in any foreground context tried (own activity, Home,
full-screen Prime Video playback including its ad pre-roll), and offers no
notification-center surface a customer could open instead. Playback was
never interrupted and the companion process was never foregrounded by a
post. DRM video captured black on its secure surface, as in P2-X04; the
player chrome (ad countdown) is the visible playback evidence.

Within the 6 h SP-2 timebox (design table) this is a FAILS verdict on
evidence, not TIMEBOX.

## Limits

- One stick, one Fire OS build (8.1.8.5), one provider app version; a
  different Fire OS build could present heads-up differently.
- Not tried, by authority or by construction: `setFullScreenIntent` (it
  foregrounds our activity, failing AFC-PR-015's "without foregrounding"
  by construction); any Settings change (e.g. per-app notification or
  DND settings) — if a customer-side setting gates peeking on this build,
  enabling it is an owner decision, and no such gate was visible in
  `dumpsys`.
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
