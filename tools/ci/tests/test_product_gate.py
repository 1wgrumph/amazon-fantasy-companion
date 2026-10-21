"""CONTRACT-AFC-P2-GATE-AREAS / SEIT-AFC-P2-GATE-01.

Resource group: host-gate-fixtures, no engine, AWS or device. Command protocol
fixtures use observed shell exit 0/1, not fabricated Gradle/cfn-lint reports.
Native Android and cfn-lint qualification remains a separate typed gap.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

from gate_support import REPO, commit_all, copy_repo, path_without, run_gate, write

AREAS = {'spec', 'docs', 'hygiene', 'tvapp', 'backend', 'vegaapp'}
TREES = {'tvapp': 'tv-app', 'backend': 'backend'}


class ProductGate(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def repo(self, name):
        return copy_repo(self.tmp / name)

    def protocol(self, repo, gradle=0, lint=0, pytest=0):
        # Shell exit controls were exercised directly before freezing this corpus.
        write(repo, {
            'tv-app/gradlew': '#!/bin/bash\nprintf "%s\\n" "$*" >> "$AFC_COMMAND_LOG"\n'
                              f'exit {gradle}\n',
            'backend/tests/unit/test_control.py': f'def test_control():\n    assert {pytest} == 0\n',
            'backend/tests/contract/test_contract.py': 'def test_contract():\n    assert True\n',
            'backend/tests/deployed/test_forbidden.py': 'raise AssertionError("deployed tests ran")\n',
            'backend/template.yaml': 'AWSTemplateFormatVersion: "2010-09-09"\nResources: {}\n',
        })
        (repo / 'tv-app/gradlew').chmod(0o755)
        bin_dir = repo / 'fixture-bin'
        write(bin_dir, {'cfn-lint': '#!/bin/bash\nprintf "%s\\n" "$*" >> "$AFC_COMMAND_LOG"\n'
                                   f'exit {lint}\n'})
        (bin_dir / 'cfn-lint').chmod(0o755)
        sdk = repo / 'fixture-sdk'
        sdk.mkdir()
        env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'],
                   ANDROID_HOME=str(sdk), ANDROID_SDK_ROOT=str(sdk),
                   AFC_COMMAND_LOG=str(repo / 'commands.log'), PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',
                   CI='true')
        return env

    def local_toolchain(self, repo):
        env = self.protocol(repo)
        for key in ('JAVA_HOME', 'ANDROID_HOME', 'ANDROID_SDK_ROOT', 'CI', 'GITHUB_ACTIONS'):
            env.pop(key, None)
        home = repo / 'user home'
        tools = home / '.local/share/afc-tools'
        write(tools, {'jdk-17.fixture/bin/java': '#!/bin/sh\nexit 0\n'})
        (tools / 'jdk-17.fixture/bin/java').chmod(0o755)
        (tools / 'android-sdk').mkdir()
        env['HOME'] = str(home)
        write(repo, {'tv-app/gradlew': '#!/bin/bash\n'
                    'printf "%s\\n" "$JAVA_HOME" "$ANDROID_HOME" "$ANDROID_SDK_ROOT" '
                    '> "$AFC_COMMAND_LOG"\n'})
        return env, tools

    def test_local_tvapp_discovers_user_toolchain_without_env(self):
        repo = self.repo('local-toolchain')
        env, tools = self.local_toolchain(repo)
        rc, out = run_gate(self, repo, 'tvapp', env=env)
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: tvapp: PASS', out)
        self.assertEqual((repo / 'commands.log').read_text().splitlines(),
                         [str(tools / 'jdk-17.fixture'), str(tools / 'android-sdk'), ''])

    def test_local_tvapp_uses_path_java_without_user_jdk(self):
        repo = self.repo('local-path-java')
        env, tools = self.local_toolchain(repo)
        java = tools / 'jdk-17.fixture/bin/java'
        java.rename(repo / 'fixture-bin/java')
        shutil.rmtree(java.parents[1])
        env['PATH'] = str(repo / 'fixture-bin') + os.pathsep + path_without(
            'java', self.tmp / 'no-host-java')
        rc, out = run_gate(self, repo, 'tvapp', env=env)
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: tvapp: PASS', out)
        self.assertEqual((repo / 'commands.log').read_text().splitlines(),
                         ['', str(tools / 'android-sdk'), ''])

    def test_local_tvapp_explicit_toolchain_wins(self):
        for sdk_var in ('ANDROID_HOME', 'ANDROID_SDK_ROOT'):
            with self.subTest(sdk_var=sdk_var):
                repo = self.repo('explicit-' + sdk_var)
                env, tools = self.local_toolchain(repo)
                write(repo, {'explicit-jdk/bin/java': '#!/bin/sh\nexit 0\n'})
                (repo / 'explicit-jdk/bin/java').chmod(0o755)
                (repo / 'explicit-sdk').mkdir()
                env.update(JAVA_HOME=str(repo / 'explicit-jdk'))
                env[sdk_var] = str(repo / 'explicit-sdk')
                rc, out = run_gate(self, repo, 'tvapp', env=env)
                self.assertEqual(rc, 0, out)
                self.assertEqual((repo / 'commands.log').read_text().splitlines(),
                                 [env['JAVA_HOME'], env.get('ANDROID_HOME', ''),
                                  env.get('ANDROID_SDK_ROOT', '')])

    def test_local_tvapp_missing_or_ambiguous_jdk_is_gap(self):
        for case in ('absent', 'nonexecutable', 'wrong-version', 'ambiguous'):
            with self.subTest(case=case):
                repo = self.repo(case)
                env, tools = self.local_toolchain(repo)
                env['PATH'] = path_without('java', self.tmp / ('no-java-' + case))
                java = tools / 'jdk-17.fixture/bin/java'
                if case == 'absent':
                    shutil.rmtree(java.parents[1])
                elif case == 'nonexecutable':
                    java.chmod(0o644)
                else:
                    shutil.copytree(java.parents[1], tools / 'jdk-17.second')
                    if case == 'wrong-version':
                        shutil.rmtree(java.parents[1])
                        (tools / 'jdk-17.second').rename(tools / 'jdk-21.fixture')
                rc, out = run_gate(self, repo, 'tvapp', env=env)
                self.assertEqual(rc, 3, out)
                self.assertIn('required tool missing: java', out)
                self.assertFalse((repo / 'commands.log').exists())

    def test_local_tvapp_missing_sdk_is_gap(self):
        repo = self.repo('local-missing-sdk')
        env, tools = self.local_toolchain(repo)
        (tools / 'android-sdk').rmdir()
        rc, out = run_gate(self, repo, 'tvapp', env=env)
        self.assertEqual(rc, 3, out)
        self.assertIn('required tool missing: Android SDK', out)
        self.assertFalse((repo / 'commands.log').exists())

    def test_ci_tvapp_ignores_user_toolchain(self):
        for ci_var in ('CI', 'GITHUB_ACTIONS'):
            with self.subTest(ci_var=ci_var):
                repo = self.repo('ci-' + ci_var)
                env, tools = self.local_toolchain(repo)
                env[ci_var] = 'true'
                env['PATH'] = path_without('java', self.tmp / ('no-java-' + ci_var))
                rc, out = run_gate(self, repo, 'tvapp', env=env)
                self.assertEqual(rc, 3, out)
                self.assertIn('required tool missing: java', out)
                env['JAVA_HOME'] = str(tools / 'jdk-17.fixture')
                rc, out = run_gate(self, repo, 'tvapp', env=env)
                self.assertEqual(rc, 3, out)
                self.assertIn('required tool missing: Android SDK', out)
                self.assertFalse((repo / 'commands.log').exists())

    def test_list_includes_exact_product_and_legacy_areas(self):
        rc, out = run_gate(self, REPO, '--list')
        self.assertEqual(rc, 0, out)
        self.assertEqual(set(out.split()), AREAS)

    def test_absent_tree_passes_with_exact_no_tree_detail(self):
        for area, tree in TREES.items():
            with self.subTest(area=area):
                repo = self.repo(area)
                self.assertFalse((repo / tree).exists())
                rc, out = run_gate(self, repo, area)
                self.assertEqual(rc, 0, out)
                self.assertIn(f'gate: {area}: PASS no {tree}/ tree', out.splitlines())

    def test_empty_tree_never_claims_no_tree_or_passes(self):
        for area, tree in TREES.items():
            with self.subTest(area=area):
                repo = self.repo(area)
                (repo / tree).mkdir()
                rc, out = run_gate(self, repo, area)
                self.assertIn(rc, (1, 3), out)
                self.assertNotIn(f'no {tree}/ tree', out)
                self.assertNotIn(f'gate: {area}: PASS', out)

    def test_missing_executable_is_exact_named_gap_exit_3(self):
        for area, tool in [('tvapp', 'java'), ('backend', 'python3.12'), ('backend', 'cfn-lint')]:
            with self.subTest(area=area, tool=tool):
                repo = self.repo(area + '-' + tool)
                env = self.protocol(repo)
                env['PATH'] = path_without(tool, self.tmp / ('bin-' + tool))
                if tool == 'java':
                    env.pop('JAVA_HOME', None)
                rc, out = run_gate(self, repo, area, env=env)
                self.assertEqual(rc, 3, out)
                self.assertIn(f'gate: {area}: GAP', out)
                self.assertIn(tool, out)
                self.assertNotIn(f'gate: {area}: PASS', out)

    def test_missing_android_sdk_is_named_gap_exit_3(self):
        repo = self.repo('sdk')
        env = self.protocol(repo)
        for key in ('ANDROID_HOME', 'ANDROID_SDK_ROOT'):
            env.pop(key, None)
        rc, out = run_gate(self, repo, 'tvapp', env=env)
        self.assertEqual(rc, 3, out)
        self.assertIn('gate: tvapp: GAP', out)
        self.assertRegex(out, r'(?i)android|sdk')

    def test_successful_subchecks_pass_and_receive_contract_arguments(self):
        for area in TREES:
            with self.subTest(area=area):
                repo = self.repo(area)
                env = self.protocol(repo)
                rc, out = run_gate(self, repo, area, env=env)
                self.assertEqual(rc, 0, out)
                self.assertIn(f'gate: {area}: PASS', out)
                self.assertNotIn('no ', out)
                self.assertTrue((repo / 'commands.log').is_file(), out)
                logged = (repo / 'commands.log').read_text().splitlines()
                self.assertIn('-p tv-app testDebugUnitTest lintDebug assembleDebug'
                              if area == 'tvapp' else 'backend/template.yaml', logged)
                if area == 'backend':
                    self.assertIn('2 passed', out)
                    self.assertNotIn('deployed tests ran', out)

    def test_each_failing_subcheck_exits_1_and_reports_fail(self):
        for area, failures in [('tvapp', {'gradle': 1}),
                               ('backend', {'pytest': 1}), ('backend', {'lint': 1})]:
            with self.subTest(area=area, failures=failures):
                repo = self.repo(area + '-' + next(iter(failures)))
                env = self.protocol(repo, **failures)
                rc, out = run_gate(self, repo, area, env=env)
                self.assertEqual(rc, 1, out)
                self.assertIn(f'gate: {area}: FAIL', out)
                self.assertNotIn(f'gate: {area}: PASS', out)

    def test_changed_selection_matches_product_paths_and_shared_gate_paths(self):
        cases = [('tv-app/marker.txt', {'tvapp'}), ('backend/marker.txt', {'backend'}),
                 ('tools/ci/marker.txt', set(TREES)), ('.githooks/marker.txt', set(TREES)),
                 ('.github/workflows/marker.txt', set(TREES)), ('unrelated.txt', set())]
        for index, (path, selected) in enumerate(cases):
            with self.subTest(path=path):
                repo = self.repo(str(index))
                env = self.protocol(repo)
                commit_all(repo)
                write(repo, {path: 'changed selection fixture\n'})
                rc, out = run_gate(self, repo, '--changed=HEAD', 'tvapp', 'backend', env=env)
                self.assertEqual(rc, 0, out)
                for area in TREES:
                    self.assertEqual(f'gate: {area}:' in out, area in selected, out)
                self.assertIn('gate: hygiene: PASS', out)


class ProductWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflow = yaml.safe_load((REPO / '.github/workflows/ci.yml').read_text())
        self.jobs = self.workflow['jobs']

    def test_product_jobs_have_stable_names_gate_invocations_and_path_conditions(self):
        self.assertEqual(set(self.jobs) - {'changes'}, AREAS)
        for area in TREES:
            with self.subTest(area=area):
                job = self.jobs[area]
                self.assertEqual(job['name'], f'gate / {area}')
                self.assertIn(job.get('needs'), ('changes', ['changes']))
                self.assertEqual(job.get('if'), "${{ needs.changes.outputs." + area + " == 'true' }}")
                self.assertIn(f'bash tools/ci/gate.sh {area}', [s.get('run') for s in job['steps']])

    def test_product_filters_outputs_and_shared_paths_are_bound(self):
        changes = self.jobs['changes']
        filters = yaml.safe_load(next(s['with']['filters'] for s in changes['steps']
                                      if s.get('id') == 'filter'))
        self.assertEqual(set(filters), AREAS - {'hygiene'})
        for area, tree in TREES.items():
            with self.subTest(area=area):
                self.assertEqual(changes['outputs'][area], '${{ steps.filter.outputs.' + area + ' }}')
                self.assertLessEqual({tree + '/**', 'tools/ci/**', '.githooks/**',
                                      '.github/workflows/**'}, set(filters[area]))

    def test_setup_actions_are_sha_pinned_with_jdk17_and_python312(self):
        for area, action, key, value in [('tvapp', 'actions/setup-java', 'java-version', '17'),
                                          ('backend', 'actions/setup-python', 'python-version', '3.12')]:
            with self.subTest(area=area):
                self.assertIn(area, self.jobs, f'missing {area} job')
                steps = self.jobs[area]['steps']
                setup = [s for s in steps if str(s.get('uses', '')).startswith(action + '@')]
                self.assertEqual(len(setup), 1, f'missing/duplicate {action}')
                self.assertEqual(str(setup[0].get('with', {}).get(key)), value)
                for step in steps:
                    if 'uses' in step:
                        self.assertRegex(step['uses'], r'^[\w./-]+@[0-9a-fA-F]{40}$')
        self.assertEqual(self.workflow['permissions'], {'contents': 'read'})
        self.assertIs(self.workflow['concurrency']['cancel-in-progress'], True)
        self.assertIn('${{ github.ref }}', self.workflow['concurrency']['group'])


if __name__ == '__main__':
    unittest.main()
