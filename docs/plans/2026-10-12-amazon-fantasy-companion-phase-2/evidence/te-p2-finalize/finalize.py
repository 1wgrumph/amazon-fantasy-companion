"""Apply the owning TE's bounded source/command finalization to its before snapshot."""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

P=Path('docs/plans/2026-10-12-amazon-fantasy-companion-phase-2')
E=P/'evidence/te-p2-finalize'
before=json.loads((E/'seit.before.json').read_text())
d=copy.deepcopy(before)
impl=json.loads((P/'implementation.json').read_text())
ie=json.loads(re.search(r'```json integration_plan\n(.*?)\n```',(P/'specialists/integration-plan.md').read_text(),re.S)[1])
closure=json.loads((P/'evidence/P2-6/codex-lead/exact-source-closure.json').read_text())
svg=json.loads((P/'evidence/svg-prolog/receipt.json').read_text())
authority=json.loads((P/'authority.json').read_text())
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pc={x['requirement_id']:x for x in d['proof_cases']}
cmd={x['id']:x for x in d['procedures_and_commands']}
pf=d['planning_findings_for_plan_integrator']
hold='Planning/tracking approval may authorize P2-L01 only after explicit approval and planning PR landing. Product/backend/spike/deployment and submission execution remain held until a subsequent owner execution instruction. Publication/public export requires separate exact-surface/history authority.'

d['artifact'].update(status='planning-finalized-for-PI-refresh',receipt=str(P/'specialists/te-p2-finalize-receipt.md'),finalized_at='2026-10-13',
 note='Owning Planning Test Engineer finalization after Plan Integrator and IE correction2; same frozen Codex CLI / GPT-6 Astra / xhigh route. No independent review/assurance or budget reset. Historical receipts remain historical; '+hold)
d['source_baseline'].update(revision=head,branch=branch,approved_authority_ref='authority.json#/baseline and authority.json#/requirement_register; approved spec authority remains DEC-AFC-APPROVAL-ST5 by reference, distinct from current checkout HEAD.')
transitions=[]
for item in d['source_baseline']['planning_inputs']:
    old=item['sha256'];item['sha256']=sha(Path(item['path']));item['binding_status']='bound'
    transitions.append({'path':item['path'],'before':old,'after':item['sha256'],'changed':old!=item['sha256']})
d['source_transition_evidence']={'prior_receipt':str(P/'specialists/te-p2-codex-receipt.md'),
 'pi_mechanical_rebind':str(P/'specialists/pi-p2-codex-receipt.md'),
 'root_closure_ref':str(P/'evidence/P2-6/codex-lead/exact-source-closure.json'),'root_transitions':closure['input_transitions'],
 'svg_receipt_ref':str(P/'evidence/svg-prolog/receipt.json'),'svg_transitions':svg['files'],
 'sysml_hashes':svg['sysml_model_hashes'],'planning_input_transitions':transitions,
 'previous_seit_sha256':sha(E/'seit.before.json'),'current_ie_sha256':sha(P/'specialists/integration-plan.md'),
 'interpretation':'PI rebound two source hashes only. This owning-role pass renews semantic/projection binding. SVG transformation is exact XML declaration removal, no model semantic change. No whole-journey digest.'}
d['source_transition_evidence']['current_authority_binding']={
 'path':str(P/'authority.json'),'sha256':sha(P/'authority.json'),
 'historical_closure_after':closure['input_transitions']['authority.json']['after'],
 'status':'CURRENT_SOURCE_BOUND_WITH_HISTORICAL_HASH_MISMATCH' if sha(P/'authority.json')!=closure['input_transitions']['authority.json']['after'] else 'HISTORICAL_CLOSURE_MATCH',
 'state':authority['state'],'effective':authority['effective'],'current_task_scope':authority['current_task_scope'],
 'license_path_allocated':'LICENSE' in authority['allowed']['paths'],
 'disposition':'Current authority was supplied as an input and has remained unchanged since TE finalization began. Its explicit hold and settled LICENSE preparation agree with the invoking packet. Preserve old closure hash as historical; do not claim unseen intervening bytes or mutate the authority. Parent may append its source-transition receipt before final freeze.'}
d['responsibility_and_change_authority'].update(
 planning_test_engineer='Owning-role finalization only: seit.json, specialists/te-p2-finalize-receipt.md and evidence/te-p2-finalize/**. No historical validator or receipt edit.',
 current_task_boundary=hold,
 owner='OA-5 controls exact public content/history and visibility, not merely scan results. Apache-2.0 is settled; D03 prepares LICENSE as agent work under subsequent execution authority. Other OA actions and credential/release/submission boundaries remain owner-only.',
 orchestrator='P&D lead under DEC-AFC-SD-039 receives this return, has PI mechanically refresh/render, then runs the one independent planning review. TE does not dispatch roles.')
d['decision_baseline']['current_lead_authority']={'id':'DEC-AFC-SD-039','source':'invoking finalization packet and authority.json#/current_task_scope','scope':hold,'note':'Explicit current authority by reference; existing parent decision statuses unchanged.'}
d['current_task_scope']=copy.deepcopy(authority['current_task_scope'])
d['required_command_scopes']['current_task_hold']=hold
d['evidence_and_pass_fail']['execution_authority']=hold
d['anomaly_corrective_closure']['closure']='Parent reconciles final mechanical PI instructions, refreshes candidate/render and then starts the one independent planning review. This author finalization consumes no review/assurance round. Runtime work is held; '+hold

# Preserve all original proof IDs/methods/negatives; add explicit owning-role dispositions.
pc['RISK-AFC-P2-09']['supporting_slices']=sorted(set(pc['RISK-AFC-P2-09']['supporting_slices']+['P2-A05']))
for sm in [pf['slice_proof_map'],d['system_description_and_requirements_flowdown']['slice_proof_map']]:
    sm['P2-A05']=sorted(set(sm['P2-A05']+['SEIT-RISK-AFC-P2-09']))
pc['RISK-AFC-P2-09']['method_fields']['allocation_disposition']='PI-P2-F01 resolved: A05 directly owns protected-video visual evidence for its UI change; X04/X09/X12/D05 evidence supports but never replaces A05 before-merge inspection.'
for n in [14,25]:
    q=pc[f'AFC-PR-{n:03}'];q['method_fields']['current_design_alignment']='Current design matches registered strict <20 (19/20/21 controls) and one alert per (profile,event), including multiple matching types; original positive/negative cases unchanged.'
