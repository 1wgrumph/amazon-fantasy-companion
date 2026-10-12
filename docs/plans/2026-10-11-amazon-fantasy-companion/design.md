---
type: design
status: amended
lifecycle: AFC-2026-10-11
technical_plan: amazon-fantasy-companion-technical-plan.md
revision_note: "Phase 1 regeneration (DEC-AFC-SD-023, DEC-AFC-SD-024). Product design of f885e48 moves to the Phase 1 spec track (SysML v2 models, D1) and Phase 2 (technical plan §Deferred to the spec track or Phase 2). OR-01 relabel: spec-track steps ST-1..ST-5 (were P2-1..P2-5)."
---

# Amazon Fantasy Companion — Design (Phase 1)

This design realizes the Phase 1 technical plan. It covers:

- **D5**, the shared spec-authoring skill;
- **D4**, the shared CI/CD capability;
- the minimum this repository needs to use them: a gate entrypoint with
  `spec`, `docs` and `hygiene` areas, local hooks, a GitHub Actions
  workflow, the vendored spec tools and a Vnv guidance tree;
- the start of the Scribe log;
- the Phase 1 spec track and the Phase 2 sequence.

It contains no product architecture. The product is specified in the
Phase 1 spec track (ST-1..ST-5), from a requirements register and SysML v2
models, under its own plan directory (DEC-AFC-SD-023).

D4 and D5 live outside this repository, in the private
`alphazede/Alphazedehq` repository's `skills/` and `hooks/` trees. They land
there through their own pull requests.

Views: `views/views.json`. Phase 1 uses MODEL-AFC-V4, the delivery tooling
view, and the Phase 1 views the Systems Modeler lists there. The product
views V1..V3 are kept as spec-track reference input only.

## Design lenses

Slices may cite only the lens names in this table in `design_lenses`.

| Lens | Question it answers |
|---|---|
| Contract-first | Does the slice build against a frozen contract without changing it? |
| Security controls | Are secrets and local paths kept out of tracked files, and do workflows keep their trust boundary? |
| Spec discipline | Does the specification tooling lint cleanly and rebuild byte-identically? |
| Parallel-safe CI | Is the check deterministic, path-filtered, pinned and safe to run concurrently? |
| Lean skill | Is the skill within skill_size_max, tested on a matching and a non-matching request, with overflow in references and no duplicated peer? |
| Repo-agnostic | Does shared skill or hook text work in any repository without naming repositories, owners or a project-specific environment? |
| Developer feedback | Does the work carry a developer_feedback section the Scribe can ingest? |
| Owner boundary | Does the work stop at owner-only actions and the conditionals C7, C9..C14? |

## Repository layout (Phase 1 target)

This repository (`1wgrumph/amazon-fantasy-companion`):

```
THIRD_PARTY_NOTICES.md            GridMarket MIT notice for the vendored spec tools (S42)
.githooks/pre-commit, pre-push    call tools/ci/gate.sh (S09)
.github/workflows/ci.yml          calls tools/ci/gate.sh per area (S09)
tools/ci/gate.sh                  gate entrypoint (CONTRACT-AFC-GATE, S09)
tools/ci/check_paths.py           rule-12 shape scan + credential patterns (S09)
tools/ci/check_docs.py            Vnv area headings + relative Markdown links (S09)
tools/ci/check_workflows.py       vendored D4-B workflow checker (S09)
tools/ci/VENDORED.md              source repository and D4-A/D4-B merge commits (S09)
tools/ci/tests/                   gate tests (S09T)
tools/spec/                       D5 scripts vendored by the skill's vendor step; VENDORED.md (S42)
docs/vnv/AGENTS.md                Vnv index (S07)
docs/vnv/{ci-cd,spec,developer-feedback}/AGENTS.md   Phase 1 areas (S07)
docs/developer-feedback/observations.md              Scribe running log (S08)
docs/plans/2026-10-11-amazon-fantasy-companion/evidence/skill-links.txt   harness link readback (S06L)
```

The shared repository (`alphazede/Alphazedehq`, private) is a cross-repo
write set:

```
skills/setup-pre-commit/          D4-A (S01)
skills/setup-a-repo/              D4-B (S02)
skills/ship-pull-request/         D4-C (S03)
skills/spec-authoring/            D5 (S06)
skills/use-requirements-system/SKILL.md   description non-trigger only, if OD-AFC-07 = yes (S06)
skills/ci-cd/SKILL.md             only if OD-AFC-01 = B (S41)
hooks/ci-gate-hook.sh, install-ci-gate-hook.py, test-ci-gate-hook.sh, README.md   D4-E (S11T, S11)
```

