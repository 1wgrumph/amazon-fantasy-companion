#!/usr/bin/env python3
"""IE chronology/profile projection (DEC-AFC-SD-040/041).

Rebuilds specialists/slice-graph.md and specialists/integration-plan.md from
baseline 51bc730 plus the Opus chronology proposal and the frozen Phase 1
journey opensource-hackathon snapshot. Deterministic and rerunnable; every
replacement asserts its expected count. Run from the repository root.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = "51bc730a880105c9b21d37a7a2dc5da79ada875f"
PLAN = Path("docs/plans/2026-10-12-amazon-fantasy-companion-phase-2")
GRAPH = PLAN / "specialists/slice-graph.md"
IEP = PLAN / "specialists/integration-plan.md"
PROPOSAL = json.loads((PLAN / "evidence/chronology-opus-review/proposal.json").read_text())
JOURNEY = json.loads(Path("docs/plans/2026-10-11-amazon-fantasy-companion/journey.json").read_text())
FS = JOURNEY["profile_selection"]["frozen_snapshots"]
OSH = FS["opensource-hackathon"]
FULL_SHA = "7d501eb8c103831a38c50d237b5d1e2e015a564b9ade8aef09a32dfc39b26ab1"
assert OSH["full_profile_sha256"] == FULL_SHA


def base(path):
    return subprocess.run(["git", "show", f"{BASE}:{path}"], check=True,
                          capture_output=True, text=True).stdout


def sub(text, old, new, count=1):
    n = text.count(old)
    assert n == count, (old[:80], n, count)
    return text.replace(old, new)


# slice -> GitHub milestone, from proposal issue groups
MS_OF = {}
for m in PROPOSAL["milestones"]:
    for i in m["issues"]:
        for s in i["slices"]:
            assert s not in MS_OF, s
            MS_OF[s] = m["id"]
assert len(MS_OF) == 52, len(MS_OF)
STEP_MS = PROPOSAL["integration_step_milestone"]
assert len(STEP_MS) == 44

# W-token rule for text where old Mn means a technical wave / release checkpoint.
WTOK = re.compile(r"(?<![-\w.])M([1-5])(?![\w.])")


def wave_words(text):
    text = re.sub(r"every other M([1-5]) slice", r"every other Wave \1 slice", text)
    text = re.sub(r"All M([1-5]) slices", r"All Wave \1 slices", text)
    text = re.sub(r"M([1-5]) entry", r"Wave \1 entry", text)
    return WTOK.sub(r"W\1", text)


def route(r):
    return f"{r['harness']} / {r['model']} / {r['reasoning']}"


def route_line(v):
    fb = ", ".join(route(f) for f in v.get("ordered_fallbacks", []))
    return f"{route(v['primary'])} (ordered fallbacks {fb})"


# ---------------------------------------------------------------- slice graph
g = base(GRAPH)
g = sub(g, """Roles: `Product Implementer`, `Test Implementer`, `Light Implementer`,
`Scribe`. Routes come from the lane's frozen profile snapshot
(journey `profile_selection.frozen_snapshots`): tv-app-ui = frontend,
backend = primary, device-integration-spikes = heavyweight,
spec-and-docs = tech-writing, defects = bug-triager; Light slices use the
lane profile's `light_implementer`; the Scribe uses `primary.scribe`.
""", f"""Roles: `Product Implementer`, `Test Implementer`, `Light Implementer`,
`Scribe`. Routes come from the frozen Phase 1 journey
`profile_selection.frozen_snapshots` (DEC-AFC-SD-041, Bearing Lite 1.1.7):
tv-app-ui, backend, device-integration-spikes, spec-and-docs and the Scribe
side lane = `opensource-hackathon` (full profile sha256
`{FULL_SHA}`); defects = `bug-triager`
(unchanged). Product Implementer uses the profile's `implementer`, Test
Implementer `test_implementer`, Light slices `light_implementer` and the
Scribe `scribe`, each with its ordered fallbacks, activated only on verified
unavailability or usage/rate-limit exhaustion. The whole snapshot binds every
dispatch: roles and fallbacks, Reviewer cadence `phase`, TDD development
strategy, concurrency, clean planning-to-implementation session,
`review.coverage_assist` (OCR, required) and
`deterministic_verification.reverify`. The 13 existing TDD pairs stay;
spikes stay evidence-only and documentation-only slices keep their declared
inspection method. Hold `muse-contributor-mode`: every Muse Code primary or
fallback dispatch launches with `--contributor-mode on`; if that cannot be
honored the dispatch returns a typed configuration gap. No route is looked up
outside the frozen snapshot.
""")
g = sub(g, "bearing-lite/1.1.6/skills/", "bearing-lite/1.1.7/skills/", 4)
g = sub(g, "Columns: ID | lane / role / work class | milestone, wave |",
        "Columns: ID | lane / role / work class | GitHub milestone, wave |")
g = sub(g, "| ID | Lane / role / class | M, wave |", "| ID | Lane / role / class | GitHub milestone, wave |")
g = sub(g, "\n## Slices\n\n", """
## Slices

