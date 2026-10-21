// Resource group: none shared. Pages are served by LocalApi on an OS-assigned loopback port (mirrors AlertFixtures.kt).
// Alert data follows the store's Alert attributes (alertType, triggerContext, commentary) and data.route.
import type {AlertText} from '../../src/alerts/alertPresenter';
import type {AccessBasis, Alert} from '../../src/net/dto';
import type {Presentation, ProfileState} from '../../src/profile/profile';
import type {Reply} from './contract';

export const PLAYER = 'Player Eleven';
export const MATCHUP = 'KC at BUF';

export function route(basis: string, provider: string | null = 'provider-a') {
  return {accessBasis: basis, provider};
}

export function alertData({
  type = 'redZone',
  player = PLAYER as string | null,
  matchup = MATCHUP as string | null,
  commentary = null as string | null,
  route: alertRoute = route('unknown') as ReturnType<typeof route> | null,
} = {}) {
  const triggerContext: Record<string, string> = {};
  if (player !== null) triggerContext.player = player;
  if (matchup !== null) triggerContext.matchup = matchup;
  return {alertType: type, eventId: 'evt-fixture', triggerContext, commentary, route: alertRoute};
}

export function alertJson(id: string, revision = 1, data: Record<string, unknown> = alertData()) {
  return {
    schemaVersion: 1,
    id,
    revision,
    source: 'replay',
    updatedAt: '2026-10-15T00:20:00Z',
    eventTime: '2026-10-15T00:19:30Z',
    data,
  };
}

/** A decoded alert built directly, so presenter tests do not depend on the decoder. */
export function alert(data: ReturnType<typeof alertData> = alertData()): Alert {
  const json = alertJson('alert-fixture', 1, data);
  return {
    envelope: {...json, data: JSON.parse(JSON.stringify(data))},
    route: data.route
      ? {provider: data.route.provider, channel: null, route: null, accessBasis: data.route.accessBasis as AccessBasis}
      : null,
  };
}

export function page(cursor: string, ...alerts: unknown[]): Reply {
  return [200, JSON.stringify({alerts, cursor})];
}

export function profile(presentation: Presentation = 'HeadsUp', voice = false): ProfileState {
  return {
    selections: {leagues: new Set(), teams: new Set(), players: new Set(['player-11']), favoriteTeams: new Set()},
    teamLeague: null,
    alertTypes: new Set(),
    minGapSeconds: 120,
    quietHours: [],
    gameDay: {enabled: false, periods: []},
    spoilerDelaySeconds: 0,
    presentation,
    voiceEnabled: voice,
    excitement: 'Off',
    providerPref: {order: [], confirmedAccess: new Set(), appOverrides: {}, localMarket: null},
    switchingConfirm: true,
    panel: {visible: true},
    detectionOptIn: false,
    scoringPreset: 'halfPpr',
  };
}

/** Every line the customer can see. */
export function allText(text: AlertText): string {
  return [text.headline, text.context, text.access, text.commentary].filter(line => line !== null).join('\n');
}
