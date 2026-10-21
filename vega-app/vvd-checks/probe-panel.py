#!/usr/bin/env python3
"""Links one profile from the workstation and records GET /v1/profile and GET /v1/panel as the app calls them.
usage: probe-panel.py <base-url> <profile-id> <out-dir>
The session token and polling handle stay in process memory; written bodies drop them and redact token-like strings."""
import json, re, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

base, profile_id, out = sys.argv[1].rstrip('/'), sys.argv[2], Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
SECRET_KEYS = {'sessionToken', 'handle'}
TOKENISH = re.compile(r'[A-Za-z0-9_-]{32,}')


def call(method, path, body=None, token=None):
    headers = {'Accept': 'application/json'}
    if token is not None:
        headers['Authorization'] = 'Bearer ' + token
    data = None if body is None else json.dumps(body).encode()
    if data is not None:
        headers['Content-Type'] = 'application/json'
    request = urllib.request.Request(base + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read() or b'null')
    except urllib.error.HTTPError as error:
        raw = error.read()
        try:
            return error.code, json.loads(raw or b'null')
        except ValueError:
            return error.code, {'nonJsonBody': len(raw)}


def redact(value):
    if isinstance(value, dict):
        return {k: ('<redacted>' if k in SECRET_KEYS else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return TOKENISH.sub('<redacted>', value)
    return value


def record(name, status, body):
    (out / f'{name}.status').write_text(f'{status}\n')
    (out / f'{name}.json').write_text(json.dumps(redact(body), indent=2, sort_keys=True) + '\n')
    print(name, status)


status, issued = call('POST', '/v1/link')
record('01-link', status, issued)
code, handle = issued['code'], issued['handle']
status, confirmed = call('POST', '/v1/link/confirm', {'code': code, 'profileId': profile_id})
record('02-link-confirm', status, confirmed)
token = None
for _ in range(10):
    status, polled = call('GET', '/v1/link?handle=' + urllib.parse.quote(handle, safe=''))
    if polled.get('state') == 'linked':
        token = polled.get('sessionToken')
        break
    time.sleep(2)
record('03-link-poll', status, polled)
if not token:
    sys.exit('no session token from the link poll')

status, profile = call('GET', '/v1/profile', token=token)
record('04-profile', status, profile)
# App.tsx sends no teamLeague when the controller's team/league is '' (no saved teamLeague, no selections).
status, panel = call('GET', '/v1/panel', token=token)
record('05-panel-no-teamleague', status, panel)
# The value the backend picks for this profile, sent explicitly, as the app would after a team/league switch.
team_league = (panel.get('data') or {}).get('teamLeague') if isinstance(panel, dict) else None
if team_league:
    status, explicit = call('GET', '/v1/panel?teamLeague=' + urllib.parse.quote(team_league, safe=''), token=token)
    record('06-panel-teamleague-explicit', status, explicit)