Paths in committed files are repository-relative (AC-AFC-PATH-01).

### Placement mapping

The D4 and D5 placements of the Systems Modeler placement receipt
(`specialists/systems-modeler-receipt.md` §D4, §D5) are adopted unchanged.
The receipt's product placements (TV app, backend) are spec-track input (ST-3). The
receipt's packaging note F6 applies to D5: `azdiagram` is a package, so D5
ships the single-file PEP 723 wrapper `scripts/diagram.py`.

## Decisions

### DES-AFC-D5 — Shared spec-authoring skill (Alphazedehq)

- One new shared skill `skills/spec-authoring/` in `alphazede/Alphazedehq`
  (S06; branch `spec-authoring/d5`, worktree
  `worktrees/Alphazedehq-spec-authoring`), generalized from the GridMarket
  kit at a pinned `1wgrumph/gridmarket` commit (`spec/template/`,
  `skills/spec-author`, `skills/spec-diagram`, `skills/spec-lint`,
  `tools/spec_build.py`, `tools/spec_lint.py`, `tools/azdiagram/`,
  `tools/tests/`). One skill, not three: the three GridMarket skills share one
  trigger surface ("write, draw or check a specification") and C10 forbids
  duplicate skills; figure and lint procedures move to references.
- Files:

| Path (under `skills/spec-authoring/`) | Content |
|---|---|
| `SKILL.md` | Trigger, non-triggers, procedure: copy template → fill `spec.yaml` → author sections → draw figures → build → lint → staleness; pass rule. Within skill_size_max. |
| `agents/openai.yaml` | Default agent metadata (create-lean-skill step 5). |
| `references/section-rules.md` | Section grammar (front matter `requirements:` ≤ 5, BLUF, Frame, T1–T8 tables, F1–F8 figures), COE-ASA-001 floor subsections. |
| `references/figures.md` | azdiagram classes F1–F8, YAML input shapes, render and lint. |
| `references/vendoring.md` | When a repository's CI cannot reach the shared skill (private skill, public repository): copy `scripts/` and `template/` to `<repo>/tools/spec/` with `scripts/vendor.sh`, which writes `VENDORED.md` (source commit, skill tree id, MIT notice) (IE-P1-F03). |
| `template/` | GridMarket `spec/template/` with project names removed (`spec.yaml` placeholders, no GridMarket identifiers). |
| `scripts/spec_build.py`, `scripts/spec_lint.py`, `scripts/diagram.py`, `scripts/azdiagram/` | GridMarket tools with PEP 723 inline metadata (`requires-python >= 3.11`, `dependencies = ["pyyaml"]`), run as `uv run --script`; no `--project` flag, no repository-specific paths. |
| `scripts/vendor.sh` | Vendor step above. |
| `tests/` | GridMarket tool tests adapted to the skill layout plus a repo-agnostic test that builds the template in a temporary non-git directory. |
| `LICENSE-gridmarket` | The MIT copyright and permission notice of the source (AC-AFC-D5-01). |

- Repo-agnostic means: no GridMarket names, no `backend/` project, no
  absolute paths, no assumption of a git repository except the staleness
  check, which uses `git diff --exit-code` only when the target is in a git
  work tree and otherwise compares two builds byte-for-byte.
- External tool: Graphviz `dot` on PATH; missing `dot` is exit 3, a typed gap
  (never a pass), matching CONTRACT-AFC-GATE.
- Trigger boundary with the strongest peer, `use-requirements-system`
  (SDoc-first architecture specifications in the Requirements System): the
  new skill owns Markdown section-sourced specifications built to one file;
  its description names SDoc/StrictDoc/Requirements System documents as a
  non-trigger, and (if OD-AFC-07 is approved) `use-requirements-system`'s
  description gains the reciprocal non-trigger. `requirements-engineering`
  remains the owner of requirement-statement quality; the new skill cites it
  by reference and does not restate its checklist.
