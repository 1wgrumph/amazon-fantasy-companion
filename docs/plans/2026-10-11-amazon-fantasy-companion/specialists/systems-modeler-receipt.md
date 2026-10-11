# Systems Modeler receipt: AFC-2026-10-11, run 2

- **Outcome:** READY
- **Verdict:** VIEW_EMITTED. Mode is `diagram-assisted` with `sysml_claim: false`. All four views pass the model quality gate for that mode (GATE_PASS). The placement receipt is complete, and every planned component has a path and either an anchor or `new`.
- **Role:** Bearing Lite Systems Modeler (planning session). Skills loaded: `bearing-lite` 1.1.6 `skills/systems-modeler/SKILL.md` and `~/.agents/skills/sysml-modeling/SKILL.md`, with its references `mbse-method.md`, `model-quality-gate.md` and `engineering-methods/references/standards-receipts.md`.
- **candidate_ref:** branch `plan/2026-10-11-amazon-fantasy-companion` at `2c13a6b`, plus the untracked plan directory `docs/plans/2026-10-11-amazon-fantasy-companion/` (PLAN below).
- **External snapshots read (gh api, read-only):**
  - `AmazonAppDev/hello-world-fire-tv` tree `50108f4f`, branch `main`.
  - `1wgrumph/gridmarket` tree `99eb98e7`, branch `main`.
  - Local read of `alphazede/Alphazedehq` at `47c46f2` (`main`).
- **Decisions honoured:** DEC-AFC-SD-013 is SUPERSEDED by DEC-AFC-SD-022. Nothing in these outputs copies the GridMarket kit as-is. D5 is modeled as the shared, generalized skill.

## changed_paths (all under PLAN; nothing else was edited)

| Path | Basis |
|---|---|
| `views/v1-context.mmd` | Run-1 draft, re-checked against the current decisions. No SD-013 dependency, so it is unchanged. |
| `views/v1-context.svg` | Same |
| `views/v2-use-cases.mmd` | Run-1 draft, plus the item-6 note on voice announcements (only if Alexa is verified, C8) |
| `views/v2-use-cases.svg` | Same |
| `views/v3-operational-flow.mmd` | Run-1 draft, re-checked and unchanged |
| `views/v3-operational-flow.svg` | Same |
| `views/v4-delivery-tooling.mmd` | New. It replaces run-1 `v4-cicd-gate`, adds the D5 lane (SD-022), the shared hook script path, and the Vnv fallback, and no longer shows REFUSED_NO_VNV leading to merge. |
| `views/v4-delivery-tooling.svg` | New |
| `views/views.json` | New: DEC-EMV-021 metadata plus SVG sha256 |
| `specialists/systems-modeler-receipt.md` | This file |

No commits, pushes, branch operations or GitHub mutations were made.

## Checks run

| Check | Result |
|---|---|
| SVG sanitizer self-check (python3 `xml.etree`): allowed tags and attributes only, double-quoted values, allowed entities only, `<title>` present, < 60 KB | PASS on all 4 (sizes 10847, 7443, 12568, 11964 bytes) |
| Forbidden markup (`<style`, `<script`, `<foreignObject`, `style="`, `href=`, `xlink:`) | 0 hits in all 4 |
| XML well-formedness | PASS on all 4 |
| Absolute user-home path, detected by shape (Linux, macOS and Windows home prefixes) in the .mmd and .svg files | 0 hits |
| sha256 (`sha256sum`) compared with `views.json` `svg_sha256` | Match (table below) |
| `views.json` parses (`python3 -m json.tool`) | PASS |
| Visual render at 1000 px | **Not run (typed gap).** No SVG rasterizer or `mmdc` is installed here. Layout was checked by coordinate review and per-line text-width estimates. Four V4 lines were shortened to fit their boxes. |
| Mermaid syntax render | **Not run (typed gap).** `mmdc` is absent. The external Mermaid validator was not used, so that unpublished plan content was not sent off-host. |
| Requirements System checker (model-quality-gate "Checker run") | **Not applicable.** No model scope is registered, and no REVIEW_READY claim is made about a model. These are explanatory diagram-assisted views. |

