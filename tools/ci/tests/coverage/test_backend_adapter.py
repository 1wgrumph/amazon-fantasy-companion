"""PROC-GATE-TOOL-QUALIFY controls for the CMD-COVERAGE-BACKEND repo adapter.

Resource group: host-python-report-fixtures; unique temporary git repo per test,
real coverage.py, pytest and diff-cover; no engine, network or AWS.
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CONTROL = 'def verdict(ok):\n    if ok:\n        return "covered"\n    return "uncovered"\n'
BOTH = ('from control import verdict\n\n\ndef test_verdict():\n'
        '    assert verdict(True) == "covered"\n    assert verdict(False) == "uncovered"\n')
ONE = 'from control import verdict\n\n\ndef test_verdict():\n    assert verdict(True) == "covered"\n'


def git(cwd, *args):
    return subprocess.run(['git', '-c', 'user.name=Gate Test', '-c', 'user.email=gate-test@example.invalid',
                           '-c', 'commit.gpgsign=false', *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


def write(root, files):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')


class BackendCoverageAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo, self.out = self.tmp / 'repo', self.tmp / 'out'
        shutil.copytree(REPO / 'tools/ci/coverage', self.repo / 'tools/ci/coverage')
        write(self.repo, {'backend/pyproject.toml': '[tool.pytest.ini_options]\npythonpath = ["src"]\n',
                          'backend/src/base.py': 'X = 1\n',
                          'backend/tests/contract/test_base.py': 'def test_base():\n    assert True\n'})
        git(self.repo, 'init', '-q', '-b', 'main')
        self.commit()
        self.base = git(self.repo, 'rev-parse', 'HEAD')

    def commit(self):
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'fixture')

    def candidate(self, files):
        write(self.repo, files)
        self.commit()

    def run_adapter(self, *args):
        result = subprocess.run(['bash', 'tools/ci/coverage/backend.sh', *(args or (self.base, str(self.out)))],
                                cwd=self.repo, capture_output=True, text=True, timeout=300)
        out = result.stdout + result.stderr
        print(f'coverage adapter exit={result.returncode}: {out.strip().splitlines()[-1:]}')
        return result.returncode, out

    def result(self):
        return json.loads((self.out / 'coverage-result.json').read_text())

    def test_covered_changed_statements_pass(self):
        self.candidate({'backend/src/control.py': CONTROL, 'backend/tests/unit/test_control.py': BOTH})
        rc, out = self.run_adapter()
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.result()['status'], 'PASS')
        self.assertEqual(self.result()['changed'], ['backend/src/control.py'])

    def test_uncovered_changed_statement_fails_threshold(self):
        self.candidate({'backend/src/control.py': CONTROL, 'backend/tests/unit/test_control.py': ONE})
        rc, out = self.run_adapter()
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.result()['status'], 'FAIL')
        self.assertLess(self.result()['percent'], 90)

    def test_no_changed_source_is_empty_denominator_gap(self):
        self.candidate({'backend/tests/unit/test_extra.py': 'def test_extra():\n    assert True\n'})
        rc, out = self.run_adapter()
        self.assertEqual(rc, 3, out)
        self.assertIn('EMPTY_DENOMINATOR', out)

    def test_absent_xml_rejects(self):
        self.candidate({'backend/src/control.py': CONTROL, 'backend/tests/unit/test_control.py': BOTH})
        result = subprocess.run(['python3', 'tools/ci/coverage/evaluate.py', self.base,
                                 str(self.tmp / 'absent.xml'), str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn('coverage XML absent', result.stdout)

    def test_stale_xml_missing_changed_file_rejects(self):
        # XML produced at the base tree cannot map a file the candidate added.
        self.out.mkdir()
        subprocess.run(['python3.12', '-m', 'coverage', 'run', '--rcfile=/dev/null', '--source=backend/src',
                        f'--data-file={self.out}/.stale', '-m', 'pytest', '-q', 'backend/tests/contract'],
                       cwd=self.repo, check=True, capture_output=True, timeout=120)
        subprocess.run(['python3.12', '-m', 'coverage', 'xml', '--rcfile=/dev/null', f'--data-file={self.out}/.stale',
                        '-o', str(self.tmp / 'stale.xml')], cwd=self.repo, check=True, capture_output=True, timeout=120)
        self.candidate({'backend/src/control.py': CONTROL, 'backend/tests/unit/test_control.py': BOTH})
        result = subprocess.run(['python3', 'tools/ci/coverage/evaluate.py', self.base, str(self.tmp / 'stale.xml'),
                                 str(self.out)], cwd=self.repo, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn('lacks source binding', result.stdout)

    def test_stale_same_file_xml_rejects(self):
        # XML bound to an earlier candidate cannot pass a changed same-file report.
        self.candidate({'backend/src/control.py': CONTROL, 'backend/tests/unit/test_control.py': BOTH})
        rc, out = self.run_adapter()
        self.assertEqual(rc, 0, out)
        stale = self.tmp / 'stale.xml'
        stale.write_bytes((self.out / 'coverage.xml').read_bytes())
        base = git(self.repo, 'rev-parse', 'HEAD')
        self.candidate({'backend/src/control.py': CONTROL.replace('"covered"', '"new"')
                        + '\n\ndef untested():\n    return "new logic"\n',
                        'backend/tests/unit/test_control.py': BOTH.replace('"covered"', '"new"')})
        result = subprocess.run(['python3', 'tools/ci/coverage/evaluate.py', base, str(stale), str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn('bound to another candidate', result.stdout)

    def test_failing_tests_fail_before_report(self):
        self.candidate({'backend/src/control.py': CONTROL,
                        'backend/tests/unit/test_control.py': BOTH.replace('"uncovered"\n', '"wrong"\n')})
        rc, out = self.run_adapter()
        self.assertEqual(rc, 1, out)
        self.assertIn('FAIL backend tests failed', out)


if __name__ == '__main__':
    unittest.main()
