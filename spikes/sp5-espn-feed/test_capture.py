"""Offline tests for capture.py: no network, a fake fetch stands in for ESPN."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

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
