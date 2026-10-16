---
type: implementation-receipt
title: ST-4 generation 1 architecture specification author receipt
okf_status: draft
tags: [afc, specification, evidence]
---

# ST-4-g1 author receipt

Verdict: PASS for the dispatched author VERIFY; candidate ready for independent review.
This is not independent assurance, owner acceptance, publication or merge authority.

- Lease: ST-4-g1, generation 1; branch `afc/st4-spec`.
- Input base: `5e59270b8320d6085039f26b64f14897736845f6`.
- Authority: DEC-AFC-SD-033 and recorded dispatch under AUTH-AFC-2026-10-11-002.
- Scope: D1 only; 65 section sources, eight YAML/SVG/draw.io figure sets,
  generated `spec/amazon-fantasy-companion/amazon-fantasy-companion.md`, and this evidence directory.
- Frozen profile: tech-writing, single_implementer, implementer primary Codex CLI /
  GPT-6 Astra / medium. Configuration digest:
  `8a6b57450b92f5658666150c7cdcb05553016240061befb226c0ae4eb83c94ce`.
  No model/harness switch or sub-agent dispatch.
- Frozen capabilities preserved: `review.coverage_assist.enabled=true`,
  `review.coverage_assist.required=true`, `deterministic_verification.reverify.enabled=true`.
  OCR/OpenCodeReview is assigned to independent review in delegation mode, not run by this author.
  Reverify: not applicable — no compiled-binary correctness claim; output is Markdown/SVG/XML.
- BRAN: unavailable, no native policy; direct repository discovery used.

## Commands and evidence

Run from the repository root:

```sh
bash docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/verify.sh
```

The runner exports `UV_OFFLINE=1 UV_PYTHON=3.12 PYTHONDONTWRITEBYTECODE=1`.
[verification.txt](verification.txt) records each exact command and exit status:
render all eight figures, build, section lint, diagram lint, build again, `cmp`,
UID/Appendix/link/path/write-set checks, whitespace check and built-file digest.
All final commands exit 0. No network dependency fetch was required.
The optional initial staged whitespace scan reported the builder’s intentional two-space
Markdown hard break at document line 3. The final checker asserts that exact line is the
only generated trailing whitespace; Git whitespace checks cover all other candidate paths.
The generated output and pinned builder are unchanged.

UID coverage: 65/65 in the built document; 65/65 in generated Appendix A; unknown UIDs: 0.
Local links resolve. Rule-12/C7 scan finds zero home-shaped or local machine-root paths
in the authorized write set. Its self-check distinguishes synthetic path shapes from XML
closing tags and HTTPS API links. No generated specification bytes were hand-edited.

The pre-commit checkout/lease comparison is recorded in `lease-check.txt`.
The final candidate SHA and draft PR receipt are returned by the author after commit/push;
this file does not embed its own commit hash.

## Evidence-driven corrections

1. Environment: default Python 3.14 offline render exited 1:
   `Failed to download pyyaml==6.0.3`; the cp314 wheel was not cached.
   Inspection found Python 3.12 installed; selecting it reused cached pinned PyYAML 6.0.3.
   Final renders/build/lints succeed with network disabled. No dependency pin or tool changed.
2. Author check: the first path scan classified the portable interpreter directive as a
   local root. Removed that unnecessary directive; the runner is invoked with `bash`.
3. Author check: the next path scan matched XML closing `root` tags in generated draw.io.
   Inspection established these were markup, not paths. Restricted root-prefix recognition
   outside XML closing tags and added positive/negative self-checks; genuine path checks remain.

These are environment and author-check corrections, not reproduced product defects.
No issue filed. No vendored lint rule weakened.

## Scope coverage and open items

D1 covers issue #1 items 1, 2, 3, 4, 6, the panel, lightweight design, interfaces/data/states,
security, failure behavior, all C1–C9, and per-UID verification. Section 4.8 disposes the entire
research topic set without adding Apple/Roku/Vega implementations or claiming vendor feasibility.
D2/D3/D4, submission materials and Scribe consolidation remain their existing program deliverables.

Section 2 surfaces every ST-2 owner question: Q1 resolved by SD-027; Q2 excitement scale,
Q3 legibility criterion, Q4 footage storage, Q5 first provider, Q6 exact stick/OS,
Q7 Yahoo approval, Q8 AWS account, Q9 license and Q10 missing S8 ledger remain open.
It also names close_game_margin, excitement_levels, stale_after, manual default scoring,
and concrete transport/security contract tuning. No answer or threshold was invented.

