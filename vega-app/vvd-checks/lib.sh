#!/bin/bash
# Shared steps for the on-VVD checks. Runs inside the Vega sandbox only (run.py <work> -- bash <check> <evidence-dir>).
# Every step writes <name>.stdout/.stderr/.exit into the evidence dir; a failed step is recorded, not fatal.
set -u
E=$1
APP=com.afc.companion.main
DEV=VirtualDevice
mkdir -p "$E" && cd "$E" || exit 90
step() { # step NAME CMD... : run, record exit
  local n=$1; shift
  "$@" > "$E/$n.stdout" 2> "$E/$n.stderr"
  local rc=$?
  printf '%s=%s\n' "$n" "$rc" | tee -a "$E/steps.txt"
  return $rc
}
cap() { # cap NAME : X root window of the VVD display, converted to PNG on the host afterwards
  step "cap-$1" xwd -root -silent -display "${DISPLAY:-:91}" -out "$E/$1.xwd"
}
key() { step "key-$1-$2" vega device run-cmd -d "$DEV" --command "inputd-cli button_press KEY_$2"; sleep "${3:-3}"; }
vvd_start() {
  # Stale AVD locks hold a pid that a new pid namespace may reuse (Stage 1 friction).
  rm -f "$HOME"/vega/sdk/*/vvd/instances/*/hardware-qemu.ini.lock "$HOME"/vega/sdk/*/vvd/instances/*/multiinstance.lock
  export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
  step vvd-start vega virtual-device start --timeout 600
  step vvd-status-start vega virtual-device status
  sleep 12 # "ready" is printed while the splash is still up; input during it kills the device.
}
app_install_launch() {
  step app-install vega device install-app -d "$DEV" -p "$E/../afc-companion_x86_64.vpkg"
  step app-installed vega device is-app-installed -d "$DEV" -a "$APP"
  step app-launch vega device launch-app -d "$DEV" -a "$APP"
}
logs() { # guest log excerpt for the app package; the dev shell rejects journalctl
  step "log-$1" vega device run-cmd -d "$DEV" --command "loggingctl log -o short_precise -v com.afc.companion"
}
vvd_stop() {
  step app-running-end vega device is-app-running -d "$DEV" -a "$APP"
  step app-terminate vega device terminate-app -d "$DEV" -a "$APP"
  step vvd-status-before-stop vega virtual-device status
  step vvd-stop vega virtual-device stop
  step vvd-status-after-stop vega virtual-device status
}
