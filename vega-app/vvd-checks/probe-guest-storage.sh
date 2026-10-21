#!/bin/bash
# Discovery only, not a feature check: where does the app keep AsyncStorage on the guest,
# and what does the app log at launch? Read-only guest commands; no network beyond the allowlist.
. "$(dirname "$0")/lib.sh" "$1"
vvd_start
app_install_launch
sleep 20
cap 00-app-after-launch
step guest-id vega device run-cmd -d "$DEV" --command "id; uname -a"
step guest-find vega device run-cmd -d "$DEV" --command "sh -c 'find / \( -path /proc -o -path /sys -o -path /dev \) -prune -o -iname \"*afc*companion*\" -print 2>/dev/null | head -60'"
logs probe
vvd_stop
