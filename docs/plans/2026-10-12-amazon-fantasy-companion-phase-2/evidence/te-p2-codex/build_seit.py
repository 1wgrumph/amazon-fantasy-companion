"""Reproduce the prospective SEIT from the bounded Phase 2 inputs; no runtime actions."""
import hashlib
import json
import re
from pathlib import Path

P = Path('docs/plans/2026-10-12-amazon-fantasy-companion-phase-2')
E = P / 'evidence/te-p2-codex'
P1 = Path('docs/plans/2026-10-11-amazon-fantasy-companion')
J = Path.home() / 'alphazede/worktrees/amazon-fantasy-companion-planning' / P1 / 'journey.json'
journey = json.loads(J.read_text())
old = json.loads((P1 / 'seit.json').read_text())
plan = (P / 'amazon-fantasy-companion-phase-2-technical-plan.md').read_text()
graph = (P / 'specialists/slice-graph.md').read_text()
ie_text = (P / 'specialists/integration-plan.md').read_text()
ie = json.loads(re.search(r'```json integration_plan\n(.*?)\n```', ie_text, re.S)[1])
register = {}
for line in (P / 'requirements-register.md').read_text().splitlines():
    if line.startswith('| AFC-PR-'):
        c = [v.strip() for v in line.strip('|').split('|')]
        register[c[0]] = c
locals_ = {}
for line in plan.splitlines():
    if re.match(r'^\| (AC|RISK)-AFC-P2-', line):
        c = [v.strip() for v in line.strip('|').split('|')]
        locals_[c[0]] = c
slices = {}
for line in graph.splitlines():
    if re.match(r'^\| P2-[A-Z0-9]+ \|', line):
        c = [v.strip() for v in line.strip('|').split('|')]
        slices[c[0]] = c
assert len(slices) == 52
active = [u for u,c in register.items() if not c[1].startswith('WITHDRAWN')]
retired = [u for u in register if u not in active]
assert len(active) == 63 and len(locals_) == 37
inputs = ['amazon-fantasy-companion-phase-2-technical-plan.md','design.md','requirements-register.md',
          'models/allocation.md','models/views.md','models/view-structure.svg','models/view-interfaces.svg',
          'models/view-states.svg','models/view-data.svg']
baseline = [{'path':str(P/f),'sha256':hashlib.sha256((P/f).read_bytes()).hexdigest(),'binding_status':'bound'} for f in inputs]
data = {
 'schema_version':'1.0',
 'artifact':{'lifecycle':'AFC-2026-10-11','phase':'Phase 2','plan_dir':str(P)+'/',
             'status':'planning-prospective','finalized_by':'Planning Test Engineer: Codex CLI / GPT-6 Astra / xhigh',
             'receipt':str(P/'specialists/te-p2-codex-receipt.md'),
             'note':'Authoring and structural validation only; no implementation, product tests, independent review, runtime assurance, owner acceptance or publication. Delta reconciliation follows Plan Integrator changes. Resume follows the confirmed Claude weekly limit; no nested agents.'},
 'source_baseline':{'repository':'1wgrumph/amazon-fantasy-companion',
                    'revision':'771c28958f78e611048528aedbd9ed4490f308e1','branch':'plan/2026-10-12-afc-phase-2',
                    'planning_inputs':baseline,'planning_input_note':'Exact working-file bytes at write time, not a claim that these inputs are in the base commit. Markdown register authority is authority.json; the explicitly requested register hash here binds this planning input only.',
                    'read_only_context':[str(P/'specialists/slice-graph.md'),str(P/'specialists/integration-plan.md'),str(P/'specialists/re-p2-ac-receipt.md'),str(P/'specialists/re-p2-delta-receipt.md'),str(P/'specialists/sm-p2-delta-receipt.md'),'spec/amazon-fantasy-companion/07.1-verification-approach.md','spec/amazon-fantasy-companion/07.1.1..07.1.15-verification.md',str(P1/'seit.json')],
                    'bran_status':'unavailable: no native policy; ordinary repository discovery used'},
 'decision_baseline':{'kind':'decision-baseline-projection',
    'confirmed_decisions':{d['id']:d.get('status','not_recorded') for d in journey['decisions'] if d['id'].startswith('DEC-AFC-')},
    'status_note':'not_recorded preserves an absent status field. These are owner-attributed decision records, not newly inferred approval. The Orchestrator owns journey normalization; DEC-AFC-APPROVAL-ST5 retains its stated ST5-F1/F2 conditions.',
    'open_items':[{'id':i,'status':'open_for_integrated_review'} for i in ['OD-AFC-02','OD-AFC-03','OD-AFC-04','OD-AFC-05','OA-AFC-A1']+[f'OD-AFC-P2-{i:02}' for i in range(1,6)]]+ [{'id':f'OA-{i}','status':'owner_action_pending'} for i in range(1,12)],
    'source':'<CONTROL_PLAN_WORKTREE>/'+str(P1/'journey.json')},
 'responsibility_and_change_authority':{
    'planning_test_engineer':'Owns method, executable evidence design, commands, proof and gate declarations only. Writes seit.json, specialists/te-p2-codex-receipt.md and own evidence; no other artifact.',
    'requirements':'Register VCASE allocations by reference; Lifecycle-local rows gated by specialists/re-p2-ac-receipt.md, with accepted repairs in current plan. RE is not rerun.',
    'design_and_assembly':'P&D owns design/slices; IE owns integration-plan.md and progressive assembly. This SEIT projects IE steps and supplies V&V, without rerunning or editing IE.',
    'test_implementation':'Test Implementer uses write-tests for method=test only; product implementation remains in the named paired slice.',
    'assurance':'Fresh Assurance Test Engineer sessions at lifecycle cadence on the M5 stable candidate for primary/frontend/heavyweight/bug-triager. Reject author ancestry; independently rerun applicable gate-chain claims. Author receipts remain diagnostic. Tech-writing assurance disabled.',
    'review':'Frozen lane Reviewer, OCR delegation required; phase cadence awaits OD-AFC-P2-01 per-PR integration-step application. One configured review and at most one repair, then deterministic closure. Planning and implementation budgets are separate.',
    'owner':'Open-item approval at integrated review; OA-1..11 and protected actions stay owner-only. No tool installation, hardware, AWS, branch, commit or remote action by this session.',
    'orchestrator':'Consumes this return; records bounded prerequisite/write-set corrections; freezes the complete profile including capabilities; alone dispatches Plan Integrator. Any changed intent needs an explicit owner amendment.'},
 'applicable_documents_and_precedence':{
    'precedence':['session owner authority','parent journey owner decisions with conditions','approved spec and Markdown register verification allocations','current Phase 2 technical plan Lifecycle-local rows','design.md and aligned models','IE integration plan and slice graph','this prospective SEIT'],
    'register_rule':'artifact-grammar.md Requirements register rule 4: reference allocated method, environment, Positive and Negative in each VCASE; do not duplicate their normative text.',
    'standards':[{'id':'SRC-EMV-NASA-SEH','document':'NASA/SP-2016-6105 Rev 2','clause':'Appendix I, Verification and Validation Plan Outline','url':'https://www.nasa.gov/reference/appendix-i-verification-and-validation-plan-outline/','use':'Outline structure only, adapted by test-engineering vnv-plan.md; no standards conformance claim. Official outline checked during preparation.'}],
    's8_gap':'S8-LEDGER-MISSING: referenced engineering-methods ledger absent. Q10 restore excluded; no invented receipt. Primary NASA outline inspected for the named appendix only.',
    'host_binding':'Not a specification Lifecycle. No Requirements System review or publication is requested; Markdown register and source_baseline identify this planning candidate.'},
 'system_description_and_requirements_flowdown':{
    'system':'Kotlin Fire TV companion, Python AWS serverless backend, supported provider launch/notification interfaces, ESPN feed/replay and Yahoo/manual lineup; no companion player.',
    'flowdown':'63 active VCASE allocations + 24 Lifecycle-local acceptance rows + 13 risks, one canonical proof row each. Supporting slices share the same row; traceability remains one ID per cell.',
    'models':['models/allocation.md','models/views.md','models/view-structure.svg','models/view-interfaces.svg','models/view-states.svg','models/view-data.svg'],
    'retired_requirements':[{'requirement_id':u,'verification_case':'VCASE-'+u,'status':'retired','reason':'DEC-AFC-SD-035; no proof case or realization'} for u in retired],
    'exclusions':['hardware benchmarking and measured hardware latency/RAM claims','messaging/social features','Mode A footage and companion player','LLM/API-key commentary service','unapproved Alexa expansion','owner-only publication/credentials/submission','S8 ledger restoration']},
 'vv_methods':{'methods':{'test':'Measured functional response; Test Implementer authors tests through write-tests, with paired red/green evidence.','inspection':'Read source, artifacts and recorded metadata against criteria; no product tests authored by TE.','demonstration':'Observe real stick operation using remote input and named replay/live basis.','analysis':'Compare revisions, digests, coverage and declared bounds; no hardware performance model.','evaluation':'Owner couch-legibility acceptance is recorded alongside the mandated demonstration; agents cannot substitute their judgment.'},
    'reverify':'Binary attribute claims require CMD-REVERIFY-APK. Source-only or observed behavior cases carry an explicit reasoned not-applicable line; adding an APK attribute claim extends applicability.',
    'coverage_assist':'OpenCodeReview delegate backend, installed and help checked; CMD-OCR-DELEGATE required for every Reviewer packet; not the independent Reviewer.',
    'interface_rule':'Each APPLICABLE contract obligation has both positive and negative coverage; missing runnable setup is a typed gap, never a mocked acceptance article.'},
 'levels':[], 'environments_fixtures_data_simulations_support':{},'procedures_and_commands':[],
 'required_commands':[], 'cross_cutting_checks':[],
 'traceability_matrix_columns':old['traceability_matrix_columns'],'traceability_matrix':[],'proof_cases':[],
 'gate_declarations':{},'evidence_and_pass_fail':{},'anomaly_corrective_closure':{},
 'integration_vv_sequence':[],'planning_findings_for_plan_integrator':{}
}
commands = {}
def cmd(id, command, pass_rule, description, steps=None):
    commands[id] = {'id':id,'command':command,'pass':pass_rule,'description':description,'used_by':[]}
    if steps: commands[id]['procedure_steps'] = steps

gap = 'Missing tool, missing article, unsupported capability, zero collected cases, skipped required case or not_run is a typed gap, never PASS. Record safe error, phase and exit status.'
for area in ['ALL','SPEC','DOCS','HYGIENE','TVAPP','BACKEND']:
    suffix='' if area=='ALL' else ' '+area.lower()
    cmd('CMD-GATE-'+area, 'bash tools/ci/gate.sh'+suffix,
        'Exit 0 with PASS for every selected area, with no GAP. Product-area no-tree PASS is admissible only before that tree is due; it never closes a product requirement. '+gap,
        'Repository gate; tvapp/backend extensions supplied by P2-G01; other areas from merged Phase 1 S09.')
cmd('CMD-MAIN-GATE','git status --porcelain && git rev-parse HEAD && bash tools/ci/gate.sh',
    'Clean exact recorded merge/candidate checkout; all five areas pass once realized; no GAP or unexpected no-tree result. '+gap,'Post-step gate on integrated candidate; clean checkout must be checked before execution.')
cmd('CMD-RED','case <suite> in gate) python3 -m unittest discover -s tools/ci/tests -v ;; backend) python3.12 -m pytest <test_paths> -v ;; tvapp) ./tv-app/gradlew -p tv-app testDebugUnitTest --tests <test_selector> ;; instrumented) ./tv-app/gradlew -p tv-app connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=<test_class> ;; *) exit 2 ;; esac; afc_rc=$?; printf "exit=%s\\n" "$afc_rc"; sha256sum <test_files>; git rev-parse HEAD; git status --porcelain; exit "$afc_rc"',
    'Expected non-zero due to named behavior assertions for the same test IDs later green; collection, import, build, syntax, tool and authorization errors are not red evidence. Capture test-file hashes, baseline HEAD and dirty diff digest. Product run must retain those IDs and hashes or return to the red boundary.',
    'Preserves Phase 1 red receipt contract, expands suites to Phase 2. Red tests remain uncommitted in pair worktree; no red-slice merge dependency.')
for id in ['CMD-OCR-DELEGATE','CMD-DX-PRESENCE','CMD-WORKFLOW-CHECK']:
    c=dict(next(c for c in old['procedures_and_commands'] if c['id']==id))
    c.pop('repository',None);c.pop('tool_availability_2026_10_11',None);c['used_by']=[]
    c['description']=c['description'].replace('Phase 1','Phase 2').replace('AC-AFC-DX-01','AC-AFC-P2-DX-01')
    commands[id]=c
cmd('CMD-SUPPLY-SCAN','cat "$HOME/.claude/skills/scan-software-supply-chain/SKILL.md"',
    'Installed supply-chain workflow returns ALLOW/PASS receipt for exact acquired digest before first execution; BLOCK or INDETERMINATE refuses use. Reading the skill alone is not PASS.',
    'Run the installed workflow against each acquisition; no invented scanner CLI.',
    ['Resolve installed skill and execute its acquisition scan procedure without executing the acquired artifact.','Bind source, pinned version/commit, sha256, receipt and first-use slice; scan SDK, JDK, starter, Gradle/plugins, SAM, cfn-lint, test dependencies and Actions.','Use only after admissible scan result; missing scanner is a typed gap.'])
cmd('CMD-ADB-BASELINE','adb -s <stick_serial> get-state && adb -s <stick_serial> shell getprop ro.product.model && adb -s <stick_serial> shell getprop ro.build.version.release && adb -s <stick_serial> shell getprop ro.build.version.sdk',
    'Selected stick matches OA-1; model, Fire OS and API recorded; incompatible device triggers RISK-01, not platform substitution. '+gap,'P2-X01 targeted identity reads only; sanitize device serial before tracked evidence.')
cmd('CMD-ADB-INSTALL','adb -s <stick_serial> install -r <host_built_apk>',
    'Install succeeds on leased target; same-host signer checked first. Record APK hash/commit and first_install_at for SP-1; operation demonstration still required.',
    'No CI-built APK on the stick; signature mismatch stops for rollback/relink procedure.')
cmd('CMD-ADB-SCREENCAP','adb -s <stick_serial> exec-out screencap -p > evidence/visual/<slice>/<state>.png',
    'Valid PNG at device output resolution shows named state with sanitized fixture data; black/blank video is a RISK-09 evidence gap, not video proof.',
    'Capture every changed UI state; create its evidence directory before this command.')
cmd('CMD-ADB-GEOMETRY','adb -s <stick_serial> shell dumpsys window > <private_capture_dir>/window.txt && adb -s <stick_serial> shell wm size > <private_capture_dir>/display.txt',
    'Sanitized geometry copied to evidence/visual/<slice>/<state>-geometry.txt; identifies panel/video rectangles and display size; no overlap/crop and preserved video aspect established when claimed.',
    'Raw dumps stay private pending account-data scrub; geometry alone cannot prove provider content or game arrival.')
cmd('CMD-TVAPP-INSTRUMENTED','./tv-app/gradlew -p tv-app connectedDebugAndroidTest -PafcApiBaseUrl=<ApiUrl> -Pandroid.testInstrumentationRunnerArguments.class=<test_class>',
    'Required classes run on recorded real stick, no skips; assertions and PROC-RELIABILITY receipts pass. '+gap,
    'P2-A03T/A04T/A05T own instrumented tests; accepts replay logic only with labels, never substitutes emulator for stick.')
