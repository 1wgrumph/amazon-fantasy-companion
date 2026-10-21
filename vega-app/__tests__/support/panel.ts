// Resource group: none shared. Each panel peer owns an OS-assigned loopback port (mirrors PanelFixtures.kt).
// TV-side PanelState wire shape: row projections carry player ID, points, game status and per-value source/freshness;
// unknown points stay null.
import type {Envelope} from '../../src/net/dto';
import type {PanelRow, PanelSnapshot} from '../../src/panel/panel';

export const TL = 'league-a/team-7';
export const AS_OF = '2026-10-15T20:00:00Z';
export const AS_OF_MS = Date.parse(AS_OF);

export function value(v: unknown, reason: string | null = null, source = 'live', asOf: string | null = AS_OF) {
  return {value: v ?? null, reason, source, asOf};
}

export function row(id: string, name: string, points: Record<string, unknown>, status: string | null = 'Q2 08:14') {
  return {playerId: id, name, points, gameStatus: status};
}

export function panelData({
  rows = [
    row('p-11', 'Player Eleven', value(12.3)),
    row('p-23', 'Player Twenty-Three', value(-1.5)),
    row('p-31', 'Player Thirty-One', value(null, 'feed withheld'), null),
  ] as unknown[],
  basis = 'halfPpr' as unknown,
  total = value(10.8),
  progress = value(0.5),
  teamLeague = TL,
} = {}): Record<string, any> {
  return {teamLeague, scoringBasis: basis ?? null, rows, teamTotal: total, progress};
}

export function envelope(data: Record<string, any>, revision = 7) {
  return {schemaVersion: 1, id: 'panel-fixture', revision, source: 'live', updatedAt: AS_OF, data};
}

/** A PanelState envelope built directly, so decode tests do not depend on the envelope decoder. */
export function state(data = panelData(), revision = 7): Envelope {
  return {...envelope(JSON.parse(JSON.stringify(data)), revision), eventTime: null};
}

export function prow(id: string, points: number | null, status: string | null = 'Q2 08:14'): PanelRow {
  return {
    playerId: id,
    name: `Player ${id}`,
    points: {value: points, reason: points === null ? 'feed withheld' : null, source: 'live', asOfMs: AS_OF_MS},
    gameStatus: status,
  };
}

/** A decoded snapshot built directly, so controller tests do not depend on the decoder. */
export function snap({
  revision = 7,
  rows = [prow('p-11', 12.3), prow('p-23', -1.5), prow('p-31', 4.0)],
  total = 14.8 as number | null,
  teamLeague = TL,
} = {}): PanelSnapshot {
  return {
    teamLeague,
    revision,
    basis: 'halfPpr',
    rows,
    teamTotal: {value: total, reason: total === null ? 'feed withheld' : null, source: 'live', asOfMs: AS_OF_MS},
    progress: {value: 0.5, reason: null, source: 'live', asOfMs: AS_OF_MS},
  };
}
