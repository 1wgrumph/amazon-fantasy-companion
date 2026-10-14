#!/usr/bin/env bash
# CMD-MUTATION-BACKEND: mutmut score for changed backend/src files of the committed candidate.
# Runs on a disposable `git archive` copy; never mutates the checkout. Exit 0 PASS, 1 FAIL, 3 GAP.
set -u
(($# == 2)) || { echo 'usage: backend.sh <base_sha> <evidence_dir>' >&2; exit 2; }
base=$1 out=$2
root=$(git rev-parse --show-toplevel) || exit 3
cd "$root" || exit 3
for tool in python3 mutmut tar timeout; do
    command -v "$tool" >/dev/null || { echo "GAP required tool missing: $tool"; exit 3; }
done
# mutmut runs pytest in-process, so it must run under an interpreter that has the
# backend test deps; PATH mutmut stays as fallback for dep-free fixtures.
if python3.12 -c 'import mutmut' >/dev/null 2>&1; then
    MUTMUT=(python3.12 -m mutmut)
else
    MUTMUT=(mutmut)
fi
[[ -d backend/src ]] || { echo 'GAP REPORT_INCOMPLETE: no backend/src/ tree'; exit 3; }
mkdir -p "$out" || exit 3
out=$(cd "$out" && pwd) || exit 3
rm -f "$out/mutmut-cicd-stats.json" "$out/mutmut-results.txt" "$out/mutmut-run.txt" "$out/mutation-result.json"
changed=$(git diff --no-renames --name-only --diff-filter=AM "$base...HEAD" -- backend/src | grep '\.py$')
if [[ -z "$changed" ]]; then
    python3 tools/ci/mutation/evaluate.py "$out" '' "$base"
    exit $?
fi
grep -qs '^\[tool\.mutmut\]' backend/pyproject.toml \
    && { echo 'GAP CONFIG_CONFLICT: backend/pyproject.toml [tool.mutmut] would override the bounded scope'; exit 3; }
work=$(mktemp -d) || exit 3
trap 'rm -rf "$work"' EXIT
git archive HEAD backend | tar -x -C "$work" || exit 3
# Every tracked top-level backend entry outside src/tests (template.yaml and any
# other non-Python file the tests read) must reach mutants/, which mutmut
# otherwise populates with src, tests and config only. Top-level entries only:
# mutmut copies also_copy files without creating parent directories.
also_copy=$(git ls-tree --name-only HEAD -- backend/ \
    | grep -v '^backend/src$' | grep -v '^backend/tests$' | sed 's#^backend/##')
{
    printf '[mutmut]\nsource_paths=src\nonly_mutate=\n'
    printf '    %s\n' $(printf '%s\n' "$changed" | sed 's#^backend/##')
    printf 'pytest_add_cli_args_test_selection=\n    tests/unit\n    tests/contract\n'
    # Shared dev hosts stall under others' load: (estimate + 5) * 30 s wall-clock
    # per mutant absorbs spikes without scoring slow-but-finishing runs as
    # timeouts. Genuine hangs still time out (later); timeouts stay UNRESOLVED.
    printf 'timeout_constant=5.0\ntimeout_multiplier=30.0\n'
    if [[ -n "$also_copy" ]]; then
        printf 'also_copy=\n'
        printf '    %s\n' $also_copy
    fi
} > "$work/backend/setup.cfg"
# shortcut: one fixed 1800 s bound for the whole run; size it per changed scope if real runs approach it.
(cd "$work/backend" && timeout 1800 "${MUTMUT[@]}" run) > "$out/mutmut-run.txt" 2>&1
rc=$?
(cd "$work/backend" && "${MUTMUT[@]}" export-cicd-stats && "${MUTMUT[@]}" results --all true) \
    >> "$out/mutmut-results.txt" 2>&1 \
    || { echo 'GAP REPORT_INCOMPLETE: mutmut export/results failed'; exit 3; }
cp "$work/backend/mutants/mutmut-cicd-stats.json" "$out/" 2>/dev/null \
    || { echo 'GAP REPORT_INCOMPLETE: mutmut stats absent'; exit 3; }
# No exec: the EXIT trap must remove the owned workspace on PASS, FAIL and GAP.
python3 tools/ci/mutation/evaluate.py "$out" "$changed" "$base" "$rc"
exit $?
