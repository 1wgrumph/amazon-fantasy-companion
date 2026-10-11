# Specialist route receipts — AFC-2026-10-11 Planning and Design

Routes come only from `journey.json` `profile_selection.frozen_snapshots.primary`
(planning profile `primary`, configuration_digest_sha256
`b81a141be5b9d83cbecbb34df460b0f25929c2ae0df165f16ff529acfc50bafa`). Each
specialist is a separate CLI process launched with full-bypass permission flags
and stdin closed (`< /dev/null`); the Planning and Design node waits for each
to exit. Start times are UTC (`*-start.txt`); logs are `*-run.log` here.

Planning and Design node: Claude Code / Claude Opus 5.5 (this session), not a
specialist route.

## Verified unavailability

| Route | Evidence | Window | Consequence |
|---|---|---|---|
| Muse Code / Muse Spark 1.3 / max | `sm-muse-429-run.log`: `API error 429 ... Subscription quota exhausted. Your usage window resets at 2026-10-12T00:00:00Z. (rate_limit_error)`, exit=1 | until 2026-10-12T00:00:00Z | Every planning role whose frozen primary is Muse activates its first approved fallback (owner-stops class B) until the window resets. |

## Runs

| Specialist (session) | Frozen primary | Effective route (ran) | Invocation | Start (UTC) | Result |
|---|---|---|---|---|---|
| Systems Modeler (planning) | Muse Code / Muse Spark 1.3 / max | none (429) | `muse exec --model muse-spark-1.3 --reasoning-effort max --workspace <PLANNING_WORKTREE> --yolo --prompt-file specialists/sm-prompt.md` | see `sm-start.txt` | FAILED: quota exhausted (above) |
| Systems Modeler (planning) | Muse Code / Muse Spark 1.3 / max | fallback 1: Claude Code / Claude Opus 5.5 / high | `claude -p --model claude-opus-5-5 --effort high --dangerously-skip-permissions` | see `sm2-start.txt` | pending |
