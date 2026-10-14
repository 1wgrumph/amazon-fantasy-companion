#!/usr/bin/env python3
"""Capture ESPN NFL scoreboard and summary JSON as replay fixtures (SP-5, P2-X05).

Layout (CONTRACT-AFC-P2-FIXTURE):
  <out>/<game-id>/<seq>-scoreboard.json   raw scoreboard body as captured
  <out>/<game-id>/<seq>-summary.json      raw summary body as captured
  <out>/<game-id>/index.json              per file: endpoint, url, capture UTC,
                                          HTTP status, sha256, bytes, provenance

Feed data is untrusted: only https GETs to site.api.espn.com, bounded body
size, JSON must parse to the expected shape, and nothing is written for a game
until every body for it has validated. Existing fixture files are never
rewritten; a later capture of the same game gets the next sequence number.

Usage:
  capture.py capture --date YYYYMMDD [--date ...] [--event ID ...]
                     --provenance historical|live [--out DIR] [--max-bytes N]
  capture.py verify [--out DIR]
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HOST = 'site.api.espn.com'
BASE = f'https://{HOST}/apis/site/v2/sports/football/nfl'
SCOREBOARD_URL = BASE + '/scoreboard?dates={date}'
SUMMARY_URL = BASE + '/summary?event={event}'
DEFAULT_OUT = 'backend/fixtures/replay'
DEFAULT_MAX_BYTES = 4 * 1024 * 1024
MIN_INTERVAL_S = 1.0
INDEX_SCHEMA = 'afc.replay-index.v1'
PROVENANCE = {'historical': 'historical-replay', 'live': 'live'}
FILE_RE = re.compile(r'^(\d{3})-(scoreboard|summary)\.json$')
ID_RE = re.compile(r'^\d{1,12}$')
DATE_RE = re.compile(r'^\d{8}$')


class CaptureError(Exception):
    pass


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def http_get(url, max_bytes):
    """Return (status, body bytes). Rejects non-ESPN hosts and oversize bodies."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != 'https' or parts.hostname != HOST:
        raise CaptureError(f'refused non-ESPN url: {url}')
    request = urllib.request.Request(url, headers={
        'Accept': 'application/json', 'User-Agent': 'afc-sp5-capture/1'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read(max_bytes + 1)
            status = response.status
    except urllib.error.HTTPError as error:
        raise CaptureError(f'HTTP {error.code} from {url}') from None
    except (urllib.error.URLError, OSError) as error:
        raise CaptureError(f'fetch failed for {url}: {error}') from None
    return status, body


def validate(kind, status, body, max_bytes, event=None):
    """Return the parsed JSON object, or raise CaptureError."""
    if status != 200:
        raise CaptureError(f'{kind}: HTTP {status}')
    if len(body) > max_bytes:
        raise CaptureError(f'{kind}: body exceeds {max_bytes} bytes')
    try:
        data = json.loads(body.decode('utf-8'))
    except (UnicodeDecodeError, ValueError) as error:
        raise CaptureError(f'{kind}: malformed JSON: {error}') from None
    if not isinstance(data, dict):
        raise CaptureError(f'{kind}: top level is not an object')
    if kind == 'scoreboard':
        if not isinstance(data.get('events'), list):
            raise CaptureError('scoreboard: missing events list')
    else:
        header = data.get('header')
        if not isinstance(header, dict) or str(header.get('id')) != str(event):
            raise CaptureError(f'summary: header id does not match event {event}')
    return data


def event_state(event):
    try:
        return event['competitions'][0]['status']['type']
    except (KeyError, IndexError, TypeError):
        raise CaptureError(f'scoreboard: event {event.get("id")} has no status') from None


def write_atomic(path, data):
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.tmp-')
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def load_index(game_dir, game_id):
    path = game_dir / 'index.json'
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return {'schema': INDEX_SCHEMA, 'game_id': game_id, 'files': []}


def next_seq(game_dir):
    seqs = [int(m.group(1)) for p in game_dir.glob('*.json') if (m := FILE_RE.match(p.name))]
    return max(seqs, default=0) + 1


def store_game(out, game_id, captures, provenance):
    """captures: list of (endpoint, url, retrieved_at, status, body, game_status)."""
    game_dir = out / game_id
    game_dir.mkdir(parents=True, exist_ok=True)
    index = load_index(game_dir, game_id)
    seq = next_seq(game_dir)
    written = []
    for endpoint, url, retrieved_at, status, body, game_status in captures:
        name = f'{seq:03d}-{endpoint}.json'
        path = game_dir / name
        if path.exists():
            raise CaptureError(f'refusing to overwrite {path}')
        write_atomic(path, body)
        index['files'].append({
            'file': name, 'seq': seq, 'endpoint': endpoint, 'url': url,
            'retrieved_at': retrieved_at, 'http_status': status,
            'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body),
            'provenance': provenance, 'game_status': game_status,
        })
        written.append(path)
    write_atomic(game_dir / 'index.json',
                 (json.dumps(index, indent=2, sort_keys=True) + '\n').encode())
    return written


def capture(dates, events, provenance_key, out, max_bytes, fetch=None, sleep=time.sleep):
    fetch = fetch or http_get
    provenance = PROVENANCE[provenance_key]
    wanted = set(events or [])
    written = []
    first = True

    def get(kind, url, event=None):
        nonlocal first
        if not first:
            sleep(MIN_INTERVAL_S)
        first = False
        retrieved_at = utc_now()
        status, body = fetch(url, max_bytes)
        data = validate(kind, status, body, max_bytes, event)
        return url, retrieved_at, status, body, data

    for date in dates:
        if not DATE_RE.match(date):
            raise CaptureError(f'bad date {date!r}, expected YYYYMMDD')
        sb_url, sb_at, sb_status, sb_body, sb = get('scoreboard', SCOREBOARD_URL.format(date=date))
        for event in sb['events']:
            game_id = str(event.get('id', ''))
            if not ID_RE.match(game_id):
                raise CaptureError(f'scoreboard: unsafe event id {game_id!r}')
            if wanted and game_id not in wanted:
                continue
            state = event_state(event)
            if provenance_key == 'historical' and not state.get('completed'):
                print(f'skip {game_id}: not completed ({state.get("name")})')
                continue
            url, at, status, body, _ = get('summary', SUMMARY_URL.format(event=game_id), game_id)
            written += store_game(out, game_id, [
                ('scoreboard', sb_url, sb_at, sb_status, sb_body, state.get('name')),
                ('summary', url, at, status, body, state.get('name')),
            ], provenance)
            print(f'captured {game_id} ({state.get("name")})')
    return written


def verify(out):
    """Recompute every indexed hash; return a list of problems (empty = OK)."""
    problems = []
    if not out.is_dir():
        return [f'{out}: missing']
    for game_dir in sorted(p for p in out.iterdir() if p.is_dir()):
        index_path = game_dir / 'index.json'
        if not index_path.exists():
            problems.append(f'{game_dir.name}: no index.json')
            continue
        try:
            index = json.loads(index_path.read_text(encoding='utf-8'))
        except ValueError:
            problems.append(f'{game_dir.name}: index.json is not valid JSON')
            continue
        if index.get('schema') != INDEX_SCHEMA or index.get('game_id') != game_dir.name:
            problems.append(f'{game_dir.name}: bad index header')
        listed = set()
        last_seq = 0
        for entry in index.get('files', []):
            name = entry.get('file', '')
            listed.add(name)
            match = FILE_RE.match(name)
            if not match or int(match.group(1)) != entry.get('seq') or match.group(2) != entry.get('endpoint'):
                problems.append(f'{game_dir.name}/{name}: name/seq/endpoint mismatch')
                continue
            if entry['seq'] < last_seq:
                problems.append(f'{game_dir.name}/{name}: sequence out of order')
            last_seq = entry['seq']
            for key in ('url', 'retrieved_at', 'http_status', 'sha256', 'provenance'):
                if key not in entry:
                    problems.append(f'{game_dir.name}/{name}: missing {key}')
            if entry.get('provenance') not in PROVENANCE.values():
                problems.append(f'{game_dir.name}/{name}: bad provenance')
            path = game_dir / name
            if not path.exists():
                problems.append(f'{game_dir.name}/{name}: file missing')
            elif hashlib.sha256(path.read_bytes()).hexdigest() != entry.get('sha256'):
                problems.append(f'{game_dir.name}/{name}: sha256 mismatch')
        for path in game_dir.glob('*.json'):
            if path.name != 'index.json' and path.name not in listed:
                problems.append(f'{game_dir.name}/{path.name}: not in index')
    return problems


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    cap = sub.add_parser('capture', help='fetch and store fixtures')
    cap.add_argument('--date', action='append', required=True, help='YYYYMMDD (repeatable)')
    cap.add_argument('--event', action='append', help='limit to these ESPN event ids (repeatable)')
    cap.add_argument('--provenance', choices=sorted(PROVENANCE), required=True,
                     help='historical: completed games only, labeled historical-replay')
    cap.add_argument('--out', default=DEFAULT_OUT)
    cap.add_argument('--max-bytes', type=int, default=DEFAULT_MAX_BYTES)
    ver = sub.add_parser('verify', help='recompute index hashes and check layout')
    ver.add_argument('--out', default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    try:
        if args.command == 'capture':
            written = capture(args.date, args.event, args.provenance, Path(args.out), args.max_bytes)
            print(f'wrote {len(written)} fixture files')
            return 0
        problems = verify(Path(args.out))
        for problem in problems:
            print(problem)
        print('verify: ' + ('FAIL' if problems else 'OK'))
        return 1 if problems else 0
    except CaptureError as error:
        print(f'capture: error: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
