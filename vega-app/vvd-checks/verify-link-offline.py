#!/usr/bin/env python3
"""Checks the PNGs from check-link-offline.sh: usage verify-link-offline.py <evidence-dir>.
The requesting and error states must differ, and the Get code retry must repeat both exactly."""
import hashlib, sys
from pathlib import Path

d = Path(sys.argv[1])
h = {n: hashlib.sha256((d / f'{n}.png').read_bytes()).hexdigest() for n in
     ['00-vvd-home', '01-link-requesting', '02-link-network-error', '03-link-after-get-code', '04-link-error-again']}
checks = {
    'app screen differs from VVD home': h['00-vvd-home'] != h['01-link-requesting'],
    'error state differs from requesting state': h['01-link-requesting'] != h['02-link-network-error'],
    'Get code returns to requesting state': h['03-link-after-get-code'] == h['01-link-requesting'],
    'retry fails to the same error state': h['04-link-error-again'] == h['02-link-network-error'],
}
for name, ok in checks.items():
    print(('PASS ' if ok else 'FAIL ') + name)
sys.exit(0 if all(checks.values()) else 1)
