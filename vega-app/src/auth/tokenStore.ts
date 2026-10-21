// The only module that reads or writes the session token. The app wires app-private
// storage (@amazon-devices/react-native-async-storage__async-storage) behind KeyValueStorage; the token is never logged.
export interface KeyValueStorage {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
}

const SESSION_KEY = 'afc.session-token';

/** The app's store over supported app-private AsyncStorage. Required lazily so unit tests never load it. */
export function appTokenStore(): TokenStore {
  const {default: AsyncStorage} = require('@amazon-devices/react-native-async-storage__async-storage') as {default: KeyValueStorage};
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
