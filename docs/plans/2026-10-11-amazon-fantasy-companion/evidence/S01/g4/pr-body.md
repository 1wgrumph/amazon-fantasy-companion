## What changed

- Replace the setup-pre-commit scaffold with a bounded procedure for one shared gate used by pre-commit, pre-push and Actions.
- Supply a gate template with changed-area selection and blocking failure/tool-gap exits, plus an idempotent installer that preserves conflicting hooks.
- Exercise the installer and gate in real temporary Git repositories, including deliberately blocked commits and pushes.

## Why

The skill previously contained only unfinished scaffold instructions. This S01 candidate implements the approved shared-gate contract and keeps standalone workflow authoring with setup-a-repo.

## Validation

Candidate: `21b4512a9e698f60dc82176996dc8dfc8b3dccb7`.
SKILL.md: 46 lines, 331 words. Independent routing: request_1 MATCH; request_2 NO_MATCH.

- CMD-D4A-TEST: exit 0.

```bash
bash skills/setup-pre-commit/tests/test-install-hooks.sh; rc=$?; echo "exit=$rc"; (exit $rc)
```

- CMD-SKILL-SIZE: exit 0.

```bash
python3 -m unittest discover -s skills/setup-pre-commit/tests -t skills/setup-pre-commit/tests -p 'test_setup_pre_commit.py' -k test_creator_validation_and_repository_metadata -v && test "$(sha256sum < $HOME/alphazede/Alphazedehq/tools/bran/runtime/bran | cut -d' ' -f1)" = "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["sha256"])' $HOME/alphazede/Alphazedehq/tools/bran/runtime/bran-release-pin.json)" && $HOME/alphazede/Alphazedehq/tools/bran/runtime/bran check . bran-strict; rc=$?; echo "exit=$rc"; (exit $rc)
```

- CMD-SKILL-TRIGGER: exit 0.

```bash
e=$(mktemp -d) && cp skills/setup-pre-commit/SKILL.md skills/setup-pre-commit/tests/trigger-requests.json "$e"/ && (cd "$e" && claude --version > harness-version.txt && claude -p 'You are an independent skill-routing evaluator. Read SKILL.md and trigger-requests.json in this directory. For each request id, answer MATCH if an agent with this skill installed should use it for that request according to its description, otherwise NO_MATCH. Reply with only a JSON object mapping every request id to MATCH or NO_MATCH.' --output-format json --max-turns 5 --allowedTools Read --disallowedTools Bash,Write,Edit,WebFetch,WebSearch < /dev/null > session.json && jq -r .result session.json | python3 -c 'import json,sys; t=sys.stdin.read(); print(json.dumps(json.loads(t[t.index("{"):t.rindex("}")+1])))' > results.json) && cp "$e"/results.json $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S01/g4/trigger-results-setup-pre-commit.json && cp "$e"/harness-version.txt "$e"/session.json $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S01/g4/ && SETUP_PRE_COMMIT_TRIGGER_RESULTS=$HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S01/g4/trigger-results-setup-pre-commit.json python3 -m unittest discover -s skills/setup-pre-commit/tests -t skills/setup-pre-commit/tests -p 'test_setup_pre_commit.py' -k test_trigger_classifications -v; rc=$?; echo "exit=$rc"; (exit $rc)
```

- CMD-D4-AGNOSTIC: exit 0.

```bash
d=$(git diff --name-only --diff-filter=ACMR 47c46f2e16fed060482a1bf3a0e34ddcb9bc57fc..HEAD -- skills/setup-pre-commit) && f=$(printf '%s\n' "$d" | grep -vE '^$|\.pyc$|(^|/)(__pycache__|build|dist)/|^skills/ship-pull-request/references/GATES\.md$'; true) && printf 'scanned: %s\n' ${f:-none} && test -n "$f" && { git grep -nIiE '1wgrumph|alphazede/|amazon-fantasy-companion|gridmarket|betbot|\bpilot\b|exclusion' HEAD -- $f; [ $? -eq 1 ]; }; rc=$?; echo "exit=$rc"; (exit $rc)
```

- `shellcheck skills/setup-pre-commit/templates/gate.sh skills/setup-pre-commit/scripts/install-hooks.sh skills/setup-pre-commit/tests/test-install-hooks.sh`: exit 0.
- `git diff --cached --check`: exit 0 before commit.

## Residual risk

- Draft pending the configured independent phase review (including OCR) and integration/landing checks; author verification is not independent assurance.
- No merge or runtime installation is authorized in this worker packet.
- Template adoption requires mapping the target repository's checks and paths; its initial hygiene check alone is not a full project gate.
- Reverify is not applicable: shell, Python, YAML and skill text only; no compiled binary is built or claimed.
