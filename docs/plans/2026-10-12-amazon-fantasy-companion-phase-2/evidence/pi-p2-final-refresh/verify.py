#!/usr/bin/env python3
"""PI final-refresh bounded verification. Run once from the repo worktree root."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

PLAN = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
BL = Path.home() / "src/bearing-lite-153"
OUT = []
ok = lambda name, detail="": OUT.append(f"{name}: PASS {detail}".rstrip())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


impl = json.loads((PLAN / "implementation.json").read_text())
seit = json.loads((PLAN / "seit.json").read_text())
auth = json.loads((PLAN / "authority.json").read_text())
tracking = json.loads((PLAN / "evidence/github-work-items/github-work-items.json").read_text())

# 1. implementation schema
import jsonschema  # noqa: E402
schema = json.loads((BL / "schemas/implementation.schema.json").read_text())
jsonschema.validate(impl, schema)
ok("SCHEMA")

# 2. counts: 100 proofs / 70 commands / 52 slices / 44 steps / 39 groups / 5 milestones
pcs = seit["proof_cases"]
assert len(pcs) == 100 and len({p["id"] for p in pcs}) == 100
assert all(p["method"] and p["negative_or_failure_case"] for p in pcs)
cmds = seit["procedures_and_commands"]
assert len(cmds) == 70 and len({c["id"] for c in cmds}) == 70
assert len(impl["slices"]) == 52 and len(impl["integration_plan"]["steps"]) == 44
assert len(impl["work_issues"]["groups"]) == 39 and len(impl["milestones"]) == 5
assert len(seit["frozen_profile_binding"]) == 5
pj = json.loads((Path.home() / "alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json").read_text())
for lane, e in impl["profile_freeze"]["lanes"].items():
    if lane == "scribe-side-lane":
        continue
    assert e["configuration_digest_sha256"] == pj["profile_selection"]["frozen_snapshots"][e["profile"]]["configuration_digest_sha256"], lane
ok("COUNTS", "100/70/52/44/39/5; 5 frozen profiles match parent")

# 3. refs resolve; work_issues cover 52 slices once; 13 TDD pairs; acyclic deps
reg = {c["id"] for c in cmds}
pcids = {p["id"] for p in pcs}
sids = {s["id"] for s in impl["slices"]}
for s in impl["slices"]:
    assert set(s["command_ids"]) <= reg, s["id"]
    assert set(s["seit_proof_rows"]) <= pcids, s["id"]
    assert set(s["depends_on"]) <= sids, s["id"]
seen, stack, adj = set(), set(), {}
for d in impl["dependencies"]:
    assert d["from"] in sids and d["to"] in sids, d
    adj.setdefault(d["from"], []).append(d["to"])


def visit(n):
    assert n not in stack, f"cycle at {n}"
    if n in seen:
        return
    stack.add(n)
    for t in adj.get(n, []):
        visit(t)
    stack.discard(n)
    seen.add(n)


for d in impl["dependencies"]:
    visit(d["from"])
    visit(d["to"])
cov = [s for g in impl["work_issues"]["groups"] for s in g["slices"]]
assert sorted(cov) == sorted(sids)
pairs = [g for g in impl["work_issues"]["groups"] if len(g["slices"]) == 2]
assert len(pairs) == 13, len(pairs)
assert len(impl["traceability"]) == 103
ok("REFS", f"{len(impl['dependencies'])} deps acyclic; 39 groups cover 52 once; 13 pairs")

# 4. exact M2 ISO + due_explanation; no other due text drift
m2 = next(m for m in impl["milestones"] if m["id"] == "M2")
assert m2["due_on"] == "2026-10-17T01:00:00Z", m2["due_on"]
assert "T_yahoo" in m2["due_explanation"] and "no date change" in m2["due_explanation"]
assert [m["due_on"] for m in impl["milestones"]] == [
    "2026-10-14T23:00:00Z", "2026-10-17T01:00:00Z", "2026-10-19T12:00:00Z",
    "2026-10-21T23:00:00Z", "2026-10-23T12:00:00Z"]
ok("M2", "exact ISO; T_yahoo in due_explanation")

# 5. current binding hashes
for pi in impl["source_baseline"]["planning_inputs"]:
    assert sha(pi["path"]) == pi["sha256"], pi["path"]
assert sha(PLAN / "seit.json") == impl["source_baseline"]["seit_json_sha256_at_integration"]
for m in impl["dod_manifest"]["models"]:
    assert m["digest"] == "sha256:" + sha(PLAN / m["view"]["path"]), m["id"]
assert impl["work_issues"]["payload_sha256"] == sha(PLAN / "evidence/github-work-items/github-work-items.json")
assert sha(PLAN / "evidence/github-work-items/github-work-items.json") == "95caddfe2b85067e2a22a3c1e7d46180193f3c67c59aa91b34d552d9116b8c4b"
assert seit["tracking_workflow"]["payload_sha256"] == impl["work_issues"]["payload_sha256"]
assert seit["tracking_workflow"]["payload_ref"].endswith("evidence/github-work-items/github-work-items.json")
ok("BINDINGS", "9 planning inputs + seit + 7 views + payload digests current")

# 6. seven selected/required READY views, all embedded
models = impl["dod_manifest"]["models"]
assert len(models) == 7 and all(m["selected"] and m["required"] and m["render_status"] == "READY" for m in models)
html = (PLAN / "amazon-fantasy-companion-phase-2-dod-manifest.html").read_text()
assert html.count("<svg") == 7, html.count("<svg")
for m in models:
    assert html.count(m["id"]) >= 2, m["id"]  # inventory row + embedded figure
assert "not embedded" not in html and "XML prolog" not in html
ok("VIEWS", "7 selected/required READY; 7 embedded SVG; workaround text gone")

# 7. TE projections: supplemental commands, A05/RISK09, IE order/phrase, X05, alias
bys = {s["id"]: s for s in impl["slices"]}
assert "PROC-TRACKING-SETUP" in bys["P2-L01"]["command_ids"]
assert "PROC-GATE-TOOL-QUALIFY" in bys["P2-G01T"]["command_ids"]
assert {"PROC-GATE-TOOL-QUALIFY", "CMD-COVERAGE-BACKEND", "CMD-COVERAGE-TVAPP",
        "CMD-MUTATION-BACKEND", "CMD-MUTATION-TVAPP"} <= set(bys["P2-G01"]["command_ids"])
assert {"PROC-GATE-TOOL-QUALIFY", "CMD-COVERAGE-TVAPP", "CMD-MUTATION-TVAPP"} <= set(bys["P2-A01"]["command_ids"])
assert {"PROC-GATE-TOOL-QUALIFY", "CMD-COVERAGE-BACKEND", "CMD-MUTATION-BACKEND"} <= set(bys["P2-B01"]["command_ids"])
assert "SEIT-RISK-AFC-P2-09" in bys["P2-A05"]["seit_proof_rows"]
steps = impl["integration_plan"]["steps"]
ids = [s["id"] for s in steps]
assert ids.index("IE-P2-35") < ids.index("IE-P2-34")
ie2 = next(s for s in steps if s["id"] == "IE-P2-2")["entry_criteria"][0]
seit_ie2 = next(e for e in seit["integration_vv_sequence"] if e["step"] == "IE-P2-2")["entry_criteria"][0]
assert ie2 == seit_ie2 and "repository-applicable workflow" in ie2
x05r1 = next(d for d in impl["dependencies"] if d["from"] == "P2-X05" and d["to"] == "P2-R1")
assert "PR 1" in x05r1["condition"]
assert next(g for g in impl["work_issues"]["groups"] if g["issue"] == "P2-X05")["milestone"] == "M2"
assert bys["P2-X05"]["milestone"] == "M1" and bys["P2-X05"]["wave"] == "Wave 1"
assert all("step_ids" in w and "integration_steps" not in w for w in impl["integration_plan"]["wave_gate_costs"])
assert "TOOL_UNALLOCATED until tool/command/pin/write-set are allocated" not in json.dumps(impl["assurance"])
ok("TE-PROJECTION", "commands/A05/order35<34/IE-P2-2 phrase/X05 PR1+M2/M1/step_ids alias")

# 8. payload mirrors + register layout rows
for i in tracking["issues"]:
    body = (PLAN / i["body_file"]).read_text()
    assert body == i["body"], i["id"]
    assert hashlib.sha256(i["body"].encode()).hexdigest() == i["body_sha256"], i["id"]
ident = {r["label"]: r["value"] for r in impl["dod_manifest"]["identity"]}
assert ident["Requirement register"] == "requirements-register.md (authority.json#/requirement_register)"
assert ident["Register digest"] == "sha256:" + auth["requirement_register"]["sha256"]
assert len(ident["Requirement register"]) < 100
ok("PAYLOAD-LAYOUT", "39 body mirrors byte-equal; short register ref + digest row")

# 9. gates: plan-package PASS with digest; renderer check; TE schema check
pp = subprocess.run(["node", str(BL / "hooks/plan-package.cjs"), str(PLAN)],
                    capture_output=True, text=True, check=True)
ppj = json.loads(pp.stdout)
assert ppj["outcome"] == "PASS" and not ppj["findings"], pp.stdout
assert impl["journey_settings"]["planning_review"]["candidate_digest"] == ppj["manifest_digest"]
rc = subprocess.run(["node", str(BL / "tools/render-dod-manifest.mjs"), str(PLAN / "implementation.json"), "--check"],
                    capture_output=True, text=True, check=True)
assert "RENDER_CHECK_PASS" in rc.stdout, rc.stdout
ck = subprocess.run(["python3", str(PLAN / "evidence/te-p2-codex/check_seit.py")],
                    capture_output=True, text=True)
assert ck.returncode == 0 and "CROSS-CHECK: PASS" in ck.stdout, (ck.returncode, ck.stdout[-500:], ck.stderr[-500:])
ok("GATES", f"plan-package PASS digest={ppj['manifest_digest'][:12]}; renderer check; check_seit CROSS-CHECK PASS")

# 10. deterministic reproduction + home-path hygiene
before = hashlib.sha256((PLAN / "implementation.json").read_bytes()).hexdigest()
subprocess.run(["python3", str(PLAN / "evidence/pi-p2-codex/gen_impl.py"), "--digest", ppj["manifest_digest"]],
               capture_output=True, text=True, check=True)
after = hashlib.sha256((PLAN / "implementation.json").read_bytes()).hexdigest()
assert before == after, (before, after)
pat = "/ho" + "me/"
for f in [PLAN / "implementation.json",
          PLAN / "amazon-fantasy-companion-phase-2-dod-manifest.html",
          PLAN / "specialists/pi-p2-final-refresh-receipt.md",
          PLAN / "evidence/pi-p2-codex/gen_impl.py",
          Path(__file__), PLAN / "evidence/pi-p2-final-refresh/rebind_seit.py"]:
    assert pat not in f.read_text(), f
ok("REPRO", f"rerun byte-identical {after[:12]}; no home paths")

print("\n".join(OUT))
print(f"DIGESTS impl={after} manifest={ppj['manifest_digest']}")
(PLAN / "evidence/pi-p2-final-refresh/verification.txt").write_text(
    "\n".join(OUT) + f"\nDIGESTS impl={after} manifest={ppj['manifest_digest']}\n")