The GitHub milestone (M01..M13, DEC-AFC-SD-040) is the issue's tracking group
from `evidence/chronology-opus-review/proposal.json`; TDD pair members share
their issue's milestone. The wave (W1..W5) is the technical wave: it keeps
wave membership, gate costs, leases and release prerequisites. Old milestone
names M1..M5 that meant a technical wave or release checkpoint are now W1..W5
or Wave 1..5.

""")

rows = []
WAVE_SLICES = {}


def fix_row(line):
    m = re.match(r"^\| (P2-[A-Z0-9]+) \| [^|]+ \| M([1-5]), W([1-5]) \|", line)
    if not m:
        assert not line.startswith("| P2-"), line[:60]
        return line
    sid, n, w = m.groups()
    assert n == w, sid
    rows.append(sid)
    WAVE_SLICES.setdefault(w, []).append(sid)
    return line.replace(f"| M{n}, W{w} |", f"| {MS_OF[sid]}, W{w} |", 1)


g = "\n".join(fix_row(line) for line in g.split("\n"))
assert len(rows) == 52, len(rows)

g = sub(g, "create/read back M1..M5 and one issue", "create/read back M01..M13 and one issue")
g = sub(g, "SP-5 in two pull requests. PR 1 (M1):",
        "SP-5 in two pull requests. PR 1 (W1 early checkpoint CP-X05-HIST; feeds P2-R1 in M03 and P2-B02 in M05):")
g = sub(g, "PR 2 (M2): capture the Thu",
        "PR 2 (closes the issue in GitHub milestone M04; final verdict by the W2 exit): capture the Thu")
g = sub(g, "PROC-VISUAL-REVIEW in M1 covers", "PROC-VISUAL-REVIEW in W1 covers")
for n in "1234":
    g = sub(g, f"| every other M{n} slice merged", f"| every other Wave {n} slice merged")
g = sub(g, "Redeploy aws-afc-dev at the M3 backend head", "Redeploy aws-afc-dev at the Wave 3 backend head")
g = sub(g, "bounded D02 delta before M4 exit.", "bounded D02 delta before W4 exit.")
g = sub(g, "Conditional (OD-AFC-03 = yes and M3 on time)", "Conditional (OD-AFC-03 = yes and W3 on time)")
g = sub(g, "| M3 exit; OD-AFC-03 = yes |", "| W3 exit; OD-AFC-03 = yes |")
g = sub(g, "| — | M4 exit | scribe |", "| — | W4 exit | scribe |")
g = sub(g, "Build the release APK at the M5 candidate commit", "Build the release APK at the W5 candidate commit")
g = sub(g, "its merge commit is the M5 candidate;", "its merge commit is the W5 candidate;")
g = sub(g, "PR 2 final live timing belongs to M2 and does not block R1",
        "PR 2 final live timing belongs to M04 and does not block R1")
g = sub(g, "Release slices P2-R1..R4 also wait for every other slice of their milestone (merged). P2-X11 waits for M3 exit and OD-AFC-03 = yes.",
        "Release slices P2-R1..R4 also wait for every other slice of their technical wave (Wave 1..4, merged); "
        "this release prerequisite derives from the wave column, never from the 13 GitHub milestone groups. "
        "P2-X05 meets its Wave 1 obligation to P2-R1 through the PR 1 checkpoint CP-X05-HIST (arrow above), "
        "not through closure of its M04 issue. P2-X11 waits for W3 exit and OD-AFC-03 = yes.")
g = sub(g, "the agent never reads the SSM secret.\n",
        "the agent never reads the SSM secret.\n\n"
        "Wave 2 entry is per lane and comes from the arrows, not from a blanket W1 exit: "
        "P2-X01 merged for P2-X04 and the stick chain; P2-B01 merged for the backend Wave 2 slices; "
        "P2-A01 merged for P2-A02T. P2-X04 does not wait for P2-R1 or the W1 exit. P2-A01's on-device "
        "review step waits for P2-X04 to release the stick, so X04 → A01 review → R1 is one visible chain "
        "in GitHub milestone M03 (schedule risk W-1 in the chronology proposal; no date moves).\n")
leftover = [m.group(0) for m in WTOK.finditer(g)]
assert not leftover, leftover
GRAPH.write_text(g)

# ---------------------------------------------------------- integration plan
t = base(IEP)

hold = OSH["holds"]
roles = OSH["snapshot"]["roles"]
ie_exec = roles["integration_engineer"]["sessions"]["execution"]
ate = roles["test_engineer"]["sessions"]["assurance"]
bt = FS["bug-triager"]["snapshot"]["roles"]
bt_ie = bt["integration_engineer"]["sessions"]["execution"]
bt_ate = bt["test_engineer"]["sessions"]["assurance"]
ie_plan = roles["integration_engineer"]["sessions"]["planning"]
assert route(ie_plan["primary"]) == "Claude Code / Claude Opus 5.5 / high"

t = sub(t, "BRAN is unavailable (no native policy); direct repository discovery was used.\n",
        f"""BRAN is unavailable (no native policy); direct repository discovery was used.

