#!/usr/bin/env python3
"""Cross-artifact conservation and chronology checks for the unapplied-to-runtime delta."""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

P = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
BASE = "51bc730a880105c9b21d37a7a2dc5da79ada875f"
OUT = P / "evidence/chronology-profile-delta"
checks = []


def check(name, value):
    if not value:
        raise ValueError(name)
    checks.append(name)


def old(file):
    return json.loads(subprocess.check_output(["git", "show", f"{BASE}:{P / file}"]))


def read(file):
    return json.loads((P / file).read_text())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def chronology(payload, impl):
    groups = {m["id"]: [] for m in payload["milestones"]}
    if list(groups) != [f"M{n:02}" for n in range(1, 14)]:
        raise ValueError("milestone identities")
    ids = [i["id"] for i in payload["issues"]]
    if len(ids) != 39 or len(set(ids)) != 39:
        raise ValueError("duplicate or missing issue")
    mapping = {}
    for issue in payload["issues"]:
        groups[issue["milestone"]].append(issue)
        for sid in issue["slices"]:
            if sid in mapping:
                raise ValueError("duplicate slice")
            mapping[sid] = issue["milestone"]
    if set(mapping) != {s["id"] for s in impl["slices"]}:
        raise ValueError("missing slice")
    if any(not 2 <= len(v) <= 6 for v in groups.values()):
        raise ValueError("milestone size outside 2..6")
    for dep in impl["dependencies"]:
        if mapping[dep["from"]] > mapping[dep["to"]] and (dep["from"], dep["to"]) != ("P2-X05", "P2-R1"):
            raise ValueError("untracked forward dependency")
    return groups, mapping


impl, prior = read("implementation.json"), old("implementation.json")
seit, old_seit = read("seit.json"), old("seit.json")
payload, old_payload = read("evidence/github-work-items/github-work-items.json"), old("evidence/github-work-items/github-work-items.json")
proposal = read("evidence/chronology-opus-review/proposal.json")
groups, mapping = chronology(payload, impl)
check("39issue52slice bijection and chronology", len(mapping) == 52)
check("exact issue counts per milestone", [len(v) for v in groups.values()] == [3, 2, 3, 4, 3, 3, 3, 3, 2, 2, 4, 4, 3])
check("13TDDpairs retained", sum(len(i["slices"]) == 2 for i in payload["issues"]) == 13)
check("proposal mapping applied", mapping == {sid: m["id"] for m in proposal["milestones"] for i in m["issues"] for sid in i["slices"]})
check("slice milestone projection agrees", all(s["milestone"] == mapping[s["id"]] for s in impl["slices"]))
check("same52slice identities", {s["id"] for s in impl["slices"]} == {s["id"] for s in prior["slices"]})
check("wave membership preserved", [(w["id"], w["slice_ids"]) for w in impl["waves"]] == [(w["id"], w["slice_ids"]) for w in prior["waves"]])
check("five release identities preserved", [(r["slice"], r["version"], r["publication"]) for r in impl["releases"]] == [(r["slice"], r["version"], r["publication"]) for r in prior["releases"]])
check("121dependency edges retained", len(impl["dependencies"]) == 121 and {(d["from"], d["to"]) for d in impl["dependencies"]} == {(d["from"], d["to"]) for d in prior["dependencies"]})
def normalized_condition(d):
    text = d.get("condition", "")
    if d["to"] in {"P2-R1", "P2-R2", "P2-R3", "P2-R4"}:
        text = text.replace("every other slice of the milestone", "every other slice of the technical wave")
    if (d["from"], d["to"]) == ("P2-X05", "P2-R1"):
        text = text.replace("M2", "M04")
    return re.sub(r"(?<![\w-])M([1-5])(?!\d)", r"W\1", text)
check("dependency conditions retain meaning", {(d["from"], d["to"]): normalized_condition(d) for d in impl["dependencies"]} == {(d["from"], d["to"]): normalized_condition(d) for d in prior["dependencies"]})
check("release condition labels identify technical waves", all("technical wave" in d["condition"] for d in impl["dependencies"] if d["to"] in {"P2-R1", "P2-R2", "P2-R3", "P2-R4"} and "every other slice" in d.get("condition", "")))
for release in ["P2-R1", "P2-R2", "P2-R3", "P2-R4"]:
    check(release + " retains all wave release prerequisites", {d["from"] for d in impl["dependencies"] if d["to"] == release} == {d["from"] for d in prior["dependencies"] if d["to"] == release})