Platform risks remain: heads-up over third-party playback, supported detection, direct game/channel
routes, entitlement evidence, provider-video composition, conditional Alexa/speech and exact device
compatibility. SysON parsing is recorded model evidence, not implementation verification.
The Mode A/replay/manual fallbacks retain their labels and separate scopes.

## Gates outside this author packet

- Shared repository gate: not run; `tools/ci/gate.sh` is absent from the leased base and S09
  owns it concurrently. The packet explicitly authorizes ST-4 to start now. This is an integration
  gap for the orchestrator, not a claimed gate pass; no tools or CI paths were changed.
- Vnv: REFUSED_NO_VNV; no Vnv guidance tree in this checkout. No independent review attempted.
- Requirements System: not a bound SDoc candidate; SD-027 selects Markdown. No host review,
  workspace revision/digest, or host mutation was fabricated.
- Real-device/API/security acceptance and hardware performance measurements: not run; the former
  belongs to Phase 2, and hardware benchmarking is excluded by owner scope.
- PR remains draft for independent review, ST-5 acceptance and the S09 integration gap. No merge.

## Skill selection

`spec-authoring` is the existing owner of Markdown section/figure/build/lint behavior.
The strongest adjacent skill, `use-requirements-system`, owns SDoc/host-bound documents;
its document form does not match this Markdown packet. The create-lean-skill precondition
“Create a skill only when no existing skill can own the outcome cleanly” therefore yields
NO_CHANGE: no duplicate skill, creator-script execution or unauthorized tool-tree edit.

Trigger checks (inspection, not a runtime skill-evaluation claim):
- Matching: “Build this Markdown architecture from numbered sections and model figures”
  selects spec-authoring; section/build/figure checks were exercised on this candidate.
- Non-matching: “Review a host-bound SDoc revision” is explicitly excluded by spec-authoring
  and belongs to use-requirements-system; this session performed no SDoc review or host binding.

## developer_feedback

Date: 2026-10-12. Reporter: Product Implementer, ST-4-g1, spec-and-docs lane.
Durations were not measured. Reproduction entrypoint and results are linked above.

| ID / tool | Used for / version | Worked well | Needs work / impact | Onboarding / workaround | Would build again |
|---|---|---|---|---|---|
| DX-ST4-01 spec-authoring skill | Template, floor sections, figures and reproducible D1; vendored source pin in tools/spec/VENDORED.md | Clear separation of source sections, generated Appendix A and requirement ownership | Environment choice must be explicit for offline use; no content-tool defect established | Read skill plus section/figure rules, then existing template | Yes: bounded author workflow and deterministic output |
| DX-ST4-02 vendored spec tools | spec_build.py, spec_lint.py, diagram.py; source commit ac47f0eca149eb281e41a6bdd9d490221c7a14cf | Build/lints pass offline; second build identical; figures preserve editable sources | No new tool defect; lint success is syntactic, so UID/link/scope checks remain necessary | Use tools/spec directly, no acquisition or mutation | Yes: small, reusable and network-independent with cached dependencies |
| DX-ST4-03 uv / Python / PyYAML | uv 0.11.6; Python 3.12.3; PyYAML 6.0.3 | Cached Python 3.12 route works offline | Default Python 3.14.4 lacked cached cp314 wheel; first render blocked, environment issue | Select installed Python with UV_PYTHON=3.12; no fallback model/harness change | Yes: pin interpreter in repeatable run recipe |
| DX-ST4-04 Graphviz | dot 14.1.2; model-derived diagram layouts | Eight figures render and diagram lint passes | No new observed friction; no manual visual acceptance claimed | Existing dot installation; vendored diagram command | Yes: deterministic editable figure pipeline |
| DX-ST4-05 Git / GitHub CLI | Source identity, issue #1 read, branch and draft PR delivery; installed versions in lease-check.txt | Read-only issue and checkout inspection supplied scope and branch facts | No new observed friction as of author verification | Existing authenticated CLI; no credential values accessed | Yes: auditable candidate and draft receipt |
| DX-ST4-06 role/workflow skills | Implementer, Ponytail, create-lean-skill and ship-pull-request instructions | Kept write set bounded, reused existing skill and preserved draft boundary | Shared PR gate expects S09 file absent at this base; explicitly recorded gap | Apply explicit packet authority; no gate bypass claim or skill duplication | Yes: separate author checks from review and publication |

No Amazon, Yahoo, ESPN, AWS runtime or device was exercised by ST-4. No vendor performance or
onboarding experience is fabricated. No external feedback was sent.
