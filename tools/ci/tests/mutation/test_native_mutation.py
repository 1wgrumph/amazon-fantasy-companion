"""PROC-GATE-TOOL-QUALIFY prerequisite; unavailable means blocking typed GAP.

Resource group: host-tool-probe, no engine. Never replace native killed/survived
evidence with manually edited source or invented exporter schemas.
"""

import subprocess
import unittest


class NativeMutation(unittest.TestCase):
    def test_mutmut_binding_is_available(self):
        result = subprocess.run(['python3.12', '-m', 'mutmut', '--version'],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0,
                         'GAP MUTMUT_UNAVAILABLE: ' + result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