pc['AFC-PR-014']['stimulus_or_procedure']=pc['AFC-PR-014']['stimulus_or_procedure'].replace('Register inside-20 criterion controls over inconsistent glossary wording.','Current glossary/design now use the registered strictly-inside-20 criterion.')
pc['AFC-PR-014']['method_fields']['stimulus']=pc['AFC-PR-014']['method_fields']['stimulus'].replace('Register inside-20 criterion controls over inconsistent glossary wording.','Current glossary/design now use the registered strictly-inside-20 criterion.')
for req in ['AFC-PR-030','AFC-PR-031','AFC-PR-032','AFC-PR-033','RISK-AFC-P2-03']:
    pc[req]['method_fields']['current_attempt_observation']={
      'positive':'Use a documented supported response for this attempt and correlate attempt ID, requested game/channel, observed destination and one reported outcome.',
      'negative':'Historical registry gameOpened plus successful launch call but unconfirmed current destination/playback => accessUnknown with reason. No invented callback, seventh enum or inferred current success.',
      'evidence':'P2-A04T current-attempt negative assertions; P2-A04 actual route observations; P2-X03 supported observation-mechanism record. Primary game-arrival obligation remains open without real proof.'}
cmd['CMD-REGISTRY-CHECK']['procedure_steps'].append('Separate historical verified_outcome from this launch. With old gameOpened and no supported current confirmation, require accessUnknown plus reason; record observation mechanism or explicitly none. Six-value enum unchanged.')
for x in d['interface_coverage']:
    if x['contract']=='CONTRACT-AFC-P2-PROVIDER-REGISTRY':
        x['obligations'].append('historical spike outcome vs supported current-attempt confirmation')
        x['negative']+=' Historical gameOpened with unconfirmed current attempt reports accessUnknown with reason; no invented callback.'

allocations={
 'P2-B01T':['backend/tests/deployed/conftest.py','backend/tests/deployed/device_auth/','backend/tests/deployed/api/'],
 'P2-B02T':['backend/tests/deployed/feed_ingest/'],'P2-B03T':['backend/tests/deployed/lineup/'],
 'P2-B04T':['backend/tests/deployed/matcher/'],'P2-B05T':['backend/tests/deployed/alert_policy/'],
 'P2-B06T':['backend/tests/deployed/provider_resolver/'],'P2-B07T':['backend/tests/deployed/panel/'],
 'P2-A02T':['tv-app/app/src/androidTest/java/com/afc/companion/profile/','tv-app/app/src/androidTest/java/com/afc/companion/detect/']}
d['planned_evidence_ownership']={'status':'ALLOCATED_NOT_EXECUTED','source':'specialists/slice-graph.md current write sets and technical plan lease table',
 'deployed_and_instrumented_paths':allocations,'shared_conftest':{'owner':'P2-B01T','path':'backend/tests/deployed/conftest.py','lease':'backend-template','rule':'Other test slices own distinct directories; shared conftest edits require serialized lease.'},
 'bootstrap':{'tv':'X01 qualifies scanned JDK17/SDK/platform/build-tools/Gradle/starter before A01T. A01T holds manifest/Gradle leases for empty build/test/interface scaffolding only; no tested feature behavior.',
 'backend':'B01T owns test deps/pyproject/API interface bootstrap and conftest under backend-template. Empty scaffold is not valid red; named behavioral assertions must collect and fail. Freeze test and bootstrap hashes before Product Implementer handoff.',
 'signing':'A01 configures release variant with same-host debug signer absent OA-11. L05 executes existing configuration only; never edits product build configuration.'},
 'boundary':'Allocation closes F01/F02 planning ownership only. No tool installed, product test written or qualified run claimed.'}
cmd['CMD-DEPLOYED-TESTS']['description']='Deployed test paths now allocated to B01T..B07T with shared conftest lease; execution remains prospective. System cases also require the real TV endpoint via PROC-SYSTEM-VCASE.'
cmd['CMD-DEPLOYED-SMOKE']['description']='Deployed device-auth/API cases and conftest now allocated to B01T; tests remain not_run. Profile and ApiUrl use documented non-printing fixture setup, not invented CLI flags.'
cmd['PROC-SYSTEM-VCASE']['description']='System settings/TV cases have deployed module owners and A02T instrumented profile/detect paths; current graph and planned_evidence_ownership close allocation only, not runtime proof.'
env=d['environments_fixtures_data_simulations_support']
env['host_tools']['missing_or_not_qualified'][-1]={'tools':['coverage.py','diff-cover','mutmut','JaCoCo via Android Gradle plugin','Android PIT fork candidate'],
 'installer_slice':'P2-G01 qualification/binding with P2-B01 Python pins and P2-A01 Android configuration',
 'first_consumers':['P2-G01T','P2-G01','P2-B01T','P2-B01','P2-A01T','P2-A01'],
 'status':'ALLOCATED_QUALIFICATION_PENDING; compatibility gaps named in gate_tool_plan. Pins, scan receipts, positive/negative controls required before use. Product execution hold applies.'}
env['host_tools']['missing_or_not_qualified'][0]['scan_before_use']='X01 current scope explicitly includes qualified JDK17, SDK/platform/build-tools, apkanalyzer/apksigner and actual compatible pins/scans before A01T.'
env['host_tools']['missing_or_not_qualified'][1]['installer_slice']='P2-X01 tool qualification, P2-A01T empty harness, P2-A01 completed build/report tasks'
env['host_tools']['missing_or_not_qualified'][2]['installer_slice']='P2-B01T test deps/bootstrap, P2-B01 complete pinned Python/SAM environment'

sources=[
 {'id':'TOOL-COVERAGE-RUN','url':'https://coverage.readthedocs.io/en/latest/commands/cmd_run.html','support':'coverage run supports module execution, data-file and configured source scope; record admitted version before use.'},
 {'id':'TOOL-COVERAGE-XML','url':'https://coverage.readthedocs.io/en/latest/commands/cmd_xml.html','support':'coverage xml emits Cobertura-compatible XML; explicit output and data-file options; qualify path mapping.'},
 {'id':'TOOL-DIFF-COVER','url':'https://github.com/Bachmann1234/diff_cover/blob/main/README.rst','support':'Accepts Cobertura/JaCoCo XML, explicit diff file, fail-under and JaCoCo source roots; missing report lines need separate completeness check.'},
 {'id':'TOOL-ANDROID-COVERAGE','url':'https://developer.android.com/studio/test/coverage-report','support':'AGP coverage enablement and variant-specific reports documented; exact pinned AGP tasks and output require qualification.'},
 {'id':'TOOL-GRADLE-JACOCO','url':'https://docs.gradle.org/current/userguide/jacoco_plugin.html','support':'JacocoReport supports XML and explicit task dependency/data/class/source configuration. Java automatic task wiring is not an Android guarantee.'},
 {'id':'TOOL-MUTMUT','url':'https://mutmut.readthedocs.io/en/latest/','support':'mutmut run and export-cicd-stats documented; bounded source_paths/test selection in config. Requires fork; 3+ focuses function mutation, not arbitrary module-level code.'},
 {'id':'TOOL-PIT-ANDROID-LIMIT','url':'https://github.com/szpak/gradle-pitest-plugin/blob/master/README.md#can-i-use-gradle-pitest-plugin-with-my-android-application','support':'Ordinary Java plugin explicitly does not directly support Android; not selected for AFC.'},
 {'id':'TOOL-PIT-ANDROID-FORK','url':'https://github.com/koral--/gradle-pitest-plugin','support':'Experimental Android fork pl.droidsonroids.pitest documents pitest<Variant> tasks and per-variant reports; compatibility with AFC pinned AGP/Kotlin/JDK remains unproven.'}]
