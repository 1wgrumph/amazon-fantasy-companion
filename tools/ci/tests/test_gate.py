"""Gate entrypoint tests: AC-AFC-CI-01 (SEIT-AFC-CI-01.U) and the spec area of
AC-AFC-CI-04 (SEIT-AFC-CI-04.U), per CONTRACT-AFC-GATE and DES-AFC-GATE."""

import json
import os
import re
import secrets
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gate_support import REPO, commit_all, copy_repo, git, path_without, run_gate, write

AREAS = {'spec', 'docs', 'hygiene'}
DIRECT_CHECKS = re.compile(r'check_(paths|docs|workflows)\.py|spec_(lint|build)\.py|diagram\.py')


def home_path():
    return '/'.join(['', 'home', 'alice', 'notes.txt'])


class AC_AFC_CI_01(unittest.TestCase):
    """One entrypoint, areas spec/docs/hygiene, same invocation everywhere, exit 0/1/2/3."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_list_prints_exactly_spec_docs_hygiene(self):
        rc, out = run_gate(self, REPO, '--list')
        self.assertEqual(rc, 0, out)
        self.assertLessEqual(AREAS, set(out.split()))
        self.assertEqual(len(out.split()), len(set(out.split())))

    def test_unknown_area_exits_2(self):
        rc, out = run_gate(self, REPO, 'android')
        self.assertEqual(rc, 2, out)

    def test_unknown_option_exits_2(self):
        rc, out = run_gate(self, REPO, '--no-such-option')
        self.assertEqual(rc, 2, out)

    def test_git_hooks_invoke_gate_changed(self):
        for hook in ('pre-commit', 'pre-push'):
            with self.subTest(hook=hook):
                path = REPO / '.githooks' / hook
                self.assertTrue(path.is_file(), f'.githooks/{hook} is missing')
                self.assertTrue(os.access(path, os.X_OK), f'.githooks/{hook} is not executable')
                text = path.read_text(encoding='utf-8')
                self.assertRegex(text, r'tools/ci/gate\.sh[^\n]*--changed')
                self.assertIsNone(DIRECT_CHECKS.search(text), f'.githooks/{hook} calls a check directly')

    def test_ci_area_jobs_invoke_gate_with_their_area(self):
        workflow = REPO / '.github' / 'workflows' / 'ci.yml'
        self.assertTrue(workflow.is_file(), '.github/workflows/ci.yml is missing')
        try:
            import yaml
        except ImportError:
            self.fail('PyYAML is required to read ci.yml')
        jobs = yaml.safe_load(workflow.read_text(encoding='utf-8')).get('jobs', {})
        rc, listed = run_gate(self, REPO, '--list')
        self.assertEqual(rc, 0, listed)
        self.assertEqual(set(jobs) - {'changes'}, set(listed.split()))
        self.assertLessEqual(AREAS, set(jobs))
        for area in AREAS:
            with self.subTest(area=area):
                runs = '\n'.join(str(step.get('run', '')) for step in jobs[area].get('steps', []))
                self.assertIn(f'bash tools/ci/gate.sh {area}', runs.splitlines())
                self.assertIsNone(DIRECT_CHECKS.search(runs), f'job {area} calls a check directly')

    def test_hygiene_exits_0_on_clean_copy_and_1_on_seeded_finding(self):
        repo = copy_repo(self.tmp / 'repo')
        rc, out = run_gate(self, repo, 'hygiene')
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: hygiene: PASS', out)
        write(repo, {'notes.md': f'first line\n{home_path()}\n'})
        commit_all(repo)
        rc, out = run_gate(self, repo, 'hygiene')
        self.assertEqual(rc, 1, out)
        self.assertIn('gate: hygiene: FAIL', out)

    def test_hygiene_whitespace_finding_reports_rule_ids_without_line_text(self):
        repo = copy_repo(self.tmp / 'repo')
        fake = 'AKIA' + secrets.token_hex(8).upper()  # generated fake credential shape
        write(repo, {'notes.md': f'first line\naws_key = {fake}   \n'})
        git(repo, 'add', 'notes.md')
        rc, out = run_gate(self, repo, 'hygiene')
        self.assertEqual(rc, 1, out)
        self.assertNotIn(fake, out, 'hygiene output echoed the staged line text')
        findings = [line for line in out.splitlines() if not line.startswith('gate: ')
                    and line != 'WS-CHECK: no origin/main; checking uncommitted changes only']
        self.assertTrue(findings, out)
        for line in findings:
            self.assertRegex(line, r'^[^:]+:[0-9]+:[A-Z0-9-]+$')

    def test_hygiene_whitespace_finding_does_not_echo_colon_shaped_line_text(self):
        repo = copy_repo(self.tmp / 'repo')
        token = 'review_' + secrets.token_hex(8)  # content shaped like a file:line location
        write(repo, {'notes.md': f'first line\n{token}:123:payload   \n'})
        git(repo, 'add', 'notes.md')
        rc, out = run_gate(self, repo, 'hygiene')  # out is stdout + stderr
        self.assertEqual(rc, 1, out.replace(token, '<token>'))
        self.assertFalse(token in out, 'hygiene output echoed colon-shaped staged line text:\n'
                         + out.replace(token, '<token>'))

    def test_hygiene_whitespace_finding_keeps_location_for_plus_leading_filename(self):
        # B1-R1: git's header for a file named "+..." starts with "+" like a content line.
        repo = copy_repo(self.tmp / 'repo')
        token = 'review_' + secrets.token_hex(8) + ':7:payload'
        write(repo, {'+plus.txt': f'{token}   \n'})
        git(repo, 'add', '+plus.txt')
        rc, out = run_gate(self, repo, 'hygiene')  # out is stdout + stderr
        shown = out.replace(token, '<token>')
        self.assertEqual(rc, 1, shown)
        self.assertFalse(token in out, 'hygiene output echoed staged line text:\n' + shown)
        self.assertTrue('+plus.txt:1:WS-CHECK' in out.splitlines(),
                        'hygiene finding lost its +plus.txt location:\n' + shown)

    def test_committed_evidence_whitespace_fails_locally_and_in_ci(self):
        evidence = ('docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/'
                    'evidence/P2-A02T/cmd-red.txt')
        for mode in ('local', 'pull_request', 'push'):
            with self.subTest(mode=mode):
                repo = copy_repo(self.tmp / mode)
                base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo,
                                               text=True).strip()
                write(repo, {evidence: 'first line\nDaemon will be stopped at the end of the build \n'})
                commit_all(repo)
                env = dict(os.environ, CI='', GITHUB_ACTIONS='')
                args = ('--changed=' + base, 'hygiene')
                if mode != 'local':
                    # Reproduce checkout's depth-1 clean tree; fetch the event base from a real remote.
                    clone = self.tmp / (mode + '-shallow')
                    git(self.tmp, 'clone', '-q', '--depth=1', repo.as_uri(), str(clone))
                    repo = clone
                    event = self.tmp / (mode + '.json')
                    payload = ({'pull_request': {'base': {'sha': base}}}
                               if mode == 'pull_request' else {'before': base})
                    event.write_text(json.dumps(payload), encoding='utf-8')
                    env.update(CI='true', GITHUB_ACTIONS='true', GITHUB_EVENT_PATH=str(event))
                    args = ('hygiene',)
                rc, out = run_gate(self, repo, *args, env=env)
                self.assertEqual(rc, 1, out)
                self.assertIn(evidence + ':2:WS-CHECK', out.splitlines())
                self.assertNotIn('Daemon will be stopped', out)
                write(repo, {evidence: 'first line\nDaemon will be stopped at the end of the build\n'})
                commit_all(repo)
                rc, out = run_gate(self, repo, *args, env=env)
                self.assertEqual(rc, 0, out)
                self.assertIn('gate: hygiene: PASS', out)

    def test_ci_base_without_fetch_access_fails_closed_or_uses_checkout_history(self):
        import yaml
        workflow = yaml.safe_load((REPO / '.github/workflows/ci.yml').read_text(encoding='utf-8'))
        checkout = next(step for step in workflow['jobs']['hygiene']['steps']
                        if step.get('uses', '').startswith('actions/checkout@'))
        self.assertIs(checkout['with']['persist-credentials'], False)
        depth = checkout['with'].get('fetch-depth', 1)
        source = copy_repo(self.tmp / 'source')
        base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source,
                                       text=True).strip()
        write(source, {'committed.txt': 'trailing space \n'})
        commit_all(source)
        for mode in ('pull_request', 'push'):
            for full_history in (False, True):
                with self.subTest(mode=mode, full_history=full_history):
                    clone = self.tmp / f'{mode}-{full_history}'
                    clone_depth = depth if full_history else 1
                    args = [] if clone_depth == 0 else [f'--depth={clone_depth}']
                    git(self.tmp, 'clone', '-q', *args, source.as_uri(), str(clone))
                    # Deny the real transport after checkout, like a private remote without auth.
                    git(clone, 'config', 'protocol.file.allow', 'never')
                    event = self.tmp / f'{mode}-{full_history}.json'
                    payload = ({'pull_request': {'base': {'sha': base}}}
                               if mode == 'pull_request' else {'before': base})
                    event.write_text(json.dumps(payload), encoding='utf-8')
                    env = dict(os.environ, CI='true', GITHUB_ACTIONS='true',
                               GITHUB_EVENT_PATH=str(event))
                    rc, out = run_gate(self, clone, 'hygiene', env=env)
                    self.assertEqual(rc, 1, out)
                    if full_history:
                        self.assertIn('committed.txt:1:WS-CHECK', out.splitlines())
                        self.assertNotIn('CI base unavailable', out)
                        write(clone, {'committed.txt': 'no trailing space\n'})
                        commit_all(clone)
                        rc, out = run_gate(self, clone, 'hygiene', env=env)
                        self.assertEqual(rc, 0, out)
                    else:
                        self.assertIn('WS-CHECK: CI base unavailable', out.splitlines())
                        self.assertNotIn('gate: hygiene: PASS', out)

    def test_local_without_origin_main_announces_uncommitted_only_fallback(self):
        repo = copy_repo(self.tmp / 'repo')
        write(repo, {'committed.txt': 'trailing space \n'})
        commit_all(repo)
        env = dict(os.environ, CI='', GITHUB_ACTIONS='')
        rc, out = run_gate(self, repo, 'hygiene', env=env)
        self.assertEqual(rc, 0, out)
        note = 'WS-CHECK: no origin/main; checking uncommitted changes only'
        self.assertEqual(out.splitlines().count(note), 1, out)
        write(repo, {'uncommitted.txt': 'trailing space \n'})
        git(repo, 'add', 'uncommitted.txt')
        rc, out = run_gate(self, repo, 'hygiene', env=env)
        self.assertEqual(rc, 1, out)
        self.assertIn('uncommitted.txt:1:WS-CHECK', out.splitlines())

    def test_docs_area_exits_1_on_seeded_broken_link(self):
        repo = copy_repo(self.tmp / 'repo')
        write(repo, {'BROKEN.md': '# Broken\n\n[gone](docs/does-not-exist.md)\n'})
        commit_all(repo)
        rc, out = run_gate(self, repo, 'docs')
        self.assertEqual(rc, 1, out)
        self.assertIn('gate: docs: FAIL', out)

    def test_copy_repo_preserves_spec_linked_documents_and_omits_untracked_files(self):
        upstream = copy_repo(self.tmp / 'upstream')
        source = upstream / 'spec' / 'demo'
        shutil.copytree(upstream / 'tools' / 'spec' / 'template', source)
        section = source / '01-introduction.md'
        section.write_text(section.read_text(encoding='utf-8')
                           + '\n[Plan](../../docs/plans/fixture.md)\n', encoding='utf-8')
        write(upstream, {'docs/plans/fixture.md': '# Fixture plan\n'})
        commit_all(upstream)
        write(upstream, {'docs/plans/untracked.txt': 'Untracked content must stay out.\n'})
        # Select a real Git fixture as the copy source; the copier and docs gate are unchanged.
        with patch('gate_support.REPO', upstream):
            repo = copy_repo(self.tmp / 'copy')
        rc, out = run_gate(self, repo, 'docs')
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: docs: PASS', out)
        self.assertEqual((repo / 'docs/plans/fixture.md').read_text(encoding='utf-8'),
                         '# Fixture plan\n')
        self.assertFalse((repo / 'docs/plans/untracked.txt').exists())

    def test_missing_tools_spec_exits_3_with_gap(self):
        repo = copy_repo(self.tmp / 'repo')
        shutil.rmtree(repo / 'tools' / 'spec')
        commit_all(repo)
        rc, out = run_gate(self, repo, 'spec')
        self.assertEqual(rc, 3, out)
        self.assertIn('gate: spec: GAP', out)


class AC_AFC_CI_04_Spec(unittest.TestCase):
    """spec area: lint, figure lint and byte-identical rebuild per spec/<name>/;
    template self-check in a removed temp dir while none exists."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = copy_repo(self.tmp / 'repo')

    def add_spec(self, name='demo'):
        shutil.copytree(self.repo / 'tools' / 'spec' / 'template', self.repo / 'spec' / name)
        commit_all(self.repo)
        return self.repo / 'spec' / name

    def built_files(self):
        """Files the spec area's rebuild wrote into the work tree (new or changed)."""
        status = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=all', '-z'],
                                cwd=self.repo, check=True, capture_output=True).stdout.decode()
        paths = [entry[3:] for entry in status.split('\0') if entry]
        return [p for p in paths if p.endswith('.md')
                and 'Generated by `spec_build.py`' in (self.repo / p).read_text(encoding='utf-8')]

    def test_template_self_check_passes_and_removes_temp_dir(self):
        scratch = self.tmp / 'scratch'
        scratch.mkdir()
        env = dict(os.environ, TMPDIR=str(scratch))
        rc, out = run_gate(self, self.repo, 'spec', env=env)
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: spec: PASS', out)
        self.assertEqual(list(scratch.iterdir()), [], 'template temp dir was not removed')

    def test_fresh_build_passes_and_stale_build_exits_1(self):
        source = self.add_spec()
        run_gate(self, self.repo, 'spec')  # first run writes the built file
        built = self.built_files()
        self.assertTrue(built, 'spec area rebuild wrote no built file into the work tree')
        commit_all(self.repo)
        rc, out = run_gate(self, self.repo, 'spec')
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: spec: PASS', out)
        # Append rather than edit template prose: the vendored template changes upstream.
        section = sorted(source.glob('*.md'))[0]
        before = section.read_text(encoding='utf-8')
        section.write_text(before.rstrip('\n') + '\n\nStale-build marker sentence added by the gate test.\n',
                           encoding='utf-8')
        self.assertNotEqual(section.read_text(encoding='utf-8'), before, 'stale edit did not change the source')
        commit_all(self.repo)
        rc, out = run_gate(self, self.repo, 'spec')
        self.assertEqual(rc, 1, out)
        self.assertIn('gate: spec: FAIL', out)

    def test_spec_lint_finding_exits_1(self):
        source = self.add_spec()
        write(source, {'08-bad.md': 'no front matter\n'})
        commit_all(self.repo)
        rc, out = run_gate(self, self.repo, 'spec')
        self.assertEqual(rc, 1, out)
        self.assertIn('gate: spec: FAIL', out)

    def build_spec(self, source):
        output = source / f'{source.name}.md'
        result = subprocess.run(['uv', 'run', '--script', 'tools/spec/spec_build.py',
                                 str(source), str(output)], cwd=self.repo,
                                capture_output=True, text=True, timeout=900)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return output

    def stage_source_change(self):
        source = self.add_spec()
        self.build_spec(source)
        commit_all(self.repo)
        section = source / '01-introduction.md'
        section.write_text(section.read_text(encoding='utf-8')
                           + '\nStaged-source marker sentence added by the gate test.\n', encoding='utf-8')
        git(self.repo, 'add', str(section.relative_to(self.repo)))
        return source

    def test_staged_source_and_rebuilt_output_pass_before_commit(self):
        source = self.stage_source_change()
        output = self.build_spec(source)
        git(self.repo, 'add', str(output.relative_to(self.repo)))
        rc, out = run_gate(self, self.repo, 'spec')
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: spec: PASS', out)

    def test_staged_source_without_rebuilt_output_exits_1(self):
        self.stage_source_change()
        rc, out = run_gate(self, self.repo, 'spec')
        self.assertEqual(rc, 1, out)
        self.assertIn('gate: spec: FAIL', out)

    def test_missing_dot_exits_3_with_gap(self):
        env = dict(os.environ, PATH=path_without('dot', self.tmp / 'bin'))
        rc, out = run_gate(self, self.repo, 'spec', env=env)
        self.assertEqual(rc, 3, out)
        self.assertIn('gate: spec: GAP', out)


if __name__ == '__main__':
    unittest.main()
