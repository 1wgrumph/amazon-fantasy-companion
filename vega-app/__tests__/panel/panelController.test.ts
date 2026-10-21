// AFC-PR-042/-043/-044/-061/-062: remote show/hide and team/league switch, every element focusable, refresh on show
// and every panel_refresh (30 s) while visible, changed-row updates only, hidden panel suspends, bounded state.
// Mirrors PanelControllerTest.kt; remote keys are Vega HWEvent eventType names.
import {readFileSync} from 'fs';
import {join} from 'path';
import {FocusTarget, PANEL_ACTIONS, PANEL_DELTA_NONE, PanelAction, PanelController, PanelDelta} from '../../src/panel/panel';
import {REPO} from '../support/contract';
import {prow, snap, TL} from '../support/panel';

const other = 'league-b/team-2';
/** The ten remote events the pinned react-native-kepler TVTypes.d.ts documents for a Vega remote. */
const REMOTE_KEYS = ['up', 'down', 'left', 'right', 'select', 'menu', 'back', 'playpause', 'rewind', 'forward'];

const controller = (visible = true) => new PanelController([TL, other], TL, visible);
const row = (playerId: string): FocusTarget => ({kind: 'row', playerId});

function keyFor(c: PanelController, action: PanelAction): string {
  const key = [...c.bindings()].find(([, bound]) => bound === action)?.[0];
  expect({action, bound: key !== undefined}).toEqual({action, bound: true});
  return key!;
}

function loaded(c = controller(), s = snap()): PanelController {
  expect(c.shouldFetch(0)).toBe(true);
  c.onFetched(s, 0);
  expect(c.snapshot).not.toBeNull();
  return c;
}

const delta = (d: PanelDelta) => ({changed: [...d.changedRows].sort(), removed: [...d.removedRows].sort(), totals: d.totalsChanged});