d['gate_tool_primary_sources']={'checked_at':'2026-10-13','sources':sources,'admission':'Documentation only, no package acquired/installed. Current docs establish command/report design, not compatibility or admission of a version.'}

def add(id,command,description,pass_rule,owners,steps,**extra):
    c={'id':id,'command':command,'description':description,'pass':pass_rule,'used_by':owners,'procedure_steps':steps,'execution_status':'not_run; prospective repo-owned command assigned to named slices'}
    c.update(extra);d['procedures_and_commands'].append(c);cmd[id]=c

complete='Missing tool/report, stale candidate, zero-test or zero-mutation denominator, unmapped changed executable source, unsupported runtime, qualification failure or not_run is a typed gap/nonzero, never unit-test substitute or PASS.'
coverage_steps=[
 'G01 implements the repo wrapper and report completeness/threshold evaluator; G01T qualifies positive and failing controls. Never count unchanged aggregate coverage as changed-line evidence.',
 'Run at exact candidate from repository root; create bounded diff from recorded base to candidate restricted to the target handwritten source. XML paths must resolve to that exact tree.',
 'Inventory every changed executable file/line before score. Missing file/line mapping is REPORT_INCOMPLETE, not a 100% empty diff. Document genuinely non-executable/generated exclusions with evidence.',
 'Require >=90% covered changed executable lines; threshold is a TE proposal pending integrated approval. Preserve all mandatory VCASEs independent of percentage.'
]
add('CMD-COVERAGE-BACKEND','bash tools/ci/coverage/backend.sh <base_sha> <evidence_dir>',
 'Prospective G01-owned wrapper; B01T/B01 own Python 3.12 dependency pins and scope configuration.',
 'Cobertura XML plus nonempty correctly mapped diff-cover result meets >=90% changed-line threshold. '+complete,
 ['P2-G01T','P2-G01','P2-B01T','P2-B01','backend gate-chain'],coverage_steps,
 native_commands=[
 'python3.12 -m coverage run --rcfile=tools/ci/coverage/backend.coveragerc --data-file=<evidence_dir>/.coverage -m pytest backend/tests/unit backend/tests/contract',
 'python3.12 -m coverage xml --rcfile=tools/ci/coverage/backend.coveragerc --data-file=<evidence_dir>/.coverage -o <evidence_dir>/coverage.xml',
 'git diff <base_sha> HEAD -- backend/src > <evidence_dir>/changed.diff',
 'diff-cover <evidence_dir>/coverage.xml --diff-file=<evidence_dir>/changed.diff --fail-under=90'],
 report_formats=['Cobertura XML','diff-cover text','repo-owned changed-line inventory and pass/fail JSON'],
 readiness='PYTHON_COVERAGE_QUALIFICATION_PENDING; exact pins/scans/paths and missing-file negative control owned by G01T/G01 with B01 deps')
add('CMD-COVERAGE-TVAPP','bash tools/ci/coverage/tvapp.sh <base_sha> <evidence_dir>',
 'Prospective G01-owned comparator wrapper; A01T/A01 own AGP/JaCoCo enablement and afcCoverageReport task in existing app module.',
 'JaCoCo XML represents exact candidate handwritten Kotlin/Java and required selected suite data; changed-line result >=90%. '+complete,
 ['P2-G01T','P2-G01','P2-A01T','P2-A01','tv-app-ui gate-chain'],coverage_steps+[
 'A01 binds a repo-owned JacocoReport task named :app:afcCoverageReport to actual pinned debug variant class/source/execution data with XML enabled; it is prospective custom task, not an assumed standard Android task.',
 'Qualified same-candidate instrumentation data may be included under stick lock if needed; local unit report never stands in for an unexercised on-device VCASE. Missing Android/Compose/Kotlin mapping stays capability gap.',
 'Do not create another application module or enable weakened Android behavior solely to make coverage pass.'],
 native_commands=['./tv-app/gradlew -p tv-app testDebugUnitTest :app:afcCoverageReport',
 'git diff <base_sha> HEAD -- tv-app/app/src/main > <evidence_dir>/changed.diff',
 'diff-cover <qualified_jacoco_xml> --diff-file=<evidence_dir>/changed.diff --src-roots tv-app/app/src/main/java tv-app/app/src/main/kotlin --fail-under=90'],
 report_formats=['JaCoCo XML','diff-cover text','repo-owned mapping/exclusion inventory'],
 readiness='ANDROID_COVERAGE_COMPATIBILITY_GAP until pinned AGP/Kotlin/JDK17 produces qualified XML with known covered/uncovered Kotlin controls; owners G01T/G01+A01T/A01')
mutation_steps=[
 'G01 implements wrapper/report evaluator; G01T runs known killed and deliberately surviving mutation controls plus absent/empty/failed report controls. B01/A01 supply the respective pinned admitted runtime/dependencies.',
 'Bind exact candidate, input/tool/config hashes and bounded changed functions/classes before run. Use isolated disposable mutation state and only test-owned resources; never mutate the submitted checkout or remote backend.',
 'Export full mutant ID/status/target inventory. Require >=70% killed/(killed+survived) non-equivalent qualified mutants; no-coverage mutant counts as surviving. Timeouts/crashes/not-run are unresolved, not killed. Equivalence exclusions need explicit rationale and reviewer evidence.',
 'Any unexamined changed executable behavior outside tool scope remains a named capability gap; no silent exclusion or app redesign. Thresholds remain TE proposals, not vendor recommendations.',
 'Stop on unsupported tool/runtime or inability to validate report schema. Pin and scan before first use; use documented options for the admitted version only; no mutmut2 flags copied into 3+.'
]
add('CMD-MUTATION-BACKEND','bash tools/ci/mutation/backend.sh <base_sha> <evidence_dir>',
 'G01 repo-owned wrapper/evaluator using mutmut (documented current 3+ execution model); B01T/B01 own pinned dependency admission.',
 'Qualified mutmut status inventory supports >=70% score, required changed targets represented and no unresolved execution failure. '+complete,
 ['P2-G01T','P2-G01','P2-B01T','P2-B01','backend gate-chain'],mutation_steps,
 native_commands=['(cd backend && mutmut run && mutmut export-cicd-stats)'],
 configuration='B01T backend/pyproject.toml tool.mutmut uses documented source_paths and pytest_add_cli_args_test_selection for local unit/contract suites; G01 wrapper binds bounded target selection in isolated config, never deployed tests. Actual admitted version controls configuration spelling/export file schema.',
 report_formats=['mutmut exported CI statistics (version schema qualified before use)','full mutant ID/status inventory','repo-owned mutation-result.json with score and unresolved counts'],
 readiness='PYTHON_MUTATION_QUALIFICATION_PENDING; additionally PYTHON_NONFUNCTION_MUTATION_GAP for changed module-level behavior unsupported by admitted mutmut. G01 owns explicit scope decision/stop, no architectural workaround.')
