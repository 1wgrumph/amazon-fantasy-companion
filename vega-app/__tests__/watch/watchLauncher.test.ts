// LAUNCHER (DES-AFC-P2-WATCH; AFC-PR-030, -031, -035, -036, -048), mirrors WatchLauncherTest.kt for the Vega client.
// The route is untrusted registry data: only a verified `platform_routes.vega` entry is executed, never `fire_os`;
// neither a launch call, the registry's historical verified_outcome nor the current-app report establishes gameOpened.
import {ApiClient} from '../../src/net/apiClient';
import type {ProviderRoute, RoutingOutcome} from '../../src/net/dto';
import type {PanelMode} from '../../src/panel/panel';
import {alexaTuningOffered, WatchLauncher} from '../../src/watch/watchLauncher';
import {node, Reply, withApi} from '../support/contract';
import {EVENT_ID, FIRE_OS_PACKAGE, gapEntry, RecordingPlatform, routeOf, VEGA_PACKAGE, vegaEntry} from '../support/watch';

const ROUTING_OUTCOMES = node('components', 'schemas', 'RoutingOutcome').enum as RoutingOutcome[];

interface Attempt {
  outcome: RoutingOutcome | null;
  reports: Record<string, unknown>[];
  confirmAsked: number;
}

async function attempt(
  platform: RecordingPlatform,
  {
    route = routeOf() as ProviderRoute,
    switchingConfirm = false,
    confirmAnswer = true,
    mode = 'modeB' as PanelMode,
    reply = [200, '{}'] as Reply,
  } = {},
): Promise<Attempt> {
  return withApi([reply], async api => {
    let asked = 0;
    const outcome = await new WatchLauncher(platform).watch(
      EVENT_ID,
      route,
      new ApiClient(api.baseUrl, {token: () => 'session-fixture'}),
      switchingConfirm,
      mode,
      async () => {
        asked++;
        platform.calls.push('confirm');
        return confirmAnswer;
      },
    );
    const reports = api.requests.filter(r => r.method === 'POST' && r.path === '/v1/routing-outcome').map(r => JSON.parse(r.body));
    return {outcome, reports, confirmAsked: asked};
  });
}

function expectSingleReport(expected: RoutingOutcome, result: Attempt) {
  expect(result.reports).toHaveLength(1);
  expect(result.reports[0].eventId).toBe(EVENT_ID);
  expect(result.reports[0].outcome).toBe(expected);
  expect(result.outcome).toBe(expected);
}

