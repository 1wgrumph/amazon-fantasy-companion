"""BUG-AFC-B01-TOOL-001 BUG 3: a changed module with zero executable statements
is nothing-to-cover, not an unmapped report gap.

backend/src/api/__init__.py (docstring only) made CMD-COVERAGE-BACKEND exit 3
GAP REPORT_INCOMPLETE on the real B01 candidate. A changed file that does have
statements but is missing from the report must still yield GAP.
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


def git(cwd, *args):
    return subprocess.run(['git', '-c', 'user.name=Gate Test', '-c', 'user.email=gate-test@example.invalid',
                           '-c', 'commit.gpgsign=false', *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def write(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')


class CoverageEmptyModule(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo, self.out = self.tmp / 'repo', self.tmp / 'out'
        shutil.copytree(REPO / 'tools/ci/coverage', self.repo / 'tools/ci/coverage')
        write(self.repo, {'backend/pyproject.toml': '[tool.pytest.ini_options]\npythonpath = ["src"]\n',
                          'backend/src/base.py': 'X = 1\n',
                          'backend/tests/contract/test_base.py': 'def test_base():\n    assert True\n'})
        git(self.repo, 'init', '-q', '-b', 'main')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'fixture')
        self.base = git(self.repo, 'rev-parse', 'HEAD')

    def candidate(self, files):
        write(self.repo, files)
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'candidate')

    def run_adapter(self):
        result = subprocess.run(['bash', 'tools/ci/coverage/backend.sh', self.base, str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=300)
        out = result.stdout + result.stderr
        print(f'coverage adapter exit={result.returncode}: {out.strip().splitlines()[-1:]}')
        return result.returncode, out

    def result(self):
        return json.loads((self.out / 'coverage-result.json').read_text())

    def test_missing_diff_cover_fails_closed(self):
        self.candidate({'backend/src/control.py': CONTROL,
                        'backend/tests/unit/test_control.py': BOTH})
        stub = self.tmp / 'noutil'
        stub.mkdir()
        for tool in ['python3', 'python3.12', 'git']:
            (stub / tool).symlink_to(shutil.which(tool))
        env = dict(os.environ, PATH=str(stub))
        result = subprocess.run([shutil.which('bash'), 'tools/ci/coverage/backend.sh',
                                 self.base, str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=120, env=env)
        out = result.stdout + result.stderr
        self.assertEqual(result.returncode, 3, out)
        self.assertIn('GAP required tool missing: diff-cover', out)

    def test_docstring_only_changed_file_is_nothing_to_cover(self):
        self.candidate({'backend/src/control.py': CONTROL,
                        'backend/src/empty.py': '"""Docstring only; no executable statements."""\n',
                        'backend/tests/unit/test_control.py': BOTH})
        rc, out = self.run_adapter()
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.result()['status'], 'PASS')

    def test_statement_bearing_file_missing_from_report_is_still_gap(self):
        # A deletion-only change adds no lines, so diff-cover maps nothing for
        # the file; with statements present that stays REPORT_INCOMPLETE.
        self.candidate({'backend/src/control.py': CONTROL.replace('    if ok:\n', '    dead = 99\n    if ok:\n'),
                        'backend/tests/unit/test_control.py': BOTH})
        self.base = git(self.repo, 'rev-parse', 'HEAD')
        self.candidate({'backend/src/control.py': CONTROL})
        rc, out = self.run_adapter()
        self.assertEqual(rc, 3, out)
        self.assertIn('unmapped changed files: backend/src/control.py', out)


if __name__ == '__main__':
    unittest.main()
