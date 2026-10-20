---
type: working
title: AFC R1 release-draft prerequisite checklist
okf_status: draft
---

# AFC R1 release-draft prerequisite checklist

Handoff candidate `6be1366e52b325d775cd92ffefbf02516b1b6473` on `afc/m03-m05-rw3-release-draft`. Preparation draft only. Independent acceptance is NOT claimed. R1 ships the Fire OS APK; P2-V01 (Vega) is non-gating VVD compatibility evidence. Milestones and source prerequisites are not marked complete.

| id | disposition | merge/source SHA | evidence |
|---|---|---|---|
| P2-L01 | SATISFIED_HISTORICAL_DELIVERED | 4994aad44ace64f3c9434f73461f3fe2d12f694b | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/` |
| P2-X01 | SATISFIED_HISTORICAL_DELIVERED | c194deefe0273f76d4a1e430de94a4c7a163aad2 | `spikes/sp1-device/VERDICT.md` |
| P2-X05 | SATISFIED_CHECKPOINT_ONLY (CP-X05-HIST); live closure is RW2, not an R1 prerequisite | 42b8be9899f7c12d94e2dd5b38f2e86815a4c7d9 | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-X05/` |
| P2-D01 | SATISFIED_HISTORICAL_DELIVERED | d86daa46fafb278f834fe395141a433b214a6989 | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-D01/` |
| P2-G01T | SATISFIED_HISTORICAL_DELIVERED | 71a99e7b4185d11f4cb422484ca495be2ba22d43 | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01T/` |
| P2-G01 | SATISFIED_HISTORICAL_DELIVERED | 71a99e7b4185d11f4cb422484ca495be2ba22d43 | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-G01/` |
| P2-A01T | SATISFIED_AUTHOR_EVIDENCE_ONLY (host/fixture checks; DEVICE-1 author PASS, independent acceptance not established) | 0c273e5d7539f17b6995c9b36f748155d77208da | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-A01T/` |
| P2-A01 | BLOCKED: DEVICE-1 author completion (SHA 0bab5002...) and addendum (SHA 52347a3e...) PASS; independent acceptance not established | 0c273e5d7539f17b6995c9b36f748155d77208da | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-A01/` |
| P2-B01T | SATISFIED_HISTORICAL_DELIVERED | 75afca022f967945a70bf715beb2a7c98e65ed9d | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01T/` |
| P2-B01 | SATISFIED_HISTORICAL_DELIVERED | 75afca022f967945a70bf715beb2a7c98e65ed9d | `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-B01/` |
| CP-X05-HIST | SATISFIED_CHECKPOINT (live-prep SHA 93c4a617d7298e5f62965c6b05b2c234441d9424fdb14374de422dc9c30f8fe7) | n/a | `recovery-m03-m05/evidence/live-prep/receipt.json` |
| P2-V01 | NON-GATING compatibility evidence (physical Vega NOT_APPLICABLE, not PASS); recorded state: Vega CLI 1.4.5 INDETERMINATE/NOT_ADMITTED; SDK/RN/OS pins unmaterialized; no physical Vega target or V01T entry evidence | none | `recovery-m03-m05/vega-cli-static-closure-consumption.json; coordinator-rw3/vega-prerequisite-integration.json; coordinator-rw3/sdk-metadata-integration.json` |

## Blockers

- P2-V01 (Vega CLI admission, SDK pins, physical target) is reported with the release and does not gate R1; physical Vega checks are NOT_APPLICABLE, never PASS.
- Independent acceptance: RW1 review running on separate read-only landing; RW3 review 0/1 unused.
- Tag target null; no tag created. Publication excluded.
