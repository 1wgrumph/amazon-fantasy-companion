#!/usr/bin/env python3
"""Recorded live-panel verdicts require observed refresh and fault comparisons."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7/stage3'


class LivePanel(unittest.TestCase):
    def run_check(self, attempt='', readings=None):
        evidence = EVIDENCE / attempt
        with tempfile.TemporaryDirectory() as tmp:
            source = evidence / 'device-readings.json'
            if readings is not None:
                source = Path(tmp) / 'device-readings.json'
                source.write_text(json.dumps(readings))
            return subprocess.run([sys.executable, '-B', str(ROOT / 'vega-app/vvd-checks/verify-panel-live.py'),
                                   str(evidence / 'api-poll.jsonl'), str(source)],
                                  capture_output=True, text=True)

    def attempt2_readings(self):
        return json.loads((EVIDENCE / 'attempt2/device-readings.json').read_text())

    def test_recorded_failure(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('FAIL backend: changed panel rows carry a higher revision', result.stdout)

    def test_recorded_success(self):
        result = self.run_check('attempt2')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_single_unavailable_capture_is_not_refresh_coverage(self):
        readings = self.attempt2_readings()[:1]
        readings[0]['total'] = [None] * 5
        result = self.run_check('attempt2', readings)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('FAIL device: live refresh coverage', result.stdout)

    def test_no_fault_captures_fail_r3(self):
        readings = [r for r in self.attempt2_readings() if not r['fault']]
        result = self.run_check('attempt2', readings)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('FAIL device: during refused refreshes', result.stdout)

    def test_one_fault_capture_fails_r3(self):
        readings = self.attempt2_readings()
        one_fault = next(r for r in readings if r['fault'])
        result = self.run_check('attempt2', [r for r in readings if not r['fault']] + [one_fault])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('FAIL device: during refused refreshes', result.stdout)


if __name__ == '__main__':
    unittest.main()
