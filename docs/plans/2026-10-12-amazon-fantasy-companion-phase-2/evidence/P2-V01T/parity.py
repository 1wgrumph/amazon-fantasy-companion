#!/usr/bin/env python3
"""PROC-VEGA-PARITY and CMD-RED-VEGA classification for P2-V01T.

Reads the landed A01T..A05T receipts (their recorded case IDs plus the frozen
androidTest file) and the Jest JSON of the red run, maps every Fire OS test ID
to exactly one V01T test, and fails on a missing, duplicate or extra mapping.
Every failing V01T test must fail on a Jest matcher assertion; any other
failure is a harness error, not red evidence.

Usage: python3 parity.py [--self-test]   (run from the repository root)
"""

import json
import re
import sys
from pathlib import Path

EVIDENCE = Path('docs/plans/2026-10-12-amazon-fantasy-companion-phase-2/evidence')
HERE = EVIDENCE / 'P2-V01T'
JEST = HERE / 'raw' / 'jest-red.json'
ANDROID_TEST = ('alerts.AlertNotifierDeviceTest#headsUpAlertPostsWatchAndDismissOnAHighImportanceChannel',
                'tv-app/app/src/androidTest/java/com/afc/companion/alerts/AlertNotifierDeviceTest.kt')

# Fire OS test -> V01T test where the platform forces a different name.
RENAMES = {
    'ShellContractTest.buildDeclaresMinSdk25': (
        'ShellContractTest manifestDeclaresMinimumVegaOsVersion',
        'Vega has no Android minSdk; manifest.toml [os.version] min from the pinned SDK template.'),
    'watch.WatchLauncherTest#executesOnlyTheFireOsRegistryLaunch': (
        'WatchLauncherTest executesOnlyTheVegaRegistryLaunch',
        'The Vega client executes only platform_routes.vega and never fire_os.'),
    'panel.PanelControllerTest#everyPanelOperationIsBoundToAFireTvRemoteKey': (
        'PanelControllerTest everyPanelOperationIsBoundToAVegaRemoteKey',
        'Vega remote events are HWEvent eventType names from react-native-kepler TVTypes.d.ts.'),
}
NOTES = {
    ANDROID_TEST[0]: 'Instrumented on Fire OS; on Vega the notifier content is a Jest test and VVD display stays with '
                     'PROC-VISUAL-REVIEW (delivery route unverified on RN 0.83).',
    'ApiPolicyTest.setsNormalTimeoutsOnRealConnection': 'fetch has one api_timeout (AbortController), scheduled through an injected timer.',
    'ApiPolicyTest.setsLongPollReadTimeoutAboveServerWait': 'fetch has one api_timeout (AbortController), scheduled through an injected timer.',
    'ApiPolicyTest.opensAndReadsNetworkOffCallingUiThread': 'JS has one UI thread: open and parse must run after the caller\'s turn.',
    'detect.AppDetectorTest#reportsEachInstalledCandidateAndNoAbsentOne': 'Vega query is Linking.canOpenURL (async).',
}
# V01T tests with no A0xT source: Vega-specific VEGA-04, or goal-listed states sourced from A01 product-slice tests.
EXTRAS = {
    'TokenStoreTest persistsTheSessionTokenAcrossRestartOnlyThroughTheTokenStore': 'AC-AFC-P2-VEGA-04',
    'TokenStoreTest sendsTheTokenOnlyAsTheBearerCredential': 'AC-AFC-P2-VEGA-04',
    'TokenStoreTest tokenNeverReachesAnyLoggerAcrossLinkRefreshAndFailure': 'AC-AFC-P2-VEGA-04',
    'TokenStoreTest onlyTheTokenStoreModuleUsesPersistentStorage': 'AC-AFC-P2-VEGA-04',
    'VegaLinkStatesTest backendNotConfiguredBlocksLinkingUntilAUsableBaseUrl':
        'goal_source_notes "Backend not configured"; Fire OS A01 ClientBoundaryTest.shellStartsAtLinkUntilASessionExistsAndRequiresAConfiguredBackend',
    'VegaLinkStatesTest networkErrorShowsRetryAndCannotContinueToProfile':
        'goal_source_notes "network error"; Fire OS A01 LinkScreen.kt networkError and ClientBoundaryTest.linkFlowStopsOnExpiryErrorAndTokenlessLink',
}


def fire_os_ids():
    """(slice, id) for every landed A01T..A05T test ID, in receipt order."""
    ids = [('A01T', c['id']) for c in json.loads((EVIDENCE / 'P2-A01T/red-test-cases.json').read_text())['cases']]
    for slice_id in ('A02T', 'A03T', 'A04T', 'A05T'):
        receipt = json.loads((EVIDENCE / f'P2-{slice_id}/receipt.json').read_text())
        ids += [(slice_id, c['id']) for c in receipt['cases']]
        if ANDROID_TEST[1] in receipt['frozen_tests']:
            ids.append((slice_id, 'com.afc.companion.' + ANDROID_TEST[0]))
    return [(s, i.removeprefix('com.afc.companion.')) for s, i in ids]


def v01t_name(fire_id):
    if fire_id in RENAMES:
        return RENAMES[fire_id][0]
    # A01T: Class.method[param]; A02T+: pkg.Class#method
    match = re.fullmatch(r'(?:[a-z]+\.)?(\w+)[.#](\w+)(\[.*\])?', fire_id)
    if not match:
        raise ValueError(f'unparseable Fire OS ID: {fire_id}')
    return f'{match[1]} {match[2]}{match[3] or ""}'


