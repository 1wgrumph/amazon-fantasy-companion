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
started_at: 2026-10-16T12:19:17Z
ended_at: 2026-10-16T12:20:31Z
first_install_at: 2026-10-16T12:19:32Z
unblocks: [P2-X02, P2-X03, P2-X04, P2-X07, device installs of P2-A01..P2-A05]
conditional: none
---

# SP-1 device baseline verdict

## Routes tried

1. Network ADB (CMD-ADB-BASELINE): `adb connect <stick-ip>:5555`; RSA prompt accepted on the TV by
   the owner after matching the host key fingerprint; `adb devices` shows the stick as `device`.
   Source: Amazon Fire TV developer docs, "Connect to Fire TV Through ADB".
2. Install (CMD-ADB-INSTALL): `./gradlew --offline assembleDebug` in `spikes/sp1-device/starter`
   (pinned AmazonAppDev/hello-world-fire-tv @ 50108f4f), then `adb install -r`: "Success".
   APK sha256 621d097744944f9fa29d51014df1ab1ba0f2922937d70f50b8e74364f6d89329.
3. Launch: `adb shell monkey -p com.amazonappstore.helloworldtv -c android.intent.category.LAUNCHER 1`;
   `dumpsys activity` shows `com.amazonappstore.helloworldtv/.MainActivity` resumed.
4. Screenshot (CMD-ADB-SCREENCAP): `adb exec-out screencap -p`.

## Observed result

The starter installs and launches; its Movies grid renders at 1920x1080. Fire OS 8 / API 30 clears
RISK-AFC-P2-01 (Fire OS 5 or API < 25 would be a class C stop).

## Evidence

- `evidence/visual/sp1-device/starter-home.png` (1920x1080, starter placeholder content only).
- Toolchain: `toolchain-pins.txt`, `install-log.txt`, `scan-verdicts.txt`, `build-log.txt`.

## Limits

- The first screencap 4 s after launch was blank (app still drawing); the retake 8 s later is the evidence.
- Scan row 9 (Gradle build classpath) is owner-accepted residual risk (2026-10-16), not a PASS.
- OA-4 (Prime Video signed in) is owner-reported; this slice did not verify it on the device.
- Stick IP, serial and account data are deliberately not recorded.

## developer_feedback

none