| View | SVG sha256 |
|---|---|
| MODEL-AFC-V1 | `ab6bf7a466e6936f17d24008d887ff02341e4f1eb8824b0e7e473fd01814996e` |
| MODEL-AFC-V2 | `e9f366139a6539d46ac162d9d3ebf67e8924fa4626941814a270bb4c4223bdc4` |
| MODEL-AFC-V3 | `cd71a995c30370f3ef26d744b74475d671d53228a2e4fc9aba9f8e0e74941e9b` |
| MODEL-AFC-V4 | `2ac3e16ef548623255c8724144c9a1b38f95187965ccf992f67b2fbf0891ef3b` |

**LOOP record:**

1. The first forbidden-token regex flagged the words "description" and "subscriptions" in text content.
   - Classification: tool (my self-check was over-broad).
   - Changed hypothesis: scope the check to tags and attributes. It was re-run and passed.
2. The first `views.json` write failed with `FileNotFoundError` because the shell's working directory had persisted into `views/`.
   - Classification: environment.
   - Re-run from the plan directory, which passed.

## Modeling-mode selection

**Mode: `diagram-assisted`, `sysml_claim: false`.**

- **Why not `sysml-v2`:**
  - No decision in `journey.json` or `scope-decision-batch.md` mandates a SysML v2 model. A search of `journey.json` for sysml, modeling mode and systems modeler returned nothing.
  - The method skill records `diagram-assisted` for this Journey and forbids upgrading it to a SysML claim.
  - No pinned S8-class receipt licenses local SysML coverage.
  - The Lifecycle is a greenfield hackathon with a 12-day horizon (deadline 2026-10-23T19:00:00Z), and the owner has asked for a lightweight design.
- **Why not `not-applicable`:**
  - The work is non-trivial: two systems, four trust boundaries, and fallback branches C2, C5 and C6.
  - The repository map records an architecture gap that activates this role.
- **What the views are:** explanatory views that fix the boundary, use cases, operational flow and delivery tooling before requirement allocation. They are not a semantic model, so Mermaid is not standing in for a mandated SysML model.
- **Persistence:** none of these is persisted to RS or SysON, which would be a `TYPED_GAP RS_PERSISTENCE` if requested. D1 is authored later with D5.

## Contextual pass (placement receipt)

**Current flow:** none. The repository at `2c13a6b` holds only `README.md`, `.gitignore` and the plan directory. There is no source tree, manifest, CI or test configuration (`repository-map.md`). Everything below is a planned placement.

**Path conventions:**
- `tv-app/` holds the imported starter. The starter's Gradle module `app/` and its source root are kept.
- `<pkg>` is the project-owned package directory that replaces `com/amazonappstore/helloworldtv` (finding F2).
- Paths prefixed `Alphazedehq:` are in the private `alphazede/Alphazedehq` repository.

Starter anchors below are cited in this form (the file and line are in the anchor column):

```
AmazonAppDev/hello-world-fire-tv:<path>:<line>
```

### TV app (`tv-app/`, Kotlin, Jetpack Compose, Fire OS)

