#!/usr/bin/env python3
"""Recorded successful captures must pass; recorded requesting/error screens must fail."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/m14-vega-i7'
NAMES = ['01-link-code', '04-main-loaded', '05a-redzone-off', '05-redzone-on',
         '09-reload-top', '11-relinked-top', '12-relinked-redzone']


class OnlineScreens(unittest.TestCase):
    def run_check(self, negative=False, bad_reload=False):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for name in NAMES:
                source = EVIDENCE / ('stage2c' if name == '01-link-code' else 'bug-token') / f'{name}.png'
                if negative:
                    source = EVIDENCE / 'stage2' / ('01-link-requesting.png' if name in
                              ['01-link-code', '05a-redzone-off'] else '02-link-network-error.png')
                if bad_reload and name == '11-relinked-top':
                    source = EVIDENCE / 'stage2/02-link-network-error.png'
                shutil.copyfile(source, d / f'{name}.png')
            (d / 'confirm-1').mkdir()
            (d / 'confirm-1/confirm.status').write_text('200\n')
            return subprocess.run([sys.executable, str(ROOT / 'vega-app/vvd-checks/verify-link-online.py'),
                                   str(d)], capture_output=True, text=True)

    def test_recorded_success(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_requesting_and_network_error_are_not_online_success(self):
        result = self.run_check(negative=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_relink_must_reach_settings(self):
        result = self.run_check(bad_reload=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)


if __name__ == '__main__':
    unittest.main()
