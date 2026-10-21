// AC-AFC-P2-VEGA-04 (Vega-specific): the session token lives only in app-private storage behind src/auth/tokenStore.ts,
// is sent only as the bearer credential and never reaches a logger.
import {readdirSync, readFileSync, statSync} from 'fs';
import {join, relative} from 'path';
import {TokenStore} from '../../src/auth/tokenStore';
import {runLinkFlow} from '../../src/link/linkScreen';
import {ApiClient} from '../../src/net/apiClient';
import {envelopeFixture, MemoryStorage, REPO, runtimeToken, withApi} from '../support/contract';

const CONSOLE_METHODS = ['log', 'info', 'warn', 'error', 'debug', 'trace'] as const;

function sources(dir: string): string[] {
  return readdirSync(dir).flatMap(name => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? sources(path) : /\.(ts|tsx|js)$/.test(name) ? [path] : [];
  });
}

describe('TokenStoreTest', () => {
  test('persistsTheSessionTokenAcrossRestartOnlyThroughTheTokenStore', async () => {
    const token = runtimeToken();
    const storage = new MemoryStorage();
    await new TokenStore(storage).write(token);
    expect(storage.values.size).toBe(1);
    expect(await new TokenStore(storage).read()).toBe(token);
    await new TokenStore(storage).clear();
    expect(await new TokenStore(storage).read()).toBeNull();
    expect(storage.values.size).toBe(0);
  });

  test('sendsTheTokenOnlyAsTheBearerCredential', async () => {
    const token = runtimeToken();
    const store = new TokenStore(new MemoryStorage());
    await store.write(token);
    await withApi([[200, JSON.stringify(envelopeFixture())]], async api => {
      const client = new ApiClient(api.baseUrl, {token: () => store.read()});
      await client.request('GET', '/v1/profile');
      await client.request('PUT', '/v1/profile', {revision: 4, data: {scoringPreset: 'halfPpr'}});
      expect(api.requests).toHaveLength(2);
      for (const sent of api.requests) {
        expect(sent.bearer).toBe(`Bearer ${token}`);
        expect(sent.path).not.toContain(token);
        expect(sent.body).not.toContain(token);
      }
    });
  });

  test('tokenNeverReachesAnyLoggerAcrossLinkRefreshAndFailure', async () => {
    const token = runtimeToken();
    const spies = CONSOLE_METHODS.map(method => jest.spyOn(console, method).mockImplementation(() => {}));
    try {
      const store = new TokenStore(new MemoryStorage());
      const replies: [number, string][] = [
        [201, JSON.stringify({code: 'ABCD2345', expires: '2026-10-14T12:10:00Z', handle: 'h'})],
        [200, JSON.stringify({state: 'linked', sessionToken: token})],
        [200, JSON.stringify(envelopeFixture())],
        [401, JSON.stringify({error: {code: 'unauthenticated', message: 'session rejected'}})],
      ];
      await withApi(replies, async api => {
        const client = new ApiClient(api.baseUrl, {token: () => store.read()});
        await runLinkFlow({client, sleep: async () => {}, show: () => {}, store: value => store.write(value)});
        expect(await store.read()).toBe(token);
        await client.request('GET', '/v1/profile');
        await client.request('GET', '/v1/profile');
        expect(api.requests.at(-1)?.bearer).toBe(`Bearer ${token}`);
      });
      const logged = spies.flatMap(spy => spy.mock.calls).map(args => args.map(arg => String(arg) + JSON.stringify(arg)).join(' '));
      expect(logged.filter(line => line.includes(token))).toEqual([]);
    } finally {
      spies.forEach(spy => spy.mockRestore());
    }
  });

  test('onlyTheTokenStoreModuleUsesPersistentStorage', () => {
    const src = join(REPO, 'vega-app/src');
    const storage = /@amazon-devices\/react-native-mmkv|react-native-mmkv|@react-native-async-storage|\bAsyncStorage\b/;
    const users = sources(src)
      .filter(path => storage.test(readFileSync(path, 'utf8')))
      .map(path => relative(src, path));
    expect(users.filter(path => path !== join('auth', 'tokenStore.ts'))).toEqual([]);
  });
});