| Component | Planned path | Anchor (file:line) or "new" | Binding constraint |
|---|---|---|---|
| App shell and navigation | `tv-app/app/src/main/java/<pkg>/MainActivity.kt` | `app/src/main/java/com/amazonappstore/helloworldtv/MainActivity.kt:49` (Activity), `:58` (NavHost) | Starter is MIT-0 (`LICENSE:1`) |
| Build configuration | `tv-app/app/build.gradle.kts` | `app/build.gradle.kts:12` (`minSdk = 21`), `:13` (`targetSdk = 34`), `:51` (dependencies) | min_sdk API 25 means raising 21 to 25. Hot file (F5). |
| ProfileSettings (items 1, 6) | `tv-app/app/src/main/java/<pkg>/profile/ProfileSettingsScreen.kt` | `app/src/main/java/com/amazonappstore/helloworldtv/Screens.kt:7` (route enum), `HomeDrawer.kt:39` (drawer entry) | Device-code Yahoo link only. No secrets in the APK. Detection is opt-in. |
| AppDetector | `tv-app/app/src/main/java/<pkg>/detect/AppDetector.kt` | `app/src/main/AndroidManifest.xml:6` (manifest root; package-visibility declarations go here, F3) | Allow-listed packages only. Installed is not subscribed. |
| AlertService | `tv-app/app/src/main/java/<pkg>/alerts/AlertService.kt` | `app/src/main/AndroidManifest.xml:16` (`<application>`; service declaration) | Foreground service, active only during enabled viewing periods. HTTPS with bearer token (TB1). |
| AlertNotifier | `tv-app/app/src/main/java/<pkg>/alerts/AlertNotifier.kt` | new (the starter has no notification code) | Heads-up notification with Watch and Dismiss. Display over third-party playback is unverified (spike). |
| WatchLauncher | `tv-app/app/src/main/java/<pkg>/watch/WatchLauncher.kt` | new | Explicit intent or deep link to allow-listed packages only (TB4). GAME_OPENED only from device observation. |
| LineupPanel | `tv-app/app/src/main/java/<pkg>/panel/LineupPanel.kt` | `app/src/main/java/com/amazonappstore/helloworldtv/HomeDrawer.kt:39` (TV Material3 drawer pattern) | Remote-navigable. Never a system overlay covering video. Mode B is subject to SP-4 within spike_panel_max of 24 h. |
| CompanionPlayer (Mode A only) | `tv-app/app/src/main/java/<pkg>/player/CompanionPlayer.kt` | `app/src/main/java/com/amazonappstore/helloworldtv/Screens.kt:10` (`Player` route, no implementation); Media3 is added at `app/build.gradle.kts:51` | CC-BY or CC0 footage only, labeled "Sample footage — not a live broadcast" (SD-006a). Footage storage location is open (F12). |

### Backend (`backend/`, Python 3.12 Lambda, API Gateway HTTP API, DynamoDB, EventBridge Scheduler, SSM, AWS SAM)

| Component | Planned path | Anchor | Binding constraint |
|---|---|---|---|
| Infrastructure as code | `backend/template.yaml` | new | Free plan (C4). One AWS account is a shared mutable resource. Hot file (F5). |
| DeviceAuth and `/v1/link` | `backend/src/device_auth/` | new | Device-code flow. Per-device bearer token. The phone link page is served here. |
| REST API `/v1/link`, `/v1/profile`, `/v1/alerts`, `/v1/panel`, `/v1/providers` | `backend/src/api/` | new | TB1. `/v1/alerts` is a long-poll. |
| FeedIngest | `backend/src/feed_ingest/` | new | ESPN responses are untrusted and validated at ingest (TB3). Polling only during game windows (EventBridge Scheduler). ESPN terms go to the owner at submission (C3). |
| ReplaySource | `backend/src/feed_ingest/replay.py` and fixtures `backend/fixtures/replay/` | new | Recorded fixtures, labeled replay (C2) |
| LineupConnector (YahooSource, ManualSource) | `backend/src/lineup/` | new | Read-only OAuth 2.0. Tokens and client secret are server-side only, in SSM SecureString (TB2). ManualSource takes over at T_yahoo, 2026-10-16T19:00:00Z (C6). |
| Matcher | `backend/src/matcher/` | new | Yahoo player to ESPN athlete identity map |
| AlertPolicy | `backend/src/alert_policy/` | new | Preferences, quiet hours, spoiler delay, frequency, duplicate suppression, corrections |
| ProviderResolver and registry | `backend/src/provider_resolver/` (curated registry data alongside) | new | Unknown access stays unknown. One real provider comes from SP-3. |
| PanelService | `backend/src/panel/` | new | Points are stats times league scoring. Freshness and stale marks. |
| Yahoo client secret | SSM SecureString parameter declared in `backend/template.yaml` | new | Setting the value is credential access, which is an owner action. Never in the APK or the repo. |

