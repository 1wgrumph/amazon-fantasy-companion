# Supply-chain scan: vendored spec-authoring tools (S42)

artifact: skills/spec-authoring/{scripts,template} + LICENSE-gridmarket (vendored)
origin: https://github.com/alphazede/Alphazedehq, origin/main commit ac47f0eca149eb281e41a6bdd9d490221c7a14cf
skill tree id: 65e520d12fb7354d682ca392e1b88396a37dbb2f
intended use: copy to 1wgrumph/amazon-fantasy-companion tools/spec/ via skills/spec-authoring/scripts/vendor.sh (S42, CONTRACT-AFC-SPECKIT)
checkout scanned: alphazedehq-main-checkout at ac47f0e (fetch verified origin/main == ac47f0e)
scan date: 2026-10-12

## CREDENTIAL FINDINGS

None. No named-prefix secret (GOCSPX-, AKIA/ASIA, ghp_/gho_/ghs_, sk-proj-,
xoxb-/xoxp-, AIza, private-key block) in scripts, template, or LICENSE-gridmarket.
Action: none.

## Inventory (no execution)

- 7 files under scripts/ (vendor.sh, spec_build.py, spec_lint.py, diagram.py,
  azdiagram/__init__.py, azdiagram/__main__.py), 40 files under template/
  (markdown, spec.yaml, figures/*.yaml/*.svg/*.drawio), LICENSE-gridmarket.
- No symlinks, no setuid/setgid, no world-writable files, no device nodes.
- Modes 664/775 (host umask group-write norm). Figure files match their
  extensions (SVG/XML ASCII text).

## Provenance and integrity

- Source commit ac47f0e is an ancestor of Alphazedehq origin/main
  (merge-base --is-ancestor PASS); skill tree id recorded above.
- Upstream review: Wave 1 receipt records S06 PR #305 reviewed PASS
  (Muse, OCR) with local-gates PASS on merged head; S06 scanned the
  GridMarket source at its pinned commit.
- Post-vendor integrity is enforced by CMD-SPEC-VENDOR (diff -r of scripts
  and template against git archive of the D5 commit, tree-id pin in VENDORED.md).

## Static security checks

- vendor.sh (acquisition mechanism, read in full): local `git` reads
  (rev-parse, status, log, ls-tree, cat-file, show) and a local staged copy
  with mode restore; refuses on uncommitted skill changes or a diverged
  existing copy; no network, no downloads, no credential reads.
- scripts: `subprocess` used only for local `git` (vendor.sh) and local
  `dot -Tjson` layout (azdiagram/__init__.py, argv list, no shell).
- No urllib/requests/socket/http, curl/wget, os.system/popen-shell, eval/exec,
  pickle/marshal, persistence (cron/systemd/launchd), privilege changes,
  HOME/profile reads, or credential patterns.
- No absolute /home/ or /Users/ paths (consistent with merged CMD-D5-AGNOSTIC).
- Template holds placeholders only (<System>, <DOC-ID>, <Author>); figures
  are static azdiagram output for the placeholder system context.
- Unavailable checks: ClamAV/YARA, SBOM/vulnerability scanners, gitleaks
  (not installed; owner approval required to install). Plain-text Python/Markdown
  tree with the bounded greps above substituted; no packed or binary payload.

## Verdict

verdict: PASS
residual risks: scanner-tool absence noted above; post-vendor equality still
to be confirmed by CMD-SPEC-VENDOR on the committed candidate.
