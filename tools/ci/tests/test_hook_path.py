"""Issue #61: real backend tooling without shell activation; no AWS or engine.

Resource group: isolated temporary git repositories. Uses the documented host
venv and real pytest/cfn-lint; the tiny backend corpus only imports test deps.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from gate_support import REPO, commit_all, copy_repo, git, path_without, run_gate, write


class HookPath(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = copy_repo(self.tmp / 'repo')
        git(self.repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
        write(self.repo, {
            'backend/tests/unit/test_imports.py':
                'import boto3\nfrom moto import mock_aws\n\ndef test_imports():\n    assert callable(mock_aws)\n',
            'backend/tests/contract/test_contract.py': 'def test_contract():\n    assert True\n',
            'backend/template.yaml': (REPO / 'backend/template.yaml').read_text(),
        })
        self.env = dict(os.environ, PATH='/usr/bin:/bin', CI='', GITHUB_ACTIONS='',
                        PYTHONDONTWRITEBYTECODE='1', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
        self.venv = Path.home() / '.local/share/afc-tools/backend-tests'

    def assert_local_result(self, rc, out):
        if not (self.venv / 'bin/python3.12').is_file():
            # Hygiene CI has no backend venv: exercise the required GAP there.
            self.assertEqual(rc, 3, out)
            self.assertIn('gate: backend: GAP', out)
            self.assertIn(str(self.venv), out)
            self.assertIn('pip install --require-hashes -r backend/requirements-dev.txt', out)
            self.assertNotIn('ModuleNotFoundError', out)
        else:
            self.assertEqual(rc, 0, out)
            self.assertIn('2 passed', out)
            self.assertIn('gate: backend: PASS', out)

    def test_local_backend_finds_environment_with_minimal_path(self):
        rc, out = run_gate(self, self.repo, 'backend', env=self.env)
        self.assert_local_result(rc, out)

    def test_both_hooks_find_environment_with_minimal_path(self):
        remote = subprocess.check_output(['git', 'rev-parse', 'origin/main'],
                                         cwd=self.repo, text=True).strip()
        for hook in ('pre-commit', 'pre-push'):
            with self.subTest(hook=hook):
                stdin = ''
                if hook == 'pre-commit':
                    # The hook gates the staged change.
                    git(self.repo, 'add', '-A')
                else:
                    # The hook gates the pushed range named on its stdin.
                    commit_all(self.repo)
                    local = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                                    cwd=self.repo, text=True).strip()
                    stdin = f'refs/heads/main {local} refs/heads/main {remote}\n'
                result = subprocess.run([str(self.repo / '.githooks' / hook)],
                                        cwd=self.repo, env=self.env, input=stdin,
                                        capture_output=True, text=True, timeout=600)
                out = result.stdout + result.stderr
                self.assert_local_result(result.returncode, out)

    def test_missing_or_incomplete_environment_is_named_provisioning_gap(self):
        home = self.tmp / 'home with spaces'
        venv = home / '.local/share/afc-tools/backend-tests'
        env = dict(self.env, HOME=str(home),
                   PATH=str(Path.home() / '.local/bin') + ':/usr/bin:/bin')
        for state in ('absent', 'incomplete'):
            with self.subTest(state=state):
                if state == 'incomplete':
                    (venv / 'bin').mkdir(parents=True)
                rc, out = run_gate(self, self.repo, 'backend', env=env)
                self.assertEqual(rc, 3, out)
                self.assertIn('gate: backend: GAP', out)
                self.assertIn(str(venv), out)
                self.assertIn('python3.12 -m venv', out)
                self.assertIn('pip install --require-hashes -r backend/requirements-dev.txt', out)
                self.assertNotIn('ModuleNotFoundError', out)
                self.assertNotIn('gate: backend: PASS', out)

    def test_local_backend_failure_still_blocks_gate(self):
        write(self.repo, {'backend/tests/unit/test_failure.py':
                         'def test_failure():\n    assert False\n'})
        rc, out = run_gate(self, self.repo, 'backend', env=self.env)
        if not (self.venv / 'bin/python3.12').is_file():
            self.assert_local_result(rc, out)
            return
        self.assertEqual(rc, 1, out)
        self.assertIn('1 failed, 2 passed', out)
        self.assertIn('gate: backend: FAIL', out)

    def test_ci_uses_ambient_environment_without_local_venv(self):
        # Tool removal must remain visible in either CI mode, without consulting HOME.
        path = path_without('python3.12', self.tmp / 'ci-bin')
        for flag in ('CI', 'GITHUB_ACTIONS'):
            with self.subTest(flag=flag):
                env = dict(self.env, HOME=str(self.tmp / 'ci-home'), PATH=path)
                env[flag] = 'true'
                rc, out = run_gate(self, self.repo, 'backend', env=env)
                self.assertEqual(rc, 3, out)
                self.assertIn('required tool missing: python3.12', out)
                self.assertNotIn('backend test environment', out)


if __name__ == '__main__':
    unittest.main()
