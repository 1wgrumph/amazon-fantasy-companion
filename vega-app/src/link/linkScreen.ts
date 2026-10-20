// AFC-PR-038 TV side: presentation of device-code and link-poll responses. Never carries the session token.
import type {ApiClient} from '../net/apiClient';
import {ContractError, isRecord, isTimestamp} from '../net/dto';

export interface LinkPresentation {
  state: string;
  code: string | null;
  message: string;
  showProfile: boolean;
}

const CODE = /^[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{8}$/;
const LINK_STATES = new Set(['unlinked', 'codePending', 'linked', 'expired']);

interface DeviceCode {
  code: string;
  expires: string;
  handle: string;
}

function deviceCodeFrom(response: Record<string, unknown>): DeviceCode | null {
  const code = typeof response.code === 'string' && CODE.test(response.code) ? response.code : null;
  if (code === null || !isTimestamp(response.expires)) return null;
  const handle = typeof response.handle === 'string' && response.handle.length > 0 ? response.handle : null;
  return handle === null ? null : {code, expires: response.expires, handle};
}

interface LinkState {
  state: string;
  sessionToken: string | null;
}

function linkStateFrom(response: Record<string, unknown>): LinkState | null {
  const state = typeof response.state === 'string' && LINK_STATES.has(response.state) ? response.state : null;
  if (state === null) return null;
  const token = response.sessionToken;
  if (token !== undefined && typeof token !== 'string') return null;
  return {state, sessionToken: token ?? null};
}

function present(response: unknown, linkPage: string): LinkPresentation | null {
  if (!isRecord(response)) return null;
  if ('code' in response) {
    const code = deviceCodeFrom(response);
    if (code === null) return null;
    return {
      state: 'codePending',
      code: code.code,
      message: `On your phone, open ${linkPage} and enter this code before ${code.expires}`,
      showProfile: false,
    };
  }
  const state = linkStateFrom(response);
  if (state === null) return null;
  switch (state.state) {
    case 'unlinked':
      return {state: state.state, code: null, message: 'This TV is not linked. Select Get code to link it.', showProfile: false};
    case 'codePending':
      return {state: state.state, code: null, message: 'Waiting for the code to be confirmed', showProfile: false};
    case 'linked':
      return {state: state.state, code: null, message: 'Linked', showProfile: true};
    default:
      return {state: state.state, code: null, message: 'The code expired. Select Get code for a new one.', showProfile: false};
  }
}

export function presentLink(response: unknown): LinkPresentation | null {
  return present(response, 'the link page');
}

export interface LinkFlowOptions {
  client: ApiClient;
  sleep: (ms: number) => Promise<void>;
  show: (presentation: LinkPresentation) => void;
  store: (sessionToken: string) => Promise<void>;
}

const POLL_INTERVAL_MS = 5_000;

function failure(status: number): LinkPresentation {
  return {state: 'error', code: null, message: `Linking failed (HTTP ${status}). Select Get code to try again.`, showProfile: false};
}

/** Issues a code, then polls its handle until linked or expired. Failures are shown, never thrown. */
export async function runLinkFlow(options: LinkFlowOptions): Promise<void> {
  const {client, sleep, show, store} = options;
  const linkPage = `${client.baseUrl.replace(/\/+$/, '')}/link`;
  try {
    const issued = await client.request('POST', '/v1/link', {});
    const code = issued.body !== null && issued.status >= 200 && issued.status <= 299 ? deviceCodeFrom(issued.body) : null;
    if (code === null) return show(failure(issued.status));
    show(present({code: code.code, expires: code.expires, handle: code.handle}, linkPage)!);
    for (;;) {
      await sleep(POLL_INTERVAL_MS);
      const polled = await client.request('GET', `/v1/link?handle=${encodeURIComponent(code.handle)}`);
      const state =
        polled.body !== null && polled.status >= 200 && polled.status <= 299 ? linkStateFrom(polled.body) : null;
      if (state === null) return show(failure(polled.status));
      if (state.state === 'codePending') continue;
      if (state.state === 'linked') {
        if (state.sessionToken === null) return show(failure(polled.status));
        await store(state.sessionToken);
        return show(present({state: state.state}, linkPage)!);
      }
      return show(present({state: state.state}, linkPage)!);
    }
  } catch (error) {
    if (error instanceof ContractError) {
      show({state: 'error', code: null, message: 'The backend sent an unexpected response.', showProfile: false});
    } else {
      show({
        state: 'networkError',
        code: null,
        message: 'Network error. Check the connection, then select Get code.',
        showProfile: false,
      });
    }
  }
}
