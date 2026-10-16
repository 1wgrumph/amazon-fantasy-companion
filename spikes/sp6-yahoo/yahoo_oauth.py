#!/usr/bin/env python3
"""SP-6 Yahoo OAuth spike helper (P2-X06).

Subcommands:
  url       print the Yahoo request_auth URL (no secret needed)
  exchange  prompt for the authorization code, exchange it, store the
            refresh token in SSM /afc/dev/yahoo-token, print "stored"
  read      refresh an access token in memory and read leagues, teams,
            current-week roster and league settings through
            backend/src/lineup/yahoo.py; writes redacted evidence only

Secrets (client secret, code, access/refresh tokens) live in process
memory only: never printed, logged or written to a file. The refresh
token's only destination is the SSM SecureString parameter.
Stdlib + boto3 only. Sources: Yahoo OAuth 2.0 guide
(developer.yahoo.com/oauth2/guide/) and Yahoo Fantasy Sports API docs.
"""

import base64
import getpass
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
REDIRECT_URI = "https://localhost/link"
CAPTURE_PORT = 8443
CAPTURE_REDIRECT_URI = f"https://localhost:{CAPTURE_PORT}/link"
PROFILE = "afc-dev"
REGION = "us-east-2"
CLIENT_ID_PARAM = "/afc/dev/yahoo-client-id"
CLIENT_SECRET_PARAM = "/afc/dev/yahoo-client-secret"
TOKEN_PARAM = "/afc/dev/yahoo-token"
HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_PATH = os.path.join(HERE, "evidence", "read-result.json")
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
SECRET_WORDS = ("token", "secret", "code", "authorization", "password",
                "email", "guid", "xoauth")


class HttpError(Exception):
    def __init__(self, status, what):
        super().__init__(f"{what} HTTP {status}")
        self.status = status


def build_auth_url(client_id, redirect_uri=REDIRECT_URI):
    # fspt-r is Fantasy Sports read. A 403 "This application is not
    # authorized" after a 200 token refresh is Yahoo's API access program
    # (VERDICT.md), not a missing scope.
    query = urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "fspt-r",
    })
    return f"{AUTH_URL}?{query}"


def extract_code(text):
    """Accept a bare code or the full failing redirect URL the owner copies."""
    text = text.strip()
    if "code=" in text:
        parsed = urllib.parse.urlparse(text)
        values = urllib.parse.parse_qs(parsed.query).get("code")
        if values:
            return values[0]
    return text


def redact(value):
    """Drop any dict key that could carry a secret or account identifier."""
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()
                if not any(word in str(k).lower() for word in SECRET_WORDS)}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def _ssm():
    import boto3  # local import: url subcommand runs without boto3
    session = boto3.session.Session(profile_name=PROFILE, region_name=REGION)
    if session.get_credentials() is None:
        # `aws login` (login_session) profiles are invisible to boto3; bridge
        # them in memory via the CLI. Credentials are never printed or stored.
        import subprocess
        exported = subprocess.run(
            ["aws", "configure", "export-credentials", "--profile", PROFILE,
             "--format", "process"], capture_output=True, text=True, check=True)
        creds = json.loads(exported.stdout)
        session = boto3.session.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds.get("SessionToken"), region_name=REGION)
    return session.client("ssm")


def ssm_get(name):
    return _ssm().get_parameter(Name=name, WithDecryption=True)["Parameter"]["Value"]


def ssm_put_token(value):
    _ssm().put_parameter(Name=TOKEN_PARAM, Value=value,
                         Type="SecureString", Overwrite=True)


