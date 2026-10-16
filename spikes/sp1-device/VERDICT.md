---
spike: SP-1
slice: P2-X01
verdict: WORKS
device:
  model: AFTKM
  fire_os: Fire OS 8.1.8.5 (RS8185/3891)
  android_release: "11"
  api_level: 30
  display: physical 3840x2160, override 1920x1080
started_at: 2026-10-14
ended_at: 2026-10-16T12:20:31Z
first_install_at: 2026-10-16T12:19:31Z
unblocks: [AFC-PR-052, AFC-PR-053, AC-AFC-P2-SPIKE-02, RISK-AFC-P2-01]
conditional: none
---

# SP-1 device baseline verdict

Device facts below are backed by `device-log.txt` (read-only re-capture during the PR #89
repair round, 2026-10-16; no install was repeated, so first-install data is unchanged).
Slice consumers unblocked by this verdict: P2-X02, P2-X03, P2-X04, P2-X07, and device
installs of P2-A01..P2-A05 (the `unblocks` field lists register UIDs per
CONTRACT-AFC-P2-VERDICT).

## Routes tried

1. Network ADB (CMD-ADB-BASELINE): `adb connect <stick>`; RSA prompt accepted on the TV by
   the owner after matching the host key fingerprint; `adb devices` shows the stick as
   `device` (device-log.txt:9-16).
   Source: Amazon Fire TV developer docs, "Connect to Fire TV Through ADB"
   (https://developer.amazon.com/docs/fire-tv/connecting-adb-to-device.html).
   Identity reads: model AFTKM (device-log.txt:22), Android 11 (device-log.txt:28),
   API 30 (device-log.txt:34), Fire OS 8.1.8.5 (RS8185/3891) via `ro.build.version.name`
   (device-log.txt:40), display physical 3840x2160 with override 1920x1080
   (device-log.txt:58-59).
2. Install (CMD-ADB-INSTALL): `./gradlew --offline assembleDebug` in `spikes/sp1-device/starter`
   (pinned AmazonAppDev/hello-world-fire-tv @ 50108f4f), then `adb install -r`: "Success".
   The installed base.apk hashes to the built APK's sha256
   621d097744944f9fa29d51014df1ab1ba0f2922937d70f50b8e74364f6d89329 (device-log.txt:86-88;
   build-log.txt:126-127,279), and `dumpsys package` reports
   firstInstallTime=2026-10-16 12:19:31 (device-log.txt:79).
   Source: Amazon Fire TV developer docs, "Install and Run Your App"
   (https://developer.amazon.com/docs/fire-tv/installing-and-running-your-app.html).
3. Launch: `adb shell monkey -p com.amazonappstore.helloworldtv -c android.intent.category.LAUNCHER 1`;
   `dumpsys activity` shows `com.amazonappstore.helloworldtv/.MainActivity` resumed.
   In the repair re-check monkey exited 251 without resuming the activity
   (device-log.txt:103-138); the launch was re-confirmed with `am start` and
   ResumedActivity = MainActivity (device-log.txt:158-168).
   Sources: Android developer docs, "UI/Application Exerciser Monkey"
   (https://developer.android.com/studio/test/other-testing-tools/monkey) and "Install and
   Run Your App" (`am start`, URL in route 2).
4. Screenshot (CMD-ADB-SCREENCAP): `adb exec-out screencap -p`.
   Source: Android developer docs, "Android Debug Bridge (adb)"
   (https://developer.android.com/tools/adb).

## Observed result

The starter installs and launches; its Movies grid renders at 1920x1080. Fire OS 8 / API 30 clears
RISK-AFC-P2-01 (Fire OS 5 or API < 25 would be a class C stop).

## Evidence

- `evidence/visual/sp1-device/starter-home.png` (1920x1080, starter placeholder content only).
- Device: `device-log.txt` (sanitized read-only re-capture, 2026-10-16T14:14Z).
- Toolchain: `toolchain-pins.txt`, `install-log.txt`, `scan-verdicts.txt`, `build-log.txt`.

## Limits

- Timebox (design.md:113) is 4 h of active spike work. Wall-clock span 2026-10-14 (part A
  host toolchain, first logged step install-log.txt:1; part A logs record the date only, so
  started_at is date-granular) to 2026-10-16T12:20:31Z (part B device session) exceeds 4 h
  because part B waited on owner device availability (OA-1/OA-4). The device session itself
  ran 12:19-12:20Z; no committed log totals part A's active duration, so exact active-time
  compliance is not measurable from the evidence (typed gap, not a pass claim).
- first_install_at follows the device: dumpsys reports 2026-10-16 12:19:31 with the stick on
  GMT (device-log.txt:79,93,99), i.e. 2026-10-16T12:19:31Z. This supersedes the original
  verdict's 12:19:32Z host `date -u` stamp taken at install success (1 s later).
- The original part B session's raw adb output was not committed; device-log.txt is a
  read-only re-capture. The install "Success" line itself is not in any committed log; the
  install is evidenced by dumpsys firstInstallTime plus the installed-APK hash match.
- The first screencap 4 s after launch was blank (app still drawing); the retake 8 s later is the evidence.
- Scan row 9 (Gradle build classpath) is owner-accepted residual risk (2026-10-16), not a PASS.
- OA-4 (Prime Video signed in) is owner-reported; this slice did not verify it on the device.
- Stick IP, serial and account data are deliberately not recorded.

## developer_feedback

none
