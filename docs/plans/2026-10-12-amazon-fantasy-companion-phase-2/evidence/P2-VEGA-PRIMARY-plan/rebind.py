"""Mechanical digest refresh for the corrected 39a145c planning package."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess

EVIDENCE = Path(__file__).resolve().parent
PLAN = EVIDENCE.parent.parent
ROOT = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
HOOK = Path.home() / '.claude/plugins/cache/bearing-lite/bearing-lite/1.1.7/hooks/plan-package.cjs'
BASE = '39a145c72eb93d42701328bf95228e3ad4e64f12'


def sha(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def write(file, data, indent, ascii):
    file.write_text(json.dumps(data, indent=indent, ensure_ascii=ascii) + '\n')


def changes(before, after, path=''):
    if isinstance(before, dict):
        assert before.keys() == after.keys(), path
        return sum((changes(v, after[k], path + '/' + k) for k, v in before.items()), [])
    if isinstance(before, list):
        assert len(before) == len(after), path
        return sum((changes(v, after[i], path + '/' + str(i)) for i, v in enumerate(before)), [])
    return [] if before == after else [{'path': path, 'before': before, 'after': after}]


assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip() == BASE
docs = {name: json.loads((PLAN / name).read_text()) for name in ['implementation.json', 'seit.json']}
old = copy.deepcopy(docs)
before_hashes = {name: sha(PLAN / name) for name in [*docs, 'amazon-fantasy-companion-phase-2-dod-manifest.html']}
for name, doc in docs.items():
    expected = subprocess.check_output(['git', 'show', BASE + ':' + (PLAN / name).relative_to(ROOT).as_posix()])
    assert expected == (PLAN / name).read_bytes(), name + ': already modified'
    for row in doc['source_baseline']['planning_inputs']:
        row['sha256'] = sha(ROOT / row['path'])
write(PLAN / 'seit.json', docs['seit.json'], 2, False)
result = json.loads(subprocess.check_output([
    'node', '-e', 'console.log(JSON.stringify(require(process.argv[1]).verifyDigests(process.argv[2])))',
    str(HOOK), str(PLAN),
], text=True, timeout=600))
assert all(f['code'] == 'candidate_digest_mismatch' for f in result['findings']), result
digest = result['manifest_digest']
impl = docs['implementation.json']
seit_hash = sha(PLAN / 'seit.json')
impl['source_baseline']['seit_json_sha256_at_integration'] = seit_hash
impl['journey_settings']['planning_review']['candidate_digest'] = digest
identity = impl['dod_manifest']['identity']
for row in identity:
    if row['label'] == 'Candidate digest':
        row['value'] = digest
    if row['label'] == 'seit.json':
        row['value'] = seit_hash

delta = {name: changes(old[name], doc) for name, doc in docs.items()}
for name, rows in delta.items():
    allowed = {f'/source_baseline/planning_inputs/{i}/sha256' for i in range(len(docs[name]['source_baseline']['planning_inputs']))}
    if name == 'implementation.json':
        allowed |= {'/source_baseline/seit_json_sha256_at_integration', '/journey_settings/planning_review/candidate_digest'}
        allowed |= {f'/dod_manifest/identity/{i}/value' for i, row in enumerate(identity) if row['label'] in ['Candidate digest', 'seit.json']}
    assert all(row['path'] in allowed for row in rows), delta
write(PLAN / 'implementation.json', impl, 1, True)
write(EVIDENCE / 'rebind-digests.json', {
    'base_commit': BASE,
    'before_file_sha256': before_hashes,
    'after_file_sha256_before_render': {name: sha(PLAN / name) for name in docs},
    'before_candidate_digest': old['implementation.json']['journey_settings']['planning_review']['candidate_digest'],
    'after_candidate_digest': digest,
    'structural_changes': delta,
    'structural_verification': 'PASS: digest fields only; historical authority and profile bindings preserved',
}, 2, False)
print(json.dumps({'outcome': 'PASS', 'candidate_digest': digest, 'seit_sha256': seit_hash, 'changed_fields': {name: len(rows) for name, rows in delta.items()}}, indent=2))
