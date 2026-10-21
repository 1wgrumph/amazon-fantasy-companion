// PROFILE: one control per frozen Settings field. Persisted settings are untrusted: decode
// validates every present field's type, enum and range and returns null whole on any violation.
import type {ApiClient} from '../net/apiClient';
import {decodeEnvelope, isRecord} from '../net/dto';
import type {JsonObject} from '../net/dto';

export type AlertType = 'RedZone' | 'PlayerScore' | 'CloseGame';
export type Presentation = 'HeadsUp' | 'PanelOnly';
export type Excitement = 'Off' | 'Mild' | 'Hype';
/** Settings.scoringPreset wire values. */
export type ScoringPreset = 'ppr' | 'halfPpr';

export const PRESENTATIONS: readonly Presentation[] = ['HeadsUp', 'PanelOnly'];
export const EXCITEMENT_LEVELS: readonly Excitement[] = ['Off', 'Mild', 'Hype'];
export const SCORING_PRESETS: readonly ScoringPreset[] = ['ppr', 'halfPpr'];
const ALERT_TYPES: readonly AlertType[] = ['RedZone', 'PlayerScore', 'CloseGame'];

/** Minutes of the local day, 0..1439; a window may wrap past midnight. */
export interface TimeWindow {
  startMinute: number;
  endMinute: number;
}

export interface FantasySelections {
  leagues: ReadonlySet<string>;
  teams: ReadonlySet<string>;
  players: ReadonlySet<string>;
  favoriteTeams: ReadonlySet<string>;
}

export interface TeamLeague {
  league: string;
  team: string;
}

export interface GameDayMode {
  enabled: boolean;
  periods: TimeWindow[];
}

export interface ProviderPreference {
  order: string[];
  confirmedAccess: ReadonlySet<string>;
  appOverrides: Record<string, boolean>;
  localMarket: string | null;
}

export interface PanelPrefs {
  visible: boolean;
}

export interface ProfileState {
  selections: FantasySelections;
  teamLeague: TeamLeague | null;
  alertTypes: ReadonlySet<AlertType>;
  minGapSeconds: number;
  quietHours: TimeWindow[];
  gameDay: GameDayMode;
  spoilerDelaySeconds: number;
  presentation: Presentation;
  voiceEnabled: boolean;
  excitement: Excitement;
  providerPref: ProviderPreference;
  switchingConfirm: boolean;
  panel: PanelPrefs;
  detectionOptIn: boolean;
  scoringPreset: ScoringPreset;
}

const CONTROL_FIELDS = new Set([
  'fantasySelections', 'teamLeague', 'alertTypes', 'frequency', 'quietHours', 'gameDayPeriods',
  'spoilerDelay', 'presentation', 'voice', 'excitement', 'providerPref', 'switchingConfirm',
  'panelPrefs', 'detectionOptIn',
]);
const SELECTION_KEYS = new Set(['leagues', 'teams', 'players', 'favoriteTeams']);

function intIn(value: unknown, min: number, max: number): number | null {
  return typeof value === 'number' && Number.isInteger(value) && value >= min && value <= max ? value : null;
}

function strings(value: unknown): string[] | null {
  if (!Array.isArray(value)) return null;
  return value.every(item => typeof item === 'string') ? (value as string[]) : null;
}

function stringSet(obj: Record<string, unknown>, key: string): ReadonlySet<string> | null {
  const list = strings(obj[key]);
  return list === null ? null : new Set(list);
}

function windows(value: unknown): TimeWindow[] | null {
  if (!Array.isArray(value)) return null;
  const result: TimeWindow[] = [];
  for (const item of value) {
    if (!isRecord(item)) return null;
    const startMinute = intIn(item.startMinute, 0, 1439);
    const endMinute = intIn(item.endMinute, 0, 1439);
    if (startMinute === null || endMinute === null) return null;
    result.push({startMinute, endMinute});
  }
  return result;
}

/** Absent yields the default; present must parse or the whole decode fails. */
function field<T>(c: Record<string, unknown>, key: string, fallback: T, parse: (value: unknown) => T | null): T | null {
  return key in c ? parse(c[key]) : fallback;
}

