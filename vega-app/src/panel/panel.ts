// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
import type {Envelope} from '../net/dto';

export type ScoringBasis = 'yahooLeague' | 'ppr' | 'halfPpr';

/** Unknown is a null value with a reason, never zero. */
export interface PanelValue {
  value: number | null;
  reason: string | null;
  source: string | null;
  asOfMs: number | null;
}

export interface PanelRow {
  playerId: string;
  name: string;
  points: PanelValue;
  gameStatus: string | null;
}

export interface PanelSnapshot {
  teamLeague: string;
  revision: number;
  basis: ScoringBasis;
  rows: PanelRow[];
  teamTotal: PanelValue;
  progress: PanelValue;
}

export function decodePanel(_state: Envelope): PanelSnapshot | null {
  return null;
}

export const PanelText = {
  value(_value: PanelValue, _nowMs: number): string {
    return '';
  },
  gameStatus(_status: string | null): string {
    return '';
  },
  basis(_basis: ScoringBasis): string {
    return '';
  },
};

/** Text sizes in px at the 1080p output. */
export const PanelTextSizes = {bodyPx: 0, scorePx: 0};

export type PanelMode = 'modeB' | 'fullScreen';

export function panelModeFor(_verdict: string | null): PanelMode | null {
  return null;
}

export interface Box {
  left: number;
  top: number;
  width: number;
  height: number;
}

export interface PanelLayout {
  panel: Box;
  video: Box | null;
}

export function panelLayout(_mode: PanelMode, _width: number, _height: number): PanelLayout {
  return {panel: {left: 0, top: 0, width: 0, height: 0}, video: null};
}

export type PanelAction = 'ToggleVisibility' | 'NextTeamLeague' | 'FocusNext' | 'FocusPrevious' | 'Select';

export const PANEL_ACTIONS: readonly PanelAction[] = [
  'ToggleVisibility',
  'NextTeamLeague',
  'FocusNext',
  'FocusPrevious',
  'Select',
];

export type FocusTarget =
  | {kind: 'teamLeagueSwitch'}
  | {kind: 'row'; playerId: string}
  | {kind: 'total'};

export interface PanelDelta {
  changedRows: ReadonlySet<string>;
  removedRows: ReadonlySet<string>;
  totalsChanged: boolean;
}

export const PANEL_DELTA_NONE: PanelDelta = {changedRows: new Set(), removedRows: new Set(), totalsChanged: false};

/** Remote keys are Vega HWEvent eventType names. */
export class PanelController {
  visible = false;
  teamLeague = '';
  snapshot: PanelSnapshot | null = null;
  focused: FocusTarget | null = null;

  constructor(_teamLeagues: string[], _initial: string, _visible: boolean) {}

  bindings(): ReadonlyMap<string, PanelAction> {
    return new Map();
  }

  onKey(_eventType: string, _nowMs: number): boolean {
    return false;
  }

  perform(_action: PanelAction, _nowMs: number): void {}

  shouldFetch(_nowMs: number): boolean {
    return false;
  }

  onFetched(_snapshot: PanelSnapshot, _nowMs: number): PanelDelta {
    return PANEL_DELTA_NONE;
  }

  focusTargets(): FocusTarget[] {
    return [];
  }
}
