#!/usr/bin/env python3
"""Checks the TE chronology/profile delta in seit.json against 51bc730. Read-only except te-check.json.

Run from the repository root:
    python3 docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/chronology-profile-delta/te-check.py
"""
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import jsonschema

BASE = "51bc730a880105c9b21d37a7a2dc5da79ada875f"
PLAN = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
SEIT = PLAN / "seit.json"
OUT = PLAN / "evidence/chronology-profile-delta/te-check.json"
SCHEMA = Path.home() / ".claude/plugins/cache/bearing-lite/bearing-lite/1.1.7/schemas/seit.schema.json"
D3 = "GitHub milestones in order (D3; create only after approval)"

old = json.loads(subprocess.run(["git", "show", f"{BASE}:{SEIT}"], check=True, capture_output=True).stdout)
new = json.loads(SEIT.read_text())
payload_path = PLAN / "evidence/github-work-items/github-work-items.json"
payload = json.loads(payload_path.read_text())
proposal = json.loads((PLAN / "evidence/chronology-opus-review/proposal.json").read_text())
journey = json.loads(Path("docs/plans/2026-10-11-amazon-fantasy-companion/journey.json").read_text())
tp = (PLAN / "amazon-fantasy-companion-phase-2-technical-plan.md").read_text()
ie = json.loads(re.search(r"```json integration_plan\n(.*)\n```", (PLAN / "specialists/integration-plan.md").read_text(), re.S).group(1))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
results, changes = [], collections.defaultdict(list)


def check(cid, ok, detail):
    results.append({"id": cid, "outcome": "PASS" if ok else "FAIL", "detail": detail})


