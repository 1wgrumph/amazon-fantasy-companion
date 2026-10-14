#!/usr/bin/env python3
"""Changed-line coverage verdict from native Cobertura XML via diff-cover.

usage: evaluate.py BASE COVERAGE_XML OUT_DIR. Exit 0 PASS, 1 FAIL, 3 GAP.
Every changed backend/src Python file must be mapped in the diff-cover result;
an empty denominator, absent or stale report is a GAP, never PASS.
"""

import json
import subprocess
import sys
from pathlib import Path

THRESHOLD = 90.0
SOURCE = 'backend/src/'


def verdict(out, status, detail, **extra):
    (out / 'coverage-result.json').write_text(
        json.dumps({'status': status, 'detail': detail, 'threshold': THRESHOLD, **extra}, indent=2) + '\n')
    print(f'{status} {detail}')
    return {'PASS': 0, 'FAIL': 1}.get(status, 3)


def main(argv):
    if len(argv) != 3:
        print('usage: evaluate.py BASE COVERAGE_XML OUT_DIR', file=sys.stderr)
        return 2
    base, xml, out = argv[0], Path(argv[1]), Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    if not xml.is_file():
        return verdict(out, 'GAP', f'REPORT_INCOMPLETE: coverage XML absent: {xml.name}')
    candidate = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    diff = subprocess.run(['git', 'diff', '--no-renames', '--name-only', '--diff-filter=AM', f'{base}...HEAD',
                           '--', SOURCE], capture_output=True, text=True)
    if diff.returncode:
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: cannot diff base: ' + diff.stderr.strip())
    changed = sorted(p for p in diff.stdout.splitlines() if p.endswith('.py'))
    if not changed:
        return verdict(out, 'GAP', 'EMPTY_DENOMINATOR: no changed backend/src Python files', candidate=candidate)
    report = out / 'diff-cover.json'
    run = subprocess.run(['diff-cover', str(xml), f'--compare-branch={base}', '--ignore-staged',
                          '--ignore-unstaged', f'--format=json:{report}'], capture_output=True, text=True)
    if run.returncode or not report.is_file():
        return verdict(out, 'GAP', f'REPORT_INCOMPLETE: diff-cover exit {run.returncode}: '
                       + (run.stderr.strip().splitlines() or [''])[-1])
    data = json.loads(report.read_text())
    stats = data.get('src_stats', {})
    # A changed file absent from the report (stale XML, outside --source) is never 100% of nothing.
    unmapped = [p for p in changed if p not in stats]
    common = dict(candidate=candidate, base=base, changed=changed,
                  total_num_lines=data.get('total_num_lines'), percent=data.get('total_percent_covered'))
    if unmapped:
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: unmapped changed files: ' + ', '.join(unmapped),
                       unmapped=unmapped, **common)
    if not data.get('total_num_lines'):
        return verdict(out, 'GAP', 'EMPTY_DENOMINATOR: no executable changed lines', **common)
    percent = float(data['total_percent_covered'])
    status = 'PASS' if percent >= THRESHOLD else 'FAIL'
    return verdict(out, status, f'changed-line coverage {percent:g}% (threshold {THRESHOLD:g}%)', **common)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