### D4 shared CI/CD (SD-016 to SD-021)

| Component | Planned path | Anchor | Binding constraint |
|---|---|---|---|
| Gate entrypoint | `tools/ci/gate.sh` (areas: android, backend, spec, hygiene) | new; authored from `Alphazedehq:skills/setup-pre-commit/SKILL.md:10` (still a `[TODO]` template, DX-007) | One verdict for every entry point. The hygiene area enforces rule 12 and C7. |
| Local git hooks | `.githooks/pre-commit`, `.githooks/pre-push` | new | Same command as CI |
| GitHub Actions | `.github/workflows/ci.yml` | Replaces the starter's `.github/workflows/android.yml:4` (push trigger), `:15` and `:17` (unpinned `@v3` actions); none of it is reused (F4). Rules come from `Alphazedehq:skills/setup-a-repo/SKILL.md:42`. | C14 `pull_request` only. SHA-pinned actions, least privilege, concurrency groups, path filters, stable check names. Free hosted runners (SD-017). Private-period minutes (C11). |
| Shared harness hook script | `Alphazedehq:hooks/ci-gate-hook.sh` | new (`Alphazedehq:hooks/` exists; no such script yet) | C13: only after the D4 skill extensions land. Muse's empty skills folder is a known gap. |
| Harness hook configurations | Per-harness user-level settings for Claude Code, Codex, Muse, Cursor and AGY (outside this repo) | new | Shared mutable resource across sessions. No absolute local paths in anything committed. |
| `ship-pull-request` conditional vnv-review | `Alphazedehq:skills/ship-pull-request/SKILL.md` and `references/GATES.md` | `Alphazedehq:skills/ship-pull-request/SKILL.md:58` (Gate section) | C12 REFUSED_NO_VNV is never a pass. C10 size limit (F9). |
| Vnv guidance tree | `docs/vnv/AGENTS.md` plus `docs/vnv/<area>/AGENTS.md` | discovery rule at `Alphazedehq:skills/vnv-review/SKILL.md:20` | SD-014. Each area names Scope, Tools, Review Focus and findings target. |

### D5 shared spec-authoring skill (SD-022) and D1

| Component | Planned path | Anchor (`1wgrumph/gridmarket:<path>:<line>`) | Binding constraint |
|---|---|---|---|
| Skill entry | `Alphazedehq:skills/spec-authoring/SKILL.md` | generalizes `skills/spec-author/SKILL.md:3` ("GridMarket-style"), `skills/spec-diagram/SKILL.md:3`, `skills/spec-lint/SKILL.md:3` | One shared skill and no duplicate skill (C10). Under skill_size_max, so overflow goes to `references/`. Nothing GridMarket-specific. |
| Template | `Alphazedehq:skills/spec-authoring/template/` | `spec/template/spec.yaml:1`, `spec/template/01-introduction.md` (42 template files in total) | Placeholders only |
| Build script | `Alphazedehq:skills/spec-authoring/scripts/spec_build.py` | `tools/spec_build.py:1` (GridMarket IDs in the docstring), `:21` (`import yaml`), `:23` (sys.path import of spec_lint) | PEP 723 inline dependencies, `uv run --script`, no project environment (F6) |
| Lint script | `Alphazedehq:skills/spec-authoring/scripts/spec_lint.py` | `tools/spec_lint.py:1`, `:16` (`import yaml`), `:161` (`main`, exit 1 on any finding) | Same as the build script |
| Diagram tool | `Alphazedehq:skills/spec-authoring/scripts/azdiagram/` | `tools/azdiagram/__init__.py:5` (Graphviz `dot -Tjson`), `:20` (`import yaml`), `tools/azdiagram/__main__.py:1` (run as `python -m azdiagram`) | Graphviz `dot` is external. Package versus single-file PEP 723 (F6). |
| License notice | kept in the skill and in each vendored copy | `LICENSE:1` (MIT) | MIT notice retained |
| Vendored copy | `tools/spec/` (this repo) plus a documented `vendor` step | new | Needed because Alphazedehq is private and this repo goes public. No absolute paths (C7). |
| D1 sources and build | `spec/amazon-fantasy-companion/` built to `spec/Amazon-Fantasy-Companion-Specification.md` | new | Authored after integrated approval. Checked by gate area `spec`. |

