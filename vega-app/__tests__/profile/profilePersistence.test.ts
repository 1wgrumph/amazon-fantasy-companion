// AFC-PR-002/-005/-066: selections and every control survive an app restart (mirrors ProfilePersistenceTest.kt).
// A restart is a new ApiClient and ProfileStore against the same backend peer.
import {ApiClient} from '../../src/net/apiClient';
import {effectiveInstalled, ProfileStore} from '../../src/profile/profile';
import {customized, ProfileServer, withProfileServer} from '../support/profile';

const store = (server: ProfileServer) => new ProfileStore(new ApiClient(server.baseUrl, {token: () => 'session-fixture'}));

describe('ProfilePersistenceTest', () => {
  test('firstLoadOfEmptyProfileIsHalfPpr', () =>
    withProfileServer({}, async server => {
      const loaded = await store(server).load();
      expect(loaded).not.toBeNull();
      expect(loaded?.scoringPreset).toBe('halfPpr');
    }));

  test('everySelectionAndControlPersistsAcrossRestart', () =>
    withProfileServer({}, async server => {
      const before = store(server);
      expect(await before.load()).not.toBeNull();
      expect(await before.save(customized())).toEqual(customized());
      expect(server.puts).toBe(1);
      const afterRestart = await store(server).load();
      expect(afterRestart).not.toBeNull();
      const expected = customized();
      for (const key of Object.keys(expected) as (keyof typeof expected)[]) {
        expect({key, value: afterRestart?.[key]}).toEqual({key, value: expected[key]});
      }
      expect(afterRestart).toEqual(expected);
    }));

  test('pprSelectionPersistsAndHalfPprReturnsAfterSwitchBack', () =>
    withProfileServer({}, async server => {
      const first = store(server);
      expect(await first.load()).not.toBeNull();
      expect(await first.save({...customized(), scoringPreset: 'ppr'})).not.toBeNull();
      expect(server.data.scoringPreset).toBe('ppr');
      expect((await store(server).load())?.scoringPreset).toBe('ppr');
      const second = store(server);
      expect(await second.load()).not.toBeNull();
      expect(await second.save({...customized(), scoringPreset: 'halfPpr'})).not.toBeNull();
      expect((await store(server).load())?.scoringPreset).toBe('halfPpr');
    }));

  // AFC-PR-005: a detection refresh after restart never discards the customer's override or local market.
  test('overrideSurvivesRestartAndDetectionRefresh', () =>
    withProfileServer({}, async server => {
      const first = store(server);
      expect(await first.load()).not.toBeNull();
      expect(await first.save(customized())).not.toBeNull();
      const reloaded = await store(server).load();
      expect(reloaded).not.toBeNull();
      const refreshed = new Set(['com.example.provider.a', 'com.example.provider.b']);
      expect(effectiveInstalled(reloaded!, refreshed)).toEqual(new Set(['com.example.provider.b', 'com.example.provider.c']));
      expect(effectiveInstalled(reloaded!, new Set([...refreshed, 'com.example.provider.a']))).toEqual(
        effectiveInstalled(reloaded!, refreshed),
      );
      expect(reloaded?.providerPref.localMarket).toBe('market-501');
    }));

  // CONTRACT-AFC-P2-ENVELOPE: a save over a stale revision is not silently forced onto the newer profile.
  test('staleSaveDoesNotOverwriteNewerProfile', () =>
    withProfileServer({}, async server => {
      const deviceA = store(server);
      const deviceB = store(server);
      expect(await deviceA.load()).not.toBeNull();
      expect(await deviceB.load()).not.toBeNull();
      const newer = {...customized(), excitement: 'Mild' as const};
      expect(await deviceB.save(newer)).toEqual(newer);
      expect(await deviceA.save({...customized(), excitement: 'Off'})).toBeNull();
      expect(await store(server).load()).toEqual(newer);
    }));

  // Persisted settings are untrusted: an invalid stored profile is not applied as if valid.
  test('invalidStoredProfileIsNotApplied', async () => {
    await withProfileServer({excitement: 12345, frequency: 'ludicrous'}, async server => {
      expect(await store(server).load()).toBeNull();
    });
    await withProfileServer({scoringPreset: 'standard'}, async server => {
      expect(await store(server).load()).toBeNull();
    });
  });
});
