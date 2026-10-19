#!/usr/bin/env bash
# Offline APK build with already-admitted local SDK (spikes/sp1-device/toolchain-pins.txt). No downloads.
set -euo pipefail
cd "$(dirname "$0")"
export JAVA_HOME="${JAVA_HOME:-$HOME/.local/share/afc-tools/jdk-17.0.20.1+1}"
export ANDROID_HOME="${ANDROID_HOME:-$HOME/.local/share/afc-tools/android-sdk}"
BT="$ANDROID_HOME/build-tools/34.0.0"
JAR="$ANDROID_HOME/platforms/android-34/android.jar"
export PATH="$JAVA_HOME/bin:$BT:$PATH"
OUT=build; rm -rf "$OUT"; mkdir -p "$OUT/classes" "$OUT/dex"
javac -source 17 -target 17 -cp "$JAR" -d "$OUT/classes" $(find src/main/java -name '*.java')
"$BT/d8" --lib "$JAR" --min-api 25 --output "$OUT/dex" $(find "$OUT/classes" -name '*.class')
"$BT/aapt2" link -o "$OUT/probe-unsigned.apk" -I "$JAR" --manifest src/main/AndroidManifest.xml --min-sdk-version 25 --target-sdk-version 34
(cd "$OUT/dex" && zip -q "../probe-unsigned.apk" classes.dex)
"$BT/zipalign" -f 4 "$OUT/probe-unsigned.apk" "$OUT/probe-aligned.apk"
KS="${ANDROID_USER_HOME:-$HOME/.local/share/afc-tools/android-user}/debug.keystore"
[ -f "$KS" ] || KS="$HOME/.android/debug.keystore"
"$BT/apksigner" sign --ks "$KS" --ks-pass pass:android --key-pass pass:android --out "$OUT/sp7probe.apk" "$OUT/probe-aligned.apk"
"$BT/apksigner" verify --verbose --print-certs "$OUT/sp7probe.apk"
sha256sum "$OUT/sp7probe.apk"
"$BT/aapt2" dump badging "$OUT/sp7probe.apk" | head -n 20