describe('PanelControllerTest', () => {
  test('initialStateReflectsTheProfileSettings', () => {
    const c = controller(true);
    expect(c.visible).toBe(true);
    expect(c.teamLeague).toBe(TL);
    expect(controller(false).visible).toBe(false);
  });

  // Vega rename of everyPanelOperationIsBoundToAFireTvRemoteKey.
  test('everyPanelOperationIsBoundToAVegaRemoteKey', () => {
    const types = readFileSync(
      join(REPO, 'vega-app/node_modules/@amazon-devices/react-native-kepler/Libraries/TV/TVTypes.d.ts'),
      'utf8',
    );
    for (const key of REMOTE_KEYS) expect(types).toContain(` ${key} - This event is received`);
    const c = controller();
    for (const action of PANEL_ACTIONS) expect({action, key: REMOTE_KEYS.includes(keyFor(c, action))}).toEqual({action, key: true});
  });

  test('remoteTogglesVisibility', () => {
    const c = controller();
    const toggle = keyFor(c, 'ToggleVisibility');
    expect(c.onKey(toggle, 0)).toBe(true);
    expect(c.visible).toBe(false);
    expect(c.onKey(toggle, 1)).toBe(true);
    expect(c.visible).toBe(true);
  });

  test('remoteSwitchesTeamLeagueAndCyclesBack', () => {
    const c = loaded();
    expect(c.onKey(keyFor(c, 'NextTeamLeague'), 1_000)).toBe(true);
    expect(c.teamLeague).toBe(other);
    expect(c.snapshot).toBeNull();
    expect(c.shouldFetch(1_000)).toBe(true);
    expect(c.onKey(keyFor(c, 'NextTeamLeague'), 2_000)).toBe(true);
    expect(c.teamLeague).toBe(TL);
  });

  test('lateResponseForTheOldTeamIsDiscarded', () => {
    const c = loaded();
    c.perform('NextTeamLeague', 1_000);
    expect(c.onFetched(snap({revision: 8, teamLeague: TL}), 1_100)).toEqual(PANEL_DELTA_NONE);
    expect(c.snapshot).toBeNull();
    const d = c.onFetched(snap({teamLeague: other}), 1_200);
    expect(c.snapshot?.teamLeague).toBe(other);
    expect(new Set(d.changedRows)).toEqual(new Set(['p-11', 'p-23', 'p-31']));
  });

  test('everyElementIsFocusableAndReachableByDpad', () => {
    const c = loaded();
    const expected: FocusTarget[] = [{kind: 'teamLeagueSwitch'}, row('p-11'), row('p-23'), row('p-31'), {kind: 'total'}];
    expect(c.focusTargets()).toEqual(expected);
    expect(c.focused).toEqual(expected[0]);
    const down = keyFor(c, 'FocusNext');
    const visited = [c.focused];
    for (let i = 1; i < expected.length; i++) {
      expect(c.onKey(down, 0)).toBe(true);
      visited.push(c.focused);
    }
    expect(visited).toEqual(expected);
    c.onKey(down, 0);
    expect(c.focused).toEqual({kind: 'total'});
    c.onKey(keyFor(c, 'FocusPrevious'), 0);
    expect(c.focused).toEqual(row('p-31'));
  });

  test('focusMovesOffARemovedRow', () => {
    const c = loaded();
    for (let i = 0; i < 3; i++) c.perform('FocusNext', 0);
    expect(c.focused).toEqual(row('p-31'));
    c.onFetched(snap({revision: 8, rows: [prow('p-11', 12.3), prow('p-23', -1.5)]}), 1);
    expect(c.focused).not.toBeNull();
    expect(c.focusTargets()).toContainEqual(c.focused);
  });

  test('hiddenPanelLeavesNavigationKeysToTheShell', () => {
    const c = loaded();
    c.perform('ToggleVisibility', 0);
    expect(c.visible).toBe(false);
    expect(c.onKey(keyFor(c, 'FocusNext'), 1)).toBe(false);
  });

  test('refreshesOnShowAndEveryThirtySecondsWhileVisible', () => {
    const c = loaded();
    expect(c.shouldFetch(29_999)).toBe(false);
    expect(c.shouldFetch(30_000)).toBe(true);
    c.onFetched(snap({revision: 8}), 30_000);
    c.perform('ToggleVisibility', 40_000);
    expect(c.visible).toBe(false);
    expect(c.shouldFetch(100_000)).toBe(false);
    c.perform('ToggleVisibility', 100_000);
    expect(c.shouldFetch(100_000)).toBe(true);
  });

  test('hiddenPanelSuspendsUpdatesAndRefreshesOnShow', () => {
    const c = loaded();
    c.perform('ToggleVisibility', 1_000);
    expect(c.onFetched(snap({revision: 8, total: 99.0}), 2_000)).toEqual(PANEL_DELTA_NONE);
    expect(c.snapshot?.teamTotal.value).toBeCloseTo(14.8, 9);
    c.perform('ToggleVisibility', 3_000);
    expect(c.shouldFetch(3_000)).toBe(true);
    const d = c.onFetched(snap({revision: 8, total: 99.0}), 3_000);
    expect(d.totalsChanged).toBe(true);
    expect(c.snapshot?.teamTotal.value).toBeCloseTo(99.0, 9);
  });

  test('onlyChangedRowsAreReported', () => {
    const c = loaded();
    const d = c.onFetched(snap({revision: 8, rows: [prow('p-11', 12.3), prow('p-23', 4.5), prow('p-31', 4.0)], total: 20.8}), 1);
    expect(delta(d)).toEqual({changed: ['p-23'], removed: [], totals: true});
    expect(c.snapshot?.rows[1].points.value).toBeCloseTo(4.5, 9);
  });

  test('firstSnapshotReportsEveryRow', () => {
    const c = controller();
    expect(c.shouldFetch(0)).toBe(true);
    expect(delta(c.onFetched(snap(), 0))).toEqual({changed: ['p-11', 'p-23', 'p-31'], removed: [], totals: true});
  });

  test('starterChangeReportsAddedAndRemovedRowsOnly', () => {
    const c = loaded();
    const d = c.onFetched(snap({revision: 8, rows: [prow('p-11', 12.3), prow('p-23', -1.5), prow('p-44', 0.0)]}), 1);
    expect(delta(d)).toEqual({changed: ['p-44'], removed: ['p-31'], totals: false});
    expect(c.snapshot?.rows.map(r => r.playerId)).toEqual(['p-11', 'p-23', 'p-44']);
  });

  test('identicalOrOlderRevisionChangesNothing', () => {
    const c = loaded(controller(), snap({revision: 9}));
    expect(c.onFetched(snap({revision: 9}), 1)).toEqual(PANEL_DELTA_NONE);
    expect(c.onFetched(snap({revision: 8, total: 0.0}), 2)).toEqual(PANEL_DELTA_NONE);
    expect(c.snapshot?.teamTotal.value).toBeCloseTo(14.8, 9);
  });

  test('burstOfUpdatesHoldsOneSnapshotAndReportsOnlyTheChangedRow', () => {
    const c = loaded();
    let last: PanelDelta = PANEL_DELTA_NONE;
    for (let i = 1; i <= 10_000; i++) {
      last = c.onFetched(snap({revision: 7 + i, rows: [prow('p-11', 12.3 + i), prow('p-23', -1.5), prow('p-31', 4.0)]}), i);
      if ([...last.changedRows].join() !== 'p-11') expect({update: i, changed: [...last.changedRows]}).toEqual({update: i, changed: ['p-11']});
    }
    expect(c.snapshot?.rows.length).toBe(3);
    expect(c.snapshot?.rows[0].points.value).toBeCloseTo(10_012.3, 6);
    expect(c.snapshot?.revision).toBe(10_007);
    expect(last.totalsChanged).toBe(false);
  });
});
