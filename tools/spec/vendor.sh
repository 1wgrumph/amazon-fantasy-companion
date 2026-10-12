#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 1 ]]; then
  echo 'usage: vendor.sh <repo root>' >&2
  exit 2
fi
python3 - "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)" "$1" <<'PY'
import pathlib
import re
import subprocess
import sys
import tempfile

skill, destination = map(pathlib.Path, sys.argv[1:])
root = pathlib.Path(subprocess.check_output(
    ['git', '-C', str(skill), 'rev-parse', '--show-toplevel']).decode().strip())

def git(*args):
    return subprocess.check_output(['git', '-C', str(root), *args])

relative = skill.relative_to(root).as_posix()
if git('status', '--porcelain', '--untracked-files=all', '--', relative):
    sys.exit('REFUSED: skill has uncommitted changes')
commit = git('log', '-1', '--format=%H', '--', relative).decode().strip()

def contents(revision):
    tree = git('rev-parse', f'{revision}:{relative}').decode().strip()
    files = {}
    for entry in git('ls-tree', '-rz', tree).split(b'\0'):
        if not entry:
            continue
        meta, rawname = entry.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        name = rawname.decode()
        if name.startswith('scripts/'):
            target = name[len('scripts/'):]
        elif name.startswith('template/'):
            target = name
        else:
            continue
        if mode not in ('100644', '100755') or kind != 'blob':
            sys.exit('REFUSED: non-regular source file')
        files[target] = (git('cat-file', 'blob', oid), int(mode[-3:], 8))
    license_text = git('show', f'{revision}:{relative}/LICENSE-gridmarket').decode()
    notice = ('# Vendored specification tools\n\n'
              'Source repository: https://github.com/alphazede/Alphazedehq\n'
              f'Source commit: {revision}\nSkill tree: {tree}\n\n'
              '## MIT notice (GridMarket)\n\n' + license_text)
    files['VENDORED.md'] = (notice.encode(), 0o644)
    return files

# Do not follow destination links into unrelated work.
if not destination.is_dir():
    sys.exit('REFUSED: destination repository directory is missing')
target = destination / 'tools' / 'spec'
for path in (destination, destination / 'tools', target):
    if path.is_symlink():
        sys.exit('REFUSED: destination is a symlink')
new = contents(commit)
if target.exists():
    marker = target / 'VENDORED.md'
    if not marker.is_file() or marker.is_symlink():
        sys.exit('REFUSED: existing copy has no provenance')
    match = re.search(r'^Source commit: ([0-9a-f]{40})$', marker.read_text(), re.M)
    if not match:
        sys.exit('REFUSED: invalid source commit')
    old = contents(match[1])
    actual = {}
    for path in target.rglob('*'):
        if path.is_symlink() or not (path.is_file() or path.is_dir()):
            sys.exit('REFUSED: modified vendored copy')
        if path.is_file():
            actual[path.relative_to(target).as_posix()] = (path.read_bytes(), path.stat().st_mode & 0o777)
    if actual != old:
        sys.exit('REFUSED: modified vendored copy')
    if old == new:
        print(f'UNCHANGED: {target}')
        sys.exit(0)
target.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='.spec-vendor-', dir=target.parent) as scratch:
    stage = pathlib.Path(scratch) / 'new'
    stage.mkdir()
    for name, (data, mode) in new.items():
        path = stage / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(mode)
    backup = pathlib.Path(scratch) / 'old'
    if target.exists():
        target.rename(backup)
    try:
        stage.rename(target)
    except OSError:
        if backup.exists():
            backup.rename(target)
        raise
print(f'VENDORED: {target} at {commit}')
PY