### Constraints binding placement

- **minSdk and targetSdk:**
  - min_sdk is API 25, and the starter is at 21.
  - targetSdk stays 34 unless Planning and Design changes it.
  - C1: if the stick is Fire OS 5 or cannot run the provider apps, the decision returns to the owner.
- **AWS Free plan (C4):**
  - DynamoDB on-demand, Lambda, API Gateway HTTP API, Scheduler and SSM standard parameters.
  - Moving to Paid is the owner's decision only.
- **No secrets in the APK:** Yahoo tokens and the client secret stay server-side (TB2). The APK holds only the per-device bearer token obtained at runtime.
- **Rule 12 and C7:** no absolute local path in any committed file. This is enforced by the hygiene gate area, which detects paths by shape.
- **impl_agent_cap = 5:** five concurrent implementation agents per orchestrating session.
- **Shared mutable resources (serialize the writers):**
  - The **single Fire TV stick**: spikes SP-3 and SP-4, alert-over-playback, and device V&V.
  - The **single AWS account**: one SAM stack, so deploys are serialized.
  - The **Alphazedehq `skills/` tree**: D4 and D5 write separate subdirectories but share the repo and its PR queue.
  - The **harness configurations**: user-level and shared by every session.
  - **Hot files inside this repo:** `tv-app/app/build.gradle.kts`, `tv-app/app/src/main/AndroidManifest.xml` and `backend/template.yaml` (F5).

## Views (`views/views.json`)

| ID | Viewpoint | Source | SVG |
|---|---|---|---|
| MODEL-AFC-V1 | Context and trust boundaries (TB1 to TB4) | `views/v1-context.mmd` | `views/v1-context.svg` |
| MODEL-AFC-V2 | Use cases and outcomes for items 1, 2, 3, 4, 6 and the panel | `views/v2-use-cases.mmd` | `views/v2-use-cases.svg` |
| MODEL-AFC-V3 | Operational flow: alert path, panel refresh, Mode B / Mode A | `views/v3-operational-flow.mmd` | `views/v3-operational-flow.svg` |
| MODEL-AFC-V4 | Delivery tooling: one gate, vnv-review branch, D5 to `tools/spec` to the spec gate to D1 | `views/v4-delivery-tooling.mmd` | `views/v4-delivery-tooling.svg` |

`views.json` carries, for each view:
- the DEC-EMV-021 fields: question, concern, source IDs, view type, rationale, canonical source, abstraction and omissions, interpretation, and supported decision;
- mode, trace and limitations;
- the SVG sha256.

Traces are component names and decision IDs. Requirement mappings are provisional until the Requirements Engineer passes.

## Findings (none blocking; for Planning and Design)

- **F1, starter minSdk:** the starter sets `minSdk = 21` (`AmazonAppDev/hello-world-fire-tv:app/build.gradle.kts:12`). The plan's min_sdk of 25 is a planned edit, not inherited.
- **F2, application ID:** the starter's `namespace` and `applicationId` are `com.amazonappstore.helloworldtv` (`app/build.gradle.kts:7`, `:11`). A project-owned ID is needed before publication. Choosing it is a Planning and Design detail, shown here as `<pkg>`.
- **F3, Android platform behaviour at targetSdk 34 (`:13`):** this is from platform knowledge and was not re-verified in this pass.
  - AppDetector needs package-visibility (`<queries>`) declarations for the allow-listed provider packages.
  - AlertService needs a declared foreground-service type.
  - Both land in `AndroidManifest.xml`.
  - The 2018 stick at API 25 does not enforce them at runtime, but the build targets 34.
