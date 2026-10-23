#!/usr/bin/env python3
"""Recorded alert evidence distinguishes a held Watch result from a second attempt."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7'


class LiveAlerts(unittest.TestCase):
    def run_check(self, readings=None, log=None):
        stage = EVIDENCE / 'stage4'
        with tempfile.TemporaryDirectory() as tmp:
            source = stage / 'alert-readings.json'
            if readings is not None:
                source = Path(tmp) / 'alert-readings.json'
                source.write_text(json.dumps(readings))
            return subprocess.run([sys.executable, '-B', str(ROOT / 'vega-app/vvd-checks/verify-alerts-live.py'),
                                   str(log or stage / 'api-poll.jsonl'), str(source), '401909093'],
                                  capture_output=True, text=True)

    def test_recorded_success_with_held_outcome(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_two_same_result_attempts_fail(self):
        readings = json.loads((EVIDENCE / 'stage4/alert-readings.json').read_text())
        readings += [
            dict(readings[2], capture='second-armed.png', utc='2026-10-22T23:47:00Z'),
            dict(readings[3], capture='second-outcome.png', utc='2026-10-22T23:47:10Z'),
        ]
        result = self.run_check(readings)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('FAIL device: exactly one Watch attempt shows a local', result.stdout)

    def test_zero_alerts_fail(self):
        result = self.run_check(log=EVIDENCE / 'stage3/attempt2/api-poll.jsonl')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('FAIL backend: alert polls 200', result.stdout)


if __name__ == '__main__':
    unittest.main()
