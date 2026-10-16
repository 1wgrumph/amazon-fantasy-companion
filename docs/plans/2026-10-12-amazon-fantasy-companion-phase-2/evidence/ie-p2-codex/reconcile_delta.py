"""Apply bounded IE planning correction 2; SEIT and source artifacts stay read-only."""
import difflib
import hashlib
import json
import re
from pathlib import Path

PLAN = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent
target = PLAN / "specialists/integration-plan.md"
before = (EVIDENCE / "integration-plan.before.md").read_text()
seit = json.loads((PLAN / "seit.json").read_text())
match = re.search(r"```json integration_plan\n(.*?)\n```", before, re.S)
old = json.loads(match[1])
data = json.loads(match[1])
steps = {s["id"]: s for s in data["steps"]}


def change(number, **fields):
    steps[f"IE-P2-{number}"].update(fields)


data["branches"][1]["merge"] = "after PR #10 (ST5-F1/F2) lands and origin/main is merged into the planning branch; preserve existing CHANGELOG and add linked planning entry"
data["branches"][3].update(role="historical PR #11 record; S42 tools/spec content already landed as d259c169 per current technical-plan Entry criteria", merge="not an additional prerequisite", consumed_as="tools/spec/VENDORED.md pin at p2.base")
data["branches"][5].update(role="two-PR spikes; recreate a visible worktree/branch from then-current main for PR 2 after PR 1 cleanup; keep one logical slice/issue identity")
data["worktrees"][0]["use"] = "existing planning continuation; IE writes only its three authorized output areas"
data["worktrees"][1]["use"] = "one per running slice or TDD pair; test/product sessions take turns in the shared pair worktree; remove worktree and local/remote branch after each merged PR"

