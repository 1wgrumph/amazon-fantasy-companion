#!/bin/sh
# P2-V01 VVD qualification, attempt 3: exact c16 lifecycle shape (cwd in the
# preparation worktree, --gl-accel) which booted running:true twice at
# 10:53/10:56 UTC, plus install/launch/input/capture for this slice.
W=$HOME/alphazede/worktrees/amazon-fantasy-companion-p2-v01
EV=$W/docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-V01
VIS=$W/evidence/visual/P2-V01
VPKG=$W/vega-app/build/x86_64-release/afc-companion_x86_64.vpkg
APP=com.afc.companion.main
step() { printf '\n=== %s\n' "$1"; shift; "$@"; rc=$?; printf 'rc=%s\n' "$rc"; return "$rc"; }

cd "$HOME/preparation-worktree" || exit 90
step CMD-VVD-START vega virtual-device start --timeout 240 --no-gui --gl-accel
step VVD-STATUS vega virtual-device status
step DEVICE-LIST vega device list
step CMD-VVD-INSTALL vega device install-app -p "$VPKG" --device VirtualDevice
step IS-INSTALLED vega device is-app-installed --device VirtualDevice --appName "$APP"
step LAUNCH vega device launch-app --device VirtualDevice --appName "$APP"
sleep 12
step IS-RUNNING vega device is-app-running --device VirtualDevice --appName "$APP"
step CMD-VVD-SCREENCAP-LINK vega device run-cmd -d VirtualDevice --command 'gwsi-tool-screenshooter /tmp/link.png'
step SCREENCAP-COPY-LINK vega device copy-from -d VirtualDevice --source /tmp/link.png --destination "$VIS/link.png"
step CMD-VVD-INPUT-DOWN vega device run-cmd -d VirtualDevice --command 'inputd-cli button_press KEY_DOWN'
sleep 2
step CMD-VVD-INPUT-ENTER vega device run-cmd -d VirtualDevice --command 'inputd-cli button_press KEY_ENTER'
sleep 4
step IS-RUNNING-AFTER-INPUT vega device is-app-running --device VirtualDevice --appName "$APP"
step CMD-VVD-SCREENCAP-AFTER-INPUT vega device run-cmd -d VirtualDevice --command 'gwsi-tool-screenshooter /tmp/link-after-input.png'
step SCREENCAP-COPY-AFTER-INPUT vega device copy-from -d VirtualDevice --source /tmp/link-after-input.png --destination "$VIS/link-after-input.png"
mkdir -p "$EV/vvd-logs"
step COPY-LOGS vega device copy-logs --device VirtualDevice --artifact system/var_log --directory "$EV/vvd-logs"
step TERMINATE vega device terminate-app --device VirtualDevice --appName "$APP"
step VVD-STOP vega virtual-device stop
printf '\n=== DONE\n'
