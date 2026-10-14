# BUG-AFC-B03-STUBPIN-001 repair receipt

Outcome: **REPAIRABLE_FAILURE**. The authorized lineup pin retirement is complete and the full gate is green. Formal mutation acceptance remains a typed GAP and B03 is not fully accepted.

Assigned route: Codex CLI / GPT-6.1 Sol / high, bug-triager Implementer. Authority: owner packet and DEC-AFC-SD-046. Baseline: `26656b7ad7c911edecba0ab364b41c2d692f55f0`. Green candidate: `d729f83f706031ab3f7835181bb94e9a31fc2568` on `afc/p2-b03`.

Origin: P2-B01 pinned all future modules as stubs, while the P2 write sets omitted ownership of retiring those pins. Escape: no stub-replacing slice had run before B03; the frozen B03T suite alone did not exercise the older pin tests. This is a plan defect repaired only in tests.

Removed exactly the lineup STUBS row and lineup contract parametrize entry. B02 and B04–B07 entries remain byte-for-byte represented in the same order; the prevention script checks both inventories against the baseline. No backend product code, other tests, tools, workflows or changelog were edited.

| Acceptance | Result | Evidence |
| --- | --- | --- |
| Only lineup pins retired | MET | Two-entry diff; [prevention.py](prevention.py) |
| Baseline red → candidate green | MET: gate exit 1, exactly 2 failed/273 passed → exit 0, 273 passed | [Red](red-gate.txt), [green](green-gate.txt) |
| Other stub pins still reject realization | MET: B02 scratch experiment exit 1, both expected failures; checker exit 0 | [Result](prevention-result.json), [output](prevention.txt) |
| Full gate exit 0 | MET: spec/docs/hygiene/backend PASS; tvapp no tree | [Green gate](green-gate.txt) |
| Coverage ≥90% | MET: formal PASS 100%, 135 changed executable lines; exit 0 | [Command](formal-coverage.txt), [native result](../P2-B03/stubpin-repair/coverage/coverage-result.json) |
| Mutation ≥70% formal PASS | UNMET: formal GAP, exit 3 | [Command](formal-mutation.txt), [native result](../P2-B03/stubpin-repair/mutation/mutation-result.json) |
| Frozen B03T hashes | MET: verify_receipt.py PASS, 11/11 files unchanged | [Hashes](frozen-hashes.json) |
| Receipt append and bug receipt | MET | [B03 receipt](../P2-B03/receipt.json), this receipt |
| Commit hooks ON | Candidate MET: pre-commit gate exit 0; evidence-commit result reported in worker return | [Candidate commit](candidate-commit.txt) |

Exact commands, PATH bindings, exit codes and artifacts are recorded under `stubpin_repair.commands` in the B03 receipt. Coverage and mutation use slice base `1ac5846`. Every heavy command is bounded by `timeout 1500`. The mutation wrapper's unchanged calibration is `timeout_constant=5.0`, `timeout_multiplier=30.0`; no timeout adjustment was needed. Existing mutmut-backend 3.8.0 and its installed backend dependencies were used; no installations.

The mutation engine completed: 344 killed / 436 total, 92 survived, 0 timeouts (raw 78.90%). The formal evaluator refuses to score because the changed module-level `PRESET_LABELS` and `DEFAULT_SETTING` in `backend/src/lineup/__init__.py:11–12` have no mutant binding. The raw score is diagnostic evidence and **not formal PASS**. The [92 survivor IDs](../P2-B03/stubpin-repair/mutation/survivors.txt) and complete native inventory are retained. A product or mutation-tool repair needs a separate bounded packet because both write sets are prohibited here. No workaround, score substitution or product edit was attempted.

Ordering correction: the unchanged mutation wrapper archives committed `HEAD`, so the two test changes were committed with hooks enabled after green and prevention checks, before coverage/mutation. Evidence is committed afterward with hooks enabled. No branch switch, reset, amend, push or PR.

These are author verification receipts, not independent review or assurance. OCR coverage assistance is not_run and remains allocated to orchestrator review. Reverify: not applicable — no compiled-binary claim. BRAN: unavailable — no native policy. Deployed/AWS tests and publication were outside this packet. Generated untracked `__pycache__` directories are removed before return.

Evidence-log correction: the first evidence commit was rejected by pre-commit WS-CHECK at two trailing-whitespace lines in the saved red traceback (exit 1; backend 273 passed). Only trailing whitespace was stripped from that log; outcomes and failure IDs are unchanged. The commit is retried with hooks enabled.

The second evidence-commit attempt was rejected for absolute home paths emitted by native pytest/coverage tools (PATH-HOME-POSIX; backend 273 passed). Log home prefixes were replaced by `$HOME` and the coverage XML source root normalized to `.`; source bindings and outcomes remain intact. The coverage evaluator is rerun on that normalized XML before another hook-enabled commit.
