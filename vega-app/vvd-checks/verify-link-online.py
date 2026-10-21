#!/usr/bin/env python3
"""Checks a drive-vvd.sh run of linking and settings: usage verify-link-online.py <evidence-dir>.
Expects the captures named in the Stage 2c command list and confirm*/confirm.status from confirm-link.sh.
Hash equality stands for "the same screen": the profile screen has no clock, so an unchanged state renders byte for byte."""
import hashlib, sys
from pathlib import Path

d = Path(sys.argv[1])
h = {n: hashlib.sha256((d / f'{n}.png').read_bytes()).hexdigest() for n in
     ['01-link-code', '04-main-loaded', '05a-redzone-off', '05-redzone-on', '09-reload-top',
      '11-relinked-top', '12-relinked-redzone']}
confirms = sorted(d.glob('confirm*/confirm.status'))
checks = {
    'phone confirm returned 200 for every code': bool(confirms) and all(p.read_text().strip() == '200' for p in confirms),
    'confirm moves the TV from the code screen to Profile/Settings': h['01-link-code'] != h['04-main-loaded'],
    'the RedZone control changes the screen': h['05a-redzone-off'] != h['05-redzone-on'],
    'a reloaded profile shows the saved RedZone state': h['12-relinked-redzone'] == h['05-redzone-on'],
    'the linked TV opens Profile/Settings after an app relaunch': h['09-reload-top'] == h['04-main-loaded'],
}
for name, ok in checks.items():
    print(('PASS ' if ok else 'FAIL ') + name)
sys.exit(0 if all(checks.values()) else 1)
