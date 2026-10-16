"""Hook scope: pre-commit checks the staged change only (correct during a
merge) and pre-push checks the pushed range only.

Regression: --changed selected areas and WS-CHECK from merge-base..worktree
plus every untracked file, so a merge commit failed on the merged-in side's
already-landed whitespace and a docs-only commit ran tvapp/backend because
of unrelated unstaged/untracked files.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from gate_support import commit_all, copy_repo, git, run_gate, write


def run_hook(case, repo, hook, stdin='', env_extra=None):
    path = Path(repo) / '.githooks' / hook
    case.assertTrue(path.is_file(), f'.githooks/{hook} is missing')
    env = dict(os.environ, CI='', GITHUB_ACTIONS='', **(env_extra or {}))
    result = subprocess.run([str(path)], cwd=repo, env=env, input=stdin,
                            capture_output=True, text=True, timeout=900)
    return result.returncode, result.stdout + result.stderr


def head(repo):
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()


class PreCommitScope(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = copy_repo(self.tmp / 'repo')
        git(self.repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')

    def test_merge_with_clean_resolution_ignores_merged_in_whitespace(self):
        repo = self.repo
        git(repo, 'checkout', '-q', '-b', 'side')
        write(repo, {'merged-in.txt': 'already landed trailing space \n'})
        commit_all(repo, 'side change with whitespace')
        git(repo, 'checkout', '-q', 'main')
        write(repo, {'main-side.txt': 'clean main change\n'})
        commit_all(repo, 'main change')
        git(repo, 'merge', '--no-ff', '--no-commit', 'side')
        rc, out = run_hook(self, repo, 'pre-commit')
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: hygiene: PASS', out)
        self.assertNotIn('merged-in.txt:1:WS-CHECK', out.splitlines())

    def test_merge_resolution_introducing_whitespace_still_fails(self):
        repo = self.repo
        git(repo, 'checkout', '-q', '-b', 'side')
        write(repo, {'merged-in.txt': 'side content\n'})
        commit_all(repo, 'side change')
        git(repo, 'checkout', '-q', 'main')
        write(repo, {'main-side.txt': 'clean main change\n'})
        commit_all(repo, 'main change')
        git(repo, 'merge', '--no-ff', '--no-commit', 'side')
        # An edit made by the merge itself (in neither parent) is this commit's own change.
        write(repo, {'merged-in.txt': 'side content edited by merge \n'})
        git(repo, 'add', 'merged-in.txt')
        rc, out = run_hook(self, repo, 'pre-commit')
        self.assertEqual(rc, 1, out)
        self.assertIn('merged-in.txt:1:WS-CHECK', out.splitlines())

    def test_merge_second_ws_diff_error_fails_closed(self):
        # F2: an unparseable error from the MERGE_HEAD diff must not clear
        # real findings from the HEAD diff via an empty intersection.
        repo = self.repo
        git(repo, 'checkout', '-q', '-b', 'side')
        write(repo, {'merged-in.txt': 'side content\n'})
        commit_all(repo, 'side change')
        git(repo, 'checkout', '-q', 'main')
        write(repo, {'main-side.txt': 'clean main change\n'})
        commit_all(repo, 'main change')
        git(repo, 'merge', '--no-ff', '--no-commit', 'side')
        write(repo, {'merged-in.txt': 'side content edited by merge \n'})
        git(repo, 'add', 'merged-in.txt')
        fakebin = self.tmp / 'fakebin'
        fakebin.mkdir()
        real_git = shutil.which('git')
        write(self.tmp, {'fakebin/git': '#!/usr/bin/env bash\n'
               'if [[ "$*" == "diff --cached --check MERGE_HEAD --" ]]; then\n'
               '    echo "fake git error" >&2; exit 2\nfi\n'
               f'exec {real_git} "$@"\n'})
        (fakebin / 'git').chmod(0o755)
        env = {'PATH': str(fakebin) + os.pathsep + os.environ['PATH']}
        rc, out = run_hook(self, repo, 'pre-commit', env_extra=env)
        self.assertEqual(rc, 1, out)
        self.assertNotIn('gate: hygiene: PASS', out)

    def test_staged_docs_only_change_ignores_unstaged_and_untracked_product_files(self):
        repo = self.repo
        write(repo, {'backend/marker.txt': 'tracked backend file\n'})
        commit_all(repo, 'track a backend file')
        write(repo, {'CHANGELOG.md': (repo / 'CHANGELOG.md').read_text(encoding='utf-8')
                     + '\nStaged docs-only marker line.\n'})
        git(repo, 'add', 'CHANGELOG.md')
        # None of these are staged, so none may select an area for this commit.
        write(repo, {'backend/marker.txt': 'unstaged backend edit\n',
                     'tv-app/untracked.txt': 'untracked tv file\n',
                     'tools/ci/__pycache__/probe.pyc': 'untracked cache\n'})
        rc, out = run_hook(self, repo, 'pre-commit')
        self.assertEqual(rc, 0, out)
        self.assertNotIn('gate: backend:', out)
        self.assertNotIn('gate: tvapp:', out)

    def test_staged_trailing_whitespace_still_fails_ws_check(self):
        repo = self.repo
        write(repo, {'notes.txt': 'staged trailing space \n'})
        git(repo, 'add', 'notes.txt')
        rc, out = run_hook(self, repo, 'pre-commit')
        self.assertEqual(rc, 1, out)
        self.assertIn('notes.txt:1:WS-CHECK', out.splitlines())
        self.assertNotIn('staged trailing space', out.replace('notes.txt:1:WS-CHECK', ''))


class PrePushScope(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = copy_repo(self.tmp / 'repo')
        git(self.repo, 'update-ref', 'refs/remotes/origin/main', 'HEAD')

    def push_line(self, local_sha, remote_sha):
        return f'refs/heads/main {local_sha} refs/heads/main {remote_sha}\n'

    def test_pushed_range_selects_its_own_areas_only(self):
        repo = self.repo
        remote = head(repo)
        write(repo, {'backend/marker.txt': 'pushed backend change\n'})
        commit_all(repo, 'backend change')
        write(repo, {'tv-app/untracked.txt': 'not part of the push\n'})
        rc, out = run_hook(self, repo, 'pre-push', self.push_line(head(repo), remote))
        self.assertIn('gate: backend:', out)
        self.assertNotIn('gate: tvapp:', out)

    def test_second_ref_checked_when_gate_child_reads_stdin(self):
        # F1: a gate child (here the hygiene unittest run) reading stdin must
        # not consume the remaining pre-push ref lines.
        repo = self.repo
        base = head(repo)
        write(repo, {'clean.md': '# Clean\n'})
        commit_all(repo, 'clean change')
        clean = head(repo)
        write(repo, {'notes.txt': 'pushed trailing space \n'})
        commit_all(repo, 'dirty change')
        dirty = head(repo)
        write(repo, {'tools/ci/tests/test_stub.py':
                     'import sys\nimport unittest\n\n\nclass Stub(unittest.TestCase):\n'
                     '    def test_ok(self):\n        sys.stdin.read()\n'})
        stdin = self.push_line(clean, base) + self.push_line(dirty, clean)
        rc, out = run_hook(self, repo, 'pre-push', stdin)
        self.assertEqual(rc, 1, out)
        self.assertIn('notes.txt:1:WS-CHECK', out.splitlines())

    def test_unknown_remote_tip_names_missing_base_and_fails(self):
        # F3: an unfetched remote tip must fail with a named reason, not usage.
        repo = self.repo
        write(repo, {'notes.md': '# Notes\n'})
        commit_all(repo, 'docs change')
        missing = '1' * 40
        rc, out = run_hook(self, repo, 'pre-push', self.push_line(head(repo), missing))
        self.assertNotEqual(rc, 0, out)
        self.assertIn(missing, out)
        self.assertIn('fetch', out.lower())
        self.assertNotIn('usage:', out)

    def test_already_pushed_commits_are_not_rechecked(self):
        repo = self.repo
        write(repo, {'backend/marker.txt': 'already pushed backend change\n'})
        commit_all(repo, 'backend change')
        remote = head(repo)
        write(repo, {'notes.md': '# Notes\n\nDocs-only follow-up.\n'})
        commit_all(repo, 'docs change')
        rc, out = run_hook(self, repo, 'pre-push', self.push_line(head(repo), remote))
        self.assertEqual(rc, 0, out)
        self.assertNotIn('gate: backend:', out)
        self.assertNotIn('gate: tvapp:', out)


class GateFailClosed(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = copy_repo(self.tmp / 'repo')

    def test_unknown_range_base_fails_closed_with_named_revision(self):
        missing = '1' * 40
        rc, out = run_gate(self, self.repo, f'--changed={missing}..HEAD', 'hygiene')
        self.assertEqual(rc, 2, out)
        self.assertIn(missing, out)
        self.assertIn('unknown revision', out)


if __name__ == '__main__':
    unittest.main()
