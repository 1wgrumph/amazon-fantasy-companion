"""Gate isolation regression (defect D1, AC-AFC-CI-01 hooks path): git exports
GIT_DIR / GIT_INDEX_FILE to hooks, and the gate's unittest run must not let
those reach the temporary repositories its tests create.

The copy runs the real hook command (gate.sh --changed) with one planted test
that builds a fixture repo through gate_support, as the real gate tests do.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from gate_support import REPO, TESTS, copy_repo, git, run_gate, write

FIXTURE_TEST = '''import tempfile
import unittest

from gate_support import init_repo


class FixtureCommit(unittest.TestCase):
    def test_fixture_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            init_repo(tmp, {'fixture.txt': 'fixture\\n'})
'''


def snapshot(git_dir):
    """Bytes of HEAD, packed-refs, every loose ref and the index."""
    git_dir = Path(git_dir)
    files = [git_dir / 'HEAD', git_dir / 'packed-refs', git_dir / 'index']
    files += sorted(p for p in (git_dir / 'refs').rglob('*') if p.is_file())
    return {str(p.relative_to(git_dir)): p.read_bytes() for p in files if p.is_file()}


class D1_HookEnvironmentIsolation(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_hook_git_env_does_not_reach_sentinel_repo(self):
        # The sentinel has the same files, so the gate's own read-only checks still resolve.
        sentinel = copy_repo(self.tmp / 'sentinel')
        git(sentinel, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
        repo = copy_repo(self.tmp / 'repo')
        write(repo, {str(TESTS / 'gate_support.py'): (REPO / TESTS / 'gate_support.py').read_text(encoding='utf-8'),
                     str(TESTS / 'test_fixture_commit.py'): FIXTURE_TEST})
        before = snapshot(sentinel / '.git')
        env = dict(os.environ, GIT_DIR=str(sentinel / '.git'), GIT_INDEX_FILE=str(sentinel / '.git' / 'index'))
        rc, out = run_gate(self, repo, '--changed', env=env)
        log = subprocess.run(['git', 'log', '--oneline', '--all'], cwd=sentinel, check=True,
                             capture_output=True, text=True).stdout
        self.assertEqual(snapshot(sentinel / '.git'), before,
                         f'gate.sh --changed wrote to the repository named by hook GIT_DIR/GIT_INDEX_FILE\n'
                         f'sentinel log:\n{log}\ngate output:\n{out}')
        self.assertEqual(len(log.splitlines()), 1, log)
        self.assertEqual(rc, 0, out)


if __name__ == '__main__':
    unittest.main()
