#!/bin/bash
# Stage 3 workstation side: link a session for one synthetic profile, write its manual NBA lineup and point the
# profile's panel at that team/league. Runs on the workstation, not in the sandbox.
# usage: put-lineup.sh <base-url> <profile-id> <lineup.json> <league/team> <evidence-dir> <private-dir> [alert-types]
# [alert-types] is an optional comma list (Stage 4: RedZone,PlayerScore) written as the profile's alertTypes.
# The session token stays in <private-dir>/session (mode 600) and is never printed. Evidence gets status codes and bodies.
set -u
B=${1%/} PROFILE=$2 LINEUP=$3 PAIR=$4 E=$5 P=$6 TYPES=${7:-}
mkdir -p "$E" "$P"
umask 077
api() { # api NAME METHOD PATH [BODY-FILE] : status to NAME.status, body to NAME.json
  local auth=() data=()
  [ -s "$P/session" ] && auth=(-H "authorization: Bearer $(cat "$P/session")")
  [ $# -ge 4 ] && data=(-H 'content-type: application/json' --data-binary "@$4")
  curl -sS -m 30 -o "$E/$1.json" -w '%{http_code}\n' -X "$2" "${auth[@]}" "${data[@]}" "$B$3" > "$E/$1.status"
  echo "$1 $2 $3 $(cat "$E/$1.status")"
}
if [ ! -s "$P/session" ]; then
  api 01-link POST /v1/link
  code=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["code"])' "$E/01-link.json")
  python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["handle"])' "$E/01-link.json" > "$P/handle"
  # The handle is a polling secret: keep it private and drop it from the evidence body.
  python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));d["handle"]="<redacted>";json.dump(d,open(sys.argv[1],"w"))' "$E/01-link.json"
  "$(dirname "$0")/confirm-link.sh" "$B" "$code" "$PROFILE" "$E/02-confirm" > /dev/null || exit 2
  curl -sS -m 30 -o "$P/poll.json" -w '%{http_code}\n' "$B/v1/link?handle=$(cat "$P/handle")" > "$E/03-poll.status"
  python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));assert d["state"]=="linked";print(d["sessionToken"])' \
    "$P/poll.json" > "$P/session" || exit 3
  rm -f "$P/poll.json" "$P/handle"
  echo "03-poll GET /v1/link $(cat "$E/03-poll.status") (token kept private)"
fi
api 04-lineup PUT /v1/lineup/manual "$LINEUP"
api 05-profile-before GET /v1/profile
python3 - "$E/05-profile-before.json" "$PAIR" "$P/profile-put.json" "$TYPES" <<'EOF'
import json, sys
profile, pair, out, types = json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3], sys.argv[4]
league, team = pair.split("/", 1)
data = dict(profile["data"], teamLeague={"league": league, "team": team})
if types:
    data["alertTypes"] = types.split(",")
json.dump({"revision": profile["revision"], "data": data}, open(out, "w"))
EOF
api 06-profile PUT /v1/profile "$P/profile-put.json"
api 07-panel GET "/v1/panel?teamLeague=$PAIR"
grep -qx 200 "$E/04-lineup.status" && grep -qx 200 "$E/06-profile.status" && grep -qx 200 "$E/07-panel.status"
