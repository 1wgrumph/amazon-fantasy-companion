// api_timeout=10s; alert_poll_wait+5s=25s; api_retry_max=3; exponential backoff=1,2,4s (mirrors ApiPolicyTest.kt).
import {ApiClient} from '../../src/net/apiClient';
import {ContractError} from '../../src/net/dto';
import {envelopeFixture, node, unavailable, withApi} from '../support/contract';

const realFetch: typeof fetch = (input, init) => fetch(input, init);
const recordingBackoff = (delays: number[]) => async (ms: number) => {
  delays.push(ms);
};

describe('ApiPolicyTest', () => {
  async function assertTimeout(path: string, timeoutMs: number) {
    const scheduled: number[] = [];
    const signals: unknown[] = [];
    await withApi([[200, JSON.stringify(envelopeFixture())]], async api => {
      const client = new ApiClient(api.baseUrl, {
        fetch: (input, init) => {
          signals.push(init?.signal);
          return realFetch(input, init);
        },
        timers: {
          setTimeout: (callback, ms) => {
            scheduled.push(ms);
            return setTimeout(callback, ms);
          },
          clearTimeout: handle => clearTimeout(handle as ReturnType<typeof setTimeout>),
        },
      });
      const result = await client.request('GET', path);
      expect(result.status).toBe(200);
      expect(signals).toHaveLength(1);
      expect(signals[0]).toBeInstanceOf(AbortSignal);
      expect(scheduled).toEqual([timeoutMs]);
    });
  }

  test('setsNormalTimeoutsOnRealConnection', () => assertTimeout('/v1/profile', 10_000));

  test('setsLongPollReadTimeoutAboveServerWait', () => assertTimeout('/v1/alerts?cursor=fixture', 25_000));

  // JS has one UI thread: network opening and body parsing must happen after the caller's synchronous turn.
  test('opensAndReadsNetworkOffCallingUiThread', async () => {
    await withApi([[200, JSON.stringify(envelopeFixture())]], async api => {
      let callerTurnOver = false;
      const observed: boolean[] = [];
      const client = new ApiClient(api.baseUrl, {
        fetch: async (input, init) => {
          observed.push(callerTurnOver);
          const response = await realFetch(input, init);
          return new Proxy(response, {
            get(target, property) {
              const value = Reflect.get(target, property, target);
              if (typeof value !== 'function') return value;
              return (...args: unknown[]) => {
                observed.push(callerTurnOver);
                return value.apply(target, args);
              };
            },
          });
        },
      });
      const pending = client.request('GET', '/v1/profile');
      callerTurnOver = true;
      const result = await pending;
      expect(result.status).toBe(200);
      expect(observed.length).toBeGreaterThanOrEqual(2);
      expect(observed.every(Boolean)).toBe(true);
    });
  });

  test('rejectsMalformedJsonResponse', async () => {
    await withApi([[200, '{']], async api => {
      await expect(new ApiClient(api.baseUrl).request('GET', '/v1/profile')).rejects.toBeInstanceOf(ContractError);
    });
  });

  test('rejectsResponseOverContract64KiB', async () => {
    await withApi([[200, JSON.stringify({padding: 'x'.repeat(65_536)})]], async api => {
      await expect(new ApiClient(api.baseUrl).request('GET', '/v1/profile')).rejects.toBeInstanceOf(ContractError);
    });
  });

  test('rejectsRequestOverContract64KiBBeforeSending', async () => {
    await withApi([[201, '{}']], async api => {
      await expect(
        new ApiClient(api.baseUrl).request('POST', '/v1/link', {padding: 'x'.repeat(65_536)}),
      ).rejects.toBeInstanceOf(ContractError);
      expect(api.requests).toHaveLength(0);
    });
  });

  test('defaultBackoffWaitsAtLeastThePrescribedOneSecond', async () => {
    await withApi([[503, unavailable], [200, JSON.stringify(envelopeFixture())]], async api => {
      const result = await new ApiClient(api.baseUrl).request('GET', '/v1/profile');
      expect(result.status).toBe(200);
      expect(api.requests).toHaveLength(2);
      // At least 1 s; no upper timing bound on a loaded host.
      expect(api.requests[1].atMs - api.requests[0].atMs).toBeGreaterThanOrEqual(1_000);
    });
  });

  test('retriesPutWithTheSameRevisionAndBody', async () => {
    const delays: number[] = [];
    const body = {revision: 4, data: {scoringPreset: 'halfPpr'}};
    await withApi([[503, unavailable], [200, JSON.stringify(envelopeFixture(5))]], async api => {
      const result = await new ApiClient(api.baseUrl, {backoff: recordingBackoff(delays)}).request('PUT', '/v1/profile', body);
      expect(result.status).toBe(200);
      expect(delays).toEqual([1_000]);
      expect(api.requests).toHaveLength(2);
      for (const sent of api.requests) expect(JSON.parse(sent.body)).toEqual(body);
    });
  });
});

