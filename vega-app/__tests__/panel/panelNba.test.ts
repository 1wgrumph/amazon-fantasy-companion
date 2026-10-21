// M14 Vega NBA panel parity (P2-V01 follow-up): mirrors NbaPanelTest.kt (#138). The optional `sport` field travels
// in the panel `data` object beside `scoringBasis`, as backend/src/panel builds it; CONTRACT-AFC-P2-ENVELOPE is unchanged.
//
// NBA-enabled assumption (Vega has no equivalent yet): Vega mirrors Fire OS's BuildConfig.AFC_ENABLE_NBA seam as
//   - `AFC_ENABLE_NBA: boolean` exported from src/config.ts (build-time config, like AFC_API_BASE_URL), shipped on, and
//   - `decodePanel(state, nbaEnabled = AFC_ENABLE_NBA)`, so both flag states are exercised without a rebuild.
// A decoded snapshot carries `sport: 'NBA' | 'NFL' | null` (null: no label), as PanelSnapshot.sport does on Fire OS.
// The recorded-shape body (fixtures/panel-nba-points.json) follows the backend snapshot builder for a manual NBA
// lineup: three starters, one without statistics for the current game, so the team total is unknown.
import {readFileSync} from 'fs';
import {join} from 'path';
import * as config from '../../src/config';
import {decodeEnvelope} from '../../src/net/dto';
import type {Envelope} from '../../src/net/dto';
import {decodePanel, PanelText} from '../../src/panel/panel';
import type {PanelSnapshot} from '../../src/panel/panel';
import {panelData, state} from '../support/panel';

type NbaSnapshot = PanelSnapshot & {sport?: string | null};
// The seam under test; HEAD has only decodePanel(state).
const decode = decodePanel as unknown as (state: Envelope, nbaEnabled?: boolean) => NbaSnapshot | null;
const basisText = PanelText.basis as (basis: string) => string;
const NFL_BASES = ['yahooLeague', 'ppr', 'halfPpr'];

function recorded(): Envelope {
  const envelope = decodeEnvelope(JSON.parse(readFileSync(join(__dirname, '..', 'fixtures', 'panel-nba-points.json'), 'utf8')));
  expect(envelope).not.toBeNull();
  return envelope!;
}

/** Patches the recorded data; an undefined value removes the key (an absent `sport` field). */
function withData(envelope: Envelope, patch: Record<string, unknown>): Envelope {
  const data: Record<string, unknown> = {...envelope.data, ...patch};
  for (const key of Object.keys(patch)) if (patch[key] === undefined) delete data[key];
  return {...envelope, data: data as Envelope['data']};
}

function nba(envelope: Envelope = recorded()): NbaSnapshot {
  const snapshot = decode(envelope, true);
  expect(snapshot).not.toBeNull(); // Missing behavior: with NBA enabled, an NBA panel decodes.
  return snapshot!;
}

const nflWithSport = (basis: string, sport: unknown) => state({...panelData({basis}), sport});

describe('NbaPanelTest', () => {
  test('flagDefaultsOnAndTheDefaultDecodeFollowsIt', () => {
    const flag = (config as Record<string, unknown>).AFC_ENABLE_NBA;
    expect(flag).toBe(true);
    expect(decode(recorded())).not.toBeNull();
    expect(decode(state())).not.toBeNull(); // NFL still decodes with the default flag.
  });

  test('recordedNbaPointsBodyDecodesWithTheNbaLabel', () => {
    const s = nba();
    expect(s.basis).toBe('nbaPoints');
    expect(s.sport).toBe('NBA');
    expect(s.teamLeague).toBe('manual/nba-starters');
    expect(s.revision).toBe(512);
    expect(s.rows.map(r => r.playerId)).toEqual(['3112335', '3945274', '4065648']);
    expect(s.rows[0].points.value).toBeCloseTo(55.9, 9);
    expect(s.rows[1].gameStatus).toBe('Q3 04:27');
  });

  test('nbaUnknownValuesStayUnavailableNeverZero', () => {
    const s = nba();
    expect(s.rows[2].points.value).toBeNull();
    expect(s.rows[2].points.reason).toBe('no statistics for current game');
    expect(s.teamTotal.value).toBeNull();
    expect(s.teamTotal.reason).toBe('team total unavailable');
    expect(PanelText.value(s.rows[2].points, Date.parse('2026-10-21T03:41:45Z'))).toBe('Unavailable');
  });

  test('sportFieldSetsTheLabelForAYahooNbaLeague', () => {
    const yahoo = nba(withData(recorded(), {scoringBasis: 'yahooLeague'}));
    expect(yahoo.basis).toBe('yahooLeague');
    expect(yahoo.sport).toBe('NBA');
    expect(nba(withData(recorded(), {sport: undefined})).sport).toBe('NBA'); // nbaPoints alone implies NBA.
    expect(decode(nflWithSport('ppr', 'nfl'), true)?.sport).toBe('NFL');
  });

  test('nflTagUnderNbaPointsRejectsTheWholeState', () => {
    expect(nba(withData(recorded(), {sport: 'nba'})).sport).toBe('NBA'); // Control: the matching tag decodes.
    expect(decode(withData(recorded(), {sport: 'nfl'}), true)).toBeNull();
  });

  test('unknownOrMalformedSportRejectsTheWholeState', () => {
    nba(); // Control: the recorded body decodes, so each rejection below is the sport field's.
    for (const sport of ['mlb', 'NBA', 5]) {
      expect(decode(withData(recorded(), {sport}), true)).toBeNull();
      expect(decode(nflWithSport('halfPpr', sport), true)).toBeNull(); // Validated under an NFL basis too.
    }
  });

  test('nbaPointsBasisTextIsPointsAndDistinctFromNfl', () => {
    expect(basisText('nbaPoints')).toBe('Points');
    expect(NFL_BASES.map(basisText)).not.toContain('Points');
  });

  test('flagOffRejectsNbaAndIgnoresSport', () => {
    expect(decode(recorded(), false)).toBeNull();
    expect(decode(withData(recorded(), {sport: undefined}), false)).toBeNull();
    const plain = decode(state(), false);
    expect(plain).not.toBeNull();
    expect(plain!.sport ?? null).toBeNull();
    for (const sport of ['nba', 'nfl', 'mlb', 5]) expect(decode(nflWithSport('halfPpr', sport), false)).toEqual(plain);
  });

  test('nflDecodeAndBasisTextMatchAcrossFlagStates', () => {
    for (const basis of NFL_BASES) {
      const off = decode(state(panelData({basis})), false);
      const on = decode(state(panelData({basis})), true);
      expect(off).not.toBeNull();
      expect(on).toEqual(off);
      expect(on!.sport ?? null).toBeNull(); // No sport field, no label.
    }
    expect(NFL_BASES.map(basisText)).toEqual(['Yahoo league scoring', 'PPR', 'Half-PPR']);
  });
});
