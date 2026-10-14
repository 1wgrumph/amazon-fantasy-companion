"""PROC-GATE-TOOL-QUALIFY controls for the CMD-MUTATION-BACKEND repo adapter.

Resource group: host-mutation-fixtures; unique temporary git repo per test, the
admitted `mutmut` on PATH (3.8.0 venv) and its pytest; no engine, network or AWS.
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


class BackendMutationAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo, self.out = self.tmp / 'repo', self.tmp / 'out'
        shutil.copytree(REPO / 'tools/ci/mutation', self.repo / 'tools/ci/mutation')
        write(self.repo, {'backend/pyproject.toml': '[tool.pytest.ini_options]\npythonpath = ["src"]\n',
                          'backend/src/base.py': 'X = 1\n',
                          'backend/tests/contract/test_base.py': 'def test_base():\n    assert True\n'})
        git(self.repo, 'init', '-q', '-b', 'main')
        self.commit()
        self.base = git(self.repo, 'rev-parse', 'HEAD')

    def commit(self):
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'fixture')

    def run_adapter(self, files):
        write(self.repo, files)
        self.commit()
        result = subprocess.run(['bash', 'tools/ci/mutation/backend.sh', self.base, str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=600)
        out = result.stdout + result.stderr
        print(f'mutation adapter exit={result.returncode}: {out.strip().splitlines()[-1:]}')
        return result.returncode, out

    def result(self):
        return json.loads((self.out / 'mutation-result.json').read_text())

    def test_known_mutants_killed_pass(self):
        rc, out = self.run_adapter({'backend/src/control.py': CONTROL, 'backend/tests/unit/test_control.py': BOTH})
        self.assertEqual(rc, 0, out)
        result = self.result()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['stats']['survived'] + result['stats']['no_tests'], 0, result)
        self.assertGreater(result['stats']['killed'], 0)
        self.assertEqual(git(self.repo, 'status', '--porcelain'), '', 'adapter mutated the checkout')

    def test_deliberate_survivor_fails_and_is_listed(self):
        rc, out = self.run_adapter({'backend/src/control.py': CONTROL, 'backend/tests/unit/test_control.py': ONE})
        self.assertEqual(rc, 1, out)
        result = self.result()
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any(name.startswith('control.x_verdict') for name in result['survivors']), result)

    def test_stale_cached_results_are_not_reused(self):
        # A cached all-killed inventory in the working tree must not reach the verdict.
        write(self.repo, {'backend/mutants/mutmut-cicd-stats.json':
                          json.dumps({'killed': 9, 'survived': 0, 'total': 9, 'no_tests': 0})})
        (self.repo / '.gitignore').write_text('backend/mutants/\n')
        rc, out = self.run_adapter({'backend/src/control.py': CONTROL, 'backend/tests/unit/test_control.py': ONE})
        self.assertEqual(rc, 1, out)
        self.assertNotEqual(self.result()['stats']['killed'], 9)

    def test_no_changed_source_is_empty_inventory_gap(self):
        rc, out = self.run_adapter({'backend/tests/unit/test_extra.py': 'def test_extra():\n    assert True\n'})
        self.assertEqual(rc, 3, out)
        self.assertIn('EMPTY_INVENTORY', out)

    def test_changed_file_without_mutants_is_wrong_mapping_gap(self):
        rc, out = self.run_adapter({'backend/src/control.py': CONTROL, 'backend/src/constants.py': 'LIMIT = 3\n',
                                    'backend/tests/unit/test_control.py': BOTH})
        self.assertEqual(rc, 3, out)
        self.assertIn('no mutants for changed files: backend/src/constants.py', out)

    def test_timeout_or_error_is_unresolved_never_killed(self):
        self.out.mkdir()
        (self.out / 'mutmut-results.txt').write_text('    control.x_verdict__mutmut_1: timeout\n')
        (self.out / 'mutmut-cicd-stats.json').write_text(json.dumps(
            {'killed': 0, 'survived': 0, 'total': 1, 'no_tests': 0, 'timeout': 1}))
        for argv in ([str(self.out), 'backend/src/control.py', '0'], [str(self.out), 'backend/src/control.py', '124']):
            with self.subTest(run_exit=argv[2]):
                result = subprocess.run(['python3', 'tools/ci/mutation/evaluate.py', *argv], cwd=self.repo,
                                        capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertIn('UNRESOLVED', result.stdout)


if __name__ == '__main__':
    unittest.main()
