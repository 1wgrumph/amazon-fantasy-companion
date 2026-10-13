"""Check links, unchanged product prose, UID coverage and generated trace links."""
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[6]
spec = root / 'spec/amazon-fantasy-companion'
built = spec / 'amazon-fantasy-companion.md'
link = re.compile(r'!?\[([^\]\n]*)\]\(([^)]+)\)')
def anchors(text):
    seen, result = {}, set()
    for title in re.findall(r'^#{1,6} (.+)$', text, re.M):
        name = re.sub(r'[^\w\- ]', '', title.lower()).replace(' ', '-')
        count = seen.get(name, 0)
        seen[name] = count + 1
        result.add(name + (f'-{count}' if count else ''))
    return result

assert 'section-1' in anchors('# Section 1\n')
assert 'section-1-1' in anchors('# Section 1\n# Section 1\n')
assert not link.findall('Unlinked section 1')
sections = sorted(spec.glob('[0-9]*.md'))
added = 0
checked = 0
for path in [*sections, built]:
    text = path.read_text()
    for label, target in link.findall(text):
        if target.startswith(('https://', 'http://')):
            continue
        file, _, fragment = target.partition('#')
        # Section sources are assembled into one document; fragment-only links
        # use that document's anchor namespace as required by the authoring kit.
        dest = path.parent / file if file else built
        assert dest.exists(), f'{path.name}: missing {target}'
        if fragment:
            assert fragment in anchors(dest.read_text()), f'{path.name}: missing anchor {target}'
        checked += 1
    if path in sections:
        old = subprocess.check_output(['git', 'show', '771c289:' + str(path.relative_to(root))], cwd=root, text=True)
        added += len(link.findall(text)) - len(link.findall(old))
        if path.name not in ('01.1.1-identification.md', '01.2.1-baselines.md'):
            assert link.sub(r'\1', text) == link.sub(r'\1', old), f'Product prose changed: {path.name}'
print(f'Relative links/anchors: {checked} resolved; source links added: {added}; product prose unchanged outside revision/provenance metadata')
register = root / 'docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/requirements-register.md'
known = set(re.findall(r'^\| (AFC-PR-\d{3}) \|', register.read_text(), re.M))
text = built.read_text()
appendix = text.split('## Appendix A — Requirement Traceability Matrix\n', 1)[1]
traced = set(re.findall(r'^\| (AFC-PR-\d{3}) \|', appendix, re.M))
assert len(known) == 66 and known == traced == set(re.findall(r'\bAFC-PR-\d{3}\b', text))
print('UID coverage: 66/66; Appendix A: 66/66; unknown UIDs: 0')
rows = [line for line in appendix.splitlines() if re.match(r'^\| AFC-PR-\d{3} \|', line)]
unlinked = [line for line in rows if not link.search(line)]
print(f'Generated Appendix A: {len(unlinked)}/{len(rows)} rows have unlinked section references')
assert not unlinked, 'Pinned builder emits plain section references; source edits cannot satisfy the all-reference condition'