- Validation per create-lean-skill: `wc -l`/`wc -w` within skill_size_max;
  one matching request ("write the architecture spec for this repo as
  Markdown sections and build it") routes to `spec-authoring`; one
  non-matching request ("publish the SDoc revision to the Requirements System
  workbench") routes to `use-requirements-system`; skill-creator validation
  scripts run; tests pass.
- Linking (S06L, light): after S06 merges, symlink the skill into
  `$HOME/.claude/skills`, `$HOME/.codex/skills`, `$HOME/.agents/skills` and
  `$HOME/.cursor/skills` like the existing shared skills; Muse and AGY are
  handled by the D4-E installer (S11), which links every shared skill the
  harness lacks or records a typed gap.
- Lenses: Lean skill, Repo-agnostic, Spec discipline.


### DES-AFC-GATE — This repository's gate

- `tools/ci/gate.sh` implements CONTRACT-AFC-GATE. Phase 1 has three areas:
  - `spec` (paths `spec/**`, `tools/spec/**`):
    - For each `spec/<name>/`: `uv run --script tools/spec/spec_lint.py
      spec/<name>/`, then `uv run --script tools/spec/diagram.py lint
      spec/<name>/`, then a rebuild and `git diff --exit-code` on its built
      file.
    - While no `spec/<name>/` exists, the area copies `tools/spec/template/`
      into a temporary directory, builds it, lints it, and removes the
      directory (AC-AFC-CI-04).
    - If `tools/spec/` is missing, the result is `GAP tools/spec missing`
      (exit 3). If Graphviz `dot` is missing, the result is a GAP (exit 3).
  - `docs` (paths `docs/**`, `*.md`): `python3 tools/ci/check_docs.py`.
    - It fails when a `docs/vnv/<area>/AGENTS.md` lacks any of the headings
      `Scope`, `Tools`, `Review Focus`, `Findings target`.
    - It fails when a tracked Markdown file has a relative link to a path
      that does not exist. External URLs are not fetched. Anchors are not
      checked.
    - It prints `file:line:DOC-<rule>`.
  - `hygiene` (always runs):
    - `python3 tools/ci/check_paths.py` over all tracked files
      (AC-AFC-CI-03, AC-AFC-PATH-01). Rule identities: `PATH-HOME-POSIX`
      (`/home/<user>/`), `PATH-HOME-MAC` (`/Users/<user>/`), `PATH-HOME-WIN`
      (`C:\Users\<user>\`), `CRED-AWS-KEY-ID`, `CRED-AWS-SECRET`,
      `CRED-YAHOO-SECRET`, `CRED-OAUTH-TOKEN`, `CRED-DEVICE-TOKEN`.
    - Each finding prints `file:line:rule-id` and never the matched text.
      Placeholder user segments (`user`, `example-user`, `someone`) are
      allowed. `check_paths.py --files <path>...` applies the same rules to
      only the named files.
    - `python3 tools/ci/check_workflows.py .github/workflows/`, the D4-B
      checker vendored from the merged D4-B commit.
    - The gate's own tests in `tools/ci/tests/`.
    - `tools/ci/VENDORED.md` records the source repository and the D4-A and
      D4-B merge commits.
- Phase 2 adds `android` and `backend` areas behind the same entrypoint
  without changing CONTRACT-AFC-GATE.
- `.githooks/pre-commit` runs `gate.sh --changed`. `.githooks/pre-push`
  runs `gate.sh --changed` against the merge base with `origin/main`. Both
  are installed by the D4-A installer (`core.hooksPath .githooks`).
- `.github/workflows/ci.yml` (AC-AFC-CI-02):
  - triggers: `on: pull_request` and `push` to `main`;
  - concurrency: `ci-${{ github.workflow }}-${{ github.ref }}` with
    `cancel-in-progress: true`;
  - a `changes` job computes the areas with a path-filter action pinned by
    SHA;
  - one job per area, named `gate / <area>`; `hygiene` always runs;
  - every action is pinned by full SHA;
  - `permissions: contents: read`; no secrets are referenced;
  - runs on `ubuntu-latest` GitHub-hosted runners;
  - the `spec` job installs Graphviz by apt and uv by a SHA-pinned action.
- Lenses: Parallel-safe CI, Security controls, Contract-first.

### DES-AFC-D4 — Shared CI/CD capability (Alphazedehq)

Write set in `alphazede/Alphazedehq` (cross-repo; each sub-change is its own
PR, branch `ci-cd/<topic>`, worktree `worktrees/Alphazedehq-ci-cd-<topic>`):

| Sub-change | Files | Content |
|---|---|---|
| D4-A `setup-pre-commit` (S01) | `skills/setup-pre-commit/SKILL.md`, `skills/setup-pre-commit/agents/openai.yaml`, `skills/setup-pre-commit/references/gate-contract.md`, `skills/setup-pre-commit/templates/gate.sh`, `skills/setup-pre-commit/scripts/install-hooks.sh`, `skills/setup-pre-commit/tests/test-install-hooks.sh` | Replace the `[TODO]` template (DX-007) with the gate entrypoint procedure: inventory checks → write `tools/ci/gate.sh` from the template → install `.githooks` via `core.hooksPath` → wire Actions per `setup-a-repo` → verify with a deliberate failing change. |
| D4-B `setup-a-repo` (S02) | `skills/setup-a-repo/SKILL.md`, `skills/setup-a-repo/references/workflow-authoring.md`, `skills/setup-a-repo/templates/ci.yml`, `skills/setup-a-repo/scripts/check-workflows.py`, `skills/setup-a-repo/tests/test_check_workflows.py` | Workflow-authoring rules (AC-AFC-CI-02 list, free hosted runners on public repos, gh_private_minutes budget, C11, C14) and a checker that exits 1 on violation. `SKILL.md` gains one "Workflows" step, its description drops "one named AlphaZede repository" for any personal or organization repository (SD-019), and it is trimmed below skill_size_max (it is exactly 60 lines today). |
| D4-C `ship-pull-request` (S03) | `skills/ship-pull-request/SKILL.md`, `skills/ship-pull-request/references/GATES.md`, `skills/ship-pull-request/references/EDIT-PR.md` | Gate step: when `docs/vnv/AGENTS.md` or `Vnv/AGENTS.md` exists run `vnv-review`, else record `REFUSED_NO_VNV` (C12, never a pass); the diff scope is passed explicitly (`--scope=commits=<base>..HEAD`) because `vnv-review` defaults to `master...HEAD`. GATES.md: a shared-gate row (`tools/ci/gate.sh`) and an amazon-fantasy-companion row. The Edit section moves to `references/EDIT-PR.md` so `SKILL.md` drops from 82 lines to below skill_size_max (C10). |
| D4-E harness hooks (S11T, S11) | `hooks/ci-gate-hook.sh`, `hooks/test-ci-gate-hook.sh`, `hooks/install-ci-gate-hook.py`, `hooks/README.md` | CONTRACT-AFC-HOOK; the installer edits each harness configuration idempotently after a timestamped backup, and links the shared skills and `vnv-review` into Muse's (and, if verified, AGY's) skill directory. Runs only after D4-A..C merge (C13). |
| D4-F thin entry-point skill (S41, only if OD-AFC-01 = B) | `skills/ci-cd/SKILL.md` | A router under 25 lines naming the three skills; no procedure of its own. |

- Every changed `SKILL.md` is checked with `wc -l` and `wc -w` against
  skill_size_max and exercised on one matching and one non-matching request
  per create-lean-skill (AC-AFC-D4-05). No text names specific repositories
  as pilots or exclusions (AC-AFC-D4-06); the amazon-fantasy-companion GATES
  row is gate data, not scoping.
- Recommendation for OD-AFC-01: extensions only (see technical plan).
- Lenses: Lean skill, Repo-agnostic, Parallel-safe CI, Owner boundary.


### DES-AFC-VNV — Vnv guidance tree (Phase 1 areas)

- `docs/vnv/AGENTS.md` indexes the areas.
- `docs/vnv/<area>/AGENTS.md` exists for `ci-cd`, `spec` and
  `developer-feedback`. This is the layout `vnv-review` reads: every
  immediate `<guidance-root>/*/AGENTS.md`. Each file names:
  - Scope: the paths.
  - Tools: the CONTRACT-AFC-GATE commands.
  - Review Focus: the lenses that apply.
  - Findings target: GitHub issues in this repository with the `vnv` label,
    filed through the issue-label policy tool.
- The shape follows the shared `vnv-review` skill's profile schema.
- Phase 2 adds the `tv-app`, `backend` and `device-integration` areas when
  those paths exist.
- Lenses: Spec discipline, Owner boundary.

### DES-AFC-DX — Scribe developer-feedback log

- `docs/developer-feedback/observations.md` is the running log. It is
  public per SD-011.
  - One row per observation, with the fields of the issue #1 Scribe
    contract.
  - Seeded with DX-001..DX-007, the planning observations and the Phase 1
    observations (S08).
- The per-tool summary and the sanitized friction log are Phase 2 work,
  done at submission.
- Every packet template in `implementation.json` carries the
  `developer_feedback` section (AC-AFC-DX-01).
- Lenses: Developer feedback, Owner boundary.

### DES-AFC-LANES — Lanes, worktrees, leases and landing (Phase 1)

- Lanes and frozen profiles (DEC-AFC-PROFILE-001):
  - `spec-and-docs` = tech-writing: S01, S02, S03, S06, S07, S41
    (conditional; skill authoring with trigger checks is judgement work).
  - `ci` = primary, the `backend` lane profile: S09T, S09, S11T, S11.
  - Light slices (S06L, S42) use the Light Implementer route of their
    lane's profile.
  - The Scribe slice (S08) uses the planning profile `primary` Scribe
    route.
- Development strategy:
  - The `ci` lane is `tdd`. Each feature is split into a Test Implementer
    slice (red, `<id>T`) and a Product Implementer slice (green).
  - The red slice ends with the CMD-RED receipt (failing output plus the
    sha256 of each test file), taken in the shared TDD-pair worktree. It
    leaves the tests uncommitted.
  - The green slice continues in that worktree. When green, it commits the
    tests first, with the Test Implementer's author identity, then the
    product code with its own. `--no-verify` is never used.
  - `spec-and-docs` is `single_implementer`.
- Worktrees: one per running slice or TDD pair, never in hidden
  directories.
  - This repository: `worktrees/amazon-fantasy-companion-<lane>-<slice>` on
    branch `afc/<lane>-p1-<slice>`.
  - Alphazedehq D4: `worktrees/Alphazedehq-ci-cd-<topic>` on branch
    `ci-cd/<topic>`.
  - Alphazedehq D5: `worktrees/Alphazedehq-spec-authoring` on branch
    `spec-authoring/d5`.
- Leases, each held by the Orchestrator and granted to one slice at a
  time:
  - `alphazedehq-skills/<skill>`: no two slices edit the same skill
    directory.
  - `harness-configs`: S06L, S11.
  - `alphazedehq-main-checkout`: a reader-writer lease (IE-P1-F02).
    - Slices that read skills from the checkout (S06L, S42) and the
      IE-P1-10 live install hold a shared read lease.
    - The Orchestrator's fast-forward (CMD-AZHQ-SYNC) takes it
      exclusively. It runs only when no read lease is held and no session
      of this Lifecycle is opening or landing a pull request.
    - Each sync records the HEAD before and after it and the sessions
      running at that moment. The HEAD is recorded in each later packet.
- impl_agent_cap: at most 5 concurrent Implementer, Test Implementer, Light
  Implementer and repair sessions per orchestrating session. Reviewer,
  Scribe, Test Engineer and Integration Engineer sessions do not count.
- Landing:
  - Alphazedehq: one pull request per sub-change (D4-A, D4-B, D4-C, D5,
    D4-E, and D4-F if chosen), under that repository's own gates.
  - This repository: one pull request each for S07, S06L (link readback
    evidence), S42, S09 (tests and gate) and S08 (IE-P1-F07).
  - Every pull request is reviewed once at its integration step (the
    Phase 1 review boundary unit), on the lane profile's reviewer route,
    with OCR delegate mode and `Reverify: not applicable` (AC-AFC-REV-01).
    It gets at most one repair and a green gate, then merges by merge
    commit (IE-P1-F01; owner item OA-AFC-A3).
  - This repository is private until the owner flips visibility. A private
    GitHub Free repository has no rulesets or branch protection, so the
    Orchestrator enforces PR-only `main` and green `gate / <area>` checks:
    CMD-PR-CHECKS runs before every merge, and nothing is pushed directly
    to `main`. Its Actions runs count against gh_private_minutes
    (RISK-AFC-08; IE-P1-F10).
- Lenses: Parallel-safe CI, Owner boundary.

### DES-AFC-PHASE2 — Spec track and Phase 2 sequence

- The Phase 1 spec track opens its own plan directory
  `docs/plans/<open-date>-amazon-fantasy-companion-phase-2/` (path kept from
  the authority record; it later also holds the Phase 2 implementation
  plan), with `journey_type: specification` and a draft `.sdoc` register
  (OD-AFC-12). The spec-track steps are ST-1..ST-5 and the Phase 2 steps
  are P2-6..P2-7 of the technical plan (ST-n replaces the earlier P2-n for
  n = 1..5; the design ID DES-AFC-PHASE2 is kept).
- Interfaces from the D5/D4 waves to the spec track and Phase 2:
  - **CONTRACT-AFC-SPECKIT**, through the vendored `tools/spec/`: D1 is
    built (ST-4) and linted with these commands.
  - **CONTRACT-AFC-GATE**: the D1 sources are checked by the existing
    `spec` area; Phase 2 adds `android` and `backend` areas.
  - **The Vnv tree**: Phase 2 adds areas.
  - **The spec-track entry receipt** (AC-AFC-PLAN-03; file
    `evidence/phase2-entry-receipt.json`).
- Dependency rule: ST-2 and ST-3 depend only on Phase 1 package approval.
  ST-4 depends on S06, S42 and S09 having landed, and on ST-2 PASS and the
  ST-3 mapping. Phase 2 (P2-6) depends on the owner's spec approval at
  ST-5.
- Visual evidence for Phase 2 UI work goes under the top-level
  `evidence/visual/<slice>/`, committed, with no account or customer data
  (DEC-AFC-SD-024).
- Lenses: Spec discipline, Owner boundary.

## Contracts

### CONTRACT-AFC-GATE — Gate entrypoint (shared contract, D4-A)

`tools/ci/gate.sh [--changed[=<base>]] [--list] [<area>...]`. No area means
all areas. `--changed` runs only areas whose paths changed against `<base>`
(default: merge base with `origin/main`) plus `hygiene`. Exit 0 pass, 1 check
failure, 2 usage error, 3 required tool missing (a typed gap, never a pass).
Each area prints `gate: <area>: PASS|FAIL|GAP <detail>`. The same invocation
runs in git hooks, in Actions (`gate.sh <area>` per job) and from harness
hooks.

### CONTRACT-AFC-HOOK — Harness hook (D4-E)

`hooks/ci-gate-hook.sh` reads the harness's pre-tool event on stdin, acts
only when the shell command is `git commit` or `git push` in a repository
that has `tools/ci/gate.sh`, and then runs `tools/ci/gate.sh --changed` when
the repository's git hooks are not installed or the command carries
`--no-verify`; a non-zero gate blocks the tool call with the gate output. It
is advisory (prints a notice) in repositories without a gate entrypoint.
Harness adapters: Claude Code `PreToolUse` (Bash), Codex `hooks.json`,
Cursor `beforeShellExecution`, Muse and AGY where a pre-tool hook surface is
verified; otherwise a typed gap (AC-AFC-D4-04).

### CONTRACT-AFC-SPECKIT — Spec-authoring commands (shared contract, D5)

From the skill directory or a vendored `tools/spec/` copy (`<kit>`):

- `uv run --script <kit>/spec_build.py <spec dir> <output.md>` — exit 0 on
  build; front matter, numbering and Appendix A traceability generated.
- `uv run --script <kit>/spec_lint.py <spec dir>` — exit 0 with no findings,
  1 with findings (file and defect per line).
- `uv run --script <kit>/diagram.py render <figure.yaml>` and
  `uv run --script <kit>/diagram.py lint <spec dir>` (`diagram.py` is a PEP 723
  wrapper that puts its own directory on `sys.path` and runs `azdiagram`) — SVG plus draw.io from one layout; lint exit 1 on
  overlap or size overflow; exit 3 when Graphviz `dot` is missing.
- `<skill>/scripts/vendor.sh <repo root>` — copies the contents of
  `scripts/` and the `template/` directory to `<repo root>/tools/spec/`
  (template at `tools/spec/template/`) and writes `VENDORED.md`:
  - the source repository;
  - the source commit, `git log -1 --format=%H -- <skill dir>` in the
    source checkout;
  - the tree id of the skill directory at that commit;
  - the MIT notice.

  It refuses to run when the skill directory has uncommitted changes. It
  refuses to overwrite a vendored copy whose files differ from its
  recorded commit (IE-P1-F03).


## Diagrams

Feature views are canonical Mermaid sources with SVG renderings. They are
listed in `views/views.json` and embedded in the DoD Manifest. Phase 1 uses
MODEL-AFC-V4 `views/v4-delivery-tooling.mmd`: one gate entrypoint called
from git hooks, Actions and harness hooks; the vnv-review branch; the D5
skill → vendored `tools/spec/` → `spec` gate area. It also uses any further
Phase 1 views the Systems Modeler adds in `views/views.json`. The
technical plan carries the Phase 1 wave graph and the spec track and Phase 2 sequence as
Mermaid.
