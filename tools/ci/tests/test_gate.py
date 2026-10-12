"""Gate entrypoint tests: AC-AFC-CI-01 (SEIT-AFC-CI-01.U) and the spec area of
AC-AFC-CI-04 (SEIT-AFC-CI-04.U), per CONTRACT-AFC-GATE and DES-AFC-GATE."""

import os
import re
import secrets
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

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
        self.assertEqual(sorted(out.split()), sorted(AREAS))

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
        self.assertEqual(set(jobs) - {'changes'}, AREAS)
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
        findings = [line for line in out.splitlines() if not line.startswith('gate: ')]
        self.assertTrue(findings, out)
        for line in findings:
            self.assertRegex(line, r'^[^:]+:[0-9]+:[A-Z0-9-]+$')

    def test_docs_area_exits_1_on_seeded_broken_link(self):
        repo = copy_repo(self.tmp / 'repo')
        write(repo, {'BROKEN.md': '# Broken\n\n[gone](docs/does-not-exist.md)\n'})
        commit_all(repo)
        rc, out = run_gate(self, repo, 'docs')
        self.assertEqual(rc, 1, out)
        self.assertIn('gate: docs: FAIL', out)

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

    def test_missing_dot_exits_3_with_gap(self):
        env = dict(os.environ, PATH=path_without('dot', self.tmp / 'bin'))
        rc, out = run_gate(self, self.repo, 'spec', env=env)
        self.assertEqual(rc, 3, out)
        self.assertIn('gate: spec: GAP', out)


if __name__ == '__main__':
    unittest.main()