change(1, entry_criteria=[
    "Owner approved the Phase 2 package at the integrated review (DEC-AFC-SD-023 P2-6)",
    "PR #10 with ST5-F1/F2 landed; S42 tools/spec content already landed as d259c169 per current technical-plan Entry criteria; PR #11 is not an additional prerequisite; origin/main merged into planning branch",
    "Sanitized tracked planning artifacts and evidence; raw agent logs remain local; CMD-GATE-HYGIENE exit 0",
    "Preserve existing CHANGELOG.md and add the planning PR's linked [Unreleased] entry; seed only if absent (AC-AFC-P2-REL-01)",
    "CMD-PR-CHECKS pass; merge by --merge or --rebase",
])
steps["IE-P2-2"]["entry_criteria"][0] = "P2-L01 after integrated approval AND p2.base landing: approved M1..M5 plus derived work issues; one issue per logical deliverable, TDD pair shares one, all 52 slices exactly once in 39 groups; conditional X11 stays labeled conditional; reuse matching identities; policy-tool dry-run then submit; saved labels/body/milestone/dependency/URL readback and slice-to-issue map; CMD-MILESTONES-CREATE and CMD-MILESTONES-READBACK match approved table (day precision; UTC due time in description)"
steps["IE-P2-2"]["post_step_vv"].append("Use technical-plan GitHub work organization/P2-L01 readback and SEIT existing proof rows; no issue/milestone created in this planning session")
steps["IE-P2-4"]["entry_criteria"][1] = "PROC-PREPARE and CMD-SUPPLY-SCAN before first use: actual compatible JDK17, Android command-line/platform/SDK/build-tools including apkanalyzer/apksigner, Gradle wrapper/plugins and pinned starter; qualify host build tools and record pins before A01T"
steps["IE-P2-4"]["post_step_vv"].append("Record X01 host-preparation completion separately from first_install_at and full verdict landing; A01T host red may start on this receipt without a new stick slot")
steps["IE-P2-5"]["entry_criteria"][0] = "B01T PROC-PREPARE with scanned/pinned Python test deps and empty API/interface harness; valid CMD-RED behavior-assertion receipt in shared B01T/B01 worktree with baseline/diff/bootstrap/test hashes, left uncommitted; B01 green on same tests; CMD-GATE-BACKEND, CMD-SAM-VALIDATE"
steps["IE-P2-5"]["entry_criteria"].append("B01T owns backend/tests/deployed/conftest.py and deployed/device_auth/, api/; shared conftest and dependency edits under backend-template; other T slices own distinct deployed module directories per current graph and TE-P2-F01")
steps["IE-P2-6"]["entry_criteria"][0] = "X05 PR 1: capture tool, endpoints and completed-game fixtures with historical/replay provenance per CONTRACT-AFC-P2-FIXTURE; interim PARTIAL verdict, live timing pending; October 12 is no longer a remaining live opportunity; first planned live capture is TNF October 15"
steps["IE-P2-7"]["entry_criteria"][0] = "A01T waits for X01 qualified host JDK17/SDK/build-tools receipt; PROC-PREPARE, buildable empty test/interface harness only, no tested feature behavior; valid CMD-RED behavior assertions in shared A01T/A01 worktree with frozen bootstrap/test hashes, left uncommitted; A01 CMD-GATE-TVAPP green on same tests"
steps["IE-P2-7"]["entry_criteria"].append("A01 configures release variant with host debug signing unless owner supplies OA-11; L05 only executes that already-configured build; no signing configuration authored by Light Implementer")
steps["IE-P2-14"]["entry_criteria"].insert(0, "B03T verified CMD-RED receipt in shared B03 pair worktree; B03 green on unchanged test IDs/hashes")
steps["IE-P2-18"]["entry_criteria"].append("A02T owns profile/ and detect/ under androidTest as well as host unit paths; all instrumented use holds fire-tv-stick cross-process lock; backend-template protects any authorized shared conftest change")
steps["IE-P2-22"]["entry_criteria"].insert(0, "B05T waits for verified B04T red receipt and frozen shared-fixture handoff, not a red-only merge; its own red receipt is verified in shared B05 pair worktree; B04 product merge remains a B05 landing prerequisite")
steps["IE-P2-24"]["entry_criteria"].insert(0, "B07T valid CMD-RED receipt in shared B07 pair worktree; B07 green on unchanged test IDs/hashes")
steps["IE-P2-28"]["entry_criteria"].insert(0, "A05T verified red receipt, including applicable instrumented run under fire-tv-stick cross-process lock; A05 green on same test IDs/hashes")

