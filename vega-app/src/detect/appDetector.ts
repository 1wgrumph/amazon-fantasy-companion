// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
import type {ApiClient, ApiResponse} from '../net/apiClient';

/** Vega detection route: Linking.canOpenURL per provider candidate. */
export type InstalledAppQuery = (packageName: string) => Promise<boolean>;

export interface InstalledApps {
  packages: string[];
}

export class AppDetector {
  constructor(_query: InstalledAppQuery, _optedIn: () => boolean) {}

  async detect(_candidates: string[]): Promise<InstalledApps> {
    return {packages: []};
  }

  async report(_client: ApiClient, _candidates: string[]): Promise<ApiResponse | null> {
    return null;
  }
}
