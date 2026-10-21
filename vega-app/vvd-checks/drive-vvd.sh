#!/bin/bash
# Remote-driven VVD session for the online features (Stage 2c). Starts the VVD, installs and launches the app, then runs
# the lines appended to <evidence-dir>/commands.txt, one per line:
#   key NAME [SECONDS] | cap NAME | log NAME | sleep SECONDS | relaunch | panel | end
# "panel" scrolls below Save profile, then captures twice and logs; verify with verify-panel-default.py on the host.
# Each executed line goes to done.txt. Ends on "end" or after 600 s without a new line, then stops the VVD.
. "$(dirname "$0")/lib.sh" "$1"
vvd_start
app_install_launch
n=0 idle=0
while [ "$idle" -lt 600 ]; do
  line=$(sed -n "$((n + 1))p" "$E/commands.txt" 2>/dev/null)
  if [ -z "$line" ]; then sleep 1; idle=$((idle + 1)); continue; fi
  n=$((n + 1)) idle=0
  read -r verb arg extra <<< "$line"
  case $verb in
    key) key "$n" "$arg" "${extra:-3}" ;;
    cap) cap "$arg" ;;
    log) logs "$arg" ;;
    sleep) sleep "$arg" ;;
    panel)
      key "panel-$n" PAGEDOWN 2
      cap panel-default
      sleep 10
      cap panel-default-held
      logs panel-default ;;
    relaunch)
      step "terminate-$n" vega device terminate-app -d "$DEV" -a "$APP"
      sleep 2
      step "launch-$n" vega device launch-app -d "$DEV" -a "$APP" ;;
    end) echo "$n $line" >> "$E/done.txt"; break ;;
    *) echo "unknown command: $line" >&2 ;;
  esac
  echo "$n $line" >> "$E/done.txt"
done
vvd_stop
# Exit 0 only when every step exited 0.
! grep -qv "=0$" "$E/steps.txt"
