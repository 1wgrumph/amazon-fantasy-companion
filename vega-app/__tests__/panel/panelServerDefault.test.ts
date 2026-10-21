// BUG AFC-M14-PANEL-DEFAULT: a profile with no team/league selection fetches GET /v1/panel with no query and the
// backend answers with its default team/league. The controller must hold that snapshot, not drop it and refetch
// every tick. The body is the one recorded on the VVD (m14-vega-i7/panel/05-panel-no-teamleague.json).
import {readFileSync} from 'fs';
import {join} from 'path';
import {decodeEnvelope} from '../../src/net/dto';
import {decodePanel, PanelController, PanelSnapshot} from '../../src/panel/panel';

const REFRESH_MS = 30_000;

function recordedDefault(): PanelSnapshot {
  const envelope = decodeEnvelope(JSON.parse(readFileSync(join(__dirname, '..', 'fixtures', 'panel-no-teamleague.json'), 'utf8')));
  expect(envelope).not.toBeNull();
  const snapshot = decodePanel(envelope!);
  expect(snapshot).not.toBeNull();
  return snapshot!;
}

describe('PanelServerDefaultTest', () => {
  test('noSelectionControllerHoldsTheServerDefaultSnapshot', () => {
    const body = recordedDefault();
    expect(body.teamLeague).toBe('unassigned/unassigned');
    // App.tsx builds this for a profile with no team/league selection.
    const c = new PanelController([], '', true);
    expect(c.shouldFetch(0)).toBe(true);
    c.onFetched(body, 0);
    expect(c.snapshot?.teamLeague ?? null).toBe('unassigned/unassigned');
    expect(c.shouldFetch(1_000)).toBe(false);
    expect(c.shouldFetch(REFRESH_MS - 1)).toBe(false);
    expect(c.shouldFetch(REFRESH_MS)).toBe(true);
  });

  test('explicitSelectionStillIgnoresASnapshotForAnotherTeamLeague', () => {
    const c = new PanelController(['league-a/team-1'], 'league-a/team-1', true);
    c.onFetched(recordedDefault(), 0);
    expect(c.snapshot).toBeNull();
    expect(c.teamLeague).toBe('league-a/team-1');
    expect(c.shouldFetch(1_000)).toBe(true);
  });
});
