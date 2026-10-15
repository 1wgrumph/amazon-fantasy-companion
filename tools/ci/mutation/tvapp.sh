#!/usr/bin/env bash
# CMD-MUTATION-TVAPP: PIT score for changed host-runnable files in tvapp_scope.json (DEC-AFC-SD-057).
# Runs :app:pitestDebug on a disposable `git archive` copy; never mutates the checkout.
# Exit 0 PASS, 1 FAIL, 3 GAP. Extra Gradle flags (e.g. --offline --no-daemon) come from AFC_GRADLE_ARGS.
set -u
(($# == 2)) || { echo 'usage: tvapp.sh <base_sha> <evidence_dir>' >&2; exit 2; }
base=$1 out=$2
root=$(git rev-parse --show-toplevel) || exit 3
cd "$root" || exit 3
for tool in python3 tar timeout; do
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
mkdir -p "$out" || exit 3
out=$(cd "$out" && pwd) || exit 3
rm -f "$out/mutations.xml" "$out/pitest-run.txt" "$out/mutation-result.json"
changed=$(git diff --no-renames --name-only --diff-filter=AM "$base...HEAD" -- tv-app/app/src/main \
    | grep -E '\.(kt|java)$')
if [[ -z "$changed" ]]; then
    python3 tools/ci/mutation/tvapp_evaluate.py "$out" '' "$base"
    exit $?
fi
work=$(mktemp -d) || exit 3
trap 'rm -rf "$work"' EXIT
# Host tests read the OpenAPI contract from the repository root (afc.repoRoot); without it PIT's green run fails (GAP).
paths=(tv-app)
git cat-file -e HEAD:backend/src/api/openapi.yaml 2>/dev/null && paths+=(backend/src/api/openapi.yaml)
git archive HEAD "${paths[@]}" | tar -x -C "$work" || exit 3
[[ -x "$work/tv-app/gradlew" ]] || { echo 'GAP required tool missing: tv-app/gradlew'; exit 3; }
# shortcut: one fixed 1500 s bound for the whole PIT run; size it per changed scope if real runs approach it.
# shellcheck disable=SC2086 # AFC_GRADLE_ARGS is a word list by design.
# The PIT Android plugin needs AGP's legacy variant API; build.gradle.kts applies it only under these flags.
(cd "$work" && timeout 1500 ./tv-app/gradlew -p tv-app ${AFC_GRADLE_ARGS:-} -Pandroid.newDsl=false \
    -Pandroid.onlyEnableUnitTestForTheTestedBuildType=false \
    --init-script "$root/tools/ci/mutation/tvapp-pitest.gradle" :app:pitestDebug) \
    > "$out/pitest-run.txt" 2>&1
rc=$?
((rc == 0)) || tail -n 20 "$out/pitest-run.txt"
mapfile -t reports < <(find "$work/tv-app/app/build/reports/pitest" -name mutations.xml 2>/dev/null)
if ((rc == 0 && ${#reports[@]} != 1)); then
    echo "GAP REPORT_INCOMPLETE: expected one PIT mutations.xml, found ${#reports[@]}"; exit 3
fi
((rc == 0)) && { cp "${reports[0]}" "$out/mutations.xml" || exit 3; }
# No exec: the EXIT trap must remove the owned workspace on PASS, FAIL and GAP.
python3 tools/ci/mutation/tvapp_evaluate.py "$out" "$changed" "$base" "$rc"
exit $?
