# S09-g3 contract failure

Outcome: CONTRACT_FAILURE. Candidate is staged, uncommitted; HEAD remains 7f12bca11e61cfdd1f5d98725e6580fb5c33ab14.

Exact command and output: CMD-COVERAGE-CI.txt and coverage-command.json.

CMD-COVERAGE-CI --exclude tools/ci/check_workflows.py does not exclude the vendored checker in diff-cover 9.7.2. The unchanged command reports it (88.0%) and exits 1 at 85%; matcher checks basename or absolute path. Local checker coverage separately is 82.72%, below 90%.

Pinned tool provenance: scan-coverage-diff-cover.md, diff-cover 9.7.2.
Relevant source: diff_cover/diff_reporter.py lines 94-102:

```python
        exclude = self._exclude
        if not exclude:
            return False
        basename = os.path.basename(path)
        if self._fnmatch(basename, exclude):
            return True

        absolute_path = os.path.abspath(path)
        return self._fnmatch(absolute_path, exclude)
```

No command was changed or claimed passing. Proposed orchestrator correction: exclude by basename `--exclude check_workflows.py` or wildcard absolute suffix `--exclude '*/tools/ci/check_workflows.py'`; re-dispatch a fixed command. Independently, existing S09T tests leave CLI/error and binary/directory paths in the local checkers uncovered; the approved tests must gain behavior checks if those branches remain, or the packet must explicitly resolve their treatment. No test file was edited.

STOP applied: mutation, commit, push, draft PR, hosted checks and review are NOT_RUN. Retain exact eight-path candidate for redispatch. Shell coverage and shell mutation remain TOOL_MISSING; no compiled binary claim (Reverify not applicable).

Billing read: `gh api users/1wgrumph/settings/billing/usage` exit 1; `gh: Not Found (HTTP 404)` and `This API operation needs the "user" scope.` No authentication or budget settings changed. RISK-AFC-08 remains NEEDS_MORE_EVIDENCE.
