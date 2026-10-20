// Interface scaffolding for P2-V01T (red). Behavior lands in P2-V01.
import type {ApiClient} from '../net/apiClient';

export interface LinkPresentation {
  state: string;
  code: string | null;
  message: string;
  showProfile: boolean;
}

export function presentLink(_response: unknown): LinkPresentation | null {
  return null;
}

export interface LinkFlowOptions {
  client: ApiClient;
  sleep: (ms: number) => Promise<void>;
  show: (presentation: LinkPresentation) => void;
  store: (sessionToken: string) => Promise<void>;
}

export async function runLinkFlow(_options: LinkFlowOptions): Promise<void> {}
