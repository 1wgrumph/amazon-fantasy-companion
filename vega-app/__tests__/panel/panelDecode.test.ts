// AFC-PR-039/-040/-044/-062: GET /v1/panel data is untrusted; rows, total, progress and basis decode or nothing does.
// Mirrors PanelDecodeTest.kt.
import {ApiClient} from '../../src/net/apiClient';
import {decodePanel, PanelSnapshot} from '../../src/panel/panel';
import {node, withApi} from '../support/contract';
import {AS_OF_MS, envelope, panelData, row, state, TL, value} from '../support/panel';

const PANEL_ROWS_MAX = node('components', 'schemas', 'PanelData', 'properties', 'rows').maxItems as number;

function decoded(data = panelData()): PanelSnapshot {
  const snapshot = decodePanel(state(data));
  expect(snapshot).not.toBeNull();
  return snapshot!;
}

describe('PanelDecodeTest', () => {
  test('rowsTotalProgressAndBasisDecode', () => {
    const s = decoded();
    expect(s.teamLeague).toBe(TL);
    expect(s.revision).toBe(7);
    expect(s.basis).toBe('halfPpr');
    expect(s.rows.map(r => r.playerId)).toEqual(['p-11', 'p-23', 'p-31']);
    expect(s.rows[0].name).toBe('Player Eleven');
    expect(s.rows[0].points.value).toBeCloseTo(12.3, 9);
    expect(s.rows[1].points.value).toBeCloseTo(-1.5, 9);
    expect(s.rows[0].gameStatus).toBe('Q2 08:14');
    expect(s.rows[0].points.source).toBe('live');
    expect(s.rows[0].points.asOfMs).toBe(AS_OF_MS);
    expect(s.teamTotal.value).toBeCloseTo(10.8, 9);
    expect(s.progress.value).toBeCloseTo(0.5, 9);
  });

  test('eachScoringBasisDecodes', () => {
    const bases = node('components', 'schemas', 'PanelData', 'properties', 'scoringBasis').enum as string[];
    expect(bases).toEqual(['yahooLeague', 'ppr', 'halfPpr']);
    for (const basis of bases) expect(decodePanel(state(panelData({basis})))?.basis).toBe(basis);
  });

  test('nullPointsKeepTheirReasonAndAreNotZero', () => {
    const unknown = decoded().rows[2];
    expect(unknown.points.value).toBeNull();
    expect(unknown.points.reason).toBe('feed withheld');
    expect(unknown.gameStatus).toBeNull();
  });

  test('malformedValueBecomesUnavailableNotZero', () => {
    const s = decoded(
      panelData({rows: [row('p-11', 'Player Eleven', value('12')), row('p-23', 'Player Twenty-Three', {})], progress: value(1.7)}),
    );
    for (const r of s.rows) {
      expect({id: r.playerId, value: r.points.value}).toEqual({id: r.playerId, value: null});
      expect(r.points.reason?.trim()).toBeTruthy();
    }
    expect(s.progress.value).toBeNull();
    expect(s.progress.reason?.trim()).toBeTruthy();
  });

  test('missingOrUnknownBasisRejectsTheWholeState', () => {
    expect(decodePanel(state(panelData({basis: null})))).toBeNull();
    expect(decodePanel(state(panelData({basis: 'standard'})))).toBeNull();
    expect(decodePanel(state(panelData({basis: 'ppr'})))).not.toBeNull();
  });

  test('malformedRowsRejectTheState', () => {
    expect(decodePanel(state())).not.toBeNull();
    expect(decodePanel(state(panelData({rows: [{name: 'No Id', points: value(1.0)}]})))).toBeNull();
    expect(decodePanel(state(panelData({rows: [row('p-11', 'A', value(1.0)), row('p-11', 'B', value(2.0))]})))).toBeNull();
    expect(decodePanel(state({...panelData(), rows: 'p-11'}))).toBeNull();
  });

  test('rowCountIsBoundedByTheDeclaredLimit', () => {
    expect(PANEL_ROWS_MAX).toBe(32);
    const rows = (n: number) => Array.from({length: n}, (_, i) => row(`p-${i + 1}`, `Player ${i + 1}`, value(1.0)));
    const atLimit = decodePanel(state(panelData({rows: rows(PANEL_ROWS_MAX)})));
    expect(atLimit).not.toBeNull();
    expect(atLimit!.rows).toHaveLength(PANEL_ROWS_MAX);
    expect(decodePanel(state(panelData({rows: rows(PANEL_ROWS_MAX + 1)})))).toBeNull();
  });

  test('panelFeedDecodesOverTheApiClientForTheSelectedTeamLeague', () =>
    withApi([[200, JSON.stringify(envelope(panelData()))]], async api => {
      const result = await new ApiClient(api.baseUrl, {token: () => 'session-fixture'}).getPanel(TL);
      expect(result.status).toBe(200);
      expect(api.requests.map(r => r.path)).toEqual(['/v1/panel?teamLeague=league-a%2Fteam-7']);
      expect(result.value).not.toBeNull();
      const s = decodePanel(result.value!);
      expect(s).not.toBeNull();
      expect(s!.rows).toHaveLength(3);
    }));
});
