# Corrected package rebind receipt

Outcome: **PASS**. Assigned role: Bearing Lite Plan Integrator; Codex CLI / GPT-6.1 Sol / high. Source candidate: `39a145c72eb93d42701328bf95228e3ad4e64f12`, branch `afc/p2-vega-primary-plan`.

The documented renderer regenerated the DoD Manifest from the corrected package. Re-embedded hashes bind the corrected technical plan, design, register and finalized SEIT. `package-freeze.json` is the house freeze output for this content. No plan semantics, control state, profiles, role routes, OCR/Reverify selections, authority, or spent review/repair limits changed. Historical delta and approval bindings remain intact.

Documentation used:

- Bearing Lite 1.1.7 `skills/planning-and-design/SKILL.md`, step 4: `node <plugin root>/hooks/plan-package.cjs <plan dir>`.
- `skills/planning-and-design/references/correction-loop.md`, step 6: re-embed artifact digests and run the normal package freeze.
- `tools/render-dod-manifest.mjs` CLI usage: `node tools/render-dod-manifest.mjs <implementation.json> [--check] [--out path]`.
- `hooks/plan-package.cjs` `verifyDigests`: SHA-256 of ordered actual planning-input hashes plus the finalized SEIT hash, joined with newlines. The rebind uses this house function rather than duplicating the formula.

For the command table, `P2=docs/plans/2026-10-12-amazon-fantasy-companion-phase-2` and `PLUGIN=$HOME/.claude/plugins/cache/bearing-lite/bearing-lite/1.1.7`.

| Command | Exit | Evidence |
|---|---:|---|
| `node "$PLUGIN/hooks/plan-package.cjs" "$P2"` before refresh | 1 (expected stale bindings) | [Before freeze](rebind-before-freeze.json) |
| `python3 "$P2/evidence/P2-VEGA-PRIMARY-plan/rebind.py"` | 0 | [Digest and structural receipt](rebind-digests.json) |
| `node "$PLUGIN/tools/render-dod-manifest.mjs" "$P2/implementation.json"` | 0 | [Renderer](rebind-render.txt) |
| `node "$PLUGIN/hooks/plan-package.cjs" "$P2"` | 0 | [Freeze](package-freeze.json) |
| `node "$PLUGIN/tools/render-dod-manifest.mjs" "$P2/implementation.json" --check` | 0 | [Byte check](rebind-render-check.txt) |
| `python3 "$P2/evidence/P2-VEGA-PRIMARY-plan/verify_delta.py"` | 0 | [Delta verification](rebind-verify-delta.txt) |
| `export PATH=$HOME/.local/share/afc-tools/backend-tests/bin:$PATH; bash tools/ci/gate.sh` | 0 | [Full gate](rebind-gate.txt) |
| Structural comparison against `39a145c` and allowed-write-set check | 0 | [Exact changed JSON paths](rebind-digests.json) |

Evidence logs replace the local home prefix with `$HOME`. The first commit hook exited 1 on PATH-HOME-POSIX in the captured logs; evidence was sanitized and re-staged before rerunning verification.

Full gate: spec, docs, hygiene and backend PASS; 61 hygiene tests and 158 backend tests passed. TV app area reports PASS because no `tv-app/` tree exists. Fatal-git and mutation/coverage GAP lines are expected negative-fixture output inside the passing hygiene suite, not failures of this package.

Candidate digest before: `3ea492c5821d3a47649cbb59428d95ba0f6409506d5901c07aaf259374ebf867`.

Candidate/freeze digest after: `fd66f4110c70da8a7bd284e8b8ff680cc0d0b9d99ca1fb0d8e0346adc59deda4`.

The pre-refresh house computation was `07c854b8aab8517ff0af4878b1a8ff912c5c1244734485c08d85c903449a4e07`; that computation used SEIT bytes with stale embedded planning hashes. The final candidate digest above uses the refreshed SEIT bytes.

| File | Before SHA-256 | After SHA-256 |
|---|---|---|
| `implementation.json` | `1c9aa87053ea39b104ef5d59ef8e12ebb25734ee3412b0f5e67816698908467a` | `a2ced13a416ab8b692dd32b3031d68b87741ad8f93e1619f61e9e27a89a21810` |
| `seit.json` | `636cf86530e32260c910fbe4bb828c547ea1486ef8d4b25718eb03d163f3fff6` | `dfc088383365aca2984d14d7e4e33a5bf05b49101c4725458ef84c6685fb3dae` |
| `amazon-fantasy-companion-phase-2-dod-manifest.html` | `b843b637cea2b9d2a29c864ce0752ea60e462fda570e9e795883b0decce6e882` | `f71d46c487c4d2e0a57b62ed5088c1ade4a06cc4401ee969f1be7d32974555da` |

Structural comparison: seven implementation digest fields and three SEIT planning-input digest fields changed; the HTML is a generated projection and the freeze changes only its digest. All other writes are confined to this evidence directory.

Recovery note: the initial receipt script exited 1 when its structural assertion caught an attempted new digest field on the correction-history row. It wrote only SEIT. Those own SEIT bytes were restored from `39a145c`, the script was corrected, and the final run exited 0. The historical proposed-delta digest is preserved. No plan-content repair was made.

Manifest text inspection found the refreshed candidate digest, `selected by DEC-AFC-SD-049`, and Fire OS secondary content. Browser visual inspection is unavailable: browser security policy rejected the local `file:` URL; no workaround was attempted. Deterministic renderer `--check` passed. BRAN: unavailable (no native `.bran/policy.yaml`). Reverify: not applicable — this packet makes no compiled-binary claim. This is mechanical author evidence, not independent planning review or acceptance.

Next action: return the committed corrected package to the controller for the second planning review. No new review or repair round was dispatched here. Push/PR and branch changes are outside this packet.
