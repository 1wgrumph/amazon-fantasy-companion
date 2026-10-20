// DES-AFC-P2-PANEL host logic. Panel state from the API is untrusted: identity/basis/bounds
// violations reject the whole state, while a malformed value becomes unavailable, never zero.
import {isRecord} from '../net/dto';
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

const PANEL_ROWS_MAX = 32;
const STALE_AFTER_MS = 60_000;
const REFRESH_MS = 30_000;

const INSTANT = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?(Z|[+-]\d{2}:\d{2})$/;

function parseInstantMs(text: unknown): number | null {
  if (typeof text !== 'string') return null;
  const match = INSTANT.exec(text);
  if (match === null) return null;
  const offset = match[8];
  if (offset !== 'Z') {
    const [hours, minutes] = offset.slice(1).split(':').map(Number);
    if (hours > 23 || minutes > 59) return null;
  }
  const ms = Date.parse(text);
  return Number.isFinite(ms) ? ms : null;
}

/** A malformed or absent numeric value is unknown with a reason; only a JSON number is a value. */
function panelValue(obj: unknown): PanelValue {
  if (!isRecord(obj)) return {value: null, reason: 'unavailable', source: null, asOfMs: null};
  const number = typeof obj.value === 'number' && Number.isFinite(obj.value) ? obj.value : null;
  const reason = typeof obj.reason === 'string' && obj.reason.trim() !== '' ? obj.reason : null;
  const source = typeof obj.source === 'string' ? obj.source : null;
  const asOfMs = parseInstantMs(obj.asOf);
  return number !== null
    ? {value: number, reason, source, asOfMs}
    : {value: null, reason: reason ?? 'unavailable', source, asOfMs};
}

/** Decodes GET /v1/panel data; null when malformed, oversized or missing its scoring basis. */
export function decodePanel(state: Envelope): PanelSnapshot | null {
  const data = state.data as Record<string, unknown>;
  const teamLeague = typeof data.teamLeague === 'string' && data.teamLeague.trim() !== '' ? data.teamLeague : null;
  if (teamLeague === null) return null;
  const basis = data.scoringBasis;
  if (basis !== 'yahooLeague' && basis !== 'ppr' && basis !== 'halfPpr') return null;
  const rawRows = data.rows;
  if (!Array.isArray(rawRows) || rawRows.length > PANEL_ROWS_MAX) return null;
  const seen = new Set<string>();
  const rows: PanelRow[] = [];
  for (const raw of rawRows) {
    if (!isRecord(raw)) return null;
    const playerId = typeof raw.playerId === 'string' && raw.playerId.trim() !== '' ? raw.playerId : null;
    if (playerId === null || seen.has(playerId)) return null;
    seen.add(playerId);
    if (typeof raw.name !== 'string') return null;
    const gameStatus = typeof raw.gameStatus === 'string' ? raw.gameStatus : null;
    rows.push({playerId, name: raw.name, points: panelValue(raw.points), gameStatus});
  }
  let progress = panelValue(data.progress);
  if (progress.value !== null && (progress.value < 0 || progress.value > 1)) {
    progress = {...progress, value: null, reason: progress.reason ?? 'progress out of range'};
  }
  return {
    teamLeague,
    revision: state.revision,
    basis,
    rows,
    teamTotal: panelValue(data.teamTotal),
    progress,
  };
}

export const PanelText = {
  value(value: PanelValue, nowMs: number): string {
    if (value.value === null) return 'Unavailable';
    const text = String(value.value);
    const provenance = value.source === 'replay' ? 'replay' : null;
    const stale =
      value.asOfMs === null
        ? 'stale'
        : nowMs - value.asOfMs >= STALE_AFTER_MS
          ? `stale ${Math.floor((nowMs - value.asOfMs) / 1_000)}s`
          : null;
    const labels = [provenance, stale].filter((label): label is string => label !== null);
    return labels.length === 0 ? text : `${text} (${labels.join(', ')})`;
  },
  gameStatus(status: string | null): string {
    return status !== null && status.trim() !== '' ? status : 'Unavailable';
  },
  basis(basis: ScoringBasis): string {
    switch (basis) {
      case 'yahooLeague':
        return 'Yahoo league scoring';
      case 'ppr':
        return 'PPR';
      case 'halfPpr':
        return 'Half-PPR';
    }
  },
};

/** Text sizes in px at the 1080p output. */
export const PanelTextSizes = {bodyPx: 24, scorePx: 32};

export type PanelMode = 'modeB' | 'fullScreen';

