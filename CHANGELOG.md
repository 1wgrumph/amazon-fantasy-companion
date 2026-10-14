# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Add the ESPN feed capture tool and historical replay fixtures for 14
  completed games, with an interim SP-5 verdict ([#63](https://github.com/1wgrumph/amazon-fantasy-companion/pull/63)).
- Add the 2026-10-14 developer friction-log catch-up (ten observations in
  the house format) ([#62](https://github.com/1wgrumph/amazon-fantasy-companion/pull/62)).
- Add the backend foundation: SAM HTTP API with throttling, Lambda router
  and response envelope, DynamoDB store, device-code linking with a
  passphrase-confirmed phone page, bounded session retry, least-privilege
  per-function grants, pipeline and module stubs, and hash-pinned CI
  dependencies ([PR #60](https://github.com/1wgrumph/amazon-fantasy-companion/pull/60)).

- Extend the shared gate with `tvapp` and `backend` areas, their CI jobs
  and backend coverage and mutation checks with qualified tooling
  ([PR #57](https://github.com/1wgrumph/amazon-fantasy-companion/pull/57)).

- Add V&V guidance areas for the TV app, backend and device integration,
  and update the V&V index so every path keeps one owning area
  ([PR #56](https://github.com/1wgrumph/amazon-fantasy-companion/pull/56)).

- Create and verify all 13 Phase 2 milestones and 39 work issues with
  dependency links; reconcile three calendar dates while preserving exact
  deadlines ([PR #55](https://github.com/1wgrumph/amazon-fantasy-companion/pull/55)).

- Add the Phase 2 delivery and verification package with 13 chronological
  GitHub milestones, 39 work-issue drafts and 52 slices, preserving five
  technical waves and release checkpoints; product execution remains held
  pending a separate owner instruction
  ([PR #15](https://github.com/1wgrumph/amazon-fantasy-companion/pull/15)).

### Changed

- Record the Phase 2 execution lease and the M01 dispatch, review and
  closeout receipts in the Lifecycle control journey
  ([PR #58](https://github.com/1wgrumph/amazon-fantasy-companion/pull/58)).

- Freeze the complete `opensource-hackathon` profile under Bearing 1.1.7,
  including capability settings and Muse contributor mode; preserve spent
  review limits and validate the Markdown register through the native
  precheck's in-memory interface
  ([PR #15](https://github.com/1wgrumph/amazon-fantasy-companion/pull/15)).

- Add architecture specification revision 0.3 with clickable references, per-revision changed sections and PR/diff links; update the vendored authoring tools ([PR #10](https://github.com/1wgrumph/amazon-fantasy-companion/pull/10), [diff](https://github.com/1wgrumph/amazon-fantasy-companion/pull/10/files)).

### Fixed

- Spec gate compares the rebuilt output against the staged index instead of
  HEAD, so a correctly regenerated staged output passes before commit
  ([PR](https://github.com/1wgrumph/amazon-fantasy-companion/pull/14)).

## 2026-10-12

### Added

- Publish AFC Lifecycle records and Orchestrator handoff ([PR #13](https://github.com/1wgrumph/amazon-fantasy-companion/pull/13)).
- B1: gate hygiene discards diff content lines before location parse ([PR #12](https://github.com/1wgrumph/amazon-fantasy-companion/pull/12)).
- S09T: gate tests (red) for AC-AFC-CI-01..04, AC-AFC-PATH-01 ([PR #9](https://github.com/1wgrumph/amazon-fantasy-companion/pull/9)).
- Link spec-authoring skill into four harness skill directories ([PR #8](https://github.com/1wgrumph/amazon-fantasy-companion/pull/8)).
- Vendor spec-authoring tools at Alphazedehq ac47f0e (S42) ([PR #7](https://github.com/1wgrumph/amazon-fantasy-companion/pull/7)).
- Spec track ST-1..ST-3: requirements register and SysML v2 models ([PR #6](https://github.com/1wgrumph/amazon-fantasy-companion/pull/6)).
- Wave 1 landing receipts and plan digest a018168f ([PR #5](https://github.com/1wgrumph/amazon-fantasy-companion/pull/5)).
- Phase 1 plan delta SD-026..028 and Wave 1 receipt ([PR #4](https://github.com/1wgrumph/amazon-fantasy-companion/pull/4)).
- docs: add Phase 1 Vnv guidance tree ([PR #3](https://github.com/1wgrumph/amazon-fantasy-companion/pull/3)).
- Add approved Phase 1 planning package (AFC-2026-10-11) ([PR #2](https://github.com/1wgrumph/amazon-fantasy-companion/pull/2)).
