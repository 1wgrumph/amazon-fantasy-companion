// Resource group: none shared. Each ProfileServer owns an OS-assigned loopback port (mirrors ProfileFixtures.kt).
import type {ProfileState} from '../../src/profile/profile';
import {LocalApi} from './contract';

/** Every control set away from its default, so a dropped or defaulted control is visible. */
export function customized(): ProfileState {
  return {
    selections: {
      leagues: new Set(['league-a']),
      teams: new Set(['team-7']),
      players: new Set(['player-11', 'player-23']),
      favoriteTeams: new Set(['KC', 'BUF']),
    },
    teamLeague: {league: 'league-a', team: 'team-7'},
    alertTypes: new Set(['RedZone', 'CloseGame']),
    minGapSeconds: 300,
    quietHours: [{startMinute: 22 * 60, endMinute: 7 * 60}],
    gameDay: {enabled: true, periods: [{startMinute: 13 * 60, endMinute: 23 * 60}]},
    spoilerDelaySeconds: 45,
    presentation: 'PanelOnly',
    voiceEnabled: true,
    excitement: 'Hype',
    providerPref: {
      order: ['provider-b', 'provider-a'],
      confirmedAccess: new Set(['provider-b']),
      appOverrides: {'com.example.provider.a': false, 'com.example.provider.c': true},
      localMarket: 'market-501',
    },
    switchingConfirm: false,
    panel: {visible: false},
    detectionOptIn: true,
    scoringPreset: 'ppr',
  };
}

/** A stateful GET/PUT /v1/profile peer that outlives each client, standing in for the backend across an app restart. */
export class ProfileServer {
  revision = 4;
  puts = 0;
  private constructor(public data: Record<string, unknown>, private api: LocalApi | null = null) {}

  get baseUrl(): string {
    return this.api!.baseUrl;
  }

  private envelope() {
    return {
      schemaVersion: 1,
      id: 'profile-fixture',
      revision: this.revision,
      source: 'manual',
      updatedAt: '2026-10-14T12:00:00Z',
      data: JSON.parse(JSON.stringify(this.data)),
    };
  }

  static async start(initialData: Record<string, unknown> = {}): Promise<ProfileServer> {
    const server = new ProfileServer(initialData);
    server.api = await LocalApi.start(request => {
      if (request.path !== '/v1/profile') return [404, JSON.stringify({error: {code: 'not_found', message: 'fixture'}})];
      if (request.method === 'GET') return [200, JSON.stringify(server.envelope())];
      if (request.method !== 'PUT') return [405, '{}'];
      server.puts++;
      const update = JSON.parse(request.body);
      if (update.revision !== server.revision) {
        return [409, JSON.stringify({error: {code: 'conflict', message: 'stale revision'}})];
      }
      server.data = update.data;
      server.revision++;
      return [200, JSON.stringify(server.envelope())];
    });
    return server;
  }

  close(): Promise<void> {
    return this.api!.close();
  }
}

export async function withProfileServer<T>(
  initialData: Record<string, unknown>,
  body: (server: ProfileServer) => Promise<T>,
): Promise<T> {
  const server = await ProfileServer.start(initialData);
  try {
    return await body(server);
  } finally {
    await server.close();
  }
}
