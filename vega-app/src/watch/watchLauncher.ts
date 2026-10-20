// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
import type {ApiClient} from '../net/apiClient';
import type {ProviderRoute, RoutingOutcome} from '../net/dto';
import type {PanelMode} from '../panel/panel';

/** Vega launch platform: Linking.canOpenURL / Linking.openURL. */
export interface LaunchPlatform {
  isInstalled(packageName: string): Promise<boolean>;
  start(packageName: string, type: string, value: string): Promise<boolean>;
  currentApp(): Promise<string | null>;
  leaveApp(): void;
}

export class WatchLauncher {
  constructor(_platform: LaunchPlatform) {}

  /** One Watch attempt; null when the customer declines the switch. */
  async watch(
    _eventId: string,
    _route: ProviderRoute,
    _client: ApiClient,
    _switchingConfirm: boolean,
    _mode: PanelMode,
    _confirm: () => Promise<boolean>,
  ): Promise<RoutingOutcome | null> {
    return null;
  }
}

export function alexaTuningOffered(_options: {voiceEnabled: boolean; routeVerified: boolean}): boolean {
  return false;
}
