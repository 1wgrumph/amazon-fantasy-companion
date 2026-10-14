"""Freeze this assigned P2-B01T handoff; run from the repository root."""

import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

OUT = Path(__file__).resolve().parent.relative_to(Path.cwd())
PLAN = OUT.parent.parent
BASELINE = "884df103e1ee7f8b53c674864db349cd00875283"
LEASE_SOURCE = Path.home() / "alphazede/worktrees/amazon-fantasy-companion-implementation/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
journey = json.loads(LEASE_SOURCE.read_text())
lease = next(x for x in journey["execution_receipts"]
             if x.get("lease_id") == "P2-B01T-g2" and x.get("kind") == "dispatch_lease")
assert lease["state"] == "active" and lease["generation"] == 2
assert lease["candidate_revision"] == head == BASELINE and lease["branch"] == branch == "afc/p2-b01"
assert os.environ.get("GIT_AUTHOR_NAME") and os.environ.get("GIT_AUTHOR_EMAIL")
for path in OUT.rglob("*"):
    if path.is_file() and path.suffix in {".txt", ".json", ".xml"}:
        path.write_text(path.read_text().replace(str(Path.home()), "$HOME"))
cases = ET.parse(OUT / "CMD-RED.xml").getroot().findall(".//testcase")
assert len(cases) == 65
assert all(c.find("failure") is not None and
           c.find("failure").get("message", "").startswith("AssertionError:") and
           c.find("error") is None and c.find("skipped") is None for c in cases)
implementation = json.loads((PLAN / "implementation.json").read_text())
slice_entry = next(s for s in implementation["slices"] if s["id"] == "P2-B01T")
seit = json.loads((PLAN / "seit.json").read_text())
proofs = []
for proof in seit["proof_cases"]:
    if proof["id"] in slice_entry["seit_proof_rows"]:
        proofs.append({"id": proof["id"], "registered_method": proof["method"],
                       "red_support": "Auth/API/template/source assertions frozen" if
                       proof["id"].startswith("SEIT-AFC-PR-") else "Packet/evidence obligation preserved",
                       "formal_row_status": "not_closed_by_red_slice",
                       "closing_slice": proof["closing_slice"]})