describe('ApiRetryTest', () => {
  test.each([429, 503])('retriesIdempotentGetWithBoundedExponentialBackoff[transient %s]', async transientStatus => {
    expect(node('paths', '/v1/profile', 'get', 'responses')).toHaveProperty(String(transientStatus));
    const delays: number[] = [];
    const success = envelopeFixture();
    await withApi(
      [[transientStatus, unavailable], [transientStatus, unavailable], [transientStatus, unavailable], [200, JSON.stringify(success)]],
      async api => {
        const result = await new ApiClient(api.baseUrl, {backoff: recordingBackoff(delays)}).request('GET', '/v1/profile');
        expect(result.status).toBe(200);
        expect(delays).toEqual([1_000, 2_000, 4_000]);
        expect(api.requests).toHaveLength(4);
        expect(api.requests.every(sent => sent.method === 'GET' && sent.path === '/v1/profile')).toBe(true);
        expect(result.body).toEqual(success);
      },
    );
  });

  test.each([429, 503])('stopsAfterThreeRetriesAndKeepsStructuredError[transient %s]', async transientStatus => {
    const delays: number[] = [];
    const error = {error: {code: 'unavailable', message: 'retry'}};
    await withApi([[transientStatus, JSON.stringify(error)]], async api => {
      const result = await new ApiClient(api.baseUrl, {backoff: recordingBackoff(delays)}).request('GET', '/v1/profile');
      expect(result.status).toBe(transientStatus);
      expect(delays).toEqual([1_000, 2_000, 4_000]);
      expect(api.requests).toHaveLength(4);
      expect(result.body).toEqual(error);
    });
  });
});

describe('ApiNoRetryTest', () => {
  const cases: [string, string, number][] = [
    ['POST', '/v1/link', 503],
    ['POST', '/v1/link/confirm', 503],
    ['POST', '/v1/routing-outcome', 503],
    ['POST', '/v1/installed-apps', 503],
    ['GET', '/v1/link?handle=fixture', 400],
    ['GET', '/v1/profile', 401],
    ['GET', '/v1/profile', 403],
    ['PUT', '/v1/profile', 409],
    ['POST', '/v1/link/confirm', 410],
  ];
  test.each(cases)('returnsPermanentOrNonIdempotentErrorWithoutRetry[%s %s %s]', async (method, path, status) => {
    expect(node('paths', path.split('?')[0], method.toLowerCase(), 'responses')).toHaveProperty(String(status));
    const delays: number[] = [];
    const error = {error: {code: 'fixture_error', message: 'safe fixture'}};
    await withApi([[status, JSON.stringify(error)]], async api => {
      const result = await new ApiClient(api.baseUrl, {backoff: recordingBackoff(delays)}).request(
        method,
        path,
        method === 'GET' ? null : {},
      );
      expect(result.status).toBe(status);
      expect(api.requests).toHaveLength(1);
      expect(delays).toEqual([]);
      expect(result.body).toEqual(error);
    });
  });
});
