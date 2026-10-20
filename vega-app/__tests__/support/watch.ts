// Synthetic route in the B06 wire shape (CONTRACT-AFC-P2-PROVIDER-REGISTRY: the whole platform_routes map, each entry
// `verified` or REGISTRY_ROUTE_GAP). Not a provider document. Mirrors WatchFixtures.kt with the Vega entry executed.
import type {ProviderRoute} from '../../src/net/dto';
import type {LaunchPlatform} from '../../src/watch/watchLauncher';

export const FIRE_OS_PACKAGE = 'test.beta.firetv';
export const VEGA_PACKAGE = 'test.beta.vega';
export const EVENT_ID = 'evt-401';

export function vegaEntry({
  packageName = VEGA_PACKAGE,
  type = 'uri',
  value = 'test-beta://watch/{event}',
  verifiedOutcome = 'gameOpened',
  status = 'verified' as string | null,
} = {}): Record<string, unknown> {
  const entry: Record<string, unknown> = {
    package: packageName,
    launch: {type, value},
    doc_source: 'test fixture, not a provider document',
    verified_outcome: verifiedOutcome,
    verified_at: '2026-10-14T19:30:00Z',
    currentAttemptObservation: 'none',
  };
  if (status !== null) entry.status = status;
  return entry;
}

export const fireOsEntry = (): Record<string, unknown> => ({
  package: FIRE_OS_PACKAGE,
  launch: {type: 'intent', value: 'test.beta.firetv.WATCH?event={event}'},
  verified_outcome: 'gameOpened',
  verified_at: '2026-10-14T19:00:00Z',
  status: 'verified',
});

export const gapEntry = (): Record<string, unknown> => ({status: 'REGISTRY_ROUTE_GAP'});

/** A decoded ProviderRoute built directly, as the alert or GET /v1/providers delivers it. */
export function routeOf({
  vega = vegaEntry(),
  fireOs = fireOsEntry(),
  channel = 'ESPN' as string | null,
} = {}): ProviderRoute {
  return {
    provider: 'beta_tv',
    channel,
    route: JSON.parse(JSON.stringify({platform_routes: {fire_os: fireOs, vega}})),
    accessBasis: 'verified',
  };
}

/**
 * Stand-in for the Vega launch platform: the real Linking.canOpenURL / openURL path needs the VVD and a provider
 * app (not available on the Ubuntu VVD). Records every call in order.
 */
export class RecordingPlatform implements LaunchPlatform {
  readonly calls: string[] = [];
  readonly starts: [string, string, string][] = [];
  constructor(
    private readonly installed: ReadonlySet<string> = new Set([FIRE_OS_PACKAGE, VEGA_PACKAGE]),
    private readonly accepts = true,
    private readonly foreground: string | null = null,
  ) {}
  async isInstalled(packageName: string): Promise<boolean> {
    return this.installed.has(packageName);
  }
  async start(packageName: string, type: string, value: string): Promise<boolean> {
    this.calls.push('start');
    this.starts.push([packageName, type, value]);
    return this.accepts;
  }
  async currentApp(): Promise<string | null> {
    return this.foreground;
  }
  leaveApp(): void {
    this.calls.push('leave');
  }
}