/** Encodes every control into its own frozen Settings field; throws on an out-of-range value. */
export function encodeProfile(state: ProfileState): JsonObject {
  const requireRange = (value: number, min: number, max: number, what: string) => {
    if (!Number.isInteger(value) || value < min || value > max) throw new RangeError(`${what} out of range`);
  };
  requireRange(state.minGapSeconds, 0, 600, 'alert_min_gap');
  requireRange(state.spoilerDelaySeconds, 0, 120, 'spoiler_delay');
  for (const window of [...state.quietHours, ...state.gameDay.periods]) {
    requireRange(window.startMinute, 0, 1439, 'minute of day');
    requireRange(window.endMinute, 0, 1439, 'minute of day');
  }
  const windowsJson = (list: TimeWindow[]) => list.map(w => ({startMinute: w.startMinute, endMinute: w.endMinute}));
  return {
    fantasySelections: {
      leagues: [...state.selections.leagues],
      teams: [...state.selections.teams],
      players: [...state.selections.players],
      favoriteTeams: [...state.selections.favoriteTeams],
    },
    teamLeague: state.teamLeague === null ? null : {league: state.teamLeague.league, team: state.teamLeague.team},
    alertTypes: [...state.alertTypes],
    frequency: state.minGapSeconds,
    quietHours: windowsJson(state.quietHours),
    gameDayPeriods: {enabled: state.gameDay.enabled, periods: windowsJson(state.gameDay.periods)},
    spoilerDelay: state.spoilerDelaySeconds,
    presentation: state.presentation,
    voice: state.voiceEnabled,
    excitement: state.excitement,
    providerPref: {
      order: [...state.providerPref.order],
      confirmedAccess: [...state.providerPref.confirmedAccess],
      appOverrides: {...state.providerPref.appOverrides},
      localMarket: state.providerPref.localMarket,
    },
    switchingConfirm: state.switchingConfirm,
    panelPrefs: {visible: state.panel.visible},
    detectionOptIn: state.detectionOptIn,
    scoringPreset: state.scoringPreset,
  } as JsonObject;
}

/** Persisted Settings are untrusted: any invalid field rejects the whole profile. */
export function decodeProfile(settings: JsonObject): ProfileState | null {
  const c = settings as Record<string, unknown>;
  if (!Object.keys(c).every(key => key === 'scoringPreset' || CONTROL_FIELDS.has(key))) return null;
  const presetRaw = 'scoringPreset' in c ? c.scoringPreset : 'halfPpr';
  const scoringPreset = SCORING_PRESETS.find(p => p === presetRaw);
  if (scoringPreset === undefined) return null;

  const selections = field<FantasySelections>(
    c, 'fantasySelections',
    {leagues: new Set(), teams: new Set(), players: new Set(), favoriteTeams: new Set()},
    value => {
      if (!isRecord(value) || !Object.keys(value).every(key => SELECTION_KEYS.has(key))) return null;
      const leagues = stringSet(value, 'leagues');
      const teams = stringSet(value, 'teams');
      const players = stringSet(value, 'players');
      const favoriteTeams = stringSet(value, 'favoriteTeams');
      return leagues === null || teams === null || players === null || favoriteTeams === null
        ? null
        : {leagues, teams, players, favoriteTeams};
    },
  );
  if (selections === null) return null;

  let teamLeague: TeamLeague | null = null;
  if ('teamLeague' in c && c.teamLeague !== null) {
    const o = c.teamLeague;
    if (!isRecord(o) || typeof o.league !== 'string' || typeof o.team !== 'string') return null;
    teamLeague = {league: o.league, team: o.team};
  }

  const alertTypes = field<ReadonlySet<AlertType>>(c, 'alertTypes', new Set(), value => {
    const names = strings(value);
    if (names === null) return null;
    const result = new Set<AlertType>();
    for (const name of names) {
      const found = ALERT_TYPES.find(t => t === name);
      if (found === undefined) return null;
      result.add(found);
    }
    return result;
  });
  if (alertTypes === null) return null;

  const minGapSeconds = field(c, 'frequency', 120, value => intIn(value, 0, 600));
  if (minGapSeconds === null) return null;
  const quietHours = field<TimeWindow[]>(c, 'quietHours', [], windows);
  if (quietHours === null) return null;
  const gameDay = field<GameDayMode>(c, 'gameDayPeriods', {enabled: false, periods: []}, value => {
    if (!isRecord(value) || typeof value.enabled !== 'boolean') return null;
    const periods = windows(value.periods);
    return periods === null ? null : {enabled: value.enabled, periods};
  });
  if (gameDay === null) return null;
  const spoilerDelaySeconds = field(c, 'spoilerDelay', 0, value => intIn(value, 0, 120));
  if (spoilerDelaySeconds === null) return null;
  const presentation = field<Presentation>(c, 'presentation', 'HeadsUp', value =>
    PRESENTATIONS.find(p => p === value) ?? null,
  );
  if (presentation === null) return null;
  const voiceEnabled = field(c, 'voice', false, value => (typeof value === 'boolean' ? value : null));
  if (voiceEnabled === null) return null;
  const excitement = field<Excitement>(c, 'excitement', 'Off', value =>
    EXCITEMENT_LEVELS.find(e => e === value) ?? null,
  );
  if (excitement === null) return null;
  const providerPref = field<ProviderPreference>(
    c, 'providerPref',
    {order: [], confirmedAccess: new Set(), appOverrides: {}, localMarket: null},
    value => {
      if (!isRecord(value) || !isRecord(value.appOverrides)) return null;
      const appOverrides: Record<string, boolean> = {};
      for (const [key, entry] of Object.entries(value.appOverrides)) {
        if (typeof entry !== 'boolean') return null;
        appOverrides[key] = entry;
      }
      if (!('localMarket' in value)) return null;
      const localMarket = value.localMarket === null ? null : typeof value.localMarket === 'string' ? value.localMarket : undefined;
      if (localMarket === undefined) return null;
      const order = strings(value.order);
      const confirmedAccess = stringSet(value, 'confirmedAccess');
      return order === null || confirmedAccess === null ? null : {order, confirmedAccess, appOverrides, localMarket};
    },
  );
  if (providerPref === null) return null;
  const switchingConfirm = field(c, 'switchingConfirm', true, value => (typeof value === 'boolean' ? value : null));
  if (switchingConfirm === null) return null;
  const panel = field<PanelPrefs>(c, 'panelPrefs', {visible: true}, value =>
    isRecord(value) && typeof value.visible === 'boolean' ? {visible: value.visible} : null,
  );
  if (panel === null) return null;
  const detectionOptIn = field(c, 'detectionOptIn', false, value => (typeof value === 'boolean' ? value : null));
  if (detectionOptIn === null) return null;

  return {
    selections, teamLeague, alertTypes, minGapSeconds, quietHours, gameDay, spoilerDelaySeconds,
    presentation, voiceEnabled, excitement, providerPref, switchingConfirm, panel, detectionOptIn, scoringPreset,
  };
}

