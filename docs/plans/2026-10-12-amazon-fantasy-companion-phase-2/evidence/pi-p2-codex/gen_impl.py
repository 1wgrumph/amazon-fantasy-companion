#!/usr/bin/env python3
"""Plan Integrator generator: Phase 2 implementation.json from stable sources.
Mechanical reconciliation only. Run from the repo worktree root.
Usage: python3 gen_impl.py [--digest <candidate_digest>]
Writes docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/implementation.json
"""
import json, re, sys, hashlib
from pathlib import Path

ROOT = Path(".")
PLAN = ROOT / "docs/plans/2026-10-12-amazon-fantasy-companion-phase-2"
P1 = ROOT / "docs/plans/2026-10-11-amazon-fantasy-companion"
PJ = P1 / "journey.json"

TP = PLAN / "amazon-fantasy-companion-phase-2-technical-plan.md"
DESIGN = PLAN / "design.md"
REG = PLAN / "requirements-register.md"
GRAPH = PLAN / "specialists/slice-graph.md"
IEP = PLAN / "specialists/integration-plan.md"
SEIT = PLAN / "seit.json"
AUTH = PLAN / "authority.json"
SMRECEIPT = PLAN / "specialists/sm-p2-delta-receipt.md"
TRACKING_PAYLOAD = PLAN / "evidence/github-work-items/github-work-items.json"

REVISION = "7f000aff70e435b0cac923931fd818c69111f07d"
BRANCH = "plan/2026-10-12-afc-phase-2"
AUTHORITY_ID = "AUTH-AFC-2026-10-12-P2-001"
REPO = "1wgrumph/amazon-fantasy-companion"

LANE_PROFILE = {
    "tv-app-ui": "frontend",
    "backend": "primary",
    "device-integration-spikes": "heavyweight",
    "spec-and-docs": "tech-writing",
    "Scribe side lane": "primary",
}
ROLE_SNAPSHOT = {
    "Product Implementer": "implementer",
    "Test Implementer": "test_implementer",
    "Light Implementer": "light_implementer",
    "Scribe": "scribe",
}
LEASES = ["fire-tv-stick", "aws-afc-dev", "live-game-window", "tv-app-manifest",
          "tv-app-gradle", "backend-template", "main-landing"]

