"""Read-only structural/coverage check of the prospective SEIT, not product V&V."""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
import jsonschema

P=Path('docs/plans/2026-10-12-amazon-fantasy-companion-phase-2')
S=Path.home()/'.claude/plugins/cache/bearing-lite/bearing-lite/1.1.6/schemas/seit.schema.json'
d=json.loads((P/'seit.json').read_text())
probe=sys.argv[1] if len(sys.argv)>1 else None
if probe=='schema':
    del d['proof_cases'][0]['preconditions']
elif probe=='coverage':
    d['proof_cases'].pop()
elif probe=='unknown-id':
    d['proof_cases'][0]['command_id']='CMD-UNDECLARED-PROBE'
elif probe:
    raise SystemExit('unknown validation probe')
schema=json.loads(S.read_text())
errors=list(jsonschema.Draft202012Validator(schema).iter_errors(d))
print('SCHEMA: '+('PASS (Draft 2020-12; 0 errors)' if not errors else f'FAIL ({len(errors)} errors)'))
for e in errors: print('schema:',list(e.absolute_path),e.message)
fail=[]
def check(ok,kind,message):
    if not ok: fail.append((kind,message))

reg={}
for line in (P/'requirements-register.md').read_text().splitlines():
    if line.startswith('| AFC-PR-'):
        c=[x.strip() for x in line.strip('|').split('|')];reg[c[0]]=c
active={u for u,c in reg.items() if not c[1].startswith('WITHDRAWN')}
retired=set(reg)-active
plan=(P/'amazon-fantasy-companion-phase-2-technical-plan.md').read_text()
local=set(re.findall(r'^\| ((?:AC|RISK)-AFC-P2-[A-Z0-9-]+) \|',plan,re.M))
pcs=d['proof_cases'];counts=Counter(x['requirement_id'] for x in pcs)
check(set(counts)==active|local,'coverage gap','requirement set differs')
check(all(v==1 for v in counts.values()),'coverage gap','not exactly one proof per active/local requirement')
check(not(retired&set(counts)),'coverage gap','withdrawn requirement has proof')
check({x['requirement_id'] for x in d['system_description_and_requirements_flowdown']['retired_requirements']}==retired,'coverage gap','retired list differs')
commands=d['procedures_and_commands'];ids=[c['id'] for c in commands];cs=set(ids)
check(len(ids)==len(cs)<=128,'unknown ID','duplicate/overlimit commands')
graph=(P/'specialists/slice-graph.md').read_text();it=(P/'specialists/integration-plan.md').read_text()
required_source_cmds=set(re.findall(r'\b(?:CMD|PROC)-[A-Z0-9-]+',graph+'\n'+it))
check(required_source_cmds<=cs,'unknown ID','source commands absent: '+str(sorted(required_source_cmds-cs)))
check(set(d['required_commands'])<=cs,'unknown ID','unknown required command')
for c in commands:
    check(all(c.get(k) for k in ('id','command','pass','description','used_by')),'schema','command missing field: '+c['id'])
    check('actor' not in c,'schema','forbidden actor: '+c['id'])
    check(bool(re.fullmatch(r'(CMD|PROC)-[A-Z0-9-]+',c['id'])),'unknown ID','invalid command ID: '+c['id'])