- **F4, starter CI:** the starter's workflow triggers on `push` (`.github/workflows/android.yml:4`) and uses unpinned `actions/checkout@v3` and `actions/setup-java@v3` (`:15`, `:17`). Both conflict with the SD-021 workflow rules. `ci.yml` replaces it, and nothing from it is reused.
- **F5, hot files:** every tv-app component that needs a permission, service or dependency touches `tv-app/app/build.gradle.kts` and `AndroidManifest.xml`. Every backend component touches `backend/template.yaml`. Lane planning should give each hot file a single owner or serialize its writers.
- **F6, D5 packaging:**
  - All three GridMarket tools `import yaml`, so their PEP 723 headers must declare it.
  - `spec_build.py` imports `spec_lint` through `sys.path` (`tools/spec_build.py:23`), so its inline metadata must cover spec_lint's dependencies.
  - `azdiagram` is a package run with `python -m azdiagram` (`tools/azdiagram/__main__.py:1`). PEP 723 inline metadata applies to single-file scripts, so D5 needs a single-file entry script for `uv run --script`, or another invocation.
  - The CI `spec` area must provision `uv` (a SHA-pinned setup action) and Graphviz on the runner.
  - This is a layout detail inside D5, not a change to SD-022.
- **F7, GridMarket-specific content to remove:**
  - `skills/spec-author/SKILL.md:3` ("GridMarket-style")
  - `tools/spec_build.py:1` (`DES-GM-SPEC`, `DEC-SPEC-004`)
  - `tools/spec_lint.py:1` (`AC-GM-SPEC-02`, `DEC-SPEC-005`, `DEC-SPEC-006`)
  - `tools/azdiagram/__init__.py:3` (`DEC-SPEC-006`)
- **F8, Vnv discovery:** vnv-review accepts `docs/vnv/AGENTS.md` and falls back to `Vnv/AGENTS.md` (`Alphazedehq:skills/vnv-review/SKILL.md:20-21`). The packet names only `docs/vnv`. V4 shows both, and this repo uses `docs/vnv` (SD-014).
- **F9, C10 skill size pressure:**
  - `Alphazedehq:skills/ship-pull-request/SKILL.md` is already 82 lines, over skill_size_max (< 60 lines).
  - `setup-a-repo/SKILL.md` is at exactly 60 lines and 396 words.
  - The D4 edits to both must move overflow into `references/`.
- **F10, merge without a Vnv tree:** V4 does not model whether merge proceeds in a repo without a Vnv tree (REFUSED_NO_VNV is a typed gap, never a pass). No decision covers this. It does not affect this repo, which will have `docs/vnv`, so it is carried to Planning and Design and the integrated review. It is not a stop.
- **F11, Yahoo client secret:** putting the secret into SSM is credential access, an owner-only action. The placement only declares the parameter in `template.yaml`.
- **F12, footage storage:** whether Mode A footage is bundled in the APK or hosted is undecided. It is a Planning and Design detail bounded by SD-006a.

## Blocker

None.

## developer_feedback

- **SM2-OBS-001, positive (tool: `gh api`):** `repos/<o>/<r>/contents/<path>` with base64 decode and `cat -n` gave line-exact anchors for both external repos without cloning. Tree listings came from `git/trees/main?recursive=1`.
- **SM2-OBS-002, friction (configuration; `sysml-modeling` skill links):**
  - `~/.agents/skills/sysml-modeling` is a symlink into `Alphazedehq/skills/`.
  - Its precondition link `../engineering-methods/references/standards-receipts.md` resolves only through the symlink target. Run from the linked location, `ls ~/.agents/skills/engineering-methods/references/standards-receipts.md` returns "No such file or directory".
  - The same file exists at `Alphazedehq:skills/engineering-methods/references/standards-receipts.md`.
  - An agent that resolves the link literally would return a false `TYPED_GAP`. This has not been filed. It is an observation for the Scribe.
