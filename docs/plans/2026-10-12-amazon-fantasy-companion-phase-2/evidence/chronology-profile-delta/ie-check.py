#!/usr/bin/env python3
"""Verify the IE chronology/profile projection against baseline 51bc730.

Run from the repository root. Writes ie-check.json next to this file and
exits 1 if any check fails.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = "51bc730a880105c9b21d37a7a2dc5da79ada875f"
PLAN = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
GRAPH = "specialists/slice-graph.md"
IEP = "specialists/integration-plan.md"
OUT = PLAN / "evidence/chronology-profile-delta/ie-check.json"
PROPOSAL = json.loads((PLAN / "evidence/chronology-opus-review/proposal.json").read_text())
JOURNEY = json.loads(Path("docs/plans/2026-10-11-amazon-fantasy-companion/journey.json").read_text())
FS = JOURNEY["profile_selection"]["frozen_snapshots"]
FULL_SHA = "7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1"

old_g = subprocess.run(["git", "show", f"{BASE}:{PLAN / GRAPH}"], check=True, capture_output=True, text=True).stdout
old_i = subprocess.run(["git", "show", f"{BASE}:{PLAN / IEP}"], check=True, capture_output=True, text=True).stdout
new_g = (PLAN / GRAPH).read_text()
new_i = (PLAN / IEP).read_text()

results = []


def check(cid, ok, detail):
    results.append({"id": cid, "result": "PASS" if ok else "FAIL", "detail": detail})


def table(text, first):
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if l.startswith(f"| {first} |") and re.match(r"^\|[\s\-|:]+\|\s*$", lines[i + 1]):
            hdr = [c.strip() for c in l.strip().strip("|").split("|")]
            rows = []
            for r in lines[i + 2:]:
                if not r.startswith("|"):
                    break
                rows.append(dict(zip(hdr, [c.strip() for c in r.strip().strip("|").split("|")])))
            return hdr, rows
    raise AssertionError(first)


oh, orows = table(old_g, "ID")
nh, nrows = table(new_g, "ID")
_, oarr = table(old_g, "Arrow")
_, narr = table(new_g, "Arrow")
O = {r["ID"]: r for r in orows}
N = {r["ID"]: r for r in nrows}
check("G01-slice-count", len(O) == len(N) == 52 and list(O) == list(N), f"old {len(O)} new {len(N)}, same order")

old_ms = {s: r["M, wave"].split(",")[0].strip() for s, r in O.items()}
old_w = {s: r["M, wave"].split(",")[1].strip() for s, r in O.items()}
new_ms = {s: r["GitHub milestone, wave"].split(",")[0].strip() for s, r in N.items()}
new_w = {s: r["GitHub milestone, wave"].split(",")[1].strip() for s, r in N.items()}
check("G02-wave-membership-unchanged", old_w == new_w, "wave column identical for 52 slices")

PMS = {}
for m in PROPOSAL["milestones"]:
    for i in m["issues"]:
        for s in i["slices"]:
            PMS[s] = m["id"]
check("G03-github-milestone-from-proposal", new_ms == PMS, "each slice's milestone equals proposal issue group milestone")

issues = [(i["issue"], tuple(i["slices"]), m["id"]) for m in PROPOSAL["milestones"] for i in m["issues"]]
per = {}
for _, _, m in issues:
    per[m] = per.get(m, 0) + 1
pairs = [s for s in N if s.endswith("T") and s[:-1] in N]
check("G04-issue-grouping",
      len(issues) == 39 and len(per) == 13 and all(2 <= v <= 6 for v in per.values())
      and per == PROPOSAL["counts"]["per_milestone"] and len(pairs) == 13
      and all(new_ms[p] == new_ms[p[:-1]] for p in pairs)
      and sorted(s for _, ss, _ in issues for s in ss) == sorted(N),
      f"39 issues, 13 milestones {per}, 13 TDD pairs share milestone, every slice once")

FIXED = ["Lane / role / class", "Register UIDs", "AC / RISK", "Spec §", "Design", "Write set", "Commands", "Leases", "Skills"]
diff_fixed = [(s, c) for s in O for c in FIXED if O[s][c] != N[s][c]]
check("G05-fixed-columns-unchanged", not diff_fixed, f"{', '.join(FIXED)} identical; diffs={diff_fixed}")

WTOK = re.compile(r"(?<![-\w.])M([1-5])(?![\w.])")


def wave_words(x):
    x = re.sub(r"every other M([1-5]) slice", r"every other Wave \1 slice", x)
    x = re.sub(r"All M([1-5]) slices", r"All Wave \1 slices", x)
    x = re.sub(r"M([1-5]) entry", r"Wave \1 entry", x)
    return WTOK.sub(r"W\1", x).replace("M1..M5", "M01..M13")


SPECIAL = {
    "PR 1 (W1):": "PR 1 (W1 early checkpoint CP-X05-HIST; feeds P2-R1 in M03 and P2-B02 in M05):",
    "PR 2 (W2):": "PR 2 (closes the issue in GitHub milestone M04; final verdict by the W2 exit):",
    "at the W3 backend head": "at the Wave 3 backend head",
}


def expected(cell):
    x = wave_words(cell)
    for k, v in SPECIAL.items():
        x = x.replace(k, v)
    return x


cell_diff = [(s, c) for s in O for c in ("Goal; stop when", "Depends on") if expected(O[s][c]) != N[s][c]]
goal_diff = sorted(s for s in O if O[s]["Goal; stop when"] != N[s]["Goal; stop when"])
dep_diff = sorted(s for s in O if O[s]["Depends on"] != N[s]["Depends on"])
check("G06-goal-depends-token-only", not cell_diff,
      f"goal/depends cells equal baseline after Mn->Wn/Wave n, M1..M5->M01..M13 and 3 named X05/L03 phrases; "
      f"changed goals {goal_diff}; changed depends {dep_diff}; unexpected={cell_diff}")
check("G07-release-depends-wave", all(f"every other Wave {n} slice merged" in N[f"P2-R{n}"]["Depends on"] for n in "1234")
      and N["P2-X11"]["Depends on"] == "W3 exit; OD-AFC-03 = yes" and N["P2-SCR1"]["Depends on"] == "W4 exit",
      "R1..R4 depend on every other Wave n slice; X11 W3 exit; SCR1 W4 exit")


def arrows(rows):
    out = {}
    for r in rows:
        a, b = [x.strip() for x in r["Arrow"].strip("`").split("-->")]
        out[(a, b)] = r["Condition"]
    return out


OA, NA = arrows(oarr), arrows(narr)
changed_cond = {k for k in OA if OA[k] != NA.get(k)}
check("G08-arrows-unchanged", set(OA) == set(NA) and len(OA) == 81 and changed_cond == {("P2-X05", "P2-R1")}
      and NA[("P2-X05", "P2-R1")] == OA[("P2-X05", "P2-R1")].replace("belongs to M2", "belongs to M04"),
      "81 arrows; only X05->R1 condition token M2->M04")


def deps(arr, member):
    d = {k: v for k, v in arr.items()}
    for n in "1234":
        r = f"P2-R{n}"
        for s in member:
            if member[s] == member[r] and s != r and (s, r) not in d:
                d[(s, r)] = "merged (every other slice of the wave)"
    return d


OD = deps(OA, old_ms)
ND = deps(NA, new_w)
check("G09-121-dependencies", len(OD) == len(ND) == 121 and set(OD) == set(ND),
      f"old {len(OD)} (milestone-derived) new {len(ND)} (wave-derived); identical edge set")
bad_rel = [f"P2-R{n}" for n in "1234" if not all((s, f"P2-R{n}") in ND for s in N if new_w[s] == f"W{n}" and s != f"P2-R{n}")]
check("G10-release-prereqs-from-wave", not bad_rel, "R1..R4 follow every other slice of their technical wave")

adj = {}
for a, b in ND:
    adj.setdefault(a, set()).add(b)


def reach(src):
    seen, st = set(), [src]
    while st:
        x = st.pop()
        for y in adj.get(x, ()):
            if y not in seen:
                seen.add(y)
                st.append(y)
    return seen


cyc = [s for s in N if s in reach(s)]
check("G11-acyclic-and-x04-not-after-r1", not cyc and "P2-X04" not in reach("P2-R1")
      and "P2-R1" in reach("P2-X04"),
      "no cycle; X04 does not wait for R1; X04 precedes R1 via A01 review")
check("G12-x05-checkpoint",
      new_ms["P2-X05"] == "M04" and new_w["P2-X05"] == "W1" and "PR 1 historical-fixture checkpoint" in NA[("P2-X05", "P2-R1")]
      and "CP-X05-HIST" in N["P2-X05"]["Goal; stop when"] and "P2-B02 in M05" in N["P2-X05"]["Goal; stop when"],
      "X05 issue closes M04; CP-X05-HIST feeds R1 (M03) and B02 (M05)")
check("G13-wave2-entry-clarified", "P2-X04 does not wait for P2-R1" in new_g and "Wave 2 entry is per lane" in new_g
      and ("Wave 2\nentry is per lane" in new_i or "Wave 2 entry is per lane" in new_i),
      "slice graph and integration plan state per-lane Wave 2 entry")
check("G14-x11-conditional", "Conditional (OD-AFC-03 = yes and W3 on time)" in N["P2-X11"]["Goal; stop when"]
      and new_ms["P2-X11"] == "M11", "X11 remains conditional in M11")

# ---- integration plan JSON
blk = lambda t: json.loads(re.search(r"```json integration_plan\n(.*)\n```", t, re.S).group(1))
OB, NB = blk(old_i), blk(new_i)
os_, ns = OB["steps"], NB["steps"]
check("I01-step-ids-order", [s["id"] for s in os_] == [s["id"] for s in ns] and len(ns) == 44
      and all(a["order"] == b["order"] and a["merges"] == b["merges"] and a["after"] == b["after"] for a, b in zip(os_, ns)),
      "44 steps; id, order, merges, after identical")
SM = PROPOSAL["integration_step_milestone"]
check("I02-step-milestone-wave", all(b["milestone"] == SM[b["id"]].split(" ")[0] and b["wave"] == "Wave " + a["milestone"][1]
                                     for a, b in zip(os_, ns)),
      "milestone from proposal integration_step_milestone; wave = old milestone number")
mis = [(st["id"], sl) for st in ns for sl in st["merges"] if PMS[sl] != st["milestone"]]
check("I03-step-slice-milestone-consistent", not mis, f"merged slices share their step's GitHub milestone; mismatches={mis}")

text_diff = []
for a, b in zip(os_, ns):
    for k in ("entry_criteria", "post_step_vv", "rollback", "exit"):
        exp = json.loads(wave_words(json.dumps(a.get(k), ensure_ascii=False)))
        if exp != b.get(k):
            text_diff.append((a["id"], k))
check("I04-step-text-token-only", not text_diff, f"step text equals baseline after Mn->Wn/Wave n mapping; diffs={text_diff}")

oc, nc = OB["cutoffs"], NB["cutoffs"]
check("I05-cutoffs", [c["id"] for c in oc] == [c["id"] for c in nc] and [c["time"] for c in oc] == [c["time"] for c in nc]
      and all(c["applies_to"] == wave_words(o["applies_to"]) for o, c in zip(oc, nc)),
      "14 cut-off IDs and times unchanged; CO-Mn apply to Wn")
og, ng = OB["wave_gate_costs"], NB["wave_gate_costs"]
keep = ["wave", "integration_steps", "slices", "added_gate_seconds", "resource_groups", "seit_case_resource_groups",
        "resource_case_refs", "qualification_ref", "estimate_source", "estimate_text"]
check("I06-wave-gate-costs", all(all(o[k] == n[k] for k in keep) and n["release_checkpoint"] == "W%d" % o["wave"]
                                 and n["github_milestones"] == sorted({PMS[s] for s in o["slices"]}) for o, n in zip(og, ng))
      and [n["added_gate_seconds"] for n in ng] == [720, 900, 2100, 0, 120],
      "gate costs, resource groups, steps and slices unchanged; W1..W5 checkpoints")
check("I07-unchanged-sections", all(OB[k] == NB[k] for k in ("branches", "worktrees", "authorized_glue", "stubs",
                                                             "anomaly_rollback_recovery", "final_candidate",
                                                             "concurrency_findings")),
      "branches, worktrees, glue, stubs, anomaly, final_candidate, historical concurrency_findings identical")
check("I08-leases-and-x05-x11", NB["cutoffs"][0]["time"] == "2026-10-14T03:15:00Z"
      and any(s["id"] == "IE-P2-6" and s["milestone"] == "M04" and "CP-X05-HIST" in s["milestone_note"] for s in ns)
      and [s["id"] for s in ns].index("IE-P2-35") < [s["id"] for s in ns].index("IE-P2-34"),
      "CO-STICK-START unchanged; early X05 checkpoint IE-P2-6 noted; IE-P2-35 before IE-P2-34")

# ---- profile binding
osh = FS["opensource-hackathon"]
recomputed = hashlib.sha256(json.dumps(osh["snapshot"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
fcb = NB["configuration_identity"]["frozen_capability_binding"]
b = fcb["opensource-hackathon"]


def route(r):
    return f"{r['harness']} / {r['model']} / {r['reasoning']}"


exp_routes = {}
for name, v in osh["snapshot"]["roles"].items():
    for key, sv in ([(f"{name}.{s}", sv) for s, sv in v["sessions"].items()] if "sessions" in v else [(name, v)]):
        e = {"enabled": sv["enabled"], "primary": route(sv["primary"]),
             "ordered_fallbacks": [route(f) for f in sv.get("ordered_fallbacks", [])]}
        if "cadence" in sv:
            e["cadence"] = sv["cadence"]
        exp_routes[key] = e
check("P01-full-profile-sha", recomputed == FULL_SHA == osh["full_profile_sha256"] == b["full_profile_sha256"]
      and b["configuration_digest_sha256"] == osh["configuration_digest_sha256"],
      f"sha256(compact sorted snapshot) = {recomputed}")
check("P02-role-routes", b["role_routes"] == exp_routes and len(exp_routes) == 13,
      "13 role/session routes with ordered fallbacks and cadences equal frozen snapshot")
check("P03-capabilities", b["review"] == {"coverage_assist": {"enabled": True, "required": True}}
      and b["deterministic_verification"] == {"reverify": {"enabled": True}}
      and b["development_strategy"] == {"mode": "tdd"} and b["concurrency"] == osh["concurrency"]
      and b["planning_to_implementation_clean_session"] is True and b["holds"] == osh["holds"]
      and exp_routes["reviewer"]["cadence"] == "phase",
      "coverage_assist required, reverify enabled, tdd, concurrency, clean session, holds, reviewer cadence phase")
check("P04-bug-triager-unchanged", fcb["bug-triager"] == OB["configuration_identity"]["frozen_capability_binding"]["bug-triager"]
      and fcb["bug-triager"]["configuration_digest_sha256"] == FS["bug-triager"]["configuration_digest_sha256"],
      "bug-triager binding byte-identical and matches journey digest")
check("P05-lanes", set(fcb["lane_profiles"].values()) == {"opensource-hackathon", "bug-triager"}
      and fcb["lane_profiles"]["defects"] == "bug-triager"
      and "tv-app-ui = frontend" not in new_g and "`primary.scribe`" not in new_g
      and all(x not in json.dumps(NB["configuration_identity"]) for x in ("b81a141b", "8e533b92", "f2c555d5", "8a6b5745")),
      "all lanes opensource-hackathon, defects bug-triager; old lane digests absent from binding")
sess = NB["lifecycle_assessment_inputs"]["sessions"]
roles = osh["snapshot"]["roles"]
check("P06-assurance-all-lanes", "assurance is disabled" not in sess and "no longer applies" in sess
      and route(roles["test_engineer"]["sessions"]["assurance"]["primary"]) in sess
      and route(roles["integration_engineer"]["sessions"]["execution"]["primary"]) in sess
      and all(route(f) in sess for f in roles["test_engineer"]["sessions"]["assurance"]["ordered_fallbacks"]),
      "IE execution and ATE routes from opensource-hackathon cover every lane; tech-writing exemption removed")
check("P07-muse-contributor-mode", "--contributor-mode on" in new_g and "--contributor-mode on" in sess,
      "Muse primary/fallback --contributor-mode on stated in graph and assessment sessions")
check("P08-skill-paths-1.1.7", new_g.count("bearing-lite/1.1.7/skills/") == 4 and "bearing-lite/1.1.6/skills/" not in new_g
      and all((Path.home() / f".claude/plugins/cache/bearing-lite/bearing-lite/1.1.7/skills/{s}/SKILL.md").exists()
              for s in ("implementer", "light-implementer", "scribe", "reviewer")),
      "bearing-lite skill paths moved to installed 1.1.7")
left_g = [m.group(0) for m in WTOK.finditer(new_g)]
cf0, wg0 = new_i.index('"concurrency_findings": ['), new_i.index('"wave_gate_costs": [')
left_i = [m.group(0) for m in WTOK.finditer(new_i[:cf0] + new_i[wg0:])]
check("T01-no-stale-wave-tokens", not left_g and not left_i, f"graph {left_g}; plan outside historical findings {left_i}")
check("T02-home-paths", "/ho" + "me/" not in new_g + new_i, "no absolute home path")

fails = [r for r in results if r["result"] != "PASS"]
OUT.write_text(json.dumps({"baseline": BASE, "checks": results, "pass": len(results) - len(fails), "fail": len(fails),
                           "sha256": {GRAPH: hashlib.sha256(new_g.encode()).hexdigest(),
                                      IEP: hashlib.sha256(new_i.encode()).hexdigest()}}, indent=2) + "\n")
for r in results:
    print(r["result"], r["id"], "-", r["detail"][:160])
print(f"{len(results) - len(fails)}/{len(results)} PASS")
sys.exit(1 if fails else 0)
