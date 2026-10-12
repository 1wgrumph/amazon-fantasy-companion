"""Workflow tests: AC-AFC-CI-02 (SEIT-AFC-CI-02.W), per DES-AFC-GATE and
CMD-WORKFLOW-CHECK. The vendored checker runs as a command, as in the gate."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gate_support import REPO

CHECKER = REPO / 'tools' / 'ci' / 'check_workflows.py'
PIN = '93cb6efe18208431cddfb8368fd83d5badbf9bfd'
FILTER_PIN = '0e4a8c6effa4802afeda77dc8d303f8176d7dfad'

VALID = f"""name: CI
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read
concurrency:
  group: ci-${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true
jobs:
  changes:
    name: Detect changes
    runs-on: ubuntu-latest
    outputs:
      spec: ${{{{ steps.filter.outputs.spec }}}}
    steps:
      - uses: actions/checkout@{PIN}
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: dorny/paths-filter@{FILTER_PIN}
        id: filter
        with:
          token: ''
          base: ${{{{ github.event_name == 'pull_request' && github.base_ref || github.ref }}}}
          filters: |
            spec:
              - 'spec/**'
  spec:
    name: gate / spec
    needs: changes
    if: ${{{{ needs.changes.outputs.spec == 'true' }}}}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@{PIN}
        with:
          persist-credentials: false
      - run: tools/ci/gate.sh spec
  hygiene:
    name: gate / hygiene
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@{PIN}
        with:
          persist-credentials: false
      - run: tools/ci/gate.sh hygiene
"""

# rule -> (replace old, new) on VALID, and the word the checker must name.
VIOLATIONS = {
    'pull_request_target trigger': (('  pull_request:\n', '  pull_request_target:\n'), 'triggers'),
    'unpinned action': ((f'actions/checkout@{PIN}\n        with:\n          persist',
                         'actions/checkout@v5\n        with:\n          persist'), 'full commit SHA'),
    'permission wider than contents: read': (('  contents: read\n', '  contents: write\n'), 'permissions'),
    'secret reachable from a fork pull request': (('      - run: tools/ci/gate.sh hygiene\n',
                                                   '      - run: tools/ci/gate.sh hygiene\n'
                                                   '        env:\n          TOKEN: ${{ secrets.TOKEN }}\n'),
                                                  'secrets'),
    'missing cancel-in-progress': (('  cancel-in-progress: true\n', ''), 'concurrency'),
    'self-hosted runner': (('    name: gate / hygiene\n    runs-on: ubuntu-latest\n',
                            '    name: gate / hygiene\n    runs-on: self-hosted\n'), 'runners'),
    'area job without a path filter': (("    needs: changes\n    if: ${{ needs.changes.outputs.spec == 'true' }}\n",
                                        ''), 'paths'),
}


class AC_AFC_CI_02(unittest.TestCase):

    def setUp(self):
        self.assertTrue(CHECKER.is_file(), 'tools/ci/check_workflows.py is missing')
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def check(self, target):
        result = subprocess.run([sys.executable, str(CHECKER), str(target)],
                                capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout + result.stderr

    def test_committed_workflows_pass_the_checker(self):
        rc, out = self.check(REPO / '.github' / 'workflows')
        self.assertEqual(rc, 0, out)
        self.assertIn('ci.yml', out)

    def test_ci_path_filters_cover_each_area(self):
        workflow = REPO / '.github' / 'workflows' / 'ci.yml'
        self.assertTrue(workflow.is_file(), '.github/workflows/ci.yml is missing')
        try:
            import yaml
        except ImportError:
            self.fail('PyYAML is required to read ci.yml')
        changes = yaml.safe_load(workflow.read_text(encoding='utf-8'))['jobs']['changes']
        filters = yaml.safe_load(next(s['with']['filters'] for s in changes['steps'] if s.get('id') == 'filter'))
        self.assertEqual(set(filters), {'spec', 'docs'})
        self.assertLessEqual({'spec/**', 'tools/spec/**'}, set(filters['spec']))
        self.assertIn('docs/**', filters['docs'])
        self.assertTrue(any(p.endswith('*.md') for p in filters['docs']), filters['docs'])

    def test_valid_fixture_passes(self):
        path = self.tmp / 'ci.yml'
        path.write_text(VALID, encoding='utf-8')
        rc, out = self.check(path)
        self.assertEqual(rc, 0, out)

    def test_each_violation_exits_1_naming_its_rule(self):
        for rule, ((old, new), word) in VIOLATIONS.items():
            with self.subTest(rule=rule):
                self.assertIn(old, VALID)
                path = self.tmp / f'{rule.replace(" ", "-").replace(":", "")}.yml'
                path.write_text(VALID.replace(old, new, 1), encoding='utf-8')
                rc, out = self.check(path)
                self.assertEqual(rc, 1, out)
                self.assertIn(word, out)


if __name__ == '__main__':
    unittest.main()
