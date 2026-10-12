# ST-4-g3 independent review result

- Candidate: https://github.com/1wgrumph/amazon-fantasy-companion/pull/10, branch `afc/st4-spec`, head `771c28958f78e611048528aedbd9ed4490f308e1` (PR head confirmed via `gh pr view 10`).
- Range reviewed: g3 `4d9b549696408ddaa5f432bac4911cbc349cb874..771c289` (81 paths, all inside `spec/amazon-fantasy-companion/` + `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/`) and register deltas `5e59270b8320d6085039f26b64f14897736845f6..4d9b549` (`429e064`, `4d9b549` touch only the register + `re-sd035-receipt.md`).
- Contract: `packets/ST-4-g3.md` (SD-034/035/036). Reviewer did not author the change. No commits, PR comments, or merges made.

## Verdict: PASS

No actionable defects. All re-runs pass; all six external sources exist and support only what the spec claims; UID coverage is 66/66 with zero unknown; withdrawn UIDs appear solely in withdrawal contexts; all eight figures re-render byte-identical and match the text.

## Findings

None. No P0-P3 findings; no advisory items withheld — every checked item is recorded below.

## Re-run exit codes (reviewer-executed, worktree `amazon-fantasy-companion-st4`)

| Check | Command | Exit |
|---|---|---|
| Build 1 | `uv run --script tools/spec/spec_build.py spec/amazon-fantasy-companion /tmp/st4-g3-review-build1.md` | 0 |
| Build 2 | `uv run --script tools/spec/spec_build.py spec/amazon-fantasy-companion /tmp/st4-g3-review-build2.md` | 0 |
| Byte compare (build1 vs build2) | `cmp` | 0, identical |
| Byte compare (build1 vs committed) | `cmp` vs `spec/amazon-fantasy-companion/amazon-fantasy-companion.md` | 0, identical; sha256 `1d5291cb990976652d3740f46ff7bfd28bd7f24eb9abb4fc1825faad43e1088a` matches `g3/receipt.json` |
| Spec lint | `uv run --script tools/spec/spec_lint.py spec/amazon-fantasy-companion` | 0 |
| Diagram lint | `uv run --script tools/spec/diagram.py lint spec/amazon-fantasy-companion` | 0 |
| Label grep | `grep -nE '\*\*(BLUF\|Frame\|Who\|What\|Why\|How\|When\|Where):?\*\*'` over sources + built file | 1 (no matches = pass) |
| UID coverage | independent Python check: 66 found, missing [], unknown [] | pass |
| Rule-12 path scan | `grep -rnE '(/home/\|/Users/)[A-Za-z0-9._-]+/' spec/ docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/` | 1 (no matches = pass) |
| Mode A grep | `grep -n -i 'sample footage\|Mode A'` on built file | 5 lines, all withdrawal/retained-model context (one is the benign `panel-mode annotates` substring hit) |
| Figures re-render | render all 8 YAML in /tmp, `cmp` SVG + draw.io vs committed | 16/16 identical |
| Section-7 vs register | full-cell compare of all 63 active verification + allocation cells | 0 mismatches |
| Local links | all 6 relative doc links + 8 figure refs in built file resolve | pass |
| Write set | g3 diff paths outside allowed prefixes | none (81/81 inside) |

SD-035 spot checks (all present, none contradicted): Off/Mild/Hype (4.1.7); 24/32 px + owner acceptance (4.1.11, 7.1.10); no Mode A, alerts + Watch, full-screen fallback (4.1.12/4.1.13); channel + can-watch basis incl. provider out-of-region/not-in-plan (4.1.8); spike order Prime Video (TNF), ESPN app, DirecTV Stream app, YouTube TV (4.1.8); local CBS/FOX/NBC channel + carrying app else no deep link (4.1.8); close game within 8 pts 4th/OT (4.1.5); stale_after 60 s (4.1.11); PPR/Half-PPR default Half-PPR, Yahoo scoring for Yahoo leagues (4.1.2, AFC-PR-066 traced in 4.1.2 + 7.1.2 + Appendix A); Apache-2.0 (1.4.1, 4.8); open items exactly Q6/Q7/Q8/Q10 (section 2). No TBD/TODO/placeholder/open-question wording (two `placeholder(s)` hits refer to native-model String placeholders, legitimate). In-repo provenance confirmed for model digest `14fb815b…`, SysON project `2a033855…` zero-errors receipt, VENDORED pin `c24e4a36…`, and T_judge_access 2026-11-20.

## Source-check table (each URL opened by the reviewer)