**Chronology and profile delta (DEC-AFC-SD-040/041, 2026-10-13).** Author:
Integration Engineer planning session on the frozen `opensource-hackathon`
route `integration_engineer.planning` ({route(ie_plan['primary'])}), Bearing
Lite 1.1.7 skills. Projection only, applied by
`evidence/chronology-profile-delta/ie-apply.py`. Step and slice `milestone`
values now name the 13 chronological GitHub milestones M01..M13 from
`evidence/chronology-opus-review/proposal.json` (`integration_step_milestone`
and issue groups); each step also carries its unchanged technical `wave`.
Technical waves and release checkpoints W1..W5 (formerly M1..M5) keep their
dates, membership, gate costs, cut-off IDs CO-M1..CO-M5 (stable identifiers
that name wave exits) and the identity names `apk.m<n>` / `release.m<n>`
(n = wave). No step ID, order, `after` list, merge set, lease, write set or
dependency condition changed. Historical `concurrency_findings` keep their
original Mn tokens, which mean wave exits Wn. Lane bindings are replaced by
the frozen `opensource-hackathon` snapshot; `bug-triager` is unchanged. This
is author planning work, not review or assurance.
""")
t = sub(t, "| Frozen profiles | journey `profile_selection.frozen_snapshots` (digests: primary `b81a141b…`, frontend `8e533b92…`, heavyweight `f2c555d5…`, tech-writing `8a6b5745…`, bug-triager `6ca3ffcc…`) |",
        f"| Frozen profiles | Phase 1 journey `profile_selection.frozen_snapshots` (DEC-AFC-SD-041): `opensource-hackathon` for all implementation lanes and the Scribe (full profile sha256 `{FULL_SHA}`, configuration digest `{OSH['configuration_digest_sha256']}`); `bug-triager` for defects (`{FS['bug-triager']['configuration_digest_sha256']}`, unchanged). The superseded primary/frontend/heavyweight/tech-writing lane snapshots are historical (`evidence/profile-migration-041/prior-profile-selection.json`). |")
t = sub(t, "retain the conditional issue, and create approved\nM1..M5 with exact table dates.",
        "retain the conditional issue, and create approved\nM01..M13 with exact table due dates (UTC times in descriptions).")
t = sub(t, "CMD-STUB-SCAN must be empty before the M3 rehearsal (IE-P2-29)",
        "CMD-STUB-SCAN must be empty before the Wave 3 rehearsal (IE-P2-29, M10)")
t = sub(t, "receive a bounded D02 delta before M4 exit,", "receive a bounded D02 delta before W4 exit,")
t = sub(t, "The five milestone dates are unchanged.",
        "The five wave release-checkpoint dates (W1..W5) are unchanged; the 13 GitHub\nmilestone due times reuse existing cut-offs only.")

# Steps summary, grouped by wave with GitHub milestones.
old_summary = t[t.index("The step list is in the JSON block. Summary:\n"):t.index("## Phase 1 IE findings carried into Phase 2")]
WAVE_STEPS = {1: range(1, 9), 2: range(9, 21), 3: range(21, 32), 4: range(32, 37), 5: range(37, 45)}
WAVE_DUE = {1: "2026-10-14T23:00Z", 2: "2026-10-17T01:00Z", 3: "2026-10-19T12:00Z",
            4: "2026-10-21T23:00Z", 5: "2026-10-23T12:00Z"}
WAVE_TEXT = {
    1: "Package baseline, gate areas,\n  device baseline, backend skeleton with frozen contracts, first fixtures, TV\n  scaffold, release v0.1.0 draft.",
    2: "Spike\n  verdicts, ingest, lineup, first deploy, profile UI, TNF amendments, Yahoo or\n  manual verdict, v0.2.0.",
    3: "Matcher,\n  policy, resolver, panel service, Wave 3 deploy, alerts, Watch and panel UI,\n  rehearsal, Sunday live run, v0.3.0.",
    4: "Sunday defects, MNF hardening,\n  D1 revision, Alexa stretch, v0.4.0.",
    5: "Submission docs, Scribe\n  assembly, visibility flip, final deploy, v1.0.0 candidate, final APK with\n  Reverify, demo capture on the final APK, Lifecycle-end assessments.",
}
ORDER = [s["id"] for s in json.loads(re.search(r"```json integration_plan\n(.*)\n```", t, re.S).group(1))["steps"]]
lines = ["The step list is in the JSON block. Steps are grouped by technical wave;",
         "`milestone` is the GitHub milestone (M01..M13) and `wave` the technical wave.",
         "Release prerequisites for P2-R1..R4 come from wave membership, never from the",
         "13 GitHub milestone groups. Summary:", ""]
for w, rng in WAVE_STEPS.items():
    ids = [f"IE-P2-{k}" for k in rng]
    seq = [i for i in ORDER if i in ids]
    mss = []
    for sid in seq:
        ms = STEP_MS[sid].split(" ")[0]
        if not mss or mss[-1][0] != ms:
            mss.append([ms, [sid]])
        else:
            mss[-1][1].append(sid)
    parts = "; ".join(f"{ms} {', '.join(x.replace('IE-P2-', '') for x in s)}" for ms, s in mss)
    lines.append(f"- **Wave {w} / W{w}** (release checkpoint due {WAVE_DUE[w]}): IE-P2-{rng[0]}..{rng[-1]}"
                 f" ({parts}). {WAVE_TEXT[w]}")
lines += ["",
          "CP-X05-HIST: IE-P2-6 (X05 PR 1) belongs to the M04 issue but executes during",
          "M02/M03 and feeds IE-P2-8 (R1, M03) and IE-P2-13 (B02, M05). CP-X03-REG:",
          "IE-P2-11 (X03 PR 1) feeds IE-P2-12 (X07) and IE-P2-23/27 (B06, A04). Wave 2",
          "entry is per lane: X01 merged for X04, B01 merged for backend Wave 2 slices,",
          "A01 merged for A02; X04 never waits for R1. X04 → A01 review → R1 sits in M03",
          "(schedule risk W-1; no date moved). IE-P2-35 still precedes IE-P2-34 in M11.",
          "", ""]
t = t.replace(old_summary, "\n".join(lines))

# JSON block regions
j0 = t.index("```json integration_plan\n")
cf0 = t.index('"concurrency_findings": [', j0)
wg0 = t.index('"wave_gate_costs": [', cf0)
j1 = t.index("\n```", wg0)
head, js_a, js_cf, js_wg, tail = t[:j0], t[j0:cf0], t[cf0:wg0], t[wg0:j1], t[j1:]

# step milestones and wave
for k in range(1, 45):
    sid = f"IE-P2-{k}"
    m = re.search(r'\{"id": "%s", "milestone": "M([1-5])", ' % sid, js_a)
    assert m, sid
    w = m.group(1)
    raw = STEP_MS[sid]
    ms = raw.split(" ")[0]
    note = raw[len(ms):].strip()[1:-1] if " " in raw else ""
    new = f'{{"id": "{sid}", "milestone": "{ms}", "wave": "Wave {w}", '
    if note:
        new += f'"milestone_note": {json.dumps(note, ensure_ascii=False)}, '
    js_a = js_a.replace(m.group(0), new, 1)

js_a = sub(js_a, "approved M1..M5 plus derived work issues", "approved M01..M13 plus derived work issues")
js_a = sub(js_a, '"apk.m1..m4, apk.final', '"apk.m1..m4 (m<n> = wave release checkpoint W<n>), apk.final')
js_a = sub(js_a, '"release.m1..m5 {tag', '"release.m1..m5 (m<n> = wave n) {tag')
js_a = sub(js_a, "39 logical issue groups for 52 slices, 5 milestones,",
           "39 logical issue groups for 52 slices, 13 GitHub milestones M01..M13 (5 wave release checkpoints W1..W5 unchanged),")
js_a = sub(js_a, "last M1 slice merge;", "last Wave 1 slice merge;")
js_a = sub(js_a, "preserve milestone dates and slice membership", "preserve release-checkpoint dates and wave membership")
js_a = sub(js_a, '"latest_safe": "per milestone exit"', '"latest_safe": "per wave release checkpoint W1..W5"')
js_a = sub(js_a, '"approved_outcome": "technical plan §Outcome and the M5 exit criteria"',
           '"approved_outcome": "technical plan §Outcome and the W5 exit criteria (GitHub milestone M13)"')

# lifecycle assessment sessions
m = re.search(r'"sessions": "Lifecycle cadence on candidate\.final[^"]*"', js_a)
assert m
sessions = (
    "Lifecycle cadence on candidate.final, fresh sessions rejecting author ancestry; routes from the frozen "
    "snapshots (DEC-AFC-SD-041). opensource-hackathon (tv-app-ui, backend, device-integration-spikes, "
    f"spec-and-docs and the Scribe side lane): Integration Engineer execution {route_line(ie_exec)}, cadence "
    f"{ie_exec['cadence']}; Assurance Test Engineer {route_line(ate)}, cadence {ate['cadence']}. Both sessions "
    "are enabled for every lane bound to this profile, so assurance covers spec-and-docs slices too; the former "
    "tech-writing assurance exemption no longer applies. bug-triager (defects, unchanged): Integration Engineer "
    f"execution {route_line(bt_ie)}, cadence {bt_ie['cadence']}; Assurance Test Engineer {route_line(bt_ate)}, "
    f"cadence {bt_ate['cadence']}. Every opensource-hackathon Muse Code primary or fallback launches with "
    "--contributor-mode on or returns a typed configuration gap. Fallbacks activate only on verified "
    "unavailability or usage/rate-limit exhaustion. A session whose route model authored a slice under "
    "assessment records that overlap; independence is by fresh session, per skill."
)
js_a = js_a.replace(m.group(0), '"sessions": ' + json.dumps(sessions, ensure_ascii=False), 1)

# frozen capability binding
fcb = js_a.index('"frozen_capability_binding": {')
obj_start = js_a.index("{", fcb)
old_obj, end = json.JSONDecoder().raw_decode(js_a, obj_start)
assert set(old_obj) == {"primary", "frontend", "heavyweight", "tech-writing", "bug-triager"}, old_obj.keys()
backend_resolution = old_obj["primary"]["backend_resolution"]
sn = OSH["snapshot"]


def role_routes(rs):
    out = {}
    for name, v in rs.items():
        if "sessions" in v:
            for s, sv in v["sessions"].items():
                out[f"{name}.{s}"] = route_entry(sv)
        else:
            out[name] = route_entry(v)
    return out


def route_entry(v):
    e = {"enabled": v["enabled"], "primary": route(v["primary"]),
         "ordered_fallbacks": [route(f) for f in v.get("ordered_fallbacks", [])]}
    if "cadence" in v:
        e["cadence"] = v["cadence"]
    return e


new_obj = {
    "decision": "DEC-AFC-SD-041 (Bearing Lite 1.1.7; supersedes the primary/frontend/heavyweight/tech-writing lane bindings)",
    "lane_profiles": {"tv-app-ui": "opensource-hackathon", "backend": "opensource-hackathon",
                      "device-integration-spikes": "opensource-hackathon", "spec-and-docs": "opensource-hackathon",
                      "scribe-side-lane": "opensource-hackathon", "defects": "bug-triager"},
    "opensource-hackathon": {
        "source_ref": "docs/plans/2026-10-11-amazon-fantasy-companion/journey.json#/profile_selection/frozen_snapshots/opensource-hackathon",
        "role_routes_ref": "docs/plans/2026-10-11-amazon-fantasy-companion/journey.json#/profile_selection/frozen_snapshots/opensource-hackathon/snapshot/roles",
        "full_profile_sha256": OSH["full_profile_sha256"],
        "configuration_digest_sha256": OSH["configuration_digest_sha256"],
        "role_routes": role_routes(sn["roles"]),
        "development_strategy": sn["development_strategy"],
        "tdd_scope": "13 existing TDD pairs unchanged; spikes evidence-only; documentation-only slices keep their declared inspection method",
        "concurrency": sn["concurrency"],
        "planning_to_implementation_clean_session": sn["planning_to_implementation_clean_session"],
        "review": sn["review"],
        "deterministic_verification": sn["deterministic_verification"],
        "holds": hold,
        "fallback_activation": "ordered; only on verified unavailability or usage/rate-limit exhaustion of the primary and all preceding approved fallbacks",
        "assurance": "test_engineer.assurance and integration_engineer.execution enabled (cadence lifecycle) for every lane bound to this profile; no tech-writing exemption",
        "backend_resolution": backend_resolution,
    },
    "bug-triager": old_obj["bug-triager"],
}
assert new_obj["opensource-hackathon"]["review"] == {"coverage_assist": {"enabled": True, "required": True}}
assert new_obj["opensource-hackathon"]["deterministic_verification"] == {"reverify": {"enabled": True}}
ind = " " * 4
dumped = json.dumps(new_obj, indent=2, ensure_ascii=False).replace("\n", "\n" + ind)
js_a = js_a[:obj_start] + dumped + js_a[end:]

js_a = wave_words(js_a)
js_wg = wave_words(re.sub(
    r'"milestone": "M([1-5])",',
    lambda m: '"release_checkpoint": "W%s",\n      "github_milestones": %s,' % (
        m.group(1), json.dumps(sorted({MS_OF[s] for s in WAVE_SLICES[m.group(1)]}))), js_wg))
for part in (head, js_a, js_wg):
    left = [m.group(0) for m in WTOK.finditer(part)]
    assert not left, left
t = head + js_a + js_cf + js_wg + tail
IEP.write_text(t)
print("applied")
