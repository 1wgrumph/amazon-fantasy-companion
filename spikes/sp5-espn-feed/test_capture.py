"""Offline tests for capture.py: no network, a fake fetch stands in for ESPN."""

import hashlib
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.request
import urllib.response
from email.message import Message
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capture  # noqa: E402

DATE = '20261011'
SB_URL = capture.SCOREBOARD_URL.format(date=DATE)


def event(game_id, completed=True):
    name = 'STATUS_FINAL' if completed else 'STATUS_IN_PROGRESS'
    return {'id': game_id, 'competitions': [{'status': {'type': {'name': name, 'completed': completed}}}]}


def scoreboard(*events):
    return json.dumps({'events': list(events)}).encode()


def summary(game_id):
    return json.dumps({'header': {'id': game_id}, 'drives': {}}).encode()


class FakeFeed:
    def __init__(self, responses):
        self.responses = responses
        self.urls = []

    def __call__(self, url, max_bytes):
        self.urls.append(url)
        return self.responses[url]


class CaptureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name) / 'replay'
        self.sleeps = []

    def tearDown(self):
        self.tmp.cleanup()

    def run_capture(self, responses, provenance='historical', events=None, max_bytes=1 << 20):
        feed = FakeFeed(responses)
        written = capture.capture([DATE], events, provenance, self.out, max_bytes,
                                  fetch=feed, sleep=self.sleeps.append)
        return feed, written

    def test_capture_writes_raw_bodies_and_provenance_index(self):
        sb, sm = scoreboard(event('101')), summary('101')
        feed, written = self.run_capture({SB_URL: (200, sb), capture.SUMMARY_URL.format(event='101'): (200, sm)})
        self.assertEqual([p.name for p in written], ['001-scoreboard.json', '001-summary.json'])
        self.assertEqual((self.out / '101' / '001-summary.json').read_bytes(), sm)
        index = json.loads((self.out / '101' / 'index.json').read_text())
        self.assertEqual(index['game_id'], '101')
        entry = index['files'][1]
        self.assertEqual(entry['sha256'], hashlib.sha256(sm).hexdigest())
        self.assertEqual(entry['provenance'], 'historical-replay')
        self.assertEqual(entry['http_status'], 200)
        self.assertEqual(entry['url'], capture.SUMMARY_URL.format(event='101'))
        self.assertRegex(entry['retrieved_at'], r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$')
        self.assertEqual(self.sleeps, [capture.MIN_INTERVAL_S])  # rate limit between the two GETs
        self.assertEqual(capture.verify(self.out), [])

    def test_malformed_json_is_rejected_and_nothing_written(self):
        responses = {SB_URL: (200, scoreboard(event('101'))),
                     capture.SUMMARY_URL.format(event='101'): (200, b'{"header": {"id": "101"')}
        with self.assertRaisesRegex(capture.CaptureError, 'malformed JSON'):
            self.run_capture(responses)
        self.assertFalse((self.out / '101').exists())

    def test_oversize_body_is_rejected(self):
        with self.assertRaisesRegex(capture.CaptureError, 'exceeds'):
            self.run_capture({SB_URL: (200, scoreboard(event('101')) + b' ' * 64)}, max_bytes=32)

    def test_non_200_and_wrong_shape_are_rejected(self):
        with self.assertRaisesRegex(capture.CaptureError, 'HTTP 503'):
            self.run_capture({SB_URL: (503, b'{}')})
        with self.assertRaisesRegex(capture.CaptureError, 'missing events'):
            self.run_capture({SB_URL: (200, b'{"leagues": []}')})
        with self.assertRaisesRegex(capture.CaptureError, 'header id'):
            self.run_capture({SB_URL: (200, scoreboard(event('101'))),
                              capture.SUMMARY_URL.format(event='101'): (200, summary('999'))})

    def test_unsafe_event_id_is_rejected(self):
        with self.assertRaisesRegex(capture.CaptureError, 'unsafe event id'):
            self.run_capture({SB_URL: (200, scoreboard(event('../etc')))})

    def test_non_espn_host_is_refused_before_any_request(self):
        with self.assertRaisesRegex(capture.CaptureError, 'non-ESPN'):
            capture.http_get('https://example.com/x', 10)
        with self.assertRaisesRegex(capture.CaptureError, 'non-ESPN'):
            capture.http_get('http://site.api.espn.com/x', 10)

    def test_http_get_rejects_302_without_following_redirect(self):
        urls = []

        def open_response(handler, request):
            urls.append(request.full_url)
            headers = Message()
            headers['Location'] = 'https://example.com/feed'
            status = 302 if request.full_url == SB_URL else 200
            response = urllib.response.addinfourl(io.BytesIO(b'{}'), headers, request.full_url, status)
            response.msg = 'Found' if status == 302 else 'OK'
            return response

        with patch.object(urllib.request, '_opener', None), \
                patch.object(urllib.request.HTTPSHandler, 'https_open', open_response), \
                patch.object(urllib.request.HTTPHandler, 'http_open', open_response):
            with self.assertRaisesRegex(capture.CaptureError, 'HTTP 302'):
                capture.http_get(SB_URL, 10)
        self.assertEqual(urls, [SB_URL])

    def test_http_get_checks_response_scheme_and_host(self):
        for url in ('https://example.com/feed', 'http://site.api.espn.com/feed'):
            with self.subTest(url=url):
                response = urllib.response.addinfourl(io.BytesIO(b'{}'), Message(), url, 200)
                response.msg = 'OK'
                with patch.object(urllib.request, '_opener', None), \
                        patch.object(urllib.request.HTTPSHandler, 'https_open', return_value=response):
                    with self.assertRaisesRegex(capture.CaptureError, 'response URL'):
                        capture.http_get(SB_URL, 10)

    def test_http_get_accepts_same_origin_response(self):
        response = urllib.response.addinfourl(io.BytesIO(b'{}'), Message(), SB_URL, 200)
        response.msg = 'OK'
        with patch.object(urllib.request, '_opener', None), \
                patch.object(urllib.request.HTTPSHandler, 'https_open', return_value=response):
            self.assertEqual(capture.http_get(SB_URL, 10), (200, b'{}'))

    def test_non_object_event_is_rejected(self):
        with self.assertRaisesRegex(capture.CaptureError, 'event is not an object'):
            self.run_capture({SB_URL: (200, scoreboard(1))})
        self.assertFalse(self.out.exists())

    def test_non_object_status_type_is_rejected(self):
        bad_event = event('101')
        bad_event['competitions'][0]['status']['type'] = 'x'
        with self.assertRaisesRegex(capture.CaptureError, 'has no status'):
            self.run_capture({SB_URL: (200, scoreboard(bad_event))})
        self.assertFalse(self.out.exists())

    def test_event_state_rejects_non_object_values(self):
        for value in (1, {'competitions': [1]}, {'competitions': [{'status': 'x'}]}):
            with self.subTest(event=value):
                with self.assertRaisesRegex(capture.CaptureError, 'has no status'):
                    capture.event_state(value)

    def test_event_id_with_trailing_newline_is_rejected(self):
        with self.assertRaisesRegex(capture.CaptureError, 'unsafe event id'):
            self.run_capture({SB_URL: (200, scoreboard(event('101\n'))),
                              capture.SUMMARY_URL.format(event='101\n'): (200, summary('101\n'))})
        self.assertFalse(self.out.exists())

    def test_date_with_trailing_newline_is_rejected_before_fetch(self):
        feed = FakeFeed({capture.SCOREBOARD_URL.format(date=DATE + '\n'): (200, scoreboard())})
        with self.assertRaisesRegex(capture.CaptureError, 'bad date'):
            capture.capture([DATE + '\n'], None, 'historical', self.out, 1024, fetch=feed)
        self.assertEqual(feed.urls, [])

    def test_verify_reports_non_object_index_header(self):
        game_dir = self.out / '101'
        game_dir.mkdir(parents=True)
        (game_dir / 'index.json').write_text('[]')
        self.assertEqual(capture.verify(self.out), ['101: bad index header'])

    def test_verify_reports_non_object_file_entries(self):
        game_dir = self.out / '101'
        game_dir.mkdir(parents=True)
        for entry in (1, 'x', None, []):
            with self.subTest(entry=entry):
                (game_dir / 'index.json').write_text(json.dumps({
                    'schema': capture.INDEX_SCHEMA, 'game_id': '101', 'files': [entry]}))
                self.assertEqual(capture.verify(self.out), ['101: files entry is not an object'])

    def test_atomic_write_uses_readable_permissions_subject_to_umask(self):
        path = Path(self.tmp.name) / 'body.json'
        previous_umask = os.umask(0o027)
        try:
            capture.write_atomic(path, b'{}')
        finally:
            os.umask(previous_umask)
        self.assertEqual(path.stat().st_mode & 0o777, 0o640)
        self.assertEqual(path.read_bytes(), b'{}')

    def test_historical_skips_unfinished_games(self):
        feed, written = self.run_capture({SB_URL: (200, scoreboard(event('101', completed=False)))})
        self.assertEqual(written, [])
        self.assertEqual(feed.urls, [SB_URL])

    def test_recapture_appends_next_sequence_without_touching_prior_files(self):
        responses = {SB_URL: (200, scoreboard(event('101'))),
                     capture.SUMMARY_URL.format(event='101'): (200, summary('101'))}
        self.run_capture(responses)
        first = (self.out / '101' / '001-summary.json').read_bytes()
        responses[capture.SUMMARY_URL.format(event='101')] = (200, json.dumps(
            {'header': {'id': '101'}, 'corrected': True}).encode())
        _, written = self.run_capture(responses)
        self.assertEqual([p.name for p in written], ['002-scoreboard.json', '002-summary.json'])
        self.assertEqual((self.out / '101' / '001-summary.json').read_bytes(), first)
        self.assertEqual(len(json.loads((self.out / '101' / 'index.json').read_text())['files']), 4)
        self.assertEqual(capture.verify(self.out), [])

    def test_verify_detects_tampering_and_unindexed_files(self):
        self.run_capture({SB_URL: (200, scoreboard(event('101'))),
                          capture.SUMMARY_URL.format(event='101'): (200, summary('101'))})
        (self.out / '101' / '001-summary.json').write_bytes(b'{}')
        (self.out / '101' / '005-summary.json').write_bytes(b'{}')
        problems = capture.verify(self.out)
        self.assertIn('101/001-summary.json: sha256 mismatch', problems)
        self.assertIn('101/005-summary.json: not in index', problems)

    def test_cli_rejects_malformed_feed_with_exit_1(self):
        original = capture.http_get
        capture.http_get = lambda url, max_bytes: (200, b'not json')
        try:
            rc = capture.main(['capture', '--date', DATE, '--provenance', 'historical', '--out', str(self.out)])
        finally:
            capture.http_get = original
        self.assertEqual(rc, 1)


if __name__ == '__main__':
    unittest.main()
