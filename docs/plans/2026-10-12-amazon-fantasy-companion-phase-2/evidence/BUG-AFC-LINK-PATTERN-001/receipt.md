# BUG-AFC-LINK-PATTERN-001 — implementation receipt

- Outcome: PASS for the assigned implementation packet; author diagnostics only.
- Binding: `bug-triager` Implementer, Codex CLI / GPT-6.1 Sol / high;
  branch `afc/bug-link-pattern`, baseline `2d973bd66182364a69b5a3088286e88c08f1107d`.
- Scope: `link.html`, one new backend unit test, this evidence directory and
  `CHANGELOG.md`. No remote writes, branch changes, deployment or real AWS calls.

## Reproduction, origin and escape

Product UI validation defect B-1, introduced by `9cd216c` (P2-B01).
The page's `[A-Za-z0-9_-]{1,64}` is invalid in JavaScript Unicode Sets (`v`)
mode; the unescaped literal hyphen prevents client-side pattern enforcement.
The existing server-side `re.fullmatch` validation remains unchanged.
Earlier tests covered server rejection and the page's CSP, but never compiled
HTML pattern attributes under the browser's `v` rules. This is an expected red
regression on the pinned baseline, not a harness/configuration failure.

## Red, green and prevention

Method: test. `backend/tests/unit/test_link_patterns.py` extracts every pattern
attribute with `HTMLParser`, compiles each with Node's real `RegExp(..., "v")`,
and compares whole-value profile ID matches with `[A-Za-z0-9_-]{1,64}`.
Its 136 samples cover every ASCII character, empty input, lengths 64 and 65,
mixed allowed characters, slash, trailing newline and non-ASCII input.
Node `v22.23.3` and Python `3.12.3` were used; Node with `v` support is required,
and unavailable tooling fails rather than skipping the regression.

All Python/gate commands below used
`PATH=$HOME/.local/share/afc-tools/backend-tests/bin:$PATH`.

| Check / command | Exit | Evidence |
| --- | --- | --- |
| Red: `python3.12 -m pytest backend/tests/unit/test_link_patterns.py -q` before the HTML edit | 1 | `1 failed`; `SyntaxError: Invalid regular expression: /[A-Za-z0-9_-]{1,64}/v: Invalid character in character class` |
| Green: same test plus `backend/tests/unit/test_router.py::test_link_page_is_framed_by_strict_headers` | 0 | `2 passed` |
| `bash tools/ci/gate.sh` | 0 | spec, docs, hygiene, tvapp and backend PASS; 61 hygiene tests and 377 backend tests passed; no tv-app tree |
| Five consecutive focused runs, then two concurrent focused copies | 0 | Each run: `1 passed`; no shared resources, network or service |
| Inline-script comparison against baseline and CSP digest assertion | 0 | Script bytes unchanged; `sha256-r5vvOH35j5Xp1ecjHhZ7oNRmS7/Xlp/C7RNPviHqeT8=` verified |
| `git diff --check` | 0 | No whitespace errors |

Fix: escape only the literal hyphen in the HTML attribute to
`[A-Za-z0-9_\-]{1,64}`. The script, CSP and server validator are unchanged.
The regression is collected by the existing backend gate and prevents the same
invalid-pattern escape. Its measured test call cost was about 0.02 seconds;
no package, fixture or gate configuration changes were needed.

## Handoff

The Unreleased / Fixed changelog entry contains the authorized `(PR #TBD)`.
Next action belongs to the orchestrator: independent review and any configured
OCR/Reverify, then landing. Those capabilities and live Chrome/browser QA were
not run by this implementer; these diagnostics do not establish assurance.
BRAN is unavailable because this repository has no native policy; evidence came
from source, history and local execution. No existing data requires recovery.
