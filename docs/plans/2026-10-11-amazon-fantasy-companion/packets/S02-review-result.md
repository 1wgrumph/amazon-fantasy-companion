# S02 Review Result — IE-P1-2 (PR #303)

- Candidate: `afc/s02-setup-a-repo` @ `451499b9827db85e8f12f056c849774af8bd1f77`
- Base: `47c46f2` (origin/main); PR: https://github.com/alphazede/Alphazedehq/pull/303 (draft, open, base main, remote head == candidate — verified by reviewer via `gh api`)
- Review unit: Phase 1 integration step IE-P1-2 (OA-AFC-A3 option A; this PR reviewed once at its own step)
- Reviewer route: Muse Code / Muse Spark 1.3 / max (frozen tech-writing snapshot primary; no fallback used)
- Author: Codex (did not self-review; independent session)
- Write set (7 paths, all within `skills/setup-a-repo/`; `git status` clean, no other changes in range):
  `SKILL.md`, `references/workflow-authoring.md`, `templates/ci.yml`,
  `scripts/check-workflows.py`, `tests/test_check_workflows.py`,
  `tests/test_setup_a_repo.py`, `tests/trigger-requests.json`

## Verdict: PASS

No introduced actionable defect found. Nothing meets the finding bar
(`file:line` + failing test or reproducer against the approved contract),
so no repair round is spent.

## Findings

| ID | Sev | Location | Defect | Fix |
|----|-----|----------|--------|-----|
| — | — | — | No findings. | — |

Advisory observations (not findings; no repair budget spent):

- ADV-01: `skills/setup-a-repo/scripts/check-workflows.py:101` —
  the checker constrains `hygiene` only when present (line 128-129) but does
  not require its presence: a derived workflow with filters `{code}` and jobs
  `{changes, code}` passes. The guide's "keep the hygiene area unconditional"
  presumes it exists. AC-AFC-CI-02 does not require a hygiene job, so this is
  not a contract violation; flagging only so S09 (which adapts this template
  for the real gate) keeps hygiene.
- ADV-02: `check-workflows.py:63` — the secrets guard rejects the word
  `secrets` anywhere in the document (fail-closed, safe direction). A future
  area whose gate path or name contains that word (e.g.
  `tools/ci/check-secrets.sh`) will fail the checker. Safe but potentially
  surprising; no change requested.
- ADV-03 (residual risk, also declared by implementer): hosted runtime
  behavior is unproven at this slice by design — the checker is structural.
  The template's dorny `base` expression and empty-token git fallback were
  verified by the reviewer against the upstream `releases/v3` README
  (empty token falls back to git; same-branch base diffs against the
  pre-push commit); first real PR/push exercise lands at S09.

## Contract check (what was actually reviewed, not just re-run)

- Workflow-authoring rules (`references/workflow-authoring.md`):
  `pull_request` + `push:[main]` only with explicit `pull_request_target`
  ban; workflow-level path filters unset (correct rationale: skipped
  workflows leave required checks pending); concurrency grouped by
  `github.workflow` + `github.ref` with `cancel-in-progress: true`;
  one literal stable `gate / <area>` name per area, no matrices;
  full 40-char SHA pins plus an explicit "SHA alone is not a safety
  assessment, follow the supply-chain scan" clause; workflow
  `permissions: {contents: read}` with identical-only job overrides;
  no secrets passed/inherited, no environments, `persist-credentials: false`;
  standard hosted runners only. Budget section states free public runners,
  the 2,000 `gh_private_minutes` Free entitlement, hard-stop at zero, and
  no paid overage without owner authority (C11 / RISK-AFC-08). Checker scope
  honestly disclaimed (structural only; exit 0/1/2 semantics match the code).
- Checker (`scripts/check-workflows.py`, 168 lines, read in full):
  exact-equality trigger match (any extra event, branch, or path filter
  fails); exact `contents: read` at workflow and job level; substring
  concurrency check that can only narrow grouping (safe direction);
  case-insensitive `secrets`-word ban over the whole document;
  `changes`-job shape pinned (unconditional full checkout, filter id, empty
  token, exact `base` expression); inline area filters required to
  correspond exactly to area jobs with exact `needs`/`if` expressions;
  runner allowlist of real hosted labels; `uses`/`environment`/`strategy`/
  `container`/`services` rejected per job; SHA regex requires a full 40-hex
  pin; every `actions/checkout` step requires `persist-credentials: false`;
  duplicate YAML keys, non-string keys, merge keys, multi-doc tails, and
  malformed input all fail closed without tracebacks. `yaml_implicit_resolvers`
  override builds a new dict (no `SafeLoader` global mutation).
- Negative tests (`tests/test_check_workflows.py`, read in full): 25
  violation fixtures, each asserting exit 1 plus its diagnostic, covering
  every AC-AFC-CI-02 rule and the main bypasses (target-event, extra event,
  condition/output/dependency bypass, filter-token, shallow checkout,
  dynamic/duplicate names, matrix, tag pins, both permission escalations,
  both secret syntaxes, credential persistence, both runner escapes,
  environment binding, conditional hygiene); 6 malformed inputs fail closed;
  multi-file and usage-error paths covered. Tests invoke the real checker
  as a subprocess and assert real exit codes.
- Template (`templates/ci.yml`): passes the checker; both pins verified by
  the reviewer against upstream (`actions/checkout v5.0.1 = 93cb6ef…`,
  `dorny/paths-filter releases/v3 = 0e4a8c6…`); no secrets, no
  `pull_request_target`, fork-safe (read-only token, no persistence,
  git-mode change detection).
