#!/bin/bash
# Phone side of device linking: confirm the code the TV shows for one profile. Runs on the workstation, not in the sandbox.
# usage: confirm-link.sh <base-url> <code> <profile-id> <evidence-dir>. Writes confirm.status and confirm.body (no token is returned).
set -u
B=$1 CODE=$2 PROFILE=$3 E=$4
mkdir -p "$E"
curl -sS -m 20 -o "$E/confirm.body" -w '%{http_code}\n' -X POST "${B%/}/v1/link/confirm" \
  -H 'content-type: application/json' --data "{\"code\":\"$CODE\",\"profileId\":\"$PROFILE\"}" > "$E/confirm.status"
cat "$E/confirm.status" "$E/confirm.body"; echo
grep -qx 200 "$E/confirm.status" && grep -q '"state": *"linked"' "$E/confirm.body"