for kind in ['DEBUG','RELEASE']:
    cmd('CMD-APK-BUILD-'+kind,'./tv-app/gradlew -p tv-app assemble'+kind.title()+' -PafcApiBaseUrl=<ApiUrl>',
        'Exit 0, expected APK exists at tv-app/app/build/outputs/apk/<variant>/<apk_name>.apk; build commit, tools, API URL, signer and digest recorded. Release signing must be configured by P2-A01 for host debug signer unless OA-11; unsigned APK fails.',
        'Exact wrapper path corrected from root ./gradlew; no unbound download or credential command.')
cmd('CMD-APK-SHA256','sha256sum <apk>', 'Digest equals installed/submitted exact artifact in receipt; candidate commit and file size recorded.','Artifact identity, not semantic binary proof.')
cmd('CMD-APK-CERT','apksigner verify --print-certs <apk>','Exit 0 and signer certificate SHA-256 recorded; equal to previous installed APK signer unless authorized keystore/relink transition. '+gap,'Build-tools prerequisite installed by P2-X01 after scan.')
cmd('CMD-REVERIFY-APK','reverify auto <apk> --json > <private_capture_dir>/reverify-auto.json && reverify verify <apk> --claims-file <apk_claims_json> --json > <private_capture_dir>/reverify-claims.json',
    'Exact APK hash bound; every claimed minSdk/package/permission/service or secret-containment attribute has a meaningful grounded VERIFIED claim with byte/semantic linkage. INCONCLUSIVE, OBSERVED, INVALIDATED, absent mapping or unsupported APK semantics = typed gap; REFUTED claim = FAIL. ZIP magic or string presence alone never proves manifest semantics or absence of secrets.',
    'Installed reverify 0.11.0 help confirms auto/verify syntax. APK semantic claim adapter not advertised; capability remains unproven, never substitute ATE or apkanalyzer output as a Reverify PASS.',
    ['Derive expected attributes from committed source/design, not from the tool output being checked.','Use apkanalyzer manifest print <apk> and apkanalyzer manifest min-sdk <apk> as supplemental inspection only; record digest and any exact APK member mapping for byte claims.','Construct <apk_claims_json> using supported claim kinds and validated mapping into the exact artifact; do not invent an apk_manifest kind. If no mapping can be grounded, retain REVERIFY_CAPABILITY_GAP with exact evidence.','Check every result, not process exit or overall grounded flag alone; never print credentials or raw strings for the secret-containment case. Keep raw output private; copy only sanitized report with claim IDs/verdicts, source linkage and raw-file digest to <evidence_dir>/reverify-claims.json; retain byte evidence privately for authorized inspection.'])
cmd('CMD-ADB-ROLLBACK','adb -s <stick_serial> install -r -d <last_green_apk>',
    'Last-green identity and signer verified, app launches and still links; otherwise typed gap. No automatic uninstall/data deletion.',
    'If signer prevents restore, explicit data-clearing authorization and OA-10 relink precede uninstall/reinstall; preserve original failure and later recovery separately.')
cmd('CMD-SAM-VALIDATE','sam validate --template-file backend/template.yaml --lint && cfn-lint backend/template.yaml','Both exit 0; Free-plan article inspection still required. '+gap,'SAM and cfn-lint installed by P2-B01 after scan.')
cmd('CMD-SAM-BUILD','(cd backend && sam build)', 'Exit 0, build artifact bound to backend tree, template digest and Python 3.12 toolchain. '+gap,'Run in the SAM project so template.yaml, samconfig.toml and .aws-sam/build have unambiguous paths. Preflight and aws-afc-dev lease for deployment sequence; no deployment during a live game.')
cmd('CMD-SAM-DEPLOY','(cd backend && sam deploy --config-env default --profile afc-dev --tags GitCommit=<deploy_sha>)',
    'Approved dev stack only; successful stack update and smoke. Any paid service/plan prompt refuses execution and records class F; no credential access or production DB mutation.',
    'P2-L02/P2-L03 and IE-P2-40 use same profile and identity; no services restarted by this planning session.')
cmd('CMD-STACK-OUTPUTS',"aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].[OutputKey,OutputValue]' --output json",
    'Only ApiUrl output captured, equals API URL compiled into the tested APK; no credential/config dump. '+gap,'Allowlisted stack output; sanitized receipt.')
cmd('CMD-DEPLOYED-COMMIT',"aws cloudformation describe-stacks --stack-name afc-dev --profile afc-dev --query 'Stacks[0].Tags[?Key==`GitCommit`].Value' --output text && git rev-parse <deploy_sha>:backend <candidate_sha>:backend",
    'Tag equals recorded deploy SHA and both backend tree IDs equal; receipt includes built template digest and smoke. '+gap,'Tag alone cannot prove deployment content; require build receipt.')
cmd('CMD-DEPLOYED-SMOKE','python3.12 -m pytest backend/tests/deployed -k link -v --junitxml=<evidence_dir>/deployed-smoke.xml',
    'Collected mapped link cases pass on afc-dev: issue/expiry/replay, unauthenticated rejection, owner phone confirmation and subsequent authorized profile; no token in output. Absent tests or unperformed owner confirmation = typed gap.',
    'Prospective deployed suite currently absent; Test Implementer allocation correction TE-P2-F01. Account profile and ApiUrl supplied by documented non-printing fixture setup, not invented CLI flags.')
cmd('CMD-DEPLOYED-TESTS','python3.12 -m pytest backend/tests/deployed -v --junitxml=<evidence_dir>/deployed.xml',
    'All mapped VCASE IDs collected with both criteria passing against afc-dev, fixture and backend tree digests bound; no stub/fake acceptance article, no silent skips. '+gap,
    'Deployed suite needs TE-P2-F01 write-set allocation. System cases also require the real TV endpoint via PROC-SYSTEM-VCASE.')
cmd('CMD-API-CLIENT-MATCH','./tv-app/gradlew -p tv-app testDebugUnitTest --tests <api_contract_test_class>',
    'A01T test enumerates every OpenAPI operationId/path and DTO/envelope/status rule; each has exactly one client mapping, no invented endpoint; 400/401/403/409/410/429/503 and body/revision boundaries exercised. '+gap,
    'Runtime selector must resolve to actual A01T class recorded in receipt; missing test is a gap.')
cmd('CMD-STUB-SCAN','git grep -n -e AFC-STUB -e NotImplementedError -- backend/src tv-app/app/src/main; afc_rc=$?; test "$afc_rc" -eq 1',
    'No matches at M3 rehearsal or final candidate; grep error is not empty success. Earlier scaffold stages record deferred markers and replacement owners.','Stub retirement check, corrected exit handling.')
cmd('CMD-CONTRACT-DIGEST','git ls-files -z -- backend/src/api/openapi.yaml backend/template.yaml backend/samconfig.toml backend/src/store backend/src/pipeline backend/src/lineup/presets.py backend/src/provider_resolver/registry.json "backend/fixtures/replay/*/index.json" | xargs -0 -r sha256sum',
    'Every contract due at this step exists; digest set nonempty and complete. B01 freezes scaffolds; presets are rebound at B03 and registry/fixtures at their respective spike merges.','Freeze an inventory, not an empty glob; used at IE-P2-5/6/11/14/16/17.')
cmd('CMD-CONTRACT-FROZEN','git diff --exit-code <contract_merge_sha>..HEAD -- <frozen_paths>',
    'No difference except exact paths named in PR with the applicable lease, reviewed successor identity and consumer checks. Expected B03/X03/X05 realizations rebind their contract digests; implicit exceptions fail.','Contract changes checked against recorded merge and declared exception list.')
cmd('CMD-TREE-EQUAL',"afc_a=$(git rev-parse <a>:tv-app) && afc_b=$(git rev-parse <b>:tv-app) && test \"$afc_a\" = \"$afc_b\" && afc_a=$(git rev-parse <a>:backend) && afc_b=$(git rev-parse <b>:backend) && test \"$afc_a\" = \"$afc_b\"",
    'Both tree IDs equal and each rev-parse succeeds; bind final docs-only merges to assessed product trees.','No changed binary-relevant input may reuse prior qualification.')
cmd('CMD-PR-CHECKS','gh pr checks <pr_number> --repo 1wgrumph/amazon-fantasy-companion --json name,state,workflow && gh pr view <pr_number> --repo 1wgrumph/amazon-fantasy-companion --json headRefOid,baseRefName,mergeable,statusCheckRollup',
    'Head equals reviewed and gated SHA; base main; MERGEABLE; every expected path-selected gate plus hygiene present and SUCCESS, none pending/missing. Required-only output is insufficient while private rulesets absent.','Pre-merge readback under main-landing; no remote action in planning.')
cmd('CMD-MILESTONES-CREATE','gh api --method POST repos/1wgrumph/amazon-fantasy-companion/milestones --input <approved_milestone_json>',
    'Only after recorded integrated approval and planning PR landing; five exact table rows created once, existing matches reused. No premature/duplicate milestone.',
    'P2-L01 runtime only; one JSON per M1..M5 containing title, due_on and full entry/exit/slices description; UTC time retained in description.')
cmd('CMD-MILESTONES-READBACK','gh api --paginate "repos/1wgrumph/amazon-fantasy-companion/milestones?state=all" --jq ".[] | {title,due_on,description}"',
    'Exactly M1..M5 expected identities match approved title, calendar due date and description field for field; full UTC due time in description. Missing row or preapproval creation fails.','P2-L01 compares machine readback to approved table, not a remembered summary.')
cmd('CMD-CHANGELOG-CHECK','git diff <base_sha>..<head_sha> -- CHANGELOG.md && git show <head_sha>:CHANGELOG.md',
    'Every landed PR has a named entry and correct PR link; normal PR entry under [Unreleased]. Release PR moves prior entries under milestone version and records its own change/link before landing, retaining an Unreleased heading. Missing/link-only/wrong-PR entry fails.','Inspection of revision history and landed PR mapping; release special handling must not erase per-PR traceability.')
cmd('CMD-RELEASE-PREP','cat "$HOME/.claude/skills/release-process/SKILL.md"',
    'Installed workflow prepares version, tag target and changelog-derived notes at exact milestone commit; no tag/publication before OA-8. Reading skill alone never passes.',
    'Skill-driven preparation only; defaults v0.1.0..v0.4.0, v1.0.0 await OD-AFC-P2-03.',
    ['Load installed release-process and use approved version table.','Acquire tv-app-gradle and main-landing for version/changelog PR; verify required gates.','Prepare notes and tag target as reviewable draft; final APK digest added to draft notes after L05 without another product commit.','Leave actual release and public tag publication to OA-8 authority.'])
cmd('CMD-JUDGE-ACCESS','curl --silent --show-error --output /dev/null --write-out "%{http_code}\\n" https://github.com/1wgrumph/amazon-fantasy-companion && curl --silent --show-error --output <private_capture_dir>/link.json --write-out "%{http_code}\\n" <ApiUrl>/v1/link',
    'Anonymous repository returns 200 after OA-5; API response matches OpenAPI, without disclosing code/token in evidence. If GET link requires a polling handle, test anonymous /link page and valid owner-approved link flow; do not invent an unauthenticated success contract. Owner retains access through T_judge_access.','Judge access inspection; expiry/authorization expectations come from B01 OpenAPI.')

def procedure(id, command, steps, rule, description):
    cmd(id, command, rule+' '+gap, description, steps)

procedure('CMD-VERDICT-CHECK','git show <spike_merge_sha>:spikes/<sp>/VERDICT.md',
 ['Inspect every CONTRACT-AFC-P2-VERDICT field and route documentation link; resolve evidence paths and UIDs.','Compare started_at/ended_at/first_install_at to the named timebox; absence of hardware is not WORKS.','Record selected conditional and affected consumer entry criteria; an interim PARTIAL blocks only the still-unproven route.'],
 'All required fields and observable evidence present, result typed WORKS/PARTIAL/FAILS/TIMEBOX honestly; consumer does not pass on absent proof.',
 'Deterministic fields plus explicit inspection; no unallocated verdict-check script invented.')
procedure('CMD-REGISTRY-CHECK','python3 -m json.tool backend/src/provider_resolver/registry.json',
 ['Check each registry field against CONTRACT-AFC-P2-PROVIDER-REGISTRY and the landed X03 route evidence.','Check provider order, documented placeholder expansion, six-value outcome and timestamp; gameOpened requires observed arrival.','Exercise absent package, unknown access and local broadcaster with no carrying app; inspect their actual outcome.'],
 'Schema shape, source documentation and evidence all agree; empty B01 registry allowed only until X03 is due. Invented URI or inflated outcome fails.',
 'Inspection of landed provider contract; JSON parse alone cannot pass.')
procedure('CMD-FIXTURE-INDEX-CHECK','git ls-files -- backend/fixtures/replay && git diff --name-status <fixtures_merge_sha>..HEAD -- backend/fixtures/replay',
 ['For each index entry resolve its raw scoreboard/summary file; recompute sha256 and compare index.','Check game ID, ordered sequence, endpoint, capture UTC and HTTP status; correction is a later raw file.','Compare prior landed fixtures byte-for-byte; reject modifications/deletions, missing metadata or fabricated live labels.'],
 'Complete CONTRACT-AFC-P2-FIXTURE inventory, hash match and append-only history; captured fixture origin is visible.',
 'Local inspection bounded to captured game IDs; no fresh live poll implied.')
procedure('CMD-ESPN-CAPTURE','python3 <capture_tool_path> <documented_capture_arguments>',
 ['P2-X05 authors the capture tool under spikes/sp5-espn-feed/; publish its --help syntax, endpoint sources and exact bound arguments before execution.','PR1 uses completed 2026-10-11 and 2026-10-12 games once final; optional live MNF only if approved before kickoff. PR2 targets TNF 2026-10-15 only.','Write immutable raw bodies and index per fixture contract; record timing as feed observation, never hardware performance.','Run CMD-FIXTURE-INDEX-CHECK; missed live event remains pending for next window.'],
 'Documented launcher bound before run, exact bounded game/time set captured with hashes and labels. Undefined tool path/arguments = PROCEDURE_UNBOUND, never PASS.',
 'Prospective capture CLI supplied by X05; placeholders avoid inventing its future API.')
procedure('PROC-PREPARE','git rev-parse HEAD && git status --porcelain && test -f <article> && test -r <article> && command -v <required_tool>',
 ['Verify complete transport/extraction and Git metadata, exact launcher/executable binding, file-vs-directory type, permissions, pinned/scanned prerequisites.','Bind candidate/input hashes, authority, synthetic data and required leases; check budget and owner actions.','Refuse costly native/protected execution on any preparation gap; no attempt consumed and no runtime evidence claimed.'],
 'All preparation checks evidenced before execution; failure returns typed preparation gap with safe error and exit/signal.',
 'Prospective test-engineering preparation contract; no install or device action by TE.')
procedure('PROC-RELIABILITY','<qualified_suite_command>',
 ['For each new/changed engine/server/driver/browser suite bind exact candidate, suite IDs and input digests.','Run five consecutive passes, then one run with two concurrent copies; both copies use unique temp roots and resource identities.','Only truly shared resources serialize through a named cross-process lock; the single fire-tv-stick lock covers each whole instrumented run, so two copies launch together but lease the stick serially. Never use two devices or a simulator as a substitute.','Servers bind port 0 or retain listeners until handoff; readiness has one bounded load-sized deadline; fresh state per fault; warm engine per test binary.','Report slowest tests, expected vs actual gate duration and wave delta. Gracefully stop owned services before descendant cleanup; remove only owned resources on every path.','Missing code lock, inability to run concurrent-copy qualification, flakiness or changed inputs invalidates reuse and is a typed gap/failure, not a waived check.'],
 'Five sequential plus two-copy run pass with exact candidate/input binding, owned cleanup and no resource collision. Applies to new/changed suites, not one-off demonstrations or hardware benchmarking.',
 'Gate-cost and reliability evidence for engineering suites; one qualified candidate gate may serve review and landing when inputs remain identical.')
