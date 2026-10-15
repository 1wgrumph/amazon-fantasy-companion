#!/usr/bin/env python3
"""Inspect this planning delta; no product execution or authority activation."""
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
PLAN = ROOT / 'docs/plans/2026-10-12-amazon-fantasy-companion-phase-2'
EVIDENCE = PLAN / 'evidence/P2-VEGA-PRIMARY-plan'
BASE = 'df259ed'  # selected-plan correction (DEC-AFC-SD-048..054); first delta base was 5097585
ALLOWED_SLICE_FIELDS = {('P2-D04', 'goal'), ('P2-D04', 'requirement_ids'), ('P2-D04', 'seit_proof_rows'), ('P2-V01', 'depends_on_text')}
ALLOWED_COMMANDS = {'CMD-COVERAGE-TVAPP', 'PROC-VEGA-PREPARE'}
ALLOWED_PROOF = {'SEIT-RISK-AFC-P2-14', 'SEIT-AFC-P2-VEGA-03'}


def baseline(name):
    relative = (PLAN / name).relative_to(ROOT).as_posix()
    return json.loads(subprocess.check_output(['git', 'show', BASE + ':' + relative], cwd=ROOT))


def topological(nodes, label):
    pending = {key: set(value) for key, value in nodes.items()}
    assert all(dep in pending for deps in pending.values() for dep in deps), label + ': missing/inactive dependency'
    order = []
    while pending:
        ready = sorted(key for key, deps in pending.items() if not deps)
        assert ready, label + ': dependency cycle: ' + repr(sorted(pending))
        order.extend(ready)
        for key in ready:
            del pending[key]
        for deps in pending.values():
            deps.difference_update(ready)
    return order


