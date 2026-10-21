// AFC-PR-038 link screen presentation (mirrors LinkScreenTest.kt) plus the Vega shell link states.
import {ApiClient} from '../../src/net/apiClient';
import {LinkPresentation, presentLink, runLinkFlow} from '../../src/link/linkScreen';
import {shellStart} from '../../src/shell';
import {node, runtimeToken, withApi} from '../support/contract';

describe('LinkScreenTest', () => {
  test('codeShownWithItsExpiry', () => {
    const response = {code: 'ABCD2345', expires: '2026-10-14T12:10:00Z', handle: 'fixture'};
    expect((node('components', 'schemas', 'DeviceCode').required as string[]).every(field => field in response)).toBe(true);
    const shown = presentLink(response);
    expect(shown).not.toBeNull();
    expect(shown?.state).toBe('codePending');
    expect(shown?.code).toBe('ABCD2345');
    expect(shown?.message).toContain(response.expires);
    expect(shown?.showProfile).toBe(false);
  });

  test('pendingPollKeepsLinkFlowOpen', () => {
    const shown = presentLink({state: 'codePending'});
    expect(shown).not.toBeNull();
    expect(shown?.state).toBe('codePending');
    expect(shown?.showProfile).toBe(false);
  });

  test('expiredCodeShowsExpiryAndCannotContinueToProfile', () => {
    const shown = presentLink({state: 'expired'});
    expect(shown).not.toBeNull();
    expect(shown?.state).toBe('expired');
    expect(shown?.code).toBeNull();
    expect(shown?.message.toLowerCase()).toContain('expired');
    expect(shown?.showProfile).toBe(false);
  });

  test('linkedStateContinuesWithoutDisplayingSessionToken', () => {
    const token = runtimeToken();
    const shown = presentLink({state: 'linked', sessionToken: token});
    expect(shown).not.toBeNull();
    expect(shown?.state).toBe('linked');
    expect(shown?.showProfile).toBe(true);
    expect(shown?.code).toBeNull();
    expect(JSON.stringify(shown)).not.toContain(token);
  });

  test('unlinkedStateRequiresCodeIssuance', () => {
    const shown = presentLink({state: 'unlinked'});
    expect(shown).not.toBeNull();
    expect(shown?.state).toBe('unlinked');
    expect(shown?.code).toBeNull();
    expect(shown?.showProfile).toBe(false);
  });
});

// Goal-listed link states with Fire OS sources outside A01T (ClientBoundaryTest.kt, LinkScreen.kt networkError).
describe('VegaLinkStatesTest', () => {
  test('backendNotConfiguredBlocksLinkingUntilAUsableBaseUrl', () => {
    for (const unusable of ['', 'http://api.example.test']) {
      expect(shellStart(unusable, false)).toEqual({destination: 'BackendNotConfigured', message: 'Backend not configured'});
      expect(shellStart(unusable, true).destination).toBe('BackendNotConfigured');
    }
    expect(shellStart('https://api.example.test', false).destination).toBe('Link');
    expect(shellStart('https://api.example.test', true).destination).toBe('ProfileSettings');
  });

  test('networkErrorShowsRetryAndCannotContinueToProfile', async () => {
    await withApi(
      (_request, _index, response) => {
        response.socket?.destroy();
        return null;
      },
      async api => {
        const shown: LinkPresentation[] = [];
        const stored: string[] = [];
        await runLinkFlow({
          client: new ApiClient(api.baseUrl),
          sleep: async () => {},
          show: presentation => shown.push(presentation),
          store: async token => {
            stored.push(token);
          },
        });
        expect(api.requests.length).toBeGreaterThan(0);
        expect(shown.at(-1)?.state).toBe('networkError');
        expect(shown.at(-1)?.message).toMatch(/network error/i);
        expect(shown.at(-1)?.showProfile).toBe(false);
        expect(stored).toEqual([]);
      },
    );
  });
});