procedure('PROC-VISUAL-REVIEW','adb -s <stick_serial> shell input keyevent <keycode> && adb -s <stick_serial> exec-out screencap -p > evidence/visual/<slice>/<state>.png',
 ['Prepare sanitized fixture profile, real target, candidate hash, selected route and fire-tv-stick lease.','Drive every changed screen/state by D-pad/select/back, including loading, empty, error and focused states; compare to spec, PR-043 and PR-045.','A01 M1 covers shell, Backend not configured and network errors. Code shown/expired/linked use the deployed API after L02 at IE-P2-15.','Record state list, APK identity, output resolution, actual vs expected and findings under evidence/visual/<slice>/; provider playback cases require real provider, not stand-in video.','For secure black video collect sanitized geometry and owner camera evidence under OD-AFC-P2-02 A; B permits companion-only demo images but leaves actual composition/game-arrival claims unproven without other admissible observation.'],
 'Every changed state inspected on stick before merge; focus/legibility/behavior criteria hold; no account data. Missing or rejected visual state fails or records typed evidence gap.',
 '1080p target viewport, no phone-width substitution. Inspector records evaluation; capture command alone is not a visual-review PASS.')
procedure('CMD-TEXT-SIZE-MEASURE','adb -s <stick_serial> exec-out screencap -p > evidence/visual/<slice>/legibility.png',
 ['Record physical output resolution and UI text-class mapping; measure rendered body and score text pixels with annotated coordinates and the source rendered-size/density calculation.','At 1080p compare to the register floor; capture owner couch-legibility decision separately.','Repeat for smallest supported panel state and focused/unfocused content; anti-aliasing bounds alone do not establish font size.'],
 'VCASE-AFC-PR-045 positive criterion and owner decision satisfied; undersize text or owner rejection fails. Missing owner observation is OWNER_EVIDENCE_PENDING.',
 'Functional legibility measurement; no latency, RAM or hardware performance measurement.')
procedure('PROC-STICK-VCASE','adb -s <stick_serial> shell input keyevent <keycode>',
 ['Apply the selected proof row preconditions and stimulus to the real stick with a fixture profile and recorded APK/backend identities.','Exercise referenced register Positive and Negative separately; collect the row evidence paths, state captures and relevant sanitized backend readback.','Use the row replay/live basis; label replay on every affected value and never use replay as proof of live feed/provider behavior.','Run PROC-VISUAL-REVIEW and geometry/owner observation when the case requires them; record conditional route disposition, not a vacuous universal pass.'],
 'Both referenced criteria observed in the allocated environment, with exact article identities and no prohibited substitute.',
 'Register demonstration procedure; individual row supplies concrete actions and data setup.')
procedure('PROC-SYSTEM-VCASE','python3.12 -m pytest backend/tests/deployed -k <vcase_test_selector> -v --junitxml=<evidence_dir>/system.xml && ./tv-app/gradlew -p tv-app connectedDebugAndroidTest -PafcApiBaseUrl=<ApiUrl> -Pandroid.testInstrumentationRunnerArguments.class=<test_class>',
 ['Record the same fixture profile, event/revision and changed setting at both endpoints.','Run named deployed assertions and stick-side assertions from the case allocation; selectors must collect the corresponding VCASE, not zero tests.','Collect correlated sanitized API observations, TV state, event timestamps and changes; isolate owned dev data and cleanup.','Qualify new/changed instrumented or server-backed suites per PROC-RELIABILITY; no simulated TV acceptance.'],
 'Both real endpoints meet the referenced Positive and Negative on the same input; single-endpoint green is insufficient.',
 'System tests with settings UI or TV surfaces; missing Android/deployed test write sets are TE-P2-F01.')
procedure('PROC-SOURCE-VCASE','git ls-tree -r --name-only <candidate_sha> -- tv-app backend && git show <candidate_sha>:<article_path>',
 ['Inspect all allocated source paths and connected callers from the case model allocation.','Compare explicit register Positive and Negative without changing their text; record file:line and inspected revisions, including a no-match result and search scope for absence claims.','For UI exclusion also inspect every actual screen/route and API operation. For secrets inspect only safe metadata and source flow, never secret values.'],
 'Complete named inspection article with positive support and no referenced negative observation; grep silence over a partial scope does not pass.',
 'Non-test source/architecture inspection; no product tests are generated by this procedure.')
procedure('PROC-SECRET-CONTAINMENT','git ls-tree -r --name-only <candidate_sha> -- backend tv-app && apkanalyzer files list <apk>',
 ['Inspect SSM parameter types/identities via owner-provided metadata or authorized role metadata, never GetParameter/WithDecryption or raw secret values.','Trace all secret reads server-side, IAM limits, no TV Yahoo/AWS credentials; inspect repo and extracted APK member inventory with secret-value output suppressed.','Run CMD-GATE-HYGIENE and CMD-REVERIFY-APK for any binary containment claim; archive-format/string checks alone cannot prove absence.','If no safe APK semantic/whole-content evidence exists, keep REVERIFY_CAPABILITY_GAP and the product case open.'],
 'VCASE-AFC-PR-055 criteria supported across source, APK and metadata; leaked values fail and trigger owner rotation without reproducing them.',
 'Credential-protecting inspection, no permission to retrieve credentials.')
procedure('PROC-E2E-LIVE','adb -s <stick_serial> exec-out screencap -p > evidence/visual/<slice>/<state>.png',
 ['Confirm ESPN scoreboard kickoff at execution; record live window, event IDs and deployed/APK hashes. X09: Sun 2026-10-18; X10: Mon 2026-10-19; X12 capture: Thu 2026-10-22.','Hold fire-tv-stick and aws-afc-dev; no redeploy during in-progress game. Use actual provider playback and linked fixture profile.','Observe relevant live event -> heads-up -> Watch -> actual outcome; panel mode, points, source and freshness; X10 adds correction, starter change, dedup and stale/unavailable scenarios.','Correlate event/revision to sanitized records and geometry/visual evidence; missing naturally occurring correction uses labeled replay for logic and leaves live-only claim open.','On missed window/no qualifying event name next window; no silent scope cut. On observed defect return to Orchestrator for bug-triager.'],
 'Named scenarios observed with correct provenance and outcomes; any replay substitute is explicitly bounded and live claims stay open until live evidence exists.',
 'Real-window functional demonstration, not hardware benchmarking.')
procedure('CMD-E2E-REPLAY','python3.12 -m pytest backend/tests/deployed -k replay -v --junitxml=<evidence_dir>/replay.xml',
 ['Use immutable indexed fixtures through the deployed supported replay path; bind profile, event sequence and fixture hashes.','On real stick observe alert, Watch outcome and panel; run CMD-ADB-SCREENCAP and CMD-ADB-GEOMETRY for each changed state.','Compare stored alert and panel revisions after duplicate/correction/starter-change inputs; record source labels.'],
 'Replay logic and connected path pass on real endpoints; provider playback remains real. No assertion of live ingest or current game arrival from replay alone.',
 'IE-P2-29/32 rehearsal and repeatability evidence; absent supported replay fixture setup is a gap.')
procedure('PROC-DEMO-CAPTURE','adb -s <stick_serial> shell screenrecord --time-limit <seconds_le_170> /sdcard/afc-demo.mp4 && adb -s <stick_serial> pull /sdcard/afc-demo.mp4 <private_clip_path>',
 ['Use final APK hash from IE-P2-42 and approved D05 shot list, TNF 2026-10-22; sanitized companion screens only in adb captures.','Owner supplies camera shots for protected video under A; source-label all replay and owner-filmed shots.','Inspect clips privately for account/customer data; manifest only sanitized relative name, duration, sha256, shot source, VCASE evidence and final APK identity. MP4/MOV ignored.','Owner uploads/submits; no public export by agent.'],
 'Manifest complete, total planned duration <=170 s and every claimed behavior has passing evidence; no protected black frame sold as game arrival.',
 'P2-X12 captures final candidate only; earlier-product clips cannot silently satisfy final APK claims.')
procedure('PROC-LAND','gh pr checks <pr_number> --repo 1wgrumph/amazon-fantasy-companion --json name,state,workflow',
 ['Use ship-pull-request after configured independent Reviewer, OCR per-file evidence, applicable Reverify and one bounded repair; no unapproved cadence change.','Hold main-landing, add required CHANGELOG entry and verify exact head with CMD-PR-CHECKS; reuse qualified gate only when inputs identical.','During authorized execution merge with gh pr merge <pr_number> --repo 1wgrumph/amazon-fantasy-companion --merge --delete-branch or --rebase --delete-branch; never --squash, force-push or local-main commit.','Record resulting SHA, ancestry and checks; remove merged worktree and local/remote branches without destroying unrelated work.'],
 'Reviewed exact candidate landed through PR with preserved commits, green expected checks, changelog and receipts; no premature milestone or public release.',
 'Prospective runtime landing procedure; this assigned TE session has no landing authority.')
procedure('PROC-BUG-TRIAGE','cat "$HOME/.claude/skills/bug-hunter-triage/SKILL.md"',
 ['Classify raw failure: expected negative, harness/configuration/environment, duplicate known issue or reproduced product defect; do not auto-file.','Return evidence to Orchestrator; it loads bug-hunter-triage and constructs a bounded bug-triager packet with reproduction, origin/escape across requirements/tests/models/plans, product vs test-only, regression red/green and prevention.','Preserve frozen bug-triager routes and capabilities; choose disjoint write set and current-wave lease. An authorized lane-route exception must carry BUG_ROUTE plus authority, never a silent substitution.','Repair within configured review/repair budget; verify regression, prevention and full affected gate before closeout.'],
 'All defect packets routed and evidenced; report-only or unverified closure fails. No defect produces a nested TE dispatch.',
 'Every observed defect routes through owner-amended bug-triager policy; no issue or remote write by this session.')
procedure('PROC-README-FRESH-SETUP','git rev-parse HEAD && bash tools/ci/gate.sh docs && bash tools/ci/gate.sh hygiene',
 ['Use a clean authorized checkout at recorded candidate, follow README setup exactly with documented owner inputs and scanned tools.','Build TV/backend, connect only to afc-dev through the documented linking flow, confirm limitations and voice status match verdicts.','Record each command, expected/actual result, no hidden local dependency, judge route and owner retention duty through 2026-11-20.'],
 'Fresh walkthrough completes with only documented inputs; undocumented step, path leak or false capability fails.',
 'P2-D03 demonstration; shell commands alone do not establish walkthrough completeness.')
procedure('PROC-SUBMISSION-CHECK','git show <candidate_sha>:docs/submission/writeup.md && git show <candidate_sha>:docs/submission/demo-plan.md && git show <candidate_sha>:docs/submission/owner-checklist.md',
 ['Check D04 implemented claims against proof evidence and current official public citations; mark SD-036 context external, preserve Fantasy View distinction without invented capability.','Sum D05 shot seconds <=170; each source and UID has passing evidence; black video, replay, unavailable voice and fallback limits named.','Map every OA-1..11 and exclusions owner-only action to accountable owner and due time, distinguish optional OA-11 and conditional OA-9; record which early actions already completed.','Check current submission rules before finalization; no posting/upload, credentials or public export by agent.'],
 'All three deliverables and their reference evidence complete; unsupported claim, overlength, omitted owner duty or unsanitized material fails.',
 'Inspection used per slice on the artifact that exists, final aggregate at IE-P2-37; other pending artifact is not a fabricated PASS.')
procedure('PROC-SCRIBE-ASSEMBLY','git show <candidate_sha>:docs/developer-feedback/observations.md && bash tools/ci/gate.sh hygiene',
 ['Enumerate every tool/API/SDK/device from packets and returns, including explicit no-new-observation tools.','Assemble per-tool Product Feedback required fields, optional priority-ranked Feature Requests, and sanitized Friction Log with official submission fields.','Verify current official rules; cross-reference observation IDs and artifacts without private paths, accounts or secrets.','Keep feedback local; OA-8 governs external sending.'],
 'Complete per-tool coverage and required fields, safe citations and no invented observations; absent tool/field or private content fails.',
 'P2-SCR1 consumes continuous observation log; no external feedback sent.')
procedure('PROC-LIFECYCLE-CONTROLS','git rev-parse HEAD && git diff --stat <base_sha>..<candidate_sha>',
 ['Inspect the selected local proof row against its named requirement and current packet/receipt/lease/approval articles.','Run its evidence commands and compare both positive controls and a negative challenge from the row; challenges use synthetic planning records or inspection, never unauthorized real protected actions.','Record exact inspected files, decision IDs, pass/fail and missing proof; do not edit authority records.'],
 'Every enumerated duty in the local row has evidence and each stated violation is rejected or absent; incomplete inspection is a gap.',
 'Common inspection entrypoint with case-specific executable checklist; no bespoke receipt schema.')
procedure('PROC-PATH-SCAN','python3 tools/ci/check_paths.py',
 ['Run gate hygiene over tracked candidate files plus inspect newly authored files before commit.','Apply shape-based home-root and root-anchored local-path detection from rule 12/PR-056; print only file:line:rule ID, never matched text.','Classify legitimate URI/API root paths separately from machine-local filesystem paths; scan binaries/captures via their appropriate safe evidence check.'],
 'No prohibited local path or secret shape; missing scanner is TOOL_MISSING. Existing unrelated leaks block landing but are not silently edited by TE.',
 'Extends inspection to untracked plan inputs before landing; required source text not duplicated.')
procedure('PROC-INTERFACE-PROFILE-CHECK','git show <candidate_sha>:backend/src/api/openapi.yaml',
 ['For API, envelope, provider registry, feed fixture and device-link boundaries record each applicability disposition and trace to proof rows.','Require both positive and negative for identity/auth, types/units/body limits, timing/retry, initialization, states/errors/recovery and provenance fields; missing value gets named gap, never N/A without reason.','Use local contract table interface_coverage in this SEIT; check against both endpoint evidence at integration.'],
 'All APPLICABLE obligations have bidirectional executable cases; unresolved limit/owner/source or one-sided case fails structural completeness.',
 'Planning coverage check does not claim semantic compatibility or connected-runtime PASS.')

