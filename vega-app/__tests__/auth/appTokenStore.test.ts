// AFC-M14-TOKEN-PERSIST / AC-AFC-P2-VEGA-04: appTokenStore() must bind the session token to the supported
// app-private Vega store, not the legacy react-native AsyncStorage. On the VVD the legacy store logs
// "Legacy AsyncStorage is on a deprecation path. Please migrate to using
// @amazon-devices/react-native-async-storage__async-storage" (react-native-kepler Libraries/Storage/AsyncStorage.js),
// then fails with "Application data root path is not set", so the token is lost on relaunch.
import type {TokenStore} from '../../src/auth/tokenStore';

// One map stands in for the device's app-private store; it outlives module reloads (app relaunches).
const mockBacking = new Map<string, string>();
const mockSupported = {
  getItem: jest.fn(async (key: string) => mockBacking.get(key) ?? null),
  setItem: jest.fn(async (key: string, value: string) => void mockBacking.set(key, value)),
  removeItem: jest.fn(async (key: string) => void mockBacking.delete(key)),
};
const mockLegacy = {
  getItem: jest.fn(async () => null),
  setItem: jest.fn(async () => {}),
  removeItem: jest.fn(async () => {}),
};

// virtual: the package is not installed in the dev tree; the device provides it.
jest.mock(
  '@amazon-devices/react-native-async-storage__async-storage',
  () => ({__esModule: true, default: mockSupported, ...mockSupported}),
  {virtual: true},
);
// AsyncStorageWithKeyScope delegates to the same legacy AsyncStorage, so binding it does not fix the defect.
jest.mock('react-native', () => ({AsyncStorage: mockLegacy, AsyncStorageWithKeyScope: jest.fn(() => mockLegacy)}));

/** A fresh module registry is a fresh app process; only mockBacking survives. */
function launch(): TokenStore {
  let store: TokenStore | undefined;
  jest.isolateModules(() => {
    store = (require('../../src/auth/tokenStore') as typeof import('../../src/auth/tokenStore')).appTokenStore();
  });
  return store!;
}

describe('AppTokenStoreTest', () => {
  beforeEach(() => {
    mockBacking.clear();
    jest.clearAllMocks();
  });

  test('bindsTheSessionTokenToTheSupportedAppPrivateStoreNotLegacyAsyncStorage', async () => {
    const store = launch();
    await store.write('token-1');
    await store.read();
    await store.clear();
    const legacyCalls = [mockLegacy.getItem, mockLegacy.setItem, mockLegacy.removeItem].reduce((n, fn) => n + fn.mock.calls.length, 0);
    expect({legacyCalls, supportedWrites: mockSupported.setItem.mock.calls.length}).toEqual({legacyCalls: 0, supportedWrites: 1});
  });

  test('tokenWrittenBeforeRelaunchIsReadAfterRelaunch', async () => {
    await launch().write('token-2');
    expect(await launch().read()).toBe('token-2');
  });
});
