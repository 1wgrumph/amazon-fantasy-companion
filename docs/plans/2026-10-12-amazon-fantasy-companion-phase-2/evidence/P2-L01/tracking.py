#!/usr/bin/env python3
"""Execute the exact approved P2-L01 payload; no retries or product authority."""
import argparse
import fcntl
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = "1wgrumph/amazon-fantasy-companion"
PLAN = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
OUT = PLAN / "evidence/P2-L01"
PAYLOAD = PLAN / "evidence/github-work-items/github-work-items.json"
APPROVED_SHA = "f0b8d5bf26d3959948e65960fc2b06525a96f964ab3454633eb6c1aaeab9acdb"
APPROVED_HEAD = "a7a16570c376222635f48a6702cd0e3eca694493"
MERGE = "88db101edb61a08dedea8037e4e9207d262a7e0f"


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def gh(*args, data=None):
    result = subprocess.run(["gh", *args], input=None if data is None else json.dumps(data),
                            text=True, capture_output=True, timeout=60)
    require(result.returncode == 0, "GitHub command failed; inspect saved state before any retry: " + " ".join(args[:3]))
    return result.stdout


def api(path, data=None):
    args = ["api", f"repos/{REPO}/{path}"]
    if data is not None:
        args += ["--method", "POST", "--input", "-"]
    return json.loads(gh(*args, data=data))


def all_records(path):
    result, page = [], 1
    while True:
        batch = api(f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}")
        result.extend(batch)
        if len(batch) < 100:
            return result
        page += 1


def save(name, value):
    path = OUT / name
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def match_issue(item, inventory):
    marker = f'Stable ID: `{item["stable_id"]}`.'
    matches = [i for i in inventory if "pull_request" not in i and
               (marker in (i.get("body") or "") or f'] {item["id"]}:' in i["title"])]
    require(len(matches) <= 1, "Ambiguous existing issue: " + item["id"])
    return matches[0] if matches else None


def match_milestone(item, inventory):
    matches = [m for m in inventory if m["title"] == item["title"] or
               re.match(r"^" + re.escape(item["id"]) + r"(?:\s|$)", m["title"])]
    require(len(matches) <= 1, "Ambiguous existing milestone: " + item["id"])
    if matches:
        saved = matches[0]
        require(saved["title"] == item["title"] and saved["description"] == item["description"]
                and (saved.get("due_on") or "")[:10] == item["due_on"][:10],
                "Existing milestone differs from approval: " + item["id"])
        return saved
    return None


def linked_body(item, issues):
    body = item["body"]
    for dependency in item["dependency_groups"]:
        key = dependency["issue_group"]
        old = f'- `{key}` /'
        if old in body:
            body = body.replace(old, f'- [{key}]({issues[key]["html_url"]}) /')
    return body


