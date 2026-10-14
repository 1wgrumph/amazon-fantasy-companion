"""PROC-GATE-TOOL-QUALIFY controls for the CMD-MUTATION-TVAPP repo adapter.

Resource group: host-python-report-fixtures; unique temporary git repo per test.
tv-app/gradlew is a fixture standing in for :app:pitestDebug: it writes the PIT
mutations.xml the Android PIT fork would emit (no PIT pin is admitted yet; the
real run's ANDROID_MUTATION_COMPATIBILITY_GAP is evidenced in P2-A01). No engine,
network or device.
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SRC = 'tv-app/app/src/main/java/com/afc/control/Control.kt'
CONTROL = ('package com.afc.control\n\nfun verdict(ok: Boolean): String {\n'
           '    if (ok) return "covered"\n    return "uncovered"\n}\n')
GRADLEW = '''#!/usr/bin/env bash
[[ -n "${FIXTURE_GRADLE_FAIL:-}" ]] && { echo "Task 'pitestDebug' not found"; exit 1; }
[[ -n "${FIXTURE_XML:-}" ]] || exit 0
cd "$(dirname "$0")/.." && mkdir -p tv-app/app/build/reports/pitest/debug \\
    && cp "$FIXTURE_XML" tv-app/app/build/reports/pitest/debug/mutations.xml
'''


def pit(mutants, partial='false'):
    """PIT mutations XML for Control.kt: [(line, status)]."""
    body = ''.join(
        f'<mutation detected="{str(s == "KILLED").lower()}" status="{s}" numberOfTestsRun="1">'
        f'<sourceFile>Control.kt</sourceFile><mutatedClass>com.afc.control.ControlKt</mutatedClass>'
        f'<mutatedMethod>verdict</mutatedMethod><lineNumber>{n}</lineNumber>'
        f'<mutator>org.pitest.mutationtest.engine.gregor.mutators.M{i}</mutator></mutation>'
        for i, (n, s) in enumerate(mutants))
    return f'<?xml version="1.0" encoding="UTF-8"?><mutations partial="{partial}">{body}</mutations>'


def git(cwd, *args):
    return subprocess.run(['git', '-c', 'user.name=Gate Test', '-c', 'user.email=gate-test@example.invalid',
                           '-c', 'commit.gpgsign=false', *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


class TvappMutationAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo, self.out = self.tmp / 'repo', self.tmp / 'out'
        shutil.copytree(REPO / 'tools/ci/mutation', self.repo / 'tools/ci/mutation')
        gradlew = self.repo / 'tv-app/gradlew'
        gradlew.parent.mkdir(parents=True)
        gradlew.write_text(GRADLEW)
        gradlew.chmod(0o755)
        (self.repo / 'tv-app/app/src/main').mkdir(parents=True)
        (self.repo / 'tv-app/app/src/main/AndroidManifest.xml').write_text('<manifest/>\n')
        git(self.repo, 'init', '-q', '-b', 'main')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'base')
        self.base = git(self.repo, 'rev-parse', 'HEAD')
        java = self.tmp / 'jdk/bin/java'
        java.parent.mkdir(parents=True)
        java.write_text('#!/bin/sh\n')
        java.chmod(0o755)
        (self.tmp / 'sdk').mkdir()
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('FIXTURE_')}
        self.env.update(JAVA_HOME=str(self.tmp / 'jdk'), ANDROID_HOME=str(self.tmp / 'sdk'))

    def candidate(self, files=None):
        for rel, text in (files or {SRC: CONTROL}).items():
            path = self.repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'candidate')

    def run_adapter(self, xml=None, **env):
        if xml is not None:
            (self.tmp / 'fixture.xml').write_text(xml)
            env['FIXTURE_XML'] = str(self.tmp / 'fixture.xml')
        result = subprocess.run(['bash', 'tools/ci/mutation/tvapp.sh', self.base, str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=300,
                                env={**self.env, **env})
        out = result.stdout + result.stderr
        print(f'tvapp mutation adapter exit={result.returncode}: {out.strip().splitlines()[-1:]}')
        return result.returncode, out

    def result(self):
        return json.loads((self.out / 'mutation-result.json').read_text())

    def test_killed_changed_mutants_pass(self):
        self.candidate()
        rc, out = self.run_adapter(pit([(4, 'KILLED'), (5, 'KILLED'), (4, 'NON_VIABLE')]))
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.result()['status'], 'PASS')
        self.assertEqual(self.result()['scored_mutants'], 2)
        self.assertEqual(self.result()['invalid'], 1)
        self.assertFalse((self.repo / 'tv-app/app/build').exists(), 'checkout must not be mutated')

    def test_survivor_and_no_coverage_fail_threshold(self):
        self.candidate()
        rc, out = self.run_adapter(pit([(4, 'KILLED'), (5, 'SURVIVED'), (3, 'NO_COVERAGE')]))
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.result()['status'], 'FAIL')
        self.assertAlmostEqual(self.result()['score'], 1 / 3)
        self.assertEqual(len(self.result()['survivors']), 2)

    def test_mutants_off_changed_lines_are_not_scored(self):
        self.candidate()
        base = git(self.repo, 'rev-parse', 'HEAD')
        self.candidate({SRC: CONTROL.replace('"uncovered"', '"missed"')})
        self.base = base
        rc, out = self.run_adapter(pit([(4, 'SURVIVED'), (5, 'KILLED')]))
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.result()['scored_mutants'], 1)

    def test_missing_report_is_gap(self):
        self.candidate()
        rc, out = self.run_adapter()
        self.assertEqual(rc, 3, out)
        self.assertIn('found 0', out)

    def test_pit_run_failure_is_compatibility_gap(self):
        self.candidate()
        rc, out = self.run_adapter(pit([(4, 'KILLED')]), FIXTURE_GRADLE_FAIL='1')
        self.assertEqual(rc, 3, out)
        self.assertIn('ANDROID_MUTATION_COMPATIBILITY_GAP', out)

    def test_unresolved_mutant_is_gap(self):
        self.candidate()
        rc, out = self.run_adapter(pit([(4, 'KILLED'), (5, 'TIMED_OUT')]))
        self.assertEqual(rc, 3, out)
        self.assertIn('UNRESOLVED', out)

    def test_partial_or_unparseable_report_is_gap(self):
        self.candidate()
        rc, out = self.run_adapter(pit([(4, 'KILLED')], partial='true'))
        self.assertEqual(rc, 3, out)
        self.assertIn('not a complete PIT', out)
        rc, out = self.run_adapter('<mutations><mutation')
        self.assertEqual(rc, 3, out)
        self.assertIn('unparseable', out)

    def test_unknown_status_is_gap(self):
        self.candidate()
        rc, out = self.run_adapter(pit([(4, 'KILLED'), (5, 'LUCKY')]))
        self.assertEqual(rc, 3, out)
        self.assertIn('unknown PIT status', out)

    def test_changed_file_without_mutants_is_gap(self):
        self.candidate({SRC: CONTROL, SRC.replace('Control', 'Other'): 'package com.afc.control\n\nfun o() = 1\n'})
        rc, out = self.run_adapter(pit([(4, 'KILLED')]))
        self.assertEqual(rc, 3, out)
        self.assertIn('no mutants for changed files', out)

    def test_zero_scored_mutants_is_gap(self):
        self.candidate()
        rc, out = self.run_adapter(pit([(4, 'NON_VIABLE')]))
        self.assertEqual(rc, 3, out)
        self.assertIn('EMPTY_INVENTORY', out)

    def test_no_changed_source_is_empty_inventory_gap(self):
        self.candidate({'tv-app/app/src/main/AndroidManifest.xml': '<manifest package="x"/>\n'})
        rc, out = self.run_adapter(pit([(4, 'KILLED')]))
        self.assertEqual(rc, 3, out)
        self.assertIn('EMPTY_INVENTORY', out)


if __name__ == '__main__':
    unittest.main()
