"""Check only newly changed bindings; reuse the original validator without editing it."""
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree

P=Path('docs/plans/2026-10-12-amazon-fantasy-companion-phase-2')
E=P/'evidence/te-p2-finalize'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((P/'seit.json').read_text());b=json.loads((E/'seit.before.json').read_text())
errors=[]
def check(ok,message):
    if not ok:errors.append(message)

# The old validator already supports dynamic commands and IE order; no adaptation needed.
r=subprocess.run(['python3',str(P/'evidence/te-p2-codex/check_seit.py')],capture_output=True,text=True)
(E/'validation.txt').write_text(r.stdout+r.stderr)
check(r.returncode==0,'existing schema/coverage validator')
print(r.stdout,end='')
check(d['source_baseline']['revision']==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'current HEAD baseline')
check(d['source_baseline']['branch']==subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'current branch baseline')
check(d['decision_baseline']['confirmed_decisions']==b['decision_baseline']['confirmed_decisions'],'source statuses changed')
check(d['decision_baseline']['open_items']==b['decision_baseline']['open_items'],'open status/owner action changed')
check(d['frozen_profile_binding']==b['frozen_profile_binding'],'frozen profile/backends changed')
for old,new in zip(b['proof_cases'],d['proof_cases']):
    for k in ['id','kind','requirement_id','design_id','command_id','method','negative_or_failure_case']:
        check(old[k]==new[k],'proof preservation '+old['id']+'/'+k)
check(len(b['proof_cases'])==len(d['proof_cases'])==100,'100 proofs preserved')
check(d['system_description_and_requirements_flowdown']['retired_requirements']==b['system_description_and_requirements_flowdown']['retired_requirements'],'withdrawn statuses changed')
pc={x['requirement_id']:x for x in d['proof_cases']}
for field in ['command','pass','procedure_steps']:
    old=next(c for c in b['procedures_and_commands'] if c['id']=='CMD-REVERIFY-APK')
    new=next(c for c in d['procedures_and_commands'] if c['id']=='CMD-REVERIFY-APK')
    check(old[field]==new[field],'Reverify invocation/semantic gap policy changed')

cl=json.loads((P/'evidence/P2-6/codex-lead/exact-source-closure.json').read_text())
for f,t in cl['input_transitions'].items():
    if f!='authority.json':check(sha(P/f)==t['after'],'root closure after hash: '+f)
ab=d['source_transition_evidence']['current_authority_binding']
check(ab['sha256']==sha(P/'authority.json'),'current authority binding')
check(ab['historical_closure_after']==cl['input_transitions']['authority.json']['after'],'historical authority hash preserved')
check(ab['state']=='proposed' and ab['effective'] is False and ab['license_path_allocated'],'current authority bounds')
check(ab['status']=='CURRENT_SOURCE_BOUND_WITH_HISTORICAL_HASH_MISMATCH','visible authority provenance discrepancy')
sv=json.loads((P/'evidence/svg-prolog/receipt.json').read_text())
prefix=b'<?xml version="1.0" encoding="UTF-8"?>\n'
check(len(prefix)==39,'XML prefix byte count')
for item in sv['files']:
    raw=(P/item['file']).read_bytes()
    check(sha(P/item['file'])==item['new_sha256'],'SVG current hash: '+item['file'])
    check(hashlib.sha256(prefix+raw).hexdigest()==item['old_sha256'],'SVG exact prefix-only transition: '+item['file'])
    check(ElementTree.tostring(ElementTree.fromstring(raw))==ElementTree.tostring(ElementTree.fromstring(prefix+raw)),'SVG XML tree: '+item['file'])
for f,h in sv['sysml_model_hashes'].items():check(sha(P/f)==h['before']==h['after'],'native SysML unchanged: '+f)

ie=json.loads(re.search(r'```json integration_plan\n(.*?)\n```',(P/'specialists/integration-plan.md').read_text(),re.S)[1])
check(d['wave_gate_costs']==ie['wave_gate_costs'],'IE costs/resources projection')
check([x['added_gate_seconds'] for x in d['levels']]==[720,900,2100,0,120],'wave ordinary cost forecasts')
steps={x['step']:x for x in d['integration_vv_sequence']}
check(steps['IE-P2-35']['order']==34 and steps['IE-P2-34']['order']==35,'X11 precedes D02')
check('IE-P2-35' in steps['IE-P2-34']['after'],'D02 X11 terminal dependency')
check('P2-A05' in pc['RISK-AFC-P2-09']['supporting_slices'],'A05 RISK09 owning row')
for sm in [d['planning_findings_for_plan_integrator']['slice_proof_map'],d['system_description_and_requirements_flowdown']['slice_proof_map']]:
    check('SEIT-RISK-AFC-P2-09' in sm['P2-A05'],'A05 RISK09 proof map')
check('SEIT-RISK-AFC-P2-09' in steps['IE-P2-28']['proof_rows'],'A05 IE projection')
graph={}
for line in (P/'specialists/slice-graph.md').read_text().splitlines():
    if re.match(r'^\| P2-[A-Z0-9]+ \|',line):
        c=[v.strip() for v in line.strip('|').split('|')];graph[c[0]]=c
for sid,paths in d['planned_evidence_ownership']['deployed_and_instrumented_paths'].items():
    for path in paths:check(path in graph[sid][8],'allocated path absent '+sid+'/'+path)