# These are executable stimuli and evidence observations; the register alone owns criteria.
# number: design, paired product slice, closing slice, stimulus, observable failure
product_specs = {
1:('LINEUP','B03','L03','Use authorized Yahoo read-only linked fixture account, two weeks and active/bench slots; inspect returned roster/settings and request-scope audit. Repeat with failed/absent Yahoo approval; keep Yahoo-route proof open if unavailable.','A write-scope request or an eligibility-derived starter appears in sanitized request/roster audit.'),
2:('TV','A02','A02','Select multiple leagues, teams, players and favorites with the remote; restart app and compare persisted profile revision and UI selection set.','Before/after selection sets differ without a recorded customer change.'),
3:('TV','A02','A02','Use X07 installed-package baseline; compare every supported installed package and an absent fixture package with detector report. Do not uninstall owner provider apps to create a negative.','Detector marks a known absent package installed or misses an installed supported package.'),
4:('RESOLVE','B06','L03','Resolve identical installed-app profiles with integration-verified, customer-confirmed and unknown access records; inspect basis field for each.','Verified access appears in an install-only result with no permitted basis.'),
5:('TV','A02','A02','Override one detected app fact and local market; restart and trigger profile/detector refresh, then compare retained overrides.','A refresh changes the customer override without action.'),
6:('LINEUP','B03','L03','Run recorded boundary fixtures immediately before, at and after T_yahoo with approval absent; submit ESPN-roster manual lineup via supported API; inspect lineage.','Post-trigger manual data carries Yahoo provenance or activation is absent.'),
7:('LINEUP','B03','L03','Exercise supported source switch with both source records prepared; query active source throughout the transition, including retry/failure.','Any sampled committed state has zero or two active sources.'),
8:('FEED','B02','L03','Replay same game set for a selected-player profile, a favorites-only profile and an unrelated profile across enabled/quiet boundaries; inspect monitored game IDs.','Irrelevant or disabled-period game is present in monitoring records.'),
9:('TV','A02','X09','Change schedule and game-day mode from the remote; correlate settings revision with deployed monitored-game readback before/after boundary.','Monitored game set does not follow the stored enablement.'),
10:('TV','A02','A02','Enable the supported X07 context mechanism, record its source; disable it and inspect the detector read trace plus decision basis. Unsupported mechanism retains a typed capability gap.','A context read occurs after opt-out or lacks a supported mechanism.'),
11:('POLICY','B05','L03','Replay with supported observed context, then disabled/unavailable detection; inspect every monitoring decision basis.','A decision lacks a basis or carries contradictory basis values.'),
12:('FEED','B02','L03','Ingest indexed raw scoreboard/summary sequence including corrections; compare normalized stored event fields and revisions, then schema-invalid derivative in isolated dev state.','Field absent, incorrect revision, or partial invalid-poll store appears.'),
13:('FEED','B02','L03','Using deployed test setup, make the feed transport unavailable and serve a contract-changed response; activate indexed replay and inspect all affected downstream values.','Any replay-derived value retains a live source label.'),
14:('POLICY','B05','L03','Replay all alert-type scenarios with matching/mismatching starters and disabled types; include yard distances 19/20/21, margins 8/9 and quarters Q3/Q4/OT. Register inside-20 criterion controls over inconsistent glossary wording.','Alert fires at a rejected boundary or lacks the required match; any player-on-field claim fails.'),
15:('ALERTPATH','A03','X09','Use verified X02 route during real provider playback; trigger live qualifying alert and select Dismiss then Watch on separate events; repeat in panel-only mode.','Playback is displaced, companion foregrounds, actions absent, or panel-only emits heads-up.'),
16:('POLICY','B05','X09','Toggle each alert type on the real settings UI and run identical labeled event stream against deployed policy; correlate revision to emitted records and UI.','Disabled-type record is emitted or stale UI setting governs the policy.'),
17:('POLICY','B05','X09','Set restrictive then permissive frequency in UI; replay identical timestamped event sequence including gap boundaries; compare emission counts and times.','Output contains a disallowed extra alert or ignores the changed setting.'),
18:('POLICY','B05','X09','Set quiet interval in UI; deliver matching events immediately before, within and after its boundaries using isolated clock-controlled test inputs.','An in-quiet-hours emission appears in recorded output.'),
19:('POLICY','B05','X09','Set game-day periods in UI; replay matching events on each boundary and outside; inspect stored settings and outputs.','An out-of-period alert appears.'),
20:('POLICY','B05','L03','Replay timestamped events for each supported delay, including zero and range endpoints; compare event, creation and release times at boundary.','Recorded release precedes the register delay criterion.'),
21:('ALERTPATH','A03','A03','Cycle every offered presentation using settings and identical replay event on real stick; observe heads-up and panel-only outputs.','Rendered presentation differs from recorded choice.'),
22:('ALERTPATH','A03','X11','If OD-AFC-03 enables X11 and verified route exists, toggle announcements enabled/disabled on stick and observe audio; otherwise inspect the actual UI and run triggering events with route unverified to prove no offer/output.','Audio/voice offer appears without verified route or enabled consent; verified enabled route fails to speak.'),
23:('POLICY','B05','L03','Replay identical event at Off/Mild/Hype and compare commentary entity IDs and phrases to triggering fields; include unknown/missing entity.','Named entity absent from source event, Off commentary, or unchanged level effect.'),
24:('MATCH','B04','L03','Use recorded cross-provider ID pairs for same and distinct players/events, ambiguous name collision and unmatched mapping; compare canonical identities.','Same entity splits or distinct entities merge.'),
25:('MATCH','B04','X10','Replay same event/revision repeatedly and with retry; include an event matching multiple alert types; count stored/emitted alerts per resolved event.','A second alert for the same resolved event appears, including cross-type duplicates.'),
26:('MATCH','B04','X10','Emit event then apply later correction revision from indexed fixture; query existing alert and panel before/after; force retry and stale revision delivery.','Alert or panel retains the superseded fact, or correction creates a duplicate alert.'),
27:('ALERTPATH','A03','X09','Trigger event for known lineup player and matchup, then inspect rendered alert against sanitized event and lineup IDs; remove context in negative fixture.','Visible alert has missing or mismatched triggering player/matchup.'),
28:('POLICY','B05','X09','Inject team red-zone event with no player-level on-field evidence; inspect deployed alert and all TV renderings.','TV/backend output asserts a player is on field or will score from team entry.'),
29:('RESOLVE','B06','L03','Resolve broadcaster/provider combinations using landed registry and four independent input facts; include CBS/FOX/NBC with and without carrying app.','Install-only verified route or unavailable-carrier deep link appears.'),
30:('WATCH','A04','X09','For each evidenced provider route select Watch during live or real channel playback, independently observe destination/game and record attempted event/channel ID.','Landing at app home/search is reported as the required game/channel arrival.'),
31:('WATCH','A04','A04','Exercise supported success and failure routes using installed/absent packages and known unknown/denied access; compare observed destination to exactly one outcome report per attempt.','No result, multiple results, invented enum or misreported destination appears.'),
32:('RESOLVE','B06','X09','Run install-only/unverifiable access fixture through API, alert, Watch and panel; inspect each visible basis label.','Any surface presents unverifiable access as verified/included.'),
33:('RESOLVE','B06','X09','Hold installed-app report true while removing subscription confirmation; inspect resolver output and every TV inclusion message.','Any inclusion promise depends solely on installation.'),
34:('RESOLVE','B06','X09','From TV settings swap preference between two genuinely available fixture services for same channel; resolve again with identical other facts.','Chosen service contradicts persisted preference.'),
35:('WATCH','A04','A04','Enable switching confirmation; select Watch, cancel, retry and confirm. Then exercise any explicitly supported opt-in automatic setting.','Launch occurs before required confirmation or after cancel.'),
36:('WATCH','A04','X11','Conditional verified Alexa tuning: enable then disable and observe actual route. Without X11 approval or verified route, inspect no offer and trigger Watch without voice output.','Alexa offer exists without both gates or claims unverified tuning.'),
37:('POLICY','B05','X09','Opt out via TV settings while monitoring remains enabled; replay same events and correlate detector read audit, policy basis and update set.','Detection/personalization data used after opt-out.'),
38:('AUTH','B01','L02','Issue device code on stick; leave unconfirmed, try expired/reused code through supported negative setup, then owner completes phone/browser action; compare TV state and authorized API access.','Link completes without owner code action, expires incorrectly or accepts replay.'),
39:('PANEL','A05','X09','Render fixture lineup under available Yahoo league scoring and both manual presets; compare rows/total/status/progress and basis to deployed projection.','Displayed value has no scoring basis or differs from same-source projection.'),
40:('PANEL','A05','X10','Withhold feed through supported scenario; observe at 59/60/61 seconds age, then provide missing-value record separately; capture labels on stick.','Old/missing value remains unlabeled or unknown becomes zero.'),
41:('PANEL','A05','X09','Only with X04 modeB route, observe simultaneous real provider video and panel; compare window rectangles and aspect dimensions plus admissible visual observation. If route absent, record unproven PR-041 with C5 disposition; PR-047 evidence cannot PASS this row.','Overlap/crop/aspect distortion or absent actual simultaneous video proof.'),
42:('PANEL','A05','A05','Use only D-pad/select/back to hide/show panel and change followed team and league; inspect resulting content and restored focus.','A required control needs touch/keyboard/phone or cannot be reached.'),
43:('PANEL','A05','A05','Enumerate panel focusable operations; traverse and activate each by TV remote, including edges, empty/error and focused states.','Any operation is remote-dead or lacks visible focus.'),
44:('PANELSVC','B07','X09','Change team/league/display setting in real UI and query deployed panel revision while visible and hidden; reopen and compare.','Panel state contradicts persisted settings.'),
45:('PANEL','A05','A05','Run CMD-TEXT-SIZE-MEASURE for smallest body/scores at 1080p; show resulting panel to owner at couch viewing position and record explicit observation.','Measured floor fails or owner rejects legibility.'),
46:('PANELSVC','B07','X10','Change starter, emit/correct event, hide panel during later update then show; compare common facts across alert record and panel revision.','Same fact differs across surfaces or hidden-panel refresh fails.'),
47:('PANEL','A05','A05','Use failed/timeboxed X04 verdict to select fullScreen and demonstrate it on stick; inspect absence of stand-in video and honest presentation. If modeB succeeds, retain conditional alternative inspection without claiming unexecuted fallback demonstration.','Fallback silently covers provider video, adds stand-in player or changes device.'),
48:('WATCH','A04','X09','With fullScreen panel scenario selected, trigger real-provider alert and Watch; observe leaving companion and actual routing outcome.','Alert/Watch is trapped in companion screen.'),
52:('TV','A01','X09','Install host-built candidate on exact X01 identified stick, launch shell and all realized features; record model/API and any target-only failure.','Target install/launch/operation fails or unsupported target is silently substituted.'),
53:('TV','A01','L05','Inspect candidate app/build.gradle.kts and exact release APK manifest via apkanalyzer; compare declared floor and run CMD-REVERIFY-APK for built-APK claims.','Source or built manifest reports another minimum API or APK evidence is not grounded.'),
54:('BACKEND','B01','L03','Inspect template and deployed-resource inventory against approved Free-plan service set and owner account evidence; no upgrade or paid trial is attempted as negative test.','Paid-only or orphan paid resource appears, or account eligibility cannot be established.'),
55:('AUTH','B01','L05','Run PROC-SECRET-CONTAINMENT across source, exact APK and parameter metadata only; compare safe inventory to the register allocation without retrieving values.','Secret material outside server-side parameters or unexamined APK content invalidates containment claim.'),
56:('GATE','G01','D03','Run PROC-PATH-SCAN across all tracked source and candidate files including plan/evidence; inspect root-anchored local paths without printing matched values.','Prohibited local path is detected or some committed source is unscanned.'),
57:('TV','A01','D03','Inventory source navigation, UI screens and backend operations; inspect actual reachable app surfaces for excluded social functions.','Excluded social surface or endpoint is present.'),
58:('BACKEND','B01','L03','Enumerate OpenAPI and client operations; execute deployed link/profile/alerts/panel/providers plus routing-outcome/installed-apps, malformed/unauthorized/foreign-profile/expired/retry paths.','Required TV operation unexposed, bad error/envelope or authorization bypass.'),
59:('BACKEND','B01','L03','Trace aggregation, game monitoring, identity resolution and commentary callers from API/pipeline to backend modules; inspect TV for duplicate heavy responsibilities.','Named backend duty is implemented on render/client path or missing backend-side.'),
60:('POLICY','B05','L03','Replay simultaneous-game fixtures for two distinct profiles; inspect each update stream under current consent/period settings.','Profile receives another or irrelevant game update.'),
61:('PANEL','A05','A05','Instrument functional row-update counters for burst payloads with unchanged/changed rows; hide panel, deliver burst, then show; compare affected IDs and state. No timing/RAM measurement.','Whole-screen rerender, uncoalesced repeats or hidden application occurs.'),
62:('PANEL','A05','A05','Inspect declarations and all growth paths for alert queues, history, images and caches in alert/panel components; record numeric bounds and eviction/reset sites.','Named resource has an unbounded allocation or growth path.'),
63:('TV','A01','A05','Trace network, parsing and computation entrypoints and coroutine/thread dispatch through alert, panel and detector components; inspect connected callers.','Any specified work can execute on rendering thread.'),
64:('FEED','B02','L03','Hash owned stored-event snapshot; inject malformed ESPN derivative through deployed ingest; rehash complete owned event set and inspect rejection record.','Any stored-event byte changes from invalid poll.'),
65:('LINEUP','B03','L03','Feed coefficient-isolating statistics under each manual preset, default, invalid third preset and Yahoo league scoring; compare values to authoritative preset table by reference.','Unsupported preset accepted, wrong coefficient/default or Yahoo uses a manual table.'),
66:('TV','A02','X09','Open new manual profile, select each offered preset, restart TV and compare backend selection and panel point changes using same feed statistics.','Third option, lost selection or silent preset change appears.')
}

def slice_uids(c):
    return ['AFC-PR-'+n for n in re.findall(r'\b\d{3}\b', c[4])]
def support_for(uid):
    return [sid for sid,c in slices.items() if uid in slice_uids(c)]
def resource_fields(method, env, product):
    if method != 'test': return {}
    if 'tv-app' in env or 'settings UI' in env or 'TV ' in env:
        return {'resource_group':'fire-tv-stick (cross-process lock); aws-afc-dev when system',
                'expected_gate_time':'Planning estimate 10 min per instrumented suite; system deployed leg 5 min. Qualify 5 sequential + one two-copy run (7 executions, serialized for stick); record actual delta, no hardware benchmark.',
                'qualification':'PROC-PREPARE and PROC-RELIABILITY; tests must declare lock name, unique temp/state and owned cleanup before first run'}
    return {'resource_group':'aws-afc-dev (isolated fixture-profile data; deployment lease); host-pytest local TDD',
            'expected_gate_time':'Planning estimate local suite 2 min, deployed suite 5 min; newly engine-backed tests require 7 executions for qualification. Actual cost and wave delta recorded; not measured yet.',
            'qualification':'PROC-PREPARE; PROC-RELIABILITY applies when suite starts server/engine/browser; plain client calls record applicability and owned-data isolation'}