export function voiceActive(state: ProfileState, routeVerified: boolean): boolean {
  return state.voiceEnabled && routeVerified;
}

/** Detected apps with the customer's overrides applied. */
export function effectiveInstalled(state: ProfileState, detected: ReadonlySet<string>): ReadonlySet<string> {
  const result = new Set<string>();
  for (const name of detected) {
    if (state.providerPref.appOverrides[name] !== false) result.add(name);
  }
  for (const [name, installed] of Object.entries(state.providerPref.appOverrides)) {
    if (installed) result.add(name);
  }
  return result;
}

export type ProfileControl =
  | 'Selections'
  | 'TeamLeague'
  | 'AlertTypes'
  | 'Frequency'
  | 'QuietHours'
  | 'GameDay'
  | 'SpoilerDelay'
  | 'Presentation'
  | 'Voice'
  | 'Excitement'
  | 'ProviderPreference'
  | 'SwitchingConfirmation'
  | 'DetectionOptIn'
  | 'PanelVisibility'
  | 'ScoringPreset';

export const PROFILE_CONTROLS: readonly ProfileControl[] = [
  'Selections', 'TeamLeague', 'AlertTypes', 'Frequency', 'QuietHours', 'GameDay', 'SpoilerDelay',
  'Presentation', 'Voice', 'Excitement', 'ProviderPreference', 'SwitchingConfirmation',
  'DetectionOptIn', 'PanelVisibility', 'ScoringPreset',
];

export interface ProfileControls {
  visible: ProfileControl[];
  limits: Partial<Record<ProfileControl, string>>;
}

export function profileControls(routes: {detectionSupported: boolean; voiceRouteVerified: boolean}): ProfileControls {
  const limits: Partial<Record<ProfileControl, string>> = {};
  if (!routes.detectionSupported) {
    limits.DetectionOptIn = 'Installed-app detection is not supported on this device, so detection cannot be enabled here.';
  }
  if (!routes.voiceRouteVerified) {
    limits.Voice = 'No verified voice route is available on this device, so voice alerts cannot be enabled here.';
  }
  return {visible: PROFILE_CONTROLS.filter(control => !(control in limits)), limits};
}

/** GET/PUT /v1/profile; save writes against the revision held from load. Null when unavailable, invalid or stale. */
export class ProfileStore {
  private revision: number | null = null;

  constructor(private readonly client: ApiClient) {}

  async load(): Promise<ProfileState | null> {
    try {
      const response = await this.client.request('GET', '/v1/profile');
      if (response.status < 200 || response.status > 299 || response.body === null) return null;
      const envelope = decodeEnvelope(response.body);
      if (envelope === null) return null;
      const state = decodeProfile(envelope.data);
      if (state === null) return null;
      this.revision = envelope.revision;
      return state;
    } catch {
      return null;
    }
  }

  /** Saves over the loaded revision; a stale revision returns null. */
  async save(state: ProfileState): Promise<ProfileState | null> {
    try {
      let held = this.revision;
      if (held === null) {
        if ((await this.load()) === null) return null;
        held = this.revision;
        if (held === null) return null;
      }
      const response = await this.client.request('PUT', '/v1/profile', {revision: held, data: encodeProfile(state)});
      if (response.status < 200 || response.status > 299 || response.body === null) return null;
      const envelope = decodeEnvelope(response.body, held);
      if (envelope === null) return null;
      const stored = decodeProfile(envelope.data);
      if (stored === null) return null;
      this.revision = envelope.revision;
      return stored;
    } catch {
      return null;
    }
  }
}