design=set(re.findall(r'\b(?:DES|CONTRACT)-AFC-P2-[A-Z0-9-]+',(P/'design.md').read_text()))
pid={x['id'] for x in pcs}
check(len(pid)==len(pcs),'unknown ID','duplicate proof IDs')
for pc in pcs:
    u=pc['requirement_id'];mf=pc['method_fields']
    check(pc['design_id'] in design,'unknown ID','unknown design: '+pc['design_id'])
    check(pc['command_id'] in cs,'unknown ID','unknown proof command: '+pc['id'])
    check(pc['method'] in {'test','demonstration','inspection','analysis','evaluation'},'schema','bad method: '+pc['id'])
    check(bool(pc['negative_or_failure_case']),'coverage gap','missing observable failure: '+pc['id'])
    check(bool(pc.get('closing_slice')),'coverage gap','missing closing slice: '+pc['id'])
    if u in active:
        alloc=reg[u][3]
        check(pc['id']=='SEIT-'+u,'unknown ID','bad registered proof ID: '+pc['id'])
        check(mf['register_verification_case']=='VCASE-'+u,'unknown ID','bad VCASE: '+pc['id'])
        check(pc['method']==alloc.split(',')[0].lower(),'coverage gap','method drift: '+pc['id'])
        check(mf['register_environment']==alloc.split('Positive:')[0].split(',',1)[1].strip().rstrip('. '),'coverage gap','environment drift: '+pc['id'])
        check('Positive' in mf['positive_criterion_ref'] and 'Negative' in mf['negative_criterion_ref'],'coverage gap','criterion reference absent: '+pc['id'])
    if pc['method']=='test':
        check(all(mf.get(k) for k in ['test_slice','product_slice','red_expectation','test_article','stimulus','measured_response','test_environment','resource_group','expected_gate_time']),'coverage gap','test fields missing: '+pc['id'])
    if pc['method']=='demonstration':
        check(all(mf.get(k) for k in ['demonstration_scenario','observed_behavior','live_window_or_replay_basis','evidence_path']),'coverage gap','demonstration fields missing: '+pc['id'])
    if mf.get('reverify','').startswith('Applicable:') or mf.get('reverify','').startswith('Applicable to'):
        check(mf.get('apk_artifact') and mf.get('reverify_invocation'),'coverage gap','binary claim missing invocation: '+pc['id'])
    else: check(mf.get('reverify','').startswith('Reverify: not applicable — '),'coverage gap','missing Reverify N/A reason: '+pc['id'])

columns=['SEIT row ID','Acceptance/risk ID','Design/contract ID','Boundary/test layer','Positive case','Negative/failure case','Command/procedure ID','Evidence']
matrix=d['traceability_matrix']
check(d['traceability_matrix_columns']==columns,'schema','wrong trace columns')
check(len(matrix)==len(pcs),'coverage gap','trace/proof counts differ')
pc_byid={p['id']:p for p in pcs}
for r in matrix:
    check(list(r)==columns,'schema','extra/missing trace column')
    p=pc_byid.get(r.get('SEIT row ID'))
    check(p is not None,'unknown ID','trace unknown proof')
    if not p:continue
    for col,key in [('SEIT row ID','id'),('Acceptance/risk ID','requirement_id'),('Design/contract ID','design_id'),('Command/procedure ID','command_id')]:
        check(r[col]==p[key],'unknown ID','trace multi/mismatched ID: '+col)
    check(r['Negative/failure case']==p['negative_or_failure_case'] and bool(r['Evidence']),'coverage gap','trace evidence/negative absent')

slice_ids=set(re.findall(r'^\| (P2-[A-Z0-9]+) \|',graph,re.M))
sm=d['planning_findings_for_plan_integrator']['slice_proof_map']
check(set(sm)==slice_ids,'coverage gap','slice inventory differs')
for s,rows in sm.items(): check(bool(rows) and set(rows)<=pid,'coverage gap','slice has no/unknown proof: '+s)
levels=d['levels'];level_slices=[s for x in levels for s in x['slices']]
check(Counter(level_slices)==Counter({s:1 for s in slice_ids}),'coverage gap','wave slice membership differs')
ie=json.loads(re.search(r'```json integration_plan\n(.*?)\n```',it,re.S)[1])
steps=d['integration_vv_sequence']
check([s['step'] for s in steps]==[s['id'] for s in ie['steps']],'unknown ID','IE step inventory/order differs')
for a,b in zip(steps,ie['steps']):
    check(a['post_step_vv']==b['post_step_vv'] and a['after']==b['after'] and a['slices']==b['merges'],'coverage gap','IE projection drift: '+a['step'])
    check(set(a['command_ids'])<=cs,'unknown ID','IE step command absent: '+a['step'])
    check(set(a['proof_rows'])<=pid,'unknown ID','IE step proof absent: '+a['step'])

expected_inputs=['amazon-fantasy-companion-phase-2-technical-plan.md','design.md','requirements-register.md','models/allocation.md','models/views.md','models/view-structure.svg','models/view-interfaces.svg','models/view-states.svg','models/view-data.svg']
bound=d['source_baseline']['planning_inputs']
check([x['path'] for x in bound]==[str(P/f) for f in expected_inputs],'coverage gap','planning input set differs')
for x in bound:
    check(x['binding_status']=='bound' and x['sha256']==hashlib.sha256(Path(x['path']).read_bytes()).hexdigest(),'coverage gap','stale digest: '+x['path'])
