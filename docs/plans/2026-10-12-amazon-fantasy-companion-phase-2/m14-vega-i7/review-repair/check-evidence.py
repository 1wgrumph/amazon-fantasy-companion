#!/usr/bin/env python3
"""Regression checks for R-4 public hygiene and R-6 current feature verdicts."""
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / 'docs/plans/2026-10-12-amazon-fantasy-companion-phase-2'

if sys.argv[1] == 'hygiene':
    names = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=AM',
                                     'origin/main...HEAD'], cwd=ROOT, text=True).splitlines()
    patterns = [r'[a-z0-9]+\.execute-api\.[a-z0-9-]+\.amazonaws\.com',
                r'\b(?:10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b',
                r'amazon-fantasy-companion-\d+']
    hits = []
    for name in names:
        if name.endswith('.png'):
            continue
        content = (ROOT / name).read_text(errors='replace')
        if any(re.search(pattern, content) for pattern in patterns):
            hits.append(name)
    assert not hits, f'Private environment details remain in {hits}'
    probe = ROOT / 'vega-app/vvd-checks/probe-guest-network.sh'
    for host, expected in [(None, 1), ('bad;command', 64)]:
        env = dict(os.environ)
        env.pop('AFC_API_HOST', None)
        if host is not None:
            env['AFC_API_HOST'] = host
        result = subprocess.run(['bash', str(probe)], env=env, capture_output=True)
        assert result.returncode == expected, 'Reject an unset or unsafe host before device commands'
    from PIL import Image
    for name in ['01-link-code.png', '09-reload-top.png']:
        im = Image.open(BASE / 'm14-vega-i7/stage2c' / name)
        assert len(im.crop((60, 198, 902, 258)).getcolors(1) or []) == 1, 'Endpoint region must be blank'
else:
    table = (BASE / 'evidence/P2-V01/feature-verdicts.md').read_text()
    device = next(line for line in table.splitlines() if line.startswith('| Device linking'))
    panel = next(line for line in table.splitlines() if line.startswith('| Lineup panel'))
    assert 'bug-token' in device and 'REPAIRABLE_FAILURE' not in device
    assert 'bug-panel' in panel and 'NEEDS_MORE_EVIDENCE' not in panel
    index = (ROOT / 'evidence/visual/P2-V01/README.md').read_text()
    assert 'bug-token' in index and 'bug-panel' in index and 'none captured' not in index
print('PASS', sys.argv[1])
