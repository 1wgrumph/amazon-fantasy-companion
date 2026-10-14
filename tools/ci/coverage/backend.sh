#!/usr/bin/env bash
# CMD-COVERAGE-BACKEND: changed-line coverage of committed backend/src since <base>.
# Exit 0 PASS, 1 FAIL, 3 GAP (missing tool, report or denominator); never PASS on missing data.
set -u
(($# == 2)) || { echo 'usage: backend.sh <base_sha> <evidence_dir>' >&2; exit 2; }
base=$1 out=$2
root=$(git rev-parse --show-toplevel) || exit 3
cd "$root" || exit 3
for tool in python3 python3.12 diff-cover; do
    command -v "$tool" >/dev/null || { echo "GAP required tool missing: $tool"; exit 3; }
done
for module in coverage pytest; do
    python3.12 -m "$module" --version >/dev/null 2>&1 || { echo "GAP required tool missing: python3.12 -m $module"; exit 3; }
done
[[ -d backend/src ]] || { echo 'GAP REPORT_INCOMPLETE: no backend/src/ tree'; exit 3; }
mkdir -p "$out" || exit 3
rm -f "$out/.coverage" "$out/coverage.xml" "$out/diff-cover.json" "$out/coverage-result.json"
# Fixed rcfile keeps the measured scope independent of repository coverage settings.
python3.12 -m coverage run --rcfile=/dev/null --source=backend/src --data-file="$out/.coverage" \
    -m pytest backend/tests/unit backend/tests/contract || { echo 'FAIL backend tests failed under coverage'; exit 1; }
python3.12 -m coverage xml --rcfile=/dev/null --data-file="$out/.coverage" -o "$out/coverage.xml" \
    || { echo 'GAP REPORT_INCOMPLETE: no native coverage XML'; exit 3; }
exec python3 tools/ci/coverage/evaluate.py "$base" "$out/coverage.xml" "$out"
