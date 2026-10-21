// CONTRACT-AFC-P2-API client (backend/src/api/openapi.yaml). Bodies are at most 64 KiB both ways;
// api_timeout is 10 s, the alerts long poll reads for alert_poll_wait + 5 s = 25 s; idempotent calls
// (GET, PUT /v1/profile) retry 429/503 up to api_retry_max = 3 times with 1, 2, 4 s backoff.
import {ContractError, decodeEnvelope, isRecord} from './dto';
import type {Envelope, JsonObject} from './dto';

export interface ApiResponse {
  status: number;
  body: JsonObject | null;
}

export interface ApiError {
  code: string;
  message: string;
}

export interface ApiResult<T> {
  status: number;
  value: T | null;
  error: ApiError | null;
}

export interface Timers {
  setTimeout(callback: () => void, ms: number): unknown;
  clearTimeout(handle: unknown): void;
}

export interface ApiClientOptions {
  /** Session token source; the app passes TokenStore.read. */
  token?: () => string | null | Promise<string | null>;
  fetch?: typeof fetch;
  /** Waits between retries of idempotent calls. */
  backoff?: (ms: number) => Promise<void>;
  /** Schedules the api_timeout abort. */
  timers?: Timers;
}

const MAX_BODY_BYTES = 65_536;
const TIMEOUT_MS = 10_000;
const LONG_POLL_READ_MS = 25_000;
const RETRY_MAX = 3;
const BACKOFF_BASE_MS = 1_000;
const METHODS = new Set(['GET', 'POST', 'PUT']);
const TRANSIENT = new Set([429, 503]);
const PUBLIC_PATHS = new Set(['/v1/link', '/v1/link/confirm']);
const LOOPBACK_HOSTS = new Set(['127.0.0.1', 'localhost']);

/** A usable build-time base URL: https, or http on loopback only; no user info, query or fragment. */
export function isUsableBaseUrl(baseUrl: string): boolean {
  if (baseUrl.trim() === '') return false;
  let url: URL;
  try {
    url = new URL(baseUrl);
  } catch {
    return false;
  }
  if (url.username !== '' || url.password !== '' || url.search !== '' || url.hash !== '') return false;
  return url.protocol === 'https:' || (url.protocol === 'http:' && LOOPBACK_HOSTS.has(url.hostname));
}

function apiErrorFrom(body: JsonObject | null): ApiError | null {
  if (!isRecord(body) || !isRecord(body.error)) return null;
  const {code, message} = body.error;
  return typeof code === 'string' && typeof message === 'string' ? {code, message} : null;
}

const defaultTimers: Timers = {
  setTimeout: (callback, ms) => setTimeout(callback, ms),
  clearTimeout: handle => clearTimeout(handle as ReturnType<typeof setTimeout>),
};

export class ApiClient {
  private readonly base: string;
  private readonly tokenSource: ApiClientOptions['token'];
  private readonly fetchImpl: typeof fetch;
  private readonly backoff: (ms: number) => Promise<void>;
  private readonly timers: Timers;

  constructor(readonly baseUrl: string, options: ApiClientOptions = {}) {
    if (!isUsableBaseUrl(baseUrl)) {
      throw new ContractError('API base URL must be https (http only for loopback)');
    }
    this.base = baseUrl.replace(/\/+$/, '');
    this.tokenSource = options.token;
    this.fetchImpl = options.fetch ?? ((input, init) => fetch(input, init));
    this.backoff = options.backoff ?? (ms => new Promise<void>(resolve => setTimeout(resolve, ms)));
    this.timers = options.timers ?? defaultTimers;
  }

  async request(method: string, path: string, body?: JsonObject | null): Promise<ApiResponse> {
    // Network opening and parsing happen after the caller's synchronous turn (one JS UI thread).
    await Promise.resolve();
    if (!METHODS.has(method) || !path.startsWith('/v1/')) throw new ContractError('Unsupported operation');
    const payload = body === undefined || body === null ? null : JSON.stringify(body);
    if (payload !== null && new TextEncoder().encode(payload).length > MAX_BODY_BYTES) {
      throw new ContractError('Request body exceeds 64 KiB');
    }
    const idempotent = method === 'GET' || method === 'PUT';
    let attempt = 0;
    let response = await this.send(method, path, payload);
    while (idempotent && TRANSIENT.has(response.status) && attempt < RETRY_MAX) {
      await this.backoff(BACKOFF_BASE_MS << attempt);
      attempt++;
      response = await this.send(method, path, payload);
    }
    return response;
  }

  async getPanel(teamLeague?: string): Promise<ApiResult<Envelope>> {
    const path = '/v1/panel' + (teamLeague !== undefined ? `?teamLeague=${encodeURIComponent(teamLeague)}` : '');
    const response = await this.request('GET', path);
    if (response.status < 200 || response.status > 299) {
      return {status: response.status, value: null, error: apiErrorFrom(response.body)};
    }
    const value = response.body === null ? null : decodeEnvelope(response.body);
    if (value === null) throw new ContractError('Response does not match the API contract');
    return {status: response.status, value, error: null};
  }

  private async send(method: string, path: string, payload: string | null): Promise<ApiResponse> {
    const bare = path.split('?')[0];
    const headers: Record<string, string> = {Accept: 'application/json'};
    if (!PUBLIC_PATHS.has(bare)) {
      const token = this.tokenSource === undefined ? null : await this.tokenSource();
      if (token !== null) headers.Authorization = `Bearer ${token}`;
    }
    if (payload !== null) headers['Content-Type'] = 'application/json';
    const controller = new AbortController();
    const handle = this.timers.setTimeout(
      () => controller.abort(),
      bare === '/v1/alerts' ? LONG_POLL_READ_MS : TIMEOUT_MS,
    );
    try {
      const response = await this.fetchImpl(this.base + path, {
        method,
        headers,
        body: payload ?? undefined,
        // RN and Node type AbortSignal differently; the runtime signal is the host AbortSignal.
        signal: controller.signal as unknown as NonNullable<Parameters<typeof fetch>[1]>['signal'],
        redirect: 'manual',
      });
      const text = await response.text();
      return {status: response.status, body: parseBody(text)};
    } finally {
      this.timers.clearTimeout(handle);
    }
  }
}

function parseBody(text: string): JsonObject | null {
  if (new TextEncoder().encode(text).length > MAX_BODY_BYTES) {
    throw new ContractError('Response body exceeds 64 KiB');
  }
  if (text.trim() === '') return null;
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    throw new ContractError('Response is not a JSON object');
  }
  if (!isRecord(parsed)) throw new ContractError('Response is not a JSON object');
  return parsed as JsonObject;
}
