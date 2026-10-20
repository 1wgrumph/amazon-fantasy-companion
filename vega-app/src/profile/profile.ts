// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
import type {ApiClient} from '../net/apiClient';
import type {JsonObject} from '../net/dto';

export type AlertType = 'RedZone' | 'PlayerScore' | 'CloseGame';
export type Presentation = 'HeadsUp' | 'PanelOnly';
export type Excitement = 'Off' | 'Mild' | 'Hype';
/** Settings.scoringPreset wire values. */
export type ScoringPreset = 'ppr' | 'halfPpr';

export const PRESENTATIONS: readonly Presentation[] = ['HeadsUp', 'PanelOnly'];
export const EXCITEMENT_LEVELS: readonly Excitement[] = ['Off', 'Mild', 'Hype'];
export const SCORING_PRESETS: readonly ScoringPreset[] = ['ppr', 'halfPpr'];

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

/** Encodes every control into its own frozen Settings field; throws on an out-of-range value. */
export function encodeProfile(_state: ProfileState): JsonObject {
  return {};
}

/** Persisted Settings are untrusted: any invalid field rejects the whole profile. */
export function decodeProfile(_settings: JsonObject): ProfileState | null {
  return null;
}

export function voiceActive(_state: ProfileState, _routeVerified: boolean): boolean {
  return false;
}

/** Detected apps with the customer's overrides applied. */
export function effectiveInstalled(_state: ProfileState, _detected: ReadonlySet<string>): ReadonlySet<string> {
  return new Set();
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
  'Selections',
  'TeamLeague',
  'AlertTypes',
  'Frequency',
  'QuietHours',
  'GameDay',
  'SpoilerDelay',
  'Presentation',
  'Voice',
  'Excitement',
  'ProviderPreference',
  'SwitchingConfirmation',
  'DetectionOptIn',
  'PanelVisibility',
  'ScoringPreset',
];

export interface ProfileControls {
  visible: ProfileControl[];
  limits: Partial<Record<ProfileControl, string>>;
}

export function profileControls(_routes: {detectionSupported: boolean; voiceRouteVerified: boolean}): ProfileControls {
  return {visible: [], limits: {}};
}

export class ProfileStore {
  constructor(_client: ApiClient) {}

  async load(): Promise<ProfileState | null> {
    return null;
  }

  /** Saves over the loaded revision; a stale revision returns null. */
  async save(_state: ProfileState): Promise<ProfileState | null> {
    return null;
  }
}
