#!/usr/bin/env python3
"""Apply the approved-to-author chronology proposal to the existing unsent drafts."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

PLAN = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
PAYLOAD = PLAN / "evidence/github-work-items/github-work-items.json"
BASE = "51bc730a880105c9b21d37a7a2dc5da79ada875f"
old_bytes = subprocess.check_output(["git", "show", f"{BASE}:{PAYLOAD}"])
payload = json.loads(old_bytes)
proposal = json.loads((PLAN / "evidence/chronology-opus-review/proposal.json").read_text())
by_issue = {i["issue"]: (m, i) for m in proposal["milestones"] for i in m["issues"]}
assert len(by_issue) == 39 and set(by_issue) == {i["id"] for i in payload["issues"]}
assert all(2 <= len(m["issues"]) <= 6 for m in proposal["milestones"])
milestones = []
for m in proposal["milestones"]:
    sequence = "\n".join(f'{i["order"]}. {i["issue"]}: {i["starts_when"]}; {i["note"]}' for i in m["issues"])
    predecessors = "; ".join(f'{p["milestone"]}: {", ".join(p["conditions"])}' for p in m["predecessor_milestones"])
    description = (f'{m["id"]} — AFC Phase 2. Exact due time: {m["due_on"]}. Basis: {m["due_basis"]}.\n\n'
                   f'Entry: {m["start"]}\n\nExit: {m["finish_and_acceptance"]}\n\n'
                   f'Issues in order:\n{sequence}\n\n'
                   f'Predecessor milestones: {predecessors or "none"}.\n'
                   f'Owner prerequisites: {"; ".join(m["owner_prerequisites"]) or "none"}.\n'
                   f'Technical waves: {", ".join(m["waves"])}. Dependencies and lease conditions remain authoritative.\n')
    description = description.replace("M3 backend head", "Wave 3 backend head")
    milestones.append({"id": m["id"], "title": m["title"], "due_on": m["due_on"],
                       "description": description, "stable_id": m["id"], "saved_number": None, "saved_url": None})
payload["milestones"] = milestones
for issue in payload["issues"]:
    m, order = by_issue[issue["id"]]
    assert re.sub(r"^\[M\d+\]", "", issue["title"]) == re.sub(r"^\[M\d+\]", "", order["new_title"])
    issue["title"] = order["new_title"]
    issue["milestone"] = m["id"]
    body = re.sub(r"(?<![\w-])M([1-5])(?!\d)", r"W\1", issue["body"])
    body = re.sub(r"within milestone \*\*W[1-5]\*\*", f'within milestone **{m["id"]}**', body)
    body = body.replace("W1..W5", "M01..M13") if issue["id"] == "P2-L01" else body
    body = body.replace("all five milestones and 39 issue groups", "all 13 milestones and 39 issue groups")
    if issue["id"] == "P2-R1":
        body = body.replace("final live timing belongs to W2", "final live timing belongs to M04")
        for dependency in issue["dependency_groups"]:
            if dependency["issue_group"] == "P2-X05":
                dependency["condition"] = dependency["condition"].replace("belongs to M2", "belongs to M04")
    sequence = f'Sequence: step {order["order"]} of {len(m["issues"])} in {m["id"]}; starts when {order["starts_when"]}. {order["note"]}\n\n'
    body = body.replace("Write set:\n", sequence + "Write set:\n", 1)
    if issue["id"] == "P2-X05":
        body = body.replace("W1 historical fixtures may pass their checkpoint while this W2 issue remains open", "The early historical-fixture checkpoint CP-X05-HIST (consumed by R1 in M03 and B02 in M05) may pass while this M04 issue remains open")
    issue["body"] = body
    issue["body_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    (PLAN / issue["body_file"]).write_text(body)
payload["counts"]["milestones"] = 13
for source in payload["source_inputs"]:
    source["sha256"] = hashlib.sha256(Path(source["path"]).read_bytes()).hexdigest()
PAYLOAD.write_text(json.dumps(payload, indent=2) + "\n")
supersession = {"authority": "DEC-AFC-SD-040", "status": "proposed; nothing created",
               "previous_payload_sha256": hashlib.sha256(old_bytes).hexdigest(),
               "review_payload_sha256": hashlib.sha256(PAYLOAD.read_bytes()).hexdigest(),
               "preserved": "39 stable issues, 52 slices, 13 TDD pairs; dependency edges/requirements/proofs/labels unchanged; X05->R1 condition renames its final-close milestone M2 to M04",
               "issue_creation_count": 0, "milestone_creation_count": 0}
(PLAN / "evidence/github-work-items/payload-supersession.json").write_text(json.dumps(supersession, indent=2) + "\n")
before = json.loads(old_bytes)
for old, new in zip(before["issues"], payload["issues"]):
    if old["id"] == "P2-R1":
        for dependency in old["dependency_groups"]:
            if dependency["issue_group"] == "P2-X05":
                dependency["condition"] = dependency["condition"].replace("belongs to M2", "belongs to M04")
    assert {k: v for k, v in old.items() if k not in {"title", "milestone", "body", "body_sha256"}} == {k: v for k, v in new.items() if k not in {"title", "milestone", "body", "body_sha256"}}
print(json.dumps(supersession, indent=2))
