# P2-D01 inspection record: AC-AFC-P2-VNV-01

Slice P2-D01 (issue #17). Baseline origin/main 4994aad44ace64f3c9434f73461f3fe2d12f694b.
Branch afc/p2-d01. Method: inspection plus CMD-GATE-DOCS. Author record only;
this is not independent review or assurance.

## Checklist

| Item | Observation | Result |
|---|---|---|
| `docs/vnv/tv-app/AGENTS.md` exists | added | PASS |
| `docs/vnv/backend/AGENTS.md` exists | added | PASS |
| `docs/vnv/device-integration/AGENTS.md` exists | added | PASS |
| Each new area has Scope, Tools, Review Focus, Findings target headings | checked by `check_docs.py` DOC-HEADING rule; all three pass | PASS |
| Index `docs/vnv/AGENTS.md` lists the three areas | entries 4 to 6 with relative links | PASS |
| Index links resolve | `check_docs.py` DOC-LINK rule; no failure | PASS |
| CI/CD scope excludes the new `docs/vnv/<area>/**` paths | exclusion list updated | PASS |
| Negative case: heading removed from an area fails the gate | `## Review Focus` renamed in backend area: `docs/vnv/backend/AGENTS.md:1:DOC-HEADING`, `gate: docs: FAIL check exit 1`, exit 1; file restored | PASS |
| No absolute home paths in `docs/vnv/` | grep for `/home/` and `/Users/`: none | PASS |

## Commands

| Command | When | Exit | Output |
|---|---|---|---|
| `bash tools/ci/gate.sh docs` | baseline, before edits | 0 | `gate: docs: PASS checks completed` |
| `bash tools/ci/gate.sh docs` (CMD-GATE-DOCS) | candidate, new files staged | 0 | `gate: docs: PASS checks completed` |
| `bash tools/ci/gate.sh` | candidate | 0 | spec PASS, docs PASS, hygiene PASS (39 unit tests OK) |
| `bash tools/ci/gate.sh docs` | negative case | 1 | `docs/vnv/backend/AGENTS.md:1:DOC-HEADING` |
| `bash tools/ci/gate.sh docs` | after restore | 0 | `gate: docs: PASS checks completed` |

## Input digests (sha256, candidate working tree)

```
181a38c9b8c654a1c96f18fffec6d7ea408febd74c8ecd9182f9e98942997e7f  docs/vnv/AGENTS.md
492f02cc571f8cd6e50d538ad95d9fabb4bd4e69d808b1991c3870a8a259ba15  docs/vnv/ci-cd/AGENTS.md
08ffa7c8ecfb912ac39cbf8db4907bf04836950ad228fc3239c4143b81b17f84  docs/vnv/tv-app/AGENTS.md
ffdefbfe0fce2f006a6ce07bed2d823878e0415c06fee17b19ec7314e19a3850  docs/vnv/backend/AGENTS.md
57113fd36e4197418c37cf7fbadcb1c8b1ef586a6fb6f4bbe356ded52cbe31ca  docs/vnv/device-integration/AGENTS.md
bafe1badd3fa87ca4359af8f126ad0ab2313726b4c70b169c28197fd4d9c2e2c  tools/ci/check_docs.py
392594299cfaceb9b4c90a9c1eca076e45999d0a4a8758796d0bec577cfb076b  tools/ci/gate.sh
```

Reverify: not applicable. This slice changes guidance documents; no binary is built or claimed.