def _token_post(client_id, client_secret, fields, what):
    body = urllib.parse.urlencode(fields).encode()
    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    request = urllib.request.Request(
        TOKEN_URL, data=body, method="POST",
        headers={"Authorization": "Basic " + basic,
                 "Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        try:  # Yahoo's error name/description carry no secret; never echo the body itself
            info = json.loads(error.read().decode())
            print(f"{what}: {info.get('error')}: {info.get('error_description')}", file=sys.stderr)
        except (ValueError, AttributeError):
            pass
        raise HttpError(error.code, what) from None


# --- Yahoo Fantasy JSON -> the flat shapes backend/src/lineup/yahoo.py validates

def _walk(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _merged(value):
    """Yahoo encodes team/player records as lists of single-key dicts."""
    if isinstance(value, dict):
        return value
    merged = {}
    if isinstance(value, list):
        for item in value:
            merged.update(_merged(item))
    return merged


def _records(raw, key):
    """All records under any `key:` node, merged from Yahoo list encoding."""
    found = []
    for node in _walk(raw):
        if isinstance(node, dict) and key in node:
            record = _merged(node[key])
            if record:
                found.append(record)
    return found


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_leagues(raw):
    leagues = []
    for record in _records(raw, "league"):
        if "league_key" in record and "name" in record:
            leagues.append({"league_key": str(record["league_key"]),
                            "name": str(record["name"]),
                            "season": _int(record.get("season"))})
    return {"leagues": leagues}


def normalize_teams(raw):
    teams = []
    for record in _records(raw, "team"):
        if "team_key" in record and "name" in record:
            teams.append({"team_key": str(record["team_key"]),
                          "name": str(record["name"])})
    return {"teams": teams}


def normalize_roster(raw, team_key, week):
    players = []
    for node in _walk(raw):
        if not (isinstance(node, dict) and isinstance(node.get("player"), list)):
            continue
        parts = node["player"]
        record = _merged(parts[0]) if parts else {}
        if "player_key" not in record:
            continue
        name = record.get("name")
        selected = {}
        for part in parts[1:]:
            if isinstance(part, dict) and "selected_position" in part:
                selected = _merged(part["selected_position"])
        positions = [str(item["position"])
                     for item in record.get("eligible_positions", [])
                     if isinstance(item, dict) and "position" in item]
        players.append({
            "player_key": str(record["player_key"]),
            "name": str(name.get("full") if isinstance(name, dict) else name or ""),
            "team": str(record.get("editorial_team_abbr", "")),
            "positions": positions,
            "slot": str(selected.get("position", "")),
        })
    return {"team_key": team_key, "week": week, "players": players}


def normalize_settings(raw, league_key):
    modifiers, slots = {}, []
    for node in _walk(raw):
        if not isinstance(node, dict):
            continue
        stats = node.get("stat_modifiers", {})
        stats = stats.get("stats", []) if isinstance(stats, dict) else []
        for entry in stats if isinstance(stats, list) else []:
            stat = entry.get("stat", {}) if isinstance(entry, dict) else {}
            if "stat_id" in stat:
                try:
                    modifiers[str(stat["stat_id"])] = float(stat.get("value", 0))
                except (TypeError, ValueError):
                    modifiers[str(stat["stat_id"])] = 0.0
        for entry in node.get("roster_positions", []) or []:
            position = entry.get("roster_position", {}) if isinstance(entry, dict) else {}
            if "position" in position:
                slots.extend([str(position["position"])] *
                             max(1, _int(position.get("count"), 1)))
    return {"league_key": league_key, "stat_modifiers": modifiers,
            "roster_slots": slots}


def current_week_from(raw):
    for record in _records(raw, "league"):
        week = _int(record.get("current_week"))
        if week >= 1:
            return week
    return None


def owned_team_key(raw):
    for record in _records(raw, "team"):
        if _int(record.get("is_owned_by_current_login")) == 1 and "team_key" in record:
            return str(record["team_key"])
    return None


def fallback_week(today=None):
    today = today or date.today()
    # 2026 NFL Week 1 kicked off the week of 2026-09-07 (Mon-Sun weeks).
    return min(18, max(1, (today - date(2026, 9, 7)).days // 7 + 1))


class YahooTransport:
    """request(method, url, headers) -> flat JSON for lineup/yahoo.py."""

    def __init__(self):
        self.statuses = []
        self.last_raw = None

    def request(self, method, url, headers):
        separator = "&" if "?" in url else "?"
        request = urllib.request.Request(f"{url}{separator}format=json",
                                         method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                status, raw = response.status, json.loads(response.read().decode())
        except urllib.error.HTTPError as error:
            self.statuses.append(error.code)
            raise HttpError(error.code, "Yahoo Fantasy API") from None
        self.statuses.append(status)
        self.last_raw = raw
        return self._normalize(url, raw)

    @staticmethod
    def _normalize(url, raw):
        if url.endswith("/leagues"):
            return normalize_leagues(raw)
        if url.endswith("/teams"):
            return normalize_teams(raw)
        roster = re.search(r"/team/([^/]+)/roster;week=(\d+)$", url)
        if roster:
            return normalize_roster(raw, roster.group(1), int(roster.group(2)))
        settings = re.search(r"/league/([^/]+)/settings$", url)
        if settings:
            return normalize_settings(raw, settings.group(1))
        raise ValueError(f"unrecognized Yahoo path: {url.rsplit('/', 1)[-1]}")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_url():
    print(build_auth_url(ssm_get(CLIENT_ID_PARAM).strip()))
    return 0


def _exchange_and_store(code, redirect_uri):
    status, payload = _token_post(
        ssm_get(CLIENT_ID_PARAM).strip(), ssm_get(CLIENT_SECRET_PARAM).strip(),
        {"grant_type": "authorization_code", "code": code,
         "redirect_uri": redirect_uri}, "token exchange")
    refresh = payload.get("refresh_token")
    if status != 200 or not isinstance(refresh, str) or not refresh:
        print(f"exchange failed: HTTP {status}, no refresh token", file=sys.stderr)
        return 1
    ssm_put_token(refresh)
    print("stored")
    return 0


def cmd_capture():
    """Catch the redirect on https://localhost:8443/link so nobody copies the code.

    shortcut: throwaway self-signed cert; the browser warns once (Advanced ->
    Proceed). Upgrade to the deployed /link callback when the backend owns OAuth.
    """
    import http.server
    import ssl
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        cert, key = os.path.join(tmp, "c.pem"), os.path.join(tmp, "k.pem")
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                        "-keyout", key, "-out", cert, "-days", "1", "-subj", "/CN=localhost"],
                       check=True, capture_output=True)
        got = {}

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                query = urllib.parse.urlparse(self.path).query
                got["code"] = (urllib.parse.parse_qs(query).get("code") or [""])[0]
                got["error"] = (urllib.parse.parse_qs(query).get("error") or [""])[0]
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"AFC: Yahoo approval received. You can close this tab.")

            def log_message(self, *args):  # never log the request line (it holds the code)
                pass

        server = http.server.HTTPServer(("127.0.0.1", CAPTURE_PORT), Handler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, key)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        print("Open this URL, approve, then click Advanced -> Proceed on the certificate warning:")
        print(build_auth_url(ssm_get(CLIENT_ID_PARAM).strip(), CAPTURE_REDIRECT_URI), flush=True)
        while not got.get("code") and not got.get("error"):
            try:
                server.handle_request()
            except ssl.SSLError:
                continue  # the browser's first, rejected TLS attempt
        server.server_close()
    if not got.get("code"):
        print(f"no code: {got.get('error')}", file=sys.stderr)
        return 2
    return _exchange_and_store(got["code"], CAPTURE_REDIRECT_URI)


def cmd_setup():
    """Owner pastes the app's Client ID and Secret (hidden), both go to SSM, then capture."""
    client_id = getpass.getpass("Client ID (hidden, Ctrl+Shift+V then Enter): ").strip()
    secret = getpass.getpass("Client Secret (hidden, Ctrl+Shift+V then Enter): ").strip()
    if len(client_id) < 40 or len(secret) < 20:
        print(f"looks wrong: client id {len(client_id)} chars, secret {len(secret)} chars", file=sys.stderr)
        return 2
    ssm = _ssm()
    ssm.put_parameter(Name=CLIENT_ID_PARAM, Value=client_id, Type="String", Overwrite=True)
    ssm.put_parameter(Name=CLIENT_SECRET_PARAM, Value=secret, Type="SecureString", Overwrite=True)
    print(f"saved to SSM (client id {len(client_id)} chars, secret {len(secret)} chars)")
    return cmd_capture()


def cmd_exchange():
    code = extract_code(getpass.getpass("code: "))
    if not code:
        print("no code given", file=sys.stderr)
        return 2
    return _exchange_and_store(code, REDIRECT_URI)


def _access_token(client_id, client_secret, refresh):
    status, payload = _token_post(
        client_id, client_secret,
        {"grant_type": "refresh_token", "refresh_token": refresh,
         "redirect_uri": REDIRECT_URI}, "token refresh")
    token = payload.get("access_token")
    if status != 200 or not isinstance(token, str) or not token:
        raise HttpError(status, "token refresh (no access token)")
    return token


def _read_once(access):
    sys.path.insert(0, os.path.join(REPO_ROOT, "backend", "src"))
    from lineup import yahoo  # backend read client under test
    transport = YahooTransport()
    leagues = yahoo.get_leagues(transport, access)
    if not leagues:
        raise ValueError("Yahoo returned no NFL leagues for this login")
    league_key = leagues[0]["league_key"]
    week = current_week_from(transport.last_raw) or fallback_week()
    teams = yahoo.get_teams(transport, access, league_key)
    if not teams:
        raise ValueError("Yahoo returned no teams for the league")
    team_key = owned_team_key(transport.last_raw) or teams[0]["team_key"]
    roster = yahoo.get_roster(transport, access, team_key, week)
    settings = yahoo.get_settings(transport, access, league_key)
    return transport, {
        "captured_at": _now(),
        "http_statuses": transport.statuses,
        "league_count": len(leagues),
        "league_key": league_key,
        "season": leagues[0]["season"],
        "team_count": len(teams),
        "team_key": team_key,
        "week": week,
        "starter_count": len(roster["starters"]),
        "bench_count": len(roster["bench"]),
        "roster_slots": sorted(p["slot"] for p in
                               roster["starters"] + roster["bench"]),
        "stat_modifiers_present": bool(settings["stat_modifiers"]),
        "stat_modifier_count": len(settings["stat_modifiers"]),
        "settings_roster_slot_count": len(settings["roster_slots"]),
    }


def cmd_read():
    client_id = ssm_get(CLIENT_ID_PARAM).strip()
    client_secret = ssm_get(CLIENT_SECRET_PARAM).strip()
    refresh = ssm_get(TOKEN_PARAM)
    evidence, refreshed = None, False
    while True:
        try:
            _, evidence = _read_once(_access_token(client_id, client_secret, refresh))
            break
        except HttpError as error:
            if error.status == 401 and not refreshed:
                refreshed = True  # loop rule: one fresh-token retry, then report
                continue
            raise
    evidence["refreshed_after_401"] = refreshed
    os.makedirs(os.path.dirname(EVIDENCE_PATH), exist_ok=True)
    with open(EVIDENCE_PATH, "w", encoding="utf-8") as handle:
        json.dump(redact(evidence), handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"read ok: statuses={evidence['http_statuses']} "
          f"week={evidence['week']} starters={evidence['starter_count']} "
          f"bench={evidence['bench_count']}")
    return 0


def _ensure_boto3():
    """Owner command is `python3 ...`; re-exec under python3.12 if needed."""
    try:
        import boto3  # noqa: F401
    except ImportError:
        alt = shutil.which("python3.12")
        if alt and not os.environ.get("AFC_YAHOO_REEXEC"):
            os.environ["AFC_YAHOO_REEXEC"] = "1"
            os.execv(alt, [alt, os.path.abspath(__file__), *sys.argv[1:]])
        raise


def main(argv):
    commands = {"url": cmd_url, "exchange": cmd_exchange, "capture": cmd_capture, "setup": cmd_setup, "read": cmd_read}
    if len(argv) != 2 or argv[1] not in commands:
        print("usage: yahoo_oauth.py {url|exchange|read}", file=sys.stderr)
        return 2
    _ensure_boto3()
    try:
        return commands[argv[1]]()
    except HttpError as error:
        print(f"failed: {error}", file=sys.stderr)
        return 1
    except (ValueError, KeyError) as error:
        print(f"failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