# Keep identities; put X11 terminal disposition before D02 in actual assembly order.
change(34, after=["IE-P2-1", "IE-P2-4", "IE-P2-9", "IE-P2-10", "IE-P2-12", "IE-P2-16", "IE-P2-17", "IE-P2-19", "IE-P2-35"], entry_criteria=[
    "All required final X01..X07 verdicts landed (X03 PR 2, X05 PR 2 included); selected X11 terminal disposition recorded and its verdict landed when run; if unselected, record OD-AFC-03/no-offer disposition without claiming enabled-voice proof",
    "PR #10 landed and merged tools/spec content/pin available (S42 d259c169); redundant PR #11 is not another prerequisite",
    "Freeze inventory binds every landed verdict through the specification freeze: paths, merge SHAs and digests; D02 includes all limits, selected modes/routes and aligned model names; any later landed verdict requires a bounded D02 delta in the same scope before M4 exit",
    "CMD-GATE-SPEC byte-identical rebuild; revision row with changed sections, PR and diff links",
    "Reviewer review; CMD-PR-CHECKS pass",
], exit="AC-AFC-P2-SPEC-01 evidence; all landed verdicts through freeze incorporated; same D02 slice owns any necessary later delta")
steps["IE-P2-35"]["rollback"] = "Unselected or timeboxed X11 records exact terminal/no-offer disposition under OD-AFC-03; only applicable no-offer criteria can close; enabled voice proof remains not_run/typed gap, never inferred PASS"
steps["IE-P2-35"]["exit"] = "X11 terminal disposition recorded; verdict landed when run; D02 may freeze only after this prerequisite"
steps["IE-P2-35"]["order"] = 34
steps["IE-P2-34"]["order"] = 35
data["steps"][33:35] = [steps["IE-P2-35"], steps["IE-P2-34"]]
steps["IE-P2-36"]["entry_criteria"][0] = "All M4 slices landed or explicit conditional terminal disposition recorded; D02 freeze inventory includes every landed required verdict and X11 when run; P2-R3 merged; no unresolved actionable review defect at any priority without explicit owner acceptance of residual risk; every active register case has its own passing evidence or owner-accepted typed gap; main-landing held"
steps["IE-P2-39"]["post_step_vv"][0] = "CMD-JUDGE-ACCESS against B01 frozen OpenAPI authentication/polling contract; no assumed successful anonymous GET /v1/link; protect returned link codes/tokens; verify anonymous repository only after OA-5"
steps["IE-P2-42"]["entry_criteria"][0] = "Build from candidate.final on main with -PafcApiBaseUrl=deploy.final ApiUrl; release signing already configured by A01 (host debug signer unless OA-11); actual tools and signer pinned; no new credential access"
steps["IE-P2-42"]["post_step_vv"][1] = "CMD-REVERIFY-APK on exact APK sha256, selected frozen backend unchanged: meaningful grounded minSdk/package/permission/service claims required; unproven semantics, absent mapping or unsupported capability = REVERIFY_CAPABILITY_GAP; ordinary ATE/apkanalyzer/ZIP-string checks never substitute; raw output private, sanitized receipt bound to raw digest"
steps["IE-P2-42"]["post_step_vv"].append("Main build identity and APK inspection may complete before tag; AC-AFC-P2-APK-01 tagged-main/publication subcriterion stays OWNER_EVIDENCE_PENDING until OA-8 authorization and tag readback names candidate.final; no early tag/release")
steps["IE-P2-42"]["exit"] = "Exact final APK identity/inspection and truthful Reverify disposition; tagged-main/publication remains OWNER_EVIDENCE_PENDING until OA-8 tag readback"
steps["IE-P2-43"]["entry_criteria"][-1] = "Manifest PR target 2026-10-23T06:00:00Z; a missed deadline records missing shots/claims, candidate hashes and remaining windows, then requires explicit owner scope decision identifying exact omissions/consequences; no automatic dropped shot"
steps["IE-P2-43"]["rollback"] = "Revert evidence PR if needed; retain final-APK capture obligation; earlier X09/X10 clips are historical evidence of those APKs only, never demonstration of apk.final; any material restriction requires exact owner scope decision"
steps["IE-P2-44"]["entry_criteria"].append("Assessments may start at IE-P2-42, but final closeout waits for IE-P2-43 manifest/tree comparison and all 100 SEIT row dispositions; tagged-main/publication subcriterion stays pending until OA-8 tag readback; author planning delta and TE planning PASS supply no independent review/assurance")
steps["IE-P2-44"]["exit"] = "M5 technical closeout only when final capture/evidence and required independent assessments complete; owner checklist handed over; pending tag/publication subcriteria remain explicitly pending until OA-8, never complete by planning PASS"

