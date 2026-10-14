"""PROC-GATE-TOOL-QUALIFY controls for the CMD-MUTATION-BACKEND repo adapter.

Resource group: host-mutation-fixtures; unique temporary git repo per test, the
admitted `mutmut` on PATH (3.8.0 venv) and its pytest; no engine, network or AWS.
"""

import json
import os
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

    def run_adapter(self, files, env=None):
        write(self.repo, files)
        self.commit()
        run_env = dict(os.environ, **env) if env else None
        result = subprocess.run(['bash', 'tools/ci/mutation/backend.sh', self.base, str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=600, env=run_env)
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

    def test_changed_module_level_without_mutants_is_nonfunction_gap(self):
        rc, out = self.run_adapter({'backend/src/control.py': CONTROL, 'backend/src/constants.py': 'LIMIT = 3\n',
                                    'backend/tests/unit/test_control.py': BOTH})
        self.assertEqual(rc, 3, out)
        self.assertIn('PYTHON_NONFUNCTION_MUTATION_GAP', out)

    def test_mixed_module_level_change_is_nonfunction_gap(self):
        rc, out = self.run_adapter({'backend/src/control.py': 'LIMIT = 3\n\n' + CONTROL,
                                    'backend/tests/unit/test_control.py': BOTH})
        self.assertEqual(rc, 3, out)
        self.assertIn('PYTHON_NONFUNCTION_MUTATION_GAP', out)
        self.assertIn('backend/src/control.py', out)

    def test_unchanged_functions_do_not_dilute_changed_score(self):
        two = CONTROL + CONTROL.replace('verdict', 'verdict2')
        two_tests = BOTH + BOTH.replace('verdict', 'verdict2').replace('test_verdict', 'test_verdict2')
        write(self.repo, {'backend/src/control.py': two, 'backend/tests/unit/test_control.py': two_tests})
        self.commit()
        base = git(self.repo, 'rev-parse', 'HEAD')
        write(self.repo, {'backend/src/control.py': two + '\n\ndef untested():\n    return "untested"\n'})
        self.commit()
        result = subprocess.run(['bash', 'tools/ci/mutation/backend.sh', base, str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=600)
        out = result.stdout + result.stderr
        print(f'mutation adapter exit={result.returncode}: {out.strip().splitlines()[-1:]}')
        self.assertEqual(result.returncode, 1, out)
        scored = self.result()
        self.assertEqual(scored['status'], 'FAIL')
        self.assertEqual(scored['score'], 0)
        self.assertEqual(scored['scored_mutants'], 2)
        self.assertGreater(scored['mutants'], scored['scored_mutants'])
        self.assertIn('control.x_verdict__mutmut_1', scored['inventory'])

    def test_mutant_outside_changed_behavior_is_scope_gap(self):
        write(self.repo, {'backend/src/control.py': CONTROL})
        self.commit()
        self.out.mkdir()
        (self.out / 'mutmut-results.txt').write_text('    control.x_ghost__mutmut_1: killed\n')
        (self.out / 'mutmut-cicd-stats.json').write_text(json.dumps(
            {'killed': 1, 'survived': 0, 'total': 1, 'no_tests': 0}))
        result = subprocess.run(['python3', 'tools/ci/mutation/evaluate.py', str(self.out),
                                 'backend/src/control.py', self.base, '0'],
                                cwd=self.repo, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn('MUTATION_SCOPE_GAP', result.stdout)

    def test_truncated_inventory_rejects(self):
        rc, out = self.run_adapter({'backend/src/control.py': CONTROL, 'backend/tests/unit/test_control.py': BOTH})
        self.assertEqual(rc, 0, out)
        lines = (self.out / 'mutmut-results.txt').read_text().splitlines(keepends=True)
        first = next(i for i, line in enumerate(lines) if '__mutmut_' in line)
        (self.out / 'mutmut-results.txt').write_text(''.join(lines[:first + 1]))
        result = subprocess.run(['python3', 'tools/ci/mutation/evaluate.py', str(self.out),
                                 'backend/src/control.py', self.base, '0'],
                                cwd=self.repo, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
        self.assertIn('inventory/stats count mismatch', result.stdout)

    def test_owned_workspace_is_removed(self):
        tmpdir = self.tmp / 'tmpdir'
        tmpdir.mkdir()
        before = set(os.listdir(tmpdir))
        rc, out = self.run_adapter({'backend/src/control.py': CONTROL,
                                    'backend/tests/unit/test_control.py': BOTH},
                                   env={'TMPDIR': str(tmpdir)})
        self.assertEqual(rc, 0, out)
        self.assertEqual(set(os.listdir(tmpdir)) - before, set(), 'adapter leaked its workdir')

    def test_timeout_or_error_is_unresolved_never_killed(self):
        write(self.repo, {'backend/src/control.py': CONTROL})
        self.commit()
        self.out.mkdir()
        (self.out / 'mutmut-results.txt').write_text('    control.x_verdict__mutmut_1: timeout\n')
        (self.out / 'mutmut-cicd-stats.json').write_text(json.dumps(
            {'killed': 0, 'survived': 0, 'total': 1, 'no_tests': 0, 'timeout': 1}))
        for argv in ([str(self.out), 'backend/src/control.py', self.base, '0'],
                    [str(self.out), 'backend/src/control.py', self.base, '124']):
            with self.subTest(run_exit=argv[3]):
                result = subprocess.run(['python3', 'tools/ci/mutation/evaluate.py', *argv], cwd=self.repo,
                                        capture_output=True, text=True, timeout=60)
                self.assertEqual(result.returncode, 3, result.stdout + result.stderr)
                self.assertIn('UNRESOLVED', result.stdout)


if __name__ == '__main__':
    unittest.main()
