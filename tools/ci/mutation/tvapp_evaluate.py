#!/usr/bin/env python3
"""Mutation verdict for tv-app from PIT mutations XML (CMD-MUTATION-TVAPP).

usage: tvapp_evaluate.py OUT_DIR CHANGED_FILES BASE [RUN_EXIT]. Exit 0 PASS, 1 FAIL, 3 GAP.
Reads OUT_DIR/mutations.xml. Score = KILLED / (KILLED + SURVIVED + NO_COVERAGE) over
mutants on changed lines of changed Kotlin/Java files; NON_VIABLE mutants are invalid
and set aside; timeouts, errors and unstarted mutants are unresolved (GAP). A changed
file with no mutant at all, an absent or unparseable report, or an empty denominator
is a GAP, never PASS. A failed PIT run is ANDROID_MUTATION_COMPATIBILITY_GAP.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import THRESHOLD, changed_lines, verdict  # noqa: E402  (shared mutmut evaluator helpers)

SCORED = ('KILLED', 'SURVIVED', 'NO_COVERAGE')
UNRESOLVED = ('TIMED_OUT', 'MEMORY_ERROR', 'RUN_ERROR', 'STARTED', 'NOT_STARTED')
INVALID = ('NON_VIABLE',)
SRC_ROOTS = ('tv-app/app/src/main/java/', 'tv-app/app/src/main/kotlin/')


def source_path(mutated_class, source_file):
    """Repository-relative path suffix for a PIT mutant: <package dirs>/<sourceFile>."""
    package = mutated_class.split('$')[0].rpartition('.')[0]
    return '/'.join(filter(None, [package.replace('.', '/'), source_file]))


def main(argv):
    if len(argv) not in (3, 4):
        print('usage: tvapp_evaluate.py OUT_DIR CHANGED_FILES BASE [RUN_EXIT]', file=sys.stderr)
        return 2
    out, changed, base = Path(argv[0]), sorted(argv[1].split()), argv[2]
    out.mkdir(parents=True, exist_ok=True)
    if not changed:
        return verdict(out, 'GAP', 'EMPTY_INVENTORY: no changed tv-app/app/src/main Kotlin/Java files')
    if len(argv) == 4 and argv[3] != '0':
        return verdict(out, 'GAP', f'ANDROID_MUTATION_COMPATIBILITY_GAP: PIT run exit {argv[3]}', changed=changed)
    report = out / 'mutations.xml'
    if not report.is_file():
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: PIT mutations.xml absent', changed=changed)
    try:
        root = ET.parse(report).getroot()
    except ET.ParseError as e:
        return verdict(out, 'GAP', f'REPORT_INCOMPLETE: PIT mutations.xml unparseable: {e}', changed=changed)
    if root.tag != 'mutations' or root.get('partial') == 'true':
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: not a complete PIT mutations report', changed=changed)
    inventory = []
    for m in root.iter('mutation'):
        fields = {k: (m.findtext(k) or '').strip() for k in ('sourceFile', 'mutatedClass', 'lineNumber', 'mutator')}
        status = m.get('status', '')
        if not fields['sourceFile'] or not fields['mutatedClass'] or not fields['lineNumber'].isdigit():
            return verdict(out, 'GAP', 'REPORT_INCOMPLETE: PIT mutant lacks file, class or line', changed=changed)
        if status not in SCORED + UNRESOLVED + INVALID:
            return verdict(out, 'GAP', f'REPORT_INCOMPLETE: unknown PIT status {status!r}', changed=changed)
        inventory.append({'id': f'{fields["mutatedClass"]}:{fields["lineNumber"]}:{fields["mutator"]}',
                          'path': source_path(fields['mutatedClass'], fields['sourceFile']),
                          'line': int(fields['lineNumber']), 'status': status})
    common = dict(changed=changed, mutants=len(inventory))
    if not inventory:
        return verdict(out, 'GAP', 'EMPTY_INVENTORY: zero mutants', **common)
    owners = {p: next((p[len(r):] for r in SRC_ROOTS if p.startswith(r)), None) for p in changed}
    unmapped = [p for p, rel in owners.items() if rel is None or not any(m['path'] == rel for m in inventory)]
    if unmapped:
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: no mutants for changed files: ' + ', '.join(unmapped),
                       unmapped=unmapped, **common)
    scored = []
    for path, rel in owners.items():
        lines = changed_lines(base, path)
        if lines is None:
            return verdict(out, 'GAP', f'MUTATION_SCOPE_GAP: cannot diff {path}', **common)
        scored += [dict(m, path=path) for m in inventory if m['path'] == rel and m['line'] in lines]
    unresolved = sorted(m['id'] for m in scored if m['status'] in UNRESOLVED)
    if unresolved:
        return verdict(out, 'GAP', f'UNRESOLVED: {len(unresolved)} mutants', unresolved=unresolved,
                       scored_mutants=len(scored), **common)
    counted = [m for m in scored if m['status'] in SCORED]
    if not counted:
        return verdict(out, 'GAP', 'EMPTY_INVENTORY: zero scored mutants on changed lines',
                       scored_mutants=len(scored), **common)
    score = sum(m['status'] == 'KILLED' for m in counted) / len(counted)
    survivors = sorted(f'{m["path"]}:{m["line"]}:{m["status"]}' for m in counted if m['status'] != 'KILLED')
    status = 'PASS' if score >= THRESHOLD else 'FAIL'
    return verdict(out, status, f'mutation score {score:.2%} (threshold {THRESHOLD:.0%})', score=score,
                   survivors=survivors, scored_mutants=len(counted),
                   invalid=sum(m['status'] in INVALID for m in scored), **common)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
