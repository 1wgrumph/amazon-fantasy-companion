"""PROC-GATE-TOOL-QUALIFY prerequisite; unavailable means blocking typed GAP.

Resource group: host-tool-probe, no engine. Never replace native killed/survived
evidence with manually edited source or invented exporter schemas.
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

PROBE_TOOL = 'mutmut'  # must name a tool in the adapter's `for tool in ...` line
ADAPTER_SH = Path(__file__).resolve().parent.parent.parent / 'mutation' / 'backend.sh'


class NativeMutation(unittest.TestCase):
    def test_mutmut_binding_is_available(self):
        exe = shutil.which(PROBE_TOOL)
        self.assertIsNotNone(exe, 'GAP MUTMUT_UNAVAILABLE: mutmut not on PATH')
        with tempfile.TemporaryDirectory() as tmp:
            # mutmut loads config at import, so --version needs a minimal config nearby
            Path(tmp, 'setup.cfg').write_text('[mutmut]\nsource_paths=src\n', encoding='utf-8')
            result = subprocess.run([exe, '--version'], cwd=tmp,
                                    capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0,
                         'GAP MUTMUT_UNAVAILABLE: ' + result.stdout + result.stderr)

    def test_probe_executable_matches_adapter(self):
        line = next(line for line in ADAPTER_SH.read_text(encoding='utf-8').splitlines()
                    if line.startswith('for tool in '))
        tools = line.split('for tool in ')[1].split(';')[0].split()
        self.assertIn(PROBE_TOOL, tools,
                      f'probe/adapter drift: {PROBE_TOOL!r} not in adapter tools {tools}')


if __name__ == '__main__':
    unittest.main()
