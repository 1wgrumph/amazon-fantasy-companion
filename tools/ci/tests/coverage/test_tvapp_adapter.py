"""PROC-GATE-TOOL-QUALIFY controls for the CMD-COVERAGE-TVAPP repo adapter.

Resource group: host-python-report-fixtures; unique temporary git repo per test,
real diff-cover over JaCoCo XML; tv-app/gradlew is a fixture that emits the
report the real :app:afcCoverageReport task would write (Gradle/Android runs are
evidenced separately in P2-A01). No engine, network or device.
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
REPORT = 'tv-app/app/build/reports/jacoco/afcCoverageReport/afcCoverageReport.xml'
GRADLEW = f'''#!/usr/bin/env bash
[[ -n "${{FIXTURE_GRADLE_FAIL:-}}" ]] && {{ echo 'BUILD FAILED'; exit 1; }}
[[ -n "${{FIXTURE_XML:-}}" ]] || exit 0
cd "$(dirname "$0")/.." && mkdir -p "$(dirname {REPORT})" && cp "$FIXTURE_XML" {REPORT}
'''


def jacoco(lines, session=True):
    """JaCoCo XML for Control.kt: {line: covered?}."""
    nodes = ''.join(f'<line nr="{n}" mi="{0 if hit else 2}" ci="{2 if hit else 0}" mb="0" cb="0"/>'
                    for n, hit in sorted(lines.items()))
    info = '<sessioninfo id="s" start="1" dump="2"/>' if session else ''
    return (f'<?xml version="1.0" encoding="UTF-8"?><report name="app">{info}<package name="com/afc/control">'
            f'<sourcefile name="Control.kt">{nodes}</sourcefile></package></report>')


def git(cwd, *args):
    return subprocess.run(['git', '-c', 'user.name=Gate Test', '-c', 'user.email=gate-test@example.invalid',
                           '-c', 'commit.gpgsign=false', *args], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout.strip()


class TvappCoverageAdapter(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo, self.out = self.tmp / 'repo', self.tmp / 'out'
        shutil.copytree(REPO / 'tools/ci/coverage', self.repo / 'tools/ci/coverage')
        gradlew = self.repo / 'tv-app/gradlew'
        gradlew.parent.mkdir(parents=True)
        gradlew.write_text(GRADLEW)
        gradlew.chmod(0o755)
        (self.repo / 'tv-app/app/src/main').mkdir(parents=True)
        (self.repo / 'tv-app/app/src/main/AndroidManifest.xml').write_text('<manifest/>\n')
        (self.repo / '.gitignore').write_text('tv-app/app/build/\n')
        git(self.repo, 'init', '-q', '-b', 'main')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'base')
        self.base = git(self.repo, 'rev-parse', 'HEAD')
        java = self.tmp / 'jdk/bin/java'
        java.parent.mkdir(parents=True)
        java.write_text('#!/bin/sh\n')
        java.chmod(0o755)
        (self.tmp / 'sdk').mkdir()
        self.env = {**os.environ, 'JAVA_HOME': str(self.tmp / 'jdk'),
                    'ANDROID_HOME': str(self.tmp / 'sdk')}
        self.env.pop('FIXTURE_XML', None)
        self.env.pop('FIXTURE_GRADLE_FAIL', None)

    def candidate(self, text=CONTROL):
        path = self.repo / SRC
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'candidate')

    def run_adapter(self, xml=None, **env):
        if xml is not None:
            (self.tmp / 'fixture.xml').write_text(xml)
            env['FIXTURE_XML'] = str(self.tmp / 'fixture.xml')
        result = subprocess.run(['bash', 'tools/ci/coverage/tvapp.sh', self.base, str(self.out)],
                                cwd=self.repo, capture_output=True, text=True, timeout=300,
                                env={**self.env, **env})
        out = result.stdout + result.stderr
        print(f'tvapp coverage adapter exit={result.returncode}: {out.strip().splitlines()[-1:]}')
        return result.returncode, out

    def result(self):
        return json.loads((self.out / 'coverage-result.json').read_text())

    def test_covered_changed_lines_pass(self):
        self.candidate()
        rc, out = self.run_adapter(jacoco({3: True, 4: True, 5: True}))
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.result()['status'], 'PASS')
        self.assertEqual(self.result()['changed'], [SRC])
        self.assertTrue((self.out / 'changed.diff').read_text().count(SRC))

    def test_uncovered_changed_line_fails_threshold(self):
        self.candidate()
        rc, out = self.run_adapter(jacoco({3: True, 4: True, 5: False}))
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.result()['status'], 'FAIL')
        self.assertLess(self.result()['percent'], 90)

    def test_missing_report_is_gap(self):
        self.candidate()
        rc, out = self.run_adapter()
        self.assertEqual(rc, 3, out)
        self.assertIn('JaCoCo XML absent', out)

    def test_stale_report_from_earlier_run_is_removed(self):
        self.candidate()
        stale = self.repo / REPORT
        stale.parent.mkdir(parents=True)
        stale.write_text(jacoco({3: True, 4: True, 5: True}))
        rc, out = self.run_adapter()
        self.assertEqual(rc, 3, out)
        self.assertIn('JaCoCo XML absent', out)

    def test_zero_execution_report_is_gap(self):
        self.candidate()
        rc, out = self.run_adapter(jacoco({3: True, 4: True, 5: True}, session=False))
        self.assertEqual(rc, 3, out)
        self.assertIn('no execution session', out)

    def test_unparseable_report_is_gap(self):
        self.candidate()
        rc, out = self.run_adapter('<report name="app"><sessioninfo')
        self.assertEqual(rc, 3, out)
        self.assertIn('unparseable', out)

    def test_unmapped_changed_file_is_gap(self):
        self.candidate()
        other = self.repo / 'tv-app/app/src/main/java/com/afc/control/Other.kt'
        other.write_text('package com.afc.control\n\nfun other() = 1\n')
        git(self.repo, 'add', '-A')
        git(self.repo, 'commit', '-q', '--no-verify', '-m', 'unmapped')
        rc, out = self.run_adapter(jacoco({3: True, 4: True, 5: True}))
        self.assertEqual(rc, 3, out)
        self.assertIn('unmapped changed files', out)
        self.assertIn('Other.kt', out)

    def test_no_changed_source_is_empty_denominator_gap(self):
        (self.repo / 'tv-app/app/src/main/AndroidManifest.xml').write_text('<manifest package="x"/>\n')
        git(self.repo, 'commit', '-qam', 'manifest only', '--no-verify')
        rc, out = self.run_adapter(jacoco({3: True}))
        self.assertEqual(rc, 3, out)
        self.assertIn('EMPTY_DENOMINATOR', out)

    def test_gradle_failure_fails(self):
        self.candidate()
        rc, out = self.run_adapter(jacoco({3: True, 4: True, 5: True}), FIXTURE_GRADLE_FAIL='1')
        self.assertEqual(rc, 1, out)
        self.assertIn('FAIL tv-app unit tests', out)

    def test_missing_android_sdk_is_gap(self):
        self.candidate()
        rc, out = self.run_adapter(jacoco({3: True, 4: True, 5: True}), ANDROID_HOME=str(self.tmp / 'absent'),
                                   ANDROID_SDK_ROOT='')
        self.assertEqual(rc, 3, out)
        self.assertIn('Android SDK', out)


if __name__ == '__main__':
    unittest.main()
