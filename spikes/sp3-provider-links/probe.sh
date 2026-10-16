#!/usr/bin/env bash
# Spike probe: run one adb shell launch, record exit code, foreground activity
# and a screencap. Usage: ADB_SERIAL=<stick> probe.sh <name> <sleep_sec> -- <adb shell args...>
# The stick serial is deliberately not recorded in the log output.
set -u
ADB="${ADB:-adb}"
: "${ADB_SERIAL:?set ADB_SERIAL to the stick serial}"
NAME="$1"; SLEEP="$2"; shift 3
{
echo "=== $NAME $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "CMD: adb shell $*"
"$ADB" -s "$ADB_SERIAL" shell "$@"; echo "exit=$?"
sleep "$SLEEP"
"$ADB" -s "$ADB_SERIAL" shell dumpsys activity activities | grep -E "ResumedActivity|topResumedActivity" | head -4
} | tee "$NAME.log"
"$ADB" -s "$ADB_SERIAL" exec-out screencap -p > "$NAME.png"
echo "screencap_exit=$?" | tee -a "$NAME.log"