for uid in active:
    n=int(uid[-3:]); row=register[uid]; vcase='VCASE-'+uid
    design,prod,close,stim,neg=product_specs[n]; product='P2-'+prod; closer='P2-'+close
    allocation=row[3]; method=allocation.split(',')[0].lower()
    env=allocation.split('Positive:')[0].split(',',1)[1].strip().rstrip('. ')
    ref=str(P/'requirements-register.md')+'#'+vcase
    if method=='test':
        command='CMD-TVAPP-INSTRUMENTED' if n==61 else ('PROC-SYSTEM-VCASE' if 'settings UI' in env or 'TV surfaces' in env or 'TV panel' in env else 'CMD-DEPLOYED-TESTS')
    elif method=='demonstration': command='CMD-TEXT-SIZE-MEASURE' if n==45 else 'PROC-STICK-VCASE'
    else: command={53:'CMD-REVERIFY-APK',55:'PROC-SECRET-CONTAINMENT',56:'PROC-PATH-SCAN'}.get(n,'PROC-SOURCE-VCASE')
    evidence=(f'evidence/visual/{closer}/{vcase}/' if method=='demonstration' else str(P/f'evidence/{closer}/{vcase}/'))
    fields={'slice':closer,'product_slice':product,'test_slice':product+'T' if product+'T' in slices else 'not applicable: evidence-only spike',
            'register_verification_case':vcase,'register_method':method,'register_environment':env,
            'positive_criterion_ref':ref+' / Verification method / Positive','negative_criterion_ref':ref+' / Verification method / Negative',
            'red_expectation':'CMD-RED binds named behavior assertions in the paired Test Implementer slice to the same IDs/hashes in product green; scaffolding/import/tool failures do not count. This supports implementation only; register method/environment still controls closure.',
            'reverify':('Applicable: exact built APK attributes; CMD-REVERIFY-APK; no runtime evidence yet.' if n in (53,55) else 'Reverify: not applicable — this row establishes '+('observed functional behavior on the real target, not static APK attributes' if method=='demonstration' else 'functional responses or source/process properties, not a compiled-binary attribute claim'))}
    if n in (53,55):
        fields.update(apk_artifact='tv-app/app/build/outputs/apk/<variant>/<apk_name>.apk (candidate.final; digest from P2-L05)',reverify_invocation=commands['CMD-REVERIFY-APK']['command'],reverify_readiness='REVERIFY_CAPABILITY_GAP until all required APK claims are groundable; installed tool does not advertise APK semantics')
    if method=='test':
        fields.update(test_article=row[4],stimulus=stim,measured_response='Correlated response/store/UI observations evaluated against '+ref,test_environment=env,test_handoff='Named Test Implementer uses write-tests; no product test code authored here',**resource_fields(method,env,product))
    elif method=='demonstration':
        fields.update(demonstration_scenario=stim,observed_behavior=ref+' criteria observed and recorded',
                      live_window_or_replay_basis=('Live Sun 2026-10-18; retry Mon 2026-10-19 then Thu 2026-10-22. Indexed replay for controlled negatives, never replacing live provider evidence.' if closer=='P2-X09' else 'Mon 2026-10-19 live check plus labeled indexed replay for corrections/stale boundaries.' if closer=='P2-X10' else 'Sanitized deterministic profile or labeled backend/fixtures/replay sequence; actual stick/provider route. X11 conditional after M3, cutoff 2026-10-21T12:00:00Z.'),evidence_path=evidence)
    else: fields.update(inspection_article=row[4],inspection_criteria=ref,inspection_record=evidence)
    pre=['Bound inputs in source_baseline unchanged; resolve '+vcase+' in Markdown register and spec §7.1; criteria remain owned there.',
         'Approved Phase 2 package and applicable open decisions resolved before dependent execution; PROC-PREPARE passes with exact candidate and fixture hashes.',
         'All supporting slices and required landed spike verdicts available; required tool or test absent is a typed gap.']
    if method=='demonstration' or command in ('PROC-SYSTEM-VCASE','CMD-TVAPP-INSTRUMENTED'):
        pre+=['Lease fire-tv-stick; X01 device identity; same-host APK hash and signer; sanitized profile; OA-4 provider sessions where needed; OA-10 owner link completion for system cases.']
    if 'backend' in env or 'AWS' in env or command in ('CMD-DEPLOYED-TESTS','PROC-SYSTEM-VCASE'):
        pre+=['OA-3 afc-dev available; aws-afc-dev lease; deployed commit/backend tree verified; test setup modifies only owned synthetic dev records through authorized route, never production or credentials.']
    if n in (22,36): fields['conditional_disposition']='Without verified route, demonstrate no voice offer/output as OD-AFC-03 permits; enabled-route branch stays unexecuted/not applicable by condition, never claimed demonstrated. If X11 is not dispatched, closure is P2-A03 (022) or P2-A04 (036).'
    if n in (1,10,15,30,41): fields['route_gap_rule']='Approved fallback or honest weaker outcome may satisfy another row; it does not prove this row. Keep this case NEEDS_MORE_EVIDENCE unless its own VCASE evidence exists; owner-accepted gap is distinct from PASS.'
    if n in (47,48): fields['conditional_disposition']='Trigger branch must be demonstrated when fullScreen selected. If modeB selected, inspect trigger/fallback contract and record branch not exercised; do not label the absent demonstration PASS.'
    data['proof_cases'].append({'id':'SEIT-'+uid,'kind':'verification','requirement_id':uid,'design_id':'DES-AFC-P2-'+design,
       'command_id':command,'method':method,'preconditions':pre,'stimulus_or_procedure':stim+' Execute '+command+' and evaluate both referenced criteria.',
       'expected_result':'The Positive allocation of '+ref+' holds in its registered environment; no Negative allocation is observed.',
       'observable_evidence':evidence+' (sanitized observations, exact command/exit, candidate/input digests and criterion comparison; visual files where required)',
       'pass_fail_rule':'PASS only when both '+vcase+' allocations are evaluated with admissible evidence in the stated environment. '+neg+' => FAIL. '+gap+' Owner-accepted gap is never rewritten PASS.',
       'method_fields':fields,'negative_or_failure_case':'Exercise the Negative allocation of '+ref+'. Observable failure: '+neg,
       'boundary_test_layer':env,'closing_slice':closer,'supporting_slices':support_for(uid),'execution_status':'not_run (planning only)'})

# local key: method, design, command, closing slice, supporting slices, stimulus, observable positive, observable failure
local_specs={
'SPIKE-01':('inspection','SPIKES','CMD-VERDICT-CHECK','P2-X07',['P2-X01','P2-X02','P2-X03','P2-X04','P2-X05','P2-X06','P2-X07','P2-X11'],
 'Inspect every required spike verdict and route consumer dispatch. Compare evidence and landing timestamps with consumer start; include conditional X11 disposition.',
 'Each dependency is backed by landed route-specific verdict and resolvable evidence before product dependence.',
 'Consumer starts on missing/unlanded verdict, or verdict omits required field/evidence/UID/conditional.'),
'SPIKE-02':('demonstration','SPIKES','PROC-STICK-VCASE','P2-X04',['P2-X01','P2-X04'],
 'Bind X01 first_install_at; check X04 end <= first_install_at +24 h; observe supported simultaneous route with geometry and admissible provider observation, else record fullScreen.',
 'Timebox and evidence-based mode choice recorded with actual observed composition or honest fallback.',
 'Late verdict or modeB selected with overlapping/cropped/absent provider evidence.'),
'SPIKE-03':('demonstration','WATCH','CMD-REGISTRY-CHECK','P2-X03',['P2-X03'],
 'Inspect/observe attempts in Prime Video, ESPN, DirecTV Stream, YouTube TV order then local-broadcast case; bind documented intent/URI to outcome and registry entry. Complete TNF follow-up separately.',
 'Every attempted provider has package/source/outcome and arrival observation, with interim vs final limits explicit.',
 'Skipped provider silently declared tried, invented URI, wrong order or false gameOpened.'),
'GATE-01':('test','GATE','CMD-GATE-ALL','P2-G01',['P2-G01T','P2-G01'],
 'Run G01T negative fixtures for failing subcheck, missing tool, absent vs empty tree, changed-path selection and workflow pins/names, then same tests green after G01.',
 'Every exit/output and selected job matches CONTRACT-AFC-P2-GATE-AREAS; missing tool nonzero GAP; no-tree only when absent.',
 'Failing check exits 0, missing tool passes, empty tree claims no-tree or path-selected job missing.'),
'VNV-01':('inspection','GATE','CMD-GATE-DOCS','P2-D01',['P2-D01'],
 'Read three new Vnv guidance files and index; inspect Scope, Tools, Review Focus and findings target per file; execute docs gate.',
 'Three complete areas and index links resolve; docs gate passes.',
 'Missing area, heading, target or dangling index reference.'),
'LAND-01':('inspection','LANES','PROC-LAND','P2-R5',list(slices),
 'Inspect each PR head/review/gate/repair/merge receipt and preserved commit ancestry under main-landing, including late evidence-only PRs.',
 'Every merge follows configured review and bounded repair with green exact-head gates; no squash/force-push/local-main commit.',
 'Unreviewed head, missing gate, squash merge, force-push or excess repair round in receipt.'),
'REV-01':('inspection','LANES','CMD-OCR-DELEGATE','P2-L05',list(slices),
 'For every Reviewer packet inspect frozen settings, run OCR preview and rules over all listed files, and inspect claim inventory for applicable Reverify vs reasoned N/A.',
 'Both capabilities preserved; per-file OCR and applicable exact-APK Reverify results or typed gaps recorded, never silently omitted.',
 'Roles-only binding, omitted file rule group, missing Reverify or unavailable tool represented as PASS.'),
'VIS-01':('demonstration','VISUAL','PROC-VISUAL-REVIEW','P2-X09',['P2-A01','P2-A02','P2-A03','P2-A04','P2-A05','P2-X09'],
 'For every rendered-UI PR enumerate changed screens/states and compare actual stick captures/review before merge to spec and focus/legibility criteria; A01 linking states finish after L02.',
 'Complete sanitized per-state visual review on exact stick candidate, with findings in same review/repair round.',
 'Changed state missing, emulator-only capture, account data, black video claimed verified, or rejected focus/legibility.'),
'BUG-01':('inspection','LANES','PROC-BUG-TRIAGE','P2-6',[],
 'Inspect all actual defect packets and one synthetic missing-route/regression/prevention packet; reject malformed packet without dispatch. If no defect occurs, inspect empty ledger and configured routing, not a fictional fix.',
 'Every actual defect has required classification, route, regression and prevention evidence; missing fields rejected.',
 'Defect fixed on unapproved route or closed without regression/prevention proof.'),
'PATH-01':('test','GATE','CMD-GATE-HYGIENE','P2-G01',list(slices),
 'Run G01T hygiene regression with runtime-generated home/root path fixtures and sanitized reports; scan complete tracked candidate and untracked intended artifacts before commit.',
 'Scanner catches prohibited local path shapes and all intended files pass without leaking matched values.',
 'Committed local path escapes scan or scanner prints private matched value.'),
'SUPPLY-01':('inspection','GATE','CMD-SUPPLY-SCAN','P2-B01',['P2-X01','P2-A01','P2-B01','P2-G01'],
 'Inventory every acquisition and compare digest-specific scan receipt timestamp with first invocation, including JDK17 prerequisite; inspect BLOCK/INDETERMINATE refusal handling.',
 'All artifacts scanned before first use, pinned digest matches; refused artifacts not executed.',
 'Unscanned artifact executed, digest drift or ignored BLOCK/INDETERMINATE.'),
'REL-01':('inspection','REVREC','CMD-CHANGELOG-CHECK','P2-R5',list(slices),
 'Compare all landed Phase 2 PRs against changelog history at their merge and successor release headings; include plan-seeding PR and late L05/X12 evidence PRs.',
 'Every landing has its change and PR link with correct release migration, none erased.',
 'Landed PR missing, wrong link, or release move loses an entry.'),
'REL-02':('inspection','REVREC','CMD-RELEASE-PREP','P2-R5',[f'P2-R{i}' for i in range(1,6)],
 'Inspect each milestone version, notes, tag target and release-process preparation receipt; verify publication absent unless OA-8 authority for that release exists.',
 'Five correctly bound prepared releases; publication remains separately authorized.',
 'Wrong candidate target, notes not derived from changelog or release published without OA-8.'),
'SPEC-01':('inspection','SPIKES','CMD-GATE-SPEC','P2-D02',['P2-D02'],
 'Compare D1 revision to every landed SP1..7 verdict and SP8 if run, aligned names and approved constants; inspect changed-section/PR/diff revision links; rebuild spec byte-identically.',
 'All landed verdicts/limitations and aligned model terms reflected, source/built output identical and gate passes.',
 'Omitted later verdict, retired player retained, unapproved constant, missing revision links or rebuild drift.'),
'PLAN-01':('inspection','LANES','PROC-LIFECYCLE-CONTROLS','P2-6',[],
 'Parse waves and all 52 slices, check unique membership, dependencies/write overlaps/lease serialization and dispatch cap; challenge missing-wave/over-cap synthetic records.',
 'Exactly one wave per planned slice and only stated dependency/resource/cap serialization; dynamic defects get current wave.',
 'Duplicate/unassigned slice, sixth implementer or undeclared overlap/serialization.'),
'MS-01':('inspection','LANES','CMD-MILESTONES-READBACK','P2-L01',['P2-L01'],
 'Read approval and planning merge receipt before create; compare gh milestone readback to approved table title/date/description and full UTC due time text.',
 'M1..M5 exact approved fields after approval, no duplicates or premature creation.',
 'Creation before approval or mismatched title/due day/criteria/slices.'),
'SCHED-01':('inspection','LANES','PROC-LIFECYCLE-CONTROLS','P2-6',[],
 'Inspect technical plan days-to-deadline statement, dated live windows and predecessor/lease timing; update execution receipt from current date without editing settled source; challenge missed-window case.',
 'All live-dependent work has preceding spike and explicit missed-window return; no concealed scope cuts.',
 'Live dependency scheduled after its window or cut represented as implicit approval.'),
'SUB-01':('demonstration','SUB','PROC-README-FRESH-SETUP','P2-D03',['P2-D03'],
 'Follow clean-checkout README with documented owner inputs; compare product, setup, access-retention, limitations and voice status to evidence.',
 'Fresh setup and judge-access route reproducible, limitations and voice status accurate.',
 'Undocumented dependency, missing judge-retention duty or unverified capability claim.'),
'SUB-02':('inspection','SUB','PROC-SUBMISSION-CHECK','P2-X12',['P2-D05','P2-X12'],
 'Sum storyboard shot durations, trace each source/UID to passing evidence and final APK manifest; check alert->Watch and panel coverage.',
 'At most 170 seconds with two required moments, honest source labels and support for every behavior claim.',
 'Overlength shot plan, unsupported claim, unlabeled replay/camera shot or clip from differing product candidate.'),
'SUB-03':('inspection','SUB','PROC-SUBMISSION-CHECK','P2-D04',['P2-D04'],
 'Read write-up and evidence; verify external primary citations at finalization, Fantasy View distinction and SD-036 external-context label; check OA-6 terms input.',
 'Implemented Fire TV/AWS claims grounded; external context clearly separated and cited.',
 'Future/context capability claimed implemented or unsupported provider comparison.'),
'DX-01':('inspection','DX','CMD-DX-PRESENCE','P2-SCR1',list(slices),
 'Inspect every dispatch and return for section, observation IDs/evidence or no-new-observation tools; check current TE packet/receipt as a matching example.',
 'Every packet/return has useful developer_feedback, including tools for zero-observation records.',
 'Missing/empty section or observation lacks evidence; no-new-observations lacks tool list.'),
'DX-02':('inspection','DX','PROC-SCRIBE-ASSEMBLY','P2-SCR1',['P2-SCR1'],
 'Cross-join packet/return tool inventory with observations and final feedback/friction files; inspect every required field and current official rules check.',
 'Complete sanitized per-tool feedback and Friction Log, optional requests use named priorities.',
 'Tool or required field omitted, fabricated observation or private data in feedback.'),
'SUB-04':('inspection','SUB','PROC-SUBMISSION-CHECK','P2-D05',['P2-D05'],
 'Enumerate OA-1..11 and exclusions owner actions; compare checklist due times and evidence of agent abstention for protected actions.',
 'All owner actions, accountable owner, due time and conditional/optional status recorded.',
 'Owner action omitted, assigned to unauthorized agent or due after required deadline.'),
'APK-01':('inspection','REVREC','CMD-REVERIFY-APK','P2-L05',['P2-L05'],
 'Bind P2-R5 candidate on main to final APK, signer, sha256 and Reverify claims; inspect draft tag target and, after OA-8, actual v1.0.0 tag identity.',
 'Same APK built from candidate, hash bound and all submitted binary claims grounded; tagged-main condition closes only after authorized tag exists.',
 'Different build/tag/installed artifact or unsupported/unverified APK claim presented as PASS.'),
}
risk_specs={
1:('inspection','SPIKES','CMD-VERDICT-CHECK','P2-X01',['P2-X01'],'Inspect X01 model/API/provider readiness and incompatible-target challenge against dispatch control.','Class C blocks dependent stick work on incompatible target; backend/docs continue.','Dependent device work runs after incompatible result or platform/device changes silently.'),
2:('demonstration','ALERTPATH','PROC-STICK-VCASE','P2-X02',['P2-X02'],'Observe heads-up over actual playback; if unsupported inspect verdict and blocked A03 entry, including no phone/foreground substitute.','Supported route evidenced or exact limitation/class C stop enforced before product dependence.','Missing supported route replaced with app-only/phone behavior and called equivalent.'),
3:('inspection','WATCH','CMD-REGISTRY-CHECK','P2-A04',['P2-X03','P2-B06','P2-A04'],'Compare failed/partial launch observation with registry, resolver and UI outcome; include denied/unknown/app-home cases.','Strongest actually observed outcome reported and missing interface recorded.','Weaker outcome is relabeled gameOpened.'),
4:('inspection','PANEL','CMD-VERDICT-CHECK','P2-A05',['P2-X04','P2-A05','P2-A04'],'Inspect failed/timeboxed composition verdict, fullScreen selection and PR-047/048 evidence, preserving PR-041 gap.','Fallback follows C5 and real-provider Watch remains available with honest limitation.','Fallback selects stand-in video or traps Watch.'),
5:('test','FEED','CMD-DEPLOYED-TESTS','P2-L03',['P2-X05','P2-B02'],'Execute outage and invalid-schema VCASE cases; compare all source labels/store hashes and inspect OA-6 terms handover.','Replay labels complete, invalid ingest makes no mutation, terms question handed over.','Substituted live label, partial store or omitted terms handover.'),
6:('inspection','LINEUP','CMD-VERDICT-CHECK','P2-X06',['P2-X06','P2-B03'],'At T_yahoo inspect approval disposition, X06 verdict and deployed active-source evidence after L03.','No approval yields explicit failed Yahoo route and one labeled manual source.','Approval absent but Yahoo route claimed verified or source switch creates mixed truth.'),
7:('inspection','BACKEND','PROC-LIFECYCLE-CONTROLS','P2-L03',['P2-B01','P2-L02','P2-L03'],'Inspect allowed service/template/account metadata and stopped paid-action records; challenge with synthetic paid-service proposal, never actual upgrade.','Paid boundary causes class F stop and no account/plan change.','Agent accepts paid action or eligibility is assumed without evidence.'),
8:('inspection','SPIKES','PROC-LIFECYCLE-CONTROLS','P2-X10',['P2-X03','P2-X05','P2-X09','P2-X10'],'Compare live-window attendance/event records with replay labels and next-window assignment; challenge no-event scenario.','Repeatable replay logic separated from still-pending live device/provider proof.','Missed live behavior closed with replay-only receipt.'),
9:('inspection','VISUAL','PROC-VISUAL-REVIEW','P2-X12',['P2-X04','P2-X09','P2-X12','P2-D05'],'Inspect black-frame case and selected OD-AFC-P2-02 branch; match companion capture, geometry and owner-camera source as applicable.','Evidence and demo use approved source policy, with remaining unobservable claims explicit.','Black frame or geometry alone is claimed to show actual video/game arrival.'),
10:('inspection','LANES','PROC-LIFECYCLE-CONTROLS','P2-6',list(slices),'Inspect dispatch binding and any fallback receipt for confirmed usage-limit evidence; challenge an authentication/runtime-error route switch.','Only approved ordered fallback after qualifying limit, capabilities retained, otherwise queue.','Route changed on mere runtime/auth error or coverage-assist/Reverify dropped.'),
11:('inspection','GATE','PROC-LAND','P2-G01',['P2-G01'],'Inspect S09 merged receipt, G01 merged prerequisite and exact-head gates before subsequent landing; simulate missing predecessor record.','Landing waits on missing gate prerequisite; local branch work can continue.','Slice lands without S09/G01 or treats local run as missing required hosted checks.'),
12:('test','GATE','CMD-GATE-HYGIENE','P2-SCR1',['P2-G01T','P2-G01','P2-D03','P2-D04','P2-D05','P2-SCR1'],'Run runtime-generated credential/path negative fixtures and scan repository plus sanitized export/capture inventory; inspect exposure response without reproducing values.','Leak blocks merge/publication; safe artifact reference and owner rotation notification if exposure occurred.','Secret/account/customer data or path reaches artifact, or matched secret printed in receipt.'),
13:('inspection','LANES','PROC-LIFECYCLE-CONTROLS','P2-6',[],'Compare expected milestone finish and due time; challenge a >12-hour slip and inspect scope-priority owner decision record.','Owner receives explicit scope-reduction choice; obligations remain until exact omission approved.','Cut applied after notification alone or lateness hidden.')
}

