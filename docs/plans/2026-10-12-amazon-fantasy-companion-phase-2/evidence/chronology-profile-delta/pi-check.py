#!/usr/bin/env python3
"""PI chronology-041 applied-delta checks over the regenerated implementation.json.

Deterministic; rerunnable. Writes pi-check.json next to this script. Exit 0 on PASS.
Compares conserved fields against the 51bc730 baseline implementation.json.
"""
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


def read(file):
    return json.loads((P / file).read_text())


def old(file):
    return json.loads(subprocess.check_output(["git", "show", f"{BASE}:{P / file}"]))


OSH_FULL = "7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1"
OSH_CFG = "11c4478edb7b0c94da196cdc8be2317f498378724ae041bde0c108832b1e2036"

impl, prior = read("implementation.json"), old("implementation.json")
seit = read("seit.json")
payload = read("evidence/github-work-items/github-work-items.json")
journey = json.loads(Path("docs/plans/2026-10-11-amazon-fantasy-companion/journey.json").read_text())
FS = journey["profile_selection"]["frozen_snapshots"]

# counts
check("52 slices", len(impl["slices"]) == 52)
check("39 groups", len(impl["work_issues"]["groups"]) == 39)
check("13 milestones", len(impl["milestones"]) == 13)
check("5 waves", len(impl["waves"]) == 5)
check("121 dependencies", len(impl["dependencies"]) == 121)
check("44 integration steps", len(impl["integration_plan"]["steps"]) == 44)
check("100 proofs", len(seit["proof_cases"]) == 100)
check("70 commands", len(seit["procedures_and_commands"]) == 70)
check("13 TDD pairs", sum(len(i["slices"]) == 2 for i in payload["issues"]) == 13)

# wave membership and release prerequisites conserved
check("wave slice_ids conserved",
      [(w["id"], w["slice_ids"]) for w in impl["waves"]] == [(w["id"], w["slice_ids"]) for w in prior["waves"]])
check("wave checkpoints W1..W5", [w["checkpoint"] for w in impl["waves"]] == ["W1", "W2", "W3", "W4", "W5"])
w2 = next(w for w in impl["waves"] if w["checkpoint"] == "W2")
check("W2 per-lane entry, no R1 cycle",
      "P2-X01 merged for P2-X04" in w2["entry"] and "P2-B01 merged" in w2["entry"]
      and "P2-A01 merged for P2-A02" in w2["entry"] and "no blanket P2-R1 prerequisite" in w2["entry"])
for rn in ("P2-R1", "P2-R2", "P2-R3", "P2-R4"):
    check(rn + " prerequisites conserved",
          {d["from"] for d in impl["dependencies"] if d["to"] == rn}
          == {d["from"] for d in prior["dependencies"] if d["to"] == rn})
check("release checkpoints and closing milestones",
      [(r["checkpoint"], r["milestone"], r["slice"], r["version"]) for r in impl["releases"]]
      == [("W1", "M03", "P2-R1", "v0.1.0"), ("W2", "M06", "P2-R2", "v0.2.0"),
          ("W3", "M10", "P2-R3", "v0.3.0"), ("W4", "M11", "P2-R4", "v0.4.0"),
          ("W5", "M13", "P2-R5", "v1.0.0")])

# milestone projection
pm = {m["id"]: m for m in payload["milestones"]}
check("milestone dues equal payload",
      all(m["due_on"] == pm[m["id"]]["due_on"] for m in impl["milestones"]))
pmap = {s: i["milestone"] for i in payload["issues"] for s in i["slices"]}
check("slice milestones equal payload mapping",
      all(s["milestone"] == pmap[s["id"]] for s in impl["slices"]))
check("X05 M04/Wave 1",
      next(s for s in impl["slices"] if s["id"] == "P2-X05")["milestone"] == "M04"
      and next(s for s in impl["slices"] if s["id"] == "P2-X05")["wave"] == "Wave 1")
x05r1 = next(d for d in impl["dependencies"] if (d["from"], d["to"]) == ("P2-X05", "P2-R1"))
check("X05->R1 sole forward edge via M04",
      "M04" in x05r1["condition"]
      and all(pmap[d["from"]] <= pmap[d["to"]] or (d["from"], d["to"]) == ("P2-X05", "P2-R1")
              for d in impl["dependencies"]))

# conserved per-slice fields vs baseline
pb = {s["id"]: s for s in prior["slices"]}
for s in impl["slices"]:
    b = pb[s["id"]]
    for k in ("write_set", "command_ids", "leases", "role", "work_class"):
        if s[k] != b[k]:
            raise ValueError(f"{s['id']} {k} changed")
