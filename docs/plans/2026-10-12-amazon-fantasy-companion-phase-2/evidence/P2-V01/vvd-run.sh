#!/bin/sh
# P2-V01 VVD qualification in ONE sandbox invocation: the wrapper's per-call
# bwrap (--die-with-parent, per-run /tmp) kills QEMU between separate calls.
# Run: vega-sandbox.sh <worktree> -- sh docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-V01/vvd-run.sh
EV=docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-V01
VIS=evidence/visual/P2-V01
VPKG=vega-app/build/x86_64-release/afc-companion_x86_64.vpkg
step() { printf '\n=== %s\n' "$1"; shift; "$@"; printf 'rc=%s\n' "$?"; }

step CMD-VVD-START vega virtual-device start --no-gui --no-gl-accel --timeout 300
step VVD-STATUS vega virtual-device status
step DEVICE-LIST vega device list
step CMD-VVD-INSTALL vega device install-app -p "$VPKG" --device VirtualDevice
step IS-INSTALLED vega device is-app-installed --device VirtualDevice --appName com.afc.companion.main
step LAUNCH vega device launch-app --device VirtualDevice --appName com.afc.companion.main
sleep 20
step IS-RUNNING vega device is-app-running --device VirtualDevice --appName com.afc.companion.main
step RUNNING-APPS vega device running-apps --device VirtualDevice
step CMD-VVD-INPUT-DOWN vega device shell -d VirtualDevice inputd-cli button_press KEY_DOWN
sleep 2
step CMD-VVD-INPUT-ENTER vega device shell -d VirtualDevice inputd-cli button_press KEY_ENTER
sleep 5
step IS-RUNNING-AFTER-INPUT vega device is-app-running --device VirtualDevice --appName com.afc.companion.main
step CMD-VVD-SCREENCAP-DEVICE vega device shell -d VirtualDevice gwsi-tool-screenshooter /tmp/link.png
step DEVICE-HELP vega device --help
step COPY-LOGS vega device copy-logs --device VirtualDevice --destination "$EV/vvd-logs"
step TERMINATE vega device terminate-app --device VirtualDevice --appName com.afc.companion.main
step VVD-STOP vega virtual-device stop
printf '\n=== DONE\n'
