// Real dependency proof before client scaffolding: the OS-bound HTTP peer produces the corpus (mirrors FixtureCalibrationTest.kt).
import {envelopeFixture, node, unavailable, withApi} from '../support/contract';

describe('FixtureCalibrationTest', () => {
  test('realHttpPeerProducesOpenApiEnvelopeAndStructuredError', async () => {
    const body = envelopeFixture();
    await withApi([[200, JSON.stringify(body)], [503, unavailable]], async api => {
      const first = await fetch(`${api.baseUrl}/v1/profile`);
      expect(first.status).toBe(200);
      const received = (await first.json()) as Record<string, unknown>;
      expect(received).toEqual(body);
      expect((node('components', 'schemas', 'Envelope').required as string[]).every(field => field in received)).toBe(true);
      const second = await fetch(`${api.baseUrl}/v1/profile`);
      expect(second.status).toBe(503);
      expect(((await second.json()) as {error: unknown}).error).toEqual({code: 'unavailable', message: 'retry'});
      expect(api.requests).toHaveLength(2);
    });
  });
});
