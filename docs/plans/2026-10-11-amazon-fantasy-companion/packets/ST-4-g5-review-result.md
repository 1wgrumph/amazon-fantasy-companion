# ST-4-g5 independent review result (ST5-F1/ST5-F2 link/revision amendment)

- Candidate: https://github.com/1wgrumph/amazon-fantasy-companion/pull/10, branch
  `afc/st4-spec`, head `2090e2dc3f804c983e0ddc25cc506f9f98922824` (confirmed via
  `gh pr view 10`; hosted CI run 38344446642 targets this exact SHA).
- Approved-content baseline: `771c28958f78e611048528aedbd9ed4490f308e1` (g3 PASS,
  historical; not re-reviewed).
- Amendment commits: product `531eea3` + evidence-only `2090e2d` on merge
  `15b3a55`. Range `771c289..2090e2d` = 290 files: 218 inherited already-reviewed
  main records + 72 amendment files.
- Contract: `packets/ST-4-g5.md` + generation-5 resume; author Codex (receipt in
  candidate `evidence/ST-4/g5/`). Reviewer (Muse Code) did not author the change.
  No candidate writes, commits, PR comments, or merges made.

## Verdict: PASS

No actionable defects in the amendment. All re-runs pass; approved prose is
unchanged apart from link formatting plus the expected revision/provenance
metadata; revision 0.3 lists exactly the 46 changed sections with PR/diff links;
CHANGELOG retains the PR14 entry and links pending PR10; vendor bytes are
identical to HQ pin `0467883` (ancestor of HQ main); no 049..051 resurrection.

## Findings

None. No P0-P3 findings; no advisory items withheld.

## Re-run exit codes (reviewer-executed)

Full table in candidate `evidence/ST-4/g5-review/commands.txt`. Summary:
lint 0; diagram lint 0; two builds 0 + byte-identical to each other and to the
committed file (sha256 `5ac2c3a1...b14a313e`, matches `g5/receipt.json`);
`check-links.py` 0 (749 relative links/anchors resolved, 184 source links added,
66/66 UIDs, 0/66 unlinked Appendix A rows); label grep clean; `check_paths.py` 0;
`bash tools/ci/gate.sh` 0 (39 tests OK); private-path and secret-shape scans
clean; vendor-check 0 with output byte-identical to committed `vendor-check.json`
and `vendor-hashes.json`; hosted checks 4/4 pass on exact head, PR MERGEABLE/CLEAN.

One reviewer-environment note (not a finding): the first vendor-check run failed
because the reviewer's own lint/build runs wrote untracked `tools/**/__pycache__/`
(author's `verify.sh` sets `PYTHONDONTWRITEBYTECODE=1`; the reviewer runs did
not). After removing those reviewer-owned files, vendor-check exits 0. The
committed tree was never dirty.

## Amendment verification (beyond command re-runs)

- Prose: `check-links.py` asserts link-stripped equality for all sources except
  the two provenance files; the reviewer read both diffs directly. `01.1.1`
  changes only `0.2`->`0.3` plus links; `01.2.1` changes only links plus the
  Build-tools provenance row (`c24e4a3`->`0467883` with re-vendor note). An
  independent link-stripped diff of the built file shows only the revision
  header/table, the 0.2->0.3 line, and the build-tools row.
- References: issue `#1` link target exists (open); all named-doc targets
  (register incl. the SD-035 anchor, models views/allocation, scope-decision
  batch, journey.json, VENDORED.md, THIRD_PARTY_NOTICES.md) exist; 72 built-file
  headings back the 749 resolved anchors. `spec_lint` (with the new link rules)
  exits 0, closing the S43 probe's 19 unlinked references.
- Revision 0.3: the 46 `changes` identities exactly equal the 46 changed source
  files' headings (no missing, no extra); `pr`/`diff` links point at PR10 and
  PR10/files; 0.2 backfill carries the same links.
- CHANGELOG: `[Unreleased]` keeps the B2 PR14 Fixed entry and adds the PR10 entry
  with PR/diff links; dated history matches the live merged list
  (2,3,4,5,6,7,8,9,12,13,14). Open PR11 is correctly absent.
- UIDs: independent check — 66 Appendix A rows equal the 66 register UIDs equal
  all UIDs in the built text; withdrawn rows link section 4.1.13; 0 unlinked.
  The 049/050/051 line count rises 7->9 solely from the two revision rows naming
  section 4.1.13; no requirement text resurrected.
- Write set: all 72 amendment files sit inside `spec/`, `CHANGELOG.md`,
  `tools/spec/`, `g5 evidence/`; `2090e2d` touches only g5 evidence;
  `changed-product-paths.json` (53 paths) exactly matches `15b3a55..531eea3`.
  THIRD_PARTY_NOTICES.md untouched (MIT notice unchanged, per vendor-check).
