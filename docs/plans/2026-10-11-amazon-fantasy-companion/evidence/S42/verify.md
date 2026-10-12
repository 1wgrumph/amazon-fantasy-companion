# S42 verification receipt (lease S42-g1, generation 1)

branch: afc/s42-vendor-spec-tools
base: 72e99989aa1b93d3afb0fbd4a3d6deb2dd7991be
head: df75f14076d7cf5201b88ffa8b3c881f0477cafd
draft PR: https://github.com/1wgrumph/amazon-fantasy-companion/pull/7
authority: AUTH-AFC-2026-10-11-002
package digest: a018168f575741b5f53bbe7fac4bcb13128e31f37f69d73ba2433cf8d09d5144
vendored source: Alphazedehq ac47f0eca149eb281e41a6bdd9d490221c7a14cf (origin/main, D5 head)
skill tree id: 65e520d12fb7354d682ca392e1b88396a37dbb2f

## Changed paths (base..head)

50 files, 1904 insertions, 0 deletions: tools/spec/ (49 files incl.
VENDORED.md) + THIRD_PARTY_NOTICES.md. No other paths touched.

## Commands

- vendor.sh: `bash <alphazedehq-main-checkout>/skills/spec-authoring/scripts/vendor.sh
  <s42-worktree>` → `VENDORED: .../tools/spec at ac47f0e...`, exit 0.
- CMD-SPEC-VENDOR on committed candidate df75f14 (substitutions:
  vendored_source_commit=ac47f0e…, alphazedehq_checkout=main checkout,
  azhq_d5_sha=ac47f0e…): `exit=0`, exit 0.
- CMD-PATH-SCAN-PLAN over `tools/spec THIRD_PARTY_NOTICES.md` (50 files):
  no output → PASS.
- Scan receipt: scan-spec-tools.md, `verdict: PASS`, written before first use
  (before vendor.sh ran).

## Proof rows

- SEIT-AFC-D5-04.V: PASS via CMD-SPEC-VENDOR (tools/spec equals merged D5
  scripts+template; VENDORED.md names ac47f0e, tree id, MIT notice).
- SEIT-AFC-SPEC-01: PASS via CMD-SPEC-VENDOR (same evidence;
  THIRD_PARTY_NOTICES.md carries the GridMarket MIT notice).
- SEIT-AFC-PATH-01.P: PASS via CMD-PATH-SCAN-PLAN on S42 outputs (no absolute
  home path; plan-directory scrub remains the Orchestrator's scope).
- SEIT-AFC-RISK-16: no new evidence (Phase 2 entry receipt is IE-P1-F08 scope;
  D5 and S42 both landed/ready within Phase 1 at time of writing).

## Stop condition

VENDORED.md names ac47f0e whose skills/spec-authoring tree id
(65e520d1…) equals the D5 head on main; vendored scripts and template equal
that tree (diff -r clean); MIT notice present in VENDORED.md and
THIRD_PARTY_NOTICES.md. STOP met.