check("100 proof identities and allocation retained", len(seit["proof_cases"]) == 100 and {(p["id"], p["requirement_id"], p["design_id"], p["command_id"], p["method"]) for p in seit["proof_cases"]} == {(p["id"], p["requirement_id"], p["design_id"], p["command_id"], p["method"]) for p in old_seit["proof_cases"]})
check("70command identities retained", len(seit["procedures_and_commands"]) == 70 and {c["id"] for c in seit["procedures_and_commands"]} == {c["id"] for c in old_seit["procedures_and_commands"]})
check("product register bytes unchanged", (P / "requirements-register.md").read_bytes() == subprocess.check_output(["git", "show", f"{BASE}:{P / 'requirements-register.md'}"]))
check("13milestone due times exactly proposal", [(m["id"], m["due_on"]) for m in payload["milestones"]] == [(m["id"], m["due_on"]) for m in proposal["milestones"]])
check("no invented due time", all(m["due_on"] in canonical(prior) for m in payload["milestones"]))
check("final ready and deadline unchanged", payload["milestones"][-1]["due_on"] == "2026-10-23T12:00:00Z" and impl["journey_settings"]["deadline"] == "2026-10-23T19:00:00Z")
for before, after in zip(old_payload["issues"], payload["issues"]):
    if before["id"] == "P2-R1":
        for dep in before["dependency_groups"]:
            if dep["issue_group"] == "P2-X05":
                dep["condition"] = dep["condition"].replace("belongs to M2", "belongs to M04")
    check(after["id"] + " preserves scope bindings", all(before[k] == after[k] for k in ["id", "slices", "dependency_groups", "requirement_ids", "proof_rows", "conditional", "stable_id", "kind"]))
    check(after["id"] + " mirror and digest", (P / after["body_file"]).read_text() == after["body"] and hashlib.sha256(after["body"].encode()).hexdigest() == after["body_sha256"])
check("X11 remains conditional", next(i for i in payload["issues"] if i["id"] == "P2-X11")["conditional"] is True)
check("product authority stays ineffective", read("authority.json")["effective"] is False)
check("44 integration identities and predecessors retained", len(impl["integration_plan"]["steps"]) == 44 and [(s["id"], s["order"], s["merges"], s["after"]) for s in impl["integration_plan"]["steps"]] == [(s["id"], s["order"], s["merges"], s["after"]) for s in prior["integration_plan"]["steps"]])
check("all step milestones match proposal", all(s["milestone"] == proposal["integration_step_milestone"][s["id"]].split()[0] for s in impl["integration_plan"]["steps"]))
profile = read("evidence/profile-migration-041/profile.json")
binding = seit["frozen_profile_binding"]["opensource-hackathon"]
check("SEIT full profile including capabilities and holds", binding["snapshot"] == profile)
check("SEIT bug-triager unchanged", seit["frozen_profile_binding"]["bug-triager"] == old_seit["frozen_profile_binding"]["bug-triager"])
def contains_full_profile(value):
    if isinstance(value, dict):
        return all(value.get(k) == v for k, v in profile.items()) or any(contains_full_profile(v) for v in value.values())
    return isinstance(value, list) and any(contains_full_profile(v) for v in value)
check("implementation embeds entire selected profile", contains_full_profile(impl))
check("authoring baseline agrees with SEIT", impl["source_baseline"]["revision"] == seit["source_baseline"]["revision"] == impl["journey_settings"]["planning_review"]["candidate_revision"])
check("no inherited docs strategy override", impl["journey_settings"]["development_strategy"]["mode"] == "tdd" and impl["journey_settings"]["development_strategy"]["lane_overrides"]["spec-and-docs"] != "single_implementer")
check("docs inspection is not a profile override", all(s["development_strategy"] != "single_implementer" for s in impl["slices"] if s["lane"] == "spec-and-docs"))
for sl in impl["slices"]:
    route = sl["model_route"]
    selected = profile["roles"][route["snapshot_role"]]
    check(sl["id"] + " frozen route and fallback order", route["snapshot_profile"] == "opensource-hackathon" and all(route[k] == selected["primary"][k] for k in ["harness", "model", "reasoning"]) and route["ordered_fallbacks"] == selected["ordered_fallbacks"])
    review = sl["review_path"]
    check(sl["id"] + " review and assurance binding", all(review["reviewer_route"][k] == profile["roles"]["reviewer"]["primary"][k] for k in ["harness", "model", "reasoning"]) and review["test_engineer_assurance"] == "lifecycle")
    check(sl["id"] + " installed skill version", "1.1.6" not in canonical(sl["skills"] + review["skills"]))
for missing in ["review", "deterministic_verification", "holds"]:
    bad_profile = copy.deepcopy(profile)
    bad_profile.pop(missing)
    check("reject omitted " + missing, not contains_full_profile(bad_profile))
negative_results = []
for label, mutation in [("duplicate issue", lambda p: p["issues"].append(copy.deepcopy(p["issues"][0]))),
                        ("missing issue", lambda p: p["issues"].pop()),
                        ("out-of-range count", lambda p: [i.update(milestone="M01") for i in p["issues"][:8]])]:
    bad = copy.deepcopy(payload)
    mutation(bad)
    try:
        chronology(bad, impl)
    except ValueError as error:
        negative_results.append({"case": label, "outcome": "rejected", "reason": str(error)})
    else:
        raise ValueError("negative accepted: " + label)
result = {"outcome": "PASS", "comparison_baseline": BASE, "checks": checks,
          "negative_cases": negative_results, "count": len(checks),
          "payload_sha256": hashlib.sha256((P / "evidence/github-work-items/github-work-items.json").read_bytes()).hexdigest(),
          "scope": "mechanical applied delta, not independent review or runtime acceptance"}
(OUT / "conservation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "checks"}, indent=2))
