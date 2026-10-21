// Reports installed candidates only while the customer opted detection in (AFC-PR-010/-037):
// opted out means no package reads and no report. Candidate names are untrusted input.
import type {ApiClient, ApiResponse} from '../net/apiClient';

/** Vega detection route: Linking.canOpenURL per provider candidate. */
export type InstalledAppQuery = (packageName: string) => Promise<boolean>;

export interface InstalledApps {
  packages: string[];
}

const PACKAGE = /^[A-Za-z0-9._]{1,255}$/;
const MAX_PACKAGES = 500;

export class AppDetector {
  constructor(
    private readonly query: InstalledAppQuery,
    private readonly optedIn: () => boolean,
  ) {}

  async detect(candidates: string[]): Promise<InstalledApps> {
    if (!this.optedIn()) return {packages: []};
    const checked: string[] = [];
    for (const name of candidates) {
      if (checked.includes(name) || !PACKAGE.test(name)) continue;
      checked.push(name);
    }
    const installed: string[] = [];
    for (const name of checked) {
      if (await this.query(name)) installed.push(name);
    }
    return {packages: installed.slice(0, MAX_PACKAGES)};
  }

  /** Sends the detector report only while detection is opted in; null when nothing was sent. */
  async report(client: ApiClient, candidates: string[]): Promise<ApiResponse | null> {
    if (!this.optedIn()) return null;
    const apps = await this.detect(candidates);
    return client.request('POST', '/v1/installed-apps', {packages: apps.packages});
  }
}
