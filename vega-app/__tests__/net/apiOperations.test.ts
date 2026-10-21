// CONTRACT-AFC-P2-API: one operation per frozen OpenAPI operation, using a real HTTP peer (mirrors ApiOperationsTest.kt).
import {ApiClient} from '../../src/net/apiClient';
import {envelopeFixture, node, runtimeToken, withApi} from '../support/contract';

const operations: [string, string, number][] = [
  ['POST', '/v1/link', 201],
  ['GET', '/v1/link?handle=fixture', 200],
  ['POST', '/v1/link/confirm', 200],
  ['GET', '/v1/profile', 200],
  ['PUT', '/v1/profile', 200],
  ['GET', '/v1/alerts?cursor=fixture', 200],
  ['GET', '/v1/panel', 200],
  ['GET', '/v1/providers', 200],
  ['POST', '/v1/routing-outcome', 200],
  ['POST', '/v1/installed-apps', 200],
];

function responseFor(method: string, bare: string): Record<string, unknown> {
  switch (bare) {
    case '/v1/link':
      return method === 'POST' ? {code: 'ABCD2345', expires: '2026-10-14T12:10:00Z', handle: 'fixture'} : {state: 'codePending'};
    case '/v1/link/confirm':
      return {state: 'linked'};
    case '/v1/profile':
    case '/v1/panel':
      return envelopeFixture();
    case '/v1/alerts':
      return {alerts: [], cursor: 'fixture'};
    default:
      return {};
  }
}

function requestFor(bare: string): Record<string, any> {
  switch (bare) {
    case '/v1/link/confirm':
      return {code: 'ABCD2345', passphrase: 'synthetic', profileId: 'fixture'};
    case '/v1/profile':
      return {revision: 4, data: {scoringPreset: 'halfPpr'}};
    case '/v1/routing-outcome':
      return {eventId: 'fixture', outcome: 'accessUnknown'};
    case '/v1/installed-apps':
      return {packages: []};
    default:
      return {};
  }
}

describe('ApiOperationsTest', () => {
  test.each(operations.map(([m, p, s]) => [`${m} ${p}`, m, p, s] as const))(
    'sendsFrozenOperationAndDecodesJson[%s]',
    async (_name, method, path, status) => {
      const bare = path.split('?')[0];
      const operation = node('paths', bare, method.toLowerCase());
      expect(operation.responses).toHaveProperty(String(status));
      const token = runtimeToken();
      const isProtected = !('security' in operation);
      const response = responseFor(method, bare);
      const request = requestFor(bare);
      await withApi([[status, JSON.stringify(response)]], async api => {
        const result = await new ApiClient(api.baseUrl, {token: () => token}).request(
          method,
          path,
          method === 'GET' ? null : request,
        );
        expect(result.status).toBe(status);
        expect(result.body).toEqual(response);
        expect(api.requests).toHaveLength(1);
        const sent = api.requests[0];
        expect(sent.method).toBe(method);
        expect(sent.path).toBe(path);
        expect(sent.bearer).toBe(isProtected ? `Bearer ${token}` : undefined);
        if (method !== 'GET') expect(JSON.parse(sent.body)).toEqual(request);
      });
    },
  );
});
