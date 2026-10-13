# Developer feedback — Scribe session, AFC generation-1 resume (2026-10-13)

Scope: event transcription only (lease SCR-codex-resume). No product edits, no external sending.
Tracks: Fire TV track + AWS Builder mini challenge (per DEC-AFC-SD-008). No AWS services used in this Scribe session.
Field rules: evidence/devpost-feedback-rules.md (DEC-AFC-SD-025). Durations, ease-of-use, and versions are stated only where directly observed; unknowns are marked unknown.

## Product feedback: Muse Code transcription session

- Tools used and for what: this Muse Code session for read-only Scribe transcription — reads of `journey.json` (checkout_lease, decisions, execution_receipts), dispatch packets, run logs, and `evidence/B3/codex-verify/` receipts; appends to `journey.json` history and this file.
- What worked well: direct repository reads returned every cited record (lease resume marker, dispatch/return records, log tails, gate receipts); no additional tooling was needed to complete the transcription.
- What needs work: nothing observed this session.
- Onboarding (zero to hello world): no setup was needed; the control checkout was the working directory and all evidence paths resolved as dispatched.
- Would you build with this again: yes — read-only inspection plus a bounded write set sufficed for the whole task.

## Friction log

### F1 — Claude Code weekly limit blocks B2T-g2 resume

- Tool: Claude Code (frozen test_implementer primary route).
- Task: resume B2 red-test work in the B2 worktree (lease B2T-g2).
- Steps taken: dispatched per packets/B2T-g2.md on the primary route; run exited before producing artifacts.
- Expected vs actual: expected the run to resume existing B2 work; actual: exit 1 with "You've hit your weekly limit · resets 2am (America/Chicago)", nothing committed.
- Classification: verified account usage exhaustion; not a product bug.
- Severity: blocking — the primary route could not start work.
- Evidence: packets/B2T-g2-run.log (tail confirms message and exit=1); return_record B2T-g2 ENVIRONMENT_FAILURE at 2026-10-13T03:33:11Z.
- Impact: B2 test work could not proceed on its primary route.
- Workaround used: frozen first fallback — B2T-g2-codex dispatched on Codex CLI at 2026-10-13T03:33:11Z (work in flight, not complete).
- Actionable suggestion: none for the product; route-level usage budget visibility would let the orchestrator pre-emptively use fallbacks (see Feature Requests).
- Uncertainty: run duration unknown; reset time is vendor-reported, not independently verified.

### F2 — Claude Code weekly limit blocks pd-phase2-resume

- Tool: Claude Code (planning_and_design route).
- Task: resume Phase 2 Planning and Design in the phase2-plan worktree (lease pd-phase2-resume).
- Steps taken: dispatched per specialists/pd-phase2-resume.md; run exited before producing new artifacts.
- Expected vs actual: expected the run to resume existing planning work; actual: exit 1 with "You've hit your weekly limit · resets 2am (America/Chicago)".
- Classification: verified account usage exhaustion; not a product bug.
- Severity: blocking — the planning route could not start work.
- Evidence: specialists/pd-phase2-resume-run.log (tail confirms message and exit=1); return_record pd-phase2-resume ENVIRONMENT_FAILURE at 2026-10-13T03:33:11Z.
- Impact: Phase 2 planning-lead work could not proceed on its Claude route; TE planning moved to its frozen fallback while the planning-lead route awaits the owner.
- Workaround used: TE-p2-codex dispatched on its frozen fallback at 2026-10-13T03:36:09Z; owner route question pending for the planning lead (no configured P&D fallback): Codex CLI route vs waiting for the Claude reset. Asked time unavailable, not fabricated; answer pending.
- Actionable suggestion: none for the product.
- Uncertainty: run duration unknown; reset time vendor-reported; owner answer pending.

### F3 — BRAN unavailable for AFC

- Tool: BRAN.
- Task: repository context for Scribe transcription.
- Steps taken: per dispatch, BRAN has no native policy for AFC, so context was gathered by direct repository reads.
- Expected vs actual: expected BRAN-assisted reads; actual: direct reads, transcription completed without gap.
- Classification: capability unavailable for this repository; not a failure.
- Severity: non-blocking — workaround fully covered the need.
- Evidence: packets/SCR-codex-resume.md.
- Impact: none on this transcription.
- Workaround used: direct repository reads. Existing configured BRAN continues for HQ/azedge where applicable.
- Actionable suggestion: none; a native AFC BRAN policy is an owner decision, not a Scribe need.
- Uncertainty: whether an AFC policy will be configured later is unknown.

## Feature requests

### FR1 — Machine-readable usage-limit signal

- Description: usage-limit refusals should carry a machine-readable marker (distinct exit code or structured field) instead of sharing the generic failure exit with task errors.
- Why it matters: the orchestrator currently distinguishes "account exhausted, use fallback" from "task failed, repair" by matching log text; a typed signal removes that fragile parse.
- Priority: Nice-to-have.
