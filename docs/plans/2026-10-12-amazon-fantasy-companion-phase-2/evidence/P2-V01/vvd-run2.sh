#!/bin/sh
# P2-V01 VVD qualification, attempt 2. Attempt 1 never booted: QEMU exited with
# "A snapshot operation for '<build>' is pending" (virtual_device.err) after an
# earlier start was killed without a stop. This run stops first, mirrors the
# prior successful c16 lifecycle flags (--gl-accel), and fits the sandbox
# 300-second wall limit. One wrapper invocation only (per-call bwrap kills QEMU).
EV=docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-V01
VIS=evidence/visual/P2-V01
VPKG=vega-app/build/x86_64-release/afc-companion_x86_64.vpkg
APP=com.afc.companion.main
step() { printf '\n=== %s\n' "$1"; shift; "$@"; rc=$?; printf 'rc=%s\n' "$rc"; return "$rc"; }

step PRE-STOP vega virtual-device stop
step CMD-VVD-START vega virtual-device start --no-gui --gl-accel --timeout 180 || { step VVD-STOP-AFTER-START-FAIL vega virtual-device stop; printf '\n=== DONE START_FAILED\n'; exit 0; }
step VVD-STATUS vega virtual-device status
step DEVICE-LIST vega device list
step CMD-VVD-INSTALL vega device install-app -p "$VPKG" --device VirtualDevice
step IS-INSTALLED vega device is-app-installed --device VirtualDevice --appName "$APP"
step LAUNCH vega device launch-app --device VirtualDevice --appName "$APP"
sleep 15
step IS-RUNNING vega device is-app-running --device VirtualDevice --appName "$APP"
step CMD-VVD-SCREENCAP-LINK vega device run-cmd -d VirtualDevice --command 'gwsi-tool-screenshooter /tmp/link.png'
step SCREENCAP-COPY-LINK vega device copy-from -d VirtualDevice --source /tmp/link.png --destination "$VIS/link.png"
step HOST-SCREENCAP-HELPER /home/spectre/.local/share/afc-tools/vvd-screencap.sh
step CMD-VVD-INPUT-DOWN vega device run-cmd -d VirtualDevice --command 'inputd-cli button_press KEY_DOWN'
sleep 2
step CMD-VVD-INPUT-ENTER vega device run-cmd -d VirtualDevice --command 'inputd-cli button_press KEY_ENTER'
sleep 5
step IS-RUNNING-AFTER-INPUT vega device is-app-running --device VirtualDevice --appName "$APP"
step CMD-VVD-SCREENCAP-AFTER-INPUT vega device run-cmd -d VirtualDevice --command 'gwsi-tool-screenshooter /tmp/link-after-input.png'
step SCREENCAP-COPY-AFTER-INPUT vega device copy-from -d VirtualDevice --source /tmp/link-after-input.png --destination "$VIS/link-after-input.png"
step COPY-LOGS vega device copy-logs --device VirtualDevice --artifact system/var_log --directory "$EV/vvd-logs"
step TERMINATE vega device terminate-app --device VirtualDevice --appName "$APP"
step VVD-STOP vega virtual-device stop
printf '\n=== DONE\n'
