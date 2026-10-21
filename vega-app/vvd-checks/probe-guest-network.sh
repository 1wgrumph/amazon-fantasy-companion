#!/bin/bash
# Discovery: how the VVD guest reaches the network from inside the sandbox (DNS, proxy settings, tools).
# The afc-dev host is on the proxy allowlist; a tokenless launch then sends POST /v1/link (authorized for Stage 2b).
. "$(dirname "$0")/lib.sh" "$1"
step vvd-start-help vega virtual-device start --help
vvd_start
H=le3r79003f.execute-api.us-east-2.amazonaws.com
for c in "id" "cat /etc/resolv.conf" "env" "getent hosts $H" "ls /usr/bin /bin" "ip route" "cat /etc/hosts"; do
  step "guest-$(echo "$c" | tr -c 'a-z0-9' '_' | cut -c1-24)" vega device run-cmd -d "$DEV" --command "$c"
done
app_install_launch
sleep 25 # Link request plus the 10 s api_timeout
cap 01-after-launch
logs probe
vvd_stop
true