for req,row in locals_.items():
    isrisk=req.startswith('RISK-')
    key=int(req[-2:]) if isrisk else req.removeprefix('AC-AFC-P2-')
    method,des,command,closer,support,stim,pos,neg=(risk_specs[key] if isrisk else local_specs[key])
    evidence=str(P/f'evidence/{closer}/{req}/')
    if method=='demonstration': evidence=f'evidence/visual/{closer}/{req}/'
    fields={'slice':closer,'requirement_ref':str(P/'amazon-fantasy-companion-phase-2-technical-plan.md')+'#'+req,
            'requirement_gate_receipt':str(P/'specialists/re-p2-ac-receipt.md'),
            'register_independence':'Lifecycle-local criterion; does not replace product VCASE allocations.',
            'reverify':'Reverify: not applicable — this row inspects process/control or observed behavior, not an APK attribute'}
    if method=='test':
        prod='P2-B02' if isrisk and key==5 else 'P2-G01'
        fields.update(test_slice=prod+'T',product_slice=prod,red_expectation='CMD-RED: named behavioral assertion fails on baseline and same IDs/test hashes pass on product; import/build/tool failure never qualifies.',test_article='backend deployed ingest' if prod=='P2-B02' else 'tools/ci gate and hygiene',stimulus=stim,measured_response=pos,test_environment='afc-dev' if prod=='P2-B02' else 'host isolated fixtures',test_handoff='write-tests by allocated Test Implementer')
        fields.update(resource_fields(method,'AWS deployment' if prod=='P2-B02' else 'host',prod))
    elif method=='demonstration':
        fields.update(demonstration_scenario=stim,observed_behavior=pos,live_window_or_replay_basis='Real stick with sanitized fixture profile/indexed replay; live provider-only claims use TNF 2026-10-15, Sun 2026-10-18 or Mon 2026-10-19. README uses clean checkout and approved afc-dev.',evidence_path=evidence)
    else: fields.update(inspection_article=row[4],inspection_criteria=req+' entire statement in bound technical plan',inspection_record=evidence)
    if key in ('APK-01','REV-01'):
        fields.update(reverify='Applicable to APK attribute claims covered by this process; CMD-REVERIFY-APK required, typed capability gap remains until grounded.',apk_artifact='tv-app/app/build/outputs/apk/<variant>/<apk_name>.apk',reverify_invocation=commands['CMD-REVERIFY-APK']['command'])
    data['proof_cases'].append({'id':'SEIT-'+req.removeprefix('AC-'),'kind':'verification' if method!='demonstration' else 'validation',
       'requirement_id':req,'design_id':'DES-AFC-P2-'+des,'command_id':command,'method':method,
       'preconditions':['Bound technical plan and current accepted RE corrections; no requirement edit by TE.','Execution requires package approval, stated owner actions, exact candidate and PROC-PREPARE; P2-6 inspection itself remains planning only.'],
       'stimulus_or_procedure':stim+' Follow '+command+' procedure and retain item-by-item observations.',
       'expected_result':pos,'observable_evidence':evidence+' (sanitized item-by-item checklist, command output/exit, candidate and input digests)',
       'pass_fail_rule':'PASS iff all duties in '+req+' and expected observations hold. '+neg+' => FAIL. '+gap,
       'method_fields':fields,'negative_or_failure_case':neg,'boundary_test_layer':'Lifecycle control / '+row[4],
       'closing_slice':closer,'supporting_slices':support,'execution_status':'not_run (planning only)'})

for proof in data['proof_cases']:
    data['traceability_matrix'].append(dict(zip(data['traceability_matrix_columns'],[
        proof['id'],proof['requirement_id'],proof['design_id'],proof['boundary_test_layer'],
        proof['expected_result'],proof['negative_or_failure_case'],proof['command_id'],proof['observable_evidence']])))
slice_map={s:[] for s in slices}
planning_rows=[]
for proof in data['proof_cases']:
    for s in set(proof['supporting_slices']+[proof['closing_slice']]):
        if s in slice_map: slice_map[s].append(proof['id'])
    if proof['closing_slice']=='P2-6': planning_rows.append(proof['id'])
for s in slice_map: slice_map[s]=sorted(set(slice_map[s]))

data['frozen_profile_binding']={name:{'configuration_digest_sha256':f['configuration_digest_sha256'],
    'development_strategy':f['development_strategy'],'roles':f['snapshot']['roles'],
    'review':f['snapshot']['review'],'deterministic_verification':f['snapshot']['deterministic_verification']}
    for name,f in journey['profile_selection']['frozen_snapshots'].items()}
data['frozen_profile_binding_note']='Projection from parent control journey frozen_snapshots only. No live profiles imported. Current TE route is confirmed usage-limit fallback; preserving a snapshot does not authorize switching routes.'
data['environments_fixtures_data_simulations_support']={
 'host_tools':{'available':'python3 with jsonschema, python3.12, git, gh, node, OCR delegate CLI, reverify 0.11.0; availability alone is not a runtime PASS.',
               'missing_or_not_qualified':[{'tools':['Android SDK command-line tools','adb/platform-tools','apkanalyzer','apksigner/build-tools','JDK 17'], 'installer_slice':'P2-X01','first_consumers':['P2-X01','P2-A01T','P2-A01'],'scan_before_use':'CMD-SUPPLY-SCAN; JDK17 prerequisite explicitly added to installer inventory by TE-P2-F02'},
                {'tools':['Gradle wrapper and plugins','Android unit/instrumented test dependencies'],'installer_slice':'P2-A01','first_consumers':['P2-A01T','P2-A01'],'scan_before_use':'CMD-SUPPLY-SCAN; red entry must wait for build harness without implementing the tested behavior'},
                {'tools':['AWS SAM CLI','cfn-lint','pinned Python runtime/test dependencies'],'installer_slice':'P2-B01','first_consumers':['P2-B01T','P2-B01'],'scan_before_use':'CMD-SUPPLY-SCAN; test environment preparation may precede product behavior'},
                {'tools':['coverage/mutation tooling beyond existing gate'],'installer_slice':'not allocated','first_consumers':['gate-chain claims'],'status':'TOOL_UNALLOCATED: preserve typed gap; Orchestrator/Plan Integrator must allocate scans/config and exact commands before claiming them'}]},
 'device':{'identity':'Single real 2018 Fire TV stick running Fire OS, exact model/API read by X01 (SD-001)','lease':'fire-tv-stick','viewport':'Actual output resolution; floor demonstration at 1080p','qualification':'Record model/Fire OS/API, SDK/JDK/Gradle versions, APK commit/hash/cert; owner enables ADB and sessions. No hardware performance benchmarking.'},
 'aws':{'profile':'afc-dev','stack':'afc-dev','lease':'aws-afc-dev','entry':'OA-3; OA-10 for manual link; only Free-plan dev resources; no credentials read/printed; no production DB mutation','isolation':'Each test creates synthetic profile/event namespace; assert only owned data; cleanup only owned data; single deployment mutation at a time; no deploy during live game.'},
 'live_windows':[{'date':'2026-10-15','slices':['P2-X03 PR2','P2-X05 PR2'],'basis':'TNF; shared live-game-window allowed host capture + disjoint stick work'},
                 {'date':'2026-10-18','slices':['P2-X09'],'basis':'Sunday simultaneous games'},
                 {'date':'2026-10-19','slices':['P2-X10'],'basis':'MNF hardening'},
                 {'date':'2026-10-22','slices':['P2-X12'],'basis':'TNF final demo capture'}],
 'fixture_contract':'CONTRACT-AFC-P2-FIXTURE; backend/fixtures/replay/<game-id>/<seq>-<scoreboard|summary>.json plus index.json with UTC/endpoint/status/sha256; immutable raw captures, correction as later sequence.',
 'fixture_readiness':'Fixtures.v1 captured by X05 PR1 from completed games; replay-derived invalid variants generated only in isolated test state and never overwrite captures. Recorded Yahoo fixtures sanitized; no real secrets or credential-shaped literals in tracked fixtures.',
 'data_provenance':'Every replay-derived value stays labeled; frame/config/source identity retained. Local test doubles, if justified by write-tests, are diagnostic only and cannot close deployed/stick register cases.',
 'visual_evidence':'evidence/visual/<slice>/ with per-state PNG and sanitized geometry TXT; raw dumps and clips remain private until sanitized. Protected video black frames require RISK-09 branch evidence; geometry never proves content by itself.',
 'evidence_dirs':'<evidence_dir> is repository-relative '+str(P)+'/evidence/<slice>/<case-or-step>/ or evidence/visual/<slice>/; execution generation comes from dispatch record. Create before capture. Text evidence .txt (root ignores .log). <private_capture_dir> and <private_clip_path> are outside tracked material and must be sanitized before copying evidence.',
 'runtime_placeholders':'Bind every <placeholder> in dispatch to a verified existing path, test ID, SHA, URL or permitted value. Shell-quote each runtime value; secrets never appear in command arguments/logs. Unresolved placeholder => PROCEDURE_UNBOUND, not executable evidence.',
 'preparation':'PROC-PREPARE before costly execution; a failed preparation consumes no attempt. Required file type, transport/Git completeness, exact launcher, permissions and prerequisites all observed.',
 'cleanup':'Stop owned services gracefully before generic descendant cleanup. Preserve original failure vs subsequent recovery. Remove only attempt-owned temp resources.',
 'lease_order':'X01 -> X04 (continuous until verdict/deadline) -> A01 visual slot -> X02 -> X03 desk -> X07. Instrumented red/green and all visual runs lease same stick. Wave numbering does not bar early X04 needed to finish M1 A01 review.',
 'cost':'Estimates only, not hardware claims. Group by actual shared resource. Gate invokes costly suites only for relevant code/payload changes; docs-only changes use docs/spec/hygiene. Record slowest tests and gate-time delta on every engine-suite change.'}

claims={
 'red_then_green':{'claim_type':'red-then-green','status':'DECLARED','command_id':'CMD-RED','tool':'repository unittest/pytest/Gradle suites per pair','threshold':'Every mapped test ID fails by behavior assertion on baseline and passes on product candidate with unchanged test-file hashes; no collection/import/syntax/tool failure as red.','typed_gap':'Missing suite, unbound selector or no recorded red/green pair is NOT_RUN/PROCEDURE_UNBOUND, never PASS.'},
 'changed_line_coverage':{'claim_type':'changed-line coverage','status':'TYPED_GAP','tool':'Not selected/configured by current product gate; coverage.py + diff-cover for Python and an Android-compatible coverage exporter are candidates only, not installed or approved gate commands.','threshold':'Planning proposal: >=90% of executable changed lines; exclusions require named justification and do not remove acceptance cases.','typed_gap':'TOOL_UNALLOCATED until scanner, pins, report scope, target-repository command and owned write set are recorded. Existing unit/lint/assemble PASS never substitutes.'},
 'mutation':{'claim_type':'mutation','status':'TYPED_GAP','tool':'No mutation command/configuration in current gate; Python/Kotlin/shell backends not yet qualified.','threshold':'Planning proposal: >=70% killed/(killed+survived) non-equivalent mutants in changed executable behavior; all survivors reviewed, invalid/equivalent separate; no zero-denominator PASS.','typed_gap':'TOOL_UNALLOCATED until exact backend, runtime support, bounded target set and command are selected and scanned; absent/not_run remains gap.'}}