check('backend-template' in graph['P2-B01T'][10],'shared conftest lease')
check('host tool preparation' in graph['P2-A01T'][11],'X01 before Android red')
check('release' in graph['P2-A01'][3] and 'signer' in graph['P2-A01'][3],'A01 release signing ownership')
check('LICENSE' in graph['P2-D03'][8],'D03 LICENSE write set')

payload=json.loads((E/'tracking-payloads.json').read_text())
counts=Counter(s for issue in payload['issues'] for s in issue['slices'])
check(len(payload['issues'])==39 and len(payload['milestones'])==5,'tracking payload count')
check(counts==Counter({s:1 for s in graph}),'every slice exactly once')
check(sum(len(i['slices'])==2 for i in payload['issues'])==13,'TDD pairs combined')
check(all(len(i['slices'])!=2 or i['slices']==[i['group']+'T',i['group']] for i in payload['issues']),'TDD pairing identity')
check(next(i for i in payload['issues'] if i['group']=='P2-X05')['milestone']=='M2','X05 final milestone')
check('M1 checkpoint' in next(i for i in payload['issues'] if i['group']=='P2-X05')['body'],'X05 historical checkpoint retained')
check(next(m for m in payload['milestones'] if m['stable_id']=='M2')['due_on']=='2026-10-17T01:00:00Z','M2 exact ISO')
groups={i['group'] for i in payload['issues']}
for i in payload['issues']:
    check(i['kind'] in ['enhancement','documentation'],'tracking kind')
    check(i['saved_url'] is None and i['saved_number'] is None,'fabricated saved issue')
    check(all(x['group'] in groups for x in i['dependencies']),'unknown issue dependency')
    check(all('## '+s+'\n' in i['body'] for s in ['Origin','Harness / version','What','Current evidence','Expected','Acceptance']),'issue body sections')
check(sha(E/'tracking-payloads.json')==d['tracking_workflow']['payload_sha256'],'tracking payload digest')
for req in ['AFC-PR-030','AFC-PR-031','AFC-PR-032','AFC-PR-033','RISK-AFC-P2-03']:
    check('accessUnknown' in pc[req]['method_fields']['current_attempt_observation']['negative'],'current Watch negative '+req)

commands={c['id']:c for c in d['procedures_and_commands']}
for id in ['CMD-COVERAGE-BACKEND','CMD-COVERAGE-TVAPP','CMD-MUTATION-BACKEND','CMD-MUTATION-TVAPP','PROC-GATE-TOOL-QUALIFY','PROC-TRACKING-SETUP']:
    check(id in commands,'new binding absent: '+id)
for lane in ['backend','tv-app-ui']:
    for claim in ['changed_line_coverage','mutation']:
        c=d['gate_declarations'][lane]['claims'][claim]
        check(c['status']=='ALLOCATED_QUALIFICATION_PENDING' and c['command_id'] in commands and c['execution_status']=='not_run','optimistic capability claim')
check('ANDROID_MUTATION_COMPATIBILITY_GAP' in d['gate_tool_plan']['remaining_gaps'],'Android PIT gap lost')
check('REVERIFY_CAPABILITY_GAP' in d['gate_tool_plan']['remaining_gaps'],'Reverify gap lost')
check(d['current_task_scope']['product_execution']=='held until subsequent owner execution instruction','product hold missing')
views=d['planning_findings_for_plan_integrator']['required_views']
check(len(views)==7 and all(v['required'] and v['selected'] and sha(P/v['path'])==v['sha256'] for v in views),'seven required view binding')
for f,h in json.loads((E/'protected-inputs.json').read_text()).items():check(sha(Path(f))==h,'protected artifact altered: '+f)
path_pattern=re.compile(r'/(?:home|Users)/[A-Za-z0-9._-]+/|[A-Za-z]:[\\/]Users[\\/][^\\/\s]+[\\/]')
for f in [P/'seit.json',*sorted(E.glob('*.py')),*sorted(E.glob('*.json'))]:
    check(not path_pattern.search(f.read_text()),'private home path in '+str(f))

summary=[
 'PRESERVATION: 100 proof IDs/methods/negative cases; 63 active + 37 local; 3 retired; 5 frozen profiles/backends unchanged',
 'SOURCES: current HEAD + 9 hashes; 3 root closure hashes match; current authority rebound with historical mismatch visible; 4 exact SVG transitions; 4 native SysML hashes unchanged',
 'ASSEMBLY: 44 correction2 steps; IE-P2-35 before IE-P2-34; D02 final verdict prerequisites; wave forecasts 720/900/2100/0/120 seconds',
 'ALLOCATION: F01/F02 planned ownership resolved; A05 RISK09 proof mapping resolved',
 'TRACKING: 5 milestones; 39 logical issues; 52 slices exactly once; 13 TDD pairs; X05 final M2; exact M2 ISO timestamp',
 'CAPABILITIES: 70 commands; native qualification not_run; Android/Python-scope/shell/Reverify gaps explicit; no backend substitution',
 'AUTHORITY: product execution hold and exact public-history approval retained; LICENSE preparation assigned D03; 7 views required',
 'HISTORY: initial validator/receipts/evidence and other protected input artifacts unchanged',
 'FINALIZATION: '+('PASS (planning-only; no runtime/independent assurance claim)' if not errors else 'FAIL: '+'; '.join(errors))]
out='\n'.join(summary)+'\n';(E/'delta-validation.txt').write_text(out)
print(out,end='')
raise SystemExit(bool(errors))
