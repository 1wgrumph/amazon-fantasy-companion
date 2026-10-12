## What changed

- Require VnV review with an explicit base-to-HEAD commit scope when guidance exists; record REFUSED_NO_VNV otherwise.
- Add shared gate and companion repository entries, preserve PR editing in a dedicated reference, and bound the skill to 52 lines / 410 words.
- Add stock skill metadata and independent trigger classification checks.

## Why

S03 implements the approved D4-C skill contract. The previous skill lacked the VnV gate and exceeded the size limit. Standalone bug reviews now route outside the PR workflow.

## Validation

Candidate: `2fc547c7e3041538bcd6a4fed904fad8d9f1a89d`.

### CMD-D4C-TEST: exit 0

```bash
bash skills/ship-pull-request/tests/edit-pr.test.sh && grep -q 'REFUSED_NO_VNV' skills/ship-pull-request/SKILL.md && grep -qE 'docs/vnv/AGENTS.md|Vnv/AGENTS.md' skills/ship-pull-request/SKILL.md && grep -q -- '--scope=commits=' skills/ship-pull-request/SKILL.md && grep -q 'tools/ci/gate.sh' skills/ship-pull-request/references/GATES.md && grep -q 'amazon-fantasy-companion' skills/ship-pull-request/references/GATES.md && test -f skills/ship-pull-request/references/EDIT-PR.md; rc=$?; echo "exit=$rc"; (exit $rc)
```

### CMD-SKILL-SIZE: exit 0

```bash
python3 -m unittest discover -s skills/ship-pull-request/tests -t skills/ship-pull-request/tests -p 'test_ship_pull_request.py' -k test_creator_validation_and_repository_metadata -v && test "$(sha256sum < $HOME/alphazede/Alphazedehq/tools/bran/runtime/bran | cut -d' ' -f1)" = "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["sha256"])' $HOME/alphazede/Alphazedehq/tools/bran/runtime/bran-release-pin.json)" && $HOME/alphazede/Alphazedehq/tools/bran/runtime/bran check . bran-strict; rc=$?; echo "exit=$rc"; (exit $rc)
```

### CMD-SKILL-TRIGGER: exit 0

```bash
e=$(mktemp -d) && cp skills/ship-pull-request/SKILL.md skills/ship-pull-request/tests/trigger-requests.json "$e"/ && (cd "$e" && claude --version > harness-version.txt && claude -p 'You are an independent skill-routing evaluator. Read SKILL.md and trigger-requests.json in this directory. For each request id, answer MATCH if an agent with this skill installed should use it for that request according to its description, otherwise NO_MATCH. Reply with only a JSON object mapping every request id to MATCH or NO_MATCH.' --output-format json --max-turns 5 --allowedTools Read --disallowedTools Bash,Write,Edit,WebFetch,WebSearch < /dev/null > session.json && jq -r .result session.json | python3 -c 'import json,sys; t=sys.stdin.read(); print(json.dumps(json.loads(t[t.index("{"):t.rindex("}")+1])))' > results.json) && cp "$e"/results.json $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S03/g4/trigger-results-ship-pull-request.json && cp "$e"/harness-version.txt "$e"/session.json $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S03/g4/ && SHIP_PULL_REQUEST_TRIGGER_RESULTS=$HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/evidence/S03/g4/trigger-results-ship-pull-request.json python3 -m unittest discover -s skills/ship-pull-request/tests -t skills/ship-pull-request/tests -p 'test_ship_pull_request.py' -k test_trigger_classifications -v; rc=$?; echo "exit=$rc"; (exit $rc)
```

### CMD-D4-AGNOSTIC: exit 0

```bash
d=$(git diff --name-only --diff-filter=ACMR 47c46f2e16fed060482a1bf3a0e34ddcb9bc57fc..HEAD -- skills/ship-pull-request) && f=$(printf '%s\n' "$d" | grep -vE '^$|\.pyc$|(^|/)(__pycache__|build|dist)/|^skills/ship-pull-request/references/GATES\.md$'; true) && printf 'scanned: %s\n' ${f:-none} && test -n "$f" && { git grep -nIiE '1wgrumph|alphazede/|amazon-fantasy-companion|gridmarket|betbot|\bpilot\b|exclusion' HEAD -- $f; [ $? -eq 1 ]; }; rc=$?; echo "exit=$rc"; (exit $rc)
```

All edit/readback tests passed; portable creator validation and BRAN strict passed. Trigger results: request_1 MATCH, request_2 NO_MATCH. The agnostic check scanned only the four changed non-gate-data files.

## Residual risk

- Draft pending the configured independent review (including OCR) and integration landing; no review or merge is claimed by this implementer.
- Landing proof SEIT-AFC-D4-05.L and combined Wave 1 scan remain integration obligations.
- Reverify is not applicable: no compiled binary is built or claimed.
- Repository-wide CI was not run locally; this packet ran its four declared verification commands.