J=Path.home()/'alphazede/worktrees/amazon-fantasy-companion-planning/docs/plans/2026-10-11-amazon-fantasy-companion/journey.json'
j=json.loads(J.read_text())
expected_dec={x['id']:x.get('status','not_recorded') for x in j['decisions'] if x['id'].startswith('DEC-AFC-')}
check(d['decision_baseline']['confirmed_decisions']==expected_dec,'coverage gap','decision projection differs')
expected_open={x:'open_for_integrated_review' for x in ['OD-AFC-02','OD-AFC-03','OD-AFC-04','OD-AFC-05','OA-AFC-A1']+[f'OD-AFC-P2-{n:02}' for n in range(1,6)]}
expected_open.update({f'OA-{n}':'owner_action_pending' for n in range(1,12)})
check({x['id']:x['status'] for x in d['decision_baseline']['open_items']}==expected_open,'coverage gap','open items differ')
for name,f in j['profile_selection']['frozen_snapshots'].items():
    b=d['frozen_profile_binding'][name]
    for key in ['roles','review','deterministic_verification']:
        check(b[key]==f['snapshot'][key],'coverage gap','frozen profile drift: '+name+'/'+key)
for x in d['planning_findings_for_plan_integrator']['cases_needing_owner_decision']:
    check(set(x['rows'])<=pid,'unknown ID','owner condition unknown proof: '+x['decision'])
for x in d['interface_coverage']:
    check(set(x['rows'])<=pid and x['positive'] and x['negative'],'coverage gap','interface one-sided or unknown row: '+x['contract'])
check(len(d['source_topic_inventory']['approved_verification_sections'])==15,'coverage gap','spec section inventory incomplete')
spec_uids={x.removeprefix('VCASE-') for row in d['source_topic_inventory']['approved_verification_sections'] for x in row['verification_cases']}
check(spec_uids==active,'coverage gap','approved spec verification coverage differs')
path_pattern=re.compile(r'/(?:home|Users)/[A-Za-z0-9._-]+/|[A-Za-z]:[\\/]Users[\\/][^\\/\s]+[\\/]')
for p in [P/'seit.json',*sorted((P/'evidence/te-p2-codex').glob('*.py'))]:
    check(not path_pattern.search(p.read_text()),'coverage gap','absolute home path in '+p.name)
for kind,msg in fail:print(kind+': '+msg)
print(f'COUNTS: register_active={len(active)}; lifecycle_acceptance=24; risks=13; source_rows={len(active)+len(local)}; proof_cases={len(pcs)}; traceability_rows={len(matrix)}; commands={len(commands)}')
print(f'COVERAGE: active_register={len(active&set(counts))}/63; lifecycle_local={len(local&set(counts))}/37; withdrawn_with_cases={len(retired&set(counts))}; duplicate_requirements={sum(v>1 for v in counts.values())}')
print(f'COMMANDS: source_ids={len(required_source_cmds)}; unresolved_source={len(required_source_cmds-cs)}; unresolved_proof={sum(p["command_id"] not in cs for p in pcs)}; actor_fields={sum("actor" in c for c in commands)}')
print(f'TRACEABILITY: rows={len(matrix)}; columns={len(columns)}; exactly_one_requirement_design_command_per_row='+('PASS' if all(list(r)==columns and r['SEIT row ID'] in pc_byid for r in matrix) else 'FAIL'))
print(f'SLICES: covered={sum(bool(x) for x in sm.values())}/52; integration_steps={len(steps)}/44; waves={len(levels)}/5')
print(f'BASELINE: bound_inputs={len(bound)}/9; decisions={len(expected_dec)}; open_items={len(expected_open)}; frozen_profiles={len(j["profile_selection"]["frozen_snapshots"])}')
print('CROSS-CHECK: '+('PASS (0 coverage gaps; 0 unknown IDs)' if not fail else f'FAIL ({len(fail)} findings)'))
sys.exit(bool(errors or fail))
