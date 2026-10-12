ROLE
Product Implementer, spec-and-docs lane (profile tech-writing; BEARING_ROLE=implementer), spec track ST-4, generation 3. RESPONSIBILITY: rewrite the product architecture specification as specification prose and bring it in line with the owner's answers. Not requirements authoring, not modeling, not review.

STATE
FACTS:
- Dispatch record in $HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json execution_receipts: lease_id ST-4-g3; worktree (cwd) $HOME/alphazede/worktrees/amazon-fantasy-companion-st4; branch afc/st4-spec (PR #10); base 4d9b549696408ddaa5f432bac4911cbc349cb874 (contains the SD-035 register deltas and main merged with the re-vendored tools/spec at Alphazedehq c24e4a3); evidence_dir docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/ (in your worktree; g3 files under g3/).
- Owner decision DEC-AFC-SD-034: sections read like a real specification. No printed **BLUF:** and no **Frame** Who/What/Why/How/When/Where labels. Each section answers an unprinted writer's checklist: the decision, the concern it addresses (cite register UIDs), the mechanism, the rationale, how it is verified. Follow the merged skill exactly: $HOME/alphazede/Alphazedehq/skills/spec-authoring/SKILL.md and its references; the vendored tools/spec/ (VENDORED.md pins c24e4a3) build and lint it, and lint rejects the labels.
- Owner decision DEC-AFC-SD-035 (register already updated; read the register, do not restate requirement text): excitement Off/Mild/Hype; legibility 24 px body / 32 px scores at 1080p plus owner acceptance on the stick; NO Mode A sample footage — if the panel cannot sit beside a provider's live video, the product is alerts + Watch only with the lineup panel as a full screen in our app (AFC-PR-049..051 withdrawn); the product is a tune-in alert system: Watch knows the broadcast channel and whether the customer can watch (location + subscription, or the provider's own out-of-region / not-in-plan answer); provider spike order Prime Video (TNF), ESPN app, DirecTV Stream app, YouTube TV; local broadcasts show the channel and offer a provider app that carries it, otherwise no deep link; close game = within 8 points in the 4th quarter or overtime; stale after 60 s; manual-lineup scoring presets PPR and Half-PPR (default Half-PPR), Yahoo leagues use Yahoo's scoring; license Apache-2.0. Still open: Q6 stick model/OS, Q7 Yahoo application, Q8 AWS account, Q10 S8 ledger restore (owner chose restore; Alphazedehq task).
- Competitive context (owner asked): YouTube TV "Fantasy View" links NFL.com or Yahoo leagues and shows roster scores beside the game (sources: https://blog.youtube/news-and-events/introducing-fantasy-view-youtube-tv/ , https://support.google.com/youtubetv/answer/9119412). No evidence found of tune-in alerts or cross-provider Watch. State this in the rationale as external context with the citations; claim only what the sources say.
- Owner decision DEC-AFC-SD-036 (discussion only, no new requirements): a future-direction subsection discusses extending the product to an AWS-powered analytics viewing experience on Prime Video (the analytics-focused alternate Thursday Night Football stream; AWS-powered NFL Next Gen Stats) and to Amazon's NBA rights on Prime Video. Cite public sources you verify (Amazon/AWS/NFL/NBA press pages); mark them external context, not product capability. Name which components are sport-agnostic (alert policy, Watch handoff, panel) and which are NFL-specific (feed adapter, scoring presets).
- Models under docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/models/ are unchanged; where a model element still reflects Mode A footage, say the element is retained pending Phase 2 design per SD-035 rather than editing models.
ASSUMPTIONS to check: the vendored build and lint run offline; figures still render.
Other agents work concurrently in other worktrees (S09 owns tools/ci/, .githooks/, .github/). core.hooksPath is unset; keep it unset.

OBJECTIVE
spec/amazon-fantasy-companion/ rewritten as prose per SD-034, consistent with the SD-035 register and SD-036, rebuilt into the single-file specification with the vendored tools; the open-items section shows only what is still open.

AUTHORITY
Allowed writes: spec/amazon-fantasy-companion/**, the built spec file the skill names, and the evidence_dir. Commit with `git commit --no-verify` (author from env; never Co-Authored-By); `git push --no-verify origin afc/st4-spec` (plain); update PR #10's description (use `gh api -X PATCH repos/1wgrumph/amazon-fantasy-companion/pulls/10` if `gh pr edit` fails). Prohibited: tools/, docs/plans/ outside evidence_dir (the register and models are read-only to you), .github/, .githooks/, git config, merge, force-push, credentials, absolute home paths.

LOOP
Write, build, lint, fix; classify failures (content / tool / environment); retry only with new evidence. A register gap or contradiction you cannot resolve in prose: stop with CONTRACT_FAILURE naming the UID.

VERIFY (record command, exit code, output tail)
- The skill's build exits 0 and a second build is byte-identical; the skill's lint exits 0.
- `! grep -nE '\*\*(BLUF|Frame|Who|What|Why|How|When|Where):?\*\*'` over spec/amazon-fantasy-companion/ and the built file.
- UID coverage: every register UID (including withdrawn ones, shown as withdrawn in Appendix A) appears in the built spec; no UID unknown to the register.
- `grep -n -i 'sample footage\|Mode A' <built file>` only where describing the SD-035 withdrawal or a retained model element.
- rule-12 path scan on your write set: no output.

RETURN
PASS | REPAIRABLE_FAILURE | CONTRACT_FAILURE | ENVIRONMENT_FAILURE | NEEDS_MORE_EVIDENCE; head SHA; PR #10 URL; built file path; commands with exit codes; UID coverage; external sources cited (URL list); remaining open items; developer_feedback (AC-AFC-DX-04: spec-authoring skill and vendored tools — used for, worked well, needs work, would build again).

STOP
After the push with VERIFY passing, or a typed failure with exact error.