| URL | Spec claim | Supported |
|---|---|---|
| https://blog.youtube/news-and-events/introducing-fantasy-view-youtube-tv/ | 2020 introduction describes linking NFL.com and viewing team, player and matchup scores during live games | yes (datePublished 2020-10-15 verified in HTML; "link your NFL.com fantasy account", team score, player stats, matchup scores) |
| https://support.google.com/youtubetv/answer/9119412 | Current views help page names ESPN and Yahoo | yes ("We currently support ESPN and Yahoo fantasy platforms") |
| https://support.google.com/youtubetv/answer/15583839 | Fantasy Football View instructions describe fantasy access while watching a live NFL game on a smart TV or streaming device | yes |
| (all three YouTube pages) | No evidence of tune-in alerts or cross-provider Watch; absence of documentation is not proof of absence | yes (pages describe views/stats only; the one "notifications" mention describes user phone habits in research, not a product capability; spec hedges correctly) |
| https://www.aboutamazon.com/news/aws/prime-video-thursday-night-football-next-gen-stats-ai-features | Prime Vision with Next Gen Stats is an alternate TNF stream with analytics and on-screen insights supported by AWS | yes (alternate stream, Expanded Next Gen Stats, AWS-powered) |
| https://operations.nfl.com/game-operations-logistics/technology/performance-tracking-data-next-gen-stats | Next Gen Stats is player-tracking data and analytics running on AWS infrastructure | yes (HTTP 200; "running entirely on Amazon Web Services (AWS) infrastructure", tracking + ML on AWS) |
| https://www.nba.com/news/nba-media-agreements-2024 | Prime Video's NBA rights run from 2025-26 through 2035-36 | yes (HTTP 200; "Prime Video will telecast NBA games beginning with the 2025-26 season and running through the 2035-36 season") |

SD-036 marking correct: future-direction subsection states discussion only, external context not capability, names sport-agnostic vs NFL-specific components, and claims no integration or data access.

## OCR (OpenCodeReview delegation — required capability)

- `ocr delegate preview --from 5e59270b8320d6085039f26b64f14897736845f6 --to 771c28958f78e611048528aedbd9ed4490f308e1`: exit 0 — 16 reviewable / 146 total. All `.md`/`.txt`/`.svg`/`.drawio` excluded as `unsupported_ext` (expected); the reviewer read the excluded spec sources and built file directly instead (see checks above).
- `ocr delegate rule <file>` for every listed file: exit 0 for all 16. Per-file application:
  - `evidence/ST-4/check-spec.py`, `evidence/ST-4/g3/check-spec.py` (Python rules): no typos, dead code, mutable defaults, boundary, exception, identity, resource, perf, concurrency, or security issues. `parents[5]`/`parents[6]` depths correct for each location; `assert`-as-check is the script's stated mechanism run under plain `python3`. No findings.
  - `evidence/ST-4/g3/receipt.json`, `evidence/ST-4/g3/sources.json` (JSON-keys spelling): no key spelling errors; `built_sha256` matches reviewer-computed hash; URL list matches the six spec citations. No findings.
  - `evidence/ST-4/verify.sh`, `evidence/ST-4/g3/verify.sh` (default rules): fail-fast `run` wrapper correct; command sequence reproduces the packet VERIFY set; no security/perf/maintainability issues. No findings.
  - 8 figure YAMLs + `spec.yaml` (YAML-keys spelling): no key spelling errors; labels match rendered SVG text and spec prose (incl. the two SD-035 annotations). No findings.
  - `tools/spec/spec_lint.py` (Python rules; delta from HQ re-vendor c24e4a3, not g3-authored): new `WRITER_LABEL` regex and opening-paragraph check correct; `_next_content` safe for index -1 (`lines[0:]`); no findings.
- Tool failures: none. No typed gaps.

## Visual review

Not applicable as rendered UI; per packet, the eight referenced SVGs were opened (text-extracted) and checked against the text: alert-lifecycle, device-link, and panel-mode state machines match 4.7/4.1.5/4.1.10/4.1.12; panel-mode and structure carry the SD-035 superseded/retained annotations the text describes; all SVGs are well-formed XML and byte-identical to fresh vendored-kit renders.

## Reverify

Not applicable — Markdown/SVG authoring; no compiled binary claimed.

## Route used

Reviewer (independent defect assurance), Lifecycle AFC-2026-10-11, spec track ST-4 generation 3. Verdict PASS is terminal; no repair transition.

## developer_feedback

no new observations. Tools exercised: vendored `tools/spec` (`spec_build.py`, `spec_lint.py`, `diagram.py` render + lint) at pinned c24e4a3, `ocr` delegate preview + rule, `gh pr view`, public-URL retrieval via browser + curl. All behaved as documented.
