ROLE
Light Implementer P2-L01-g1. Frozen opensource-hackathon primary Muse Code / Muse Spark1.3 / xhigh; exact --contributor-mode on required. No nested agents or coordinator. Load $HOME/.codex/plugins/cache/bearing-lite/bearing-lite/1.1.7/skills/light-implementer/SKILL.md.

STATE
Cwd is approved tracking worktree, branch afc/p2-l01-tracking, baseline88db101edb61a08dedea8037e4e9207d262a7e0f (PR15 merged; head a7a16570c376222635f48a6702cd0e3eca694493). PLAN=docs/plans/2026-10-12-amazon-fantasy-companion-phase-2; OUT=PLAN/evidence/P2-L01. Exact current owner 'approved' is recorded in OUT/owner-approval.json as DEC-AFC-P2-APPROVAL-001. This authorizes PRIVATE GitHub tracking creation after landing only; no product execution. Read OUT/lease.json and approval. Full frozen profile SHA7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1; payload SHA f0b8d5bf26d3959948e65960fc2b06525a96f964ab3454633eb6c1aaeab9acdb. No live profile reads.

OBJECTIVE / EXACT RUNBOOK
Execute the prepared immutable driver, no authoring/choices: OUT/tracking.py SHA256 c0e58de95de3e31cd04ad7f92837628ce9ebbac1940eabebabcd0874c40e8051. It implements approved CMD-MILESTONES-CREATE/READBACK and PROC-TRACKING-SETUP, with action-time target/permission/label/helper-policy/duplicate checks, then13milestones and39issues in milestone/sequence order, then approved dependency-link substitutions and complete readback. Current helper scope excludes this personal repo; script refuses if that changes (native branch only). CLI create uses exact approved title/body/label/milestone; REST PATCH is the equivalent native metadata reconciliation for dependency links, no creation-policy bypass. No blind retry after error.
1. Verify cwd branch and baseline ancestor, exact driver hash, lease identity, approval/payload identities. If mismatch stop WAITING_ON without writes.
2. `python3 {OUT}/tracking.py preflight` (exit0 required, no remote mutation).
3. `python3 {OUT}/tracking.py apply` (approved remote mutation; exit0 required).
4. `python3 {OUT}/tracking.py verify` (read-only GitHub; exit0 required).
5. Write OUT/worker-receipt.json with exact commands/exits, driver/payload hashes, counts13/39/52/13, receipt pathreadback.json, issue/milestone URL range, and developer_feedback. Deterministic evidence is diagnostic/inspection, not independent review.
Use the literal PLAN path in commands; braces are path notation only. No source code or script edits. All runtime proofs stay not_run. Keep every work issue OPEN, including L01, X05 and conditionalX11; parent handles receipt review/landing/eligible closure. Owner issue#1 staysopen.

AUTHORITY
Write only OUT/** receipts/progress/lock; never edit tracking.py, owner-approval.json, lease.json, .gitignore or approved payload/bodies. Remote scope only github:1wgrumph/amazon-fantasy-companion exact13milestones39issues and approved bodylinks. No commits/pushes, branchchanges, issueclosure, publicvisibility/tag/release/publication, credentials/device/AWS/product/runtime actions. GitHub authentication uses existing CLI integration; no credential values read.

VERIFY / STOP
On any commandfailure or uncertainty STOP with safe error and progressfile; do not retry creation, repair code, choose another route or make policy decisions. No fallback absent confirmed usage/rate limit; configuration/auth/runtime errors preserve selected route. Print CANDIDATE_READY or typedgap with artifact path. Time bound20min.
Reverify not applicable: tracking metadata only. OCR applies to subsequent independent receipt review; not this mechanical execution. Product implementation budgets untouched.
BUG_ROUTE: not-a-bug owner-approved tracking setup, not a product repair.
