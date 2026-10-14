"""BUG-AFC-B01-TOOL-001 BUG 2: the mutation wrapper runs mutmut under the
backend-test interpreter and copies non-Python files the tests read.

mutmut runs pytest in-process, so PATH `mutmut` (deps-free venv) cannot run the
real backend suite; and mutmut copies only src/tests/config into mutants/, so
the conftest read of backend/template.yaml fails. Unique temporary git repo per
test; no engine, network or AWS.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CONTROL = 'def verdict(ok):\n    if ok:\n        return "covered"\n    return "uncovered"\n'
BOTH = ('from control import verdict\n\n\ndef test_verdict():\n'
        '    assert verdict(True) == "covered"\n    assert verdict(False) == "uncovered"\n')
FAKE_PYTHON312 = """#!/usr/bin/env bash
# Emulates `python3.12 -m mutmut ...`: version probes pass, run captures the
# generated setup.cfg, export/results succeed with no report on disk.
if [[ "$*" == *--version* ]]; then exit 0; fi
if [[ "$*" == *run* ]]; then cp setup.cfg "$BUG2_CAPTURE"; exit 1; fi
exit 0
"""
FAKE_MUTMUT = """#!/usr/bin/env bash
echo called >> "$BUG2_PATH_CALLED"
exit 1
"""


def git(cwd, *args):
    return subprocess.run(['git', '-c', 'user.name=Gate Test', '-c', 'user.email=gate-test@example.invalid',
                           '-c', 'commit.gpgsign=false', *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def write(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')


class MutationEnv(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo, self.out = self.tmp / 'repo', self.tmp / 'out'
        shutil.copytree(REPO / 'tools/ci/mutation', self.repo / 'tools/ci/mutation')
        write(self.repo, {'backend/pyproject.toml': '[tool.pytest.ini_options]\npythonpath = ["src"]\n',
                          'backend/src/base.py': 'X = 1\n',
                          'backend/tests/contract/test_base.py': 'def test_base():\n    assert True\n'})
        git(self.repo, 'init', '-q', '-b', 'main')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'fixture')
        self.base = git(self.repo, 'rev-parse', 'HEAD')

    def commit(self):
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'candidate')

    def test_backend_interpreter_mutmut_is_preferred_and_data_files_copied(self):
        # Stub PATH proves which mutmut the wrapper invokes and what setup.cfg
        # it generates, without a real mutation run.
        write(self.repo, {'backend/src/control.py': CONTROL,
                          'backend/tests/unit/test_control.py': BOTH,
                          'backend/template.yaml': 'AWSTemplateFormatVersion: "2010-09-09"\n',
                          'backend/data/extra.txt': 'fixture data\n'})
        self.commit()
        stub = self.tmp / 'stub'
        stub.mkdir()
        (stub / 'python3.12').write_text(FAKE_PYTHON312)
        (stub / 'mutmut').write_text(FAKE_MUTMUT)
        (stub / 'python3.12').chmod(0o755)
        (stub / 'mutmut').chmod(0o755)
        capture, called = self.tmp / 'setup.cfg', self.tmp / 'path-called'
        env = dict(os.environ, PATH=f'{stub}{os.pathsep}{os.environ["PATH"]}',
                   BUG2_CAPTURE=str(capture), BUG2_PATH_CALLED=str(called))
        result = subprocess.run(['bash', 'tools/ci/mutation/backend.sh', self.base, str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=120, env=env)
        out = result.stdout + result.stderr
        print(f'mutation adapter exit={result.returncode}: {out.strip().splitlines()[-1:]}')
        self.assertFalse(called.exists(),
                         'wrapper used PATH mutmut instead of python3.12 -m mutmut')
        self.assertTrue(capture.is_file(), 'python3.12 -m mutmut was never invoked: ' + out)
        text = capture.read_text()
        config = text.splitlines()
        self.assertIn('timeout_multiplier=30.0', config, 'no shared-host timeout calibration:\n' + text)
        self.assertIn('also_copy=', config, 'no also_copy section:\n' + text)
        also = [line.strip() for line in config[config.index('also_copy=') + 1:]
                if line.startswith('    ')]
        self.assertIn('template.yaml', also, 'template.yaml missing from also_copy: ' + str(also))
        self.assertIn('data', also, 'nested data dir missing from also_copy: ' + str(also))

    def test_test_read_data_file_reaches_mutants_end_to_end(self):
        read_data = ('from pathlib import Path\n\n\ndef test_data():\n'
                     '    assert (Path(__file__).parents[2] / "data" / "threshold.txt").read_text()'
                     ' == "3\\n"\n')
        write(self.repo, {'backend/src/control.py': CONTROL,
                          'backend/tests/unit/test_control.py': BOTH,
                          'backend/tests/unit/test_data.py': read_data,
                          'backend/data/threshold.txt': '3\n'})
        self.commit()
        result = subprocess.run(['bash', 'tools/ci/mutation/backend.sh', self.base, str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=600)
        out = result.stdout + result.stderr
        print(f'mutation adapter exit={result.returncode}: {out.strip().splitlines()[-1:]}')
        self.assertEqual(result.returncode, 0, out)
        self.assertEqual(json.loads((self.out / 'mutation-result.json').read_text())['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