def main():
    impl = json.loads((PLAN / 'implementation.json').read_text())
    seit = json.loads((PLAN / 'seit.json').read_text())
    old_i, old_s = baseline('implementation.json'), baseline('seit.json')
    current = {row['id']: row for row in impl['slices']}
    original = {row['id']: row for row in old_i['slices']}
    assert len(current) == len(impl['slices']) == len(original) == 54
    assert current.keys() == original.keys(), 'new/deleted slice IDs'
    for key, old in original.items():
        for field in old:
            if (key, field) not in ALLOWED_SLICE_FIELDS and field != 'vega_primary_contingency':
                assert current[key][field] == old[field], key + '.' + field + ': baseline field changed'
    for field in ['profile_freeze', 'role_states', 'assurance', 'dependencies']:
        assert impl[field] == old_i[field], field + ': baseline changed'
    for field in ['review_cardinality', 'review_capabilities', 'assurance_cadence']:
        assert impl['journey_settings'][field] == old_i['journey_settings'][field], field
    for field in ['reviewer_slots', 'independent_review_rounds', 'aggregate_repair_rounds', 'additional_dispatch_authorized']:
        assert impl['journey_settings']['planning_review'][field] == old_i['journey_settings']['planning_review'][field], field
    for name in ['authority.json', 'journey.json']:
        assert json.loads((PLAN / name).read_text()) == baseline(name), name + ': control state changed'
    commands = {row['id']: row for row in seit['procedures_and_commands']}
    assert len(commands) == len(seit['procedures_and_commands'])
    for old in old_s['procedures_and_commands']:
        if old['id'] in ALLOWED_COMMANDS:
            continue
        assert {k: commands[old['id']][k] for k in old if k != 'vega_primary_contingency'} == {k: v for k, v in old.items() if k != 'vega_primary_contingency'}, 'prior command/correction changed: ' + old['id']
    proof = {row['id']: row for row in seit['proof_cases']}
    assert len(proof) == len(seit['proof_cases'])
    for old in old_s['proof_cases']:
        if old['id'] in ALLOWED_PROOF:
            continue
        assert {k: proof[old['id']][k] for k in old if k != 'vega_primary_contingency'} == {k: v for k, v in old.items() if k != 'vega_primary_contingency'}, 'prior proof field changed: ' + old['id']
    inactive = set()  # DEC-AFC-SD-049: Fire OS A0x/T are secondary, not inactive
    secondary = set(impl['vega_primary_contingency']['secondary_target_slices'])
    effective = {}
    starts, closes = {}, {}
    for key, row in current.items():
        alt = row.get('vega_primary_contingency', {})
        assert not alt or alt['dispatchable'] is False
        if key in inactive:
            continue
        candidate = {k: copy.deepcopy(v) for k, v in row.items() if k != 'vega_primary_contingency'}
        candidate.update(copy.deepcopy(alt.get('overrides', {})))
        assert len(candidate['goal']) <= 512, key + ': goal too long'
        for field in ['role', 'model_route', 'reasoning_level', 'review_path', 'authority_id']:
            assert candidate[field] == row[field], key + ': route/authority changed'
        assert all(cmd in commands for cmd in candidate['command_ids']), key + ': unknown command'
        assert all(pid in proof for pid in candidate['seit_proof_rows']), key + ': unknown proof'
        assert all(uid in impl['traceability'] for uid in candidate['requirement_ids']), key + ': unknown requirement'
        starts[key] = candidate['depends_on']
        closes[key] = list(dict.fromkeys(candidate['depends_on'] + alt.get('completion_dependencies', [])))
        effective[key] = {'depends_on': starts[key], 'completion_dependencies': closes[key], 'role': candidate['role'], 'write_set': candidate['write_set'], 'command_ids': candidate['command_ids']}
    start_order = topological(starts, 'slice start graph')
    close_order = topological(closes, 'slice completion graph')
    assert not (set(closes['P2-V01T']) & inactive)
    assert set(closes['P2-V01']) >= {'P2-X02', 'P2-X03', 'P2-X04', 'P2-X07', 'P2-L03'}
    integration = {}
    for step in impl['integration_plan']['steps']:
        alt = step['vega_primary_contingency']
        integration[step['id']] = alt['after']
    integration_order = topological(integration, 'integration graph')
    secondary_steps = {s['id'] for s in impl['integration_plan']['steps'] if s['vega_primary_contingency']['status'] == 'fire_os_secondary'}
    assert not any(set(integration[k]) & secondary_steps for k in integration if k not in secondary_steps), 'primary integration step waits on Fire OS secondary'
    assert integration_order.index('IE-P2-V01') < integration_order.index('IE-P2-29')
    assert impl['vega_primary_contingency']['active'] is True and impl['vega_primary_contingency']['owner_decision_ref'] == 'DEC-AFC-SD-049'
    assert impl['planning_deltas'][-1]['F1'].startswith('closed') and seit['planning_deltas'][-1]['F1'].startswith('closed')
    d04 = current['P2-D04']
    assert d04['requirement_ids'][-1] == 'RISK-AFC-P2-14' and d04['seit_proof_rows'][-1] == 'SEIT-RISK-AFC-P2-14'
    assert d04['goal'].endswith('otherwise report it as in progress with its limits.')
    assert 'P2-D04' in impl['traceability']['RISK-AFC-P2-14']['slices']
    assert proof['SEIT-RISK-AFC-P2-14']['closing_slice'] == 'P2-D04' and proof['SEIT-RISK-AFC-P2-14']['supporting_slices'] == ['P2-V01']
    assert '--fail-under=70' in commands['CMD-COVERAGE-TVAPP']['native_commands'][2]
    assert 'PROC-POST-SUBMISSION-UTP-NETTY' in commands
    assert all(not (set(effective[k]['completion_dependencies']) & secondary) for k in effective if k not in secondary), 'primary slice waits on Fire OS secondary'
    for key in secondary:
        assert current[key] is not None, key + ': secondary slice deleted'
    for pid in [p for p in proof if 'VPRIMARY-' in p] + ['SEIT-RISK-AFC-P2-16', 'SEIT-RISK-AFC-P2-17']:
        row = proof[pid]
        assert row['execution_status'] == 'not_run'
        assert row['requirement_id'] in impl['traceability']
        assert row['command_id'] in commands
        assert row['closing_slice'] in effective
    report = {'outcome': 'PASS', 'base_commit': BASE, 'existing_slices_preserved': len(original), 'active_proposed_slices': len(effective), 'new_slices': 0, 'baseline_commands_and_F2_F8_preserved_except': sorted(ALLOWED_COMMANDS), 'authority_and_journey_unchanged': True, 'frozen_routes_capabilities_and_spent_bounds_preserved': True, 'start_order': start_order, 'completion_order': close_order, 'integration_order': integration_order, 'F1': 'closed by DEC-AFC-SD-050', 'secondary_target_slices': sorted(secondary), 'execution': 'not_run; no binary claim'}
    projection = {'status': 'selected by DEC-AFC-SD-049; execution authority pending planning review', 'base_commit': BASE, 'notes': ['X01 host/VVD milestone releases V01T while physical qualification remains pending.', 'X05 PR1 fixtures release B02T; original late live receipt still required.', 'Integration graph names closure order; slice start graph allows independent preparation.', 'No blanket wave/release barrier is added to backend or V01 prerequisites.'], 'secondary_target_slices': sorted(secondary), 'critical_path': impl['vega_primary_contingency']['critical_path'], 'milestone_order': impl['vega_primary_contingency']['milestone_order'], 'slices': effective, 'integration_dependencies': integration}
    if '--write-evidence' in sys.argv:
        (EVIDENCE / 'effective-graph.json').write_text(json.dumps(projection, indent=2) + '\n')
        (EVIDENCE / 'mechanical-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: value for key, value in report.items() if not key.endswith('_order')}, indent=2))


if __name__ == '__main__':
    main()