def diff(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(f"{path}/{k} (added)")
            elif k not in b:
                out.append(f"{path}/{k} (removed)")
            else:
                diff(a[k], b[k], f"{path}/{k}", out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and not all(isinstance(x, str) for x in a + b):
        for i, (x, y) in enumerate(zip(a, b)):
            diff(x, y, f"{path}/{i}", out)
    elif a != b:
        out.append(path)


# 1 schema
errs = sorted(e.message for e in jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(new))
check("S01-seit-schema-1.1.7", not errs, f"{SCHEMA.name} sha256 {sha(SCHEMA)}; errors={errs[:5]}")

# 2 stable IDs and counts
ids = lambda d, k, f="id": [x[f] for x in d[k]]
same = {k: ids(old, k, f) == ids(new, k, f) for k, f in [("proof_cases", "id"), ("procedures_and_commands", "id"),
        ("cross_cutting_checks", "id"), ("traceability_matrix", "SEIT row ID"), ("integration_vv_sequence", "step")]}
counts = {"proof_cases": len(new["proof_cases"]), "procedures_and_commands": len(new["procedures_and_commands"]),
          "required_commands": len(new["required_commands"]), "traceability_matrix": len(new["traceability_matrix"]),
          "integration_vv_sequence": len(new["integration_vv_sequence"]), "levels": len(new["levels"]),
          "wave_gate_costs": len(new["wave_gate_costs"])}
check("S02-stable-ids-and-counts", all(same.values()) and old["required_commands"] == new["required_commands"]
      and counts == {"proof_cases": 100, "procedures_and_commands": 70, "required_commands": 27, "traceability_matrix": 100,
                     "integration_vv_sequence": 44, "levels": 5, "wave_gate_costs": 5},
      f"identical id order {same}; counts {counts}")

# 3 proof cases: every changed field enumerated; product (PR) rows only the W3 token
OP, NP = {p["id"]: p for p in old["proof_cases"]}, {p["id"]: p for p in new["proof_cases"]}
FIXED = ["kind", "requirement_id", "design_id", "command_id", "method", "preconditions", "observable_evidence",
         "boundary_test_layer", "closing_slice", "supporting_slices", "execution_status", "resource_group", "expected_gate_seconds"]
fixed_bad = [(i, f) for i in OP for f in FIXED if OP[i].get(f) != NP[i].get(f)]
for i in OP:
    out = []
    diff(OP[i], NP[i], "", out)
    if out:
        changes["proof_cases/" + i] = out
pr_bad = []
pr_rows = [i for i in OP if i.startswith("SEIT-AFC-PR-")]
for i in OP:
    if i.startswith("SEIT-AFC-PR-"):
        o = json.loads(json.dumps(OP[i]).replace("X11 conditional after M3", "X11 conditional after W3"))
        if o != NP[i]:
            pr_bad.append(i)
allowed_text = {"SEIT-AFC-P2-MS-01": {"/stimulus_or_procedure", "/expected_result", "/pass_fail_rule", "/negative_or_failure_case"},
                "SEIT-AFC-P2-REL-02": {"/stimulus_or_procedure", "/expected_result"},
                "SEIT-RISK-AFC-P2-13": {"/stimulus_or_procedure"}}
core_bad = [(i, f) for i in OP for f in ("stimulus_or_procedure", "expected_result", "pass_fail_rule", "negative_or_failure_case")
            if OP[i][f] != NP[i][f] and "/" + f not in allowed_text.get(i, set())]
pos_neg_ok = all(OP[i]["negative_or_failure_case"] == NP[i]["negative_or_failure_case"] for i in OP if i != "SEIT-AFC-P2-MS-01")
check("P01-proof-allocations-and-assertions", not fixed_bad and not pr_bad and not core_bad and pos_neg_ok,
      f"{len(OP)} proofs: {len(FIXED)} allocation/identity fields identical; {len(pr_rows)} product PR rows equal baseline after the "
      f"W3 token only; assertion text changed only in MS-01/REL-02/RISK-13; negatives unchanged except MS-01 "
      f"(fixed_bad={fixed_bad}, pr_bad={pr_bad}, core_bad={core_bad})")
check("P02-product-row-count", len(pr_rows) == 63, f"{len(pr_rows)} SEIT-AFC-PR rows; {sum(1 for i in pr_rows if 'proof_cases/'+i in changes)} carry only the X11 W3 token")

# 4 commands
OC, NC = {c["id"]: c for c in old["procedures_and_commands"]}, {c["id"]: c for c in new["procedures_and_commands"]}
cmd_fixed_bad = [(i, f) for i in OC for f in ("command", "used_by", "execution_status", "read_only_commands",
                                              "helper_dry_run_command", "helper_submit_command") if OC[i].get(f) != NC[i].get(f)]
for i in OC:
    out = []
    diff(OC[i], NC[i], "", out)
    if out:
        changes["procedures_and_commands/" + i] = out
expected_cmd = {"CMD-MILESTONES-CREATE", "CMD-MILESTONES-READBACK", "PROC-TRACKING-SETUP", "CMD-STUB-SCAN", "PROC-VISUAL-REVIEW",
                "CMD-CHANGELOG-CHECK", "CMD-RELEASE-PREP"}
changed_cmd = {k.split("/", 1)[1] for k in changes if k.startswith("procedures_and_commands/")}
check("C01-commands", not cmd_fixed_bad and changed_cmd == expected_cmd,
      f"70 commands; executable command/used_by/status identical; text changed only in {sorted(changed_cmd)}")

# 5 traceability
OT, NT = {r["SEIT row ID"]: r for r in old["traceability_matrix"]}, {r["SEIT row ID"]: r for r in new["traceability_matrix"]}
tchg = sorted((i, k) for i in OT for k in OT[i] if OT[i][k] != NT[i][k])
check("T01-traceability", tchg == [("SEIT-AFC-P2-MS-01", "Negative/failure case"), ("SEIT-AFC-P2-MS-01", "Positive case"),
                                   ("SEIT-AFC-P2-REL-02", "Positive case")]
      and all(NT[i]["Positive case"] == NP[i]["expected_result"] and NT[i]["Negative/failure case"] == NP[i]["negative_or_failure_case"]
              for i in ("SEIT-AFC-P2-MS-01", "SEIT-AFC-P2-REL-02")),
      f"columns/IDs/allocations unchanged; changed cells {tchg} mirror the proof rows")

# 6 levels, gate costs, steps, timestamps
keep_lv = ["wave", "title", "due_utc", "levels", "slices", "integration_steps", "evidence_focus", "expected_gate_time_delta",
           "added_gate_seconds", "resource_groups", "due_explanation"]
lv_ok = all(all(o[k] == n[k] for k in keep_lv) and n["release_checkpoint"] == f"W{o['wave']}" and "milestone" not in n
            and n["github_milestones"] for o, n in zip(old["levels"], new["levels"]))
keep_w = ["wave", "integration_steps", "slices", "added_gate_seconds", "estimate_source", "estimate_text", "resource_groups",
          "seit_case_resource_groups", "resource_case_refs", "qualification_ref"]
IEW = {w["wave"]: w for w in ie["wave_gate_costs"]}
w_ok = all(all(o[k] == n[k] for k in keep_w) and n["release_checkpoint"] == f"W{o['wave']}"
           and n["github_milestones"] == IEW[o["wave"]]["github_milestones"] for o, n in zip(old["wave_gate_costs"], new["wave_gate_costs"]))
check("G01-levels-and-gate-costs", lv_ok and w_ok and [w["added_gate_seconds"] for w in new["wave_gate_costs"]] == [720, 900, 2100, 0, 120]
      and [l["due_utc"] for l in new["levels"]] == ["2026-10-14T23:00:00Z", "2026-10-17T01:00:00Z", "2026-10-19T12:00:00Z",
                                                     "2026-10-21T23:00:00Z", "2026-10-23T12:00:00Z"],
      "W1..W5 dues, slices, steps, resource groups and gate seconds 720/900/2100/0/120 unchanged; Mn key -> release_checkpoint Wn")
IE = {s["id"]: s for s in ie["steps"]}
st_keep = ["step", "wave", "order", "after", "slices", "proof_rows", "command_ids", "rollback_ref", "note"]
st_bad = [o["step"] for o, n in zip(old["integration_vv_sequence"], new["integration_vv_sequence"])
          if any(o.get(k) != n.get(k) for k in st_keep) or n["milestone"] != IE[o["step"]]["milestone"]
          or n["release_checkpoint"] != f"W{o['wave']}"]
check("I01-integration-steps", not st_bad, f"44 steps: order/after/slices/proofs/commands unchanged; milestone = IE GitHub milestone; bad={st_bad}")
TS = re.compile(r"20\d\d-\d\d-\d\dT\d\d:\d\d(?::\d\d)?Z")
old_ts, new_ts = set(TS.findall(json.dumps(old))), set(TS.findall(json.dumps(new)))
check("G02-cutoffs-and-live-windows", old_ts <= new_ts, f"every baseline UTC time still present ({len(old_ts)}); missing={sorted(old_ts - new_ts)}")
co = lambda d: sorted(set(re.findall(r"CO-[A-Z0-9-]+", json.dumps(d))))
check("G03-cutoff-ids", co(old) == co(new), f"cut-off IDs referenced in SEIT unchanged ({len(co(new))}; CO-* cut-offs are carried by integration-plan.md, not SEIT)")

# 7 tracking
tw = new["tracking_workflow"]
pm = {m["id"]: m for m in payload["milestones"]}
sec = tp.split("### " + D3, 1)[1].split("\n### ", 1)[0]
rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in sec.splitlines() if re.match(r"\| M\d\d \|", ln)]
table_ok = (tw["milestones"] == 13 == len(tw["milestone_table"]) == len(rows) == len(payload["milestones"])
            and all((m["id"], m["title"], m["due_on"]) == (r[0], r[1], r[2]) == (pm[r[0]]["id"], pm[r[0]]["title"], pm[r[0]]["due_on"])
                    and m["github_due_date"] == r[2][:10] and m["issues_in_order"] == [x.strip() for x in r[5].split(",")]
                    for m, r in zip(tw["milestone_table"], rows)))
check("K01-milestone-table", table_ok, "13 rows equal technical-plan D3 table and payload (id, title, due_on, issues in order)")
allsl = [s for g in tw["groups"] for s in g["slices"]]
per = collections.Counter(g["milestone"] for g in tw["groups"])
pi = {i["id"]: i for i in payload["issues"]}
check("K02-groups", len(tw["groups"]) == 39 and len(allsl) == 52 == len(set(allsl))
      and all(g["milestone"] == pi[g["issue"]]["milestone"] and g["slices"] == pi[g["issue"]]["slices"] for g in tw["groups"])
      and dict(per) == proposal["counts"]["per_milestone"] and sum(1 for g in tw["groups"] if len(g["slices"]) == 2) == 13
      and [g["issue"] for g in tw["groups"]] == [g["issue"] for g in old["tracking_workflow"]["groups"]]
      and all(go["slices"] == gn["slices"] for go, gn in zip(old["tracking_workflow"]["groups"], tw["groups"])),
      f"39 groups, 52 slices once, 13 pairs, group order/slices unchanged, per-milestone {dict(sorted(per.items()))} = proposal")
psha = sha(payload_path)
ms = NP["SEIT-AFC-P2-MS-01"]["method_fields"]
check("K03-payload-binding", tw["payload_sha256"] == psha and ms["tracking_evidence"] == tw
      and NC["PROC-TRACKING-SETUP"]["tracking_payload_sha256"] == psha
      and NC["PROC-TRACKING-SETUP"]["tracking_payload_ref"] == tw["payload_ref"] == str(payload_path)
      and psha in tw["filing_scope"]["payload_note"] and "f485d8f6" not in json.dumps({k: v for k, v in tw.items() if k != "filing_scope"})
      and all(sha(f) == h for f, h in tw["filing_scope"]["evidence"].items()),
      f"tracking_workflow, MS-01 copy and PROC-TRACKING-SETUP bind {payload_path.name} sha256 {psha}; filing evidence hashes current")
check("K04-no-fixed-M2-assertion", "M2 2026-10-17" not in json.dumps(new) and "M1..M5" not in json.dumps(new).replace("former M1..M5", "")
      and all(m["due_on"] in NC["PROC-TRACKING-SETUP"]["procedure_steps"][4] for m in tw["milestone_table"]),
      "old M2 due assertion removed; M1..M5 only as 'former M1..M5' history; PROC-TRACKING-SETUP step 4 lists all 13 per-row due times")

# 8 RE binding
re2 = (PLAN / "specialists/re-chronology-041-regate-receipt.md").read_text()
re_stmt = re.search(r"\| AC-AFC-P2-MS-01 \| (.*?) \|", tp).group(1)
check("R01-re-gated-statements", sha(PLAN / "amazon-fantasy-companion-phase-2-technical-plan.md") in re2 and D3 in re_stmt
      and "### " + D3 in tp and ms["requirement_gate_receipt"].endswith("re-chronology-041-regate-receipt.md")
      and all(NP[i]["method_fields"]["requirement_gate_receipt"].endswith("re-chronology-041-receipt.md")
              for i in ("SEIT-AFC-P2-REL-02", "SEIT-RISK-AFC-P2-13", "SEIT-AFC-P2-DX-02"))
      and "W1..W5" in NP["SEIT-AFC-P2-REL-02"]["stimulus_or_procedure"] and "W1..W5" in NP["SEIT-RISK-AFC-P2-13"]["stimulus_or_procedure"],
      "live plan sha equals RE re-gate candidate; MS-01 names the D3 table; four rows bound to current RE receipts")

# 9 profile binding
fpb = new["frozen_profile_binding"]
OH = journey["profile_selection"]["frozen_snapshots"]["opensource-hackathon"]
cs = hashlib.sha256(json.dumps(fpb["opensource-hackathon"]["snapshot"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
snap = fpb["opensource-hackathon"]["snapshot"]
prior = json.loads((PLAN / "evidence/profile-migration-041/prior-profile-selection.json").read_text())["frozen_snapshots"]
check("F01-profile-binding", set(fpb) == {"opensource-hackathon", "bug-triager"}
      and cs == OH["full_profile_sha256"] == "7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1"
      and {k: v for k, v in fpb["opensource-hackathon"].items() if k in OH} == OH
      and fpb["bug-triager"] == old["frozen_profile_binding"]["bug-triager"]
      and snap["review"]["coverage_assist"] == {"enabled": True, "required": True}
      and snap["deterministic_verification"]["reverify"] == {"enabled": True}
      and snap["development_strategy"] == {"mode": "tdd"} and snap["planning_to_implementation_clean_session"] is True
      and snap["holds"][0]["required_cli_args"] == ["--contributor-mode", "on"]
      and all(prior[k]["configuration_digest_sha256"] == v for k, v in new["superseded_profile_bindings"]["configuration_digest_sha256"].items()),
      f"opensource-hackathon snapshot sha {cs} equals journey; bug-triager byte-identical; 4 superseded digests preserved by reference")
gd = new["gate_declarations"]
check("F02-lane-profiles-and-assurance", all(gd[l]["profile"] == "opensource-hackathon" for l in ("backend", "tv-app-ui", "device-integration-spikes", "spec-and-docs"))
      and gd["defects"]["profile"] == "bug-triager" and all(gd[l]["assurance"]["enabled"] for l in gd if l != "policy")
      and "--contributor-mode on" in gd["policy"]["muse_contributor_mode_hold"]
      and "unsupported_ext" in gd["policy"]["coverage_assist_backend"] and "REVERIFY_CAPABILITY_GAP" in gd["policy"]["reverify_backend"]
      and all(gd[l]["coverage_assist"] == old["gate_declarations"][l]["coverage_assist"] and gd[l]["reverify"] == old["gate_declarations"][l]["reverify"]
              for l in gd if l != "policy"),
      "4 lanes opensource-hackathon, defects bug-triager; every lane assurance enabled; Muse hold, OCR .md gap and Reverify gap stated; lane coverage_assist/reverify unchanged")
live = {k: v for k, v in new.items() if k not in ("superseded_profile_bindings", "planning_findings_for_plan_integrator")}
check("F03-no-stale-exemption", "tech-writing" not in json.dumps(live).replace("former tech-writing assurance exemption", "")
      and "assurance disabled" not in json.dumps(new).lower() and "assurance remains disabled" not in json.dumps(new),
      "no active tech-writing binding or disabled-assurance text outside superseded history")

# 10 residual wave tokens, hygiene, sources, decisions
WTOK = re.compile(r"(?<![-\w.])M([1-5])(?![\w.])")
resid = sorted(set(m.group() for m in WTOK.finditer(json.dumps(live))))
check("H01-no-stale-wave-tokens", not resid, f"standalone M1..M5 tokens remaining outside planning-findings history: {resid}")
check("H02-no-home-paths", not re.search(r"/home/[a-z]|/Users/[A-Za-z]", SEIT.read_text()), "no absolute home paths")
sb = new["source_baseline"]
check("H03-source-binding", all(sha(p["path"]) == p["sha256"] for p in sb["planning_inputs"])
      and sb["revision"] == subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip(),
      f"{len(sb['planning_inputs'])} planning inputs equal live bytes; revision = HEAD")
cd = new["decision_baseline"]["confirmed_decisions"]
check("H04-decision-baseline", all(cd[k] == v for k, v in old["decision_baseline"]["confirmed_decisions"].items())
      and all(x["id"] in cd for x in journey["decisions"]) and len(cd) == len(journey["decisions"]),
      f"{len(cd)} decisions projected; prior statuses unchanged; SD-040/041/041-AMENDMENT-1 = {[cd[k] for k in ('DEC-AFC-SD-040', 'DEC-AFC-SD-041', 'DEC-AFC-SD-041-AMENDMENT-1')]}")

top = []
diff({k: v for k, v in old.items() if k not in ("proof_cases", "procedures_and_commands")},
     {k: v for k, v in new.items() if k not in ("proof_cases", "procedures_and_commands")}, "", top)
for p in top:
    changes[p.split("/")[1]].append(p)
ok = all(r["outcome"] == "PASS" for r in results)
OUT.write_text(json.dumps({"outcome": "PASS" if ok else "FAIL", "baseline": BASE, "seit_sha256": sha(SEIT),
                           "baseline_seit_sha256": hashlib.sha256(subprocess.run(["git", "show", f"{BASE}:{SEIT}"], check=True, capture_output=True).stdout).hexdigest(),
                           "checks": results, "changed_fields_by_scope": {k: sorted(set(v)) for k, v in sorted(changes.items())}},
                          indent=2, ensure_ascii=False) + "\n")
for r in results:
    print(r["outcome"], r["id"], "-", r["detail"])
print("OVERALL", "PASS" if ok else "FAIL", f"{sum(r['outcome'] == 'PASS' for r in results)}/{len(results)}")
sys.exit(0 if ok else 1)
