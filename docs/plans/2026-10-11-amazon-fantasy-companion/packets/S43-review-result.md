# S43 Review Result (Reviewer, independent)

- Candidate: https://github.com/alphazede/Alphazedehq/pull/316, branch afc/s43-revision-record
- Head: 68172c3e987d1825efff3b9fead02ff05d3a9def, base: 23f0bb28a9ef9e0ec6ca1d4ec130489e8c569beb
- Packet: packets/S43-g1.md; author receipt: evidence/S43/receipt.json
- Verdict: REPAIR_REQUIRED (one fixable P3 finding; all deterministic checks reproduce green)

## Findings

| ID | Sev | Location | Defect | Exact fix |
|----|-----|----------|--------|-----------|
| S43-R1 | P3 | AGENTS.md:364 | Revision-record pointer uses a relative link `../../AGENTS.md#cross-repo-rules` that resolves only in worktree checkouts. In the direct checkout it resolves to `$HOME/AGENTS.md` (missing; reproducer below), and on GitHub it escapes the repository (404). Packet objective 5 required mirroring the bug-triage pointer style (AGENTS.md:358), which is plain text precisely because the workspace file is outside the repo. | Replace line 364 with the plain-text pointer: `Canonical: workspace \`AGENTS.md\` cross-repo rule #21.` |

Reproducer for S43-R1 (no code change needed to observe):

```sh
python3 -c "from pathlib import Path; print((Path('$HOME/alphazede/Alphazedehq/AGENTS.md').parent / '../../AGENTS.md').resolve())"
# $HOME/AGENTS.md
ls $HOME/AGENTS.md  # No such file or directory
```

Line 364 is the only parent-escaping relative link in AGENTS.md; all sibling
cross-repo pointers (rules #18, #20) use plain text.

## Re-run exit codes (all reproduce the receipt)

- Four skill suites with independently classified triggers (each skill
  request_1 MATCH, request_2 NO_MATCH from its SKILL.md): 119 passed,
  4 subtests passed, exit 0.
- Template build twice + `cmp`: byte-identical, exit 0; template lint exit 0.
- Negative fixtures: issue/section/document/revision each exit 1 with the
  specific messages (`unlinked issue/PR reference: #123`,
  `unlinked section reference: section 4.2`,
  `unlinked document/file reference: design.md`,
  `revision 0.2: changes/links.pr/links.diff ...`).
- `bash tools/ci/local-gates.sh`: exit 0 (passed=2, failed=0, N/A=15).
- `git diff --check` on the candidate range: clean. No `/home/` paths in any
  of the 20 changed files. Only test file touched is the new
  `test_reference_records.py`; no existing test weakened (fixture
  `spec.yaml` gained the rev-0.2 positive case; full suite green).
- SKILL.md sizes: spec-authoring 48/359, ship-pull-request 55/429,
  setup-a-repo 58/441, release-process 59/399 (lines/words; all <60/<650,
  matching the receipt).

## AFC-spec lint probe (origin/afc/st4-spec, spec/amazon-fantasy-companion)

New lint exit 1 with 19 findings: 3 revision findings on spec.yaml
(rev 0.2 lacks changes/PR/diff — expected, pre-S43 spec), plus 16 reference
findings: 6x `issue #1`, 7x section refs (`Section 7`, `section 7`,
`Section 7.1`, `Section 7.1.11`, `section 2.1`, `Sections 4.1.5`),
3x file refs (`replay.py`, `backend/template.yaml`, `template.yaml`).

- False positives: 0. Every flagged section number exists as a heading
  (7, 7.1, 7.1.11, 2.1, 4.1.5 verified); `issue #1` is linkable to the
  GitHub issue URL the spec itself already uses
  (`[Product intent](https://github.com/1wgrumph/amazon-fantasy-companion/issues/1)`);
  file mentions are genuine file references.
- False negatives: 0 on in-scope forms. All 7 distinct URLs in section
  sources sit inside Markdown links and none were flagged; linked
  `[label](target)` / reference-style forms pass; `AFC-PR-015`-style tokens,
  version numbers, dates, and bare "section" prose correctly pass.
  Bare number refs (`in 4.1.12`, 5 occurrences) are not flagged by design —
  outside the contracted `section N` / `see N` forms.
- Assumption correction: headings ARE scanned (synthetic probe: refs in an
  `##` heading are flagged). The "not headings" assumption is false, but the
  behavior matches the packet contract ("fails an unlinked reference outside
  code spans/fences"), so this is a corrected assumption, not a defect.

Other assumptions all hold: first revision exempt (template rev 0.1 with
empty changes/links builds and lints clean); revision rows render changed
sections as anchor links plus PR/Diff links; ship-pull-request creates
CHANGELOG.md when missing (seed reference) and preserves unrelated entries;
setup-a-repo seeds CHANGELOG.md (step 8 + template); release-process moves
[Unreleased] under the linked version heading; reported exit codes reproduce.

## OCR section (delegate mode, required)

- `ocr delegate preview --from 23f0bb... --to 68172c3...`: ok — 3 reviewable
  of 20 files (spec_build.py, spec_lint.py, template/spec.yaml); 17 excluded
  (unsupported_ext/default_path). No tool failure.
- `ocr delegate rule` on each of the 3 listed files: ok — Python rule group
  (precision-over-recall, typos, dead code, shared state, boundary handling)
  for the two scripts; YAML key-spelling group for the template.
- Per-file application: spec_lint.py — no dead code, no mutable defaults,
  no unguarded empty-indexing; regexes bounded to line scans; fence parser
  handles unclosed/tilde/info-string cases. spec_build.py — `revision_findings`
  gate precedes render; unknown changed sections raise with rev context;
  `section_anchors` overwrite on duplicate headings is benign (same slug
  family). template/spec.yaml — keys (revisions/rev/date/author/summary/
  changes/links) correctly spelled. OCR finds no defects and gives no
  verdict; I additionally read every excluded prose/test/fixture file
  directly (Markdown carries this change's contract).

## Reverify

Not applicable — no compiled binary (Python scripts + Markdown + YAML only).

## Route used

Reviewer role, direct packet; no subagents; `ocr` CLI for coverage-assist;
pytest, spec_build.py, spec_lint.py, local-gates.sh, git/gh-free probes.

## developer_feedback

no new observations. Tools: read_skill(reviewer), git diff/show, ocr
delegate preview/rule, python3 -m pytest, spec_build.py, spec_lint.py,
tools/ci/local-gates.sh, grep/python probes.
