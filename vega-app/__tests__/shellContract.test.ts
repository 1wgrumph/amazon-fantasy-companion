// Shell and repository contract checks (mirrors ShellContractTest.kt).
import {readdirSync, readFileSync, statSync} from 'fs';
import {join} from 'path';
import {shellDestinations} from '../src/shell';
import {node, REPO} from './support/contract';

function files(dir: string): string[] {
  return readdirSync(dir).flatMap(name => {
    const path = join(dir, name);
    return statSync(path).isDirectory() ? files(path) : [path];
  });
}

describe('ShellContractTest', () => {
  // Vega has no Android minSdk; the Vega equivalent is the manifest's minimum OS version from the pinned SDK template.
  test('manifestDeclaresMinimumVegaOsVersion', () => {
    const manifest = readFileSync(join(REPO, 'vega-app/manifest.toml'), 'utf8');
    expect(manifest).toMatch(/\[os\.version\]\s*\nmin\s*=\s*"1\.2"/);
    expect(manifest).toMatch(/^id = "com\.afc\.companion"$/m);
  });

  test('exposesOnlyLinkProfileAndPanelNavigation', () => {
    expect(shellDestinations()).toEqual(new Set(['Link', 'Profile/Settings', 'Panel']));
  });

  test('noMessagingEndpointsInFrozenContract', () => {
    expect(new Set(Object.keys(node('paths')))).toEqual(
      new Set([
        '/v1/link',
        '/v1/link/confirm',
        '/link',
        '/v1/profile',
        '/v1/alerts',
        '/v1/panel',
        '/v1/providers',
        '/v1/routing-outcome',
        '/v1/installed-apps',
      ]),
    );
  });

  test('committedTestTokensDoNotMatchCredentialShapes', () => {
    const assignment = `["']?\\s*[:=]\\s*["']?`;
    const rules = [
      /\b(?:AKIA|ASIA)[A-Z0-9]{16}\b/,
      new RegExp(`\\b(?:access_token|refresh_token|device_token)${assignment}[A-Za-z0-9._/+\\-]{32,}`, 'i'),
      new RegExp(`\\b(?:aws_secret_access_key|yahoo_client_secret)${assignment}[A-Za-z0-9._/+\\-]{40,}`, 'i'),
      new RegExp(`\\bsessionToken${assignment}[A-Za-z0-9._/+\\-]{32,}`),
    ];
    const sources = files(join(REPO, 'vega-app/__tests__'));
    expect(sources.length).toBeGreaterThan(0);
    for (const path of sources) {
      const source = readFileSync(path, 'utf8');
      expect({path, matches: rules.filter(rule => rule.test(source)).map(String)}).toEqual({path, matches: []});
    }
  });
});