def red_classification(test):
    if test['status'] == 'passed':
        return 'passing_at_red'
    if test['status'] != 'failed':
        return 'harness_error:' + test['status']
    message = (test['failureMessages'] or [''])[0]
    if 'Matcher error' in message:
        return 'harness_error:matcher_misuse'
    details = test.get('failureDetails') or [{}]
    if all(isinstance(d, dict) and 'matcherResult' in d for d in details) or message.startswith('Error: expect('):
        return 'behavioral_red'
    return 'harness_error:' + message.split('\n', 1)[0][:120]


def check(fire_ids, jest_tests):
    """Return (rows, errors)."""
    errors, rows, used = [], [], {}
    by_name = {}
    for test in jest_tests:
        if test['fullName'] in by_name:
            errors.append(f'duplicate V01T test name: {test["fullName"]}')
        by_name[test['fullName']] = test
    seen = set()
    for slice_id, fire_id in fire_ids:
        if fire_id in seen:
            errors.append(f'duplicate Fire OS ID: {fire_id}')
        seen.add(fire_id)
        name = v01t_name(fire_id)
        if name not in by_name:
            errors.append(f'missing V01T test for {fire_id}: {name}')
            continue
        if name in used:
            errors.append(f'V01T test {name} mapped twice ({used[name]}, {fire_id})')
        used[name] = fire_id
        rows.append({'fire_os_slice': slice_id, 'fire_os_id': fire_id, 'v01t_id': name,
                     'red': red_classification(by_name[name]),
                     'note': RENAMES.get(fire_id, (None, NOTES.get(fire_id, '')))[1]})
    for name, test in by_name.items():
        if name in used:
            continue
        if name in EXTRAS:
            rows.append({'fire_os_slice': None, 'fire_os_id': None, 'v01t_id': name,
                         'red': red_classification(test), 'note': EXTRAS[name]})
        else:
            errors.append(f'extra V01T test without an A0xT source or declared Vega reason: {name}')
    for name in EXTRAS:
        if name not in by_name:
            errors.append(f'declared Vega-specific test not collected: {name}')
    for row in rows:
        if row['red'].startswith('harness_error'):
            errors.append(f'{row["v01t_id"]}: {row["red"]}')
    return rows, errors


def self_test(fire_ids, jest_tests):
    _, ok = check(fire_ids, jest_tests)
    assert not ok, ok
    _, dropped = check(fire_ids, jest_tests[1:])
    assert dropped, 'a dropped V01T test must fail parity'
    extra = dict(jest_tests[0], fullName='Unmapped invented')
    _, added = check(fire_ids, jest_tests + [extra])
    assert any('extra V01T test' in e for e in added), added
    _, doubled = check(fire_ids + fire_ids[:1], jest_tests)
    assert any('duplicate Fire OS ID' in e for e in doubled), doubled
    broken = dict(jest_tests[0], status='failed', failureMessages=['TypeError: x is not a function'], failureDetails=[{}])
    _, harness = check(fire_ids, [broken] + jest_tests[1:])
    assert any('harness_error' in e for e in harness), harness
    print('self-test: PASS (complete passes; dropped, extra, duplicate and harness-error cases fail)')


def main(argv):
    fire_ids = fire_os_ids()
    jest = json.loads(JEST.read_text())
    tests = [t for suite in jest['testResults'] for t in suite['assertionResults']]
    if '--self-test' in argv:
        self_test(fire_ids, tests)
    rows, errors = check(fire_ids, tests)
    counts = {key: sum(1 for r in rows if r['red'] == key) for key in ('behavioral_red', 'passing_at_red')}
    summary = {'fire_os_ids': len(fire_ids), 'v01t_tests': len(tests), 'mapped': sum(1 for r in rows if r['fire_os_id']),
               'vega_specific': sum(1 for r in rows if not r['fire_os_id']), **counts, 'errors': errors}
    (HERE / 'parity.json').write_text(json.dumps({'summary': summary, 'rows': rows}, indent=2) + '\n')
    lines = ['---', 'type: evidence', 'title: P2-V01T Fire OS to Vega test parity', 'okf_status: draft',
             'tags: [evidence, vega, p2-v01t, parity]', '---', '', '# P2-V01T parity (PROC-VEGA-PARITY)', '',
             'Generated by `parity.py` from the A01T..A05T receipts and `raw/jest-red.json`.', '',
             f'- Fire OS test IDs: {summary["fire_os_ids"]}; V01T tests: {summary["v01t_tests"]}.',
             f'- Mapped: {summary["mapped"]}; Vega-specific: {summary["vega_specific"]}.',
             f'- Red: {counts["behavioral_red"]} behavioral; {counts["passing_at_red"]} passing at red.',
             f'- Errors: {len(errors)}' + ('' if not errors else ' — ' + '; '.join(errors)), '',
             '| Fire OS slice | Fire OS test ID | V01T test ID | Red result | Note |', '|---|---|---|---|---|']
    for r in rows:
        lines.append('| {} | {} | {} | {} | {} |'.format(
            r['fire_os_slice'] or 'Vega', (r['fire_os_id'] or '—').replace('|', '\\|'),
            r['v01t_id'].replace('|', '\\|'), r['red'], r['note'].replace('|', '\\|')))
    (HERE / 'parity.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(summary, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
