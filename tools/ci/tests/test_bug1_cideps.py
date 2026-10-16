"""BUG-AFC-B01-TOOL-001 BUG 1: CI backend job installs hash-pinned test deps.

The CI backend job runs `bash tools/ci/gate.sh backend` on a bare runner; with
no dependency install step the gate fails at conftest import (ModuleNotFoundError:
No module named 'moto'). The install must be hash-verified per the CI supply-chain
trust boundary. No subprocess, network or venv: static binding checks only.
"""

import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
DEV_REQS = REPO / 'backend' / 'requirements-dev.txt'
CI_YML = REPO / '.github' / 'workflows' / 'ci.yml'


def stanzas(text):
    """Logical requirement lines with backslash continuations joined."""
    out, buf = [], ''
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if stripped.endswith('\\'):
            buf += stripped[:-1] + ' '
        else:
            out.append(buf + stripped)
            buf = ''
    if buf.strip():
        out.append(buf.strip())
    return out


class BackendCIDeps(unittest.TestCase):
    def test_dev_requirements_are_hash_pinned(self):
        reqs = [s for s in stanzas(DEV_REQS.read_text(encoding='utf-8'))
                if not s.startswith('-')]
        self.assertTrue(reqs, 'requirements-dev.txt names no packages')
        unpinned = [s.split(';')[0].strip()
                    for s in reqs if '--hash=sha256:' not in s]
        self.assertEqual(unpinned, [],
                         'requirements without hashes cannot use --require-hashes: '
                         + ', '.join(unpinned))

    def test_ci_backend_job_installs_dev_requirements_hash_verified_before_gate(self):
        steps = yaml.safe_load(CI_YML.read_text(encoding='utf-8'))['jobs']['backend']['steps']
        runs = [s.get('run', '') for s in steps]
        gate = next(i for i, r in enumerate(runs) if r == 'bash tools/ci/gate.sh backend')
        install = [i for i, r in enumerate(runs)
                   if '--require-hashes' in r and 'requirements-dev.txt' in r]
        self.assertTrue(install, 'backend job installs no hash-verified requirements')
        self.assertLess(install[0], gate, 'dependency install must precede the gate')


if __name__ == '__main__':
    unittest.main()