data["configuration_identity"]["proposed_commands"] = []
data["configuration_identity"]["command_registry_ref"] = "seit.json/procedures_and_commands (64 finalized IDs; unchanged in this delta)"
data["configuration_identity"]["frozen_capability_binding"] = {
    name: {
        "source_ref": f"seit.json/frozen_profile_binding/{name}",
        "role_routes_ref": f"seit.json/frozen_profile_binding/{name}/roles",
        "configuration_digest_sha256": snapshot["configuration_digest_sha256"],
        "review": snapshot["review"],
        "deterministic_verification": snapshot["deterministic_verification"],
        "backend_resolution": {
            "coverage_assist": "OpenCodeReview delegation; TE help/provenance inspected; execution not_run here; missing/unavailable is typed gap",
            "reverify": "reverify 0.11.0 selected; TE backend inventory inspected; exact-APK execution not_run; APK semantic grounding unproven, REVERIFY_CAPABILITY_GAP; no backend change or ATE substitute",
        },
    }
    for name, snapshot in seit["frozen_profile_binding"].items()
}
data["configuration_identity"]["records"].extend([
    "red.<pair> {shared worktree, baseline commit, dirty diff digest, test IDs/file hashes, bootstrap file hashes, scanned tool pins, preparation disposition}; consumed before green, never a red-only merge",
    "spec.freeze {required X01..X07 final verdict paths/merge SHAs/digests, X11 terminal disposition and verdict when run, every other landed verdict through freeze, later D02 delta if needed}",
    "work.organization {approved graph/payload digests, 39 logical issue groups for 52 slices, 5 milestones, duplicate search, policy dry-run/submit receipts, saved labels/body/milestone/dependency/URL readback}",
    "qualification.<suite> {candidate/input/suite hashes, five consecutive passes and one two-concurrent-copy pass, named cross-process locks, owned cleanup, actual duration}; ordinary reuse only for unchanged qualified candidate/inputs",
    "publication {OA-8 authorization, tag readback target on main}; separate from prepublication APK inspection"
])
data["configuration_identity"]["rule"] = "Never consume an unrecorded identity: predecessor merge receipt for product, explicit preparation/red handoff for premerge TDD, and terminal conditional disposition for X11. Stable step IDs retain identity; order/after/entry predicates place IE-P2-35 before IE-P2-34."
data["stubs"].insert(0, {"owner_slice": "P2-A01T and P2-B01T", "paths": "Only bootstrap/build/test/interface paths expressly authorized by current graph", "replaced_by": "Paired green Product Implementer realizes all tested behavior", "removal_check": "PROC-PREPARE before CMD-RED; freeze test/bootstrap hashes; missing tools/imports/collection/build is a preparation gap, never valid red"})
for c in data["cutoffs"]:
    if c["id"] in {"CO-STICK-START", "CO-X03-DESK"}:
        c["on_miss"] = "Preserve all required provider trials in order. Record exact untried providers/routes, evidence and schedule consequences; material omissions require explicit owner decision identifying omitted topics and consequences. Owner notice alone grants no reduction; untried is not appAbsent/accessUnknown evidence."
    if c["id"] == "CO-M1":
        c["on_miss"] = "M1 exit remains unmet until all required slices land; preserve milestone dates and slice membership; record forecast and request explicit scope decision for any material omission, never release completion from a partial set"
    if c["id"] == "CO-M2": c["time"] = "2026-10-17T01:00:00Z"
    if c["id"] == "CO-M3": c["time"] = "2026-10-19T12:00:00Z"
    if c["id"] in {"CO-CANDIDATE", "CO-DEMO"}:
        c["on_miss"] = "Final-APK demo requirement remains open. Earlier APK clips are labeled historical for their own candidate, not proof of apk.final. Record final APK status/hash, missed shots/window and consequences; exact owner scope decision required if final-candidate capture cannot be met."
data["owner_dependencies"][7]["blocks"] = ["publication", "AC-AFC-P2-APK-01 tagged-main subcriterion (OWNER_EVIDENCE_PENDING until tag readback)"]
for o in data["owner_dependencies"]:
    o["id"] = o["id"].replace(" (proposed, IE-P2-F15)", "").replace(" (proposed, optional, IE-P2-F16)", " (optional)")
data["final_candidate"]["invariants"].extend([
    "Final demo captures bind apk.final, not an earlier APK; any claim restriction requires exact owner scope decision",
    "APK inspection before tag does not close tagged-main subcriterion: OWNER_EVIDENCE_PENDING until OA-8 tag readback",
    "REVERIFY_CAPABILITY_GAP stays visible while APK semantics ungrounded; no frozen backend switch or ordinary-assurance substitution"
])
data["lifecycle_assessment_inputs"]["inputs"].extend([
    "All 100 existing SEIT proof-row dispositions including every negative case; fallback proof closes only its own criteria",
    "Qualification and wave resource/cost receipts; review/landing reuse bound to unchanged candidate/inputs",
    "D02 verdict freeze inventory; P2-L01 approved payload and exact slice-to-issue readback",
    "OA-8/tag readback or explicit OWNER_EVIDENCE_PENDING; REVERIFY_CAPABILITY_GAP where semantic proof ungrounded"
])

