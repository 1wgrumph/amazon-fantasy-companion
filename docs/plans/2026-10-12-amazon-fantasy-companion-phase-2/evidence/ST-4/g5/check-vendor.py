"""Verify vendored regular files, modes, provenance and byte hashes against Git."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

source = Path.home() / 'alphazede/Alphazedehq'
target = Path('tools/spec')
pin = sys.argv[1]
def git(*args):
    return subprocess.check_output(['git', '-C', str(source), *args])
skill = 'skills/spec-authoring'
expected = {}
for entry in git('ls-tree', '-rz', f'{pin}:{skill}').split(b'\0'):
    if not entry:
        continue
    meta, name = entry.split(b'\t')
    mode, kind, oid = meta.decode().split()
    name = name.decode()
    if not name.startswith(('scripts/', 'template/')):
        continue
    assert kind == 'blob' and mode in ('100644', '100755')
    relative = name.removeprefix('scripts/')
    expected[relative] = (git('cat-file', 'blob', oid), int(mode[-3:], 8))
marker = target / 'VENDORED.md'
assert f'Source commit: {pin}\n' in marker.read_text()
assert git('rev-parse', f'{pin}:{skill}').decode().strip() in marker.read_text()
assert git('show', f'{pin}:{skill}/LICENSE-gridmarket').decode() in marker.read_text()
actual = {str(p.relative_to(target)): p for p in target.rglob('*') if not p.is_dir()}
assert set(actual) == set(expected) | {'VENDORED.md'}
for name, (data, mode) in expected.items():
    p = actual[name]
    assert not p.is_symlink() and p.is_file()
    assert p.read_bytes() == data, name
    assert p.stat().st_mode & 0o777 == mode, name
assert marker.stat().st_mode & 0o777 == 0o644
print(json.dumps({'pin': pin, 'tree': git('rev-parse', f'{pin}:{skill}').decode().strip(), 'files': {name: hashlib.sha256(p.read_bytes()).hexdigest() for name, p in sorted(actual.items())}}, indent=2))
