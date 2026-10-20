---
spike: SP-7
slice: P2-X07
verdict: PARTIAL
device:
  model: AFTKM
  fire_os: Fire OS 8.1.8.5
  android_release: "11"
  api_level: 30
  display: physical 3840x2160, override 1920x1080
started_at: 2026-10-19T11:04:00Z
ended_at: 2026-10-19T11:26:00Z
first_install_at: 2026-10-19T11:07:47Z
unblocks: [AFC-PR-003, AFC-PR-010, AC-AFC-P2-SPIKE-01]
conditional: null
---

# SP-7 installed-app detection verdict

**Verdict: PARTIAL.** Shell-level installed/absent detection works on this
stick, and leanback-launchability of the Prime Video package resolves. The
disabled-state probe is **unsupported from the ADB shell** on this Fire OS
build. Later in-app proof (see below) exercised `PackageManager` visibility
and own-package self-disable; the product still keeps detection hidden
behind `detectionSupported = false` and no product activation follows.

Probes (full sanitized record: `evidence/visual/sp7-detection/commands.txt`):

- Installed: `pm path` returned a package path for `com.amazon.firebat`
  (Prime Video), `com.netflix.ninja`, and `com.afc.companion` (after install).
- Absent: `pm path` returned nothing (exit 1) for
  `com.amazon.avod.thirdpartyclient`, `com.google.android.youtube.tv`,
  `com.espn.score_center`, `com.disney.disneyplus`, `tv.sling.airtv`,
  `com.hulu.livingroomplus`, `com.cbs.ott`, `com.foxsports.videogo`,
  `com.nfl.android.tv`, and control `com.example.absent.afcprobe`.
- Leanback resolution: `cmd package resolve-activity` for MAIN +
  LEANBACK_LAUNCHER on `com.amazon.firebat` resolved its ignition activity.
  URI/intent resolution is not entitlement, launch, or game-arrival proof.
- Disabled: `pm disable com.netflix.ninja` failed with
  `SecurityException: Shell cannot change component state` — the shell
  cannot create a disabled state on this build, so detection-of-disabled
  could not be exercised. No state changed; a following `pm enable` set
  explicit enabled, and `pm default-state` restored the original
  `enabled=0` (default) setting, verified by `dumpsys package`.

Viewing context (2026-10-19 probes): foreground was a system tutorial
activity, not live viewing; no provider app was launched, uninstalled,
or cleared. The bounded current-viewing-context read below
(2026-10-20) closes that open question.

Later in-app proof (R-T-DEVICE-1 completion, exact APK
`ad9b04355e79c44bb2fcddca539c226b12606c5a9a2a3a101c0d2320060ea880`):
in-app `PackageManager` probe reported installed-enabled, absent, and —
after the disposable own fixture package self-disabled via
`setApplicationEnabledSetting` (`enabled=2`) — installed-disabled. No
provider package was disabled or mutated; both probe/fixture packages
were removed and verified absent.

Honest labels: installed/absent detection **supported** (shell route);
disabled-state creation **unsupported via shell** on this build, but
disabled-state detection **supported in-app** via the own-package
self-disable proof above; in-app `PackageManager` visibility under the
manifest `<queries>` leanback intent **exercised** by that later proof.
The companion UI correctly keeps the detection control hidden
(`detectionSupported = false`) with its stated limit; no product
activation is claimed.

Current-viewing-context read (2026-10-20, issue #26 remaining proof;
full sanitized record:
`evidence/visual/sp7-detection/viewing-context.txt`): Prime Video
(`com.amazon.firebat`) was foregrounded to its home screen on the same
stick (explicit component launch; `monkey` and the leanback-intent
launch did not foreground it) and returned to home afterward. No
playback was started and no account, provider, or profile state
changed. **No supported app-callable API exposes current viewing
context (what title, channel, or game is being watched) to the
companion on this build; viewing context stays unsupported/unknown
and `detectionSupported = false` is unchanged.** Per API checked:

| API | App-callable by the companion? | Result |
|-----|-------------------------------|--------|
| `dumpsys activity` ResumedActivity (shell) | No — shell diagnosis only | Foreground package/activity visible (`firebat/IgnitionActivity`); no viewing title or game. |
| `ActivityManager.getRunningTasks` | No — own tasks only since API 21 | Cannot report another app's foreground task; not a viewing-context route. |
| `dumpsys media_session` (shell) | No — shell diagnosis only | `firebat` session `active=true`, `state=0` (STATE_NONE), `metadata: null` on the Prime Video home; no title/channel/event. |
| `MediaSessionManager.getActiveSessions` | No — needs an enabled NotificationListenerService or `MEDIA_CONTENT_CONTROL` | `enabled_notification_listeners` is `null`; the companion has no such grant. |
| `dumpsys usagestats` (shell) | No — shell diagnosis only | `ACTIVITY_RESUMED` events give package/class/time only; no title/game/channel. |
| `UsageStatsManager` (`PACKAGE_USAGE_STATS`) | No — usage-access app-op not granted | `cmd appops get com.afc.companion android:get_usage_stats` returned no operations, default mode. Even granted, it reports foreground package/class, not what is being watched. |

Shell `dumpsys` visibility is a diagnosis route, not product support:
nothing above lets the shipped app learn the current viewing context,
so no detection or viewing-context activation follows.

## developer_feedback

- DX-SP7-01: The ADB shell cannot create a disabled package state on
  this Fire OS build: `pm disable com.netflix.ninja` fails with
  `SecurityException: Shell cannot change component state` (finding
  COMP-2), so disabled-state detection cannot be exercised from the
  shell; the in-app own-package self-disable route above is the
  workaround. Tools: `adb shell pm disable/enable/default-state`,
  `dumpsys package`. Evidence:
  `evidence/visual/sp7-detection/commands.txt`.
- DX-SP7-02: Foregrounding Prime Video from the shell needs the
  explicit component (`am start -n
  com.amazon.firebat/com.amazon.pyrocore.IgnitionActivity`);
  `monkey -p … -c LEANBACK_LAUNCHER` exited 251 and the MAIN +
  LEANBACK_LAUNCHER intent did not resolve, both leaving the launcher
  foreground. Tools: `adb shell am/monkey`, `dumpsys activity`.
  Evidence: `evidence/visual/sp7-detection/viewing-context.txt`.