add('CMD-MUTATION-TVAPP','bash tools/ci/mutation/tvapp.sh <base_sha> <evidence_dir>',
 'G01 repo-owned mutation wrapper; prospective Android-specific PIT candidate pl.droidsonroids.pitest (koral-- fork), not ordinary info.solidsoft.pitest.',
 'Only after compatibility qualification: PIT XML target inventory supports >=70%, actual changed Kotlin targets represented and all required tests preserved. Until then ANDROID_MUTATION_COMPATIBILITY_GAP, never PASS. '+complete,
 ['P2-G01T','P2-G01','P2-A01T','P2-A01','tv-app-ui gate-chain'],mutation_steps+[
 'A01T/A01 bind candidate fork in existing app Gradle config only after scan. Documented variant task is :app:pitestDebug; produce PIT XML and retain per-variant reports. The docs example version is not an admitted pin.',
 'Qualify actual AFC Kotlin/JDK17/AGP/starter versions with a known Kotlin mutant killed and a known survivor reported. Classpath/Compose/framework errors are capability gaps, not red assertions.',
 'No new product module, returnDefaultValues weakening, replacement harness, or ordinary-Java-plugin substitution. If the candidate fails bounded qualification, stop this declared claim and return named gap to parent.'],
 native_commands=['./tv-app/gradlew -p tv-app :app:pitestDebug'],
 report_formats=['PIT mutations XML','PIT per-variant report directory','repo-owned mutation-result.json'],
 readiness='ANDROID_MUTATION_COMPATIBILITY_GAP; prospective Android fork selected for qualification only, not represented as working or installed')
add('PROC-GATE-TOOL-QUALIFY','python3 -m unittest discover -s tools/ci/tests/coverage -v && python3 -m unittest discover -s tools/ci/tests/mutation -v',
 'Prospective qualification harness owned by G01T/G01; not a command run by this TE session.',
 'Both positive and negative controls prove native reporter plus repo adapter semantics on admitted versions and intended target language. Missing capability returns named gap and stops affected gate; ordinary unit-test success never substitutes.',
 ['P2-G01T','P2-G01','P2-A01T','P2-A01','P2-B01T','P2-B01'],[
 'Bind executable versions, artifact pins/sha256 and supply-chain receipts, target runtime, candidate/tool/config digests; help output for admitted native CLI recorded without secrets.',
 'Coverage controls: covered changed statement passes; intentionally uncovered changed statement fails threshold; absent XML, stale XML, missing changed file and empty denominator reject.',
 'Mutation controls: observable known mutant killed; deliberate survivor remains surviving; empty inventory, wrong target mapping, timeout/error and stale cached evidence reject. Preserve every status and denominator.',
 'G01 generic adapters can qualify against fixtures before A01/B01 land; actual Android/Python qualification closes only after their prepared build/dependencies exist. Avoid cyclic landing: preparation and capability checks can occur in pair worktrees; no gate is called PASS before native evidence.',
 'Initial tiny-control budget: forecast <=10 min coverage per language and <=20 min mutation per language, with explicit timeout/gap on overrun. No unbounded all-repo mutation; qualify scoped modules. Actual measured gate overhead is recorded after future execution and added to wave receipts.',
 'New/changed engine-backed qualification suites retain PROC-RELIABILITY five sequential and one two-concurrent-copy run with named locks and owned cleanup; no hardware benchmark.'])

d['gate_tool_plan']={'status':'OWNERS_AND_PROSPECTIVE_COMMANDS_BOUND; EXECUTION_NOT_RUN',
 'owners':{'P2-G01T':'positive/negative qualification controls in tools/ci/tests/coverage and mutation','P2-G01':'repo wrappers/evaluators/config in tools/ci/coverage and mutation; bind exact commands to gate-chain',
 'P2-A01T/P2-A01':'existing Android build/report configuration and native qualification under tv-app-gradle lease','P2-B01T/P2-B01':'Python deps/config/native qualification under backend-template'},
 'qualifier':'PROC-GATE-TOOL-QUALIFY','commands':['CMD-COVERAGE-BACKEND','CMD-COVERAGE-TVAPP','CMD-MUTATION-BACKEND','CMD-MUTATION-TVAPP'],
 'remaining_gaps':['PYTHON_COVERAGE_QUALIFICATION_PENDING','PYTHON_MUTATION_QUALIFICATION_PENDING','PYTHON_NONFUNCTION_MUTATION_GAP when applicable','ANDROID_COVERAGE_COMPATIBILITY_GAP','ANDROID_MUTATION_COMPATIBILITY_GAP','SHELL_GATE_CAPABILITY_GAP','REVERIFY_CAPABILITY_GAP'],
 'shell_disposition':'G01-owned changed shell gate logic has no admitted coverage/mutation backend in the bounded evidence. SHELL_GATE_CAPABILITY_GAP remains for those claims; do not count Python/Kotlin reports or ordinary gate tests as shell coverage/mutation. G01 must qualify a documented backend in its existing paths or return exact gap before claiming the gate.',
 'pins':'Actual version locks/digests/scans are early-slice deliverables, not invented here. No acquisition or installation during planning.',
 'cost':'IE wave ordinary gate estimates unchanged; new tool qualification and mutation runtime cost are additional unmeasured work, bounded per procedure and reported in runtime wave receipt.',
 'backend_protection':'Frozen OCR delegate and Reverify 0.11.0 unchanged. APK semantics unproven; no alternate backend, APK claim kind, string/ZIP or ATE substitute.'}
for lane,flavor in [('backend','BACKEND'),('tv-app-ui','TVAPP')]:
    claims=d['gate_declarations'][lane]['claims']
    for name,prefix in [('changed_line_coverage','COVERAGE'),('mutation','MUTATION')]:
        c=claims[name];id='CMD-'+prefix+'-'+flavor
        c.update(status='ALLOCATED_QUALIFICATION_PENDING',command_id=id,tool=cmd[id]['description'],
                 typed_gap=cmd[id]['readiness'],qualification_command='PROC-GATE-TOOL-QUALIFY',report_formats=cmd[id]['report_formats'],
                 owners=cmd[id]['used_by'][:4],execution_status='not_run')
        if lane=='backend': c['additional_scope_gap']='SHELL_GATE_CAPABILITY_GAP on changed shell gate code; G01 owns resolution.'
    d['gate_declarations'][lane]['gate_commands']+=['CMD-COVERAGE-'+flavor,'CMD-MUTATION-'+flavor]
for name in ['changed_line_coverage','mutation']:
    for target in [d['gate_declarations']['defects']['claims'],d['gate_declarations']['device-integration-spikes']['product_code_claims']]:
        target[name].update(status='ALLOCATED_BY_TARGET_LANGUAGE',tool='Use qualified backend or tv-app-ui command for changed product language; shell and unsupported scope retain named gaps.',
          command_ids=['CMD-COVERAGE-BACKEND','CMD-COVERAGE-TVAPP'] if name=='changed_line_coverage' else ['CMD-MUTATION-BACKEND','CMD-MUTATION-TVAPP'],
          typed_gap='Same native compatibility, report, scope and not_run gaps as the target lane; no unit-test substitute.',qualification_command='PROC-GATE-TOOL-QUALIFY')
