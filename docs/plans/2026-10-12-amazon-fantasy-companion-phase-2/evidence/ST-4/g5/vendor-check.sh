#!/usr/bin/env bash
set -euo pipefail
pin=04678835350b529b44ab69ee5f805ca21cab5e76
source_repo="$HOME/alphazede/Alphazedehq"
git -C "$source_repo" merge-base --is-ancestor "$pin" origin/main
python3 docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g5/check-vendor.py "$pin"
grep -q 'Permission is hereby granted' tools/spec/VENDORED.md
grep -q 'Permission is hereby granted' THIRD_PARTY_NOTICES.md
git diff --exit-code HEAD -- THIRD_PARTY_NOTICES.md
