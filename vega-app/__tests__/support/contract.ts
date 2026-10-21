// Resource group: none shared. Each LocalApi owns a loopback port the OS assigns (listen on 0) and its sockets.
import {readFileSync} from 'fs';
import {createServer, IncomingMessage, Server, ServerResponse} from 'http';
import {AddressInfo, Socket} from 'net';
import {join} from 'path';
import {load} from 'js-yaml';

export const REPO = join(__dirname, '..', '..', '..');
export const openApi = load(readFileSync(join(REPO, 'backend/src/api/openapi.yaml'), 'utf8')) as Record<string, any>;

export function node(...keys: string[]): Record<string, any> {
  return keys.reduce((current, key) => {
    const next = current?.[key];
    if (next === undefined) throw new Error(`openapi.yaml has no ${keys.join(' > ')}`);
    return next;
  }, openApi as Record<string, any>);
}

export function envelopeFixture(revision = 4): Record<string, any> {
  return {
    schemaVersion: 1,
    id: 'profile-fixture',
    revision,
    source: 'manual',
    updatedAt: '2026-10-14T12:00:00Z',
    data: {scoringPreset: 'halfPpr'},
  };
}

export const unavailable = JSON.stringify({error: {code: 'unavailable', message: 'retry'}});

export interface RecordedRequest {
  method: string;
  path: string;
  bearer: string | undefined;
  body: string;
  atMs: number;
}

export type Reply = [number, string];
export type Handler = (request: RecordedRequest, index: number, response: ServerResponse) => Reply | null;

/** A real HTTP peer on loopback that replays replies in order (the last one repeats). */
export class LocalApi {
  readonly requests: RecordedRequest[] = [];
  private readonly sockets = new Set<Socket>();
  private constructor(private readonly server: Server, readonly baseUrl: string) {}

  static async start(replies: Reply[] | Handler): Promise<LocalApi> {
    let api: LocalApi;
    const server = createServer((req: IncomingMessage, res: ServerResponse) => {
      const chunks: Buffer[] = [];
      req.on('data', chunk => chunks.push(chunk));
      req.on('end', () => {
        const index = api.requests.length;
        const recorded: RecordedRequest = {
          method: req.method ?? '',
          path: req.url ?? '',
          bearer: req.headers.authorization,
          body: Buffer.concat(chunks).toString('utf8'),
          atMs: performance.now(),
        };
        api.requests.push(recorded);
        const reply = typeof replies === 'function' ? replies(recorded, index, res) : replies[Math.min(index, replies.length - 1)];
        if (reply === null) return;
        const bytes = Buffer.from(reply[1], 'utf8');
        res.writeHead(reply[0], {'Content-Type': 'application/json', 'Content-Length': bytes.length});
        res.end(bytes);
      });
    });
    server.on('connection', socket => {
      api.sockets.add(socket);
      socket.on('close', () => api.sockets.delete(socket));
    });
    await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve));
    api = new LocalApi(server, `http://127.0.0.1:${(server.address() as AddressInfo).port}`);
    return api;
  }

  async close(): Promise<void> {
    for (const socket of this.sockets) socket.destroy();
    await new Promise<void>(resolve => this.server.close(() => resolve()));
  }
}

/** Runs body against a fresh LocalApi and always closes it. */
export async function withApi<T>(replies: Reply[] | Handler, body: (api: LocalApi) => Promise<T>): Promise<T> {
  const api = await LocalApi.start(replies);
  try {
    return await body(api);
  } finally {
    await api.close();
  }
}

/** A token generated at run time, never a committed literal. */
export function runtimeToken(): string {
  return `${crypto.randomUUID()}${crypto.randomUUID()}`;
}

/** Map-backed app-private storage; a new TokenStore over the same map stands in for an app restart. */
export class MemoryStorage {
  readonly values = new Map<string, string>();
  async getItem(key: string): Promise<string | null> {
    return this.values.get(key) ?? null;
  }
  async setItem(key: string, value: string): Promise<void> {
    this.values.set(key, value);
  }
  async removeItem(key: string): Promise<void> {
    this.values.delete(key);
  }
}