- Skill leanness / agnosticism: `SKILL.md` 59 lines / 421 words (under
  60/650); description names the matching trigger and the setup-pre-commit
  non-trigger; `azedge` worked-reference and private-scope repo names
  removed; CMD-D4-AGNOSTIC clean on the slice paths.
- Stock pattern: `tests/test_setup_a_repo.py` mirrors
  `skills/release-process/tests/test_release_process.py` line-for-line
  except the plan-directed deltas (`SETUP_A_REPO` prefix, 650-word limit,
  added `[TODO]` assertion); `quick_validate` runs only on a temp
  portable-fields copy, never on the repo file; `trigger-requests.json`
  matches `gate_declarations.spec_and_docs.trigger_requests.setup-a-repo`
  verbatim.

## Re-run evidence (reviewer ran every VERIFY command; all exit 0)

| Command | Exit | Evidence |
|---------|------|----------|
| CMD-D4B-TEST | 0 | `34 passed` via offline scanned wheels; `templates/ci.yml: PASS` |
| CMD-SKILL-SIZE | 0 | `test_creator_validation_and_repository_metadata … ok` (`Skill is valid!`); pinned BRAN `bran check . bran-strict` pass; 59 lines / 421 words |
| CMD-SKILL-TRIGGER | 0 | fresh evaluator session (Read-only, `</dev/null`), result `{"request_1":"MATCH","request_2":"NO_MATCH"}`; `test_trigger_classifications … ok`. Evidence: `/tmp/afc-s02-review-evidence/` (uncommitted) |
| CMD-D4-AGNOSTIC | 0 | no match on `skills/setup-a-repo` |
| CMD-SCAN | 0 | `verdict: PASS` receipt re-grepped; wheel sha256s re-verified byte-identical to receipt (`WHEELS-MATCH`); receipt (2026-10-12T06:57:00Z) predates this review's wheel use |

Implementer's reported exit codes reproduce exactly. Commit identity verified:
author `Codex <1wgrumph+codex@gmail.com>`, committer `1wgrumph <1wgrumph@gmail.com>`.

## OCR (coverage assist, delegate mode — required, all exit 0, no tool failures)

- `ocr delegate preview --from 47c46f2 --to 451499b` (open-code-review
  v1.12.13): 3 reviewable / 7 total. Excluded with reasons: `SKILL.md`,
  `references/workflow-authoring.md` (`unsupported_ext`);
  `tests/test_check_workflows.py`, `tests/test_setup_a_repo.py`
  (`default_path`). Per the reviewer skill the list is advisory: the
  reviewer read all four excluded files in full anyway (see Contract check).
- `ocr delegate rule` run for every listed file (7/7, exit 0 each):
  - `scripts/check-workflows.py`, `tests/test_check_workflows.py`,
    `tests/test_setup_a_repo.py` → `system / **/*.{py,pyi,ipynb}` rule group
    (precision-over-recall, dead code, edge cases, exceptions, security).
    Applied: no dead code, no swallowed exceptions (all caught errors become
    `errors` entries or exit codes), no `shell=True`/eval/pickle, YAML always
    through the hardened `WorkflowLoader`, no secret/PII literals.
  - `templates/ci.yml` → `**/*.{yaml,yml}` (key spelling): keys
    `pull_request`, `push`, `permissions`, `concurrency`, `cancel-in-progress`,
    `persist-credentials`, `fetch-depth` all spelled correctly.
  - `tests/trigger-requests.json` → `**/*.{json,json5}` (key spelling):
    `request_1`, `request_2` correct.
  - `SKILL.md`, `references/workflow-authoring.md` → `system / default`
    (correctness/security/performance/maintainability/coverage): rules match
    AC-AFC-CI-02 clause-for-clause; no overclaim (checker limits and
    no-operational-proof clauses present); coverage present via the 25
    negative fixtures.
- OCR finds no defects and gives no verdict (by design); it contributed
  only the file list and the per-file rule lenses above.

## Reverify

Reverify: not applicable — no compiled binary is built or claimed
(per frozen review path; skill text, Python scripts, workflow YAML only).

## Proof rows

- SEIT-AFC-D4-02.T: PASS (checker exits 0 on template; guide states CI-02 rules + free runners + budget)
- SEIT-AFC-D4-02.S: PASS (SKILL.md 59 lines / 421 words)
- SEIT-AFC-D4-05.T: PASS (fresh MATCH/NO_MATCH evidence reproduced by reviewer)
- SEIT-AFC-D4-05.L: PENDING (draft PR #303 open; merge outside review authority; rebase/merge-commit per landing skill at merge time)
- SEIT-AFC-D4-06: PASS (agnostic grep clean)

## developer_feedback

- used_for: S02 independent review (workflow-authoring rules, checker, template, skill validation)
- worked_well: offline scanned-wheel re-run reproduced bit-for-bit; fresh trigger evaluator agreed on first run; dorny/action pins verifiable against upstream; OCR delegate ran clean on all 7 files
- needs_work: no new observations
- onboarding_zero_to_hello_world: unknown
- would_build_again: n/a (review, not build)
- AWS: n/a
- friction: none (severity None)
- feature_requests: n/a
- tools: ocr v1.12.13, uv 0.11.6 (offline), python3 + PyYAML 6.0.3, BRAN strict via pinned main-checkout runtime (slice worktree ships no `tools/bran/runtime/bran`, same as implementer), gh, dorny README (network fetch for claim verification)
