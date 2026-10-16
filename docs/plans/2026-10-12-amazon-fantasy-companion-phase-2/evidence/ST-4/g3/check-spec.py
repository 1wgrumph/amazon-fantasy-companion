"""Check the ST-4 candidate against its register, source links and write boundary."""
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[6]
spec = root / 'spec/amazon-fantasy-companion'
evidence = Path(__file__).resolve().parent
register = root / 'docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/requirements-register.md'
built = spec / 'amazon-fantasy-companion.md'
# Detect home-root shapes without disclosing a particular machine's layout.
private_home = re.compile(r'(?:/(?:home|Users)/[^/\s]+/|[A-Za-z]:[\\/]Users[\\/][^\\/\s]+[\\/])')
# Root-anchored local machine directories; /v1 API paths and HTTPS URLs are not local paths.
local_root = re.compile(r'(?<![:/<\w])/(?:tmp|var|opt|usr|etc|root|mnt|media|srv)(?:/|\b)')
assert private_home.search('/'.join(['', 'home', 'example-user', 'project']))
assert local_root.search('/'.join(['', 'tmp', 'candidate']))
assert not local_root.search('</root>')
assert not local_root.search('https://example.test/v1/profile')
files = sorted(p for folder in (spec, evidence) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for p in files:
    source = p.read_text()
    assert not private_home.search(source), f'Private home path shape in {p.relative_to(root)}'
    assert not local_root.search(source), f'Local absolute path in {p.relative_to(root)}'


if '--paths-only' in sys.argv:
    sys.exit(0)

uid = re.compile(r'\bAFC-PR-\d{3}\b')
known = set(re.findall(r'^\| (AFC-PR-\d{3}) \|', register.read_text(), re.M))
assert len(known) == 66, f'Expected 66 register rows; found {len(known)}'
text = built.read_text()
seen = set(uid.findall(text))
assert seen == known, f'UID mismatch: missing={sorted(known-seen)} unknown={sorted(seen-known)}'
appendix = text.split('## Appendix A — Requirement Traceability Matrix\n', 1)[1]
traced = set(re.findall(r'^\| (AFC-PR-\d{3}) \|', appendix, re.M))
assert traced == known, f'Appendix mismatch: missing={sorted(known-traced)} unknown={sorted(traced-known)}'
for number in (49, 50, 51):
    uid_value = f'AFC-PR-{number:03}'
    row = next(line for line in appendix.splitlines() if line.startswith(f'| {uid_value} |'))
    assert 'Withdrawn requirements' in row, row
print('UID coverage: 66/66; Appendix A: 66/66; unknown UIDs: 0; withdrawn: 3')

sections = sorted(spec.glob('[0-9]*.md'))
for p in sections:
    source = p.read_text()
    assert not (set(uid.findall(source)) - known), p.name
    assert not re.search(r'<(?:System|Author|Feature name|YYYY-MM-DD|One assertive)', source), p.name
for p in [*sections, built]:
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', p.read_text()):
        if target.startswith(('https://', 'http://', '#')):
            continue
        assert (p.parent / target.split('#')[0]).exists(), f'{p.name}: missing {target}'
print(f'Section and local-link checks: {len(sections)} sections; PASS')
trailing = [(n, line) for n, line in enumerate(text.splitlines(), 1) if line.rstrip() != line]
assert trailing == [(3, '**Document ID:** AFC-D1  ')], trailing
print('Generated whitespace: only the builder’s intentional Markdown hard break at line 3')

changed = subprocess.check_output(['git', 'diff', '--name-only', '4d9b549696408ddaa5f432bac4911cbc349cb874'], cwd=root, text=True).splitlines()
changed += subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=root, text=True).splitlines()
allowed = ('spec/amazon-fantasy-companion/', 'docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/')
assert all(p.startswith(allowed) for p in changed), 'Changed path outside ST-4 write set'
print(f'Write-set check: {len(set(changed))} changed paths; PASS')
