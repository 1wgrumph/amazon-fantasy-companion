---
type: review-receipt
title: AFC B3 independent review result
okf_status: active
tags: [internal, review, afc, bug-triager]
---

# B3 independent review

Verdict: **REPAIR_REQUIRED**

- Lifecycle: AFC-2026-10-11; defect B3; boundary: exact B3 candidate, one independent review.
- Role: Reviewer (`BEARING_ROLE=reviewer`), bug-triager route Codex CLI / GPT-6 Astra / high, DEC-AFC-SD-037.
- Candidate: [PR 320](https://github.com/alphazede/Alphazedehq/pull/320), branch `afc/b3-appendix-links`.
- Base: `c323c56f556cf708b7104838d2f2977af015fe67`.
- Head: `2b46eae6e855629ef161075ba32bf76d9c7cc0c1`.
- Changed paths: `CHANGELOG.md`, `skills/spec-authoring/scripts/spec_build.py`, `skills/spec-authoring/tests/test_appendix_links.py`.
- Candidate was clean before and after verification, and HEAD remained pinned. Reviewer did not author or modify it.
- Consumed `packets/B3T-g1.md`, `packets/B3-g1.md`, `evidence/B3/B3T-red-receipt.json`, and `evidence/B3/B3-green-receipt.json`. These are author/test-implementer receipts, not independent assurance. This receipt supplies the independent checks requested by the review packet.
- Contract: ST5-F1 / ST4-G4-F1 and B3/B3T objective: every generated Appendix A section reference links to the corresponding section anchor. The packet explicitly calls out punctuation and duplicate headings. No separate B3 SEIT case ID was supplied.
- This is a builder code review. The temporary AFC build is a validation fixture, not formal Requirements System document review, acceptance, or publication; no bound-host revision/digest is claimed.

## Findings

| ID | Severity | File:line | Defect | Exact fix |
|---|---|---|---|---|
| B3-R1 | P2 | `skills/spec-authoring/scripts/spec_build.py:140` (data originates at lines 83 and 91) | Appendix lookup by heading text loses the section occurrence. Two lint-valid sources titled `Repeated`, binding REQ-1 and REQ-2 respectively, both render `[Repeated](#repeated-1)`. REQ-1 should target `#repeated`; it currently navigates to the other requirement's section. | Store each traced section's label and allocated anchor together when reading that source, and render its captured anchor instead of looking the label up in the final `section_anchors` dictionary. Add a regression that checks the first and second occurrences independently, including one requirement bound to both occurrences. |
| B3-R2 | P2 | `skills/spec-authoring/scripts/spec_build.py:140` (anchor allocation at lines 40–45 and 63–71) | The new Appendix links inherit an incomplete heading-anchor registry. A section matching the document title links to the title instead of the section. Also, headings `Foo`, `Foo`, `Foo-1` make REQ-3 link to `#foo-1` (the second Foo), rather than its actual `#foo-1-1` heading. | Seed allocation with the document title before generated front matter, and reserve every emitted anchor, including suffixed anchors. Advance suffixes until the anchor is unused. Capture those per-occurrence anchors for Appendix rendering. Add literal expected-target regressions for title collision and generated-suffix collision; preserve existing punctuation behavior. |

Both are reachable product defects on valid inputs: each reproducer's complete source directory passes the CLI linter (exit 0), and its builder completes (exit 0). Each expected-row assertion fails (exit 1). Neither requires malformed input or a harness failure. The antecedent anchor helpers existed on base; the introduced behavior is the new Appendix links resolving to wrong section occurrences through those helpers. Preexisting ToC/revision behavior is not counted as a separate finding.

GitHub's documented rule makes anchors unique across the document, with suffixes for collisions: [GitHub section links](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links). Expected values above follow that rule and were not obtained from the production `slug()` function.

### Reproduce the findings

Run from the pinned candidate root. This uses only temporary fixtures and installed Python dependencies. `CASE` selects one independently failing case. All three cases were executed; each source lint returned 0 and the final expected-row assertion returned 1.

```bash
TMPDIR=/var/tmp/az PYTHONDONTWRITEBYTECODE=1 CASE=duplicates python3 - <<'PYCODE'
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path('skills/spec-authoring/scripts').resolve()))
from spec_build import build

cases = {
    'duplicates': (
        ['Repeated', 'Repeated'],
        '| REQ-1 | [Repeated](#repeated) |'),
    'title_collision': (
        ['Example Fixture Specification'],
        '| REQ-1 | [Example Fixture Specification](#example-fixture-specification-1) |'),
    'slug_collision': (
        ['Foo', 'Foo', 'Foo-1'],
        '| REQ-3 | [Foo-1](#foo-1-1) |'),
}
headings, expected = cases[os.environ['CASE']]
with tempfile.TemporaryDirectory() as scratch:
    root = Path(scratch)
    src = root / 'src'
    src.mkdir()
    (src / 'spec.yaml').write_text(
        'title: Example Fixture Specification\n'
        'document_id: REVIEW\nrevisions:\n'
        '  - rev: "0.1"\n    date: "2026-10-12"\n'
        '    author: Reviewer\n    summary: Fixture\n'
        '    changes: []\n    links: {}\n')
    for n, heading in enumerate(headings, 1):
        (src / f'{n:02d}-section.md').write_text(
            f'---\nrequirements: [REQ-{n}]\n---\n\n## {heading}\n\n'
            'This paragraph defines the contract.\n')
    subprocess.run([sys.executable, 'skills/spec-authoring/scripts/spec_lint.py',
                    str(src)], check=True)
    output = root / 'built.md'
    build(src, output)
    text = output.read_text()
    print(text.split('## Appendix A — Requirement Traceability Matrix')[1])
    assert expected in text, f'Missing expected row: {expected}'
PYCODE
```

Repair targets: `skills/spec-authoring/scripts/spec_build.py` and regression coverage in `skills/spec-authoring/tests/test_appendix_links.py`. Tests were frozen for B3-g1; the parent should issue the repair/test packet covering these exact targets. No repair was performed in this read-only review. No new general review round is requested: the configured repair round should fix both findings and rerun deterministic verification.

## Independent red-then-green receipt

All Python/test/build runs used `TMPDIR=/var/tmp/az` and `PYTHONDONTWRITEBYTECODE=1`; pytest used `-p no:cacheprovider` to preserve the clean candidate.

- Archived the exact base's `skills/spec-authoring` to a temporary directory and overlaid only the candidate's unchanged B3 regression file. Compared archived builder bytes to `git show <base>:skills/spec-authoring/scripts/spec_build.py` successfully.
- Base focused command: `python3 -m pytest <base-copy>/skills/spec-authoring/tests/test_appendix_links.py -q -p no:cacheprovider` → **exit 1; 1 failed, 1 passed**, 0.10 s. Failure: `AC-EX-DATA-01: Appendix A sections are not links: 'Overview'`, `assert [] == ['Overview']`, line 85.
- Head command: `SPEC_AUTHORING_TRIGGER_RESULTS=<temporary-results.json> python3 -m pytest skills/spec-authoring/tests -q -p no:cacheprovider` → **exit 0; 78 passed**, 6.76 s. Nothing deselected.
- An initial full-suite run on the base archive returned **exit 1; 2 failed, 76 passed**: the expected B3 failure plus the vendoring test's `fatal: not a git repository`. The latter is caused by the archive lacking Git metadata, is not a product finding, and is not claimed as baseline regression evidence. The focused base rerun above removes that unrelated harness dependency; the complete head suite ran on the real clean worktree.
- `git diff --exit-code 9b0ca5e2d3d64b9898148f051057da0b3ad959e0 <head> -- skills/spec-authoring/tests` → **exit 0**. The test implementer's frozen tests were unchanged by the implementation. The base-to-head diff adds only the new test file; no existing test was weakened.
- Base builder SHA-256: `561a43f0253d8c000fa43a186de26f1a7938e881d1c65c422bdbc75b0c44489e`.
- Head builder SHA-256: `99f268c002cc3c9dc5aa71ed5463121ef4175bccb8b0cb9657303c452ee01f0e`.
- B3 regression SHA-256: `cbeebcc582968747dfe8a35c99b69e38ae4c022eb5c2c641514f4101013d3ca3`.

### Trigger classifications supplied by Reviewer

```json
{"request_1":"MATCH","request_2":"NO_MATCH"}
```

Derived from `SKILL.md`: request 1 explicitly asks for Markdown-section architecture authoring and a build, within this skill's scope. Request 2 asks to publish SDoc to the Requirements System workbench, which this skill explicitly excludes. The classification test received this JSON via `SPEC_AUTHORING_TRIGGER_RESULTS`; it passed.

## Required reruns

| Check | Exit | Observed result |
|---|---:|---|
| Candidate full spec-authoring suite | 0 | 78 passed; no skipped/deselected trigger test |
| Base B3 regression file | 1 expected | 1 failed / 1 passed; unlinked Overview row |
| `uv run --script skills/spec-authoring/scripts/spec_build.py skills/spec-authoring/template <first.md>` | 0 | Built template |
| Same template command to `<second.md>` | 0 | Rebuilt template |
| `cmp <first.md> <second.md>` | 0 | Byte-identical |
| `uv run --script skills/spec-authoring/scripts/spec_lint.py skills/spec-authoring/template` | 0 | No findings |
| Candidate builder on copied AFC source directory | 0 | Built temporary AFC specification |
| Independent AFC Appendix link/anchor check | 0 | 66/66 rows linked; 177/177 links point to existing matching heading labels; 72 heading anchors examined |
| `bash tools/ci/local-gates.sh` | 0 | passed=2, failed=0, skipped=0, not-applicable=15; 1 s |
| Duplicate / title-collision / suffix-collision fixture lint | 0 each | All valid source directories |
| Expected-row assertion for those three fixtures | 1 each | Wrong Appendix target, as detailed above |

The local gate ran `diff-check` and `secret-scan`; the other 15 gates were N/A under its unchanged path filters, not passing claims. `AZ_GATE_RECEIPTS` was redirected to the temporary review directory so this read-only review did not publish a durable merge-authorization receipt. The explicitly requested spec-authoring suite ran separately.

AFC source: `$HOME/alphazede/worktrees/amazon-fantasy-companion-st4/spec/amazon-fantasy-companion/`. Copied to the review temp directory without modifying the source. Per-file SHA-256 maps matched at copy time and source hashes were unchanged after build. The anchor check generated anchors from the output heading order independently of the builder and checked link coverage, absence of bare section text, existence, and matching label.

- Template build SHA-256: `cb75378cdaa2bb7f7c43e3f6400334eec3af147c489f866ad554183a729eef1b`.
- AFC build SHA-256: `73f534a3a2efdc4aa996df98a64c213e8a6a711303c0e1cb826c0c9b61f215cf`.

The ordinary punctuation fixture (`Settlement & Payout` → `#settlement--payout`) passes. The real AFC copy passes. These results do not satisfy the separately requested duplicate-heading assumption; B3-R1 and B3-R2 remain blocking.

## OCR delegate coverage

Backend: OpenCodeReview `open-code-review v1.12.13 (fabbdb2) linux/amd64`, built 2026-10-08. Required capability available and run; no OCR tool gap.

`ocr delegate preview --from c323c56f556cf708b7104838d2f2977af015fe67 --to 2b46eae6e855629ef161075ba32bf76d9c7cc0c1` → **exit 0**; merge-base matches base; 1 reviewable / 3 total; +108/-1.

| File | Preview classification | `ocr delegate rule <file>` | Reviewer application |
|---|---|---:|---|
| `skills/spec-authoring/scripts/spec_build.py` | Reviewable | 0; Python rule group | Inspected the full builder and connected lint/parser contract. Boundary and identity checks produced B3-R1/B3-R2. No additional evidenced security, concurrency, or performance defect in the change. |
| `skills/spec-authoring/tests/test_appendix_links.py` | Excluded: `default_path`; nevertheless inspected | 0; Python rule group | Test file unchanged after red commit; new tests pass/fail as described. Fixture lacks duplicate/title/suffix collisions. Its anchor oracle repeats the production base-count approach and collapses equal labels, so it cannot establish the requested occurrence-specific behavior. Prevention: literal per-occurrence expectations in the repair regressions. |
| `CHANGELOG.md` | Excluded: `unsupported_ext`; nevertheless inspected | 0; default rule group | Correct PR 320 link under Unreleased Fixed; description matches the intended change. No separate finding. |

OCR supplies file/rule coverage, not an independent verdict; the observations and verdict above are the Reviewer's.

Reverify: **not applicable — no compiled binary is changed or under review**.

## BRAN and developer_feedback

`bran_status: hit`. Verified trusted pinned BRAN runtime SHA-256 `776b782a3ab1d9d931f3c121a729a16ae2e8426fa53cb27224273bf59ddd883e` against the trusted checkout's pin. `bran check <candidate-root> bran-strict` returned exit 0, all profiles passed. The query covered all seven terms (spec-authoring, builder, Appendix, section, links, review, tests) and grounded the skill, builder, lint, section rules and tests. The candidate lacks its own binary, so the verified trusted checkout runtime was used as the skill prescribes. The only scanner warning was the existing `skills/use-requirements-system` symlink.

`bran_refs`: `skills/spec-authoring/SKILL.md`, `skills/spec-authoring/scripts/spec_build.py`, `skills/spec-authoring/scripts/spec_lint.py`, `skills/spec-authoring/references/section-rules.md`, `skills/spec-authoring/tests/test_appendix_links.py`. Coverage: exact B3 code, tests, author receipts and required checks; bounded raw reads remained necessary for the exact diff, command definitions and reproduction. Extra repository-wide discovery was avoided.

`developer_feedback`: Two evidenced observations, B3-R1 and B3-R2. The test oracle's missing occurrence/collision coverage explains why 78 green tests coexist with these defects. Tools used: pinned BRAN, Git, Python 3.14.4 / pytest, uv, cmp, local-gates, OCR delegate, and GitHub's primary section-link documentation. No candidate repair, commit, push, merge, issue mutation, release or host change was performed. The explicit review scratch directory was removed; pytest manages its own temporary fixtures. The only persisted review artifact is this receipt.

The current AFC build succeeds, but duplicate/colliding section headings remain a navigation/traceability risk. Stop after this review; return the findings to the parent for its bounded repair round.
