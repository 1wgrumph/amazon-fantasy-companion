---
type: review-result
title: ST-4 independent review result — D1 architecture specification
lifecycle: AFC-2026-10-11
step: ST-4
role: reviewer
candidate_pr: https://github.com/1wgrumph/amazon-fantasy-companion/pull/10
candidate_branch: afc/st4-spec
candidate_head: b39553be846d7905ea4f0b0028082d6979cab402
candidate_base: 5e59270b8320d6085039f26b64f14897736845f6
verdict: PASS
---

# ST-4 review result: PASS

Independent review of the D1 architecture specification candidate (PR #10,
`afc/st4-spec` @ `b39553b`, 97 files, OPEN draft). The reviewer did not author
the candidate. Worktree was clean at the candidate head before and after
review; no candidate bytes were modified (all reproduction outputs went to
`/tmp`).

## Verdict rationale

The spec is faithful to the gated register (65 UIDs), the ST-3d SysML v2
models at digest `14fb815b…`, the scope-decision batch, and issue #1: no
invented requirements (zero unknown UIDs), no contradicted SD decisions,
messaging excluded, Mode A/B and C1–C9 correct, unverified platform
capabilities stated as risks/assumptions, every UID traced in Appendix A,
all 8 figures match the model views, interfaces/data/states are consistent
with the models, all ST-2 owner questions are surfaced, and
spec-authoring format rules hold (both lints exit 0). Build reproduces
byte-identical offline. The single finding (P3) is a stale file count in
author evidence, not a spec defect, and does not block ST-5.

## Findings