for lane,profile in [('backend','primary'),('tv-app-ui','frontend'),('defects','bug-triager')]:
    data['gate_declarations'][lane]={'profile':profile,'strategy':'tdd','assurance':{'enabled':True,'cadence':'lifecycle','candidate':'candidate.final at IE-P2-44','independence':'Fresh session rejects author ancestry; rerun claims, author receipts diagnostic.'},'claims':json.loads(json.dumps(claims)),
      'gate_commands':['CMD-GATE-BACKEND','CMD-GATE-HYGIENE','CMD-WORKFLOW-CHECK'] if lane=='backend' else ['CMD-GATE-TVAPP','CMD-TVAPP-INSTRUMENTED','PROC-VISUAL-REVIEW'] if lane=='tv-app-ui' else ['CMD-RED','PROC-BUG-TRIAGE','CMD-GATE-ALL'],
      'coverage_assist':{'enabled':True,'required':True,'backend':'ocr delegation','availability':'installed; runtime success still required'},
      'reverify':{'enabled':True,'backend':'reverify 0.11.0','availability':'installed; APK semantic grounding unproven','rule':'CMD-REVERIFY-APK for binary claims, reasoned N/A otherwise'}}
data['gate_declarations']['defects']['prevention']='Every bug packet names reproduced escape through requirement/test/model/plan/agent evidence, red-then-green regression, and a distinct prevention check. No nested triage from assigned TE.'
data['gate_declarations']['device-integration-spikes']={'profile':'heavyweight','strategy':'tdd for product code; evidence-only spikes conditional on OD-AFC-04',
 'assurance':{'enabled':True,'cadence':'lifecycle'},'evidence_gate':'CMD-VERDICT-CHECK against CONTRACT-AFC-P2-VERDICT, real target/provenance/timebox and typed route outcomes; WORKS never inferred from simulated endpoint.',
 'product_code_claims':json.loads(json.dumps(claims)),'investigation_disposition':'Red/coverage/mutation on throwaway evidence probes not applicable only after OD-AFC-04; any realized product behavior retains TDD and claims. No hardware benchmark.',
 'commands':['CMD-VERDICT-CHECK','CMD-FIXTURE-INDEX-CHECK','CMD-REGISTRY-CHECK','PROC-E2E-LIVE','PROC-VISUAL-REVIEW'],
 'coverage_assist':{'enabled':True,'required':True,'backend':'ocr delegation'},'reverify':{'enabled':True,'backend':'reverify','rule':'Applies to any built-APK attribute claim; runtime/demonstration rows alone reasoned N/A'}}
data['gate_declarations']['spec-and-docs']={'profile':'tech-writing','strategy':'single_implementer','assurance':{'enabled':False,'cadence':'disabled (snapshot records phase but enabled=false)'},
 'gate_commands':['CMD-GATE-DOCS','CMD-GATE-SPEC','CMD-GATE-HYGIENE','PROC-README-FRESH-SETUP','PROC-SUBMISSION-CHECK','PROC-SCRIBE-ASSEMBLY','CMD-CHANGELOG-CHECK'],
 'red_then_green':{'status':'NOT_APPLICABLE','reason':'Frozen single_implementer documentation lane; no new product behavior.'},
 'changed_line_coverage':{'status':'NOT_APPLICABLE','reason':'Docs/spec outputs have no executable product lines; moved executable work must retain its appropriate TDD lane and claims.'},
 'mutation':{'status':'NOT_APPLICABLE','reason':'Documentation inspection/reproducible build; no product test mutation.'},
 'coverage_assist':{'enabled':True,'required':True,'backend':'ocr delegation'},'reverify':{'enabled':True,'rule':'Reasoned N/A for docs; any APK claim delegates to exact applicable proof, never disabled by lane.'}}
data['gate_declarations']['policy']={'threshold_authority':'Thresholds are prospective TE proposals, approved only with integrated package. No benchmark or extra hardware proof introduced.',
 'runtime_gap_rule':gap,'cadence':'Lifecycle assurance is not replaced by per-slice author realization or Reviewer OCR. No automatic new review rounds.',
 'prospective_preparation_and_cost':'Every new/changed engine-backed suite uses PROC-PREPARE/PROC-RELIABILITY and records resource group/estimated and actual gate duration; on/off Ponytail must preserve identical proof coverage.'}

milestones=[]
for line in plan.splitlines():
    if re.match(r'^\| M[1-5] \|',line):
        c=[v.strip() for v in line.strip('|').split('|')]
        milestones.append(c)
for m in milestones:
    num=int(m[0][1:]); ss=[s for s,c in slices.items() if re.search(r'W'+str(num)+r'\b',c[2])]
    steps=[x['id'] for x in ie['steps'] if x['milestone']==m[0]]
    data['levels'].append({'milestone':m[0],'wave':num,'title':m[1],'due_utc':m[2],
        'entry_criteria_ref':str(P/'amazon-fantasy-companion-phase-2-technical-plan.md')+'#Milestones '+m[0]+' entry',
        'exit_criteria_ref':str(P/'amazon-fantasy-companion-phase-2-technical-plan.md')+'#Milestones '+m[0]+' exit',
        'levels':['unit','contract','integration','system/real stick','owner validation/inspection'],
        'slices':ss,'integration_steps':steps,
        'evidence_focus':{1:'Tool prerequisites, baseline device, TDD scaffold/gates and initial replay fixture inventory',2:'Route verdicts, deployed link/profile, contract and settings evidence',3:'Connected deployed backend/TV behavior and Sunday live system run',4:'Correction/starter/stale fault evidence, spec revision and all active cases disposition',5:'Immutable final APK/backend identity, submission/feedback inspection and fresh lifecycle assurance'}[num],
        'expected_gate_time_delta':{1:'Estimate +2 min host gate tests, +8 min Gradle unit/lint/assemble, +2 min Python unit/contract; first engine-suite qualification separately 7 runs; actual baseline not measured.',2:'Estimate +5 min deployed suite and +10 min stick suite per relevant candidate; engine qualification 7 runs where applicable. Live-window observation scheduled separately.',3:'Estimate three changed instrumented areas at +10 min each, serialized on stick; backend suite +5 min. Reuse same qualified run for review/landing only on identical inputs.',4:'No fixed increase assumed: rerun changed-suite qualification and record actual delta; replay functional checks <=5 min estimate, live MNF observation separate.',5:'Docs-only gate estimated <=2 min; final binary/deployed/assurance commands actual times recorded; no repeated full engine gate for evidence-only merge with unchanged trees.'}[num]})
for x in ie['steps']:
    row={'step':x['id'],'milestone':x['milestone'],'wave':int(x['milestone'][1:]),'order':x['order'],'after':x['after'],'slices':x['merges'],
         'entry_criteria':x['entry_criteria'],'post_step_vv':x['post_step_vv'],'rollback_ref':str(P/'specialists/integration-plan.md')+'#'+x['id'],
         'proof_rows':sorted({p for s in x['merges'] for p in slice_map[s]}),
         'command_ids':sorted(set(re.findall(r'\b(?:CMD|PROC)-[A-Z0-9-]+',json.dumps(x))))}
    row['note']='Projection of IE authority, not a new assembly decision. Command definitions here finalize invocation and gap rules. Any changed product/binary/input invalidates reused evidence.'
    data['integration_vv_sequence'].append(row)
data['integration_vv_sequence_note']='IE-P2-1..44 retained. X03/X05 intentionally appear in two steps for two-PR spikes. Named gates at milestones are not new assurance cadence boundaries. Step IDs/order are identifiers; obey dependencies and continuous X04 clock. Read TE-P2-F01..F09 before dispatch; correct source packet allocations through Orchestrator, not by silently executing outside write sets.'

data['interface_coverage']=[
 {'contract':'CONTRACT-AFC-P2-API','obligations':['identity/auth/foreign-profile authorization','operations and DTO mapping','64 KiB request/response limits','400/401/403/409/410/429/503','timeouts/retries and cancellation','owner-only confirmation and replay refusal'],
  'positive':'Valid authenticated same-profile operations with exact shapes and bounded retry; successful customer code action.',
  'negative':'Malformed/oversize body, wrong/absent/foreign session, duplicate/expired confirmation, unavailable route, no automatic retry on confirmation/Watch.',
  'rows':['SEIT-AFC-PR-038','SEIT-AFC-PR-055','SEIT-AFC-PR-058'],'test_slices':['P2-B01T','P2-A01T'],'runtime':'PROC-SYSTEM-VCASE / CMD-DEPLOYED-TESTS'},
 {'contract':'CONTRACT-AFC-P2-ENVELOPE','obligations':['schemaVersion/id/revision/source/eventTime/updatedAt','RFC3339 UTC timestamps','monotonic per-entity revision and idempotency'],
  'positive':'Newer correctly labeled revision updates both endpoints.', 'negative':'Older/invalid envelope rejected without partial update, retry retains identity; absent/misleading provenance fails.',
  'rows':['SEIT-AFC-PR-012','SEIT-AFC-PR-013','SEIT-AFC-PR-025','SEIT-AFC-PR-026','SEIT-AFC-PR-046','SEIT-AFC-PR-058'],'test_slices':['P2-B01T','P2-B02T','P2-B04T','P2-A01T','P2-A03T']},
 {'contract':'CONTRACT-AFC-P2-PROVIDER-REGISTRY','obligations':['documented package and URI/intent','supported placeholders only','actual outcome/verification time','local channel and preference'],
  'positive':'Documented route executes and reports observed destination.', 'negative':'Absent/unknown/denied/app-home, invented URI, unsupported placeholder and no carrying app never report gameOpened.',
  'rows':['SEIT-AFC-PR-029','SEIT-AFC-PR-030','SEIT-AFC-PR-031','SEIT-AFC-PR-032','SEIT-AFC-PR-033','SEIT-AFC-PR-034'],'test_slices':['P2-B06T','P2-A04T']},
 {'contract':'CONTRACT-AFC-P2-FIXTURE','obligations':['immutable raw capture','UTC/endpoint/status/hash metadata','correction sequence/provenance'],
  'positive':'Valid indexed captures accepted/replayed with source labels.', 'negative':'Missing/hash-mismatched/edited capture refused; invalid schema makes no store mutation.',
  'rows':['SEIT-AFC-PR-012','SEIT-AFC-PR-013','SEIT-AFC-PR-064'],'test_slices':['P2-B02T']},
 {'contract':'CONTRACT-AFC-P2-PRESETS','obligations':['exact two scoring tables/default','Yahoo distinct scoring','customer persistence'],
  'positive':'Every coefficient exercised, default and saved choice align.', 'negative':'Third preset, silent change, wrong coefficient or Yahoo override rejected.',
  'rows':['SEIT-AFC-PR-065','SEIT-AFC-PR-066'],'test_slices':['P2-B03T','P2-A02T']}]

data['cross_cutting_checks']=[
 {'id':'CC-PATH','command_id':'PROC-PATH-SCAN','rule':'Rule 12 shape scan of all intended files including plans and evidence, plus PR-056 root-anchored local paths; zero leaks, no matched private text output.'},
 {'id':'CC-SECRETS','command_id':'CMD-GATE-HYGIENE','rule':'Secrets/account/customer content scanned in repository, APK and visual/submission material; sensitive raw outputs stay private, metadata only; exposure => owner rotation notice.'},
 {'id':'CC-DX','command_id':'CMD-DX-PRESENCE','rule':'Every packet and return has developer_feedback observation IDs + evidence, or no new observations naming tools.'},
 {'id':'CC-OCR','command_id':'CMD-OCR-DELEGATE','rule':'OCR delegate in every Reviewer packet with per-file application; frozen enabled+required and exact tool errors preserved; never substitutes independent review.'},
 {'id':'CC-REVERIFY','command_id':'CMD-REVERIFY-APK','rule':'APK claims require exact artifact/claim run; all other proof cases carry reasoned Reverify: not applicable line; backend absence/unavailable/not_run remains typed gap.'},
 {'id':'CC-LAND','command_id':'PROC-LAND','rule':'No squash, force push or local-main commit; exact-head checks, configured independent review and bounded repair, preserved history.'},
 {'id':'CC-CHANGELOG','command_id':'CMD-CHANGELOG-CHECK','rule':'AC-AFC-P2-REL-01 per landed PR, correct [Unreleased] entry/link and release migration.'},
 {'id':'CC-VISUAL','command_id':'PROC-VISUAL-REVIEW','rule':'AC-AFC-P2-VIS-01 every changed UI state on actual stick before merge, screenshot evidence and focus/text criteria; no black-frame PASS.'},
 {'id':'CC-BUG','command_id':'PROC-BUG-TRIAGE','rule':'AC-AFC-P2-BUG-01 defects route via Orchestrator to bug-triager after safe classification; regression+prevention required.'},
 {'id':'CC-APPROVAL','command_id':'CMD-MILESTONES-READBACK','rule':'No milestone before integrated package approval; creating a plan, finding or draft is not owner acceptance. Public tag/release/submission stay OA actions.'},
 {'id':'CC-PREPARE','command_id':'PROC-PREPARE','rule':'Preparation failures consume no native/protected attempt and never count as runtime evidence.'},
 {'id':'CC-RELIABILITY','command_id':'PROC-RELIABILITY','rule':'New/changed engine-backed tests qualify five consecutive and one two-concurrent-copy run, named resource group and gate cost; identical coverage with Ponytail on/off.'},
 {'id':'CC-INTERFACE','command_id':'PROC-INTERFACE-PROFILE-CHECK','rule':'Positive and negative for every applicable interface field; defined GAP on missing timing/shape/owner/source, no silent N/A.'}]
data['evidence_and_pass_fail']={
 'evidence':'Every result binds exact candidate revision, method, VCASE/local row, fixture/input hashes, artifact digest, named environment, command/procedure, actual observation and exit/signal; no invented hook/receipt schema.',
 'passing':'All method-specific expected observations with both criteria in allocated environment. Expected negative must be observed as rejection/containment, not treated as test-suite failure. File existence or tool exit alone is insufficient where inspection is required.',
 'failure':'Observable deviation from stated criterion on prepared article. Preserve phase and safe child error. Reproduce/classify before product-bug attribution.',
 'typed_gaps':['TOOL_MISSING','TOOL_UNALLOCATED','PROCEDURE_UNBOUND','NOT_RUN','ENVIRONMENT_UNAVAILABLE','OWNER_EVIDENCE_PENDING','ROUTE_UNPROVEN','REVERIFY_CAPABILITY_GAP','EVIDENCE_MISSING'],
 'gap_policy':'A gap stays a gap even when owner accepts it as a residual risk; no passing binary/coverage/mutation substitute. No requirement silently removed because fallback works.',
 'red_green':'Bind baseline failing assertions and candidate passes over same named test IDs and unchanged test hashes; changes return to the red boundary.',
 'reuse':'Exact candidate and relevant input digests must match; changed contract/source/APK/fixture/tool invalidates qualification. Late docs-only merges require both product trees equal and updated docs check.',
 'final_identity':'candidate.final = P2-R5 merge on main; APK final sha256/cert, deployed backend tree, registry/fixture/contracts identities and complete step receipts. Public tag v1.0.0 absent before OA-8 is pending publication, not tagged PASS.',
 'limits':'No hardware benchmark or measured latency/RAM claim. Functional timing boundaries from register are retained. Live schedule is execution input rechecked at capture, not independently researched here.'}
data['anomaly_corrective_closure']={
 'classify':'Expected negative; preparation/harness/configuration/environment error; reproduced product defect; missing integration route; owner/protected boundary. Never report raw failure as product defect.',
 'correction_bound':'At most three evidence-driven planning correction rounds, each with new hypothesis and result. No independent review/assurance budget spent here.',
 'closure':'Orchestrator reconciles TE findings and returns relevant changed inputs for SEIT delta; runtime defects via bug-triager current round, regression+prevention before merge. No dispatch, issue mutation, commit or remote write by TE.',
 'spikes':'FAILS/PARTIAL/TIMEBOX is admissible truthful verdict, not a product requirement pass; C1/C5/C6/C8 control dependencies and owner stops.',
 'rollbacks':'Use IE step rollback under exact resource lease; do not execute data-clearing uninstall without applicable authorization/OA-10 relink. Preserve original failure and recovery outcomes separately.',
 'owner_decision_rule':'Existing OD/OA items remain for integrated review. Stop planning only if proof itself needs new material owner intent that source plan cannot answer; no such additional intent question introduced.'}

