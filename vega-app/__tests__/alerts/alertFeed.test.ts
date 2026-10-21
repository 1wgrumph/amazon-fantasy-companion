// DES-AFC-P2-ALERTPATH ALERTSVC: GET /v1/alerts?cursor= long poll (cursor maxLength 256), queue bounded by
// alert_queue_max = 20 (AFC-PR-062), burst updates coalesced per alert (AFC-PR-061). Mirrors AlertFeedTest.kt.
import {AlertFeed} from '../../src/alerts/alertFeed';
import {ApiClient} from '../../src/net/apiClient';
import type {Alert} from '../../src/net/dto';
import {LocalApi, withApi} from '../support/contract';
import {alertJson, page} from '../support/alerts';

const feed = (api: LocalApi) => new AlertFeed(new ApiClient(api.baseUrl, {token: () => 'session-fixture'}));
const ids = (alerts: Alert[]) => alerts.map(a => a.envelope.id);
const revisions = (alerts: Alert[]) => Object.fromEntries(alerts.map(a => [a.envelope.id, a.envelope.revision]));
function paths(api: LocalApi, expected: number): string[] {
  expect(api.requests).toHaveLength(expected);
  return api.requests.map(r => r.path);
}

describe('AlertFeedTest', () => {
  test('firstPollSendsNoCursorAndEachNextPollSendsTheReturnedCursor', () =>
    withApi([page('c1', alertJson('a1')), page('c2'), page('c3')], async api => {
      const f = feed(api);
      expect(ids(await f.poll())).toEqual(['a1']);
      expect(f.cursor).toBe('c1');
      expect(ids(await f.poll())).toEqual([]);
      await f.poll();
      expect(paths(api, 3)).toEqual(['/v1/alerts', '/v1/alerts?cursor=c1', '/v1/alerts?cursor=c2']);
      expect(f.cursor).toBe('c3');
    }));

  test('invalidPageDeliversNothingAndKeepsTheCursor', () => {
    const broken: Record<string, unknown> = alertJson('a2');
    delete broken.schemaVersion;
    return withApi([page('c1', alertJson('a1')), page('c2', alertJson('a3'), broken), page('c3')], async api => {
      const f = feed(api);
      expect(ids(await f.poll())).toEqual(['a1']);
      expect(ids(await f.poll())).toEqual([]);
      expect(f.cursor).toBe('c1');
      await f.poll();
      expect(paths(api, 3)[2]).toBe('/v1/alerts?cursor=c1');
      expect(ids(f.queue)).toEqual(['a1']);
    });
  });

  test('errorStatusDeliversNothingAndKeepsTheCursor', () =>
    withApi(
      [page('c1', alertJson('a1')), [401, JSON.stringify({error: {code: 'unauthenticated', message: 'session rejected'}})], page('c2')],
      async api => {
        const f = feed(api);
        expect(ids(await f.poll())).toEqual(['a1']);
        expect(ids(await f.poll())).toEqual([]);
        expect(f.cursor).toBe('c1');
        await f.poll();
        expect(paths(api, 3)[2]).toBe('/v1/alerts?cursor=c1');
      },
    ));

  test('cursorLongerThanTheContractIsNotAdopted', () =>
    withApi([page('c1'), page('x'.repeat(257), alertJson('a1')), page('c2')], async api => {
      const f = feed(api);
      await f.poll();
      expect(f.cursor).toBe('c1');
      expect(ids(await f.poll())).toEqual([]);
      expect(f.cursor).toBe('c1');
      await f.poll();
      expect(paths(api, 3)[2]).toBe('/v1/alerts?cursor=c1');
    }));

  test('queueKeepsAtMostTwentyNewestAlerts', () => {
    const first = Array.from({length: 15}, (_, i) => alertJson(`a${i + 1}`));
    const second = Array.from({length: 10}, (_, i) => alertJson(`a${i + 16}`));
    return withApi([page('c1', ...first), page('c2', ...second)], async api => {
      const f = feed(api);
      expect(await f.poll()).toHaveLength(15);
      expect(ids(await f.poll())).toEqual(Array.from({length: 10}, (_, i) => `a${i + 16}`));
      expect(f.queue).toHaveLength(20);
      expect(new Set(ids(f.queue))).toEqual(new Set(Array.from({length: 20}, (_, i) => `a${i + 6}`)));
    });
  });

  test('burstUpdatesCoalesceToOneLatestRevisionPerAlert', () =>
    withApi(
      [
        page('c1', alertJson('a1', 1), alertJson('a1', 2), alertJson('a2', 1)),
        page('c2', alertJson('a1', 2), alertJson('a2', 3)),
        page('c3', alertJson('a2', 1)),
      ],
      async api => {
        const f = feed(api);
        expect(revisions(await f.poll())).toEqual({a1: 2, a2: 1});
        expect(revisions(await f.poll())).toEqual({a2: 3});
        expect(ids(await f.poll())).toEqual([]);
        expect(revisions(f.queue)).toEqual({a1: 2, a2: 3});
        expect(f.queue).toHaveLength(2);
      },
    ));

  test('dismissAcknowledgesLocallyWithoutABackendCall', () =>
    withApi([page('c1', alertJson('a1'))], async api => {
      const f = feed(api);
      await f.poll();
      expect(f.dismiss('a1')).toBe(true);
      expect(f.dismiss('a-unknown')).toBe(false);
      expect(paths(api, 1)).toEqual(['/v1/alerts']);
    }));
});