d['gate_declarations']['policy']['tool_finalization_ref']='gate_tool_plan and gate_tool_primary_sources; TOOL_UNALLOCATED ownership resolved, native qualification remains pending.'
for id in ['CMD-GATE-ALL','CMD-GATE-BACKEND','CMD-GATE-TVAPP']:
    cmd[id]['gate_chain_note']='Existing unit/lint/build gate plus applicable separately declared changed-line/mutation commands. Product-area PASS alone does not close additional claims; native/tool gap remains blocking for affected gate. '+hold
cmd['PROC-PREPARE']['procedure_steps'].insert(0,'Verify subsequent owner execution instruction for all product/backend/spike/deployment work; planning/tracking approval alone is insufficient. P2-L01 uses its separate explicit tracking boundary.')
cmd['CMD-ESPN-CAPTURE']['procedure_steps']=[s.replace('optional live MNF only if approved before kickoff','October 12 capture is historical-only; first remaining live window is October 15 TNF') for s in cmd['CMD-ESPN-CAPTURE']['procedure_steps']]

groups=copy.deepcopy(impl['work_issues']['groups'])
by_slice={s:g['issue'] for g in groups for s in g['slices']}
si={s['id']:s for s in impl['slices']}
assert len(groups)==39 and len(by_slice)==52
assert next(g for g in groups if g['issue']=='P2-X05')['milestone']=='M2'
payload={'status':'PROPOSED_NOT_APPROVED_NOT_SUBMITTED','source_revision':head,
 'approval_boundary':hold,'milestones':[],'issues':[],
 'labels_note':'Exactly one kind proposed. Resolve actual existing labels with the policy tool at authorized dry-run; preserve policy-added labels. Missing label/permission is a gap, never create arbitrary labels or file unlabeled.',
 'payload_edit_rule':'After approval only mechanical substitutions of known issue/milestone numbers and dependency URLs; changed scope/acceptance returns for review.',
 'saved_mapping':'P2-L01 records stable group ID, every slice, issue number/URL, final milestone number, dependency URLs, saved labels/body digest, reuse/create result; Orchestrator transcribes to journey. All remain null here.'}
