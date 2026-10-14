"""PROC-GATE-TOOL-QUALIFY native reporter controls, not adapter qualification.

Resource group: host-python-report-fixtures; unique temporary root, no engine.
Missing diff-cover blocks changed-line qualification even when coverage passes.
"""

import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

PROBE_TOOL = 'diff-cover'  # must name a tool in the adapter's `for tool in ...` line
ADAPTER_SH = Path(__file__).resolve().parent.parent.parent / 'coverage' / 'backend.sh'


class NativeCoverage(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / 'src').mkdir()
        shutil.copy2(Path(__file__).with_name('control.py'), self.tmp / 'src/control.py')

    def native(self, *args):
        result = subprocess.run(['python3.12', '-m', 'coverage', *args], cwd=self.tmp,
                                capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout + result.stderr

    def report(self, both):
        (self.tmp / 'runner.py').write_text(
            'from src.control import verdict\nassert verdict(True) == "covered"\n'
            + ('assert verdict(False) == "uncovered"\n' if both else ''), encoding='utf-8')
        rc, out = self.native('run', '--rcfile=/dev/null', '--source=src',
                              '--data-file=.coverage', 'runner.py')
        self.assertEqual(rc, 0, out)
        rc, out = self.native('xml', '--rcfile=/dev/null', '--data-file=.coverage',
                              '--fail-under=90', '-o', 'coverage.xml')
        root = ET.parse(self.tmp / 'coverage.xml').getroot()
        classes = root.findall('.//class')
        self.assertEqual([c.attrib['filename'] for c in classes], ['src/control.py'])
        lines = {int(line.attrib['number']): int(line.attrib['hits'])
                 for line in classes[0].findall('./lines/line')}
        self.assertTrue(lines, 'empty native statement denominator')
        print(f'native coverage both={both} exit={rc} lines={lines}; {out.strip()}')
        return rc, out, lines

    def test_covered_statements_pass_native_threshold(self):
        rc, out, lines = self.report(True)
        self.assertEqual(rc, 0, out)
        self.assertTrue(all(lines.values()), lines)

    def test_uncovered_statement_fails_native_threshold(self):
        rc, out, lines = self.report(False)
        self.assertEqual(rc, 2, out)
        self.assertIn(0, lines.values())
        self.assertIn('failure', out.lower())

    def test_absent_native_data_rejects_report(self):
        rc, out = self.native('xml', '--rcfile=/dev/null', '--data-file=absent', '-o', 'coverage.xml')
        self.assertNotEqual(rc, 0, out)
        self.assertIn('No data to report', out)
        self.assertFalse((self.tmp / 'coverage.xml').exists())

    def test_diff_cover_binding_is_available(self):
        exe = shutil.which(PROBE_TOOL)
        self.assertIsNotNone(exe, 'GAP DIFF_COVER_UNAVAILABLE: diff-cover not on PATH')
        result = subprocess.run([exe, '--version'],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0,
                         'GAP DIFF_COVER_UNAVAILABLE: ' + result.stdout + result.stderr)

    def test_probe_executable_matches_adapter(self):
        line = next(line for line in ADAPTER_SH.read_text(encoding='utf-8').splitlines()
                    if line.startswith('for tool in '))
        tools = line.split('for tool in ')[1].split(';')[0].split()
        self.assertIn(PROBE_TOOL, tools,
                      f'probe/adapter drift: {PROBE_TOOL!r} not in adapter tools {tools}')


if __name__ == '__main__':
    unittest.main()
