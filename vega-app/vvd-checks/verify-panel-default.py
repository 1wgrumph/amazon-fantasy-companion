#!/usr/bin/env python3
"""Verify drive-vvd.sh's panel captures: verify-panel-default.py <evidence-dir>.

Use the linked synthetic profile with no selection, panel visible and halfPpr.
From the loaded top, send 33 DOWN keys to focus Save profile, then panel and end.
The visually checked reference shows Lineup panel, Team/league:
unassigned/unassigned, Half-PPR, no player rows, and Total: Unavailable.
Convert both XWD captures to PNG with the same converter used for the reference.
shortcut: exact screenshot matching needs the same VVD viewport, scroll and focus;
refresh the reference after visually checking any intentional rendering change.
"""
import hashlib
import sys
from pathlib import Path

directory = Path(sys.argv[1])
reference = hashlib.sha256((Path(__file__).parent / 'panel-default.png').read_bytes()).digest()
checks = {
    f'{name} shows the default team/league, basis and empty rows':
        hashlib.sha256((directory / f'{name}.png').read_bytes()).digest() == reference
    for name in ['panel-default', 'panel-default-held']
}
for name, ok in checks.items():
    print(('PASS ' if ok else 'FAIL ') + name)
sys.exit(0 if all(checks.values()) else 1)