checks.append("write_set/command_ids/leases/role/work_class conserved on 52 slices")
check("no absolute home path", "/home/" not in json.dumps(impl))
# IE-owned historical concurrency_findings keep their Mn tokens by IE instruction (Mn means Wn);
# everything else PI projects must use Wn or M01..M13.
_live = {k: v for k, v in impl.items() if k != "integration_plan"}
_live["integration_plan"] = {k: v for k, v in impl["integration_plan"].items() if k != "concurrency_findings"}
check("no stale wave token outside IE history",
      not re.search(r"(?<![\w-])M([1-5])(?!\d)", json.dumps(_live).replace("M01..M13", "")))

# profile projection
check("all slice lanes opensource-hackathon",
      {s["lane_profile"] for s in impl["slices"]} == {"opensource-hackathon"})
check("model route digests frozen",
      all(s["model_route"]["configuration_digest_sha256"] == OSH_CFG for s in impl["slices"]))
pf = impl["profile_freeze"]
check("freeze bindings equal journey", pf["bindings"] == FS)
check("freeze digests", pf["planning"]["full_profile_sha256"] == OSH_FULL
      and pf["planning"]["configuration_digest_sha256"] == OSH_CFG)
check("freeze lanes project", all(
      set(pf["lanes"][lane]) >= {"profile", "configuration_digest_sha256", "development_strategy",
                                 "concurrency", "planning_to_implementation_clean_session",
                                 "coverage_assist", "deterministic_verification", "holds"}
      for lane in ("tv-app-ui", "backend", "device-integration-spikes", "spec-and-docs", "defects")))
check("contributor-mode hold projected",
      any(h.get("id") == "muse-contributor-mode"
          and h.get("required_cli_args") == ["--contributor-mode", "on"]
          for h in pf["lanes"]["backend"]["holds"]))
check("observed lead preserved, no invented route",
      pf["observed_orchestrator"] == journey["profile_selection"]["observed_orchestrator"]
      and pf["observed_orchestrator"]["model"] == "not exposed by session metadata")
check("no stale lane profile lookup",
      "frozen_snapshots/primary\"" not in json.dumps(impl)
      and "frozen_snapshots/frontend\"" not in json.dumps(impl)
      and "frozen_snapshots/heavyweight\"" not in json.dumps(impl)
      and "frozen_snapshots/tech-writing\"" not in json.dumps(impl))
check("assurance enabled every lane",
      all(s["review_path"]["test_engineer_assurance"] == "lifecycle" for s in impl["slices"])
      and "lane_overrides" not in impl["journey_settings"]["assurance_cadence"]["test_engineer"])
check("reviewer route is frozen snapshot route",
      impl["journey_settings"]["planning_review"]["reviewer_slots"][0]["primary_route_ref"]
      == "Cursor Agent / Grok 4.7 / high")

# spent bounds
pr = impl["journey_settings"]["planning_review"]
check("spent bounds carried",
      pr["independent_review_rounds"] == "1/1 spent"
      and pr["aggregate_repair_rounds"] == "1/1 spent"
      and pr["additional_dispatch_authorized"] is False)
check("authority stays proposed/ineffective",
      read("authority.json")["effective"] is False and read("authority.json")["state"] == "proposed")

# manifest projection
man = impl["dod_manifest"]
check("manifest tasks cover 52 slices",
      {t["id"] for t in man["tasks"]} == {s["id"] for s in impl["slices"]})
check("manifest scope lists 13 milestones",
      len(man["scope"]) == 13 and all("issues in order" in line and "entry:" in line for line in man["scope"]))
check("manifest closeout grouped by wave",
      [v["id"] for v in man["vv"]] == ["VV-W1", "VV-W2", "VV-W3", "VV-W4", "VV-W5"]
      or [v["id"] for v in man["vv"]] == ["VV-W1", "VV-W2", "VV-W3", "VV-W4", "VV-W5", "VV-planning"])
check("manifest carries full profile hash", OSH_FULL in json.dumps(man["identity"]))

result = {"outcome": "PASS", "comparison_baseline": BASE, "checks": checks, "count": len(checks),
          "implementation_sha256": hashlib.sha256((P / "implementation.json").read_bytes()).hexdigest(),
          "candidate_digest": pr["candidate_digest"],
          "payload_sha256": hashlib.sha256((P / "evidence/github-work-items/github-work-items.json").read_bytes()).hexdigest(),
          "scope": "mechanical applied delta, not independent review or runtime acceptance"}
(OUT / "pi-check.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "checks"}, indent=2))
