"""Artifact consistency only: no TE procedure, product test or independent review."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

PLAN = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent


def load_plan(text):
    return json.loads(re.search(r"```json integration_plan\n(.*?)\n```", text, re.S)[1])


def topological(nodes, edges):
    remaining = set(nodes)
    ordered = []
    while remaining:
        ready = sorted(n for n in remaining if not any(b == n and a in remaining for a, b in edges))
        assert ready, ("DEPENDENCY_CYCLE", sorted(remaining))
        ordered.extend(ready)
        remaining.difference_update(ready)
    return ordered


before = load_plan((EVIDENCE / "integration-plan.before.md").read_text())
text = (PLAN / "specialists/integration-plan.md").read_text()
current = load_plan(text)
seit = json.loads((PLAN / "seit.json").read_text())
graph = (PLAN / "specialists/slice-graph.md").read_text()
technical = (PLAN / "amazon-fantasy-companion-phase-2-technical-plan.md").read_text()
source_slices = re.findall(r"^\| (P2-[A-Z0-9]+) \|", graph, re.M)
assert len(source_slices) == len(set(source_slices)) == 52
steps = current["steps"]
ids = [step["id"] for step in steps]
assert len(ids) == len(set(ids)) == 44
assert set(ids) == {step["id"] for step in before["steps"]} == {f"IE-P2-{n}" for n in range(1, 45)}
assert [step["order"] for step in steps] == list(range(1, 45))
assert {step["id"]: (step["merges"], step["milestone"]) for step in steps} == {step["id"]: (step["merges"], step["milestone"]) for step in before["steps"]}
merged = Counter(s for step in steps for s in step["merges"])
assert set(merged) == set(source_slices)
assert {s: n for s, n in merged.items() if n != 1} == {"P2-X03": 2, "P2-X05": 2}
assert current["concurrency_findings"] == before["concurrency_findings"]
assert current["authorized_glue"] == before["authorized_glue"] == []
edges = {(parent, step["id"]) for step in steps for parent in step["after"]}
assert all(a in ids and b in ids and a != b for a, b in edges)
assert all(ids.index(a) < ids.index(b) for a, b in edges)
assembly_order = topological(ids, edges)
assert assembly_order.index("IE-P2-35") < assembly_order.index("IE-P2-34")

command_ids = [c["id"] for c in seit["procedures_and_commands"]]
assert len(command_ids) == len(set(command_ids)) == 64
used = set(re.findall(r"\b(?:CMD|PROC)-[A-Z0-9-]+\b", json.dumps(current)))
assert used <= set(command_ids), ("UNRESOLVED_COMMANDS", used - set(command_ids))
proof_ids = [c["id"] for c in seit["proof_cases"]]
assert len(proof_ids) == len(set(proof_ids)) == 100
assert set(seit["planning_findings_for_plan_integrator"]["slice_proof_map"]) == set(source_slices)
assert {x["step"] for x in seit["integration_vv_sequence"]} == set(ids)
assert all(ref in proof_ids for wave in current["wave_gate_costs"] for ref in wave["resource_case_refs"])
assert [w["added_gate_seconds"] for w in current["wave_gate_costs"]] == [720, 900, 2100, 0, 120]
for wave, level in zip(current["wave_gate_costs"], seit["levels"]):
    assert type(wave["added_gate_seconds"]) is int
    assert wave["slices"] == level["slices"] and wave["integration_steps"] == level["integration_steps"]
    assert wave["estimate_text"] == level["expected_gate_time_delta"]
    source_date = re.search(r"^\| " + wave["milestone"] + r" \|[^\n]+", technical, re.M)[0].split("|")[3].strip()
    assert level["due_utc"] == source_date
    declared = {seit["proof_cases"][proof_ids.index(ref)]["method_fields"]["resource_group"] for ref in wave["resource_case_refs"]}
    assert set(wave["seit_case_resource_groups"]) == declared
for name, snapshot in seit["frozen_profile_binding"].items():
    binding = current["configuration_identity"]["frozen_capability_binding"][name]
    assert binding["configuration_digest_sha256"] == snapshot["configuration_digest_sha256"]
    assert binding["review"] == snapshot["review"]
    assert binding["deterministic_verification"] == snapshot["deterministic_verification"]
assert seit["frozen_profile_binding"]["primary"]["roles"]["integration_engineer"]["sessions"]["planning"]["ordered_fallbacks"][0] == {
    "condition": "Verified unavailability or usage/rate-limit exhaustion of the primary route.",
    "harness": "Codex CLI", "model": "GPT-6.1 Sol", "reasoning": "xhigh",
}

# Effective source graph uses its explicit continuation note to correct literal merged-T arrows.
source_edges = {(a, b) for a, b in re.findall(r"`(P2-[A-Z0-9]+) --> (P2-[A-Z0-9]+)`", graph)}
assert all(a in source_slices and b in source_slices for a, b in source_edges)
effective_edges = source_edges | {("P2-X01", "P2-A01T")} | {(f"P2-X{n:02}", "P2-D02") for n in range(1, 8)} | {("P2-X11", "P2-D02"), ("P2-R3", "P2-X11")}
slice_order = topological(source_slices, effective_edges)
groups = {}
for s in source_slices:
    group = s[:-1] if s.endswith("T") and s[:-1] in source_slices else s
    groups.setdefault(group, []).append(s)
assert len(groups) == 39 and len([v for v in groups.values() if len(v) == 2]) == 13
assert Counter(x for group in groups.values() for x in group) == Counter(source_slices)

manifest = json.loads((EVIDENCE / "input-provenance.json").read_text())
for record in manifest["inputs"]:
    path = Path(record["path"])
    if path.name == "integration-plan.md":
        path = EVIDENCE / "integration-plan.before.md"
    content = path.read_bytes()
    assert len(content) == record["bytes"] and hashlib.sha256(content).hexdigest() == record["sha256"], ("INPUT_DRIFT", record["path"])
lead = json.loads((PLAN / "evidence/P2-6/codex-lead/input-delta.json").read_text())
assert all(hashlib.sha256((PLAN / path).read_bytes()).hexdigest() == delta["after"] for path, delta in lead.items())
stale = []
for source in seit["source_baseline"]["planning_inputs"]:
    actual = hashlib.sha256(Path(source["path"]).read_bytes()).hexdigest()
    if actual != source["sha256"]:
        relative = str(Path(source["path"]).relative_to(PLAN.relative_to(Path.cwd())))
        assert lead[relative]["before"] == source["sha256"] and lead[relative]["after"] == actual
        stale.append(source["path"])
assert len(stale) == 2  # Explicit recorded source transition; no fabricated SEIT rebinding.

findings = [x["id"] for x in current["concurrency_findings"]]
assert len(findings) == len(set(findings)) == len(before["concurrency_findings"]) == 27
assert not re.search(r"\x2f(?:home|Users)\x2f[^/\s]+/", text)
assert "./tv-app/gradlew -p tv-app" in text
assert not re.search(r"(?<!tv-app/)\./gradlew -p", text)
assert "OWNER_EVIDENCE_PENDING" in json.dumps(current)
assert "REVERIFY_CAPABILITY_GAP" in json.dumps(current)

report = {
    "status": "PASS — artifact consistency only; no independent review/assurance",
    "stable_steps": 44, "stable_slices": 52, "logical_issue_groups": 39, "tdd_pairs": 13,
    "unique_command_ids": 64, "resolved_used_commands": len(used), "unchanged_proof_cases": 100,
    "source_dates_preserved": 5, "frozen_capability_bindings_preserved": 5,
    "historical_findings_preserved": 27, "assembly_dependencies_acyclic": True,
    "effective_slice_dependencies_acyclic": True, "assembly_topological_order": assembly_order,
    "effective_slice_topological_order": slice_order,
    "source_graph_literal_condition_gap": "15 merged-T arrows need receipt wording; explicit source continuation already establishes intended semantics",
    "typed_source_projection_gap": {"type": "SEIT_INPUT_PROJECTION_STALE", "prior_bound_inputs_changed_by_recorded_lead_delta": stale, "assembly_projection_stale": [x["step"] for x in seit["integration_vv_sequence"] if any(x[field] != steps[ids.index(x["step"])][field] for field in ["after", "order"])], "disposition": "Root/Plan Integrator must synthesize current IE assembly authority with unchanged TE proof/commands and preserve input lineage; no SEIT edit/rerun by IE"},
    "input_bytes_verified": len(manifest["inputs"]), "code_runtime_checked": False,
}
(EVIDENCE / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
(EVIDENCE / "derived-issue-groups.json").write_text(json.dumps({"status": "prospective grouping only; not approved payload or remote write", "source_ref": "specialists/slice-graph.md", "groups": groups}, indent=2) + "\n")
lines = [f"{k}: PASS {report[k]}" for k in ["stable_steps", "stable_slices", "logical_issue_groups", "tdd_pairs", "resolved_used_commands", "unchanged_proof_cases", "source_dates_preserved", "frozen_capability_bindings_preserved", "historical_findings_preserved", "input_bytes_verified"]]
lines.extend(["DAG: PASS assembly + effective source graph; stable IE-P2-35 precedes IE-P2-34", "PROVENANCE: PASS lead-delta before/after chain; SEIT bytes unchanged; stale input/projection remains typed gap"])
(EVIDENCE / "validation.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
