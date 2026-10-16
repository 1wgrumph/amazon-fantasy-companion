#!/usr/bin/env python3
"""PI final-refresh SEIT payload rebind (data-binding glue, not V&V authorship).

Rebinds ONLY payload_ref/payload_sha256 and the payload_note data-binding note
in tracking_workflow and its MS-01 metadata copy to the parent-selected review
payload. Proof IDs/methods/negative strings, command definitions (70, incl.
PROC-TRACKING-SETUP tracking_payload_* pointers) and frozen profiles stay
byte-equivalent values. Run from the repo worktree root.
"""
import hashlib
import json
from pathlib import Path

PLAN = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
SEIT = PLAN / "seit.json"
OUT = PLAN / "evidence/pi-p2-final-refresh"

OLD_REF = "docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/te-p2-finalize/tracking-payloads.json"
OLD_SHA = "7b3935cfdae840fc6618aba64ba7726336e060a4733c59eca9da037d3903ab45"
NEW_REF = "docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence/github-work-items/github-work-items.json"
NEW_SHA = "95caddfe2b85067e2a22a3c1e7d46180193f3c67c59aa91b34d552d9116b8c4b"
OLD_NOTE = ("Historical proposed issue bodies/grouping remain unchanged. Any older helper-only filing or labels_note "
            "prose in that payload is superseded by this scope resolution; it is not authority to submit. PI refreshes "
            "filing metadata only, preserves exact reviewed body content and acceptance.")
NEW_NOTE = ("Parent P&D-selected review payload: evidence/github-work-items/github-work-items.json (sha256 "
            "95caddfe2b85067e2a22a3c1e7d46180193f3c67c59aa91b34d552d9116b8c4b) with 39 body_file mirrors; supersedes "
            "the TE method-example payload evidence/te-p2-finalize/tracking-payloads.json (sha256 "
            "7b3935cfdae840fc6618aba64ba7726336e060a4733c59eca9da037d3903ab45), retained as history, not a creation "
            "authority. Group mapping verified equal (payload-supersession.json); bodies/acceptance unchanged; nothing "
            "approved or submitted. Any older helper-only filing or labels_note prose in either payload is superseded "
            "by this scope resolution; it is not authority to submit. PI refreshes filing metadata only, preserves "
            "exact reviewed body content and acceptance.")

text = SEIT.read_text()
before_sha = hashlib.sha256(text.encode()).hexdigest()
assert before_sha == "8ce273d4550c9694523ef12cb7f7dcfd22d278555491fde69e0a812fe5c11b69", before_sha
before = json.loads(text)


def frozen_proof_view(doc):
    return [(p["id"], p["requirement_id"], p["method"], p["negative_or_failure_case"]) for p in doc["proof_cases"]]


def frozen_command_view(doc):
    return [json.dumps(c, sort_keys=True) for c in doc["procedures_and_commands"]]


proofs_before = frozen_proof_view(before)
commands_before = frozen_command_view(before)
profiles_before = json.dumps(before["frozen_profile_binding"], sort_keys=True)
assert len(proofs_before) == 100 and len(commands_before) == 70

# Exact replacements; the `"payload_*": "` prefix matches tracking_workflow and
# the MS-01 copy only (the command object uses `tracking_payload_*` keys).
edits = [
    (f'"payload_ref": "{OLD_REF}"', f'"payload_ref": "{NEW_REF}"'),
    (f'"payload_sha256": "{OLD_SHA}"', f'"payload_sha256": "{NEW_SHA}"'),
    (f'"payload_note": "{OLD_NOTE}"', f'"payload_note": "{NEW_NOTE}"'),
]
for old, new in edits:
    assert text.count(old) == 2, (old[:60], text.count(old))
    text = text.replace(old, new)

after = json.loads(text)
assert frozen_proof_view(after) == proofs_before, "proof IDs/methods/negative strings changed"
assert frozen_command_view(after) == commands_before, "command definitions changed"
assert json.dumps(after["frozen_profile_binding"], sort_keys=True) == profiles_before, "frozen profiles changed"
assert after["tracking_workflow"]["payload_ref"] == NEW_REF
assert after["tracking_workflow"]["payload_sha256"] == NEW_SHA
ms01 = next(p for p in after["proof_cases"] if p["id"] == "SEIT-AFC-P2-MS-01")
te = ms01["method_fields"]["tracking_evidence"]
assert te["payload_ref"] == NEW_REF and te["payload_sha256"] == NEW_SHA
assert after["tracking_workflow"]["filing_scope"]["payload_note"] == NEW_NOTE
assert te["filing_scope"]["payload_note"] == NEW_NOTE
# New payload binds source inputs only (no implementation/SEIT digest cycle).
payload = json.loads((PLAN / "evidence/github-work-items/github-work-items.json").read_text())
assert all("implementation.json" not in i["path"] and "seit.json" not in i["path"] for i in payload["source_inputs"])

SEIT.write_text(text)
after_sha = hashlib.sha256(text.encode()).hexdigest()

OUT.mkdir(parents=True, exist_ok=True)
paths = [
    "/tracking_workflow/payload_ref",
    "/tracking_workflow/payload_sha256",
    "/tracking_workflow/filing_scope/payload_note",
    "/proof_cases[SEIT-AFC-P2-MS-01]/method_fields/tracking_evidence/payload_ref",
    "/proof_cases[SEIT-AFC-P2-MS-01]/method_fields/tracking_evidence/payload_sha256",
    "/proof_cases[SEIT-AFC-P2-MS-01]/method_fields/tracking_evidence/filing_scope/payload_note",
]
(OUT / "seit-rebind-before.json").write_text(json.dumps(
    {"seit_sha256": before_sha, "changed_paths": paths,
     "payload_ref": OLD_REF, "payload_sha256": OLD_SHA, "payload_note": OLD_NOTE}, indent=1) + "\n")
(OUT / "seit-rebind-after.json").write_text(json.dumps(
    {"seit_sha256": after_sha, "changed_paths": paths,
     "payload_ref": NEW_REF, "payload_sha256": NEW_SHA, "payload_note": NEW_NOTE}, indent=1) + "\n")
(OUT / "seit-rebind-provenance.json").write_text(json.dumps(
    {"authority": "pi-p2-final-refresh-prompt.md ONE TRACKING PAYLOAD (parent P&D selection)",
     "old_payload_role": "historical method example, not a creation authority",
     "command_definitions": "70 byte-equivalent; PROC-TRACKING-SETUP tracking_payload_* pointers untouched",
     "proof_rows": "100 IDs/requirement_ids/methods/negative_or_failure_case strings unchanged",
     "frozen_profiles": "unchanged",
     "hash_cycle": "none: payload source_inputs bind TP/design/graph/register/authority only",
     "receipt": "specialists/te-p2-filing-binding-receipt.md stays historical for the prior binding"}, indent=1) + "\n")
print(f"REBIND: 6 fields; seit {before_sha[:12]} -> {after_sha[:12]}")