- **SM2-OBS-003, environment:** no SVG rasterizer or `mmdc` exists on this host, so neither the SVGs nor the Mermaid could be rendered for visual review. Only `dot` and `uv` are present.
- **SM2-OBS-004, already known (DX-007 still present):** `Alphazedehq:skills/setup-pre-commit/SKILL.md:10` is still the `[TODO]` skill-creator template at `47c46f2`.
- **SM2-OBS-005, own error (tool usage):** the Bash working directory persists between calls. A plan-relative path then failed once (`FileNotFoundError`), and the run was repeated from the plan directory.
- **Tools exercised:** `gh api`, `sha256sum`, `python3 -I` (`xml.etree`, `json`, `hashlib`), `grep`, `sed`, `cp`, `wc`, `ls`, `git log`/`rev-parse`, Read and Write.

## Mapping finalization (2026-10-11, after Requirements Engineer PASS, receipt r2)

Verdict: **READY**. Inputs: register in `amazon-fantasy-companion-technical-plan.md` (gated by `specialists/requirements-engineer-receipt.md` and `specialists/requirements-engineer-receipt-r2.md`), IDs in `design.md`. The view content was not changed.

### changed_paths

- `views/views.json`: each view's `trace` is replaced by the exact AC-AFC/RISK-AFC/DES-AFC/CONTRACT-AFC IDs it depicts. `requirement_mapping_status` is now `final: mapped after Requirements Engineer PASS (receipt r2)`. No other field changed: a key-by-key comparison against the pre-edit copy shows only these two keys differ, and key order is unchanged.
- This section, appended to this receipt. No `.mmd` or `.svg` file was touched.

### Final trace

| View | Requirements (AC, RISK) | Design (DES, CONTRACT) |
|---|---|---|
| MODEL-AFC-V1 context and trust boundaries | AC-AFC-PROF-01 (phone link page, device code), PROF-03 (AppDetector), ALERT-04 (notification system edge), WATCH-02 (TB4 explicit intent to allow-listed package), FEED-01 (TB3 untrusted, validated at ingest), SEC-01 (TB2, SSM SecureString, no secrets in APK), SEC-02 (TB1 bearer token), SEC-03 (backend resource types), SEC-04 (Yahoo read-only), SUB-01 (judge access) | DES-AFC-ARCH, TV, AUTH, INFRA, FEED, LINEUP, POLICY, ALERTPATH, WATCH, PANEL, SPIKES (SP-3 provider, SP-7 optional Alexa), SUB; CONTRACT-AFC-API, TABLES, LINEUPSOURCE, PROVIDERS, LAUNCH |
| MODEL-AFC-V2 use cases and outcomes | AC-AFC-PROF-01..04 (UC-1, O1), MON-01, MON-03 (UC-2, O2), FEED-02, FEED-03, ALERT-01..05 (UC-3, O3), WATCH-01..03 (UC-4, O4), CTRL-01, CTRL-03 (UC-6, O6), PANEL-01, -02, -05 (UC-P, OP); RISK-AFC-03 (details/app-home outcomes), RISK-AFC-04 (Mode A), RISK-AFC-05 (labeled replay), RISK-AFC-06 (ManualSource at T_yahoo) | DES-AFC-TV, AUTH, LINEUP, FEED, POLICY, ALERTPATH, WATCH, PANEL, SPIKES; CONTRACT-AFC-LINEUPSOURCE, ALERT, LAUNCH, PANEL |
| MODEL-AFC-V3 operational flow | AC-AFC-PROF-04, MON-01, MON-02, MON-04, FEED-01..03, ALERT-01..04, WATCH-01..03, SEC-02 (TB1 edges), PANEL-01..05; RISK-AFC-03, -04, -05, -06 | DES-AFC-ARCH (long-poll), INFRA (EventBridge Scheduler), FEED, LINEUP, POLICY, ALERTPATH, WATCH, PANEL, SPIKES (SP-4); CONTRACT-AFC-EVENT, LINEUPSOURCE, ALERT, API, PROVIDERS, LAUNCH, PANEL |
| MODEL-AFC-V4 delivery tooling | AC-AFC-CI-01, CI-02, CI-03, PATH-01 (hygiene area), VNV-01, D4-01..04 (D4-04 covers the harness hooks and the Muse skill-directory gap), LAND-01 (never squash), D5-01, D5-02, D5-04, SPEC-01, SPEC-02 | DES-AFC-GATE, D4, VNV, D5, SPEC, LANES; CONTRACT-AFC-GATE, HOOK, SPECKIT |

