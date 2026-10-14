#!/usr/bin/env python3
"""Mutation verdict from mutmut 3 native CI stats and full result inventory.

usage: evaluate.py OUT_DIR CHANGED_FILES BASE [RUN_EXIT]. Exit 0 PASS, 1 FAIL, 3 GAP.
Score = killed / (killed + survived + no_tests) over mutants bound to changed
executable behavior only; timeouts, suspicious, segfaults, interruptions, skips,
unchecked and type-check-caught mutants are unresolved. Changed module-level
behavior unsupported by mutmut is PYTHON_NONFUNCTION_MUTATION_GAP, and any
mutant that cannot be bound to changed behavior is MUTATION_SCOPE_GAP.
"""

import ast
import json
import re
import subprocess
import sys
from pathlib import Path

THRESHOLD = 0.70
# mutmut results text -> mutmut-cicd-stats.json key (mutmut/stats.py status_by_exit_code).
STATUS_KEY = {
    'killed': 'killed',
    'survived': 'survived',
    'no tests': 'no_tests',
    'timeout': 'timeout',
    'suspicious': 'suspicious',
    'skipped': 'skipped',
    'segfault': 'segfault',
    'check was interrupted by user': 'check_was_interrupted_by_user',
    'not checked': 'not_checked',
    'caught by type check': 'caught_by_type_check',
}
KNOWN_STATS = frozenset(STATUS_KEY.values()) | {'total'}
UNRESOLVED = ('timeout', 'suspicious', 'segfault', 'check was interrupted by user',
              'skipped', 'not checked', 'caught by type check')
MUTANT_LINE = re.compile(r'^\s*([\w.ǁ]+__mutmut_\d+): (.+)$', re.M)
HUNK = re.compile(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@')


def verdict(out, status, detail, **extra):
    (out / 'mutation-result.json').write_text(
        json.dumps({'status': status, 'detail': detail, 'threshold': THRESHOLD, **extra}, indent=2) + '\n')
    print(f'{status} {detail}')
    return {'PASS': 0, 'FAIL': 1}.get(status, 3)


def module(path):
    # backend/src/pkg/mod.py -> pkg.mod (mutmut names mutants <module>.x_<function>__mutmut_<n>).
    return path.removeprefix('backend/src/').removesuffix('.py').removesuffix('/__init__').replace('/', '.')


def split_mutant(name):
    """(module, (class|None, func)) following mutmut's x_/xǁ mangling; Nones when unparseable."""
    mangled = name.partition('__mutmut_')[0]
    parts = mangled.split('.')
    for i in range(len(parts) - 1, -1, -1):
        seg = parts[i]
        if seg.startswith('x_') or seg.startswith('xǁ'):
            if 'ǁ' in seg:
                _, class_name, func = seg.split('ǁ')
                return '.'.join(parts[:i]), (class_name, func)
            return '.'.join(parts[:i]), (None, seg[2:])
    return None, None


def changed_lines(base, path):
    """Added line numbers in HEAD for path; None when the diff cannot be read."""
    diff = subprocess.run(['git', 'diff', '-U0', '--no-renames', f'{base}...HEAD', '--', path],
                          capture_output=True, text=True)
    if diff.returncode:
        return None
    lines = set()
    for line in diff.stdout.splitlines():
        m = HUNK.match(line)
        if m:
            start, count = int(m.group(1)), int(m.group(2) or '1')
            lines.update(range(start, start + max(count, 1)))
    return lines


def scopes(tree):
    """(func_spans, behavior_spans): func spans keyed (class|None, func); behavior spans are
    top-level/class-level executable statements outside any function, minus imports/docstrings."""
    funcs, behaviors = {}, []

    def is_docstring(node):
        return (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str))

    def funcs_in(node, enclosing):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                funcs_in(child, child.name)
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = min([child.lineno] + [d.lineno for d in child.decorator_list])
                funcs.setdefault((enclosing, child.name), []).append((start, child.end_lineno))
                funcs_in(child, None)  # nested defs are not methods
            else:
                funcs_in(child, enclosing)

    def behaviors_in(body, doc_ok):
        for i, node in enumerate(body):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            elif isinstance(node, ast.ClassDef):
                behaviors_in(node.body, True)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            elif doc_ok and i == 0 and is_docstring(node):
                continue
            elif isinstance(node, ast.stmt):
                behaviors.append((node.lineno, node.end_lineno))

    funcs_in(tree, None)
    behaviors_in(tree.body, True)
    return funcs, behaviors


