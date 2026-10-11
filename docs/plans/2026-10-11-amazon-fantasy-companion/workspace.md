# Workspace Environment: Amazon Fantasy Companion: architecture, program plan, milestones

Observed 2026-10-11 by Architectural Alignment (Bearing Lite, Claude Code).
Repository map: [`repository-map.md`](./repository-map.md).

## Repository Identity
- Root: `$HOME/alphazede/worktrees/amazon-fantasy-companion-planning`
  (linked worktree of `$HOME/alphazede/Hackathons/amazon-fantasy-companion`)
- Remote: `github:1wgrumph/amazon-fantasy-companion` (private)
- Plan directory: `docs/plans/2026-10-11-amazon-fantasy-companion/`
- Confirmed by: DEC-AFC-001 (`journey.json`)

## Mapped Inputs
- `README.md`: product one-liner; status "planning"; intent tracked in issue #1;
  architecture/program plan/milestones land under `docs/plans/`.
- `.gitignore`: ignores `node_modules/`, `.env`, `.env.*` (keeps `.env.example`),
  `*.log`, `.DS_Store`, `build/`, `dist/`.
- `docs/plans/2026-10-11-amazon-fantasy-companion/journey.json`: lifecycle id
  AFC-2026-10-11, deadline `2026-10-23T19:00:00Z`, intake accepted.
- Issue `1wgrumph/amazon-fantasy-companion#1`: product intent (supplied in packet;
  not re-fetched).

## Observed Systems
- None. No product code, manifest, task runner, CI entrypoint, test config, or
  repo-level `AGENTS.md`/`CLAUDE.md` exists at depth 2.

## Constraints and Git Boundaries
- Branch / Worktree: `plan/2026-10-11-amazon-fantasy-companion` at `2c13a6b`
  (dirty: `?? docs/` — the uncommitted plan directory only).
- `main` is PR-only by convention; rulesets return HTTP 403 on this private
  free-tier repo, so it is not enforced (DEC-AFC-002).
- `.gitignore` `*.log` ignores `specialists/intake-run.log` and
  `specialists/aa-run.log` (verified `git status --ignored`); `journey.json`
  cites `specialists/intake-run.log` as evidence, so it will not be committed
  without `-f` or a `.gitignore` change. Orchestrator decision; unchanged here.
- Rules: workspace `AGENTS.md` cross-repo rules (no AI co-author lines, secrets
  out of commits, worktrees under `worktrees/`, never squash-merge, OCR +
  Reverify on reviews, visual review for UI changes, ≤5 implementation agents).
  No repo-level rule file exists.
- Deadline: Devpost submission **2026-10-23 12:00 PM PDT** (19:00Z).
- Excluded scope (owner, 2026-10-10): messenger, message boards, community
  rooms, shared chat, watch-party social features.
- Performance boundary (owner): design lightweight; no hardware benchmark gate,
  no measured-device latency/RAM claims.
- Publication/submission/external feedback: owner-authorized only.
- Scribe `developer_feedback` contract: every dispatch packet and return carries
  a `developer_feedback` section (observation IDs/evidence, or an explicit "no
  new observations" naming tools exercised). Lifecycle must allocate a private
  observation log, per-tool summary, and sanitized friction log; paths not yet
  assigned.

## Validation Commands [observed, not run]
- Test: none observed (no anchor file).
- Lint: none observed (no anchor file).
- Build: none observed (no anchor file).
- Candidate starter commands are recorded per repo in `repository-map.md`
  (source: upstream READMEs) [observed, not run]; none apply until a starter is
  selected and imported.

## Unknowns
- **Architecture gap:** no existing architecture covers any affected scope.
  Systems Modeler must be activated; this node does not design.
- Starter repository selection (7 AmazonAppDev candidates; Scope Definition
  owner decision).
- Target OS/device: Fire OS (Android) vs Vega OS (React Native/VPKG), or both.
  Owner's ~2018 Fire TV model and OS unconfirmed. Reference tiers: Fire TV Stick
  4K 1st Gen (Fire OS 6, 1.5 GB), 4K Max 2nd Gen (Fire OS 8, 2 GB), 4K Select
  2025 (Vega OS 1.1, 1 GB), 4K 3rd Gen 2026 (Vega OS 2.0, 1 GB).
- Backend hosting/runtime for event ingestion and matching: unselected.
- Yahoo Fantasy API access: unapproved. NFL/live-event feed: unselected/unverified.
- Simultaneous panel + third-party video composition route on the target OS:
  unverified (owner requires precise limitation if unsupported).
- Provider deep-link contract for one real viewing provider: unidentified.
- Local tooling: `adb`, `vega`, `emulator`, `sdkmanager`, `avdmanager` absent from
  PATH per issue #1 (not re-checked here).
- Whether ignored `specialists/*.log` evidence should be tracked.

## Map Freshness
- Tier 1: Recorded root and plan directory match confirmed inputs (DEC-AFC-001).
- Tier 2: `git status --porcelain` at observation showed only `?? docs/`; mapped
  inputs `README.md`, `.gitignore` unmodified at `2c13a6b`.
- Note: Does not detect committed changes postdating this observation.
