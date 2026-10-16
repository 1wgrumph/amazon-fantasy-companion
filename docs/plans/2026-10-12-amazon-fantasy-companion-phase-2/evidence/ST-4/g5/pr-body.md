## What changed

- Add the AFC architecture specification with the approved SD-035 product decisions and SD-036 future discussion, retaining all 66 requirement UIDs and the three withdrawn trace entries.
- Publish draft revision 0.3 with clickable document, issue, scope-decision and section references; render linked changed-section and PR/diff records for revisions 0.2 and 0.3.
- Vendor the authoring tools from reviewed Alphazedehq revision `04678835350b529b44ab69ee5f805ca21cab5e76`, including linked Appendix A traces and corrected heading anchors.
- Add PR #10 and dated merged history to the changelog while preserving PR #14's gate-fix entry.

## Why

The owner's ST5-F1/F2 approval conditions require readers to follow references and identify each revision's changes. This amendment preserves the approved product text at `771c289`; only links and revision/provenance metadata change. The content already received generation-3 review; the link/revision amendment awaits one independent delta review.

## Validation

- `bash docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g5/vendor-check.sh` — exit 0; exact reviewed source bytes, file modes, tree and MIT notice verified. Supply-chain admission PASS; redacted secrets scan clean.
- `bash docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g5/verify.sh` — exit 0; both builds and byte comparison, specification lint, figure lint, printed-label scan and private-path scan pass.
- `python3 docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/ST-4/g5/check-links.py` — exit 0 within the verification runner; 184 source links added, 749 relative links/anchors resolved, 66/66 UIDs, all 66 Appendix A rows linked.
- `bash tools/ci/gate.sh` — exit 0 within the verification runner; spec, docs and hygiene pass, including 39 tests. Normal commit hooks also run the gate.

## Residual risk

This is author verification, not independent assurance or product acceptance. Leave this PR unmerged for the independent amendment review. OCR delegation is selected and required for that reviewer; it was not run by this author. Reverify is enabled but not applicable: no compiled binary claim. BRAN is unavailable because the repository has no native policy. No host-bound Requirements System review is requested or claimed.

An initial build rejected the generated Appendix A heading in the revision's source-section list; the record now describes that generated change in its summary and lists valid source sections. The corrected full verification passes. PR #11 remains open and is not represented as merged history.

Remaining product obligations include Phase 2 contracts and model alignment, provider/device evidence and owner prerequisites already documented in the specification. Issue #1 stays open. No release, tag, runtime activation or public export is performed. Exact commands, prior provenance and developer feedback are in the ST-4/g5 evidence directory.