costs = [720, 900, 2100, 0, 120]
resource_map = []
for level, seconds in zip(seit["levels"], costs):
    cases = [c for c in seit["proof_cases"] if c.get("closing_slice") in level["slices"] or set(c.get("supporting_slices", [])) & set(level["slices"])]
    if level["wave"] == 5:
        cases = seit["proof_cases"]  # Existing IE-P2-44 consumes all rows.
    exact_groups = sorted({c["method_fields"]["resource_group"] for c in cases if "resource_group" in c["method_fields"]})
    groups = {"host-gate-fixtures"}
    if any("aws-afc-dev" in group for group in exact_groups): groups.add("aws-afc-dev")
    if any("P2-B" in s or s == "P2-G01" for s in level["slices"]): groups.add("host-pytest")
    if any("P2-A" in s or s.startswith("P2-R") for s in level["slices"]): groups.add("host-gradle")
    # Real demonstration/install leases also apply where method_fields has no engine-suite group.
    groups.update({"fire-tv-stick", "aws-afc-dev"} if level["wave"] > 1 else {"fire-tv-stick"})
    resource_map.append({"wave": level["wave"], "milestone": level["milestone"], "integration_steps": level["integration_steps"], "slices": level["slices"], "added_gate_seconds": seconds, "estimate_source": f"seit.json/levels/{level['wave'] - 1}/expected_gate_time_delta", "estimate_text": level["expected_gate_time_delta"], "resource_groups": sorted(groups), "seit_case_resource_groups": exact_groups, "resource_case_refs": [c["id"] for c in cases if "resource_group" in c["method_fields"]], "qualification_ref": "seit.json/procedures_and_commands/PROC-RELIABILITY", "limits": "Planning forecast only, not measured/hardware benchmark; additive work budget, not wall-clock promise. M4 fixed increment 0; changed-suite requalification extra and replay <=300s estimate. M5 120s docs estimate excludes unmeasured final binary/deployed/independent assurance. Qualification five consecutive + two concurrent copies is separate from ordinary qualified gate reuse."})
data["wave_gate_costs"] = resource_map
(EVIDENCE / "wave-resource-map.json").write_text(json.dumps(resource_map, indent=2) + "\n")

# Preserve compact source formatting, historical findings and all stable identities.
body = match[1]
for key, value in data.items():
    if key == "steps":
        for prev in old["steps"]:
            current = steps[prev["id"]]
            start = body.index('    {"id": ' + json.dumps(prev["id"]))
            end = body.index('"exit": ', start)
            end = body.index("}", end) + 1
            segment = body[start:end]
            for field in prev:
                if prev[field] != current[field]:
                    value_pattern = r'\[[^\n]*\]' if isinstance(prev[field], list) else r'\d+' if isinstance(prev[field], int) else r'"(?:\\.|[^"\\])*"'
                    pattern = r'("' + field + r'": )(' + value_pattern + ')'
                    segment, count = re.subn(pattern, lambda m: m[1] + json.dumps(current[field], ensure_ascii=False), segment, count=1)
                    assert count == 1, (prev["id"], field)
            body = body[:start] + segment + body[end:]
        begin = body.index('    {"id": "IE-P2-34"')
        middle = body.index('    {"id": "IE-P2-35"', begin)
        finish = body.index('    {"id": "IE-P2-36"', middle)
        body = body[:begin] + body[middle:finish] + body[begin:middle] + body[finish:]
    elif key not in old:
        body = body[:-2] + ',\n  "' + key + '": ' + json.dumps(value, ensure_ascii=False, indent=2).replace("\n", "\n  ") + "\n}"
    elif value != old[key]:
        begin = body.index('  "' + key + '": ')
        next_keys = list(old)[list(old).index(key) + 1:]
        finish = body.index('  "' + next_keys[0] + '": ', begin) if next_keys else len(body) - 2
        body = body[:begin] + '  "' + key + '": ' + json.dumps(value, ensure_ascii=False, indent=2).replace("\n", "\n  ") + ",\n" + body[finish:]

