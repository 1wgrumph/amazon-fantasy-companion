// Interface scaffolding for P2-V01T (red). The only module that reads or writes the session token.
export interface KeyValueStorage {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
  removeItem(key: string): Promise<void>;
}

export class TokenStore {
  constructor(_storage: KeyValueStorage) {}

  async read(): Promise<string | null> {
    return null;
  }

  async write(_token: string): Promise<void> {}

  async clear(): Promise<void> {}
}
