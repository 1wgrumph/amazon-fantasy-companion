#!/usr/bin/env python3
"""Mutation verdict from mutmut 3 native CI stats and full result inventory.

usage: evaluate.py OUT_DIR CHANGED_FILES [RUN_EXIT]. Exit 0 PASS, 1 FAIL, 3 GAP.
Score = killed / (killed + survived + no_tests); timeouts, suspicious, segfaults,
interruptions and skips are unresolved. Every changed file needs mutants.
"""

import json
import re
import sys
from pathlib import Path

THRESHOLD = 0.70
UNRESOLVED = ('timeout', 'suspicious', 'segfault', 'check_was_interrupted_by_user', 'skipped')


def verdict(out, status, detail, **extra):
    (out / 'mutation-result.json').write_text(
        json.dumps({'status': status, 'detail': detail, 'threshold': THRESHOLD, **extra}, indent=2) + '\n')
    print(f'{status} {detail}')
    return {'PASS': 0, 'FAIL': 1}.get(status, 3)


def module(path):
    # backend/src/pkg/mod.py -> pkg.mod (mutmut names mutants <module>.x_<function>__mutmut_<n>).
    return path.removeprefix('backend/src/').removesuffix('.py').removesuffix('/__init__').replace('/', '.')


def main(argv):
    if len(argv) not in (2, 3):
        print('usage: evaluate.py OUT_DIR CHANGED_FILES [RUN_EXIT]', file=sys.stderr)
        return 2
    out, changed = Path(argv[0]), sorted(argv[1].split())
    if not changed:
        return verdict(out, 'GAP', 'EMPTY_INVENTORY: no changed backend/src Python files')
    if len(argv) == 3 and argv[2] != '0':
        return verdict(out, 'GAP', f'UNRESOLVED: mutmut run exit {argv[2]}', changed=changed)
    stats_path, results_path = out / 'mutmut-cicd-stats.json', out / 'mutmut-results.txt'
    if not stats_path.is_file() or not results_path.is_file():
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: mutmut stats or inventory absent', changed=changed)
    stats = json.loads(stats_path.read_text())
    inventory = dict(re.findall(r'^\s*([\w.ǁ]+__mutmut_\d+): (.+)$', results_path.read_text(), re.M))
    common = dict(changed=changed, stats=stats, mutants=len(inventory))
    if not stats.get('total') or not inventory:
        return verdict(out, 'GAP', 'EMPTY_INVENTORY: zero mutants', **common)
    unmapped = [p for p in changed if not any(name.startswith(module(p) + '.') for name in inventory)]
    if unmapped:
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: no mutants for changed files: ' + ', '.join(unmapped),
                       unmapped=unmapped, **common)
    unresolved = {key: stats.get(key, 0) for key in UNRESOLVED if stats.get(key, 0)}
    if unresolved:
        return verdict(out, 'GAP', f'UNRESOLVED: {unresolved}', **common)
    denominator = stats['killed'] + stats['survived'] + stats['no_tests']
    if not denominator:
        return verdict(out, 'GAP', 'EMPTY_INVENTORY: zero scored mutants', **common)
    score = stats['killed'] / denominator
    survivors = sorted(name for name, status in inventory.items() if status in ('survived', 'no tests'))
    status = 'PASS' if score >= THRESHOLD else 'FAIL'
    return verdict(out, status, f'mutation score {score:.2%} (threshold {THRESHOLD:.0%})',
                   score=score, survivors=survivors, **common)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
