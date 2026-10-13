#!/usr/bin/env python3
"""Lossless Markdown row adapter to Bearing's pure precheck; no SDoc is persisted."""
import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

PLAN = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
OUT = PLAN / "evidence/chronology-profile-delta"
PLUGIN = Path(sys.argv[1]).resolve()
REGISTER = PLAN / "requirements-register.md"
TECHNICAL_PLAN = PLAN / "amazon-fantasy-companion-phase-2-technical-plan.md"


def rows(text):
    result = []
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("| UID |"):
            header = [c.strip() for c in line.strip("|").split("|")]
        elif line.startswith("| AFC-PR-"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            assert len(cells) == len(header), (number, "malformed register row")
            result.append({**dict(zip(header, cells)), "source_line": number})
    assert [r["UID"] for r in result] == [f"AFC-PR-{n:03}" for n in range(1, 67)], "missing, duplicate or reordered register UID"
    return result


def evaluate(source_rows, proofs):
    # ST5 approves the common product-register basis; all individual sources remain intact.
    fields = {"UID": "UID", "Statement": "STATEMENT", "Rationale": "RATIONALE",
              "Verification method": "VERIFICATION_METHOD", "Allocation": "ALLOCATION", "Sources": "SOURCE"}
    blocks = []
    for row in source_rows:
        if row["Statement"].startswith("WITHDRAWN"):
            continue
        block = ["[REQUIREMENT]"]
        for key, field in fields.items():
            block += [field + ": >>>", row[key], "<<<"]
        block += ["VERIFICATION_CASES: " + ", ".join(proofs[row["UID"]]),
                  "DECISION: DEC-AFC-APPROVAL-ST5", "[/REQUIREMENT]"]
        blocks.append("\n".join(block))
    plan = TECHNICAL_PLAN.read_text()
    register = "\n".join(blocks)
    files = {}
    for name in re.findall(r"(?:^|[\s`(])((?:[\w.-]+/)*[\w.-]+\.[\w.-]+):\d+\b", register + "\n" + plan):
        path = Path(name)
        assert not path.is_absolute() and ".." not in path.parts
        if path.is_file():
            files[name] = path.read_text()
    request = {"register": register, "technicalPlan": plan,
               "registerPath": "in-memory Markdown projection (UID maps to rows.json/source_line)",
               "planPath": str(TECHNICAL_PLAN), "files": files}
    js = 'const fs=require("fs");const c=require(process.argv[1]);console.log(JSON.stringify(c.checkRegister(JSON.parse(fs.readFileSync(0,"utf8")))));'
    return json.loads(subprocess.check_output(["node", "-e", js, str(PLUGIN / "hooks/register-precheck.cjs")], input=json.dumps(request).encode()))


source = REGISTER.read_text()
original = rows(source)
assert sum(r["Statement"].startswith("WITHDRAWN") for r in original) == 3
proofs = {}
for p in json.loads((PLAN / "seit.json").read_text())["proof_cases"]:
    proofs.setdefault(p["requirement_id"], []).append(p["id"])
result = evaluate(original, proofs)
assert source == REGISTER.read_text(), "register modified during check"
for mutation in [lambda t: t.replace("| AFC-PR-001 |", "| AFC-PR-002 |", 1),
                 lambda t: "\n".join(l for l in t.splitlines() if not l.startswith("| AFC-PR-001 |"))]:
    try:
        rows(mutation(source))
    except AssertionError:
        pass
    else:
        raise AssertionError("adapter accepted a lost or duplicate row")
bad = copy.deepcopy(original)
bad[0]["Verification method"] = ""
assert any(f["class"] == "verification" for f in evaluate(bad, proofs)["findings"])
result["adapter"] = {"source": str(REGISTER), "register_authority": "Markdown per DEC-AFC-SD-027",
                     "active_rows_checked": 63, "withdrawn_rows_retained_in_source_and_snapshot": 3,
                     "statement_rationale_verification_allocation_sources": "verbatim",
                     "decision_basis": "DEC-AFC-APPROVAL-ST5 common approved register basis",
                     "negative_checks": ["duplicate UID rejected", "missing UID rejected", "missing verification method rejected"],
                     "technical_plan_sha256": hashlib.sha256(TECHNICAL_PLAN.read_bytes()).hexdigest(),
                     "plugin_precheck_sha256": hashlib.sha256((PLUGIN / "hooks/register-precheck.cjs").read_bytes()).hexdigest(),
                     "sdoc_persisted": False}
(OUT / "rows.json").write_text(json.dumps(original, indent=2) + "\n")
(OUT / "register-precheck.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
sys.exit(0 if result["outcome"] == "PASS" else 1)
