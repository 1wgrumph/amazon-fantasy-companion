# S09-r1 R2 repair evidence (lease S09-r1)

Fix: tools/ci/gate.sh hygiene whitespace check parses `git diff --check`
into `file:line:WS-CHECK` lines via sed + sort -u; never echoes line text.
Unparseable git errors fail closed (return 1, no PASS).

## VERIFY (all exit codes observed this session)

- `env -u GIT_INDEX_FILE -u GIT_DIR python3 -m unittest discover -s tools/ci/tests -v`
  exit 0, 34 tests OK (includes
  test_hygiene_whitespace_finding_reports_rule_ids_without_line_text).
- `bash tools/ci/gate.sh` exit 0; `bash tools/ci/gate.sh --changed` exit 0
  on the clean tree.
- Throwaway repo, staged trailing-whitespace file named `note file.md`
  (path with spaces): raw `git diff --check` exit 2 printing `+trailing`;
  gate hygiene exit 1 printing only `note file.md:2:WS-CHECK` plus the
  `gate: hygiene: FAIL` line.
- Throwaway repo with unborn HEAD (`git diff --check` exit 128
  `fatal: bad revision 'HEAD'`): gate hygiene exit 1, no PASS, no echo.
- `git diff --check` clean; `shellcheck tools/ci/gate.sh` clean.
- `core.hooksPath` confirmed unset; left unset.

## Assumptions resolved

- Paths with spaces: handled (`[^:]*` matches spaces); proven by probe.
- Git error output: not swallowed; any nonzero git rc returns 1.

## Remaining risk

- Filenames containing a literal colon remain ambiguous in
  `file:line:rule-id` parsing (git's own `path:line:` format shares this).