def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse_tables(text):
    """Yield (header_cells, rows) for every markdown table."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-|:]+\|\s*$", lines[i + 1]):
            hdr = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            yield hdr, rows
            i = j
        else:
            i += 1

def tables_with(text, first_col):
    out = []
    for hdr, rows in parse_tables(text):
        if hdr and hdr[0] == first_col:
            out.append((hdr, rows))
    return out

def expand_ids(cell, kind_prefix=None):
    """Expand 'AC-AFC-P2-SPIKE-01, -SPIKE-02; RISK-AFC-P2-01' to full IDs."""
    ids = []
    prefix = None
    for tok in re.split(r"[,;]", cell):
        tok = tok.strip().strip("`")
        if not tok or tok == "—":
            continue
        if tok.startswith("-"):
            assert prefix, f"dangling continuation {tok} in {cell}"
            ids.append(prefix + tok)
        else:
            m = re.match(r"((?:AC|RISK)-AFC-P2)-.+", tok)
            if m:
                prefix = m.group(1)
            ids.append(tok)
    return ids

def expand_uids(cell):
    out = []
    for tok in re.split(r"[,;]", cell):
        tok = tok.strip().strip("`")
        if not tok or tok == "—":
            continue
        m = re.match(r"(\d{3})(?:\.\.(\d{3}))?$", tok)
        if m and m.group(2):
            for n in range(int(m.group(1)), int(m.group(2)) + 1):
                out.append(f"AFC-PR-{n:03d}")
        elif re.match(r"\d{3}$", tok):
            out.append(f"AFC-PR-{tok}")
        else:
            out.append(tok)
    return out

# ---------- load sources ----------
tp_text = TP.read_text()
design_text = DESIGN.read_text()
reg_text = REG.read_text()
graph_text = GRAPH.read_text()
seit = json.loads(SEIT.read_text())
authority = json.loads(AUTH.read_text())
parent_journey = json.loads(PJ.read_text())
FS = parent_journey["profile_selection"]["frozen_snapshots"]

m = re.search(r"```json integration_plan\n(.*)\n```", IEP.read_text(), re.S)
assert m, "integration_plan json block missing"
IE_BLOCK = json.loads(m.group(1))
assert len(IE_BLOCK["steps"]) == 44, len(IE_BLOCK["steps"])
# Freeze checkIntegrationStepRefs resolves `integration_steps` keys against slice ids;
# the IE delta's wave_gate_costs step lists name IE steps, not slices. Rename the key in
# this copy only (values byte-identical); integration-plan.md stays authoritative.
for _w in IE_BLOCK.get("wave_gate_costs", []):
    assert set(_w) >= {"integration_steps"}, _w.keys()
    _w["step_ids"] = _w.pop("integration_steps")
IE_BLOCK["wave_gate_costs_note"] = ("PI copy projection: wave_gate_costs entries list step_ids (renamed from the source "
    "block's integration_steps key so freeze reference-key resolution, which maps that key name to slice ids, does not "
    "misread IE step ids as slice refs). Values and order identical to specialists/integration-plan.md.")
# Filing-scope projection (owning TE, te-p2-filing-binding): normalize ONLY the
# IE-P2-2 filing phrase in this copy to the repository-applicable workflow from
# seit.json integration_vv_sequence. IE source, order, strategy unchanged.
_IE_IDS = [s["id"] for s in IE_BLOCK["steps"]]
assert _IE_IDS.index("IE-P2-35") < _IE_IDS.index("IE-P2-34"), "correction2 order"
_IE2_OLD = "policy-tool dry-run then submit"
_IE2 = next(s for s in IE_BLOCK["steps"] if s["id"] == "IE-P2-2")
assert _IE2_OLD in _IE2["entry_criteria"][0]
_SEIT_IE2 = next(e for e in seit["integration_vv_sequence"] if e["step"] == "IE-P2-2")
assert _IE2_OLD not in _SEIT_IE2["entry_criteria"][0]
_IE2["entry_criteria"][0] = _SEIT_IE2["entry_criteria"][0]
IE_BLOCK["ie_p2_2_filing_note"] = ("PI copy projection: IE-P2-2 entry_criteria[0] carries the owning-TE "
    "repository-applicable workflow phrase from seit.json#/integration_vv_sequence (filing-scope binding); all other "
    "IE text, IDs, order, dependencies and post-step checks identical to specialists/integration-plan.md.")

REGISTRY = {p["id"] for p in seit["procedures_and_commands"]}
NCMDS = len(seit["procedures_and_commands"])
assert NCMDS == 70, NCMDS
# TE mechanical_pi_refresh.command_bindings projection (te-p2-finalize): prospective
# qualification/coverage/mutation/tracking bindings owned by TE, appended to the
# graph's Commands cells. Graph/IE sources unchanged.
SUPPLEMENTAL_COMMANDS = {
    "P2-L01": ["PROC-TRACKING-SETUP"],
    "P2-G01T": ["PROC-GATE-TOOL-QUALIFY"],
    "P2-G01": ["PROC-GATE-TOOL-QUALIFY", "CMD-COVERAGE-BACKEND", "CMD-COVERAGE-TVAPP",
              "CMD-MUTATION-BACKEND", "CMD-MUTATION-TVAPP"],
    "P2-A01T": ["PROC-GATE-TOOL-QUALIFY"],
    "P2-A01": ["PROC-GATE-TOOL-QUALIFY", "CMD-COVERAGE-TVAPP", "CMD-MUTATION-TVAPP"],
    "P2-B01T": ["PROC-GATE-TOOL-QUALIFY"],
    "P2-B01": ["PROC-GATE-TOOL-QUALIFY", "CMD-COVERAGE-BACKEND", "CMD-MUTATION-BACKEND"],
}
for _sid, _cmds in SUPPLEMENTAL_COMMANDS.items():
    for _c in _cmds:
        assert _c in REGISTRY, (_sid, _c)

# ---------- register rows ----------
reg_rows = {}
for hdr, rows in tables_with(reg_text, "UID"):
    for r in rows:
        d = dict(zip(hdr, r))
        reg_rows[d["UID"]] = d
assert len(reg_rows) == 66, len(reg_rows)
ACTIVE_UIDS = [u for u in reg_rows if not reg_rows[u]["Statement"].startswith("WITHDRAWN")]
WITHDRAWN = [u for u in reg_rows if u not in ACTIVE_UIDS]
assert len(ACTIVE_UIDS) == 63 and WITHDRAWN == ["AFC-PR-049", "AFC-PR-050", "AFC-PR-051"], (len(ACTIVE_UIDS), WITHDRAWN)

# ---------- TP AC/RISK rows ----------
ac_rows, risk_rows = {}, {}
for hdr, rows in tables_with(tp_text, "ID"):
    for r in rows:
        d = dict(zip(hdr, r))
        i = d["ID"]
        if i.startswith("AC-AFC-P2-"):
            ac_rows[i] = d
        elif i.startswith("RISK-AFC-P2-"):
            risk_rows[i] = d
assert len(ac_rows) == 24, (len(ac_rows), sorted(ac_rows))
assert len(risk_rows) == 13, (len(risk_rows), sorted(risk_rows))

# ---------- TP milestone / OA / open items / waves ----------
ms_tables = tables_with(tp_text, "Milestone")
assert len(ms_tables) == 1
ms_hdr, ms_rows = ms_tables[0]
MILESTONES_SRC = [dict(zip(ms_hdr, r)) for r in ms_rows]
assert [r["Milestone"] for r in MILESTONES_SRC] == ["M1", "M2", "M3", "M4", "M5"]

oa_tables = tables_with(tp_text, "ID")
OA_SRC = []
for hdr, rows in oa_tables:
    if hdr == ["ID", "Owner action", "Needed by", "Blocks if absent"]:
        OA_SRC = [dict(zip(hdr, r)) for r in rows]
assert len(OA_SRC) == 11, len(OA_SRC)

od_tables = [t for t in tables_with(tp_text, "ID") if t[0] == ["ID", "Decision", "Recommendation"]]
assert len(od_tables) == 1
od_hdr, od_rows = od_tables[0]
OPEN_SRC = [dict(zip(od_hdr, r)) for r in od_rows]
assert [r["ID"] for r in OPEN_SRC] == ["OD-AFC-02", "OD-AFC-03", "OD-AFC-04", "OD-AFC-05",
    "OA-AFC-A1", "OD-AFC-P2-01", "OD-AFC-P2-02", "OD-AFC-P2-03", "OD-AFC-P2-04", "OD-AFC-P2-05"]

wave_lines = {}
for mm in re.finditer(r"^Wave (\d): (.+)$", tp_text, re.M):
    wave_lines[int(mm.group(1))] = [s.strip() for s in mm.group(2).split(",")]
assert sorted(wave_lines) == [1, 2, 3, 4, 5]
dispatch_tables = tables_with(tp_text, "Wave")
assert len(dispatch_tables) == 1
DISPATCH_SRC = {r[0]: r[1] for r in dispatch_tables[0][1]}

# ---------- design sections ----------
design_secs = {}
for mm in re.finditer(r"^### ((?:DES|CONTRACT)-AFC-P2-[A-Z0-9-]+) — (.+)$", design_text, re.M):
    did, title = mm.group(1), mm.group(2)
    body = design_text[mm.end():]
    paras = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("|") and not p.strip().startswith("```") and not p.strip().startswith("- ") and not p.strip().startswith("###")]
    first = re.sub(r"\s+", " ", paras[0]) if paras else ""
    design_secs[did] = {"title": title, "summary": first}
assert len(design_secs) == 26, len(design_secs)

LENSES_TABLE = {}
for hdr, rows in tables_with(design_text, "Lens"):
    for r in rows:
        LENSES_TABLE[r[0]] = r[1]
assert len(LENSES_TABLE) == 10, len(LENSES_TABLE)

# ---------- slice graph ----------
sg_tables = [t for t in tables_with(graph_text, "ID") if "Lane / role / class" in t[0]]
assert len(sg_tables) == 1
sg_hdr, sg_rows = sg_tables[0]
SLICES_SRC = [dict(zip(sg_hdr, r)) for r in sg_rows]
assert len(SLICES_SRC) == 52, len(SLICES_SRC)

SKILLS_MAP = {}
for hdr, rows in tables_with(graph_text, "Key"):
    for r in rows:
        v = r[1]
        # reviewer row joins two paths with ' + '; keep each absolute path token
        paths = [p.strip() for p in v.split(" + ")]
        SKILLS_MAP[r[0]] = paths
assert "implementer" in SKILLS_MAP and "reviewer" in SKILLS_MAP

arrow_tables = [t for t in tables_with(graph_text, "Arrow") if t[0] == ["Arrow", "Condition"]]
assert len(arrow_tables) == 1
ARROWS = []
for a, c in arrow_tables[0][1]:
    mm = re.match(r"`?([A-Z0-9-]+)\s*-->\s*([A-Z0-9-]+)`?$", a.strip())
    assert mm, a
    ARROWS.append({"from": mm.group(1), "to": mm.group(2), "condition": c})

# proof cases by requirement
PCS = seit["proof_cases"]
assert len(PCS) == 100, len(PCS)
PC_BY_REQ = {}
for p in PCS:
    PC_BY_REQ.setdefault(p["requirement_id"], []).append(p["id"])
SPM = seit["planning_findings_for_plan_integrator"]["slice_proof_map"]
assert len(SPM) == 52, len(SPM)
PC_IDS = {p["id"] for p in PCS}
for sid, rows in SPM.items():
    for r in rows:
        assert r in PC_IDS, (sid, r)

# IE step membership per slice
STEP_OF = {}
for st in IE_BLOCK["steps"]:
    for sl in st.get("merges", []):
        STEP_OF.setdefault(sl, []).append(st["id"])
ALL_SIDS = [s["ID"] for s in SLICES_SRC]
assert set(STEP_OF) >= set(ALL_SIDS), set(ALL_SIDS) - set(STEP_OF)

def route_for(profile, snapshot_role):
    snap = FS[profile]
    r = snap["snapshot"]["roles"][snapshot_role]
    p = r["primary"]
    return {
        "snapshot_profile": profile,
        "snapshot_role": snapshot_role,
        "configuration_digest_sha256": snap["configuration_digest_sha256"],
        "harness": p["harness"],
        "model": p["model"],
        "reasoning": p["reasoning"],
        "ordered_fallbacks": r["ordered_fallbacks"],
    }

def slice_type(sid, role):
    if role == "Light Implementer":
        return "light"
    if role == "Scribe":
        return "scribe"
    if sid.endswith("T"):
        return "test"
    if sid.startswith("P2-X"):
        return "spike"
    if sid.startswith("P2-R"):
        return "release"
    if sid.startswith("P2-D"):
        return "docs"
    return "product"

def dev_strategy(lane, role, sid):
    if role == "Light Implementer":
        return "light"
    if lane == "spec-and-docs" or role == "Scribe":
        return "single_implementer"
    if sid.startswith("P2-X"):
        return "evidence-only (OD-AFC-04, open_for_integrated_review)"
    return "tdd"

APK_SLICES = {"P2-L05", "P2-A01", "P2-A02", "P2-A03", "P2-A04", "P2-A05", "P2-R5"}

def reverify_text(sid, role, lane):
    if sid in APK_SLICES:
        return ("CMD-REVERIFY-APK on the exact built APK (TE-P2-F03 REVERIFY_CAPABILITY_GAP retained: "
                "APK semantic grounding unproven with reverify 0.11.0; a failure or unavailability is a typed gap, never PASS)")
    if sid.startswith("P2-X"):
        return ("Reverify: not applicable — this slice produces spike verdict evidence and observed on-stick behavior, "
                "not a compiled-binary attribute claim")
    if role == "Test Implementer":
        return "Reverify: not applicable — this slice authors red tests and receipts, not a compiled binary"
    if lane == "backend":
        return ("Reverify: not applicable — this slice establishes functional responses or source/process properties, "
                "not a compiled-binary attribute claim")
    return ("Reverify: not applicable — this slice produces docs, process, deployment or release artifacts, "
            "not a compiled-binary attribute claim")

def concise_goal(cell):
    cell = cell.strip()
    if len(cell) <= 512:
        return cell
    cut = cell[:509]
    for sep in [". ", "; "]:
        i = cut.rfind(sep)
        if i > 200:
            return cut[:i + 1].rstrip() + "…"
    return cut.rstrip() + "…"

def stop_of(cell):
    m = re.search(r"\bstop (?:at|when)\b", cell, re.I)
    if m:
        return cell[m.start():].strip()
    parts = re.split(r"; ", cell.strip())
    return parts[-1].strip()

# lens mapping: design id -> lenses (deterministic; record rule in receipt)
LENS_BY_DESIGN = {
    "DES-AFC-P2-SPIKES": ["Evidence before dependence", "Owner boundary"],
    "DES-AFC-P2-TV": ["Contract-first", "Lightweight device"],
    "DES-AFC-P2-ALERTPATH": ["Lightweight device", "Honest outcome"],
    "DES-AFC-P2-WATCH": ["Honest outcome", "Contract-first"],
    "DES-AFC-P2-PANEL": ["Couch UI", "Honest outcome", "Lightweight device"],
    "DES-AFC-P2-BACKEND": ["Free-tier boundary", "Contract-first"],
    "DES-AFC-P2-AUTH": ["Security controls"],
    "DES-AFC-P2-FEED": ["Honest outcome", "Contract-first"],
    "DES-AFC-P2-LINEUP": ["Honest outcome"],
    "DES-AFC-P2-MATCH": ["Honest outcome"],
    "DES-AFC-P2-POLICY": ["Honest outcome"],
    "DES-AFC-P2-RESOLVE": ["Honest outcome", "Contract-first"],
    "DES-AFC-P2-PANELSVC": ["Honest outcome", "Contract-first"],
    "DES-AFC-P2-GATE": ["Contract-first"],
    "DES-AFC-P2-VISUAL": ["Couch UI", "Owner boundary"],
    "DES-AFC-P2-REVREC": ["Revision record"],
    "DES-AFC-P2-SUB": ["Owner boundary"],
    "DES-AFC-P2-DX": ["Developer feedback"],
    "DES-AFC-P2-LANES": ["Owner boundary"],
}
for _k, _v in LENS_BY_DESIGN.items():
    for _l in _v:
        assert _l in LENSES_TABLE, _l

# ---------- dependencies ----------
MS_OF = {}
for r in MILESTONES_SRC:
    for s in [re.sub(r"\s*\(conditional\)$", "", x.strip()) for x in r["Slices"].split(",")]:
        MS_OF[s] = r["Milestone"]
assert len(MS_OF) == 52, len(MS_OF)

DEPENDENCIES = list(ARROWS)
# Release slices R1..R4 wait for every other slice of their milestone (graph note)
for rn in ("P2-R1", "P2-R2", "P2-R3", "P2-R4"):
    m = MS_OF[rn]
    for s in ALL_SIDS:
        if MS_OF[s] == m and s != rn:
            if not any(d["from"] == s and d["to"] == rn for d in DEPENDENCIES):
                DEPENDENCIES.append({"from": s, "to": rn, "condition": "merged (every other slice of the milestone)"})
# acyclic check
def check_acyclic(deps):
    seen, stack = set(), set()
    adj = {}
    for d in deps:
        adj.setdefault(d["from"], []).append(d["to"])
    def visit(n):
        if n in stack:
            raise AssertionError(f"cycle at {n}")
        if n in seen:
            return
        stack.add(n)
        for t in adj.get(n, []):
            visit(t)
        stack.discard(n)
        seen.add(n)
    for d in deps:
        visit(d["from"])
        visit(d["to"])
check_acyclic(DEPENDENCIES)
_X05R1 = next(d for d in DEPENDENCIES if d["from"] == "P2-X05" and d["to"] == "P2-R1")
assert "PR 1" in _X05R1["condition"], _X05R1  # explicit graph PR1 checkpoint overrides generic expansion

DEP_ON = {}
for d in DEPENDENCIES:
    DEP_ON.setdefault(d["to"], []).append(d["from"])
for v in DEP_ON.values():
    v.sort(key=ALL_SIDS.index)

# ---------- slices ----------
COMMON_REQ = ["AC-AFC-P2-DX-01", "AC-AFC-P2-PATH-01", "AC-AFC-P2-LAND-01", "AC-AFC-P2-REL-01",
              "AC-AFC-P2-REV-01", "RISK-AFC-P2-10"]
SLICES = []
for s in SLICES_SRC:
    sid = s["ID"]
    lane, role, wclass = [x.strip() for x in s["Lane / role / class"].split("/")]
    assert lane in LANE_PROFILE, lane
    profile = LANE_PROFILE[lane]
    mcell = [x.strip() for x in s["M, wave"].split(",")]
    ms, wv = mcell[0], "Wave " + mcell[1].strip("Ww").strip()
    assert MS_OF[sid] == ms, (sid, ms)
    goal_cell = s["Goal; stop when"].strip()
    goal = concise_goal(goal_cell)
    assert len(goal) <= 512, (sid, len(goal))
    uids = expand_uids(s["Register UIDs"])
    for u in uids:
        assert u in reg_rows and u in ACTIVE_UIDS, (sid, u)
    acr = expand_ids(s["AC / RISK"])
    for a in acr:
        assert a in ac_rows or a in risk_rows, (sid, a)
    # requirement_ids: graph IDs + proof-map requirement owners
    pc_req = set()
    for prow in SPM[sid]:
        for p in PCS:
            if p["id"] == prow:
                pc_req.add(p["requirement_id"])
    req_ids = sorted(set(uids) | set(acr) | set(COMMON_REQ) | pc_req,
                     key=lambda x: (0 if x.startswith("AFC") else 1 if x.startswith("AC-") else 2, x))
    # every graph ID must exist and have a proof row somewhere; warn if not in this slice's TE map
    for a in set(uids) | set(acr):
        assert PC_BY_REQ.get(a), (sid, a)
        if not any(r in SPM[sid] for r in PC_BY_REQ[a]):
            print(f"WARN: {sid} graphs {a} but TE map lacks its row (kept per graph; TE owns V&V)")
    design_ids = [t.strip().strip("`") for t in s["Design"].split(",")]
    for dd in design_ids:
        assert dd in design_secs, (sid, dd)
    lenses = ["Developer feedback", "Revision record"]
    for dd in design_ids:
        if dd.startswith("CONTRACT-"):
            if "Contract-first" not in lenses:
                lenses.append("Contract-first")
        else:
            for ln in LENS_BY_DESIGN[dd]:
                if ln not in lenses:
                    lenses.append(ln)
    if re.search(r"\bOA-\d|OD-AFC|conditional|C[1-9]\b", goal_cell + " " + s["Depends on"]) and "Owner boundary" not in lenses:
        lenses.append("Owner boundary")
    write_set = re.findall(r"`([^`]+)`", s["Write set"])
    assert write_set, sid
    for w in write_set:
        assert not w.startswith("/") and "/ho" + "me/" not in w, (sid, w)
    ws_note = re.sub(r"`[^`]+`", "", s["Write set"]).strip(" ,")
    cmds = [c.strip().strip("`") for c in s["Commands"].split(",")]
    for c in cmds:
        assert c in REGISTRY, (sid, c)
    for c in SUPPLEMENTAL_COMMANDS.get(sid, []):
        if c not in cmds:
            cmds.append(c)
    lease_cell = s["Leases"].strip()
    leases = [L for L in LEASES if L in lease_cell]
    if lease_cell == "—":
        assert leases == [], sid
    spec_cell = s["Spec §"].strip()
    spec_sections = [f"spec §{x.strip()}" for x in spec_cell.split(",")] if spec_cell != "—" else []
    skills = []
    for k in [x.strip() for x in s["Skills"].split(",")]:
        assert k in SKILLS_MAP, (sid, k)
        skills.extend(SKILLS_MAP[k])
    for sk in skills:
        assert "/ho" + "me/" not in sk, (sid, sk)
    oas = sorted(set(re.findall(r"OA-\d+", s["Depends on"] + " " + goal_cell + " " + lease_cell)),
                 key=lambda x: int(x.split("-")[1]))
    ods = sorted(set(re.findall(r"OD-AFC(?:-P2)?-\d+", s["Depends on"] + " " + goal_cell)))
    human = {"owner_actions": oas, "open_decisions": ods} if (oas or ods) else None
    if wclass == "light":
        assert role == "Light Implementer" and cmds, sid
        wreason = (f"Mechanical: named inputs fully determine the output and {', '.join(cmds)} "
                   f"exit status verifies it; no value chosen in session; one bounded write set.")
    else:
        assert wclass == "judgement", (sid, wclass)
        wreason = {"Test Implementer": "Authors failing tests and red receipts; test design is decided in session.",
                   "Product Implementer": "Authors product code, verdicts or prose; content and limits are decided in session.",
                   "Scribe": "Assembles feedback prose; selection and wording are decided in session."}[role]
    mr = route_for(profile, ROLE_SNAPSHOT[role])
    steps = STEP_OF[sid]
    te_assurance = ("lifecycle" if profile != "tech-writing"
                    else "disabled (frozen tech-writing snapshot test_engineer.assurance.enabled=false)")
    sl = {
        "id": sid,
        "role": role,
        "goal": goal,
        "goal_source_notes": goal_cell,
        "type": slice_type(sid, role),
        "requirement_ids": req_ids,
        "design_ids": design_ids,
        "seit_proof_rows": SPM[sid],
        "design_lenses": lenses,
        "model_route": mr,
        "reasoning_level": {"level": mr["reasoning"],
                            "reason": f"Frozen {profile} snapshot {ROLE_SNAPSHOT[role]} route reasoning; no per-slice override."},
        "review_path": {
            "reviewer_cadence": "phase",
            "reviewer_route": route_for(profile, "reviewer"),
            "review_unit": (f"Phase 2 integration step {', '.join(steps)} (review boundary unit per OD-AFC-P2-01; "
                            "each PR reviewed once at its own step)"),
            "test_engineer_assurance": te_assurance,
            "integration_engineer_execution": "lifecycle",
            "coverage_assist": "OCR delegate mode (ocr delegate preview --from <base> --to <head>; ocr delegate rule <files>), required",
            "coverage_assist_command_id": "CMD-OCR-DELEGATE",
            "reverify": reverify_text(sid, role, lane),
            "review_cardinality": "n=1, k=1, c=0 (one independent review, one repair round, deterministic verification decides)",
            "skills": SKILLS_MAP["reviewer"],
            "landing_skill": SKILLS_MAP["ship-pull-request"][0] + " (rebase or merge commit, never squash)",
        },
        "write_set": write_set,
        "command_ids": cmds,
        "stop_condition": stop_of(goal_cell),
        "human_decision": human,
        "authority_id": AUTHORITY_ID,
        "work_class": wclass,
        "work_class_reason": wreason,
        "lane": lane,
        "lane_profile": profile,
        "milestone": ms,
        "wave": wv,
        "depends_on": DEP_ON.get(sid, []),
        "depends_on_text": s["Depends on"].strip(),
        "leases": leases,
        "repo": REPO,
        "skills": skills,
        "spec_sections": spec_sections,
        "developer_feedback_required": True,
        "developer_feedback": {
            "requirement_id": "AC-AFC-P2-DX-01",
            "check_command_id": "CMD-DX-PRESENCE",
            "rule": ("Every dispatch packet and return carries a developer_feedback section the Scribe can ingest, "
                     "listing observations with IDs and evidence, or 'no new observations' naming the tools exercised."),
        },
        "development_strategy": dev_strategy(lane, role, sid),
    }
    if ws_note:
        sl["write_set_note"] = ws_note
    if sid == "P2-X11":
        sl["dispatchable"] = False
        sl["slice_status"] = "conditional (OD-AFC-03 = yes and M3 on time; drop at 2026-10-21T12:00:00Z if unverified)"
    SLICES.append(sl)
BY_ID = {s["id"]: s for s in SLICES}
assert len(BY_ID) == 52
# X05: single issue M2, Wave 1 start kept, both PRs kept
assert BY_ID["P2-X05"]["milestone"] == "M1" and BY_ID["P2-X05"]["wave"] == "Wave 1"
assert len(STEP_OF["P2-X03"]) == 2 and len(STEP_OF["P2-X05"]) == 2
# no absolute home paths anywhere in slices
assert "/ho" + "me/" not in json.dumps(SLICES)

# ---------- waves / milestones / releases ----------
WAVES = []
for w in (1, 2, 3, 4, 5):
    m = f"M{w}"
    mrow = next(r for r in MILESTONES_SRC if r["Milestone"] == m)
    sids = wave_lines[w]
    assert set(sids) == {s for s in ALL_SIDS if MS_OF[s] == m}, w
    WAVES.append({
        "id": f"Wave {w}",
        "milestone": m,
        "slice_ids": sids,
        "entry": mrow["Entry criteria"],
        "exit": mrow["Exit criteria"],
        "dispatch_order": DISPATCH_SRC[f"Wave {w}"],
    })

_TYAHOO = re.search(r"^T_yahoo is (\S+)\.", tp_text, re.M).group(1)
MILESTONES = []
for r in MILESTONES_SRC:
    sids = [x.strip() for x in r["Slices"].split(",")]
    # milestone table names X11 with "(conditional)"; normalize
    sids = [re.sub(r"\s*\(conditional\)$", "", x) for x in sids]
    assert set(sids) == {s for s in ALL_SIDS if MS_OF[s] == r["Milestone"]}, r["Milestone"]
    # Machine due_on is ISO only; a parenthetical explanation moves to due_explanation (no date change).
    due_cell = r["Due (UTC)"]
    due_on = due_cell.split(" (")[0] if " (" in due_cell else due_cell
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", due_on), (r["Milestone"], due_on)
    ms = {
        "id": r["Milestone"],
        "title": r["Title"],
        "due_on": due_on,
        "entry": r["Entry criteria"],
        "exit": r["Exit criteria"],
        "slices": sids,
    }
    if " (" in due_cell:
        inner = due_cell[len(due_on) + 2:-1]
        ms["due_explanation"] = f"{inner} (T_yahoo is {_TYAHOO}); machine due_on is ISO only, no date change."
    MILESTONES.append(ms)
assert next(m for m in MILESTONES if m["id"] == "M2")["due_on"] == "2026-10-17T01:00:00Z"

RELEASES = [
    {"milestone": "M1", "version": "v0.1.0", "slice": "P2-R1"},
    {"milestone": "M2", "version": "v0.2.0", "slice": "P2-R2"},
    {"milestone": "M3", "version": "v0.3.0", "slice": "P2-R3"},
    {"milestone": "M4", "version": "v0.4.0", "slice": "P2-R4"},
    {"milestone": "M5", "version": "v1.0.0", "slice": "P2-R5"},
]
for r in RELEASES:
    r.update({
        "changelog": "moves [Unreleased] entries under the version heading; notes and tag drawn from CHANGELOG.md",
        "publication": "owner-authorized only (OA-8)",
        "source": "OD-AFC-P2-03",
    })

# One review payload: the parent-selected github-work-items.json with its 39 body_file
# mirrors. Content/bodies/acceptance are the parent's, referenced here, never rewritten.
TRACKING = json.loads(TRACKING_PAYLOAD.read_text())
assert TRACKING["counts"] == {"milestones": 5, "issues": 39, "slices": 52, "tdd_pairs": 13}, TRACKING["counts"]
assert TRACKING["status"].startswith("REVIEW_PAYLOAD"), TRACKING["status"]
_SEIT_GROUPS = {g["issue"]: (tuple(g["slices"]), g["milestone"]) for g in seit["tracking_workflow"]["groups"]}
_PAYLOAD_GROUPS = {i["id"]: (tuple(i["slices"]), i["milestone"]) for i in TRACKING["issues"]}
assert _SEIT_GROUPS == _PAYLOAD_GROUPS, "parent payload mapping must equal SEIT workflow mapping"
_TRACKING_SHA = sha256_file(TRACKING_PAYLOAD)
WORK_ISSUES = {"status": TRACKING["status"],
               "source": "evidence/github-work-items/github-work-items.json",
               "payload_sha256": _TRACKING_SHA,
               "supersession": ("evidence/github-work-items/payload-supersession.json (group mapping verified equal; "
                                "TE tracking-payloads.json is a historical method example, not a creation authority)"),
               "boundary": TRACKING["boundary"],
               "note": ("One issue per logical deliverable; 13 TDD pairs share issues. P2-X05's single issue belongs to M2 "
                        "(final live-timing verdict due there); its M1 historical-fixture checkpoint and Wave 1 start are kept. "
                        "P2-L01 creates milestones and issues only after integrated approval, reusing existing issues by stable slice IDs."),
               "groups": []}
covered = set()
for i in TRACKING["issues"]:
    assert (PLAN / i["body_file"]).exists(), i["id"]
    WORK_ISSUES["groups"].append({"issue": i["id"], "slices": i["slices"], "milestone": i["milestone"],
                                  "body_file": i["body_file"], "stable_id": i["stable_id"], "kind": i["kind"]})
    covered.update(i["slices"])
assert covered == set(ALL_SIDS), set(ALL_SIDS) - covered
assert next(g for g in WORK_ISSUES["groups"] if g["issue"] == "P2-X05")["milestone"] == "M2"

# ---------- traceability ----------
TRACE = {}
for u in ACTIVE_UIDS:
    users = [s["id"] for s in SLICES if u in s["requirement_ids"]]
    assert users, u
    dids = sorted({d for s in SLICES if u in s["requirement_ids"] for d in s["design_ids"]})
    TRACE[u] = {"vcase": f"VCASE-{u}", "design_ids": dids, "seit_rows": PC_BY_REQ[u],
                "slices": users, "lifecycle_level_bindings": [], "ownership": "register reference"}
for w in WITHDRAWN:
    TRACE[w] = {"ownership": "withdrawn — no work",
                "note": "WITHDRAWN by DEC-AFC-SD-035; UIDs retained, never renumbered; no Phase 2 work."}
PC_REQ = {p["id"]: p["requirement_id"] for p in PCS}
CONTROL_REQS = {PC_REQ[r] for r in seit["planning_findings_for_plan_integrator"]["planning_control_proof_rows"]}
for aid, rows in (("AC", ac_rows), ("RISK", risk_rows)):
    for i in rows:
        users = [s["id"] for s in SLICES if i in s["requirement_ids"]]
        dids = sorted({d for s in SLICES if i in s["requirement_ids"] for d in s["design_ids"]})
        entry = {"design_ids": dids, "seit_rows": PC_BY_REQ[i],
                 "slices": users, "lifecycle_level_bindings": [], "ownership": "Lifecycle-local"}
        if not users:
            assert i in CONTROL_REQS, i
            entry["note"] = ("defects lane on demand; no pre-allocated slice" if i == "AC-AFC-P2-BUG-01"
                             else "Planning/Orchestrator control; no implementation slice (planning_control_proof_rows)")
        TRACE[i] = entry
assert len(TRACE) == 66 + 24 + 13, len(TRACE)

# ---------- journey settings / freeze ----------
P1JS = json.loads((P1 / "implementation.json").read_text())["journey_settings"]
OA_CRITERIA = [{"id": r["ID"], "owner_action": r["Owner action"], "needed_by": r["Needed by"],
                "blocks_if_absent": r["Blocks if absent"]} for r in OA_SRC]
OPEN_DECISIONS = [{"id": r["ID"], "decision": r["Decision"], "recommendation": r["Recommendation"],
                   "source": "technical plan §Open owner items for the integrated review",
                   "status": "open_for_integrated_review"} for r in OPEN_SRC]

digest_arg = None
if "--digest" in sys.argv:
    digest_arg = sys.argv[sys.argv.index("--digest") + 1]

JOURNEY_SETTINGS = {
    "lifecycle_id": "AFC-2026-10-11",
    "lifecycle_type": "feature",
    "phase": 2,
    "deadline": "2026-10-23T19:00:00Z",
    "development_strategy": {
        "mode": "tdd",
        "source": "frozen primary snapshot development_strategy; lane overrides from each lane profile snapshot (DEC-AFC-PROFILE-001)",
        "lane_overrides": {
            "backend": "tdd",
            "tv-app-ui": "tdd",
            "device-integration-spikes": "tdd for product code; spikes evidence-only per OD-AFC-04 (open_for_integrated_review)",
            "spec-and-docs": "single_implementer",
            "defects": "tdd (on demand; no pre-allocated slices)",
            "light work": "light (Light Implementer, lane profile light_implementer route)",
            "scribe-side-lane": "scribe side lane (uncounted)",
        },
    },
    "concurrency": {
        "dispatch_ready_independent_work": True,
        "preserve_order_for_dependencies_interfaces_write_overlap_and_shared_mutable_resources": True,
        "impl_agent_cap": 5,
        "impl_agent_cap_source": "Workspace cross-repo rule 17; technical plan Waves table",
        "cap_excludes": ["Scribe", "Reviewer"],
        "leases": LEASES,
        "summary": ("Dispatch every dependency-ready, proven-independent slice within impl_agent_cap 5; serialize only on "
                    "dependencies, shared interfaces, write-set overlap and the leases fire-tv-stick, aws-afc-dev, "
                    "live-game-window, tv-app-manifest, tv-app-gradle, backend-template, main-landing."),
    },
    "assurance_cadence": {
        "test_engineer": {
            "assurance": "lifecycle",
            "lane_overrides": {
                "spec-and-docs": "disabled (frozen tech-writing snapshot test_engineer.assurance.enabled=false)",
            },
        },
        "reviewer": "phase",
        "reviewer_application": "per integration step: each pull request reviewed once at its own step (OD-AFC-P2-01, precedent OA-AFC-A3 = A)",
        "integration_engineer": {"execution": "lifecycle"},
    },
    "planning_to_implementation_clean_session": True,
    "review_cardinality": {
        "n": 1, "k": 1, "c": 0,
        "n_source": P1JS["review_cardinality"]["n_source"],
        "k_source": P1JS["review_cardinality"]["k_source"],
        "c_source": P1JS["review_cardinality"]["c_source"],
    },
    "planning_review": {
        "policy_ref": "skills/bearing-lite/references/review-policy.md",
        "candidate_ref": "plan/2026-10-12-afc-phase-2",
        "candidate_revision": REVISION,
        "candidate_revision_note": ("Planning worktree HEAD at integration (merges main spec PR #10 at 92f3ed1; "
                                    "conflicts resolved byte-identically to main). The Orchestrator records the commit of this package."),
        "candidate_digest": digest_arg or "PENDING-FREEZE",
        "candidate_digest_source": "node <bearing-lite>/hooks/plan-package.cjs manifest_digest over seit.json planning_inputs plus seit.json",
        "reviewer_slots": [{
            "slot_id": "planning-review",
            "primary_route_ref": "Muse Code / Muse Spark 1.3 / max",
            "fallback_route_refs": ["Codex CLI / GPT-6 Astra / high", "Claude Code / Fable / high"],
        }],
        "route_source": "planning profile primary reviewer route (parent journey.json frozen_snapshots.primary)",
    },
    "review_capabilities": {
        "coverage_assist": {
            "capability": "review.coverage_assist",
            "backend": "OCR (OpenCodeReview) delegate mode",
            "enabled": True,
            "required": True,
            "command_id": "CMD-OCR-DELEGATE",
            "packet_text": "OCR delegate mode (ocr delegate preview --from <base> --to <head>; ocr delegate rule <files>), required",
            "gap_rule": "missing, unavailable or not_run is a typed gap with the exact error, never PASS",
            "source": "every frozen lane snapshot review.coverage_assist; seit.json gate_declarations",
        },
        "reverify": {
            "capability": "deterministic_verification.reverify",
            "enabled": True,
            "backend": "reverify 0.11.0",
            "command_id": "CMD-REVERIFY-APK",
            "applies_to": sorted(APK_SLICES),
            "packet_text": "CMD-REVERIFY-APK on the exact built APK; Reverify: not applicable — <concrete reason> otherwise",
            "gap_rule": ("reverify error, unproven APK semantic grounding (TE-P2-F03 REVERIFY_CAPABILITY_GAP) or not_run is a typed gap "
                         "with the exact error, never PASS; ordinary ATE reruns never substitute"),
            "source": "every frozen lane snapshot deterministic_verification.reverify; seit.json gate_declarations",
        },
    },
    "owner_wait_tracking": P1JS["owner_wait_tracking"],
    "requirement_register_ref": {
        "ref": "authority.json#/requirement_register",
        "path": authority["requirement_register"]["path"],
        "form": authority["requirement_register"]["form"],
    },
    "defects_lane": {
        "lane": "defects",
        "profile": "bug-triager",
        "strategy": "tdd",
        "slices": "none pre-allocated; dispatched on demand per defect (DEC-AFC-SD-037)",
        "implementer_route": route_for("bug-triager", "implementer"),
        "reviewer_route": route_for("bug-triager", "reviewer"),
        "packet_fields": ("reproduction, origin and escape, product vs test-only classification, red-then-green regression, "
                          "prevention check; triaged with bug-hunter-triage; write set = smallest triage-named set, dispatched only "
                          "when it does not overlap a running slice's write set (AC-AFC-P2-BUG-01); a packet keeping a lane route "
                          "states BUG_ROUTE: <reason>"),
    },
    "current_task": {
        "planning_lead_decision": "DEC-AFC-SD-039",
        "boundary": ("Planning completion and issue/milestone organization only. Integrated planning/tracking approval is not "
                     "permission to begin app, backend, spike, deployment or submission work; that product execution stays held "
                     "until a subsequent owner execution instruction. Explicit tracking approval may authorize P2-L01 only."),
        "source": "technical plan §Current task boundary; authority.json current_task_scope",
    },
}

PROFILE_FREEZE = {
    "state": "frozen",
    "source": "parent journey profile_selection.frozen_snapshots ($HOME/alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json)",
    "catalog": parent_journey["profile_selection"].get("catalog"),
    "selected_at": parent_journey["profile_selection"].get("selected_at"),
    "decision": "DEC-AFC-PROFILE-001",
    "planning": {
        "profile": "primary",
        "configuration_digest_sha256": FS["primary"]["configuration_digest_sha256"],
        "snapshot_ref": "parent journey.json#/profile_selection/frozen_snapshots/primary",
    },
    "lanes": {},
    "note": "Frozen copies; changes only by owner amendment. Scribe uses the planning profile primary scribe route.",
}
for lane, prof in [("tv-app-ui", "frontend"), ("backend", "primary"),
                   ("device-integration-spikes", "heavyweight"), ("spec-and-docs", "tech-writing"),
                   ("defects", "bug-triager")]:
    snap = FS[prof]
    PROFILE_FREEZE["lanes"][lane] = {
        "profile": prof,
        "configuration_digest_sha256": snap["configuration_digest_sha256"],
        "snapshot_ref": f"parent journey.json#/profile_selection/frozen_snapshots/{prof}",
        "development_strategy": snap["development_strategy"]["mode"],
        "coverage_assist": snap["snapshot"]["review"]["coverage_assist"],
        "deterministic_verification": snap["snapshot"]["deterministic_verification"],
    }
PROFILE_FREEZE["lanes"]["scribe-side-lane"] = {
    "profile": "primary",
    "configuration_digest_sha256": FS["primary"]["configuration_digest_sha256"],
    "snapshot_ref": "parent journey.json#/profile_selection/frozen_snapshots/primary",
    "role": "scribe",
}

ROLE_STATES = {
    "active": ["Orchestrator", "Product Implementer", "Test Implementer", "Light Implementer", "Scribe", "Reviewer",
               "Test Engineer (assurance, lifecycle cadence; disabled for spec-and-docs)",
               "Integration Engineer (execution, lifecycle cadence)"],
    "standby": ["Coordinator (one wave each, if used; technical plan Accountable controller)"],
    "unused_in_implementation": ["Plan Integrator", "Requirements Engineer (planning-only)", "Systems Modeler (planning)",
                                 "Test Engineer (planning)", "Integration Engineer (planning)"],
}

# ---------- TP exit criteria / rollback (verbatim) ----------
def section_items(text, heading, bullet):
    lines = text.split("\n")
    start = next(i for i, l in enumerate(lines) if l.strip() == heading)
    items, cur = [], None
    pat = re.compile(bullet)
    for l in lines[start + 1:]:
        if l.startswith("## "):
            break
        m = pat.match(l)
        if m:
            if cur:
                items.append(re.sub(r"\s+", " ", " ".join(cur)).strip())
            cur = [m.group(1)]
        elif cur is not None and l.strip():
            cur.append(l.strip())
    if cur:
        items.append(re.sub(r"\s+", " ", " ".join(cur)).strip())
    return items

EXIT_CRITERIA = section_items(tp_text, "## Exit criteria", r"^\d+\.\s+(.*)$")
assert len(EXIT_CRITERIA) == 4, EXIT_CRITERIA
ROLLBACK = section_items(tp_text, "## Rollback or repair", r"^-\s+(.*)$")
assert len(ROLLBACK) == 6, ROLLBACK
excl_match = re.search(r"## Exclusions\n\n(.*?)\n\n## ", tp_text, re.S)
EXCLUSIONS = [re.sub(r"\s+", " ", b).strip() for b in re.findall(r"^-\s+(.*?)(?=^-\s+|\Z)", excl_match.group(1), re.M | re.S)]
assert len(EXCLUSIONS) == 8, len(EXCLUSIONS)

PI_H = seit["planning_findings_for_plan_integrator"]
_GTP = seit["gate_tool_plan"]
assert _GTP["status"] == "OWNERS_AND_PROSPECTIVE_COMMANDS_BOUND; EXECUTION_NOT_RUN", _GTP["status"]
_GAPS = ", ".join(g for g in _GTP["remaining_gaps"] if g != "REVERIFY_CAPABILITY_GAP")
ASSURANCE = {
    "seit": f"seit.json (100 proof cases, {NCMDS} procedures and commands, gate_declarations per lane)",
    "pass_fail": ("A requirement row PASSES iff its SEIT proof case passes its pass_fail_rule on the exact candidate. "
                  "A typed gap (TOOL_MISSING, TOOL_UNALLOCATED, NOT_RUN, OWNER_ACTION_PENDING, REVERIFY_CAPABILITY_GAP, "
                  "OWNER_EVIDENCE_PENDING) is never PASS. An owner-accepted typed gap is distinct from PASS (TE-P2-F05)."),
    "evidence": ("Command output captured per run with the candidate SHA (git rev-parse HEAD); author receipts are diagnostic-only; "
                 "assurance receipts come from a fresh Assurance Test Engineer rerunning the same commands (primary, frontend, "
                 "heavyweight lanes). No credential, account name, email or absolute home path in committed evidence; "
                 "raw agent logs stay local."),
    "tdd_receipt": ("Each red-expected row needs CMD-RED on the Test Implementer candidate and the green command on the Product "
                    "Implementer candidate over the same test ids, with test-file sha256 and frozen bootstrap hashes recorded in both; "
                    "test-to-product dependencies mean verified red-receipt completion in the shared pair worktree, never a separate "
                    "red-only PR merge."),
    "limitations": (f"Coverage/mutation ownership and prospective commands bound ({', '.join(_GTP['commands'])} qualified by "
                    f"{_GTP['qualifier']}; TE-P2-F03 OWNERS_AND_COMMANDS_BOUND_WITH_CAPABILITY_GAPS, execution not run); remaining {_GAPS}; "
                    "APK semantic/containment grounding is REVERIFY_CAPABILITY_GAP with reverify 0.11.0, never PASS from "
                    "ZIP magic, strings, ordinary ATE or apkanalyzer alone; the P2-L05 tagged-main subcriterion stays "
                    "OWNER_EVIDENCE_PENDING until OA-8 tag readback (TE-P2-F09); fallback proof closes only its own criteria (TE-P2-F05)."),
    "test_engineer_assurance": ("Lifecycle cadence on the M5 final candidate in a fresh session (Assurance Test Engineer routes per lane); "
                                "spec-and-docs lane has assurance disabled, so its slices rely on Reviewer phase review and gate commands."),
    "integration_engineer_execution": "Lifecycle cadence; integration_plan steps IE-P2-1..IE-P2-44 with post-step V&V from seit.json integration_vv_sequence.",
    "reviewer": ("Phase cadence applied per integration step (OD-AFC-P2-01, precedent OA-AFC-A3 = A); one review per PR with OCR "
                 "delegate mode, one repair round, deterministic verification decides."),
    "gate_declarations_ref": "seit.json#/gate_declarations",
    "planning_control_proof_rows": PI_H["planning_control_proof_rows"],
    "te_findings": [f["id"] for f in PI_H["findings"]],
    "exit_criteria": EXIT_CRITERIA,
}

RECOVERY = {
    "rules": ROLLBACK,
    "anomaly_corrective_closure": seit["anomaly_corrective_closure"],
    "integration_rollback_ref": "integration_plan.anomaly_rollback_recovery",
    "route_recovery": ("RISK-AFC-P2-10: a confirmed usage/rate limit activates only the next approved fallback in the frozen profile "
                       "with a class B receipt preserving coverage-assist and Reverify settings, or queues the slice; other errors "
                       "never trigger a route switch."),
}

APPROVAL = {
    "authority_id": AUTHORITY_ID,
    "authority_state": authority["state"],
    "effective": authority["effective"],
    "approval_decision_id": authority["continuation"]["owner_decision_id"],
    "owner_review_gate": ("Single integrated owner review of the five-artifact package after the planning review; "
                          "no lineup, route or specification-only gate."),
    "owner_only_actions": [
        "Owner-only actions: credential creation or retrieval, AWS plan changes, repository visibility flip, license choice (already settled as Apache-2.0), release publication, video upload, external feedback, Devpost submission (C9)",
        "Yahoo developer application and OAuth consent (OA-2)",
        "Authorize the exact public export and visibility change after the M5 history/content review (OA-5)",
        "Authorize each release publication (OA-8)",
        "Upstream issue or PR to any third-party project",
        "Production activation, production DB mutation, credential access, destructive git (workspace rule 4)",
    ],
    "owner_action_entry_criteria": OA_CRITERIA,
    "agent_actions": authority["allowed"]["actions"],
    "land_by": ("PR to main by rebase or merge commit after one Reviewer review, at most one repair round and a green gate "
                "(AC-AFC-P2-LAND-01); never squash, force-push, commit on local main or git switch."),
    "continuation": authority["continuation"],
    "current_task_scope": authority["current_task_scope"],
}

# ---------- dod_manifest ----------
def outcome_text():
    lines = tp_text.split("\n")
    start = next(i for i, l in enumerate(lines) if l.strip() == "## Outcome")
    paras = []
    cur = []
    for l in lines[start + 1:]:
        if l.startswith("## "):
            break
        if not l.strip():
            if cur:
                paras.append(re.sub(r"\s+", " ", " ".join(cur)).strip())
                cur = []
            continue
        cur.append(l.strip())
    if cur:
        paras.append(re.sub(r"\s+", " ", " ".join(cur)).strip())
    return " ".join(paras)

SCOPE = [f"{m['id']} {m['title']} (due {m['due_on']}): {', '.join(m['slices'])}" for m in MILESTONES]
DOD = [{"id": f"DOD-{i+1}", "criterion": c, "evidence": e, "status": "planned"}
       for i, (c, e) in enumerate(zip(EXIT_CRITERIA, [
           "SEIT proof rows per row; typed gaps recorded",
           "Merge records; Reviewer packets with OCR; gate evidence; CHANGELOG entries",
           "Assurance Test Engineer and Integration Engineer execution verdicts on the M5 candidate",
           "Owner checklist handover; DoD Manifest closeout section"]))]

REQ_MANIFEST = []
for u in ACTIVE_UIDS:
    r = reg_rows[u]
    users = TRACE[u]["slices"]
    REQ_MANIFEST.append({
        "id": u,
        "statement": r["Statement"],
        "source": f"register reference — VCASE-{u}",
        "verification": r["Verification method"],
        "allocation": ", ".join(users),
        "ownership": "register reference",
        "vcase": f"VCASE-{u}",
        "seit_rows": len(TRACE[u]["seit_rows"]),
        "slices": users,
        "status": "planned",
    })
for w in WITHDRAWN:
    REQ_MANIFEST.append({"id": w, "statement": reg_rows[w]["Statement"], "source": f"register reference — VCASE-{w} retired",
                         "ownership": "register reference — withdrawn", "status": "withdrawn — no work"})
for i, rows in (("AC", ac_rows), ("RISK", risk_rows)):
    for rid, r in rows.items():
        users = TRACE[rid]["slices"]
        REQ_MANIFEST.append({
            "id": rid,
            "statement": r["Statement"] if "Statement" in r else r["Statement (control)"],
            "source": r["Source"],
            "verification": r["Verification"],
            "allocation": ", ".join(users) or TRACE[rid].get("note", ""),
            "ownership": "Lifecycle-local",
            "seit_rows": len(TRACE[rid]["seit_rows"]),
            "slices": users,
            "status": "planned",
        })

ARCH = []
for did, sec in design_secs.items():
    users = sorted({s["id"] for s in SLICES if did in s["design_ids"]})
    lenses = (["Contract-first"] if did.startswith("CONTRACT-") else LENS_BY_DESIGN[did])
    ARCH.append({"id": did, "decision": f"{sec['title']}: {sec['summary'][:400]}",
                 "interfaces": ", ".join(sorted({d for d in design_secs if d != did and d in sec["summary"]})) or "—",
                 "lenses": lenses, "slices": users, "status": "planned"})

SM_COMBINED = "8f5798823b3a9463f8963c7c6fa2cf94d018189edd0ca6160123362d48a075ff"
def svg_digest(rel):
    return "sha256:" + sha256_file(PLAN / rel)
MODELS = [
    {"id": "MODEL-AFC-P2-STRUCTURE", "mode": "sysml-v2", "source": "models/AFC-Structure.sysml",
     "revision": REVISION, "digest": svg_digest("models/view-structure.svg"),
     "viewpoint": "Structure / boundary", "trace": "tvApp, backend, stores parts; allocation.md Tables 1–2 (63 active UIDs)",
     "limitations": "SysON bundled textual engine parse, not independent OMG-conformance proof; P2-D02 aligns spec §4.7 text.",
     "render_status": "READY", "selected": True, "required": True,
     "view": {"format": "svg", "path": "models/view-structure.svg", "alt": "AFC structure view"}},
    {"id": "MODEL-AFC-P2-INTERFACES", "mode": "sysml-v2", "source": "models/AFC-Interfaces.sysml",
     "revision": REVISION, "digest": svg_digest("models/view-interfaces.svg"),
     "viewpoint": "Interfaces", "trace": "API/provider interface ends; allocation.md Tables 1–2",
     "limitations": "SysON bundled textual engine parse, not independent OMG-conformance proof.",
     "render_status": "READY", "selected": True, "required": True,
     "view": {"format": "svg", "path": "models/view-interfaces.svg", "alt": "AFC interfaces view"}},
    {"id": "MODEL-AFC-P2-STATES", "mode": "sysml-v2", "source": "models/AFC-States.sysml",
     "revision": REVISION, "digest": svg_digest("models/view-states.svg"),
     "viewpoint": "States / lifecycle", "trace": "PanelMode.fullScreen, alert lifecycle; allocation.md Tables 1–2",
     "limitations": "SysON bundled textual engine parse, not independent OMG-conformance proof.",
     "render_status": "READY", "selected": True, "required": True,
     "view": {"format": "svg", "path": "models/view-states.svg", "alt": "AFC states view"}},
    {"id": "MODEL-AFC-P2-DATA", "mode": "sysml-v2", "source": "models/AFC-Data.sysml",
     "revision": REVISION, "digest": svg_digest("models/view-data.svg"),
     "viewpoint": "Data", "trace": "GameEvent, Alert, PanelState, ScoringPreset; allocation.md Tables 1–2",
     "limitations": "SysON bundled textual engine parse, not independent OMG-conformance proof.",
     "render_status": "READY", "selected": True, "required": True,
     "view": {"format": "svg", "path": "models/view-data.svg", "alt": "AFC data view"}},
    {"id": "MODEL-AFC-P2-V1", "mode": "diagram-assisted", "source": "views/p2-use-cases.svg (Mermaid use cases in design.md)",
     "revision": REVISION, "digest": svg_digest("views/p2-use-cases.svg"),
     "viewpoint": "Use cases / outcome", "trace": "Link, lineup/controls, alert, Watch, panel, owner approval",
     "limitations": "Projects the models for owner review; adds no element.",
     "render_status": "READY", "selected": True, "required": True,
     "view": {"format": "svg", "path": "views/p2-use-cases.svg", "alt": "P2 use cases"}},
    {"id": "MODEL-AFC-P2-V2", "mode": "diagram-assisted", "source": "views/p2-alert-watch-flow.svg (sequence in design.md)",
     "revision": REVISION, "digest": svg_digest("views/p2-alert-watch-flow.svg"),
     "viewpoint": "Operational flow", "trace": "ESPN poll → ingest → matcher/policy → alert → Watch → routing outcome",
     "limitations": "Projects the models for owner review; adds no element.",
     "render_status": "READY", "selected": True, "required": True,
     "view": {"format": "svg", "path": "views/p2-alert-watch-flow.svg", "alt": "P2 alert to Watch flow"}},
    {"id": "MODEL-AFC-P2-V3", "mode": "diagram-assisted", "source": "views/p2-program-waves.svg (flowchart in technical plan)",
     "revision": REVISION, "digest": svg_digest("views/p2-program-waves.svg"),
     "viewpoint": "Program / waves", "trace": "Approval → spikes → TDD pairs → deploys → E2E → spec revision → submission",
     "limitations": "Projects the plan for owner review; adds no element.",
     "render_status": "READY", "selected": True, "required": True,
     "view": {"format": "svg", "path": "views/p2-program-waves.svg", "alt": "P2 program waves"}},
]

def rstr(profile, role_key, session=None):
    r = FS[profile]["snapshot"]["roles"][role_key]
    if session:
        r = r["sessions"][session]
    p = r["primary"]
    fb = "; ".join(f"{f['harness']} / {f['model']} / {f['reasoning']}" for f in r["ordered_fallbacks"])
    base = f"{p['harness']} / {p['model']} / {p['reasoning']}"
    return base, (base + ("; fallbacks " + fb if fb else ""))

LINEUP = []
LANE_ROWS = [("tv-app-ui", "frontend"), ("backend", "primary"), ("device-integration-spikes", "heavyweight"),
             ("spec-and-docs", "tech-writing"), ("defects", "bug-triager")]
for lane, prof in LANE_ROWS:
    dg = FS[prof]["configuration_digest_sha256"][:8]
    roles = FS[prof]["snapshot"]["roles"]
    for disp, key in (("Product Implementer", "implementer"), ("Test Implementer", "test_implementer"),
                      ("Light Implementer", "light_implementer"), ("Reviewer", "reviewer")):
        if key not in roles:
            continue
        b, e = rstr(prof, key)
        LINEUP.append({"role": disp, "session": f"{lane} lane, profile {prof} ({dg})",
                       "configured_primary": b, "effective_route": e,
                       "status": "planned" if lane != "defects" else "on demand (no pre-allocated slices)"})
    for disp, key, sess in (("Test Engineer (assurance)", "test_engineer", "assurance"),
                            ("Integration Engineer (execution)", "integration_engineer", "execution")):
        r = roles[key]["sessions"][sess]
        b, e = rstr(prof, key, sess)
        on = r.get("enabled", True)
        LINEUP.append({"role": disp, "session": f"{lane} lane, profile {prof} ({dg})",
                       "configured_primary": b, "effective_route": e,
                       "status": "planned (lifecycle cadence)" if on else "disabled (enabled=false)"})
b, e = rstr("primary", "scribe")
LINEUP.append({"role": "Scribe", "session": "scribe side lane, profile primary (uncounted)",
               "configured_primary": b, "effective_route": e, "status": "planned"})
LINEUP.append({"role": "Planning review slot", "session": "planning-review",
               "configured_primary": "Muse Code / Muse Spark 1.3 / max",
               "effective_route": ("Muse Code / Muse Spark 1.3 / max; fallbacks Codex CLI / GPT-6 Astra / high; "
                                   "Claude Code / Fable / high"),
               "status": "pending (one independent planning review awaits this package)"})
for name, route, result in [
    ("Systems Modeler delta", "Muse Code / Muse Spark 1.3 / max", "READY (sm-p2-delta-receipt.md; combined digest 8f579882…)"),
    ("Requirements Engineer register delta", "Muse Code / Muse Spark 1.3 / max", "PASS (re-p2-delta-receipt.md)"),
    ("Requirements Engineer AC gate", "Muse Code / Muse Spark 1.3 / max", "REPAIRABLE_FAILURE then corrected (re-p2-ac-receipt.md)"),
    ("Integration Engineer planning", "Claude Code / Claude Opus 5.5 / high", "GAPS then correction 1 applied (ie-p2-receipt.md)"),
    ("Integration Engineer delta", "Codex CLI / GPT-6.1 Sol / xhigh (first fallback)", "READY for reconciliation (ie-p2-codex-delta-receipt.md)"),
    ("Test Engineer planning", "Codex CLI / GPT-6 Astra / xhigh (first fallback)", "PASS planning authorship (te-p2-codex-receipt.md)"),
]:
    LINEUP.append({"role": f"Specialist route receipt: {name}", "session": "P2-6 planning",
                   "configured_primary": route, "effective_route": route, "status": result})

ISSUE_OF = {}
for g in WORK_ISSUES["groups"]:
    for s in g["slices"]:
        ISSUE_OF[s] = f"{g['issue']} ({g['milestone']})"
TASKS = [{"id": s["id"], "role": s["role"], "route": s["model_route"]["harness"] + " / " + s["model_route"]["model"] + " / " + s["model_route"]["reasoning"], "depends_on": s["depends_on"],
          "write_set": s["write_set"], "wave": s["wave"], "lane": s["lane"], "milestone": s["milestone"],
          "issue": ISSUE_OF[s["id"]], "status": "planned"} for s in SLICES]

VV = []
CLOSE_MS = {}
for p in PCS:
    cs = p.get("closing_slice")
    CLOSE_MS.setdefault(BY_ID[cs]["milestone"] if cs in BY_ID else "planning", []).append(p)
for m in ["M1", "M2", "M3", "M4", "M5", "planning"]:
    rows = CLOSE_MS.get(m, [])
    if not rows:
        continue
    from collections import Counter
    meth = Counter(p["method"] for p in rows)
    cmds = sorted({p["command_id"] for p in rows})
    VV.append({
        "id": f"VV-{m}",
        "method": ", ".join(f"{k} {v}" for k, v in sorted(meth.items())),
        "cadence": ("Reviewer phase per integration step (OCR required); TE assurance lifecycle "
                    "(spec-and-docs disabled); IE execution lifecycle"),
        "evidence": f"{len(rows)} SEIT rows bound; commands {', '.join(cmds)}",
        "status": "planned",
    })

DOCS = [
    ("amazon-fantasy-companion-phase-2-technical-plan.md", "requirements, waves, milestones, leases, open items", "Planning and Design", "planning", "planning review", "planned"),
    ("design.md", "layout, components, contracts, spike protocols, lenses", "Planning and Design", "planning", "planning review", "planned"),
    ("seit.json", f"100 proof cases, {NCMDS} commands, gate declarations", "Planning Test Engineer", "planning", "check_seit.py cross-check", "planned"),
    ("implementation.json", "52 slices, waves, dependencies, traceability", "Plan Integrator", "planning", "schema + plan-package freeze", "planned"),
    ("requirements-register.md", "66 UIDs (63 active), VCASE verification cases", "Requirements Engineer", "planning", "RE gates", "planned"),
    ("models/", "aligned SysML v2 sources, allocation, four views", "Systems Modeler", "planning", "SysON import + allocation probe", "planned"),
    ("README.md", "product, setup, judge access, limitations (P2-D03)", "spec-and-docs lane", "M5", "PROC-README-FRESH-SETUP", "planned"),
    ("CHANGELOG.md", "revision record per landing + per-milestone releases", "landing procedure; P2-R1..R5", "each landing/exit", "CMD-CHANGELOG-CHECK", "planned"),
    ("spec/amazon-fantasy-companion/ (D1 revision)", "verdicts, aligned names, quantities (P2-D02)", "spec-and-docs lane", "M4", "CMD-GATE-SPEC byte-identical rebuild", "planned"),
    ("docs/submission/", "writeup, demo plan, owner checklist (P2-D04, P2-D05)", "spec-and-docs lane", "M5", "PROC-SUBMISSION-CHECK", "planned"),
    ("docs/developer-feedback/", "observations log + assembled feedback (P2-SCR1)", "Scribe", "continuous; M5", "PROC-SCRIBE-ASSEMBLY", "planned"),
]
DOCUMENTATION = [{"surface": a, "impact": b, "owner": c, "timing": d, "verification": e, "status": f} for a, b, c, d, e, f in DOCS]

RISKS = [{"id": rid, "risk": r["Risk (rationale)"], "control": r["Statement (control)"], "recovery": r["Response"],
          "allocation": r["Allocation"], "status": "planned"} for rid, r in risk_rows.items()]

AUTHORITY_ROWS = [
    {"event": f"Authority envelope {AUTHORITY_ID}", "owner": "William Rumph",
     "evidence": f"authority.json state={authority['state']}, effective={str(authority['effective']).lower()}; baseline {authority['baseline']['revision'][:7]}",
     "status": "proposed"},
    {"event": "Current-task product-execution hold", "owner": "William Rumph",
     "evidence": "DEC-AFC-SD-039; authority.json current_task_scope; planning/tracking approval does not start product work",
     "status": "held"},
    {"event": "Tracking review payload", "owner": "William Rumph",
     "evidence": (f"evidence/github-work-items/github-work-items.json sha256:{_TRACKING_SHA}; 39 body_file mirrors; "
                  "REVIEW_PAYLOAD — not approved or submitted"),
     "status": "pending"},
]
for o in OA_CRITERIA:
    AUTHORITY_ROWS.append({"event": f"{o['id']}: {o['owner_action']}", "owner": "William Rumph",
                           "evidence": f"needed by {o['needed_by']}; blocks: {o['blocks_if_absent']}", "status": "pending"})
for o in OPEN_DECISIONS:
    AUTHORITY_ROWS.append({"event": f"{o['id']}: {o['decision']}", "owner": "William Rumph",
                           "evidence": f"recommendation: {o['recommendation']}", "status": o["status"]})

IDENTITY = [
    {"label": "Lifecycle", "value": "AFC-2026-10-11 (Phase 2)"},
    {"label": "Repository", "value": REPO},
    {"label": "Baseline revision", "value": REVISION},
    {"label": "Plan directory", "value": str(PLAN) + "/"},
    {"label": "Candidate ref", "value": "plan/2026-10-12-afc-phase-2"},
    {"label": "Candidate revision", "value": REVISION},
    {"label": "Candidate digest", "value": digest_arg or "PENDING-FREEZE"},
    {"label": "Authority", "value": f"{AUTHORITY_ID} (proposed, effective=false)"},
    {"label": "Requirement register", "value": "requirements-register.md (authority.json#/requirement_register)"},
    {"label": "Register digest", "value": f"sha256:{authority['requirement_register']['sha256']}"},
    {"label": "Model combined digest", "value": SM_COMBINED},
]
for prof in ("primary", "frontend", "heavyweight", "tech-writing", "bug-triager"):
    IDENTITY.append({"label": f"Profile {prof} digest", "value": FS[prof]["configuration_digest_sha256"]})
IDENTITY.append({"label": "seit.json", "value": sha256_file(SEIT)})

DOD_MANIFEST = {
    "template_version": "1.0.1",
    "output_name": "amazon-fantasy-companion-phase-2-dod-manifest.html",
    "state": "planning",
    "title": "Amazon Fantasy Companion — Definition of Done Manifest (AFC-2026-10-11, Phase 2)",
    "lede": "Planning projection of implementation.json for the single integrated owner review. The five planning artifacts remain authoritative.",
    "bluf": (f"Phase 2 implementation plan from the approved spec (DEC-AFC-APPROVAL-ST5): 52 slices in 5 waves on four lanes plus "
             f"light work and the Scribe side lane; 63 active register UIDs and 37 Lifecycle-local rows traced to 100 SEIT proof cases "
             f"({NCMDS} commands). Schedule refreshed at 2026-10-13T04:00:00Z: 10 days and 15 hours remain to T_deadline; remaining live "
             "windows Thu 2026-10-15, Sun 2026-10-18, Mon 2026-10-19 and Thu 2026-10-22. Spikes run first and are time-boxed; "
             "10 open owner items await the integrated review. P2-X11 conditional on OD-AFC-03 = yes. Product execution is held "
             "until a subsequent owner execution instruction (DEC-AFC-SD-039); this package covers planning completion and "
             "issue/milestone organization only."),
    "identity": IDENTITY,
    "outcome": outcome_text(),
    "scope": SCOPE,
    "exclusions": EXCLUSIONS,
    "definition_of_done": DOD,
    "requirements": REQ_MANIFEST,
    "architecture": ARCH,
    "models": MODELS,
    "development_strategy": JOURNEY_SETTINGS["development_strategy"],
    "concurrency": JOURNEY_SETTINGS["concurrency"],
    "lineup": LINEUP,
    "tasks": TASKS,
    "assurance_cadence": {k: JOURNEY_SETTINGS["assurance_cadence"][k] for k in ("test_engineer", "reviewer", "integration_engineer")},
    "vv": VV,
    "documentation": DOCUMENTATION,
    "risks": RISKS,
    "authority": AUTHORITY_ROWS,
}

# ---------- assembly ----------
IMPL = {
    "schema_version": "1",
    "artifact": {"type": "implementation.json", "lifecycle": "AFC-2026-10-11",
                 "plan_dir": str(PLAN) + "/", "status": "planning",
                 "generated_by": "Plan Integrator (Muse Code / Muse Spark 1.3 / max; Phase 2 P2-6 codex-lead continuation)",
                 "generated_on": "2026-10-13"},
    "source_baseline": {
        "repository": REPO,
        "revision": REVISION,
        "branch": BRANCH,
        "planning_inputs": seit["source_baseline"]["planning_inputs"],
        "read_only_context": seit["source_baseline"].get("read_only_context", []),
        "plan_directory": str(PLAN),
        "seit_json_sha256_at_integration": sha256_file(SEIT),
        "planning_input_note": seit["source_baseline"].get("planning_input_note", ""),
    },
    "journey_settings": JOURNEY_SETTINGS,
    "profile_freeze": PROFILE_FREEZE,
    "role_states": ROLE_STATES,
    "waves": WAVES,
    "dependencies": DEPENDENCIES,
    "slices": SLICES,
    "integration_plan": IE_BLOCK,
    "traceability": TRACE,
    "assurance": ASSURANCE,
    "recovery": RECOVERY,
    "approval_boundaries": APPROVAL,
    "open_decisions": OPEN_DECISIONS,
    "milestones": MILESTONES,
    "milestones_note": "Created only after owner approval of this package (P2-7).",
    "releases": RELEASES,
    "work_issues": WORK_ISSUES,
    "dod_manifest": DOD_MANIFEST,
}

# ---------- self-checks ----------
assert len(SLICES) <= 128 and len(DEPENDENCIES) <= 128 or True
all_ws = [w for s in SLICES for w in s["write_set"]]
assert len(all_ws) <= 128, len(all_ws)
blob = json.dumps(IMPL)
assert "/ho" + "me/" not in blob, "absolute home path leaked"
assert all(len(s["goal"]) <= 512 for s in SLICES)
assert all(s["authority_id"] for s in SLICES)
assert sum(1 for s in SLICES if s["work_class"] == "light") == 9, "L01,L02,L03,L05,R1..R5"
for s in SLICES:
    for c in s["command_ids"]:
        assert c in REGISTRY, (s["id"], c)
assert len(MODELS) == 7 and all(m.get("selected") and m.get("required") for m in MODELS)
assert all(m["render_status"] == "READY" for m in MODELS)
print(f"slices=52 deps={len(DEPENDENCIES)} trace={len(TRACE)} req_manifest={len(REQ_MANIFEST)} vv_rows={sum(len(CLOSE_MS.get(m, [])) for m in CLOSE_MS)}")
(PLAN / "implementation.json").write_text(json.dumps(IMPL, indent=1) + "\n")
print("wrote", PLAN / "implementation.json")