def run(mode):
    require(hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() == APPROVED_SHA, "Unapproved payload bytes")
    payload = json.loads(PAYLOAD.read_text())
    approval = json.loads((OUT / "owner-approval.json").read_text())
    require(approval["status"] == "confirmed" and approval["id"] == "DEC-AFC-P2-APPROVAL-001"
            and approval["candidate_revision"] == APPROVED_HEAD and approval["payload_sha256"] == APPROVED_SHA,
            "Exact tracking approval absent")
    require(subprocess.run(["git", "merge-base", "--is-ancestor", MERGE, "HEAD"], capture_output=True).returncode == 0,
            "Checkout does not contain approved planning merge")
    pr = api("pulls/15")
    require(pr["merged"] and pr["merge_commit_sha"] == MERGE and pr["head"]["sha"] == APPROVED_HEAD,
            "Approved planning PR not landed")
    policy_path = Path.home() / "alphazede/Alphazedehq/hooks/issue-label-policy.json"
    policy = json.loads(policy_path.read_text())
    require(REPO.split('/')[0] not in policy["owners"] and REPO not in policy["repositories"],
            "Target now covered by helper policy; native creation prohibited")
    repo = json.loads(gh("api", f"repos/{REPO}"))
    require(repo["full_name"] == REPO and repo["private"] and not repo["archived"]
            and repo["has_issues"] and repo["permissions"].get("push"), "Repository boundary/permissions changed")
    labels = {x["name"] for x in all_records("labels")}
    slices = [s for i in payload["issues"] for s in i["slices"]]
    require(len(payload["milestones"]) == 13 and len(payload["issues"]) == 39
            and len(slices) == len(set(slices)) == 52, "Incomplete approved mapping")
    for item in payload["issues"]:
        require(item["kind"] in labels and item["labels_proposed"] == [item["kind"]], "Missing approved kind label")
        require(hashlib.sha256(item["body"].encode()).hexdigest() == item["body_sha256"]
                and (PLAN / item["body_file"]).read_text() == item["body"], "Body mirror differs from approval")
        require(all(f"## {heading}\n" in item["body"] for heading in
                    ["Origin", "Harness / version", "What", "Current evidence", "Expected", "Acceptance"]), "Missing body section")
    ordered_issues = sorted(payload["issues"], key=lambda i:
                            (i["milestone"], int(re.search(r"Sequence: step (\d+) of", i["body"]).group(1))))
    subprocess.run(["python3", "tools/ci/check_paths.py", "--files", str(PAYLOAD),
                    *[str(PLAN / i["body_file"]) for i in payload["issues"]]], check=True)
    milestone_inventory = all_records("milestones?state=all")
    issue_inventory = all_records("issues?state=all")
    milestones = {m["id"]: match_milestone(m, milestone_inventory) for m in payload["milestones"]}
    issues = {i["id"]: match_issue(i, issue_inventory) for i in payload["issues"]}
    for item in payload["issues"]:
        saved = issues[item["id"]]
        if saved is not None:
            bodies = [item["body"]]
            if all(issues[d["issue_group"]] for d in item["dependency_groups"]):
                bodies.append(linked_body(item, issues))
            require(saved["title"] == item["title"] and saved["body"] in bodies
                    and saved["state"] == "open" and milestones[item["milestone"]] is not None
                    and saved["milestone"] is not None
                    and saved["milestone"]["number"] == milestones[item["milestone"]]["number"]
                    and {x["name"] for x in saved["labels"]} == {item["kind"]},
                    "Existing issue differs from approved metadata: " + item["id"])
    save("preflight.json", {"outcome": "PASS", "payload_sha256": APPROVED_SHA, "merged_planning_pr": MERGE,
         "repo": REPO, "private": repo["private"], "helper_scope": "SCOPE_NOT_APPLICABLE",
         "policy_sha256": hashlib.sha256(policy_path.read_bytes()).hexdigest(),
         "existing_milestones": sum(m is not None for m in milestones.values()),
         "existing_work_issues": sum(i is not None for i in issues.values()), "mode": mode})
    if mode == "preflight":
        print("PREFLIGHT_PASS; no remote mutation")
        return
    if mode == "apply":
        for item in payload["milestones"]:
            if milestones[item["id"]] is None:
                # BUG-AFC-L01-DATE-001: the API due_on field is calendar-day
                # significant, so send midday UTC to preserve the approved date
                # in transport. Exact UTC deadline stays in description/payload.
                saved = api("milestones", {"title": item["title"], "description": item["description"],
                                           "due_on": item["due_on"][:10] + "T12:00:00Z"})
                milestones[item["id"]] = saved
                save("progress.json", {"milestones": {k: m["number"] for k, m in milestones.items() if m},
                                      "issues": {k: i["number"] for k, i in issues.items() if i}})
        for item in ordered_issues:
            if issues[item["id"]] is None:
                url = gh("issue", "create", "--repo", REPO, "--title", item["title"],
                         "--body-file", str(PLAN / item["body_file"]), "--label", item["kind"],
                         "--milestone", milestones[item["milestone"]]["title"]).strip()
                require(re.fullmatch(r'https://github.com/1wgrumph/amazon-fantasy-companion/issues/\d+', url),
                        "Uncertain create result; inspect saved state before retry")
                issues[item["id"]] = api("issues/" + url.rsplit('/', 1)[1])
                save("progress.json", {"milestones": {k: m["number"] for k, m in milestones.items()},
                                      "issues": {k: i["number"] for k, i in issues.items() if i}})
        for item in ordered_issues:
            saved = issues[item["id"]]
            expected = linked_body(item, issues)
            require(saved["title"] == item["title"] and saved["state"] == "open"
                    and saved["body"] in [item["body"], expected], "Existing issue body/title/state differs: " + item["id"])
            if saved["body"] != expected:
                gh("api", f'repos/{REPO}/issues/{saved["number"]}', "--method", "PATCH", "--input", "-", data={"body": expected})
    require(all(milestones.values()) and all(issues.values()), "Tracking set incomplete")
    milestone_inventory = all_records("milestones?state=all")
    issue_inventory = all_records("issues?state=all")
    readback, milestone_readback = [], []
    for item in payload["milestones"]:
        saved = match_milestone(item, milestone_inventory)
        require(saved is not None and saved["state"] == "open", "Milestone readback missing/closed")
        milestone_readback.append({k: saved[k] for k in ["number", "title", "description", "due_on", "html_url", "state"]})
    for item in payload["issues"]:
        saved = match_issue(item, issue_inventory)
        require(saved is not None and saved["title"] == item["title"] and saved["state"] == "open"
                and saved["body"] == linked_body(item, issues)
                and {x["name"] for x in saved["labels"]} == {item["kind"]}
                and saved["milestone"]["number"] == milestones[item["milestone"]]["number"],
                "Issue readback mismatch: " + item["id"])
        readback.append({"id": item["id"], "slices": item["slices"], "milestone": item["milestone"],
                         **{k: saved[k] for k in ["number", "html_url", "title", "body", "state"]},
                         "labels": [x["name"] for x in saved["labels"]]})
    result = {"outcome": "PASS", "method": "inspection", "payload_sha256": APPROVED_SHA,
              "milestones": milestone_readback, "issues": readback, "slice_to_issue":
              {s: {"number": i["number"], "url": i["html_url"]} for i in readback for s in i["slices"]},
              "counts": {"milestones": 13, "issues": 39, "slices": 52, "tdd_pairs": 13},
              "product_execution": "held", "all_work_issues_open": True}
    save("readback.json", result)
    print("TRACKING_READBACK_PASS: 13 milestones, 39 issues, 52 slices, 13 TDD pairs; all open")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["preflight", "apply", "verify"])
    args = parser.parse_args()
    with (OUT / "execution.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args.mode)
