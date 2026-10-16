# B1T-g1 red receipt
- lease: B1T-g1; branch afc/b1-hygiene-colon-leak; base 17b40b4bdf8214b300bee05d594e13100d5d0d93
- head: 41fa6e3aed774f0822b1555f994c9138f1a1fc0c
- test: tools/ci/tests/test_gate.py::AC_AFC_CI_01::test_hygiene_whitespace_finding_does_not_echo_colon_shaped_line_text
- sha256(test_gate.py): 9d430a2f7de753f57c0efc37e4e38c8fa7ee40e18e4803bbf00c280d7c320545
- command: env -u GIT_INDEX_FILE -u GIT_DIR python3 -m unittest discover -s tools/ci/tests -v
- result: Ran 35, FAILED (failures=1) — only the new test; AssertionError (not error). Full log: B1T-g1-red-run.txt (token redacted in-test, 0 raw token matches in log).
- failure text (token redacted):
  AssertionError: True is not false : hygiene output echoed colon-shaped staged line text:
  +<token>:123:WS-CHECK
  notes.md:2:WS-CHECK
  gate: hygiene: FAIL check exit 1
- rc assertion (exit 1) held; the leak is the extra "+<token>:123:WS-CHECK" record from a diff content line.
