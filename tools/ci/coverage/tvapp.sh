#!/usr/bin/env bash
# CMD-COVERAGE-TVAPP: changed-line coverage of committed tv-app/app/src/main since <base>.
# Exit 0 PASS, 1 FAIL, 3 GAP (missing tool, report or denominator); never PASS on missing data.
# Extra Gradle flags (e.g. --offline --no-daemon) come from AFC_GRADLE_ARGS.
set -u
(($# == 2)) || { echo 'usage: tvapp.sh <base_sha> <evidence_dir>' >&2; exit 2; }
base=$1 out=$2
root=$(git rev-parse --show-toplevel) || exit 3
cd "$root" || exit 3
for tool in python3 diff-cover; do
    command -v "$tool" >/dev/null || { echo "GAP required tool missing: $tool"; exit 3; }
done
if [[ -n "${JAVA_HOME:-}" ]]; then
    [[ -x "$JAVA_HOME/bin/java" ]] || { echo 'GAP required tool missing: java (JAVA_HOME)'; exit 3; }
else
    command -v java >/dev/null || { echo 'GAP required tool missing: java'; exit 3; }
fi
sdk=${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}
[[ -n "$sdk" && -d "$sdk" ]] || { echo 'GAP required tool missing: Android SDK (ANDROID_HOME or ANDROID_SDK_ROOT)'; exit 3; }
[[ -d tv-app/app/src/main ]] || { echo 'GAP REPORT_INCOMPLETE: no tv-app/app/src/main/ tree'; exit 3; }
[[ -x tv-app/gradlew ]] || { echo 'GAP required tool missing: tv-app/gradlew'; exit 3; }
mkdir -p "$out" || exit 3
out=$(cd "$out" && pwd) || exit 3
report=tv-app/app/build/reports/jacoco/afcCoverageReport/afcCoverageReport.xml
# A leftover report from an earlier run must never be scored.
rm -f "$report" "$out/jacoco.xml" "$out/changed.diff" "$out/diff-cover.json" "$out/coverage-result.json"
# shellcheck disable=SC2086 # AFC_GRADLE_ARGS is a word list by design.
./tv-app/gradlew -p tv-app ${AFC_GRADLE_ARGS:-} testDebugUnitTest :app:afcCoverageReport > "$out/gradle.txt" 2>&1 \
    || { tail -n 20 "$out/gradle.txt"; echo 'FAIL tv-app unit tests or :app:afcCoverageReport failed'; exit 1; }
[[ -s "$report" ]] || { echo "GAP REPORT_INCOMPLETE: JaCoCo XML absent: $report"; exit 3; }
cp "$report" "$out/jacoco.xml" || exit 3
candidate=$(git rev-parse HEAD) || exit 3
# Zero execution data is a zero-test run, never coverage; then bind the report to the measured source.
python3 - "$out/jacoco.xml" "$candidate" <<'EOF' || exit 3
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
xml, candidate = Path(sys.argv[1]), sys.argv[2]
try:
    root = ET.parse(xml).getroot()
except ET.ParseError as e:
    sys.exit(f'GAP REPORT_INCOMPLETE: JaCoCo XML unparseable: {e}')
if root.tag != 'report' or root.find('sessioninfo') is None:
    sys.exit('GAP REPORT_INCOMPLETE: JaCoCo XML has no execution session (zero-test run)')
files = {p.as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(Path('tv-app/app/src/main').rglob('*')) if p.suffix in ('.kt', '.java')}
binding = json.dumps({'candidate': candidate, 'files': files}, sort_keys=True)
with xml.open('a', encoding='utf-8') as f:
    f.write(f'<!-- afc-coverage-binding {binding} -->\n')
EOF
exec python3 tools/ci/coverage/evaluate.py "$base" "$out/jacoco.xml" "$out" --profile=tvapp
