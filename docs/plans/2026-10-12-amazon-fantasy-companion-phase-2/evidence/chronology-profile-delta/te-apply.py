#!/usr/bin/env python3
"""TE chronology/profile delta (DEC-AFC-SD-040/041) for seit.json.

Deterministic rebuild from the 51bc730 baseline. Run from the repository root:
    python3 docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/chronology-profile-delta/te-apply.py
Writes only PLAN/seit.json. Metadata/text only: no proof or command is added,
dropped or renamed.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

BASE = "51bc730a880105c9b21d37a7a2dc5da79ada875f"
PLAN = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
REL = str(PLAN) + "/"
SEIT = PLAN / "seit.json"
TP = PLAN / "amazon-fantasy-companion-phase-2-technical-plan.md"
PAYLOAD = PLAN / "evidence/github-work-items/github-work-items.json"
JOURNEY = Path("docs/plans/2026-10-11-amazon-fantasy-companion/journey.json")
RE1 = REL + "specialists/re-chronology-041-receipt.md"
RE2 = REL + "specialists/re-chronology-041-regate-receipt.md"
D3 = "GitHub milestones in order (D3; create only after approval)"
WT = "Technical waves and release checkpoints (W1..W5)"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


base = json.loads(subprocess.run(["git", "show", f"{BASE}:{SEIT}"], check=True, capture_output=True).stdout)
d = copy.deepcopy(base)
payload = json.loads(PAYLOAD.read_text())
journey = json.loads(JOURNEY.read_text())
tp = TP.read_text()
ie = json.loads(re.search(r"```json integration_plan\n(.*)\n```", (PLAN / "specialists/integration-plan.md").read_text(), re.S).group(1))
IE = {s["id"]: s for s in ie["steps"]}
PC = {p["id"]: p for p in d["procedures_and_commands"]}
PR = {p["id"]: p for p in d["proof_cases"]}
TM = {r["SEIT row ID"]: r for r in d["traceability_matrix"]}


def sub1(s, old, new):
    assert s.count(old) == 1, (old, s)
    return s.replace(old, new)


# ---- approved 13-row D3 table (technical plan) joined with the review payload
sec = tp.split("### " + D3, 1)[1].split("\n### ", 1)[0]
rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in sec.splitlines() if re.match(r"\| M\d\d \|", ln)]
ISSUE_ORDER = {r[0]: [x.strip() for x in r[5].split(",")] for r in rows}
pm = {m["id"]: m for m in payload["milestones"]}
milestone_table = []
for r in rows:
    m = pm[r[0]]
    assert (m["title"], m["due_on"]) == (r[1], r[2]), r[0]
    milestone_table.append({"id": r[0], "title": r[1], "due_on": r[2], "github_due_date": r[2][:10],
                            "issues_in_order": ISSUE_ORDER[r[0]]})
assert [m["id"] for m in milestone_table] == [f"M{i:02d}" for i in range(1, 14)]
DUE_LIST = "; ".join(f"{m['id']} {m['due_on']}" for m in milestone_table)
PAYLOAD_SHA = sha(PAYLOAD)
ISSUE_MS = {i["id"]: i["milestone"] for i in payload["issues"]}

# ---- tracking workflow (single source; MS-01 carries a copy)
tw = d["tracking_workflow"]
assert PR["SEIT-AFC-P2-MS-01"]["method_fields"]["tracking_evidence"] == tw
tw["milestones"] = 13
tw["milestone_table_ref"] = TP.as_posix() + "#" + D3
tw["milestone_table"] = milestone_table
for g in tw["groups"]:
    g["milestone"] = ISSUE_MS[g["issue"]]
tw["payload_sha256"] = PAYLOAD_SHA
tw["X05"] = ("W1 early checkpoint CP-X05-HIST (PR 1 historical fixtures feed P2-R1 in M03 and P2-B02 in M05); "
             "single issue final milestone M04 at the TNF live-timing verdict; partial work stays open.")
tw["inspection_evidence"] = sub1(tw["inspection_evidence"], "five milestone readbacks",
                                 "thirteen milestone readbacks (M01..M13 title, calendar due date and description with exact UTC due time)")
neg = tw["negative_cases"]
neg[neg.index("X05 M1 closure before final work")] = "X05 closure at the W1 CP-X05-HIST checkpoint before its M04 final verdict"
neg += ["milestone due date or exact UTC due time differing from its approved D3 row",
        "readback bound to the W1..W5 release-checkpoint table instead of the 13-row D3 table"]
tw["no_new_requirement"] += " DEC-AFC-SD-040 changes milestone count/grouping only; W1..W5 release checkpoints keep the former M1..M5 dues and slices."
fs = tw["filing_scope"]
fs["local_preview"] = ("Supplied local preflight (39/39 body/label/target/permission checks; 0/39 helper admissions, 0 submissions) "
                       "bound superseded payload f485d8f62f72bf09c1e90c57493e03a178ec93ba7e9fc155cd776a32f736f5e9; it is not "
                       f"current for {PAYLOAD_SHA} and is rerun at action time. Revalidate scope and saved-state prerequisites "
                       "at action time; no gh dry-run option.")
fs["payload_note"] = (f"Parent-selected review draft payload under DEC-AFC-SD-040: evidence/github-work-items/github-work-items.json "
                      f"(sha256 {PAYLOAD_SHA}) with 13 milestones and 39 body_file mirrors. It supersedes "
                      "f485d8f62f72bf09c1e90c57493e03a178ec93ba7e9fc155cd776a32f736f5e9 (evidence/github-work-items/payload-supersession.json), "
                      "which superseded the TE method-example payload evidence/te-p2-finalize/tracking-payloads.json "
                      "(sha256 7b3935cfdae840fc6618aba64ba7726336e060a4733c59eca9da037d3903ab45), retained as history, not a creation "
                      "authority. 39 issues, 52 slices, 13 TDD pairs, dependency edges, requirements, proofs and labels unchanged; only "
                      "milestone assignment, title prefix and milestone/sequence body lines changed. Nothing approved or submitted. "
                      "PI may mechanically rebind payload_ref/sha; TE authors no body content.")

# ---- milestone commands
c = PC["CMD-MILESTONES-CREATE"]
c["pass"] = (f"Only after recorded integrated approval and planning PR landing; the thirteen approved rows M01..M13 of `{D3}` "
             "are created once each, existing matches reused. No premature/duplicate milestone; W1..W5 release checkpoints are never created as milestones.")
c["description"] = ("P2-L01 runtime only; one JSON per M01..M13 from the approved payload containing title, due_on and description "
                    "(entry criteria, exit criteria, issues in order); GitHub stores day precision, so each row's exact UTC due time stays in its description.")
c["procedure_steps"][1] = ("Thirteen stable IDs M01..M13 only; reconcile/reuse before POST, no delete on mismatch. Machine due_on ISO per "
                           "approved row (tracking_workflow.milestone_table); full UTC time and basis in description.")
c = PC["CMD-MILESTONES-READBACK"]
c["pass"] = sub1(c["pass"], "Exactly M1..M5 expected identities match approved title, calendar due date and description field for field; full UTC due time in description. Missing row or preapproval creation fails.",
                 f"Exactly the thirteen expected identities M01..M13 match the approved table `{D3}` field for field: title, calendar due date "
                 "and description (entry criteria, exit criteria, issues in order) with that row's exact UTC due time. Missing, mismatched or "
                 "preapproval row fails; a readback compared with the W1..W5 release-checkpoint table fails.")
c["procedure_steps"][0] = sub1(c["procedure_steps"][0], "Verify five milestones against approved payloads,",
                               "Verify thirteen milestones row by row against the approved payload and tracking_workflow.milestone_table (title, due date, exact UTC due time in description, issues in order),")
c = PC["PROC-TRACKING-SETUP"]
c["pass"] = sub1(c["pass"], "Five matching approved milestones", "Thirteen matching approved milestones M01..M13 (3,2,3,4,3,3,3,3,2,2,4,4,3 issues)")
c["procedure_steps"][4] = ("Create/reuse thirteen milestones M01..M13 with CMD-MILESTONES-CREATE; machine due_on is ISO only, per approved row: "
                           f"{DUE_LIST}. Each description keeps the row's exact UTC time and basis; the W2 release checkpoint "
                           "2026-10-17T01:00:00Z keeps its T_yahoo + 6 h explanation; never alter a date.")
c["procedure_steps"][11] = sub1(c["procedure_steps"][11],
                                "X05 M1 PR1 historical-fixture checkpoint permits R1 while its single M2 issue stays open until final work passes.",
                                "X05 PR 1 historical-fixture checkpoint CP-X05-HIST (W1; feeds P2-R1 in M03 and P2-B02 in M05) permits R1 while its single M04 issue stays open until final work passes.")
c["tracking_payload_ref"] = PAYLOAD.as_posix()
c["tracking_payload_sha256"] = PAYLOAD_SHA

# ---- governed proof rows (RE-gated statements)
p = PR["SEIT-AFC-P2-MS-01"]
p["stimulus_or_procedure"] = sub1(p["stimulus_or_procedure"],
                                  "compare gh milestone readback to approved table title/date/description and full UTC due time text.",
                                  f"compare gh milestone readback for M01..M13 to the approved table `{D3}` title/calendar date/description "
                                  "(entry criteria, exit criteria, issues in order) and each row's exact UTC due time text.")
p["expected_result"] = sub1(p["expected_result"], "M1..M5 exact approved fields after approval,",
                            "M01..M13 exact approved fields of the 13-row D3 table (not the W1..W5 release-checkpoint table) after approval,")
NEG_MS = ("Creation before approval or mismatched title/due day/exact UTC due time/entry criteria/exit criteria/issues in order, "
          "or readback bound to the W1..W5 table.")
p["pass_fail_rule"] = sub1(p["pass_fail_rule"], "Creation before approval or mismatched title/due day/criteria/slices.", NEG_MS)
p["negative_or_failure_case"] = NEG_MS
mf = p["method_fields"]
mf["requirement_gate_receipt"] = RE2
mf["tracking_evidence"] = copy.deepcopy(tw)
mf["additional_negative_observations"] = list(tw["negative_cases"])
TM["SEIT-AFC-P2-MS-01"]["Positive case"] = p["expected_result"]
TM["SEIT-AFC-P2-MS-01"]["Negative/failure case"] = NEG_MS

p = PR["SEIT-AFC-P2-REL-02"]
p["stimulus_or_procedure"] = sub1(p["stimulus_or_procedure"], "Inspect each milestone version,",
                                  "Inspect each technical-wave release checkpoint W1..W5 (P2-R1..P2-R5) version,")
p["expected_result"] = ("Five correctly bound prepared releases, one per technical-wave release checkpoint W1..W5; the 13 GitHub "
                        "milestones add no release; publication remains separately authorized.")
p["method_fields"]["requirement_gate_receipt"] = RE1
TM["SEIT-AFC-P2-REL-02"]["Positive case"] = p["expected_result"]

p = PR["SEIT-RISK-AFC-P2-13"]
p["stimulus_or_procedure"] = sub1(p["stimulus_or_procedure"], "Compare expected milestone finish and due time;",
                                  "Compare expected finish and due time of each technical-wave release checkpoint W1..W5 (earlier M01..M13 GitHub milestone dues are not this trigger);")
p["method_fields"]["requirement_gate_receipt"] = RE1
PR["SEIT-AFC-P2-DX-02"]["method_fields"]["requirement_gate_receipt"] = RE1

# ---- Mn tokens that mean a technical wave become Wn
for pid, pp in PR.items():
    lw = pp["method_fields"].get("live_window_or_replay_basis")
    if lw and "X11 conditional after M3" in lw:
        pp["method_fields"]["live_window_or_replay_basis"] = lw.replace("X11 conditional after M3", "X11 conditional after W3")
ac = PR["SEIT-AFC-P2-SPIKE-01"]["method_fields"]
ac["aggregate_closure"] = sub1(ac["aggregate_closure"], "aggregate M4 closure", "aggregate W4 closure")
PC["CMD-STUB-SCAN"]["pass"] = sub1(PC["CMD-STUB-SCAN"]["pass"], "M3 rehearsal", "W3 rehearsal")
PC["PROC-VISUAL-REVIEW"]["procedure_steps"][2] = sub1(PC["PROC-VISUAL-REVIEW"]["procedure_steps"][2], "A01 M1", "A01 W1")
PC["CMD-CHANGELOG-CHECK"]["pass"] = sub1(PC["CMD-CHANGELOG-CHECK"]["pass"], "under milestone version", "under the W1..W5 release-checkpoint version")
PC["CMD-RELEASE-PREP"]["pass"] = sub1(PC["CMD-RELEASE-PREP"]["pass"], "exact milestone commit", "exact W1..W5 release-checkpoint commit")
env = d["environments_fixtures_data_simulations_support"]
env["lease_order"] = sub1(env["lease_order"], "finish M1 A01 review", "finish W1 A01 review")


def cost_words(s):
    return s.replace("M4 fixed increment", "W4 fixed increment").replace("M5 120s docs", "W5 120s docs")


def gh_ms(slices):
    return sorted({ISSUE_MS[g["issue"]] for g in tw["groups"] for s in g["slices"] if s in slices})


for lv in d["levels"]:
    n = lv.pop("milestone")[1]
    assert int(n) == lv["wave"]
    lv2 = {"release_checkpoint": f"W{n}", "github_milestones": gh_ms(lv["slices"])}
    lv2.update(lv)
    lv.clear(); lv.update(lv2)
    lv["entry_criteria_ref"] = TP.as_posix() + f"#{WT} W{n} entry"
    lv["exit_criteria_ref"] = TP.as_posix() + f"#{WT} W{n} exit"
    lv["cost_limits"] = cost_words(lv["cost_limits"])
IEW = {w["wave"]: w for w in ie["wave_gate_costs"]}
for w in d["wave_gate_costs"]:
    n = w.pop("milestone")[1]
    assert int(n) == w["wave"]
    w2 = {"wave": w.pop("wave"), "release_checkpoint": f"W{n}", "github_milestones": IEW[int(n)]["github_milestones"]}
    w2.update(w)
    w.clear(); w.update(w2)
    w["limits"] = cost_words(w["limits"])

WTOK = re.compile(r"(?<![-\w.])M([1-5])(?![\w.])")


def wave_words(x):  # same mapping as ie-check.py
    x = re.sub(r"every other M([1-5]) slice", r"every other Wave \1 slice", x)
    x = re.sub(r"All M([1-5]) slices", r"All Wave \1 slices", x)
    x = re.sub(r"M([1-5]) entry", r"Wave \1 entry", x)
    return WTOK.sub(r"W\1", x).replace("M1..M5", "M01..M13")


FILING_SEIT = ("repository-applicable workflow per PROC-TRACKING-SETUP: mandatory helper dry-run/submit when covered; "
               "current exempt target native GitHub only after exact approval and local preflight")
FILING_IE = "policy-tool dry-run then submit"
for st in d["integration_vv_sequence"]:
    e = IE[st["step"]]
    assert int(st["milestone"][1]) == st["wave"] and e["wave"] == f"Wave {st['wave']}"
    st["milestone"] = e["milestone"]
    if "milestone_note" in e:
        st["milestone_note"] = e["milestone_note"]
    st["release_checkpoint"] = f"W{st['wave']}"
    for f in ("entry_criteria", "post_step_vv"):
        new = []
        for a, b in zip(st.get(f, []), e.get(f, [])):
            if a != b:  # SEIT IE-P2-2 keeps its PI-normalized filing phrase (mechanical_pi_refresh.integration)
                assert wave_words(a).replace(FILING_SEIT, FILING_IE) == b, (st["step"], a, b)
            new.append(wave_words(a))
        if f in st:
            st[f] = new
st7 = next(s for s in d["integration_vv_sequence"] if s["step"] == "IE-P2-8")
st7["X05_checkpoint_binding"] = ("P2-X05 -> P2-R1 is PR 1 historical-fixture checkpoint CP-X05-HIST merged at IE-P2-6 (W1), not final "
                                 "M04 issue closure. PR 2 final live timing remains IE-P2-17 (M04, W2). Existing assembly strategy/order unchanged.")

# ---- frozen profile binding (DEC-AFC-SD-041 + AMENDMENT-1)
OH = journey["profile_selection"]["frozen_snapshots"]["opensource-hackathon"]
BT = journey["profile_selection"]["frozen_snapshots"]["bug-triager"]
compact = json.dumps(OH["snapshot"], sort_keys=True, separators=(",", ":")).encode()
assert hashlib.sha256(compact).hexdigest() == OH["full_profile_sha256"] == "7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1"
old_fpb = base["frozen_profile_binding"]
bt_seit = old_fpb["bug-triager"]
assert {k: v for k, v in bt_seit.items() if k not in ("configuration_digest_sha256", "development_strategy")} == BT["snapshot"]
assert bt_seit["development_strategy"] == BT["development_strategy"] and bt_seit["configuration_digest_sha256"] == BT["configuration_digest_sha256"]
oh = {"source_ref": str(JOURNEY) + "#/profile_selection/frozen_snapshots/opensource-hackathon",
      "decision": "DEC-AFC-SD-041; DEC-AFC-SD-041-AMENDMENT-1 (Bearing Lite 1.1.7)",
      "lanes": ["tv-app-ui", "backend", "device-integration-spikes", "spec-and-docs", "scribe-side-lane", "planning"]}
oh.update(copy.deepcopy(OH))
PRIOR = PLAN / "evidence/profile-migration-041/prior-profile-selection.json"
prior = json.loads(PRIOR.read_text())["frozen_snapshots"]
superseded = {}
for k in ("primary", "frontend", "heavyweight", "tech-writing"):
    assert prior[k]["configuration_digest_sha256"] == old_fpb[k]["configuration_digest_sha256"], k
    superseded[k] = old_fpb[k]["configuration_digest_sha256"]
d["frozen_profile_binding"] = {"opensource-hackathon": oh, "bug-triager": bt_seit}
d["superseded_profile_bindings"] = {
    "decision": "DEC-AFC-SD-041 supersedes the primary/frontend/heavyweight/tech-writing lane bindings; snapshots preserved, not deleted.",
    "preserved_at": PRIOR.as_posix(), "preserved_sha256": sha(PRIOR),
    "configuration_digest_sha256": superseded,
    "note": "History only; never a dispatch route. Spent planning review 1/1 and repair 1/1 stay spent."}
d["frozen_profile_binding_note"] = (
    "Projection from parent control journey profile_selection.frozen_snapshots only (full_profile_sha256 7d501eb8…6ab1 recomputed "
    "from the compact sorted snapshot). No live catalog read or import. opensource-hackathon covers every product and planning lane; "
    "bug-triager stays separate and byte-identical for defects. Roles, ordered fallbacks, cadences, TDD, concurrency, clean session, "
    "review.coverage_assist and deterministic_verification.reverify are frozen. Hold muse-contributor-mode: every Muse Code primary "
    "and fallback dispatch passes --contributor-mode on, else a typed configuration gap. Preserving a snapshot never authorizes a route switch.")

gd = d["gate_declarations"]
for lane in ("backend", "tv-app-ui", "device-integration-spikes", "spec-and-docs"):
    gd[lane]["profile"] = "opensource-hackathon"
sd = gd["spec-and-docs"]
sd["strategy"] = "tdd (frozen opensource-hackathon); documentation/evidence-only slices use their declared verification method"
sd["assurance"] = {"enabled": True, "cadence": "lifecycle",
                   "candidate": "candidate.final at IE-P2-44",
                   "independence": "Fresh session rejects author ancestry; rerun claims, author receipts diagnostic."}
sd["red_then_green"]["reason"] = ("Documentation-only slices add no product behavior; any executable work keeps a TDD pair and its "
                                  "red-then-green, coverage and mutation claims.")
pol = gd["policy"]
pol["muse_contributor_mode_hold"] = (
    "Frozen opensource-hackathon hold muse-contributor-mode: every Muse Code primary or fallback invocation (implementer, test_implementer, "
    "light_implementer, scribe, plan_integrator, systems_modeler, reviewer and test/integration/requirements sessions) launches with "
    "--contributor-mode on and the packet records the exact per-run flag; if it cannot be honored, return a typed configuration gap. "
    "bug-triager Muse routes are unchanged by this profile-specific hold.")
pol["coverage_assist_backend"] = (
    "OpenCodeReview v1.13.0 delegation (ocr delegate preview/rule), frozen review.coverage_assist enabled+required. Inherited gap stays "
    "visible: delegation excludes Markdown (.md) as unsupported_ext, so planning/docs-only diffs have no OCR rule coverage; reviewers "
    "inspect those files directly and record OCR_COVERAGE_GAP unsupported_ext, never PASS.")
pol["reverify_backend"] = (
    "reverify 0.11.0; `reverify backends --json` observed 2026-10-13: capstone 5.0.7, unicorn 2.1.4, lief 1.0.0, z3 4.13.0, angr 9.3.4, "
    "full_fidelity true. Backend availability is not APK semantic qualification: REVERIFY_CAPABILITY_GAP remains a future typed gap; no "
    "source-only, string/ZIP or unit check becomes a binary PASS.")

r = d["responsibility_and_change_authority"]
r["assurance"] = ("Fresh Assurance Test Engineer sessions at lifecycle cadence on the W5 stable candidate for every opensource-hackathon "
                  "lane (tv-app-ui, backend, device-integration-spikes, spec-and-docs) on the frozen test_engineer.assurance route and "
                  "ordered fallbacks, and for defects on the bug-triager assurance route. Reject author ancestry; independently rerun "
                  "applicable gate-chain claims. Author receipts remain diagnostic. The former tech-writing assurance exemption is removed.")
r["planning_test_engineer"] = ("Chronology/profile delta only (DEC-AFC-SD-040/041): seit.json, specialists/te-chronology-041-receipt.md and "
                               "evidence/chronology-profile-delta/te-*. No historical validator or receipt edit.")
d["required_command_scopes"]["tech_writing"] = ("spec-and-docs lane: docs/spec/hygiene and named PROC inspection; lifecycle assurance enabled "
                                                "under frozen opensource-hackathon.")
pf = d["planning_findings_for_plan_integrator"]
pf["integration_step_proof_policy"] = sub1(pf["integration_step_proof_policy"], "without treating tech-writing as enabled ATE assurance.",
                                           "with ATE assurance enabled for every opensource-hackathon lane and bug-triager.")
cod = next(x for x in pf["cases_needing_owner_decision"] if x["decision"] == "OA-AFC-A1")
cod["rule"] = "Frontend skill binding; preserve the frozen opensource-hackathon route for the tv-app-ui lane."
mp = pf["mechanical_pi_refresh"]
mp["vv_and_capabilities"] = sub1(mp["vv_and_capabilities"], "Keep all five frozen route/capability snapshots unchanged.",
                                 "Keep the frozen opensource-hackathon and bug-triager snapshots unchanged; superseded lane snapshots are history only.")
mp["tracking"] = sub1(mp["tracking"], "X05 issue final M2, M1 PR1 checkpoint only.",
                      "13 milestones M01..M13 from the review payload; X05 issue final M04, W1 CP-X05-HIST checkpoint only.")
mp["milestone_due"] = ("Set implementation.json milestones M01..M13 due_on exactly per approved row: " + DUE_LIST +
                       ". W1..W5 release checkpoints keep the former M1..M5 dues; W2 2026-10-17T01:00:00Z keeps (T_yahoo + 6 h for "
                       "the P2-X06 verdict pull request and P2-R2) in its explanation. No date change.")
mp["checks"] = sub1(mp["checks"], "exact M2 timestamp", "exact per-row M01..M13 due times and W2 2026-10-17T01:00:00Z")

# ---- decision baseline and source baseline
cd = d["decision_baseline"]["confirmed_decisions"]
for x in journey["decisions"]:
    cd.setdefault(x["id"], x.get("status", "not_recorded"))
d["decision_baseline"]["chronology_profile_authority"] = {
    "ids": ["DEC-AFC-SD-040", "DEC-AFC-SD-041", "DEC-AFC-SD-041-AMENDMENT-1"],
    "scope": "13 chronological GitHub milestones and full opensource-hackathon/Bearing 1.1.7 migration; no tracking creation, product execution or PR15 merge authority."}
sb = d["source_baseline"]
sb["revision"] = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
for pi in sb["planning_inputs"]:
    pi["sha256"] = sha(pi["path"])
sb["planning_input_note"] += (" TE chronology delta rebound the technical plan and design after reading them; PI refreshes mechanical "
                              "hashes after graph integration.")
for ref in ["specialists/re-chronology-041-receipt.md", "specialists/re-chronology-041-regate-receipt.md",
            "specialists/chronology-opus-review.md", "evidence/chronology-opus-review/proposal.json",
            "specialists/ie-chronology-041-receipt.md", "evidence/github-work-items/github-work-items.json"]:
    if REL + ref not in sb["read_only_context"]:
        sb["read_only_context"].append(REL + ref)

a = d["artifact"]
a["status"] = "chronology-profile-delta-041-for-PI-refresh"
a["finalized_by"] = "Planning Test Engineer: Claude Code / Claude Opus 5.5 / high (frozen opensource-hackathon primary)"
a["receipt"] = REL + "specialists/te-chronology-041-receipt.md"
a["note"] = ("Bounded TE delta for DEC-AFC-SD-040/041 over 51bc730: 13 GitHub milestones, Mn->Wn wave labels, RE-gated MS-01/REL-02/"
             "RISK-13/DX-02 bindings and the opensource-hackathon binding. Proof/command IDs, allocations and product assertions unchanged. "
             "Planning authorship only; review 1/1 and repair 1/1 stay spent. Product execution, tracking creation and publication remain held.")
a["finalized_at"] = "2026-10-13"

SEIT.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print("wrote", SEIT, sha(SEIT))