| ID | Sev | file:line | Defect | Exact fix |
|---|---|---|---|---|
| F1 | P3 | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/verification.txt:39-40` | Stale counts: claims "96 authorized files" and "96 changed paths", but the committed candidate has 97 of each (PR reports 97 changed files; independent `check-spec.py` re-run prints 97). The author's verification ran before the final file was added. Reproducer: `python3 …/evidence/ST-4/check-spec.py` → `Rule-12 / C7 path scan: 97 authorized files; 0 findings` + `Write-set check: 97 changed paths; PASS`. | Re-run `verify.sh` on the final tree and update the two count lines to 97 (fold into any ST-5 follow-up commit; no spec content changes). |

No P0–P2 findings. No finding blocks ST-5 owner acceptance.

## Fidelity checklist (all observed, not inferred)

- Register: 65/65 UIDs in built doc and Appendix A; 0 unknown (independent
  re-run); Appendix A rows match section front-matter bindings 65/65
  (modulo `04` vs `4` numbering style).
- Front matter: 65/65 section sources carry exactly 1 heading and ≤5
  requirement bindings; all 15 COE-ASA-001 floor subsections present
  with template names.
- Models: recomputed sha256 over the four `.sysml` sources equals the
  ST-3d digest `14fb815b…` cited in spec §1.2.1 and every figure YAML.
- Figures: F7 state figures reproduce the native states/transitions
  exactly (AlertLifecycle 7 states/7 transitions, DeviceLink 4/4,
  PanelMode 2/1 with no return); interfaces figure names all 8 native
  interfaces with the C8 conditional; structure figure groups all
  modeled parts; data figure covers all 7 items; Table 14 native fields
  match `AFC-Data.sysml` field-for-field; §4.7 transition prose matches.
- Decisions: SD-001..SD-011, SD-027 (Markdown register), C1–C9
  (Table 7 matches the scope batch, incl. T_yahoo `2026-10-16T19:00:00Z`,
  24 h spike clock, exact Mode A label); C10–C14 correctly scoped to D4.
- Starter claim verified live: `AmazonAppDev/hello-world-fire-tv` is
  Kotlin + Jetpack Compose (`.kt` sources, Compose imports), grounding
  §1.4.1; SysON project id `2a033855-…` matches `sm-syson-receipt.md`.
- Issue #1: items 1/2/3/4/6, panel, lightweight design (no benchmark),
  messaging exclusion (§1.4.1 + PR-057; no messaging surface anywhere),
  all research topics disposed in §4.8 without new vendor promises.
- Risks: unverified capabilities (heads-up over provider playback,
  provider URI contracts, detection, entitlement, panel composition,
  voice routes) appear as assumptions/risks/open items, never as facts.
- Owner questions: Q1–Q10 match the ST-2 receipt list (Q1 = persistence,
  resolved by SD-027); P1–P3/D1–D2 match register open parameters.

## Re-run exit codes (reviewer, `UV_OFFLINE=1 UV_PYTHON=3.12`)

| Command | Exit |
|---|---|
| `spec_build.py` → /tmp build 1 | 0 |
| `spec_build.py` → /tmp build 2 | 0 |
| `cmp` build1 build2 (rebuild identical) | 0 |
| `cmp` build1 committed doc (matches `1b391d23…`) | 0 |
| `spec_lint.py` | 0 |
| `diagram.py lint` | 0 |
| `check-spec.py` (65/65, 65/65, 0 unknown, links PASS, paths 0, writeset 97 PASS) | 0 |
| 8× `diagram.py render` in /tmp copy → SVG + draw.io byte-identical to committed | 0 (all 16) |

Offline assumption holds: no download was required under `UV_OFFLINE=1`.

## OCR (coverage assist, delegate mode)

- `ocr delegate preview --from 5e59270… --to b39553be…`: exit 0 —
  11 reviewable / 97 total; 86 excluded as `unsupported_ext` (all `.md`,
  `.txt`, `.svg`, `.drawio`). No tool failure; exclusions carry reasons
  per the OCR contract, so no typed gap. The exclusion list is advisory:
  the reviewer read the excluded spec sections directly (full 1617-line
  build plus all 65 section sources as needed).
- `ocr delegate rule` exit 0 for all 11 listed files. Per-file result:
  - `evidence/ST-4/check-spec.py` (python rules): no defect — no dead
    code, no mutable defaults, no bare/broad except, `subprocess`
    without shell; `assert` use is idiomatic for a check script.
  - `evidence/ST-4/verify.sh` (default rules): no defect — `set -euo
    pipefail`, failures propagate, temp file trapped.
  - 8 figure `*.yaml` (yaml-key spelling): no typos; every file has
    `class/title/max_width/max_height` + the body its class requires;
    caption classes (F1/F5/F2/F7×3/F3×2) match the YAML classes.
  - `spec.yaml`: keys `title/document_id/revisions` correct.
- OCR finds no defects and gives no verdict per the reviewer skill; the
  verdict above rests on direct inspection and re-runs.

## Reverify

Not applicable — no compiled binary; artifact is Markdown/SVG/draw.io.

## Route used

Muse Code (agentic CLI) powered by Meta Muse Spark, read-only review
session; no subagents; no commits, PR comments, or merges.

## developer_feedback

Date: 2026-10-12. Reporter: Reviewer, ST-4 (spec track).

| ID / tool | Used for / version | Worked well | Needs work / impact | Onboarding / workaround | Would build again |
|---|---|---|---|---|---|
| DX-RV-01 spec tools + uv offline | Build/lint/render re-runs; `UV_OFFLINE=1 UV_PYTHON=3.12` | All exits 0 first try following the author recipe; renders byte-identical | None observed this session | Copy author env exports verbatim | Yes |
| DX-RV-02 `ocr` delegate CLI | preview + 11 rule calls | Ran cleanly; exclusions labeled with reasons | `.md` exclusion means OCR covers almost none of a spec candidate; direct reading carried the review (expected per skill, not a defect) | None | Yes, with direct reading |
| DX-RV-03 GitHub CLI | PR/issue/starter verification; read-only | `gh pr view` confirmed head/branch/draft/97 files; starter contents confirmed Kotlin+Compose | `gh pr view --json baseRefOid` is not a valid field (used `baseRefName`); `gh issue view` printed a GraphQL classic-projects deprecation notice to stderr (cosmetic) | Use `--json` field list from error text | Yes |
| DX-RV-04 Graphviz dot | Figure renders via vendored `diagram.py` | 8/8 renders deterministic | None observed | Existing installation | Yes |

No Amazon/Yahoo/ESPN/AWS runtime or device was exercised. No vendor
defect claimed. No external feedback sent.
