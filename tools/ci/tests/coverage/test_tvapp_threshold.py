"""DEC-AFC-SD-052 control: CMD-COVERAGE-TVAPP passes at 70% changed-line coverage; backend stays 90%.

Resource group: host-python-report-fixtures; reuses the tvapp adapter fixture (unique
temporary git repo per test, real diff-cover over JaCoCo XML). No engine, network or device.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_tvapp_adapter as fixture  # noqa: E402  (module import: its TestCase is not re-collected here)

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'coverage'))
import evaluate  # noqa: E402

FOUR_LINES = ('package com.afc.control\n\nfun verdict(ok: Boolean): String {\n    val seen = ok\n'
              '    if (seen) return "covered"\n    return "uncovered"\n}\n')


class TvappThreshold(unittest.TestCase):
    setUp = fixture.TvappCoverageAdapter.setUp
    candidate = fixture.TvappCoverageAdapter.candidate
    run_adapter = fixture.TvappCoverageAdapter.run_adapter
    result = fixture.TvappCoverageAdapter.result

    def test_seventy_five_percent_passes_tvapp_threshold(self):
        self.candidate(FOUR_LINES)
        rc, out = self.run_adapter(fixture.jacoco({3: True, 4: True, 5: True, 6: False}))
        self.assertEqual(rc, 0, out)
        self.assertEqual((self.result()['status'], self.result()['threshold']), ('PASS', 70.0))
        self.assertIn('(threshold 70%)', out)

    def test_below_seventy_percent_fails(self):
        self.candidate()
        rc, out = self.run_adapter(fixture.jacoco({3: True, 4: True, 5: False}))
        self.assertEqual(rc, 1, out)
        self.assertEqual((self.result()['status'], self.result()['threshold']), ('FAIL', 70.0))

    def test_backend_threshold_unchanged(self):
        self.assertEqual(evaluate.THRESHOLD, 90.0)
        self.assertEqual(evaluate.TVAPP['threshold'], 70.0)


if __name__ == '__main__':
    unittest.main()
