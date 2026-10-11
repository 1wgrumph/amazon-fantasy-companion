# Repository Map: Amazon Fantasy Companion

Observed 2026-10-11 at `2c13a6b` on `plan/2026-10-11-amazon-fantasy-companion`.
Bounded discovery: depth 2, read-only, `docs/` excluded from traversal except
the plan directory. BRAN: unavailable (no `.bran/policy.yaml`).

## In-repository map

| Path | Kind | Establishes |
|---|---|---|
| `README.md` | doc | Product one-liner; status planning; intent in issue #1 |
| `.gitignore` | config | Node/build ignores; `*.log` also ignores `specialists/*.log` evidence |
| `docs/plans/2026-10-11-amazon-fantasy-companion/` | plan dir (untracked) | `journey.json`, `specialists/`, this map, `workspace.md` |

Not present: package manifest, lockfile, task runner, CI workflows, test
config, source tree, repo `AGENTS.md`/`CLAUDE.md`, `LICENSE`.

## Existing architecture

None. No component, interface, data flow, or deployment architecture exists
in the repository. **Gap → activate Systems Modeler.** Architecture elements
named in issue #1 (Yahoo lineup connector, NFL event ingestion, player/event
matching, alerting, provider routing resolver, right-side lineup panel,
customer settings, backend aggregation) are product intent, not observed
architecture.

## External starter candidates [observed, not run; not cloned; not selected]

Source: `gh repo view` + upstream README/LICENSE via `gh api`, 2026-10-11.
All are owned by `AmazonAppDev`, unarchived, default branch `main`. GitHub
reports no SPDX id; each `LICENSE` file reads "MIT No Attribution" (MIT-0).

| Repo | Lang | Target OS | Last push | Run commands (README) |
|---|---|---|---|---|
| `vega-sports-app` | TypeScript (RN) | Vega OS (VVD + Vega Fire TV Stick) | 2026-08-06 | `npm install`; `npm run build:app`; `vega virtual-device start`; `vega run-app build/<arch>-release/keplersportapp_<arch>.vpkg`. Node 18–20, Vega SDK |
| `react-native-multi-tv-helloworld` | TypeScript (RN, Yarn workspaces) | Vega OS, Android TV, tvOS (Expo TV), web | 2026-10-01 | `yarn`; `yarn vega:build`; `yarn vega:vvd:intel`; `yarn vega:firetv <DSN>`; `yarn expotv:android`. Node ≥18, Vega SDK |
| `react-native-multi-tv-app-sample` | TypeScript (Expo SDK 54 + Vega SDK) | Fire OS, Vega OS, Android TV, tvOS, web | 2026-10-05 | Yarn monorepo (`apps/`, `packages/`); exact commands not extracted. README links Vega SDK 0.21 docs |
| `hello-world-fire-tv` | Kotlin (Jetpack Compose) | Fire OS (Android) | 2024-10-10 | Android Studio → Gradle build → Run app (`gradlew` present) |
| `vega-video-sample` | TypeScript (RN) | Vega OS | 2026-08-06 | `npm install`; `npm run build:app`; `vega run-app build/<arch>-release/keplervideoapp_<arch>.vpkg` |
| `vega-epg-sample` | TypeScript (RN) | Vega OS | 2026-09-25 | `npm install`; `npm run build:app`; `kepler virtual-device start`; `kepler run-kepler …/epgsampleapp_<arch>.vpkg` (older `kepler` CLI naming; Vega SDK 0.21 link) |
| `vega-tv-interfaces-sample` | TypeScript (RN) | Vega OS | 2026-08-06 | `npm install`; `npm run build:app`; `vega run-app build/<arch>-release/keplertvinterfaces_<arch>.vpkg` |

Observations relevant to Scope Definition (facts, not choices):
- Only `react-native-multi-tv-app-sample` and `hello-world-fire-tv` state Fire OS
  support; the `vega-*` samples target Vega OS only.
- Vega builds emit `armv7` VPKGs for physical Vega Fire TV Sticks and
  `x86_64`/`aarch64` VPKGs for the Vega Virtual Device.
- CLI naming differs across samples (`vega` vs `kepler`), and pinned Vega SDK
  doc versions differ (0.21 vs "latest"); version alignment is unverified.
- No candidate is evidence of notification-over-third-party-playback, side-by-
  side panel composition with another app's video, or provider deep links.

## Constraints carried to planning
- Deadline 2026-10-23 12:00 PDT; target track Fire TV (Fire OS/Vega OS with
  device or simulator evidence).
- Excluded: all community messaging/social features.
- Lightweight design; no hardware performance verification or claims.
- Every packet/return carries `developer_feedback` (Scribe contract, issue #1).
- External sharing, publication, and submission are owner-only.

## Map freshness
Valid while `README.md`, `.gitignore`, and the plan directory are unchanged
relative to `2c13a6b`. Upstream candidate metadata is a 2026-10-11 snapshot.
