#!/usr/bin/env bash
set -uo pipefail
export UV_OFFLINE=1 UV_PYTHON=3.12 PYTHONDONTWRITEBYTECODE=1
spec=spec/amazon-fantasy-companion
evidence=docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g4
run() {
 printf 'COMMAND:'; printf ' %q' "$@"; printf '\n'
 "$@"
 result=$?
 printf 'EXIT: %s\n' "$result"
}
run uv run --script tools/spec/spec_build.py "$spec" "$spec/amazon-fantasy-companion.md"
run uv run --script tools/spec/spec_lint.py "$spec"
run uv run --script tools/spec/diagram.py lint "$spec"
second=$(mktemp)
trap 'rm -f "$second"' EXIT
run uv run --script tools/spec/spec_build.py "$spec" "$second"
run cmp "$spec/amazon-fantasy-companion.md" "$second"
run python3 "$evidence/check-links.py"
run python3 -c 'from pathlib import Path; import re; assert not any(re.search(r"\*\*(BLUF|Frame|Who|What|Why|How|When|Where):?\*\*", p.read_text()) for p in Path("spec/amazon-fantasy-companion").glob("*.md")); print("Label grep clean")'
run python3 tools/ci/check_paths.py
run bash tools/ci/gate.sh