receipt = {
    "outcome": "PASS", "scope": "Assigned P2-B01T behavioral red boundary only; backend intentionally fails",
    "lifecycle": "AFC-2026-10-11", "phase": 2, "wave": 1, "milestone": "M02", "issue": 20,
    "slice_id": "P2-B01T", "authority_id": "AUTH-AFC-2026-10-12-P2-001",
    "lease_id": "P2-B01T-g2", "lease": lease,
    "lease_source": str(LEASE_SOURCE).replace(str(Path.home()), "$HOME"),
    "lease_source_sha256": sha(LEASE_SOURCE), "branch": branch, "baseline": BASELINE,
    "candidate_binding": "Precommit red working delta; committed receipt is bound to its containing local commit",
    "route": "Codex CLI / GPT-6.1 Sol / high",
    "profile": {"name": "opensource-hackathon", "sha256": "7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1", "live_catalog_read": False},
    "review_capabilities": {
        "coverage_assist": {"enabled": True, "required": True, "backend": "OCR OpenCodeReview delegate mode",
                            "status": "not_run; allocated to independent review at IE-P2-5, never claimed PASS"},
        "reverify": {"enabled": True, "backend": "reverify 0.11.0", "status": "not_applicable",
                     "reason": "red tests/source contracts, no compiled-binary claim"}},
    "bran_status": "unavailable: no native .bran/policy.yaml; ordinary repository discovery used",
    "method": "SEIT supporting TDD method=test; registered proof methods/environments unchanged",
    "frozen_test_sha256": {str(p): sha(p) for p in sorted(Path("backend/tests").rglob("*.py"))},
    "bootstrap_sha256": {str(p): sha(p) for p in [Path("backend/requirements-dev.txt"),
                         Path("backend/pyproject.toml"), *sorted(Path("backend/src/api").glob("*.py"))]},
    "red": {"command_id": "CMD-RED", "command": "PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $HOME/.local/share/afc-tools/backend-tests/bin/python3.12 -m pytest backend/tests/unit backend/tests/contract -v -p no:cacheprovider --tb=short --junitxml=" + str(OUT / "CMD-RED.xml"),
            "exit_code": 1, "output": str(OUT / "CMD-RED.txt"), "junit": str(OUT / "CMD-RED.xml"),
            "failed": 65, "passed": 0, "errors": 0, "skipped": 0, "elapsed_seconds": 3.57,
            "failure_class": "All JUnit messages begin AssertionError; pytest 8.4.2 omits the failure type attribute",
            "test_ids": [c.get("classname").replace(".", "/") + ".py::" + c.get("name") for c in cases],
            "output_sha256": sha(OUT / "CMD-RED.txt"), "sanitization": "Only local home prefix replaced with $HOME"},
    "existing_suite": {"command": "PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3.12 -m pytest -q tools -p no:cacheprovider",
                       "exit_code": 0, "tests": 75, "output": str(OUT / "repo-suite.txt")},
    "tool_qualification": {"command_id": "PROC-GATE-TOOL-QUALIFY", "coverage_exit_code": 0, "mutation_exit_code": 0,
                           "outputs": [str(OUT / "qualify-coverage.txt"), str(OUT / "qualify-mutation.txt")],
                           "scope": "G01 native/repo adapter positive/negative controls; actual backend coverage/mutation deferred to P2-B01 green"},
    "installation_receipt": str(OUT / "supply-scan.json"),
    "resource_group": "host-pytest; fresh per-test Moto state; sockets blocked; no engine/server/AWS/device",
    "gate_cost": {"red_seconds": 3.57, "planning_budget_seconds": 120, "seven_execution_qualification": "not applicable: no engine/server/driver/browser started"},
    "proof_rows": proofs,
    "handoff_contract_choices": [
        "HTTP API v2 Lambda event, template ApiFunction.Handler; empty scaffold api.handler.lambda_handler.",
        "Link fields code/expires/handle; poll handle; states codePending/linked/expired; confirm code/passphrase/profileId; opaque sessionToken in confirmation or linked poll.",
        "Foreign selector profileId in query/body; templates own env/secret parameter names and key schemas.",
        "Logical table IDs from design, with optional Table suffix; Links template TTL mutated deterministically for expiry test.",
        "600-second code TTL from approved plan; no new session lifetime imposed.",
        "409/429 schemas plus API throttling declarations support future runtime cases; no fabricated profile-revision/rate policy behavior."],
    "scope_reconciliation": [
        "Current owner packet authorizes local --no-verify red commit, superseding older uncommitted-red plan wording.",
        "No [tool.mutmut] section: installed G01 wrapper rejects CONFIG_CONFLICT and writes its own bounded disposable setup.cfg.",
        "Baseline Actions backend job has no dependency install step; outside worker write set, prerequisite handed to orchestrator; no gate weakened."],
    "deferred": ["P2-B01 green on unchanged frozen tests, SAM/cfn-lint, coverage/mutation and deps in isolated mutmut venv",
                 "Independent OCR review at IE-P2-5", "Device demonstration P2-L02; deployment/Free-plan/backend placement P2-L03",
                 "Exact APK/parameter secret inspection P2-L05; complete social UI/source inspection P2-D03",
                 "Orchestrator landing/changelog and allocated lifecycle proof closure"],
    "developer_feedback": {"observations": [
        {"id": "P2B01T-DX-001", "tool": "Python scanner launchers", "observation": "Bare launchers bound a different Python environment; explicit python3.12 -m binding worked. Bandit stdout progress is not JSON; use -o. No route change.", "evidence": str(OUT / "supply-scan.json")},
        {"id": "P2B01T-DX-002", "tool": "pytest/Moto", "observation": "65 all-assertion red cases collect and run offline in 3.57 seconds with fresh in-process tables and SSM parameters.", "evidence": str(OUT / "CMD-RED.xml")},
        {"id": "P2B01T-DX-003", "tool": "G01 gate/workflow", "observation": "Backend job assumes prepared dependencies but includes no installation step; orchestrator must resolve prerequisite before landing within authorized write scope.", "evidence": ".github/workflows/ci.yml backend job; tools/ci/gate.sh backend branch"}],
        "tools_exercised": ["git", "python3.12", "pytest", "boto3/botocore", "Moto", "PyYAML", "coverage", "diff-cover", "mutmut", "ClamAV", "gitleaks", "pip-audit", "bandit", "skill-creator scripts"]}
}
(OUT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print("PASS lease/baseline binding; 65 assertion failures; four frozen test files")