prose = before[:match.start()]
prose = prose.replace("planning profile `primary`: Claude Code / Claude Opus 5.5 / high), 2026-10-12.", "frozen primary planning first fallback: Codex CLI / GPT-6.1 Sol / xhigh).\nThis is continuation/correction **2** on 2026-10-13, after initial IE findings\nwere applied as correction 1; no planning, review or repair budget resets.\nConfirmed Claude weekly-limit evidence: `evidence/ie-p2-codex/route-evidence.json`.\nDEC-AFC-SD-039 makes the parent Codex session the Planning and Design lead.")
begin = prose.index("This plan covers assembly strategy only.")
end = prose.index("## Inputs and evidence read")
prose = prose[:begin] + """This plan covers assembly strategy only. It is author planning work, not
independent review or assurance. SEIT commands, proof methods and criteria remain
owned by TE; none was edited or rerun. Historical `concurrency_findings` and the
initial receipt remain correction-1 evidence, not a new dispatch hold list.
Current source bytes and lineage are in `evidence/ie-p2-codex/input-provenance.json`.
BRAN is unavailable (no native policy); direct repository discovery was used.

""" + prose[end:]
prose = prose.replace("## Inputs and evidence read", "## Inputs and evidence read (original inspection plus correction-2 source binding)")
prose = prose.replace("No `CHANGELOG.md` yet.", "Original inspection had no `CHANGELOG.md`; current lead sources record PR #14 created it. Preserve it at planning landing.")
prose = prose.replace("| Open Phase 1 PRs | #10 `afc/st4-spec` (head `771c289…`, which is also this plan branch's base; D1 spec, ST5-F1/F2 in progress) and #11 `afc/s42-revendor-prose` (re-vendors `tools/spec/**`) |", "| Current Phase 1 entry source | Technical-plan Entry criteria: land PR #10 with ST5-F1/F2; S42 content already landed as d259c169; PR #11 is redundant, not another prerequisite. No remote state was refreshed in this delta. |")
prose = prose.replace("JDK 21; Docker present;", "Original host inspection had JDK 21 and Docker;")
prose = prose.replace("(P2-X01, P2-B01 install them after a supply-chain scan)", "(X01 qualifies JDK17/Android/build-tools before A01T; B01T prepares scanned Python deps, B01 owns SAM/cfn-lint acquisition)")
prose = prose.replace("- **TDD pairs.** The `<id>T` red slice and its green slice share one worktree\n  and one PR (DES-AFC-P2-LANES). The step lists both IDs in `merges`.", """- **TDD pairs.** The `<id>T` red and green slices share one worktree and one
  PR (DES-AFC-P2-LANES). `merges` lists both for scope accounting; it does not
  mean a red-only PR. Green waits for verified CMD-RED behavioral assertions
  with frozen tests/bootstrap hashes in that worktree. Only empty build/test/
  interface scaffolding is allowed before red; tool/import/collection failures
  are preparation gaps. Product-to-product and landed spike dependencies remain
  merge dependencies. A01T waits for X01 host preparation. Cross-test shared
  fixture handoffs B04T→B05T and A03T→A04T consume verified red receipts, not merges.""")
