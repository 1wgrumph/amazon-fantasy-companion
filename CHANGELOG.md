# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added the Phase 2 delivery and verification plan, five milestone definitions,
  39 work-issue drafts, and sanitized Lifecycle evidence; product execution
  remains held pending a subsequent owner instruction
  ([PR #15](https://github.com/1wgrumph/amazon-fantasy-companion/pull/15)).

### Changed

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