- PR11 discrepancy: `git cherry origin/main 579b951` = `-`, PR11 OPEN, head
  `579b951` ("Re-vendor ... c24e4a3"). Patch-equivalent to main, correctly not
  merged and correctly excluded from history. No action for this review; parent
  closes the redundant PR and corrects the planning text.

## OCR (OpenCodeReview delegation — required capability)

- `ocr delegate preview --from 771c289... --to 2090e2d...`: exit 0 —
  80 reviewable / 290 total.
- `ocr delegate rule` for every reviewable file: exit 0 for all 80, zero
  nonzero. Rules are advisory checklists (Python declaration-typo, JSON/YAML key
  spelling, shell default, workflow security/correctness); the reviewer applied
  each group below. Raw outputs retained in `evidence/ST-4/g5-review/`.
- Amendment files (reviewed directly, not just via rules):
  - `g5/check-links.py`, `g5/check-vendor.py` (Python): no declaration typos;
    `parents[6]` root resolution, GitHub-style anchor slugging with duplicate
    suffixing, `int(mode[-3:], 8)` mode parse, and assert-as-check under plain
    `python3` (same accepted pattern as g3) all correct. Re-ran both: exit 0.
  - 10 g5 JSONs (key spelling): no key errors; `receipt.json` command list,
    link/UID counts, and `build_sha256` all match reviewer recomputation;
    `supply-chain.json` merge-base and skill-tree-equality claims re-verified
    (exits 0); `merged-prs.json` matches the live merged list.
  - `g5/vendor-check.sh`, `g5/verify.sh` (default rules): fail-fast wrappers
    correct; command sequences reproduce the packet VERIFY set. No defects.
  - `spec.yaml` + `tools/spec/template/spec.yaml` (YAML keys): no key errors;
    revision metadata verified above.
  - `tools/spec/spec_build.py`, `spec_lint.py` (Python): byte-identical to HQ
    pin `0467883` (proven by vendor-check), i.e. HQ B3-reviewed content; no
    declaration typos; behavior confirmed through the passing build/lint/UID
    re-runs. No defects.
  - Excluded amendment files read directly instead: 46 spec sources + built
    file + CHANGELOG (prose/link checks above), `VENDORED.md` (pin + skill tree
    `16985771...` + MIT notice verified), and `.md`/`.txt` evidence files.
- Inherited files (already reviewed on main; accounted by group, not re-litgated):
  hooks + `ci.yml` + `tools/ci/*` (S09/B1/B2-reviewed), `journey.json`, and
  B3/S02/S06/S09/S42/S43/S44/S45 evidence JSONs — each covered by its own
  merged-PR review in the planning packets; rule outputs recorded for all.
- Excluded-file rationale: 201 `unsupported_ext` (Markdown/text evidence and
  spec sources — amendment ones read directly, inherited ones covered by their
  own reviews), 4 `binary` (coverage-data artifacts), 5 `default_path`
  (`tools/ci/tests/test_*.py`, inherited S09T gate tests, green in the gate).
- Tool failures: none. No typed gaps.

## Visual review

Not applicable as rendered UI. No figure files changed in the amendment
(`azdiagram`/`diagram.py` untouched; figure YAML/SVG/draw.io absent from the
amendment diff), so the g3 figure evidence stands.

## Reverify

Enabled but not applicable — Markdown/Python tooling sources only; no compiled
binary built or claimed (consistent with `docs/vnv` guidance). Not recorded
as a pass of anything.

## Vnv instructions

Read `docs/vnv/AGENTS.md` + `spec/AGENTS.md`. Explicit `vnv-review` commit scope
for this repository is `main`: honored by separating the 218 inherited main
records from the 72 amendment files while accounting for all 290 preview paths.
Evidence sanitized (no home paths, keys, or sessions). No `vnv`-label findings:
nothing to file.

## Route used

Reviewer (independent defect assurance), Lifecycle AFC-2026-10-11, spec track
ST-4 generation 5 (amendment only). Verdict PASS is terminal; no repair
transition. Prior g1/g3 reviews and bounds remain historical.

## developer_feedback

Link/revision tooling behaved as documented: lint enforces linked references,
the builder emits clickable Appendix A traces, and revision `changes`/`links`
render correctly. Two observations for the skill owner: (1) `check-vendor.py`'s
exact file-set assertion trips on `__pycache__` from ordinary verification
runs — the author's `PYTHONDONTWRITEBYTECODE=1` works around it, but ignoring
`__pycache__` in the checker would be more robust; (2) `changes` accepts source
headings only, so generated-Appendix-A changes must live in `summary` (author
already noted this). No new tooling gaps: `ocr` delegate preview + all 80 rules
ran clean.
