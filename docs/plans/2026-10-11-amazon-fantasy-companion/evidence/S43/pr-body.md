Specification prose could reference issues, sections and files without clickable links, and revision rows showed summaries without the changed sections or change links. S43 adds reference linting and linked revision records, seeds Keep a Changelog, and makes PR landing and release notes use that record.

- Spec-authoring rejects unlinked issue/PR, numbered section and explicit file/URL references outside code. Revision entries record changed sections and PR/diff links; lint and build reject incomplete later revisions, and the build renders section anchors and change links.
- Ship-pull-request requires a linked Unreleased entry before landing; setup-a-repo seeds a changelog. Release-process moves unreleased entries under a linked version and derives release notes from those entries while preserving publication authority.
- HQ instructions point to workspace rule 21. This PR records its own change in CHANGELOG.md. Three pre-existing absolute home paths in that allowed instruction file now use equivalent $HOME paths.

Validation at `68172c3e987d1825efff3b9fead02ff05d3a9def`: 119 skill tests and 4 subtests passed, including portable creator metadata validation and independent matching/non-matching trigger classifications. PR edit and pin-consumer shell suites, the local gate, strict BRAN validation, diff checks and changed-file home-path scan passed. The template built twice byte-identically and linted cleanly; four negative fixture CLIs exited 1 with their expected messages. The 19 new regression cases failed against the baseline and passed on the candidate.

Scope: AFC-2026-10-11 S43 generation 1; DEC-AFC-SD-038 and ST5-F1/F2. Only the four shared skills, HQ instructions and changelog changed. No AFC specification or other repository content changed.

Draft gap: independent review and lifecycle integration remain outside this Implementer packet. No merge or release publication is authorized here. Reference detection is lexical: named-document titles and actual anchor/remote target correctness still need author checking. Revision URLs are GitHub PR/files or compare URLs. The workspace-rule link uses the dispatched worktree layout.