for m in impl['milestones']:
    date=re.match(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',m['due_on'])[0]
    explanation=m['due_on'][len(date):].strip()
    body=f"Milestone: {m['id']}\nDue UTC: {date}\n"+(f'Explanation: {explanation}\n' if explanation else '')
    body+=f"Entry: {m['entry']}\nExit: {m['exit']}\nSlices: {', '.join(m['slices'])}\n"
    # Current authority overrides older shorthand in M5 table entry, without changing the date.
    if m['id']=='M5': body+='OA-5 authorizes exact public export/history; LICENSE preparation is D03 agent work under settled Apache-2.0. Scans alone do not authorize visibility change.\n'
    payload['milestones'].append({'stable_id':m['id'],'title':m['title'],'due_on':date,'due_explanation':explanation,'description':body,'saved_number':None,'saved_url':None})
for g in groups:
    slices=[si[s] for s in g['slices']];representative=si[g['issue']]
    kind='documentation' if representative['lane'] in ['spec-and-docs','scribe-side-lane','Scribe side lane'] or g['issue']=='P2-SCR1' else 'enhancement'
    proof=sorted({r for s in g['slices'] for r in pf['slice_proof_map'][s]})
    reqs=sorted({p['requirement_id'] for p in d['proof_cases'] if p['id'] in proof})
    deps=[]
    for edge in impl['dependencies']:
        if edge['to'] in g['slices'] and edge['from'] in by_slice and by_slice[edge['from']]!=g['issue']:
            dep={'group':by_slice[edge['from']],'source_slice':edge['from'],'target_slice':edge['to'],'condition':edge.get('condition',''),'url':None}
            if dep not in deps:deps.append(dep)
    stable='AFC-2026-10-11/'+g['issue']
    body=f"## Origin\n\nPhase 2 approved-planning candidate; stable ID `{stable}`. Slices: {', '.join(g['slices'])}.\n\n"
    body+=f"## Harness / version\n\nPlanning baseline `{head}`; execution tool pins and candidate identities will be recorded in the assigned slice evidence. No runtime execution claimed.\n\n"
    body+=f"## What\n\n{representative['goal']}\n\n"
    body+='## Current evidence\n\nProspective plan and SEIT allocations only. Product execution remains held until a subsequent owner instruction.\n\n'
    body+='## Expected\n\n'+f"Final-completion milestone: {g['milestone']}.\nRequirements: {', '.join(reqs)}.\nProof rows: {', '.join(proof)}.\n"
    if deps: body+='Dependencies (URLs substituted from saved mapping):\n'+''.join(f"- {x['group']}: {x['condition']}\n" for x in deps)
    body+='\n## Acceptance\n\nComplete every listed slice/proof duty in its allocated environment; retain typed gaps. Required review, gates and evidence must pass before closure. Partial work stays open.\n'
    if g['issue']=='P2-X05': body+='M1 checkpoint: historical fixtures only. Keep this issue open until M2 final live-timing/correction verdict and all acceptance evidence; M1 completion is not live proof.\n'
    if g['issue']=='P2-X11': body+='Conditional only: OD-AFC-03 and timing gates govern dispatch. Unselected/no-offer terminal disposition does not claim enabled voice proof.\n'
    owner_blocker=representative.get('human_decision')
    body+='Owner blockers: '+(json.dumps(owner_blocker,ensure_ascii=False) if owner_blocker else 'Applicable OA/OD actions per approved plan')+'\n'
    payload['issues'].append({'stable_id':stable,'group':g['issue'],'slices':g['slices'],'kind':kind,'labels_proposed':[kind],
      'title':'['+g['issue']+'] '+representative['goal'].split(';')[0][:140],
      'milestone':g['milestone'],'body':body,'dependencies':deps,'proof_rows':proof,'requirement_ids':reqs,'conditional':g['issue']=='P2-X11',
      'saved_number':None,'saved_url':None,'reuse_rule':'Search all open and closed issues by stable ID and slice IDs; exactly one matching identity => reuse. Ambiguity/multiple matches => stop, never create another.'})
(E/'tracking-payloads.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
add('PROC-TRACKING-SETUP','python3 "$HOME/alphazede/Alphazedehq/hooks/issue-labels.py" file --repo 1wgrumph/amazon-fantasy-companion --kind <enhancement_or_documentation> --title <approved_title> --body-file <approved_body_file>',
 'P2-L01 prospective two-pass tracking setup; policy dry-run entrypoint, not executed during planning.',
 'Five matching approved milestones and 39 unique logical issues map all 52 slices exactly once; 13 TDD pairs combined; labels/milestone/dependencies/body/URL readback agrees. Duplicate reused, ambiguity refused, unapproved write refused, partial X05 stays open. No product dispatch implied.',
 ['P2-L01','IE-P2-2','SEIT-AFC-P2-MS-01'],[
 'Require explicit integrated planning/tracking approval of the exact payloads and recorded planning PR landing. Without both, produce only local proposed payloads and no remote mutation. Product execution remains held separately.',
 'Read all milestone and open/closed issue identities; search stable ID and slice IDs, including old titles. Reuse exactly one matching identity; ambiguous collisions stop. Extra unrelated repository issues are not deleted or counted as this plan.',
 'Create/reuse five milestones with CMD-MILESTONES-CREATE; machine due_on is ISO only, M2 2026-10-17T01:00:00Z. Keep T_yahoo +6h explanation in description, never alter date.',
 'Materialize each approved body from tracking_payload_ref byte-for-byte; source and requirements/proof links stay relative to approved repository content. Dry-run every new issue through command above; inspect kind and existing labels. No create through gh/HTTP/connector.',
 'After exact approval and successful dry-run, repeat the same policy command adding --submit; preserve FILED_VERIFIED number/URL and saved labels. Never blindly retry uncertain submission: search stable ID and read back first. Existing matches skip creation and are reconciled only within approved metadata scope.',
 'Once all identities known, assign milestone using gh issue edit <number> --repo 1wgrumph/amazon-fantasy-companion --milestone <approved_milestone_title>; link dependencies by saved issue URLs in reviewed body using gh issue edit <number> --repo 1wgrumph/amazon-fantasy-companion --body-file <approved_linked_body>. These edits are prospective authorized P2-L01 actions, not issue creation bypass.',
 'Read back each issue with gh issue view <number> --repo 1wgrumph/amazon-fantasy-companion --json number,url,title,body,labels,milestone,state; compare saved labels/body/dependencies/milestone and produce total slice-to-issue URL map. Parent records mapping in journey; this TE does not edit it.',
 'Inspect complete-map positive case and duplicate-reuse case; reject missing/doubled slice, split TDD pair, duplicate stable ID, unapproved submission, missing saved URL/label, wrong X05 milestone or partial-work closure. Conditional X11 remains labeled conditional in body unless existing label can be safely used; not an execution grant.'
 ],tracking_payload_ref=str(E/'tracking-payloads.json'),tracking_payload_sha256=sha(E/'tracking-payloads.json'),
 read_only_commands=['gh api --paginate "repos/1wgrumph/amazon-fantasy-companion/milestones?state=all&per_page=100"',
 'gh api --paginate "repos/1wgrumph/amazon-fantasy-companion/issues?state=all&per_page=100"',
 'gh issue view <number> --repo 1wgrumph/amazon-fantasy-companion --json number,url,title,body,labels,milestone,state'])
d['tracking_workflow']={'status':'PROPOSED_LOCAL_ONLY','command_id':'PROC-TRACKING-SETUP','milestones':5,'logical_issues':39,'slices':52,'tdd_pairs':13,
 'groups':groups,'payload_ref':str(E/'tracking-payloads.json'),'payload_sha256':sha(E/'tracking-payloads.json'),
 'approval_boundary':hold,'X05':'Wave1/M1 historical checkpoint; single issue final milestone M2; partial work stays open.',
 'inspection_evidence':str(P/'evidence/P2-L01/tracking/')+'approved-payload digest, duplicate inventory/reuse, five milestone readbacks, 39 saved issue readbacks, all dependency URLs and bijective slice mapping; no saved URL fabricated now.',
 'negative_cases':['missing/duplicate slice','TDD pair split','multiple matching stable IDs','creation before explicit approval or plan landing','missing/wrong saved labels or milestone','X05 M1 closure before final work','tracking approval treated as product execution authority'],
 'no_new_requirement':'Workflow proof extends existing AC-AFC-P2-MS-01 and planning/landing/authority control rows; no product requirement or new proof row.'}
cmd['CMD-MILESTONES-CREATE']['procedure_steps']=['Use PROC-TRACKING-SETUP approval/duplicate guard before any create; exact proposed milestone payloads are in tracking_payload_ref.','Five stable IDs only; reconcile/reuse before POST, no delete on mismatch. Machine due_on ISO only; full UTC time and explanation in description.']
cmd['CMD-MILESTONES-READBACK']['procedure_steps']=['Verify five milestones against approved payloads, then inspect PROC-TRACKING-SETUP saved mapping/readbacks for 39 issues and all 52 slices. This readback phase must not rerun filing/submission.']
cmd['CMD-MILESTONES-READBACK']['pass']+=' Also inspect the complete approved issue mapping and duplicate/authority controls in PROC-TRACKING-SETUP; no unrecorded logical deliverable or prematurely closed partial work.'
ms=pc['AC-AFC-P2-MS-01'];ms['method_fields']['tracking_evidence']=copy.deepcopy(d['tracking_workflow'])
ms['expected_result']+=' The approved tracking projection has 39 logical issues, every slice exactly once, duplicate reuse, saved URL mapping and no premature partial-work closure.'
ms['stimulus_or_procedure']+=' Inspect the PROC-TRACKING-SETUP payload/map/readback positive and negative cases; no remote action in this TE session.'
ms['method_fields']['additional_negative_observations']=d['tracking_workflow']['negative_cases']

# Owner-only public export is a distinct surface/history decision, never a scan result.
owner_class={'OA-5':'Owner authorizes exact public export/history and visibility; private prompt/route history is not automatically exportable after secrets/path scan.',
 'LICENSE':'Settled Apache-2.0 choice; standard file preparation allocated to P2-D03 as agent work, under current subsequent-execution hold.',
 'OA-8':'Separate per-release/tag/external-sending authority; tagged-main proof waits for actual authorized tag readback.',
 'current_hold':hold}
d['owner_action_classification']=owner_class
pc['AC-AFC-P2-SUB-01']['method_fields']['license_and_publication']=owner_class
pc['AC-AFC-P2-SUB-04']['method_fields']['owner_action_classification']=owner_class
pc['RISK-AFC-P2-12']['method_fields']['public_surface_control']='Sanitization is necessary but insufficient: OA-5 exact history/content authorization must include or exclude private prompts/routes; no silent export or destructive history rewrite.'
cmd['PROC-README-FRESH-SETUP']['procedure_steps'].append('Inspect D03 standard Apache-2.0 LICENSE preparation under settled SD-035. Public judge access needs OA-5 exact content/history and visibility approval; scan cleanliness alone grants nothing.')
cmd['PROC-SUBMISSION-CHECK']['procedure_steps'].append('Classify LICENSE preparation as D03 agent work, not unresolved owner license choice. Before any public flip/export, require OA-5 exact surface/history approval for existing private prompts/routes; no agent silently rewrites history or publishes them.')
cmd['CMD-JUDGE-ACCESS']['pass']+=' Public visibility/readback requires OA-5 approval of the exact content/history; never infer export permission from a secrets/path scan.'
d['cross_cutting_checks'].append({'id':'CC-EXECUTION-HOLD','command_id':'PROC-PREPARE','rule':hold})
d['cross_cutting_checks'].append({'id':'CC-PUBLIC-HISTORY','command_id':'PROC-SUBMISSION-CHECK','rule':owner_class['OA-5']+' '+owner_class['LICENSE']})

# Renew the IE projection exactly; preserve correction2 IDs and nonnumeric assembly ordering.
sm=pf['slice_proof_map']
d['integration_vv_sequence']=[]
for x in ie['steps']:
    row={'step':x['id'],'milestone':x['milestone'],'wave':int(x['milestone'][1:]),'order':x['order'],'after':x['after'],'slices':x['merges'],
      'entry_criteria':x['entry_criteria'],'post_step_vv':x['post_step_vv'],'rollback_ref':str(P/'specialists/integration-plan.md')+'#'+x['id'],
      'proof_rows':sorted({r for s in x['merges'] for r in sm[s]}),
      'command_ids':sorted(set(re.findall(r'\b(?:CMD|PROC)-[A-Z0-9-]+',json.dumps(x)))),
      'note':'Exact correction2 assembly projection; current task hold overrides prospective execution entry. Additional TE commands assigned through supplemental_command_ids and PI refresh; no IE edit.'}
    if x['id']=='IE-P2-2':row['supplemental_command_ids']=['PROC-TRACKING-SETUP']
    if x['id'] in ['IE-P2-3','IE-P2-5','IE-P2-7']:
        row['supplemental_command_ids']=['PROC-GATE-TOOL-QUALIFY']+({'IE-P2-3':[],'IE-P2-5':['CMD-COVERAGE-BACKEND','CMD-MUTATION-BACKEND'],'IE-P2-7':['CMD-COVERAGE-TVAPP','CMD-MUTATION-TVAPP']}[x['id']])
    d['integration_vv_sequence'].append(row)
d['integration_vv_sequence_note']='Owning TE projection of IE correction2. IE-P2-35 has order34 and precedes IE-P2-34/order35; D02 waits every final X01..X07 verdict and X11 terminal/no-offer disposition, including later landed verdicts through freeze. No review/assurance round reset. '+hold
d['wave_gate_costs']=copy.deepcopy(ie['wave_gate_costs'])
for l,w in zip(d['levels'],ie['wave_gate_costs']):
    l['integration_steps']=[s['id'] for s in ie['steps'] if s['milestone']==l['milestone']]
    l['added_gate_seconds']=w['added_gate_seconds'];l['resource_groups']=w['resource_groups'];l['cost_limits']=w['limits']
    match=re.match(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)(.*)',l['due_utc'])
    if match:l['due_utc']=match[1];l['due_explanation']=match[2].strip()
pc['AC-AFC-P2-SPEC-01']['method_fields']['verdict_freeze']='IE-P2-35 terminal disposition before IE-P2-34; include final X01..X07 including X03/X05 PR2 and every later landed verdict through freeze; selected X11 verdict or unselected/no-offer disposition. Same D02 slice owns required later delta.'
pc['AC-AFC-P2-SPEC-01']['preconditions'].append(pc['AC-AFC-P2-SPEC-01']['method_fields']['verdict_freeze'])

dispositions={
 'TE-P2-F01':('RESOLVED_PLANNED_OWNERSHIP','Current graph assigns deployed module directories, B01T shared conftest under backend-template and A02T instrumented profile/detect paths. Tests remain not_run.'),
 'TE-P2-F02':('RESOLVED_PLANNED_OWNERSHIP','X01 qualified/scanned JDK17/SDK/build-tools before A01T; empty bounded harness/interface bootstrap and leases explicit; valid behavioral red and hashes required; A01 release signer setup owned. No tools installed.'),
 'TE-P2-F03':('OWNERS_AND_COMMANDS_BOUND_WITH_CAPABILITY_GAPS','G01T/G01 qualification, A01T/A01 Android report tasks, B01T/B01 Python deps allocated. Six focused prospective command/procedure bindings added including tracking separately; native qualification and unsupported scopes remain exact named gaps in gate_tool_plan. OCR/Reverify unchanged; APK semantics unproven.'),
 'TE-P2-F04':('RESOLVED_DESIGN_AND_PROOF_ALIGNMENT','Strictly-inside20 and one alert per(profile,event) in current design, existing negative boundaries preserved. Added current-attempt Watch evidence; historical gameOpened never supplies current success.'),
 'TE-P2-F05':('PRESERVED','Fallback proof never closes missing primary-route proof. Conditional no-offer disposition does not claim enabled voice. Existing 100 rows/methods/negative cases retained.'),
 'TE-P2-F06':('RESOLVED_SOURCE_AND_IE_PROJECTION','Current graph red receipts/leases and correction2 D02 final-verdict/X11 order carried. No notice-only scope cut; final APK identity unchanged. Projection refreshed after PI mechanical rebind.'),
 'TE-P2-F07':('PRESERVED_AND_RESOURCE_BOUND','Copied IE ordinary wave forecasts 720/900/2100/0/120 seconds and resource groups, unmeasured. New tool qualification overhead is separate. Five sequential plus concurrent-copy rule, cleanup, locks and exact-input reuse retained.'),
 'TE-P2-F08':('PRESERVED_SOURCE_FIDELITY','Existing decision statuses unchanged, absent statuses remain not_recorded. Current lead DEC-AFC-SD-039 by reference; no whole journey digest. External S8 gap and BRAN unavailable unchanged. SVG prolog-only transition bound without semantic model claim.'),
 'TE-P2-F09':('RESOLVED_PROSPECTIVE_COMMANDS_WITH_PUBLICATION_PENDING','Correct tv-app wrapper, actual OpenAPI judge-flow conditions and same-main build identity retained. Tagged-main/publication remains OWNER_EVIDENCE_PENDING until OA-8 tag readback. OA-5 exact history/export boundary and settled LICENSE classification aligned.')}
for f in pf['findings']:
    status,text=dispositions[f['id']]
    f['historical_required_correction']=f.pop('required_correction')
    f.update(status=status,current_disposition=text,disposition_ref=str(P/'specialists/te-p2-finalize-receipt.md'))
pf['slices_with_unallocated_executable_evidence']=[]
pf['current_capability_gaps']=d['gate_tool_plan']['remaining_gaps']
pf['additional_dispositions']=[{'id':'PI-P2-F01','status':'RESOLVED','resolution':'RISK09 owning proof now includes A05; both slice_proof_map copies and IE-P2-28 projection include SEIT-RISK-AFC-P2-09.'}]
pf['additional_dispositions'].append({'id':'TE-FIN-SOURCE-01','status':'CURRENT_INPUT_BOUND; HISTORICAL_RECEIPT_STALE',
 'resolution':'Three root closure after-hashes still match. authority.json current hash differs from historical exact-source-closure after, but is unchanged since this session began and explicitly retains proposed/effective=false, product hold and LICENSE allocation. Current hash recorded in source_transition_evidence; historical receipt unchanged. Parent should append provenance for its intervening authority changes, not relabel old PASS.'})
pf['owner_observation_pending']=['AFC-PR-045 couch acceptance','OA-1..11 applicable protected actions; OA-5 exact public history/export, OA-8 tag readback. LICENSE choice settled and preparation belongs to D03.']
for item in pf['cases_needing_owner_decision']:
    if item['decision']=='OD-AFC-P2-04':item['rule']='Owner approves exact public surface/history and timing under OA-5. Settled Apache-2.0 standard LICENSE prepared by D03; no new license-choice question.'
pf['handoff']='Return to P&D lead under DEC-AFC-SD-039. PI refresh is mechanical; no TE role dispatch. One independent planning review follows refreshed candidate/render. '+hold

binds={'P2-L01':['PROC-TRACKING-SETUP'],
 'P2-G01T':['PROC-GATE-TOOL-QUALIFY'], 'P2-G01':['PROC-GATE-TOOL-QUALIFY','CMD-COVERAGE-BACKEND','CMD-COVERAGE-TVAPP','CMD-MUTATION-BACKEND','CMD-MUTATION-TVAPP'],
 'P2-A01T':['PROC-GATE-TOOL-QUALIFY'], 'P2-A01':['PROC-GATE-TOOL-QUALIFY','CMD-COVERAGE-TVAPP','CMD-MUTATION-TVAPP'],
 'P2-B01T':['PROC-GATE-TOOL-QUALIFY'], 'P2-B01':['PROC-GATE-TOOL-QUALIFY','CMD-COVERAGE-BACKEND','CMD-MUTATION-BACKEND']}
pf['mechanical_pi_refresh']={
 'command_bindings':binds,
 'slice_proof_rows':'Replace from current slice_proof_map, retaining all100 proofs/52 slices. A05 gains SEIT-RISK-AFC-P2-09; reproject requirement owners/traceability consistently.',
 'vv_and_capabilities':'Copy finalized methods/commands/gate declarations/remaining typed gaps; remove stale active TOOL_UNALLOCATED wording where ownership now bound. Do not claim native tools installed/qualified. Keep all five frozen route/capability snapshots unchanged.',
 'integration':'Refresh correction2 projection and TE supplemental command IDs; preserve IE-P2-35 before34 and D02 prerequisites. Copy wave_gate_costs unchanged; implementation may use documented step_ids key alias, preserving values and source link.',
 'tracking':'Project evidence/te-p2-finalize/tracking-payloads.json and its digest into work_issues/approval package. Exactly39 groups, 52 slices, 13 pairs, X05 final issue M2 and historical checkpoint M1. Bind PROC-TRACKING-SETUP to L01; no remote creation before explicit approval + plan landing.',
 'milestone_due':'Set implementation.json milestones[id=M2].due_on to 2026-10-17T01:00:00Z exactly. Preserve (T_yahoo + 6 h for the P2-X06 verdict pull request and P2-R2) separately in due_explanation/description. No date change.',
 'views':'For all four dod_manifest.models with models/view-*.svg: rebind current sha256, set selected=true and required=true, remove rejected non-embedded/render workaround text, restore safe embedding. Keep all three illustrative SVGs as selected/required views too: seven total. Unsafe/missing required asset is blocking, never optional.',
 'baseline_and_digest':'Refresh implementation checkout HEAD, nine planning hashes and SEIT-derived V&V/manifest digest from finalized seit.json. Do not rewrite approved register/spec authority or hash the whole journey. Recompute planning-review candidate_digest after all projections.',
 'authority_provenance':'Use current_authority_binding actual hash/state/scope. Historical root closure authority after-hash is stale; parent appends its source-transition provenance rather than treating the old receipt as current. No authority edit or activation by PI.',
 'authority':'Preserve current_task_product_execution_hold throughout settings, authority projection, slice dispatch and rendered text. P2-L01 tracking permission is not permission for D01/X01 or other product work. D03 owns LICENSE preparation; OA-5 exact export/history approval and OA-8 publication remain protected.',
 'checks':'Run implementation schema, freeze/manifest digest, renderer write/check on refreshed candidate; prove all seven embedded SVGs and exact M2 timestamp, all command/proof references and unchanged100-case coverage. Old schema/freeze/render PASS is historical, not current binding.',
 'scope':'PI edits only its authorized projection/render/evidence. No TE/RE/IE semantics, proof edits, model omission, role dispatch or independent review by PI.'}
pf['command_finalizations']+=['Added concrete repo-owned coverage/mutation qualification commands and PROC-TRACKING-SETUP; all existing64 IDs retained.','Ownership gaps resolved to allocated-but-unqualified named capability gaps, not runtime PASS.']
pf['required_views']=[{'id':v['id'],'path':v['view']['path'],'sha256':sha(P/v['view']['path']),'selected':True,'required':True} for v in impl['dod_manifest']['models']]

# Keep trace cells synchronized without rewriting any original negative-case string.
byid={q['id']:q for q in d['proof_cases']}
for r in d['traceability_matrix']:
    q=byid[r['SEIT row ID']]
    r['Positive case']=q['expected_result'];r['Evidence']=q['observable_evidence']
for q in d['proof_cases']:
    q['preconditions'].append(hold)
for s in d['integration_vv_sequence']:
    for id in s['command_ids']+s.get('supplemental_command_ids',[]):
        assert id in cmd,id
        cmd[id]['used_by']=sorted(set(cmd[id]['used_by']+[s['step']]))
d['required_commands']+=list(binds['P2-G01'])+['PROC-TRACKING-SETUP']
d['required_commands']=list(dict.fromkeys(d['required_commands']))
d['system_description_and_requirements_flowdown']['counts']['commands']=len(cmd)
assert len(d['proof_cases'])==100 and len(cmd)==70
(P/'seit.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
(E/'source-transitions.json').write_text(json.dumps(d['source_transition_evidence'],ensure_ascii=False,indent=2)+'\n')
(E/'tool-decisions.json').write_text(json.dumps({'sources':d['gate_tool_primary_sources'],'plan':d['gate_tool_plan']},ensure_ascii=False,indent=2)+'\n')
changes=[]
def diff(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        for k in sorted(set(a)|set(b)):
            if k not in a or k not in b:changes.append(path+'/'+k)
            else:diff(a[k],b[k],path+'/'+k)
    elif isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):changes.append(path+' [length]')
        for n,(aa,bb) in enumerate(zip(a,b)):diff(aa,bb,path+'/'+str(n))
    elif a!=b:changes.append(path)
diff(before,d)
(E/'changed-fields.json').write_text(json.dumps({'before_sha256':sha(E/'seit.before.json'),'after_sha256':sha(P/'seit.json'),'fields':changes},indent=2)+'\n')
print(f'FINALIZE: {len(d["proof_cases"])} proof cases preserved; {len(cmd)} commands; 44 IE steps; 39 issue payloads; {len(changes)} field paths changed')
