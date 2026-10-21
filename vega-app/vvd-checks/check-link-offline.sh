#!/bin/bash
# Device linking, tokenless launch with the afc-dev host NOT on the proxy allowlist.
# A tokenless launch POSTs /v1/link (a backend write); blocking the host keeps that write off afc-dev.
# Expect: the Link screen, "Requesting a code…", then the network-error message and a focused Get code button;
# Get code (KEY_ENTER) retries and fails the same way.
. "$(dirname "$0")/lib.sh" "$1"
vvd_start
cap 00-vvd-home
app_install_launch
sleep 4
cap 01-link-requesting
sleep 16 # api_timeout is 10 s
cap 02-link-network-error
step app-running vega device is-app-running -d "$DEV" -a "$APP"
key 03 ENTER 2
cap 03-link-after-get-code
sleep 14
cap 04-link-error-again
logs link
vvd_stop
cap 05-after-stop
# Exit 0 only when every step exited 0; verify-link-offline.py then checks the captured states.
! grep -qv "=0$" "$E/steps.txt"