def main(argv):
    if len(argv) not in (3, 4):
        print('usage: evaluate.py OUT_DIR CHANGED_FILES BASE [RUN_EXIT]', file=sys.stderr)
        return 2
    out, changed, base = Path(argv[0]), sorted(argv[1].split()), argv[2]
    if not changed:
        return verdict(out, 'GAP', 'EMPTY_INVENTORY: no changed backend/src Python files')
    if len(argv) == 4 and argv[3] != '0':
        return verdict(out, 'GAP', f'UNRESOLVED: mutmut run exit {argv[3]}', changed=changed)
    stats_path, results_path = out / 'mutmut-cicd-stats.json', out / 'mutmut-results.txt'
    if not stats_path.is_file() or not results_path.is_file():
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: mutmut stats or inventory absent', changed=changed)
    try:
        stats = json.loads(stats_path.read_text())
    except json.JSONDecodeError as e:
        return verdict(out, 'GAP', f'REPORT_INCOMPLETE: mutmut stats not JSON: {e}', changed=changed)
    if (not isinstance(stats, dict) or any(k not in KNOWN_STATS for k in stats)
            or any(type(v) is not int for v in stats.values()) or 'total' not in stats):
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: unsupported mutmut stats schema', changed=changed)
    pairs = MUTANT_LINE.findall(results_path.read_text())
    inventory = dict(pairs)
    common = dict(changed=changed, stats=stats, mutants=len(inventory), inventory=inventory)
    if len(pairs) != len(inventory):
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: duplicate mutant IDs in inventory', **common)
    unknown = sorted({s for s in inventory.values() if s not in STATUS_KEY})
    if unknown:
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: unknown mutant statuses: ' + ', '.join(unknown),
                       **common)
    if not stats['total'] or not inventory:
        return verdict(out, 'GAP', 'EMPTY_INVENTORY: zero mutants', **common)
    counts = {key: 0 for key in STATUS_KEY.values()}
    for status in inventory.values():
        counts[STATUS_KEY[status]] += 1
    mismatch = (['total'] if sum(counts.values()) != stats['total'] else [])
    mismatch += [k for k in sorted(counts) if counts[k] != stats.get(k, 0)]
    if mismatch:
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: inventory/stats count mismatch: '
                       + ', '.join(mismatch), **common)
    # Bind mutants to changed executable behavior before scoring anything.
    changed_funcs, scope_funcs, unmapped_scope = {}, {}, []
    for path in changed:
        lines = changed_lines(base, path)
        src = subprocess.run(['git', 'show', f'HEAD:{path}'], capture_output=True, text=True)
        if lines is None or src.returncode:
            return verdict(out, 'GAP', f'MUTATION_SCOPE_GAP: cannot diff/read {path}', **common)
        try:
            funcs, stmts = scopes(ast.parse(src.stdout))
        except SyntaxError as e:
            return verdict(out, 'GAP', f'MUTATION_SCOPE_GAP: cannot parse {path}: {e}', **common)
        hits = lambda span: any(n in lines for n in range(span[0], span[1] + 1))
        if any(hits(span) for span in stmts):
            return verdict(out, 'GAP', 'PYTHON_NONFUNCTION_MUTATION_GAP: '
                           f'changed module-level behavior in {path} has no mutant binding', **common)
        changed_funcs[path] = {k for k, spans in funcs.items() if any(hits(s) for s in spans)}
        scope_funcs[path] = funcs
    unmapped = [p for p in changed if not any(name.startswith(module(p) + '.') for name in inventory)]
    if unmapped:
        return verdict(out, 'GAP', 'REPORT_INCOMPLETE: no mutants for changed files: ' + ', '.join(unmapped),
                       unmapped=unmapped, **common)
    scored = {}
    for name, status in inventory.items():
        mod_name, key = split_mutant(name)
        owner = next((p for p in changed if module(p) == mod_name), None)
        if owner is None or key is None or key not in scope_funcs[owner]:
            unmapped_scope.append(name)
        elif key in changed_funcs[owner]:
            scored[name] = status
    if unmapped_scope:
        return verdict(out, 'GAP', 'MUTATION_SCOPE_GAP: mutants not bound to changed behavior: '
                       + ', '.join(sorted(unmapped_scope)), scored_mutants=len(scored), **common)
    unresolved = {s: sum(1 for v in scored.values() if v == s) for s in UNRESOLVED if s in scored.values()}
    if unresolved:
        return verdict(out, 'GAP', f'UNRESOLVED: {unresolved}', scored_mutants=len(scored),
                       changed_functions={p: sorted(f'{c}.{f}' if c else f for c, f in keys)
                                          for p, keys in changed_funcs.items()}, **common)
    denominator = sum(1 for v in scored.values() if v in ('killed', 'survived', 'no tests'))
    if not denominator:
        return verdict(out, 'GAP', 'EMPTY_INVENTORY: zero scored mutants in changed behavior',
                       scored_mutants=len(scored), **common)
    score = sum(1 for v in scored.values() if v == 'killed') / denominator
    survivors = sorted(n for n, s in scored.items() if s in ('survived', 'no tests'))
    status = 'PASS' if score >= THRESHOLD else 'FAIL'
    return verdict(out, status, f'mutation score {score:.2%} (threshold {THRESHOLD:.0%})',
                   score=score, survivors=survivors, scored_mutants=len(scored),
                   changed_functions={p: sorted(f'{c}.{f}' if c else f for c, f in keys)
                                      for p, keys in changed_funcs.items()}, **common)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
