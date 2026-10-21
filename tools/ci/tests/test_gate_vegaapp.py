"""CMD-GATE-VEGAAPP / DES-AFC-P2-VEGA: gate area `vegaapp` (P2-V01T red; P2-V01 adds it).

Resource group: host-gate-fixtures, no engine, network, VVD or device. Protocol
fixtures put a recording `npm` and `node` on PATH; the real Jest run is
CMD-VEGA-UNIT, never this test. `.vpkg` builds and VVD runs are SEIT
procedures and must never run in the gate.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from gate_support import REPO, commit_all, copy_repo, git_output, path_without, run_gate, write

PACKAGE = '{"name": "fixture", "private": true, "scripts": {"test": "jest"}}\n'


class VegaAppGate(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def repo(self, name, tree=True):
        repo = copy_repo(self.tmp / name)
        shutil.rmtree(repo / 'vega-app', ignore_errors=True)
        if tree:
            write(repo, {'vega-app/package.json': PACKAGE})
        commit_all(repo)
        return repo

    def protocol(self, repo, npm=0):
        # Recording tools stand in for node/npm; their exit codes are the only stimulus.
        bin_dir = repo / 'fixture-bin'
        write(bin_dir, {
            'npm': '#!/bin/bash\nprintf "%s\\n" "$*" >> "$AFC_COMMAND_LOG"\n' f'exit {npm}\n',
            'node': '#!/bin/bash\nexit 0\n',
        })
        for tool in ('npm', 'node'):
            (bin_dir / tool).chmod(0o755)
        return dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'],
                    AFC_COMMAND_LOG=str(repo / 'commands.log'), CI='true')

    def commands(self, repo):
        log = repo / 'commands.log'
        return log.read_text().splitlines() if log.exists() else []

    def test_list_includes_vegaapp(self):
        rc, out = run_gate(self, REPO, '--list')
        self.assertEqual(rc, 0, out)
        self.assertIn('vegaapp', out.split())

    def test_absent_tree_passes_with_exact_no_tree_detail(self):
        repo = self.repo('absent', tree=False)
        rc, out = run_gate(self, repo, 'vegaapp')
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: vegaapp: PASS no vega-app/ tree', out.splitlines())

    def test_runs_npm_ci_then_jest_ci(self):
        repo = self.repo('protocol')
        rc, out = run_gate(self, repo, 'vegaapp', env=self.protocol(repo))
        self.assertEqual(rc, 0, out)
        self.assertIn('gate: vegaapp: PASS checks completed', out.splitlines())
        self.assertEqual(self.commands(repo), ['--prefix vega-app ci', '--prefix vega-app test -- --ci'])

    def test_failing_jest_is_fail_not_gap(self):
        # A tool's own exit 3 must never read as a missing-tool GAP.
        for npm in (1, 3):
            with self.subTest(npm=npm):
                repo = self.repo(f'fail-{npm}')
                rc, out = run_gate(self, repo, 'vegaapp', env=self.protocol(repo, npm=npm))
                self.assertEqual(rc, 1, out)
                self.assertIn('gate: vegaapp: FAIL', out)
                self.assertNotIn('gate: vegaapp: GAP', out)
                self.assertNotIn('gate: vegaapp: PASS', out)

    def test_missing_node_or_npm_is_named_gap_exit_3(self):
        for tool in ('node', 'npm'):
            with self.subTest(tool=tool):
                repo = self.repo('missing-' + tool)
                env = self.protocol(repo)
                (repo / 'fixture-bin' / tool).unlink()
                env['PATH'] = str(repo / 'fixture-bin') + os.pathsep + path_without(tool, self.tmp / ('bin-' + tool))
                rc, out = run_gate(self, repo, 'vegaapp', env=env)
                self.assertEqual(rc, 3, out)
                self.assertIn('gate: vegaapp: GAP', out)
                self.assertIn(tool, out)
                self.assertNotIn('gate: vegaapp: PASS', out)
                self.assertEqual(self.commands(repo), [])

    def test_empty_tree_never_claims_no_tree_or_passes(self):
        repo = self.repo('empty', tree=False)
        (repo / 'vega-app').mkdir()
        rc, out = run_gate(self, repo, 'vegaapp')
        self.assertIn(rc, (1, 3), out)
        self.assertNotIn('no vega-app/ tree', out)
        self.assertNotIn('gate: vegaapp: PASS', out)

    def test_changed_paths_select_vegaapp(self):
        for changed, selected in (('vega-app/src/a.ts', True), ('tools/ci/gate.sh', True), ('tv-app/a.txt', False)):
            with self.subTest(changed=changed):
                repo = self.repo('changed-' + changed.replace('/', '-'))
                base = git_output(repo, 'rev-parse', 'HEAD')
                path = repo / changed
                write(repo, {changed: (path.read_text() if path.exists() else '') + '# fixture\n'})
                commit_all(repo, 'change')
                rc, out = run_gate(self, repo, f'--changed={base}..HEAD', 'vegaapp', env=self.protocol(repo))
                self.assertEqual('gate: vegaapp:' in out, selected, out)
                if selected:
                    self.assertEqual(rc, 0, out)
                    self.assertIn('gate: vegaapp: PASS checks completed', out.splitlines())

    def test_openapi_change_selects_both_client_contract_mirrors(self):
        # Both shellContract mirror tests read backend/src/api/openapi.yaml.
        cases = (('backend/src/api/openapi.yaml', {'tvapp', 'vegaapp'}),
                 ('backend/src/api/handler.py', set()))
        for index, (changed, selected) in enumerate(cases):
            with self.subTest(changed=changed):
                repo = self.repo(f'openapi-{index}')
                base = git_output(repo, 'rev-parse', 'HEAD')
                path = repo / changed
                write(repo, {changed: (path.read_text() if path.exists() else '') + '# fixture\n'})
                commit_all(repo, 'change')
                rc, out = run_gate(self, repo, f'--changed={base}..HEAD', 'tvapp', 'vegaapp',
                                   env=self.protocol(repo))
                self.assertEqual(rc, 0, out)
                for area in ('tvapp', 'vegaapp'):
                    self.assertEqual(f'gate: {area}:' in out, area in selected, out)
        workflow = yaml.safe_load((REPO / '.github/workflows/ci.yml').read_text())
        filters = yaml.safe_load(next(s['with']['filters'] for s in workflow['jobs']['changes']['steps']
                                      if s.get('id') == 'filter'))
        for area in ('tvapp', 'vegaapp'):
            with self.subTest(filter=area):
                self.assertIn('backend/src/api/openapi.yaml', filters[area])
                self.assertNotIn('backend/src/api/handler.py', filters[area])

    def test_ci_workflow_runs_a_path_filtered_vegaapp_job(self):
        workflow = yaml.safe_load((REPO / '.github/workflows/ci.yml').read_text())
        changes = workflow['jobs']['changes']
        self.assertIn('vegaapp', changes['outputs'])
        step = next(s for s in changes['steps'] if s.get('id') == 'filter')
        filters = yaml.safe_load(step['with']['filters'])
        self.assertIn('vega-app/**', filters.get('vegaapp', []))
        job = workflow['jobs'].get('vegaapp')
        self.assertIsNotNone(job, 'jobs.vegaapp missing')
        self.assertEqual(job['name'], 'gate / vegaapp')
        self.assertEqual(job['if'], "${{ needs.changes.outputs.vegaapp == 'true' }}")
        self.assertIn('bash tools/ci/gate.sh vegaapp', [s.get('run') for s in job['steps']])


if __name__ == '__main__':
    unittest.main()
