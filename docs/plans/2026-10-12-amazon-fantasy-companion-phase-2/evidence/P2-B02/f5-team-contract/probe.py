"""Diagnostic contract probe; never edits product or frozen tests.

The strict mode adds only the required rejection of the synthetic SYN team.
It is not a proposed full validator or evidence of a candidate repair.
"""
import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(ROOT / 'backend' / 'src'))

if sys.argv[1] == 'nonleader-red':
    proof = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'relevance-contract-gap.py'))
    assert proof['actual'] is True, 'F5: selected manual nonleader game is not monitored'
else:
    import pytest
    from lineup import manual

    if sys.argv[1] == 'reject-synthetic-team':
        original = manual.build

        def reject_synthetic(espn_roster, entries, preset):
            if any(player.get('team') == 'SYN' for player in espn_roster):
                raise ValueError('SYN is not an NFL team abbreviation or ESPN NFL team id')
            return original(espn_roster, entries, preset)

        manual.build = reject_synthetic
    elif sys.argv[1] != 'frozen-baseline':
        raise ValueError('Unknown probe mode')
    tests = [
        'test_build_labels_the_entry_manual_with_its_preset',
        'test_build_applies_the_selected_preset',
        'test_manual_values_are_never_presented_as_yahoo',
    ]
    path = str(ROOT / 'backend/tests/unit/lineup/test_manual_source.py')
    print(json.dumps({'probe_mode': sys.argv[1], 'tests': tests}), flush=True)
    sys.exit(pytest.main(['-q', '--tb=short', *[path + '::' + test for test in tests]]))
