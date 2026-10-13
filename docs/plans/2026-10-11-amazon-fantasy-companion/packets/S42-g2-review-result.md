# S42-g2 review result (lease S42-g2, generation 2)

verdict: PASS
candidate: https://github.com/1wgrumph/amazon-fantasy-companion/pull/11
branch: afc/s42-revendor-prose
base: 5e59270b8320d6085039f26b64f14897736845f6
head: 579b9519d5c2e5a92b208112768cb4654d114798
authority: AUTH-AFC-2026-10-11-002
reviewer: independent (did not author this change)

## Candidate identity (verified, not assumed)

- Local HEAD = 579b9519d5c2e5a92b208112768cb4654d114798; worktree clean, on
  afc/s42-revendor-prose tracking origin/afc/s42-revendor-prose.
- PR #11 readback: OPEN, draft, base main, head afc/s42-revendor-prose @
  579b9519, 40 files, +55/-389 — matches local base..head diff exactly.
- Commit author `Muse Code <1wgrumph+muse-code@gmail.com>`, committer
  `1wgrumph <1wgrumph@gmail.com>`, no Co-Authored-By.
- Write set exact: all 40 changed paths under tools/spec/ (VENDORED.md,
  spec_lint.py, 38 template files). THIRD_PARTY_NOTICES.md untouched.
- Alphazedehq checkout at c24e4a36131c03dcda283b5431990cf14e603e68 =
  origin/main; c24e4a3 is ancestor of origin/main.

## Re-run exit codes (reviewer ran these)

- CMD-SPEC-VENDOR (vendored_source_commit=c24e4a3 from VENDORED.md,
  alphazedehq_checkout=$HOME/alphazede/Alphazedehq, azhq_d5_sha=c24e4a3):
  `exit=0` — PASS, reproduces the receipt.
- CMD-PATH-SCAN-PLAN over `tools/spec THIRD_PARTY_NOTICES.md`: no output —
  PASS.

## Assumption checks

- tools/spec equals c24e4a3 skill scripts+template exactly: YES (both
  diff -r legs clean inside CMD-SPEC-VENDOR, exit 0).
- VENDORED.md pins c24e4a3 and its tree id: YES (Source commit c24e4a3…,
  Skill tree d97986b6…; rev-parse of c24e4a3:skills/spec-authoring =
  d97986b6351ada4e20807d6bebed213033fb3c56).
- THIRD_PARTY_NOTICES.md unchanged is correct: YES (LICENSE-gridmarket
  exists at c24e4a3 and `git diff ac47f0e c24e4a3` on it is 0 bytes; MIT
  notice present in both files per CMD greps).
- Reported exit codes reproduce: YES (both commands above).
- Upstream SKILL.md / references / tests changed ac47f0e..c24e4a3 are
  correctly NOT vendored (only scripts+template per IE-P1-F03); no
  SKILL.md, references/, or tests/ under tools/spec/.
- spec_lint.py parses (ast), `_next_content` is defined (line 77) at both
  call sites (lines 107, 124); diff matches SD-034 prose intent (BLUF/Frame
  requirement replaced by writer-label rejection + opening-paragraph check).
  Sample template diff (01-introduction.md) shows the same BLUF/Frame
  removal. No introduced defect: vendored bytes are upstream's and equality
  is the requirement, so there is no candidate-side fix to propose for
  upstream content.

## Findings

No findings. No file:line + reproducer pair exists, so per the reviewer
rule nothing counts toward REPAIR_REQUIRED.

| ID | Severity | file:line | Defect | Exact fix |
|----|----------|-----------|--------|-----------|
| (none) | — | — | — | — |

## OCR section (CMD-OCR-DELEGATE)

- `ocr delegate preview --from 5e59270… --to 579b9519…`: exit 0.
  1 reviewable / 40 total; merge_base = base; +55/-389.
- `ocr delegate rule` run for every previewed file: 40/40 exit 0, no tool
  failure, no typed gap.

Per-file OCR outcome (rule group returned, exit):

| File | Preview status | Rule group | Exit |
|------|----------------|------------|------|
| tools/spec/spec_lint.py | reviewable | system / **/*.{py,pyi,ipynb} | 0 |
| tools/spec/VENDORED.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01-introduction.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.1-background.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.1.1-identification.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.1.2-system-context.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.2-baseline.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.2.1-baselines.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.3-feature-set.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.4-scope.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.4.1-purpose-and-scope.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.4.2-stakeholders.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.5-assumptions.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.6-terms.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/01.6.1-requirements.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/02-open-items.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/02.1-risks.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/03-use-model.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/03.1-operational-concept.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04-feature-architecture.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.1-feature-decomposition.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.1.1-feature.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.1.99-allocation.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.2-feature-interfaces.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.2.1-internal-interfaces.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.2.2-external-interfaces.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.2.3-interfaces-and-contracts.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.3-data-model.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.4-performance.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.5-fault-behavior.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.6-architecture-views.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.7-model-correspondence.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/04.8-rationale.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/05-security.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/05.1-security-considerations.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/05.2-security-features.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/05.3-security-interfaces.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/06-programming-model.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/07-verification.md | excluded: unsupported_ext | system / default | 0 |
| tools/spec/template/07.1-verification-approach.md | excluded: unsupported_ext | system / default | 0 |

OCR raised no defects (advisory only, per skill). The reviewer read the
one reviewable file's full diff plus VENDORED.md and a sample template
directly; the remaining 38 template diffs are covered byte-exact by the
CMD-SPEC-VENDOR equality leg (exit 0) against the pinned upstream tree.

## Reverify

Reverify: not applicable — no compiled binary.

## Route used

Reviewer session on Muse Code (BEARING_ROLE=reviewer); read-only review,
no implementation route consumed.

## developer_feedback

No new observations. Tools used: git, gh (read-only pr view), ocr
(delegate preview + rule), python3 (ast parse only).
