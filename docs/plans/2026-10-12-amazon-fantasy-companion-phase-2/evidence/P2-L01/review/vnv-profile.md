# VnV Review Profile

**Scope:** commits=88db101edb61a08dedea8037e4e9207d262a7e0f..1d706270ea05f1c658df2ff8eef32762c900928b — 23 files, 2 commits.
**Generated:** 2026-10-13T17:11:28.226386+00:00.

## Subsystem map

| Subsystem | Files |
|---|---|
| CI/CD | `CHANGELOG.md`, `docs/plans/2026-10-11-amazon-fantasy-companion/journey.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/.gitignore`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/date-fix-after.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/date-fix-before.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/date-fix-packet.md`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/date-fix-probe.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/date-fix-receipt.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/date-red-packet.md`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/date-red.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/date-triage.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/issue-metadata-inspection.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/lease.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/owner-approval.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/packet.md`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/parent-receipt.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/preflight-initial-apply.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/preflight.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/progress.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/readback.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/tracking.py`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/verification-plan.json`, `docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/P2-L01/worker-stop.json` |

## Must-run commands

### CI/CD

- `tools/ci/gate.sh docs hygiene`

Packet also requires `TMPDIR=/var/tmp/az bash tools/ci/gate.sh`. Both passed with `PYTHONDONTWRITEBYTECODE=1`.

## Optional deeper tools

No SECURITY_TOOLS.md, PERFORMANCE_TOOLS.md or SEO_GEO_CHECKLIST.md is declared in this guidance root; no tool catalog inferred.

## Threat-model prompts

- GitHub tracking integration: do exact approval, payload identity, private target, permissions, policy scope and duplicate guards precede each authorized creation flow, and can verify remain GET-only?

## Findings target

- CI/CD findings → repository issues with existing `vnv` label per guidance; this packet prohibits issue mutation, so retain any findings in the active review receipt.
- No unmapped paths.

## VnV rules in force

1. Preserve raw SARIF unchanged.
2. Findings format: rule_id | path | severity | status | date; attach reproducer and candidate identity.
3. Sanitize findings and reports; no credentials, account details, local home paths, proprietary prompts, model names or scoring formulas.
4. Bind evidence to the exact candidate and distinguish author checks from independent review.
5. Preserve OCR delegation and Reverify dispositions; unavailable is a typed gap.
6. Preserve contract-first gates, failure propagation, documentation links, hygiene and owner boundaries; guidance grants no deployment, activation or publication authority.

## Evidence routing

- **Guidance root:** `docs/vnv`
- **Evidence root:** none declared; sanitized receipts in the active review output. Raw logs remain outside the repository.

---

## Notes

- Status: PROFILE. Scope was clean before review artifacts were created.
- Read index and all three immediate area AGENTS.md files in declared order. CI/CD owns all changed paths, including the .gitignore under docs.
- BRAN unavailable: no native policy. No unmapped warnings.