prose = prose.replace("- **Two-PR spikes.** P2-X03 and P2-X05 each land in two PRs (IE-P2-F03,\n  IE-P2-F05), so each appears in two steps.", "- **Two-PR spikes.** X03/X05 retain one logical slice/issue each and two PR\n  landings; after PR 1 cleanup, PR 2 gets a new visible worktree from current main.")
prose = prose.replace(" *(proposed)*", "")
prose = prose.replace("- **Stubs (B01, A01 only).**", "- **Product stubs (B01, A01).** B01T/A01T may prepare only the bounded empty\n  interface/build/test harness described in DES-AFC-P2-LANES before valid red.\n  No tested feature behavior is allowed in that preparation.")
begin = prose.index("### Proposed command IDs")
end = prose.index("## Configuration identity", begin)
prose = prose[:begin] + """### Finalized command references (TE owns definitions)

All command IDs in the JSON resolve to `seit.json/procedures_and_commands`.
Use those exact definitions and pass/fail/gap rules; old IE proposals are superseded.
Build paths are `./tv-app/gradlew -p tv-app assembleDebug` and
`./tv-app/gradlew -p tv-app assembleRelease`, with `-PafcApiBaseUrl=<ApiUrl>`.
CMD-JUDGE-ACCESS checks B01 OpenAPI authentication/polling, not assumed anonymous
GET success. CMD-REVERIFY-APK keeps the frozen backend and exact APK hash;
unproven semantics remains REVERIFY_CAPABILITY_GAP with no ordinary ATE substitute.
Inspection of a main-built final APK may precede tag; tagged-main/publication
stays OWNER_EVIDENCE_PENDING until OA-8 and tag readback.

P2-L01 uses the technical-plan GitHub work organization procedure after
integrated approval **and** plan landing. Derive 39 issue groups from 52 slices
(13 TDD pairs share an issue), retain the conditional issue, and create approved
M1..M5 with exact table dates. Duplicate-search/reuse comes before policy-tool
dry-run and submission. Saved labels, body, milestone, dependencies and URLs
are read back; every slice maps exactly once. The configured filing entrypoint is
`python3 "$HOME/alphazede/Alphazedehq/hooks/issue-labels.py" file --repo
1wgrumph/amazon-fantasy-companion --kind <enhancement-or-documentation> --title
<approved-title> --body-file <approved-body>`; run without `--submit` first,
then with it only under recorded integrated approval. No remote action runs here.

""" + prose[end:]
begin = prose.index("## Concurrency proof")
end = prose.index("## Steps, cut-offs", begin)
prose = prose[:begin] + """## Concurrency and assembly readiness — correction 2 (author check)

Source: current graph plus design DES-AFC-P2-LANES/Planning completion controls;
SEIT `planning_findings_for_plan_integrator` F01/F02/F06/F07/F09 and `levels`.
The before artifact and unchanged historical findings preserve correction 1.
This is no independent concurrency review or hardware feasibility proof.

- B01T owns deployed `conftest.py`, `device_auth/` and `api/`; B02T..B07T
  own disjoint deployed `feed_ingest/`, `lineup/`, `matcher/`, `alert_policy/`,
  `provider_resolver/`, `panel/`. Shared conftest/dependency changes serialize
  under backend-template. A02T owns instrumented `profile/` and `detect/`;
  all instrumented T slices and green/review runs hold fire-tv-stick.
- A01T bootstrap manifest/Gradle paths use tv-app-manifest/tv-app-gradle;
  B01T bootstrap/shared conftest uses backend-template. Bootstrap ownership
  transfers inside the pair after frozen red evidence; no concurrent writers.
- First five ready implementation packets: X01, X05, B01T, D01, G01T.
  A01T queues until X01 qualifies host tools. Pair green starts only after its
  verified red receipt; G01 product lands before A01/B01 product landings.
- B04T's verified red/shared-fixture handoff precedes B05T; B04 product still
  precedes B05 product. Every other product dependency remains landed.
- Stick priority remains X01→X04 uninterrupted until verdict or first install
  +24h→A01 review→X02→X03 desk→X07; X03 live TNF then applicable instrumented
  qualification/reviews, rehearsal, X09/X10, selected X11, final APK and X12.
  X05 host-only TNF capture shares live-game-window with disjoint stick users.
- D02 waits for X01..X07 final verdicts plus selected X11 terminal disposition;
  it records every landed verdict through freeze. IE-P2-34 waits on IE-P2-35:
  Stable IDs remain; only their assembly order swaps. Later verdicts
  receive a bounded D02 delta before M4 exit, never an omitted topic.

The technical plan's schedule baseline is 2026-10-13T04:00:00Z (10d15h to
T_deadline). October 12 is removed from remaining live opportunities. Host-only
earlier captures stay historical/replay. Remaining windows: October 15 TNF,
October 18 Sunday, October 19 MNF, October 22 TNF; kickoff is rechecked at capture.
The five milestone dates are unchanged. CO-STICK-START remains a planning
forecast at 2026-10-14T03:15Z; qualification adds pressure and its real duration
is unmeasured. Missed forecasts never authorize provider omissions or earlier-APK
clips as final proof. Exact omitted topics/claims and consequences need an owner
scope decision with evidence; no new owner question is posed by this delta.

### Wave resources and incremental gate estimates

`wave_gate_costs` below carries SEIT `levels.expected_gate_time_delta`, exact
case resource declarations, normalized actual host/device/deployment groups,
and integer `added_gate_seconds`: W1 720, W2 900, W3 2100, W4 0, W5 120.
These are additive planning budgets, not hardware benchmarks or wall-clock
predictions. W4 has no fixed gate increase; changed-suite requalification and
estimated replay ≤300s are separate. W5's 120s docs forecast excludes unmeasured
final binary/deployed/independent assessment work. Suites with disjoint actual
resources may run concurrently; a system suite needing both stick and AWS
competes for both, in the SEIT lease order.

Apply existing PROC-PREPARE and PROC-RELIABILITY: a new/changed engine/server/
driver/browser suite needs **5 consecutive passes + one two-concurrent-copy
run**. Copies launch together with unique owned roots; the named cross-process
fire-tv-stick lock serializes the whole instrumented run on the one stick.
No extra device or simulator substitutes. Owned state/cleanup, bounded readiness,
fresh fault state, exact candidate/input hashes and slowest-test/cost evidence
come from SEIT. Ordinary qualified gate reuse for review/landing on unchanged
candidate/inputs is separate; no routine seven-execution rerun is added.
Changed suites/inputs invalidate reuse; evidence-only unchanged-tree merges
reuse qualified runtime evidence while retaining required source gates.

""" + prose[end:]
prose = prose.replace("proposed due 2026-10-17T01:00Z, IE-P2-F20", "due 2026-10-17T01:00Z").replace("proposed due 2026-10-19T12:00Z, IE-P2-F21", "due 2026-10-19T12:00Z")
text = prose + "```json integration_plan\n" + body + "\n```" + before[match.end():]
assert len(data["steps"]) == 44 and len({s for step in data["steps"] for s in step["merges"]}) == 52
assert json.loads(body) == data
target.write_text(text)
(EVIDENCE / "integration-plan.diff").write_text("".join(difflib.unified_diff(before.splitlines(True), text.splitlines(True), fromfile="integration-plan.before.md", tofile="specialists/integration-plan.md")))
def changed_paths(a, b, path=""):
    if a == b:
        return []
    if isinstance(a, dict) and isinstance(b, dict):
        return [p for key in sorted(a.keys() | b.keys()) for p in (changed_paths(a[key], b[key], path + "/" + key) if key in a and key in b else [path + "/" + key])]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and all(isinstance(x, dict) for x in a + b):
        return [p for n, (x, y) in enumerate(zip(a, b)) for p in changed_paths(x, y, path + "/" + str(n))]
    return [path]


changed_fields = changed_paths(old, data)
(EVIDENCE / "changed-fields.json").write_text(json.dumps({"correction": 2, "fields": changed_fields, "historical_findings_unchanged": old["concurrency_findings"] == data["concurrency_findings"]}, indent=2) + "\n")
print(f"RECONCILED: {len(changed_fields)} exact JSON fields; 44 stable steps; 52 slices; SEIT untouched")
