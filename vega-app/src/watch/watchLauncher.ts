// LAUNCHER (DES-AFC-P2-WATCH; CONTRACT-AFC-P2-PROVIDER-REGISTRY). Registry routes are untrusted:
// only a `verified` own-platform (`vega`) entry with a well-formed package and intent|uri launch is
// executed. No current-attempt observation exists, so a started launch is `accessUnknown` whatever
// the registry's historical `verified_outcome` or the platform's current-app report says.
import type {ApiClient} from '../net/apiClient';
import {isRecord} from '../net/dto';
import type {ProviderRoute, RoutingOutcome} from '../net/dto';
import type {PanelMode} from '../panel/panel';

/** Vega launch platform: Linking.canOpenURL / Linking.openURL. */
export interface LaunchPlatform {
  isInstalled(packageName: string): Promise<boolean>;
  start(packageName: string, type: string, value: string): Promise<boolean>;
  currentApp(): Promise<string | null>;
  leaveApp(): void;
}

const PACKAGE = /^[A-Za-z0-9._]{1,255}$/;
const ACTION_MAIN = 'android.intent.action.MAIN';

interface VerifiedLaunch {
  packageName: string;
  type: string;
  value: string;
}

function verifiedLaunch(eventId: string, channel: string | null, entry: Record<string, unknown>): VerifiedLaunch | null {
  if (entry.status !== 'verified') return null;
  const packageName = typeof entry.package === 'string' && PACKAGE.test(entry.package) ? entry.package : null;
  if (packageName === null || !isRecord(entry.launch)) return null;
  const type = entry.launch.type === 'intent' || entry.launch.type === 'uri' ? entry.launch.type : null;
  const template = typeof entry.launch.value === 'string' && entry.launch.value !== '' ? entry.launch.value : null;
  if (type === null || template === null) return null;
  if (template.includes('{channel}') && (channel === null || channel === '')) return null;
  const value = template.replaceAll('{event}', eventId).replaceAll('{channel}', channel ?? '');
  // A bare MAIN intent with only a package is never a launch (P2-X03).
  if (type === 'intent') {
    const action = value.split('?')[0];
    if (action === '' || action === ACTION_MAIN) return null;
  }
  return {packageName, type, value};
}

export class WatchLauncher {
  constructor(private readonly platform: LaunchPlatform) {}

  /** One Watch attempt; null when the customer declines the switch. */
  async watch(
    eventId: string,
    route: ProviderRoute,
    client: ApiClient,
    switchingConfirm: boolean,
    mode: PanelMode,
    confirm: () => Promise<boolean>,
  ): Promise<RoutingOutcome | null> {
    if (switchingConfirm && !(await confirm())) return null;
    let started = false;
    const outcome = await this.launchOnce(eventId, route, () => {
      started = true;
    });
    // The launch already happened: a report failure may not swallow the one report or the leave.
    try {
      await client.request('POST', '/v1/routing-outcome', {eventId, outcome});
    } catch {
      // Best-effort report; the known local outcome still stands.
    }
    if (started && mode === 'fullScreen') this.platform.leaveApp();
    return outcome;
  }

  /** Single pass: an uncertain outcome never relaunches (AFC-PR-031). */
  private async launchOnce(
    eventId: string,
    route: ProviderRoute,
    onStarted: () => void,
  ): Promise<RoutingOutcome> {
    const routes = isRecord(route.route) ? route.route.platform_routes : undefined;
    const entry = isRecord(routes) ? routes.vega : undefined;
    if (!isRecord(entry)) return 'accessUnknown';
    const launch = verifiedLaunch(eventId, route.channel, entry);
    if (launch === null) return 'accessUnknown';
    if (!(await this.platform.isInstalled(launch.packageName))) return 'appAbsent';
    if (!(await this.platform.start(launch.packageName, launch.type, launch.value))) return 'playbackDenied';
    onStarted();
    return 'accessUnknown';
  }
}

/** Alexa-assisted tuning is offered only over an enabled, verified route (AFC-PR-036). */
export function alexaTuningOffered(options: {voiceEnabled: boolean; routeVerified: boolean}): boolean {
  return options.voiceEnabled && options.routeVerified;
}
