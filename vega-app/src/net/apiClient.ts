// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
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

export class ApiClient {
  constructor(readonly baseUrl: string, _options: ApiClientOptions = {}) {}

  async request(_method: string, _path: string, _body?: JsonObject | null): Promise<ApiResponse> {
    return {status: 0, body: null};
  }

  async getPanel(_teamLeague?: string): Promise<ApiResult<Envelope>> {
    return {status: 0, value: null, error: null};
  }
}