findings=[
 {'id':'TE-P2-F01','class':'coverage gap / test write-set allocation','severity':'dispatch prerequisite','affected_slices':['P2-B01T','P2-B02T','P2-B03T','P2-B04T','P2-B05T','P2-B06T','P2-B07T','P2-A02T'],
  'evidence':'Graph red slices list unit/contract paths; CMD-DEPLOYED-TESTS and register AWS/system environments require deployed suites. backend/tests/deployed and A02 system instrumented controls are not allocated to those authors.',
  'required_correction':'Orchestrator records routine write-set extension: B01T owns backend/tests/deployed/conftest.py and auth/API deployed cases; B02T feed/replay cases; B03T lineup/presets; B04T identity/dedup/corrections; B05T policy; B06T resolver; B07T panel. Use distinct deployed subdirectories per module, shared conftest serialized under backend-template. A02T additionally owns tv-app/app/src/androidTest/java/com/afc/companion/profile/ and detect/ for UI-to-backend cases. A03T/A04T/A05T already own relevant instrumented paths. Preserve selected routes and write-tests handoff; runtime selection must collect mapped VCASE IDs.',
  'resolution':'All proofs retained; Plan Integrator copies allocations before dispatch; no test code authored here.'},
 {'id':'TE-P2-F02','class':'environment/prerequisite inventory','severity':'dispatch prerequisite','evidence':'X01/A01 require JDK for Gradle, apkanalyzer/apksigner for APK inspection; current graph lists SDK/starter scan but no explicit JDK17 preparation. A01T red precedes full product scaffold.',
  'required_correction':'Add scanned JDK17/build-tools to X01 preparation; pin actual compatible tools. Ensure A01T receives a buildable empty harness without implementing tested behavior before valid red assertions; B01T likewise gets scanned Python deps. A01 configures the release variant to use the host debug signer unless OA-11 supplies a keystore, so Light slice L05 only executes the build. Missing harness is not CMD-RED. No installing in TE session.'},
 {'id':'TE-P2-F03','class':'typed deterministic claim gaps','severity':'assurance prerequisite','evidence':'Current gate definitions contain no changed-line coverage or mutation tools; installed reverify 0.11.0 lists no APK manifest claim kind.',
  'required_correction':'Keep TOOL_UNALLOCATED coverage/mutation declarations visible until tool/command/pin/write-set are allocated by Orchestrator. Execute CMD-REVERIFY-APK on exact APK; semantic/absence proof ungrounded => REVERIFY_CAPABILITY_GAP. Do not switch frozen backend or substitute ordinary ATE runs.'},
 {'id':'TE-P2-F04','class':'requirement precedence in test design','severity':'before affected implementation','evidence':'PR-014 verification says inside the 20-yard line; proposed glossary red_zone_yards says at or inside 20. PR-025 says at most one alert per resolved event; design MATCH alert key includes alert type.',
  'required_correction':'B05T exercises 19/20/21 yards using register inside-20 criterion; B04T/B05T exercise one event matching multiple types and assert one alert total. P&D reconciles implementation design with existing requirements; no new owner threshold inferred and no requirement edits by TE.'},
 {'id':'TE-P2-F05','class':'proof vs conditional fallback','severity':'visible residual risk','evidence':'PR-001/010/015/030/041 primary route demonstrations/tests can remain unproven after permitted manual/unsupported/honest-outcome/fullScreen alternatives.',
  'required_correction':'Retain each row and its exact evidence disposition; fallback proof closes only its own criteria. Owner-accepted typed gap is distinct from PASS. PR-022/036 conditional no-offer branch follows OD-AFC-03; do not claim enabled-voice demonstration when not run.'},
 {'id':'TE-P2-F06','class':'integration packet reconciliation','severity':'before relevant dispatch','evidence':'Graph still says Test Implementer arrows merged; design TDD pairs says red tests uncommitted until Product Implementer. D02 waits only X02..X04 despite local SPEC-01 covering all landed spike verdicts. IE cutoffs permit shortened X03 scope after owner notice and earlier APK clips, contrary to explicit scope/final-candidate constraints.',
  'required_correction':'Use red receipt completion as TDD entry, not a separate red-only merge. D02 must incorporate every landed required verdict through its freeze and X11 when run; order it accordingly or perform bounded later delta in same scope. Never reduce provider trials on notice alone; request exact omitted-topic decision. X12 final-APK claims require final APK; earlier clips need honest claim restriction and explicit owner scope decision if requirement cannot be met. No IE artifact edited here.'},
 {'id':'TE-P2-F07','class':'prospective resource/cost obligation','severity':'before engine-suite review','evidence':'Current method requires preparation, five sequential plus two-copy qualification, named lock/resource group and gate-time delta; existing IE projection has no wave-cost field.',
  'required_correction':'Plan Integrator carries levels.expected_gate_time_delta into integration plan/packets and case resource groups into test dispatch; implement real cross-process fire-tv-stick lock for concurrent-copy qualification, unique owned state and cleanup. Estimates are not measurements or hardware benchmarks.'},
 {'id':'TE-P2-F08','class':'baseline metadata preservation','severity':'non-blocking planning metadata','evidence':'Parent journey decision records SD-035/036/037/038 and APPROVAL-ST5 have no status field; S8 ledger absent; BRAN unavailable.',
  'required_correction':'decision_baseline preserves not_recorded rather than fabricating source status; Orchestrator may normalize from existing owner-attributed records. Q10 restore remains excluded. No host binding or new acceptance inferred.'},
 {'id':'TE-P2-F09','class':'command finalization and publication boundary','severity':'packet correction','evidence':'Root ./gradlew does not match tv-app/gradlew layout; GET /v1/link is underspecified until B01 OpenAPI; APK tagged-main condition depends on OA-8 after build.',
  'required_correction':'Use ./tv-app/gradlew -p tv-app throughout. CMD-JUDGE-ACCESS tests actual OpenAPI authentication/polling contract, not assumed GET success. P2-L05 build identity can pass prepublication but tagged-main subcriterion remains OWNER_EVIDENCE_PENDING until OA-8 tag readback. No tag/release created by TE.'}
]
data['planning_findings_for_plan_integrator']={'findings':findings,
 'command_ids_renamed':[],
 'command_finalizations':['All graph/IE command IDs retained; future capture selector placeholders explicitly PROCEDURE_UNBOUND until bound.','CMD-RED expanded to Phase2 suites; red exit kept nonzero and behavioral.','CMD-APK-BUILD-* and instrumented commands use correct repository-relative wrapper.','CMD-ADB-GEOMETRY writes raw output privately before sanitization.','No invented SAM/pytest/plugin options; prospective tests and claim-file paths bound at dispatch.'],
 'slices_lacking_proof':[],
 'slices_with_unallocated_executable_evidence':findings[0]['affected_slices'],
 'cases_needing_owner_decision':[
  {'decision':'OD-AFC-02','rows':['SEIT-AFC-PR-023'],'rule':'Template-only recommendation remains pending integrated approval.'},
  {'decision':'OD-AFC-03','rows':['SEIT-AFC-PR-022','SEIT-AFC-PR-036','SEIT-AFC-P2-SPIKE-01'],'rule':'Conditional stretch/no-offer branch; both prospectively specified.'},
  {'decision':'OD-AFC-04','rows':['SEIT-AFC-P2-SPIKE-01'],'rule':'Evidence-only spikes recommendation, product code retains TDD.'},
  {'decision':'OD-AFC-05','rows':['SEIT-AFC-PR-017','SEIT-AFC-PR-020','SEIT-AFC-PR-038','SEIT-AFC-PR-062','SEIT-AFC-P2-SPEC-01'],'rule':'Proposed constants effective only when approved; no weakening registered boundaries.'},
  {'decision':'OA-AFC-A1','rows':['SEIT-AFC-P2-VIS-01'],'rule':'Frontend skill binding; preserve frozen frontend route.'},
  {'decision':'OD-AFC-P2-01','rows':['SEIT-AFC-P2-LAND-01','SEIT-AFC-P2-REV-01'],'rule':'Configured per-PR boundary requires integrated decision, not TE assumption.'},
  {'decision':'OD-AFC-P2-02','rows':['SEIT-AFC-PR-041','SEIT-RISK-AFC-P2-09','SEIT-AFC-P2-SUB-02'],'rule':'A/B capture policy; insufficient content evidence remains a gap.'},
  {'decision':'OD-AFC-P2-03','rows':['SEIT-AFC-P2-REL-02','SEIT-AFC-P2-APK-01'],'rule':'Version table approval; publication separate OA-8.'},
  {'decision':'OD-AFC-P2-04','rows':['SEIT-AFC-P2-SUB-01','SEIT-AFC-P2-SUB-04'],'rule':'Visibility/README access timing; OA-5 owner action.'},
  {'decision':'OD-AFC-P2-05','rows':['SEIT-AFC-P2-SPEC-01','SEIT-AFC-PR-047','SEIT-AFC-PR-066'],'rule':'Approve design/model alignment already recorded; no new scope here.'}],
 'owner_observation_pending':['AFC-PR-045 couch legibility','OA-1..11 as applicable, including tag/publication subcriterion of AC-AFC-P2-APK-01'],
 'slice_proof_map':slice_map,'planning_control_proof_rows':planning_rows,
 'integration_step_proof_policy':'For steps without a slice, apply step commands and affected proof cases by method/identity. IE-P2-44 evaluates all 100 rows without treating tech-writing as enabled ATE assurance.',
 'handoff':'Return to Orchestrator. Do not dispatch Plan Integrator or alter RE/IE artifacts. Bounded implementation prerequisites are routine reconciliation, not new owner-intent questions.'}

# Link commands after all rows/steps exist; every declared command has a known consumer.
for sid,c in slices.items():
    for id in re.findall(r'\b(?:CMD|PROC)-[A-Z0-9-]+',c[9]):
        if id in commands: commands[id]['used_by'].append(sid)
for step in data['integration_vv_sequence']:
    for id in step['command_ids']:
        if id in commands: commands[id]['used_by'].append(step['step'])
for proof in data['proof_cases']:
    commands[proof['command_id']]['used_by'].append(proof['id'])
for check in data['cross_cutting_checks']:
    commands[check['command_id']]['used_by'].append(check['id'])
for id,c in commands.items():
    if not c['used_by']: c['used_by']=['applicable Phase 2 dispatches and IE-P2-44']
    c['used_by']=sorted(set(c['used_by']))
    c['execution_status']='not_run (prospective procedure; help/preparation inspection is not execution)'
data['procedures_and_commands']=list(commands.values())
data['required_commands']=['CMD-GATE-ALL','CMD-GATE-SPEC','CMD-GATE-DOCS','CMD-GATE-HYGIENE','CMD-GATE-TVAPP','CMD-GATE-BACKEND','CMD-RED','CMD-WORKFLOW-CHECK','CMD-OCR-DELEGATE','CMD-DX-PRESENCE','CMD-REVERIFY-APK','CMD-PR-CHECKS','CMD-CHANGELOG-CHECK','CMD-DEPLOYED-TESTS','CMD-TVAPP-INSTRUMENTED','CMD-CONTRACT-FROZEN','CMD-TREE-EQUAL','PROC-PATH-SCAN','PROC-PREPARE','PROC-RELIABILITY','PROC-INTERFACE-PROFILE-CHECK']
data['required_command_scopes']={'rule':'This is a registry of required verification capabilities, not a shell batch. Execute only applicable row/step commands after preparation. Mutating build/install/deploy/milestone/release/landing procedures are owned by named slices and must never be blindly replayed by assurance.',
 'per_candidate':'Path-selected gate + hygiene, developer feedback, independent Reviewer OCR and exact-head check; Reverify only for actual APK claims.',
 'per_tdd_pair':'CMD-RED then corresponding product green; no requirement to rerun every unrelated test for a docs-only edit.',
 'lifecycle_assurance':'Independently rerun applicable deterministic gate-chain, deployed/system evidence and binary claims at IE-P2-44 on stable candidate. Inspect owner-action/landing evidence; do not recreate milestones or publish releases.',
 'tech_writing':'Docs/spec/hygiene and named PROC inspection; assurance remains disabled in frozen profile.'}
data['system_description_and_requirements_flowdown']['counts']={'requirement_rows':len(active)+len(locals_),'active_register_uids':len(active),'lifecycle_acceptance_rows':24,'risk_rows':13,'proof_rows':len(data['proof_cases']),'commands':len(commands)}
data['system_description_and_requirements_flowdown']['slice_proof_map']=slice_map
data['source_topic_inventory']={'approved_verification_sections':[
 {'path':str(p),'verification_cases':['VCASE-'+u for u in sorted(set(re.findall(r'AFC-PR-\d{3}',p.read_text())))]}
 for p in sorted(Path('spec/amazon-fantasy-companion').glob('07.1.*-verification.md'))],
 'register_topics':['profile/access','lineup/scoring','monitoring/consent','feed integrity/replay','alert relevance','policy timing','presentation/conditional voice','provider handoff','routing controls/linking','panel content/remote/legibility','panel consistency/modes','fullScreen handoff','platform/protection','scope/backend boundaries','TV bounded resources/thread placement'],
 'local_deliverables':['spike verdicts/registry/fixtures','repository gates/Vnv','review/assurance/landing','changelog/releases','program/waves/milestones','README/setup/judge access','write-up/demo/checklist','developer feedback','final APK identity'],
 'disposition':'All active items map to proof; 049..051 retired; no topic narrowed; future direction is guidance/context in SUB-03, not new product requirement.'}
for proof in data['proof_cases']:
    if proof['method']=='test' and proof['method_fields'].get('test_environment')=='host isolated fixtures':
        proof['method_fields'].update(resource_group='host-gate-fixtures; unique temporary repository/root per test',expected_gate_time='Planning estimate 2 min per suite; no engine started by default. If new test starts engine/server/driver/browser, apply 7-execution qualification and record actual delta.',qualification='PROC-PREPARE; PROC-RELIABILITY only when the actual test starts a covered runtime')
    pairs=sorted({s.removesuffix('T') for s in proof['supporting_slices'] if s.endswith('T') and s.removesuffix('T') in slices})
    if pairs:
        proof['method_fields']['tdd_supporting_pairs']=[{'test_slice':s+'T','product_slice':s,'red_expectation':'CMD-RED behavioral assertions then same test IDs and hashes green; does not replace this row registered method/environment.'} for s in pairs]
    if proof['requirement_id']=='AC-AFC-P2-SPIKE-01':
        proof['method_fields']['aggregate_closure']='P2-X07 closes required initial verdict inventory only after X01..X07 all landed; if X11 runs, its verdict is added before aggregate M4 closure. An open applicable spike cannot be hidden by an earlier closing_slice label.'
    if proof['requirement_id'] in ('AC-AFC-P2-LAND-01','AC-AFC-P2-REL-01','AC-AFC-P2-REV-01','AC-AFC-P2-DX-01'):
        proof['method_fields']['aggregate_closure']='Per-slice control applies through the final evidence-only PRs and handoff; the named closing slice provides the main milestone receipt, while IE-P2-44 checks the complete inventory. No early aggregate PASS.'

assert len(commands)<=128
(P/'seit.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print(f'WRITE seit.json: {len(data["proof_cases"])} proof cases; {len(commands)} commands; {len(slice_map)} slices; {len(ie["steps"])} integration steps')
