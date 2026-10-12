# S42 verification receipt (lease S42-g2, generation 2)

branch: afc/s42-revendor-prose
base: 5e59270b8320d6085039f26b64f14897736845f6
head: 579b9519d5c2e5a92b208112768cb4654d114798
draft PR: https://github.com/1wgrumph/amazon-fantasy-companion/pull/11
authority: AUTH-AFC-2026-10-11-002
package digest: a018168f575741b5f53bbe7fac4bcb13128e31f37f69d73ba2433cf8d09d5144
vendored source: Alphazedehq c24e4a36131c03dcda283b5431990cf14e603e68 (= origin/main, merged D5 prose commit, PR #309 / SD-034)
skill tree id: d97986b6351ada4e20807d6bebed213033fb3c56

## Changed paths (base..head)

40 files, 55 insertions, 389 deletions, all under tools/spec/
(VENDORED.md, spec_lint.py, 38 template files). THIRD_PARTY_NOTICES.md
untouched: LICENSE-gridmarket is byte-identical between ac47f0e and
c24e4a3 (verified via git diff, empty). No other paths touched.

## Commands

- vendor.sh: `bash <alphazedehq-main-checkout>/skills/spec-authoring/scripts/vendor.sh
  <s42-worktree>` → `VENDORED: .../tools/spec at c24e4a3...`, exit 0.
  First attempt exit 1 (`REFUSED: modified vendored copy`): environment
  artifact — the umask-002 checkout left worktree files at 664/775 while
  the guard compares exact modes 644/755; every byte was identical
  (verified file-by-file against pristine `contents(ac47f0e)`).
  Normalized modes with chmod (git-invisible: status stayed clean, git
  tracks only the exec bit) and re-ran the unchanged command.
- CMD-SPEC-VENDOR on committed candidate 579b9519 (substitutions:
  vendored_source_commit read from VENDORED.md = c24e4a3…,
  alphazedehq_checkout = main checkout at c24e4a3 = origin/main,
  azhq_d5_sha = c24e4a3…): `exit=0`, exit 0. Also exit 0 pre-commit.
- CMD-PATH-SCAN-PLAN over `tools/spec THIRD_PARTY_NOTICES.md` (50 files):
  no output → PASS.
- Commit/push with --no-verify per packet (core.hooksPath unset):
  author `Muse Code <1wgrumph+muse-code@gmail.com>`, committer from repo
  config, no Co-Authored-By. Push exit 0; draft PR #11 created, readback
  confirms draft/base/head and all four body sections.
- No software-acquisition scan: source is the leased main checkout at a
  main commit read via git objects (no network fetch); neither S42
  command requires CMD-SCAN.

## Proof rows

- SEIT-AFC-D5-04.V: PASS via CMD-SPEC-VENDOR (tools/spec equals merged D5
  scripts+template; VENDORED.md names c24e4a3, tree id, MIT notice).
- SEIT-AFC-SPEC-01: PASS via CMD-SPEC-VENDOR (same evidence;
  THIRD_PARTY_NOTICES.md carries the GridMarket MIT notice).
- SEIT-AFC-PATH-01.P: PASS via CMD-PATH-SCAN-PLAN on S42 outputs (no absolute
  home path; plan-directory scrub remains the Orchestrator's scope).
- SEIT-AFC-RISK-16: no new evidence (Phase 2 entry receipt is IE-P1-F08 scope;
  D5 merged and S42 candidate ready within Phase 1 at time of writing).

## Stop condition

VENDORED.md names c24e4a3 whose skills/spec-authoring tree id
(d97986b6…) equals the merged D5 commit's; vendored scripts and template
equal that tree (diff -r clean); MIT notice present in VENDORED.md and
THIRD_PARTY_NOTICES.md. STOP met.
