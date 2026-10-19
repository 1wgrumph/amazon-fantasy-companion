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

Viewing context: foreground was a system tutorial activity, not live
viewing; no provider app was launched, uninstalled, or cleared.

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
