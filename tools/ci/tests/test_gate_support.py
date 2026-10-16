"""BUG-AFC-B01T-FIXTURE-001: copy_repo must not copy real product trees."""

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import gate_support
from gate_support import copy_repo, init_repo


class CopyRepoProductTreeIsolation(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_copy_repo_excludes_real_product_trees(self):
        source = self.tmp / 'source'
        source.mkdir()
        init_repo(source, {
            'backend/x.py': 'X = 1\n',
            'tv-app/y.py': 'Y = 1\n',
            'tools/ci/gate.sh': '#!/bin/sh\nexit 0\n',
        })
        with mock.patch.object(gate_support, 'REPO', source):
            result = copy_repo(self.tmp / 'copy')
        self.assertFalse((result / 'backend').exists(), 'copy carries real backend/')
        self.assertFalse((result / 'tv-app').exists(), 'copy carries real tv-app/')
        self.assertTrue((result / 'tools' / 'ci' / 'gate.sh').is_file())


if __name__ == '__main__':
    unittest.main()
