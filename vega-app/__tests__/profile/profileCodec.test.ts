// PROFILE settings codec: every control round-trips through its frozen Settings field (mirrors ProfileCodecTest.kt).
import {
  decodeProfile,
  encodeProfile,
  EXCITEMENT_LEVELS,
  PRESENTATIONS,
  ProfileState,
  SCORING_PRESETS,
} from '../../src/profile/profile';
import {node} from '../support/contract';
import {customized} from '../support/profile';

const settingsSchema = node('components', 'schemas', 'Settings');
const CONTROLS = Object.keys(settingsSchema.properties).filter(field => field !== 'scoringPreset');

function roundTrip(state: ProfileState): ProfileState | null {
  return decodeProfile(JSON.parse(JSON.stringify(encodeProfile(state))));
}

describe('ProfileCodecTest', () => {
  test('emptySettingsDecodeToDocumentedDefaults', () => {
    const defaults = decodeProfile({});
    expect(defaults).not.toBeNull();
    expect(defaults?.scoringPreset).toBe(settingsSchema.properties.scoringPreset.default);
    expect(defaults?.scoringPreset).toBe('halfPpr');
    expect(defaults?.minGapSeconds).toBe(120);
    expect(defaults?.spoilerDelaySeconds).toBe(0);
    expect(defaults?.switchingConfirm).toBe(true);
    expect(defaults?.detectionOptIn).toBe(false);
    expect(defaults?.voiceEnabled).toBe(false);
  });

  test('everyControlRoundTrips', () => {
    expect(roundTrip(customized())).toEqual(customized());
  });

  test('eachExcitementLevelRoundTrips', () => {
    expect(EXCITEMENT_LEVELS).toEqual(['Off', 'Mild', 'Hype']);
    for (const level of EXCITEMENT_LEVELS) expect(roundTrip({...customized(), excitement: level})?.excitement).toBe(level);
  });

  test('eachScoringPresetRoundTripsWithFrozenWire', () => {
    expect(SCORING_PRESETS).toEqual(settingsSchema.properties.scoringPreset.enum);
    for (const preset of SCORING_PRESETS) {
      const state = {...customized(), scoringPreset: preset};
      expect(encodeProfile(state).scoringPreset).toBe(preset);
      expect(roundTrip(state)?.scoringPreset).toBe(preset);
    }
  });

  test('eachPresentationRoundTrips', () => {
    for (const choice of PRESENTATIONS) expect(roundTrip({...customized(), presentation: choice})?.presentation).toBe(choice);
  });

  // Each control lives in its own Settings field, which the backend policy reads; changing one changes only that field.
  test('eachControlWritesOnlyItsOwnSettingsField', () => {
    const base = customized();
    const changes: Record<string, ProfileState> = {
      fantasySelections: {...base, selections: {...base.selections, players: new Set(['player-99'])}},
      teamLeague: {...base, teamLeague: {league: 'league-b', team: 'team-2'}},
      alertTypes: {...base, alertTypes: new Set(['PlayerScore'])},
      frequency: {...base, minGapSeconds: 600},
      quietHours: {...base, quietHours: [{startMinute: 0, endMinute: 360}]},
      gameDayPeriods: {...base, gameDay: {...base.gameDay, enabled: false}},
      spoilerDelay: {...base, spoilerDelaySeconds: 120},
      presentation: {...base, presentation: 'HeadsUp'},
      voice: {...base, voiceEnabled: false},
      excitement: {...base, excitement: 'Mild'},
      providerPref: {...base, providerPref: {...base.providerPref, order: ['provider-a', 'provider-b']}},
      switchingConfirm: {...base, switchingConfirm: true},
      panelPrefs: {...base, panel: {visible: true}},
      detectionOptIn: {...base, detectionOptIn: false},
      scoringPreset: {...base, scoringPreset: 'halfPpr'},
    };
    expect(new Set(Object.keys(changes))).toEqual(new Set([...CONTROLS, 'scoringPreset']));
    const before = encodeProfile(base);
    for (const [field, changed] of Object.entries(changes)) {
      const after = encodeProfile(changed);
      const keys = new Set([...Object.keys(before), ...Object.keys(after)]);
      const differing = [...keys].filter(key => JSON.stringify(before[key]) !== JSON.stringify(after[key]));
      expect({field, differing}).toEqual({field, differing: [field]});
    }
  });

  test('overridesAndLocalMarketRoundTrip', () => {
    const decoded = roundTrip(customized());
    expect(decoded?.providerPref.appOverrides).toEqual(customized().providerPref.appOverrides);
    expect(decoded?.providerPref.localMarket).toBe('market-501');
  });

  // Persisted settings are untrusted input: a wrong-typed control is rejected whole, never partially applied.
  test('wrongTypedControlIsRejected', () => {
    const valid = encodeProfile(customized());
    for (const field of CONTROLS) {
      const bad = typeof valid[field] === 'string' ? 12345 : 'ludicrous';
      expect({field, decoded: decodeProfile({...valid, [field]: bad})}).toEqual({field, decoded: null});
    }
  });

  test('outOfRangeValuesCannotBeEncoded', () => {
    const base = customized();
    expect(() => encodeProfile({...base, minGapSeconds: 601})).toThrow(RangeError);
    expect(() => encodeProfile({...base, minGapSeconds: -1})).toThrow(RangeError);
    expect(() => encodeProfile({...base, spoilerDelaySeconds: 121})).toThrow(RangeError);
    expect(() => encodeProfile({...base, quietHours: [{startMinute: 0, endMinute: 1440}]})).toThrow(RangeError);
    const boundary = {...base, minGapSeconds: 600, spoilerDelaySeconds: 120, quietHours: [{startMinute: 0, endMinute: 1439}]};
    expect(roundTrip(boundary)).toEqual(boundary);
  });
});
