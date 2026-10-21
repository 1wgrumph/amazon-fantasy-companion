// DETECTOR (AFC-PR-003, -010, -037): installed-app facts only through the platform query, only while opted in
// (mirrors AppDetectorTest.kt). The Vega query is Linking.canOpenURL, so it is asynchronous.
import {AppDetector, InstalledAppQuery} from '../../src/detect/appDetector';
import {ApiClient} from '../../src/net/apiClient';
import {node, withApi} from '../support/contract';

const MAX_PACKAGES = node('paths', '/v1/installed-apps', 'post', 'requestBody', 'content', 'application/json', 'schema', 'properties', 'packages')
  .maxItems as number;
const installed = new Set(['com.example.provider.a', 'com.example.provider.c']);
const candidates = ['com.example.provider.a', 'com.example.provider.b', 'com.example.provider.c'];

describe('AppDetectorTest', () => {
  let queried: string[];
  let query: InstalledAppQuery;
  beforeEach(() => {
    queried = [];
    query = async name => {
      queried.push(name);
      return installed.has(name);
    };
  });

  test('reportsEachInstalledCandidateAndNoAbsentOne', async () => {
    const apps = await new AppDetector(query, () => true).detect(candidates);
    expect(new Set(apps.packages)).toEqual(installed);
    expect(apps.packages.length).toBe(new Set(apps.packages).size);
    expect(apps.packages).not.toContain('com.example.provider.b');
  });

  test('optedOutPerformsNoReads', async () => {
    const apps = await new AppDetector(query, () => false).detect(candidates);
    expect(apps.packages).toEqual([]);
    expect(queried).toEqual([]);
  });

  // Candidate names are untrusted: malformed names are never queried or reported.
  test('malformedCandidatesAreSkipped', async () => {
    const apps = await new AppDetector(async name => {
      queried.push(name);
      return true;
    }, () => true).detect(['com.example.provider.a', 'bad name;', '']);
    expect(apps.packages).toEqual(['com.example.provider.a']);
    expect(queried).toEqual(['com.example.provider.a']);
  });

  test('reportIsBoundedByTheContractCap', async () => {
    expect(MAX_PACKAGES).toBe(500);
    const many = Array.from({length: MAX_PACKAGES + 100}, (_, i) => `com.example.p${i}`);
    const apps = await new AppDetector(async () => true, () => true).detect(many);
    expect(apps.packages).toHaveLength(MAX_PACKAGES);
  });

  test('detectorReportPostsInstalledApps', () =>
    withApi([[200, '{}']], async api => {
      const result = await new AppDetector(query, () => true).report(
        new ApiClient(api.baseUrl, {token: () => 'session-fixture'}),
        candidates,
      );
      expect(result).not.toBeNull();
      expect(result?.status).toBe(200);
      expect(api.requests).toHaveLength(1);
      expect(api.requests[0].method).toBe('POST');
      expect(api.requests[0].path).toBe('/v1/installed-apps');
      expect(new Set(JSON.parse(api.requests[0].body).packages)).toEqual(installed);
    }));

  test('optedOutSendsNoReport', () =>
    withApi([[200, '{}']], async api => {
      await new AppDetector(query, () => false).report(new ApiClient(api.baseUrl, {token: () => 'session-fixture'}), candidates);
      expect(api.requests).toEqual([]);
      expect(queried).toEqual([]);
    }));
});