/** The P2-X04 verdict selects the mode; anything but a modeB verdict is fullScreen. */
export function panelModeFor(verdict: string | null): PanelMode {
  return verdict === 'modeB' ? 'modeB' : 'fullScreen';
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

/** video is null in fullScreen: no stand-in video. modeB fits the video left at 16:9, panel right. */
export function panelLayout(mode: PanelMode, width: number, height: number): PanelLayout {
  if (mode === 'fullScreen') return {panel: {left: 0, top: 0, width, height}, video: null};
  const panelWidth = Math.min(Math.max(Math.floor(width / 4), 1), Math.max(width - 1, 1));
  const panel: Box = {left: width - panelWidth, top: 0, width: panelWidth, height};
  const availableWidth = panel.left;
  const aspect = 16 / 9;
  const video: Box =
    availableWidth / aspect <= height
      ? {left: 0, top: Math.floor((height - Math.floor(availableWidth / aspect)) / 2), width: availableWidth, height: Math.floor(availableWidth / aspect)}
      : {left: 0, top: 0, width: Math.floor(height * aspect), height};
  return {panel, video};
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

function sameValue(a: PanelValue, b: PanelValue): boolean {
  return a.value === b.value && a.reason === b.reason && a.source === b.source && a.asOfMs === b.asOfMs;
}

function sameRow(a: PanelRow, b: PanelRow): boolean {
  return a.playerId === b.playerId && a.name === b.name && a.gameStatus === b.gameStatus && sameValue(a.points, b.points);
}

function sameTarget(a: FocusTarget | null, b: FocusTarget): boolean {
  if (a === null || a.kind !== b.kind) return false;
  return a.kind !== 'row' || (b.kind === 'row' && a.playerId === b.playerId);
}

/** Remote keys are Vega HWEvent eventType names. */
export class PanelController {
  visible: boolean;
  teamLeague: string;
  snapshot: PanelSnapshot | null = null;
  focused: FocusTarget | null = {kind: 'teamLeagueSwitch'};

  private readonly teamLeagues: string[];
  private lastFetchMs: number | null = null;
  private needsFetch = true;

  constructor(teamLeagues: string[], initial: string, visible: boolean) {
    this.teamLeagues = [...teamLeagues];
    this.teamLeague = initial !== '' ? initial : (this.teamLeagues[0] ?? '');
    this.visible = visible;
  }

  bindings(): ReadonlyMap<string, PanelAction> {
    return new Map<string, PanelAction>([
      ['menu', 'ToggleVisibility'],
      ['forward', 'NextTeamLeague'],
      ['down', 'FocusNext'],
      ['up', 'FocusPrevious'],
      ['select', 'Select'],
    ]);
  }

  onKey(eventType: string, nowMs: number): boolean {
    const action = this.bindings().get(eventType);
    if (action === undefined) return false;
    if (!this.visible && action !== 'ToggleVisibility') return false;
    this.perform(action, nowMs);
    return true;
  }

  perform(action: PanelAction, _nowMs: number): void {
    switch (action) {
      case 'ToggleVisibility':
        this.visible = !this.visible;
        if (this.visible) this.needsFetch = true;
        break;
      case 'NextTeamLeague': {
        if (this.teamLeagues.length === 0) return;
        const index = this.teamLeagues.indexOf(this.teamLeague);
        const next = this.teamLeagues[(index + 1) % this.teamLeagues.length];
        if (next === this.teamLeague) return;
        this.teamLeague = next;
        this.snapshot = null;
        this.focused = {kind: 'teamLeagueSwitch'};
        this.needsFetch = true;
        break;
      }
      case 'FocusNext':
        this.moveFocus(1);
        break;
      case 'FocusPrevious':
        this.moveFocus(-1);
        break;
      case 'Select':
        break;
    }
  }

  shouldFetch(nowMs: number): boolean {
    if (!this.visible) return false;
    if (this.needsFetch) return true;
    if (this.lastFetchMs === null) return true;
    return nowMs - this.lastFetchMs >= REFRESH_MS;
  }

  onFetched(snapshot: PanelSnapshot, nowMs: number): PanelDelta {
    if (!this.visible) return PANEL_DELTA_NONE;
    if (snapshot.teamLeague !== this.teamLeague) return PANEL_DELTA_NONE;
    this.lastFetchMs = nowMs;
    this.needsFetch = false;
    const previous = this.snapshot;
    if (previous !== null && snapshot.revision <= previous.revision) return PANEL_DELTA_NONE;
    let delta: PanelDelta;
    if (previous === null) {
      delta = {changedRows: new Set(snapshot.rows.map(row => row.playerId)), removedRows: new Set(), totalsChanged: true};
    } else {
      const previousById = new Map(previous.rows.map(row => [row.playerId, row]));
      const changed = new Set(
        snapshot.rows.filter(row => {
          const before = previousById.get(row.playerId);
          return before === undefined || !sameRow(before, row);
        }).map(row => row.playerId),
      );
      const currentIds = new Set(snapshot.rows.map(row => row.playerId));
      const removed = new Set([...previousById.keys()].filter(id => !currentIds.has(id)));
      const totalsChanged =
        !sameValue(previous.teamTotal, snapshot.teamTotal) ||
        !sameValue(previous.progress, snapshot.progress) ||
        previous.basis !== snapshot.basis;
      delta = {changedRows: changed, removedRows: removed, totalsChanged};
    }
    const oldIndex = this.focusTargets().findIndex(target => sameTarget(this.focused, target));
    this.snapshot = snapshot;
    const targets = this.focusTargets();
    if (!targets.some(target => sameTarget(this.focused, target))) {
      this.focused = targets.length === 0 ? null : targets[Math.min(Math.max(oldIndex, 0), targets.length - 1)];
    }
    return delta;
  }

  focusTargets(): FocusTarget[] {
    const snapshot = this.snapshot;
    if (snapshot === null) return [{kind: 'teamLeagueSwitch'}];
    return [
      {kind: 'teamLeagueSwitch'} as FocusTarget,
      ...snapshot.rows.map((row): FocusTarget => ({kind: 'row', playerId: row.playerId})),
      {kind: 'total'} as FocusTarget,
    ];
  }

  private moveFocus(delta: number): void {
    const targets = this.focusTargets();
    if (targets.length === 0) return;
    const index = targets.findIndex(target => sameTarget(this.focused, target));
    this.focused = index < 0 ? targets[0] : targets[Math.min(Math.max(index + delta, 0), targets.length - 1)];
  }
}
