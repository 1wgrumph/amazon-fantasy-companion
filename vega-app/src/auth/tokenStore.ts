// The only module that reads or writes the session token. The app wires app-private
// storage (@amazon-devices/react-native-mmkv) behind KeyValueStorage; the token is never logged.
export interface KeyValueStorage {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
}

const SESSION_KEY = 'afc.session-token';

/** The app's store over Kepler AsyncStorage (app-private). Required lazily so unit tests never load it. */
export function appTokenStore(): TokenStore {
  const {AsyncStorage} = require('react-native') as {AsyncStorage: KeyValueStorage};
  return new TokenStore(AsyncStorage);
}

export class TokenStore {
  constructor(private readonly storage: KeyValueStorage) {}

  async read(): Promise<string | null> {
    return this.storage.getItem(SESSION_KEY);
  }

  async write(token: string): Promise<void> {
    await this.storage.setItem(SESSION_KEY, token);
  }

  async clear(): Promise<void> {
    await this.storage.removeItem(SESSION_KEY);
  }
}
