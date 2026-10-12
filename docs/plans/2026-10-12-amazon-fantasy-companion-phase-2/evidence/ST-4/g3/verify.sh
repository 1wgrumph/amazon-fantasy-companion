set -euo pipefail
export UV_OFFLINE=1 UV_PYTHON=3.12 PYTHONDONTWRITEBYTECODE=1
spec=spec/amazon-fantasy-companion
evidence=docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g3
run() {
  printf 'COMMAND:'
  printf ' %q' "$@"
  printf '\n'
  local result=0
  "$@" || result=$?
  printf 'EXIT: %s\n' "$result"
  return "$result"
}
for figure in "$spec"/figures/*.yaml; do
  run uv run --script tools/spec/diagram.py render "$figure"
done
run uv run --script tools/spec/spec_build.py "$spec" "$spec/amazon-fantasy-companion.md"
run uv run --script tools/spec/spec_lint.py "$spec"
run uv run --script tools/spec/diagram.py lint "$spec"
second="$evidence/rebuild.tmp.md"
trap 'rm -f "$second"' EXIT
run uv run --script tools/spec/spec_build.py "$spec" "$second"
run cmp "$spec/amazon-fantasy-companion.md" "$second"
rm -f "$second"
run python3 "$evidence/check-spec.py"
run bash -c '! grep -nRE "\*\*(BLUF|Frame|Who|What|Why|How|When|Where):?\*\*" spec/amazon-fantasy-companion/'
run grep -n -i 'sample footage\|Mode A' "$spec/amazon-fantasy-companion.md"
run python3 "$evidence/check-spec.py" --paths-only
run git diff --check -- . ":!$spec/amazon-fantasy-companion.md"
run git diff --cached --check -- . ":!$spec/amazon-fantasy-companion.md"
run sha256sum "$spec/amazon-fantasy-companion.md"