describe('WatchLauncherTest', () => {
  // Vega client: the Fire OS test executesOnlyTheFireOsRegistryLaunch, with the platforms swapped.
  test('executesOnlyTheVegaRegistryLaunch', async () => {
    const platform = new RecordingPlatform();
    await attempt(platform);
    expect(platform.starts).toEqual([[VEGA_PACKAGE, 'uri', `test-beta://watch/${EVENT_ID}`]]);
    expect(platform.starts.some(([pkg, , value]) => pkg === FIRE_OS_PACKAGE || value.includes('WATCH?event='))).toBe(false);
  });

  test('channelPlaceholderIsFilledFromTheResolvedChannel', async () => {
    const platform = new RecordingPlatform();
    await attempt(platform, {route: routeOf({vega: vegaEntry({value: 'test-beta-vega://channel/{channel}'})})});
    expect(platform.starts).toEqual([[VEGA_PACKAGE, 'uri', 'test-beta-vega://channel/ESPN']]);
  });

  test('ownPlatformGapLaunchesNothingAndReportsAccessUnknown', async () => {
    const platform = new RecordingPlatform();
    const result = await attempt(platform, {route: routeOf({vega: gapEntry()})});
    expect(platform.starts).toEqual([]);
    expectSingleReport('accessUnknown', result);
  });

  test('unverifiedOrMalformedEntryIsNeverLaunched', async () => {
    const untrusted = [
      vegaEntry({status: null}),
      vegaEntry({status: 'pending'}),
      vegaEntry({packageName: 'bad package;rm'}),
      vegaEntry({type: 'shell'}),
    ];
    for (const entry of untrusted) {
      const platform = new RecordingPlatform(new Set([VEGA_PACKAGE, 'bad package;rm']));
      const result = await attempt(platform, {route: routeOf({vega: entry})});
      expect({entry, starts: platform.starts}).toEqual({entry, starts: []});
      expectSingleReport('accessUnknown', result);
    }
  });

  test('missingPackageReportsAppAbsent', async () => {
    const platform = new RecordingPlatform(new Set());
    const result = await attempt(platform);
    expect(platform.starts).toEqual([]);
    expectSingleReport('appAbsent', result);
  });

  test('refusedLaunchReportsPlaybackDenied', async () => {
    const platform = new RecordingPlatform(undefined, false);
    const result = await attempt(platform);
    expect(platform.starts).toHaveLength(1);
    expectSingleReport('playbackDenied', result);
  });

  // Negative check: a prior registry gameOpened plus an unconfirmed current-app launch is accessUnknown.
  test('priorGameOpenedPlusUnconfirmedCurrentAppIsAccessUnknown', async () => {
    const platform = new RecordingPlatform(undefined, true, VEGA_PACKAGE);
    const result = await attempt(platform, {route: routeOf({vega: vegaEntry({verifiedOutcome: 'gameOpened'})})});
    expect(platform.starts).toHaveLength(1);
    expect(result.outcome).not.toBe('gameOpened');
    expectSingleReport('accessUnknown', result);
  });

  test('historicalVerifiedOutcomeIsNeverTheCurrentOutcome', async () => {
    for (const historical of ROUTING_OUTCOMES) {
      const platform = new RecordingPlatform();
      const result = await attempt(platform, {route: routeOf({vega: vegaEntry({verifiedOutcome: historical})})});
      expect({historical, starts: platform.starts.length}).toEqual({historical, starts: 1});
      expectSingleReport('accessUnknown', result);
    }
  });

  test('eachAttemptReportsExactlyOneOutcome', () =>
    withApi([[200, '{}']], async api => {
      const client = new ApiClient(api.baseUrl, {token: () => 'session-fixture'});
      const cases = [new RecordingPlatform(new Set()), new RecordingPlatform(undefined, false), new RecordingPlatform()];
      const outcomes: (RoutingOutcome | null)[] = [];
      for (const platform of cases) {
        outcomes.push(await new WatchLauncher(platform).watch(EVENT_ID, routeOf(), client, false, 'modeB', async () => true));
      }
      const reported = api.requests.filter(r => r.path === '/v1/routing-outcome').map(r => JSON.parse(r.body).outcome);
      expect(reported).toEqual(['appAbsent', 'playbackDenied', 'accessUnknown']);
      expect(outcomes).toEqual(reported);
    }));

  test('noRelaunchAfterUncertainOutcome', async () => {
    const platform = new RecordingPlatform();
    const result = await attempt(platform, {reply: [503, JSON.stringify({error: {code: 'unavailable', message: 'try later'}})]});
    expect(platform.starts).toHaveLength(1);
    expectSingleReport('accessUnknown', result);
  });

  test('switchingConfirmationBlocksTheSwitchUntilConfirmed', async () => {
    const platform = new RecordingPlatform();
    const result = await attempt(platform, {switchingConfirm: true, confirmAnswer: false});
    expect(result.confirmAsked).toBe(1);
    expect(platform.starts).toEqual([]);
    expect(result.outcome).toBeNull();
    expect(result.reports).toEqual([]);
  });

  test('confirmedSwitchLaunchesAfterConfirmation', async () => {
    const platform = new RecordingPlatform();
    const result = await attempt(platform, {switchingConfirm: true, confirmAnswer: true});
    expect(platform.calls.filter(call => call !== 'leave')).toEqual(['confirm', 'start']);
    expectSingleReport('accessUnknown', result);
  });

  test('confirmationOffNeverAsks', async () => {
    const platform = new RecordingPlatform();
    const result = await attempt(platform, {switchingConfirm: false});
    expect(result.confirmAsked).toBe(0);
    expect(platform.starts).toHaveLength(1);
  });

  test('fullScreenWatchLeavesTheCompanionApp', async () => {
    const platform = new RecordingPlatform();
    await attempt(platform, {mode: 'fullScreen'});
    expect(platform.calls).toEqual(['start', 'leave']);
    expect(platform.starts[0][0]).toBe(VEGA_PACKAGE);
  });

  test('fullScreenFailedLaunchStaysToShowTheOutcome', async () => {
    const platform = new RecordingPlatform(new Set());
    const result = await attempt(platform, {mode: 'fullScreen'});
    expect(platform.calls).not.toContain('leave');
    expectSingleReport('appAbsent', result);
  });

  test('alexaTuningHiddenWithoutVerifiedRoute', () => {
    expect(alexaTuningOffered({voiceEnabled: true, routeVerified: false})).toBe(false);
    expect(alexaTuningOffered({voiceEnabled: false, routeVerified: false})).toBe(false);
    expect(alexaTuningOffered({voiceEnabled: false, routeVerified: true})).toBe(false);
  });

  test('alexaTuningOfferedOverEnabledVerifiedRoute', () => {
    expect(alexaTuningOffered({voiceEnabled: true, routeVerified: true})).toBe(true);
  });
});