What was excluded, and why:
- V1 lists no RISK. Its nodes are boundaries and components, and no risk response is drawn.
- V3 does not draw DynamoDB, so CONTRACT-AFC-TABLES is left out of V3. The run-2 trace named "DynamoDB".
- AC-AFC-ALERT-05 (text templates) is depicted in V2 (O3 and the excitement setting in O6). V3 does not show text selection.
- V4 does not depict RISK-AFC-12 (no pre-tool hook in Muse or AGY). The "known gap" on the HH node is the Muse skills folder, which is AC-AFC-D4-04.

### Checks run

- **ID existence:** every traced ID was grepped for its defining row (`^| <ID> |` in the plan) or heading (`^### <ID> —` in `design.md`). Output: `ids_checked=79 missing=0`. No ID was invented or repaired.
- **JSON validity:** `python3 -m json.tool views/views.json` returned `json.tool exit=0`.
- **SVG digests:** the before and after hashes are identical, and each equals `svg_sha256` in `views.json`:
  - `v1-context.svg` ab6bf7a466e6936f17d24008d887ff02341e4f1eb8824b0e7e473fd01814996e
  - `v2-use-cases.svg` e9f366139a6539d46ac162d9d3ebf67e8924fa4626941814a270bb4c4223bdc4
  - `v3-operational-flow.svg` cd71a995c30370f3ef26d744b74475d671d53228a2e4fc9aba9f8e0e74941e9b
  - `v4-delivery-tooling.svg` 2ac3e16ef548623255c8724144c9a1b38f95187965ccf992f67b2fbf0891ef3b

### Findings (none blocking)

- **MF1, IDs not depicted by any view.** These IDs are verified by inspection, process records or spikes, not shown in a view:
  - AC-AFC-CTRL-02, D4-05, D4-06, D5-03, D5-05, DX-01..03, LW-01, PLAN-01, PLAN-02, REV-01, SPEC-03, SPIKE-01, SPIKE-02, SUB-02..04, VIS-01
  - RISK-AFC-01, -02, -07..-16
  - DES-AFC-DX

  32 of the 111 register and design IDs are not depicted. This is not a STOP: the STOP condition is a view that depicts behavior without an ID, and that did not occur. Each node in each view maps to at least one listed ID. For the Plan Integrator: if the DoD Manifest needs view coverage for any of these, that is a new view request, not a trace edit.
- **MF2, trace semantics changed from run 2.** `trace` now holds only register and design IDs. The component names that were in it are still in the `.mmd` sources, in `interpretation`, and in `design.md` §Placement mapping.

### Blocker

None.

### developer_feedback

- **SM3-OBS-001, positive (method):** a key-by-key JSON comparison against a pre-edit copy proved that only `trace` and `requirement_mapping_status` changed. This is stronger than reading a text diff after the trace arrays were reformatted.
- **SM3-OBS-002, friction (register format):** the RISK rows put the allocation in a different column from the AC rows. A single `awk` column pick returned allocation for AC rows but the response text for RISK rows. Mapping still used the full row text.
- **Tools exercised:** `grep`, `sed`, `awk`, `comm`, `python3` (`json`, `hashlib`), `python3 -m json.tool`, `sha256sum`, `git diff --no-index --stat`.
